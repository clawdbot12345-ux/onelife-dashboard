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

**UNBLOCKED 2026-06-12** via Omni reports (`data/omni/reports-v2/`, Codex catalog). Saved reports expose current-period data, not TTM — baselines locked on June 2026 run-rate (the honest available base; prior-FY periods requested as follow-up). All figures **excl VAT**.

| Store | June 2026 run-rate (from dated Daily Turnover, 8–9 trading days) | GP% | Baseline /mo (locked) | Target /mo (31 Dec) |
|---|---|---|---|---|
| Centurion/HO* | ~R57.5k/trading day → R1.50–1.73M/mo | 33.8% | **R1.50M** | **R1.80M** (+20%) |
| Edenvale | ~R13.0k/day → R338–390k/mo | 34.4% | **R360k** | **R576k** (+60%) |
| Glen Village | ~R11.4k/day → R298–343k/mo | 32.4% | **R320k** | **R480k** (+50%) |

*HO includes online fulfilment — the ~R109k/mo ex-VAT Shopify revenue sits inside HO's number; per-channel split within HO is a refinement task.
Cross-check: company-wide `Monthly Turnover Analysis` shows R2.14M (FY period 01) / R2.04M (02) — consistent with branch sums. **Blended GP 33–34% confirmed against owner's business_config (0.33).** Whole business ≈ R2.0–2.1M/mo ex VAT → online is currently ~5% of revenue; Vivid's R500k+/mo target = ~24% of total revenue (Vivid current share: extraction task queued).

## T5 — Brand awareness (continuous)

| Metric | Baseline (2026-06-12) | Source |
|---|---|---|
| WhatsApp Hub members | **410 (confirmed by Naadir 2026-06-12)** → target 1,000+ | interviews/FOUNDER.md. Cadence Mon/Wed/Thu but "terrible and not exclusive" — engine to take over programming |
| Facebook (One Life Health Supermarket) | **24,000 followers** — underused asset | Naadir screenshot 2026-06-12 |
| TikTok (@onelifehealthstore) | **10,600 followers, 13.1K likes** — active | Naadir screenshot 2026-06-12 |
| Instagram (@one_life_health_supermarket) | **1,411 followers** — the weak channel | Naadir screenshot 2026-06-12 |
| Vivid Health revenue | **R829,933 (GP 35.9%) over saved report period ≈ TTM → ~R72k/mo** vs owner target R500k+/mo. Shares: HO 4.2%, EDN 1.9%, GVS 2.0% | data/omni/reports-v2/vivid-summary.md (supplier IL = Interlife; period caveat noted in source) |
| Branded search volume | TBD — needs Search Console access | |
| Klaviyo list size + growth rate | TBD — pull in Phase 2 completion | |
| Google review count/rating per store ×4 | TBD — partial in COMPETITORS.md; needs GBP access | |

## Changelog
- 2026-06-12: Created. T1 locked from live Shopify pull; T2–T4 blocked on Omni; T5 partial.
