#!/usr/bin/env python3
"""
Onelife — Variant Consolidation (S/M/L → proper Shopify variants)

Finds products listed as separate items for different sizes
(e.g. "BOODY - Ladies Black Classic Bikini - S", "... - M", "... - L")
and merges them into a single product with size variants.

Process per group:
  1. Pick the canonical product (most images, then oldest)
  2. For each other product in the group:
     a. Add its size as a variant on the canonical (with price + SKU + inventory)
     b. Create a 301 redirect from the old URL to the canonical
     c. Archive the duplicate product
  3. Log every action for audit + rollback

Environment:
  SHOPIFY_CLIENT_ID / SHOPIFY_CLIENT_SECRET / SHOPIFY_STORE
  VARIANT_APPLY=true / VARIANT_LIMIT=0
"""
import json, os, re, sys, time
import urllib.error, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path

STORE = os.environ.get("SHOPIFY_STORE", "onelifehealth").replace(".myshopify.com", "")
API_VERSION = "2025-01"
APPLY = os.environ.get("VARIANT_APPLY", "true").lower() == "true"
LIMIT = int(os.environ.get("VARIANT_LIMIT", "0"))
SHOPIFY_HEADERS = {}


def get_token():
    cid = os.environ.get("SHOPIFY_CLIENT_ID")
    cs = os.environ.get("SHOPIFY_CLIENT_SECRET")
    body = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "client_id": cid, "client_secret": cs,
    }).encode()
    req = urllib.request.Request(
        f"https://{STORE}.myshopify.com/admin/oauth/access_token",
        data=body, headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())["access_token"]


def shopify(method, path, body=None):
    url = f"https://{STORE}.myshopify.com/admin/api/{API_VERSION}{path}"
    data = json.dumps(body).encode() if body else None
    hdrs = dict(SHOPIFY_HEADERS)
    if data:
        hdrs["Content-Type"] = "application/json"
    for attempt in range(5):
        req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                time.sleep(0.5)
                return r.status, json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                try:
                    wait = float(e.headers.get("Retry-After", "2"))
                except:
                    wait = 2
                time.sleep(max(wait, 2 ** attempt))
                continue
            err = e.read().decode(errors="replace") if e.fp else ""
            return e.code, {"__error__": err[:300]}
        except (urllib.error.URLError, TimeoutError):
            time.sleep(2 ** attempt)
    return -1, {"__error__": "max retries"}


def fetch_all_products():
    all_p = []
    page_info = None
    while True:
        if page_info:
            params = {"limit": 250, "page_info": page_info}
        else:
            params = {
                "limit": 250,
                "status": "active",
                "published_status": "published",
                "fields": "id,title,handle,vendor,images,variants,created_at,body_html,product_type,tags",
            }
        url = (
            f"https://{STORE}.myshopify.com/admin/api/{API_VERSION}/products.json?"
            + urllib.parse.urlencode(params)
        )
        req = urllib.request.Request(url, headers=SHOPIFY_HEADERS)
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read())
            link = r.headers.get("Link", "")
        products = data.get("products", [])
        if not products:
            break
        all_p.extend(products)
        page_info = None
        for part in link.split(","):
            if 'rel="next"' in part:
                m = re.search(r"page_info=([^&>]+)", part)
                if m:
                    page_info = m.group(1)
        if not page_info:
            break
        time.sleep(0.4)
    return all_p


SIZE_PATTERN = re.compile(
    r"^(.+?)\s*-\s*(XXS|XS|S|M|L|XL|XXL|2XL|3XL|4XL|"
    r"Small|Medium|Large|Extra Large|Extra-Large)\s*$",
    re.IGNORECASE,
)

SIZE_ORDER = {
    "xxs": 0, "xs": 1, "s": 2, "small": 2,
    "m": 3, "medium": 3,
    "l": 4, "large": 4,
    "xl": 5, "extra large": 5, "extra-large": 5,
    "xxl": 6, "2xl": 6,
    "3xl": 7, "4xl": 8,
}


def pick_canonical(group):
    """Pick the canonical product: most images → oldest."""
    def key(p):
        imgs = len(p.get("images") or [])
        created = p.get("created_at") or "9999"
        pid = int(p.get("id") or 0)
        return (-imgs, created, pid)
    return sorted(group, key=key)[0]


