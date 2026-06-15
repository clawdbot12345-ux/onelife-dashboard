#!/usr/bin/env python3
"""Daily Omni sync — fetches the P0 report set (see data/omni/reports-v2/CATALOG.md)
and maintains the cumulative per-branch daily turnover history that feeds
SCOREBOARD T2–T4. Runs on the Mac Mini via codex_bridge.sh (or any host that
can reach the Omni server). Env: OMNI_REPORT_URL (any valid report URL — only
its origin + credentials are used).
"""
import csv
import datetime
import json
import os
import re
import sys
import urllib.parse
import urllib.request

P0_REPORTS = [
    "Daily Turnover One Life",   # HO/Centurion, dated, with GP
    "Daily Turnover EDEN",
    "Daily Turnover GVS",
    "ANA_Most Popular Products GP",
    "Stock Export - wooCommerce - Levels Only",
    "ANA_Stock Listing_CEN",
    "ANA_Stock Listing_EDN",
    "ANA_Stock Listing_GVS",
    "Supplier Profitability",
    "Stock Valuation - Slow movers 6 Months",
    "OL_PO_Generator_V6",
]
BRANCH_OF = {"Daily Turnover One Life": "HO", "Daily Turnover EDEN": "EDN", "Daily Turnover GVS": "GVS"}
BRANCH_BUSY_YESTERDAY = {
    "OL_HO_Busy Times_Yesterday": "HO",
    "OL_EDN_Busy Times_Yesterday": "EDN",
    "OL_GVS_Busy Times_Yesterday": "GVS",
}
OUT = "data/omni/daily"
HISTORY = "data/omni/daily_turnover_history.csv"
TRANSACTION_HISTORY = "data/omni/daily_branch_transactions_history.csv"


def slugify(name):
    return re.sub(r"[^A-Za-z0-9]+", "-", name).strip("-").lower()


def snake_slug(name):
    return re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_").lower()


def report_url(origin, creds, name):
    return f"{origin}/Report/{urllib.parse.quote(name)}?{creds}"


def rows_from_payload(payload):
    return next(iter(payload.values())) if isinstance(payload, dict) else []


def fetch_report(origin, creds, name, timeout=240):
    url = report_url(origin, creds, name)
    with urllib.request.urlopen(urllib.request.Request(url), timeout=timeout) as r:
        payload = json.loads(r.read())
    rows = rows_from_payload(payload)
    return payload, rows


def write_daily(today, name, payload):
    slug = slugify(name)
    with open(f"{OUT}/{today}_{slug}.json", "w") as f:
        json.dump(payload, f)
    return f"{OUT}/{today}_{slug}.json"


def read_seen_pairs(path, columns):
    if not os.path.exists(path):
        return set()
    with open(path) as f:
        return {tuple(r.get(column, "") for column in columns) for r in csv.DictReader(f)}


def ensure_csv(path, header):
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", newline="") as f:
            csv.writer(f).writerow(header)


def num(value):
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def build_transaction_rows(transaction_sources, document_date):
    rows = []
    for report_name, branch in BRANCH_BUSY_YESTERDAY.items():
        source_rows = transaction_sources.get(report_name) or []
        transaction_count = sum(int(num(row.get("count"))) for row in source_rows)
        value_excl = round(sum(num(row.get("value_excl_after_discount")) for row in source_rows), 2)
        rows.append(
            {
                "document_date": document_date,
                "company_branch_code": branch,
                "transaction_count": transaction_count,
                "value_excl_after_discount": value_excl,
                "average_basket_ex_vat": round(value_excl / transaction_count, 2) if transaction_count else None,
                "source_report": report_name,
                "source_rows": len(source_rows),
            }
        )
    return rows


