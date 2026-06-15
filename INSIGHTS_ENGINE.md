# Onelife — from dashboard to decision cockpit (insights → foresights → actions)

_The north star: a world-class interactive retail-intelligence cockpit that doesn't just
report what happened, but tells you **what to market** and **what to do next** — with the
story and the Rand impact behind each call._

## The four levels (where we are → where we're going)

1. **Descriptive — "what happened."** ✅ Mostly built. Live store revenue/GP/transactions/
   basket (Omni), Shopify, Klaviyo. This is the current dashboard.
2. **Diagnostic — "why."** ⏳ Partly there (Signals: dead stock, supplier issues, basket
   gap). Deepen once cost + GRV land.
3. **Predictive (foresight) — "what's coming."** 🔜 Stockout forecasts, replenishment
   timing, demand trend by condition/season, supplier-risk, churn risk.
4. **Prescriptive — "what to do."** 🎯 The destination: a ranked, dated action list and a
   "what to market" list, each with the reason and the R-impact.

## Dual purpose (exactly what you asked for)

### A. "What to Market" — feeds the marketing engine automatically
A single ranked list of products to push this week, scored by fusing the live data:

`score = margin × stock-cover × velocity × season/condition fit × (online-vs-store gap)`

- **High margin + well stocked + on-trend/seasonal** → push hard (the "double-down" set).
- **Selling in-store but weak online** → make it the week's online hero / WhatsApp deal.
- **Condition-aligned** (winter immunity, sleep/magnesium, GLP-1) → routes to the matching
  TikTok/Reel pillar, email segment, and VIP WhatsApp broadcast.
- **Avoid:** never feature anything low-stock at the target branch (uses live per-branch
  stock) or below-margin.

Output plugs straight into the content engine: the week's **Monday Hero / Wednesday Vivid /
Thursday Bundle**, the VIP WhatsApp deal, the in-store shelf-talker — all chosen by data,
not guesswork. Codex renders the creative; I write the copy/targeting; you approve.

### B. "Actions for You" — your weekly executive briefing
A prioritised list, each item in one line: **Insight → Foresight → Action → R-impact.**
Examples (live-data driven):
- _"Edenvale basket is R396 vs Centurion R623 (R227 gap). Action: till-point 'complete your
  protocol' upsell + consultant prompt. Impact: +R50 basket × 460 tx ≈ +R23k/mo."_
- _"MAG 7/87 reordered 10× with 86 units sitting (R-cost trapped). Action: pause reorder,
  bundle to clear."_
- _"DSI fill-rate low on R451k ordered. Action: supplier call this week."_
- _(foresight)_ _"Vitamin D / immunity demand rising into winter + low stock at GVS. Action:
  reorder now + feature; pre-load the WhatsApp/TikTok immunity week."_

## How it's wired (the moat)
Omni (stock, margin, velocity, dead stock, suppliers) + Shopify (online demand) + Klaviyo
(engagement, segments) → the cockpit's scoring + an **AI-written briefing** (Claude) that
turns numbers into stories and actions, refreshed daily. This is the dual-use asset: it runs
the marketing engine *and* gives you the foresight/action layer — something no SA health
retailer has.

## Build sequence
1. **Unblock cost** (Omni desktop report — see `codex-queue/2026-06-15_omni-cost-report-REQUEST.md`).
   Lifts margin coverage 72% → ~100%.
2. **Finish the descriptive layer live** — Products, Categories, Stock-Intelligence,
   Suppliers off Omni (one clean pass; auto-upgrades as cost lands).
3. **Build the "What to Market" engine** — the scored list, wired into the content calendar.
4. **Build "Actions for You"** — the AI executive briefing (insight→foresight→action→impact),
   daily.
5. **Foresights** — stockout/replenishment/demand-trend/churn models on the accumulating
   daily history.

## What world-class looks like (researched, 2025/26) — the standard we build to
Leading retail/marketing BI (Tableau+Einstein, Power BI+Copilot, Looker+Gemini, Improvado)
converges on five things — and one anti-pattern:
- **A few hero KPIs, not 30.** The #1 failure mode is a cluttered board nobody reads. Start
  with 3–5 decision KPIs per view, drill-down on demand.
- **Automated anomaly detection** — outliers flagged *without* hand-set rules (sales/margin
  dips, conversion drops, stockouts on top sellers, return spikes, supplier-fill drops,
  "spend without clicks", YoY drop >30%).
- **Prescriptive, not just descriptive** — not "churn risk high" but "do X → est. +R/▲%".
- **Omnichannel, real-time** — POS + online + marketing fused (real-time personalization
  lifted AOV 259% in Adidas' 2025 case).
- **Role-based + interactive** — filter by store/category/period; an exec view vs an ops view.

**Retail KPIs we'll add** (beyond revenue): **GMROI**, **sell-through rate**, **inventory
turnover**, sales-per-store/sqm, basket analysis, gross-margin-return, and customer
**cohort/LTV** (from Shopify+Klaviyo). GMROI/turnover/sell-through need cost + GRV — the
exact Omni reports now requested.

## Data sources & coverage (do we have everything?)
| Source | Covers | Status |
|---|---|---|
| **Omni** (in-store ERP) | store sales, GP, transactions/basket, per-branch stock, suppliers, POs, dead stock | ✅ live daily feed; **needs cost + GRV (+returns)** from Johann to be 100% |
| **Shopify** | online orders, products, inventory, customers | ✅ reachable (Admin API / MCP); wire product-level online + cohort/LTV |
| **Klaviyo** | email/SMS, flows, campaigns, segments, engagement | ✅ live |
| **GA4** | web traffic, acquisition channel, on-site funnel, source/medium | ⏳ **need access** — a service account / Data API key (as a GitHub secret), or the BigQuery export |
| **Social** (TikTok/IG/FB) | reach, followers, engagement | ⚠️ manual today; APIs later |
| **External** | seasonality, SA holidays, weather, search trends | ➕ optional, layer in for demand foresight |

### What's needed to "build everything"
- **From Johann/IT (Omni):** the 3 reports in `codex-queue/2026-06-15_omni-cost-report-REQUEST.md`
  (per-SKU cost ✅critical, GRV, returns). That completes the Omni side.
- **From you:** **GA4 access** (service-account JSON / Data API, or BigQuery export) so we
  wire web acquisition + funnel + true online attribution; and confirm **Shopify Admin API**
  credentials for the automated daily pull (we have interactive access via MCP already).
- **Already in hand:** Omni daily feed, Shopify (MCP), Klaviyo (live).
