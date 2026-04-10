# Blog Content Queue

This directory is the source of truth for Onelife Health blog content. The weekly publish workflow picks the next unpublished `.md` file and publishes it to Shopify + Klaviyo.

## How it works

1. Write a blog in markdown with YAML frontmatter (see `2026-04-berberine-natures-ozempic.md` for the template).
2. Name the file `YYYY-MM-NN-slug.md` so they sort chronologically.
3. The Monday 07:00 SAST workflow picks the oldest unpublished file and ships it.
4. After publishing, the workflow renames it to `*.published.md` so it's skipped next time.

## Frontmatter schema

```yaml
title: Blog title
slug: url-slug
handle: health-wellness-hub   # Shopify blog handle
author: Onelife Health
excerpt: Email hero / SEO description
tags: comma,separated,tags
subject: Email subject line
preview: Email preview text
campaign_segment: Xrk5jD      # Klaviyo list/segment ID
send_offset_days: 2           # Days from now to schedule
products:
  - name: Product Name
    price: R420
    url: https://onelife.co.za/products/...
    badge: BEST VALUE          # Small tag above product
    blurb: Short description
```

## 12-week content calendar

| Week | Pillar | Blog Topic |
|---|---|---|
| 1 (current) | Metabolic | Berberine — "Nature's Ozempic" |
| 2 | Sleep/Stress | Magnesium Glycinate vs Other Forms |
| 3 | Immunity | SA Winter Immunity Stack |
| 4 | Women's Health | PCOSITOL vs Imported Inositol |
| 5 | Metabolic | Vitamin D in SA — Why Even Sunny Countries Have A Problem |
| 6 | Gut Health | Postbiotics: Beyond Probiotics |
| 7 | Sleep/Stress | The 3-Supplement Sleep Stack |
| 8 | Women's Health | Collagen: Marine vs Bovine |
| 9 | Immunity | Cold & Flu Prevention — What Actually Works |
| 10 | Kids | Kids' Winter Immunity Family Plan |
| 11 | Sleep/Stress | Adaptogens for Winter Blues |
| 12 | Women's Health | Hormonal Balance After 35 |

Each blog rotates through the four pillars (Metabolic, Sleep/Stress, Immunity, Women's Health) to give engaged subscribers variety without fatigue.
