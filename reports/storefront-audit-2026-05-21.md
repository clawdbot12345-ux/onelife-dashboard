# Onelife Storefront Audit — 2026-05-21

**Site:** https://onelife.co.za
**Scope:** End-to-end audit — design, ease of use, SEO, speed
**Lens:** Mobile-first (majority of SA retail traffic is mobile)
**Methodology:** Live HTTP fetches with iPhone user-agent, raw HTML parsing of homepage + PDP + PLP, CDN + compression checks, JSON-LD inspection, third-party payload sampling. Lab CWV from Google PSI was throttled (HTTP 429) so field signals below are derived, not CrUX-confirmed — recommend re-running PSI for confirmation.

---

## Scorecard

| Area | Grade | One-line verdict |
|---|---|---|
| Design / brand | C | Functional Shopify theme, but hero asset is a phone-cam PNG and the homepage is a CTA pile — no brand story |
| Ease of use (mobile) | C+ | Predictive search and cart drawer are good; mega-menu with 80+ links and sold-out featured PDPs hurt |
| SEO — on-page | B− | Strong blog hub, clean canonical/OG, good Product schema; missing Review/Breadcrumb/FAQ schema |
| SEO — catalog | C | `/collections/all` exposes 4,238 products across 265 pages with only 2 filters — discoverability gap |
| Speed (mobile) | C+ | Brotli + Cloudflare + WebP + fetchpriority hero are right; 27 ext / 70 inline scripts + 35 CSS files + 8 trackers drag it back |
| Accessibility | B− | Alt text present on PDP gallery, but home announcement bar relies on color only; nav has 80 tappable items |

---

## 1. Mobile-first findings (lead with these)

### M1 — Tracker payload is doing the heavy lifting on mobile CPUs
Detected on the homepage: **GA4 (`G-FQ819LGSV3`), Google Tag Manager, Klaviyo (`company_id=S86r7e`), Judge.me, Hotjar, TikTok, Pinterest, Facebook references, Shopify Monorail**. That's 8 distinct third parties, each adding 30–150 KB of JS and contributing to Total Blocking Time on mid-range Android. Mobile is where this hurts most.
- **Fix:** Audit which of TikTok / Pinterest / Hotjar are actually used by marketing. Disable any unused pixels. Move what remains behind GTM with `<script async>` and consent gating. Defer Hotjar to `requestIdleCallback`.

### M2 — Sticky element pile-up
On mobile the user is competing with: announcement bar (top), sticky header, bottom mobile-nav bar (`.ol-mobile-nav`), chat widget (bottom-right), cookie/consent overlay (Shopify default). On a 360×640 viewport that's roughly **~22% of the screen** lost to chrome before any product is visible.
- **Fix:** Collapse the announcement bar after first scroll. Hide the chat widget bubble on PDPs until the user has scrolled past the buy box, or replace it with a single "Ask a consultant" CTA inside the PDP.

### M3 — Featured PDP is sold out
`/products/781159888755` (NEUROACTIVE Neuro Day) is reachable via the on-site nav but shows "Sold out" with no in-stock alternatives, no notify-me form, no related products list. This is a dead conversion path that mobile shoppers won't recover from with a tap-back.
- **Fix:** Hide sold-out items from "Top Supplements" and merchandised rails. On PDPs, render an "In-stock alternatives" rail above the fold when `availability=OutOfStock` (Shopify Liquid: `unless current_variant.available`). Add a "Notify me" email capture wired to Klaviyo.

### M4 — Mega-menu has ~80 items
The desktop mega-menu (13 top-level groups, 27+ "Health Conditions" sub-items, 11 "Health Supplements" sub-items) collapses into a single hamburger on mobile. That's roughly **80 tap targets behind one button**, with deep accordions. SA users on 3G/LTE pay for each interaction.
- **Fix:** Cap the mobile menu at ~5 top-level entries (Shop, Conditions, Brands, Consult, Account). Push the long tail to the "Conditions" landing page. Add visited-link styling so users can see where they've been.

### M5 — Hero image is a screenshot-style PNG
`IMG_0318.png` (filename suggests phone-camera origin) is a 2000×672 promotional banner with text baked into the image. Pros: it preloads correctly with `fetchpriority=high` and a 7-step srcset (360–2000w), and Shopify CDN serves WebP via `Accept` negotiation (verified: width=800 PNG → 64 KB WebP, vs 465 KB PNG). Cons: text-in-image is uncrawlable, untranslatable, and renders blurry on hi-DPI when scaled.
- **Fix:** Render the banner as a CSS+HTML composition (real `<h1>`/CTA over a small lifestyle image). Bonus: the LCP element becomes text, which paints earlier than an image.

