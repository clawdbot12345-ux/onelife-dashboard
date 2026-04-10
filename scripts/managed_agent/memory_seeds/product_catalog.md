# Onelife Product Catalog — Reference Notes

## How to find real products

The Onelife storefront search returns JSON-like HTML from:
```
https://onelife.co.za/search?q=<query>&type=product&view=json
```

Parse the HTML for `<a href="/collections/.../products/...">` patterns. Each
result includes product name, price, and image. Always verify the URL
resolves (HTTP 200) before including it in an email.

## Known top sellers (from Klaviyo Shopify integration + top_products data)

These products have been featured in past campaigns and have sales data:

### Metabolic / PCOS / GLP-1 category
- DELFRAN Pcositol — 30 Sachets (their #1 online product)
- DELFRAN Pcositol Orange & Lime — 30 Sachets
- DELFRAN Naleo Spectrum — 30 x 5g Scoops
- DELFRAN Family Starter Pack

### Berberine (existing "blood sugar" blog already covers these)
- GENOLOGIX Berberine 1000 mg — 90 Veg Capsules (R420)
- CHARAVA Berberine 500 mg — 60 Capsules (R629.99)
- WILLOW Berberine — 90 Capsules (R778)
- PRIMESELF Dihydro Berberine — 60 Veg Capsules (R340.27)
- BIOMAX Bio-Berberine Advanced — 60 Capsules (R585) [featured in blood-sugar-supplements blog]
- B.WELLNESS Weight Control + Energy — 30 Veg Capsules (R749.66) [also in blood-sugar blog]

### Magnesium
- WILLOW Magnesium Glycinate — 120 Capsules (R361) — best value
- SOLAL Magnesium Glycinate — 60 Tablets (R399)
- NOW Magnesium Glycinate with BioPerine — 60 Veg Capsules (R405)
- FORTIFOOD Magnesium Orotate — 120 Capsules (top seller from historical data)

### Immunity
- NOW Vitamin C-500 — 100 Tablets (R475)
- SWANSON Extra Strength Zinc Picolinate 50 mg — 60 Capsules (R238)
- NUTRIHERB Elderberry — 60 Capsules (R174.29)
- GREEN PHARM Elderberry No97 — 50ml (R112.13)
- DISO Vitamin C with Elderberry Extracts — 30 Dissolvable Strips (R362.25)
- GREEN PHARM Vitamin D No172 — 50ml (R112.13)

### Gut health
- PHYTOCEUTICS Bettergut Pre and Postbiotic — 30 Capsules (R435) — only dedicated postbiotic SKU

### Longevity (featured in winning NAD+ campaign)
- ALTWELL NMN500 Plus — 30 Capsules
- Your Wellbeing Resveratrol — 60 Capsules
- BIOMAX CoQ10 — 30 Capsules

## Known product gaps (opportunities)

These categories are thinly stocked and could drive new SKU decisions:
- **Postbiotics:** Only 1 dedicated product. Growing category.
- **Vitamin D3+K2 combos:** Search returns minimal results
- **Magnesium L-threonate:** Zero results (brain-specific, 74K monthly searches globally)
- **Creatine monohydrate:** Not explicitly searched — likely exists but worth checking
- **Collagen peptides:** Scheduled blog exists (Marine vs Bovine) — confirm products before publish

## How to verify a product is live

```bash
curl -s -o /dev/null -w "%{http_code}" <product_url>
# Expect 200
```

If a product page returns 404, the product has been discontinued or moved.
Find an alternative via search, update the blog frontmatter, and log the
change in memory (`/product_changes/<date>.md`).
