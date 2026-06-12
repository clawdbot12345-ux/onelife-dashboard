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

**T1 target definition (proposed, needs sign-off):** monthly online total sales ≥ **R105,650** (= TTM avg × 1.5) sustained for the full month of September 2026. Note: Apr 2026 (R100,969) and May 2026 (R107,185) already touch this level — propose Naadir either confirms this definition (engine defends + consolidates recent growth) or re-bases to "May 2026 × 1.5 = R160,778/mo", which is the honest stretch reading. **Decision needed.**

## T2–T4 — Store revenue (Centurion +20%, GVS +50%, Edenvale +60%) by 31 Dec 2026

**BLOCKED: no Omni ERP access.** Cannot establish per-store TTM baselines. This is the #1 item in `state/NEEDS.md`. Even a nightly CSV export of per-store sales unblocks measurement.

## T5 — Brand awareness (continuous)

| Metric | Baseline (2026-06-12) | Source |
|---|---|---|
| WhatsApp Hub members | **410 (confirmed by Naadir 2026-06-12)** → target 1,000+ | interviews/FOUNDER.md. Cadence Mon/Wed/Thu but "terrible and not exclusive" — engine to take over programming |
| Instagram followers | ~1.4K | research/COMPETITORS.md (vs FTN 118K, WW 51K) |
| TikTok followers (@onelifehealthstore) | TBD — Naadir/pull | |
| Branded search volume | TBD — needs Search Console access | |
| Klaviyo list size + growth rate | TBD — pull in Phase 2 completion | |
| Google review count/rating per store ×4 | TBD — partial in COMPETITORS.md; needs GBP access | |

## Changelog
- 2026-06-12: Created. T1 locked from live Shopify pull; T2–T4 blocked on Omni; T5 partial.
