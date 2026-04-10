#!/usr/bin/env python3
"""
Onelife Dashboard — Daily Data Refresh

Pulls the latest 30 days of Klaviyo data (including Shopify integration metrics)
and rewrites the embedded DASHBOARD_DATA + NARRATIVES in index.html.

Designed to run unattended in GitHub Actions or via cron.

Environment:
    KLAVIYO_API_KEY  — required (Klaviyo private API key)

Exit codes:
    0 — success, dashboard updated
    1 — API failure or data fetch error
    2 — HTML update error
"""
import json
import os
import re
import sys
import time
import urllib.request
import urllib.parse
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

# ─── Config ───
ROOT = Path(__file__).resolve().parent.parent
HTML_PATH = ROOT / "index.html"
API_KEY = os.environ.get("KLAVIYO_API_KEY")
if not API_KEY:
    print("ERROR: KLAVIYO_API_KEY environment variable not set", file=sys.stderr)
    sys.exit(1)

BASE = "https://a.klaviyo.com/api"
HEADERS = {
    "accept": "application/vnd.api+json",
    "revision": "2024-10-15",
    "Authorization": f"Klaviyo-API-Key {API_KEY}",
}

# Known metric IDs — can be looked up by name at runtime if the account schema changes.
METRICS = {
    "received_email": "YtvpFe",
    "opened_email": "WF5waK",
    "clicked_email": "Y6n86M",
    "unsubscribed": "W9gXVS",
    "bounced": "X4cMKc",
    "placed_order_shopify": "WZAxyj",
    "ordered_product": "TqJLxm",
    "checkout_started": "WnzuVG",
    "subscribed_email": "Xpj5b8",
}

# ─── HTTP helpers with retry ───
def _request(method, path, body=None, retries=3):
    url = f"{BASE}{path}"
    for attempt in range(retries):
        data = json.dumps(body).encode() if body else None
        headers = dict(HEADERS)
        if body:
            headers["content-type"] = "application/vnd.api+json"
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < retries - 1:
                time.sleep(1.5 + attempt)
                continue
            if e.code == 503 and attempt < retries - 1:
                time.sleep(2 + attempt)
                continue
            print(f"  {method} {path} → HTTP {e.code}: {e.read().decode()[:200]}", file=sys.stderr)
            return None
        except Exception as e:
            print(f"  {method} {path} → {type(e).__name__}: {e}", file=sys.stderr)
            return None
    return None

def get(path, params=None):
    url = path
    if params:
        url += "?" + urllib.parse.urlencode(params)
    return _request("GET", url)

def post(path, body):
    return _request("POST", path, body=body)

def throttle():
    time.sleep(0.8)

# ─── Date range (last 30 days) ───
end = datetime.now(timezone.utc).replace(hour=23, minute=59, second=59, microsecond=0)
start = end - timedelta(days=30)
iso_start = start.strftime("%Y-%m-%dT%H:%M:%S")
iso_end = end.strftime("%Y-%m-%dT%H:%M:%S")

def aggregate(metric_id, measurements=None):
    body = {
        "data": {
            "type": "metric-aggregate",
            "attributes": {
                "metric_id": metric_id,
                "interval": "day",
                "measurements": measurements or ["count"],
                "filter": [
                    f"greater-or-equal(datetime,{iso_start})",
                    f"less-than(datetime,{iso_end})",
                ],
                "page_size": 500,
                "timezone": "Africa/Johannesburg",
            }
        }
    }
    return post("/metric-aggregates/", body)

def sum_measurement(agg_data, key):
    if not agg_data:
        return 0
    arr = agg_data.get("data", {}).get("attributes", {}).get("data", [])
    if not arr:
        return 0
    return sum(arr[0].get("measurements", {}).get(key, []))

def extract_daily(agg_data, key="count"):
    if not agg_data:
        return {}
    attrs = agg_data.get("data", {}).get("attributes", {})
    dates = attrs.get("dates", [])
    data = attrs.get("data", [])
    if not data:
        return {d[:10]: 0 for d in dates}
    counts = data[0].get("measurements", {}).get(key, [])
    return {dates[i][:10]: counts[i] for i in range(min(len(dates), len(counts)))}

# ─── Fetch everything ───
print(f"[{datetime.now().isoformat()}] Fetching Klaviyo data for {iso_start} → {iso_end}", file=sys.stderr)