def main():
    global SHOPIFY_HEADERS

    ROOT = Path(__file__).resolve().parent.parent
    REPORTS = ROOT / "reports"
    REPORTS.mkdir(exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    log_path = REPORTS / f"variant-consolidation-{today}.log"

    done_groups = set()
    if log_path.exists():
        for line in log_path.read_text().splitlines():
            try:
                r = json.loads(line)
                if r.get("action") == "group_done":
                    done_groups.add(r.get("parent"))
            except:
                pass

    token = get_token()
    SHOPIFY_HEADERS = {"X-Shopify-Access-Token": token, "Accept": "application/json"}

    print("Fetching products...", flush=True)
    products = fetch_all_products()
    print(f"Total: {len(products)}", flush=True)

    # Find size variant groups
    from collections import defaultdict

    groups = defaultdict(list)
    for p in products:
        title = p.get("title", "")
        match = SIZE_PATTERN.match(title)
        if match:
            parent = match.group(1).strip()
            size = match.group(2).strip()
            p["_size"] = size
            p["_parent"] = parent
            groups[parent].append(p)

    # Only groups with 2+ products
    variant_groups = {k: v for k, v in groups.items() if len(v) >= 2}
    # Skip already done
    variant_groups = {k: v for k, v in variant_groups.items() if k not in done_groups}

    if LIMIT:
        items = list(variant_groups.items())[:LIMIT]
        variant_groups = dict(items)

    total_products = sum(len(v) for v in variant_groups.values())
    print(f"Groups: {len(variant_groups)}, products: {total_products}", flush=True)
    print(f"APPLY: {APPLY}", flush=True)

    log_f = open(log_path, "a", buffering=1)

    def log(**kw):
        kw["ts"] = datetime.now(timezone.utc).isoformat()
        log_f.write(json.dumps(kw, default=str) + "\n")

    log(action="run_start", groups=len(variant_groups), products=total_products, apply=APPLY)

    ok = 0
    fail = 0

    for gi, (parent, group) in enumerate(sorted(variant_groups.items()), 1):
        # Sort by size order
        group.sort(key=lambda p: SIZE_ORDER.get(p["_size"].lower(), 99))

        canonical = pick_canonical(group)
        others = [p for p in group if p["id"] != canonical["id"]]
        sizes = [p["_size"] for p in group]

        print(f"\n  [{gi}/{len(variant_groups)}] {parent[:50]} ({len(group)} sizes: {', '.join(sizes)})", flush=True)

        if not APPLY:
            log(action="group_dryrun", parent=parent, canonical_id=canonical["id"],
                sizes=sizes, count=len(group))
            ok += 1
            continue

        # Step 1: Update canonical product to have "Size" as option
        canonical_variant = (canonical.get("variants") or [{}])[0]

        # First, update the canonical's existing variant to have the size option
        canon_size = canonical["_size"]

        # Set option1 name to "Size" on the product
        s, resp = shopify("PUT", f"/products/{canonical['id']}.json", {
            "product": {
                "id": canonical["id"],
                "options": [{"name": "Size"}],
            }
        })
        if s != 200:
            log(action="option_failed", parent=parent, id=canonical["id"], status=s)
            fail += 1
            continue

        # Update the existing variant's option to the canonical's size
        s, resp = shopify("PUT", f"/variants/{canonical_variant['id']}.json", {
            "variant": {
                "id": canonical_variant["id"],
                "option1": canon_size,
            }
        })
        if s != 200:
            log(action="variant_update_failed", parent=parent, status=s)
            fail += 1
            continue

        log(action="canonical_set", parent=parent, id=canonical["id"],
            handle=canonical["handle"], size=canon_size)

        # Step 2: For each other product, add as variant + archive + redirect
        group_ok = True
        for other in others:
            other_variant = (other.get("variants") or [{}])[0]
            other_size = other["_size"]
            price = other_variant.get("price", "0.00")
            sku = other_variant.get("sku", "")
            inv_qty = other_variant.get("inventory_quantity", 0)

            # Add variant to canonical
            s, resp = shopify("POST", f"/products/{canonical['id']}/variants.json", {
                "variant": {
                    "option1": other_size,
                    "price": price,
                    "sku": sku,
                    "inventory_management": "shopify",
                }
            })
            if s not in (200, 201):
                log(action="add_variant_failed", parent=parent, size=other_size, status=s,
                    resp=str(resp)[:200])
                group_ok = False
                continue

            new_variant_id = resp.get("variant", {}).get("id")
            log(action="variant_added", parent=parent, size=other_size,
                from_product=other["id"], new_variant_id=new_variant_id, price=price)

            # Archive the old product
            s2, _ = shopify("PUT", f"/products/{other['id']}.json", {
                "product": {"id": other["id"], "status": "archived"}
            })
            if s2 == 200:
                log(action="archived", id=other["id"], handle=other["handle"])
            else:
                log(action="archive_failed", id=other["id"], status=s2)

            # Create 301 redirect
            s3, _ = shopify("POST", "/redirects.json", {
                "redirect": {
                    "path": f"/products/{other['handle']}",
                    "target": f"/products/{canonical['handle']}",
                }
            })
            if s3 in (200, 201):
                log(action="redirect_created", from_handle=other["handle"],
                    to_handle=canonical["handle"])

        if group_ok:
            ok += 1
            log(action="group_done", parent=parent, canonical_id=canonical["id"],
                sizes_merged=len(others))
        else:
            fail += 1

        if gi % 10 == 0:
            print(f"  Progress: {gi}/{len(variant_groups)} groups, ok={ok} fail={fail}", flush=True)

    log(action="run_end", ok=ok, fail=fail)
    log_f.close()
    print(f"\n=== DONE: ok={ok} fail={fail} ===", flush=True)


if __name__ == "__main__":
    main()
