#!/usr/bin/env python3
"""
Onelife — Blog Publication Pipeline
====================================

Takes a markdown blog post from content/blogs/ and:
  1. Publishes it to the Onelife Shopify blog (requires SHOPIFY_ADMIN_TOKEN)
  2. Creates a matching Klaviyo email template
  3. Creates a draft Klaviyo campaign scheduled to send the next morning
  4. All outbound links get UTM parameters for GA4 tracking

Usage:
  python scripts/publish_blog.py content/blogs/2026-04-berberine-natures-ozempic.md

Required environment variables:
  KLAVIYO_API_KEY      Klaviyo private API key (pk_...)
  SHOPIFY_ADMIN_TOKEN  Shopify Admin API access token (shpat_...)  [OPTIONAL — blog will be saved locally if missing]
  SHOPIFY_STORE        myshop.myshopify.com host                   [defaults to onelifehealth.myshopify.com]

The markdown file must start with a frontmatter block:
---
title: Blog title
slug: url-slug-here
handle: health-wellness-hub      # Shopify blog handle
excerpt: Short preview for the email
subject: Email subject line
preview: Email preview text
campaign_segment: Xrk5jD         # Klaviyo list/segment ID
send_offset_days: 2              # Days from now to schedule
products:                        # Featured products (for email module)
  - name: GENOLOGIX Berberine 1000 mg
    price: R420
    url: https://onelife.co.za/...
    badge: BEST VALUE
    blurb: 90 veg capsules...
  - name: ...
---

(markdown body here)
"""
import json
import os
import re
import sys
import time
import urllib.request
import urllib.parse
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from pathlib import Path

import email_template

# ─── Config ───
KLAVIYO_KEY = os.environ.get("KLAVIYO_API_KEY")

# Shopify auth — Dev Dashboard apps use OAuth client credentials grant
# (since Jan 2026, legacy shpat_ tokens are no longer created for new custom apps).
# You can either pass:
#   1. SHOPIFY_CLIENT_ID + SHOPIFY_CLIENT_SECRET (preferred, new apps)
#   2. SHOPIFY_ADMIN_TOKEN (legacy shpat_ token, if still valid)
SHOPIFY_CLIENT_ID = os.environ.get("SHOPIFY_CLIENT_ID")
SHOPIFY_CLIENT_SECRET = os.environ.get("SHOPIFY_CLIENT_SECRET")
SHOPIFY_TOKEN_OVERRIDE = os.environ.get("SHOPIFY_ADMIN_TOKEN")  # optional legacy token
SHOPIFY_STORE_RAW = os.environ.get("SHOPIFY_STORE", "onelifehealth.myshopify.com")
# Normalize: strip .myshopify.com if present, we'll add it in URL formatting
SHOPIFY_STORE_HANDLE = SHOPIFY_STORE_RAW.replace(".myshopify.com", "")
SHOPIFY_STORE = f"{SHOPIFY_STORE_HANDLE}.myshopify.com"
SHOPIFY_API_VERSION = "2025-01"

if not KLAVIYO_KEY:
    print("ERROR: KLAVIYO_API_KEY not set", file=sys.stderr)
    sys.exit(1)

def get_shopify_token():
    """Get a Shopify Admin API access token.

    If SHOPIFY_ADMIN_TOKEN is set (legacy shpat_ token), use it directly.
    Otherwise, exchange SHOPIFY_CLIENT_ID + SHOPIFY_CLIENT_SECRET for a
    24-hour token via the OAuth client credentials grant.
    """
    if SHOPIFY_TOKEN_OVERRIDE:
        return SHOPIFY_TOKEN_OVERRIDE
    if not (SHOPIFY_CLIENT_ID and SHOPIFY_CLIENT_SECRET):
        return None
    url = f"https://{SHOPIFY_STORE}/admin/oauth/access_token"
    body = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "client_id": SHOPIFY_CLIENT_ID,
        "client_secret": SHOPIFY_CLIENT_SECRET,
    }).encode()
    req = urllib.request.Request(url, data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read())
            return data.get("access_token")
    except urllib.error.HTTPError as e:
        print(f"  ✗ Shopify OAuth failed: {e.code} {e.read().decode()[:200]}", file=sys.stderr)
        return None

SHOPIFY_TOKEN = get_shopify_token()

