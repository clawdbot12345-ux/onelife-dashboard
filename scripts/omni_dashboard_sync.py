#!/usr/bin/env python3
"""Omni → dashboard sync.

Reads the daily Omni exports in data/omni/daily/ (produced by scripts/fetch_omni.py
running on a host that can reach the Omni report server) and rewrites the live
store section of DASHBOARD_DATA in index.html:

  - stores.{centurion,glen_village,edenvale}: daily sales, totals, gross profit,
    real GP margin (per branch, month-to-date from Omni Daily Turnover reports)
  - kpis: store_sales_30d_excl, combined_revenue_30d_excl, store_gross_profit_excl,
    store_gross_margin_pct, generated_at, period
  - omni_sync provenance block
  - flips the obsolete "branch-level stock not available" note
  - rewrites the Overview narrative with live numbers

Transaction counts / avg basket are intentionally left null — they are not in the
current daily report set (Daily Turnover gives value + GP only). Add a count
report to fetch_omni.py's P0 set to restore them.

Idempotent: safe to run daily. Mirrors the injection style of refresh_dashboard.py.
"""
import datetime
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, "index.html")
DAILY = os.path.join(ROOT, "data", "omni", "daily")

# Omni report slug -> (dashboard store key, top-level JSON key, display name, branch code)
BRANCHES = [
    ("daily-turnover-one-life", "centurion", "daily_turnover_one_life", "Centurion (HO)", "HO"),
    ("daily-turnover-gvs", "glen_village", "daily_turnover_gvs", "Glen Village", "GVS"),
    ("daily-turnover-eden", "edenvale", "daily_turnover_eden", "Edenvale", "EDN"),
]


def newest_for(slug):
    files = sorted(glob.glob(os.path.join(DAILY, f"*_{slug}.json")))
    if not files:
        return None, None
    path = files[-1]
    sync_date = os.path.basename(path)[:10]
    with open(path) as f:
        payload = json.load(f)
    return payload, sync_date


def rows_of(payload, top_key):
    if isinstance(payload, dict):
        return payload.get(top_key) or next(iter(payload.values()), [])
    return payload or []


def replace_block(html, key, new_value):
    """Replace a top-level `"key": { ... }` object inside DASHBOARD_DATA."""
    pattern = f'"{key}": {{'
    idx = html.find(pattern)
    if idx == -1:
        return html, False
    brace_start = idx + len(pattern) - 1
    depth, i, in_string, escape = 0, brace_start, False, False
    while i < len(html):
        ch = html[i]
        if escape:
            escape = False
        elif ch == "\\":
            escape = True
        elif ch == '"':
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
        return html, False
    indented = json.dumps(new_value, indent=2, ensure_ascii=False).replace("\n", "\n  ")
    return html[:idx] + f'"{key}": {indented}' + html[brace_end + 1:], True


