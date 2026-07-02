# Codex Handoff — Round 2 (2026-07-02, mobile audit follow-up)

Already executed by Claude (do not redo): 2,643 catalogue prices rounded to
clean rand (verified live; rollback snapshot in `reports/price-rounding/`),
vendor artifacts fixed (RELEASESCE ×3, Florish → SEBASTIAN SIEBERT
SUPPLEMENTS), full audit committed as `site-audit-2026-07-02.md`.

## 1. Theme — publish (or build) the mobile-fixes copy
Claude's Actions job is building a patched copy of the live theme named
**"LIVE + MOBILE FIXES 2026-07-02 (publish me)"** (mirror of live + one new
stylesheet `assets/onelife-mobile-fixes.css`).
- If it EXISTS: preview on mobile — check (a) announcement bar rotation no
  longer shifts layout, (b) card badges not clipped under Add-to-cart,
  (c) WhatsApp button sits above the bottom nav, (d) "Buy it now" is outline
  style, (e) no orphaned "No reviews" near prices, (f) prices show
  " incl. VAT" — then **Publish**.
- If it does NOT exist or looks broken: execute `theme-patch-spec-2026-07-02.md`
  manually on a fresh copy of live. Never edit the live theme directly.

## 2. Search & Discovery app — fix "magnesium" (highest search-revenue fix)
A kids' chew is result #1 of 418 for "magnesium". Boost best-sellers for
generic supplement terms, demote/exclude Kids products from generic queries
(keep for "kids ..." queries), add synonyms (mag→magnesium etc.).
Verify: mobile search "magnesium" → adult glycinate/complex in top 3.

## 3. Tracking stack cleanup (biggest mobile speed win)
(a) gtag loads TWICE per Google tag — Analyzify AND the native Google
channel both inject `AW-11098746320` and `GT-5RF9VTL` (~443KB from GTM
alone). Pick one owner per tag (recommend native Google & YouTube channel)
and disable the duplicate injection in Analyzify.
(b) Analyzify adds 5 synchronous render-blocking scripts in <head>
(an_analyzify.js, app_embed.js, an_klaviyo.js, an_tiktok.js,
f-find-elem.js) — switch its embeds to async/defer if the app allows, or
raise with Analyzify support.
Verify: view-source shows each tag ID once; blocking scripts reduced.

## 4. Data hygiene (Shopify admin)
- Rename location "One Life Health Supermarket" → "One Life Health
  Centurion" (leaks into PDP pickup text).
- Duplicate product: "CREDÉ NATURAL OILS - Almond Butter 400g" exists twice
  (now ~R93 and ~R133) — merge or fix labelling.
- Price anomaly: "PROBIOTECH ... Bio-Liquid Dish 750ml" ~R979 vs 5L ~R215 —
  confirm intended price.
- 301 redirect `/pages/vivid` → `/collections/vivid-health` (currently 404,
  may have inbound links).

## 5. Still open from Round 1
- Google Ads 2FA unlock → run Mike Rhodes PMax script, keep exactly ONE
  primary Purchase conversion action, add brand exclusions to PMax; attach
  evidence to the repo.
- Klaviyo: align Replenishment flow email labels with live delays (names
  say 21/50/80; delays are 21/35/65).

## 6. Do NOT
- Don't strip vendor prefixes from the 237 product titles (owner decision,
  SEO-sensitive — parked).
- Don't start BNPL or change Google Ads spend (parked).
- Don't edit the live theme directly — always copy → patch → preview → publish.

## Definition of done
- [ ] Patched theme published; mobile spot-check passes (a)–(f)
- [ ] "magnesium" search returns adult products top 3
- [ ] Each Google tag loads once; Analyzify embeds async
- [ ] Location renamed; dupes/anomaly resolved; /pages/vivid redirects
- [ ] Google Ads evidence attached; replenishment labels aligned
