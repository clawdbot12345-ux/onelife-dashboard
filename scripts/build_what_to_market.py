#!/usr/bin/env python3
"""Build the "What to Market" engine.

Scores products from real Omni data — 12-month item sales + gross profit
(ANA_Most Popular Products GP) joined to live per-branch stock availability
(ANA_Stock Listing_*) — and writes a ranked `what_to_market` block into
DASHBOARD_DATA in index.html. Needs no cost column (uses realized GP).

Score favours products worth *marketing*: profitable + proven demand + in stock
+ seasonally/condition relevant. Each item carries a plain-English reason and a
suggested channel that maps to the marketing engine (TikTok/Reel, VIP WhatsApp,
front-of-shelf, online hero, bundle).

Idempotent; re-runnable daily. Mirrors omni_dashboard_sync.py's injection.
"""
import datetime
import glob
import json
import math
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML = os.path.join(ROOT, "index.html")
DAILY = os.path.join(ROOT, "data", "omni", "daily")

# winter is current season (SA, June) — boost these conditions
CONDITIONS = [
    # (keywords, label, winter_relevant)
    (("immun", "vitamin c", "vit c", "zinc", "elderberry", "echinacea", "sambuc"), "Immunity", True),
    (("sleep", "insomnia", "magnesium", "magn", "mag 7", "melatonin", "valerian"), "Sleep & calm", True),
    (("joint", "collagen", "msm", "glucosamine", "cod liver", "omega", "fish oil", "krill"), "Joint & mobility", True),
    (("vitamin d", "vit d", "vit-d", "d3"), "Vitamin D", True),
    (("stress", "ashwagandha", "adaptogen", "cortisol", "rhodiola"), "Stress & adrenal", True),
    (("gut", "probiotic", "biotic", "digest", "enzyme"), "Gut health", False),
    (("energy", "b12", "iron", "coq10", "co-q", "ubiquinol"), "Energy", False),
    (("menopause", "pcos", "women", "hormone", "meno", "evening primrose"), "Women's health", False),
    (("glp", "metabol", "berberine", "weight", "keto", "carb"), "Metabolic / GLP-1", False),
    (("nootropic", "brain", "focus", "memory", "cognit"), "Brain & focus", False),
    (("skin", "hair", "nail", "beauty", "biotin"), "Beauty", False),
]
DENY = ("posgeld", "postage", "courier", "loyalty", "discount", "delivery", "rounding",
        "admin", "deposit", "voucher", "gift card", "<---")
BRANCH_DISP = {"HO": "Centurion", "EDN": "Edenvale", "GVS": "Glen Village"}


def newest(slug):
    fs = sorted(glob.glob(os.path.join(DAILY, f"*_{slug}.json")))
    if not fs:
        return []
    with open(fs[-1]) as f:
        d = json.load(f)
    return next(iter(d.values())) if isinstance(d, dict) else d


def condition_of(desc):
    d = desc.lower()
    for kws, label, winter in CONDITIONS:
        if any(k in d for k in kws):
            return label, winter
    return None, False


