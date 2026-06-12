#!/usr/bin/env python3
"""
Onelife — Tuesday Education Digest Pipeline

Every Tuesday (or on demand), emails the Engaged 90d segment the newest
article from The Apothecary blog, in the 2026 design system, with the
matching topic banner as hero and a soft protocol CTA.

Content source: the PUBLIC Atom feed of the blog (no Shopify creds needed).
Audience: Engaged 90d segment (S3MAsK) — never the full list.

Environment:
    KLAVIYO_API_KEY      required
    SEND_OFFSET_DAYS     default 1 (created Mon, sends Tue 09:00 SAST)
    AUTO_SCHEDULE        default true
"""
import json
import os
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone

KLAVIYO_KEY = os.environ.get("KLAVIYO_API_KEY")
SEND_OFFSET_DAYS = int(os.environ.get("SEND_OFFSET_DAYS", "1"))
AUTO_SCHEDULE = os.environ.get("AUTO_SCHEDULE", "true").lower() == "true"
SEGMENT_ID = "S3MAsK"  # Engaged 90d — full-list sends drove 1-2% unsubs (audit 2026-06-10)
BLOG_FEED = "https://onelife.co.za/blogs/health-wellness-hub.atom"
STATE_PATH = os.path.join(os.path.dirname(__file__), ".digest_state.json")

if not KLAVIYO_KEY:
    print("ERROR: KLAVIYO_API_KEY required", file=sys.stderr)
    sys.exit(1)