# ─── Parse markdown frontmatter ───
def parse_frontmatter(md_content):
    m = re.match(r'^---\n(.*?)\n---\n(.*)$', md_content, re.DOTALL)
    if not m:
        raise ValueError("Blog file must start with YAML frontmatter")
    import yaml  # requires PyYAML — in GHA we'll `pip install pyyaml`
    return yaml.safe_load(m.group(1)), m.group(2).strip()

# Fallback parser without pyyaml (handles simple key: value frontmatter)
def parse_frontmatter_simple(md_content):
    m = re.match(r'^---\n(.*?)\n---\n(.*)$', md_content, re.DOTALL)
    if not m:
        raise ValueError("Blog file must start with YAML frontmatter")
    fm_text = m.group(1)
    body = m.group(2).strip()
    fm = {}
    current_key = None
    current_list = None
    current_obj = None
    for line in fm_text.split('\n'):
        if not line.strip():
            continue
        if line.startswith('  - '):
            # New list item (dict)
            if current_list is None:
                current_list = fm[current_key] = []
            current_obj = {}
            current_list.append(current_obj)
            kv = line[4:]
            if ':' in kv:
                k, _, v = kv.partition(':')
                current_obj[k.strip()] = _strip_quotes(v.strip())
        elif line.startswith('    '):
            kv = line[4:]
            if ':' in kv and current_obj is not None:
                k, _, v = kv.partition(':')
                current_obj[k.strip()] = _strip_quotes(v.strip())
        elif ':' in line and not line.startswith(' '):
            k, _, v = line.partition(':')
            k = k.strip()
            v = _strip_quotes(v.strip())
            if not v:
                current_key = k
                current_list = None
                fm[k] = None
            else:
                fm[k] = v
                current_key = None
                current_list = None
    return fm, body

def _strip_quotes(v):
    """Strip a single pair of surrounding quotes from a simple-parsed value."""
    if len(v) >= 2 and v[0] == v[-1] and v[0] in ("'", '"'):
        return v[1:-1]
    return v

def parse(md_content):
    try:
        import yaml
        return parse_frontmatter(md_content)
    except ImportError:
        return parse_frontmatter_simple(md_content)

# ─── UTM helpers ───
def utm_url(url, campaign_slug, content_id):
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}utm_source=klaviyo&utm_medium=email&utm_campaign={campaign_slug}&utm_content={content_id}"

