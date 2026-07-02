# Vivid Health — Shopify Online Store 2.0 theme

This is the Liquid theme for the Vivid Health Shopify store. It matches
the design source of truth in **`vivid/index.html`** (~3,900 lines).

The single-file prototype is the canonical design — keep this theme in
lockstep with it. Copy in either file should match across both, and
the same CSS lives in `theme/assets/base.css` and the prototype's inline
`<style>` block.

## Structure

```
theme/
├── layout/theme.liquid           # base layout, font + color token injection
├── templates/
│   ├── index.json                # home page composition
│   ├── product.json              # PDP
│   ├── collection.json           # collection grid
│   └── page.about.json
├── sections/
│   ├── announcement-bar.liquid   # forest-deep dot-separated strip
│   ├── header.liquid             # sticky paper-translucent nav
│   ├── hero.liquid               # full-bleed photo + mini-stats + trust strip
│   ├── trust-strip.liquid        # below-hero proof band
│   ├── why-vivid.liquid          # 3 editorial photo cards (NEW)
│   ├── category-grid.liquid      # 8 goal tiles w/ hybrid bottle-label naming
│   ├── featured-products.liquid  # Top sellers band
│   ├── editorial.liquid          # Vivid Lab dark editorial section
│   ├── founder-cameo.liquid      # DR portrait + quote (NEW)
│   ├── bundle-row.liquid         # 3 curated stacks
│   ├── reviews-band.liquid       # 3 testimonial cards (NEW)
│   ├── email-capture.liquid      # Klaviyo-ready signup
│   ├── footer.liquid             # Trust band + grid + certs + payments + legal
│   ├── product-main.liquid       # PDP main
│   └── main-collection-product-grid.liquid
├── snippets/
│   ├── product-card.liquid       # data-goal palette + bench + price
│   └── cart-drawer.liquid        # right-slide cart w/ ship progress + upsell
├── assets/
│   ├── base.css                  # ~1,140 lines ported from prototype
│   └── theme.js                  # cart, sticky CTA, reveal observer
├── config/
│   ├── settings_schema.json      # colors, fonts, container width
│   └── settings_data.json
└── locales/en.default.json
```

## What landed in the last port

| Section | Status | Notes |
|---|---|---|
| `hero.liquid` | **Rebuilt** | Full-bleed photo + scrim + headline + lede + CTAs + mini-stats blocks + bottom trust-strip blocks |
| `why-vivid.liquid` | **New** | 3 photo cards. Each block: image, eyebrow, heading, body |
| `category-grid.liquid` | **Rebuilt** | Hybrid bottle-label naming (marketing name + bottle label tag), botanical SVG accent, per-goal palette |
| `founder-cameo.liquid` | **New** | Portrait OR fallback monogram, since-tag, eyebrow, quote, attribution |
| `reviews-band.liquid` | **New** | Schema-driven testimonials. Each block: stars, quote, author, location, product |
| `footer.liquid` | **Rebuilt** | Trust band (3 stats), brand col + menu cols + social cols, certs strip, payment methods strip, legal bottom |
| `header.liquid` | Polished | Search + account + cart-pip icon buttons |
| `announcement-bar.liquid` | Polished | Multi-message dot-separated |
| `assets/base.css` | **Replaced** | All 1,140 lines ported from prototype `<style>` block |
| `assets/theme.js` | **Rebuilt** | Cart drawer w/ free-ship progress, sticky CTA variants (product + cta), reveal observer |
| `layout/theme.liquid` | Updated | Color tokens now schema-injected; body opts into sticky CTA on home via `data-sticky-cta` |
| `config/settings_schema.json` | Updated | Color defaults now match prototype hex values |

## Install / deploy

1. Create a development store at https://partners.shopify.com (or use the live Vivid store).
2. Install Shopify CLI: `npm install -g @shopify/cli @shopify/theme`
3. From `vivid/theme/`:
   ```
   shopify theme dev --store=your-vivid-store.myshopify.com
   ```
4. Push to the live theme:
   ```
   shopify theme push --store=your-vivid-store.myshopify.com
   ```

## Catalogue import

`vivid/data/products.json` carries the 52 SKUs with handles, ZAR prices,
sizes, goals, forms, diet tags, and image URLs. Two import paths:

1. **CSV via Shopify Admin** — convert products.json to Shopify product
   CSV (handle, title, body_html, vendor, product type, tags, price,
   compare_at_price, sku, weight, inventory, image src).
2. **GraphQL Admin API** — script that creates products + variants +
   uploads images. Faster if you've got many SKUs.

## Metafields the theme reads

Set these in Shopify Admin → Products → Metafields to enrich cards/PDPs.
The theme has fallbacks so missing values won't break rendering.

| Namespace.key | Type | Where it shows |
|---|---|---|
| `vivid.bench` | single_line_text | Product card sub-headline + PDP sub-title |
| `vivid.category` | single_line_text | Product card category line (e.g. "Mental Health · capsule") |
| `vivid.size` | single_line_text | Product card size tag (overrides variant title) |
| `vivid.save` | number_integer | Bundle "Save Rx" badge |

## Goal palette via product tags

The card backdrop colour-shifts per goal. Tag products with one of:
`goal:gut`, `goal:immunity`, `goal:energy`, `goal:stress`, `goal:joints`,
`goal:women`, `goal:men`, `goal:daily`. The card snippet reads the tag
and applies the matching `--g-*-bg` token from `base.css`.

## Theme handover gaps

- **Predictive search drawer** — Shopify ships `/search/suggest.json` —
  wire a search overlay snippet (the prototype has the UI; needs Liquid port).
- **Reviews integration** — `reviews-band.liquid` is schema-driven for
  now. Wire Judge.me or Klaviyo Reviews when chosen.
- **Subscriptions** — Recharge or Shopify Subscriptions for the PDP
  subscribe-and-save toggle (`product-main.liquid` already renders the UI).
- **Klaviyo form** — `email-capture.liquid` uses the native Shopify
  `customer` form. Swap for the Klaviyo embed once `PRIVATE_API_KEY` is
  set in `.mcp.json` and the list ID is known.
- **Schema.org** — extend `product-main.liquid` with `aggregateRating`
  once a reviews provider is live.
- **Mega menu** — the prototype's mega menu is a key conversion path;
  needs a Liquid port (probably as a header subsection w/ blocks for
  goal columns, curated column, help column, feature card).

## Design tokens

Color, font, and container-width tokens are in
`config/settings_schema.json` and get injected as CSS custom properties
by `layout/theme.liquid`'s `{%- raw -%}{% style %}{%- endraw -%}` block.
Defaults match the prototype's `:root`. Merchants can override in the
Shopify Theme Editor under **Theme settings → Colors / Typography /
Layout** without touching code.

Everything else (per-goal palettes, shadows, radii, spacing scale) lives
verbatim in `assets/base.css` — keep in sync with the prototype.
