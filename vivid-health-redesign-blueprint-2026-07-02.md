# Vivid Health — World-Class Store Blueprint
**Date:** 2026-07-02 · **Scope:** complete audit + redesign spec for the dedicated Vivid Health Shopify store (currently in draft) · **Companions:** `vivid-health-audit-2026-07-02.md` (current-state audit) · `vivid/redesign-mockup.html` (high-fidelity visual mockup — open it, click "Product page" and "💡 Design notes")

**Research base:** live teardowns of Ritual, Seed, AG1, Thorne, Cymbiotika, Wild Nutrition, Moon Juice, HUM, Perelel and Aesop (2026-07-02); a 60+-source feature/app research sweep with verified Shopify App Store pricing; the July SA market research (`reports/market-research-2026-07-01.md`); live catalog data for all 55 Vivid SKUs.

---

## 1. The one-paragraph strategy

Vivid Health should launch as **South Africa's transparent supplement brand**: consultant-formulated, SA-made, honestly dosed, with the country's first batch-certificate lookup and its first true Subscribe & Save. The world-class brands split into two camps — loud discount machines (Cymbiotika) and silent luxury (Aesop). The profitable middle, where Ritual and Wild Nutrition live, is **calm design + one clear subscription offer + radical ingredient transparency + named human experts**. That middle is exactly what One Life already owns culturally (Precious, the counter, "we tell people NOT to buy things") — no SA competitor can copy it, and it costs mostly copy, metafields and discipline rather than expensive apps.

**Brand line:** *Supplements with nothing to hide.*

## 2. Positioning & voice

| Axis | Decision |
|---|---|
| Category story | "Born behind the counter of South Africa's apothecary — since 1996" |
| Premium proof | Paper trail, not adjectives: batch COAs, dosing policy, named consultants |
| Voice | The Precious house voice, systematised: warm, direct, zero hype, "supports" never "cures", and **every PDP includes when NOT to buy** ("The honest bit") |
| Price posture | Hold premium prices; **gift, don't discount** (GWP + subscription perks instead of red sale badges) |
| Regulatory | SAHPRA low-risk claim wording only ("contributes / assists / helps / maintains"); prices displayed **incl VAT**, rounded; POPIA express opt-in everywhere |

## 3. Product architecture — fix before design (blocking)

The live catalog is the biggest premium-killer today. 55 SKUs carry **nine inconsistent range prefixes** — `IMMUNE`, `GUT HEALTH`, `GUT HEALTH & IMMUNE`, `VIVID BODY`, `PHYSICAL HEALTH`, `STAY VIVID`, `VIVID NOURISHMENT`, `NUTRIENT HEALTH`, `NUTRITENT HEALTH` (typo, 2 SKUs), `WOMAN`, `MEN` — in ALL-CAPS titles like `VIVID HEALTH - IMMUNE - Mullein 60 Capsules`. Plus: `Colest Control` (misspelt Cholesterol), `Angus Castus` (should be *Agnus Castus*), `Dmae`, mixed odd-cent prices (R132.99, R239.90, R90.99) among round ones, and the Omega Oil filed under a different range in its title than its tag.

**New architecture — six goal ranges, one naming grammar:**

| Range | Label colour | SKUs (examples) |
|---|---|---|
| Vivid Immune | Coral `#DD5A3A` | Buffered C (90/150g/300), Advanced Buffered C, Immune Plus, Quercetin Complex, Astragalus, Mullein, L-Lysine, Allergy Control, Liver & Kidney |
| Vivid Gut | Turmeric tan `#C09A5E` | Turmeric, Turmeric Plus, Clove, Black Walnut, Wormwood, Colon Flush, Apple Cider, Liquorice Root |
| Vivid Mind | Indigo `#3C5A7D` | Griffonia 5-HTP, GABA, Tranquil, DMAE, D-Ribose |
| Vivid Body | Olive `#6F7F4E` | MSM (all sizes), Flexijoint, Joint Relief, Bone Supreme, CoQ10, Omega Oil, L-Glutamine, Colest Control→**Cholesterol Support**, Garcinia |
| Vivid Woman | Plum `#8C4A63` | Maca, Sage, Agnus Castus |
| Vivid Man | Navy `#2E4057` | Prosta Care (+ future) |
| *(pantry sub-range)* Vivid Nourish | — | Spirulina, Moringa, Barley Grass, Cayenne, Epsom |

**Naming grammar:** `<Product Name> — <plain-language benefit>` with range/size as structured fields, e.g. **"Buffered C — gentle everyday vitamin C · 300 capsules"**. Title case, never ALL-CAPS. Every product gets a one-line benefit in human words (nobody searches "Griffonia"; they search "sleep" and "serotonin").

**Pricing:** round to R5/R10 (R132.99→R135, R90.99→R89 or R95), label everything "incl VAT". Restock or retire the 5 OOS SKUs before launch (Omega 300, Bone Supreme 500, Barley Grass ×2, DMAE).

## 4. Design system (implemented in the mockup)

