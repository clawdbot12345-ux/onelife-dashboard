# One Life Online — Weekly Business Report (2026-06-29)

Period: last 30 days · Source: Shopify order journeys (own attribution),
Klaviyo values reports, data/business_config.yml.

## P&L (online, 30 days)
| Line | Amount |
|---|---|
| Revenue incl VAT | R125,642 (198 paid orders, AOV R635) |
| Revenue ex VAT | R109,254 |
| Gross profit @33% | R36,054 |
| Delivery | −R17,000 (R86/order) |
| Ad spend (G/M/T) | −R14,000 |
| Agency | −R5,500 |
| **Net contribution** | **R-446** |

Break-even ROAS (on incl-VAT revenue, before delivery/agency): **3.48**

## Where the money actually comes from — LAST CLICK
| Channel | Orders | Revenue (incl VAT) | Share |
|---|---|---|---|
| google-free-listings | 88 | R41,467 | 33.0% |
| organic-search | 43 | R35,981 | 28.6% |
| direct | 38 | R24,391 | 19.4% |
| email-klaviyo | 10 | R9,159 | 7.3% |
| referral | 7 | R5,774 | 4.6% |
| ai-assistants | 3 | R3,488 | 2.8% |
| google-unclassified | 5 | R3,252 | 2.6% |
| unknown | 2 | R1,329 | 1.1% |
| other | 2 | R801 | 0.6% |
| google-paid | 0 | R0 | 0.0% |
| meta-paid | 0 | R0 | 0.0% |
| tiktok-paid | 0 | R0 | 0.0% |
| other-paid | 0 | R0 | 0.0% |

## Who finds the customers — FIRST CLICK
| Channel | Orders | Revenue (incl VAT) | Share |
|---|---|---|---|
| google-free-listings | 100 | R47,673 | 37.9% |
| organic-search | 52 | R40,351 | 32.1% |
| direct | 29 | R22,988 | 18.3% |
| ai-assistants | 5 | R5,932 | 4.7% |
| email-klaviyo | 7 | R5,864 | 4.7% |
| unknown | 2 | R1,329 | 1.1% |
| google-unclassified | 1 | R880 | 0.7% |
| other | 1 | R401 | 0.3% |
| referral | 1 | R224 | 0.2% |

## Email (Klaviyo, 30d)
- Flows: R13,082 · Campaigns: R8,644 · Total: R21,726 (17.3% of revenue; target 25%)

## Attribution hygiene — GA4 join readiness
- **52%** of orders (103/198) carry a UTM/click-id stamp that can be joined to a GA4 session (target ≥50%, ideally ≥70%).
- Ambiguous / unreconcilable: 52 orders worth **R34,745** (27.7% of revenue) sit in direct/unknown/unclassified.
- Lift this by completing the UTM cleanup (Klaviyo auto-tagging + Google auto-tagging + Meta URL params) — see `codex-attribution-cleanup.md`.

## Flags
🔴 PAID IS UNDERWATER: paid-attributed revenue R3,252 yields ~R933 gross profit vs R19,500/mo ads+agency cost.
🔴 ONLINE NET CONTRIBUTION NEGATIVE: R-446.

*Costs are monthly figures from data/business_config.yml applied to a 30-day window — update that file when spend changes. 'google-unclassified' may contain auto-tagged (gclid) paid traffic; require utm tagging on all ads to split it.*
