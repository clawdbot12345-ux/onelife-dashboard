# Codex task: Vivid Health revenue & GP extract

Unblocks: T1b scoreboard (owner target: Vivid R500k+/mo combined channels — current share unknown).

From your cached full extract of `ANA_Most Popular Products GP` (11,069 rows — and `ANA_Sales Analysis` 123,869 rows if needed): identify Vivid Health items (stock_description/line_item_description containing "VIVID", or the Vivid supplier_# — verify which supplier code is the in-house one) and compute:

1. Vivid total: quantity, value_excl_after_discount, gross_profit, GP% — overall and **per company_branch_code (HO/EDN/GVS)**
2. Vivid share of each branch's sales (vs branch totals in `data/omni/reports-v2/branch-sales-summary.json`)
3. Top 20 Vivid SKUs by revenue and by GP
4. Note the period the saved report covers if determinable (the catalog flags these reports as "saved default period")

Write results to `data/omni/reports-v2/vivid-summary.json` + a short human-readable `vivid-summary.md`, commit to `claude/end-to-end-goal-tdcj0f`, push. No customer fields needed; redact if any appear.
