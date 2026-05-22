# Vivid Health — 90-day digital presence strategy

A working document for the relaunch of `vividhealthsa.co.za` as a
Shopify-powered DTC brand, and the interim activations needed
to build presence while the store is being built.

---

## 1. Audit of the current site

`vividhealthsa.co.za` is a WordPress brochure with portfolio-style
product pages. Honest reading:

| Problem | Impact |
|---|---|
| No e-commerce, no prices, no cart | Every visitor leaves to find the brand on `onelife.co.za`. We lose the email, the data, and the brand attribution. |
| Generic positioning ("transformative power…") | No reason to choose Vivid over Solal, Solgar, Faithful to Nature private label. |
| No founder story, no SA-made angle made loud | The strongest differentiator (local manufacture, dose transparency) is invisible. |
| Thin SEO — no schema, no blog, default meta descriptions | Vivid does not rank for any of its own product names without "vividhealthsa" in the query. |
| One social link (Facebook), no IG, no email capture | Zero re-engagement infrastructure. Every visitor is a one-shot. |
| Product detail pages have good copy + clean PNGs | **Reusable asset.** Don't throw it out. |

Meanwhile **55 Vivid SKUs already trade on `onelife.co.za`** with
real ZAR prices and product photography on Shopify CDN. The
catalogue exists. The brand site doesn't sell it.

---

## 2. Brand positioning

**One-line:** Plant-based supplements made in South Africa.
Real doses, transparent ingredients, vegetable capsules.

**Tagline:** *Vivid by nature. Verified by science.*

**Three pillars** (use these everywhere — PDPs, ads, packaging copy):

1. **Stated dosage.** Every Vivid label lists milligrams. No
   proprietary blends. If a study used 810 mg of MSM, our MSM
   capsule has 810 mg.
2. **Made in Centurion.** Blended and bottled in South Africa.
   Not imported white-label with a SA sticker.
3. **Plant-first.** Vegetable capsule shells (HPMC).
   Sugar-free, gluten-free, dairy-free where indicated. Vegan
   where the formulation allows.

**Voice:** Direct. South African. Confident but not bro-y.
Lead with the ingredient + dose, not the lifestyle promise.

> *"810 mg MSM, plant-derived sulphur. Supports cartilage and
> collagen."* — yes.
>
> *"Discover your wellness journey with our holistic
> botanical companion."* — no.

---

## 3. Information architecture

```
vividhealthsa.co.za
├── /                              Home
├── /shop                          Collection — all 55 SKUs
│   ├── ?goal=gut                  filtered by health goal
│   ├── ?form=capsule              filtered by form
│   ├── ?diet=vegan
│   └── ?bundles=1
├── /products/[handle]             PDP (55 + 3 bundles)
├── /ingredients                   Ingredient library (SEO/GEO play)
│   └── /ingredients/[name]        Per-ingredient page
├── /conditions                    Condition pages (SEO/GEO play)
│   └── /conditions/[name]        e.g. /conditions/seasonal-allergies
├── /journal                       Long-form content
│   └── /journal/[slug]
├── /about                         Brand story + Onelife retail story
├── /stores                        Find a stockist (3 Onelife stores)
├── /contact
└── /pages/{shipping, returns, faq, popia}
```

**Key SEO move:** the **Ingredient library** + **Condition pages**.
These are programmatic landing pages that target high-intent SA
queries like *"mullein for chest tightness south africa"* or
*"buffered vitamin c reflux"*. They each link out to 2–4 Vivid
products. This is how a small brand outranks pharmacies on the
specific ingredient queries.

---

## 4. SEO — technical foundations

Set these before any content goes live.

- **Shopify Online Store 2.0 theme** (the starter in `vivid/theme/`).
- **Schema markup**: `Product`, `Breadcrumb`, `FAQPage`, `Article`,
  `Organisation`, `LocalBusiness` (for Onelife stores).
  Snippets ship in `product-main.liquid`.
