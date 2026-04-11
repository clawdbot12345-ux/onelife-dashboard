# Onelife Shopify — Exact Duplicate Dedup Breakdown

**Generated:** 2026-04-11 11:07 UTC
**Scope:** Live catalog only (`status=active` + `published_status=published`)
**Rule:** Keep the one with images → fall back to highest inventory → fall back to oldest

## Summary

| Metric | Count |
|---|---:|
| Live products before dedup | 7,585 |
| Unique titles | 4,702 |
| Duplicate groups | 2,862 |
| **Products to archive** | **2,883** |
| **Products after dedup** | **4,702** |

### Duplicate group size distribution

| Group size | # groups | Products in these groups |
|---:|---:|---:|
| 4× | 10 | 40 |
| 3× | 1 | 3 |
| 2× | 2,851 | 5,702 |

### Canonical quality check

- ✓ Groups where the kept (canonical) product HAS images: **2,838**
- ⚠ Groups where NO member has an image (canonical chosen by inventory/age): **24**

## Sample of 30 duplicate groups (showing decision for each)

### 1. BOODY - Ladies Black Classic Bikini - S
_4 duplicate listings in live catalog_

**✅ KEEP** (canonical)
- id: `8950634938678`
- handle: `boody-ladies-black-classic-bikini-s-v1`
- 🖼 has images (3 img, 1 variants, 0 units in stock)
- created: 2023-12-07T09:02:08+02:00

**📦 ARCHIVE**
- id: `9325173047606`
- handle: `boody-ladies-black-classic-bikini-s-v2`
- ❌ 0 images, 1 variants, 0 units
- created: 2024-04-23T17:38:07+02:00

**📦 ARCHIVE**
- id: `10655555223862`
- handle: `9340447025213`
- ❌ 0 images, 1 variants, 0 units
- created: 2026-04-07T10:02:28+02:00

**📦 ARCHIVE**
- id: `10655578456374`
- handle: `9351383070038`
- ❌ 0 images, 1 variants, 0 units
- created: 2026-04-07T10:10:16+02:00

### 2. BOODY - Men Light Grey Original Briefs - S
_4 duplicate listings in live catalog_

**✅ KEEP** (canonical)
- id: `8956790374710`
- handle: `boody-men-light-grey-original-briefs-s-v1`
- 🖼 has images (3 img, 1 variants, 0 units in stock)
- created: 2023-12-11T09:34:31+02:00

**📦 ARCHIVE**
- id: `8956791226678`
- handle: `boody-men-light-grey-original-briefs-s-v2`
- 🖼 3 images, 1 variants, 0 units
- created: 2023-12-11T09:35:16+02:00

**📦 ARCHIVE**
- id: `10655576064310`
- handle: `9340447026524`
- ❌ 0 images, 1 variants, 0 units
- created: 2026-04-07T10:09:30+02:00

**📦 ARCHIVE**
- id: `10655576097078`
- handle: `9340447026531`
- ❌ 0 images, 1 variants, 0 units
- created: 2026-04-07T10:09:31+02:00

### 3. ESCENTIA - Caraway Essential Oil - 10ml
_4 duplicate listings in live catalog_

**✅ KEEP** (canonical)
- id: `8492883935542`
- handle: `escentia-caraway-essential-oil-10ml-v1`
- 🖼 has images (1 img, 1 variants, 0 units in stock)
- created: 2023-07-12T10:46:10+02:00

**📦 ARCHIVE**
- id: `8492888916278`
- handle: `escentia-caraway-essential-oil-10ml-v2`
- 🖼 1 images, 1 variants, 0 units
- created: 2023-07-12T10:49:03+02:00

**📦 ARCHIVE**
- id: `10655639830838`
- handle: `6009704870302`
- ❌ 0 images, 1 variants, 0 units
- created: 2026-04-07T10:31:35+02:00

**📦 ARCHIVE**
- id: `10655639863606`
- handle: `6009704870289`
- ❌ 0 images, 1 variants, 0 units
- created: 2026-04-07T10:31:36+02:00

### 4. ESCENTIA - Cedarwood Essential Oil - 10ml
_4 duplicate listings in live catalog_

**✅ KEEP** (canonical)
- id: `8492937707830`
- handle: `escentia-cedarwood-essential-oil-10ml-v1`
- 🖼 has images (1 img, 1 variants, 2 units in stock)
- created: 2023-07-12T11:12:12+02:00

**📦 ARCHIVE**
- id: `8499088490806`
- handle: `escentia-cedarwood-essential-oil-10ml-v2`
- 🖼 1 images, 1 variants, 0 units
- created: 2023-07-14T09:49:03+02:00

