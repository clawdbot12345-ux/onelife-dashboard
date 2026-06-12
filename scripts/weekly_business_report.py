#!/usr/bin/env python3
"""
Onelife — Weekly Business Report (the autonomous analyst)

Every Monday: pulls 30 days of orders from Shopify with per-order customer
journeys (Shopify's OWN attribution — not ad-platform claims), pulls Klaviyo
flow + campaign revenue, reads the owner's cost structure from
data/business_config.yml, and writes a unit-economics report to
reports/weekly/business-report-YYYY-MM-DD.md.

The point: revenue ex VAT x gross margin - delivery - ads - agency, by
channel, every week, with loud flags when a paid channel is under its
break-even ROAS. Built after the 2026-06-12 finding that Shopify journey
data attributed ~0 orders to paid CPC while ads+agency cost R19.5k/mo.

Environment:
    KLAVIYO_API_KEY, SHOPIFY_ADMIN_TOKEN
    Optional fallback: SHOPIFY_CLIENT_ID, SHOPIFY_CLIENT_SECRET
"""
import json
import os
import sys
import urllib.request
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
KLAVIYO_KEY = os.environ.get("KLAVIYO_API_KEY")
SHOPIFY_ADMIN_TOKEN = (os.environ.get("SHOPIFY_ADMIN_TOKEN")
                       or os.environ.get("SHOPIFY_ADMIN_ACCESS_TOKEN")
                       or os.environ.get("SHOPIFY_ACCESS_TOKEN"))
SHOPIFY_CLIENT_ID = os.environ.get("SHOPIFY_CLIENT_ID")
SHOPIFY_CLIENT_SECRET = os.environ.get("SHOPIFY_CLIENT_SECRET")
SHOPIFY_STORE = "onelifehealth.myshopify.com"
API_VERSION = "2025-01"
CONVERSION_METRIC = "WZAxyj"  # Placed Order
DAYS = 30

if not (KLAVIYO_KEY and (SHOPIFY_ADMIN_TOKEN or (SHOPIFY_CLIENT_ID and SHOPIFY_CLIENT_SECRET))):
    print("ERROR: KLAVIYO_API_KEY and SHOPIFY_ADMIN_TOKEN required "
          "(or SHOPIFY_CLIENT_ID + SHOPIFY_CLIENT_SECRET fallback)", file=sys.stderr)
    sys.exit(1)


def load_config():
    """Tiny YAML reader for our flat config (no dependency)."""
    cfg = {"vat_rate": 0.15, "gross_margin": 0.33,
           "monthly_costs": {"delivery": 0, "agency_fee": 0, "ad_spend": {}}}
    section = None
    for line in (ROOT / "data" / "business_config.yml").read_text().splitlines():
        s = line.split("#")[0].rstrip()
        if not s.strip():
            continue
        indent = len(s) - len(s.lstrip())
        k, _, v = s.strip().partition(":")
        v = v.strip()
        if indent == 0:
            section = k if not v else None
            if v:
                cfg[k] = float(v)
        elif section == "monthly_costs":
            if k == "ad_spend" and not v:
                section = "ad_spend"
            elif v:
                cfg["monthly_costs"][k] = float(v)
        elif section == "ad_spend" and v:
            cfg["monthly_costs"]["ad_spend"][k] = float(v)
    return cfg


