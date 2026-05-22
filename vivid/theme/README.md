# Vivid Health — Shopify theme starter

A Shopify Online Store 2.0 theme starter built to match the design system in
`vivid/index.html`. Drop into a Shopify Partner dev store, link the product
catalogue, and ship.

## What's here

```
theme/
├── layout/theme.liquid              # base layout, fonts, header/footer wiring
├── templates/
│   ├── index.json                   # home: hero, trust, goals, featured, editorial, bundles, journal, capture
│   ├── product.json                 # PDP
│   ├── collection.json              # collection grid + filters
│   └── page.about.json              # about page
├── sections/
│   ├── announcement-bar.liquid
│   ├── header.liquid                # sticky nav + cart drawer trigger
│   ├── hero.liquid                  # editorial split hero
│   ├── trust-strip.liquid
│   ├── category-grid.liquid         # "Shop by goal" tiles
│   ├── featured-products.liquid     # 4-up product carousel
│   ├── editorial.liquid             # founder/philosophy split block
│   ├── bundle-row.liquid            # 3-up bundle cards
│   ├── ingredient-teaser.liquid
│   ├── journal-teaser.liquid
│   ├── email-capture.liquid         # Klaviyo-ready form
│   ├── footer.liquid
│   ├── product-main.liquid          # PDP main section
│   └── main-collection-product-grid.liquid
├── snippets/
│   ├── product-card.liquid
│   ├── price.liquid
│   └── icon.liquid
├── assets/
│   ├── base.css                     # design tokens + components
│   └── theme.js                     # cart drawer, tabs, qty stepper
├── config/
│   ├── settings_schema.json         # theme settings (colors, fonts, etc.)
│   └── settings_data.json
└── locales/
    └── en.default.json
```

## Install

1. Create a development store at <https://partners.shopify.com> (or use the existing Vivid store once provisioned).
2. Install the **Shopify CLI**: `npm install -g @shopify/cli @shopify/theme`.
3. From this directory:
   ```
   cd theme
   shopify theme dev --store=your-vivid-store.myshopify.com
   ```
4. Push to the live theme when ready:
   ```
   shopify theme push --store=your-vivid-store.myshopify.com
   ```

## Catalogue import

The 55 Vivid SKUs (with prices, images, and tags) are extracted into
`vivid/data/products.json`. To bulk-import:

1. Format that file as a Shopify product CSV (use `scripts/products-to-csv.js` — TODO).
2. Use Shopify Admin → Products → Import → CSV.
3. Or, since these products already exist on `onelife.co.za`, duplicate them
   via the **Shopify Migration Tool** or a direct GraphQL Admin script.

## What's not here yet (handover list for a Shopify dev)

- Liquid wiring for **predictive search** drawer (we ship a prompt-based fallback in the prototype).
- **Reviews** — recommend Judge.me or Yotpo, plug into `product-main.liquid`.
- **Subscriptions** — Recharge or Shopify Subscriptions for repeat orders.
- **Klaviyo** form snippet — replace the `form` in `email-capture.liquid`
  with the Klaviyo embed once API key is in `.mcp.json`.
- **Schema.org** `Product` and `FAQPage` markup is partially included in
  `product-main.liquid` — extend with reviews/aggregateRating once those are in.
- Multi-currency and **markets** — the existing site is ZAR-only; enable
  Shopify Markets if expanding.

## Design tokens

All tokens live as CSS custom properties in `assets/base.css` and as theme
settings in `config/settings_schema.json` so they're editable in the
theme editor. See the prototype `vivid/index.html` for the canonical
visual reference.
