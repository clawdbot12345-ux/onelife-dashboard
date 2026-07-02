# Vivid Health — Best-in-Class Feature Catalog (Shopify, 2026)
**Date:** 2026-07-02 · Companion to `vivid-health-redesign-blueprint-2026-07-02.md`. App pricing verified against the Shopify App Store mid-2026. Stat flags: `[V]` vendor-claimed · `[I]` independent/press · `[U]` unverified/directional.

**Strategic thread:** the consultants and the 17 protocols are the moat — most features below digitise that human expertise, not replace it.

## Executive summary — the "do first" stack (launch quarter)

| Priority | Feature | Implementation | ~Cost/mo | Effort |
|---|---|---|---|---|
| 1 | Subscribe & Save + cancel-save + dunning | Appstle Business | $30 | S |
| 2 | Supplement quiz → protocol recommendation | RevenueHunt | $0–39 | S |
| 3 | Protocol stacks as shoppable bundles | Shopify Bundles (native) + landing pages | Free | M |
| 4 | WhatsApp order updates + refill reminders | Wati/Zoko + Meta fees | ~$35–99 | M |
| 5 | Loyalty with VIP tiers (perk = free consult) | Rivo Scale | $49 | S–M |
| 6 | Batch COA lookup + QR on label | Custom page + metafields | Free (dev days) | S |
| 7 | SA payments: Peach/Yoco + Ozow + Payflex/PayJustNow | Gateways | % fees | S |
| 8 | Bob Go shipping (Courier Guy, Pudo, Pargo) | Bob Go app | Low | S |
| 9 | Reviews | Judge.me | $15 | S |
| 10 | Founding-100 waitlist launch, milestone referrals | Klaviyo + landing page | Free | M |

Total core app spend ≈ **$130–230/mo**, deliberately avoiding %-of-revenue apps (Skio, Loop paid, ReferralCandy) that tax a high-margin ZAR brand in USD.

## 1. Personalization

**1.1 Product recommendation quiz — S — DO FIRST.** Map quiz outcomes to the 17 Dispensary stacks; gate results behind email/WhatsApp opt-in → Klaviyo. Quizzes convert 37.6% of starters to leads at 55.5% completion (Interact, 80M leads `[V-large]`); quiz-takers purchase at 7–25% (Octane AI brands `[V]`). App: **RevenueHunt free (100 responses/mo) / $39 (500)**, 4.9★. Octane AI $50–200/mo is poor value at launch traffic; skip Jebbit.

**1.2 Native curated cross-sells — S — free.** Shopify **Search & Discovery**: hand-set complementary products per PDP encoding consultant pairing knowledge (magnesium ↔ 5-HTP). Personalization lifts revenue 5–15% (McKinsey `[I]`); this is the zero-cost 60% of Rebuy.

**1.3 Quiz → named routine → subscription box (Care/of mechanic, done safely) — M.** Quiz output = "Your Stress & Sleep Protocol" pre-loaded as a subscription bundle. Lesson: Care/of died June 2024 because it personalised *manufacturing*, not because quizzes failed (TechCrunch `[I]`) — personalise the *recommendation*, sell standard SKUs. HUM/Gainful pair quiz with a free human expert — exactly the consultant model.

**1.4 Claude-powered "Ask a Vivid consultant" — L — phase 2 differentiator.** RAG over 50 labels + 17 signed protocols + SAHPRA-approved claim language only; interaction/pregnancy/diagnosis triggers hand off to live WhatsApp. No competitor can train on signed consultant protocols. ~$50–200/mo API at launch traffic.

**1.5 Off-the-shelf AI concierge — M — test first.** **Rep AI free→$99 (10k visitors)→$350**; vendor claims +22–25% CVR `[V]`. Generic bots can't enforce supplement-claim guardrails — audit before trusting. Shopify Magic/Sidekick = free native admin AI (team leverage, not shopper-facing).

## 2. Subscriptions & Retention

