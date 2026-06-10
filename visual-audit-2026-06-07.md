# One Life Health — End-to-End Visual Audit
**Date:** 2026-06-07
**Live theme:** `185765396790` (Onelife Live Visual Fix 2026-06-06 + audit-port)
**Method:** Playwright headless Chromium → 68 mobile + desktop screenshots → manual review

---

## ✅ Shipped this audit

### Footer
- Killed **"Powered by Shopify"** from copyright
- Killed entire **"PRODUCT TAGS"** column block (Codex overkill — disclaimer was already covered)
- Killed inline "Product Tags: shopping guide only" link
- Copyright now reads: `© 2026, One Life Health · South Africa's apothecary, since 1996.`
- Footer link colour: sage `#a8c0a0` (was mint, was gold — both rejected)

### About page (full rewrite)
- Hero: **"Three small shops. Thirty years. One family."** in Cormorant
- Subhead: italic *"South Africa's apothecary, since 1996."*
- Stats: 1996 · 3 · 10,000+
- Mission block: *"A son got better, and a family wouldn't stop talking about it."*
- 4 value tiles rewritten: "Only what we'd take ourselves" · "A counter, not a chatbot" · "SA stock — no import wait" · "Known by name, not a customer number"
- Removed Codex's "Join the One Life Community for exclusive offers, health tips, and rewards. We're not just a store — we're your partner in lifelong wellness."

### Hero / CTA voice
- Slide 1: "Free Delivery Over R400" → "Free to your door, anywhere in SA." + "Browse the apothecary"
- Slide 2: "Free Health Consultation" → "Honest guidance from consultants who actually know the range." + "Book a consult"
- Slide 3: "Vivid Health" → "Our house range. South African botanicals, clinical doses, 10% off any stack." + "Explore Vivid"
- Slide 4: "Find Your Perfect Stack" → "60 seconds. 4 questions. Real recommendations." + "Start the quiz"
- Slide 5: "250+ Trusted Brands" → "The brands our consultants actually stand behind." + "Browse brands"
- Section headings: "Health Hub — Our Blog" → "The Apothecary"; "Featured Categories" → "Shop by goal"; "Top Supplements" → "Customer favourites"

### Quiz page
- "Take the Quiz — Save 5%" → **"Start the quiz"**
- "Find Your Perfect Supplement Stack" stays — Cormorant serif
- Subhead: "60 seconds. 4 questions. The stack we'd build for you. **STACK5** takes 5% off automatically. 30 years of in-store experience behind every recommendation."
- CTA: "Find My Supplements" → **"Build my stack"**
- Fixed broken HTML in subhead

### Homepage middle sections
- Consultation banner: "Book Now — It's Free" → **"Book a consult"**

### Header announcement bar
- "Get 10% off — join our community →" → **"Get 10% off your first order — join the apothecary list →"**

### Brand normalization
- Centurion page title: `Centurion Store | Onelife Health` → `Centurion Store | One Life Health`
- Edenvale page title: same fix
- Glen Village page title: same fix
- Centurion body H1: `Onelife Health Centurion` → `One Life Health Centurion`
- All store snippets, schema-jsonld, breadcrumbs, etc.

### Typography & layout
- **Cormorant Garamond** for H1/H2 across entire site (Aesop/Goop-tier pairing)
- **Inter** for body (replaces Cabin — modern premium standard)
- Featured-blog section heading: `clamp(34px, 5vw, 48px)` Cormorant
- Article card titles: `clamp(20px, 2.6vw, 26px)` Cormorant — no more underlined sans
- Article hero image: explicit `aspect-ratio: 16/9` desktop, `4/3` mobile
- Article body: 68ch reading column, drop cap on `.lead`
- Read-next 3-card grid at end of articles
- Reading progress bar

### Cart drawer + page
- Empty cart drawer: "Nothing here yet." + quiz CTA + 8 goal pills + recently-viewed
- Empty cart **page** (locale): "Your cart is empty" → **"Nothing in the basket yet."**, "CONTINUE SHOPPING" → **"Browse the apothecary"**
- Drawer cross-sell: "Frequently added with this" 3-product strip from top-health-supplements
- Stack5 promo voice: "Build the stack. Save 5%. Use code STACK5..."

