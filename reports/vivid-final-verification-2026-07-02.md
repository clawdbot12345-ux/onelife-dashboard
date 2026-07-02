# Vivid Health — Final Verification (2026-07-02, end of build day)

## Where the store stands

Independent final audit scored **8.7/10** (from 7/10 at the start of the day), with 10/11 fix
verifications passing. The one critical find — **Subscribe & Save silently adding items as
one-time purchases** — was root-caused (the buy column lacked the `.pdp-buybox` class both
selling-plan JS lookups were scoped to), fixed, and **proven end-to-end**: subscribe click →
ATC label "Subscribe — R 271.69 / delivery" → cart line carries selling plan *"Every month —
save 10%"* at R271.69. All audit round-2 code items also applied and live: bundle "0" badge
hidden, sentence-safe card excerpts, square-cropped cart thumbnails, centred page wrappers.

Page scores after the day's two polish rounds (previous → final audit):
home 8→9 · collection 7.5→9 · PDP 7→8 (now higher with the subscribe fix) · quiz 7→9.5 ·
sourcing 1→9 · search 2→9 · about 6→9 · cart 7→8.5 · OOS PDP 9.5 · compare 8.5 · blog 8.5.

Performance: TTFB 0.56–0.67s on all pages (target <1.2s ✓); no single image >400KB; page
weight flagged on collection (~15MB full-scroll) — resolved by the imagery migration below.

## One Life price round-down

**2,203 / 2,203 variants applied · 0 drifted · 0 failed** (drift-checked against the plan
snapshot; the plan's `old_price` column remains the rollback map).
Log: `reports/price-rounding/apply-result.json`.

## Remaining before launch (not code)

**Imagery (Codex — `codex-vivid-design-direction.md`):**
1. Migrate card/product imagery from static theme assets to product media so the CDN can
   serve responsive sizes — the single biggest performance lever (collection ~15MB → ~3MB est.)
2. Per-article blog thumbnails (10 of 12 share one turmeric image)
3. Label-panel macro shots per SKU; bundle product photography; label art fixes
   (ANGUS CASTUS / DIETARY SUPPLEMENT wording)

**Admin/apps (owner/Codex — `codex-vivid-handoff-2026-07-02.md` §3):**
1. ⚠️ **Subscriptions billing app** — selling plans now sell correctly, but confirm an app
   (e.g. Shopify Subscriptions) is installed to bill recurring orders; run one test checkout
2. **Reviews app** — PDP reviews are labelled SAMPLE; install Judge.me and seed real reviews
3. Payments confirmation (PayFast/EFT live; add Payflex/PayJustNow + Ozow)
4. Inventory: 16/58 products OOS; restock or hide before launch
5. Domain, pixels, Klaviyo (unchanged from the handoff)

## Autonomy running

Vivid Journal: first article live; publisher runs Wednesdays; monthly Claude writer drafts
4 articles as a review PR. Kill switch: `VIVID_BLOG_ENABLED`.
