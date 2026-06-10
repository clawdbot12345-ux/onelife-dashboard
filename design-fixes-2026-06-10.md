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

---

# Round 2 — same day (owner feedback on menu content, colour, blog CTAs, GLP-1)

## Upload recovery
The round-1 background upload only delivered 3 of 9 files (cart drawer, brands page,
about hero). The remaining six (consultants/practitioner/vivid/subscribe/stack-builder
heroes + grid CSS) were re-uploaded and verified this round.

## Menu content v2 (world-class IA)
`main-nav-2026` rebuilt as a true 3-level mega menu — 6 top-level items:
- **Shop**: By Category (8) · By Health Goal (10) · Most Shopped (8 ingredients)
- **The Dispensary**: Consultant Protocols (top 6 + "View all 17") · Do It Yourself
  (Build Your Stack, Quiz, Subscribe & Save) — GLP-1 no longer floats redundantly
- **Vivid Health**: Shop + Story
- **Brands**: International (7) · South African (7) · "All 250+ brands A–Z"
- **Learn**: 6 real buyer's guides (GLP-1, Magnesium, Collagen, Protein, Vit D, Gut) + Journal
- **Help & Stores**: WhatsApp consult, consultants, contact, about, practitioner, rewards, delivery

## Colour system (global)
`assets/onelife-grid-fixes.css` (loaded site-wide via whatsapp-float) now carries a
category accent palette: every health goal gets its own colour (immunity amber, sleep
indigo, gut teal, energy orange, women pink, men slate, heart rose, …) applied to the
Apothecary category tiles, Dispensary hub cards, brand filter chips and cart promo.
Narrative pages got colour-coded benefit cards + warm amber CTA bands. Forest green
remains the anchor for primary CTAs and trust.

## GLP-1 Companion stack
Added **Sport RX Protein Rx (Vanilla Caramel 800g)** as item 1 with a consultant note —
protein is the most important muscle-preservation lever on a GLP-1 and was missing.
Stack is now 5 products; verdict copy updated.

## Blog product CTAs — finding
NOT cut: `main-article.liquid` still renders the conversion kit (intro + footer) on
every article, with topic-matched shop links for 9 topics and a generic fallback.
The dynamic product-pick cards only render on articles with the
`apothecary.picks` metafield (the 2026 cornerstone guides). Recommended next:
backfill picks metafields on the top-20 trafficked articles + extend the keyword map
(ashwagandha, creatine, iron, zinc, menopause, detox, joints, kids).

---

# Round 3 — same day (Apothecary in menu, marquee colour, image uniformity, blog all-articles, tagging)

- **Menu:** top-level "Shop" renamed **The Apothecary** (→ /pages/shop) — the brand
  identity now leads the nav. "Help & Stores" shortened to "Help" for one-row fit.
- **Brands marquee v2:** grey text → coloured pill chips cycling 6 palette accents;
  Vivid Health chip in solid forest with shadow.
- **Product image uniformity (no-cost pass):** `mix-blend-mode: multiply` + warm
  uniform tile (#f7f4ed) + contain/padding applied to all product imagery (Dawn cards,
  Apothecary/shop grids, brands grids, protocol items, cart, blog picks). Melts
  mismatched white supplier backgrounds into one consistent shelf look. Evaluate this
  before paying for batch background removal.
- **Blog picks — ALL articles:** `article-guide-picks.liquid` v2 now derives 3
  shoppable consultant picks from the article topic when no metafield exists
  (17 topic maps + consultant-favourites default, real handles, OOS auto-skip).
  Every one of the 125 articles now has product cards + add-to-cart.
- **Tagging:** background agent auditing the full active catalogue; ADD-only fixes
  with title-level evidence (Vegan/Vegetarian/Gluten Free/Sugar Free/Dairy Free/
  Organic/Non-GMO/Keto), full CSV change log, typo report for human review.
- **Subscribe & Save:** owner to install app (recommended below), then selling plans
  get configured on repeat-purchase SKUs and the page flips from interest-list to live.

---

# Round 4 — premium design pass (Codex Vivid page as the bar)

Adopted the Vivid-page design language across all custom surfaces:
- **Serif display type** (Cormorant Garamond) on every hero H1 — hub, protocols,
  landers, shop, brands, all narrative pages. Matches the homepage serif + Vivid page.
- **Botanical photographic texture** layered under the dark-green gradient on the
  hub / protocol / lander heroes (no more flat green boxes).
- **Glass stat chips** on the Dispensary hub (Vivid-page pattern).
- **Warm paper world**: theme scheme-1 background #FFFFFF → #FAF7F0, scheme-2 →
  #F4EFE4; all custom pages aligned; white cards lift off the paper with soft
  warm shadows. "ZAR" currency suffix disabled store-wide.
- **Badge semantics fixed**: SA Made = SA-flag green (#007749) — plus a meaningful
  palette (gluten free = wheat amber not RED, sugar free = blue, dairy free = sky,
  organic = olive, keto = violet, non-GMO = teal). Applied to both badge systems.
- **Add-to-cart alignment**: badges get a fixed 2-row zone, buttons pin to card
  bottom full-width — rows now align across every grid.
- **Menu**: "Guides & Journal" column added to The Apothecary mega menu
  (Journal, GLP-1 guide, Magnesium guide, Quiz, Tag guide).

---

# Round 5 — brands page live data, homepage colour bands, product-page tags

- **Brands page v3**: featured brand sections now render LIVE from each brand's
  collection in Liquid — 4 in-stock products each (fixes Willow's 2-product row),
  uncropped `image_url` images on warm tiles (fixes the horrible centre-cropped
  shots), serif brand headings, 20 featured brands. Static data blob deleted.
- **Product page**: dietary tag badges moved from below the trust tiles up to
  directly under the price (templates/product.json block order).
- **Marquee v3**: deep forest gradient band; coloured chips pop on dark; Vivid
  chip inverted white with green ring.
- **Trust strip v2**: warm cream gradient band, each promise in a white card with
  its own coloured icon chip (delivery amber, collect SA-green, WhatsApp green,
  brands indigo).
- **Why One Life v2**: serif lede; three cards with coloured top borders + icon
  chips (green / amber / indigo) and matching link colours.
- **Dispensary homepage promo v2**: botanical photographic background, serif
  heading, and emoji-led pastel protocol chips (🌙 Sleep, 🛡️ Immunity, 🌿 Gut,
  ⚡ Energy, 🧠 Focus, 🌸 Women, 💪 GLP-1 …) — each in its own accent colour.
