#!/usr/bin/env python3
"""
Onelife — Product Image Generator (Gemini 3 Pro Image / Nano Banana Pro)

Generates professional product photography for every live Shopify product
that has no images, and uploads the result to Shopify via the Admin API.

Reads the latest SEO audit to find products flagged `no_image`, then:
  1. Derives a category from the product title/vendor
  2. Builds a clean-label product photography prompt
  3. Calls Gemini 3 Pro Image (Nano Banana Pro) to generate a square image
  4. POST /products/:id/images.json to attach it
  5. Logs every action as JSONL for resume + audit

Environment:
  GEMINI_API_KEY          Google AI Studio key (AIza...)
  SHOPIFY_CLIENT_ID
  SHOPIFY_CLIENT_SECRET
  SHOPIFY_STORE=onelifehealth
  IMG_LIMIT=0             (0 = all, N = canary of first N)
  IMG_CONCURRENCY=3       (parallel Gemini calls)
  IMG_SLEEP=2.0           (seconds between Gemini calls per worker)
  IMG_APPLY=true          (false = dry-run, generates but doesn't upload)
  IMG_MODEL=gemini-3-pro-image-preview

Output:
  reports/product-images-applied-YYYY-MM-DD.log   (JSONL, resumable)
  reports/product-images-summary-YYYY-MM-DD.md    (human-readable summary)
"""
import base64
import json
import os
import re
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_MODEL = os.environ.get("IMG_MODEL", "gemini-3-pro-image-preview")
STORE = os.environ.get("SHOPIFY_STORE", "onelifehealth").replace(".myshopify.com", "")
API_VERSION = "2025-01"
LIMIT = int(os.environ.get("IMG_LIMIT", "0"))
CONCURRENCY = int(os.environ.get("IMG_CONCURRENCY", "3"))
IMG_SLEEP = float(os.environ.get("IMG_SLEEP", "2.0"))
APPLY = os.environ.get("IMG_APPLY", "true").lower() == "true"

if not GEMINI_API_KEY:
    print("ERROR: GEMINI_API_KEY required", file=sys.stderr)
    sys.exit(1)

SHOPIFY_HEADERS = {}

# ============================================================================
# Progress tracking + heartbeat
# ============================================================================

class Progress:
    def __init__(self):
        self.lock = threading.Lock()
        self.total = 0
        self.ok = 0
        self.fail = 0
        self.last_change = time.time()

    def set_total(self, total):
        with self.lock:
            self.total = total
            self.last_change = time.time()

    def inc_ok(self):
        with self.lock:
            self.ok += 1
            self.last_change = time.time()

    def inc_fail(self):
        with self.lock:
            self.fail += 1
            self.last_change = time.time()

    def snapshot(self):
        with self.lock:
            return self.ok, self.fail, self.total, time.time() - self.last_change


PROGRESS = Progress()


def heartbeat_loop(stop):
    while not stop.wait(60):
        ok, fail, total, idle = PROGRESS.snapshot()
        flag = ""
        if total and idle > 300:
            flag = f"  ⚠ STALLED ({int(idle)}s idle)"
        elif total and idle > 120:
            flag = f"  · idle {int(idle)}s"
        print(f"  ♥ heartbeat {ok + fail}/{total} ok={ok} fail={fail}{flag}",
              flush=True)


# ============================================================================
# Shopify helpers (global rate limit, same pattern as seo_fix_agent)
# ============================================================================

SHOPIFY_SLEEP = 0.5
_sh_lock = threading.Lock()
_sh_last = [0.0]


def _shopify_throttle():
    with _sh_lock:
        now = time.time()
        delta = now - _sh_last[0]
        if delta < SHOPIFY_SLEEP:
            time.sleep(SHOPIFY_SLEEP - delta)
        _sh_last[0] = time.time()


def get_shopify_token():
    client_id = os.environ.get("SHOPIFY_CLIENT_ID")
    client_secret = os.environ.get("SHOPIFY_CLIENT_SECRET")
    if not (client_id and client_secret):
        print("ERROR: SHOPIFY_CLIENT_ID + SECRET required", file=sys.stderr)
        sys.exit(1)
    body = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }).encode()
    req = urllib.request.Request(
        f"https://{STORE}.myshopify.com/admin/oauth/access_token",
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())["access_token"]


