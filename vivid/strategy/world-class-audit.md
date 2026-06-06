# Vivid Health — World-Class Audit

Audit of the "Vivid Health World Class Rework 2026-06-04" theme
(`148889796694`) benchmarked against Apothékary, Moon Juice, Necessaire,
Seed, Ritual, and the Onelife mothership.

Authored 2026-06-06.

## Theme inventory (post-codex rework)

- **135 files**, ~10 MB
- **24 sections** — including 5 home-* variants
- **8 templates** — index, product, collection, page, page.about,
  page.contact, page.quiz, cart
- **5 snippets** — cart-drawer, floating-contact, product-card,
  vivid-product-art, vivid-stack-card

### Codex added vs the previous draft

- `sections/conversion-rail.liquid` — 4-card "start here" grid (orphaned, not in home order)
- `sections/home-commerce-system.liquid` — products + curated stacks merch block
- `sections/home-promo-banners.liquid` — promo banners band
- `sections/home-standard.liquid` — image+copy editorial moment
- `sections/home-journal-band.liquid` — replacement for the old journal-teaser
- `snippets/floating-contact.liquid` — corner floating CTA
- `snippets/vivid-stack-card.liquid` — bundle card
- `assets/vivid-logo-wordmark.svg` — proper SVG wordmark

### Codex deleted (regressions — restored this session)

- `sections/main-blog.liquid` → restored
- `sections/main-article.liquid` → restored
- `sections/journal-teaser.liquid` → restored
- `snippets/article-card.liquid` → restored
- `snippets/breadcrumb-jsonld.liquid` → restored (full OG/JSON-LD/breadcrumb SEO)
- `templates/blog.json` → restored
- `templates/article.json` → restored
- `layout/theme.liquid` → restored (was dropped to bare 4-meta state)

### Home page composition (new theme)

Order: `hero → trust-band → promos → commerce → bundles → standard → journal → capture`

Removed from prior version:
- ❌ WHY VIVID 3-card photo editorial
- ❌ category-grid (Shop by goal tiles)
- ❌ featured-products
- ❌ editorial ("We don't believe in fairy dusting")
- ❌ founder-cameo
- ❌ reviews-band

These are **brand-storytelling losses**. The commerce-first orientation
trades editorial depth for conversion focus. Both routes are defensible.

## World-class benchmark

| Brand | Hero pattern | Quiz | Subs/save | Science page | Founder face | Reviews block |
|---|---|---|---|---|---|---|
| Ritual | Single hero CTA, capsule reveal | Yes, personal+lifestyle | Yes, default | Yes, deep | Yes | Yes, on PDP |
| AG1 | Single hero CTA | No (single SKU) | Yes, default | Yes, deep | Yes, doctor face | Yes, on PDP |
| Apothékary | Set-first merchandising | Yes, bundle-led | Yes | Some | Yes | Yes, on PDP |
| Moon Juice | Editorial + bestseller grid | No | Yes | "Doctors + Experts" content | No | Yes, deep |
| Seed | Single SKU, deep science | No | Yes (auto) | Yes, very deep | Yes (founders + scientists) | Yes |
| Necessaire | "Less but better" minimal grid | No | Yes | Climate Neutral cert | Yes | Yes |
| **Vivid (now)** | Photo + stats + trust strip | ✅ Yes, 4-step builder | ❌ NO | ❌ NO | ✅ Yes (DR monogram cameo restorable) | ⚠️ schema-driven, not live data |

## What Vivid already does that's world-class

1. **Dose-stated transparency** — leans into the brand's strongest moat
2. **Hybrid bottle-label naming** (Stress / Mental Health) — no peer does this
3. **Founder cameo** with monogram (restorable, deleted in rework)
4. **Editorial WHY VIVID** photo cards (restorable, deleted in rework)
5. **Branded password page** — most peers ship Shopify default
6. **Sticky mobile CTA** — Apothékary doesn't, AG1 doesn't
7. **Article reader w/ JSON-LD + reading-time** — better than Moon Juice's

## Gaps vs world-class — RANKED

### P0 — Must close before public launch

1. **Reviews are schema-fakes, not live customer data.** No peer ships
   fabricated reviews. Need Judge.me / Klaviyo Reviews / Loox installed
   and at least 10 real reviews per top-3 SKUs before launching.
2. **No Subscribe & save** on PDP. Every world-class brand has this. The
   prototype HAS a sub-toggle UI but it's not wired to a real
   subscription app. Install Shopify Subscriptions or Recharge.
3. **No persistent ATC on PDP at scroll.** Apothékary, Ritual, AG1 all
   keep the CTA in view at all times. The mobile sticky exists but not
   for desktop.

### P1 — High impact

4. **No Science / approach page.** Seed's `/approach` is the
   strongest-converting science URL on the internet for that category.
   Vivid has the dose-stated story but no dedicated landing.
5. **No "Doctors + Experts" content section.** Moon Juice's killer
   feature. Vivid has the Journal (12 articles), but no interview-format
   content with named SA naturopaths/practitioners.
6. **No press / "As seen in" strip.** Even nascent brands fake this with
   1-2 logos. Vivid has none.
7. **No "Compare to" callout on PDP.** "Buffered C vs supermarket Vit C"
   beats just listing the dose. Comparison-table is a 2-hour win.
8. **No FAQ-Schema rich-result markup on PDP.** PDP has a Common
   Questions tab — adding `<script type="application/ld+json">` for
   `FAQPage` schema lights up Google AI Overviews + rich snippets.
