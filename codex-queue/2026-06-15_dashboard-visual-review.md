# Codex task: visual QA review of the dashboard (PR #19)

Date: 2026-06-15
Branch to review: **`claude/onelife-marketing-strategy-9zty6c`** (PR #19) — check it out and
open `index.html` in a real browser (it's self-contained; Chart.js loads from CDN, so allow
network). The cloud Claude sandbox can't render a browser — that's why this is for you.

## Context — what's new since the live store layer
All driven by `DASHBOARD_DATA` blocks built by these scripts (data is real Omni):
`omni_dashboard_sync.py` (stores), `build_what_to_market.py`, `build_actions.py`,
`build_stock_moves.py`. New UI: the Onelife logo in the topbar, two new tabs, and two new
Signals sections.

## Please visually verify (report a punch-list)
1. **Topbar / logo** — the Onelife logo (white chip, base64 PNG) renders crisply, correct
   aspect ratio, not stretched/cut; "Retail Intelligence" subtitle reads on the dark bar.
2. **Overview** — store cards show Revenue / Transactions / Avg Basket / GP Margin with live
   numbers; the two GP KPI cards render; hover lift/shadow works; revenue chart renders.
3. **🧭 Actions for You** (new tab, after Overview) — 6 story cards render with kind badges
   (Insight/Foresight/Hindsight/Action), accent stripes, **bold** rendered (not literal
   `**`), and the green R-impact pills. Text legible, no overflow.
4. **🎯 What to Market** (new tab) — the **Margin × Demand bubble chart** renders (axes
   labelled, tooltips show product name on hover), the **condition filter chips** actually
   filter the table on click, and the in-row **margin bars** display.
5. **⚡ Signals** — two new sections render with populated tables:
   **🔀 Stock in the wrong store** and **🔁 Reordering but not selling**.
6. **General** — open the browser console and report **any JS errors**; check **mobile /
   narrow-width** layout (tables scroll, cards stack, topbar wraps cleanly); check colour
   contrast and that nothing overlaps.
7. **Data sanity** — spot-check that the numbers in the new panels look plausible (e.g.,
   What-to-Market margins, Actions impacts, cross-store GP).

## How to report
- Capture 3–4 screenshots (Overview, Actions, What to Market, Signals new sections) if you
  can, and a written punch-list of issues by severity.
- If a fix is small and unambiguous (CSS overflow, a contrast tweak, a chart option), push
  it to this branch and note it. For anything structural or subjective (layout/brand
  direction), just report and let Claude/the owner decide.

## Notes
- Brand accent is currently `#6c63ff` (purple) + `#22c55e` (green). If the logo's exact
  brand colours differ, suggest the hex values rather than changing wholesale.
- Don't touch the `DASHBOARD_DATA` numbers or the build scripts' logic — this is a UI/visual
  review.
