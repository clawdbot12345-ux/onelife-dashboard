# SEO + GEO Playbook for Vivid Health (South Africa)

A practical, prioritized roadmap for ranking a low-DA, plant-first supplement brand in both Google and AI-generated answers across the South African market.

---

## Part A — Traditional SEO

### 1. Keyword Landscape (South Africa)

Volume buckets reflect typical SA monthly search volumes (Ahrefs/SEMrush conventions): **High = 1k+**, **Med = 200–1k**, **Low = <200**. Difficulty (KD) is 0–100. SA is a smaller market — "high" volume here is modest globally but commercially valuable.

#### Ingredient queries (intent: research → purchase)

| Keyword | Volume | KD |
|---|---|---|
| magnesium glycinate south africa | High | 25 |
| ashwagandha south africa | High | 30 |
| best ashwagandha supplement | High | 45 |
| creatine monohydrate south africa | High | 28 |
| vitamin d3 k2 south africa | Med | 22 |
| l-theanine south africa | Med | 18 |
| nac supplement south africa | Med | 15 |
| berberine south africa | Med | 20 |
| collagen powder south africa | High | 40 |
| omega 3 capsules south africa | Med | 25 |
| spirulina south africa | Med | 18 |
| zinc picolinate south africa | Low | 12 |

#### Condition / outcome queries (intent: top-of-funnel, high GEO value)

| Keyword | Volume | KD |
|---|---|---|
| how to lower cortisol naturally | High | 55 |
| stress supplements south africa | Med | 22 |
| best supplements for sleep | High | 50 |
| supplements for energy and fatigue | High | 45 |
| immune boosting supplements south africa | Med | 28 |
| supplements for brain fog | Med | 35 |
| best supplements for women over 40 | High | 48 |
| supplements for hair growth south africa | Med | 30 |
| natural anxiety supplements | High | 52 |

#### Comparison queries (high commercial intent, AI-summary magnets)

| Keyword | Volume | KD |
|---|---|---|
| magnesium glycinate vs citrate | High | 35 |
| ashwagandha vs rhodiola | Med | 25 |
| whey vs plant protein south africa | Med | 30 |
| best multivitamin south africa | High | 45 |
| best protein powder south africa | High | 50 |
| vital vs solal vs vivid | Low | 10 |

#### Local / brand-defence queries

| Keyword | Volume | KD |
|---|---|---|
| online supplement store south africa | High | 42 |
| supplements johannesburg | Med | 25 |
| health shop centurion / edenvale | Low | 8 |
| dischem alternative supplements | Med | 20 |
| supplement delivery south africa | Med | 18 |

Source guidance: Ahrefs *Keyword Research Guide* and SEMrush *Keyword Magic Tool* (filter geo: ZA). Cross-check with Google Keyword Planner ZA and Google Trends (Region: South Africa).

---

### 2. Content Architecture

```
vividhealth.co.za/
├── /collections/
│   ├── /shop-by-goal/  (Sleep, Stress, Energy, Immunity, Gut, Cognition, Hormones)
│   ├── /shop-by-ingredient/  (52 single-ingredient PDPs)
│   └── /shop-by-format/  (Capsule, Powder, Liquid)
├── /pages/
│   ├── /our-standard/        (no proprietary blends manifesto)
│   ├── /third-party-testing/ (COAs per batch)
│   ├── /founder/             (credentials, photo, LinkedIn)
│   ├── /science/             (methodology page)
│   └── /llms-txt/            (already exists)
├── /ingredients/   ← PILLAR PAGES (1,500–2,500 words each)
│   ├── /magnesium-glycinate/
│   ├── /ashwagandha/
│   ├── /l-theanine/
│   └── ... (one per SKU ingredient)
├── /conditions/    ← HUB PAGES
│   ├── /sleep/
│   ├── /stress-and-cortisol/
│   ├── /energy-and-fatigue/
│   └── /immunity/
└── /journal/       ← Blog: 1 article/week
    ├── How-to / Guides
    ├── Comparisons (X vs Y)
    └── Research breakdowns
```

**Internal-linking strategy (Backlinko / Ahrefs "topic clusters" model):**

