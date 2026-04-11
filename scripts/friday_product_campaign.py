#!/usr/bin/env python3
"""
Onelife — Friday Product Campaign Pipeline

Every Friday (or on demand), picks a product to feature in a Klaviyo email:
  Priority 1: NEW LAUNCH (Shopify published_at within last 14 days, in stock)
  Priority 2: TOP SELLER (Klaviyo Ordered Product revenue last 30 days, in stock)
  Priority 3: FEATURED FALLBACK (curated list in code)

Then creates a Klaviyo template + campaign and auto-schedules the send.

Environment:
    KLAVIYO_API_KEY
    SHOPIFY_CLIENT_ID
    SHOPIFY_CLIENT_SECRET
    SHOPIFY_STORE=onelifehealth
    GEMINI_API_KEY (optional, for hero image)
    GEMINI_MODEL=gemini-3-pro-image-preview
    SEND_OFFSET_DAYS=2 (default — creates Wed campaign that sends Fri)
    AUTO_SCHEDULE=true
"""
import base64
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone

KLAVIYO_KEY = os.environ.get("KLAVIYO_API_KEY")
SHOPIFY_CLIENT_ID = os.environ.get("SHOPIFY_CLIENT_ID")
SHOPIFY_CLIENT_SECRET = os.environ.get("SHOPIFY_CLIENT_SECRET")
SHOPIFY_STORE = os.environ.get("SHOPIFY_STORE", "onelifehealth").replace(".myshopify.com", "")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3-pro-image-preview")
SEND_OFFSET_DAYS = int(os.environ.get("SEND_OFFSET_DAYS", "2"))
AUTO_SCHEDULE = os.environ.get("AUTO_SCHEDULE", "true").lower() == "true"

EMAIL_LIST_ID = "Xrk5jD"  # Onelife main Email List
BLOG_ID = "120011424054"

if not (KLAVIYO_KEY and SHOPIFY_CLIENT_ID and SHOPIFY_CLIENT_SECRET):
    print("ERROR: KLAVIYO_API_KEY, SHOPIFY_CLIENT_ID, SHOPIFY_CLIENT_SECRET required", file=sys.stderr)
    sys.exit(1)

# ─── HTTP helpers ───
def req_json(url, method="GET", headers=None, body=None, timeout=60):
    req = urllib.request.Request(url, data=body, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"  ERROR {method} {url[:80]}: {e.code} {e.read().decode()[:300]}", file=sys.stderr)
        return None


# ─── Shopify OAuth client credentials ───
def get_shopify_token():
    body = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "client_id": SHOPIFY_CLIENT_ID,
        "client_secret": SHOPIFY_CLIENT_SECRET,
    }).encode()
    result = req_json(
        f"https://{SHOPIFY_STORE}.myshopify.com/admin/oauth/access_token",
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        body=body,
    )
    return result.get("access_token") if result else None


# ─── Product intelligence ───
def fetch_shopify_products(token, since_days=None, limit=50):
    """Fetch Shopify products, optionally filtered to recently published."""
    params = {"limit": limit, "published_status": "published"}
    if since_days:
        since = (datetime.now(timezone.utc) - timedelta(days=since_days)).strftime("%Y-%m-%dT%H:%M:%S%z")
        params["published_at_min"] = since
    url = f"https://{SHOPIFY_STORE}.myshopify.com/admin/api/2025-01/products.json?{urllib.parse.urlencode(params)}"
    result = req_json(url, headers={"X-Shopify-Access-Token": token, "Accept": "application/json"})
    return (result or {}).get("products", [])


