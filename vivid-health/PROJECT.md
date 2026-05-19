# Vivid Health — Digital Overhaul Project Log

> Living document. Update at every phase boundary, every decision, every open question.

## Phase status

| Phase | Status | Output |
|---|---|---|
| 0 — Recon & audit | **AWAITING GATE 1** | `recon/` |
| 1 — Architecture & store provisioning spec | PENDING | `setup/` |
| 2 — Brand & design system | PENDING | `design/` |
| 3 — Theme build (Dawn) | PENDING | `theme/` |
| 4 — Content & SEO engine | PENDING | `content/` |
| 5 — Migration, QA, launch | PENDING | — |

**Human gates:** **GATE 1 (catalogue/redirects sign-off) → REACHED — awaiting owner.** GATE 2 (design sign-off) → not reached. GATE 3 (DNS cutover) → not reached.

### Where to start (for the owner reviewing this branch)

1. Read `recon/curated-launch-proposal.md` — the synthesized recommendation. Answer the 5 questions in §1 and §3.
2. Open `recon/catalogue-audit.csv` in a spreadsheet — eyeball the `decision` column, override any rows you disagree with.
3. Skim `recon/crawl-report.md` — the live site is currently 503; restore origin so Phase 0a can re-run and feed Phase 5 redirects.
4. Reply on the PR (or message Claude) with answers to the **open questions** listed below.

## Locked decisions (do not relitigate)

1. Standalone Shopify store on `vividhealthsa.co.za` — not a One Life collection.
2. One Life remains a wholesale reseller. No channel conflict.
3. v1 = Liquid theme on Dawn. Headless migration path documented for later.
4. Curated launch (`CATALOGUE_SCOPE = CURATED_PREMIUM`), default unless owner overrides.
5. South Africa context mandatory: ZAR, VAT-inclusive, POPIA, SA payment gateway (Shopify Payments NOT available in SA), SAHPRA claim compliance.
6. Live brand domain = `vividhealthsa.co.za`. `vividhealth.co.za` is an unrelated third-party herbal practice — DO NOT reference or scrape.

## Working parameters

- `CATALOGUE_SCOPE` = `CURATED_PREMIUM` (default; surface curation list at GATE 1).
- Hero range (5): Ashwagandha, Lion's Mane, Magnesium Glycinate, Vitamin C + Zinc, Omega-3.
- Brand tiers: **Premium** (amber glass) / **Daily** (bone HDPE).

## Source store for catalogue audit

Shopify store handle `onelifehealth` (`onelife.co.za`), ZAR, SAST. Filter: `vendor:"VIVID HEALTH"`. Read-only access in Phases 0–2.

## Phase 0 — Recon log

### 0a. Old-site crawl — COMPLETE (with caveat)

- Target: `https://vividhealthsa.co.za`
- Tooling: Playwright + Chromium, headless, BFS depth 4, cap 300 pages, 1s delay, 3 retries (2/4/8s backoff). Hard URL-filter block on `vividhealth.co.za` to prevent brand cross-contamination.
- Crawler: `recon/crawl_old_site.js` — **idempotent, just re-run when origin is back.**

**Result: site is fully down.** Every URL returned HTTP 503 with Envoy upstream-connect-error signature — the edge LB is healthy but the origin backend is offline (stopped container / scaled-to-zero). Confirmed across 4 seed endpoints (`/`, `robots.txt`, `sitemap.xml`, `wp-sitemap.xml`) plus crawler retries. Median edge latency 1375 ms (Playwright `networkidle` against static 503).

Outputs (skeleton state — origin needed to populate):
- `recon/crawl_old_site.js` — crawler (idempotent re-run)
- `recon/crawl-report.md` — full report, outage forensics, platform-guess, SEO/compliance flags
- `recon/old-site-inventory.csv` — header + 1 row (homepage 503)
- `recon/redirect-map.csv` — header + 1 skeleton row
- `recon/keeper-content.md` — explicitly empty + reason
- `recon/screenshots/` — empty (cannot screenshot a 503)

