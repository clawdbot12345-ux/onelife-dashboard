# Vivid Health — World-Class Roadmap

> The synthesis. How we go from "promising D2C draft" to **leading SA online health brand at R300k/month**.
> Authoring date: 2026-06-09. Working draft theme: `149043052630` (live theme `148873674838` untouched).

---

## 1. The thesis

**The South African online supplement category is structurally weak on six things every serious international DTC nails:**

1. Subscription / auto-replenish at scale
2. Quiz-to-stack personalisation
3. Exact-dose transparency (mg-per-Rand)
4. TikTok as an organic channel
5. Batch-level COAs
6. Bundle UX

Vivid is one brand sprint away from matching all six. The international benchmarks (Seed, Ritual, AG1, HUM, Wellbeing) have done the hard product work — we just copy the patterns that recur in 3+ of them, then layer two of our own moats:

- **"Made Traceable"** — published per-ingredient supplier + country + standardisation (no SA brand does this)
- **Anonymous 1996 founder origin** — the real Onelife story, retold for Vivid, no named face — credibility without ego

Hit those, and Vivid is the brand the under-40 SA wellness buyer trusts over Solal and the brand they discover over Faithful to Nature.

---

## 2. Where we stand right now (post round 6)

### Shipped to the new working draft (`149043052630`)

**Trust & GEO infrastructure**
- PDP JSON-LD now `Product` + `DietarySupplement` (with `activeIngredient`, `recommendedIntake`, `manufacturer`, `mpn`, returns + shipping) + `aggregateRating` + `review[]` + a separate `FAQPage` script — broader AI Overview surface than any SA competitor.
- `/pages/our-sourcing` — the Ritual-style Made Traceable page. 17 ingredient rows (KSM-66 ex India, Albion/Balchem mag glycinate ex Germany, DSM Quali-C ex UK, Kaneka Q10 ex Japan, IFOS-grade omega ex Peru, Indena mullein ex Bulgaria, etc.) + ISO 17025 SA batch testing + the 4-stage testing card.
- `/pages/the-team` — anonymous SA family page with belief panel, credential pills (HPCSA-registered clinical adviser, registered pharmacist, ISO-aligned SA lab), AboutPage schema.

**Content backbone (E-E-A-T + AI Overviews)**
- 8 ingredient pillar pages — magnesium glycinate, ashwagandha, l-theanine, vitamin D3, omega-3, curcumin, quercetin, 5-HTP
- 4 condition hubs — sleep, stress, energy, immunity
- 6 comparison journal articles — magnesium glycinate vs citrate vs oxide / ashwagandha vs rhodiola / best magnesium SA / whey vs plant protein / D3 vs D3+K2 / buffered vit C vs standard
- Every page has SEO title + description metafields
- New "Learn" footer column links all 12 guides

**Catalog**
- 3 new persona/seasonal bundle SKUs: **Highveld Hay-fever Stack** (R689), **Perimenopause Essentials** (R829), **Comrades Recovery Stack** (R599) — all ACTIVE on Online Store, in /collections/bundles
- 11 SKUs tagged with primary ingredient so PDP↔journal cross-linking fires

**Conversion**
- PDP OOS UX rebuilt — back-in-stock email capture (Shopify contact form) + 3 in-stock alternatives. Closes the 35% dead-end on the catalog where the Onelife Omni sync flags OOS.
- PDP "Related reading from the journal" — exact ingredient-tag match, surfaces the comparison articles inside the purchase decision.
- `/pages/vivid-members` — subscription positioning page. Reframes the 10%-off selling plans as a Vivid Members benefit, with 4 perks (10% off / skip-swap-cancel / free shipping at R300 / early access to drops).

**Mobile**
- Sweep across 27 routes — 0 overflow. Comparison tables now `display:block; overflow-x:auto` in both page and article contexts.

### Untouched but in plan
- Quiz "Building your stack..." loading + richer result panel (current quiz works but is one step shy of Care/of-quality UX)
- Klaviyo flows (Welcome 5 / Abandoned cart 3 / Post-purchase 5 / Winback 2) — wire once Klaviyo PRIVATE_API_KEY is verified
- Seed-style PDP hero rebuild (capsule cutaway photography)
- Real review collection to replace the 15 labelled samples
- Bespoke photography across the new bundles and pillar pages
- Practitioner portal (Pure Encapsulations-style B2B2C entry for dietitians and GPs)