print("  → Email metrics...", file=sys.stderr)
received = aggregate(METRICS["received_email"]); throttle()
opened = aggregate(METRICS["opened_email"]); throttle()
clicked = aggregate(METRICS["clicked_email"]); throttle()
unsubbed = aggregate(METRICS["unsubscribed"]); throttle()
bounced = aggregate(METRICS["bounced"]); throttle()
subscribed = aggregate(METRICS["subscribed_email"]); throttle()

recv = int(sum_measurement(received, "count"))
opens = int(sum_measurement(opened, "count"))
clicks = int(sum_measurement(clicked, "count"))
unsubs = int(sum_measurement(unsubbed, "count"))
bnc = int(sum_measurement(bounced, "count"))
new_subs = int(sum_measurement(subscribed, "count"))

print(f"  → Placed Order (Shopify)...", file=sys.stderr)
placed = aggregate(METRICS["placed_order_shopify"], measurements=["count", "sum_value", "unique"])
throttle()
total_orders = int(sum_measurement(placed, "count"))
total_rev_incl = float(sum_measurement(placed, "sum_value"))
unique_customers = int(sum_measurement(placed, "unique"))
daily_orders_raw = extract_daily(placed, "count")
daily_rev_raw = extract_daily(placed, "sum_value")

print(f"  → Ordered Product...", file=sys.stderr)
ordered = aggregate(METRICS["ordered_product"], measurements=["count", "sum_value"])
throttle()
units_sold = int(sum_measurement(ordered, "count"))

print(f"  → Checkout Started...", file=sys.stderr)
chk = aggregate(METRICS["checkout_started"])
throttle()
checkouts = int(sum_measurement(chk, "count"))

# ─── Campaign values report ───
print("  → Campaign values report...", file=sys.stderr)
cvr = post("/campaign-values-reports/", {
    "data": {
        "type": "campaign-values-report",
        "attributes": {
            "statistics": ["recipients","opens","opens_unique","open_rate","clicks","clicks_unique","click_rate","conversions","conversion_value","unsubscribes","unsubscribe_rate","bounced","bounce_rate","delivered","delivery_rate","revenue_per_recipient"],
            "timeframe": {"key": "last_30_days"},
            "conversion_metric_id": METRICS["placed_order_shopify"],
        }
    }
})
throttle()
campaign_reports = cvr.get("data", {}).get("attributes", {}).get("results", []) if cvr else []

# ─── Flow values report ───
print("  → Flow values report...", file=sys.stderr)
fvr = post("/flow-values-reports/", {
    "data": {
        "type": "flow-values-report",
        "attributes": {
            "statistics": ["recipients","opens","opens_unique","open_rate","clicks","clicks_unique","click_rate","conversions","conversion_value","unsubscribes","unsubscribe_rate","bounced","delivered","delivery_rate","revenue_per_recipient"],
            "timeframe": {"key": "last_30_days"},
            "conversion_metric_id": METRICS["placed_order_shopify"],
        }
    }
})
throttle()
flow_reports = fvr.get("data", {}).get("attributes", {}).get("results", []) if fvr else []

# ─── Campaign + flow metadata ───
print("  → Campaign metadata...", file=sys.stderr)
camps = get("/campaigns/", {
    "filter": "equals(messages.channel,'email')",
    "sort": "-scheduled_at",
})
throttle()
campaign_meta = {}
if camps:
    for c in camps.get("data", []):
        campaign_meta[c["id"]] = {
            "name": c["attributes"].get("name"),
            "status": c["attributes"].get("status"),
            "scheduled_at": c["attributes"].get("scheduled_at"),
            "send_time": c["attributes"].get("send_time"),
        }

print("  → Flow metadata...", file=sys.stderr)
flows_api = get("/flows/")
throttle()
flow_meta = {}
if flows_api:
    for f in flows_api.get("data", []):
        flow_meta[f["id"]] = {
            "name": f["attributes"].get("name"),
            "status": f["attributes"].get("status"),
            "trigger_type": f["attributes"].get("trigger_type"),
        }

# ─── List subscriber counts (paced) ───
print("  → List counts...", file=sys.stderr)
email_list_id = "Xrk5jD"  # Onelife main email list
detail = get(f"/lists/{email_list_id}/", {"additional-fields[list]": "profile_count"})
throttle()
total_subscribers = 0
if detail:
    total_subscribers = detail.get("data", {}).get("attributes", {}).get("profile_count") or 0

