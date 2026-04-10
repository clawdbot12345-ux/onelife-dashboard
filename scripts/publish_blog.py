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
import urllib.request
import urllib.parse
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ─── Config ───
KLAVIYO_KEY = os.environ.get("KLAVIYO_API_KEY")
SHOPIFY_TOKEN = os.environ.get("SHOPIFY_ADMIN_TOKEN")
SHOPIFY_STORE = os.environ.get("SHOPIFY_STORE", "onelifehealth.myshopify.com")
SHOPIFY_API_VERSION = "2025-01"

if not KLAVIYO_KEY:
    print("ERROR: KLAVIYO_API_KEY not set", file=sys.stderr)
    sys.exit(1)

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
                current_obj[k.strip()] = v.strip()
        elif line.startswith('    '):
            kv = line[4:]
            if ':' in kv and current_obj is not None:
                k, _, v = kv.partition(':')
                current_obj[k.strip()] = v.strip()
        elif ':' in line and not line.startswith(' '):
            k, _, v = line.partition(':')
            k = k.strip()
            v = v.strip()
            if not v:
                current_key = k
                current_list = None
                fm[k] = None
            else:
                fm[k] = v
                current_key = None
                current_list = None
    return fm, body

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
def md_to_html(md_body):
    """Minimal markdown to HTML converter — headings, bold, paragraphs, lists, links."""
    html_out = []
    lines = md_body.split('\n')
    in_list = False
    for line in lines:
        # Headings
        if line.startswith('### '):
            if in_list: html_out.append('</ul>'); in_list = False
            html_out.append(f'<h3>{line[4:].strip()}</h3>')
        elif line.startswith('## '):
            if in_list: html_out.append('</ul>'); in_list = False
            html_out.append(f'<h2>{line[3:].strip()}</h2>')
        elif line.startswith('# '):
            if in_list: html_out.append('</ul>'); in_list = False
            html_out.append(f'<h1>{line[2:].strip()}</h1>')
        elif line.startswith('- ') or line.startswith('* '):
            if not in_list: html_out.append('<ul>'); in_list = True
            item = line[2:].strip()
            item = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', item)
            item = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', item)
            html_out.append(f'<li>{item}</li>')
        elif line.strip() == '---':
            if in_list: html_out.append('</ul>'); in_list = False
            html_out.append('<hr>')
        elif not line.strip():
            if in_list: html_out.append('</ul>'); in_list = False
            continue
        else:
            if in_list: html_out.append('</ul>'); in_list = False
            para = line
            para = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', para)
            para = re.sub(r'\*(.+?)\*', r'<em>\1</em>', para)
            para = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2">\1</a>', para)
            html_out.append(f'<p>{para}</p>')
    if in_list:
        html_out.append('</ul>')
    return '\n'.join(html_out)