- **Sitemap** — Shopify auto-generates `/sitemap.xml`. Submit
  to Google Search Console + Bing Webmaster on day 1.
- **Page speed**: target LCP <2.0s, CLS <0.05. Hero image
  served as WebP, lazy-load below the fold.
- **Internal linking**: every PDP links to its ingredient
  pages and condition pages. Every ingredient page links to
  the products containing it. Every condition page links to
  3–5 recommended products.
- **Robots/meta**: canonicals on every URL. `noindex` on
  internal search results, account pages, cart.
- **Image alt text** policy: `{Ingredient} {dose} — Vivid Health
  {form}, made in South Africa`. Not "supplement bottle."
- **Hreflang**: skip for now — ZAR-only, SA-only. Revisit if
  Markets expand.

---

## 5. SEO — content plan (first 90 days)

Two parallel content streams. **Ingredient pages = breadth.**
**Journal = depth.**

### Ingredient pages (build in first 30 days)

One per ingredient currently in a Vivid formulation. ~30 pages.
Each follows the same template:

1. H1: *{Ingredient} in South Africa — what it is, what it does, dosage*
2. 250–400 words of original, scientifically careful copy
3. Studies block (3–5 PubMed citations, no fluff)
4. Typical dose range (what the research uses)
5. Linked Vivid products containing the ingredient
6. `FAQPage` schema block with the 4–5 questions people ask

Priority ingredients (highest search volume in SA):

| Ingredient | Target query | Linked products |
|---|---|---|
| MSM | *"msm benefits south africa"* | MSM 90/300/500g/150g |
| Mullein | *"mullein for chest"* | Mullein 60 |
| Turmeric | *"curcumin south africa"* | Turmeric 300, Turmeric Plus |
| Buffered C | *"non-acidic vitamin c"* | Buffered C ×4 |
| Quercetin | *"quercetin for hay fever"* | Quercetin Complex, Allergy Control |
| 5-HTP | *"5-htp south africa"* | Griffonia 60 |
| Maca | *"maca for energy women"* | Maca 60 |
| Saw Palmetto | *"saw palmetto prostate"* | Prosta Care |
| L-Lysine | *"l-lysine cold sores"* | L-Lysine 60 |
| Apple Cider Vinegar | *"acv capsules south africa"* | Apple Cider 90 |

### Condition / journal pages (build through 90 days)

Long-form, journal-style. One per week. These are the GEO play.

| Wk | Title | Target |
|----|-------|--------|
| 1  | "Why we buffer vitamin C with calcium" | Buffered C ×4 |
| 2  | "A parasite cleanse without the woo: what black walnut, clove, and wormwood actually do" | Black Walnut, Clove, Wormwood |
| 3  | "Three magnesiums, three jobs: oxide vs glycinate vs citrate vs sulfate" | Colon Flush, Epsom Salt |
| 4  | "Hay fever in Gauteng: a non-drowsy supplement protocol" | Allergy Control, Quercetin, Buffered C |
| 5  | "Mullein for chronic chest tightness — what the herb is good at" | Mullein 60 |
| 6  | "Curcumin's bioavailability problem (and why piperine matters)" | Turmeric Plus 60 |
| 7  | "Saw palmetto and the prostate: a careful look at the evidence" | Prosta Care |
| 8  | "5-HTP for sleep and mood — when it works, when it doesn't" | Griffonia 5-HTP |
| 9  | "Vitex for PMS: what 90 days of consistent dosing actually does" | Angus Castus |
| 10 | "MSM is mostly sulphur. So what?" | MSM ×4 |
| 11 | "Adrenal fatigue is not a diagnosis. Liquorice still helps." | Liquorice Root |
| 12 | "D-Ribose for athletes and the post-COVID heart" | D-Ribose |

---

## 6. GEO — Generative Engine Optimization

The new front door is ChatGPT, Claude, Gemini, and Perplexity.
When a South African asks "what's the best buffered vitamin C
in South Africa?" — we want Vivid in the answer.

### What this requires