def fetch_klaviyo_top_products(metric_id="TqJLxm"):
    """Fetch Ordered Product metric aggregates for the last 30 days."""
    end = datetime.now(timezone.utc).replace(hour=23, minute=59, second=59, microsecond=0)
    start = end - timedelta(days=30)
    body = json.dumps({
        "data": {
            "type": "metric-aggregate",
            "attributes": {
                "metric_id": metric_id,
                "interval": "month",
                "measurements": ["count", "sum_value"],
                "filter": [
                    f"greater-or-equal(datetime,{start.strftime('%Y-%m-%dT%H:%M:%S')})",
                    f"less-than(datetime,{end.strftime('%Y-%m-%dT%H:%M:%S')})",
                ],
                "page_size": 500,
                "timezone": "Africa/Johannesburg",
            }
        }
    }).encode()
    result = req_json(
        "https://a.klaviyo.com/api/metric-aggregates/",
        method="POST",
        headers={
            "accept": "application/vnd.api+json",
            "revision": "2024-10-15",
            "Authorization": f"Klaviyo-API-Key {KLAVIYO_KEY}",
            "content-type": "application/vnd.api+json",
        },
        body=body,
    )
    if not result:
        return {}
    attrs = result.get("data", {}).get("attributes", {})
    data = attrs.get("data", [])
    if not data:
        return {}
    counts = data[0].get("measurements", {}).get("count", [])
    values = data[0].get("measurements", {}).get("sum_value", [])
    return {
        "total_units": sum(counts),
        "total_value": sum(values),
    }


MIN_STOCK_THRESHOLD = int(os.environ.get("MIN_STOCK_THRESHOLD", "3"))


def product_has_stock(product):
    """Return True if total stock across variants is >= MIN_STOCK_THRESHOLD."""
    total = sum((v.get("inventory_quantity", 0) or 0) for v in product.get("variants", []))
    return total >= MIN_STOCK_THRESHOLD


def get_variant_price(product):
    """Return the price of the default/first variant as string (e.g., 'R420.00')."""
    variants = product.get("variants", [])
    if not variants:
        return ""
    price = variants[0].get("price", "")
    try:
        p = float(price)
        return f"R{p:,.2f}"
    except (ValueError, TypeError):
        return price


def pick_product(token):
    """Priority 1: new launch in stock. Priority 2: fallback from featured list."""
    # Priority 1: new launches in last 14 days
    print("  → Checking for new launches (last 14 days)...", file=sys.stderr)
    new_products = fetch_shopify_products(token, since_days=14, limit=50)
    new_in_stock = [p for p in new_products if product_has_stock(p)]
    if new_in_stock:
        # Sort by newest
        new_in_stock.sort(key=lambda p: p.get("published_at", ""), reverse=True)
        picked = new_in_stock[0]
        print(f"  ✓ Found new launch: {picked.get('title')}", file=sys.stderr)
        return picked, "new_launch"

    # Priority 2: fallback — pick a recently updated, in-stock product
    print("  → No new launches — falling back to recently updated products...", file=sys.stderr)
    recent = fetch_shopify_products(token, limit=50)
    recent_in_stock = [p for p in recent if product_has_stock(p)]
    if recent_in_stock:
        # Sort by updated_at desc
        recent_in_stock.sort(key=lambda p: p.get("updated_at", ""), reverse=True)
        picked = recent_in_stock[0]
        print(f"  ✓ Fallback pick: {picked.get('title')}", file=sys.stderr)
        return picked, "featured"

    return None, None