def shopify_token():
    if SHOPIFY_ADMIN_TOKEN:
        return SHOPIFY_ADMIN_TOKEN
    body = json.dumps({"client_id": SHOPIFY_CLIENT_ID, "client_secret": SHOPIFY_CLIENT_SECRET,
                       "grant_type": "client_credentials"}).encode()
    req = urllib.request.Request(f"https://{SHOPIFY_STORE}/admin/oauth/access_token",
                                 data=body, headers={"content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())["access_token"]


def shopify_gql(token, query, variables=None):
    body = json.dumps({"query": query, "variables": variables or {}}).encode()
    req = urllib.request.Request(f"https://{SHOPIFY_STORE}/admin/api/{API_VERSION}/graphql.json",
                                 data=body, headers={"X-Shopify-Access-Token": token,
                                                     "content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


ORDERS_QUERY = """
query($cursor: String, $q: String!) {
  orders(first: 250, after: $cursor, query: $q) {
    pageInfo { hasNextPage endCursor }
    nodes {
      totalPriceSet { shopMoney { amount } }
      customerJourneySummary {
        lastVisit { source sourceType utmParameters { source medium } }
        firstVisit { source sourceType utmParameters { source medium } }
      }
    }
  }
}"""


def classify(visit):
    if not visit:
        return "unknown"
    src = (visit.get("source") or "").lower()
    st = (visit.get("sourceType") or "").lower()
    utm = visit.get("utmParameters") or {}
    us = (utm.get("source") or "").lower()
    um = (utm.get("medium") or "").lower()
    if us == "klaviyo" or "klaviyo" in src:
        return "email-klaviyo"
    if um in ("cpc", "ppc", "paid", "paid_social"):
        if "google" in (us + src):
            return "google-paid"
        if any(k in (us + src) for k in ("facebook", "instagram", "meta", "fb")):
            return "meta-paid"
        if "tiktok" in (us + src):
            return "tiktok-paid"
        return "other-paid"
    if um == "product_sync" or us == "sag_organic":
        return "google-free-listings"
    if st == "seo":
        return "organic-search"
    if any(k in src for k in ("chatgpt", "claude", "perplexity", "gemini", "copilot")):
        return "ai-assistants"
    if any(k in (us + src) for k in ("facebook", "instagram", "fb.", "meta")):
        return "meta-organic"
    if "tiktok" in (us + src):
        return "tiktok-organic"
    if src == "direct":
        return "direct"
    if "google" in src:
        return "google-unclassified"
    if src.startswith("http"):
        return "referral"
    return "other"


def fetch_orders(token, since):
    q = f"created_at:>{since} financial_status:paid"
    cursor, out = None, []
    while True:
        data = shopify_gql(token, ORDERS_QUERY, {"cursor": cursor, "q": q})
        block = data["data"]["orders"]
        out.extend(block["nodes"])
        if not block["pageInfo"]["hasNextPage"]:
            return out
        cursor = block["pageInfo"]["endCursor"]


def klaviyo_values(report_type, since_iso):
    body = {"data": {"type": report_type.rstrip("s").replace("-report", "-report"),
                     "attributes": {
                         "statistics": ["conversion_value", "conversions"],
                         "timeframe": {"start": since_iso, "end": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")},
                         "conversion_metric_id": CONVERSION_METRIC}}}
    body["data"]["type"] = report_type
    req = urllib.request.Request("https://a.klaviyo.com/api/" + report_type.replace("-report", "-reports") + "/",
                                 data=json.dumps(body).encode(),
                                 headers={"Authorization": f"Klaviyo-API-Key {KLAVIYO_KEY}",
                                          "Content-Type": "application/vnd.api+json",
                                          "accept": "application/vnd.api+json", "revision": "2025-04-15"})
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            rows = json.loads(r.read())["data"]["attributes"]["results"]
        total = sum(x["statistics"].get("conversion_value", 0) or 0 for x in rows)
        return total, rows
    except Exception as e:
        print(f"  ⚠ Klaviyo {report_type} failed: {e}", file=sys.stderr)
        return 0.0, []


def main():
    cfg = load_config()
    vat, gm = cfg["vat_rate"], cfg["gross_margin"]
    mc = cfg["monthly_costs"]
    ad_total = sum(mc["ad_spend"].values())
    since_dt = datetime.now(timezone.utc) - timedelta(days=DAYS)
    since = since_dt.strftime("%Y-%m-%d")

    token = shopify_token()
    orders = fetch_orders(token, since)
    n = len(orders)
    total = sum(float(o["totalPriceSet"]["shopMoney"]["amount"]) for o in orders)

    last = defaultdict(lambda: [0, 0.0])
    first = defaultdict(lambda: [0, 0.0])
    for o in orders:
        amt = float(o["totalPriceSet"]["shopMoney"]["amount"])
        j = o.get("customerJourneySummary") or {}
        last[classify(j.get("lastVisit"))][0] += 1
        last[classify(j.get("lastVisit"))][1] += amt
        first[classify(j.get("firstVisit"))][0] += 1
        first[classify(j.get("firstVisit"))][1] += amt

    flow_rev, _ = klaviyo_values("flow-values-report", since_dt.strftime("%Y-%m-%dT00:00:00Z"))
    camp_rev, _ = klaviyo_values("campaign-values-report", since_dt.strftime("%Y-%m-%dT00:00:00Z"))
    email_rev = flow_rev + camp_rev

    rev_ex = total / (1 + vat)
    gp = rev_ex * gm
    net = gp - mc["delivery"] - ad_total - mc["agency_fee"]
    breakeven_roas = (1 + vat) / gm
    paid_rev = sum(last[k][1] for k in ("google-paid", "meta-paid", "tiktok-paid", "other-paid", "google-unclassified"))

    def table(d):
        rows = sorted(d.items(), key=lambda x: -x[1][1])
        out = "| Channel | Orders | Revenue (incl VAT) | Share |\n|---|---|---|---|\n"
        for k, (c, r) in rows:
            out += f"| {k} | {c} | R{r:,.0f} | {r / total * 100:.1f}% |\n"
        return out

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    flags = []
    if paid_rev * gm / (1 + vat) < ad_total + mc["agency_fee"]:
        flags.append(f"🔴 PAID IS UNDERWATER: paid-attributed revenue R{paid_rev:,.0f} yields ~R{paid_rev * gm / (1 + vat):,.0f} gross profit vs R{ad_total + mc['agency_fee']:,.0f}/mo ads+agency cost.")
    if email_rev / max(total, 1) < 0.15:
        flags.append(f"🟠 Email is {email_rev / max(total, 1) * 100:.1f}% of revenue (target 25%).")
    if net < 0:
        flags.append(f"🔴 ONLINE NET CONTRIBUTION NEGATIVE: R{net:,.0f}.")

    report = f"""# One Life Online — Weekly Business Report ({today})

Period: last {DAYS} days · Source: Shopify order journeys (own attribution),
Klaviyo values reports, data/business_config.yml.

## P&L (online, {DAYS} days)
| Line | Amount |
|---|---|
| Revenue incl VAT | R{total:,.0f} ({n} paid orders, AOV R{total / max(n, 1):,.0f}) |
| Revenue ex VAT | R{rev_ex:,.0f} |
| Gross profit @{gm * 100:.0f}% | R{gp:,.0f} |
| Delivery | −R{mc['delivery']:,.0f} (R{mc['delivery'] / max(n, 1):,.0f}/order) |
| Ad spend (G/M/T) | −R{ad_total:,.0f} |
| Agency | −R{mc['agency_fee']:,.0f} |
| **Net contribution** | **R{net:,.0f}** |

Break-even ROAS (on incl-VAT revenue, before delivery/agency): **{breakeven_roas:.2f}**

## Where the money actually comes from — LAST CLICK
{table(last)}
## Who finds the customers — FIRST CLICK
{table(first)}
## Email (Klaviyo, {DAYS}d)
- Flows: R{flow_rev:,.0f} · Campaigns: R{camp_rev:,.0f} · Total: R{email_rev:,.0f} ({email_rev / max(total, 1) * 100:.1f}% of revenue; target 25%)

## Flags
{chr(10).join(flags) if flags else '✅ No flags this week.'}

*Costs are monthly figures from data/business_config.yml applied to a {DAYS}-day window — update that file when spend changes. 'google-unclassified' may contain auto-tagged (gclid) paid traffic; require utm tagging on all ads to split it.*
"""
    out_dir = ROOT / "reports" / "weekly"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"business-report-{today}.md"
    path.write_text(report)
    print(report)
    print(f"Saved: {path}", file=sys.stderr)


if __name__ == "__main__":
    main()
