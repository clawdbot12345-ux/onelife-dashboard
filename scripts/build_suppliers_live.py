#!/usr/bin/env python3
"""Rebuild the Suppliers tab data around real signals — 12-month purchases
(importance) + outstanding-order exposure (who's sitting on our orders, how old).
No fill rate (open POs are undelivered by definition).

Sources: ana-purchase-analysis (12-mo spend per supplier),
engine-supplier-outstanding (per-supplier outstanding value/qty/po_count/age).
Injects DASHBOARD_DATA.suppliers[] + DASHBOARD_DATA.supplier_health. Idempotent.
"""
import glob, json, os, re
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, "index.html")
DAILY = os.path.join(ROOT, "data", "omni", "daily")


def newest(slug):
    fs = sorted(glob.glob(os.path.join(DAILY, f"*_{slug}.json")))
    return next(iter(json.load(open(fs[-1])).values())) if fs else []


def num(x):
    try: return float(x)
    except (TypeError, ValueError): return 0.0


def norm(s): return re.sub(r"\s+", " ", (s or "").strip().upper())


def replace_top(html, key, value):
    pat = f'"{key}": '
    idx = html.find(pat)
    if idx == -1:
        # insert after opening brace
        rendered = json.dumps(value, indent=2, ensure_ascii=False).replace("\n", "\n  ")
        return html.replace("const DASHBOARD_DATA = {\n",
                            f'const DASHBOARD_DATA = {{\n  "{key}": {rendered},\n', 1)
    open_ch = html[idx + len(pat)]; close_ch = "}" if open_ch == "{" else "]"
    depth = 0; i = idx + len(pat); ins = esc = False
    while i < len(html):
        c = html[i]
        if esc: esc = False
        elif c == "\\": esc = True
        elif c == '"': ins = not ins
        elif not ins:
            if c == open_ch: depth += 1
            elif c == close_ch:
                depth -= 1
                if depth == 0: end = i + 1; break
        i += 1
    rendered = json.dumps(value, indent=2, ensure_ascii=False).replace("\n", "\n  ")
    return html[:idx] + f'"{key}": {rendered}' + html[end:]


def main():
    purch = newest("ana-purchase-analysis")
    outs = newest("engine-supplier-outstanding")

    sup = {}
    for r in purch:
        code = norm(r.get("supplier_#") or r.get("supplier_account_no"))
        if not code:
            continue
        s = sup.setdefault(code, {"code": code, "name": r.get("supplier_name") or "",
                                  "purchases_12m_excl": 0.0, "outstanding_excl": 0.0,
                                  "outstanding_qty": 0.0, "po_count": 0, "oldest_age_days": 0})
        s["purchases_12m_excl"] += num(r.get("value_excl_after_discount"))
        if not s["name"]: s["name"] = r.get("supplier_name") or ""

    for r in outs:
        code = norm(r.get("supplier_#"))
        if not code:
            continue
        s = sup.setdefault(code, {"code": code, "name": r.get("supplier_name") or "",
                                  "purchases_12m_excl": 0.0, "outstanding_excl": 0.0,
                                  "outstanding_qty": 0.0, "po_count": 0, "oldest_age_days": 0})
        s["outstanding_excl"] += num(r.get("outstanding_value_excl"))
        s["outstanding_qty"] += num(r.get("outstanding_qty"))
        s["po_count"] += int(num(r.get("po_count")))
        s["oldest_age_days"] = max(s["oldest_age_days"], int(num(r.get("age_days"))))
        if r.get("supplier_name"): s["name"] = r["supplier_name"]

    suppliers = []
    for s in sup.values():
        if s["purchases_12m_excl"] <= 0 and s["outstanding_excl"] <= 0:
            continue
        suppliers.append({
            "code": s["code"], "name": s["name"],
            "purchases_12m_excl": round(s["purchases_12m_excl"], 2),
            "outstanding_excl": round(s["outstanding_excl"], 2),
            "outstanding_qty": int(s["outstanding_qty"]),
            "po_count": s["po_count"], "oldest_age_days": s["oldest_age_days"],
        })
    suppliers.sort(key=lambda s: -s["outstanding_excl"])

    total_out = sum(s["outstanding_excl"] for s in suppliers)
    aged = [s for s in suppliers if s["oldest_age_days"] > 30 and s["outstanding_excl"] > 0]
    health = {
        "total_outstanding_excl": round(total_out, 2),
        "total_purchases_12m_excl": round(sum(s["purchases_12m_excl"] for s in suppliers), 2),
        "supplier_count": len(suppliers),
        "outstanding_supplier_count": sum(1 for s in suppliers if s["outstanding_excl"] > 0),
        "aged_outstanding_excl": round(sum(s["outstanding_excl"] for s in aged), 2),
        "aged_count": len(aged),
    }

    html = open(HTML).read()
    html = replace_top(html, "suppliers", suppliers)
    html = replace_top(html, "supplier_health", health)

    # rewrite the Suppliers narrative (NARRATIVES.suppliers string)
    top = suppliers[0] if suppliers else None
    narrative = (
        f"**Live Omni supplier data.** Outstanding (undelivered) orders total "
        f"**R{total_out:,.0f} excl VAT** across {health['outstanding_supplier_count']} suppliers"
        + (f", biggest being **{top['name']}** (R{top['outstanding_excl']:,.0f}, {top['oldest_age_days']}d old)" if top else "")
        + f". Over the last 12 months you purchased **R{health['total_purchases_12m_excl']:,.0f}** "
        f"from {health['supplier_count']} suppliers. "
        + (f"**{health['aged_count']} suppliers have orders older than 30 days** "
           f"(R{health['aged_outstanding_excl']:,.0f}) — chase these first."
           if health['aged_count'] else "No orders are aged beyond 30 days — delivery is current.")
    )
    esc = json.dumps(narrative, ensure_ascii=False)[1:-1]
    html = re.sub(r'"suppliers":\s*"(?:[^"\\]|\\.)*"',
                  lambda _m: f'"suppliers": "{esc}"', html, count=1)

    open(HTML, "w").write(html)
    print(f"[suppliers_live] {len(suppliers)} suppliers | outstanding R{total_out:,.0f} "
          f"| 12mo purchases R{health['total_purchases_12m_excl']:,.0f} | aged>30d {health['aged_count']}")


if __name__ == "__main__":
    main()