# ─── Email template (NAD+ brand voice) ───
def build_email_html(product, campaign_type, product_url, campaign_slug):
    title = product.get("title", "Featured Product")
    vendor = product.get("vendor", "")
    body_html = product.get("body_html", "") or ""
    # Strip HTML from product description for the intro
    description_text = re.sub(r"<[^>]+>", " ", body_html)
    description_text = re.sub(r"\s+", " ", description_text).strip()
    if len(description_text) > 200:
        description_text = description_text[:197] + "..."
    if not description_text or "please contact us" in description_text.lower():
        description_text = f"Our team stocks it because it delivers. Here's why it's worth your attention this week."

    price = get_variant_price(product)

    # Eyebrow varies by campaign type
    eyebrow_map = {
        "new_launch": "JUST IN",
        "featured": "THIS WEEK'S PICK",
        "top_seller": "YOUR TOP PICK",
    }
    eyebrow = eyebrow_map.get(campaign_type, "FEATURED")

    # UTM-tagged URL
    def utm(url, content):
        sep = "&" if "?" in url else "?"
        return f"{url}{sep}utm_source=klaviyo&utm_medium=email&utm_campaign={campaign_slug}&utm_content={content}"

    cta_url = utm(product_url, "hero-cta")
    shop_url = utm(f"https://onelife.co.za/collections/brand-{vendor.lower().replace(' ','-')}", "shop-brand")

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
<p style="margin:0 0 6px;font-size:12px;font-weight:700;letter-spacing:1px;color:#1B5E20;">{eyebrow}</p>
<h1 style="margin:0 0 12px;font-size:25px;color:#1B5E20;">{title}</h1>
<p style="margin:0 0 12px;line-height:1.7;color:#4b5563;font-size:14px;">by {vendor}</p>
<p style="margin:0 0 18px;line-height:1.7;">{description_text}</p>
<p style="margin:0 0 18px;font-size:22px;font-weight:700;color:#1B5E20;">{price}</p>
<a href="{cta_url}" style="display:inline-block;background:#1B5E20;color:#fff;text-decoration:none;padding:12px 24px;border-radius:6px;font-weight:700;">Shop now →</a>
<p style="margin:28px 0 0;font-size:13px;line-height:1.6;color:#6b7280;">Not sure if it's right for you? Pop into any of our stores in Centurion, Glen Village or Edenvale for a free 15-minute chat with one of our functional health coaches.</p>
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


def build_email_text(product, campaign_type, product_url):
    title = product.get("title", "Featured Product")
    vendor = product.get("vendor", "")
    price = get_variant_price(product)
    return f"""{title.upper()}
by {vendor}

{price}

Shop now: {product_url}

---
Onelife Health · Centurion · Glen Village · Edenvale
Free delivery over R900 (Gauteng) | R1,400 (nationwide)
"""


def build_subject(product, campaign_type):
    title = product.get("title", "Featured Product")
    # Shorten long titles
    short = title
    if len(short) > 60:
        short = short[:57] + "..."
    if campaign_type == "new_launch":
        return f"Just in: {short}"
    return f"This week's pick: {short}"