**📦 ARCHIVE**
- id: `10655636357430`
- handle: `6009704870395`
- ❌ 0 images, 1 variants, 0 units
- created: 2026-04-07T10:30:15+02:00

**📦 ARCHIVE**
- id: `10655639699766`
- handle: `6009704870388`
- ❌ 0 images, 1 variants, 0 units
- created: 2026-04-07T10:31:32+02:00

### 5. ESCENTIA - Frankincense Serrata Essential Oil - 10ml
_4 duplicate listings in live catalog_

**✅ KEEP** (canonical)
- id: `8875800133942`
- handle: `escentia-frankincense-serrata-essential-oil-10ml-v2`
- 🖼 has images (1 img, 1 variants, 15 units in stock)
- created: 2023-10-27T11:32:54+02:00

**📦 ARCHIVE**
- id: `8493025886518`
- handle: `escentia-frankincense-serrata-essential-oil-10ml-v1`
- 🖼 1 images, 1 variants, 4 units
- created: 2023-07-12T11:55:54+02:00

**📦 ARCHIVE**
- id: `10655592218934`
- handle: `6009704873761`
- ❌ 0 images, 1 variants, 0 units
- created: 2026-04-07T10:15:10+02:00

**📦 ARCHIVE**
- id: `10655639011638`
- handle: `6009704870753`
- ❌ 0 images, 1 variants, 0 units
- created: 2026-04-07T10:31:15+02:00

### 6. ESCENTIA - Frankincense Serrata Essential Oil - 20ml
_4 duplicate listings in live catalog_

**✅ KEEP** (canonical)
- id: `10094766194998`
- handle: `escentia-frankincense-serrata-essential-oil-20ml-v2`
- 🖼 has images (1 img, 1 variants, 3 units in stock)
- created: 2025-02-13T11:10:25+02:00

**📦 ARCHIVE**
- id: `8499124306230`
- handle: `escentia-frankincense-serrata-essential-oil-20ml-v1`
- 🖼 1 images, 1 variants, 2 units
- created: 2023-07-14T10:22:40+02:00

**📦 ARCHIVE**
- id: `10655545819446`
- handle: `6009704873778`
- ❌ 0 images, 1 variants, 0 units
- created: 2026-04-07T09:58:50+02:00

**📦 ARCHIVE**
- id: `10655635931446`
- handle: `6009704870760`
- ❌ 0 images, 1 variants, 0 units
- created: 2026-04-07T10:30:06+02:00

### 7. NEOGENESIS HEALTH - Nightcaps - 30 Capsules
_4 duplicate listings in live catalog_

**✅ KEEP** (canonical)
- id: `8874167402806`
- handle: `neogenesis-health-nightcaps-30-capsules`
- 🖼 has images (1 img, 1 variants, 2 units in stock)
- created: 2023-10-26T16:47:24+02:00

**📦 ARCHIVE**
- id: `8481796718902`
- handle: `neogenesis-health-nightcaps-30-capsules-1`
- 🖼 1 images, 1 variants, 0 units
- created: 2023-07-08T10:30:50+02:00

**📦 ARCHIVE**
- id: `10655592513846`
- handle: `700371686093`
- ❌ 0 images, 1 variants, 0 units
- created: 2026-04-07T10:15:16+02:00

**📦 ARCHIVE**
- id: `10655644483894`
- handle: `700371686086`
- ❌ 0 images, 1 variants, 0 units
- created: 2026-04-07T10:33:20+02:00

### 8. REAL GOOD - Sunflower Seeds - 400g
_4 duplicate listings in live catalog_

**✅ KEEP** (canonical)
- id: `9131055874358`
- handle: `real-good-sunflower-seeds-400g-v1`
- 🖼 has images (2 img, 1 variants, 2 units in stock)
- created: 2024-02-27T18:16:43+02:00

**📦 ARCHIVE**
- id: `9131058266422`
- handle: `real-good-sunflower-seeds-400g-v2`
- 🖼 2 images, 1 variants, 2 units
- created: 2024-02-27T18:18:43+02:00

**📦 ARCHIVE**
- id: `10655561253174`
- handle: `6009702593807`
- ❌ 0 images, 1 variants, 0 units
- created: 2026-04-07T10:04:29+02:00

**📦 ARCHIVE**
- id: `10655561318710`
- handle: `6009702593838`
- ❌ 0 images, 1 variants, 0 units
- created: 2026-04-07T10:04:30+02:00

### 9. THURSDAY PLANTATION - Tea Tree Oil - 25ml
_4 duplicate listings in live catalog_