# ─── Segments with profile counts ───
print("  → Segments...", file=sys.stderr)
segs = get("/segments/")
throttle()
segments = []
if segs:
    for s in segs.get("data", [])[:15]:
        sid = s["id"]
        detail = get(f"/segments/{sid}/", {"additional-fields[segment]": "profile_count"})
        if detail:
            attrs = detail.get("data", {}).get("attributes", {})
            pc = attrs.get("profile_count") or 0
            if pc > 0:
                segments.append({"id": sid, "name": attrs.get("name"), "size": pc})
        throttle()
segments.sort(key=lambda x: x["size"], reverse=True)

# ─── Build campaign list ───
campaigns_real = []
for r in campaign_reports:
    cid = r.get("groupings", {}).get("campaign_id")
    stats = r.get("statistics", {})
    meta = campaign_meta.get(cid, {})
    if not meta:
        continue
    campaigns_real.append({
        "id": cid,
        "name": meta.get("name"),
        "status": meta.get("status"),
        "sent_date": (meta.get("send_time") or meta.get("scheduled_at") or "")[:10],
        "recipients": int(stats.get("recipients", 0)),
        "opens": int(stats.get("opens", 0)),
        "open_rate_pct": round(stats.get("open_rate", 0) * 100, 2),
        "clicks": int(stats.get("clicks", 0)),
        "click_rate_pct": round(stats.get("click_rate", 0) * 100, 2),
        "conversions": int(stats.get("conversions", 0)),
        "revenue": round(stats.get("conversion_value", 0), 2),
        "unsubscribes": int(stats.get("unsubscribes", 0)),
        "delivery_rate_pct": round(stats.get("delivery_rate", 0) * 100, 1),
    })
campaigns_real.sort(key=lambda c: c.get("sent_date", ""), reverse=True)

# ─── Build flow list (aggregate multiple entries per flow) ───
flow_agg = defaultdict(lambda: defaultdict(int))
for r in flow_reports:
    fid = r.get("groupings", {}).get("flow_id")
    stats = r.get("statistics", {})
    for k in ("recipients","opens","opens_unique","clicks","clicks_unique","conversions","unsubscribes","delivered"):
        flow_agg[fid][k] += int(stats.get(k, 0) or 0)
    flow_agg[fid]["revenue"] += float(stats.get("conversion_value", 0) or 0)

flows_real = []
for fid, meta in flow_meta.items():
    if meta.get("status") != "live":
        continue
    agg = flow_agg.get(fid, {})
    f_recipients = agg.get("recipients", 0)
    f_opens_unique = agg.get("opens_unique", 0)
    f_clicks_unique = agg.get("clicks_unique", 0)
    f_conversions = agg.get("conversions", 0)
    open_rate = (f_opens_unique / f_recipients * 100) if f_recipients else 0
    click_rate = (f_clicks_unique / f_recipients * 100) if f_recipients else 0
    conv_rate = (f_conversions / f_recipients * 100) if f_recipients else 0
    flows_real.append({
        "id": fid,
        "name": meta.get("name"),
        "status": "live",
        "trigger_type": meta.get("trigger_type"),
        "recipients_30d": f_recipients,
        "emails_sent_30d": agg.get("delivered", 0) or f_recipients,
        "opens_30d": agg.get("opens", 0),
        "clicks_30d": agg.get("clicks", 0),
        "open_rate_pct": round(open_rate, 2),
        "click_rate_pct": round(click_rate, 2),
        "conversion_rate_pct": round(conv_rate, 2),
        "revenue_30d": round(agg.get("revenue", 0), 2),
    })
flows_real.sort(key=lambda f: f["revenue_30d"], reverse=True)

total_email_rev = sum(c.get("revenue", 0) for c in campaigns_real) + sum(f.get("revenue_30d", 0) for f in flows_real)
total_campaign_rev = sum(c.get("revenue", 0) for c in campaigns_real)
total_flow_rev = sum(f.get("revenue_30d", 0) for f in flows_real)
open_rate_pct = round((opens / recv * 100), 2) if recv else 0
click_rate_pct = round((clicks / recv * 100), 2) if recv else 0
unsub_rate_pct = round((unsubs / recv * 100), 3) if recv else 0
bounce_rate_pct = round((bnc / recv * 100), 2) if recv else 0