**App verdict:** **Appstle Business $30/mo, 0% fees** (build-a-box, prepaid, cancel-save, dunning, swap). Seal $9.95–24.95 = simplicity runner-up. Skio ($599+1%+$0.20), Loop paid ($99–399+0.75–1%), Recharge ($99+1.49%+$0.19) only past ~$50k/mo sub revenue. Native Shopify subscriptions lack churn tooling — false economy.

- **2.1 Subscribe & Save (10–20% off heroes + stacks) — S.** Supplement subscribers = 2–3x LTV; ~8–9x gross profit vs one-time buyers reordering ~1.4x (Eightx `[I-modeled]`); replenishment churn 4–7%/mo vs 8–12% curated `[I]`.
- **2.2 Cancellation-save flow — S (in Appstle).** Reason survey → matched counter-offer. 12–20% cancel in month 1; 44% of cancels inside 90 days (Eightx `[I]`); good flows save 10–34% (Churnkey `[V-large]`); paused subscribers reactivate 40–60% vs 3–10% for cancels.
- **2.3 Dunning — S (included).** Involuntary churn = 20–40%+ of losses `[I]`; SA card declines above US average.
- **2.4 WhatsApp refill reminders — M — unfair advantage.** Usage-cycle timed, 1-click reorder; WhatsApp reorder converts 18–24% vs 6–8% email `[V]`; ~98% opens `[V]`. Pair Appstle with **Wati ~$30–49 / Zoko $34.99** + Meta fees. POPIA consent required.
- **2.5 Prepaid 3/6/12-month + gifting — S (native in Appstle).** Annual prepaid retains ~2.5x monthly at month 12 (28% vs 11% `[I-modeled]`); cash-flow positive.
- **2.6 Build-a-box protocol subscription — M.** 3–5-SKU monthly box mirroring protocols, tiered discount. Bundle buyers 18–54% higher LTV `[I]`.
- **2.7 Frictionless skip/swap/pause portal — S.** 19% of H&W subscribers skipped ≥1 order — flexibility is the alternative to cancelling (Recharge `[V-large]`). Don't hide it.

## 3. Trust & Transparency

- **3.1 Batch COA lookup + QR on label — S — highest trust-per-rand.** "Enter batch → lab certificate" (Sunset Lake/Nootropics Depot pattern). Baymard: 1–3 trust-signal types convert ~23% better than none, **7+ types convert worse** `[I-via-summary/U-exact]`. Nobody in SA does batch-level COA. Custom page + metafields, R0/mo.
- **3.2 SAHPRA claim compliance — S — non-negotiable.** Low-risk claims only: "contributes / assists / helps / aids / maintains"; no disease claims; complementary-medicine labelling per Medicines Act (SAHPRA guideline 7.04 `[I]`). Bake into PDP templates, quiz, any AI advisor allowlist. VAT-inclusive prices; POPIA express opt-in.
- **3.3 Ingredient traceability page — M.** Ritual's Made Traceable, SA edition: named manufacturer + source per hero ingredient + clinical-dose disclosure. Metafields + photography.
- **3.4 Clinical-reference library on PDPs — M.** Thorne/Momentous "Research" tab: numbered citations per ingredient in SAHPRA wording. The substance behind premium price.
- **3.5 Named consultant endorsements — S.** Faces, names, signatures on the 17 protocols and PDPs. Zero cost, unreplicable.
- **3.6 Third-party testing badges — S–M.** Real lab partners; 2–3 badges max (Baymard). Informed Choice/NSF-type marks later for the sport angle.
- **3.7 Verified reviews — S.** **Judge.me $15/mo flat** for fastest accumulation; upgrade to Okendo ($19–299) later for attribute reviews ("helped my sleep: 9/10").

## 4. Loyalty, Referral & Community

**App verdict:** **Rivo Scale $49/mo** — only major app with VIP tiers under $199 (Smile needs $199; LoyaltyLion starts $199), plus Shopify POS earn/redeem linking the 3 Gauteng stores. Skip ReferralCandy ($39 + 10.5% success fee).