---

## 3. What recurs across the international top brands

| Pattern | AG1 | Ritual | Seed | Thorne | MaryRuth | Olly | HUM | Wellbeing | Persona | Bulletproof |
|---|---|---|---|---|---|---|---|---|---|---|
| Subscribe-first pricing | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Free-shipping threshold | ✓ | ✓ | – | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Bundle ladder (2/4/6) | – | ✓ | ✓ | – | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Quiz primary acquisition | – | – | ✓ | ✓ | – | – | ✓ | – | ✓ | – |
| Multi-axis IA | – | ✓ | – | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ |
| PDP trust badge stack | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ |
| Reviews 1000+ above-fold | – | ✓ | ✓ | – | ✓ | – | ✓ | – | ✓ | ✓ |
| 30–90 day money-back | ✓ | ✓ | ✓ | – | ✓ | – | – | – | ✓ | ✓ |
| No-model hero photography | ✓ | ✓ | ✓ | ✓ | – | – | ✓ | – | – | – |
| Founder/expert visible | ✓ | ✓ | ✓ | – | ✓ | – | ✓ | ✓ | ✓ | ✓ |
| Welcome kit first order | ✓ | – | ✓ | – | – | – | – | – | – | – |
| Editorial blog | ✓ | ✓ | ✓ | ✓ | ✓ | – | ✓ | – | ✓ | ✓ |

**Vivid status vs each row:** subscribe-first ✓, threshold ✓ (R400→R300 for members), bundles ✓ (3 new + the 3 originals), quiz ✓, multi-axis IA ⚠ (goal-only — add format & life-stage), PDP badge stack ✓, reviews ⚠ (sample-flagged), 30-day money-back ✓, no-model hero ✓, expert visible ✓, welcome kit ✗ (post-launch), editorial blog ✓ (12 articles now).

---

## 4. The 6 differentiators Vivid is uniquely positioned to own

| # | Differentiator | Status | Next action |
|---|---|---|---|
| 1 | Made Traceable supplier table | ✓ Shipped (`/pages/our-sourcing`) | Add scanned COA PDFs per ingredient batch; tag "Last batch: 2026-Q2" |
| 2 | Single-SKU clarity at premium price | ✗ | Evaluate "Vivid Daily" — one all-in-one canister at R899/mo, AG1 positioning |
| 3 | Format ownership | ✗ | Evaluate dissolvable strips ("Vivid Lift") or 7-day blister packs as SA category |
| 4 | Free human expert post-purchase | ⚠ Free consultation page exists | Wire Klaviyo flow with named pharmacist responding within 24h |
| 5 | Refillable jar + travel vial | ✗ | 2026-Q4 — physical product change, supplier work |
| 6 | Forked practitioner / consumer entry | ✗ | Build `/pages/practitioners` with code request form |

---

## 5. SA market positioning

| Tier | Price band (Vit C 1000mg / 60ct) | Players | Vivid play |
|---|---|---|---|
| Cheap | R80–R150 | Clicks house, Bettaway, Cipla | Don't compete |
| Mid (our flagship) | R150–R280 | Biogen, Vital, NutriZen, The Real Thing | Match price, beat on UX/design/evidence/subscription |
| Premium (Vivid Pro lane) | R280–R450 | Solal, Coyne, Solgar, Terranova | Compete on novel actives — chelates, methyl-B12, mag L-threonate, NMN |
| Ultra-premium | R450+ | Solal complexes, grey-import Thorne | Optional 2027 lane via practitioner portal |

**Sweet spot for the AOV strategy:** stack bundles at R599–R799 (we shipped 3) with 15% subscribe-and-save → AOV R650+ and LTV through auto-ship.

---

## 6. SEO + GEO prioritised actions (top 10)

