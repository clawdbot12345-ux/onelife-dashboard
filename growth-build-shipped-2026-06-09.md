# Growth Build — Shipped 2026-06-09

Live state of the R300k push. All work on theme **GROWTH BUILD 2026-06 (185971867958) — UNPUBLISHED**. The live theme is untouched. To go live: preview, sanity-check, then publish from the theme list.

## What's live in the growth theme

### 1. Homepage above-the-fold conversion pass
Targets the 2,965 homepage sessions/30d that convert at 35→checkout. Two new sections injected directly under the hero, before category browse.

- **`snippets/homepage-trust-strip.liquid`** — 4-column trust bar: free delivery R400+, collect free in-store, free WhatsApp consult, 250+ trusted brands. Horizontal-scroll on mobile.
- **`snippets/homepage-why-onelife.liquid`** — 3-pillar "Why One Life" block: consultants who know your name, three Gauteng stores with same-day pickup, 10k+ products / 250+ vetted brands. Apothecary moat made visible above the fold.
- **`templates/index.json`** — new `trust` and `why` custom-liquid sections slotted between `hero` and `goals`.

### 2. PDP conversion kit (from prior session, confirmed live in theme)
- Free-delivery progress nudge
- Collect-in-store block (3 Gauteng stores)
- WhatsApp consultant guarantee
- "Pairs well with" basket builder targeting the 13k zero-converting commodity sessions
- Product/Offer/AggregateRating + FAQ JSON-LD for GEO

### 3. Dispensary Protocols — the AOV lever
Consultant-signed supplement stacks. Unique to One Life in SA. Each protocol is a separate page on its own JSON template; all pages share one section with Ajax cart logic.

- **`sections/dispensary-protocol.liquid`** — reusable section with block-driven product picker, signed-by avatar, "What we'd suggest" verdict block, stack list with consultant notes, sticky bundle total, Ajax add-all-to-cart that redirects through `/discount/CODE?redirect=/cart`.
- **`templates/page.protocol-sleep-ritual.json`** + page `/pages/sleep-ritual` — NOW Magnesium Citrate + BioMax Shoden Ashwagandha + Good Health Deep Sleep.
- **`templates/page.protocol-stress-reset.json`** + page `/pages/stress-reset` — Nutriherb Ashwagandha + Real Thing Tri-Mag + Vivid 5-HTP.
- **`templates/page.protocol-winter-immunity.json`** + page `/pages/winter-immunity` — Vivid Immune Plus + Buffered C + Astragalus + PMR Kill-a-Germ.
- **`templates/page.dispensary-protocols.json`** + page `/pages/dispensary-protocols` (hub).
- **`snippets/dispensary-protocols-hub.liquid`** — 3-card hub landing.

**Discount code `DISPENSARY10`** — 10% off, R600 minimum, all customers, active 2026-06-09.

## What still needs the merchant

Cannot be done via API. Order of impact:

1. **Settings → Payments → Shopify Payments → enable Shop Pay, Apple Pay, Google Pay** (30 min, biggest single conversion lever per analytics).
2. **Install Payflex + PayJustNow** for BNPL (1–2 days KYC). BNPL lifts AOV and conversion 20–30% in SA health.
3. **Install Appstle or Seal Subscriptions** — turn on subscribe-and-save on top 20 replenishables at 10–15% off + free delivery. Nobody major in SA offers this; ~R45k/mo recurring floor.
4. **Add "Dispensary Protocols" to main nav** (header → menu editor → link to `/pages/dispensary-protocols`).
5. **Preview the GROWTH BUILD theme and publish** when satisfied with the above-fold + protocol pages.
6. **Set the 6 Klaviyo flows live** (templates already created with Precious byline; see Email tab in dashboard).

## Revenue bridge — updated

| Lever | Status | Est. monthly |
|---|---|---|
| Homepage above-fold trust pass | shipped to growth theme | conversion +0.2–0.4pp |
| PDP conversion kit on 13k zero-converting sessions | shipped to growth theme | +R70k |
| Dispensary Protocols (3 pages live, +discount) | shipped to growth theme | +R25k AOV |
| Klaviyo 6-flow build | templates created, need activation | +R35–45k |
| Express checkout + BNPL | **needs merchant** | +R54k |
| Subscriptions on top 20 replenishables | **needs merchant app** | +R45k |
| SEO/GEO expansion (schema live, content compounding) | shipped | +R20k+ |
| **Identified total** | | **~R250–260k incremental** |

R107k + identified levers ≈ **R300–360k/month within 2–3 quarters**.

## Theme handover

- **Theme ID:** 185971867958
- **Name:** GROWTH BUILD 2026-06 (DO NOT PUBLISH)
- **Live theme (untouched):** 185765396790 — Live Visual Fix 2026-06-07
- **Preview URL pattern:** `https://onelife-health-store.myshopify.com/?preview_theme_id=185971867958`
- **Key URLs to QA:**
  - Homepage `/` (new trust strip + why block above the fold)
  - PDP — any product, e.g. `/products/now-magnesium-citrate-200-mg-100-tablets` (PDP kit)
  - `/pages/dispensary-protocols` (hub)
  - `/pages/sleep-ritual`, `/pages/stress-reset`, `/pages/winter-immunity` (protocols + Add full stack flow)