**Action required from owner before Phase 1:** restore the origin (likely a stopped container at the hosting provider — Envoy fingerprint suggests GCP LB / Istio / Fly.io). Once back, re-run `node recon/crawl_old_site.js` to populate the real inventory + redirect map.

### 0b. Catalogue audit — COMPLETE
- Source: Shopify Admin GraphQL via MCP (`vendor:"VIVID HEALTH"`), full pagination (77 nodes across 2 pages).
- Outputs:
  - `recon/catalogue-raw-page{1,2}.json` — raw GraphQL responses.
  - `recon/catalogue-audit.csv` — 77 rows, decision + rationale per SKU.
  - `recon/curated-launch-range.csv` — 27 in-stock KEEP/KEEP_HERO rows.
  - `recon/catalogue-summary.md` — exec summary.
  - `recon/curated-launch-proposal.md` — proposal with canonical-size picks, RETIRE list, hero-range gap analysis. **Read this before GATE 1.**
  - `recon/triage_catalogue.py` — reproducible triage script.

### Phase 0 — KEY FINDINGS

1. **Hero-range gap (LAUNCH BLOCKER).** Brief specifies 5 anchor SKUs (Ashwagandha, Lion's Mane, Magnesium Glycinate, Vit C + Zinc, Omega-3). **Only Omega-3 exists in the current catalogue.** The other 4 must be sourced/manufactured before the curated launch can ship its named anchor range. This is the single most important question for the owner at GATE 1.
2. **Triage breakdown:** 2 KEEP_HERO (Omega Oils) · 35 KEEP · 16 MERGE · 2 REVIEW (DRAFT) · 22 RETIRE.
3. **Stock health is fragile:** 17/53 active SKUs are at zero inventory — including all 3 bundles. Operations/manufacturing issue, not digital.
4. **Sub-brand taxonomy inconsistent:** typo (`NUTRITENT` vs `NUTRIENT`), duplicated groupings (`MEN` vs `MEN'S HEALTH`). New Premium/Daily binary collapses all of this — do NOT migrate the old sub-brand grouping.
5. **Commodity items are off-brand:** Epsom salt, Himalayan salt, sodium bicarbonate, xylitol, dextrose. Retire from Vivid storefront; keep on One Life if margin justifies.
6. **COGS data is missing** — Shopify Admin API does not expose vendor COGS from the One Life side. Owner must supply COGS at GATE 1 for margin-floor checks.

## Open questions for owner (carry to HUMAN GATE 1)

1. **Hero-range gap (URGENT).** Are Ashwagandha, Lion's Mane, Magnesium Glycinate, Vit C + Zinc in production, in formulation, or to-be-sourced? This gates launch timing — see `recon/curated-launch-proposal.md` §1 for the two-path recommendation.
2. **CATALOGUE_SCOPE confirmation.** Default = `CURATED_PREMIUM`. Override?
3. **Canonical sizes for MERGE families** (Buffered C, MSM, Cayenne, Bone Supreme, Barley Grass, Colon Flush, Omega Oil). Recommendations in `curated-launch-proposal.md` §3.
4. **Commodities (Epsom/Himalayan/bicarb/xylitol/dextrose):** confirm RETIRE from Vivid storefront.
5. **DRAFT items** (Cranberry 60 Caps; Xylitol 2.5kg): abandoned or in-progress?
6. **COGS data for launch SKUs** — required for margin-floor checks before pricing.
7. **Free-shipping thresholds:** confirm R900 Gauteng / R1400 national, or specify.
8. **SA payment gateway** preference (recommendation will be made with reasoning in Phase 1).
9. **Inventory master:** confirm Omni Accounts (Firebird, Centurion) as single source of truth.
10. **Legacy SAHPRA registration numbers** tied to specific SKUs that must persist on PDPs?

## Assumptions (flag if wrong)

- Brand name in Shopify vendor field is literally `VIVID HEALTH` (uppercase). Will widen the search if first query returns zero.
- Old site sometimes down — crawl uses retry-with-backoff; intermittent failure is itself a finding to log.
- No live PDP imagery exists in the new packaging system yet — Phase 3 PDPs will use whatever real assets the owner can supply; placeholders are not permitted on live.