| # | Action | Status | Owner |
|---|---|---|---|
| 1 | DietarySupplement + Product + Offer + AggregateRating schema across all PDPs | ✓ Shipped | – |
| 2 | 8 ingredient pillar pages, 1,500w+, FAQ schema | ✓ Shipped | – |
| 3 | Credentialed founder/clinical reviewer page (E-E-A-T) | ✓ Shipped (`/pages/the-team`) | – |
| 4 | Per-batch third-party COAs as linked PDFs on PDPs | ⏳ Owner — upload PDFs | Naadir |
| 5 | `/pages/llms-txt` + `/llms-full.txt` for GEO | ✓ llms-txt exists; full pending | – |
| 6 | 4 condition hub pages (Sleep, Stress, Energy, Immunity) | ✓ Shipped | – |
| 7 | 6 comparison posts (AI Overview magnets) | ✓ Shipped | – |
| 8 | Digital PR to 10 SA pubs | ✗ | Owner / PR retainer |
| 9 | GBP optimization for 3 Onelife sister stores | ✗ | Owner |
| 10 | Klaviyo review-collection flow @ day 14 | ⏳ Depends on Klaviyo key activation | Naadir |

---

## 7. Marketing & social — run to R300k MRR

### Budget (Month-3+ at proven ROAS 3x = R100k ad spend / R300k revenue)

| Channel | Monthly | % |
|---|---|---|
| Meta (FB+IG) | R60,000 | 60% |
| Google (Search + Shopping + PMax) | R22,000 | 22% |
| TikTok | R10,000 | 10% |
| YouTube pre-roll | R5,000 | 5% |
| Reserve / influencer | R3,000 | 3% |

### Organic targets (6 months)

| Platform | Cadence | 6-mo target |
|---|---|---|
| Instagram | 4 reels + 3 carousels + 2 stories / day | 0 → 12k |
| TikTok | 1–2 / day | 0 → 18k |
| YouTube Shorts | 5 / week | 4k subs |
| Pinterest | 10 pins / day (Tailwind) | 50k MV |
| LinkedIn (founder) | 4 / week | 5k |

### Influencer tiers

- **Nano (1–10k)**: gifted full stack + 15% affiliate → 30/month
- **Micro (10–100k)**: gifted + R3–12k flat + affiliate → 4/month
- **Macro (100k+)**: paid R25–150k → 1/quarter

(SA shortlist of 20 in `research/marketing-playbook.md`)

### Promo calendar (SA-specific)

| Month | Moment | Vivid angle |
|---|---|---|
| Jan | New Year Reset | Cleanse + energy stacks |
| Feb | Back to work | Focus + immunity |
| Mar | Autumn Immunity | Vit D, zinc, elderberry |
| Apr | Comrades training | ★ Comrades Recovery Stack push |
| May | Mother's Day | Gift bundles |
| Jun | Winter Wellness | Immune restock |
| Jul | Mandela Day | 67-min give-back |
| Aug | Women's Month | ★ Perimenopause Essentials push |
| Sep | Heritage + Hay Fever | ★ Highveld Hayfever Stack push |
| Oct | Spring Reset | Detox + skin |
| Nov | **Black Friday week** | 25% sitewide — biggest day of year |
| Dec | Festive recovery | Liver + gut + electrolytes |

---

## 8. 12-week launch sprint

| Week | Organic | Paid | Content | Email/CRM | PR/Influencer |
|---|---|---|---|---|---|
| 1 | Set up IG/TikTok/Threads/Pinterest accounts | Pixel + GA4 + Conv API | 4 blog drafts | Klaviyo flows live | 20 nano gifting boxes |
| 2 | Daily TikTok start | Meta R400/d broad + RT | 4 more blogs | WhatsApp opt-in | 10 micro outreach |
| 3 | First IG collab | Google brand + Shopping | Pillar article (more) | Welcome flow refined | 5 nano live |
| 4 | First trend-jack | Scale winners R700/d | 4 blogs | Cart A/B subject line | 1 micro paid |
| 5 | YouTube long-form #1 | Add PMax | Hayfever hub live | Quiz broadcast | Founder podcast pitch x10 |
| 6 | 100 posts retro | Meta R1,000/d | 4 blogs | Subscription email push | 1 macro outreach |
| 7 | Pinterest scale | TikTok ads start R200/d | BF landing draft | VIP segment cleanup | SA press release |
| 8 | LinkedIn cadence | LAL audiences | 4 blogs | Winback flow live | 2nd micro live |
| 9 | UGC compilation reel | Retargeting 7/14/30 | Pillar #2 | Loyalty launch | Podcast #1 records |
| 10 | UGC trend | Meta R1,500/d | 4 blogs | Referral launch | Macro signed |
| 11 | BF teaser content | BF creative review | BF guide live | BF segment built | Macro posts |
| 12 | BF go-live | +50% BF week | BF email sequence (5) | – | PR push BF |

