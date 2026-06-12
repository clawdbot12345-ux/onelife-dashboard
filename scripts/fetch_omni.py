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
]
BRANCH_OF = {"Daily Turnover One Life": "HO", "Daily Turnover EDEN": "EDN", "Daily Turnover GVS": "GVS"}
OUT = "data/omni/daily"
HISTORY = "data/omni/daily_turnover_history.csv"


def main():
    base = os.environ.get("OMNI_REPORT_URL", "").strip()
    if not base:
        sys.exit("FATAL: OMNI_REPORT_URL not set")
    p = urllib.parse.urlparse(base)
    origin, creds = f"{p.scheme}://{p.netloc}", p.query
    today = datetime.date.today().isoformat()
    os.makedirs(OUT, exist_ok=True)

    # load existing history keys to make appends idempotent
    seen = set()
    if os.path.exists(HISTORY):
        with open(HISTORY) as f:
            seen = {(r["branch"], r["document_date"]) for r in csv.DictReader(f)}
    else:
        with open(HISTORY, "w", newline="") as f:
            csv.writer(f).writerow(["branch", "document_date", "value_excl_after_discount", "gross_profit"])

    new_rows = []
    for name in P0_REPORTS:
        url = f"{origin}/Report/{urllib.parse.quote(name)}?{creds}"
        try:
            with urllib.request.urlopen(urllib.request.Request(url), timeout=120) as r:
                payload = json.loads(r.read())
        except Exception as e:
            print(f"[fetch_omni] {name}: FAILED {e}")
            continue
        slug = re.sub(r"[^A-Za-z0-9]+", "-", name).strip("-").lower()
        with open(f"{OUT}/{today}_{slug}.json", "w") as f:
            json.dump(payload, f)
        rows = next(iter(payload.values())) if isinstance(payload, dict) else []
        print(f"[fetch_omni] {name}: {len(rows)} rows")
        if name in BRANCH_OF:
            b = BRANCH_OF[name]
            for row in rows:
                key = (b, row.get("document_date", ""))
                if key[1] and key not in seen:
                    new_rows.append([b, key[1], row.get("value_excl_after_discount", ""), row.get("gross_profit", "")])
                    seen.add(key)

    if new_rows:
        with open(HISTORY, "a", newline="") as f:
            csv.writer(f).writerows(sorted(new_rows, key=lambda r: (r[1], r[0])))
    print(f"[fetch_omni] appended {len(new_rows)} new turnover rows to {HISTORY}")


if __name__ == "__main__":
    main()
