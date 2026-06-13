# Onelife — Theme Fix Brief (Add-to-Cart Alignment + Theme Check Debt)

**Date:** 2026-06-13
**Store:** onelife.co.za · **Live (MAIN) theme:** **186060112182** ("ONE LIFE
HEALTH STORE — AUDIT FIXES 2026-06-13"). Note: the old handoffs referenced
186035765558, but that is now unpublished — the current published theme is
186060112182.
**Why this is a separate doc:** the `onelife-dashboard` repo holds content,
data and automation scripts — it does **not** contain the Shopify theme
(`*.liquid`) source. Findings #3 and #4 live in the theme.

---

## FINDING #4 (visible bug) — "Add to cart" alignment ✅ FIXED LIVE

### Status
Root-caused, fixed, and **applied directly to the live theme 186060112182**
(verified live 2026-06-13 via the Admin API — `assets/onelife-grid-fixes.css`,
14490 bytes, cart-scoped block present). No publish/theme-swap needed — editing
the published theme's asset is effective immediately.

- An unpublished preview copy (`186060964150`) was also created during the work
  and is now redundant — safe to delete (left in place pending owner OK, per the
  no-theme-deletion rule).

### Confirmed root cause (not what the first pass assumed)
The "Frequently Added" block is the **cart page `upsell` section**
(`templates/cart.json` → `featured-collection`, `title: "Frequently Added"`,
`collection: top-health-supplements`, `swipe_on_mobile: true`). It renders
`snippets/card-product.liquid` cards. With `quick_add: "standard"`, the visible
button is the custom **`.ol-card-action`** block, which sits **inside
`.card__information`**. The existing alignment CSS in `onelife-grid-fixes.css`
sets `.card__information { flex: 0 0 auto }` and only pins `.quick-add`
(`margin-top:auto`) — **not** `.ol-card-action`. So when one card's title wraps
to 3 lines and another's to 2, the buttons land at different heights. (It was
*not* primarily the dietary-pill rows — those are already clamped to 44px.)

### The fix that shipped (scoped to the cart template only)
Appended to `assets/onelife-grid-fixes.css` on the preview theme — let
`.card__information` grow and pin the action button to the bottom:

```css
body.template-cart .product-card-wrapper .card__content { display: flex !important; flex-direction: column !important; }
body.template-cart .product-card-wrapper .card__information { display: flex !important; flex-direction: column !important; flex: 1 1 auto !important; }
body.template-cart .product-card-wrapper .ol-card-action,
body.template-cart .product-card-wrapper .quick-add { margin-top: auto !important; }
```

Scoped to `body.template-cart` so it can only affect the cart "Frequently Added"
upsell — zero impact on collection/PDP/home. The body carries
`template-{{ request.page_type | handle }}`, so `template-cart` is correct.

### Verify before publishing
1. Open the preview URL above on a **mobile** viewport with ≥3 items in cart.
2. Confirm every **Add to cart** button in the "Frequently Added" row shares the
   same baseline — including 2-line vs 3-line titles and 3-tag vs 5-tag cards.
3. Desktop `/cart` too. Then Publish 186060964150.

### One-line revert (if ever needed)
Delete the `body.template-cart …` block at the end of
`assets/onelife-grid-fixes.css` (everything after the
`/* ---- Cart "Frequently Added" upsell … */` comment), or just re-publish the
prior theme 186060112182.

---

## FINDING #3 — Theme Check lint debt (email-signup-banner + header parser)

Codex notes these are **pre-existing, unrelated** lint offenses (not caused by
recent work) and that **browser verification passed** — so this is hygiene, not
a live regression. Clear it so the next audit is green and real issues aren't
buried in noise.

### Process
```bash
shopify theme pull --theme 186035765558 --path ./onelife-theme
cd onelife-theme
shopify theme check                      # full offense list
shopify theme check sections/email-signup-banner.liquid
shopify theme check sections/header.liquid snippets/header*.liquid
```

### Typical offenses to expect & how to clear them
- **`UnusedAssign`** in `email-signup-banner.liquid` — remove the `{% assign %}`
  that is never output, or actually use it. Most common cause of banner lint.
- **`ParserBlockingScript` / `ParserBlockingJavaScript`** (the "header parser
  pattern") — add `defer` (or `async`) to the flagged `<script src=...>` in the
  header, or move it to `{{ 'file.js' | asset_url | script_tag }}` which Shopify
  defers. Do **not** remove the script; just stop it blocking the parser.
- **`MissingTemplate`** — a `render`/`section` pointing at a snippet that no
  longer exists; fix the path or delete the dead reference.
- **`ImgLazyLoading`** — add `loading="lazy"` to non-hero `<img>` in the banner.
- **`DeprecatedFilter` (`img_url`)** — migrate `| img_url:` to `| image_url:`
  with an explicit `width:`.
- **`UnclosedHTMLElement` / `ParserBlockingScript`** in header — close the tag
  Theme Check points at; these are line-specific.

### Guardrails
- **No theme deletions** without owner approval (20-theme Shopify limit; the
  standing rule in the close-out handoff).
- Work on a **duplicate/dev copy** or an unpublished theme, run Theme Check to
  green, browser-verify header + banner render, **then** publish.
- Keep the fix to lint only — do not restyle the header or banner in the same
  pass.

### Definition of done
- [ ] `shopify theme check` reports 0 offenses in `email-signup-banner.liquid`
- [ ] Header parser-blocking-script offense cleared (script now deferred)
- [ ] Header + email-signup banner render correctly on mobile + desktop
- [ ] Add-to-cart buttons aligned across all product-card rows (Finding #4)
- [ ] Changes published to 186035765558 and spot-checked live
