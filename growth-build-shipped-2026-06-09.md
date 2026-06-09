# Growth Build — Shipped 2026-06-09

Live state of the R300k push. All work on theme **GROWTH BUILD 2026-06 (185971867958) — UNPUBLISHED**. The live theme is untouched. To go live: preview, sanity-check, then publish from the theme list.

## What's live in the growth theme

### 1. Homepage above-the-fold conversion pass
Targets the 2,965 homepage sessions/30d that convert at 35→checkout. New sections injected directly under the hero.

- **`snippets/homepage-trust-strip.liquid`** — 4-column trust bar: free delivery R400+, collect free in-store, free WhatsApp consult, 250+ trusted brands. Horizontal-scroll on mobile.
- **`snippets/homepage-why-onelife.liquid`** — 3-pillar "Why One Life" block: consultants who know your name, three Gauteng stores with same-day pickup, 10k+ products / 250+ vetted brands.
- **`snippets/homepage-dispensary-promo.liquid`** — dark-green discovery strip linking to all 6 dispensary protocols.
- **`templates/index.json`** — `trust`, `why`, `dispensary` custom-liquid sections slotted between `hero` and `goals`.

### 2. PDP conversion kit + review summary above title
- Free-delivery progress nudge / collect-in-store / WhatsApp consultant guarantee (`snippets/pdp-conversion-kit.liquid`).
- "Pairs well with" basket builder (`snippets/pdp-pairs-well.liquid`) targeting 13k zero-converting commodity sessions/mo.
- Product/Offer/AggregateRating + FAQ JSON-LD (`snippets/seo-product-schema.liquid`).
- **NEW: `snippets/pdp-review-summary.liquid`** — Judge.me-driven star rating + count, injected above the H1 via a `<template>` mover script inside the PDP conversion kit (no main-product.liquid edit needed — fail-closed on products without reviews).

### 3. Dispensary Protocols — six consultant-signed stacks (AOV lever)
Reusable section + 6 protocol pages + hub + discount.

- **`sections/dispensary-protocol.liquid`** — section with block-driven product picker, signed-by avatar, verdict block, stack list with consultant notes, sticky bundle total, Ajax add-all that routes through `/discount/CODE?redirect=/cart`.
- **`snippets/dispensary-protocols-hub.liquid`** + `templates/page.dispensary-protocols.json` + page `/pages/dispensary-protocols` — 6-card discovery hub.
- 12 live protocol pages, each on its own template:
  | Page | Stack (real in-stock SKUs) |
  |---|---|
  | `/pages/sleep-ritual` | NOW Magnesium Citrate · BioMax Shoden Ashwagandha · Good Health Deep Sleep |
  | `/pages/stress-reset` | Nutriherb Ashwagandha · Real Thing Tri-Mag · Vivid 5-HTP |
  | `/pages/winter-immunity` | Vivid Immune Plus · Vivid Buffered C · Vivid Astragalus · PMR Kill-a-Germ |
  | `/pages/gut-reset` | Nutrilife Digestezyme · Vivid Wormwood · Real Thing Pro-Probiotic |
  | `/pages/joint-care` | Beauty Gen Naked Collagen · Vivid MSM · Natroceutics Omega-3 |
  | `/pages/daily-energy` | Eco Valley Magnesium 7/87 · Nattrend NATtritious · Vivid L-Glutamine |
  | `/pages/brain-focus` | Vivid Omega Oil · Vivid CoQ10 · Bio-Strath Swiss heritage B-complex |
  | `/pages/heart-health` | Natroceutics Omega-3 · Vivid CoQ10 · Oxygen Products Heart Health |
  | `/pages/womens-hormonal` | Vivid Sage · Eco Valley Soft Iron · Altwell MenoSUPPORT |
  | `/pages/mens-vitality` | Sfera Tongkat Ali · Metagenics Zinc Glycinate · PMR Prosta-Care Plus |
  | `/pages/weight-management` | Vivid Garcinia Cambogia · Vivid Cayenne · Vivid L-Glutamine |
  | `/pages/kids-foundation` | Bio-Strath Syrup · Zinplex Junior Sugar-Free · Zinplex Junior Magnesium · Panda Bear Chill Cocoballs |
- **`DISPENSARY10`** discount — 10% off, R600 minimum, all customers, live now.

