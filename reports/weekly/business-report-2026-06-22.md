# One Life Online — Weekly Business Report (2026-06-22)

Period: last 30 days · Source: Shopify order journeys (own attribution),
Klaviyo values reports, data/business_config.yml.

## P&L (online, 30 days)
| Line | Amount |
|---|---|
| Revenue incl VAT | R116,492 (184 paid orders, AOV R633) |
| Revenue ex VAT | R101,297 |
| Gross profit @33% | R33,428 |
| Delivery | −R17,000 (R92/order) |
| Ad spend (G/M/T) | −R14,000 |
| Agency | −R5,500 |
| **Net contribution** | **R-3,072** |

Break-even ROAS (on incl-VAT revenue, before delivery/agency): **3.48**

## Where the money actually comes from — LAST CLICK
| Channel | Orders | Revenue (incl VAT) | Share |
|---|---|---|---|
| google-free-listings | 84 | R39,407 | 33.8% |
| organic-search | 41 | R33,329 | 28.6% |
| direct | 35 | R25,014 | 21.5% |
| email-klaviyo | 7 | R7,378 | 6.3% |
| ai-assistants | 3 | R3,515 | 3.0% |
| google-unclassified | 5 | R3,340 | 2.9% |
| unknown | 3 | R2,144 | 1.8% |
| referral | 4 | R1,564 | 1.3% |
| other | 2 | R801 | 0.7% |
| google-paid | 0 | R0 | 0.0% |
| meta-paid | 0 | R0 | 0.0% |
| tiktok-paid | 0 | R0 | 0.0% |
| other-paid | 0 | R0 | 0.0% |

## Who finds the customers — FIRST CLICK
| Channel | Orders | Revenue (incl VAT) | Share |
|---|---|---|---|
| google-free-listings | 95 | R43,963 | 37.7% |
| organic-search | 49 | R37,723 | 32.4% |
| direct | 24 | R21,030 | 18.1% |
| ai-assistants | 6 | R6,235 | 5.4% |
| email-klaviyo | 6 | R4,994 | 4.3% |
| unknown | 3 | R2,144 | 1.8% |
| other | 1 | R401 | 0.3% |

## Email (Klaviyo, 30d)
- Flows: R7,006 · Campaigns: R5,278 · Total: R12,284 (10.5% of revenue; target 25%)

## Attribution hygiene — GA4 join readiness
- **52%** of orders (96/184) carry a UTM/click-id stamp that can be joined to a GA4 session (target ≥50%, ideally ≥70%).
- Ambiguous / unreconcilable: 47 orders worth **R32,062** (27.5% of revenue) sit in direct/unknown/unclassified.
- Lift this by completing the UTM cleanup (Klaviyo auto-tagging + Google auto-tagging + Meta URL params) — see `codex-attribution-cleanup.md`.

## Flags
🔴 PAID IS UNDERWATER: paid-attributed revenue R3,340 yields ~R958 gross profit vs R19,500/mo ads+agency cost.
🟠 Email is 10.5% of revenue (target 25%).
🔴 ONLINE NET CONTRIBUTION NEGATIVE: R-3,072.

*Costs are monthly figures from data/business_config.yml applied to a 30-day window — update that file when spend changes. 'google-unclassified' may contain auto-tagged (gclid) paid traffic; require utm tagging on all ads to split it.*
