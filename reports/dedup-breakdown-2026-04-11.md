# Onelife Shopify — Exact Duplicate Dedup Breakdown

**Generated:** 2026-04-11 11:52 UTC
**Scope:** Live catalog only (`status=active` + `published_status=published`)
**Canonical rule:** images -> oldest -> highest stock -> lowest id
**Stock rule:** variant-level merge onto canonical by title key; unmatched stock flagged for manual review

## Summary

| Metric | Value |
|---|---:|
| Live products before dedup | 7,542 |
| Unique titles | 4,701 |
| Duplicate groups | 2,820 |
| **Products to archive** | **2,841** |
| **Products after dedup** | **4,701** |
| Stock units to transfer onto canonicals | 22 |
| Stock units flagged for manual review | 0 |
| Groups needing manual review | 0 |
| No-image edge-case groups | 24 |

### Duplicate group size distribution

| Group size | # groups | Products in these groups |
|---:|---:|---:|
| 4x | 10 | 40 |
| 3x | 1 | 3 |
| 2x | 2,809 | 5,618 |

### Canonical quality check

- Groups where the kept canonical HAS images: **2,796**
- Groups where NO member has an image (canonical chosen by stock/age): **24**

## Stock preservation plan

Before archiving, the apply script will transfer **22 units** of stock from soon-to-be-archived duplicates onto their canonical counterparts, variant-by-variant, matched on normalized variant title key.

**0 units** across **0 groups** could not be matched cleanly (variant title on the duplicate does not exist on the canonical). These are listed under 'Groups needing manual review' below and will NOT be auto-merged.

Variants with `inventory_quantity <= 0` are skipped entirely (no sellable stock to preserve).

## No-image edge-case groups

These 24 groups have **no images on any member**. The canonical was picked by stock then age. Review each one to decide whether to upload an image or kill the listing outright.

**1. KARA - Coconut Water - 1L** (3 listings)
- KEEP: `9132995674422` / `kara-coconut-water-1l` (1 variants, -1 units)
- ARCHIVE: `10655559975222` / `8938507849179` (1 variants, 0 units)
- ARCHIVE: `10655586353462` / `8997212611013` (1 variants, 0 units)

**2. ESCENTIA - Neem Oil - Cold Pressed - 1 Litre** (2 listings)
- KEEP: `8522463609142` / `escentia-neem-oil-cold-pressed-1-litre` (1 variants, 0 units)
- ARCHIVE: `10655629082934` / `600000019448` (1 variants, 0 units)

**3. ESCENTIA - Sea Buckthorn Fruit Essential Oil - 20ml** (2 listings)
- KEEP: `8499133677878` / `escentia-sea-buckthorn-fruit-essential-oil-20ml` (1 variants, 0 units)
- ARCHIVE: `10655635702070` / `6007930001965` (1 variants, 0 units)

**4. ESCENTIA - Soybean Cold Pressed Carrier Oil - 1 Litre** (2 listings)
- KEEP: `8522496770358` / `escentia-soybean-cold-pressed-carrier-oil-1-litre` (1 variants, 0 units)
- ARCHIVE: `10655628886326` / `600000076861` (1 variants, 0 units)

**5. ESCENTIA - Vitamin E Oil - 20ml** (2 listings)
- KEEP: `8499138068790` / `escentia-vitamin-e-oil-20ml` (1 variants, 2 units)
- ARCHIVE: `10655635570998` / `600000080123` (1 variants, 0 units)

**6. ESCENTIA - Wintergreen Essential Oil - 100ml** (2 listings)
- KEEP: `8518364660022` / `escentia-wintergreen-essential-oil-100ml` (1 variants, 0 units)
- ARCHIVE: `10655630655798` / `6000000170004` (1 variants, 0 units)

**7. GREEN PHARM - Artichoke No178 - 50ml** (2 listings)
- KEEP: `8378512081206` / `green-pharm-artichoke-no178-50ml` (1 variants, 2 units)
- ARCHIVE: `10655657722166` / `6000000013813` (1 variants, 0 units)

**8. GREEN PHARM - Black Walnut No82 - 50ml** (2 listings)
- KEEP: `8361125478710` / `green-pharm-black-walnut-no82-50ml` (1 variants, 2 units)
- ARCHIVE: `10655661654326` / `600000080441` (1 variants, 0 units)