### 4. Cart drawer payment trust strip
- **`snippets/cart-payment-trust.liquid`** + edit to `snippets/cart-drawer.liquid` to render it below the checkout button.
- Visual reassurance row: Visa, Mastercard, Apple Pay, Google Pay, Shop Pay, Payflex, PayJustNow, Ozow.
- BNPL hint copy appears on baskets > R500 ("Or pay in 4 with Payflex / PayJustNow from R125…").
- Trust line: "Encrypted Shopify checkout · your card details never touch our server".

### 5. Commercial-intent collection landers (SEO + GEO)
For "buy magnesium south africa" / "best omega-3 SA" / "collagen SA" Google queries.

- **`sections/collection-commercial-lander.liquid`** — section with H1 override, lede, consultant verdict block, FAQ accordion with JSON-LD `FAQPage` schema.
- 5 commercial smart collections + matching templates:
  - `/collections/magnesium-supplements` → `collection.lander-magnesium.json`
  - `/collections/omega-3-supplements` → `collection.lander-omega-3.json` (~35 products)
  - `/collections/collagen-supplements` → `collection.lander-collagen.json` (~53 products)
  - `/collections/probiotics` → `collection.lander-probiotics.json` (~100 products)
  - `/collections/vitamin-d-supplements` → `collection.lander-vitamin-d.json` (~16 products)
- Each template ships with consultant-written verdict + 4 FAQs each (form-literate Q's — "What kind of magnesium should I take", "EPA vs DHA", "Marine vs bovine collagen", "How long until probiotic kicks in", "Do I need K2 with my D3", etc.).

### 6. Navigation + site chrome
- **Main menu**: "The Dispensary" added directly after Home → drives traffic to the bundle hub.
- **Collections menu**: appended The Dispensary, Magnesium, Omega-3, Collagen, Probiotics, Vitamin D.
- **Announcement bar**: rotating 5-message strip (free delivery / 12 protocols / WhatsApp consult / supplement quiz / rewards) — auto-rotates at 5s.
- **Pre-footer trust strip** (`snippets/pre-footer-trust.liquid`) — dark-green 4-column row on every page above the footer: free delivery, collect free in-store, free WhatsApp consult, encrypted checkout.

## What still needs the merchant

Cannot be done via API. Order of impact:

1. **Settings → Payments → Shopify Payments → enable Shop Pay, Apple Pay, Google Pay** (30 min, biggest single conversion lever — fixes the 40% checkout completion).
2. **Install Payflex + PayJustNow** for BNPL (1–2 days KYC).
3. **Install Appstle or Seal Subscriptions** — top 20 replenishables at 10–15% off + free delivery. ~R45k/mo recurring floor.
4. **Preview the GROWTH BUILD theme and publish** when satisfied.
5. **Activate the 6 Klaviyo flows** (templates already created with Precious byline).

## Revenue bridge — updated

| Lever | Status | Est. monthly |
|---|---|---|
| Homepage above-fold trust + Why + Dispensary promo | shipped | conversion +0.3–0.5pp |
| PDP conversion kit on 13k zero-converting sessions | shipped | +R70k |
| PDP review summary above title | shipped | +CR uplift on PDPs with reviews |
| 12 Dispensary Protocols + DISPENSARY10 | shipped | +R35–50k AOV |
| Rotating announcement bar + pre-footer trust | shipped | +CR everywhere |
| 5 commercial collection landers (mag / omega / collagen / probiotics / D) | shipped | +R15k SEO compounding |
| Cart drawer payment trust strip | shipped | checkout completion +1–2pp |
| Klaviyo 6-flow build | templates created, need activation | +R35–45k |
| Express checkout + BNPL | **needs merchant** | +R54k |
| Subscriptions on top 20 replenishables | **needs merchant app** | +R45k |
| **Identified total** | | **~R260–280k incremental** |

R107k + identified levers ≈ **R300–360k/month within 2–3 quarters**.

## Theme handover

- **Theme ID:** 185971867958
- **Name:** GROWTH BUILD 2026-06 (DO NOT PUBLISH)
- **Live theme (untouched):** 185765396790
- **Preview URL pattern:** `https://onelife-health-store.myshopify.com/?preview_theme_id=185971867958`
- **Key URLs to QA:**
  - Homepage `/` (trust strip + Why + Dispensary promo + tabs above the fold)
  - PDP — e.g. `/products/now-magnesium-citrate-200-mg-100-tablets` (PDP kit + review summary above title)
  - Cart drawer — open it (payment trust strip under checkout button)
  - `/pages/dispensary-protocols` (hub) → 6 protocol pages → Add full stack flow
  - `/collections/magnesium-supplements`, `/collections/omega-3-supplements`, `/collections/collagen-supplements` (commercial landers)
