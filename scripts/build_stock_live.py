#!/usr/bin/env python3
"""Wire Products, Categories, Stock-Intelligence and stock KPIs live from Omni,
now that real per-SKU cost is flowing (unit_cost_price, ~99.8% coverage, excl VAT).

Sources:
  engine-stock-listing-with-derived-cost  (per-branch SKU: avail, sell, real cost, category)
  ana-most-popular-products-gp             (12-mo units sold → "moving" vs not)
  purchase-orders                          (PO date/qty/value by description → reorder history)
  engine-supplier-master                   (supplier code → name)

Rebuilds DASHBOARD_DATA.products{all, double_down, margin_warning, negative_margin,
reorder_alerts, ordered_not_moving, chronic_overorder, top_50_by_cost_value},
DASHBOARD_DATA.categories[], and stock KPIs. Does NOT touch suppliers/ordering_health
(fill-rate still blocked on GRV). Idempotent.
"""
import datetime, glob, json, os, re
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, "index.html")
DAILY = os.path.join(ROOT, "data", "omni", "daily")
DENY = ("posgeld", "postage", "courier", "loyalty", "discount", "delivery", "rounding",
        "deposit", "voucher", "<---", "in fridge")


def newest(slug):
    fs = sorted(glob.glob(os.path.join(DAILY, f"*_{slug}.json")))
    return next(iter(json.load(open(fs[-1])).values())) if fs else []


def num(x):
    try: return float(x)
    except (TypeError, ValueError): return 0.0


def norm(s): return re.sub(r"\s+", " ", (s or "").strip().upper())


def deny(d):
    d = (d or "").strip()
    return len(d) < 4 or d.isdigit() or any(x in d.lower() for x in DENY)


def cat_map(html):
    """stock_category code -> friendly name, learned from the existing products.all."""
    k = '"products": {'; bs = html.find("{", html.find(k)); depth = 0; i = bs; ins = esc = False
    while True:
        c = html[i]
        if esc: esc = False
        elif c == "\\": esc = True
        elif c == '"': ins = not ins
        elif not ins:
            if c == "{": depth += 1
            elif c == "}":
                depth -= 1
                if depth == 0: e = i + 1; break
        i += 1
    prods = json.loads(html[bs:e])["all"]
    sku2cat = {p["sku"]: p["category"] for p in prods}
    lst = newest("engine-stock-listing-with-derived-cost")
    code2 = defaultdict(lambda: defaultdict(int))
    for r in lst:
        sc, scat = r.get("stock_code"), r.get("stock_category")
        if sc in sku2cat and scat:
            code2[scat][sku2cat[sc]] += 1
    return {code: max(c, key=c.get) for code, c in code2.items()}