**9. GREEN PHARM - Bugleweed No182 - 50ml** (2 listings)
- KEEP: `8378524205366` / `green-pharm-bugleweed-no182-50ml` (1 variants, 2 units)
- ARCHIVE: `10655657492790` / `737186120726` (1 variants, 0 units)

**10. GREEN PHARM - Cilantro No181 - 50ml** (2 listings)
- KEEP: `8378522239286` / `green-pharm-cilantro-no181-50ml` (1 variants, 3 units)
- ARCHIVE: `10655657558326` / `600000000645` (1 variants, 0 units)

**11. GREEN PHARM - Comfrey No174 - 50ml** (2 listings)
- KEEP: `8378503627062` / `green-pharm-comfrey-no174-50ml` (1 variants, 0 units)
- ARCHIVE: `10655657853238` / `600000013803` (1 variants, 0 units)

**12. GREEN PHARM - Horny Goats Weed No174 - 50ml** (2 listings)
- KEEP: `8378505101622` / `green-pharm-horny-goats-weed-no174-50ml` (1 variants, 1 units)
- ARCHIVE: `10655657820470` / `600000080443` (1 variants, 0 units)

**13. GREEN PHARM - Horseradish No173 - 50ml** (2 listings)
- KEEP: `8378501890358` / `green-pharm-horseradish-no173-50ml` (1 variants, 1 units)
- ARCHIVE: `10655657886006` / `600000002989` (1 variants, 0 units)

**14. GREEN PHARM - Mugwort No176 - 50ml** (2 listings)
- KEEP: `8378506805558` / `green-pharm-mugwort-no176-50ml` (1 variants, 2 units)
- ARCHIVE: `10655657787702` / `6000000584733` (1 variants, 0 units)

**15. GREEN PHARM - Pricklypear No177 - 50ml** (2 listings)
- KEEP: `8378508837174` / `green-pharm-pricklypear-no177-50ml` (1 variants, 2 units)
- ARCHIVE: `10655657754934` / `6000000826970` (1 variants, 0 units)

**16. GREEN PHARM - Rosehip No179 - 100ml** (2 listings)
- KEEP: `8378515685686` / `green-pharm-rosehip-no179-100ml` (1 variants, 1 units)
- ARCHIVE: `10655657656630` / `600000070048` (1 variants, 0 units)

**17. GREEN PHARM - Rosehip No179 - 50ml** (2 listings)
- KEEP: `8378513948982` / `green-pharm-rosehip-no179-50ml` (1 variants, 2 units)
- ARCHIVE: `10655657689398` / `600000000043` (1 variants, 0 units)

**18. GREEN PHARM - Vitamin C No180 - 100ml** (2 listings)
- KEEP: `8378521059638` / `green-pharm-vitamin-c-no180-100ml` (1 variants, 0 units)
- ARCHIVE: `10655657591094` / `600000082476` (1 variants, 0 units)

**19. GREEN PHARM - Vitamin C No180 - 50ml** (2 listings)
- KEEP: `8378519748918` / `green-pharm-vitamin-c-no180-50ml` (1 variants, 1 units)
- ARCHIVE: `10655657623862` / `6000000006488` (1 variants, 0 units)

**20. GREEN PHARM - Vitamin D No172 - 50ml** (2 listings)
- KEEP: `8378498351414` / `green-pharm-vitamin-d-no172-50ml` (1 variants, 1 units)
- ARCHIVE: `10655657918774` / `600000002404` (1 variants, 0 units)

**21. HAPPY EARTH PEOPLE - Dark Choc Chip Cookies - 180g** (2 listings)
- KEEP: `10655616500022` / `6001651103243` (1 variants, 0 units)
- ARCHIVE: `10655616532790` / `6001651102703` (1 variants, 0 units)

**22. HEEL - Traumeel S Gel - 50g** (2 listings)
- KEEP: `8476718596406` / `heel-traumeel-s-gel-50g` (1 variants, 0 units)
- ARCHIVE: `10655644811574` / `600966589204` (1 variants, 0 units)

