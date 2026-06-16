# Codex result: stock cost key dump

Date: 2026-06-15
Branch: `claude/end-to-end-goal-tdcj0f`

## Done

- Cache-busted and re-pulled:
  - `ANA_Stock Listing_CEN`
  - `ANA_Stock Listing_EDN`
  - `ANA_Stock Listing_GVS`
- Wrote the serialized key dump to:
  - `data/omni/probe/stock-listing-cost-key-dump-2026-06-15.json`
- Updated `scripts/fetch_omni.py` to detect real cost under any of:
  - `cost_price`
  - `unit_cost_price`
  - `costprice`
  - `unit_cost`
  - `cost_excl`
  - plus existing tolerant aliases `cost_price_excl`, `average_cost`, `average_cost_excl`
- When real Omni cost appears, the pipeline emits:
  - `cost_price`
  - `cost_source = "omni_report"`
  - `cost_basis = "latest"`

## API result

The API still returns the old schema for all three stock listing reports.

Serialized keys:

`stock_code, stock_description, bar_code, unit_of_measure, pack, selling_price_excl, available, product_group, stock_category, supplier_#`

Detected cost keys:

- `ANA_Stock Listing_CEN`: none
- `ANA_Stock Listing_EDN`: none
- `ANA_Stock Listing_GVS`: none

This confirms the cost field is not currently serialized by the Omni web/report API. It is likely a stale report-server definition or a layout-only/report-preview field rather than a data column in the API response.

## Current emitted cost field

Exact field for Claude to consume remains:

`cost_price`

Current generated source coverage:

- `engine_stock_cost_by_sku`: 6,114 rows, all `sales_gross_profit_average`
- `engine_stock_listing_with_derived_cost`: 25,321 rows
  - `sales_gross_profit_average`: 18,309
  - `unavailable_from_current_omni_reports`: 7,012
  - `omni_report`: 0

## Human action needed

Ask Johann to re-save/publish the report definitions and restart or recycle the Omni web/report service. Also confirm `Cost Price` / `Unit Cost Price` is added as a serialized data column, not only a print/layout preview field.

Once the API serializes the field, the next daily pull will switch those rows to `cost_source = "omni_report"` automatically.
