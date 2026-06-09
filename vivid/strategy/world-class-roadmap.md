# Vivid — World-Class Roadmap (synthesis)

The condensed plan tying together the 4 research streams. Each move maps to a phase, a measurable, and an owner status (T = theme, A = admin, M = marketing, O = owner). Status: ✓ done · ▢ in flight · ☐ pending.

---

## North star
Become **South Africa's category-defining online supplement brand** within 12 months. Hit **R300,000/month** online revenue by month 6 at a blended 3× ROAS.

## Positioning — one line
*"Plant-first. Exact mg on the bottle. Subscribed, delivered, explained."*

The three pillars Vivid will out-execute SA peers on:
1. **Transparency** — exact mg, no proprietary blends, per-batch COAs, traceable sourcing (Ritual's Made Traceable applied to SA).
2. **Personalisation** — 90-second quiz, named stacks, free expert chat, subscribe & save (HUM/Persona/AG1 fused).
3. **Brand love** — editorial science aesthetic (Seed), goal-coloured collection IA (Olly), founder/expert voice (Goop's pattern, anonymised SA-1996 origin).

## Differentiators with no SA equivalent (Vivid's wedge)
| Move | Source pattern | Vivid play |
|---|---|---|
| **Traceable sourcing page** | Ritual *Made Traceable* | `/pages/our-sourcing` lists supplier name + manufacturing location for every ingredient — no SA brand does this |
| **Subscribe-first pricing** | AG1, Ritual, Seed | Already wired — push 25% of revenue to subscription by month 6 |
| **Quiz → personalised stack** | HUM, Persona, Care/of (cautious) | Already wired — cut to 6 questions, add "Building your stack…" load, free expert follow-up |
| **Per-batch COAs** | Thorne, Seed | Upload PDFs as a metafield on each PDP |
| **Goal-colour collection IA** | Olly | Sleep = indigo, Energy = ochre, etc., on collection cards |
| **Format ownership** | Wellbeing's *Melts*, Seed's *ViaCap* | 2027 — explore liposomal or sachet line |
| **Free RD chat** | HUM, Persona | Wire to existing free-consultation page |
| **Practitioner portal** | Pure Encapsulations | 2026 H2 — pharmacist/dietitian sign-up + 25% wholesale tier |

## Catalog reality
- 55 SKUs (52 supplements + 3 bundles)
- 36 in stock — **Onelife Omni stock sync gap is the #1 P0** (owner: O)
- Mostly entry/mid price band (R0–R400). Sweet-spot bundles R599–R799 with 15% subscription = R650+ AOV.
- Gaps vs international: no liposomal, no creatine for women SKU, no menopause stack, no Highveld hay-fever seasonal stack, no electrolyte sachet. **Formulation roadmap below.**

## Formulation roadmap (12-month)
1. **Highveld Hayfever Stack** (existing quercetin + bromelain + nettle + vit C) — bundle for Sept push
2. **Perimenopause Essentials** (existing vitex + adaptogens + magnesium + vit D) — bundle
3. **Comrades Recovery Stack** (existing magnesium + creatine + curcumin + electrolytes) — bundle
4. **NEW SKU — Vivid Daily** (single-scoop greens, AG1-style flagship) — H2 2026
5. **NEW SKU — Magnesium L-threonate** (no SA player owns this) — Q3
6. **NEW SKU — Creatine for women (3g micro-dosed daily)** — Q3
7. **NEW SKU — Liposomal vitamin C** — Q4 (format wedge)
8. **NEW SKU — Quercetin + Nettle hay-fever** — annualise for spring 2027

## Implementation phases

### Phase 1 — Theme + IA shipping (this sprint, weeks 1–2)
- ✓ Duplicate theme → `149043052630` (working draft)
- ▢ DietarySupplement + Product + Offer + AggregateRating + Review schema on every PDP
- ▢ Traceability page (`/pages/our-sourcing`) — Ritual-style
- ▢ Credentialed founder/family page (`/pages/founder-family`) with Person schema — anonymous but credentialed
- ▢ Goal-colour system on collection cards (Olly-inspired)
- ▢ Bundle ladder pricing visual on PDP (1/2/4 with escalating discount)
- ▢ Trust badge row on PDP — 4 icons (3rd-party tested · no proprietary blends · vegan · SAHPRA-aligned)
- ▢ Free shipping threshold A/B (R400 → R450) — frontend gate
- ▢ Quiz cut to 6 questions + "Building your stack…" load

### Phase 2 — Content shipping (weeks 2–4)
- ☐ 4 condition hub pages: `/conditions/sleep`, `/stress`, `/energy`, `/immunity`
- ☐ 8 ingredient pillar pages: magnesium glycinate, ashwagandha, L-theanine, vit D3, omega-3, curcumin, quercetin, 5-HTP
- ☐ 6 comparison blog posts: mag glycinate vs citrate; ashwa vs rhodiola; collagen marine vs bovine; whey vs plant SA; mag forms; vit D forms
- ☐ Update `/pages/llms-txt` + add `/pages/llms-full`
- ☐ Refresh `/pages/about` + `/pages/our-approach` with new positioning copy

### Phase 3 — Marketing infra (weeks 2–6)
- ☐ Klaviyo flows: welcome (5), abandoned cart (3), post-purchase education (5), winback (2)
- ☐ WhatsApp opt-in at checkout (POPIA-compliant) + WATI/Bird hookup
- ☐ Judge.me wired with day-21 review request + R50 voucher GWP
- ☐ Referral programme (ReferralCandy or Friendbuy) — Give R75 / Get R75
- ☐ Loyalty programme (Smile.io) — 1 pt/R1, bonus pts for review/quiz/birthday
- ☐ Meta Pixel + GA4 + CAPI audit; quiz event tracking

### Phase 4 — Paid acquisition (weeks 4–24)
- ☐ Meta R400/day broad + RT (weeks 4–8) → R1,000/day (weeks 8–12) → R1,800–2,500/day (months 4–6)
- ☐ Google Search brand + product + intent; Shopping/PMax
- ☐ TikTok Spark ads boosting organic winners
- ☐ YouTube pre-roll bumpers on health/podcast inventory

### Phase 5 — Organic social (weeks 1–24, daily)
- ☐ IG: 4 reels + 3 carousels + 2 stories/day; 12k followers by month 6
- ☐ TikTok: 1–2/day; 18k by month 6
- ☐ YouTube Shorts: 5/wk + 1 long-form/mo; 4k subs
- ☐ Pinterest: 10 idea pins/day; 50k monthly views
- ☐ LinkedIn (founder): 4/wk; 5k followers
- ☐ X (founder): 3–5/day; 3.5k followers
- ☐ Threads: 5–8/day; 4k followers

### Phase 6 — PR + influencer (weeks 2–24)
- ☐ Nano gifting: 30/mo (R600–1,200 stack + 15% affiliate)
- ☐ Micro paid: 4/mo (R3,000–12,000 + affiliate)
- ☐ Macro paid: 1/quarter (R25,000–150,000 + usage rights)
- ☐ SA media: pitch 10 publications (News24, IOL, Daily Maverick, Women's Health SA, Longevity, Health24, BusinessLive, TimesLIVE, Health Intelligence, Sowetan Lifestyle) — 5 placements in 90 days
- ☐ Podcast tour: 8 SA wellness podcasts in 6 months

### Phase 7 — SEO + GEO (continuous)
- ☐ Submit sitemap to GSC + Bing Webmaster Tools; set ZA geo target
- ☐ Optimise GBP for the 3 Onelife stores; cross-link Vivid
- ☐ Core Web Vitals: LCP <2.5s, INP <200ms (Shopify app cull)
- ☐ Get on listicles (Women's Health SA, Longevity, Health24 "best magnesium" roundups)
- ☐ Reddit seeding (founder account, disclosed) in `r/southafrica`, `r/Supplements`, `r/Nootropics`
- ☐ Monthly AI-citation monitoring (Profound or manual prompt logs across ChatGPT, Perplexity, Gemini, Claude)

---

## Revenue model — getting to R300k/mo

Working backwards from the target at 3× blended ROAS = **R100k/mo ad spend**:

| Month | Ad spend | Revenue target | AOV | Orders | Subs % | Notes |
|---|---|---|---|---|---|---|
| 1 | R12k | R36k | R550 | 65 | 5% | Learning phase |
| 2 | R20k | R65k | R580 | 112 | 8% | First scaling |
| 3 | R35k | R120k | R600 | 200 | 12% | Influencer kicking in |
| 4 | R60k | R200k | R625 | 320 | 18% | Subs flywheel |
| 5 | R85k | R270k | R650 | 415 | 22% | Loyalty + referral live |
| 6 | R100k | **R300k** | R675 | 445 | 25% | Target hit |

Sub revenue at 25% = **R75k/mo recurring** by month 6.

---

## Daily/weekly dashboards
Pipe Shopify + Klaviyo + Meta + Google + TikTok into Looker Studio.
Stand up a "Vivid growth" tab inside the existing Onelife dashboard (already has Klaviyo + Shopify tabs) — see `CLAUDE.md`.

Weekly: revenue, ROAS by channel, CPA, quiz→purchase rate, sub growth, follower growth.
Monthly: LTV(90d), repeat rate, sub %, cohort retention, LTV:CAC.
Quarterly: brand search volume, NPS, channel mix vs target.
