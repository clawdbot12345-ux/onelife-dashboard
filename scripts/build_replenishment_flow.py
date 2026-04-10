#!/usr/bin/env python3
"""
Build the Replenishment Reminder flow assets in Klaviyo.

Creates 3 email templates (30/60/90 day reminders) and leaves them as drafts
in your Klaviyo account. Then prints the exact UI steps to wire them into
a Placed Order time-delay flow.

Klaviyo's own docs recommend against programmatic flow creation, so we
create the assets and hand-off the wiring to a single 15-minute UI session.
"""
import os
import json
import sys
import urllib.request

API_KEY = os.environ.get("KLAVIYO_API_KEY", "pk_c3d588d7e95567d363e4772f227ea548ec")
HEADERS = {
    "accept": "application/vnd.api+json",
    "revision": "2024-10-15",
    "Authorization": f"Klaviyo-API-Key {API_KEY}",
    "content-type": "application/vnd.api+json",
}

def post(path, body):
    req = urllib.request.Request(f"https://a.klaviyo.com/api{path}",
        data=json.dumps(body).encode(),
        headers=HEADERS,
        method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"ERROR {e.code}: {e.read().decode()[:500]}", file=sys.stderr)
        return None

# ─── Brand-consistent email HTML (matches NAD+ winning template) ───
def make_html(title, preview, intro_p1, intro_p2, cta_label, cta_url, closing_line):
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
<p style="margin:0 0 10px;color:#4b5563;font-size:14px;">Preview text: {preview}</p>
<h1 style="margin:0 0 12px;font-size:25px;color:#1B5E20;">{title}</h1>
<p style="margin:0 0 12px;line-height:1.7;">{intro_p1}</p>
<p style="margin:0 0 18px;line-height:1.7;">{intro_p2}</p>
<a href="{cta_url}" style="display:inline-block;background:#1B5E20;color:#fff;text-decoration:none;padding:12px 20px;border-radius:6px;font-weight:700;">{cta_label} →</a>
<p style="margin:22px 0 0;line-height:1.7;color:#4b5563;font-size:14px;">{closing_line}</p>
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

def make_text(title, intro_p1, intro_p2, cta_label, cta_url, closing_line):
    return f"""{title.upper()}

{intro_p1}

{intro_p2}

{cta_label}: {cta_url}

{closing_line}

---
Onelife Health · Centurion · Glen Village · Edenvale
Free delivery over R900 (Gauteng) | R1,400 (nationwide)
"""

# ─── Shop URL with UTM tracking ───
SHOP_URL = "https://onelife.co.za/account/orders?utm_source=klaviyo&utm_medium=email&utm_campaign=replenishment-flow&utm_content=reorder-cta"
SHOP_STORE_URL = "https://onelife.co.za/pages/store-locator?utm_source=klaviyo&utm_medium=email&utm_campaign=replenishment-flow&utm_content=store-locator"

# ─── 3 email templates ───
templates = [
    {
        "name": "Replenishment Flow — Email 1 (21 days)",
        "title": "Running low yet?",
        "preview": "Most supplements start wearing off right about now. Time to top up.",
        "subject": "Running low yet? Here's how to reorder in one tap",
        "intro_p1": "It's been about three weeks since your last order from Onelife. If you picked up a 30-day supply, you're hitting the point where most people start noticing the bottle getting light.",
        "intro_p2": "Consistency matters more with supplements than almost anything else. Missing a week or two can undo months of progress — especially with things like magnesium, PCOSITOL, NAD+ boosters, or anything you're taking for metabolic or hormonal support.",
        "cta_label": "Reorder from your account",
        "closing_line": "Not sure if you need it again, or want to try something different? Reply to this email and our team will take a look at what you ordered and suggest what makes sense next.",
    },
    {
        "name": "Replenishment Flow — Email 2 (50 days)",
        "title": "Time to top up — we've missed you",
        "preview": "Your last order was nearly two months ago. Don't let the routine slip now.",
        "subject": "Time to top up? It's been ~50 days",
        "intro_p1": "It's been about 50 days since your last order. If you went with a 60-day supply last time, this is the perfect window to reorder — so you don't end up with a gap.",
        "intro_p2": "Supplement consistency is where the real results come from. Most of the research-backed benefits only show up after 8-12 weeks of uninterrupted use. A short break resets the clock, and nobody wants to start over.",
        "cta_label": "Reorder now",
        "closing_line": "Want to tweak what you're taking? Reply to this email or pop into our Centurion, Glen Village or Edenvale store for a free 15-minute chat with one of our functional health coaches.",
    },
    {
        "name": "Replenishment Flow — Email 3 (80 days)",
        "title": "We're here when you're ready",
        "preview": "A gentle nudge — no pressure.",
        "subject": "A gentle nudge from Onelife",
        "intro_p1": "It's been a while since your last order, and we just wanted to check in. No pressure — sometimes supplements are a season-of-life thing, and sometimes life just gets busy.",
        "intro_p2": "If you're ready to get back to it, your order history is a tap away and we can get it shipped out to you (or hold it for collection at your nearest store). If you're trying something new, we'd love to help you find the right thing — just hit reply.",
        "cta_label": "See your previous orders",
        "closing_line": "This will be our last replenishment reminder for this order cycle. We're not going anywhere, though — whenever you need us, we're at onelife.co.za and in-store at Centurion, Glen Village and Edenvale.",
    },
]

# ─── Create each template ───
created = []
for t in templates:
    html = make_html(t["title"], t["preview"], t["intro_p1"], t["intro_p2"], t["cta_label"], SHOP_URL, t["closing_line"])
    text = make_text(t["title"], t["intro_p1"], t["intro_p2"], t["cta_label"], SHOP_URL, t["closing_line"])
    body = {
        "data": {
            "type": "template",
            "attributes": {
                "name": t["name"],
                "editor_type": "CODE",
                "html": html,
                "text": text,
            }
        }
    }
    result = post("/templates/", body)
    if result:
        tid = result["data"]["id"]
        print(f"✓ {t['name']}")
        print(f"   Template ID: {tid}")
        print(f"   Subject: {t['subject']}")
        created.append({"id": tid, "name": t["name"], "subject": t["subject"]})
    else:
        print(f"✗ Failed: {t['name']}", file=sys.stderr)

print()
print("=" * 70)
print("NEXT STEP — Wire the flow in Klaviyo UI (15 min, one time)")
print("=" * 70)
print("""
1. Open Klaviyo → Flows → Create Flow → Create from Scratch
2. Name: "Replenishment Reminder"
3. Trigger:
   • Metric: Placed Order (Shopify)
   • Filters: none
4. Add first action — Time Delay:
   • Wait 21 days
5. Add Conditional Split (to skip people who already reordered):
   • Condition: "What someone has done (or not done)"
   • Has NOT: Placed Order zero times since starting this flow
6. On the YES branch, add an Email action:
   • Template: "Replenishment Flow — Email 1 (21 days)"
""")
for i, t in enumerate(created):
    print(f'     Template ID {i+1}: {t["id"]}')
print("""
7. Repeat for Email 2 (delay 29 more days = day 50) and Email 3 (delay 30 more = day 80)
8. Leave the flow in Draft, preview each email, then set to Live
9. Recommended: exclude the PCOS and GLP-1 segments from this flow since
   they already have dedicated post-purchase sequences

""")
print(json.dumps({"templates": created}))
