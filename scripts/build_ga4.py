#!/usr/bin/env python3
"""Aggregate the GA4 daily feed (data/ga4/daily/*) into DASHBOARD_DATA.ga4 for the
Online tab: acquisition by (corrected) channel, on-site funnel, top products +
"viewed but not bought", geo, devices.

GA4 revenue is incl-VAT and used only as a web attribution/funnel signal — Shopify
and Omni remain the money ledger. Idempotent.
"""
import datetime, glob, json, os, re
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, "index.html")
GDIR = os.path.join(ROOT, "data", "ga4", "daily")


def newest(slug):
    fs = sorted(glob.glob(os.path.join(GDIR, f"*_{slug}.json")))
    return next(iter(json.load(open(fs[-1])).values())) if fs else []


def num(x):
    try: return float(x)
    except (TypeError, ValueError): return 0.0


def main():
    acq = newest("ga4_acquisition_daily")
    fun = newest("ga4_ecommerce_funnel_daily")
    prod = newest("ga4_top_products")
    geo = newest("ga4_geo")
    dev = newest("ga4_devices")

    # acquisition by corrected channel (only rows flagged for acquisition)
    ch = defaultdict(lambda: {"sessions": 0.0, "users": 0.0, "new_users": 0.0,
                              "conversions": 0.0, "revenue": 0.0})
    dates = set()
    for r in acq:
        dates.add(r.get("date"))
        if not r.get("include_in_acquisition"):
            continue
        c = ch[r.get("corrected_channel_group") or "Unassigned"]
        c["sessions"] += num(r.get("sessions")); c["users"] += num(r.get("total_users"))
        c["new_users"] += num(r.get("new_users")); c["conversions"] += num(r.get("conversions"))
        c["revenue"] += num(r.get("total_revenue"))
    channels = [{"channel": k, "sessions": int(v["sessions"]), "users": int(v["users"]),
                 "new_users": int(v["new_users"]), "conversions": round(v["conversions"], 1),
                 "revenue_incl": round(v["revenue"], 0),
                 "conv_rate": round(v["conversions"] / v["sessions"] * 100, 2) if v["sessions"] else 0}
                for k, v in ch.items()]
    channels.sort(key=lambda c: -c["sessions"])

    # funnel (sum across days)
    f = defaultdict(float)
    for r in fun:
        for k in ("sessions", "items_viewed", "add_to_carts", "checkouts",
                  "ecommerce_purchases", "purchase_revenue"):
            f[k] += num(r.get(k))
    sess = f["sessions"] or 1
    funnel = {
        "sessions": int(f["sessions"]), "product_views": int(f["items_viewed"]),
        "add_to_carts": int(f["add_to_carts"]), "checkouts": int(f["checkouts"]),
        "purchases": int(f["ecommerce_purchases"]),
        "purchase_revenue_incl": round(f["purchase_revenue"], 0),
        "conv_rate_pct": round(f["ecommerce_purchases"] / sess * 100, 2),
        "cart_rate_pct": round(f["add_to_carts"] / sess * 100, 1),
        "checkout_rate_pct": round(f["checkouts"] / sess * 100, 1),
    }

    # top products + viewed-but-not-bought
    pr = [p for p in prod if (p.get("item_name") or "").strip() and p.get("item_name") != "(not set)"]
    top_products = sorted(pr, key=lambda p: -num(p.get("item_revenue")))[:15]
    top_products = [{"name": p["item_name"], "views": int(num(p.get("items_viewed"))),
                     "add_to_carts": int(num(p.get("add_to_carts"))),
                     "purchased": int(num(p.get("items_purchased"))),
                     "revenue_incl": round(num(p.get("item_revenue")), 0)} for p in top_products]
    vnb = [p for p in pr if num(p.get("items_viewed")) >= 80 and num(p.get("items_purchased")) <= num(p.get("items_viewed")) * 0.03]
    vnb.sort(key=lambda p: -num(p.get("items_viewed")))
    viewed_not_bought = [{"name": p["item_name"], "views": int(num(p.get("items_viewed"))),
                          "purchased": int(num(p.get("items_purchased"))),
                          "conv_pct": round(num(p.get("items_purchased")) / num(p.get("items_viewed")) * 100, 1)}
                         for p in vnb[:10]]

    # geo (drop not-set; top by sessions)
    g = [r for r in geo if (r.get("city") or "(not set)") != "(not set)"]
    g.sort(key=lambda r: -num(r.get("sessions")))
    geo_top = [{"city": r["city"], "region": r.get("region", ""), "sessions": int(num(r.get("sessions"))),
                "conversions": round(num(r.get("conversions")), 0),
                "revenue_incl": round(num(r.get("purchase_revenue")), 0)} for r in g[:10]]

    devices = [{"device": r.get("device_category"), "sessions": int(num(r.get("sessions"))),
                "conv_rate_pct": round(num(r.get("session_conversion_rate")) * 100, 2),
                "revenue_incl": round(num(r.get("purchase_revenue")), 0)}
               for r in sorted(dev, key=lambda r: -num(r.get("sessions")))]

    block = {
        "generated_at": datetime.datetime.utcnow().isoformat(),
        "window": {"start": min(dates) if dates else "", "end": max(dates) if dates else "", "days": len(dates)},
        "revenue_note": "GA4 figures are web-analytics signals; revenue is GA4-attributed (incl VAT). "
                        "Shopify/Omni remain the money ledger.",
        "totals": {"sessions": int(sum(c["sessions"] for c in channels)),
                   "conversions": round(sum(c["conversions"] for c in channels), 0)},
        "channels": channels, "funnel": funnel, "top_products": top_products,
        "viewed_not_bought": viewed_not_bought, "geo": geo_top, "devices": devices,
    }

    html = open(HTML).read()
    payload = json.dumps(block, indent=2, ensure_ascii=False).replace("\n", "\n  ")
    key = '"ga4":'
    idx = html.find(key)
    if idx != -1:
        bs = html.find("{", idx); depth = 0; i = bs; ins = esc = False
        while i < len(html):
            ch_ = html[i]
            if esc: esc = False
            elif ch_ == "\\": esc = True
            elif ch_ == '"': ins = not ins
            elif not ins:
                if ch_ == "{": depth += 1
                elif ch_ == "}":
                    depth -= 1
                    if depth == 0: break
            i += 1
        html = html[:idx] + f'"ga4": {payload}' + html[i + 1:]
    else:
        html = html.replace("const DASHBOARD_DATA = {\n",
                            f'const DASHBOARD_DATA = {{\n  "ga4": {payload},\n', 1)
    open(HTML, "w").write(html)
    print(f"[ga4] channels={len(channels)} funnel_sessions={funnel['sessions']:,} "
          f"top_products={len(top_products)} viewed_not_bought={len(viewed_not_bought)} "
          f"geo={len(geo_top)} | window {block['window']['days']}d")


if __name__ == "__main__":
    main()
