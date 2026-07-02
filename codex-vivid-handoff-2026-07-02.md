# Codex Handoff — Vivid Health Store (hgywg0-w7.myshopify.com) · v3, 2026-07-02 (evening)

**Supersedes v2.** Read this file + the ROUND-2 section of `codex-vivid-design-direction.md`.
Working branch: `claude/vivid-health-audit-redesign-9fmzon` (PR #26 already merged; new work lands via this branch again).

## Standing rules (unchanged, non-negotiable)

1. **Never touch onelifehealth.myshopify.com.** All Vivid work targets **hgywg0-w7** via `VIVID_CLIENT_ID`/`VIVID_CLIENT_SECRET`. (The one exception — the owner-approved One Life price round-down — is DONE: 2,203/2,203 applied, log in `reports/price-rounding/apply-result.json`. Nothing further there.)
2. **No text baked into imagery, ever.** No headlines, bullets, prices, buttons, wordmarks or slogans rendered inside artwork. Physical bottle labels in photos are fine. This is the owner's hard gate and the reason the last QA returned NO-GO.
3. Claude owns all theme/code; you own imagery + admin UI. Don't edit Liquid/JS — request via PR comment instead.

## State as of this handover (all verified live)

- Final design QA scored the store **8.5–9/10 on most pages**; overall NO-GO **only** because of the imagery items below.
- Claude's entire code punch list is done and verified: branded search, compare table mobile scroll, sourcing supplier grid, sold-out dimming, announcement bar, sentence-safe copy, cart thumbnails, FAB behaviour (labelled automated, scroll-aware), About h1 + heritage, hero images moved to og:image position, baked-text assets stripped from all 20 PDP gallery templates.
- **Subscribe & Save now works end-to-end** (verified: cart line carries "Every month — save 10%" at the subscription price) — but see admin item 4 (billing app).
- Blog engine live: first article published, weekly publisher + monthly writer armed.
- Performance: collection ~6MB (was 15), TTFB 0.56–0.67s everywhere.

## 🔴 CRITICAL PATH — Round-2 imagery (blocks the owner's walkthrough)

Full detail in `codex-vivid-design-direction.md` → "ROUND-2 IMAGERY FIXES". Summary:

| # | Task |
|---|---|
| A | **Delete every `*-infographic.jpg`** (~52) plus `wellness-kitchen.jpg`, `clutter-to-calm.jpg`, `bone-supreme-them-vs-us.jpg`, `scattered-to-sorted.jpg`, `griffonia-before-after.jpg` — marketing cards with baked text (incl. hallucinated "SHOPIFY-MATCHED FORMAT" and fake SHOP NOW buttons). Claude already unlinked them from templates; the files must go and never be regenerated. Also remove the "VIVID HEALTH" wordmark rendered into the stack lineup art |
| B | **Attach real product media to the 3 stacks** — `comrades-recovery-stack`, `highveld-hayfever-stack`, perimenopause stack currently have `images: []` (carts/OG/feeds render nothing). Compositions must match each stack's ACTUAL contents (current theme art shows Bone Supreme bottles on Comrades and four unbranded canisters for a 3-bottle stack) |
| C | **Label art**: the new Agnus Castus hero still reads "ANGUS CASTUS"; "DIETARY SUPPLEMENT" survives on new artwork (About hero, MSM cards). Fix per §3.4 of the direction doc. Also "60 capules" typo on the old master |
| D | **Label-panel macro shot per SKU** (§3.1 shot 2) — still missing everywhere; the single highest-priority shot in the direction doc |
| E | Hygiene: replace the Cayenne 250g variant photo (filename `WhatsAppImage2026-02-23…jpg`); the old cold IMG-5xxx masters are demoted from position 1 — delete or re-shoot at your discretion |

**Delivery:** upload as product media / replace Files in the Shopify admin (never append text-bearing cards), or commit to `vivid/assets/store/` on the branch for Claude to push. Comment progress on the branch/PR.

**Gate:** when A–E are done, Claude re-runs the full two-viewport design QA. GO requires zero text-bearing artwork and all three stacks carrying real media. Then the owner walks the site.

## Admin items still open (do alongside imagery)

| # | Task | Status |
|---|---|---|
| 1 🔴 | **Subscriptions billing app** — selling plans now sell correctly but nothing bills recurring orders (plans were created via API, `app_id: null`). Install Shopify Subscriptions (free) or equivalent, then place ONE test subscription checkout end-to-end | Blocks launch |
| 2 🔴 | **Reviews app** — PDP reviews are hardcoded "SAMPLE (4.5 · 2 reviews)". Install Judge.me, enable post-purchase requests, remove/replace the sample block (ask Claude for the theme edit once installed) | Blocks launch |
| 3 🔴 | **Inventory**: 16/58 products sold out incl. Buffered C · 300 (homepage hero product). Restock or hide | Blocks launch |
| 4 | **Payments**: confirm PayFast/EFT live; add Payflex/PayJustNow + Ozow. Claude then adds PDP installment messaging | High |
| 5 | **Klaviyo**: connect + add `VIVID_KLAVIYO_API_KEY` repo secret (WELCOME 10% popup currently feeds nothing) | High |
| 6 | **Pixels**: GA4 + Meta + TikTok channels before launch | High |
| 7 | **Vivid price rounding** (58 products, odd cents like R189.76): confirm no POS/ERP owns these prices, get owner sign-off, then Claude applies. Vivid store ONLY | Medium |
| 8 | **Domain**: vividhealth.co.za is an unrelated practitioner's (brand-risk). Choose/buy + connect | Blocks launch |
| 9 | **Shipping**: confirm rates match the R400 free-shipping promise + R100 estimate shown in cart | Medium |
| 10 | **COAs from the manufacturer** — one PDF unlocks Claude's batch-lookup build (PDPs already promise batch testing) | Medium |

## Done — do not redo

PR #26 merge · blog engine enablement + first article · One Life price round-down (2,203/2,203) ·
One Life rollback (store restored, off-limits) · all theme/code QA fixes · hero/og:image reordering ·
catalog typo + duplicate-title fixes · Subscribe & Save frontend.