**✅ KEEP** (canonical)
- id: `8446234001718`
- handle: `thursday-plantation-tea-tree-oil-25ml-v1`
- 🖼 has images (1 img, 1 variants, 8 units in stock)
- created: 2023-06-23T15:36:35+02:00

**📦 ARCHIVE**
- id: `8446238327094`
- handle: `thursday-plantation-tea-tree-oil-25ml-v2`
- 🖼 1 images, 1 variants, 0 units
- created: 2023-06-23T15:39:29+02:00

**📦 ARCHIVE**
- id: `10655654347062`
- handle: `931214600129`
- ❌ 0 images, 1 variants, 0 units
- created: 2026-04-07T10:37:06+02:00

**📦 ARCHIVE**
- id: `10655654379830`
- handle: `9312146001300`
- ❌ 0 images, 1 variants, 0 units
- created: 2026-04-07T10:37:07+02:00

### 10. VIRIDIAN - L-Lysine 500mg - 30 Veg Capsules
_4 duplicate listings in live catalog_

**✅ KEEP** (canonical)
- id: `8473494520118`
- handle: `viridian-l-lysine-500mg-30-veg-capsules-v1`
- 🖼 has images (1 img, 1 variants, 0 units in stock)
- created: 2023-07-06T11:42:44+02:00

**📦 ARCHIVE**
- id: `8473495666998`
- handle: `viridian-l-lysine-500mg-30-veg-capsules-v2`
- 🖼 1 images, 1 variants, 0 units
- created: 2023-07-06T11:44:10+02:00

**📦 ARCHIVE**
- id: `10655646187830`
- handle: `5060003590323`
- ❌ 0 images, 1 variants, 0 units
- created: 2026-04-07T10:33:51+02:00

**📦 ARCHIVE**
- id: `10655646220598`
- handle: `5060003590309`
- ❌ 0 images, 1 variants, 0 units
- created: 2026-04-07T10:33:52+02:00

### 11. KARA - Coconut Water - 1L
_3 duplicate listings in live catalog_

**✅ KEEP** (canonical)
- id: `10655559975222`
- handle: `8938507849179`
- ⚠ no image (0 img, 1 variants, 0 units in stock)
- created: 2026-04-07T10:04:04+02:00

**📦 ARCHIVE**
- id: `9132995674422`
- handle: `kara-coconut-water-1l`
- ❌ 0 images, 1 variants, -1 units
- created: 2024-02-28T17:11:00+02:00

**📦 ARCHIVE**
- id: `10655586353462`
- handle: `8997212611013`
- ❌ 0 images, 1 variants, 0 units
- created: 2026-04-07T10:13:06+02:00

### 12. A.VOGEL - Echinaforce® Echinacea Tablets - 120 Tablets
_2 duplicate listings in live catalog_

**✅ KEEP** (canonical)
- id: `8387632300342`
- handle: `avogel-echinaforce-echinacea-tablets-120-tablets`
- 🖼 has images (1 img, 1 variants, 3 units in stock)
- created: 2023-05-29T13:45:19+02:00

**📦 ARCHIVE**
- id: `10655656509750`
- handle: `6007650000675`
- ❌ 0 images, 1 variants, 0 units
- created: 2026-04-07T10:37:54+02:00

### 13. A.VOGEL - Echinaforce® Echinacea Tablets - 60 Tablets
_2 duplicate listings in live catalog_

**✅ KEEP** (canonical)
- id: `8387628564790`
- handle: `avogel-echinaforce-echinacea-tablets-60-tablets`
- 🖼 has images (1 img, 1 variants, 11 units in stock)
- created: 2023-05-29T13:41:49+02:00

**📦 ARCHIVE**
- id: `10655656542518`
- handle: `6007650000552`
- ❌ 0 images, 1 variants, 0 units
- created: 2026-04-07T10:37:55+02:00

### 14. A.VOGEL - Echinaforce® Forte Echinacea - 30 Tablets
_2 duplicate listings in live catalog_

**✅ KEEP** (canonical)
- id: `8387655008566`
- handle: `avogel-echinaforce-forte-echinacea-30-tablets`
- 🖼 has images (1 img, 1 variants, 13 units in stock)
- created: 2023-05-29T14:01:58+02:00

**📦 ARCHIVE**
- id: `10655656476982`
- handle: `6007650001030`
- ❌ 0 images, 1 variants, 0 units
- created: 2026-04-07T10:37:54+02:00

### 15. A.VOGEL - Echinaforce® Junior Tablets - 120 Chewable Tablets
_2 duplicate listings in live catalog_