def turnover_quality_audit(turnover_rows):
    all_dates = sorted(
        {
            row.get("document_date")
            for rows in turnover_rows.values()
            for row in rows
            if row.get("document_date")
        }
    )
    branch_rows = {}
    for report_name, branch in BRANCH_OF.items():
        rows = turnover_rows.get(report_name) or []
        dates = sorted(row.get("document_date") for row in rows if row.get("document_date"))
        low_value_rows = [
            {
                "document_date": row.get("document_date"),
                "value_excl_after_discount": row.get("value_excl_after_discount"),
                "gross_profit": row.get("gross_profit"),
            }
            for row in rows
            if num(row.get("value_excl_after_discount")) and num(row.get("value_excl_after_discount")) < 1000
        ]
        branch_rows[branch] = {
            "source_report": report_name,
            "row_count": len(rows),
            "first_date": dates[0] if dates else None,
            "latest_date": dates[-1] if dates else None,
            "missing_vs_union": [date for date in all_dates if date not in set(dates)],
            "low_value_rows_under_1000": low_value_rows,
        }
    return {
        "turnover_quality_audit": [
            {
                "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "union_dates": all_dates,
                "branch_rows": branch_rows,
                "scope_note": "Daily Turnover One Life is treated as HO/Centurion because the cataloged ANA branch source maps HO to Centurion/HO; the turnover feed does not expose warehouse/channel split.",
            }
        ]
    }


def main():
    base = os.environ.get("OMNI_REPORT_URL", "").strip()
    if not base:
        sys.exit("FATAL: OMNI_REPORT_URL not set")
    p = urllib.parse.urlparse(base)
    origin, creds = f"{p.scheme}://{p.netloc}", p.query
    today = datetime.date.today().isoformat()
    yesterday = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    os.makedirs(OUT, exist_ok=True)

    # load existing history keys to make appends idempotent
    ensure_csv(HISTORY, ["branch", "document_date", "value_excl_after_discount", "gross_profit"])
    seen = read_seen_pairs(HISTORY, ["branch", "document_date"])
    ensure_csv(TRANSACTION_HISTORY, ["branch", "document_date", "transaction_count", "value_excl_after_discount", "average_basket_ex_vat"])
    seen_transactions = read_seen_pairs(TRANSACTION_HISTORY, ["branch", "document_date"])

    new_rows = []
    new_transaction_rows = []
    turnover_rows = {}
    for name in P0_REPORTS:
        try:
            payload, rows = fetch_report(origin, creds, name)
        except Exception as e:
            print(f"[fetch_omni] {name}: FAILED {e}")
            continue
        write_daily(today, name, payload)
        print(f"[fetch_omni] {name}: {len(rows)} rows")
        if name in BRANCH_OF:
            turnover_rows[name] = rows
            b = BRANCH_OF[name]
            for row in rows:
                key = (b, row.get("document_date", ""))
                if key[1] and key not in seen:
                    new_rows.append([b, key[1], row.get("value_excl_after_discount", ""), row.get("gross_profit", "")])
                    seen.add(key)

    transaction_sources = {}
    for name in BRANCH_BUSY_YESTERDAY:
        try:
            payload, rows = fetch_report(origin, creds, name)
        except Exception as e:
            print(f"[fetch_omni] {name}: FAILED {e}")
            payload, rows = {snake_slug(name): []}, []
        write_daily(today, name, payload)
        transaction_sources[name] = rows
        print(f"[fetch_omni] {name}: {len(rows)} rows")

    derived_rows = build_transaction_rows(transaction_sources, yesterday)
    write_daily(today, "Engine Daily Branch Transactions", {"engine_daily_branch_transactions": derived_rows})
    print(f"[fetch_omni] Engine Daily Branch Transactions: {len(derived_rows)} rows for {yesterday}")
    for row in derived_rows:
        key = (row["company_branch_code"], row["document_date"])
        if key not in seen_transactions:
            new_transaction_rows.append(
                [
                    row["company_branch_code"],
                    row["document_date"],
                    row["transaction_count"],
                    row["value_excl_after_discount"],
                    row["average_basket_ex_vat"] if row["average_basket_ex_vat"] is not None else "",
                ]
            )
            seen_transactions.add(key)

    audit_payload = turnover_quality_audit(turnover_rows)
    write_daily(today, "Turnover Quality Audit", audit_payload)

    if new_rows:
        with open(HISTORY, "a", newline="") as f:
            csv.writer(f).writerows(sorted(new_rows, key=lambda r: (r[1], r[0])))
    if new_transaction_rows:
        with open(TRANSACTION_HISTORY, "a", newline="") as f:
            csv.writer(f).writerows(sorted(new_transaction_rows, key=lambda r: (r[1], r[0])))
    print(f"[fetch_omni] appended {len(new_rows)} new turnover rows to {HISTORY}")
    print(f"[fetch_omni] appended {len(new_transaction_rows)} new transaction rows to {TRANSACTION_HISTORY}")


if __name__ == "__main__":
    main()