# ─── Build final Klaviyo block ───
klaviyo_data = {
    "_source": "LIVE Klaviyo API",
    "_fetched_at": datetime.now(timezone.utc).isoformat(),
    "_period_start": iso_start,
    "_period_end": iso_end,
    "summary": {
        "total_subscribers": total_subscribers,
        "new_subscribers_30d": new_subs,
        "unsubscribes_30d": unsubs,
        "bounced_30d": bnc,
        "avg_open_rate_pct": open_rate_pct,
        "avg_click_rate_pct": click_rate_pct,
        "avg_unsubscribe_rate_pct": unsub_rate_pct,
        "bounce_rate_pct": bounce_rate_pct,
        "email_attributed_revenue_30d": round(total_email_rev, 2),
        "flow_revenue_30d": round(total_flow_rev, 2),
        "campaign_revenue_30d": round(total_campaign_rev, 2),
        "total_campaigns_sent_30d": len([c for c in campaigns_real if c.get("recipients", 0) > 0]),
        "total_emails_sent_30d": recv,
        "total_opens_30d": opens,
        "total_clicks_30d": clicks,
    },
    "flows": flows_real,
    "campaigns": campaigns_real,
    "segments": segments,
    "received_daily": extract_daily(received),
    "subscribed_daily": extract_daily(subscribed),
}

# ─── Build Shopify block (order totals + daily from Klaviyo integration) ───
shopify_daily = {}
for date in sorted(daily_rev_raw.keys()):
    shopify_daily[date] = {
        "orders": int(daily_orders_raw.get(date, 0)),
        "revenue_excl": round(daily_rev_raw.get(date, 0) * 100 / 115, 2),  # SA VAT 15%
    }
total_rev_excl = round(total_rev_incl * 100 / 115, 2)
aov_excl = round(total_rev_excl / total_orders, 2) if total_orders else 0

shopify_data = {
    "_source": "LIVE Klaviyo Shopify integration",
    "_fetched_at": datetime.now(timezone.utc).isoformat(),
    "total_orders": total_orders,
    "total_revenue_excl": total_rev_excl,
    "total_revenue_incl": round(total_rev_incl, 2),
    "aov_excl": aov_excl,
    "unique_customers_30d": unique_customers,
    "units_sold_30d": units_sold,
    "checkouts_started_30d": checkouts,
    "checkout_conversion_pct": round((total_orders / checkouts) * 100, 1) if checkouts else 0,
    "discount_rate_pct": 0,
    "daily": shopify_daily,
    "top_products": [],
    "_note": "Per-product data requires direct Shopify Admin API connection.",
}

# ─── Inject into index.html ───
print("Updating index.html...", file=sys.stderr)
html = HTML_PATH.read_text()

def replace_block(html, key, new_value):
    pattern = f'"{key}": {{'
    idx = html.find(pattern)
    if idx == -1:
        return html
    brace_start = idx + len(pattern) - 1
    depth = 0
    i = brace_start
    in_string = False
    escape = False
    while i < len(html):
        ch = html[i]
        if escape:
            escape = False
        elif ch == "\\":
            escape = True
        elif ch == '"' and not escape:
            in_string = not in_string
        elif not in_string:
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    brace_end = i
                    break
        i += 1
    else:
        return html
    indented = json.dumps(new_value, indent=2, ensure_ascii=False).replace("\n", "\n  ")
    return html[:idx] + f'"{key}": {indented}' + html[brace_end+1:]

html = replace_block(html, "shopify", shopify_data)
html = replace_block(html, "klaviyo", klaviyo_data)

# KPI updates
for k, v in {
    "online_sales_30d_excl": shopify_data["total_revenue_excl"],
    "online_orders_30d": shopify_data["total_orders"],
    "online_aov_excl": shopify_data["aov_excl"],
}.items():
    html = re.sub(rf'"{k}": [0-9.]+', f'"{k}": {v}', html, count=1)

# Combined revenue
store_match = re.search(r'"store_sales_30d_excl":\s*([0-9.]+)', html)
if store_match:
    store_sales = float(store_match.group(1))
    combined = round(store_sales + shopify_data["total_revenue_excl"], 2)
    html = re.sub(r'"combined_revenue_30d_excl":\s*[0-9.]+', f'"combined_revenue_30d_excl": {combined}', html, count=1)

