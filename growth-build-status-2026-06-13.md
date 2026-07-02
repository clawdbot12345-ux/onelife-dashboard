# Growth Build status — 2026-06-13

**Theme:** GROWTH BUILD 2026-06 — LAUNCH READY (ID 185971867958, **unpublished**).
**Live theme** (ID 185765396790) untouched.

---

## The three things you screamed about — already fixed in draft

The screenshots you sent (Wed 10 Jun) were taken **before** these three uploads landed. Pull a fresh preview to confirm.

### 1. Stack prices: R 17,582.40 → R 1,598.40
**`sections/dispensary-protocol.liquid` v5.** The v4 bug was Liquid filter chaining without precedence:

```liquid
# WRONG (v4)
assign discounted_total = stack_total | times: 100 | minus: stack_total | times: saving_pct | divided_by: 100
# Liquid evaluates left-to-right: ((1776×100)−1776)×10÷100 = 17,582.40

# RIGHT (v5)
assign pct_remaining = 100 | minus: saving_pct
assign discounted_total = stack_total | times: pct_remaining | divided_by: 100
assign you_save = stack_total | minus: discounted_total
# 1776 × 90 ÷ 100 = 1,598.40 · save 177.60 ✓
```

All 17 protocol pages render through this single section, so the fix covers every stack — Sleep Ritual, Stress Reset, Winter Immunity, GLP-1 Companion, all of them.

### 2. Payment options: only what the store actually accepts
**`snippets/cart-payment-trust.liquid` v2.** Removed Apple Pay, Shop Pay, Google Pay, Payflex, PayJustNow, Ozow. Now shows only:

```
VISA · MASTERCARD · INSTANT EFT · PAYFAST
"Secure checkout via Payfast · your card details never touch our server"
```

This matches what your Payfast integration actually settles: Visa, Mastercard, and Instant EFT (Ozow is technically inside Instant EFT). If you later wire up Payflex BNPL or Mobicred via Payfast, we'll add those chips back in.

### 3. Menu: 5 rows of 27 items → 6 top-level items with megamenu
**`sections/header-group.json`** now points the header at the **`main-nav-2026`** link list. Top level:

| Item | Megamenu columns |
|---|---|
| The Apothecary | By Category · By Health Goal · Most Shopped · Guides & Journal |
| The Dispensary | Consultant Protocols (with 6 featured + "view all 17") · Do It Yourself (Build Your Stack, Quiz, Subscribe) |
| Vivid Health | Shop Vivid Health · The Vivid Story |
| Brands | International (Solgar, NOW, Metagenics…) · South African (Vivid, Willow, PMR…) · A–Z directory |
| Learn | Buyer's Guides (GLP-1, Magnesium, Collagen…) · The Journal |
| Help | Talk To Us (WhatsApp, Consultants, Stores) · More (About, Practitioner, Rewards, Delivery) |

Old menu (`collections` handle, 27 flat items) is no longer rendered by the header.

---

## What's pending (in priority order)

### Brands page v5 — richer filters (~next push)
v4 has search + origin tabs + A–Z. Adding:
- **Category filter** (Supplements · Skin & Beauty · Sport · Food · Home & Garden) so "show me only beauty brands" works
- **In-stock filter** so dead brand pages with no live SKUs auto-hide
- Larger brand cards with category badges
- Featured brand rows: 6 per row on desktop (currently 4 — wasted whitespace)

### Visuals on new narrative pages
About-Heritage, Practitioner B2B, Health Consultants, Vivid Story, Subscribe & Save, Build Your Stack — currently icon + text. Each needs a hero image and 1–2 inline photographs to feel premium, not designed-by-a-developer. Asset library has consultation hero, store photography (Centurion/Glen Village/Edenvale), Vivid product shelf. Need merchant approval before commissioning new photo work.

### Color palette diversification
You're right — too much dark green (`#1b4332`). Plan:
- Keep dark green as the **brand** colour (header, primary CTA, dispensary)
- Introduce **warm gold** (`#daa55f`) for "premium" moments — practitioner page, Vivid story, GLP-1 protocol
- Introduce **muted sage** (`#a3c4a8`) for "calm" moments — sleep, stress, mood content
- Each Dispensary protocol already has a per-page hero tint (Sleep=indigo, Stress=violet, Winter=amber, etc.) via the `--ph-tint` vars in v5 — we should extend this pattern to the commercial landers and category collections so each section feels distinct.

### Grid density fixes
Commercial lander grids currently render 3-per-row at 1200px wide. Updating to `repeat(auto-fill, minmax(220px, 1fr))` so 4 fit when there's space, 3 when there isn't. Already done on brands; pending on commercial-collection landers and homepage tabs.

### Cart drawer surface
Native Shopify drawer with our trust strip retrofitted. To make it "best in class" we'd need:
- Replace native drawer with custom (4–6 hrs of work)
- Add "complete your stack" pairs-well slot
- Add discount code field with live recompute
- Stack savings progress bar ("R 230 away from R400 free delivery")

This is a bigger lift — flag if you want this in this sprint or after launch.

---

## Cumulative build (sprint to date)

- 17 Dispensary protocols (incl. GLP-1 Companion — the muscle/skin/energy stack nobody else has)
- 17 commercial collection landers with consultant verdicts + FAQ JSON-LD
- 7 narrative pages (About-Heritage, Practitioner B2B, Health Consultants, Vivid Story, Subscribe & Save, Build Your Stack, Dispensary hub)
- 125 articles total — 3 new cornerstones + 66 voice-fixed, all on Precious + WhatsApp CTA + SA context
- Klaviyo templates ready for flow activation
- Header v3 with main-nav-2026 megamenu
- Cart-payment-trust v2 (SA-only payment surface)
- Dispensary protocol section v5 (price math fixed, per-protocol hero tints)
- Brands page v4 (live featured brand grids, A–Z directory, SA/Intl filter)
