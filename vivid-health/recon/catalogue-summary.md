# Phase 0b — Catalogue audit summary

**Source:** Shopify store `onelifehealth` / `onelife.co.za`. Filter: `vendor:"VIVID HEALTH"`.
**Total products:** **77** (2 hero · 35 keep · 16 merge · 2 review · 22 retire)

## Critical findings

1. **Hero-range coverage gap.** Brief specifies 5 hero SKUs: Ashwagandha, Lion's Mane, Magnesium Glycinate, Vitamin C + Zinc, Omega-3. Currently in catalogue: Omega-3. **Missing: Ashwagandha, Lion's Mane, Magnesium Glycinate, Vitamin C + Zinc.** These must be sourced/manufactured before the curated launch can ship its anchor range.

2. **Stock health.** 17/53 active SKUs are at zero inventory. This is a manufacturing/operations issue, not a digital one — but the storefront cannot launch on an empty shelf.

3. **Sub-brand taxonomy is inconsistent.** Variants observed: `NUTRIENT HEALTH` vs `NUTRITENT HEALTH` (typo present in live store), `MEN` vs `MEN'S HEALTH`, `GUT HEALTH` vs `GUT HEALTH & IMMUNE`. The Premium/Daily binary in the new brand system collapses all of these — no need to migrate the old grouping.

4. **Commodity items off-brand.** NOURISHMENT contains Epsom salt, Himalayan salt, sodium bicarbonate, xylitol, dextrose. These are kitchen commodities, not supplements. Recommendation: RETIRE from Vivid storefront; keep on One Life if margin justifies.

## Triage breakdown

| Decision | Count | Meaning |
|---|---|---|
| `KEEP_HERO` | 2 | see triage rules in `triage_catalogue.py` |
| `KEEP` | 35 | see triage rules in `triage_catalogue.py` |
| `MERGE` | 16 | see triage rules in `triage_catalogue.py` |
| `REVIEW` | 2 | see triage rules in `triage_catalogue.py` |
| `RETIRE` | 22 | see triage rules in `triage_catalogue.py` |

## Sub-brand distribution (legacy)

| Sub-brand | Count |
|---|---|
| VIVID NOURISHMENT | 20 |
| IMMUNE | 13 |
| VIVID BODY | 12 |
| STAY VIVID | 8 |
| GUT HEALTH | 4 |
| NUTRITENT HEALTH | 4 |
| BUNDLE/OTHER | 3 |
| WOMAN | 3 |
| MEN | 2 |
| NUTRIENT HEALTH | 2 |
| PHYSICAL HEALTH | 2 |
| GUT HEALTH & IMMUNE | 1 |
| CAPSULES SIZE 0 | 1 |
| CAPSULES SIZE 00 | 1 |
| MEN’S HEALTH | 1 |

## Files produced

- `catalogue-audit.csv` — full 77-row audit with decision + rationale per SKU
- `curated-launch-range.csv` — proposed CURATED_PREMIUM launch range (in-stock KEEP + KEEP_HERO)
- `catalogue-raw-page{1,2}.json` — raw GraphQL responses

## Open questions for HUMAN GATE 1

1. Confirm `CATALOGUE_SCOPE = CURATED_PREMIUM` (default) — or override to `FULL_RANGE`?
2. Confirm hero-range gaps (Ashwagandha, Lion's Mane, Magnesium Glycinate, Vit C + Zinc): are these in production, in development, or to be sourced? **Launch dependency.**
3. For each `MERGE` family, pick the canonical size (e.g. Buffered C 90 vs 300 caps vs 150g vs 500g)?
4. Are NOURISHMENT commodities (salts/sugars) acceptable to RETIRE from Vivid storefront?
5. Of the `REVIEW` (DRAFT) items, which are abandoned vs in-progress?
