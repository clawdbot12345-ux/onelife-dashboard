# Codex task: full visual QA + polish pass (dashboard complete)

Date: 2026-06-16
Branch: **`claude/onelife-marketing-strategy-9zty6c`** (PR #19). Check it out, open
`index.html` in a real browser (Chart.js loads from CDN — allow network). The cloud
Claude sandbox can't render a browser, so the visual pass is yours.

## Context — every tab is now LIVE on real data
No more static March snapshot. Built by these scripts off the Omni/GA4/Klaviyo feeds:
`omni_dashboard_sync.py`, `build_stock_live.py`, `build_suppliers_live.py`, `build_ga4.py`,
`build_what_to_market.py`, `build_actions.py`, `build_stock_moves.py`.

- **Overview** — store revenue / transactions / avg basket / GP margin (live)
- **🧭 Actions for You** — 9 story cards (Insight/Foresight/Hindsight → Action → R-impact)
- **🎯 What to Market** — bubble map + condition filter chips + margin bars
- **Products / Categories / Stock-Intelligence** — live at real cost (99.8%)
- **Suppliers** — purchases + outstanding exposure + watch-list (just rebuilt)
- **Online → Web Analytics (GA4)** — channels, funnel, viewed-not-bought, geo, devices
- **Signals** — incl. 🔀 Stock in wrong store, 🔁 Reordering but not selling
- **Email Marketing (Klaviyo)** — live
- Onelife logo in the topbar (white chip)

## Part A — visual QA (report a punch-list + screenshots)
Open every tab and check:
1. No JS console errors anywhere.
2. All charts render (Overview revenue, store sparkline charts, What-to-Market bubble,
   GA4 channel + funnel, Suppliers outstanding bar, Categories bar, Klaviyo charts).
3. The new/rebuilt tabs look right: Actions cards (bold renders, not literal `**`),
   What to Market (filter chips actually filter, margin bars show), Suppliers (new
   columns sort, watch-list cards), GA4 section (tables populate, viewed-not-bought).
4. **Mobile / narrow width:** tables scroll, cards stack, topbar wraps, logo not stretched.
5. Contrast/overlap; numbers look plausible.
Push small, unambiguous CSS fixes to the branch; report anything structural/subjective.

## Part B — polish to implement (if straightforward) or spec back
1. **KPI sparklines** — add a small inline trend (last ~14–30 days) under the Overview
   KPI cards where a daily series exists (store revenue from
   `data/omni/daily_turnover_history.csv` / `DASHBOARD_DATA.stores[*].daily_sales_excl`).
   Hindsight-at-a-glance. Keep it lightweight (Chart.js sparkline or inline SVG).
2. **Printable "Monday briefing"** — a print stylesheet (`@media print`) + a "Print / PDF"
   button on the **Actions for You** tab that outputs the 9 action cards (and optionally
   the What-to-Market top 10) as a clean one/two-pager. The existing
   `scripts/generate_pdf.js` (Puppeteer) can target it for the automated daily PDF too.
3. **Brand accent** — the dashboard accent is `#6c63ff` (purple) + `#22c55e` (green). If the
   Onelife logo's exact brand hues differ, suggest the precise hex values (don't change
   wholesale without sign-off).

## Notes
- **Node bump already done** by Claude (`daily-refresh.yml` → Node 24), so the deprecation
  warning is resolved — no action needed there.
- Don't change `DASHBOARD_DATA` numbers or the build-script logic — this is UI/visual only.
- Coordinate: if you implement a polish item, say so in your result note so Claude doesn't
  duplicate it.
