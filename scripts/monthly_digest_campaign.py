#!/usr/bin/env python3
"""
Onelife — Monthly Digest campaign (locked cadence slot: 25th, 09:00 SAST).

The June 2026 Monthly Digest was the month's best-earning campaign
(R4,085 from 1,396 recipients — R2.93/recipient vs ~R0.33 for education
sends). This pipeline makes it a mechanical monthly ritual: this month's
Apothecary articles + three in-stock picks, in the master template, to the
Engaged 90d segment.

Content sources are all public (blog Atom feed + storefront JSON) so the
pipeline has no Shopify Admin dependency.

Environment:
    KLAVIYO_API_KEY   required
    AUTO_SCHEDULE     default true
"""
import json
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

import email_template

KLAVIYO_KEY = os.environ.get("KLAVIYO_API_KEY")
AUTO_SCHEDULE = os.environ.get("AUTO_SCHEDULE", "true").lower() == "true"
SEGMENT_ID = "S3MAsK"  # Engaged 90d — never the full list (audit 2026-06-10)
BLOG_FEED = "https://onelife.co.za/blogs/health-wellness-hub.atom"
STOREFRONT_PRODUCTS = "https://onelife.co.za/products.json?limit=50"
MAX_ARTICLES = 4
MAX_PICKS = 3

if not KLAVIYO_KEY:
    print("ERROR: KLAVIYO_API_KEY required", file=sys.stderr)
    sys.exit(1)


def fetch_articles():
    with urllib.request.urlopen(BLOG_FEED, timeout=30) as r:
        tree = ET.fromstring(r.read())
    ns = {"a": "http://www.w3.org/2005/Atom"}
    out = []
    for entry in tree.findall("a:entry", ns)[:MAX_ARTICLES]:
        title = entry.findtext("a:title", "", ns).strip()
        link = ""
        for l in entry.findall("a:link", ns):
            if l.get("rel") in (None, "alternate"):
                link = l.get("href", "").split("?")[0]
                break
        summary = re.sub(r"<[^>]+>", " ", entry.findtext("a:content", "", ns) or "")
        summary = re.sub(r"\s+", " ", summary).strip()
        out.append({"title": title, "url": link,
                    "teaser": summary[:150].rsplit(" ", 1)[0] + "…"})
    return out