**✅ KEEP** (canonical)
- id: `8387532390710`
- handle: `avogel-echinaforce-junior-tablets-120-chewable-tablets`
- 🖼 has images (2 img, 1 variants, 12 units in stock)
- created: 2023-05-29T12:48:36+02:00

**📦 ARCHIVE**
- id: `10655656575286`
- handle: `6007650000798`
- ❌ 0 images, 1 variants, 0 units
- created: 2026-04-07T10:37:56+02:00

### 16. A.VOGEL - Ginkgoforce Drops - 30ml
_2 duplicate listings in live catalog_

**✅ KEEP** (canonical)
- id: `8409953567030`
- handle: `avogel-ginkgoforce-drops-30ml`
- 🖼 has images (1 img, 1 variants, 0 units in stock)
- created: 2023-06-07T14:53:38+02:00

**📦 ARCHIVE**
- id: `10655656313142`
- handle: `6007650000354`
- ❌ 0 images, 1 variants, 0 units
- created: 2026-04-07T10:37:50+02:00

### 17. A.VOGEL - Haemorrhoid Formula - 30 ml
_2 duplicate listings in live catalog_

**✅ KEEP** (canonical)
- id: `8409970114870`
- handle: `avogel-haemorrhoid-formula-30-ml`
- 🖼 has images (2 img, 1 variants, 2 units in stock)
- created: 2023-06-07T14:56:42+02:00

**📦 ARCHIVE**
- id: `10655656280374`
- handle: `6007650001252`
- ❌ 0 images, 1 variants, 0 units
- created: 2026-04-07T10:37:49+02:00

### 18. A.VOGEL - Herbamare Spicy - 125g
_2 duplicate listings in live catalog_

**✅ KEEP** (canonical)
- id: `8447004705078`
- handle: `avogel-herbamare-spicy-125g`
- 🖼 has images (1 img, 1 variants, 4 units in stock)
- created: 2023-06-24T09:31:51+02:00

**📦 ARCHIVE**
- id: `10655653986614`
- handle: `7610313424825`
- ❌ 0 images, 1 variants, 0 units
- created: 2026-04-07T10:36:58+02:00

### 19. A.VOGEL - Herbamare® Original - 125g
_2 duplicate listings in live catalog_

**✅ KEEP** (canonical)
- id: `8436622262582`
- handle: `avogel-herbamare-original-125g`
- 🖼 has images (1 img, 1 variants, 3 units in stock)
- created: 2023-06-19T16:36:28+02:00

**📦 ARCHIVE**
- id: `10655655526710`
- handle: `7610313426706`
- ❌ 0 images, 1 variants, 0 units
- created: 2026-04-07T10:37:32+02:00

### 20. A.VOGEL - Herbamare® Original - 250g
_2 duplicate listings in live catalog_

**✅ KEEP** (canonical)
- id: `8436616266038`
- handle: `avogel-herbamare-original-250g`
- 🖼 has images (1 img, 1 variants, 13 units in stock)
- created: 2023-06-19T16:33:30+02:00

**📦 ARCHIVE**
- id: `10655655559478`
- handle: `7610313424795`
- ❌ 0 images, 1 variants, 0 units
- created: 2026-04-07T10:37:33+02:00

### 21. A.VOGEL - Herbamare® Original - 500g
_2 duplicate listings in live catalog_

**✅ KEEP** (canonical)
- id: `8439528784182`
- handle: `avogel-herbamare-original-500g`
- 🖼 has images (1 img, 1 variants, 11 units in stock)
- created: 2023-06-20T08:03:37+02:00

**📦 ARCHIVE**
- id: `10655655493942`
- handle: `7610313424771`
- ❌ 0 images, 1 variants, 0 units
- created: 2026-04-07T10:37:31+02:00

### 22. A.VOGEL - Indigestion Formula - 30ml
_2 duplicate listings in live catalog_

**✅ KEEP** (canonical)
- id: `8410004422966`
- handle: `avogel-indigestion-formula-30ml`
- 🖼 has images (1 img, 1 variants, 3 units in stock)
- created: 2023-06-07T15:03:31+02:00

**📦 ARCHIVE**
- id: `10655656247606`
- handle: `6007650000941`
- ❌ 0 images, 1 variants, 0 units
- created: 2026-04-07T10:37:49+02:00

### 23. A.VOGEL - Influaforce - 30ml
_2 duplicate listings in live catalog_

**✅ KEEP** (canonical)
- id: `8446267490614`
- handle: `avogel-influaforce-30ml`
- 🖼 has images (1 img, 1 variants, 0 units in stock)
- created: 2023-06-23T16:09:15+02:00

