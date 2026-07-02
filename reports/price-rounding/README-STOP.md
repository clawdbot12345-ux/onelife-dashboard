# Price rounding — One Life store: OWNER APPROVED ✅ (2026-07-02)

Update: the owner confirmed the One Life price round-down is an intentional,
separately-approved initiative ("we also did a price round down on Onelife").
The earlier STOP in this file is retracted.

Execution: `plan-2026-07-02T125406Z.csv` (2,203 variants, floor-to-rand) is
applied by the **Vivid Price Rounding** workflow via scripts/vivid_ops.py
mode `apply_prices` with a drift check: a variant is only changed if its live
price still equals the plan's `old_price`; drifted/missing rows are logged and
skipped. Result log: `reports/price-rounding/apply-result.json`.
Rollback: the plan's old_price column IS the rollback map.
