# Onelife — Theme Fix Brief (Add-to-Cart Alignment + Theme Check Debt)

**Date:** 2026-06-13
**Store:** onelife.co.za · **Live theme:** 186035765558
**Why this is a separate doc:** the `onelife-dashboard` repo holds content,
data and automation scripts — it does **not** contain the Shopify theme
(`*.liquid`) source. Findings #3 and #4 from the Codex SEO/site audit live in
the theme and must be applied there (Shopify CLI `shopify theme pull` against
186035765558, or the theme code editor). This brief specifies the exact fix
for each so it can be applied and browser-verified in one pass.

---

## FINDING #4 (visible bug) — "Add to cart" alignment is inconsistent

### What's happening
On the **Frequently Added** strip (and any product-card grid), the green
**Add to cart** button sits at a different vertical position from card to card.
Root cause is variable card content height, primarily the **dietary tag pills**
row: a product tagged `Vegan · Gluten Free · Sugar Free · Dairy Free ·
Vegetarian` wraps the pills onto two lines, while a 3-tag product stays on one
line. Because the button follows content in normal flow, the taller card pushes
its button down and the row of buttons no longer lines up. (Screenshots
2026-06-13: Metagenics UltraFlora cards vs Viridian/Release_SCE cards.)

### The fix (CSS — pin the button to the bottom of an equal-height card)
The card needs to be a full-height flex column, the media/title/price/tags
block grows to fill, and the button is pushed to the bottom with
`margin-top:auto`. Add to the card's stylesheet (e.g. `assets/component-card.css`
or the product-card section `{% stylesheet %}`), scoping to the real class
names in the theme:

```css
/* Product card: equal height + bottom-pinned CTA */
.card-wrapper,
.product-card { height: 100%; }

.card,
.product-card__inner {
  display: flex;
  flex-direction: column;
  height: 100%;
}

/* the content block between image and button grows to fill */
.card__content,
.product-card__info { flex: 1 1 auto; }

/* tag pills: reserve room for up to two rows so 3-tag and 5-tag cards match */
.product-card__tags,
.card__badges {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  min-height: 3.25rem;        /* ≈ two pill rows; tune to the real pill height */
  align-content: flex-start;
}

/* the CTA is pushed to the bottom of every card, so the row aligns */
.card__cta,
.product-card__add,
.product-form__buttons { margin-top: auto; }
```

Also make the grid stretch its tracks so each card fills its row:

```css
.product-grid,
.grid--peek { align-items: stretch; }
.product-grid > li,
.grid__item { display: flex; }
```

### How to verify (required before sign-off)
1. Mobile + desktop user agents on the homepage **Frequently Added** strip and
   on a collection page (e.g. `/collections/gut-health`).
2. Confirm every **Add to cart** button in a row shares the same baseline,
   including cards with 3 tags vs 5 tags, long vs short titles, and
   `R xxx,xx` vs `R xx,xx` prices.
3. Check the cart-drawer "Frequently Added" upsell specifically — that's the
   strip in the audit screenshots.

> Use the real selector names from the theme (`shopify theme pull` then grep
> the product-card section/snippet). The classes above are the common
> Dawn-derived names; swap in whatever this theme actually uses.

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