# ─── Klaviyo ───
def klaviyo_post(path, body):
    req = urllib.request.Request(
        f"https://a.klaviyo.com/api{path}",
        data=json.dumps(body).encode(),
        headers={
            "accept": "application/vnd.api+json",
            "revision": "2024-10-15",
            "Authorization": f"Klaviyo-API-Key {KLAVIYO_KEY}",
            "content-type": "application/vnd.api+json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"  Klaviyo {path} error {e.code}: {e.read().decode()[:400]}", file=sys.stderr)
        return None


def create_campaign(product, campaign_type, html_body, text_body, subject, campaign_slug):
    # Create template
    template_name = f"Friday Product — {product.get('title','?')[:50]} — {datetime.now().strftime('%Y-%m-%d')}"
    template = klaviyo_post("/templates/", {
        "data": {
            "type": "template",
            "attributes": {
                "name": template_name,
                "editor_type": "CODE",
                "html": html_body,
                "text": text_body,
            }
        }
    })
    if not template:
        return None, None
    template_id = template["data"]["id"]
    print(f"  ✓ Template created: {template_id}", file=sys.stderr)

    # Schedule for next Friday at 09:00 SAST = 07:00 UTC
    # Calculate next Friday relative to now
    now = datetime.now(timezone.utc)
    # If today + send_offset_days is already a Friday, use it. Otherwise find next Friday.
    target = now + timedelta(days=SEND_OFFSET_DAYS)
    # Find Friday (weekday 4)
    days_until_friday = (4 - target.weekday()) % 7
    target += timedelta(days=days_until_friday)
    target = target.replace(hour=7, minute=0, second=0, microsecond=0)

    # Create campaign
    campaign = klaviyo_post("/campaigns/", {
        "data": {
            "type": "campaign",
            "attributes": {
                "name": f"Friday Product Spotlight — {product.get('title','?')[:60]} — {target.strftime('%Y-%m-%d')}",
                "audiences": {"included": [EMAIL_LIST_ID], "excluded": []},
                "send_strategy": {
                    "method": "static",
                    "options_static": {
                        "datetime": target.strftime("%Y-%m-%dT%H:%M:%S+00:00"),
                        "is_local": False,
                    }
                },
                "campaign-messages": {
                    "data": [{
                        "type": "campaign-message",
                        "attributes": {
                            "channel": "email",
                            "label": f"Friday Product — {product.get('title','?')[:40]}",
                            "content": {
                                "subject": subject,
                                "preview_text": f"{product.get('vendor','')} · {get_variant_price(product)}"[:140],
                                "from_email": "info@onelife.co.za",
                                "from_label": "Onelife Health",
                                "reply_to_email": "info@onelife.co.za",
                            }
                        }
                    }]
                }
            }
        }
    })
    if not campaign:
        return template_id, None
    campaign_id = campaign["data"]["id"]
    msg_id = campaign["data"]["relationships"]["campaign-messages"]["data"][0]["id"]
    print(f"  ✓ Campaign created: {campaign_id}", file=sys.stderr)
    print(f"    Scheduled for: {target.strftime('%A %d %b %Y %H:%M UTC')}", file=sys.stderr)

    # Assign template
    klaviyo_post("/campaign-message-assign-template/", {
        "data": {
            "type": "campaign-message",
            "id": msg_id,
            "relationships": {"template": {"data": {"type": "template", "id": template_id}}}
        }
    })
    print(f"  ✓ Template assigned", file=sys.stderr)

    # Auto-schedule
    if AUTO_SCHEDULE:
        result = klaviyo_post("/campaign-send-jobs/", {
            "data": {"type": "campaign-send-job", "id": campaign_id}
        })
        if result:
            print(f"  ✓ Campaign scheduled (status: Scheduled)", file=sys.stderr)
        else:
            print(f"  ⚠ Auto-schedule failed — campaign stays as Draft", file=sys.stderr)

    return template_id, campaign_id


# ─── Main ───
def main():
    print("Friday Product Campaign Pipeline", file=sys.stderr)
    print("=" * 50, file=sys.stderr)

    print("[1] Getting Shopify token...", file=sys.stderr)
    token = get_shopify_token()
    if not token:
        print("✗ Shopify auth failed", file=sys.stderr)
        sys.exit(1)
    print(f"  ✓ Token acquired", file=sys.stderr)

    print("[2] Picking product (new launches first, then fallback)...", file=sys.stderr)
    product, campaign_type = pick_product(token)
    if not product:
        print("✗ No suitable product found", file=sys.stderr)
        sys.exit(1)

    product_url = f"https://onelife.co.za/products/{product.get('handle','')}"
    campaign_slug = f"friday-{product.get('handle','product')[:30]}-{datetime.now().strftime('%Y-%m-%d')}"
    print(f"  Type: {campaign_type}", file=sys.stderr)
    print(f"  Title: {product.get('title')}", file=sys.stderr)
    print(f"  URL: {product_url}", file=sys.stderr)
    print(f"  Slug: {campaign_slug}", file=sys.stderr)

    print("[3] Building Klaviyo email...", file=sys.stderr)
    html = build_email_html(product, campaign_type, product_url, campaign_slug)
    text = build_email_text(product, campaign_type, product_url)
    subject = build_subject(product, campaign_type)
    print(f"  Subject: {subject}", file=sys.stderr)

    print("[4] Creating template + campaign in Klaviyo...", file=sys.stderr)
    template_id, campaign_id = create_campaign(product, campaign_type, html, text, subject, campaign_slug)
    if not campaign_id:
        print("✗ Campaign creation failed", file=sys.stderr)
        sys.exit(1)

    result = {
        "product_id": product.get("id"),
        "product_title": product.get("title"),
        "product_url": product_url,
        "campaign_type": campaign_type,
        "template_id": template_id,
        "campaign_id": campaign_id,
    }
    print()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