# Topic keyword → article banner asset slug (mirrors snippets/article-guide-cta.liquid)
TOPIC_MAP = [
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
TOPIC_PROTOCOL = {
    "magnesium": ("/pages/sleep-ritual", "The Sleep Ritual"),
    "omega3": ("/pages/heart-health", "The Heart Health protocol"),
    "vitamind": ("/pages/winter-immunity", "Winter Immunity"),
    "ashwagandha": ("/pages/stress-reset", "The Stress Reset"),
    "collagen": ("/pages/skin-beauty", "The Skin & Beauty protocol"),
    "probiotics": ("/pages/gut-reset", "The Gut Reset"),
    "sleep": ("/pages/sleep-ritual", "The Sleep Ritual"),
    "stress": ("/pages/stress-reset", "The Stress Reset"),
    "immunity": ("/pages/winter-immunity", "Winter Immunity"),
    "gut": ("/pages/gut-reset", "The Gut Reset"),
    "glp1": ("/pages/glp1-companion", "The GLP-1 Companion"),
    "energy": ("/pages/daily-energy", "Daily Energy"),
    "joints": ("/pages/joint-care", "Joint Care"),
    "skin": ("/pages/skin-beauty", "The Skin & Beauty protocol"),
    "hormones": ("/pages/womens-hormonal", "Women's Hormonal Balance"),
    "general": ("/pages/dispensary-protocols", "the 17 protocols"),
}
BANNER_FALLBACK = "https://d3k81ch9hvuctc.cloudfront.net/company/S86r7e/images/d45bbf5c-fb99-44cf-aa2b-d0a22e40dafd.jpeg"  # apothecary counter (Klaviyo CDN, permanent)


BANNER_FILES_BASE = "https://cdn.shopify.com/s/files/1/0682/9136/3126/files/onelife-article-topic-{slug}-1600.jpg"

def banner_for_article(url, topic):
    """Primary: permanent Shopify Files URL for the topic (deterministic).
    Fallbacks: the article page's own banner/og:image, then the Klaviyo-
    hosted apothecary hero."""
    if topic:
        return BANNER_FILES_BASE.format(slug=topic)
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            html = r.read().decode("utf-8", errors="ignore")
        m = re.search(r'src="([^"]*onelife-article-topic-[a-z0-9]+-1600\.webp[^"]*)"', html)
        if m:
            src = m.group(1)
            return "https:" + src if src.startswith("//") else src
        m = re.search(r'property="og:image"\s+content="([^"]+)"', html)
        if m:
            return m.group(1)
    except Exception as e:
        print(f"  banner extraction failed: {e}", file=sys.stderr)
    return BANNER_FALLBACK


def topic_for(title, summary):
    text = (title + " " + summary).lower()
    for kw, slug in TOPIC_MAP:
        if kw in text:
            return slug
    return "general"


def fetch_latest_article():
    with urllib.request.urlopen(BLOG_FEED, timeout=30) as r:
        tree = ET.fromstring(r.read())
    ns = {"a": "http://www.w3.org/2005/Atom"}
    entry = tree.find("a:entry", ns)
    if entry is None:
        return None
    title = entry.findtext("a:title", "", ns).strip()
    link = ""
    for l in entry.findall("a:link", ns):
        if l.get("rel") in (None, "alternate"):
            link = l.get("href", "")
            break
    summary = re.sub(r"<[^>]+>", " ", entry.findtext("a:content", "", ns) or "")
    summary = re.sub(r"\s+", " ", summary).strip()[:400]
    published = entry.findtext("a:published", "", ns)
    art_id = entry.findtext("a:id", link, ns)
    return {"title": title, "url": link.split("?")[0], "summary": summary,
            "published": published, "id": art_id}


def already_sent(art_id, art_url=""):
    try:
        with open(STATE_PATH) as f:
            st = json.load(f)
        if st.get("last_sent_id") == art_id:
            return True
        # The Monday publisher records last_sent_url after creating its own
        # campaign for the article it just published — skip to avoid a
        # duplicate Tuesday email for the same piece.
        return bool(art_url) and st.get("last_sent_url", "").rstrip("/") == art_url.rstrip("/")
    except Exception:
        return False


def mark_sent(art_id):
    with open(STATE_PATH, "w") as f:
        json.dump({"last_sent_id": art_id, "at": datetime.now(timezone.utc).isoformat()}, f)


def utm(url, slug, content):
    sep = "&" if "?" in url else "?"
    return f"{url}{sep}utm_source=klaviyo&utm_medium=email&utm_campaign={slug}&utm_content={content}"


def build_html(art, topic, slug):
    proto_path, proto_name = TOPIC_PROTOCOL.get(topic, TOPIC_PROTOCOL["general"])
    hero = banner_for_article(art["url"], topic)
    read_url = utm(art["url"], slug, "read-article")
    proto_url = utm("https://onelife.co.za" + proto_path, slug, "protocol-cta")
    teaser = art["summary"][:280].rsplit(" ", 1)[0] + "…"
    return f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"/><meta content="width=device-width, initial-scale=1" name="viewport"/><title>{art['title']}</title></head>
<body style="margin:0;padding:0;background:#f4f1ea;font-family:Arial,Helvetica,sans-serif;color:#374151;">
<table cellpadding="0" cellspacing="0" role="presentation" style="background:#f4f1ea;padding:28px 0;" width="100%"><tr><td align="center">
<table cellpadding="0" cellspacing="0" role="presentation" style="max-width:620px;background:#ffffff;border-radius:12px;overflow:hidden;" width="620">
<tr><td style="background:#1b4332;padding:22px 40px;text-align:center;">
<img alt="One Life Health" src="https://onelife.co.za/cdn/shop/files/OneLife_LOGO_51277c55-2099-4f3a-a659-ef42cdcac5d9.png?v=1671450106" style="display:block;margin:0 auto;max-width:130px;height:auto;" width="130"/></td></tr>
<tr><td style="height:4px;background:#2d6a4f;font-size:0;line-height:0;">&nbsp;</td></tr>
<tr><td><a href="{read_url}"><img alt="From The Apothecary journal" src="{hero}" style="display:block;width:100%;height:auto;" width="620"/></a></td></tr>
<tr><td style="padding:36px 40px 8px;">
<p style="margin:0 0 14px;font-size:11px;letter-spacing:2px;text-transform:uppercase;color:#2d6a4f;font-weight:bold;">From the Apothecary journal</p>
<h1 style="margin:0 0 16px;font-family:Georgia,'Times New Roman',serif;font-size:28px;line-height:1.2;color:#1b4332;font-weight:normal;">{art['title']}</h1>
<p style="margin:0 0 22px;font-size:15px;line-height:1.65;">Hi {{{{ first_name|default:'there' }}}} — Precious here. This week's read from the counter: {teaser}</p>
<table cellpadding="0" cellspacing="0" role="presentation" width="100%"><tr><td align="center" style="padding:0 0 22px;">
<a href="{read_url}" style="display:inline-block;background:#1b4332;color:#ffffff;padding:14px 30px;border-radius:10px;font-size:15px;font-weight:bold;text-decoration:none;">Read the full article →</a></td></tr></table>
<table cellpadding="0" cellspacing="0" role="presentation" style="margin:0 0 24px;" width="100%"><tr><td style="padding:16px 20px;background:#f1f5f1;border-radius:12px;">
<p style="margin:0;font-size:13.5px;line-height:1.7;color:#374151;">Acting on it? The consultant-signed stack for this topic is <a href="{proto_url}" style="color:#1b4332;font-weight:bold;">{proto_name} →</a> — 10% off bundled with <strong>DISPENSARY10</strong> (orders over R600).</p></td></tr></table>
<p style="margin:0 0 6px;font-size:13.5px;line-height:1.6;color:#555;">Questions about anything in the article? <a href="https://wa.me/27713744910?text=Hi%20Precious%2C%20I%20read%20the%20article%20%E2%80%94%20quick%20question" style="color:#1b4332;font-weight:bold;">WhatsApp me</a> — free, no pressure.</p>
<p style="margin:20px 0 4px;font-size:14px;">— Precious</p>
<p style="margin:0 0 28px;font-size:12px;color:#888;">One Life Health Consultant · Centurion</p></td></tr>
<tr><td style="background:#14291e;padding:20px 40px;text-align:center;">
<p style="margin:0 0 4px;font-family:Georgia,serif;font-size:16px;color:#ffffff;">A real apothecary. Family-owned since 1996.</p>
<p style="margin:0;font-size:11px;color:#9db8a8;">Centurion · Glen Village · Edenvale · Free delivery over R400 nationwide</p>
<p style="margin:12px 0 0;font-size:11px;color:#9db8a8;">{{% unsubscribe 'Unsubscribe' %}} · <a href="https://onelife.co.za" style="color:#9db8a8;">onelife.co.za</a></p></td></tr>
</table></td></tr></table></body></html>"""


def build_text(art, topic, slug):
    proto_path, proto_name = TOPIC_PROTOCOL.get(topic, TOPIC_PROTOCOL["general"])
    return (f"{art['title']}\n\nPrecious here. This week's read from the counter:\n"
            f"{art['summary'][:300]}\n\nRead it: {utm(art['url'], slug, 'read-article')}\n\n"
            f"The matching consultant-signed stack: {proto_name} — "
            f"https://onelife.co.za{proto_path} (10% off with DISPENSARY10, orders over R600)\n\n"
            "— Precious, One Life Health Consultant\n"
            "Free delivery over R400 nationwide | Collect free in store\n")


def klaviyo(path, body, method="POST"):
    req = urllib.request.Request(
        "https://a.klaviyo.com/api" + path,
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Klaviyo-API-Key {KLAVIYO_KEY}",
                 "Content-Type": "application/vnd.api+json", "accept": "application/vnd.api+json",
                 "revision": "2025-04-15"},
        method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read()) if r.status != 204 else {}
    except urllib.error.HTTPError as e:
        print(f"  ERROR {path}: {e.code} {e.read().decode()[:300]}", file=sys.stderr)
        return None


def main():
    art = fetch_latest_article()
    if not art:
        print("No article found in feed", file=sys.stderr)
        sys.exit(1)
    if already_sent(art["id"], art["url"]):
        print(f"Latest article already sent ({art['title']}) — skipping (no repeat sends)")
        return
    topic = topic_for(art["title"], art["summary"])
    slug = "tuesday-digest-" + datetime.now().strftime("%Y-%m-%d")
    print(f"Article: {art['title']}\nTopic: {topic}")

    tpl = klaviyo("/templates/", {"data": {"type": "template", "attributes": {
        "name": f"[AUTO] Tuesday Digest — {art['title'][:60]}",
        "editor_type": "CODE",
        "html": build_html(art, topic, slug),
        "text": build_text(art, topic, slug)}}})
    if not tpl:
        sys.exit(1)
    tpl_id = tpl["data"]["id"]

    send_at = (datetime.now(timezone.utc) + timedelta(days=SEND_OFFSET_DAYS)).replace(
        hour=7, minute=0, second=0, microsecond=0)  # 07:00 UTC = 09:00 SAST
    camp = klaviyo("/campaigns/", {"data": {"type": "campaign", "attributes": {
        "name": f"[AUTO] Tuesday Digest — {art['title'][:60]}",
        "audiences": {"included": [SEGMENT_ID], "excluded": []},
        "send_strategy": {"method": "static", "datetime": send_at.isoformat()},
        "send_options": {"use_smart_sending": True},
        "campaign-messages": {"data": [{"type": "campaign-message", "attributes": {
            "definition": {"channel": "email", "label": "Tuesday Digest", "content": {
                "subject": f"From the counter: {art['title']}",
                "preview_text": "This week's read from The Apothecary journal.",
                "from_email": "hello@onelife.co.za", "from_label": "Precious at One Life Health"}}}}]}}}})
    if not camp:
        sys.exit(1)
    camp_id = camp["data"]["id"]
    msg_id = camp["data"]["relationships"]["campaign-messages"]["data"][0]["id"]
    klaviyo(f"/campaign-messages/{msg_id}/relationships/template/",
            {"data": {"type": "template", "id": tpl_id}})

    if AUTO_SCHEDULE:
        job = klaviyo("/campaign-send-jobs/", {"data": {"type": "campaign-send-job", "id": camp_id}})
        print("✓ Scheduled" if job is not None else "⚠ left as Draft — schedule in Klaviyo UI")
    mark_sent(art["id"])
    print(f"Campaign {camp_id} created for {send_at.isoformat()} → segment {SEGMENT_ID}")


if __name__ == "__main__":
    main()
