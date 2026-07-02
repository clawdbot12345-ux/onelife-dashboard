#!/usr/bin/env python3
"""
Phase 0b — Catalogue audit & triage.

Reads raw GraphQL paginated dumps of the Vivid Health vendor catalogue from the
One Life Shopify store and emits:
  - recon/catalogue-audit.csv        (full catalogue, one row per product, with decision)
  - recon/curated-launch-range.csv   (the proposed CURATED_PREMIUM launch range)
  - recon/catalogue-summary.md       (executive summary for HUMAN GATE 1)

Triage rules (deterministic, conservative):
  ARCHIVED                         -> RETIRE  (already retired by prior owner decision)
  DRAFT + 'Empty Capsules'         -> RETIRE  (packaging material, not product)
  DRAFT + other                    -> REVIEW
  ACTIVE NOURISHMENT salts/sugars  -> RETIRE  (commodity kitchen items; off-brand for supplement house)
  ACTIVE bundle (Stack/Pack)       -> KEEP    (merchandising assets, rebrand)
  ACTIVE supplement, hero-range    -> KEEP_HERO
  ACTIVE supplement, multi-format  -> MERGE   (flag duplicate sizes/formats; pick canonical later)
  ACTIVE supplement, inventory>0   -> KEEP
  ACTIVE supplement, inventory=0   -> KEEP    (rebrand candidate; flag stock-out separately)
"""
from __future__ import annotations
import csv, json, re, sys
from collections import defaultdict
from pathlib import Path

RECON = Path(__file__).resolve().parent
RAW_FILES = sorted(RECON.glob("catalogue-raw-page*.json"))

# --- Hero range from the project brief ---------------------------------------
HERO_PATTERNS = [
    ("Ashwagandha",         re.compile(r"\bashwagandha\b", re.I)),
    ("Lion's Mane",         re.compile(r"\blion'?s?\s*mane\b", re.I)),
    ("Magnesium Glycinate", re.compile(r"\bmagnesium\b.*\bglycinate\b|\bglycinate\b.*\bmagnesium\b", re.I)),
    ("Vitamin C + Zinc",    re.compile(r"\bvitamin\s*c\b.*\bzinc\b|\bzinc\b.*\bvitamin\s*c\b|\bbuffered\s*c\b.*\bzinc\b", re.I)),
    ("Omega-3",             re.compile(r"\bomega(\s*-?\s*3| oil)\b", re.I)),
]

# Commodity kitchen items shipped under NOURISHMENT — off-brand for premium supplement house.
COMMODITY_PATTERNS = [
    re.compile(r"\bepsom\s*salt\b", re.I),
    re.compile(r"\bhimalayan\s*salt\b", re.I),
    re.compile(r"\bsodium\s*bicarbonate\b", re.I),
    re.compile(r"\bxylitol\b", re.I),
    re.compile(r"\bdextrose\b", re.I),
]

BUNDLE_PATTERNS = [re.compile(r"\b(stack|pack|bundle)\b", re.I)]
EMPTY_CAP_PATTERN = re.compile(r"empty.*capsules?", re.I)

# Family key — collapses size/format variants so we can detect duplicates.
SIZE_PATTERN = re.compile(
    r"\b\d+\s*(?:capsules?|caps?|tablets?|tabs?|g|kg|ml|mg)\b|\bpowder\b|\b(?:size\s*0+)\b",
    re.I,
)
SUBBRAND_PREFIX = re.compile(r"^vivid\s+health\s*-\s*[^-]+-\s*", re.I)

def family_key(title: str) -> str:
    t = SUBBRAND_PREFIX.sub("", title).strip()
    t = SIZE_PATTERN.sub("", t).strip(" -")
    # collapse whitespace + dashes
    t = re.sub(r"[\s\-]+", " ", t).strip().lower()
    return t

def parse_subbrand(title: str) -> str:
    m = re.match(r"VIVID HEALTH\s*-\s*([^-]+?)\s*-", title, re.I)
    if not m:
        return "BUNDLE/OTHER"
    return m.group(1).strip().upper()

def detect_hero(title: str) -> str:
    for label, pat in HERO_PATTERNS:
        if pat.search(title):
            return label
    return ""

def is_commodity(title: str) -> bool:
    return any(p.search(title) for p in COMMODITY_PATTERNS)

def is_bundle(title: str) -> bool:
    return any(p.search(title) for p in BUNDLE_PATTERNS) and not title.upper().startswith("VIVID HEALTH -")

