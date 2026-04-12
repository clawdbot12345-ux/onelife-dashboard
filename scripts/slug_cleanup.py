#!/usr/bin/env python3
"""
Onelife — URL Slug Cleanup

Finds products with barcode/numeric URL handles (e.g. /products/6007650001153)
and replaces them with descriptive slugs derived from the product title
(e.g. /products/a-vogel-allergy-formula-30ml).

For each renamed product:
  1. PUT /products/:id.json with the new handle
  2. POST /redirects.json to create a 301 from the old URL to the new one
  3. Log every action for audit + rollback

Environment:
  SHOPIFY_CLIENT_ID / SHOPIFY_CLIENT_SECRET / SHOPIFY_STORE
  SLUG_APPLY=true      (false = dry-run)
  SLUG_LIMIT=0         (0 = all, N = first N)

Output:
  reports/slug-cleanup-YYYY-MM-DD.log   (JSONL, resumable)
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

STORE = os.environ.get("SHOPIFY_STORE", "onelifehealth").replace(".myshopify.com", "")
API_VERSION = "2025-01"
APPLY = os.environ.get("SLUG_APPLY", "false").lower() == "true"
LIMIT = int(os.environ.get("SLUG_LIMIT", "0"))
SLEEP = 0.5


def get_token():
    cid = os.environ.get("SHOPIFY_CLIENT_ID")
    cs = os.environ.get("SHOPIFY_CLIENT_SECRET")
    if not (cid and cs):
        print("ERROR: SHOPIFY_CLIENT_ID + SECRET required", file=sys.stderr)
        sys.exit(1)
    body = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "client_id": cid,
        "client_secret": cs,
    }).encode()
    req = urllib.request.Request(
        f"https://{STORE}.myshopify.com/admin/oauth/access_token",
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())["access_token"]


HEADERS = {}


def shopify(method, path, body=None):
    url = f"https://{STORE}.myshopify.com/admin/api/{API_VERSION}{path}"
    data = None
    hdrs = dict(HEADERS)
    if body is not None:
        data = json.dumps(body).encode()
        hdrs["Content-Type"] = "application/json"
    backoff = [2, 4, 8, 16, 32]
    for attempt in range(len(backoff)):
        req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                raw = resp.read()
                out = json.loads(raw) if raw else {}
                time.sleep(SLEEP)
                return resp.status, out
        except urllib.error.HTTPError as e:
            if e.code == 429:
                try:
                    retry = float(e.headers.get("Retry-After", "0"))
                except (TypeError, ValueError):
                    retry = 0.0
                time.sleep(max(retry, backoff[attempt]))
                continue
            err = e.read().decode(errors="replace") if e.fp else ""
            time.sleep(SLEEP)
            return e.code, {"__error__": err}
        except (urllib.error.URLError, TimeoutError):
            time.sleep(backoff[attempt])
            continue
    return -1, {"__error__": "max retries"}


def title_to_handle(title):
    """Convert a product title to a Shopify-friendly URL handle."""
    s = title.lower().strip()
    # Remove vendor prefix pattern "VENDOR - " or "VENDOR -"
    s = re.sub(r"^[a-z0-9][a-z0-9 &''.]+\s*-\s*", "", s)
    # Replace special chars with hyphens
    s = re.sub(r"[^a-z0-9]+", "-", s)
    # Collapse multiple hyphens
    s = re.sub(r"-+", "-", s)
    # Strip leading/trailing hyphens
    s = s.strip("-")
    # Truncate to 80 chars (Shopify limit is 255 but short is better for SEO)
    if len(s) > 80:
        s = s[:80].rsplit("-", 1)[0]
    return s


def fetch_all_products():
    """Fetch all active+published products with id, title, handle."""
    all_products = []
    page_info = None
    while True:
        if page_info:
            params = {"limit": 250, "page_info": page_info}
        else:
            params = {
                "limit": 250,
                "status": "active",
                "published_status": "published",
                "fields": "id,title,handle,vendor",
            }
        url = f"https://{STORE}.myshopify.com/admin/api/{API_VERSION}/products.json"
        url += "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers=HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                data = json.loads(r.read())
                link = r.headers.get("Link", "")
        except urllib.error.HTTPError:
            break
        products = data.get("products", [])
        if not products:
            break
        all_products.extend(products)
        page_info = None
        if link:
            for part in link.split(","):
                if 'rel="next"' in part:
                    m = re.search(r"page_info=([^&>]+)", part)
                    if m:
                        page_info = m.group(1)
        if not page_info:
            break
        time.sleep(0.4)
    return all_products


def main():
    global HEADERS

    ROOT = Path(__file__).resolve().parent.parent
    REPORTS = ROOT / "reports"
    REPORTS.mkdir(exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    log_path = REPORTS / f"slug-cleanup-{today}.log"

    token = get_token()
    HEADERS = {"X-Shopify-Access-Token": token, "Accept": "application/json"}

    # Load resume log
    done_ids = set()
    if log_path.exists():
        for line in log_path.read_text().splitlines():
            try:
                r = json.loads(line)
                if r.get("action") == "handle_changed":
                    done_ids.add(r.get("id"))
            except json.JSONDecodeError:
                pass

    print(f"APPLY: {APPLY}", flush=True)
    print(f"LIMIT: {LIMIT or 'none'}", flush=True)
    if done_ids:
        print(f"Resume: {len(done_ids)} already done", flush=True)

    print("Fetching products...", flush=True)
    products = fetch_all_products()
    print(f"Total live products: {len(products):,}", flush=True)

    # Filter to barcode handles only
    barcode_products = [
        p for p in products
        if re.match(r"^\d+$", p.get("handle", ""))
    ]
    print(f"Products with barcode handles: {len(barcode_products):,}", flush=True)

    # Skip already done
    targets = [p for p in barcode_products if p["id"] not in done_ids]
    if LIMIT:
        targets = targets[:LIMIT]
    print(f"To process: {len(targets):,}", flush=True)

    # Generate new handles and check for collisions
    existing_handles = {p["handle"] for p in products}
    new_handles = {}  # id -> (old_handle, new_handle)
    collisions = 0

    for p in targets:
        old = p["handle"]
        # Generate from full title (including vendor prefix for uniqueness)
        new = title_to_handle(p.get("title", ""))
        if not new:
            new = f"product-{p['id']}"

        # Handle collisions by appending a suffix
        candidate = new
        suffix = 1
        while candidate in existing_handles or candidate in {v[1] for v in new_handles.values()}:
            suffix += 1
            candidate = f"{new}-{suffix}"
            if suffix > 10:
                candidate = f"{new}-{p['id']}"
                break
        if candidate != new:
            collisions += 1

        new_handles[p["id"]] = (old, candidate)

    print(f"Handle collisions resolved: {collisions}", flush=True)

    # Execute
    log_f = open(log_path, "a", buffering=1)

    def log(**kw):
        kw["ts"] = datetime.now(timezone.utc).isoformat()
        log_f.write(json.dumps(kw, default=str) + "\n")

    log(action="run_start", apply=APPLY, targets=len(targets), collisions=collisions)

    ok = 0
    fail = 0
    for i, (pid, (old_handle, new_handle)) in enumerate(new_handles.items(), 1):
        if not APPLY:
            log(action="dryrun", id=pid, old=old_handle, new=new_handle)
            ok += 1
        else:
            # Step 1: Change the handle
            s, resp = shopify("PUT", f"/products/{pid}.json", {
                "product": {"id": pid, "handle": new_handle}
            })
            if s != 200:
                log(action="handle_failed", id=pid, old=old_handle, new=new_handle, status=s)
                fail += 1
            else:
                log(action="handle_changed", id=pid, old=old_handle, new=new_handle)

                # Step 2: Create 301 redirect
                s2, r2 = shopify("POST", "/redirects.json", {
                    "redirect": {
                        "path": f"/products/{old_handle}",
                        "target": f"/products/{new_handle}",
                    }
                })
                if s2 in (200, 201):
                    log(action="redirect_created", id=pid, old=old_handle, new=new_handle)
                elif s2 == 422:
                    log(action="redirect_exists", id=pid, old=old_handle, new=new_handle)
                else:
                    log(action="redirect_failed", id=pid, old=old_handle, new=new_handle, status=s2)
                ok += 1

        if i % 50 == 0 or i == len(new_handles):
            print(f"  [{i}/{len(new_handles)}] ok={ok} fail={fail}", flush=True)

    log(action="run_end", ok=ok, fail=fail)
    log_f.close()
    print(f"\n=== SLUG CLEANUP {'DONE' if APPLY else 'DRY RUN'}: ok={ok} fail={fail} ===", flush=True)


if __name__ == "__main__":
    main()
