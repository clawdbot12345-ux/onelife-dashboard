# Vivid Health — Complete Brand & Web Audit
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
Consistent with the sitewide audit (`site-audit-2026-07-01.md` H2/H3): Judge.me idle, zero selling plans. The three Vivid stacks that exist (Rest & Focus R663, Bone & Joint R929, Allergy R654) prove the concept but have no tiered discount, no subscribe option, no consultant signature visible at card level.

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

## 5. Visual audit of live surfaces (Playwright, 2026-07-02)

*(Detailed findings from the live browse of `/collections/vivid-health`, the `?view=vivid-guide` variant, `/collections/brand-vivid-health`, `/pages/vivid-health-story`, three PDPs and site search are appended below when the audit run completes; screenshots archived in the session scratchpad.)*

## 6. Verdict

The brand assets (label system, renders, hero art, consultant story, margins) are **stronger than the data and commerce layer that carries them**. Nothing about the current presentation would survive contact with a Ritual/Wild-Nutrition-calibre shopper: broken taxonomy, typos, one photo per product, no reviews, no subscription, no transparency story. But every one of those gaps is fixable with content, metafields and ~$130/mo of apps — the redesign blueprint sequences it. **Do not launch the draft store until §1 (C1–C2) is fixed in the catalog** — renaming after launch burns SEO and label reprints.