def fetch_picks():
    req = urllib.request.Request(STOREFRONT_PRODUCTS, headers={
        "Accept": "application/json", "User-Agent": "onelife-monthly-digest/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            products = json.loads(r.read()).get("products", [])
    except Exception as e:
        print(f"  ⚠ storefront fetch failed: {e}", file=sys.stderr)
        return []
    in_stock = [p for p in products
                if any(v.get("available") for v in p.get("variants", []))]
    in_stock.sort(key=lambda p: p.get("published_at") or "", reverse=True)
    picks = []
    for p in in_stock[:MAX_PICKS]:
        price = ""
        variants = p.get("variants", [])
        if variants:
            try:
                price = f"R{float(variants[0].get('price', 0)):,.2f}"
            except (TypeError, ValueError):
                price = str(variants[0].get("price", ""))
        body = re.sub(r"<[^>]+>", " ", p.get("body_html") or "")
        body = re.sub(r"\s+", " ", body).strip()
        picks.append({
            "name": p.get("title", ""),
            "url": f"https://onelife.co.za/products/{p.get('handle', '')}",
            "price": price,
            "badge": "PICK OF THE MONTH",
            "blurb": (body[:110].rsplit(" ", 1)[0] + "…") if body else
                     "One of the newest arrivals on our shelves.",
        })
    return picks


def article_rows(articles, slug):
    rows = ""
    for i, a in enumerate(articles):
        url = email_template.utm(a["url"], slug, f"article-{i + 1}")
        rows += (f'<tr><td style="padding:12px 0;border-bottom:1px solid #e8e4da;">'
                 f'<p style="margin:0 0 4px;font-size:15px;font-weight:bold;">'
                 f'<a href="{url}" style="color:#1b4332;text-decoration:none;">{a["title"]} →</a></p>'
                 f'<p style="margin:0;font-size:13px;line-height:1.5;color:#555;">{a["teaser"]}</p>'
                 f'</td></tr>')
    if not rows:
        return ""
    return (f'<p style="margin:0 0 6px;font-size:11px;letter-spacing:2px;'
            f'text-transform:uppercase;color:#2d6a4f;font-weight:bold;">This month from the counter</p>'
            f'<table cellpadding="0" cellspacing="0" role="presentation" '
            f'style="margin:0 0 26px;" width="100%">{rows}</table>')


def klaviyo(path, body, method="POST"):
    req = urllib.request.Request(
        "https://a.klaviyo.com/api" + path,
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Klaviyo-API-Key {KLAVIYO_KEY}",
                 "Content-Type": "application/vnd.api+json",
                 "accept": "application/vnd.api+json", "revision": "2025-04-15"},
        method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read()) if r.status != 204 else {}
    except urllib.error.HTTPError as e:
        print(f"  ERROR {path}: {e.code} {e.read().decode()[:300]}", file=sys.stderr)
        return None


def main():
    now = datetime.now(timezone.utc)
    month_name = now.strftime("%B %Y")
    slug = "monthly-digest-" + now.strftime("%Y-%m")

    articles = fetch_articles()
    picks = fetch_picks()
    if not articles and not picks:
        print("✗ No content available for the digest", file=sys.stderr)
        sys.exit(1)
    print(f"Articles: {len(articles)} · Picks: {len(picks)}", file=sys.stderr)

    title = f"The Monthly Digest — {month_name}"
    html = email_template.render_email(
        title=title,
        eyebrow="The Monthly Digest",
        campaign_slug=slug,
        intro_html=("Once a month, the round-up worth your inbox: what we wrote, "
                    "what people kept coming back for, and what just landed on the shelves."),
        extra_html=article_rows(articles, slug),
        products=picks,
        note_html=('Stocking up? <strong>STACK5</strong> takes 5% off any 3+ items, '
                   '<strong>STACK10</strong> takes 10% off 5+ — and delivery is free over R400.'),
        whatsapp_lead="Want a hand choosing?",
        whatsapp_prefill="Hi Precious, I read the monthly digest — quick question",
    )
    text = "\n".join(
        [f"THE MONTHLY DIGEST — {month_name.upper()}", ""]
        + [f"- {a['title']}: {a['url']}" for a in articles]
        + ["", "PICKS OF THE MONTH"]
        + [f"- {p['name']} ({p['price']}): {p['url']}" for p in picks]
        + ["", email_template.TEXT_FOOTER])

    tpl = klaviyo("/templates/", {"data": {"type": "template", "attributes": {
        "name": f"[AUTO] {title}", "editor_type": "CODE", "html": html, "text": text}}})
    if not tpl:
        sys.exit(1)
    tpl_id = tpl["data"]["id"]

    # Send at 09:00 SAST (07:00 UTC); if running later than that, push out ~2h
    send_at = now.replace(hour=7, minute=0, second=0, microsecond=0)
    if send_at < now + timedelta(minutes=30):
        send_at = (now + timedelta(hours=2)).replace(minute=0, second=0, microsecond=0)

    camp = klaviyo("/campaigns/", {"data": {"type": "campaign", "attributes": {
        "name": f"[AUTO] {title}",
        "audiences": {"included": [SEGMENT_ID], "excluded": []},
        "send_strategy": {"method": "static", "datetime": send_at.isoformat()},
        "send_options": {"use_smart_sending": True},
        "campaign-messages": {"data": [{"type": "campaign-message", "attributes": {
            "definition": {"channel": "email", "label": "Monthly Digest", "content": {
                "subject": f"The Monthly Digest: {now.strftime('%B')}'s best from the counter",
                "preview_text": "What we wrote, what moved, what just landed.",
                "from_email": "hello@onelife.co.za",
                "from_label": "Precious at One Life Health"}}}}]}}}})
    if not camp:
        sys.exit(1)
    camp_id = camp["data"]["id"]
    msg_id = camp["data"]["relationships"]["campaign-messages"]["data"][0]["id"]
    klaviyo(f"/campaign-messages/{msg_id}/relationships/template/",
            {"data": {"type": "template", "id": tpl_id}})

    if AUTO_SCHEDULE:
        job = klaviyo("/campaign-send-jobs/", {"data": {"type": "campaign-send-job", "id": camp_id}})
        print("✓ Scheduled" if job is not None else "⚠ left as Draft — schedule in Klaviyo UI")
    print(f"Campaign {camp_id} created for {send_at.isoformat()} → segment {SEGMENT_ID}")


if __name__ == "__main__":
    main()