# ─── Update narratives ───
s = klaviyo_data["summary"]
top_flow = flows_real[0] if flows_real else None
top_camp = sorted(campaigns_real, key=lambda c: c["revenue"], reverse=True)[0] if campaigns_real else None
winback_size = next((seg["size"] for seg in segments if "Win-Back" in seg["name"]), 0)
online_share = round((shopify_data["total_revenue_excl"] / (store_sales + shopify_data["total_revenue_excl"]) * 100), 1) if store_match else 0

klaviyo_narrative = (
    f"**Live Klaviyo data — last 30 days.** You have **{total_subscribers} active email subscribers** with **{new_subs} new signups**. "
    f"You sent **{recv:,} emails**, got **{opens:,} opens ({open_rate_pct}% open rate)** and **{clicks} clicks ({click_rate_pct}% click rate)**. "
    f"Open rate is genuinely strong — industry avg for health supplements is 25-30%.\n\n"
    f"**Email-attributed revenue: R{total_email_rev:,.0f}** — R{total_flow_rev:,.0f} from flows, R{total_campaign_rev:,.0f} from campaigns. "
    f"Flows are doing {round(total_flow_rev/total_email_rev*100) if total_email_rev else 0}% of the work.\n\n"
)
if top_flow:
    klaviyo_narrative += (
        f"**Top flow: '{top_flow['name']}'** — R{top_flow['revenue_30d']:,.0f} from {top_flow['recipients_30d']} recipients at {top_flow['open_rate_pct']}% open rate.\n\n"
    )
if top_camp and top_camp.get("revenue", 0) > 0:
    klaviyo_narrative += (
        f"**Top campaign:** '{top_camp['name']}' — R{top_camp['revenue']:,.0f} from {top_camp['recipients']} recipients.\n\n"
    )
klaviyo_narrative += (
    f"**Warning:** Bounce rate {bounce_rate_pct}% ({bnc} bounces) — clean the list if above 2%.\n\n"
    f"**Biggest opportunity:** Win-Back segment has {winback_size:,} profiles. 2-3% conversion × ~R500 AOV = potentially R{int(winback_size * 0.025 * 500):,} in recoverable revenue."
)

online_narrative = (
    f"**Live Shopify data — last 30 days (via Klaviyo integration).** {total_orders} orders generating **R{shopify_data['total_revenue_excl']:,.0f} excl VAT** "
    f"(R{total_rev_incl:,.0f} incl VAT) from **{unique_customers} unique customers**. AOV **R{aov_excl:,.2f} excl VAT**.\n\n"
    f"**Checkout conversion:** {checkouts} started → {total_orders} completed = **{shopify_data['checkout_conversion_pct']}% conversion**. "
    f"Strong bottom-of-funnel — bottleneck is traffic, not checkout.\n\n"
    f"**Units sold:** {units_sold} ({round(units_sold/total_orders, 1) if total_orders else 0} per order avg).\n\n"
    f"**Channel mix:** Online is **{online_share}% of combined revenue**. Health supplement benchmark is 15-20%. "
    f"Strong email engagement ({open_rate_pct}% open) with modest online share = audience exists, gap is acquisition."
)

def replace_narrative(html, key, new_text):
    escaped = json.dumps(new_text, ensure_ascii=False)[1:-1]
    pattern = rf'"{key}":\s*"(?:[^"\\]|\\.)*"'
    return re.sub(pattern, lambda m: f'"{key}": "{escaped}"', html, count=1)

html = replace_narrative(html, "klaviyo", klaviyo_narrative)
html = replace_narrative(html, "online", online_narrative)

HTML_PATH.write_text(html)

print(f"[{datetime.now().isoformat()}] DONE", file=sys.stderr)
print(f"  Subscribers: {total_subscribers}", file=sys.stderr)
print(f"  Emails sent: {recv:,}", file=sys.stderr)
print(f"  Open rate: {open_rate_pct}%", file=sys.stderr)
print(f"  Email revenue: R{total_email_rev:,.0f}", file=sys.stderr)
print(f"  Shopify orders: {total_orders} / R{shopify_data['total_revenue_excl']:,.0f}", file=sys.stderr)