- **4.1 Points, omnichannel via POS — S.** Redeemers show 5.3x repeat rates; member CLV +15–40% `[V-agg]`. The store↔web loop is One Life's unique bridge.
- **4.2 Give-get referral "Give R150, get R150" — S.** Flat ZAR protects margin; consultants get their own links. H&W referral conversion median 3.6%, top quartile 7.2% `[I]`.
- **4.3 VIP tiers with experiential perks — M.** "Vivid / Vivid+ / Inner Circle"; top perk = **free WhatsApp consult** (near-zero marginal cost). Tiered programs ~1.8x ROI of flat; VIPs ~73% higher AOV `[V-agg]`; Vitamin Shoppe precedent (free nutrition coaching top-tier `[I]`).
- **4.4 Subscriber × loyalty stacking — S.** Points on recurring charges; "subscribers reach Gold 2x faster."
- **4.5 "30-Day Reset" challenge + private WhatsApp community — M — signature play.** Buy Reset stack → consultant-led WhatsApp group → finishers get tier boost → graduates get the sub offer. Converts one-time buyers into habit-formed subscribers inside the 90-day churn window. WhatsApp Communities + Klaviyo + landing page; cost = consultant moderation time.

## 5. Content & Education

- **5.1 Shop-by-goal navigation — S.** Outcome collections (standard at MegaFood, New Chapter, GNC). Cheapest findability win.
- **5.2 Protocol pages (17 stacks as shoppable landers) — M — flagship asset.** Consultant rationale + science + one-click bundle/sub + signature. SEO hub + merchandising + trust engine in one. Native, $0/mo.
- **5.3 Learn hub/journal — M ongoing.** Ingredient explainers, "magnesium types compared", SA-seasonal content. Compounding SEO for a new domain.
- **5.4 Consultant video on PDPs — M.** 60-sec "why we formulated it this way". Video PDPs show 8–35% CVR lifts (Tolstoy cases `[V]`). Start free (native video + Tolstoy free tier).
- **5.5 Email/WhatsApp drip courses — S–M.** "5-day Magnesium Masterclass" Klaviyo flow + WhatsApp variant; each lesson ends in one product link. Course frame beats discount frame for a premium brand.

## 6. Commerce UX Value-Adds

- **6.1 Bundles with tiered discounts — S.** Native **Shopify Bundles (free)**; Rhode grew kit revenue $948k→$2.53M/mo on native bundles `[I-reported]`. Bundles lift AOV 15–35% `[V-agg]`. Rebuy (from $25/mo) post-launch for dynamic cart-aware bundles (+20–46% AOV `[V]`).
- **6.2 Free-shipping + gift progress bar — S.** "R120 from free delivery… R300 from a free MSM sample." Tiered GWP 25–35% higher AOV than single-tier `[U]`. Free apps or theme-native.
- **6.3 Gift-with-purchase — S.** Native Functions. Perceived value ~3x cost vs discounting; **gift, don't discount** protects premium price integrity.
- **6.4 "Complete your routine" cross-sells — S→M.** Native Search & Discovery first; Rebuy Smart Cart later.
- **6.5 Sample program — M.** Free sachet at checkout + paid "Discovery Pack" with credit-back. Drives category expansion across 50 SKUs.
- **6.6 Premium unboxing + QR-to-routine card — M.** Matte insert: "Your protocol — scan for your routine + reorder." 52% say premium packaging raises repeat likelihood `[V-survey]`. Print cost only.
- **6.7 Delivery-date/instructions picker — S nice-to-have.** Order-note instructions matter in SA (complexes, estates); full apps ~$10–20/mo lower priority than pickup points.

## 7. South Africa Specific