- **Type:** Fraunces (display serif, close kin to the Onelife Cormorant world but more contemporary) + Inter (UI). Two faces total, carried from site to labels to inserts — the Aesop/AG1 coherence rule.
- **Palette:** warm bone `#FAF7F0` / deep slate `#12181B` / gold accent `#C9A227` used sparingly — plus the six label colours above as the *only* other colour. No discount-red anywhere.
- **Photography standard:** the current 3D renders are fine for launch (crop the huge canvases!); the upgrade path is (1) real studio shots on slate/botanical sets matching the existing hero banner, (2) texture macros (capsules, powders, botanicals), (3) SA-context lifestyle, (4) a 30-sec consultant video per hero SKU.
- **Motion:** subtle only — hover lifts, scroll fades, smooth cart transitions. Restraint is the trust signal.
- **Premium tells:** generous whitespace, VAT-inclusive round prices, no countdown timers, no stacked promo popups, one calm announcement bar.

## 5. Sitemap

```
Home
├─ Shop by goal (6 colour-coded collections: Immune / Gut / Mind / Body / Woman / Man)
├─ Bestsellers
├─ Stacks (17 consultant-signed protocols as shoppable bundle pages)
├─ Subscribe & Save (landing + build-a-box)
├─ Our Standards  ← the premium engine
│   ├─ Batch certificate lookup (enter batch # → COA)
│   ├─ Our dosing policy ("honestly dosed" manifesto)
│   ├─ Sourcing & manufacturing (SA traceability cards, Ritual-style)
│   └─ Quality FAQ
├─ Learn (journal: ingredient explainers, SA-seasonal, consultant bylines)
├─ Our Story (born behind the counter, 1996, the 3 stores, the consultants)
├─ Quiz (2 minutes → named routine → one-click subscribe box)
└─ Help: WhatsApp a consultant / Delivery & returns / Stores / Practitioner & wholesale
```

## 6. Page-by-page spec (see mockup for visual reference)

### Homepage (mockup: "Homepage" view)
1. Announcement bar — delivery promise + WhatsApp consultant (one line, calm)
2. Hero — dark slate, real pack lineup, one serif headline ("Supplements with nothing to hide."), quiz + bestsellers CTAs, trust proof inline. **No carousel.**
3. Gold trust ticker — SA-made · batch certificates · consultant formulated · no import wait
4. Shop by goal — six colour tiles (the label system becomes navigation)
5. Bestsellers — cards with benefit line, stars, **incl-VAT price + subscription price on every card**
6. "Premium isn't a claim. It's a paper trail." — 4 standards cards (SA-made / batch-verified / honestly dosed / consultant-formulated)
7. Subscribe & Save band with live example box
8. Consultant-signed stacks (3 featured, each with routine timing + signature)
9. Batch-lookup interactive band (dark)
10. Story band (1996 / 50+ formulas / 3 stores / 17 protocols)
11. Reviews (3, verified, including a "they told me NOT to buy" story)
12. Quiz CTA band
13. Footer — POPIA-compliant unticked opt-in, payment badges incl Payflex/Ozow

### PDP (mockup: "Product page" view)
Gallery spec (front / label-legible / capsule macro / lifestyle / 30-sec video) → colour range chip → human name + benefit subtitle → stars → **incl-VAT price + Payflex installment line** → **subscription-default buy box** (10% off, "pause or cancel anytime" at the button) → stock + store-collect + batch line → **"The honest bit"** (consultant paragraph incl. when not to buy) → accordions: Supplement facts (real table, not an image — SEO win) / Why-the-science (citations) / How to take / Batch certificate / Delivery & returns → "Pairs well with" + stack cross-sell → sticky ATC bar. 8–11 question FAQ per hero SKU.

### Collection pages
Editorial colour-band header with the goal story + consultant one-liner, then clean grid. Filters: goal, format (capsules/powder), price. Nothing like today's 584-product soup — each collection is 5–15 SKUs.

### Stack/protocol pages (flagship content asset)
One editorial page per protocol: consultant rationale + photo + signature, the science in SAHPRA wording, time-of-day routine table, the stack as one-click bundle (10% off) with subscribe option. These are simultaneously SEO hubs, bundle merchandising and the trust engine.

### Our Standards / batch lookup
The differentiating page: batch number input → COA (product, manufacture date+place, potency vs label claim, heavy metals, micro results, PDF download). Implementation: product+batch metafields or a Sheet-backed lookup, QR code on every label deep-linking to the result. A few dev-days, R0/mo, and **no other SA brand has it**.

## 7. Feature roadmap

