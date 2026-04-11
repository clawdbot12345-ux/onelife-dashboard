#!/usr/bin/env python3
"""
Onelife — Exact Duplicate Analyzer

Finds exact-title duplicates in the live (active + published) Shopify catalog
and builds a merge plan using this rule:

  1. Keep the one WITH product images
  2. If multiple have images, keep the one with the most total inventory
  3. If still tied, keep the oldest (by created_at)

All other duplicates in the group get marked for ARCHIVE (not delete — reversible).

Does NOT include variant-size duplicates (S/M/L/XL) — those are a separate
problem (should be consolidated into proper Shopify variants).

Output:
  reports/dedup-breakdown-YYYY-MM-DD.md       (human-readable breakdown)
  reports/dedup-breakdown-YYYY-MM-DD.json     (full per-group decisions)

Dry-run only. To actually apply, use dedup_apply.py with the same breakdown file.

Environment:
  SHOPIFY_CLIENT_ID
  SHOPIFY_CLIENT_SECRET
  SHOPIFY_STORE=onelifehealth
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

CLIENT_ID = os.environ.get("SHOPIFY_CLIENT_ID")
CLIENT_SECRET = os.environ.get("SHOPIFY_CLIENT_SECRET")
STORE = os.environ.get("SHOPIFY_STORE", "onelifehealth").replace(".myshopify.com", "")
API_VERSION = "2025-01"

if not (CLIENT_ID and CLIENT_SECRET):
    print("ERROR: SHOPIFY_CLIENT_ID + SECRET required", file=sys.stderr)
    sys.exit(1)


def get_token():
    body = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }).encode()
    req = urllib.request.Request(
        f"https://{STORE}.myshopify.com/admin/oauth/access_token",
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())["access_token"]


TOKEN = get_token()
HEADERS = {"X-Shopify-Access-Token": TOKEN, "Accept": "application/json"}


def api_get_raw(path, params=None):
    url = f"https://{STORE}.myshopify.com/admin/api/{API_VERSION}{path}"
    if params:
        url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    for attempt in range(5):
        req = urllib.request.Request(url, headers=HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                return json.loads(resp.read()), resp.headers.get("Link", "")
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(int(e.headers.get("Retry-After", "2")))
                continue
            print(f"  ERROR {e.code} on {path}", file=sys.stderr)
            return None, ""
    return None, ""


def parse_next(link_header):
    if not link_header:
        return None
    for part in link_header.split(","):
        if 'rel="next"' in part:
            m = re.search(r"page_info=([^&>]+)", part)
            if m:
                return m.group(1)
    return None


def fetch_all_live_products():
    """Fetch all active + published products with full image + variant data."""
    all_products = []
    page_info = None
    page_num = 0
    while True:
        page_num += 1
        if page_info:
            params = {"limit": 250, "page_info": page_info}
        else:
            params = {
                "limit": 250,
                "status": "active",
                "published_status": "published",
                "fields": "id,title,handle,vendor,product_type,tags,status,published_at,created_at,updated_at,images,variants,body_html",
            }
        data, link = api_get_raw("/products.json", params)
        if not data:
            break
        products = data.get("products", [])
        if not products:
            break
        all_products.extend(products)
        print(f"  page {page_num}: +{len(products)} (total {len(all_products)})", file=sys.stderr)
        page_info = parse_next(link)
        if not page_info:
            break
        time.sleep(0.4)
    return all_products


def pick_canonical(group):
    """Pick the canonical product from a duplicate group.

    Rules (in order):
      1. Has product images (len(images) > 0)
      2. Higher total inventory across variants
      3. Oldest created_at (earliest in Shopify)
    """
    def score(p):
        images = p.get("images") or []
        has_images = 1 if len(images) > 0 else 0
        total_stock = sum((v.get("inventory_quantity", 0) or 0) for v in (p.get("variants") or []))
        # Negative created_at for "oldest wins"
        created = p.get("created_at", "9999")
        return (has_images, total_stock, -ord(created[0]) if created else 0, -int(p.get("id", 0)))

    return max(group, key=score)


def analyze(products):
    """Group by exact title and identify duplicates + canonicals."""
    # Normalize title: strip whitespace, collapse internal whitespace
    title_map = defaultdict(list)
    for p in products:
        title = (p.get("title") or "").strip()
        title = re.sub(r"\s+", " ", title)
        if title:
            title_map[title].append(p)

    duplicate_groups = {t: ps for t, ps in title_map.items() if len(ps) > 1}

    # For each group, pick canonical and mark the rest
    merge_plan = []
    total_to_archive = 0
    for title, group in sorted(duplicate_groups.items(), key=lambda x: -len(x[1])):
        canonical = pick_canonical(group)
        to_archive = [p for p in group if p["id"] != canonical["id"]]
        total_to_archive += len(to_archive)

        # Build a decision record
        record = {
            "title": title,
            "group_size": len(group),
            "canonical": summarize_product(canonical),
            "archive": [summarize_product(p) for p in to_archive],
        }
        merge_plan.append(record)

    return {
        "total_live_products": len(products),
        "unique_titles": len(title_map),
        "duplicate_groups": len(duplicate_groups),
        "products_to_archive": total_to_archive,
        "products_after_dedup": len(products) - total_to_archive,
        "merge_plan": merge_plan,
    }


def summarize_product(p):
    """Short dict representation of a product for the plan."""
    images = p.get("images") or []
    variants = p.get("variants") or []
    total_stock = sum((v.get("inventory_quantity", 0) or 0) for v in variants)
    return {
        "id": p.get("id"),
        "handle": p.get("handle"),
        "vendor": p.get("vendor"),
        "status": p.get("status"),
        "has_images": len(images) > 0,
        "image_count": len(images),
        "variant_count": len(variants),
        "total_inventory": total_stock,
        "created_at": p.get("created_at"),
        "first_image_url": images[0].get("src") if images else None,
    }


def build_markdown(analysis):
    lines = [
        f"# Onelife Shopify — Exact Duplicate Dedup Breakdown",
        f"",
        f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"**Scope:** Live catalog only (`status=active` + `published_status=published`)",
        f"**Rule:** Keep the one with images → fall back to highest inventory → fall back to oldest",
        f"",
        f"## Summary",
        f"",
        f"| Metric | Count |",
        f"|---|---:|",
        f"| Live products before dedup | {analysis['total_live_products']:,} |",
        f"| Unique titles | {analysis['unique_titles']:,} |",
        f"| Duplicate groups | {analysis['duplicate_groups']:,} |",
        f"| **Products to archive** | **{analysis['products_to_archive']:,}** |",
        f"| **Products after dedup** | **{analysis['products_after_dedup']:,}** |",
        f"",
    ]

    # Quick breakdown by group size
    size_buckets = defaultdict(int)
    for g in analysis["merge_plan"]:
        size_buckets[g["group_size"]] += 1
    lines.append("### Duplicate group size distribution")
    lines.append("")
    lines.append("| Group size | # groups | Products in these groups |")
    lines.append("|---:|---:|---:|")
    for size in sorted(size_buckets.keys(), reverse=True):
        n = size_buckets[size]
        lines.append(f"| {size}× | {n:,} | {n * size:,} |")
    lines.append("")

    # Canonical quality sanity-check
    canonical_with_image = sum(1 for g in analysis["merge_plan"] if g["canonical"]["has_images"])
    canonical_without_image = len(analysis["merge_plan"]) - canonical_with_image
    lines.append("### Canonical quality check")
    lines.append("")
    lines.append(f"- ✓ Groups where the kept (canonical) product HAS images: **{canonical_with_image:,}**")
    lines.append(f"- ⚠ Groups where NO member has an image (canonical chosen by inventory/age): **{canonical_without_image:,}**")
    lines.append("")

    # Top 30 sample decisions
    lines.append("## Sample of 30 duplicate groups (showing decision for each)")
    lines.append("")
    for i, g in enumerate(analysis["merge_plan"][:30], 1):
        lines.append(f"### {i}. {g['title'][:70]}")
        lines.append(f"_{g['group_size']} duplicate listings in live catalog_")
        lines.append("")
        c = g["canonical"]
        img_mark = "🖼 has images" if c["has_images"] else "⚠ no image"
        lines.append(f"**✅ KEEP** (canonical)")
        lines.append(f"- id: `{c['id']}`")
        lines.append(f"- handle: `{c['handle']}`")
        lines.append(f"- {img_mark} ({c['image_count']} img, {c['variant_count']} variants, {c['total_inventory']} units in stock)")
        lines.append(f"- created: {c['created_at']}")
        lines.append("")
        for a in g["archive"]:
            img_mark = "🖼" if a["has_images"] else "❌"
            lines.append(f"**📦 ARCHIVE**")
            lines.append(f"- id: `{a['id']}`")
            lines.append(f"- handle: `{a['handle']}`")
            lines.append(f"- {img_mark} {a['image_count']} images, {a['variant_count']} variants, {a['total_inventory']} units")
            lines.append(f"- created: {a['created_at']}")
            lines.append("")

    if len(analysis["merge_plan"]) > 30:
        lines.append(f"*(...{len(analysis['merge_plan']) - 30:,} more groups in the JSON file)*")
        lines.append("")

    lines.append("## Next step")
    lines.append("")
    lines.append("This is a **DRY RUN** — nothing has been changed in Shopify yet.")
    lines.append("")
    lines.append("To execute: run `scripts/dedup_apply.py` (requires explicit `APPLY=true`), which will:")
    lines.append("1. For each group, set the 'archive' products to `status=archived` via PUT /products/:id")
    lines.append("2. Create 301 redirects from the archived product URLs to the canonical URL")
    lines.append("3. Log every action to `reports/dedup-applied-YYYY-MM-DD.log`")
    lines.append("4. All changes are reversible by setting `status=active` again on the archived products")

    return "\n".join(lines)


def main():
    ROOT = Path(__file__).resolve().parent.parent
    REPORTS_DIR = ROOT / "reports"
    REPORTS_DIR.mkdir(exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    print("Fetching live catalog (active + published)...", file=sys.stderr)
    products = fetch_all_live_products()
    print(f"Total live products: {len(products):,}", file=sys.stderr)

    print("Analyzing duplicates...", file=sys.stderr)
    analysis = analyze(products)

    # Save JSON
    json_path = REPORTS_DIR / f"dedup-breakdown-{today}.json"
    json_path.write_text(json.dumps(analysis, indent=2, default=str))
    print(f"✓ JSON: {json_path}", file=sys.stderr)

    # Save markdown
    md = build_markdown(analysis)
    md_path = REPORTS_DIR / f"dedup-breakdown-{today}.md"
    md_path.write_text(md)
    print(f"✓ Markdown: {md_path}", file=sys.stderr)

    # Print top summary to stdout
    print()
    print(f"═══ DEDUP BREAKDOWN ═══")
    print(f"  Before: {analysis['total_live_products']:,} live products")
    print(f"  After:  {analysis['products_after_dedup']:,} (archived {analysis['products_to_archive']:,})")
    print(f"  Groups: {analysis['duplicate_groups']:,} duplicate groups detected")
    print(f"  Canonical products WITH images: {sum(1 for g in analysis['merge_plan'] if g['canonical']['has_images']):,}/{len(analysis['merge_plan']):,}")


if __name__ == "__main__":
    main()
