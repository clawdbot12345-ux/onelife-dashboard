#!/usr/bin/env python3
"""Autonomous daily pulse — computes per-store month-to-date pace vs the T2-T4
targets from data/omni/daily_turnover_history.csv (synced daily by the Mac Mini
bridge) and writes reports/pulse/YYYY-MM-DD.md. Runs in GitHub Actions on a
schedule; no human in the loop. Flags stale data instead of guessing.
"""
import csv
import datetime
import os
from collections import defaultdict

TARGETS = {  # monthly target R excl VAT by 31 Dec 2026 (state/BASELINES.md)
    "HO": ("Centurion/HO", 1_500_000, 1_800_000),
    "EDN": ("Edenvale", 360_000, 576_000),
    "GVS": ("Glen Village", 320_000, 480_000),
}
HIST = "data/omni/daily_turnover_history.csv"
today = datetime.date.today()


def main():
    rows = []
    if os.path.exists(HIST):
        with open(HIST) as f:
            rows = [r for r in csv.DictReader(f) if r.get("document_date")]
    mtd = defaultdict(float)
    gp = defaultdict(float)
    latest = ""
    for r in rows:
        d = r["document_date"]
        latest = max(latest, d)
        if d[:7] == today.strftime("%Y-%m"):
            try:
                mtd[r["branch"]] += float(r["value_excl_after_discount"] or 0)
                gp[r["branch"]] += float(r["gross_profit"] or 0)
            except ValueError:
                pass

    stale = (not latest) or (today - datetime.date.fromisoformat(latest)).days > 3
    day_frac = max(today.day - 1, 1) / 30.0  # rough month progress

    lines = [f"# Daily Pulse — {today.isoformat()}", ""]
    if stale:
        lines.append(f"🔴 **DATA STALE**: latest Omni row is `{latest or 'none'}` — bridge sync likely down. Fix before trusting numbers.")
        lines.append("")
    lines.append("| Store | MTD (ex VAT) | GP% | Run-rate /mo | Baseline | Dec target | Pace |")
    lines.append("|---|---|---|---|---|---|---|")
    for code, (name, base, target) in TARGETS.items():
        v = mtd.get(code, 0.0)
        g = (gp.get(code, 0.0) / v * 100) if v else 0
        rate = v / day_frac if v else 0
        pace = "🟢" if rate >= base else ("🟡" if rate >= base * 0.9 else "🔴")
        lines.append(f"| {name} | R{v:,.0f} | {g:.1f}% | R{rate:,.0f} | R{base:,.0f} | R{target:,.0f} | {pace} vs baseline |")
    lines += ["", f"_Latest Omni data: {latest or 'n/a'} · T1 (online R200k by Oct) and email/Klaviyo KPIs update in the weekly report · generated automatically._"]

    os.makedirs("reports/pulse", exist_ok=True)
    out = f"reports/pulse/{today.isoformat()}.md"
    with open(out, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
