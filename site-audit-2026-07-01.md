# onelife.co.za — Conversion & Marketing Site Audit
**Date:** 2026-07-01 · **Method:** Live Playwright audit (Chromium), desktop 1440×900 + mobile 390×844, plus raw-HTML/JSON-LD analysis of homepage, PDP, collection, cart, checkout step 1, blog and policy pages. Theme: Shopify Dawn 14.0.0 ("AUDIT FIXES 2026-06-13"). No purchase completed; no personal data entered.

Companion to `marketing-strategy-2026-07.md` (§3 "Fix the leaks first").

---

## CRITICAL

**C1. Free-shipping promise contradicts the official Shipping Policy — sitewide.**
Announcement bar, popup, PDP and cart all say *"🚚 FREE DELIVERY on orders over R400 nationwide"*; the cart drawer at R645 says *"🎉 You qualify for free nationwide delivery!"*. But `/policies/shipping-policy` states: *"Gauteng: Free delivery on orders over R900. Nationwide: Free delivery on orders over R1,400. Standard Delivery Rates: Gauteng R75 flat rate, Nationwide R130 flat rate."* Either customers are being charged shipping they were promised free (chargeback/complaint/CPA risk) or the policy page is stale and undermines the store's most-repeated promise at the exact moment cautious buyers verify it. Delivery-time claims also disagree: footer "1–5 working days" vs PDP "3–7 business days" vs policy "2–5 working days". **Fix the policy page same-day.**

## HIGH

**H1. No Meta pixel, no TikTok pixel.** Zero `fbq(` and zero `ttq` references in the HTML. Present: GA4 (G-FQ819LGSV3), Google Ads (AW-11098746320), Microsoft Clarity, Klaviyo onsite. R6k/mo of Meta+TikTok ads have been running with no conversion measurement, no retargeting audiences, no lookalikes possible.

**H2. Best-seller has zero reviews.** Delfran Pcositol (R645, #1 seller) shows "No reviews". Judge.me is installed but idle; Product JSON-LD `aggregateRating: None` → no star rich-snippets in Google. Post-purchase review-request flow + REVIEW25 credit fixes supply within weeks.

**H3. No subscription option on replenishable products.** No selling-plan widget (`subscription: false` in product JSON). 30-day repurchase products with no autoship = the single biggest missing LTV lever; no verified SA competitor offers one.

**H4. No BNPL / local wallet options visible.** Checkout shows only "Payfast +3" (Visa/MC/Instant EFT) with a redirect notice. No Payflex, PayJustNow, Zapper/SnapScan or Ozow as distinct options; no installment messaging on PDPs ("4 × R161 with Payflex"). At a R566 ex-VAT AOV this measurably suppresses SA conversion.

## MEDIUM

**M1. Old low-res purple "one Life" logo at checkout** while the storefront runs the new green branding — brand discontinuity at the payment step (see `checkout-step1-mobile.png`).

**M2. Pre-ticked marketing consent (POPIA risk)** on both the email popup and checkout news/offers checkbox. April 2025 POPIA regulations require express opt-in ("opt-out shall not constitute consent"); pre-ticked boxes also fill Klaviyo with low-intent profiles.

**M3. Odd-cent pricing + no VAT labelling.** Grid prices like R440.06, R154.51, R80.01 read as ex-VAT conversion/sync artifacts, not retail prices. No "incl. VAT" label anywhere near prices; checkout says taxes "calculated at checkout". SA consumer prices should display VAT-inclusive and labelled.

**M4. Mobile above-the-fold consumed by pre-header stack.** Announcement bar + 4-stat trust block + quiz banner + header push the hero ~780px down on mobile (`home-mobile.png`). Desktop fine. Collapse or reorder on mobile.

**M5. Data-hygiene artifacts visible to shoppers.** Vendor "RELEASE_SCE" in cart upsells; product names in vendor fields ("Vendor: FLORISH SPORE PROBIOTIC…"); a sold-out item (Viridian Grape Seed) in the "Frequently Added" upsell row.

**M6. Refund policy is thin** (714 chars): no return window, no refund timeline, no exchange process. CPA-relevant; a pre-purchase objection for first-time buyers.

**M7. Duplicate Product JSON-LD on PDPs** (theme block + custom block with `shippingDetails`), slightly different offer payloads — Google may pick either. Consolidate to one.

**M8. Very broad collections dilute discovery.** "Gut Health & Digestion" = 584 products; "magnesium" search returns 418 results with a kids' chew first. Boost best-sellers, tighten tagging.

## LOW

- **L1.** Homepage links zero `/products/` URLs (all paths via quiz/collections) — add a Best Sellers row for high-intent/returning visitors.
- **L2.** Homepage 356 requests / ~3.4 MB (load ~3.3s via proxy); PDP 297 requests / ~2.7 MB (~4.7s). Images well-optimized (WebP, ≤97 KB); weight is app/script sprawl. Prune apps.
- **L3.** 23 sub-32px tap targets in first 2000px on mobile (footer/social/quantity icons). No horizontal overflow.
- **L4.** PDP "Pickup currently unavailable at Glen Village South" next to "Only 2 left at Centurion" — accurate but confusing multi-store phrasing.
- **L5.** Full-page captures show blank bands below main content (likely lazy-load sections not rendering under scripted scroll) — verify no genuinely empty sections.

---

## What's already strong (keep)

- **5-second clarity passes:** "South Africa's apothecary, since 1996" + trust strip (10,000+ products / 250+ brands / 3 stores / 30+ years) + quiz hero with clear CTAs.
- **Differentiation:** free WhatsApp consult, 17 consultant-signed Dispensary stacks (10% off), supplement quiz, Vivid house range, PDP trust badges ("SA stock — no import wait").
- **Cart:** drawer on add-to-cart, free-shipping progress bar, STACK5 prompt, cross-sells, payment badges, "your card details never touch our server".
- **Checkout:** guest checkout (email or phone), Ship/Pickup toggle, discount field — low friction up to payment.
- **Credible urgency:** "Only 2 left at Centurion — Order today for same-day dispatch."
- **Search/discovery:** predictive search surfaces products + guide pages; logical nav; editorial collection banners with linked guides; dietary badges on cards.
- **SEO fundamentals:** unique titles, meta with the R400 hook, canonicals, OG + custom social card, single H1, JSON-LD Organization/WebSite/HealthAndBeautyBusiness×3 + Product w/ Offer & shippingDetails; robots.txt 200; all four policy pages exist.
- **Email capture:** Klaviyo popup ~9–12s, clean 10% first-order offer, dismissible; footer signup block (fix M2 consent).
- **Blog:** 12 posts, weekly cadence through June, SA-localized SEO titles, strong internal linking (magnesium post → 7 product pages).
- **Mobile sticky bottom nav:** Home / Rewards / Quiz / Cart / Account — app-like.

## Top 5 actions by expected impact
1. Reconcile shipping policy vs the R400 promise (C1) — same day.
2. Post-purchase review requests + stars in consolidated JSON-LD (H2/M7).
3. Payflex or PayJustNow + PDP installment messaging (H4).
4. Install Meta + TikTok pixels (H1).
5. Subscribe & Save on top 50 replenishable SKUs (H3).

*Screenshot evidence (session scratchpad): home/collection/PDP/cart/checkout in both viewports, popup states, predictive search — 15 captures + findings.json + raw HTML of audited pages.*