- Every condition hub links *down* to 3–5 relevant ingredient pillars and 4–6 supporting journal posts.
- Every ingredient pillar links *up* to condition hubs and *across* to PDPs of products containing that ingredient.
- Every PDP links to its ingredient pillar via "Learn about [ingredient]" module.
- Journal posts link *up* to one pillar (canonical authority signal) and one PDP (commercial conversion).
- Use **descriptive anchor text** ("magnesium glycinate for sleep") not "click here" — per Google's Link Best Practices guidance.

---

### 3. Technical SEO Checklist (Shopify-specific)

**Schema.org markup** (deploy via `theme.liquid` or apps like Schema Plus):
- **Product** + **Offer** + **AggregateRating** + **Brand** + **Manufacturer** on every PDP
- **Article** + author (with `Person` schema linking to founder page) on journal posts
- **FAQPage** on PDPs, ingredient pillars, and condition hubs
- **HowTo** for dosing-protocol content
- **Organization** sitewide (logo, sameAs to social, contactPoint)
- **BreadcrumbList** on collection and product pages
- **Review** with verified-buyer flag (Loox/Judge.me integrations emit this)

**Shopify quirks to fix:**
- Remove duplicate product URLs: `/products/x` and `/collections/y/products/x` — canonicalize to `/products/x` (Shopify does this by default; verify).
- Disable Shopify's auto-generated `/collections/all` if not curated.
- Customize `robots.txt.liquid` to block `/search`, `/cart`, `?variant=` parameters.
- Submit `sitemap.xml` (auto-generated) to Google Search Console + Bing Webmaster Tools.