# ─── Markdown → HTML ───
def _inline(text):
    """Inline markdown → HTML: bold, italic, links."""
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    text = re.sub(r'\*(.+?)\*', r'<em>\1</em>', text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', text)
    return text

def _is_table_row(line):
    s = line.strip()
    return s.startswith('|') and s.count('|') >= 2

def _is_table_divider(line):
    s = line.strip().strip('|')
    cells = [c.strip() for c in s.split('|')]
    return bool(cells) and all(re.fullmatch(r':?-{2,}:?', c) for c in cells)

def _split_row(line):
    return [c.strip() for c in line.strip().strip('|').split('|')]

def md_to_html(md_body):
    """Minimal markdown → HTML — headings, bold, italics, links, lists, and
    GitHub-style pipe tables (added 2026-06 so product-comparison and
    dosing tables render instead of being dropped)."""
    html_out = []
    lines = md_body.split('\n')
    in_list = False
    i = 0
    n = len(lines)
    while i < n:
        line = lines[i]
        # Pipe table: a header row, a divider row, then 0+ body rows
        if _is_table_row(line) and i + 1 < n and _is_table_divider(lines[i + 1]):
            if in_list:
                html_out.append('</ul>'); in_list = False
            headers = _split_row(line)
            i += 2  # skip header + divider
            body_rows = []
            while i < n and _is_table_row(lines[i]):
                body_rows.append(_split_row(lines[i]))
                i += 1
            thead = ''.join(f'<th>{_inline(h)}</th>' for h in headers)
            tbody = ''.join(
                '<tr>' + ''.join(f'<td>{_inline(c)}</td>' for c in row) + '</tr>'
                for row in body_rows
            )
            html_out.append(
                f'<table class="apothecary-table"><thead><tr>{thead}</tr></thead>'
                f'<tbody>{tbody}</tbody></table>'
            )
            continue
        # Headings
        if line.startswith('### '):
            if in_list: html_out.append('</ul>'); in_list = False
            html_out.append(f'<h3>{_inline(line[4:].strip())}</h3>')
        elif line.startswith('## '):
            if in_list: html_out.append('</ul>'); in_list = False
            html_out.append(f'<h2>{_inline(line[3:].strip())}</h2>')
        elif line.startswith('# '):
            if in_list: html_out.append('</ul>'); in_list = False
            html_out.append(f'<h1>{_inline(line[2:].strip())}</h1>')
        elif line.startswith('- ') or line.startswith('* '):
            if not in_list: html_out.append('<ul>'); in_list = True
            html_out.append(f'<li>{_inline(line[2:].strip())}</li>')
        elif line.strip() == '---':
            if in_list: html_out.append('</ul>'); in_list = False
            html_out.append('<hr>')
        elif not line.strip():
            if in_list: html_out.append('</ul>'); in_list = False
        else:
            if in_list: html_out.append('</ul>'); in_list = False
            html_out.append(f'<p>{_inline(line)}</p>')
        i += 1
    if in_list:
        html_out.append('</ul>')
    return '\n'.join(html_out)

# ─── Shopify: publish blog article ───
# ─── Topic banner (mirrors the theme's article keyword→topic map) ───
TOPIC_KEYWORDS = [
    ("magnesium", "magnesium"), ("omega", "omega3"), ("fish oil", "omega3"),
    ("vitamin d", "vitamind"), ("ashwagandha", "ashwagandha"),
    ("collagen", "collagen"), ("probiotic", "probiotics"), ("sleep", "sleep"),
    ("insomnia", "sleep"), ("stress", "stress"), ("anxiety", "stress"),
    ("immun", "immunity"), ("winter", "immunity"), ("gut", "gut"),
    ("bloat", "gut"), ("glp-1", "glp1"), ("glp1", "glp1"), ("ozempic", "glp1"),
    ("berberine", "glp1"), ("energy", "energy"), ("fatigue", "energy"),
    ("joint", "joints"), ("arthrit", "joints"), ("skin", "skin"),
    ("hair", "skin"), ("hormon", "hormones"), ("menopause", "hormones"),
    ("pcos", "hormones"),
]

# Permanent Shopify Files URLs (uploaded 2026-06-12) — these survive theme
# publishes and deletions, unlike /cdn/shop/t/NN/assets/ theme-asset URLs.
BANNER_FILES_BASE = "https://cdn.shopify.com/s/files/1/0682/9136/3126/files/onelife-article-topic-{slug}-1600.jpg"

def topic_for(fm):
    text = (fm.get("title", "") + " " + fm.get("excerpt", "")).lower()
    for kw, slug in TOPIC_KEYWORDS:
        if kw in text:
            return slug
    return "general"

def topic_banner_url(fm):
    """Resolve the article's hero banner. Primary: the permanent Files CDN
    map (deterministic, can't fail). The old runtime page-scrape is gone —
    it grabbed the feed's self-link instead of an article and silently
    returned None, which shipped an imageless article on 2026-06-12."""
    return BANNER_FILES_BASE.format(slug=topic_for(fm))


def _esc(s):
    """Escape text for safe HTML/JSON-LD embedding."""
    return (str(s or "").replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))

def article_canonical_url(fm, blog_handle="health-wellness-hub"):
    return f"https://onelife.co.za/blogs/{blog_handle}/{fm.get('slug','')}"

def render_product_table(products):
    """On-page comparison table built from the SAME frontmatter products the
    email uses. Gives the article internal product links + a structured block
    Google can lift into rich results, and answers the SEO audit's
    'no comparison table / no product links' findings."""
    products = products or []
    if not products:
        return ""
    rows = ""
    for p in products:
        name = _esc(p.get("name", ""))
        url = _esc(p.get("url", "#"))
        price = _esc(p.get("price", ""))
        badge = _esc(p.get("badge", ""))
        blurb = _esc(p.get("blurb", ""))
        best_for = f"<strong>{badge}</strong> — {blurb}" if badge else blurb
        rows += (f'<tr><td><a href="{url}">{name}</a></td>'
                 f'<td>{price}</td><td>{best_for}</td></tr>')
    return ('<h2>How the picks compare</h2>\n'
            '<table class="apothecary-table apothecary-compare">'
            '<thead><tr><th>Product</th><th>Price</th><th>Best for</th></tr></thead>'
            f'<tbody>{rows}</tbody></table>')