**Weeks 13–24:** double down on winning creative, scale Meta to R2,000–2,500/d, YouTube pre-roll on, corporate-wellness B2B via LinkedIn, push subscriptions to 25% of revenue. **R300k MRR target = month 6.**

---

## 9. The revenue model behind R300k/month

**Assumptions** (see `research/marketing-playbook.md`):
- AOV: R650 (bundles + 2 SKUs)
- Conversion rate: 2.2% blended; quiz-led 3.8%
- Subscription % of revenue: 25% by month 6
- Repeat rate: 38% by month 6
- Blended ROAS: 3.2x

**Path to R300k/month:**
- 462 orders/month × R650 AOV = R300k
- 462 orders @ 2.2% conv = ~21,000 sessions/month
- Channel mix: Meta 60% / Google 22% / TikTok 10% / SEO+organic+email 8% → growing to 25–30% by month 6
- Implied ad spend: ~R100k/month at 3.2x blended ROAS = R320k revenue

---

## 10. Owner items still gated (not theme-fixable)

- Replace the 15 labelled-sample reviews with real verified reviews
- Bespoke photography for the 3 new bundles + the pillar pages + the founder family
- Payfast verification, theme publish, DNS cutover
- GMB profiles for the 3 Onelife sister stores
- Klaviyo PRIVATE_API_KEY confirmed and the Klaviyo flow scripts run
- COA PDFs uploaded as linked-files-on-PDPs (Shopify Files API)
- Practitioner portal copy + the wholesale price sheet
- Hellopeter listing claimed (start collecting; target ≥7.5 within 60 days)
- WhatsApp Business API verified (POPIA-compliant opt-in already on the quiz)
- Resolve the Onelife Omni sync so the persistent 35% OOS reduces

---

## 11. Theme operations

All work to date is on the new working draft **Vivid — Best in Class (working draft 2026-06-06)** ID `149043052630`. The MAIN live theme `148873674838` is untouched. The previous round of work `148889796694` is kept as a rollback snapshot.

- **Preview**: `https://hgywg0-w7.myshopify.com?preview_theme_id=149043052630`
- **Publish**: Shopify admin → Online Store → Themes → Actions → Publish on the "Vivid — Best in Class" theme. Recommend doing this only after the owner items above are cleared.

---

## 12. Companion documents

- `research/international-brand-audit.md` — AG1, Ritual, Seed, Thorne, MaryRuth, Olly, HUM, Wellbeing, Goop, Persona, Bulletproof + 12 pattern table-stakes + 6 differentiators
- `research/sa-competitive-audit.md` — FtN, WW, Dis-Chem, Clicks, Solal, Coyne, Real Thing, NutriZen, Lifematrix, Earthshine, Onelife — with SA price points + market gaps map
- `research/seo-geo-playbook.md` — SA keyword landscape, content architecture, schema, llms.txt, GEO tactics, top-15 prioritised actions
- `research/marketing-playbook.md` — Personas, paid budgets, organic cadences, influencer shortlist (20 SA names), 12-week sprint, KPIs

---

## 13. One-page summary

> Vivid is a sprint away from being the modern SA digital health brand. The infrastructure is built (sourcing transparency, SEO content backbone, schema, bundles, subscription positioning, OOS UX). The remaining items are owner-side (PR, photography, reviews, social cadence, ad spend, Klaviyo key activation). At a R100k/month ad budget with the playbook in `research/marketing-playbook.md`, the revenue model lands R300k MRR by month 6. The differentiation that no SA brand can quickly copy — Made Traceable, anonymous family origin, exact-mg labelling, batch COAs, ingredient pillar SEO — is the moat.