def main():
    stores = {}
    sync_dates = []
    all_dates = set()
    blended_sales = 0.0
    blended_gp = 0.0

    for slug, store_key, top_key, _disp, _code in BRANCHES:
        payload, sync_date = newest_for(slug)
        if payload is None:
            sys.exit(f"FATAL: no Omni daily file for {slug} in {DAILY}")
        sync_dates.append(sync_date)
        rows = rows_of(payload, top_key)
        daily = {}
        gp_total = 0.0
        for r in rows:
            d = r.get("document_date")
            if not d:
                continue
            v = float(r.get("value_excl_after_discount") or 0)
            daily[d] = round(v, 2)
            gp_total += float(r.get("gross_profit") or 0)
            all_dates.add(d)
        sales_total = round(sum(daily.values()), 2)
        gp_total = round(gp_total, 2)
        margin = round(gp_total / sales_total * 100, 1) if sales_total else 0.0
        blended_sales += sales_total
        blended_gp += gp_total
        stores[store_key] = {
            "total_sales_excl": sales_total,
            "total_returns_excl": None,        # not in Daily Turnover feed
            "net_sales_excl": sales_total,
            "transaction_count": None,         # pending Omni count report
            "avg_basket_excl": None,           # pending Omni count report
            "gross_profit_excl": gp_total,
            "gross_margin_pct": margin,
            "daily_sales_excl": dict(sorted(daily.items())),
        }

    # --- merge live MTD transactions + avg basket (engine_mtd_branch_transactions) ---
    TX_OF = {"HO": "centurion", "EDN": "edenvale", "GVS": "glen_village"}
    txp, _ = newest_for("engine-mtd-branch-transactions")
    if txp is not None:
        for r in rows_of(txp, next(iter(txp.keys()))):
            sk = TX_OF.get(r.get("company_branch_code"))
            if sk and sk in stores:
                tc = r.get("transaction_count")
                ab = r.get("average_basket_ex_vat")
                stores[sk]["transaction_count"] = tc if tc else None
                stores[sk]["avg_basket_excl"] = round(ab, 2) if ab else None

    period_start = min(all_dates)
    period_end = max(all_dates)
    days = len(all_dates)
    store_sales = round(blended_sales, 2)
    store_gp = round(blended_gp, 2)
    store_margin = round(store_gp / store_sales * 100, 1) if store_sales else 0.0
    last_sync = max(sync_dates)

    html = open(HTML).read()

    # online revenue (from the Shopify/Klaviyo refresh) to recompute combined
    m = re.search(r'"online_sales_30d_excl":\s*([0-9.]+)', html)
    online = float(m.group(1)) if m else 0.0
    combined = round(store_sales + online, 2)

    # --- stores block ---
    html, ok = replace_block(html, "stores", stores)
    if not ok:
        sys.exit("FATAL: could not locate stores block in index.html")

    # --- KPIs ---
    kpi_updates = {
        "store_sales_30d_excl": store_sales,
        "combined_revenue_30d_excl": combined,
        "store_gross_profit_excl": store_gp,
        "store_gross_margin_pct": store_margin,
    }
    for k, v in kpi_updates.items():
        if re.search(rf'"{k}":\s*[0-9.]+', html):
            html = re.sub(rf'"{k}":\s*[0-9.]+', f'"{k}": {v}', html, count=1)
        else:
            # insert new key after store_sales_30d_excl
            html = re.sub(
                r'("store_sales_30d_excl":\s*[0-9.]+,)',
                rf'\1\n    "{k}": {v},',
                html, count=1,
            )

    # generated_at + period
    html = re.sub(r'"generated_at":\s*"[^"]*"',
                  f'"generated_at": "{datetime.datetime.utcnow().isoformat()}"', html, count=1)
    html = re.sub(r'("period":\s*{)[^}]*(})',
                  rf'\1\n    "start": "{period_start}",\n    "end": "{period_end}",\n    "days": {days}\n  \2',
                  html, count=1)

    # --- live per-branch stock summary (no cost in feed yet; sell value only) ---
    STOCK = [("centurion", "ana-stock-listing-cen"), ("glen_village", "ana-stock-listing-gvs"),
             ("edenvale", "ana-stock-listing-edn")]
    branch_stock = {}
    union_instock = set()
    for store_key, slug in STOCK:
        payload, _ = newest_for(slug)
        if payload is None:
            continue
        rs = rows_of(payload, next(iter(payload.keys())) if isinstance(payload, dict) else "")
        instock = [x for x in rs if (x.get("available") or 0) > 0]
        for x in instock:
            union_instock.add(x.get("stock_code"))
        branch_stock[store_key] = {
            "skus_in_stock": len(instock),
            "stockout_risk_le5": sum(1 for x in rs if 0 < (x.get("available") or 0) <= 5),
            "stock_value_sell_excl": round(
                sum((x.get("available") or 0) * (x.get("selling_price_excl") or 0) for x in instock), 2),
        }

    # latest available per-branch transactions (single-day; HO may be 0 on no-sync days)
    tx_payload, _ = newest_for("engine-daily-branch-transactions")
    latest_tx = {}
    if tx_payload is not None:
        for r in rows_of(tx_payload, next(iter(tx_payload.keys()))):
            latest_tx[r.get("company_branch_code")] = {
                "date": r.get("document_date"),
                "transaction_count": r.get("transaction_count"),
                "avg_basket_ex_vat": r.get("average_basket_ex_vat"),
            }

    # --- omni_sync provenance ---
    prov = {
        "source": "Omni Web Server (Daily Turnover reports)",
        "last_sync": last_sync,
        "window": {"start": period_start, "end": period_end, "days": days},
        "branches": {k: v["total_sales_excl"] for k, v in stores.items()},
        "branch_stock": branch_stock,
        "total_skus_in_stock_live": len(union_instock),
        "latest_transactions": latest_tx,
        "note": "Live (month-to-date): store revenue, gross profit, transactions, avg basket, "
                "and per-branch stock (sell value). Pending from Omni: a true per-SKU cost "
                "report (only ~72% sales-derived cost coverage today) and GRV-by-supplier "
                "(for fill rates).",
    }
    if '"omni_sync":' in html:
        html, _ = replace_block(html, "omni_sync", prov)
    else:
        prov_str = json.dumps(prov, indent=2, ensure_ascii=False).replace("\n", "\n  ")
        html = html.replace("const DASHBOARD_DATA = {\n",
                            f"const DASHBOARD_DATA = {{\n  \"omni_sync\": {prov_str},\n", 1)

    # --- flip the obsolete branch-stock note ---
    html = re.sub(
        r'<strong>⚠️ Branch-level stock split not yet available via Omni API</strong>[^<]*',
        f'<strong>✅ Branch-level data live via Omni</strong> — per-branch sales & GP '
        f'syncing daily (last sync {last_sync}). Per-branch stock listings available; '
        f'wiring into the product table next.',
        html, count=1,
    )

    # --- Overview narrative (live) ---
    def share(v):
        return round(v / store_sales * 100) if store_sales else 0
    cen, gvs, edn = stores["centurion"], stores["glen_village"], stores["edenvale"]
    online_share = round(online / combined * 100, 1) if combined else 0
    baskets = {k: stores[k]["avg_basket_excl"] for k in ("centurion", "glen_village", "edenvale")
               if stores[k]["avg_basket_excl"]}
    total_tx = sum(stores[k]["transaction_count"] or 0
                   for k in ("centurion", "glen_village", "edenvale"))
    if baskets and len(baskets) == 3:
        gap = round(max(baskets.values()) - min(baskets.values()))
        basket_line = (
            f"**Live MTD transactions: {total_tx:,}** at a combined avg basket of "
            f"**R{store_sales / total_tx:,.0f}** (Centurion R{cen['avg_basket_excl']:,.0f}, "
            f"Glen Village R{gvs['avg_basket_excl']:,.0f}, Edenvale R{edn['avg_basket_excl']:,.0f}). "
            f"The R{gap} basket gap between the strongest and weakest store is a ranging / "
            f"upsell opportunity, not a footfall one."
        )
    else:
        basket_line = "Per-store transactions / avg basket pending the Omni MTD count report."
    narrative = (
        f"**Live Omni data — month-to-date ({period_start} to {period_end}).** "
        f"The three stores generated **R{store_sales:,.0f} excl VAT** at a real gross "
        f"profit of **R{store_gp:,.0f} ({store_margin}% GP margin)**.\n\n"
        f"**Centurion** leads with **R{cen['total_sales_excl']:,.0f}** ({share(cen['total_sales_excl'])}% of "
        f"store revenue) at {cen['gross_margin_pct']}% GP. **Edenvale** R{edn['total_sales_excl']:,.0f} "
        f"({share(edn['total_sales_excl'])}%, {edn['gross_margin_pct']}% GP) and **Glen Village** "
        f"R{gvs['total_sales_excl']:,.0f} ({share(gvs['total_sales_excl'])}%, {gvs['gross_margin_pct']}% GP).\n\n"
        f"**Online (trailing 30 days):** R{online:,.0f} — store figures here are "
        f"month-to-date, so the two windows aren't directly comparable.\n\n"
        + basket_line
    )
    escaped = json.dumps(narrative, ensure_ascii=False)[1:-1]
    html = re.sub(r'"overview":\s*"(?:[^"\\]|\\.)*"',
                  lambda _m: f'"overview": "{escaped}"', html, count=1)

    open(HTML, "w").write(html)
    print(f"[omni_dashboard_sync] synced {period_start}..{period_end} "
          f"({days}d) | store R{store_sales:,.0f} | GP R{store_gp:,.0f} ({store_margin}%) "
          f"| last_sync {last_sync}")


if __name__ == "__main__":
    main()
