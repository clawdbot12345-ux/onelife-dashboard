# Codex result: Omni feed round 2

Date: 2026-06-15
Branch: `claude/end-to-end-goal-tdcj0f`

## Done

- Expanded `scripts/fetch_omni.py` with new raw daily pulls:
  - `Stock Valuation`
  - `Purchase Orders`
  - `Stock Price List with Supplier Price Comparison`
  - `Stock Reorder Report - Daily Material Requirements`
  - `Supplier Payment Schedule`
  - `OL_HO_Busy Times_MTD`
  - `OL_EDN_Busy Times_MTD`
  - `OL_GVS_Busy Times_MTD`
- Added derived daily outputs:
  - `engine_stock_cost_by_sku`
  - `engine_stock_listing_with_derived_cost`
  - `engine_mtd_branch_transactions`
  - `engine_supplier_master`
  - `engine_supplier_po_grv`
- Changed turnover history maintenance from append-only to branch/date upsert so same-day partial turnover values can be corrected by later runs.

## Generated files

- `data/omni/daily/2026-06-15_engine-stock-cost-by-sku.json` - 6,110 rows
- `data/omni/daily/2026-06-15_engine-stock-listing-with-derived-cost.json` - 25,321 rows
- `data/omni/daily/2026-06-15_engine-mtd-branch-transactions.json` - 3 rows
- `data/omni/daily/2026-06-15_engine-supplier-master.json` - 310 rows
- `data/omni/daily/2026-06-15_engine-supplier-po-grv.json` - 221 rows
- `data/omni/daily/2026-06-15_purchase-orders.json` - 3,001 rows
- `data/omni/daily/2026-06-15_supplier-payment-schedule.json` - 97 rows
- `data/omni/daily/2026-06-15_stock-valuation.json` - 10,778 rows
- `data/omni/daily/2026-06-15_stock-price-list-with-supplier-price-comparison.json` - 8,441 rows
- `data/omni/daily/2026-06-15_stock-reorder-report-daily-material-requirements.json` - 203 rows

## MTD branch transactions

`engine_mtd_branch_transactions` now uses the live branch MTD busy-time reports:

| branch | transactions | value_excl_after_discount | avg basket ex VAT |
|---|---:|---:|---:|
| `HO` | 1,176 | 730,889.79 | 621.50 |
| `EDN` | 455 | 178,090.93 | 391.41 |
| `GVS` | 370 | 170,470.97 | 460.73 |

Period fields are `period_start=2026-06-01`, `period_end=2026-06-15`, `period_type=month_to_date`.

## Cost coverage

No true inventory average-cost report is exposed in the current Omni catalog. Live probes found:

- `Stock Valuation` exists but has only `warehouse_code`, `stock_code`, `stock_description`, `level`.
- Guessed cost-bearing report names such as `Stock Valuation with Cost`, `Stock Valuation with Cost Price`, `Stock Listing with Cost`, and `Stock Average Cost` returned 500 or timed out.

To unblock Claude without fabricating values, `engine_stock_cost_by_sku` derives `average_cost_excl` from real sales GP:

`average_cost_excl = (value_excl_after_discount - gross_profit) / quantity`

This covers 6,110 sold SKUs from `ANA_Most Popular Products GP`. `engine_stock_listing_with_derived_cost` joins that cost onto branch stock listings and leaves cost fields `null` with `cost_source=unavailable_from_current_omni_reports` where no sales-derived cost exists.

## Supplier / PO / GRV coverage

- `Purchase Orders` is live and now aggregated by `supplier_account_no` into `engine_supplier_po_grv`.
- Supplier master is built from stock supplier codes, supplier price-list names, reorder supplier names, purchase-order supplier accounts, slow-mover supplier codes, and payment-schedule names.
- `engine_supplier_po_grv` contains real `po_value_excl`, `order_count`, and `ordered_qty` for PO rows.
- Omni did not expose a GRV-by-supplier report in the current catalog; `grv_value_excl` and `fill_pct` are therefore left `null` with an explicit coverage note.
- `Supplier Payment Schedule` is included for real payables/outstanding values. These rows carry `outstanding_incl` and derived `outstanding_excl`.

## Validation

- `python3 -m py_compile scripts/fetch_omni.py` passed.
- `.github/workflows/daily-refresh.yml` parsed successfully.
- Full local fetch with `OMNI_REPORT_URL` completed.
- History duplicate checks passed:
  - `data/omni/daily_turnover_history.csv`: 43 rows, 0 duplicate branch/date keys.
  - `data/omni/daily_branch_transactions_history.csv`: 3 rows, 0 duplicate branch/date keys.
- Repeat upsert simulation against the generated turnover JSON returned 0 pending updates.

## Notes for Claude

- Use `engine_mtd_branch_transactions` for store-card Transactions and Avg Basket.
- Use `engine_stock_listing_with_derived_cost` for stock/capital views, but treat `cost_source` carefully.
- Use `engine_supplier_po_grv` for live PO value/order count and payables; do not treat null GRV/fill fields as zero.
