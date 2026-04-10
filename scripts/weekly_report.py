#!/usr/bin/env python3
"""
Onelife — Weekly Blog + Email Performance Report

Pulls the last 7-14 days of campaign performance from Klaviyo and
(optionally) GA4 conversion data, writes a markdown summary, and
commits it to reports/.

Environment:
  KLAVIYO_API_KEY       — required
  GA4_PROPERTY_ID       — optional, GA4 property ID (numeric)
  GA4_SERVICE_ACCOUNT   — optional, path to GA4 service account JSON

Output: reports/weekly-YYYY-MM-DD.md
"""
import json
import os
import sys
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

KLAVIYO_KEY = os.environ.get("KLAVIYO_API_KEY")
if not KLAVIYO_KEY:
    print("ERROR: KLAVIYO_API_KEY not set", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = ROOT / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

HEADERS = {
    "accept": "application/vnd.api+json",
    "revision": "2024-10-15",
    "Authorization": f"Klaviyo-API-Key {KLAVIYO_KEY}",
    "content-type": "application/vnd.api+json",
}

def post(path, body):
    req = urllib.request.Request(f"https://a.klaviyo.com/api{path}",
        data=json.dumps(body).encode(), headers=HEADERS, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"ERROR {e.code}: {e.read().decode()[:400]}", file=sys.stderr)
        return None

def get(path):
    req = urllib.request.Request(f"https://a.klaviyo.com/api{path}",
        headers={k:v for k,v in HEADERS.items() if k != "content-type"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return None

# ─── Campaign performance for the last 7 days ───
print("Fetching campaign report...", file=sys.stderr)
cvr = post("/campaign-values-reports/", {
    "data": {
        "type": "campaign-values-report",
        "attributes": {
            "statistics": ["recipients","opens_unique","open_rate","clicks_unique","click_rate","conversions","conversion_value","unsubscribes","bounced","delivery_rate"],
            "timeframe": {"key": "last_7_days"},
            "conversion_metric_id": "WZAxyj",
        }
    }
})
campaign_results = cvr.get("data", {}).get("attributes", {}).get("results", []) if cvr else []

# Campaign metadata for names
camps = get("/campaigns/?filter=equals(messages.channel,%27email%27)&sort=-scheduled_at")
camp_meta = {}
if camps:
    for c in camps.get("data", []):
        camp_meta[c["id"]] = c["attributes"]

# Match reports to names
campaigns = []
for r in campaign_results:
    cid = r.get("groupings", {}).get("campaign_id")
    stats = r.get("statistics", {})
    meta = camp_meta.get(cid, {})
    if not meta or stats.get("recipients", 0) == 0:
        continue
    campaigns.append({
        "id": cid,
        "name": meta.get("name"),
        "sent": (meta.get("send_time") or meta.get("scheduled_at") or "")[:10],
        "recipients": int(stats.get("recipients", 0)),
        "open_rate": round(stats.get("open_rate", 0) * 100, 1),
        "click_rate": round(stats.get("click_rate", 0) * 100, 2),
        "opens_unique": int(stats.get("opens_unique", 0)),
        "clicks_unique": int(stats.get("clicks_unique", 0)),
        "conversions": int(stats.get("conversions", 0)),
        "revenue": round(stats.get("conversion_value", 0), 2),
        "unsubscribes": int(stats.get("unsubscribes", 0)),
    })
campaigns.sort(key=lambda c: c.get("revenue", 0), reverse=True)

# ─── Build the report ───
today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
total_recipients = sum(c["recipients"] for c in campaigns)
total_opens = sum(c["opens_unique"] for c in campaigns)
total_clicks = sum(c["clicks_unique"] for c in campaigns)
total_revenue = sum(c["revenue"] for c in campaigns)
total_unsubs = sum(c["unsubscribes"] for c in campaigns)

avg_open = round(total_opens / total_recipients * 100, 1) if total_recipients else 0
avg_click = round(total_clicks / total_recipients * 100, 2) if total_recipients else 0

report = f"""# Weekly Performance Report — {today}

**Period:** Last 7 days
**Campaigns sent:** {len(campaigns)}
**Total recipients:** {total_recipients:,}
**Total revenue:** R{total_revenue:,.0f}

## Summary

| Metric | Value | Benchmark |
|---|---|---|
| Avg open rate | {avg_open}% | 25-30% |
| Avg click rate | {avg_click}% | 2.5-3.5% |
| Total opens | {total_opens:,} | — |
| Total clicks | {total_clicks:,} | — |
| Conversions | {sum(c['conversions'] for c in campaigns)} | — |
| Unsubscribes | {total_unsubs} | — |
| Email revenue | R{total_revenue:,.0f} | — |

## Campaigns ranked by revenue

| Campaign | Sent | Recipients | Open % | Click % | Revenue |
|---|---|---|---|---|---|
"""
for c in campaigns:
    name = c["name"] or "(unnamed)"
    if len(name) > 50:
        name = name[:47] + "..."
    report += f"| {name} | {c['sent']} | {c['recipients']:,} | {c['open_rate']}% | {c['click_rate']}% | R{c['revenue']:,.0f} |\n"

# ─── Winners and losers ───
report += "\n## Insights\n\n"
if campaigns:
    winner = campaigns[0]
    loser = [c for c in campaigns if c["recipients"] > 50][-1] if len(campaigns) > 1 else None

    if winner["revenue"] > 0:
        report += f"**Top performer:** \"{winner['name']}\" generated **R{winner['revenue']:,.0f}** from {winner['recipients']} recipients "
        report += f"({winner['open_rate']}% open, {winner['click_rate']}% click). "
        if winner["click_rate"] > 3:
            report += "Click rate above 3% — strong intent. More like this.\n\n"
        else:
            report += "Open rate strong but clicks could be higher — test harder CTAs.\n\n"

    if loser and loser != winner and loser["open_rate"] < 25:
        report += f"**Underperformer:** \"{loser['name']}\" got only {loser['open_rate']}% open rate. "
        report += "Check subject line, send time, or segment targeting.\n\n"

# ─── Recommendations ───
report += "## Recommendations for next week\n\n"
if avg_open > 40:
    report += "- Open rate is exceptional — you can push to **4 sends/week** without list fatigue.\n"
elif avg_open < 25:
    report += "- ⚠ Open rate is below benchmark. Pause non-critical campaigns and focus on list hygiene.\n"
if avg_click < 2:
    report += "- Click rate is below benchmark — CTAs need work. Test single-CTA emails vs multi-product layouts.\n"
if total_revenue == 0 and len(campaigns) > 0:
    report += "- **Zero conversions this week.** Review tracking setup and make sure campaigns link to product pages (not just blogs).\n"
if total_unsubs > 20:
    report += f"- {total_unsubs} unsubscribes is high — review content relevance and segment targeting.\n"

report_path = REPORTS_DIR / f"weekly-{today}.md"
report_path.write_text(report)
print(f"Report written: {report_path}", file=sys.stderr)
print(report)