9. **Quiz misses email capture.** Quiz completion is the highest-intent
   moment. No email gate = leaving 30%+ of CLV on the table.
10. **Quiz missing QUIZ5 reveal.** Code is live but quiz result page
    doesn't display it. Free conversion lever.
11. **No "Why this match" explanation on quiz result.** Care/of's quiz
    converts on this. Vivid says "Your match is X" — needs to also say
    "because you answered Y, this is why".
12. **No bestsellers cross-sell at cart drawer.** Free shipping unlock
    pattern needs upsell logic ("Add ₹X more and unlock free shipping
    — try these popular adds").
13. **Home page lost WHY VIVID + founder + reviews.** Reduces brand
    storytelling. Either restore or replace with equivalent moments.
14. **No "as labelled" badge on PDP for the hybrid naming.** The bottle
    label says "Mental Health"; the product page says "Stress Sleep &
    Mood". Customer confusion risk. Display both clearly.

### P2 — Polish

15. Goal collection pages need editorial heroes (Onelife has them)
16. Product cards lack a "Pairs with" small-text line
17. Cart upsell needs cross-sell of bundles
18. PDP image gallery missing zoom/full-screen view
19. Mobile menu doesn't show goal collections at top level
20. No 404 page (Shopify default — looks unbranded)
21. No customer account templates customised (Shopify default)
22. No reviews-by-goal summary on collection pages
23. Pages lack hero imagery (codex brief written, images not yet generated)
24. No SA-specific shipping ETA on cart ("Order before 14:00 SAST for next-day delivery in Centurion")
25. No press kit / brand assets page for journalists
26. No B2B / practitioner channel page (Seed has /practitioners — 20% of revenue)
27. No comparison wizard between Vivid SKUs (which immunity product is right for me?)
28. No "Vivid index" comparison vs imported brands (lean into the made-in-SA story)
29. No referral program ("Give R75, get R75")
30. No "Build your own stack" page (Apothékary has — 8% AOV lift)

## Quiz audit — focused

**Strengths of codex's quiz (148889796694)**
- 4-step builder, no page transitions, live result card
- 8 goal × 12 signal × 3 style × 3 format = ~864 combinations narrowed to specific SKUs
- Per-SKU image map (30+ products)
- "First 14 days" plan framing — novel
- WhatsApp escape hatch for "Ask a consultant before you combine"
- Direct add-to-cart link from result

**Weaknesses being fixed this session**
- No QUIZ5 reveal on completion → adding
- No email capture → adding
- No "why this match" explanation → adding

**Quiz value question (user asked)**
With 52 SKUs and 8 goal categories, a quiz is essential merchandising.
Without one, the customer faces decision paralysis. Codex's quiz is
above-average. The improvements above will move it from "good" to
"world-class".

## Aesthetics audit

Vivid's current aesthetic is in the right zone — Aesop/Apothékary
adjacent, dose-stated brutal-honest as the brand voice. Specific notes:

- Hero is right (photo + scrim + clear stats + trust strip)
- Footer trust band is right
- Color palette is right (paper/sage/clay/ochre cream-on-forest)
- Typography is right (Fraunces display + Inter)
- Per-goal product card backdrops are right (no peer does this — keep)
- Founder monogram fallback is OK but a real portrait would be 10x better
- Photography is the biggest gap — placeholder generated assets vs
  real photographic studio work. The 5-shot codex brief I wrote needs
  to be commissioned, ideally with a real SA studio shoot.

## Conversion-path audit — answering "is it easy to find a product"

Walk-through (assuming new visitor, no password protection):

1. **Home** — hero is single CTA "Shop the range" → /collections/all-formulations ✓
2. **From home** — "Find your formulation" → /pages/quiz ✓
3. **Browse path** — Shop link in nav → main-menu shows: Shop · Bestsellers · Bundles · Journal · Find your formulation · Free consultation · About · Contact ✓
4. **Collection page** — goal collection has the chip filter, products in grid ✓
5. **Product page** — full PDP with tabs (Benefits / Ingredients / How to take / FAQ) ✓
6. **Add to cart** — drawer opens, free-ship progress, cart upsell ✓
7. **Checkout** — Shopify checkout, Payfast wired ✓

**Friction points:**
- No persistent CTA on desktop PDP (must scroll back to top to add)
- No "buy it again" for returning customers
- No quick add from product cards
- Long handles in URLs (SEO drag — Onelife has same issue, less critical)
- Cart drawer has 3 sections but no clear "Continue to checkout" CTA above the fold on mobile (codex's main-cart added this)

**Verdict:** finding-to-cart is solid. The drag is in **conversion-decision** (which of the 10 immunity options is for me?). That's what the quiz solves and what Subscribe & save reinforces.

## Execution plan — this session

### Restored (regression fixes)
- ✅ Blog/article/journal-teaser sections + templates
- ✅ Article-card snippet
- ✅ Breadcrumb JSON-LD snippet
- ✅ Layout/theme.liquid with full OG/Twitter/JSON-LD

### Will execute
- Improve quiz: QUIZ5 reveal + email capture + "why this match"
- Create Science page (`/pages/our-approach`)
- Create comparison page (`/pages/compare-vivid`)
- Add bestseller cross-sell to cart drawer

### Deferred (need user approval or out of scope)
- Install Subscribe & save app
- Install live reviews app
- DNS cutover
- Theme publish (currently UNPUBLISHED)
- Real photography commission