### Launch quarter (the "do first" stack — ~$130–230/mo total app spend)
| # | Feature | How | Effort |
|---|---|---|---|
| 1 | Subscribe & Save + cancel-save flow + dunning + build-a-box | **Appstle Business $30/mo, 0% fees** (Skio/Recharge %-fees punish a high-margin ZAR brand) | S |
| 2 | Quiz → named routine → subscribe box | **RevenueHunt** free→$39; logic = map answers to the 17 protocols; email/WhatsApp gate → Klaviyo | S |
| 3 | Protocol stacks as bundles | **Shopify Bundles (native, free)** + stack landing pages | M |
| 4 | Batch COA lookup + QR labels | Custom page + metafields | S |
| 5 | Reviews | **Judge.me $15/mo** — post-purchase requests from day 1 (fixes the zero-reviews problem before it starts) | S |
| 6 | WhatsApp commerce: order updates, refill reminders, consultant chat | **Wati/Zoko ~$35–99/mo** + Meta fees (~R0.14 utility msg); Klaviyo's native WhatsApp channel as alternative | M |
| 7 | Loyalty with VIP tiers | **Rivo Scale $49/mo** (only app with VIP tiers <$199; POS earn/redeem links the 3 stores) — top-tier perk: free consult | S–M |
| 8 | SA payments | Peach/Yoco cards + **Ozow EFT (1.5% beats card fees)** + **Payflex & PayJustNow BNPL** + installment messaging on PDPs | S |
| 9 | Delivery | **Bob Go** (free app): Courier Guy door, Pudo/Pargo pickup (~R60), same-day Gauteng premium, **free click-&-collect at 3 stores**; free delivery threshold R400 (parity with onelife.co.za promise) | S |
| 10 | Pixels from day 1 | GA4 + Meta + TikTok channels installed **before** launch (don't repeat the onelife.co.za H1 finding) | S |

### Next 90 days
- **"The honest bit" + clinical-reference accordions** on all 55 PDPs (content sprint, consultant-reviewed)
- **SA traceability cards** (Ritual pattern, done authentically: named SA manufacturer, source origins per hero ingredient)
- **Consultant faces everywhere** — bios, signatures on protocols, 60-sec PDP videos (Tolstoy free tier)
- **Gift-with-purchase ladder** in cart (progress bar: free delivery → free sample → free MSM 150g) — native Functions
- **30-Day Reset challenge**: buy the Reset stack → private consultant-led WhatsApp community → graduates get the subscription offer (attacks the 90-day churn window)
- **Referral** inside Rivo: "Give R150, get R150" + consultant referral links
- **Takealot billboard**: 5–10 hero SKUs at RRP only; subscriptions/stacks stay DTC-exclusive

### Later (only after the above is flawless)
Custom Claude-powered "Ask a Vivid consultant" advisor (RAG over the 50 labels + 17 protocols, hard SAHPRA guardrails, live WhatsApp handoff) · Welcome Kit for first subscription orders · prepaid 3/6/12-month gift plans (in Appstle) · practitioner/wholesale portal · Informed-Choice-type certification for the sport angle.

## 8. Launch play — "The Founding 100"

1. **Waitlist microsite** (Klaviyo + landing page): email/WhatsApp capture → referral page with milestone rewards (3 friends = sample pack; 5 = GWP; 10 = a year of Inner Circle). Harry's collected 100k emails in a week with this exact mechanic.
2. **Founding-member offer:** first 100 subscribers get their **founding % discount locked for life** (percentage, not fixed price — you can still raise prices), numbered welcome card in box #1, top loyalty tier for year one.
3. **Seed through what you already own:** the 3 stores (till QR), the consultant WhatsApp lists, onelife.co.za banners + Klaviyo list (65k profiles), the existing "Vivid story" traffic. Most DTC brands spend six figures to rent the audience One Life already has.
4. Launch sequence in Klaviyo: consultant story tease → protocol education drip → 48-h founding window → social proof follow-up.

## 9. KPIs for quarter one

| Metric | Target |
|---|---|
| Subscription attach on hero SKUs | ≥ 25% of orders |
| Founding subscribers | 100 in 30 days (~R45k/mo recurring floor at R450 avg) |
| Reviews on top 10 SKUs | ≥ 15 each by day 60 (Judge.me + REVIEW25) |
| Quiz completion → purchase | ≥ 10% |
| Repeat/refill rate day-90 | ≥ 30% (WhatsApp reminders) |
| Batch-lookup usage | tracked from day 1 — it's the PR story |

## 10. What I need from you (blocking items, in order)

1. **Draft store access** — the storefront preview URL + password (or collaborator access / an Admin API token). I could not find the draft store from here; once I have it I can audit the actual build and apply this blueprint page-by-page directly.
2. **Domain decision** — ⚠️ **vividhealth.co.za is owned by an unrelated practitioner business** (herbal/ultrasound services, WordPress, active). Options: buy it, or launch on `vividhealth.shop` / `getvivid.co.za` / `vivid.co.za` (check availability) / keep it as a branded section of onelife.co.za. This needs deciding before any SEO work.
3. **Lab paperwork** — batch COAs from the SA contract manufacturer (MJ Labs / SA-Labs per the growth playbook). If potency/micro certificates exist per run, the batch-lookup feature is a few dev-days away; if not, that conversation with the manufacturer is the highest-leverage phone call of the launch.
4. **Consultant assets** — names, photos, one-paragraph bios and sign-off approval for protocol signatures (Precious + team).
5. **Label QR real estate** — next print run should carry the batch-lookup QR.

---

*Everything else in this blueprint is buildable without new access: the mockup, naming/architecture migration sheet, page copy, and app configuration list are in this repo. See the audit companion doc for the full current-state findings.*