- **Structured, fact-dense product pages.** Models extract
  best from clear `H2 / table / list` structures with
  unambiguous facts ("500 mg of calcium ascorbate per
  capsule"). The PDP template in `product-main.liquid` is
  built for this.
- **Comparison tables.** Build a `/compare` page comparing
  Vivid SKUs to common alternatives, with prices and doses.
- **FAQ schema with exact-match questions.** Mirror the
  language people use in voice/AI searches: *"is it safe
  to take buffered C with my omeprazole?"*
- **Citable studies.** Every claim on a journal post links
  out to PubMed or a SAHPRA monograph. Models reward
  citation-heavy content.
- **Brand mention seeding.** Get Vivid mentioned by name in
  third-party sources (see Activations).
  Models pull from Reddit, Quora, journalist articles,
  and forums — not just our own site.

### Tracking

- Weekly: query 5 target prompts in ChatGPT and Perplexity,
  log whether Vivid appears. Set a goal of being mentioned
  in 3+ of 10 prompts by day 90.
- Submit to `ai.txt` and `llms.txt` standards as those
  emerge.

---

## 7. Interim activations (before site launch + first 60 days)

You have **three physical retail stores** (Centurion, Glen
Village, Edenvale) and a customer base that already buys
Vivid via Onelife. Use them.

### Weeks 1–2 — *Pre-launch*

- **In-store**: announcement-bar style print signage at all
  three Onelife stores: *"Coming soon: vividhealthsa.co.za —
  scan to be first."* QR code → email capture landing page
  (single Klaviyo form, deploys in 30 minutes).
- **Email**: announce relaunch to the existing Onelife list,
  segmented to anyone who ever bought a Vivid SKU. Single
  email, single CTA.
- **Sampling**: package small samples of three flagship SKUs
  (Mullein, Buffered C, Tranquil) and hand them out at the
  tills of all three stores for two weeks. Each comes with a
  card and a coupon code valid only on `vividhealthsa.co.za`
  when it launches.

### Weeks 3–6 — *Launch + activation*

- **Launch event** at the Centurion store. *"Ingredient Day"*
  — invite local naturopaths and integrative doctors for an
  hour. Show the new site, hand out samples, get them on
  the email list. ~30 attendees, low cost, high credibility.
- **Press push**: email South African health journalists
  (`Health24`, `Longevity`, `Bona`, `IOL Lifestyle`,
  `Sunday Times Lifestyle`). Pitch is *"the first SA
  supplement brand to publish its dosing logic."* One
  follow-up at week 5.
- **Influencer**: identify 8–10 SA naturopaths / integrative
  practitioners on Instagram with 5–30k followers. Send a
  product care-package + a private link to a 30% practitioner
  discount. No gifting fee, no obligation. The ones who
  recommend product will recommend authentically.
- **Local SEO**: claim/refresh Google Business Profiles for
  all three Onelife stores. Add Vivid as a stocked brand.
  Vivid PDPs link to the stores page. Stores page links to
  each GBP.

### Weeks 7–12 — *Compounding*

- **Sampling at Park Run**: Centurion and Edenvale Park Runs
  every Saturday. Hand out D-Ribose / Tranquil samples and a
  card. ~200 runners each weekend, perfect demographic for
  joint/recovery/sleep SKUs.
- **Pharmacy seeding**: pitch a private-label or stocked
  arrangement at independent pharmacies in Centurion and
  Pretoria East. Lead with dosing-data: hand them a one-page
  PDF of the 5 most-trafficked Vivid SKUs vs imported
  competitors at the same dose.
- **Sponsorship**: one local cycling or trail event in
  Gauteng (~R10k spend), get the Vivid logo and a sampling
  presence. CoQ10 + D-Ribose are perfect for cyclist demo.
- **Practitioner CPD lunch**: invite 15 Gauteng integrative
  practitioners to lunch at a Pretoria venue. Walk through
  the formulation logic for three flagship SKUs. Cost ~R5k,
  builds the prescription channel.

---

## 8. Email — Klaviyo flows

You already have the Klaviyo MCP server configured for the
Onelife data. Migrate or fork these flows for the Vivid
list:

1. **Welcome series** (3 emails, 5 days)
   - Email 1: "What Vivid actually is" — story + 10% code
   - Email 2: "How to read a supplement label" — educational + 3 best-seller PDPs
   - Email 3: "Find your formulation" — quiz to a goal collection
2. **Abandoned cart** (3 emails, 24h / 48h / 72h)
   - Email 1: gentle reminder + image
   - Email 2: social proof (review snippets, "47 SA customers reorder this")
   - Email 3: 10% one-time code
3. **Post-purchase** (4 emails over 60 days)
   - Day 2: "How to take this for the next 4 weeks"
   - Day 14: "Common questions at the 2-week mark"
   - Day 42: review request
   - Day 56: reorder reminder
4. **Winback** (anyone who hasn't bought in 90 days)
   - Two emails, 7 days apart. Second includes a R75 voucher.
5. **Birthday flow** — 15% off, valid 7 days. (POPIA: only
   to customers who provided birthday voluntarily.)

---

## 9. Social — channel plan

| Channel | Cadence | Content |
|---|---|---|
| **Instagram** | 4 posts/wk | 1× ingredient flash card, 1× founder/lab BTS, 1× UGC repost, 1× journal teaser |
| **TikTok** | 3 short videos/wk | "60 seconds on [ingredient]" — explainer format, founder on camera |
| **YouTube** | 1 long-form/month | "How we formulate" series — 6–10 min, evergreen |
| **Facebook** | 2 posts/wk | Repurpose IG. Older SA demographic, good for menopause/men's health SKUs |
| **LinkedIn** | 1 post/wk | Founder-led, B2B angle for practitioner channel |

Skip X/Twitter — wrong audience in SA.

---

## 10. Paid

**Don't spend on paid until SEO/email/sampling are running.**
Paid is amplification, not substitution. When you do:

- **Google PMax** with the 30 ingredient pages + 55 product
  pages feeding the catalogue. R5–8k/month to start.
- **Meta**: lookalike of Onelife's existing Vivid buyers.
  Creative: founder-on-camera + the dose-stating angle.
- **No "supplements for energy"** broad targeting. Too
  saturated, too expensive. Stay on long-tail.

---

## 11. KPIs — day 30 / 60 / 90

| Metric | Day 30 | Day 60 | Day 90 |
|---|---:|---:|---:|
| Sessions / month | 4,000 | 9,000 | 18,000 |
| Email subscribers | 1,200 | 2,800 | 5,500 |
| Conversion rate | 0.8% | 1.4% | 2.0% |
| Orders / month | 32 | 126 | 360 |
| Avg order value (ZAR) | R420 | R460 | R510 |
| Revenue / month (ZAR) | R13.4k | R58k | R184k |
| Indexed pages | 80 | 130 | 200 |
| Ranking keywords (top 10) | 5 | 25 | 80 |
| AI mentions (10 test prompts) | 0 | 1 | 3 |

Numbers are deliberately conservative — beat them.

---

## 12. What needs decisions / hands

1. **Shopify Partner account or new Shopify store** — register
   `vividhealthsa.co.za` to the new store, redirect WordPress.
2. **Catalogue migration** — duplicate the 55 Vivid SKUs from
   Onelife to the new Vivid store. Use Matrixify or a direct
   GraphQL Admin script (see `vivid/data/products.json`).
3. **Photography refresh (optional, month 2)** — the current
   PNGs are clean but uniform. Commission one editorial shoot
   for hero + journal use.
4. **Klaviyo account** — separate Vivid account, or sub-list
   under Onelife? Recommend separate for clean attribution.
5. **Practitioner program** — needs a separate
   `/practitioners` page and 30% wholesale code.
6. **GBP refresh** — needs your hands. Owner verification can't
   be done remotely.

Everything else can be built in this repo and the new
Shopify store, then handed off for go-live.