def shopify(method, path, data=None):
    url = f"https://{STORE}.myshopify.com/admin/api/{API_VERSION}{path}"
    body = None
    headers = dict(SHOPIFY_HEADERS)
    if data is not None:
        body = json.dumps(data).encode()
        headers["Content-Type"] = "application/json"
    backoff = [2, 4, 8, 16, 32]
    for attempt in range(len(backoff)):
        _shopify_throttle()
        req = urllib.request.Request(url, data=body, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                raw = resp.read()
                return resp.status, json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            if e.code == 429:
                try:
                    retry_secs = float(e.headers.get("Retry-After", "0"))
                except (TypeError, ValueError):
                    retry_secs = 0.0
                time.sleep(max(retry_secs, backoff[attempt]))
                continue
            err = e.read().decode(errors="replace") if e.fp else ""
            return e.code, {"__error__": err}
        except (urllib.error.URLError, TimeoutError):
            time.sleep(backoff[attempt])
            continue
    return -1, {"__error__": "max retries"}


# ============================================================================
# Gemini image generation
# ============================================================================

def generate_image(prompt, aspect_ratio="1:1"):
    """Call Nano Banana Pro and return (bytes, mime)."""
    url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
           f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}")
    body = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {"aspectRatio": aspect_ratio},
        },
    }
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
                                 headers={"Content-Type": "application/json"},
                                 method="POST")
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                data = json.loads(resp.read())
                break
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 503) and attempt < 2:
                time.sleep(5 * (attempt + 1))
                continue
            err = e.read().decode(errors="replace") if e.fp else ""
            raise RuntimeError(f"Gemini {e.code}: {err[:300]}")
        except (urllib.error.URLError, TimeoutError) as e:
            if attempt < 2:
                time.sleep(5)
                continue
            raise RuntimeError(f"Gemini network error: {e}")
    candidates = data.get("candidates", [])
    if not candidates:
        raise RuntimeError(f"No candidates in response: {json.dumps(data)[:300]}")
    for part in candidates[0].get("content", {}).get("parts", []):
        if "inlineData" in part:
            return (base64.b64decode(part["inlineData"]["data"]),
                    part["inlineData"].get("mimeType", "image/png"))
    raise RuntimeError("No image data in response")


# ============================================================================
# Prompt building — category-aware
# ============================================================================

CATEGORY_STYLES = {
    "tincture": "a dark amber dropper bottle with a black dropper top",
    "oil": "a small amber glass bottle with a dropper",
    "capsules": "a white plastic or amber glass supplement bottle with a screw cap",
    "tablets": "a white plastic or amber glass supplement bottle with a screw cap",
    "powder": "a matte white plastic tub with a screw lid",
    "cream": "a small frosted glass or matte white jar with a screw lid",
    "lotion": "a squeeze-pump plastic bottle with a clean minimalist label",
    "spray": "a clear glass spray bottle with a black trigger",
    "serum": "a small amber glass dropper bottle",
    "extract": "a dark amber dropper bottle",
    "tea": "a tin box or kraft pouch containing loose leaf tea",
    "bar": "a wrapped nutrition bar in minimal cream packaging",
    "gel": "a small squeeze tube in clean wellness branding",
    "oleo resin": "a small amber glass bottle with black cap",
    "syrup": "a clear glass bottle with a clean label",
    "herbs": "a kraft paper bag of dried herbs with minimal label",
    "flowers": "a kraft paper bag of dried herbal flowers",
    "seeds": "a kraft paper bag of seeds",
}

DEFAULT_STYLE = "a premium wellness product bottle or container in clean minimalist packaging"


def derive_category(title: str) -> str:
    t = title.lower()
    for k, style in CATEGORY_STYLES.items():
        if k in t:
            return style
    return DEFAULT_STYLE


def build_prompt(title: str, vendor: str) -> str:
    """Build a product photography prompt from title + vendor."""
    category_style = derive_category(title)
    # Clean the product name — remove the leading "VENDOR - " prefix if present
    clean_name = re.sub(r"^[A-Z][A-Z0-9 &'']+\s*-\s*", "", title).strip()
    brand = vendor or "a premium wellness brand"
    return (
        "Professional product photography for a premium South African health and wellness brand. "
        f"A single {category_style} containing '{clean_name}' from {brand}. "
        "The product is centered, photographed from a slightly elevated 3/4 angle, "
        "sitting on a soft cream linen surface. "
        "Clean minimalist studio composition, lots of negative space. "
        "Natural soft daylight from the upper left creating gentle shadows. "
        "Sharp focus on the product, shallow depth of field, subtle reflections. "
        "Muted earthy palette: warm cream, natural stone, soft sage. "
        "Premium e-commerce catalog photography. Ultra high resolution, "
        "photorealistic. 1:1 square format. No text overlays, no human hands, "
        "no distracting backgrounds, no additional props, no decorative elements."
    )


# ============================================================================
# Shopify image upload
# ============================================================================

def upload_product_image(pid, img_bytes, mime_type, alt_text):
    """POST /products/:id/images.json with base64 attachment."""
    b64 = base64.b64encode(img_bytes).decode("ascii")
    ext = "png" if "png" in mime_type else "jpg"
    status, resp = shopify("POST", f"/products/{pid}/images.json", {
        "image": {
            "attachment": b64,
            "filename": f"product-{pid}.{ext}",
            "alt": alt_text[:255],
        },
    })
    if status not in (200, 201):
        raise RuntimeError(f"Shopify {status}: {str(resp)[:300]}")
    return resp.get("image", {}).get("src", "")


# ============================================================================
# Action log (resumable)
# ============================================================================