def replace_top(html, key, value):
    """Replace a top-level DASHBOARD_DATA value (object {} or array [])."""
    pat = f'"{key}": '
    idx = html.find(pat)
    if idx == -1:
        return html
    open_ch = html[idx + len(pat)]
    close_ch = "}" if open_ch == "{" else "]"
    depth = 0; i = idx + len(pat); ins = esc = False; start = i
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
    html = open(HTML).read()
    CMAP = cat_map(html)
    lst = newest("engine-stock-listing-with-derived-cost")
    mpp = newest("ana-most-popular-products-gp")
    pos = newest("purchase-orders")
    smaster = newest("engine-supplier-master")

    sup_name = {}
    for s in smaster:
        for k in ("supplier_account_no", "supplier_#"):
            if s.get(k):
                sup_name[norm(s[k])] = s.get("supplier_name") or ""

    # 12-month units sold per SKU
    sold = defaultdict(float)
    for r in mpp:
        if r.get("stock_code"):
            sold[r["stock_code"]] += num(r.get("quantity"))

    # PO history aggregated by normalised description
    po_agg = defaultdict(lambda: {"order_count": set(), "qty": 0.0, "value": 0.0, "last": "", "supplier": ""})
    for r in pos:
        d = norm(r.get("line_item_description"))
        if not d:
            continue
        a = po_agg[d]
        a["order_count"].add(r.get("reference"))
        a["qty"] += num(r.get("ordered_qty"))
        a["value"] += num(r.get("value_excl_after_discount"))
        dt = r.get("document_date") or ""
        if dt > a["last"]: a["last"] = dt
        if r.get("supplier_account_no"): a["supplier"] = r["supplier_account_no"]

    # aggregate stock per SKU across branches
    prod = {}
    for r in lst:
        sc, desc = r.get("stock_code"), (r.get("stock_description") or "").strip()
        if not sc or deny(desc):
            continue
        p = prod.setdefault(sc, {"sku": sc, "name": desc, "available": 0.0,
                                 "cost": 0.0, "sell": 0.0, "scat": r.get("stock_category"),
                                 "group": r.get("product_group"), "sup": r.get("supplier_#") or ""})
        p["available"] += num(r.get("available"))
        if num(r.get("cost_price")) > 0: p["cost"] = num(r["cost_price"])
        if num(r.get("selling_price_excl")) > 0: p["sell"] = num(r["selling_price_excl"])

    GROUP = {"SHOP": "Health Shop", "NON": "Non-stock"}
    rows = []
    for sc, p in prod.items():
        sell, cost, av = p["sell"], p["cost"], p["available"]
        if sell <= 0:
            continue
        margin = round((sell - cost) / sell * 100, 1) if cost > 0 else None
        rows.append({
            "sku": sc, "name": p["name"],
            "category": CMAP.get(p["scat"], "Other"),
            "group": GROUP.get(p["group"], p["group"] or "Health Shop"),
            "available": av, "cost_price": round(cost, 2),
            "sell_price_excl": round(sell, 2), "sell_price_incl": round(sell * 1.15, 2),
            "margin_pct": margin if margin is not None else 0,
            "stock_value_cost": round(av * cost, 2), "stock_value_sell": round(av * sell, 2),
            "reorder_qty": 0.0,
            "supplier_code": p["sup"], "supplier_name": sup_name.get(norm(p["sup"]), ""),
            "_sold12": sold.get(sc, 0),
            "_po": po_agg.get(norm(p["name"])),
        })

    instock = [r for r in rows if r["available"] > 0]

    def strip(r):
        return {k: v for k, v in r.items() if not k.startswith("_")}

    all_list = sorted(instock, key=lambda r: -r["stock_value_cost"])
    double_down = sorted([r for r in instock if r["margin_pct"] >= 42 and r["available"] >= 10],
                         key=lambda r: -r["margin_pct"])[:40]
    margin_warning = sorted([r for r in instock if 0 <= r["margin_pct"] < 28],
                            key=lambda r: r["margin_pct"])[:30]
    negative_margin = [dict(r, is_error=True) for r in instock if r["margin_pct"] < 0][:20]
    reorder_alerts = sorted([r for r in instock if r["available"] <= 5 and r["sell_price_excl"] >= 200],
                            key=lambda r: -r["sell_price_excl"])[:50]
    top_50 = all_list[:50]

    # ordered-not-moving (capital trapped): reordered, on shelf, barely selling
    onm = []
    over = []
    for r in instock:
        po = r["_po"]
        if not po:
            continue
        oc = len(po["order_count"])
        if oc >= 2 and r["_sold12"] <= 5:
            onm.append({**strip(r), "order_count": oc, "qty_ordered_ytd": int(po["qty"]),
                        "po_value_excl": round(po["value"], 2), "last_ordered": po["last"]})
        if oc >= 5:
            over.append({**strip(r), "order_count": oc, "qty_ordered": int(po["qty"]),
                         "po_value_excl": round(po["value"], 2), "last_ordered": po["last"]})
    onm.sort(key=lambda r: -r["stock_value_cost"]); onm = onm[:50]
    over.sort(key=lambda r: -r["order_count"]); over = over[:30]

    # attach last_ordered to reorder_alerts
    for r in reorder_alerts:
        po = r.get("_po")
        r["last_ordered"] = po["last"] if po else "never"

    products = {
        "all": [strip(r) for r in all_list],
        "ordered_not_moving": onm,
        "reorder_alerts": [strip(r) for r in reorder_alerts],
        "double_down": [strip(r) for r in double_down],
        "chronic_overorder": over,
        "margin_warning": [strip(r) for r in margin_warning],
        "negative_margin": [strip(r) for r in negative_margin],
        "top_50_by_cost_value": [strip(r) for r in top_50],
    }

    # categories
    cat = defaultdict(lambda: {"skus": 0, "available": 0.0, "cost": 0.0, "sell": 0.0})
    for r in instock:
        c = cat[r["category"]]
        c["skus"] += 1; c["available"] += r["available"]
        c["cost"] += r["stock_value_cost"]; c["sell"] += r["stock_value_sell"]
    categories = []
    for name, c in cat.items():
        margin = round((c["sell"] - c["cost"]) / c["sell"] * 100, 1) if c["sell"] else 0
        categories.append({"name": name, "skus": c["skus"], "available": int(c["available"]),
                           "stock_value_cost": round(c["cost"], 2),
                           "stock_value_sell": round(c["sell"], 2), "avg_margin_pct": margin})
    categories.sort(key=lambda c: -c["stock_value_cost"])

    # KPIs
    tot_cost = sum(r["stock_value_cost"] for r in instock)
    tot_sell = sum(r["stock_value_sell"] for r in instock)
    kpis = {
        "total_skus_in_stock": len(instock),
        "total_stock_value_cost": round(tot_cost, 2),
        "total_stock_value_sell_excl": round(tot_sell, 2),
        "avg_gross_margin_pct": round((tot_sell - tot_cost) / tot_sell * 100, 1) if tot_sell else 0,
        "stockout_risk_count": sum(1 for r in instock if r["available"] <= 5),
    }

    html = replace_top(html, "products", products)
    html = replace_top(html, "categories", categories)
    for k, v in kpis.items():
        html = re.sub(rf'"{k}":\s*[0-9.]+', f'"{k}": {v}', html, count=1)
    open(HTML, "w").write(html)
    print(f"[stock_live] all={len(instock)} cost=R{tot_cost:,.0f} margin={kpis['avg_gross_margin_pct']}% "
          f"| double_down={len(double_down)} trapped={len(onm)} overorder={len(over)} "
          f"margin_warn={len(margin_warning)} cats={len(categories)}")


if __name__ == "__main__":
    main()