**23. OILGROW - African Immortelle Essential Oil Blend - 10ml** (2 listings)
- KEEP: `8487734575414` / `oilgrow-african-immortelle-essential-oil-blend-10ml` (1 variants, 0 units)
- ARCHIVE: `10655642288438` / `600000017254` (1 variants, 0 units)

**24. VIRIDIAN - Rhodiola Rosea - 30 Veg Capsules** (2 listings)
- KEEP: `10655645794614` / `5060003598473` (1 variants, 0 units)
- ARCHIVE: `10655645827382` / `5060003598459` (1 variants, 0 units)

## Groups needing manual review (0 total — showing top 50 by unmatched qty)

_None — every duplicate variant matched a canonical variant cleanly._

## Sample of clean merges (top 20 by group size)

### 1. ESCENTIA - Frankincense Serrata Essential Oil - 10ml
_4 duplicate listings_

**KEEP** `8493025886518` `escentia-frankincense-serrata-essential-oil-10ml-v1` (has images, 1 img, 1 variants, 4 units) created 2023-07-12T11:55:54+02:00
**ARCHIVE** `8875800133942` `escentia-frankincense-serrata-essential-oil-10ml-v2` (img, 1 variants, 15 units)
**ARCHIVE** `10655592218934` `6009704873761` (no img, 1 variants, 0 units)
**ARCHIVE** `10655639011638` `6009704870753` (no img, 1 variants, 0 units)
- Stock transfer: 15 units across 1 variant(s)

### 2. ESCENTIA - Frankincense Serrata Essential Oil - 20ml
_4 duplicate listings_

**KEEP** `8499124306230` `escentia-frankincense-serrata-essential-oil-20ml-v1` (has images, 1 img, 1 variants, 2 units) created 2023-07-14T10:22:40+02:00
**ARCHIVE** `10094766194998` `escentia-frankincense-serrata-essential-oil-20ml-v2` (img, 1 variants, 3 units)
**ARCHIVE** `10655545819446` `6009704873778` (no img, 1 variants, 0 units)
**ARCHIVE** `10655635931446` `6009704870760` (no img, 1 variants, 0 units)
- Stock transfer: 3 units across 1 variant(s)

### 3. NEOGENESIS HEALTH - Nightcaps - 30 Capsules
_4 duplicate listings_

**KEEP** `8481796718902` `neogenesis-health-nightcaps-30-capsules-1` (has images, 1 img, 1 variants, 0 units) created 2023-07-08T10:30:50+02:00
**ARCHIVE** `8874167402806` `neogenesis-health-nightcaps-30-capsules` (img, 1 variants, 2 units)
**ARCHIVE** `10655592513846` `700371686093` (no img, 1 variants, 0 units)
**ARCHIVE** `10655644483894` `700371686086` (no img, 1 variants, 0 units)
- Stock transfer: 2 units across 1 variant(s)

### 4. REAL GOOD - Sunflower Seeds - 400g
_4 duplicate listings_

**KEEP** `9131055874358` `real-good-sunflower-seeds-400g-v1` (has images, 2 img, 1 variants, 2 units) created 2024-02-27T18:16:43+02:00
**ARCHIVE** `9131058266422` `real-good-sunflower-seeds-400g-v2` (img, 1 variants, 2 units)
**ARCHIVE** `10655561253174` `6009702593807` (no img, 1 variants, 0 units)
**ARCHIVE** `10655561318710` `6009702593838` (no img, 1 variants, 0 units)
- Stock transfer: 2 units across 1 variant(s)

### 5. BOODY - Ladies Black Classic Bikini - S
_4 duplicate listings_

**KEEP** `8950634938678` `boody-ladies-black-classic-bikini-s-v1` (has images, 3 img, 1 variants, 0 units) created 2023-12-07T09:02:08+02:00
**ARCHIVE** `9325173047606` `boody-ladies-black-classic-bikini-s-v2` (no img, 1 variants, 0 units)
**ARCHIVE** `10655555223862` `9340447025213` (no img, 1 variants, 0 units)
**ARCHIVE** `10655578456374` `9351383070038` (no img, 1 variants, 0 units)
- Stock transfer: 0 units (all duplicates were already empty)

### 6. BOODY - Men Light Grey Original Briefs - S
_4 duplicate listings_

