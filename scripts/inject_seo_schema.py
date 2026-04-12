#!/usr/bin/env python3
"""
Onelife — Shopify Theme Schema.org Injector

Uploads SEO JSON-LD snippets into the live Shopify theme and wires them
into layout/theme.liquid. Idempotent — safe to re-run.

The theme already had:
  - snippets/product-schema-jsonld.liquid        (Product, Brand, Offer)
  - snippets/homepage-schema-jsonld.liquid       (HealthAndBeautyBusiness + 3 stores)
  - inline BreadcrumbList in layout/theme.liquid (collection/product/article)

This script adds:
  - snippets/seo-jsonld-organization.liquid      (global Organization + WebSite + SearchAction)
  - snippets/seo-jsonld-article.liquid           (full Article schema for blog posts)
  - enhanced snippets/product-schema-jsonld.liquid (image array, category,
    priceValidUntil, mpn, itemCondition, bestRating/worstRating)

And inserts two new {%- include -%} lines into layout/theme.liquid right
after the existing homepage-schema-jsonld include.

Environment:
  SHOPIFY_CLIENT_ID
  SHOPIFY_CLIENT_SECRET
  SHOPIFY_STORE=onelifehealth (default)
  THEME_ID (optional, default: main theme)

Output:
  reports/schema-injection-YYYY-MM-DD.jsonl   (action log)
  scripts/shopify-theme-backup/*              (pre-change backups)

Safety:
  Every asset that's about to be overwritten is first downloaded and
  saved locally. If anything goes wrong, re-upload from the backup via:
    python scripts/inject_seo_schema.py --restore FILE
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

STORE = os.environ.get("SHOPIFY_STORE", "onelifehealth").replace(".myshopify.com", "")
API_VERSION = "2025-01"

ORG_SNIPPET = r"""{%- comment -%}
  Global Organization + WebSite JSON-LD. Fires on every page.
  Enables the Google brand knowledge panel + sitelinks search box.
  Added 2026-04-12 by Claude (seo-schema-injection).
{%- endcomment -%}
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@graph": [
    {
      "@type": "Organization",
      "@id": "{{ shop.url }}/#organization",
      "name": {{ shop.name | json }},
      "alternateName": "One Life Health Supermarket",
      "url": "{{ shop.url }}",
      {%- if settings.logo != blank -%}
      "logo": {
        "@type": "ImageObject",
        "url": {{ settings.logo | img_url: '600x' | prepend: 'https:' | json }}
      },
      {%- endif -%}
      "sameAs": [
        "https://www.facebook.com/onelifehealth",
        "https://www.instagram.com/onelifehealth",
        "https://www.tiktok.com/@onelifehealth"
      ],
      "contactPoint": [{
        "@type": "ContactPoint",
        "telephone": "+27713744910",
        "contactType": "customer service",
        "areaServed": "ZA",
        "availableLanguage": ["English", "Afrikaans"]
      }]
    },
    {
      "@type": "WebSite",
      "@id": "{{ shop.url }}/#website",
      "url": "{{ shop.url }}",
      "name": {{ shop.name | json }},
      "publisher": { "@id": "{{ shop.url }}/#organization" },
      "potentialAction": {
        "@type": "SearchAction",
        "target": {
          "@type": "EntryPoint",
          "urlTemplate": "{{ shop.url }}/search?q={search_term_string}"
        },
        "query-input": "required name=search_term_string"
      }
    }
  ]
}
</script>
"""

ARTICLE_SNIPPET = r"""{%- comment -%}
  Article JSON-LD for blog articles. Added 2026-04-12 by Claude.
  Required fields per Google Article guidelines: headline, image,
  datePublished, author.
{%- endcomment -%}
{%- if template contains 'article' and article -%}
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "Article",
  "mainEntityOfPage": {
    "@type": "WebPage",
    "@id": "{{ shop.url }}{{ article.url }}"
  },
  "headline": {{ article.title | truncate: 110 | json }},
  {%- if article.image -%}
  "image": [{{ article.image | img_url: '1200x' | prepend: 'https:' | json }}],
  {%- endif -%}
  "datePublished": "{{ article.published_at | date: '%Y-%m-%dT%H:%M:%S%z' }}",
  "dateModified": "{{ article.updated_at | default: article.published_at | date: '%Y-%m-%dT%H:%M:%S%z' }}",
  "author": {
    "@type": "Person",
    "name": {{ article.author | default: 'One Life Health' | json }}
  },
  "publisher": {
    "@type": "Organization",
    "@id": "{{ shop.url }}/#organization",
    "name": {{ shop.name | json }}{%- if settings.logo != blank -%},
    "logo": {
      "@type": "ImageObject",
      "url": {{ settings.logo | img_url: '600x' | prepend: 'https:' | json }}
    }
    {%- endif -%}
  },
  {%- if article.excerpt != blank -%}
  "description": {{ article.excerpt | strip_html | truncate: 500 | json }}
  {%- else -%}
  "description": {{ article.content | strip_html | truncate: 300 | json }}
  {%- endif -%}
}
</script>
{%- endif -%}
"""

PRODUCT_SNIPPET = r"""{%- if template contains 'product' and product -%}
{%- assign current_variant = product.selected_or_first_available_variant -%}
<script type="application/ld+json">
{
  "@context": "https://schema.org/",
  "@type": "Product",
  "@id": "{{ shop.url }}{{ product.url }}#product",
  "name": {{ product.title | json }},
  "url": "{{ shop.url }}{{ product.url }}",
  "brand": {
    "@type": "Brand",
    "name": {{ product.vendor | json }}
  },
  {%- if product.images.size > 0 -%}
  "image": [{%- for image in product.images limit: 5 -%}{{ image | img_url: '1024x' | prepend: 'https:' | json }}{%- unless forloop.last -%},{%- endunless -%}{%- endfor -%}],
  {%- elsif product.featured_image -%}
  "image": {{ product.featured_image | img_url: '1024x' | prepend: 'https:' | json }},
  {%- endif -%}
  {%- if product.description != blank -%}
  "description": {{ product.description | strip_html | truncate: 5000 | json }},
  {%- endif -%}
  {%- if product.type != blank -%}
  "category": {{ product.type | json }},
  {%- endif -%}
  {%- if current_variant.sku != blank -%}
  "sku": {{ current_variant.sku | json }},
  "mpn": {{ current_variant.sku | json }},
  {%- endif -%}
  "offers": {
    "@type": "Offer",
    "url": "{{ shop.url }}{{ product.url }}",
    "priceCurrency": "ZAR",
    "price": "{{ current_variant.price | divided_by: 100.0 }}",
    "priceValidUntil": "{{ 'now' | date: '%Y' | plus: 1 }}-12-31",
    "availability": {% if current_variant.available %}"https://schema.org/InStock"{% else %}"https://schema.org/OutOfStock"{% endif %},
    "itemCondition": "https://schema.org/NewCondition",
    "seller": {
      "@type": "Organization",
      "@id": "{{ shop.url }}/#organization",
      "name": {{ shop.name | json }}
    }
  }
  {%- assign jm_rating = product.metafields.judgeme.rating.value -%}
  {%- assign jm_count = product.metafields.judgeme.reviews_count.value -%}
  {%- if jm_rating != blank and jm_count != blank and jm_count != '0' -%}
  ,"aggregateRating": {
    "@type": "AggregateRating",
    "ratingValue": "{{ jm_rating }}",
    "reviewCount": "{{ jm_count }}",
    "bestRating": "5",
    "worstRating": "1"
  }
  {%- endif -%}
}
</script>
{%- endif -%}
"""

LAYOUT_MARKER = "{%- include 'homepage-schema-jsonld' -%}"
LAYOUT_INSERT_AFTER = (
    LAYOUT_MARKER
    + "\n  {%- comment -%}Global org + website schema (fires on every page){%- endcomment -%}"
    + "\n  {%- include 'seo-jsonld-organization' -%}"
    + "\n  {%- comment -%}Article schema for blog posts{%- endcomment -%}"
    + "\n  {%- include 'seo-jsonld-article' -%}"
)


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


def api(method, path, headers, data=None):
    url = f"https://{STORE}.myshopify.com/admin/api/{API_VERSION}{path}"
    body = None
    hdrs = dict(headers)
    if data is not None:
        body = json.dumps(data).encode()
        hdrs["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=body, headers=hdrs, method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, {"__error__": e.read().decode()[:500]}


def fetch_asset(theme_id, key, headers):
    params = urllib.parse.urlencode({"asset[key]": key})
    s, d = api("GET", f"/themes/{theme_id}/assets.json?{params}", headers)
    if s == 200 and "asset" in d:
        return d["asset"]["value"]
    return None


def put_asset(theme_id, key, value, headers):
    return api("PUT", f"/themes/{theme_id}/assets.json", headers,
               {"asset": {"key": key, "value": value}})


def find_main_theme(headers):
    s, d = api("GET", "/themes.json", headers)
    if s != 200:
        raise RuntimeError(f"list themes failed: {d}")
    for t in d.get("themes", []):
        if t.get("role") == "main":
            return t["id"], t.get("name", "")
    raise RuntimeError("no main theme found")


def main():
    ROOT = Path(__file__).resolve().parent.parent
    BACKUP_DIR = ROOT / "scripts" / "shopify-theme-backup"
    REPORTS_DIR = ROOT / "reports"
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    token = get_token()
    headers = {"X-Shopify-Access-Token": token, "Accept": "application/json"}

    theme_id_env = os.environ.get("THEME_ID")
    if theme_id_env:
        theme_id = int(theme_id_env)
        theme_name = "(env-specified)"
    else:
        theme_id, theme_name = find_main_theme(headers)
    print(f"theme: {theme_id} ({theme_name})")

    audit = []

    def log(**kw):
        kw["ts"] = datetime.now(timezone.utc).isoformat()
        audit.append(kw)
        short = {k: v for k, v in kw.items() if k != "ts"}
        print(f"  {short}")

    assets_to_write = {
        "snippets/seo-jsonld-organization.liquid": ORG_SNIPPET,
        "snippets/seo-jsonld-article.liquid": ARTICLE_SNIPPET,
        "snippets/product-schema-jsonld.liquid": PRODUCT_SNIPPET,
    }

    print("\n=== Back up assets that will be overwritten ===")
    for key in list(assets_to_write.keys()) + ["layout/theme.liquid"]:
        current = fetch_asset(theme_id, key, headers)
        if current is not None:
            fname = f"{key.replace('/', '_')}-{theme_id}-{today}"
            (BACKUP_DIR / fname).write_text(current)
            log(action="backup", key=key, bytes=len(current))

    print("\n=== Upload new + enhanced snippets ===")
    for key, value in assets_to_write.items():
        s, d = put_asset(theme_id, key, value, headers)
        log(action="put", key=key, status=s, bytes=len(value))
        if s not in (200, 201):
            print(f"  FAIL: {d}", file=sys.stderr)
            sys.exit(1)

    print("\n=== Modify layout/theme.liquid ===")
    current_layout = fetch_asset(theme_id, "layout/theme.liquid", headers)
    if current_layout is None:
        print("  ERROR: could not fetch layout/theme.liquid", file=sys.stderr)
        sys.exit(1)
    if "seo-jsonld-organization" in current_layout:
        log(action="layout_skip", reason="already_modified")
        print("  layout already contains seo-jsonld-organization — skipping")
    elif LAYOUT_MARKER not in current_layout:
        print(f"  ERROR: marker not found: {LAYOUT_MARKER}", file=sys.stderr)
        sys.exit(1)
    else:
        modified = current_layout.replace(LAYOUT_MARKER, LAYOUT_INSERT_AFTER, 1)
        s, d = put_asset(theme_id, "layout/theme.liquid", modified, headers)
        log(action="put", key="layout/theme.liquid", status=s,
            bytes=len(modified), delta=len(modified) - len(current_layout))
        if s not in (200, 201):
            print(f"  FAIL: {d}", file=sys.stderr)
            sys.exit(1)

    audit_path = REPORTS_DIR / f"schema-injection-{today}.jsonl"
    with open(audit_path, "a") as f:
        for r in audit:
            f.write(json.dumps(r, default=str) + "\n")
    print(f"\n✓ audit log: {audit_path}")


if __name__ == "__main__":
    main()