def variants_summary(node):
    vs = node.get("variants", {}).get("nodes", []) or []
    prices = [float(v["price"]) for v in vs if v.get("price")]
    skus = [v.get("sku") or "" for v in vs]
    barcodes = [v.get("barcode") or "" for v in vs]
    return {
        "variant_count": len(vs),
        "min_price": min(prices) if prices else None,
        "max_price": max(prices) if prices else None,
        "primary_sku": next((s for s in skus if s), ""),
        "primary_barcode": next((b for b in barcodes if b), ""),
    }

def load_nodes():
    nodes = []
    for f in RAW_FILES:
        data = json.loads(f.read_text())
        nodes.extend(data["data"]["products"]["nodes"])
    return nodes

def decide(node, family_counts):
    title  = node["title"]
    status = node["status"]
    inv    = node.get("totalInventory") or 0

    if status == "ARCHIVED":
        return "RETIRE", "Already archived in source store"
    if status == "DRAFT" and EMPTY_CAP_PATTERN.search(title):
        return "RETIRE", "Empty capsule packaging material, not a finished product"
    if status == "DRAFT":
        return "REVIEW", "Draft in source store — owner intent unclear"

    hero = detect_hero(title)
    if hero:
        return "KEEP_HERO", f"Hero range: {hero}"
    if is_commodity(title):
        return "RETIRE", "Commodity kitchen item (salt/sugar/bicarb) — off-brand for premium supplement house; consider keeping on One Life only"
    if is_bundle(title):
        return "KEEP", "Existing bundle; rebrand under new system"

    fam = family_key(title)
    sibling_count = family_counts.get(fam, 1)
    if sibling_count > 1:
        return "MERGE", f"Multi-format family ({sibling_count} sibling SKUs share base product); pick canonical size at gate"

    if inv == 0:
        return "KEEP", "Active but out of stock — rebrand candidate, flag stock-out"
    return "KEEP", "Active in-stock SKU"

