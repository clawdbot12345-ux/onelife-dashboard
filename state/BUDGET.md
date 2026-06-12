# BUDGET — approved budgets, spend to date, ROAS per channel

Last updated: 2026-06-12 (engine bootstrap)

## Approved budgets
| Item | Amount | Status |
|---|---|---|
| Month-1 engine test envelope | **R5,000** | Offered by Naadir 2026-06-12; engine recommendation sent (below); awaiting final confirm + R2k/test standing approval |

**Hard GP% floor for any promotion: 25% (Naadir, 2026-06-12).** Compliance-checker and bundle math enforce this.

### Engine recommendation on budget size (sent 2026-06-12)
R5,000/month is the RIGHT number for months 1–2 — not because more wouldn't help, but because nothing measurable currently earns above the 3.48 break-even ROAS, so new money would burn like the old money. Plan: 2 × R2,000 Meta local-radius tests (Centurion + Edenvale defence) + R1,000 reserve, 2-week cycles, kill at ROAS <1.5. The bigger lever is the EXISTING R19.5k/mo (ads+agency) producing ≤R6.3k revenue — recommend UTM enforcement first, then pause/restructure what can't prove itself. Scale to R15–20k/mo in months 2–3 ONLY into channels that prove ROAS >3.5 on a test.

## Pre-existing standing spend (from data/business_config.yml — owner-maintained)
| Line | Monthly | Attributed return (30d to 2026-06-12) |
|---|---|---|
| Google ads | R8,000 | R0 last-click `google-paid`; some revenue may hide in `google-unclassified` (R6,263) |
| Meta ads | R2,750 | R0 attributed |
| TikTok ads | R3,250 | R0 attributed |
| Agency fee | R5,500 | — |
| **Total** | **R19,500** | ≤ R6,263 revenue → ≤ R2,067 gross profit @33% |

🔴 **Paid is underwater.** Break-even ROAS = 3.48 (on incl-VAT revenue, before delivery/agency). Current measurable ROAS ≈ 0.3 at best. Engine recommendation (pending Phase 3 + Naadir): fix UTM attribution first, then pause/restructure rather than continue blind spend.

## Engine running cost (token burn)
| Week | Est. burn | Notes |
|---|---|---|
| 2026-06-12 (bootstrap) | ~150k subagent tokens (3 research agents) + main session | Phase 1 research fan-out — the expensive week by design |

Policy: if engine running cost exceeds 10% of marketing budget, flag and simplify (GROWTH_ENGINE.md principle 7).

## Kill-criteria log
(empty — no live engine-managed ads)