**KEEP** `8956790374710` `boody-men-light-grey-original-briefs-s-v1` (has images, 3 img, 1 variants, 0 units) created 2023-12-11T09:34:31+02:00
**ARCHIVE** `8956791226678` `boody-men-light-grey-original-briefs-s-v2` (img, 1 variants, 0 units)
**ARCHIVE** `10655576064310` `9340447026524` (no img, 1 variants, 0 units)
**ARCHIVE** `10655576097078` `9340447026531` (no img, 1 variants, 0 units)
- Stock transfer: 0 units (all duplicates were already empty)

### 7. ESCENTIA - Caraway Essential Oil - 10ml
_4 duplicate listings_

**KEEP** `8492883935542` `escentia-caraway-essential-oil-10ml-v1` (has images, 1 img, 1 variants, 0 units) created 2023-07-12T10:46:10+02:00
**ARCHIVE** `8492888916278` `escentia-caraway-essential-oil-10ml-v2` (img, 1 variants, 0 units)
**ARCHIVE** `10655639830838` `6009704870302` (no img, 1 variants, 0 units)
**ARCHIVE** `10655639863606` `6009704870289` (no img, 1 variants, 0 units)
- Stock transfer: 0 units (all duplicates were already empty)

### 8. ESCENTIA - Cedarwood Essential Oil - 10ml
_4 duplicate listings_

**KEEP** `8492937707830` `escentia-cedarwood-essential-oil-10ml-v1` (has images, 1 img, 1 variants, 2 units) created 2023-07-12T11:12:12+02:00
**ARCHIVE** `8499088490806` `escentia-cedarwood-essential-oil-10ml-v2` (img, 1 variants, 0 units)
**ARCHIVE** `10655636357430` `6009704870395` (no img, 1 variants, 0 units)
**ARCHIVE** `10655639699766` `6009704870388` (no img, 1 variants, 0 units)
- Stock transfer: 0 units (all duplicates were already empty)

### 9. THURSDAY PLANTATION - Tea Tree Oil - 25ml
_4 duplicate listings_

**KEEP** `8446234001718` `thursday-plantation-tea-tree-oil-25ml-v1` (has images, 1 img, 1 variants, 8 units) created 2023-06-23T15:36:35+02:00
**ARCHIVE** `8446238327094` `thursday-plantation-tea-tree-oil-25ml-v2` (img, 1 variants, 0 units)
**ARCHIVE** `10655654347062` `931214600129` (no img, 1 variants, 0 units)
**ARCHIVE** `10655654379830` `9312146001300` (no img, 1 variants, 0 units)
- Stock transfer: 0 units (all duplicates were already empty)

### 10. VIRIDIAN - L-Lysine 500mg - 30 Veg Capsules
_4 duplicate listings_

**KEEP** `8473494520118` `viridian-l-lysine-500mg-30-veg-capsules-v1` (has images, 1 img, 1 variants, 0 units) created 2023-07-06T11:42:44+02:00
**ARCHIVE** `8473495666998` `viridian-l-lysine-500mg-30-veg-capsules-v2` (img, 1 variants, 0 units)
**ARCHIVE** `10655646187830` `5060003590323` (no img, 1 variants, 0 units)
**ARCHIVE** `10655646220598` `5060003590309` (no img, 1 variants, 0 units)
- Stock transfer: 0 units (all duplicates were already empty)

### 11. KARA - Coconut Water - 1L
_3 duplicate listings_

**KEEP** `9132995674422` `kara-coconut-water-1l` (NO IMAGE, 0 img, 1 variants, -1 units) created 2024-02-28T17:11:00+02:00
**ARCHIVE** `10655559975222` `8938507849179` (no img, 1 variants, 0 units)
**ARCHIVE** `10655586353462` `8997212611013` (no img, 1 variants, 0 units)
- Stock transfer: 0 units (all duplicates were already empty)

### 12. ALIVE LIFESTYLES - Alive Essential Aminos+ - 220g
_2 duplicate listings_

**KEEP** `9557244346678` `alive-lifestyles-alive-essential-aminos-220g` (has images, 16 img, 1 variants, 3 units) created 2024-08-07T12:49:21+02:00
**ARCHIVE** `10655550800182` `726872005850` (no img, 1 variants, 0 units)
- Stock transfer: 0 units (all duplicates were already empty)

