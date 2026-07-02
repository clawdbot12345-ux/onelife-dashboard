# onelife.co.za — Mobile-First Visual + Performance Audit (2026-07-02)

Follow-up to `site-audit-2026-07-01.md`. iPhone 13 emulation (390x844) via Playwright+CDP, desktop secondary. ~83% of purchases are mobile.

## Prior-issue verification

| # | Issue (2026-07-01) | Status | Measurement |
|---|---|---|---|
| 1 | Hero pushed ~780px down on mobile | ✅ FIXED | Hero heading at Y≈383px, fully in first viewport; 4-stat block still eats ~13% of screen 1 |
| 2 | Vivid 30,000px / Brands 41,000px pages | ◐ PARTIAL | /pages/vivid now 404 (check inbound links); /collections/vivid-health 18,091px; /pages/brands 24,199px |
| 3 | 23 sub-32px tap targets | ◐ IMPROVED | 13 remain (slideshow dots, 5 hero CTAs at 27–32px, 3 value-prop links, announcement link) |
| 4 | Odd-cent prices; no VAT label | 🔴 (fix in flight) | 32% of variants odd-cent; "VAT" appears nowhere storefront-wide. Bulk rounding job running (2,643 variants, −R0.44 avg, down only); VAT label in theme patch |
| 5 | Vendor artifacts | ✅ FIXED TODAY | RELEASESCE (3 products) + Florish→Sebastian Siebert Supplements corrected via Admin API. Data smell remains: 237/250 titles start with vendor name (duplicated on cards) — owner decision, SEO-sensitive |
| 6 | Blank bands on full-page shots | ✅ NOT REAL | Lazy-load screenshot artifact; zero content gaps ≥500px |
| 7 | "magnesium" search: kids chew #1 | 🔴 OPEN | Still #1 of 418. Fix = Search & Discovery boosts + demote Kids to filter (app config) |

## Performance (mobile, lab)

| Metric | Home | Collection | PDP |
|---|---|---|---|
| Requests / bytes | 330 / **5.3MB** (regressed from 3.4MB) | 340 / 3.9MB | 448 / 4.0MB |
| LCP | 1.38s (hero webp) | 1.70s | 1.41s |
| CLS | 0.0004 load; 0.356 scroll (lazy section) | **0.336 (rotator)** | clean |

Top offenders: googletagmanager 443KB — **gtag loaded 2× per ID** (Analyzify + native channel double-inject); **Analyzify = 5 synchronous render-blocking head scripts**; homepage collection tiles are 200–317KB JPGs (~1MB recoverable); Klaviyo 26 requests; Smile 10; raw HTML 565KB.

## New issues (mobile)

High: badge row clipped under Add-to-cart on cards · ragged card heights · collection CLS 0.34 (rotator) · WhatsApp FAB covers titles/badges/footer.
Medium: sticky header overlaps "Filter and sort" · breadcrumb shows "Brand - CANNACO" · pickup location named "One Life Health Supermarket" · Add-to-cart and Buy-it-now visually identical · orphaned "No reviews" + bare review form (zero social proof) · newsletter block mid-cart page · author box/related-articles not on pre-merge articles (new articles will have them).
Low: popup covers hero at 10s · logo lockup mismatch · quiz trust chips low contrast · "Add R74.49 for free delivery" odd-cent symptom.

## Fixes executed today

- DATA: bulk price rounding (2,643 variants, snapshot-first) · RELEASESCE ×3 · Florish vendor.
- THEME (on "LIVE + MOBILE FIXES 2026-07-02" copy — owner publishes): CLS rotator reserve, card badge/height fixes, WhatsApp FAB offset, Buy-it-now outline, Judge.me zero-state hide, sticky-header fix, VAT-incl label, collection-tile image sizing.

## Remaining (owner/Codex)

1. Publish the patched theme (1 click).
2. Search & Discovery: boost bestsellers, demote Kids products for generic terms, synonyms.
3. Dedupe Google tags (Analyzify vs native channel — pick one per ID) and make Analyzify embeds async → biggest real-world mobile speed win.
4. Rename Shopify location "One Life Health Supermarket" → "One Life Health Centurion".
5. Duplicate products (e.g. Credé Almond Butter 400g twice at R93.72/R133.67) + price anomaly (Bio-Liquid Dish 750ml R979 vs 5L R216) — merge/fix.
6. Decision: strip vendor prefix from 237 product titles (cards say brand twice) — SEO-sensitive, recommend staged.
7. Brands page (24k px): add A–Z jump index. Consider collapsing collection-page guide into accordion.
8. /pages/vivid 404 — 301 it to /collections/vivid-health.