---

## 2. Design & brand

### D1 — Homepage is 9 promotional sections stacked
Order: hero banner → "Free Delivery R400" → "Book Free Consultation" → Shop by Health Goal → Shop by Dietary Preference → Featured Categories → Top Supplements → second "Book a Free 15-Min Consultation" → "One account. All the benefits." → "Health Hub — Our Blog" → footer. **Two consultation CTAs** in the same scroll, no editorial moments, no proof.
- **Fix:** Cut to 5 modules: hero with a real value prop, social proof rail (Google/Judge.me stars, store photos, "15+ years" credential), Shop-by-Goal, Top Supplements (in-stock only), Blog. Keep the second consult CTA but anchor it to the footer pre-CTA only.

### D2 — Brand identity reads as generic Shopify
- "Powered by Shopify" exposed in the footer leaks platform identity to a wellness audience that values curation.
- Logo is wordmark-only (Cabin font, preloaded — good engineering, weak brand).
- No founder photo, no store photos, no "from our Centurion shelves" texture.
- **Fix:** Remove the "Powered by Shopify" line (theme setting → disable). Add a "Visit us in Centurion / Glen Village / Edenvale" rail with one real photo per store — credibility, local SEO, and a brand voice in one block.

### D3 — Announcement bar is a wall of equal-weight messages
Detected content suggests rotating/comma-joined: "FREE DELIVERY on orders over R400 nationwide" + "Get 10% off — join our community" stacked. No visual hierarchy.
- **Fix:** Pick one. Free delivery threshold is the higher-converting message for an unfamiliar visitor; "10% off" belongs in an exit-intent or scroll-50% modal where it can be measured.

---

## 3. Ease of use

### U1 — `/collections/all` has 4,238 products on 265 pages with 2 filters
Only **Availability** and **Price** filters are exposed. No Brand (despite 100+ brands), no Dietary (Vegan/Gluten-Free/Organic), no Condition, no Form (capsule/powder/liquid/tincture), no Rating. This is the single biggest mobile friction point — once a user lands here from search, they cannot narrow.
- **Fix:** Enable Shopify Search & Discovery filters for `tag`, `vendor`, and a small set of metafields (`dietary`, `form`, `condition`). Same effort, transforms PLP UX.

### U2 — Predictive search exists but is hidden behind an icon
`predictive-search` and `search-modal` are wired (good). On mobile the search trigger is an icon in the header. Given that 60–70% of supplement shoppers arrive with a product name in mind, this should be visible as a full search bar, not a magnifying glass.
- **Fix:** Replace the mobile-header icon with an inline search bar (Amazon/Takealot pattern). Free real estate from the cluttered header by collapsing the WhatsApp icon into the bottom nav.

### U3 — PDP buy-box is below the fold
On the sampled PDP, add-to-cart sits below the description and quantity selector. The Shopify default places the price + ATC above the description, so this is a theme override worth reverting.
- **Fix:** Buy box (price, stock pill, qty, ATC) above the fold on mobile. Add a sticky ATC bar that appears once the user scrolls past the original button (the theme already has 8 `sticky` references — likely 90% built).

### U4 — Reviews loaded but not surfaced
Judge.me is loaded on every page (6 script references on home, 11 KB+ raw JS preload) but the sampled PDP shows "No reviews" and **no `aggregateRating` JSON-LD**. Either products genuinely have no reviews (in which case Judge.me is wasted JS) or reviews exist but aren't rendering in schema (in which case rich-result stars in Google are being left on the table).
- **Fix:** Run a Judge.me review-import campaign (CSV from Shopify orders past 12 months → request review emails). Wire the Judge.me widget's `aggregateRating` into the Product JSON-LD via the official theme integration.

### U5 — No "store pickup" mode in cart
PDP shows "Store pickup in Gauteng" as a trust signal, but it's static copy, not an actual pickup-locator/option in the cart. SA shoppers near Centurion/Glen Village/Edenvale would convert higher if they could see "In stock at Centurion — collect today".
- **Fix:** Enable Shopify Local Pickup per location and surface real-time availability on PDP.

---

## 4. SEO

