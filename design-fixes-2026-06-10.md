# Design & Correctness Fixes — 2026-06-10 session

**Theme:** GROWTH BUILD 2026-06 (185971867958, unpublished — live theme untouched)
**Trigger:** Owner review with screenshots (iPad): oversized menu, wrong stack prices,
bad cart drawer, weak brands-page filters, plain narrative pages, wrong payment icons.

## 1. CRITICAL — Stack price bug (all 17 protocol pages)

`sections/dispensary-protocol.liquid` computed the bundle price as:

```liquid
assign discounted_total = stack_total | times: 100 | minus: stack_total | times: saving_pct | divided_by: 100
```

Liquid chains filters left-to-right, so this evaluated to
`((total×100 − total) × 10) ÷ 100` = **9.9× the real price** instead of 90% of it.
The GLP-1 Companion stack displayed **R17,582.40** instead of **R1,598.40**.

Fixed to:

```liquid
assign pct_remaining = 100 | minus: saving_pct
assign discounted_total = stack_total | times: pct_remaining | divided_by: 100
assign you_save = stack_total | minus: discounted_total
```

Also: the "SAVE 10%" corner ribbon now uses the section's `saving_pct` setting
instead of a hardcoded 10%.

## 2. Payment methods — honesty fix

`snippets/cart-payment-trust.liquid` showed Apple Pay, G Pay, Shop Pay, Payflex,
PayJustNow and Ozow — none of which are active. Shopify Payments (the prerequisite
for Apple/Google/Shop Pay wallets) **is not available in South Africa**.

Now shows only what the store actually offers via **Payfast**: VISA, MASTERCARD,
INSTANT EFT, PAYFAST + "Secure checkout via Payfast" line. The "Or pay in 4 with
Payflex/PayJustNow" upsell line was removed until those apps are actually installed.

## 3. Header menu — world-class rebuild

The header pointed at the flat `collections` navigation menu: 27 top-level links,
zero nesting → a 4-row text wall on desktop.

- Created new Shopify navigation menu **`main-nav-2026`**: 7 top-level items
  (Shop · Popular · The Dispensary · Vivid Health · Brands · Learn · Stores & Help),
  each with mega-menu children (categories, popular ingredients, protocols, top brands).
- Header group updated to use it (`menu_type_desktop: mega` was already set).
- Announcement bar copy fixed: "8 consultant-signed stacks" → 17.

## 4. Cart drawer polish

`snippets/cart-drawer.liquid`:
- Checkout button now full-width, 52px, proper shadow (was rendering as an odd block).
- Estimated total uses `money` (drops the "ZAR" suffix), 24px forest-green emphasis.
- New "You're saving R…" pill when any discount is applied.
- Item rows: bordered rounded thumbnails, tighter typography, softer remove button.
- Tax note + tag disclaimer visually de-emphasised; drawer capped at 440px on desktop.

## 5. Brands page — proper filters + A–Z directory

`snippets/brands-page.liquid`:
- Sticky filter bar (search + chips + live result count).
- New "★ Featured" chip; SA Made / International classification expanded from
  **21 brands to ~180** (the old filter made most brands vanish).
- All-brands section rebuilt as an **A–Z directory**: letter index bar, grouped
  sections, brand cards with letter avatars, de-duplication, alphabetical sort.
- Removed the confusing second search box.

## 6. Narrative pages — photographic heroes

All six "plain" pages got lifestyle-photo heroes (assets were already in the theme,
just unused) with dark-green gradient overlays and white display type:

| Page | Hero image |
|---|---|
| About (Heritage) | onelife-about-page-hero |
| Health Consultants | onelife-consultation-hero-banner |
| Practitioner Pricing | onelife-store-centurion-hero |
| Vivid Health Story | onelife-vivid-health-page-hero |
| Subscribe & Save | onelife-hero-01-unboxing |
| Build Your Stack | onelife-quiz-hero-banner |

## 7. Grid fill + colour variety

- iPad/tablet (750–989px): product grids now show **3 per row** instead of 2 chunky cards.
- Very wide screens (≥1500px): collection grid relaxes to 5 per row.
- Guide-card grids switched to `auto-fill` so they never strand empty space.
- Shop page quiz CTA switched to a warm amber treatment — first step away from
  green-everywhere; more accent work recommended (see below).

## SA payment options — research for owner decision

Available to SA Shopify stores (Shopify Payments is NOT available in SA):

| Provider | Type | Notes |
|---|---|---|
| **Payfast (current)** | Gateway | Visa, Mastercard, Instant EFT, Mobicred, MoreTyme, SnapScan/Zapper QR. Keep as primary. |
| **Peach Payments** | Gateway | Alternative full gateway; Apple Pay support on some plans. |
| **Ozow** | Instant EFT | Popular bank-to-bank; good for card-averse shoppers. Shopify app. |
| **Payflex** | BNPL — pay in 4 | Zero interest. Shopify app. Strongest BNPL brand recognition in SA health/beauty. |
| **PayJustNow** | BNPL — pay in 3 | Zero interest. Shopify app. |
| **Float** | Card installments | Uses shopper's existing credit card limit; no new credit. |

**Recommendation:** keep Payfast primary; install **Payflex** (or PayJustNow) for
BNPL — typical AOV lift on R400–R1,800 baskets is meaningful, and the protocol
stacks (R600–R1,800) are exactly the BNPL sweet spot. Add Ozow if checkout data
shows EFT demand. Once installed, re-add the badges to the cart trust strip.

## Still open (needs owner / next session)

- Publish decision on the GROWTH theme (preview first).
- Install chosen BNPL app, then restore its badge in cart trust strip.
- Homepage TTFB reduction (section count) — unchanged from previous audit.
- More colour-system variety across landers (amber/cream secondary established on shop page).
- Replace ~20 older article hero images (needs image generation).
