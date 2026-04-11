#!/usr/bin/env python3
"""
Onelife — Exact Duplicate Analyzer (with stock-preserving merge planner)

Scans the live (active + published) Shopify catalog, groups by exact title,
picks a canonical product per group, and builds a variant-level inventory
merge plan so that archiving a duplicate never strands sellable stock.

Canonical selection (applied in order):
  1. Has product images                  (len(images) > 0)
  2. Higher total inventory               (tiebreaker)
  3. Oldest created_at                    (tiebreaker)
  4. Lowest product id                    (deterministic final tiebreaker)

Inventory merge plan (per duplicate group):
  For every non-canonical product in the group, for each of its variants:
    - Match the variant to a canonical variant by normalized title key
      (option1/option2/option3 joined, or variant title, case-insensitive,
      "Default Title"/empty treated as a single-variant placeholder).
    - If matched and qty > 0   -> queue a transfer onto the canonical variant.
    - If unmatched and qty > 0 -> flag for manual review (do NOT auto-merge;
                                  the human decides: add variant to canonical,
                                  fold into default, or skip).
    - If qty <= 0              -> skip (nothing sellable to preserve).

Scope:
  - Single Shopify location (online warehouse). We operate on the aggregate
    variant.inventory_quantity field; no per-location logic needed.
  - Variant-size duplicates (separate products for S/M/L/XL that should be
    real variants on one product) are STILL out of scope — separate pass.
  - Unique products (including unique no-image products) are NEVER touched;
    the analyzer only acts on duplicate groups of size >= 2.

Output:
  reports/dedup-breakdown-YYYY-MM-DD.md    (exec summary, stock plan,
                                            all no-image edge cases,
                                            top manual-review groups,
                                            sample of clean merges)
  reports/dedup-breakdown-YYYY-MM-DD.json  (full per-group decisions
                                            including every transfer and
                                            every flagged unmatched variant)

DRY RUN. Nothing in Shopify is changed. The apply script (dedup_apply.py)
will be built only after the updated breakdown is reviewed.

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

STORE = os.environ.get("SHOPIFY_STORE", "onelifehealth").replace(".myshopify.com", "")
API_VERSION = "2025-01"

# Populated in main() so the pure analysis functions remain importable
# without Shopify credentials (lets us unit-test in isolation).
HEADERS = {}


def get_token():
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


def normalize_variant_key(v):
    """Case-insensitive key used to match variants across duplicate products.

    Prefers option1/option2/option3 (the raw option values) joined with " / ".
    Falls back to the variant `title`. Whitespace is collapsed and lower-cased.
    An empty key or "default title" is normalized to "__default__" so that
    single-variant products in a group always match each other.
    """
    opts = []
    for i in (1, 2, 3):
        val = v.get(f"option{i}")
        if val and str(val).strip():
            opts.append(str(val).strip().lower())
    if opts:
        key = " / ".join(opts)
    else:
        key = (v.get("title") or "").strip().lower()
    key = re.sub(r"\s+", " ", key)
    if key in ("", "default title"):
        return "__default__"
    return key


def pick_canonical(group):
    """Pick the canonical (surviving) product from a duplicate group.

    Implementation note: we use `sorted(... key=...)[0]` and encode every
    rule so that "better" sorts smaller. This is the fix for the previous
    `-ord(created[0])` bug that made "oldest wins" a no-op.

    Rules (smaller sorts first = better):
      1. has_images_rank: 0 if images present, else 1
      2. -total_stock:    more stock -> more negative -> sorts earlier
      3. created:         older ISO date -> lexicographically smaller
      4. pid:             lower id as final deterministic tiebreaker
    """
    def sort_key(p):
        images = p.get("images") or []
        has_images_rank = 0 if len(images) > 0 else 1
        variants = p.get("variants") or []
        total_stock = sum((v.get("inventory_quantity") or 0) for v in variants)
        created = p.get("created_at") or "9999-12-31T00:00:00Z"
        pid = int(p.get("id") or 0)
        return (has_images_rank, -total_stock, created, pid)

    return sorted(group, key=sort_key)[0]


def plan_merge(canonical, archives):
    """Build a variant-level inventory transfer plan for a duplicate group.

    For every archive product's variant with qty > 0:
      - if a canonical variant shares the same normalized title key, queue a
        transfer of that qty onto the canonical variant;
      - otherwise flag the variant as `unmatched` so a human decides what to
        do (add variant to canonical, fold into default, skip, etc.).
    Variants with qty <= 0 are skipped (no stock to preserve).

    Returns a dict with `transfers`, `unmatched`, aggregate qtys, and
    `needs_review` (True iff at least one unmatched variant exists).
    """
    canon_variants = canonical.get("variants") or []
    canon_index = {}
    for cv in canon_variants:
        key = normalize_variant_key(cv)
        # If canonical has duplicate variant keys (rare), keep the first.
        if key not in canon_index:
            canon_index[key] = cv

    transfers = []
    unmatched = []
    for ap in archives:
        for av in (ap.get("variants") or []):
            qty = av.get("inventory_quantity") or 0
            if qty <= 0:
                continue
            key = normalize_variant_key(av)
            cv = canon_index.get(key)
            if cv is not None:
                transfers.append({
                    "from_product_id": ap.get("id"),
                    "from_variant_id": av.get("id"),
                    "from_variant_title": av.get("title"),
                    "to_variant_id": cv.get("id"),
                    "to_variant_title": cv.get("title"),
                    "variant_key": key,
                    "qty": qty,
                })
            else:
                unmatched.append({
                    "from_product_id": ap.get("id"),
                    "from_variant_id": av.get("id"),
                    "from_variant_title": av.get("title"),
                    "variant_key": key,
                    "qty": qty,
                })

    return {
        "transfers": transfers,
        "unmatched": unmatched,
        "total_transfer_qty": sum(t["qty"] for t in transfers),
        "total_unmatched_qty": sum(u["qty"] for u in unmatched),
        "needs_review": len(unmatched) > 0,
    }


def summarize_product(p):
    """Short dict representation of a product for the plan."""
    images = p.get("images") or []
    variants = p.get("variants") or []
    total_stock = sum((v.get("inventory_quantity") or 0) for v in variants)
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


def analyze(products):
    """Group by exact title, pick canonicals, and build merge plans."""
    # Normalize title: strip whitespace, collapse internal whitespace
    title_map = defaultdict(list)
    for p in products:
        title = (p.get("title") or "").strip()
        title = re.sub(r"\s+", " ", title)
        if title:
            title_map[title].append(p)

    # Only groups of size >= 2 enter the merge plan. Unique products
    # (including unique no-image products) are NEVER touched.
    duplicate_groups = {t: ps for t, ps in title_map.items() if len(ps) > 1}

    merge_plan = []
    total_to_archive = 0
    total_transfer_qty = 0
    total_unmatched_qty = 0
    groups_needing_review = 0
    no_image_groups = []  # groups where NO member has any image

    for title, group in sorted(duplicate_groups.items(), key=lambda x: -len(x[1])):
        canonical = pick_canonical(group)
        archives = [p for p in group if p["id"] != canonical["id"]]
        total_to_archive += len(archives)

        merge = plan_merge(canonical, archives)
        total_transfer_qty += merge["total_transfer_qty"]
        total_unmatched_qty += merge["total_unmatched_qty"]
        if merge["needs_review"]:
            groups_needing_review += 1

        record = {
            "title": title,
            "group_size": len(group),
            "canonical": summarize_product(canonical),
            "archive": [summarize_product(p) for p in archives],
            "merge": merge,
        }
        merge_plan.append(record)

        no_member_has_image = not (canonical.get("images") or []) and not any(
            (p.get("images") or []) for p in archives
        )
        if no_member_has_image:
            no_image_groups.append(record)

    return {
        "total_live_products": len(products),
        "unique_titles": len(title_map),
        "duplicate_groups": len(duplicate_groups),
        "products_to_archive": total_to_archive,
        "products_after_dedup": len(products) - total_to_archive,
        "total_transfer_qty": total_transfer_qty,
        "total_unmatched_qty": total_unmatched_qty,
        "groups_needing_review": groups_needing_review,
        "no_image_groups": no_image_groups,
        "merge_plan": merge_plan,
    }


def build_markdown(analysis):
    lines = [
        "# Onelife Shopify — Exact Duplicate Dedup Breakdown",
        "",
        f"**Generated:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        "**Scope:** Live catalog only (`status=active` + `published_status=published`)",
        "**Canonical rule:** images -> highest stock -> oldest -> lowest id",
        "**Stock rule:** variant-level merge onto canonical by title key; unmatched stock flagged for manual review",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|---|---:|",
        f"| Live products before dedup | {analysis['total_live_products']:,} |",
        f"| Unique titles | {analysis['unique_titles']:,} |",
        f"| Duplicate groups | {analysis['duplicate_groups']:,} |",
        f"| **Products to archive** | **{analysis['products_to_archive']:,}** |",
        f"| **Products after dedup** | **{analysis['products_after_dedup']:,}** |",
        f"| Stock units to transfer onto canonicals | {analysis['total_transfer_qty']:,} |",
        f"| Stock units flagged for manual review | {analysis['total_unmatched_qty']:,} |",
        f"| Groups needing manual review | {analysis['groups_needing_review']:,} |",
        f"| No-image edge-case groups | {len(analysis['no_image_groups']):,} |",
        "",
    ]

    # Duplicate group size distribution
    size_buckets = defaultdict(int)
    for g in analysis["merge_plan"]:
        size_buckets[g["group_size"]] += 1
    lines.append("### Duplicate group size distribution")
    lines.append("")
    lines.append("| Group size | # groups | Products in these groups |")
    lines.append("|---:|---:|---:|")
    for size in sorted(size_buckets.keys(), reverse=True):
        n = size_buckets[size]
        lines.append(f"| {size}x | {n:,} | {n * size:,} |")
    lines.append("")

    # Canonical quality check
    canonical_with_image = sum(1 for g in analysis["merge_plan"] if g["canonical"]["has_images"])
    canonical_without_image = len(analysis["merge_plan"]) - canonical_with_image
    lines.append("### Canonical quality check")
    lines.append("")
    lines.append(f"- Groups where the kept canonical HAS images: **{canonical_with_image:,}**")
    lines.append(f"- Groups where NO member has an image (canonical chosen by stock/age): **{canonical_without_image:,}**")
    lines.append("")

    # Stock preservation plan
    lines.append("## Stock preservation plan")
    lines.append("")
    lines.append(
        f"Before archiving, the apply script will transfer **{analysis['total_transfer_qty']:,} units** "
        f"of stock from soon-to-be-archived duplicates onto their canonical counterparts, "
        f"variant-by-variant, matched on normalized variant title key."
    )
    lines.append("")
    lines.append(
        f"**{analysis['total_unmatched_qty']:,} units** across "
        f"**{analysis['groups_needing_review']:,} groups** could not be matched cleanly "
        f"(variant title on the duplicate does not exist on the canonical). These are "
        f"listed under 'Groups needing manual review' below and will NOT be auto-merged."
    )
    lines.append("")
    lines.append("Variants with `inventory_quantity <= 0` are skipped entirely (no sellable stock to preserve).")
    lines.append("")

    # No-image edge case groups — list ALL of them (expected ~24)
    lines.append("## No-image edge-case groups")
    lines.append("")
    if not analysis["no_image_groups"]:
        lines.append("_None — every duplicate group has at least one member with images._")
        lines.append("")
    else:
        lines.append(
            f"These {len(analysis['no_image_groups'])} groups have **no images on any member**. "
            f"The canonical was picked by stock then age. Review each one to decide whether to "
            f"upload an image or kill the listing outright."
        )
        lines.append("")
        for i, g in enumerate(analysis["no_image_groups"], 1):
            lines.append(f"**{i}. {g['title'][:80]}** ({g['group_size']} listings)")
            c = g["canonical"]
            lines.append(
                f"- KEEP: `{c['id']}` / `{c['handle']}` "
                f"({c['variant_count']} variants, {c['total_inventory']} units)"
            )
            for a in g["archive"]:
                lines.append(
                    f"- ARCHIVE: `{a['id']}` / `{a['handle']}` "
                    f"({a['variant_count']} variants, {a['total_inventory']} units)"
                )
            m = g["merge"]
            if m["total_transfer_qty"] or m["total_unmatched_qty"]:
                lines.append(
                    f"- merge: {m['total_transfer_qty']} units transferable, "
                    f"{m['total_unmatched_qty']} units unmatched"
                )
            lines.append("")

    # Groups needing manual review — top 50 by unmatched qty
    review_groups = [g for g in analysis["merge_plan"] if g["merge"]["needs_review"]]
    review_groups.sort(key=lambda g: -g["merge"]["total_unmatched_qty"])
    lines.append(f"## Groups needing manual review ({len(review_groups):,} total — showing top 50 by unmatched qty)")
    lines.append("")
    if not review_groups:
        lines.append("_None — every duplicate variant matched a canonical variant cleanly._")
        lines.append("")
    else:
        lines.append(
            "These groups contain duplicate variants whose title key does NOT exist on "
            "the canonical. The apply script will transfer the matched variants but will "
            "NOT auto-handle the unmatched stock listed below."
        )
        lines.append("")
        for i, g in enumerate(review_groups[:50], 1):
            m = g["merge"]
            lines.append(f"### {i}. {g['title'][:80]}")
            lines.append(
                f"_{g['group_size']} listings; "
                f"{m['total_transfer_qty']} units transferable, "
                f"**{m['total_unmatched_qty']} units unmatched**_"
            )
            lines.append("")
            c = g["canonical"]
            img_mark = "has images" if c["has_images"] else "NO IMAGE"
            lines.append(f"**KEEP** `{c['id']}` `{c['handle']}` ({img_mark}, {c['variant_count']} variants, {c['total_inventory']} units)")
            lines.append("")
            if m["transfers"]:
                lines.append(f"**Transfers ({m['total_transfer_qty']} units):**")
                for t in m["transfers"][:10]:
                    lines.append(
                        f"- `{t['from_variant_id']}` ({t['from_variant_title']}) "
                        f"-> `{t['to_variant_id']}` ({t['to_variant_title']}): {t['qty']} units"
                    )
                if len(m["transfers"]) > 10:
                    lines.append(f"- (...{len(m['transfers']) - 10} more transfers)")
                lines.append("")
            lines.append(f"**Unmatched ({m['total_unmatched_qty']} units) — manual decision required:**")
            for u in m["unmatched"][:10]:
                lines.append(
                    f"- `{u['from_variant_id']}` ({u['from_variant_title']}) "
                    f"key=`{u['variant_key']}` qty={u['qty']}"
                )
            if len(m["unmatched"]) > 10:
                lines.append(f"- (...{len(m['unmatched']) - 10} more unmatched)")
            lines.append("")

    # Sample of 20 clean merges — biggest groups first
    clean_groups = [g for g in analysis["merge_plan"] if not g["merge"]["needs_review"]]
    clean_groups.sort(key=lambda g: (-g["group_size"], -g["merge"]["total_transfer_qty"]))
    lines.append("## Sample of clean merges (top 20 by group size)")
    lines.append("")
    for i, g in enumerate(clean_groups[:20], 1):
        lines.append(f"### {i}. {g['title'][:80]}")
        lines.append(f"_{g['group_size']} duplicate listings_")
        lines.append("")
        c = g["canonical"]
        img_mark = "has images" if c["has_images"] else "NO IMAGE"
        lines.append(
            f"**KEEP** `{c['id']}` `{c['handle']}` "
            f"({img_mark}, {c['image_count']} img, "
            f"{c['variant_count']} variants, {c['total_inventory']} units) "
            f"created {c['created_at']}"
        )
        for a in g["archive"]:
            a_img = "img" if a["has_images"] else "no img"
            lines.append(
                f"**ARCHIVE** `{a['id']}` `{a['handle']}` "
                f"({a_img}, {a['variant_count']} variants, {a['total_inventory']} units)"
            )
        m = g["merge"]
        if m["total_transfer_qty"] > 0:
            lines.append(f"- Stock transfer: {m['total_transfer_qty']} units across {len(m['transfers'])} variant(s)")
        else:
            lines.append("- Stock transfer: 0 units (all duplicates were already empty)")
        lines.append("")

    # Next step
    lines.append("## Next step")
    lines.append("")
    lines.append("This is a **DRY RUN** — nothing has been changed in Shopify yet.")
    lines.append("")
    lines.append("The planned apply script (`scripts/dedup_apply.py`, requires explicit `APPLY=true`) will:")
    lines.append("")
    lines.append("1. For each group, execute every queued variant transfer")
    lines.append("   (POST `/inventory_levels/adjust.json` on the online location) BEFORE archiving.")
    lines.append("2. Set every non-canonical product to `status=archived` via PUT `/products/:id`.")
    lines.append("3. Create 301 redirects from archived handles to the canonical handle.")
    lines.append("4. Log every action to `reports/dedup-applied-YYYY-MM-DD.log`.")
    lines.append("5. Skip groups flagged as `needs_review` for unmatched variants, or (if the")
    lines.append("   operator chooses) transfer the matched variants only and leave the rest.")
    lines.append("")
    lines.append("All archiving is reversible: setting `status=active` restores the listing.")
    lines.append("Inventory transfers are NOT reversible automatically — they are real Shopify writes.")

    return "\n".join(lines)


def main():
    global HEADERS
    token = get_token()
    HEADERS = {"X-Shopify-Access-Token": token, "Accept": "application/json"}

    ROOT = Path(__file__).resolve().parent.parent
    REPORTS_DIR = ROOT / "reports"
    REPORTS_DIR.mkdir(exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    print("Fetching live catalog (active + published)...", file=sys.stderr)
    products = fetch_all_live_products()
    print(f"Total live products: {len(products):,}", file=sys.stderr)

    print("Analyzing duplicates + building merge plan...", file=sys.stderr)
    analysis = analyze(products)

    # Save JSON
    json_path = REPORTS_DIR / f"dedup-breakdown-{today}.json"
    json_path.write_text(json.dumps(analysis, indent=2, default=str))
    print(f"  JSON:     {json_path}", file=sys.stderr)

    # Save markdown
    md = build_markdown(analysis)
    md_path = REPORTS_DIR / f"dedup-breakdown-{today}.md"
    md_path.write_text(md)
    print(f"  Markdown: {md_path}", file=sys.stderr)

    # Print top summary to stdout
    print()
    print("=== DEDUP BREAKDOWN ===")
    print(f"  Before:         {analysis['total_live_products']:,} live products")
    print(f"  After:          {analysis['products_after_dedup']:,} (archived {analysis['products_to_archive']:,})")
    print(f"  Groups:         {analysis['duplicate_groups']:,} duplicate groups")
    print(f"  Stock to merge: {analysis['total_transfer_qty']:,} units onto canonicals")
    print(f"  Needs review:  {analysis['total_unmatched_qty']:,} units across {analysis['groups_needing_review']:,} groups")
    print(f"  No-image edge: {len(analysis['no_image_groups']):,} groups")
    print(f"  Canonicals w/ images: {sum(1 for g in analysis['merge_plan'] if g['canonical']['has_images']):,}/{len(analysis['merge_plan']):,}")


if __name__ == "__main__":
    main()