def render_faq_section(faq):
    """Render a FAQ block. Pairs with the FAQPage JSON-LD so the same Q&As are
    both human-readable and machine-readable."""
    faq = faq or []
    if not faq:
        return ""
    items = ""
    for qa in faq:
        q = _inline(_esc(qa.get("q", "")))
        a = _inline(_esc(qa.get("a", "")))
        items += f'<h3>{q}</h3>\n<p>{a}</p>\n'
    return f'<h2>Frequently asked questions</h2>\n<div class="apothecary-faq">\n{items}</div>'

def render_references(references):
    """Render a numbered references list. External links get rel=nofollow."""
    references = references or []
    if not references:
        return ""
    items = ""
    for ref in references:
        if isinstance(ref, dict):
            label = _esc(ref.get("label", ref.get("url", "")))
            url = ref.get("url", "")
        else:
            label, url = _esc(ref), ""
        if url:
            items += (f'<li><a href="{_esc(url)}" rel="nofollow noopener" '
                      f'target="_blank">{label}</a></li>')
        else:
            items += f'<li>{label}</li>'
    return ('<h2>References</h2>\n'
            f'<ol class="apothecary-references">{items}</ol>')

def build_jsonld(fm, body_text, blog_handle="health-wellness-hub"):
    """FAQPage + BreadcrumbList JSON-LD for the article body.

    NOTE: the live theme's `snippets/seo-jsonld-article.liquid` already emits
    the canonical Article schema in <head> for every blog post, so we do NOT
    repeat a BlogPosting here (that would duplicate it). We only add what the
    theme does not: a BreadcrumbList, and a FAQPage when the article ships an
    `faq:` block. Answers the audit's 'missing FAQ schema' for articles."""
    url = article_canonical_url(fm, blog_handle)
    graph = [{
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": "https://onelife.co.za"},
            {"@type": "ListItem", "position": 2, "name": "Health & Wellness Hub",
             "item": f"https://onelife.co.za/blogs/{blog_handle}"},
            {"@type": "ListItem", "position": 3, "name": fm.get("title", ""), "item": url},
        ],
    }]
    faq = fm.get("faq") or []
    if faq:
        graph.append({
            "@type": "FAQPage",
            "mainEntity": [{
                "@type": "Question",
                "name": qa.get("q", ""),
                "acceptedAnswer": {"@type": "Answer", "text": qa.get("a", "")},
            } for qa in faq],
        })
    payload = {"@context": "https://schema.org", "@graph": graph}
    return ('<script type="application/ld+json">'
            + json.dumps(payload, ensure_ascii=False)
            + '</script>')

def build_article_html(fm, body_md, blog_handle="health-wellness-hub"):
    """Assemble the full article body Shopify stores: JSON-LD schema, the prose,
    a product comparison table, an FAQ block and a references list. Everything
    after the prose is generated from frontmatter, so an article only needs
    `products`, `faq` and `references` keys to gain all four blocks."""
    body_text = re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", md_to_html(body_md))).strip()
    parts = [
        build_jsonld(fm, body_text, blog_handle),
        md_to_html(body_md),
        render_product_table(fm.get("products")),
        render_faq_section(fm.get("faq")),
        render_references(fm.get("references")),
    ]
    return "\n".join(p for p in parts if p)