### 13. ALMANS - Almond Bar - 50g
_2 duplicate listings_

**KEEP** `9031361823030` `almans-almond-bar-50g` (has images, 1 img, 1 variants, 15 units) created 2024-01-04T12:01:48+02:00
**ARCHIVE** `10655571968310` `6009609796226` (no img, 1 variants, 0 units)
- Stock transfer: 0 units (all duplicates were already empty)

### 14. ALMANS - Almonds Pink & White - 500g
_2 duplicate listings_

**KEEP** `9035167465782` `almans-almonds-pink-white-500g` (has images, 1 img, 1 variants, 0 units) created 2024-01-08T11:38:21+02:00
**ARCHIVE** `10655569641782` `6009609794949` (no img, 1 variants, 0 units)
- Stock transfer: 0 units (all duplicates were already empty)

### 15. ALMANS - Almonds Raw - 100g
_2 duplicate listings_

**KEEP** `9035159404854` `almans-almonds-raw-100g` (has images, 1 img, 1 variants, 12 units) created 2024-01-08T11:33:48+02:00
**ARCHIVE** `10655569740086` `6009609790170` (no img, 1 variants, 0 units)
- Stock transfer: 0 units (all duplicates were already empty)

### 16. ALMANS - Almonds Raw - 1kg
_2 duplicate listings_

**KEEP** `9035168809270` `almans-almonds-raw-1kg` (has images, 1 img, 1 variants, 1 units) created 2024-01-08T11:39:54+02:00
**ARCHIVE** `10655569609014` `6009609791122` (no img, 1 variants, 0 units)
- Stock transfer: 0 units (all duplicates were already empty)

### 17. ALMANS - Almonds Raw - 500g
_2 duplicate listings_

**KEEP** `9035196662070` `almans-almonds-raw-500g` (has images, 1 img, 1 variants, 10 units) created 2024-01-08T12:07:16+02:00
**ARCHIVE** `10655569412406` `6009609797544` (no img, 1 variants, 0 units)
- Stock transfer: 0 units (all duplicates were already empty)

### 18. ALMANS - Banana Chips - 150g
_2 duplicate listings_

**KEEP** `9035187061046` `almans-banana-chips-150g` (has images, 1 img, 1 variants, 7 units) created 2024-01-08T11:57:32+02:00
**ARCHIVE** `10655569445174` `6009609790422` (no img, 1 variants, 0 units)
- Stock transfer: 0 units (all duplicates were already empty)

### 19. ALMANS - Brazil Nuts - 100g
_2 duplicate listings_

**KEEP** `9031391641910` `almans-brazil-nuts-100g` (has images, 1 img, 1 variants, 13 units) created 2024-01-04T12:52:45+02:00
**ARCHIVE** `10655571902774` `6009609798824` (no img, 1 variants, 0 units)
- Stock transfer: 0 units (all duplicates were already empty)

### 20. ALMANS - Brazil Nuts - 1kg
_2 duplicate listings_

**KEEP** `9031391445302` `almans-brazil-nuts-1kg` (has images, 1 img, 1 variants, 2 units) created 2024-01-04T12:52:07+02:00
**ARCHIVE** `10655571935542` `6009609791740` (no img, 1 variants, 0 units)
- Stock transfer: 0 units (all duplicates were already empty)

## Next step

This is a **DRY RUN** — nothing has been changed in Shopify yet.

The planned apply script (`scripts/dedup_apply.py`, requires explicit `APPLY=true`) will:

1. For each group, execute every queued variant transfer
   (POST `/inventory_levels/adjust.json` on the online location) BEFORE archiving.
2. Set every non-canonical product to `status=archived` via PUT `/products/:id`.
3. Create 301 redirects from archived handles to the canonical handle.
4. Log every action to `reports/dedup-applied-YYYY-MM-DD.log`.
5. Skip groups flagged as `needs_review` for unmatched variants, or (if the
   operator chooses) transfer the matched variants only and leave the rest.

All archiving is reversible: setting `status=active` restores the listing.
Inventory transfers are NOT reversible automatically — they are real Shopify writes.