def main():
    nodes = load_nodes()
    if not nodes:
        sys.exit("No catalogue nodes loaded — check raw page files exist.")

    # First pass — count families to flag MERGE candidates
    family_counts: dict[str, int] = defaultdict(int)
    for n in nodes:
        if n["status"] == "ACTIVE" and not is_commodity(n["title"]) and not is_bundle(n["title"]):
            family_counts[family_key(n["title"])] += 1

    rows = []
    for n in nodes:
        vs = variants_summary(n)
        decision, rationale = decide(n, family_counts)
        hero = detect_hero(n["title"])
        rows.append({
            "shopify_id":         n["id"].split("/")[-1],
            "title":              n["title"],
            "handle":             n["handle"],
            "status":             n["status"],
            "sub_brand":          parse_subbrand(n["title"]),
            "family_key":         family_key(n["title"]),
            "total_inventory":    n.get("totalInventory"),
            "variant_count":      vs["variant_count"],
            "primary_sku":        vs["primary_sku"],
            "primary_barcode":    vs["primary_barcode"],
            "min_price_zar":      vs["min_price"],
            "max_price_zar":      vs["max_price"],
            "hero_match":         hero,
            "is_bundle":          "Y" if is_bundle(n["title"]) else "",
            "is_commodity":       "Y" if is_commodity(n["title"]) else "",
            "decision":           decision,
            "proposed_tier":      ("Premium" if (hero or decision == "KEEP_HERO") else
                                   ("Premium" if is_bundle(n["title"]) else "Daily")),
            "rationale":          rationale,
            "tags":               ", ".join(n.get("tags", []) or []),
            "seo_title":          (n.get("seo") or {}).get("title") or "",
            "seo_description":    (n.get("seo") or {}).get("description") or "",
            "created_at":         n.get("createdAt"),
            "updated_at":         n.get("updatedAt"),
            "online_store_url":   n.get("onlineStoreUrl") or "",
            "featured_image_url": (((n.get("featuredMedia") or {}).get("preview") or {}).get("image") or {}).get("url") or "",
            "collections":        ", ".join(c["title"] for c in (n.get("collections", {}).get("nodes", []) or [])),
        })

    rows.sort(key=lambda r: (r["decision"], r["sub_brand"], r["title"]))

    out_full = RECON / "catalogue-audit.csv"
    with out_full.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    # Curated launch range
    curated = [r for r in rows if r["decision"] in {"KEEP_HERO", "KEEP"} and r["total_inventory"] not in (None, 0)]
    # Promote hero matches and bundles to the top
    curated.sort(key=lambda r: (0 if r["decision"] == "KEEP_HERO" else (1 if r["is_bundle"] == "Y" else 2),
                                -(r["total_inventory"] or 0)))
    out_curated = RECON / "curated-launch-range.csv"
    with out_curated.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(curated)

    # Summary
    by_decision = defaultdict(int)
    for r in rows:
        by_decision[r["decision"]] += 1

    by_subbrand = defaultdict(int)
    for r in rows:
        by_subbrand[r["sub_brand"]] += 1

    hero_found  = sorted({r["hero_match"] for r in rows if r["hero_match"]})
    hero_target = [name for name, _ in HERO_PATTERNS]
    hero_gaps   = [h for h in hero_target if h not in hero_found]

    oos_active  = [r for r in rows if r["status"] == "ACTIVE" and (r["total_inventory"] or 0) == 0]

    summary = []
    s = summary.append
    s("# Phase 0b — Catalogue audit summary")
    s("")
    s(f"**Source:** Shopify store `onelifehealth` / `onelife.co.za`. Filter: `vendor:\"VIVID HEALTH\"`.")
    s(f"**Total products:** **{len(rows)}** ({by_decision.get('KEEP_HERO',0)} hero · "
      f"{by_decision.get('KEEP',0)} keep · {by_decision.get('MERGE',0)} merge · "
      f"{by_decision.get('REVIEW',0)} review · {by_decision.get('RETIRE',0)} retire)")
    s("")
    s("## Critical findings")
    s("")
    s(f"1. **Hero-range coverage gap.** Brief specifies 5 hero SKUs: "
      f"{', '.join(hero_target)}. Currently in catalogue: "
      f"{', '.join(hero_found) if hero_found else 'NONE'}. "
      f"**Missing: {', '.join(hero_gaps) if hero_gaps else 'none'}.** "
      "These must be sourced/manufactured before the curated launch can ship its anchor range.")
    s("")
    s(f"2. **Stock health.** {len(oos_active)}/{by_decision.get('KEEP_HERO',0)+by_decision.get('KEEP',0)+by_decision.get('MERGE',0)} "
      f"active SKUs are at zero inventory. This is a manufacturing/operations issue, not a digital one — "
      "but the storefront cannot launch on an empty shelf.")
    s("")
    s("3. **Sub-brand taxonomy is inconsistent.** Variants observed: "
      "`NUTRIENT HEALTH` vs `NUTRITENT HEALTH` (typo present in live store), "
      "`MEN` vs `MEN'S HEALTH`, `GUT HEALTH` vs `GUT HEALTH & IMMUNE`. "
      "The Premium/Daily binary in the new brand system collapses all of these — no need to migrate the old grouping.")
    s("")
    s("4. **Commodity items off-brand.** NOURISHMENT contains Epsom salt, Himalayan salt, sodium bicarbonate, "
      "xylitol, dextrose. These are kitchen commodities, not supplements. Recommendation: RETIRE from Vivid storefront; "
      "keep on One Life if margin justifies.")
    s("")
    s("## Triage breakdown")
    s("")
    s("| Decision | Count | Meaning |")
    s("|---|---|---|")
    for k in ("KEEP_HERO", "KEEP", "MERGE", "REVIEW", "RETIRE"):
        s(f"| `{k}` | {by_decision.get(k, 0)} | see triage rules in `triage_catalogue.py` |")
    s("")
    s("## Sub-brand distribution (legacy)")
    s("")
    s("| Sub-brand | Count |")
    s("|---|---|")
    for sb, n in sorted(by_subbrand.items(), key=lambda x: -x[1]):
        s(f"| {sb} | {n} |")
    s("")
    s("## Files produced")
    s("")
    s("- `catalogue-audit.csv` — full 77-row audit with decision + rationale per SKU")
    s("- `curated-launch-range.csv` — proposed CURATED_PREMIUM launch range (in-stock KEEP + KEEP_HERO)")
    s("- `catalogue-raw-page{1,2}.json` — raw GraphQL responses")
    s("")
    s("## Open questions for HUMAN GATE 1")
    s("")
    s("1. Confirm `CATALOGUE_SCOPE = CURATED_PREMIUM` (default) — or override to `FULL_RANGE`?")
    s("2. Confirm hero-range gaps (Ashwagandha, Lion's Mane, Magnesium Glycinate, Vit C + Zinc): "
      "are these in production, in development, or to be sourced? **Launch dependency.**")
    s("3. For each `MERGE` family, pick the canonical size (e.g. Buffered C 90 vs 300 caps vs 150g vs 500g)?")
    s("4. Are NOURISHMENT commodities (salts/sugars) acceptable to RETIRE from Vivid storefront?")
    s("5. Of the `REVIEW` (DRAFT) items, which are abandoned vs in-progress?")
    s("")
    (RECON / "catalogue-summary.md").write_text("\n".join(summary))

    print(f"Wrote {len(rows)} rows -> {out_full}")
    print(f"Wrote {len(curated)} curated rows -> {out_curated}")
    print("Hero range present:", hero_found or "NONE")
    print("Hero range MISSING:", hero_gaps or "none")
    print("Decision counts:", dict(by_decision))

if __name__ == "__main__":
    main()
