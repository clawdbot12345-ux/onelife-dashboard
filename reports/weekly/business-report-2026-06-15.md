# One Life Online — Weekly Business Report (2026-06-15)

Period: last 30 days · Source: Shopify order journeys (own attribution),
Klaviyo values reports, data/business_config.yml.

## P&L (online, 30 days)
| Line | Amount |
|---|---|
| Revenue incl VAT | R119,685 (187 paid orders, AOV R640) |
| Revenue ex VAT | R104,074 |
| Gross profit @33% | R34,345 |
| Delivery | −R17,000 (R91/order) |
| Ad spend (G/M/T) | −R14,000 |
| Agency | −R5,500 |
| **Net contribution** | **R-2,155** |

Break-even ROAS (on incl-VAT revenue, before delivery/agency): **3.48**

## Where the money actually comes from — LAST CLICK
| Channel | Orders | Revenue (incl VAT) | Share |
|---|---|---|---|
| google-free-listings | 87 | R41,877 | 35.0% |
| organic-search | 42 | R34,083 | 28.5% |
| direct | 34 | R25,559 | 21.4% |
| email-klaviyo | 7 | R5,890 | 4.9% |
| google-unclassified | 5 | R4,521 | 3.8% |
| referral | 6 | R2,641 | 2.2% |
| ai-assistants | 2 | R2,569 | 2.1% |
| unknown | 3 | R2,144 | 1.8% |
| other | 1 | R401 | 0.3% |
| google-paid | 0 | R0 | 0.0% |
| meta-paid | 0 | R0 | 0.0% |
| tiktok-paid | 0 | R0 | 0.0% |
| other-paid | 0 | R0 | 0.0% |

## Who finds the customers — FIRST CLICK
| Channel | Orders | Revenue (incl VAT) | Share |
|---|---|---|---|
| google-free-listings | 99 | R47,436 | 39.6% |
| organic-search | 46 | R37,050 | 31.0% |
| direct | 27 | R24,073 | 20.1% |
| ai-assistants | 7 | R6,188 | 5.2% |
| email-klaviyo | 4 | R2,394 | 2.0% |
| unknown | 3 | R2,144 | 1.8% |
| other | 1 | R401 | 0.3% |

## Email (Klaviyo, 30d)
- Flows: R10,566 · Campaigns: R9,176 · Total: R19,741 (16.5% of revenue; target 25%)

## Attribution hygiene — GA4 join readiness
- **52%** of orders (97/187) carry a UTM/click-id stamp that can be joined to a GA4 session (target ≥50%, ideally ≥70%).
- Ambiguous / unreconcilable: 48 orders worth **R34,866** (29.1% of revenue) sit in direct/unknown/unclassified.
- Lift this by completing the UTM cleanup (Klaviyo auto-tagging + Google auto-tagging + Meta URL params) — see `codex-attribution-cleanup.md`.

## Flags
🔴 PAID IS UNDERWATER: paid-attributed revenue R4,521 yields ~R1,297 gross profit vs R19,500/mo ads+agency cost.
🔴 ONLINE NET CONTRIBUTION NEGATIVE: R-2,155.

*Costs are monthly figures from data/business_config.yml applied to a 30-day window — update that file when spend changes. 'google-unclassified' may contain auto-tagged (gclid) paid traffic; require utm tagging on all ads to split it.*
