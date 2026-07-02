#!/usr/bin/env python3
"""
Onelife — store-wide price rounding (site audit 2026-07-01 M3).

Most catalogue prices carry conversion-artifact cents (R164.91, R109.48,
R435.18 — an ex-VAT import multiplied by 1.15). They read as data glitches,
not retail prices. This rounds variant prices DOWN to the nearest rand
(never up — no customer ever pays more) unless the cents already look
deliberate (.00 / .50 / .90 / .95 / .99).

Safety:
  - DRY_RUN=true (default): writes the full proposed-change CSV and stats,
    changes nothing.
  - Apply mode first writes the same CSV as a rollback snapshot
    (reports/price-rounding/) BEFORE any mutation.
  - compare_at prices are rounded the same way when present, so sale
    percentages stay sensible.

Environment: SHOPIFY_ADMIN_TOKEN (write_products), DRY_RUN (default true).
"""
import csv
import json
import os
import sys
import time
import urllib.request
from datetime import datetime, timezone

TOKEN = os.environ.get("SHOPIFY_ADMIN_TOKEN")
STORE = os.environ.get("SHOPIFY_STORE", "onelifehealth").replace(".myshopify.com", "")
API = "2025-01"
DRY_RUN = os.environ.get("DRY_RUN", "true").lower() != "false"
DELIBERATE_CENTS = {0, 50, 90, 95, 99}

if not TOKEN:
    print("ERROR: SHOPIFY_ADMIN_TOKEN required", file=sys.stderr)
    sys.exit(1)


def gql(query, variables=None):
    body = json.dumps({"query": query, "variables": variables or {}}).encode()
    for attempt in range(5):
        req = urllib.request.Request(
            f"https://{STORE}.myshopify.com/admin/api/{API}/graphql.json",
            data=body, headers={"X-Shopify-Access-Token": TOKEN,
                                "Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                out = json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 4:
                time.sleep(4)
                continue
            print(f"HTTP {e.code}: {e.read().decode()[:300]}", file=sys.stderr)
            return None
        errs = out.get("errors") or []
        if any("THROTTLED" in str(e) for e in errs) and attempt < 4:
            time.sleep(4)
            continue
        if errs:
            print(f"GraphQL errors: {json.dumps(errs)[:400]}", file=sys.stderr)
            return None
        return out["data"]
    return None


def rounded(price_str):
    """Return rounded-down price string, or None if no change needed."""
    try:
        value = float(price_str)
    except (TypeError, ValueError):
        return None
    cents = round(value * 100) % 100
    if cents in DELIBERATE_CENTS or value < 1:
        return None
    return f"{int(value):d}.00"


def iter_products():
    cursor = None
    while True:
        data = gql("""
          query($cursor: String) {
            products(first: 100, after: $cursor, query: "status:active") {
              pageInfo { hasNextPage endCursor }
              nodes {
                id title
                variants(first: 50) {
                  nodes { id price compareAtPrice }
                }
              }
            }
          }""", {"cursor": cursor})
        if not data:
            sys.exit(1)
        page = data["products"]
        yield from page["nodes"]
        if not page["pageInfo"]["hasNextPage"]:
            return
        cursor = page["pageInfo"]["endCursor"]


def main():
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    os.makedirs("reports/price-rounding", exist_ok=True)
    plan_path = f"reports/price-rounding/{'plan' if DRY_RUN else 'snapshot'}-{ts}.csv"

    changes = []          # (product_id, product_title, variant_id, old, new, old_cmp, new_cmp)
    scanned = products_touched = 0
    for p in iter_products():
        scanned += 1
        pv = []
        for v in p["variants"]["nodes"]:
            new_price = rounded(v["price"])
            new_cmp = rounded(v.get("compareAtPrice")) if v.get("compareAtPrice") else None
            if new_price or new_cmp:
                pv.append((v["id"], v["price"], new_price, v.get("compareAtPrice"), new_cmp))
        if pv:
            products_touched += 1
            for vid, old, new, oc, nc in pv:
                changes.append((p["id"], p["title"], vid, old, new or old, oc or "", nc or oc or ""))
        if scanned % 500 == 0:
            print(f"  scanned {scanned} products, {len(changes)} variant changes so far",
                  file=sys.stderr)

    with open(plan_path, "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["product_id", "product_title", "variant_id",
                    "old_price", "new_price", "old_compare_at", "new_compare_at"])
        w.writerows(changes)
    delta = sum(float(c[3]) - float(c[4]) for c in changes)
    print(f"Scanned {scanned} active products; {products_touched} need rounding "
          f"({len(changes)} variants). Total price reduction across catalogue: R{delta:,.2f}. "
          f"{'PLAN' if DRY_RUN else 'SNAPSHOT'}: {plan_path}")

    if DRY_RUN:
        print("DRY_RUN — no changes made. Re-run with DRY_RUN=false to apply.")
        return

    # ── apply, grouped per product ──
    by_product = {}
    for pid, _t, vid, old, new, oc, nc in changes:
        by_product.setdefault(pid, []).append((vid, new, nc))
    applied = failed = 0
    for i, (pid, variants) in enumerate(by_product.items()):
        vinput = []
        for vid, new, nc in variants:
            entry = {"id": vid, "price": new}
            if nc:
                entry["compareAtPrice"] = nc
            vinput.append(entry)
        data = gql("""
          mutation($productId: ID!, $variants: [ProductVariantsBulkInput!]!) {
            productVariantsBulkUpdate(productId: $productId, variants: $variants) {
              userErrors { field message }
            }
          }""", {"productId": pid, "variants": vinput})
        errs = (data or {}).get("productVariantsBulkUpdate", {}).get("userErrors") \
            if data else [{"message": "request failed"}]
        if errs:
            failed += 1
            print(f"  ✗ {pid}: {json.dumps(errs)[:200]}", file=sys.stderr)
        else:
            applied += 1
        if i % 100 == 0:
            print(f"  applied {applied}/{len(by_product)} products (failed {failed})",
                  file=sys.stderr)
        time.sleep(0.35)  # stay under the cost-based throttle
    print(f"DONE: {applied} products updated, {failed} failed. Rollback snapshot: {plan_path}")
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()
