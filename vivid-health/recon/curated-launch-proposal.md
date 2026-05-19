# Curated launch range — proposal for HUMAN GATE 1

**Scope parameter:** `CATALOGUE_SCOPE = CURATED_PREMIUM` (default per brief).
**Source:** `recon/catalogue-audit.csv` (77 SKUs from `vendor:"VIVID HEALTH"` on `onelifehealth.myshopify.com`).
**Brand tiers:** Premium (amber glass, hero) · Daily (bone HDPE, accessible).

---

## 1. Hero range (anchor — 5 SKUs)

The brief locks the hero range to **Ashwagandha · Lion's Mane · Magnesium Glycinate · Vitamin C + Zinc · Omega-3**.

| Hero SKU | In current catalogue? | Recommended canonical | Tier | Launch status |
|---|---|---|---|---|
| Omega-3 | **Yes** (2 SKUs) | Omega Oil 300 Caps (existing handle) | Premium | ✅ Ready to rebrand |
| Omega-3 (Daily) | Yes | Omega Oil 90 Caps | Daily | ✅ Ready to rebrand |
| Ashwagandha | **No** | — | Premium | 🛑 **BLOCKER — must source/manufacture** |
| Lion's Mane | **No** | — | Premium | 🛑 **BLOCKER — must source/manufacture** |
| Magnesium Glycinate | **No** | — | Premium | 🛑 **BLOCKER — must source/manufacture** |
| Vitamin C + Zinc | **No** (Buffered C exists, no Zinc co-formula) | — | Premium | 🛑 **BLOCKER — reformulate** |

> **Critical question for owner:** are the 4 missing hero SKUs in production, in formulation, or to be sourced? Storefront launch cannot ship the named anchor range without them. Two options if timeline pressure:
> 1. **Delay launch** until full hero range is manufactured (recommended for brand credibility).
> 2. **Soft-launch with partial hero range** (only Omega-3 + the best in-stock secondary SKUs) and reveal full hero range in a Phase-3.5 relaunch.

---

## 2. Recommended launch range (in-stock today)

These are all `KEEP` decisions with positive inventory. They form the launch SKU set alongside the hero range. ~30 SKUs — a curated, premium-feeling assortment, not a dump.

### Stress · Sleep · Focus (Premium)
| SKU | Inventory | Price (ZAR ex-VAT) |
|---|---|---|
| Griffonia (5-HTP) 60 Caps | 27 | R275 |
| Tranquil 60 Caps | 19 | R130 |
| GABA 150g | 15 | (in audit) |
| D-Ribose 150g | 16 | (in audit) |
| DMAE 150g | (low) | (in audit) |

### Immunity (Premium + Daily)
| SKU | Inventory | Notes |
|---|---|---|
| Astragalus 60 Caps | 35 | Best-stocked, lead immune SKU |
| Immune Plus 60 Caps | 30 | Combo formula |
| L-Lysine 60 Caps | 19 | |
| Mullein 60 Caps | 23 | |
| Quercetin Complex 60 Caps | 5 | Low stock — flag |
| Allergy Control 60 Caps | 5 | Low stock — flag |
| Buffered C 300 Caps *(canonical)* | 15 | Pick this over 90 Caps + 150g + 500g |

### Vitality · Body (Premium + Daily)
| SKU | Inventory | Notes |
|---|---|---|
| Coenzyme Q10 60 Caps | 27 | High value |
| Turmeric 300 Caps *(canonical)* | 20 | Replaces NUTRIENT vs NUTRITENT inconsistency |
| L-Glutamine 500g | 29 | |
| MSM 90 Caps *(canonical)* | 19 | Best-stocked of the MSM family |
| Garcinia Cambogia 60 Caps | 22 | |
| Liquorice Root 60 Caps | 21 | |
| Flexijoint 300 Caps | 8 | Low — flag |

### Gut & Cleanse (Premium)
| SKU | Inventory | Notes |
|---|---|---|
| Colon Flush Powder 135g *(canonical)* | 27 | Powder format chosen — better dosing |
| Black Walnut 60 Caps | 17 | |
| Clove 60 Caps | 22 | |
| Wormwood 60 Caps | 27 | |

### Women's (Daily)
| SKU | Inventory | Notes |
|---|---|---|
| Sage 60 Caps | 28 | |
| Angus Castus 60 Caps | 11 | |

### Bundles (rebrand all 3 — strong launch merchandising)
| SKU | Inventory | Notes |
|---|---|---|
| Vivid Allergy Stack | 0 | Rebrand + restock |
| Vivid Bone & Joint Pack | 0 | Rebrand + restock |
| Vivid Rest & Focus Stack | 0 | Rebrand + restock |

---

## 3. MERGE decisions (pick canonical size per family)

Recommendations — owner to confirm at gate.

| Family | Options in catalogue | Recommended canonical | Rationale |
|---|---|---|---|
| Buffered C | 90 caps / 300 caps / 150g / 500g | **300 caps Premium** + retire others | Capsules over loose powder for retail; 300 = best value tier |
| MSM | 90 caps / 300 caps / 150g / 500g | **90 caps Daily** | Most in-stock format; powders better as B2B/bulk |
| Cayenne | 90 caps / 300 caps / 250g | **300 caps Premium** | Highest inventory + value |
| Bone Supreme | 120 caps / 500 caps | **120 caps** | 500 caps is institutional, not retail |
| Barley Grass | 200g / 300 caps | **300 caps Daily** | Capsule format preferred |
| Colon Flush | 120 caps / 135g powder | **Powder Daily** | Powder dosing better for cleanse use case |
| Omega Oil | 90 caps / 300 caps | **Both — Daily 90 + Premium 300** | Two-tier opportunity in hero range |

---

## 4. RETIRE list (22 SKUs)

- **19 ARCHIVED** — already retired in source store; do not migrate.
- **5 commodity items** (Epsom salt, Himalayan salt, sodium bicarbonate, xylitol, dextrose) — off-brand for premium supplement house. Keep on One Life if margin justifies; do not place on Vivid storefront.
- **2 DRAFT empty-capsule SKUs** — packaging material, not finished product. Move to B2B channel if anywhere.

---

## 5. REVIEW (DRAFT — owner intent unclear)

| SKU | Question |
|---|---|
| NUTRITENT HEALTH - Cranberry 60 Capsules | Abandoned or in development? Recommend KEEP if going to production (women's UTI segment is high-value). |
| NUTRITENT HEALTH - Xylitol 2.5kg | Bulk commodity — likely RETIRE per rule above. Confirm. |

---

## 6. Margin awareness (information gap)

The Shopify Admin API does not expose COGS for vendor products from the One Life store side. **Owner must supply per-SKU COGS** (or a margin floor target) before final pricing decisions. Surfacing risks blind without it.

Recommendation: at HUMAN GATE 1, owner provides COGS for the proposed launch range so we can flag any SKU below a healthy retail floor before pricing the new storefront.

---

## 7. Net SKU count for launch

| Bucket | Count |
|---|---|
| Hero range (target) | 5 |
| Hero range (available today) | 1 (Omega-3, both sizes) |
| Secondary curated SKUs (in-stock KEEP, post-merge) | ~25 |
| Bundles | 3 |
| **Curated launch range total (if hero gaps closed)** | **~33 SKUs** |
| **Soft-launch range (today's reality)** | **~28 SKUs** |

vs the brief's "~100+ legacy SKUs" — a ~70% curation. This is consistent with the locked decision *"curate, don't dump"*.
