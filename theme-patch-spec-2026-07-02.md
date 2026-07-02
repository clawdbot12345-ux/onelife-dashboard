# Theme Patch Spec — Mobile Conversion Fixes (2026-07-02)

From `site-audit-2026-07-02.md`. Target: a copy of the live theme
("ONE LIFE HEALTH STORE — LIVE 2026-07-02", 185669910838) — never edit live
directly; publish the patched copy when done. Note: scratch theme
186060964150 may contain a partial sync from a stopped run — verify or resync
before reuse.

All changes land in one new stylesheet `assets/onelife-mobile-fixes.css`
(included in layout/theme.liquid before </head>) unless marked Liquid.

1. CLS 0.34 on collections: fix the rotating announcement/utility bar —
   give the rotator a fixed min-height so text swaps never shift layout.
2. Collection cards: badge row clips under the Add-to-cart button (see
   Florish card) — add bottom padding/space in the card content; equalize
   card min-heights so prices/buttons align across the grid.
3. WhatsApp floating button: on mobile it covers product titles, badges and
   the footer copyright — raise it above the bottom app-nav, keep z-index
   below modals/drawers. Do not hide it.
4. PDP: "Buy it now" → outline/secondary style (currently identical to
   Add to cart; no visual hierarchy).
5. Judge.me zero-state: hide the orphaned "No reviews" preview badge near
   the price when data-number-of-reviews="0"; keep the bottom write-review
   widget.
6. Sticky header overlaps the "Filter and sort / N products" row on
   collections at scroll — z-index/top offset fix.
7. VAT label (Liquid preferred): append small muted " incl. VAT" to the
   final displayed price in snippets/price.liquid (PDP + cards + cart).
   CSS :after fallback acceptable.
8. Homepage collection tiles: 200–317KB JPGs — cap via image_url width
   params/srcset in the collection-list section (~1MB saved on home).

Owner-side afterwards: publish the patched theme; separately (not theme):
Search & Discovery boosts for "magnesium"-class queries, dedupe the double
gtag injection (Analyzify vs native Google channel), make Analyzify's 5 sync
head scripts async, rename location "One Life Health Supermarket".
