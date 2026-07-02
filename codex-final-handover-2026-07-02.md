# Codex FINAL Handover — 2026-07-02

Single source of truth for everything outstanding. Supersedes
`codex-round2-handoff-2026-07-02.md`. Everything not listed here is DONE and
verified (see Ledger at the bottom).

---

## A. Publish the patched theme (5 min) 🔴 do first

Theme **"LIVE + MOBILE FIXES 2026-07-02 (publish me)"** is ready in
Online Store → Themes (exact mirror of live + `assets/onelife-mobile-fixes.css`).

1. Preview on a phone: home, one collection, one PDP.
2. Confirm: (a) rotating announcement bar no longer shifts layout,
   (b) card badges not clipped under Add-to-cart, (c) WhatsApp button sits
   above the bottom nav, (d) "Buy it now" is outline style, (e) no orphaned
   "No reviews" near prices, (f) prices show " incl. VAT".
3. **Publish.** If anything looks broken, do NOT publish — report back instead.

## B. Merge PR #25 (2 min)

github.com/clawdbot12345-ux/onelife-dashboard/pull/25 — the round-2 record:
audits, price-rounding snapshot (rollback file), theme/flow tooling, specs.
Doc+script only; no behaviour changes on merge.

## C. Search & Discovery app — "magnesium" relevance (30 min)

Kids' chew is result #1 of 418 for "magnesium".
- Boost best-sellers for generic supplement queries.
- Demote/exclude Kids products from generic terms (keep for "kids ..." queries).
- Add synonyms (mag → magnesium, etc.).
Verify: mobile search "magnesium" → adult glycinate/complex in top 3.

## D. Tracking stack cleanup (45 min — biggest mobile speed win)

1. gtag loads TWICE per Google tag: Analyzify AND the native Google & YouTube
   channel both inject `AW-11098746320` and `GT-5RF9VTL` (~443KB from GTM
   alone). Pick ONE owner per tag (recommend the native channel) and disable
   the duplicate injection in Analyzify.
2. Analyzify adds 5 synchronous render-blocking head scripts (an_analyzify,
   app_embed, an_klaviyo, an_tiktok, f-find-elem). Switch its embeds to
   async/defer if the app allows; otherwise raise with Analyzify support.
Verify: view-source shows each tag ID once; PageSpeed render-blocking count drops.

## E. Data hygiene (Shopify admin, 30 min)

1. Rename location "One Life Health Supermarket" → "One Life Health
   Centurion" (leaks into PDP pickup text).
2. Duplicate product: "CREDÉ NATURAL OILS - Almond Butter 400g" listed twice
   (~R93 and ~R133) — merge or relabel.
3. Price anomaly: "PROBIOTECH ... Bio-Liquid Dish 750ml" ~R979 vs 5L ~R215 —
   confirm/fix intended price.
4. URL redirect: `/pages/vivid` → `/collections/vivid-health` (currently 404).

## F. Google Ads (owner unlocks 2FA first) — round-1 leftover

1. Run the Mike Rhodes PMax script (mikerhodes.com.au/scripts/pmax); save the
   brand-share output to the repo.
2. Conversion actions: exactly ONE primary "Purchase" (two exist — set the
   duplicate to Secondary).
3. Add brand exclusions ("one life", "onelife", misspellings) to PMax.
4. Pause the "One Life Shopping" campaign (Maximise Clicks, 0.26% conv rate)
   per marketing-strategy-2026-07.md §4.

## G. Klaviyo tidy-up (15 min)

1. Align Replenishment flow email labels with live delays (names say
   21/50/80; delays are 21/35/65).
2. In ~2 weeks (once the new checkout ladder is proven): archive the DRAFT
   duplicates left as rollback — flows `SN89LS`, `SkRBCP` (Touch 2/3 old
   copies) and `WY4cae` (old 2d Consultant Check). Do NOT touch the live
   ones: `YcByas` (Touch 2/3) and `TR9tVa` (4h Consultant Check).

## H. Nice-to-have (only if time)

- Brands page (24,199px tall): add an A–Z jump index.
- Collection pages: collapse the "From the Apothecary" guide into an
  accordion so products appear on screen 2.
- Homepage collection-tile images: serve sized WebP via image_url width
  params (200–317KB JPGs today; ~1MB saving).

## Do NOT

- Don't strip vendor prefixes from product titles (owner decision, SEO risk).
- Don't start BNPL or change ad spend (parked by owner).
- Don't edit the live theme directly — always copy → patch → preview → publish.
- Don't touch the live Klaviyo flows listed in G.2.

## Ledger — already done & verified (no action)

- Strategy + audits: marketing-strategy-2026-07, site-audit-2026-07-01/-02,
  market research, flow audits — all in repo.
- Email machine on main: Mon publish → Tue email, Fri spotlight (auth fixed +
  storefront fallback), Monthly Digest (25th), failure alerting everywhere;
  master template across all senders; GLP-1 4-article series queued (starts
  next Monday); blog author schema + related-articles live for new posts.
- Klaviyo flows live + verified: welcome, browse (24h + 30-day cap), checkout
  ladder 4h → d1 → d2 SMS → d3 (guarded, smart sending), post-purchase
  cross-sell, PCOS (item-filtered), replenishment, winback + catch-up
  segments, sunset.
- Store data: 2,643 prices rounded down to clean rand (verified 100% on
  storefront sample; snapshot in reports/price-rounding/); RELEASESCE ×3 and
  Florish vendor fixed; shipping policy R400 live; checkout logo fixed;
  Meta + TikTok pixels firing; consent boxes default-unchecked; Judge.me live.

## Definition of done
- [ ] Theme published after mobile preview passes (a)–(f)
- [ ] PR #25 merged
- [ ] "magnesium" returns adult products top 3
- [ ] Each Google tag loads once; Analyzify embeds async/deferred
- [ ] Location renamed; almond-butter dupe + R979 price resolved; /pages/vivid redirects
- [ ] Google Ads: Rhodes output saved, one primary Purchase, brand exclusions on, Shopping campaign paused
- [ ] Replenishment labels aligned (+ calendar note to archive draft flows in 2 weeks)