# ─── Shopify: publish blog article ───
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
            "author": fm.get("author", "Onelife Health"),
            "body_html": md_to_html(body_md),
            "handle": fm.get("slug"),
            "summary_html": fm.get("excerpt", ""),
            "tags": fm.get("tags", "wellness,supplements,evidence-based"),
            "published": False,  # draft first for safety
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
    """Build email HTML matching Onelife's actual brand voice (NAD+ template style).

    Style reference: the winning NAD+ campaign (R1,770 revenue) uses:
    - Dark green #1B5E20 header with Onelife logo
    - White content card
    - Short H1 in dark green
    - 2 short paragraphs of intro
    - Green CTA button "Read the full guide →"
    - Simple product list (no badges, no prices — just bold name + description)
    - "Shop [category]" catch-all link
    - Green footer with stores + delivery info
    """
    products = fm.get("products", []) or []
    products_html = ""
    for i, p in enumerate(products):
        prod_url = utm_url(p.get("url", "#"), campaign_slug, f"product-{i+1}")
        is_last = i == len(products) - 1
        border = "" if is_last else "border-bottom:1px solid #e5e7eb;"
        products_html += f'''
<tr><td style="padding:14px 0;{border}"><a href="{prod_url}" style="color:#1B5E20;text-decoration:none;font-weight:700;">{p.get('name','')}</a><br/><span style="color:#4b5563;">{p.get('blurb','')}</span></td></tr>'''

    blog_cta = utm_url(blog_url, campaign_slug, "blog-cta")
    shop_collection_url = fm.get("shop_collection_url", "https://onelife.co.za/collections/all")
    shop_cta = utm_url(shop_collection_url, campaign_slug, "shop-collection")
    shop_label = fm.get("shop_label", "Shop all supplements")
    category_heading = fm.get("category_heading", "Top picks")
    intro_p1 = fm.get("intro_p1", fm.get("excerpt", ""))
    intro_p2 = fm.get("intro_p2", "")

    return f'''<!DOCTYPE html>
<html>
<head><meta charset="utf-8"/><meta content="width=device-width, initial-scale=1" name="viewport"/></head>
<body style="margin:0;padding:0;background:#f3f7f3;font-family:Arial,sans-serif;color:#1f2937;">
<table cellpadding="0" cellspacing="0" role="presentation" style="background:#f3f7f3;padding:24px 0;" width="100%">
<tr><td align="center">
<table cellpadding="0" cellspacing="0" role="presentation" style="max-width:600px;background:#ffffff;border-radius:8px;overflow:hidden;" width="600">
<tr><td style="background:#1B5E20;padding:18px 24px;text-align:center;">
  <img alt="Onelife Health" src="https://onelife.co.za/cdn/shop/files/OneLife_LOGO_51277c55-2099-4f3a-a659-ef42cdcac5d9.png?v=1671450106" style="display:inline-block;max-width:180px;height:auto;" width="180"/>
</td></tr>
<tr><td style="padding:24px;">
<p style="margin:0 0 10px;color:#4b5563;font-size:14px;">Preview text: {fm.get('preview','')}</p>
<h1 style="margin:0 0 12px;font-size:25px;color:#1B5E20;">{fm.get('title','')}</h1>
<p style="margin:0 0 12px;line-height:1.7;">{intro_p1}</p>
{f'<p style="margin:0 0 18px;line-height:1.7;">{intro_p2}</p>' if intro_p2 else ''}
<a href="{blog_cta}" style="display:inline-block;background:#1B5E20;color:#fff;text-decoration:none;padding:12px 20px;border-radius:6px;font-weight:700;">Read the full guide →</a>
<h2 style="margin:28px 0 12px;font-size:20px;color:#1B5E20;">{category_heading}</h2>
<table cellpadding="0" cellspacing="0" role="presentation" style="border-top:1px solid #e5e7eb;" width="100%">{products_html}
</table>
<p style="margin:18px 0 0;"><a href="{shop_cta}" style="color:#1B5E20;font-weight:700;text-decoration:none;">{shop_label}</a></p>
</td></tr>
<tr><td style="padding:18px 24px;background:#f9fafb;color:#6b7280;font-size:12px;line-height:1.6;">
Onelife Health stores: Centurion | Glen Village, Faerie Glen | Edenvale<br/>
Free delivery over R900 (Gauteng) | R1,400 (nationwide)<br/>
<a href="{{{{ unsubscribe }}}}" style="color:#6b7280;">Unsubscribe</a>
</td></tr>
</table>
</td></tr>
</table>
</body>
</html>'''

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

def publish_to_klaviyo(fm, blog_url):
    campaign_slug = fm.get("slug", "blog-campaign")

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
    list_id = fm.get("campaign_segment", "Xrk5jD")
    campaign_body = {
        "data": {
            "type": "campaign",
            "attributes": {
                "name": fm.get("title", "Blog Campaign"),
                "audiences": {"included": [list_id], "excluded": []},
                "send_strategy": {
                    "method": "static",
                    "options_static": {
                        "datetime": (datetime.now(timezone.utc) + timedelta(days=send_offset)).strftime("%Y-%m-%dT09:00:00+00:00"),
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
                                "from_email": "info@onelife.co.za",
                                "from_label": "Onelife Health",
                                "reply_to_email": "info@onelife.co.za",
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
    if not blog_url:
        blog_url = f"https://onelife.co.za/blogs/{fm.get('handle','health-wellness-hub')}/{fm.get('slug','')}"
        print(f"  → Using fallback URL: {blog_url}", file=sys.stderr)

    # 2. Klaviyo
    print("[2/2] Creating Klaviyo template + campaign...", file=sys.stderr)
    template_id, campaign_id = publish_to_klaviyo(fm, blog_url)

    print(file=sys.stderr)
    print("═" * 60, file=sys.stderr)
    print("PUBLISHED", file=sys.stderr)
    print(f"  Blog URL:    {blog_url}", file=sys.stderr)
    print(f"  Template:    {template_id}", file=sys.stderr)
    print(f"  Campaign:    {campaign_id}", file=sys.stderr)
    print(f"  Status:      Draft (review + send in Klaviyo)", file=sys.stderr)
    print("═" * 60, file=sys.stderr)

    print(json.dumps({
        "blog_url": blog_url,
        "template_id": template_id,
        "campaign_id": campaign_id,
    }))

if __name__ == "__main__":
    main()
