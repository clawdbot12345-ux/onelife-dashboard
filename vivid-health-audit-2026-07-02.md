# Vivid Health — Complete Brand & Web Audit
> **⚠️ STATUS (2026-07-02, later the same day):** This document audits Vivid Health's presence **on onelife.co.za** (One Life's store), written before the dedicated Vivid store was identified. Fixes for C4–C6 were applied to the One Life store that morning and then **fully rolled back at the owner's instruction** — the One Life store must not be modified as part of Vivid work, so the bugs listed in §1 and §6 are live again on onelife.co.za and fixing them there is a **separate owner decision**. All Vivid build work now targets **hgywg0-w7.myshopify.com** — see `reports/vivid-store-visual-audit-2026-07-02.md`, `codex-vivid-handoff-2026-07-02.md` and `codex-vivid-design-direction.md`.

**Date:** 2026-07-02 · **Method:** live catalog pull (55 SKUs via `/collections/vivid-health/products.json`), Playwright visual audit of every Vivid surface on onelife.co.za (desktop 1440×900 + mobile 390×844), asset review of the repo's Vivid imagery, domain/platform probing · **Companion:** `vivid-health-redesign-blueprint-2026-07-02.md` (the fix for everything below) and `vivid/redesign-mockup.html` (what it should look like)

---

## 0. Where the Vivid Health "website" actually lives today

There is **no dedicated Vivid Health website live anywhere**. Current state:

1. **onelife.co.za surfaces** — a collection (`/collections/vivid-health`, 55 products), a brand collection (`/collections/brand-vivid-health`), a story page (`/pages/vivid-health-story`), and stack bundles. All inside the retailer's Dawn theme.
2. **The draft Shopify store** — referenced by the owner, not publicly discoverable (no `vivid*.myshopify.com` variant resolves; no links from the live site). **Not auditable from this environment without the preview URL/password or admin access.**
3. ⚠️ **vividhealth.co.za is taken** — an active, unrelated WordPress site (a practitioner offering herbal/resonance/ultrasound services, butterfly logo, Yoast + Elementor, content updated 2024). The exact-match brand domain belongs to someone else. This is a launch-blocking naming/domain decision — see blueprint §10.

## 1. CRITICAL — product data undermines the premium ambition

### C1. Nine range names for six ranges, with typos, in ALL-CAPS
Live titles follow `VIVID HEALTH - <RANGE> - <Product> <size>`, where `<RANGE>` is any of: `IMMUNE`, `GUT HEALTH`, `GUT HEALTH & IMMUNE`, `VIVID BODY`, `PHYSICAL HEALTH`, `STAY VIVID`, `VIVID NOURISHMENT`, `NUTRIENT HEALTH`, **`NUTRITENT HEALTH`** (typo, live on 2 SKUs), `WOMAN`, `MEN`. The same product family is split across names — Omega Oil 90 is titled `PHYSICAL HEALTH` but tagged `STAY VIVID`; Turmeric Plus is titled `NUTRIENT HEALTH` but tagged `VIVID NOURISHMENT`. A customer cannot learn the range system because there isn't one.

### C2. Spelling errors on product labels/titles
- **`Colest Control`** (Cholesterol) — live title
- **`Angus Castus`** (should be *Agnus Castus* / Vitex) — live title
- **`NUTRITENT HEALTH`** — live range prefix ×2
- `Dmae` (should be DMAE)

For a health brand asking for trust, label-grade typos are the single fastest premium-killer.

