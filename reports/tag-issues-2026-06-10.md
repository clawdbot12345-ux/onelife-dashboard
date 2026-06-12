# Suspicious Tag Inconsistencies — 2026-06-10
Flagged for human review during the dietary-tag audit of 4,256 ACTIVE products.
Nothing below was changed — per safety rules, no tags were removed or renamed.

## 1. Casing variants of the same dietary tag (filter-splitting risk)
The store convention is lowercase-hyphenated dietary tags, but a handful of products
carry Title Case variants. Shopify tag filters are case-sensitive, so these products
will NOT appear under the dominant lowercase filter badge.

| Variant pair | Counts | Example product |
|---|---|---|
| `Vegan` vs `vegan` | 1 vs 2,159 | 10605700448566 "NMN 1000mg - 60 Vegetarian Capsules" has `Vegan` |
| `Vegetarian` vs `vegetarian` | 2 vs 2,136 | 10605700448566 "NMN 1000mg - 60 Vegetarian Capsules" has `Vegetarian` |
| `Sugar-Free` vs `sugar-free` | 1 vs 2,525 | 10605695566134 "DripDrop Electrolyte Hydration Sticks - Sugar-Free Box" has `Sugar-Free` |

Recommendation: consolidate the 1–2 Title Case outliers to the lowercase convention
(requires a remove+add, which was out of scope for this audit).

## 2. New tags added today use spec casing, not store convention
Per the audit spec, today's additions were `Organic` (23 products) and `Keto` (1 product).
The existing store convention is lowercase `organic` (245 products) and `keto` (69 products).
This creates two more casing splits identical to section 1. If the storefront filter keys on
`organic`/`keto`, consider consolidating the 24 new Title Case tags to lowercase.

## 3. Parallel/duplicate dietary facets in the `Food>` hierarchy
- `Food>Gluten Free` (135 products) duplicates the meaning of `gluten-free` (2,998)
- `Food>Vegan` (149 products) duplicates the meaning of `vegan` (2,159)
These hierarchical tags coexist with the flat dietary tags; verify which one the
storefront filters actually use and whether both are intended.

## 4. Whitespace anomalies in hierarchy tags (likely typos)
- `Food >Baking` (56 products) — stray space before `>`
- `Food> Beverages` (255), `Food> Milk Alternatives` (14), `Food> Spices` (64) — stray space after `>`
These differ from the clean `Food>Oils`, `Food>Fruit`, etc. pattern and would split collections/filters.

## 5. Spelling issue
- `Conditions>Pain&Inflamation` (242 products) — "Inflamation" should be "Inflammation".
  Consistent across all 242 uses, so filters still work, but it is misspelled site-wide.

## 6. Semantically questionable additions made today (rule-compliant but worth review)
The audit rule was literal title-substring matching, which these satisfy, but a human
should confirm the badge is appropriate:
- `Organic` added to 3x GAIA ORGANICS Hydrogen Peroxide products (8053024981302,
  8053025079606, 8053025177910) — "organic" comes from the BRAND name; hydrogen peroxide
  is not an organic-certified food product.
- `Organic` added to 19x ORGANIC CHOICE and 1x PLUSH ORGANICS products — also brand-name
  driven, though most other products of these brands already carried lowercase `organic`,
  so this matches existing store practice.
- `Keto` added to 8053055095094 "G.I.NUTRILEAN - Raspberry Ketones 60 Capsules" —
  "keto" matched inside "Ketones"; raspberry ketones are a weight-loss compound, not
  necessarily a keto-diet product.