- **7.1 Payments — S — conversion-critical.** Shopify Payments unavailable in SA (third-party gateway + 0.6–2% Shopify platform fee by plan `[I]`). Recommended: **Peach Payments or Yoco (~2.95% cards) + Ozow pay-by-bank (1.5% — beats card economics at high AOV)**. 3+ payment methods = up to 25% higher checkout conversion `[V]`.
- **7.2 BNPL: Payflex + PayJustNow — S.** SA BNPL doubled 3%→6% of volume 2024→25; most-requested method (34%) `[I-ish]`; Payflex claims +30% AOV `[V]`; SA BNPL baskets avg ~R1,568 — protocol-stack territory. PDP installment messaging ("4 × R107").
- **7.3 WhatsApp Business commerce — M — THE channel.** ~96% of SA digital population uses WhatsApp (DataReportal `[I]`); cart recovery 10–25% vs 5–8% email `[V]`. Wati/Zoko + POPIA opt-in at checkout. Klaviyo native WhatsApp (Sept 2025) is the stack-consistent alternative; Klaviyo SMS likely doesn't support SA numbers — WhatsApp is the path.
- **7.4 Delivery: Bob Go + Courier Guy + Pudo/Pargo — S.** Bob Go (free SA aggregator app); Pargo 4,000+ points (~R60–85); Pudo lockers ~R50–60; same-day Gauteng as premium flex; **free click-&-collect at the 3 stores** (zero marginal cost + foot traffic). FTN/WW anchor free shipping at R400.
- **7.5 Takealot as billboard — M strategic.** 5–10 hero SKUs at RRP only (R400/mo + ~8–15% success fees); protocols/subs stay DTC-exclusive so the store is always the better deal.
- **7.6 Loadshedding comms — deprioritise.** Suspended 300+ consecutive days; Eskom projects none through summer 2026 `[I]`. Keep a banner pattern in reserve only.

## 8. Premium Signals (design discipline, not apps)

1. **Restraint as a system:** 2 typefaces, ~double element spacing, tight palette, no discount-red.
2. **Photography standard:** consistent studio + SA-context lifestyle + texture macros — the biggest perceived-quality lever.
3. **Micro-interactions:** smooth ATC, considered hover/loading states; speed itself is a premium signal.
4. **Editorial voice:** calm, evidence-led, first-person consultant; never hype (SAHPRA-safer too).
5. **Baymard discipline:** few strong trust signals beat many; payment badges at checkout (~18% abandonment stems from trust `[I]`).
6. **Theme:** quality OS 2.0 premium theme (~$300–400 once) customised, over heavy custom build at launch.

## 9. Launch Plays

- **9.1 Milestone-referral waitlist ("Founding 100") — M.** Harry's: 100k emails in one week, 77% from referrals `[I]`. Vivid: 3 friends = sample pack; 5 = GWP; 10 = 3 months Inner Circle. Klaviyo + landing page (Viral Loops ~$49 if turnkey).
- **9.2 Founding-member perks — S.** Founding **% discount locked for life while subscribed** (% not fixed price); numbered welcome card; top tier year one; first access to new SKUs.
- **9.3 Launch sequence — S.** Klaviyo: consultant-story tease → protocol education drip → 48-h founding window → social proof. Seed via the 3 stores + consultant WhatsApp lists + onelife.co.za — the built-in audience most DTC brands rent for six figures.

## Flagged/unverified stats
GWP repeat-rate & progress-bar figures `[U]`; bundle-buyer 2.7x LTV `[U]`; unboxing 52% (industry survey); challenge +34% `[U-weak]`; HUM +18% AOV `[U]`; Baymard 23% via secondary summary; all Rep AI/Rebuy/Tolstoy/Payflex lifts are vendor cases; Takealot health success fee unpublished (use their estimator).

## Sources (abridged — full URLs in PR description of origin research)
Octane AI/RevenueHunt/Rep AI/Appstle/Seal/Loop/Skio/Recharge/Smile/Rivo/LoyaltyLion/ReferralCandy/Judge.me/Tolstoy/Bob Go Shopify App Store listings · Interact quiz benchmarks · TechCrunch & NutraIngredients on Care/of · Eightx supplement-subscription economics · Recharge H&W subscriber trends · Churnkey save benchmarks · Klaviyo replenishment docs · Ritual Made Traceable + Modern Retail coverage · Thorne clinical research · SAHPRA complementary-medicines guideline 7.04 · Baymard vitamins & supplements research · Stitch BNPL SA · Payflex/Ozow/Netcash gateway guides · DataReportal Digital 2025 SA · Pargo/Takealot fee guides · Eskom loadshedding statements · Viral Loops & Tim Ferriss on Harry's prelaunch · Retently/Meyers unboxing studies.