def publish_to_shopify(fm, body_md, blog_handle="health-wellness-hub"):
    if not SHOPIFY_TOKEN:
        print("  ⚠ SHOPIFY_ADMIN_TOKEN not set — skipping Shopify publish", file=sys.stderr)
        return None

    # Find the blog ID for the given handle
    url = f"https://{SHOPIFY_STORE}/admin/api/{SHOPIFY_API_VERSION}/blogs.json"
    req = urllib.request.Request(url, headers={
        "X-Shopify-Access-Token": SHOPIFY_TOKEN,
        "accept": "application/json",
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            blogs = json.loads(resp.read())["blogs"]
    except urllib.error.HTTPError as e:
        print(f"  ✗ Shopify blogs fetch failed {e.code}: {e.read().decode()[:300]}", file=sys.stderr)
        return None

    blog_id = None
    for b in blogs:
        if b["handle"] == blog_handle:
            blog_id = b["id"]
            break
    if not blog_id:
        print(f"  ✗ Blog handle '{blog_handle}' not found. Available: {[b['handle'] for b in blogs]}", file=sys.stderr)
        return None

    # Create the article
    article_body = {
        "article": {
            "title": fm.get("title"),
            # Default matches the existing Onelife blog convention
            "author": fm.get("author", "Precious — One Life Health Consultant"),
            "body_html": build_article_html(fm, body_md, blog_handle),
            "handle": fm.get("slug"),
            "summary_html": fm.get("excerpt", ""),
            "tags": fm.get("tags", "wellness,supplements,evidence-based"),
            "published": False,  # ALWAYS draft first; goes live only after the featured image is attached and verified
        }
    }
    url = f"https://{SHOPIFY_STORE}/admin/api/{SHOPIFY_API_VERSION}/blogs/{blog_id}/articles.json"
    req = urllib.request.Request(url,
        data=json.dumps(article_body).encode(),
        headers={
            "X-Shopify-Access-Token": SHOPIFY_TOKEN,
            "content-type": "application/json",
            "accept": "application/json",
        },
        method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            result = json.loads(resp.read())
            article = result["article"]
            article_id = article["id"]
            article_url = f"https://{SHOPIFY_STORE.replace('.myshopify.com','')}.co.za/blogs/{blog_handle}/{article['handle']}"
            # Prefer canonical domain
            article_url = f"https://onelife.co.za/blogs/{blog_handle}/{article['handle']}"
            print(f"  ✓ Shopify article created (draft): {article_id}", file=sys.stderr)
            print(f"    URL: {article_url}", file=sys.stderr)

            # HARD GATE (added after the 2026-06-12 imageless-article incident):
            # attach the topic banner, VERIFY Shopify accepted it, and only
            # then flip the article live. No image => stays draft => the
            # workflow fails loudly and the queue file is NOT archived.
            go_live = os.environ.get("PUBLISH_LIVE", "").lower() == "true"
            banner = topic_banner_url(fm)
            upd = {"article": {"id": article_id,
                               "image": {"src": banner, "alt": fm.get("title", "")},
                               "published": go_live}}
            u2 = f"https://{SHOPIFY_STORE}/admin/api/{SHOPIFY_API_VERSION}/blogs/{blog_id}/articles/{article_id}.json"
            r2 = urllib.request.Request(u2, data=json.dumps(upd).encode(),
                headers={"X-Shopify-Access-Token": SHOPIFY_TOKEN,
                         "content-type": "application/json", "accept": "application/json"},
                method="PUT")
            try:
                with urllib.request.urlopen(r2, timeout=90) as resp2:
                    updated = json.loads(resp2.read())["article"]
            except urllib.error.HTTPError as e:
                print(f"  ✗ Image attach/publish failed {e.code}: {e.read().decode()[:300]}", file=sys.stderr)
                sys.exit(1)
            if not (updated.get("image") or {}).get("src"):
                print("  ✗ Shopify did not retain the featured image — article left as DRAFT, aborting", file=sys.stderr)
                sys.exit(1)
            state = "LIVE" if updated.get("published_at") else "draft"
            print(f"  ✓ Featured image verified ({topic_for(fm)} banner) — article is {state}", file=sys.stderr)

            # Write the article's on-page product picks from the SAME products
            # chosen for the email (frontmatter), so the theme's
            # article-guide-picks metafield path renders curated products
            # instead of keyword-guessing. (2026-06-12: a sleep article's
            # title contained "Winter" and the keyword fallback served
            # immunity products.)
            try:
                picks = []
                for p in (fm.get("products") or []):
                    handle = (p.get("url", "").split("/products/")[-1].split("?")[0].strip("/"))
                    if handle:
                        picks.append({"handle": handle, "kicker": p.get("badge", "Consultant pick")})
                if picks:
                    mf = {"metafield": {"namespace": "apothecary", "key": "picks",
                                        "type": "json", "value": json.dumps(picks)}}
                    u3 = f"https://{SHOPIFY_STORE}/admin/api/{SHOPIFY_API_VERSION}/blogs/{blog_id}/articles/{article_id}/metafields.json"
                    r3 = urllib.request.Request(u3, data=json.dumps(mf).encode(),
                        headers={"X-Shopify-Access-Token": SHOPIFY_TOKEN,
                                 "content-type": "application/json", "accept": "application/json"},
                        method="POST")
                    with urllib.request.urlopen(r3, timeout=60):
                        pass
                    print(f"  ✓ On-page picks metafield set ({len(picks)} products, same as email)", file=sys.stderr)
            except Exception as e:
                print(f"  ⚠ Picks metafield failed: {e} — theme falls back to topic picks", file=sys.stderr)

            return article_url
    except urllib.error.HTTPError as e:
        print(f"  ✗ Shopify article create failed {e.code}: {e.read().decode()[:500]}", file=sys.stderr)
        return None

# ─── Klaviyo: create template + draft campaign ───
KLAVIYO_HEADERS = {
    "accept": "application/vnd.api+json",
    "revision": "2024-10-15",
    "Authorization": f"Klaviyo-API-Key {KLAVIYO_KEY}",
    "content-type": "application/vnd.api+json",
}

def klaviyo_post(path, body):
    req = urllib.request.Request(f"https://a.klaviyo.com/api{path}",
        data=json.dumps(body).encode(),
        headers=KLAVIYO_HEADERS,
        method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"    Klaviyo POST {path} failed {e.code}: {e.read().decode()[:500]}", file=sys.stderr)
        return None

def render_email_html(fm, blog_url, campaign_slug):
    """Campaign HTML via the master template (scripts/email_template.py)."""
    blog_cta = utm_url(blog_url, campaign_slug, "blog-cta")
    intro = fm.get("intro_p1", fm.get("excerpt", ""))
    banner = topic_banner_url(fm) or "https://d3k81ch9hvuctc.cloudfront.net/company/S86r7e/images/d45bbf5c-fb99-44cf-aa2b-d0a22e40dafd.jpeg"
    return email_template.render_email(
        title=fm.get("title", ""),
        eyebrow="From the Apothecary journal",
        campaign_slug=campaign_slug,
        intro_html=intro,
        hero={"src": banner, "href": blog_cta, "alt": "From The Apothecary journal"},
        cta={"label": "Read the full article →", "href": blog_cta},
        products=fm.get("products", []) or [],
        whatsapp_lead="Questions about anything in the article?",
        whatsapp_prefill="Hi Precious, I read the article — quick question",
    )


def render_email_text(fm, blog_url, campaign_slug):
    products = fm.get("products", []) or []
    lines = [
        fm.get('title','').upper(),
        "",
        fm.get('excerpt',''),
        "",
        f"Read the full article: {utm_url(blog_url, campaign_slug, 'blog-cta')}",
        "",
        "FEATURED PRODUCTS",
        "=================",
    ]
    for i, p in enumerate(products):
        prod_url = utm_url(p.get('url','#'), campaign_slug, f"product-{i+1}")
        lines.append(f"")
        lines.append(f"{i+1}. {p.get('name','')} — {p.get('price','')}")
        lines.append(f"   {p.get('blurb','')}")
        lines.append(f"   {prod_url}")
    lines += [
        "",
        "---",
        "Onelife Health · Centurion · Glen Village · Edenvale",
        "onelife.co.za · info@onelife.co.za",
    ]
    return "\n".join(lines)

def filter_products_by_stock(products, min_stock=3):
    """Check each product's inventory via Shopify and filter out low-stock items.

    Args:
        products: list of product dicts with 'url' field (Shopify product URL)
        min_stock: minimum required stock quantity to keep the product

    Returns:
        (kept_products, removed_products) — tuple of lists. Removed items get
        a 'reason' field explaining why.
    """
    if not SHOPIFY_TOKEN:
        print(f"  ⚠ No Shopify token — skipping stock check", file=sys.stderr)
        return products, []

    kept = []
    removed = []

    for p in products:
        url = p.get("url", "")
        # Extract handle from URL like https://onelife.co.za/collections/.../products/xyz-abc
        m = re.search(r"/products/([^/?#]+)", url)
        if not m:
            removed.append({**p, "reason": "no handle in URL"})
            continue
        handle = m.group(1)

        # Query Shopify for the product
        api_url = f"https://{SHOPIFY_STORE}/admin/api/{SHOPIFY_API_VERSION}/products.json?handle={handle}&fields=id,title,variants,status"
        req = urllib.request.Request(api_url, headers={
            "X-Shopify-Access-Token": SHOPIFY_TOKEN,
            "Accept": "application/json",
        })
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read())
            found = result.get("products", [])
        except urllib.error.HTTPError as e:
            removed.append({**p, "reason": f"shopify {e.code}"})
            continue

        if not found:
            removed.append({**p, "reason": "not found on Shopify"})
            continue

        prod = found[0]
        if prod.get("status") != "active":
            removed.append({**p, "reason": f"status: {prod.get('status')}"})
            continue

        variants = prod.get("variants", [])
        total_qty = sum((v.get("inventory_quantity", 0) or 0) for v in variants)

        if total_qty < min_stock:
            removed.append({**p, "reason": f"only {total_qty} in stock (need ≥{min_stock})"})
            continue

        # Enrich the product with the verified title (in case YAML is stale)
        p["_verified_title"] = prod.get("title")
        p["_verified_qty"] = total_qty
        kept.append(p)

    return kept, removed


def publish_to_klaviyo(fm, blog_url):
    campaign_slug = fm.get("slug", "blog-campaign")

    # ─── Stock verification ───
    # Filter out any products that are out of stock or below the minimum threshold.
    # MIN_STOCK_THRESHOLD env var (default 1) keeps out-of-stock products out
    # of email while preserving the curated article picks. A higher default
    # caused two-pick articles to send with one card when a valid secondary
    # product had only 1-2 online units available.
    min_stock = int(os.environ.get("MIN_STOCK_THRESHOLD", "1"))
    raw_products = fm.get("products", []) or []
    if raw_products:
        print(f"  → Stock check (min_stock={min_stock})...", file=sys.stderr)
        kept, removed = filter_products_by_stock(raw_products, min_stock=min_stock)
        for r in removed:
            print(f"  ⚠ REMOVED: {r.get('name','?')} — {r.get('reason','?')}", file=sys.stderr)
        for k in kept:
            qty = k.get("_verified_qty", "?")
            print(f"  ✓ KEPT: {k.get('name','?')} ({qty} in stock)", file=sys.stderr)
        fm["products"] = kept
        # Abort if no products survive
        if not kept:
            print(f"  ✗ No products in stock — aborting Klaviyo publish", file=sys.stderr)
            return None, None

    # Create template
    template_body = {
        "data": {
            "type": "template",
            "attributes": {
                "name": f"{fm.get('title','Blog')} — {datetime.now().strftime('%Y-%m-%d')}",
                "editor_type": "CODE",
                "html": render_email_html(fm, blog_url, campaign_slug),
                "text": render_email_text(fm, blog_url, campaign_slug),
            }
        }
    }
    tmpl = klaviyo_post("/templates/", template_body)
    if not tmpl:
        return None, None
    template_id = tmpl["data"]["id"]
    print(f"  ✓ Klaviyo template created: {template_id}", file=sys.stderr)

    # Create campaign
    send_offset = int(fm.get("send_offset_days", 2))
    send_at = (datetime.now(ZoneInfo("Africa/Johannesburg")) + timedelta(days=send_offset)).replace(
        hour=9, minute=0, second=0, microsecond=0
    )
    list_id = fm.get("campaign_segment", "S3MAsK")  # default: Engaged 90d, not full list (audit 2026-06-10)
    campaign_body = {
        "data": {
            "type": "campaign",
            "attributes": {
                "name": fm.get("title", "Blog Campaign"),
                "audiences": {"included": [list_id], "excluded": []},
                "send_strategy": {
                    "method": "static",
                    "options_static": {
                        "datetime": send_at.isoformat(),
                        "is_local": False,
                    }
                },
                "campaign-messages": {
                    "data": [{
                        "type": "campaign-message",
                        "attributes": {
                            "channel": "email",
                            "label": fm.get("title", "Blog Email"),
                            "content": {
                                "subject": fm.get("subject", fm.get("title", "New from Onelife")),
                                "preview_text": fm.get("preview", fm.get("excerpt", "")[:140]),
                                "from_email": "hello@onelife.co.za",
                                "from_label": "Precious at One Life Health",
                                "reply_to_email": "hello@onelife.co.za",
                            }
                        }
                    }]
                }
            }
        }
    }
    camp = klaviyo_post("/campaigns/", campaign_body)
    if not camp:
        return template_id, None
    campaign_id = camp["data"]["id"]
    msg_id = camp["data"]["relationships"]["campaign-messages"]["data"][0]["id"]
    print(f"  ✓ Klaviyo campaign created (draft): {campaign_id}", file=sys.stderr)

    # Assign template to message
    assign_body = {
        "data": {
            "type": "campaign-message",
            "id": msg_id,
            "relationships": {"template": {"data": {"type": "template", "id": template_id}}}
        }
    }
    result = klaviyo_post("/campaign-message-assign-template/", assign_body)
    if result:
        print(f"  ✓ Template assigned to campaign message", file=sys.stderr)

    # ─── Auto-schedule the campaign (move Draft → Scheduled) ───
    # Respects AUTO_SCHEDULE_CAMPAIGNS env var — defaults to "true" for autonomous pipeline.
    # Set to "false" if you want all future campaigns to require manual Klaviyo UI approval.
    auto_schedule = os.environ.get("AUTO_SCHEDULE_CAMPAIGNS", "true").lower() == "true"
    if auto_schedule:
        schedule_result = klaviyo_post("/campaign-send-jobs/", {
            "data": {"type": "campaign-send-job", "id": campaign_id}
        })
        if not schedule_result:
            time.sleep(10)
            print(f"  ⚠ Auto-schedule failed — retrying once...", file=sys.stderr)
            schedule_result = klaviyo_post("/campaign-send-jobs/", {
                "data": {"type": "campaign-send-job", "id": campaign_id}
            })
        if schedule_result:
            print(f"  ✓ Campaign scheduled (status: Scheduled)", file=sys.stderr)
        else:
            # A drafted campaign silently skips the send day (the 2026-06-30
            # Tuesday gap). Leave a marker so the workflow can raise an alert
            # without failing the job (the article itself IS published).
            print(f"  ⚠ Auto-schedule failed — campaign will stay as Draft", file=sys.stderr)
            print(f"::error::Klaviyo campaign {campaign_id} left in Draft — it will NOT send without manual scheduling", file=sys.stderr)
            with open(".campaign_draft_alert", "w") as f:
                f.write(campaign_id)
    else:
        print(f"  → Campaign left as Draft (AUTO_SCHEDULE_CAMPAIGNS=false)", file=sys.stderr)

    return template_id, campaign_id

# ─── Main ───
def main():
    if len(sys.argv) < 2:
        print("Usage: publish_blog.py <path/to/blog.md>", file=sys.stderr)
        sys.exit(1)
    blog_path = Path(sys.argv[1])
    if not blog_path.exists():
        print(f"ERROR: {blog_path} not found", file=sys.stderr)
        sys.exit(1)

    print(f"Publishing: {blog_path.name}", file=sys.stderr)
    md = blog_path.read_text()
    fm, body = parse(md)
    print(f"  Title: {fm.get('title')}", file=sys.stderr)
    print(f"  Slug:  {fm.get('slug')}", file=sys.stderr)

    # 1. Shopify
    print("[1/2] Publishing to Shopify...", file=sys.stderr)
    blog_url = publish_to_shopify(fm, body, fm.get("handle", "health-wellness-hub"))
    publish_live = os.environ.get("PUBLISH_LIVE", "").lower() == "true"
    if not blog_url:
        if publish_live:
            print("ERROR: live publish requested but Shopify article creation failed", file=sys.stderr)
            sys.exit(1)
        blog_url = f"https://onelife.co.za/blogs/{fm.get('handle','health-wellness-hub')}/{fm.get('slug','')}"
        print(f"  → Using fallback URL: {blog_url}", file=sys.stderr)

    # 2. Klaviyo
    print("[2/2] Creating Klaviyo template + campaign...", file=sys.stderr)
    template_id, campaign_id = publish_to_klaviyo(fm, blog_url)
    if publish_live and not campaign_id:
        print("ERROR: live publish requested but Klaviyo campaign creation/scheduling failed", file=sys.stderr)
        sys.exit(1)

    print(file=sys.stderr)
    print("═" * 60, file=sys.stderr)
    print("PUBLISHED", file=sys.stderr)
    print(f"  Blog URL:    {blog_url}", file=sys.stderr)
    print(f"  Template:    {template_id}", file=sys.stderr)
    print(f"  Campaign:    {campaign_id}", file=sys.stderr)
    print(f"  Status:      {'Scheduled' if campaign_id else 'Draft / incomplete'}", file=sys.stderr)
    print("═" * 60, file=sys.stderr)

    print(json.dumps({
        "blog_url": blog_url,
        "template_id": template_id,
        "campaign_id": campaign_id,
    }))

if __name__ == "__main__":
    main()