def main():
    mpp = newest("ana-most-popular-products-gp")
    stock = {"HO": newest("ana-stock-listing-cen"),
             "EDN": newest("ana-stock-listing-edn"),
             "GVS": newest("ana-stock-listing-gvs")}

    # per-branch availability by stock_code
    avail = {b: {} for b in stock}
    price = {}
    for b, rows in stock.items():
        for x in rows:
            sc = x.get("stock_code")
            if sc:
                avail[b][sc] = (x.get("available") or 0)
                if x.get("selling_price_excl"):
                    price.setdefault(sc, x["selling_price_excl"])

    # aggregate sales/GP per stock_code across branches (12-month window)
    agg = {}
    for r in mpp:
        sc = r.get("stock_code")
        desc = (r.get("line_item_description") or "").strip()
        if not sc or not desc or any(d in desc.lower() for d in DENY):
            continue
        a = agg.setdefault(sc, {"desc": desc, "supplier": r.get("supplier_#") or "",
                                "value": 0.0, "gp": 0.0, "qty": 0.0})
        a["value"] += r.get("value_excl_after_discount") or 0
        a["gp"] += r.get("gross_profit") or 0
        a["qty"] += r.get("quantity") or 0

    cands = []
    for sc, a in agg.items():
        if a["value"] <= 0 or a["qty"] <= 0:
            continue
        margin = a["gp"] / a["value"] * 100
        if margin <= 0 or margin > 90:        # guard data errors
            continue
        av = {b: avail[b].get(sc, 0) for b in stock}
        av_total = sum(av.values())
        if av_total <= 0:                      # never market what's out of stock
            continue
        cond, winter = condition_of(a["desc"])
        cands.append({
            "sku": sc, "name": a["desc"], "supplier": a["supplier"],
            "margin_pct": round(margin, 1), "units_12m": int(a["qty"]),
            "gp_12m": round(a["gp"], 2), "value_12m": round(a["value"], 2),
            "avail_total": int(av_total),
            "avail_by_branch": {BRANCH_DISP[b]: int(av[b]) for b in stock},
            "condition": cond, "winter": winter,
            "monthly_velocity": a["qty"] / 12.0,
        })

    if not cands:
        raise SystemExit("FATAL: no What-to-Market candidates built")

    max_gp = max(c["gp_12m"] for c in cands)
    max_units = max(c["units_12m"] for c in cands)
    units_list = sorted(c["units_12m"] for c in cands)
    median_units = units_list[len(units_list) // 2]

    for c in cands:
        m_norm = min(c["margin_pct"] / 50.0, 1.0)
        v_norm = math.log(c["units_12m"] + 1) / math.log(max_units + 1)
        gp_norm = c["gp_12m"] / max_gp
        cover = c["avail_total"] / c["monthly_velocity"] if c["monthly_velocity"] else 99
        gate = 1.0 if cover >= 1 else (0.7 if cover >= 0.5 else 0.45)
        seasonal = 0.15 if c["winter"] else 0.0
        c["_cover"] = cover
        c["score"] = round((0.35 * m_norm + 0.30 * v_norm + 0.20 * gp_norm) * gate + seasonal * gate, 4)

        # suggested channel + reason
        bits = [f"{c['margin_pct']:.0f}% margin", f"{c['units_12m']:,} sold/yr"]
        if c["condition"]:
            bits.append(("winter — " if c["winter"] else "") + c["condition"])
        bits.append(f"{c['avail_total']} in stock")
        c["reason"] = " · ".join(bits)
        if c["winter"] and c["condition"]:
            c["channel"] = f"TikTok/Reel + VIP WhatsApp ({c['condition']})"
        elif c["margin_pct"] >= 40 and c["units_12m"] < median_units:
            c["channel"] = "Front-of-shelf + online hero (under-marketed margin)"
        elif c["gp_12m"] >= 0.5 * max_gp:
            c["channel"] = "Bundle & cross-sell (proven mover)"
        elif c["condition"]:
            c["channel"] = f"Online hero + email segment ({c['condition']})"
        else:
            c["channel"] = "Feature in-store + online"

    cands.sort(key=lambda c: -c["score"])
    items = cands[:25]

    # hidden gems: high margin, well stocked, under-sold (room to grow)
    # high margin, proven-but-not-top demand, well stocked, not already a top pick → room to scale
    top_skus = {c["sku"] for c in items}
    gems = [c for c in cands
            if c["sku"] not in top_skus and c["margin_pct"] >= 42
            and 24 <= c["units_12m"] <= 250 and c["avail_total"] >= 20]
    gems.sort(key=lambda c: -(c["margin_pct"] * math.log(c["units_12m"] + 1)))
    gems = gems[:8]

    def clean(c):
        return {k: v for k, v in c.items() if not k.startswith("_") and k not in ("winter", "monthly_velocity")}

    block = {
        "generated_at": datetime.datetime.utcnow().isoformat(),
        "basis": "12-month item sales + gross profit (Omni ANA_Most Popular Products GP) "
                 "joined to live per-branch stock. Margin is realized GP (no cost column needed). "
                 "Season: winter (SA, June).",
        "scoring": "0.35·margin + 0.30·demand + 0.20·GP contribution, gated by stock cover, "
                   "+0.15 winter/condition boost.",
        "items": [clean(c) for c in items],
        "hidden_gems": [clean(c) for c in gems],
    }

    html = open(HTML).read()
    payload = json.dumps(block, indent=2, ensure_ascii=False).replace("\n", "\n  ")
    # brace-matched replace if present, else insert after the opening brace
    key = '"what_to_market":'
    idx = html.find(key)
    if idx != -1:
        brace_start = html.find("{", idx)
        depth, i, ins, esc = 0, brace_start, False, False
        while i < len(html):
            ch = html[i]
            if esc: esc = False
            elif ch == "\\": esc = True
            elif ch == '"': ins = not ins
            elif not ins:
                if ch == "{": depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        break
            i += 1
        html = html[:idx] + f'"what_to_market": {payload}' + html[i + 1:]
    else:
        html = html.replace("const DASHBOARD_DATA = {\n",
                            f'const DASHBOARD_DATA = {{\n  "what_to_market": {payload},\n', 1)
    open(HTML, "w").write(html)
    print(f"[what_to_market] {len(items)} ranked + {len(gems)} hidden gems | "
          f"top: {items[0]['name']} ({items[0]['margin_pct']}%, {items[0]['units_12m']} u/yr)")


if __name__ == "__main__":
    main()
