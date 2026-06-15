#!/usr/bin/env python3
"""Build "Stock Moves" intelligence:
  1. cross_store  — products selling well at one store but out of stock at another
                    (transfer / ranging opportunities).
  2. reorder_idle — items on order (or freshly reordered) that aren't selling
                    (reordering dead stock).

Real Omni data: ANA_Most Popular Products GP (per-branch 12-mo sales+GP),
ANA_Stock Listing_* (per-branch availability + price + supplier),
OL_PO_Generator_V6 (on_order / movements). Injects DASHBOARD_DATA.stock_moves.
Idempotent; runs daily.
"""
import datetime, glob, json, os
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, "index.html")
DAILY = os.path.join(ROOT, "data", "omni", "daily")
BR = {"HO": "Centurion", "EDN": "Edenvale", "GVS": "Glen Village"}
DENY = ("posgeld", "postage", "courier", "loyalty", "discount", "delivery",
        "rounding", "deposit", "voucher", "<---")


def newest(slug):
    fs = sorted(glob.glob(os.path.join(DAILY, f"*_{slug}.json")))
    return next(iter(json.load(open(fs[-1])).values())) if fs else []


def num(x):
    try: return float(x)
    except (TypeError, ValueError): return 0.0


def deny(desc):
    d = (desc or "").strip()
    if len(d) < 4 or d.isdigit():
        return True
    return any(x in d.lower() for x in DENY)


def main():
    mpp = newest("ana-most-popular-products-gp")
    stock = {"HO": newest("ana-stock-listing-cen"),
             "EDN": newest("ana-stock-listing-edn"),
             "GVS": newest("ana-stock-listing-gvs")}
    pog = newest("ol-po-generator-v6")

    # per-branch availability; price + supplier (from any listing)
    avail = {b: {} for b in stock}
    price, supplier = {}, {}
    for b, rows in stock.items():
        for x in rows:
            sc = x.get("stock_code")
            if not sc:
                continue
            avail[b][sc] = num(x.get("available"))
            if x.get("selling_price_excl"):
                price.setdefault(sc, x["selling_price_excl"])
            if x.get("supplier_#"):
                supplier.setdefault(sc, x["supplier_#"])

    # per-branch sales + GP
    sales = defaultdict(lambda: defaultdict(lambda: {"qty": 0.0, "gp": 0.0}))
    desc = {}
    for r in mpp:
        sc = r.get("stock_code"); d = (r.get("line_item_description") or "").strip()
        if not sc or deny(d):
            continue
        desc[sc] = d
        b = r.get("company_branch_code")
        sales[sc][b]["qty"] += num(r.get("quantity"))
        sales[sc][b]["gp"] += num(r.get("gross_profit"))

    # 1) cross-store: strong selling branch vs a branch with ~0 stock
    cross = []
    for sc, by_b in sales.items():
        strong_b = max(by_b, key=lambda b: by_b[b]["gp"])
        s = by_b[strong_b]
        if s["qty"] < 24 or avail.get(strong_b, {}).get(sc, 0) <= 0:
            continue  # must sell well AND be stocked where it sells
        missing = [BR[b] for b in stock if b != strong_b and avail[b].get(sc, 0) <= 2]
        if not missing:
            continue
        cross.append({
            "name": desc.get(sc, sc), "supplier": supplier.get(sc, ""),
            "strong_branch": BR[strong_b], "strong_qty": int(s["qty"]),
            "strong_gp": round(s["gp"], 0),
            "strong_avail": int(avail[strong_b].get(sc, 0)),
            "missing_branches": missing,
        })
    cross.sort(key=lambda c: -c["strong_gp"])
    cross = cross[:15]

    # 2) reorder_idle: on order but not moving, still on shelf
    idle = []
    for r in pog:
        sc = r.get("stock_code"); d = (r.get("stock_description") or "").strip()
        if deny(d):
            continue
        on_order, mv_out, av = num(r.get("on_order")), num(r.get("movements_out")), num(r.get("available"))
        if on_order > 0 and mv_out == 0 and av > 0:
            idle.append({
                "name": d, "supplier": supplier.get(sc, ""),
                "on_order": int(on_order), "available": int(av),
                "movements_in": int(num(r.get("movements_in"))),
                "sell_value_excl": round(av * price.get(sc, 0), 0),
            })
    idle.sort(key=lambda x: -(x["sell_value_excl"] or x["available"]))
    idle = idle[:15]

    block = {
        "generated_at": datetime.datetime.utcnow().isoformat(),
        "cross_store_note": "Selling well at one store but out of stock at another — transfer or range it there.",
        "reorder_idle_note": "On order (being reordered) but not selling and still on the shelf — pause the reorder until it clears.",
        "cross_store": cross,
        "reorder_idle": idle,
    }

    html = open(HTML).read()
    payload = json.dumps(block, indent=2, ensure_ascii=False).replace("\n", "\n  ")
    key = '"stock_moves":'
    idx = html.find(key)
    if idx != -1:
        bs = html.find("{", idx); depth = 0; i = bs; ins = esc = False
        while i < len(html):
            ch = html[i]
            if esc: esc = False
            elif ch == "\\": esc = True
            elif ch == '"': ins = not ins
            elif not ins:
                if ch == "{": depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0: break
            i += 1
        html = html[:idx] + f'"stock_moves": {payload}' + html[i + 1:]
    else:
        html = html.replace("const DASHBOARD_DATA = {\n",
                            f'const DASHBOARD_DATA = {{\n  "stock_moves": {payload},\n', 1)
    open(HTML, "w").write(html)
    print(f"[stock_moves] cross-store: {len(cross)} | reorder-idle: {len(idle)}")


if __name__ == "__main__":
    main()
