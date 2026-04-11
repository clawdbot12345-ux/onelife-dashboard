#!/usr/bin/env python3
"""
Onelife — Full-Catalog SEO Audit

Audits every product, blog article, page, and collection on the Onelife Shopify
store against a set of rule-based SEO checks. Designed for scale (12K+ products)
with cursor-based pagination and graceful rate-limit handling.

Output:
  - reports/seo-audit-YYYY-MM-DD.md       (human-readable executive summary)
  - reports/seo-audit-YYYY-MM-DD.json     (full structured findings, for fix agent)

Environment:
  SHOPIFY_CLIENT_ID
  SHOPIFY_CLIENT_SECRET
  SHOPIFY_STORE=onelifehealth           (default)
  AUDIT_SAMPLE_SIZE=0                    (0 = full catalog, >0 = first N products for testing)
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from collections import defaultdict, Counter
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

CLIENT_ID = os.environ.get("SHOPIFY_CLIENT_ID")
CLIENT_SECRET = os.environ.get("SHOPIFY_CLIENT_SECRET")
STORE = os.environ.get("SHOPIFY_STORE", "onelifehealth").replace(".myshopify.com", "")
SAMPLE_SIZE = int(os.environ.get("AUDIT_SAMPLE_SIZE", "0"))
API_VERSION = "2025-01"

if not (CLIENT_ID and CLIENT_SECRET):
    print("ERROR: SHOPIFY_CLIENT_ID and SHOPIFY_CLIENT_SECRET required", file=sys.stderr)
    sys.exit(1)


# ─── HTTP + auth ───
def get_shopify_token():
    url = f"https://{STORE}.myshopify.com/admin/oauth/access_token"
    body = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }).encode()
    req = urllib.request.Request(url, data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())["access_token"]


TOKEN = get_shopify_token()
HEADERS = {"X-Shopify-Access-Token": TOKEN, "Accept": "application/json"}


def api_get(path, params=None, raw_response=False):
    """GET with rate-limit handling and Link-header pagination support."""
    url = f"https://{STORE}.myshopify.com/admin/api/{API_VERSION}{path}"
    if params:
        url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    for attempt in range(5):
        req = urllib.request.Request(url, headers=HEADERS)
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read())
                link = resp.headers.get("Link", "")
                if raw_response:
                    return data, link
                return data
        except urllib.error.HTTPError as e:
            if e.code == 429:  # rate limit
                retry_after = int(e.headers.get("Retry-After", "2"))
                print(f"  Rate limited, sleeping {retry_after}s...", file=sys.stderr)
                time.sleep(retry_after)
                continue
            print(f"  ERROR {e.code} on {path}: {e.read().decode()[:200]}", file=sys.stderr)
            return None if not raw_response else (None, "")
    return None if not raw_response else (None, "")


def parse_next_page_info(link_header):
    """Parse Shopify's Link header to find the next page_info token."""
    if not link_header:
        return None
    # Format: <https://...?page_info=xyz&limit=250>; rel="next"
    for part in link_header.split(","):
        if 'rel="next"' in part:
            m = re.search(r"page_info=([^&>]+)", part)
            if m:
                return m.group(1)
    return None


def paginate_all(path, params=None, max_pages=100):
    """Collect all items across paginated Shopify REST responses."""
    params = params or {}
    params.setdefault("limit", 250)
    all_items = []
    page_info = None
    for page_num in range(max_pages):
        if page_info:
            # When using page_info, can't mix other filters
            paged_params = {"limit": params["limit"], "page_info": page_info}
        else:
            paged_params = dict(params)
        result = api_get(path, paged_params, raw_response=True)
        if not result or result[0] is None:
            break
        data, link = result
        # The key in the response varies (products, articles, etc.) — grab the first list value
        items = []
        for v in data.values():
            if isinstance(v, list):
                items = v
                break
        if not items:
            break
        all_items.extend(items)
        print(f"  page {page_num + 1}: +{len(items)} (total {len(all_items)})", file=sys.stderr)
        page_info = parse_next_page_info(link)
        if not page_info:
            break
        # Stop early if we've hit the sample size
        if SAMPLE_SIZE and len(all_items) >= SAMPLE_SIZE:
            all_items = all_items[:SAMPLE_SIZE]
            break
        time.sleep(0.5)  # be gentle on rate limits
    return all_items