### S1 — Strengths to keep
- Single H1 per page, correctly populated (`Health Supplements South Africa | Onelife Health` on home).
- `<link rel="canonical">` present and correct on home and PDP.
- OG tags complete (title, description, image, type, url).
- Three JSON-LD blocks on home: `HealthAndBeautyBusiness`, `Organization`, `WebSite` (with `potentialAction` search action — good).
- PDP has `Product` schema with `Offer` (price ZAR, availability, url) and `Brand`.
- Sitemap index lists products / collections / pages / blogs / agentic-discovery (Shopify default).
- `robots.txt` properly blocks crawl traps (filter/sort params, preview themes) and admin/cart paths.
- Blog hub `/blogs/health-wellness-hub/*` has well-titled 2026 evergreen guides (Best Probiotics SA, Best Vitamin D SA, Joint & Bone, Collagen marine vs bovine vs vegan). This is your strongest SEO asset.

### S2 — Missing structured data on PDP
The sampled PDP is missing:
- `BreadcrumbList` (HTML breadcrumb exists; schema doesn't)
- `Review` / `aggregateRating` (Judge.me loaded but unused — see U4)
- `gtin` / `mpn` (only `sku` is populated)
- `FAQPage` (no on-PDP FAQ markup)
- `weight` / `width` / `height` (Shopify has the data; theme doesn't expose it)
- **Impact:** No star-rating rich result, weaker Google Shopping/Merchant Center match, no FAQ accordions in SERP.

### S3 — `/collections/all` has weak SEO surface
- Title: "Products" (generic, no brand suffix, no keyword).
- Meta description: not visible in HTML.
- H1: "Products" (per WebFetch).
- 265 paginated pages, all canonical-pointing to themselves, all near-duplicate templates.
- **Fix:** Either `noindex` the `/all` collection and rely on themed collections to rank, or rewrite the title to `Shop All Supplements & Wellness Products — Onelife Health SA` and write 120-word intro copy. Add `rel=prev/next` is no longer used by Google but consolidated canonical to page 1 helps consolidate signals.

### S4 — Collection intro copy is good but only on `/collections/health`
The flagship Health Supplements collection has a 120-word intro with relevant keywords. Most other collections likely don't (the 2026-05-01 SEO audit flagged **150 collections without an image and 9 without a description**). On mobile this matters because users land on `/collections/sleep` from Google and see a wall of product cards with no orientation.
- **Fix:** Auto-generate (LLM-assist) a 60–80 word intro + a 200 word "What to look for" block for the top 30 collections by traffic.

### S5 — Hreflang absent, but only `en-ZA` is the target
Single-country site, fine. **But** declare `<link rel="alternate" hreflang="en-za" href="https://onelife.co.za/" />` and `<link rel="alternate" hreflang="x-default" ...>` to signal intent. Helps when Google considers showing the site to en-US searchers near SA.

### S6 — Blog assets to lean into
The `/blogs/health-wellness-hub/` is currently the strongest organic surface. Internal-link audit recommendation: each blog post should link to the relevant collection (best-probiotics-south-africa → /collections/probiotics) and 3–5 in-stock products, with `rel="" target="_self"`. This is mechanical and high-ROI.

---

## 5. Speed (mobile)

### Measured (this session, iPhone UA from US edge)
| Metric | Value | Verdict |
|---|---|---|
| TTFB (home) | 917 ms | High. Target <600 ms. Likely better from a SA edge (Cloudflare PoP CPT/JNB), but server-timing shows `render;dur=49ms` so the slow part is upstream not Shopify-render. |
| TTFB (PDP) | 479 ms | Acceptable. |
| Compression | Brotli level 5 | Good. |
| CDN | Cloudflare (ORD edge in this test) | Good. |
| HTML transfer | 372 KB raw → ~70 KB Brotli | Acceptable for a Shopify storefront, but the inline JS + theme settings are the bloat. |
| Hero image strategy | `fetchpriority=high` + 7-step srcset 360–2000w + WebP via Accept negotiation | **Correct.** Width=800 served as 64 KB WebP. |

### Diagnostic counts (homepage)
- **External scripts:** 27
- **Inline scripts:** 70
- **Stylesheets:** 35 ← biggest red flag; Shopify themes typically concatenate to 3–5
- **Total `<img>`:** 20 (5 lazy-loaded, 6 with srcset on hero/banner block)
- **Third-party domains:** googletagmanager.com, klaviyo.com, judge.me (×3 hosts), monorail-edge.shopifysvc.com, plus referenced facebook/tiktok/pinterest

### Speed wins, ranked by ROI
1. **Concatenate / drop stylesheets (35 → ≤5).** Many of those are theme settings + per-section CSS. The current theme is loading section CSS as separate `<link>` tags rather than inlining critical CSS. Use Shopify's `{% style %}` or inline above-the-fold CSS. Estimated mobile FCP improvement: 300–700 ms.
2. **Audit 70 inline scripts.** Most are Shopify theme settings JSON dumps. Move to a single `<script type="application/json" id="theme-settings">` block parsed once, not 70 separate parse events. Estimated TBT improvement: 100–250 ms.
3. **Defer Hotjar + Judge.me preloader until `requestIdleCallback`.** Neither needs to fire on first paint.
4. **Remove unused tracking pixels.** Confirm with marketing which of FB / TikTok / Pinterest are running active campaigns; turn off the rest. Each removal saves 50–150 KB and ~30 ms of main-thread work.
5. **`<link rel="preconnect">` is correctly set for `fonts.shopifycdn.com`.** Add one for `static.klaviyo.com` if Klaviyo's onsite forms run on most pages.
6. **HTTP/2 push / Early Hints already used** (server-timing shows `earlyhints`) — good.

---

## 6. Accessibility (spot-check)

- Viewport meta present and correct.
- Hero LCP image has descriptive alt: `"Onelife Health supplement promotion"` — acceptable but generic; would be better at describing the offer.
- All PDP gallery images had alt text and lazy-loading (good).
- 80 nav tap targets behind a single hamburger is a screen-reader rotor nightmare. Use `<nav aria-label="Primary">` + grouped `<ul>` with `<h2>` headings so VoiceOver/TalkBack users can skim.
- Color-only signaling in the announcement bar (red/green pills) — add an icon or text label.
- Cabin webfont is preloaded with `crossorigin` — good. Confirm `font-display: swap` is set in the `@font-face` declaration to avoid invisible text during FOIT on slow networks.

---

## 7. Prioritized action list (next 4 weeks)

**Week 1 — quick wins, no dev cost**
- [ ] Disable any unused tracking pixels in GTM (TikTok / Pinterest / FB if dormant).
- [ ] Remove "Powered by Shopify" footer text.
- [ ] Drop second homepage consultation CTA; keep one.
- [ ] Replace announcement bar dual message with a single "Free delivery over R400".
- [ ] Hide sold-out products from "Top Supplements" rail.

**Week 2 — theme settings + Shopify Admin**
- [ ] Enable Search & Discovery filters (`vendor`, `tag`, `dietary` metafield) on all collections.
- [ ] Add Local Pickup per location; surface on PDP.
- [ ] Move PDP buy-box above the description; enable the existing sticky ATC.
- [ ] Replace the hamburger menu's flat 80-item dump with 5 top-level groups.

**Week 3 — SEO compounders**
- [ ] Wire Judge.me `aggregateRating` into Product JSON-LD.
- [ ] Add `BreadcrumbList` + `FAQPage` JSON-LD to PDPs.
- [ ] Auto-generate intro copy for top 30 collections (use the dashboard's existing LLM tooling).
- [ ] Internal-link audit on blog posts → collections + 3–5 products each.
- [ ] Either `noindex` `/collections/all` or rewrite its title/meta/intro.

**Week 4 — performance**
- [ ] Concatenate the 35 stylesheets to ≤5 (theme dev task).
- [ ] Consolidate 70 inline theme-settings scripts into one parsed-once JSON block.
- [ ] Defer Hotjar + Judge.me preloader to idle.
- [ ] Re-run PSI mobile audit; track LCP / INP / CLS before/after.

---

## 8. What we couldn't verify in this audit
- Field CWV (CrUX) data — PSI API was rate-limited.
- Checkout flow (`robots.txt` correctly disallows automated probing).
- Logged-in / rewards experience.
- Search results quality (would need ~20 query samples).
- Real device perf on a low-end Android (Moto G4 budget) from a SA network.

**Recommend** running Lighthouse mobile + WebPageTest from Johannesburg PoP, and a 5-user moderated mobile usability test with the buy box and PLP filter changes in scope.

---

_Generated 2026-05-21 from live HTTP fetches; no admin access required. See also `reports/seo-audit-2026-05-01.md` for catalog-level SEO findings (4,240 products, 1,321 with issues, 150 collections with no image)._
