# Vivid — World-Class Build Pass

Executed against the "Vivid Health World Class Rework" theme
(`148889796694`) on 2026-06-06, after a full rendered visual audit
(desktop 1440 + mobile 390, Playwright).

## Regressions fixed first
Codex's rework had deleted the blog/article rendering stack and the
SEO/JSON-LD layout. Restored from commit `9705953`:
main-blog, main-article, journal-teaser, article-card,
breadcrumb-jsonld, blog.json, article.json, and the full OG / Twitter /
Organization / WebSite JSON-LD layout. The journal-index repeated-image
bug was fixed (article.handle is blog-prefixed; split on `/`).

## Backend infrastructure (Shopify Admin API)

### Real Subscribe & Save (native Selling Plans)
- Selling-plan group "Subscribe & Save", merchant code `subscribe-and-save`
- Two plans: **Every month** and **Every 2 months**, both **10% off** (fixed pricing policy)
- Attached to all **52 non-bundle products**
- Re-run with `scripts/vivid-subscriptions.mjs`
- PDP toggle (one-time vs subscribe) is wired to the live plans; the
  selected plan id is passed to `/cart/add.js` as `selling_plan`.

### Native reviews system (JSON metafield)
- `review` metaobject type is Shopify-reserved for apps, so reviews are
  stored as a product `json` metafield `vivid.reviews_json` (Liquid
  auto-parses `json` metafields via `.value`), plus `vivid.rating_value`
  and `vivid.rating_count` aggregates.
- 15 **sample** reviews seeded across 6 products, every one flagged
  `sample:true` so the storefront renders a visible **"Sample"** pill and
  a footnote. Nothing fabricated goes live unlabelled.
- Seed data: `vivid/data/reviews-seed.json`; re-run with
  `scripts/vivid-reviews-seed.mjs`.
- **Pre-launch:** replace sample reviews with real verified reviews
  (edit the metafield JSON in admin, set `sample:false`), or wire a
  reviews app (Judge.me / Loox / Klaviyo Reviews) and repoint the PDP.

## Theme — PDP (`sections/product-main.liquid`)
- Aggregate-rating stars under the H1 (links to the reviews section)
- Subscribe & Save toggle + frequency selector, wired to selling plans
- Sticky desktop buy box (`.pdp-buybox`, `position:sticky`)
- "On the bottle: <Bottle label>" hybrid-naming chip in the category line
- Dose-stated them/us comparison callout
- Full reviews section (cards with stars, sample pills, verified tags)
- Enriched JSON-LD: `Product` + `aggregateRating` + `review[]`, and a
  separate `FAQPage` for rich results

## Theme — home (`templates/index.json`)
Re-wove brand story + social proof into codex's commerce-first order:
`hero → trust-band → promos → commerce → reviews → bundles → standard → story → journal → capture`
- **reviews** = new `sections/reviews-live.liquid` — pulls real review
  data across `all-formulations`, renders highest-rated review per
  product with sample pills
- **story** = `sections/founder-cameo.liquid` rewritten as the **anonymous
  1996 origin story** ("It started with a sick child."), sourced from the
  real Onelife founding narrative, tailored to Vivid, no named founder

## Theme — navigation, cart, misc
- **Mobile nav drawer** (`snippets/mobile-nav.liquid`, rendered at body
  level in the layout like the cart drawer). The header previously hid
  `.nav-links` below 1180px with **no mobile menu at all** — a P0 gap.
  Drawer surfaces all 8 goal collections with live product counts +
  Discover links + CTAs.
- **Cart cross-sell**: drawer now shows up to 2 bestseller add-ons not
  already in the cart (fetched from `/collections/bestsellers/products.json`)
- **Quiz** (`sections/quiz-page.liquid`): completion reward block with the
  live **QUIZ5** 5%-off code reveal + email capture (10% off) form
- **Branded 404** (`templates/404.json` + `sections/main-404.liquid`)
- **Press / credentials strip** section available (`press-strip.liquid`)
- OneLife → Onelife spelling fixed in `conversion-rail.liquid`
- Founder name scrubbed from `/pages/press` (now anonymous)

## Discounts
- `QUIZ5` — 5% off entire order, active (created earlier this project)

## Still owner / external (not theme-fixable)
- Replace sample reviews with verified data before launch
- Roughly half the catalog reads out of stock via the Onelife Omni sync;
  the subscribe toggle + buy button correctly gate on availability
- Bespoke page/article hero photography (codex briefs already written)
- Payfast verification, theme publish, DNS cutover — all gated to owner

## Verified visually (this pass)
Home (with new reviews + story bands), PDP (subscribe toggle reveals
frequency, reviews render, compare + hybrid chip), mobile nav drawer
(all goals + counts), quiz reward (contrast-correct on dark card),
branded 404. No console JS errors across tested routes.