### C3. No reviews, no subscriptions, no bundle logic beyond 3 static stacks
Consistent with the sitewide audit (`site-audit-2026-07-01.md` H2/H3): Judge.me is installed and fully themed (#1B4332 stars) yet shows **0 reviews on all 55 SKUs**; zero selling plans. The three Vivid bundle products (Rest & Focus R663, Bone & Joint R929, Allergy R654) prove the concept but have no tiered discount, no subscribe option, no consultant signature at card level.

### C4. Ghost SKU inside the flagship "Immunity Shield" stack
The curated Immunity Shield stack on `/collections/vivid-health` line-items "Advanced Buffered C 90 Capsules" (R205, variant 45763225059638) — **that product's URL returns 404 and it's absent from the live catalog**. The stack's add-to-cart references an orphaned variant. Fix or pull the stack today.

### C5. Wrong copy on live PDPs
The **CoQ10 product page carries an entire probiotic description** ("multi-strain probiotic formula delivering… CFUs", "Your Gut Runs the Show") with the CoQ10 title mail-merged in; MSM 90 carries generic filler. Bespoke copy elsewhere (Sage, Maca, Turmeric, 5-HTP, Buffered C) is genuinely good — but every one of the 55 PDPs needs a correctness pass.

### C6. Prices contradict themselves in three places
(1) Bundle artwork has old prices baked into the images — Rest & Focus artwork says "R587.67 — SAVE R65" while the live price is R663.00 (Allergy: image R594.72 vs live R654; Bone & Joint: R742.66 vs R929). (2) The landing page renders its 52-product grid from a **hard-coded inline JS payload whose prices drift from live variant prices** (Buffered C R428.49 vs R428.00, CoQ10 R340.40 vs R340.00, Flexijoint R625.60 vs R625.00…). (3) Odd-cent prices (R136.85, R170.77, R179.86, R263.92, R301.88) read as percentage-repricing artifacts.

## 2. HIGH

### H1. Naming is search-hostile and benefit-free
Nobody searches "Griffonia" or knows what `D-Ribose 150g` does. No title or card carries a plain-language benefit line. (The blueprint's naming grammar fixes this: "Buffered C — gentle everyday vitamin C · 300 capsules".)

### H2. Pricing hygiene
Mixed odd-cent prices among round ones — R132.99, R239.90, R90.99 next to R428, R125 — reads as sync artifacts, not merchandising. No "incl VAT" label anywhere near prices (sitewide M3). Range R90.99–R1,251.

### H3. Five SKUs out of stock in a 55-SKU brand catalog
Omega Oil 300 (R684), Bone Supreme 500 (R1,251 — the most expensive SKU), Barley Grass 300caps + 200g, DMAE 150g. That's 9% of the range dead on arrival for the brand launch; restock or retire before the store opens.

### H4. Product photography is one render per product with hostile filenames
Every product has exactly one image — a decent 3D label render on a 5688×3200 mostly-empty light canvas, named `IMG-5xxx.png` (phone-photo naming, no alt-friendly slugs). No label-legible shot, no capsule/texture macro, no lifestyle, no video. The renders themselves are usable for launch **if cropped**; the label design system (white jar + colour-coded two-tone label + category icon) is genuinely good and is the seed of the whole redesign palette.

### H5. The good imagery that exists isn't on the products
The repo carries a professional dark-slate botanical hero series (`vivid/assets/lifestyle/onelife-prompts/onelife-vivid-health-hero-banner.jpg` and 28 siblings) — premium, editorial, on-brand. None of this quality appears at PDP level.

## 3. MEDIUM

- **M1. Tag soup**: `brand_VIVID HEALTH - IMMUNE` style brand tags duplicate the broken range names into the tag layer; `Conditions>Colesterol` (typo) exists as a live tag; `sa made` vs structured origin data.
- **M2. The Vivid story page** exists and has the right bones (hero, why-tiles, ranges) but a prior audit measured the page at ~30,000px tall on mobile (visual-audit 2026-06-07); it sells the range but has no commerce integration beyond links.
- **M3. Three range families are marketed** ("Vivid Immune / Vivid Body / Stay Vivid" per the June growth build) **while the catalog encodes nine** — marketing and data never converged.
- **M4. Bundles are `type: Bundle` products** with hand-made images and stale-price risk (the old Allergy Stack was removed from the homepage for exactly this in June — R594 marketing image vs R654 live price).

## 4. What's genuinely strong (build on it, don't rebuild it)

1. **The label design system** — white jars, colour-coded ranges (coral immune / olive body / indigo mind / plum women / tan botanicals / navy men), clean VIVID HEALTH wordmark. This is a real, differentiated identity; the redesign lifts its colour system into navigation.
2. **The render quality** — consistent angle, lighting and label legibility across the range; crop + rename and they're launch-ready.
3. **The hero/lifestyle series** — dark slate + botanicals + warm light is a premium art direction most SA competitors don't have.
4. **The stacks concept + consultant provenance** — 3 live Vivid stacks and 17 consultant protocols on the parent site; no SA competitor has consultant-signed routines.
5. **The economics** — house brand, SA-made (MJ Labs/SA-Labs per the growth playbook, 25–30pts higher margin), nobody can price-compare it, wholesale expansion path documented.
6. **Distribution head start** — 65k-profile Klaviyo list, 3 stores, WhatsApp consultant culture, existing R400 free-delivery promise.

## 5. Visual audit of live surfaces (Playwright, 2026-07-02, desktop 1440×900 + mobile 390×844)

**Overall premium feel: 6/10 on the custom Vivid pages, 4/10 on stock Dawn pages** — copy 8/10, product imagery 3/10.

### Brand tokens in production
- **Colours:** deep forest `#1B4332` (Vivid primary, stack CTAs, Judge.me theme) · theme green `#2D6A4F` · mints `#B7E4C7`/`#D8F3DC` (tile icons) · WhatsApp CTA `#35D477` · cream `#FAF7F0` bg with warm variants (#F8F4EA, #EEE5D7) · gold contrast `rgb(218,196,144)`.
- **Type:** Cabin (body AND headings via Dawn), Cormorant Garamond (story hero, BOGO strip serif), **Inter loaded on every page but barely used** — three font families is a sloppy font budget. Buttons are 0px-radius.

### Per-page findings
- **`/collections/vivid-health`** (custom landing; desktop 8,083px / **mobile 18,091px ≈ 21 screens** — improved from the ~30,000px of June but still a scroll marathon; **6.5/10**). Hero with "PROUDLY SOUTH AFRICAN · EST. 2011" + 4 glass stat tiles (15 Years / 55+ Products / SA Made / Expert Stack Advice); 4 why-tiles using **emoji as brand iconography** (🇿🇦🧪🌱💰); **6 curated stacks** with 10%-off math (Gut Reset R359, Immunity Shield R561 ⚠ ghost SKU, Calm & Sleep R597, Joint R734, Women's R518, Energy R893); 52-product grid **rendered client-side from an inline JS payload** (the price-drift source; last ~12 cards lazy-load blank under slow conditions); WhatsApp consult band; BOGO strip (5 SKUs, "auto-applies at checkout"). `?view=vivid-guide` renders **byte-identical** — dead URL.
- **`/collections/brand-vivid-health`** (stock Dawn; 4/10): plain "Brand - VIVID HEALTH" H1, 55 products paginated ×3, sorted A–Z so bundles + GUT HEALTH lead instead of best sellers. **Two competing Vivid landing experiences coexist** (52 vs 55 products) — collapse to one.
- **`/pages/vivid-health-story`** (7/10 — the strongest asset): serif hero "the supplements our consultants use themselves"; 4 what-sets-Vivid-apart tiles (clinical doses declared in mg / SA-made GMP / honestly priced / consultant-formulated); **3 marketed ranges (Vivid Immune / Vivid Body / Stay Vivid) that the 8-prefix catalog doesn't match**; "How we make Vivid" evidence-led band; CTA band with a **discount-code mismatch** (headline "save another 10%" but the 3+-item code STACK5 gives 5%; 10% needs STACK10 at 5+ items).
- **PDPs** (5/10; desktop 5,223–7,786px, mobile 8,139–9,741px, no accordions): only **2 near-identical 16:9 label renders** per product served at 1200×675 with the bottle ~25% of frame; empty Judge.me stars + "No reviews" under every title; no VAT wording; good trust rail (per-store stock, same-day cutoff, R400 progress bar, WhatsApp consult, 4 trust chips); **no cross-sells, no related products, no subscription markup at all**; tag-driven breadcrumbs misfile products (Buffered C under Home › Beauty › Skin). Old kraft-pouch packshots still live on Cayenne/Spirulina/Epsom next to the new white tubs — two packaging generations side by side.
- **Search "vivid"**: 113 results across 5 pages bury the 55-product range; unstyled grey "Page" cards mixed in; every card shouts `VIVID HEALTH - …`; no stars anywhere.

### Bundle mechanics — four overlapping systems, no hierarchy
(1) six landing-page curated stacks at 10% off; (2) three real bundle products; (3) codes STACK5/STACK10/DISPENSARY10; (4) an automatic BOGO on ~5 SKUs — plus the newsletter's 10% first-order code. Powerful ingredients, uncoordinated offer architecture.

### Measured page heights (CSS px)
| Page | Desktop | Mobile |
|---|---|---|
| /collections/vivid-health (+identical ?view=vivid-guide) | 8,083 | **18,091** |
| /collections/brand-vivid-health | 4,809 | 7,644 |
| /pages/vivid-health-story | 3,208 | 5,369 |
| /search?q=vivid | 4,450 | 6,731 |
| PDPs (Buffered C / Immune+ / CoQ10 / 5-HTP / bundle) | 5,223–7,786 | 8,139–9,741 |

*20 full-page screenshots + crops + extracted JSON archived in the session scratchpad (`vivid-audit/`).*

### vividhealth.co.za detail
The exact-match domain is the practice of **Vivienne Pietersen (DipNutMed)** — Live Blood Analysis, Magnetic Resonance Analysis, ultrasound therapy, distance Rife frequency therapy, "Intervene Herbal" medicines, positioned around healing chronic conditions and cancers. Beyond the domain being unavailable, there is **brand-adjacency risk**: searches for "Vivid Health South Africa" surface a practice making claims a SAHPRA-conscious supplement brand must never be associated with. Factor this into the domain/name decision.

## 6. Same-day fixes on the LIVE site (independent of the new store)

1. Pull or repair the **Immunity Shield stack** (ghost SKU, C4).
2. Replace the **CoQ10 probiotic description** (C5) and audit MSM 90.
3. Re-export the three **bundle images without baked-in prices** (C6).
4. Fix **`NUTRITENT HEALTH`**, **`Colest Control`**, **`Angus Castus`** titles (C2).
5. Correct the story-page **STACK5 "10%" mismatch** (it's 5%).
6. Retire the dead `?view=vivid-guide` URL and pick ONE Vivid collection page.
7. Turn on Judge.me post-purchase requests (also Round-1 item 6 in `codex-round1-handoff-2026-07-01.md`).

## 7. Verdict

The brand assets (label system, renders, hero art, consultant story, margins) are **stronger than the data and commerce layer that carries them**. Nothing about the current presentation would survive contact with a Ritual/Wild-Nutrition-calibre shopper: broken taxonomy, label typos, ghost SKUs, wrong copy, contradicting prices, two images per product, zero reviews, no subscription, no transparency story. Every gap is fixable with content, metafields and ~$130/mo of apps — the redesign blueprint sequences it. **Do not launch the draft store until C1–C6 are fixed in the catalog** — renaming after launch burns SEO and label reprints, and the new store must not import this data as-is.