# ─── HTML stripping ───
class HTMLToText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.text_parts = []

    def handle_data(self, data):
        self.text_parts.append(data)

    def get_text(self):
        return re.sub(r"\s+", " ", " ".join(self.text_parts)).strip()


def html_to_text(html):
    if not html:
        return ""
    parser = HTMLToText()
    try:
        parser.feed(html)
    except Exception:
        return re.sub(r"<[^>]+>", " ", html)
    return parser.get_text()


# ─── Rule-based SEO checks ───
PLACEHOLDER_PHRASES = [
    "please contact us for more info",
    "please contact us for more information",
    "contact us for more info",
    "more info coming soon",
    "coming soon",
    "no description",
    "[description]",
]


def check_product(product):
    """Run all rule-based SEO checks on a single product. Returns a dict of findings."""
    findings = {
        "id": product.get("id"),
        "handle": product.get("handle"),
        "title": product.get("title", ""),
        "vendor": product.get("vendor", ""),
        "status": product.get("status"),
        "published": product.get("published_at") is not None,
        "issues": [],
    }

    title = product.get("title", "") or ""
    handle = product.get("handle", "") or ""
    body_html = product.get("body_html", "") or ""
    body_text = html_to_text(body_html)
    product_type = product.get("product_type", "") or ""
    tags = product.get("tags", "") or ""
    images = product.get("images", []) or []
    variants = product.get("variants", []) or []

    # TITLE checks
    if not title:
        findings["issues"].append(("critical", "title_missing", "Product has no title"))
    else:
        if len(title) < 20:
            findings["issues"].append(("medium", "title_short", f"Title is only {len(title)} chars (ideal 30-70)"))
        elif len(title) > 90:
            findings["issues"].append(("medium", "title_long", f"Title is {len(title)} chars (truncates in search results >70)"))
        if title.isupper() or (sum(1 for c in title if c.isupper()) / max(len(title), 1)) > 0.8:
            findings["issues"].append(("low", "title_allcaps", "Title is all/mostly uppercase — hurts readability + clickthrough"))

    # DESCRIPTION checks
    if not body_text or len(body_text) < 30:
        findings["issues"].append(("critical", "description_missing", f"No product description ({len(body_text)} chars)"))
    else:
        if len(body_text) < 150:
            findings["issues"].append(("high", "description_thin", f"Thin description: {len(body_text)} chars (<150)"))
        lower = body_text.lower()
        for phrase in PLACEHOLDER_PHRASES:
            if phrase in lower:
                findings["issues"].append(("critical", "description_placeholder", f"Placeholder text detected: '{phrase}'"))
                break

    # IMAGE checks
    if not images:
        findings["issues"].append(("high", "no_image", "Product has no images at all"))
    else:
        missing_alt = 0
        weak_alt = 0
        for img in images:
            alt = (img.get("alt") or "").strip()
            if not alt:
                missing_alt += 1
            elif alt.lower() in ("product image", "image", title.lower(), handle.replace("-", " ").lower()):
                weak_alt += 1
            elif len(alt) < 10:
                weak_alt += 1
        if missing_alt == len(images):
            findings["issues"].append(("high", "alt_missing_all", f"ALL {len(images)} image(s) missing alt text"))
        elif missing_alt > 0:
            findings["issues"].append(("medium", "alt_missing_some", f"{missing_alt}/{len(images)} image(s) missing alt text"))
        if weak_alt > 0:
            findings["issues"].append(("low", "alt_weak", f"{weak_alt}/{len(images)} image(s) have weak/generic alt text"))

    # PRODUCT TYPE + TAGS
    if not product_type:
        findings["issues"].append(("medium", "no_product_type", "No product_type (Shopify uses this for filtering + schema)"))
    if not tags:
        findings["issues"].append(("low", "no_tags", "No tags (hurts collection membership + internal linking)"))

    # HANDLE quality
    if handle and len(handle) > 80:
        findings["issues"].append(("low", "handle_long", f"Handle is {len(handle)} chars — long URLs hurt SEO"))

    # VARIANT / INVENTORY
    if not variants:
        findings["issues"].append(("high", "no_variants", "Product has no variants (unusual)"))
    total_inventory = sum(v.get("inventory_quantity", 0) or 0 for v in variants)
    is_active = product.get("status") == "active"
    if is_active and total_inventory == 0:
        findings["issues"].append(("medium", "active_but_oos", "Active product with 0 inventory (consider hiding or restocking)"))

    # PRICE
    for variant in variants:
        price = variant.get("price")
        if not price or price == "0.00":
            findings["issues"].append(("medium", "no_price", "Variant has no price or zero price"))
            break

    findings["issue_count"] = len(findings["issues"])
    findings["critical_count"] = sum(1 for sev, _, _ in findings["issues"] if sev == "critical")
    findings["high_count"] = sum(1 for sev, _, _ in findings["issues"] if sev == "high")
    return findings


