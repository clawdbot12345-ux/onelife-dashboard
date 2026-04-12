#!/usr/bin/env python3
"""
Onelife — Blog Article Image Generator (Gemini)

Generates editorial lifestyle hero images for blog articles that have
no featured image, and uploads them to Shopify via the Admin API.

Environment:
  GEMINI_API_KEY / SHOPIFY_CLIENT_ID / SHOPIFY_CLIENT_SECRET
  BLOG_IMG_APPLY=true   (false = dry-run)
  BLOG_IMG_LIMIT=0      (0 = all)
"""
import base64, json, os, re, sys, time
import urllib.error, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_MODEL = os.environ.get("BLOG_IMG_MODEL", "gemini-3-pro-image-preview")
STORE = os.environ.get("SHOPIFY_STORE", "onelifehealth").replace(".myshopify.com", "")
API_VERSION = "2025-01"
APPLY = os.environ.get("BLOG_IMG_APPLY", "true").lower() == "true"
LIMIT = int(os.environ.get("BLOG_IMG_LIMIT", "0"))

if not GEMINI_API_KEY:
    print("ERROR: GEMINI_API_KEY required", file=sys.stderr); sys.exit(1)

SHOPIFY_HEADERS = {}


def get_token():
    cid = os.environ.get("SHOPIFY_CLIENT_ID")
    cs = os.environ.get("SHOPIFY_CLIENT_SECRET")
    body = urllib.parse.urlencode({"grant_type": "client_credentials", "client_id": cid, "client_secret": cs}).encode()
    req = urllib.request.Request(f"https://{STORE}.myshopify.com/admin/oauth/access_token",
                                 data=body, headers={"Content-Type": "application/x-www-form-urlencoded"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())["access_token"]


def shopify_get(path):
    req = urllib.request.Request(f"https://{STORE}.myshopify.com/admin/api/{API_VERSION}{path}", headers=SHOPIFY_HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def generate_image(prompt):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    body = {"contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"responseModalities": ["IMAGE"], "imageConfig": {"aspectRatio": "16:9"}}}
    req = urllib.request.Request(url, data=json.dumps(body).encode(), headers={"Content-Type": "application/json"}, method="POST")
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                data = json.loads(resp.read())
                for part in data.get("candidates", [{}])[0].get("content", {}).get("parts", []):
                    if "inlineData" in part:
                        return base64.b64decode(part["inlineData"]["data"]), part["inlineData"].get("mimeType", "image/png")
                raise RuntimeError("No image data in response")
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 503) and attempt < 2:
                time.sleep(5 * (attempt + 1)); continue
            raise RuntimeError(f"Gemini {e.code}: {e.read().decode()[:200]}")
        except (urllib.error.URLError, TimeoutError):
            if attempt < 2: time.sleep(5); continue
            raise


def build_prompt(title):
    """Build an editorial lifestyle photography prompt from article title."""
    clean = re.sub(r"\s*\|.*$", "", title).strip()
    clean = re.sub(r"\s*\(.*?\)", "", clean).strip()
    return (
        "Professional editorial lifestyle photography for a South African health and wellness blog. "
        f"The article is titled '{clean}'. Create a warm, inviting flat-lay or lifestyle scene "
        "that visually represents this health topic. Use natural ingredients, supplements, fresh produce, "
        "herbal elements, or wellness props as appropriate. Soft natural morning light from the upper left. "
        "Muted earthy palette: warm cream, soft sage green, natural wood tones, terracotta accents. "
        "Shot on a textured cream linen or light wooden surface. Shallow depth of field, photorealistic, "
        "ultra high quality editorial photography. 16:9 landscape format. "
        "NO text, NO words, NO letters, NO numbers, NO brand names anywhere in the image. "
        "NO human faces or identifiable people. Clean, uncluttered, premium wellness aesthetic."
    )


def main():
    global SHOPIFY_HEADERS
    ROOT = Path(__file__).resolve().parent.parent
    REPORTS = ROOT / "reports"
    REPORTS.mkdir(exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    log_path = REPORTS / f"blog-images-applied-{today}.log"

    # Resume
    done_ids = set()
    if log_path.exists():
        for line in log_path.read_text().splitlines():
            try:
                r = json.loads(line)
                if r.get("action") == "blog_image_uploaded":
                    done_ids.add(r.get("article_id"))
            except json.JSONDecodeError:
                pass

    token = get_token()
    SHOPIFY_HEADERS = {"X-Shopify-Access-Token": token, "Accept": "application/json"}

    # Find articles without images
    blogs = shopify_get("/blogs.json")
    targets = []
    for blog in blogs.get("blogs", []):
        bid = blog["id"]
        articles = shopify_get(f"/blogs/{bid}/articles.json?limit=250&fields=id,title,image")
        for art in articles.get("articles", []):
            if not art.get("image") and art["id"] not in done_ids:
                targets.append({"id": art["id"], "blog_id": bid, "title": art.get("title", "")})

    if LIMIT:
        targets = targets[:LIMIT]
    print(f"Articles without images: {len(targets)} (already done: {len(done_ids)})", flush=True)
    print(f"APPLY: {APPLY}", flush=True)

    log_f = open(log_path, "a", buffering=1)

    ok = 0
    fail = 0
    for i, art in enumerate(targets, 1):
        aid = art["id"]
        bid = art["blog_id"]
        title = art["title"]
        try:
            prompt = build_prompt(title)
            img_bytes, mime = generate_image(prompt)
            print(f"  [{i}/{len(targets)}] generated {len(img_bytes):,}B for: {title[:50]}", flush=True)

            if APPLY:
                b64 = base64.b64encode(img_bytes).decode("ascii")
                ext = "png" if "png" in mime else "jpg"
                body = json.dumps({"article": {"id": aid, "image": {
                    "attachment": b64, "filename": f"blog-{aid}.{ext}",
                    "alt": title[:200]
                }}}).encode()
                req = urllib.request.Request(
                    f"https://{STORE}.myshopify.com/admin/api/{API_VERSION}/blogs/{bid}/articles/{aid}.json",
                    data=body, headers={**SHOPIFY_HEADERS, "Content-Type": "application/json"}, method="PUT")
                with urllib.request.urlopen(req, timeout=120) as r:
                    result = json.loads(r.read())
                    src = result.get("article", {}).get("image", {}).get("src", "")
                log_f.write(json.dumps({"action": "blog_image_uploaded", "article_id": aid, "title": title[:80], "src": src, "ts": datetime.now(timezone.utc).isoformat()}) + "\n")
                ok += 1
            else:
                log_f.write(json.dumps({"action": "blog_image_dryrun", "article_id": aid, "title": title[:80], "ts": datetime.now(timezone.utc).isoformat()}) + "\n")
                ok += 1
        except Exception as e:
            log_f.write(json.dumps({"action": "blog_image_failed", "article_id": aid, "title": title[:80], "err": repr(e)[:200], "ts": datetime.now(timezone.utc).isoformat()}) + "\n")
            fail += 1
            print(f"  [{i}/{len(targets)}] FAILED: {repr(e)[:100]}", flush=True)
        time.sleep(3)  # Gemini rate limit

    log_f.close()
    print(f"\n=== DONE: ok={ok} fail={fail} ===", flush=True)


if __name__ == "__main__":
    main()
