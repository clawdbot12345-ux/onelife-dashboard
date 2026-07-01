# One Life Health — Online Marketing Strategy: R130k → R500k/month
**Date:** 2026-07-01 · **Scope:** onelife.co.za + email + WhatsApp + TikTok/social + paid media + store↔online
**Basis:** Google Ads ROAS report (1 Apr–8 Jun), live dashboard data (June 2026), full Playwright site audit (`site-audit-2026-07-01.md`), SA market research (`reports/market-research-2026-07-01.md`), repo playbook history.

---

## 1. Executive summary

**The online store is losing money, and the loss is structural, not a spend problem.** Per R100 of online revenue (incl VAT): R13 VAT → R28.70 gross profit (33% GP on ex-VAT) → minus ~R14–15 delivery (R17–20k/mo on R130k) → **~R14 contribution before any marketing**. That makes the breakeven ROAS **~7.0**, and **~10** once the R5,500 agency fee is spread over R14,000 of spend (a 39% fee vs the SA norm of 10–20%).

Nothing currently running clears that bar:

| Channel | Spend/mo | Claimed return | Reality |
| --- | --- | --- | --- |
| Google PMax | ~R1.2k | ROAS 29.5 | Inflated — PMax harvests brand searches (91% of accounts in Optmyzr's 503-account study); campaign is "limited by budget; asset groups limited by policy" |
| Google Shopping | ~R3k | ROAS 3.3 | Set to **Maximise Clicks**, 0.26% conv rate — buys 51k cheap clicks, not buyers. Worst campaign, biggest Google line |
| Google Search "Launch" | ~R3.2k | ROAS 4.5 | 10.8% CTR = brand terms; paying R4.03/click for people already searching "One Life" |
| Meta | R2,750 | none (agency's own admission) | **No Meta pixel installed on the site** — Meta literally cannot optimise or report |
| TikTok paid | R3,250 | none measured | **No TikTok pixel installed** either |
| Agency fee | R5,500 | — | 39% of spend; 2–4× SA norm |

The repo's own weekly business report agrees: Shopify last-click attributes **R0 to paid** in June; 62% of online revenue came from **free** channels (Google free listings 33% + organic search 28.6%). Email is the one channel working (R20.3k = 18% of June online revenue, trending up).

**The plan:** stop the bleed (paid + delivery + agency), fix the conversion plumbing the site audit found, then scale the three channels where One Life has an unfair advantage — **email (working), TikTok (national follower lead), WhatsApp (SA's #1 platform + existing VIP group)** — with the 3 stores as a fulfilment and acquisition moat. The R500k path is a bridge of six compounding levers (§8), not one big bet.

---

## 2. The P&L truth (monthly, June baseline)

```
Revenue (incl VAT)                 R130,000
  less VAT (15%)                  −R16,957
Revenue (excl VAT)                 R113,043
  Gross profit @ 33%               R37,304
  Delivery                        −R17,000 … −R20,000
  Contribution before marketing    ~R18,300
  Ad spend                        −R14,000
  Agency fee                       −R5,500
  Payment processing (~2.9%)       ~−R3,800
NET                                ≈ −R5,000/month  (before packaging & pick/pack labour)
```

**Breakeven ROAS ≈ 7.0** (revenue incl VAT ÷ spend), **≈ 9.8 with agency fee loaded**. Every paid decision below is judged against 7.

Two structural notes:
- **Delivery at 14–15% of revenue vs a healthy 6–10%.** Cause: free shipping at R400 (competitive, but low vs a R566 ex-VAT AOV) paid out on door-to-door courier rates (~R65–130/parcel) with no cheaper option in the mix.
- **Retention is broken.** Repeat rate fell 33% (Feb) → 18% (Jun); ~zero repeat buyers within the June window. The email list is **shrinking** (−153 net/mo). Growth on a leaky bucket is rented, not owned.

---

## 3. Fix the leaks first (Weeks 1–2) — "Pillar 0"

From the live site audit (full detail in `site-audit-2026-07-01.md`):

1. **🔴 Shipping policy contradiction (same-day fix).** Site-wide promise: "FREE DELIVERY over R400 nationwide". `/policies/shipping-policy`: free over R900 Gauteng / R1,400 nationwide, else R75/R130. Whichever is true, reconcile today — this is a refund-complaint/CPA risk and a checkout-trust killer. Delivery-time claims also disagree (1–5 vs 3–7 vs 2–5 days).
2. **Install Meta pixel + TikTok pixel** (Shopify channel apps, ~an hour each). Without them there is no retargeting, no lookalikes, no measurement — any paid-social rand is burned blind. Prerequisite for ever restarting paid social.
3. **Reviews engine.** #1 best-seller shows "No reviews"; Product JSON-LD has `aggregateRating: None` (no stars in Google). Judge.me is already installed: switch on post-purchase review requests (offer the existing REVIEW25 credit), seed the top 20 SKUs, consolidate the duplicate Product schema so stars appear in search.
4. **Payment options.** Checkout is a bare Payfast redirect. Add **Payflex or PayJustNow** (BNPL) and **Ozow/instant EFT as a visible option**, plus "4 × R161" messaging on PDPs. The R1m playbook estimated ~319 lost checkouts/mo; at 56% checkout conversion there's real headroom. *(This was owner-deferred on 2026-06-12 — it should be un-deferred; it's the highest-leverage single fix on the list.)*
5. **POPIA hygiene:** un-tick the pre-checked marketing consent boxes (popup + checkout). April 2025 POPIA regs require express opt-in; pre-ticked boxes also pollute the Klaviyo list with low-intent profiles.
6. **Quick CRO batch:** checkout still shows the old blurry purple logo (replace); odd-cent prices (R440.06, R80.01) look like sync glitches — round them and label prices "incl. VAT"; collapse the mobile pre-header stack so the hero isn't 780px down; clean vendor-field artifacts ("RELEASE_SCE"); flesh out the refund policy (no return window stated).
7. **Subscriptions (Subscribe & Save) on the top 50 replenishable SKUs.** The PDP has no selling-plan widget. Supplements are a 30-day cycle and **no verified SA competitor runs a real autoship** — this is the retention lever and a moat. (Seal/Appstle-class app ≈ R500–1k/mo.)

Expected effect of Pillar 0 alone: site conversion from ~0.4% toward 0.8–1%, i.e. **+R60–100k/mo from traffic you already have** — before any new marketing.

---

## 4. Paid media: restructure, don't just cut

**Recommendation: take paid down to ~R7.5k/mo and restructure Google; pause Meta/TikTok paid entirely until pixels are installed and seasoned. Expected saving: ~R12k/mo (spend + fee) redirected to owned channels.**

### Google (R8k → ~R6k, restructured)
1. **Run Mike Rhodes' free PMax script first** (mikerhodes.com.au/scripts/pmax) to quantify how much of the 29.5× "ROAS" is your own brand traffic. This is the audit's smoking gun to show the agency.
2. **Brand Search campaign:** exact/phrase "one life health" variants, Manual/Max-Clicks, hard-capped at ~R500–800/mo. Brand clicks should cost cents, not R4.03.
3. **One consolidated non-brand campaign** — at ~30–50 orders/mo you're at the minimum for Smart Bidding: either Standard Shopping (Max Clicks → tROAS at 30+ conv/mo) or PMax **with brand exclusions applied** — never both overlapping. Feed it the 45–52% margin heroes and the condition niches that already convert (PCOS/Pcositol, GLP-1 support, magnesium/sleep, Lions Mane).
4. **Kill "Maximise Clicks" Shopping as-is.** 0.26% conversion rate is paying for traffic, not customers.
5. **One purchase conversion action.** The account has two "Purchase" actions (double-count risk). Fix conversion tracking before trusting any number.
6. **Target: ROAS ≥ 7 measured on the cleaned account, or the campaign gets cut.** Add this rule to the weekly business report as an explicit kill-switch line.
7. **Merchant Center free listings already drive 33% of revenue at R0** — keep feeding it (titles, GTINs, ratings from the review engine).

### Meta (R2,750 → R0 now; retargeting-only later)
No pixel = no case. After the pixel has 60 days of data: restart at ~R1.5–2k/mo **retargeting + email-list custom audiences only** (site visitors, cart abandoners, Engaged-90d lookalike). Judge on ROAS ≥ 7. The agency's "square designs and copy for Meta placements" spend is moot until then.

### TikTok paid (R3,250 → R0 now; Spark Ads later)
Redirect to organic + Live (§6). Once the pixel is in and organic proves which videos convert, **Spark Ads on proven winners** at ~R1.5k/mo is the re-entry — SA CPMs are among the cheapest globally.

### The agency
R5,500 on R14k across three platforms (~R4.7k each — all below any algorithm's learning threshold) is a structural mismatch. Three options, in order of preference:
1. **Renegotiate to Google-only management at ≤R2.5k/mo** with the restructure above and the ROAS-7 kill rule in the contract;
2. **Bring it in-house** — this repo already automates reporting, email, blog and SEO; a restructured R6k Google account is 2 hours/week of work;
3. Keep them only if they accept performance terms against *your* breakeven, not platform-reported ROAS.

---

## 5. Delivery economics: from 15% of revenue to <10%

Keep the R400 free-shipping promise — it beats Dis-Chem (R600), Clicks (R650) and Takealot (R650) and is at parity with Faithful to Nature/Wellness Warehouse. Fix the **cost per parcel and the mix** instead:

1. **Add a cheap fulfilment tier at checkout:** Pargo pickup points (~R70–85, 4,000+ locations, Shopify app) and/or TCG Lockers locker-to-locker (~R60). Make the *default* for sub-R400 orders the cheap tier; door-to-door becomes the paid premium option.
2. **Push click-and-collect hard** — it's free for you (3 stores, same-day pickup already live), it's the Clicks/Dis-Chem template, and every collection visit is an upsell opportunity. Target: 25% of Gauteng orders to collection by October.
3. **Rate-shop couriers via Bob Go** (free PAYG plan; rate-shopping across ~10 couriers incl. TCG, Aramex R99.99 sleeves, Paxi R59.95 satchels). At ~200 parcels/mo you should be paying R60–85 blended, not R85–100+.
4. **Nudge AOV over the threshold:** the cart already has a free-shipping progress bar and STACK5/STACK10 — add a "add R120 for free delivery" product suggestion row. Every order pushed from R450 to R620 adds ~R56 gross profit at zero delivery-cost change.

Target: delivery ≤ R12k/mo at current volume (≈9% of revenue), scaling sub-linearly as collection share grows.

---

## 6. TikTok: convert the follower lead into a revenue engine

Facts that matter: TikTok Shop is **not live in SA** (no confirmed date; ignore SEO articles claiming otherwise). SA has 29.1M adult TikTok users (+33% in 2025). The proven African monetization pattern is **TikTok Live + WhatsApp order-close** (documented in Nigeria at scale), because link-out funnels leak at the app exit.

The engine, weekly rhythm:
1. **3–4 organic videos/week** in 4 repeatable formats: "From the counter" (Precious answers a real customer question), product demo/unboxing of a hero SKU, "what we'd actually take for X" protocol shorts, myth-busting. Always: pinned comment with link + code.
2. **One TikTok Live per week** (start biweekly): themed ("Winter immunity night", "PCOS Q&A"), live-only bundle code, **orders closed in WhatsApp** — "WhatsApp 'LIVE' to 06x xxx xxxx" — with a payment link sent in chat. This is the highest-intent funnel available without Shop.
3. **Creator seeding:** R3k/mo of product (not cash) to 5–10 SA nano/micro creators in health/fitness/PCOS/GLP-1 niches; each gets a personal 10% code for attribution. Track redemptions in Shopify.
4. **Measurement:** TikTok pixel + `?utm_source=tiktok` on every bio/pinned link + unique codes. Today TikTok's contribution is literally invisible.
5. **When TikTok Shop launches in SA** (watchlist item), the brand with catalog, live-selling muscle and creator bench moves first — that's you.

Facebook/Instagram: stop treating them as growth channels. Repurpose TikTok winners as Reels (zero marginal cost), keep the pages warm for social proof and WhatsApp entry points. Their stagnation is not worth paid money to fix.

---

## 7. WhatsApp: from VIP group to commerce channel

WhatsApp reaches ~95% of SA internet users. Current setup (a group) has a POPIA problem — members see each other's numbers — and no analytics, no scale, no automation.

1. **Migrate the VIP group → WhatsApp Business API opted-in broadcast list.** Klaviyo launched a **native WhatsApp channel (Sept 2025)** — run it from the stack you already have (segments, flows, templates in one place). Cost ≈ R0.68/marketing message (a 1,000-person broadcast ≈ R680), utility messages ≈ R0.14, replies within the 24h window free.
2. **POPIA-compliant opt-in:** express consent captured at checkout tickbox (un-pre-ticked), popup, till-slip QR, and an in-group migration message ("VIP list is moving — tap to keep your spot + get member pricing"). STOP opt-out in every broadcast.
3. **Cadence:** 1 broadcast/week max (offer, restock, protocol of the month, Live announcement) + transactional/utility (order confirm, ship, collect-ready) + **abandoned-checkout WhatsApp nudge** (beats email open rates by multiples).
4. **Commerce loop:** catalog message → payment link (Payfast/Ozow) in chat → free utility confirmation. Same loop closes TikTok Live sales.
5. **The consult angle is the moat:** "Free WhatsApp consult" is already on the site. Formalise it — every consult ends with a cart link. That's a conversion path Dis-Chem cannot copy at their scale.

Target: 1,500 opted-in WhatsApp contacts by October; WhatsApp-attributed revenue R25–40k/mo by December.

---

## 8. Email: standardize the machine (it's already your best channel)

June: R20.3k attributed (18% of online revenue), up from 11% in early June. The system is designed well (`email-cadence-system-2026.md`) but is running at ~⅔ reliability with three dead flows. Standardization plan:

### Cadence — one fixed weekly grid, no improvisation
| Slot | Send | Audience | Status |
| --- | --- | --- | --- |
| Tue 09:00 | Apothecary education digest (automated) | Engaged 90d | ✅ runs — missed 06-30; add failure alerting |
| Fri 09:00 | Product spotlight (automated) | Engaged 90d | 🔴 **fired once (06-05), silent 3 Fridays — repair the workflow + add alerting** |
| Week 1 | **Monthly Digest** (best economics: R4,085/send, R2.93/recipient) | Engaged 90d | Make it a locked monthly ritual |
| Week 3 | Protocol Spotlight / social proof (human-curated) | Engaged 90d | Per design doc — actually schedule it |

Rules (already proven in your own data): Engaged-90d only; utility/digest subject lines over curiosity ones (curiosity gets 67% opens and R0 revenue); every send has a product module and one CTA; standard UTMs.

### One master template
Consolidate `tuesday_blog_digest.py` and `friday_product_campaign.py` inline HTML into **one shared template module**: same header/logo, hero, product-card grid, protocol CTA block, Precious sign-off, footer with WhatsApp line + unsubscribe. Every future campaign (human or automated) uses it — that's the consistency you're asking for, enforced in code. CTAs need a visible button treatment (clicks stuck at ~2% vs 2.5–3.5% benchmark).

### Fix the three dead/weak flows (biggest email upside)
- **Winback 60/90/120: zero recipients despite 1,462 at-risk profiles** — trigger misconfigured; at benchmark this is R3–6k/mo left on the table.
- **Post-purchase: 302 recipients, R0** — rebuild as replenishment cross-sell (30-day reminder on the exact SKU bought + protocol upsell).
- **Abandoned cart: reaches only 36/mo** on 349 started checkouts — trigger too narrow; benchmark recovery (3–5% of ~150 abandoners with email) is worth R5–10k/mo.

### Grow the list (it's shrinking: −153/mo vs +500 target)
Un-pre-ticked but *prominent* checkout opt-in; popup A/B (3% submit-rate bar); **till-slip QR + counter ask at all 3 stores** ("10% off your first online order") — R2.17m/mo of store revenue walks past the counters uncaptured; blog content upgrades (protocol PDFs); WhatsApp cross-opt-in.

Target: email+WhatsApp = 25–30% of online revenue by December (R125–150k of the R500k).

---

## 9. Retention & loyalty
1. **Subscribe & Save** (§3.7) at 10% off on ~50 replenishable heroes — anchor of the retention fix.
2. **Loyalty positioning vs Dis-Chem Better Rewards** (10–15% instant off ~180 mainstream brands): don't fight on their brands. Position member value on **practitioner/premium brands they don't discount** + protocol bundles + consult access. Exploit Faithful to Nature's 6-month points expiry with longer validity.
3. **Replenishment flow** already earns (R1,329/mo from one API-built flow) — extend to the top 20 repurchase SKUs.
4. **Win the second order:** first-order → 14-day "how's it going + what to pair" consult email/WhatsApp from Precious. Repeat rate 18% → 30% is worth more than any acquisition channel: at 196 orders/mo, every 5 points of repeat rate ≈ +R55k/yr.

---

## 10. The R130k → R500k bridge (incl VAT, monthly)

| Lever | Dec run-rate contribution | Basis |
| --- | --- | --- |
| Baseline (June) | R130k | current |
| Conversion fixes: reviews, BNPL/EFT, pricing/VAT labels, mobile fold, policy fix (CVR 0.4→0.9%) | +R95k | same traffic, audited friction removed; R1m playbook sized checkout loss at ~R190k/mo |
| Email standardized + 3 flows fixed + list growth | +R60k | 18%→25-30% of a larger base; dead flows at benchmark |
| WhatsApp channel (broadcasts + abandoned-checkout + Live closes) | +R35k | 1,500 opt-ins × SA engagement rates |
| TikTok engine (organic + Live + creator codes) | +R55k | follower lead monetized via the Nigeria-pattern funnel |
| Google restructured non-brand + free-listings/SEO compounding | +R70k | free listings already 33% at R0; cleaned paid held to ROAS ≥7 |
| Store→online capture (till QR, collect-in-store upsell) | +R30k | 3,900 store txns/mo, even 1–2% capture |
| Subscriptions/repeat (18%→30%) | +R45k | ~50 heroes on autoship; second-order program |
| **Total** | **≈ R520k** | |

Monthly milestones: **Jul R160k** (Pillar 0 live) → **Aug R210k** (email fixed, WhatsApp migrated, Google restructured) → **Sep R270k** (TikTok Live rhythm, subscriptions live) → **Oct R340k** (flywheel + collect share up) → **Nov R430k** (Black Friday on owned channels) → **Dec R500k**. Each month's target assumes the prior month's levers stay on — if a milestone misses by >20%, we stop and re-diagnose rather than spend into the gap.

**Profitability check at R500k:** GP ~R143k; delivery ~R35k (9% with collect mix); marketing ~R25k (restructured paid + WhatsApp/creator costs + tools); processing ~R14k → **~R65–70k/mo contribution** vs −R5k today.

---

## 11. Budget: R19.5k → R16k, reallocated

| Line | Now | Proposed (from Aug) |
| --- | --- | --- |
| Google Ads | R8,000 | R6,000 (brand-capped + one non-brand, ROAS≥7 rule) |
| Meta ads | R2,750 | R0 (restart retargeting-only ~R1.5k after pixel seasons) |
| TikTok ads | R3,250 | R0 → R1,500 Spark Ads on proven organic winners (Sep+) |
| Agency | R5,500 | ≤R2,500 (Google-only, renegotiated) or R0 in-house |
| WhatsApp API/Klaviyo channel | — | R1,000 |
| Creator seeding (product) | — | R3,000 |
| Reviews/subscriptions apps | — | R1,000 |
| Contingency/test | — | R1,000 |
| **Total** | **R19,500** | **≈R16,000** |

---

## 12. 30/60/90-day roadmap

**Days 1–14:** shipping-policy reconciliation · Meta+TikTok pixels · un-tick consent boxes · checkout logo · Judge.me review flow on · Rhodes PMax script + fix conversion actions · repair Friday email workflow + alerting · winback/abandoned-cart trigger fixes.
**Days 15–30:** BNPL (Payflex/PayJustNow) + Ozow live · brand/non-brand Google restructure + agency renegotiation · WhatsApp API via Klaviyo + VIP migration · till-slip QR in 3 stores · master email template shipped · Pargo/Bob Go at checkout.
**Days 31–60:** Subscribe & Save on top 50 SKUs · TikTok Live biweekly → weekly with WhatsApp close · creator seeding round 1 · post-purchase flow rebuilt · price rounding/VAT labels · monthly digest ritual locked.
**Days 61–90:** Meta retargeting restart (if pixel data supports) · Spark Ads on winners · loyalty positioning vs Better Rewards · collect-in-store push to 25% · Black Friday plan on owned channels.

**KPI dashboard (add to weekly business report):** online revenue & CVR · contribution after delivery+marketing (the real number) · blended ROAS vs the 7.0 line with kill rule · email+WhatsApp % of revenue · list net growth · repeat rate · delivery % of revenue · collect-in-store share · TikTok code redemptions.

---

## 13. What can be implemented from this repo (say the word)
- Repair `friday-product-email.yml` + add failure alerting to both email workflows; build the shared email template module.
- Winback/abandoned-cart/post-purchase flow fixes via Klaviyo API (keys already configured).
- Weekly business report: add breakeven-ROAS kill rule, delivery-%, collect-share, WhatsApp metrics.
- Dashboard: pull per-product online sales via Shopify Admin API (currently empty), refresh the stale March POS snapshot.
- Draft the renegotiation brief for the agency with the Rhodes-script evidence pack.
- Shopify theme edits for the CRO batch (prices, labels, mobile fold, vendor artifacts) as a PR-able change list.

Everything else (BNPL signup, courier accounts, WhatsApp API/BSP onboarding, store till QR printing) needs owner action — the roadmap flags each.