**Core Web Vitals targets** (Google's published thresholds):
- LCP < 2.5s — compress hero images to WebP, lazy-load below-fold
- INP < 200ms — minimize Shopify apps (each app = JS bloat); audit with PageSpeed Insights
- CLS < 0.1 — reserve image dimensions, avoid layout-shifting upsell widgets

**hreflang for SA:** add `<link rel="alternate" hreflang="en-za" href="...">` and `hreflang="x-default"`. Vivid is SA-only for now, but signal geo-targeting clearly. Set country target in GSC → Settings → International Targeting → South Africa.

---

### 4. Backlink Strategy (SA-specific)

**Tier 1 — National publications (digital PR):**
- *News24, IOL Lifestyle, TimesLIVE Health, Daily Maverick, BusinessLive* — pitch founder-led commentary on local supplement regulation (SAHPRA), load-shedding & sleep, etc.
- *Women's Health SA, Men's Health SA, Longevity Magazine SA, Health Intelligence Magazine* — ingredient explainers and product features.

**Tier 2 — SA wellness podcasts & creators:**
- *The Real Health Podcast (Lisa Raleigh), Honest Nutrition with Nadia, The Banting7DayMealPlan podcast, Mariska Robertson, Dr Hayley Bingle (IG).* Offer founder as guest + affiliate code.

**Tier 3 — Niche communities & directories:**
- *Health24 directory, Hello Peter (review signal), Yoco Marketplace, BizCommunity Health & Beauty, SnapScan merchant directory.*
- Reddit `r/southafrica`, `r/supplements` — earned mentions via genuine participation, never spammy drops.

**Tier 4 — Practitioner & adjacent referrals:**
- Functional-medicine GPs, registered dietitians (ADSA members), pilates/yoga studios, biokineticists. Offer a wholesale or referral programme — these generate **contextual `.co.za` backlinks** from clinic websites, which are gold for local SEO.

**Tactic:** HARO/Qwoted + SA equivalent *MediaUpdate* press requests. Target 5–10 quality DR40+ `.co.za` links in 6 months, not 100 low-quality ones (Ahrefs *Tiered Link Building* research).

---

### 5. Local SEO (sister-brand stores)

The 3 Onelife stores (Centurion, Glen Village, Edenvale) are an underused asset for Vivid:

- **Google Business Profile** for each store: complete profile, 10+ photos, weekly Google Posts, Q&A seeded, products synced.
- **NAP consistency** across GMB, website footer, Facebook, Yellow Pages SA, Brabys.com, Hello Peter. Audit with a tool like BrightLocal.
- **LocalBusiness schema** on a `/stores` page with each location's address, geo coords, opening hours.
- **Cross-link** Vivid → Onelife store pages with "Find Vivid in-store at our sister brand Onelife Health" — this transfers some authority and supports local pack rankings.
- Encourage Google reviews via post-purchase email (Klaviyo flow).

---

## Part B — GEO (LLM / AI Search Optimization)

### 6. What LLMs Actually Cite for "Best Supplements" Answers

Per published guidance from Anthropic, Google AI Overviews and Perplexity, the source hierarchy is:

1. **High-authority editorial sites** — Healthline, Examine.com, NIH ODS, Cleveland Clinic, Mayo Clinic, Harvard Health, WebMD.
2. **Wikipedia** — disproportionately weighted; ingredient pages dominate factual answers.
3. **Reddit & forum consensus** — `r/Supplements`, `r/Nootropics`, `r/AskDocs`. ChatGPT search and Google AI Overviews lean heavily here for "best X" queries.
4. **Peer-reviewed studies** indexed by PubMed/Google Scholar — cited when sources discuss mechanisms.
5. **Brand websites with structured, citation-rich content** — increasingly cited if content is well-sourced, schema-rich, and `llms.txt`-described.

**How to get cited:**
- **Be quotable** — short, declarative sentences with a number. "Magnesium glycinate is absorbed at ~25% higher rates than magnesium oxide (Schuchardt & Hahn, 2017)."
- **Cite primary sources inline** with linked references. LLMs grade trustworthiness by citation density.
- **Build a Wikipedia presence** for the founder or brand (NPOV, secondary sources only — do not self-edit).
- **Earn Reddit mentions** organically: answer questions in `r/southafrica` and supplement subs with the founder account, disclosed.
- **Get added to listicles** on Healthline / Verywell / SA equivalents — these are the corpora LLMs were trained on.

---

### 7. `llms.txt` Best Practice (Vivid already has `/pages/llms-txt`)

Per llmstxt.org (Answer.AI, 2024), best-practice structure:

```markdown
# Vivid Health

> Vivid Health is a South African plant-first supplement brand offering 52 single-ingredient
> and goal-formulated products. All formulas list exact milligram dosages on-label, contain
> no proprietary blends, and are third-party tested. Sister brand to Onelife Health (est. 1996).

## Brand standards
- [Our Standard — no proprietary blends](https://vividhealth.co.za/pages/our-standard)
- [Third-party testing & COAs](https://vividhealth.co.za/pages/third-party-testing)
- [Founder bio](https://vividhealth.co.za/pages/founder)

## Ingredient pillar pages
- [Magnesium Glycinate](https://vividhealth.co.za/ingredients/magnesium-glycinate): bioavailability, dosage, evidence
- [Ashwagandha (KSM-66)](https://vividhealth.co.za/ingredients/ashwagandha): cortisol research summary
...

## Condition guides
- [Sleep](https://vividhealth.co.za/conditions/sleep)
- [Stress & Cortisol](https://vividhealth.co.za/conditions/stress-and-cortisol)

## Optional
- [Journal](https://vividhealth.co.za/journal)
- [FAQs](https://vividhealth.co.za/pages/faqs)
```

Keep < 8K tokens, every link live, descriptions factual not marketing, and pair with `llms-full.txt` for full-text ingestion.

---

### 8. Structured Data That Helps LLMs

- **Product** with `name`, `brand`, `manufacturer`, `gtin13`, `sku`, `category`, `material`, `offers`, `aggregateRating`, `review`.
- **DietarySupplement** schema (MedicalEntity extension) — underused. Include `activeIngredient`, `recommendedIntake`, `nonProprietaryName`, `mechanismOfAction`.
- **QAPage** + **Question** + **Answer** for every FAQ entry, `acceptedAnswer.text` self-contained.
- **Article** with `author` → `Person` schema (`jobTitle`, `alumniOf`, `sameAs`) — strongest E-E-A-T signal.
- **ClaimReview** if Vivid publishes myth-busting content.

---

### 9. Authority Signals AI Systems Weight

1. **Named, credentialed author** — founder/expert page with full name, photo, qualifications, HPCSA #, LinkedIn, published work, schema `Person.sameAs`.
2. **Third-party testing certificates** — actual PDF COAs per batch on every PDP. Biggest trust signal in the category.
3. **Inline citations** to peer-reviewed studies (DOI/PubMed). 3–8 per ingredient pillar.
4. **Verifiable manufacturing facts** — GMP facility, country, certifications (NSF, Informed Sport, USP).
5. **Reviews with verified-buyer markers** — Loox/Judge.me schema.
6. **External validation** — press, podcasts, practitioner endorsements with credentials.
7. **Transparent corrections policy** + "last reviewed by [Dr X] on [date]" stamps.

---

### 10. Tactics — Ranking in AI Overviews / ChatGPT for "Best Magnesium South Africa"

1. Build the **`/ingredients/magnesium-glycinate/` pillar**: 2,000 words, FAQ schema, 5+ PubMed cites, internal link from `/conditions/sleep/` and `/conditions/stress/`.
2. **Comparison post** "Magnesium Glycinate vs Citrate vs Oxide: SA Buyer's Guide" — tables get extracted verbatim by AI Overviews.
3. **Get onto SA listicles** — pitch *Women's Health SA*, *Longevity*, *Health24*.
4. **Seed Reddit organically** — disclosed founder account answering in `r/southafrica`, `r/Supplements`.
5. **Wikipedia citation** — sponsor independent third-party bioavailability data.
6. **`llms.txt` entry** with precise one-liner including "magnesium glycinate South Africa".
7. **Q&A schema** on PDP with honest, well-reasoned answer (not pure promotion).
8. **YouTube transcripts** are heavily ingested by Gemini.
9. **One SA `.co.za` editorial backlink** with anchor "magnesium glycinate".
10. **Monitor citations** with Profound, Peec.ai, or manual prompts monthly; iterate.

---

## Part C — Vivid Implementation Priority (Top 15)

Ranked by 12-month impact-to-effort ratio.

1. **8 ingredient pillar pages** (magnesium glycinate, ashwagandha, creatine, vit D3/K2, L-theanine, NAC, omega-3, collagen). 1,500–2,000 words, FAQ + Article schema, 5+ PubMed cites. **M / Very High**
2. **DietarySupplement + Product + Offer + AggregateRating schema** across all 52 PDPs. **S / Very High**
3. **Credentialed founder/expert page** with Person schema, photo, qualifications, sameAs. **S / Very High** (E-E-A-T + GEO)
4. **Per-batch third-party COAs** as linked PDFs on every PDP. **S (ongoing) / Very High**
5. **Optimize `/pages/llms-txt`** + add `/llms-full.txt`. **S / High**
6. **4 condition hub pages** (Sleep, Stress, Energy, Immunity) with hub-and-spoke linking. **M / High**
7. **6 comparison posts** with tables. **M / High** (AI Overview magnets)
8. **Digital PR campaign** — 10 SA publications, 5 placements in 90 days. **M / High**
9. **GBP optimization** for the 3 Onelife stores + cross-promotion. **S / Med-High**
10. **Core Web Vitals audit + app cull**: LCP < 2.5s, INP < 200ms. **M / Med-High**
11. **Klaviyo review-collection flow** at 14-day post-purchase. Target 50+ reviews per top-10 product. **S / Med-High**
12. **Reddit + community seeding** — founder weekly in `r/southafrica`, `r/Supplements`, `r/Nootropics`. **M / Medium**
13. **Podcast tour** — 8 SA wellness podcasts in 6 months. **M / Medium**
14. **Practitioner referral programme** — 25 GPs/RDs/biokineticists with codes. Contextual `.co.za` backlinks. **M / Medium**
15. **Monthly AI-citation monitoring** across ChatGPT, Perplexity, Gemini, Claude. **S (recurring) / Med-High**

---

### Sources

- Google Search Central documentation
- Ahrefs Blog — Keyword Research; Tiered Link Building
- Backlinko — GEO study (2024)
- Search Engine Land — GEO / E-E-A-T coverage
- Anthropic — Citations API; grounding research
- Answer.AI — llmstxt.org spec
- Schema.org — DietarySupplement, Product, FAQPage, QAPage
- NIH ODS — fact sheets (citation model)