class ActionLog:
    def __init__(self, path):
        self.path = path
        self.done = set()
        if path.exists():
            for line in path.read_text().splitlines():
                try:
                    r = json.loads(line)
                    if r.get("action") == "image_uploaded":
                        self.done.add(r.get("product_id"))
                except json.JSONDecodeError:
                    continue
        self.f = open(path, "a", buffering=1)
        self.lock = threading.Lock()

    def write(self, **kw):
        kw["ts"] = datetime.now(timezone.utc).isoformat()
        with self.lock:
            self.f.write(json.dumps(kw, default=str) + "\n")

    def close(self):
        self.f.close()


# ============================================================================
# Main
# ============================================================================

def find_latest_audit(reports_dir):
    candidates = sorted(reports_dir.glob("seo-audit-*.json"))
    if not candidates:
        print("ERROR: no seo-audit-*.json found", file=sys.stderr)
        sys.exit(1)
    return candidates[-1]


def main():
    global SHOPIFY_HEADERS

    ROOT = Path(__file__).resolve().parent.parent
    REPORTS_DIR = ROOT / "reports"
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    audit_path = find_latest_audit(REPORTS_DIR)
    print(f"audit: {audit_path}", flush=True)
    audit = json.loads(audit_path.read_text())

    products = audit.get("product_findings", [])
    targets = [
        p for p in products
        if any(c == "no_image" for s, c, _ in (p.get("issues") or []))
    ]
    total_all = len(targets)
    print(f"found {total_all:,} products with no_image", flush=True)

    log_path = REPORTS_DIR / f"product-images-applied-{today}.log"
    log = ActionLog(log_path)
    if log.done:
        print(f"resume: {len(log.done):,} products already processed", flush=True)
    targets = [p for p in targets if p["id"] not in log.done]
    if LIMIT:
        targets = targets[:LIMIT]
    print(f"to process: {len(targets):,}", flush=True)
    print(f"model: {GEMINI_MODEL}", flush=True)
    print(f"concurrency: {CONCURRENCY}", flush=True)
    print(f"apply: {APPLY}", flush=True)

    PROGRESS.set_total(len(targets))

    # Auth
    token = get_shopify_token()
    SHOPIFY_HEADERS = {"X-Shopify-Access-Token": token, "Accept": "application/json"}

    log.write(action="run_start", model=GEMINI_MODEL, limit=LIMIT,
              concurrency=CONCURRENCY, apply=APPLY, target_count=len(targets))

    # Heartbeat
    stop_hb = threading.Event()
    hb_thread = threading.Thread(target=heartbeat_loop, args=(stop_hb,), daemon=True)
    hb_thread.start()

    def worker(p):
        pid = p["id"]
        title = p.get("title") or ""
        vendor = p.get("vendor") or ""
        try:
            prompt = build_prompt(title, vendor)
            img_bytes, mime = generate_image(prompt)
            log.write(action="image_generated", product_id=pid,
                      bytes=len(img_bytes), mime=mime)
            if APPLY:
                alt = f"{title[:200]}"
                cdn_src = upload_product_image(pid, img_bytes, mime, alt)
                log.write(action="image_uploaded", product_id=pid,
                          title=title[:80], src=cdn_src)
            else:
                log.write(action="image_dryrun", product_id=pid, title=title[:80])
            PROGRESS.inc_ok()
            time.sleep(IMG_SLEEP)
        except Exception as e:
            log.write(action="image_failed", product_id=pid,
                      title=title[:80], err=repr(e)[:300])
            PROGRESS.inc_fail()
            time.sleep(IMG_SLEEP)

    try:
        with ThreadPoolExecutor(max_workers=CONCURRENCY) as ex:
            futures = [ex.submit(worker, p) for p in targets]
            for i, fut in enumerate(as_completed(futures), 1):
                try:
                    fut.result()
                except Exception as e:
                    print(f"  worker exception: {e!r}", flush=True)
                if i % 10 == 0 or i == len(targets):
                    ok, fail, _, _ = PROGRESS.snapshot()
                    print(f"  [{i}/{len(targets)}] ok={ok} fail={fail}", flush=True)
    finally:
        stop_hb.set()
        ok, fail, _, _ = PROGRESS.snapshot()
        log.write(action="run_end", ok=ok, fail=fail)
        log.close()

    # Human-readable summary
    summary_path = REPORTS_DIR / f"product-images-summary-{today}.md"
    ok, fail, total, _ = PROGRESS.snapshot()
    summary_path.write_text(
        f"# Product Image Generation Run — {today}\n\n"
        f"| | |\n"
        f"|---|---:|\n"
        f"| Target (fixable `no_image`) | {total_all:,} |\n"
        f"| Already done (resume) | {len(log.done):,} |\n"
        f"| Attempted this run | {total:,} |\n"
        f"| **Succeeded** | **{ok:,}** |\n"
        f"| **Failed** | **{fail:,}** |\n"
        f"| Model | `{GEMINI_MODEL}` |\n"
        f"| Concurrency | {CONCURRENCY} |\n"
        f"| Apply mode | {APPLY} |\n"
    )
    print(f"\nsummary: {summary_path}", flush=True)
    print(f"=== PRODUCT IMAGE GEN DONE: ok={ok} fail={fail} ===", flush=True)


if __name__ == "__main__":
    main()
