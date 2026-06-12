# BASELINES — Trailing-12-Month (Jun 2025 – May 2026)

**Status: PROVISIONAL — awaiting Naadir's explicit sign-off (`approvals/granted/baselines.flag`).**
T1 numbers are locked from live Shopify analytics (pulled 2026-06-12, `onelifehealth.myshopify.com`).
T2–T4 are BLOCKED on Omni ERP access. T5 partially measurable.

## T1 — Online (Shopify) revenue: +50% by 30 Sep 2026

| Metric (TTM Jun 2025–May 2026) | Value | Source |
|---|---|---|
| Total sales (incl VAT, incl shipping) | **R845,201** | ShopifyQL `FROM sales SHOW total_sales` |
| Net sales | R781,354 | ShopifyQL |
| Gross sales | R790,372 | ShopifyQL |
| Orders | 1,209 | ShopifyQL |
| TTM monthly average (total sales) | **R70,433/mo** | derived |
| AOV (TTM range) | R520–R746 (May 2026: R594) | ShopifyQL |
| Sessions (TTM) | 444,754 | ShopifyQL `FROM sessions` |
| Conversion rate (TTM range) | 0.13%–0.42% (May 2026: 0.37%) | ShopifyQL |
| Returning-customer rate | 33.8% (Jun 25) → **15.7% (May 26)** — collapsing, confirmed | ShopifyQL |
| Email % of online revenue (30d at pull) | 15.8% (R19.8k of R125k) | weekly business report 2026-06-12 |

**T1 target — SET BY NAADIR 2026-06-12: online store to R200,000/month** (supersedes the A/B options previously proposed). From the current ~R125k/30d run-rate that is **+60%**. Deadline assumption: 30 Sep 2026 per the master prompt's T1 — requires ~3.1% compound weekly growth for ~15 weeks. **Flag: aggressive but not absurd given Apr–May momentum (+45% in 2 months). If Naadir means "by year-end", pace relaxes to ~1.7%/week — confirm when convenient; engine paces against 30 Sep until told otherwise.**

## T2–T4 — Store revenue (Centurion +20%, GVS +50%, Edenvale +60%) by 31 Dec 2026

**BLOCKED: no Omni ERP access.** Cannot establish per-store TTM baselines. This is the #1 item in `state/NEEDS.md`. Even a nightly CSV export of per-store sales unblocks measurement.

## T5 — Brand awareness (continuous)

| Metric | Baseline (2026-06-12) | Source |
|---|---|---|
| WhatsApp Hub members | **410 (confirmed by Naadir 2026-06-12)** → target 1,000+ | interviews/FOUNDER.md. Cadence Mon/Wed/Thu but "terrible and not exclusive" — engine to take over programming |
| Facebook (One Life Health Supermarket) | **24,000 followers** — underused asset | Naadir screenshot 2026-06-12 |
| TikTok (@onelifehealthstore) | **10,600 followers, 13.1K likes** — active | Naadir screenshot 2026-06-12 |
| Instagram (@one_life_health_supermarket) | **1,411 followers** — the weak channel | Naadir screenshot 2026-06-12 |
| Vivid Health revenue /mo | TBD from Omni — **owner target: R500k+/mo short term, GP 35–40%** | FOUNDER.md batch 2 |
| Branded search volume | TBD — needs Search Console access | |
| Klaviyo list size + growth rate | TBD — pull in Phase 2 completion | |
| Google review count/rating per store ×4 | TBD — partial in COMPETITORS.md; needs GBP access | |

## Changelog
- 2026-06-12: Created. T1 locked from live Shopify pull; T2–T4 blocked on Omni; T5 partial.