def check_article(article):
    findings = {
        "id": article.get("id"),
        "handle": article.get("handle"),
        "title": article.get("title", ""),
        "issues": [],
    }
    title = article.get("title", "") or ""
    body_html = article.get("body_html", "") or ""
    body_text = html_to_text(body_html)
    summary = article.get("summary_html", "") or ""
    image = article.get("image")
    tags = article.get("tags", "") or ""
    author = article.get("author", "") or ""

    if not title:
        findings["issues"].append(("critical", "title_missing", "Article has no title"))
    elif len(title) < 25:
        findings["issues"].append(("medium", "title_short", f"Title is only {len(title)} chars"))
    elif len(title) > 70:
        findings["issues"].append(("low", "title_long", f"Title is {len(title)} chars (will truncate in SERP)"))

    if not body_text or len(body_text) < 300:
        findings["issues"].append(("high", "body_thin", f"Thin content: {len(body_text)} chars (<300)"))

    if not summary:
        findings["issues"].append(("medium", "no_excerpt", "No summary/excerpt (hurts social share + SERP CTR)"))

    if not image:
        findings["issues"].append(("medium", "no_image", "No featured image"))
    elif not image.get("alt"):
        findings["issues"].append(("medium", "image_no_alt", "Featured image missing alt text"))

    if not tags:
        findings["issues"].append(("low", "no_tags", "No tags"))

    if not author:
        findings["issues"].append(("low", "no_author", "No author set"))

    findings["issue_count"] = len(findings["issues"])
    return findings


def check_page(page):
    findings = {
        "id": page.get("id"),
        "handle": page.get("handle"),
        "title": page.get("title", ""),
        "issues": [],
    }
    title = page.get("title", "") or ""
    body_html = page.get("body_html", "") or ""
    body_text = html_to_text(body_html)

    if not title:
        findings["issues"].append(("critical", "title_missing", "Page has no title"))
    if not body_text or len(body_text) < 100:
        findings["issues"].append(("high", "thin_content", f"Thin content: {len(body_text)} chars"))

    findings["issue_count"] = len(findings["issues"])
    return findings


def check_collection(col):
    findings = {
        "id": col.get("id"),
        "handle": col.get("handle"),
        "title": col.get("title", ""),
        "issues": [],
    }
    title = col.get("title", "") or ""
    body_html = col.get("body_html", "") or ""
    body_text = html_to_text(body_html)
    image = col.get("image")

    if not title:
        findings["issues"].append(("critical", "title_missing", "Collection has no title"))
    if not body_text or len(body_text) < 50:
        findings["issues"].append(("high", "no_description", f"Thin description: {len(body_text)} chars"))
    if not image:
        findings["issues"].append(("medium", "no_image", "No collection image"))
    elif image and not image.get("alt"):
        findings["issues"].append(("low", "image_no_alt", "Collection image missing alt text"))

    findings["issue_count"] = len(findings["issues"])
    return findings


