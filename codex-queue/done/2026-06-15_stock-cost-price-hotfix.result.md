# Codex result: stock cost_price hotfix

Date: 2026-06-15
Branch: `claude/end-to-end-goal-tdcj0f`

## Requested

Johann added `Cost Price` to the end of:

- `ANA_Stock Listing_CEN`
- `ANA_Stock Listing_EDN`
- `ANA_Stock Listing_GVS`

Codex needed to re-pull the reports, confirm the slugged field, prefer real cost over sales-derived cost, and commit updated daily JSON.

## Pull result

I re-pulled all three stock listing reports twice:

- Normal JSON pull through `fetch_omni.py`
- Cache-busted/no-cache pull with a timestamp query parameter

The API still returns the old 10-column schema:

`stock_code, stock_description, bar_code, unit_of_measure, pack, selling_price_excl, available, product_group, stock_category, supplier_#`

No `cost_price`, `cost_price_excl`, `average_cost`, or other cost-like field is currently present in the API response.

## Pipeline change

`scripts/fetch_omni.py` now supports Johann's new column when it appears:

- It looks for `cost_price` first.
- It also tolerates `cost_price_excl`, `average_cost`, and `average_cost_excl`.
- If a real positive cost is present, it wins and emits `cost_source = "omni_report"`.
- If cost is blank or `0`, it falls back to the GP-derived cost.
- If neither exists, cost fields remain `null` and `cost_source = "unavailable_from_current_omni_reports"`.

## Emitted field name

Canonical cost field for Claude to wire:

`cost_price`

Compatibility alias still emitted:

`average_cost_excl`

Both are excl-VAT cost values in the derived files. Current fallback costs are derived from `value_excl_after_discount - gross_profit`, so they are definitely excl VAT. The real Omni `Cost Price` basis cannot be proven until the API returns the column, but the pipeline treats it as excl VAT to reconcile with `selling_price_excl`.

## Current generated coverage

After the full fetch:

- `engine_stock_cost_by_sku`: 6,113 rows
  - `sales_gross_profit_average`: 6,113
  - `omni_report`: 0, because `cost_price` is not in the API response yet
- `engine_stock_listing_with_derived_cost`: 25,321 rows
  - `sales_gross_profit_average`: 18,306
  - `unavailable_from_current_omni_reports`: 7,015
  - `omni_report`: 0

## Validation

- `python3 -m py_compile scripts/fetch_omni.py` passed.
- Full local fetch with `OMNI_REPORT_URL` completed.
- Stock listing schema was inspected after the pull.
- History duplicate checks still pass.

## Next action for Johann / Claude

Johann needs to confirm the edited report definition is published to the report API, not only visible in the report builder/UI. Once the API returns `cost_price`, the existing code will switch those rows to `cost_source = "omni_report"` automatically on the next daily pull.