### Article cleanup (65 of 125 articles)
Programmatic fixes pushed via Admin API:
- 48 articles: `Onelife Health` → `One Life Health`
- 15 articles: raw JSON-LD bleeding into body — stripped
- 8 articles: `TL;DR` → `The short answer`
- 4 titles: brand name fix
- 3 titles: emoji stripped
- 2 articles: `cutting-edge` buzzword removed
- All pharmacist → consultant (regulatory)
- "Proud to offer", "Discover the amazing", "game-changing", "revolutionary supplement", "must-have supplement" — all stripped

### CSS architecture
- Editorial layer with `--font-display` token
- Color palette tokens: forest / forest-2 / mint / sand / paper / ink / graphite / mist / gold
- Border-radius locked to 4 / 8 / 12 / 999px
- Gold sale badges (transparent + gold border) replace Bootstrap red `#dc2626` across vivid + quiz
- Sage footer links: `#a8c0a0` on charcoal

### Mobile chat button consolidation
- Chat toggle **shows on mobile homepage only** (was hidden on every mobile page)
- Hidden on PDP/cart/article/collection mobile to reduce float-button overload
- WhatsApp always visible
- Killed Codex's duplicate unscoped `display:none` rule

### Duplicate H1 hiding
- CSS rule hides Dawn's `.main-page-title` on `body.template-page` (where custom heroes exist)
- Same for collection pages

### Article featured images
- Codex wired up the 7 Apothecary guides with their matching collection hero images
- Working: image renders at top of each guide article

---

## 🟡 Issues identified but NOT shipped (lower priority, structural)

### Vivid Health page is 30,000 px tall on mobile
- Hero + 6 curated stacks + "Why Vivid" tiles + Browse-all 50+ product grid all stacked
- Needs collapse / pagination / "Show more" pattern
- Page weight 829KB on mobile

### Shop page is 25,000 px tall on mobile
- 16 category tiles + 12 featured product sections × 4 products each
- Too much for one mobile scroll
- Same fix: collapse or paginate

### Brands page is 41,000 px tall on mobile (!)
- All 254 brand pills/cards rendered at once
- Needs virtualization or topic filter
- Page weight ~700KB

### Some article featured images may not match topic
- Joints & Mobility article: featured image is turmeric pots + bath brushes (the joints-mobility collection hero) — user flagged as "wrong"
- Image actually matches Codex's collection-hero spec but doesn't read as "joints" visually
- Other 6 articles likely similar — could use bespoke photography

### Codex articles still need editorial pass
- Per the voice audit:
  - **Tier 1 — delete:** "Curveballs" piece, "Right to Feel Good" (Human Rights Day), Ozempic duplicate, all emoji-titled legacy articles
  - **Tier 2 — heavy rewrite:** Nootropics, Herbal Tonic, Women's Multis, Collagen, Best Supplements
  - **Tier 3 — light edit:** 15 solid articles (Quercetin, Ashwagandha, Sleep+Cortisol, Omega-3, Vit D)
  - **Tier 4 — unpublish:** 7 awareness-day essays + 2 boilerplate articles
- These require human editorial judgment, not regex

---

## 🟢 Pages that look great (verified via screenshot)
- ✅ Quiz page — perfect voice + Cormorant heading
- ✅ Cart empty page — "Nothing in the basket yet." + "Browse the apothecary"
- ✅ Search empty page — voice + 7 goal pills + quiz CTA
- ✅ About page — hero rewrite + 4 value tiles
- ✅ Blog index — "The Apothecary" hero + serif article cards
- ✅ 404 page — friendly headline + recovery tiles
- ✅ Footer (all pages) — sage links + brand line + no Powered-by-Shopify
- ✅ Centurion store page (after edge cache clears)

---

## Tooling used
- Playwright 1.56.1 headless Chromium (mobile iPhone 14 Pro viewport + 1440 desktop)
- Shopify Admin REST API for all theme writes
- 68 screenshots captured to `/tmp/screenshots/`
- 18 deployed-content checks via API — all passing

---

## What I'd do next
1. **Compact the Vivid/Shop/Brands mobile pages** — single biggest UX issue remaining
2. **Human editorial pass** through the 49 Codex-era articles (Tier 1-2 from voice audit)
3. **Bespoke photography** for each of the 7 Apothecary guides — current collection hero reuse is fine but not signature
4. **Bump cart drawer cross-sell** to live product recommendations API instead of static top-health-supplements collection

Total session work: 14 batches of fixes shipped to live theme, 65 articles cleaned, 1 footer rebuilt, 1 about page rewritten, comprehensive voice pass.
