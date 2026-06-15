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
