# One Life Health — Growth Plan to R300k/month
**Date:** 2026-06-09 · **Author:** Claude (growth build session)
**Goal:** R300k/month online revenue. May 2026 actual: R107k. Trajectory: 65k → 107k → ~120k.

---

## 1. The math (why conversion, not traffic)

| Metric (May 2026) | Value | Industry healthy |
|---|---|---|
| Sessions | 46,483 | — |
| Conversion rate | **0.37%** | 2–3% |
| Session → cart add | **1.65%** | 7–10% |
| Checkout → completed | **40%** | 60–70% |
| AOV | R594 | — |
| Repeat customer rate | **15.7% and falling** (33% in Feb) | 25–35% |
| Mobile share of traffic | 83% | converts at 0.33% vs desktop 0.68% |
| Email sessions (60d) | **129** | should be 15–25% of revenue |
| Paid sessions (60d) | 159 | agency producing ~nothing measurable |

**Path to R300k without any new traffic:**
46,000 sessions × 1.1% conversion × R600 AOV = **R304k/month**.
Tripling conversion from a catastrophically low base is far easier than tripling traffic.

## 2. The three smoking guns (found in analytics)

### A. No express checkout — `supportedDigitalWallets: []`
No Apple Pay, Google Pay, or Shop Pay on a store that is 83% mobile.
Every mobile buyer must hand-type card details. This is the #1 driver of the
40% checkout completion (vs 65% healthy).
**Fix (merchant, 30 min):** Settings → Payments → Shopify Payments → enable
Apple Pay, Google Pay, Shop Pay. Add Payflex or PayJustNow (BNPL) — SA health
shoppers expect 4-instalment options on R500+ baskets.

### B. ~13,000 SEO sessions/month land on commodity PDPs and convert at ZERO
Top organic landing pages (Multiforce 1,106 sessions/30d, Echinaforce 896,
Nephrosolid 846, Tim Jan 804, MSM 746, UltraFlora 732…) = in stock, price-
competitive, **zero orders**. Cause: R130 shipping on a R173 product is a 75%
surcharge; Dis-Chem/Clicks offer free click-&-collect everywhere.
**Fix (theme, this build):**
1. Free-shipping progress nudge on PDP ("You're R227 from free delivery")
2. "Collect free at Centurion / Glen Village / Edenvale — ready today" block on every PDP (Gauteng = 60% of revenue)
3. "Pairs well with" basket-builder under ATC targeted at sub-R400 landings
4. BNPL badge ("4 payments of R43 with Payflex") once app installed

### C. Email is dead — 129 sessions in 60 days
Klaviyo is configured but flows are not driving traffic. For health e-comm,
flows (welcome, abandoned cart, browse abandonment, post-purchase, replen)
should drive 15–25% of revenue. At R300k target that's R45–75k/month from
email alone.
**Fix:** Build the 6 core Klaviyo flows (this session, see §6).

## 3. Funnel leak inventory

| Stage | Now | Target | Levers |
|---|---|---|---|
| Session → PDP engagement | weak | — | speed, mobile UX (done in prior session), trust strip |
| PDP → Cart | 1.65% | 5% | wallets badge, BNPL, stock/collect messaging, reviews above fold, basket-builder |
| Cart → Checkout | 56% | 70% | free-ship progress (done), trust, express checkout buttons in drawer |
| Checkout → Order | 40% | 65% | **digital wallets**, BNPL, shipping shock removal (collect option) |
| Repeat purchase | 16% | 30% | subscriptions (Shopify native), replenishment flows, loyalty |

## 4. Revenue bridge to R300k

| Lever | Mechanics | Est. monthly impact |
|---|---|---|
| Express checkout + BNPL | checkout completion 40%→60% | +R54k |
| Commodity-PDP conversion kit (collect-in-store, basket builder, progress bar) | 13k sessions × 1.2% × R450 | +R70k |
| Klaviyo 6-flow build | 15% of revenue at maturity | +R35–45k |
| Subscriptions on top-50 replenishables | 100 subs × R450 by month 3 | +R45k |
| AOV bundles (stack builder, "complete the routine") | AOV R594→R680 | +R25k |
| SEO/GEO expansion (collection landers, schema) | compounding | +R20k+ |
| **Total identified** | | **~R250–260k incremental** |

## 5. Gauteng moat
60% of revenue, 3 physical stores, same-day potential. No national competitor
can match "order by 12pm, collect at Centurion today, talk to Precious".
This is the differentiation wedge vs Dis-Chem (impersonal) and Faithful to
Nature (no stores, slower shipping).

## 6. Workstreams this build
1. ✅ Theme duplicated → GROWTH BUILD 2026-06 (185971867958)
2. PDP conversion kit (progress bar, collect-in-store, basket-builder, BNPL/wallet badges)
3. Cart drawer express-checkout block
4. Klaviyo flows: welcome, abandoned checkout, browse abandonment, post-purchase, winback, replenishment
5. SEO: product schema + FAQ schema on PDPs/guides, collection landers for top commercial queries
6. Research agents (running): international patterns, SA gap map, social playbook → final marketing playbook doc
7. Merchant action list (payments, BNPL app, subscriptions app)

*(Research agent outputs + final playbook appended when complete.)*