# ─── Duplicate detection ───
def find_duplicate_descriptions(product_findings, all_products):
    """Find products that share the exact same description text."""
    desc_map = defaultdict(list)
    for p in all_products:
        text = html_to_text(p.get("body_html", "") or "").strip()
        if text and len(text) > 50:
            desc_map[text].append({"id": p["id"], "title": p.get("title", ""), "handle": p.get("handle", "")})

    duplicates = {}
    for text, prods in desc_map.items():
        if len(prods) >= 2:
            duplicates[text[:100]] = prods
    return duplicates


# ─── Main ───
def main():
    ROOT = Path(__file__).resolve().parent.parent
    REPORTS_DIR = ROOT / "reports"
    REPORTS_DIR.mkdir(exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    md_path = REPORTS_DIR / f"seo-audit-{today}.md"
    json_path = REPORTS_DIR / f"seo-audit-{today}.json"

    print(f"[{datetime.now().isoformat()}] Starting SEO audit", file=sys.stderr)
    if SAMPLE_SIZE:
        print(f"  SAMPLE MODE: first {SAMPLE_SIZE} products only", file=sys.stderr)

    # 1. Fetch everything
    print("\n[1/5] Fetching products...", file=sys.stderr)
    products = paginate_all("/products.json", {"fields": "id,title,handle,body_html,vendor,product_type,tags,status,published_at,images,variants,options"})
    print(f"  Total products fetched: {len(products)}", file=sys.stderr)

    print("\n[2/5] Fetching collections...", file=sys.stderr)
    custom_cols = paginate_all("/custom_collections.json")
    smart_cols = paginate_all("/smart_collections.json")
    collections = custom_cols + smart_cols
    print(f"  Total collections: {len(collections)}", file=sys.stderr)

    print("\n[3/5] Fetching blog articles...", file=sys.stderr)
    blogs = api_get("/blogs.json")
    articles = []
    if blogs:
        for blog in blogs.get("blogs", []):
            arts = paginate_all(f"/blogs/{blog['id']}/articles.json")
            articles.extend(arts)
    print(f"  Total articles: {len(articles)}", file=sys.stderr)

    print("\n[4/5] Fetching pages...", file=sys.stderr)
    pages = paginate_all("/pages.json")
    print(f"  Total pages: {len(pages)}", file=sys.stderr)

    # 2. Run checks
    print("\n[5/5] Running rule-based SEO checks...", file=sys.stderr)
    product_findings = [check_product(p) for p in products]
    article_findings = [check_article(a) for a in articles]
    page_findings = [check_page(p) for p in pages]
    collection_findings = [check_collection(c) for c in collections]

    # Duplicate detection
    print("  → Detecting duplicate descriptions...", file=sys.stderr)
    duplicate_descs = find_duplicate_descriptions(product_findings, products)

    # 3. Aggregate stats
    def aggregate(findings, label):
        total = len(findings)
        with_issues = sum(1 for f in findings if f["issue_count"] > 0)
        critical = sum(1 for f in findings if f.get("critical_count", 0) > 0)
        issue_counter = Counter()
        for f in findings:
            for sev, code, _ in f["issues"]:
                issue_counter[f"{sev}:{code}"] += 1
        return {
            "label": label,
            "total": total,
            "with_issues": with_issues,
            "critical": critical,
            "issue_breakdown": dict(issue_counter.most_common()),
        }

    stats = {
        "products": aggregate(product_findings, "Products"),
        "articles": aggregate(article_findings, "Blog articles"),
        "pages": aggregate(page_findings, "Pages"),
        "collections": aggregate(collection_findings, "Collections"),
    }

    # 4. Save JSON
    full_data = {
        "audited_at": datetime.now(timezone.utc).isoformat(),
        "store": STORE,
        "sample_size": SAMPLE_SIZE or "full",
        "stats": stats,
        "duplicate_descriptions": {
            k: v for k, v in list(duplicate_descs.items())[:50]  # top 50 only
        },
        "duplicate_description_count": len(duplicate_descs),
        "product_findings": product_findings,
        "article_findings": article_findings,
        "page_findings": page_findings,
        "collection_findings": collection_findings,
    }
    json_path.write_text(json.dumps(full_data, indent=2, default=str))
    print(f"\n  ✓ JSON saved: {json_path}", file=sys.stderr)

    # 5. Generate markdown report
    md = build_report(stats, product_findings, article_findings, page_findings, collection_findings, duplicate_descs)
    md_path.write_text(md)
    print(f"  ✓ Report saved: {md_path}", file=sys.stderr)

    # 6. Print summary to stdout
    print()
    print(md.split("## Detailed findings")[0])


def build_report(stats, products, articles, pages, collections, duplicates):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    lines = [
        f"# Onelife SEO Audit — {today}",
        "",
        f"**Store:** onelife.co.za",
        f"**Audit type:** Rule-based (Shopify Admin API)",
        "",
        "## Executive summary",
        "",
    ]

    # Top-level stats table
    lines.append("| Resource | Total | With issues | % clean | Critical |")
    lines.append("|---|---:|---:|---:|---:|")
    for key in ["products", "articles", "pages", "collections"]:
        s = stats[key]
        total = s["total"]
        with_iss = s["with_issues"]
        pct_clean = f"{((total - with_iss) / total * 100):.1f}%" if total else "—"
        lines.append(f"| {s['label']} | {total:,} | {with_iss:,} | {pct_clean} | {s['critical']:,} |")
    lines.append("")

    # Duplicate descriptions
    lines.append(f"### Duplicate descriptions")
    lines.append(f"**{len(duplicates)} distinct description texts** are used on multiple products. "
                 f"This is a MAJOR SEO issue — Google penalises duplicate content and only one of each cluster will rank.")
    lines.append("")
    if duplicates:
        sample_dupes = sorted(duplicates.items(), key=lambda x: -len(x[1]))[:10]
        lines.append("Top 10 most-duplicated description texts:")
        lines.append("")
        for text_snippet, prods in sample_dupes:
            lines.append(f"- **{len(prods)} products** share: _\"{text_snippet[:80]}...\"_")
            for p in prods[:3]:
                lines.append(f"    - {p['title'][:60]}")
            if len(prods) > 3:
                lines.append(f"    - ...and {len(prods)-3} more")
        lines.append("")

    # Issue breakdown
    lines.append("## Issue breakdown by category")
    lines.append("")
    for key in ["products", "articles", "pages", "collections"]:
        s = stats[key]
        if not s["issue_breakdown"]:
            continue
        lines.append(f"### {s['label']}")
        lines.append("")
        lines.append("| Severity | Code | Count |")
        lines.append("|---|---|---:|")
        for code_full, count in s["issue_breakdown"].items():
            sev, code = code_full.split(":", 1)
            emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "⚪"}.get(sev, "")
            lines.append(f"| {emoji} {sev} | `{code}` | {count:,} |")
        lines.append("")

    # Prioritized action list
    lines.append("## Top 20 worst-offending products")
    lines.append("")
    lines.append("(sorted by critical + high issue count)")
    lines.append("")
    worst = sorted(
        [p for p in products if p["issue_count"] > 0],
        key=lambda p: (-p.get("critical_count", 0), -p.get("high_count", 0), -p["issue_count"]),
    )[:20]
    for i, p in enumerate(worst, 1):
        lines.append(f"{i}. **{p['title'][:60]}** ({p.get('vendor','?')}) — {p['issue_count']} issues")
        for sev, code, msg in p["issues"][:5]:
            emoji = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "⚪"}.get(sev, "")
            lines.append(f"   - {emoji} {code}: {msg}")
    lines.append("")

    # Detailed findings header for JSON drill-down
    lines.append("## Detailed findings")
    lines.append("")
    lines.append("Full per-item findings are in the companion JSON file: `reports/seo-audit-YYYY-MM-DD.json`")
    lines.append("")
    lines.append("Use the JSON to drill into specific issue codes, or feed into `scripts/seo_fix.py` to generate Claude-written fixes.")

    return "\n".join(lines)


if __name__ == "__main__":
    main()