**📦 ARCHIVE**
- id: `10655654281526`
- handle: `6007650001283`
- ❌ 0 images, 1 variants, 0 units
- created: 2026-04-07T10:37:04+02:00

### 24. A.VOGEL - Kelpamare
_2 duplicate listings in live catalog_

**✅ KEEP** (canonical)
- id: `8447002378550`
- handle: `avogel-kelpamare`
- 🖼 has images (1 img, 1 variants, 0 units in stock)
- created: 2023-06-24T09:28:58+02:00

**📦 ARCHIVE**
- id: `10655654019382`
- handle: `7610313412433`
- ❌ 0 images, 1 variants, 0 units
- created: 2026-04-07T10:36:58+02:00

### 25. A.VOGEL - Liver and Gall Bladder Formula - 30ml
_2 duplicate listings in live catalog_

**✅ KEEP** (canonical)
- id: `8411709636918`
- handle: `avogel-liver-and-gall-bladder-formula-30ml`
- 🖼 has images (1 img, 1 variants, 2 units in stock)
- created: 2023-06-08T07:31:39+02:00

**📦 ARCHIVE**
- id: `10655656214838`
- handle: `6007650001269`
- ❌ 0 images, 1 variants, -1 units
- created: 2026-04-07T10:37:48+02:00

### 26. A.VOGEL - Menoforce - 30 Tablets (Previously named Hot Flush & Night S
_2 duplicate listings in live catalog_

**✅ KEEP** (canonical)
- id: `8411716223286`
- handle: `avogel-menoforce-30-tablets-previously-named-hot-flush-night-sweats`
- 🖼 has images (1 img, 1 variants, 8 units in stock)
- created: 2023-06-08T07:35:01+02:00

**📦 ARCHIVE**
- id: `10655656182070`
- handle: `6007650001368`
- ❌ 0 images, 1 variants, 0 units
- created: 2026-04-07T10:37:47+02:00

### 27. A.VOGEL - Menopause Formula - 30ml
_2 duplicate listings in live catalog_

**✅ KEEP** (canonical)
- id: `8411730084150`
- handle: `avogel-menopause-formula-30ml`
- 🖼 has images (1 img, 1 variants, 0 units in stock)
- created: 2023-06-08T07:42:45+02:00

**📦 ARCHIVE**
- id: `10655656149302`
- handle: `6007650001290`
- ❌ 0 images, 1 variants, 0 units
- created: 2026-04-07T10:37:46+02:00

### 28. A.VOGEL - Menstruation Formula - 30ml
_2 duplicate listings in live catalog_

**✅ KEEP** (canonical)
- id: `8411736670518`
- handle: `avogel-menstruation-formula-30ml`
- 🖼 has images (1 img, 1 variants, 1 units in stock)
- created: 2023-06-08T07:47:27+02:00

**📦 ARCHIVE**
- id: `10655656116534`
- handle: `6007650001306`
- ❌ 0 images, 1 variants, 0 units
- created: 2026-04-07T10:37:46+02:00

### 29. A.VOGEL - Migraine Formula - 30ml
_2 duplicate listings in live catalog_

**✅ KEEP** (canonical)
- id: `8411742601526`
- handle: `avogel-migraine-formula-30ml`
- 🖼 has images (1 img, 1 variants, 0 units in stock)
- created: 2023-06-08T07:51:40+02:00

**📦 ARCHIVE**
- id: `10655656083766`
- handle: `6007650000910`
- ❌ 0 images, 1 variants, 0 units
- created: 2026-04-07T10:37:45+02:00

### 30. A.VOGEL - Molkosan® Original - 200ml
_2 duplicate listings in live catalog_

**✅ KEEP** (canonical)
- id: `8428658229558`
- handle: `avogel-molkosan-original-200ml`
- 🖼 has images (1 img, 1 variants, 7 units in stock)
- created: 2023-06-15T11:47:49+02:00

**📦 ARCHIVE**
- id: `10655656018230`
- handle: `7610313411597`
- ❌ 0 images, 1 variants, 0 units
- created: 2026-04-07T10:37:44+02:00

*(...2,832 more groups in the JSON file)*

## Next step

This is a **DRY RUN** — nothing has been changed in Shopify yet.

To execute: run `scripts/dedup_apply.py` (requires explicit `APPLY=true`), which will:
1. For each group, set the 'archive' products to `status=archived` via PUT /products/:id
2. Create 301 redirects from the archived product URLs to the canonical URL
3. Log every action to `reports/dedup-applied-YYYY-MM-DD.log`
4. All changes are reversible by setting `status=active` again on the archived products