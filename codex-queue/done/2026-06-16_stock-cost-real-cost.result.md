# Codex result: Omni stock cost now live

Date: 2026-06-16
Branch: `claude/end-to-end-goal-tdcj0f`

## Done

- Re-pulled `ANA_Stock Listing_CEN`, `ANA_Stock Listing_EDN`, and `ANA_Stock Listing_GVS`.
- Confirmed the serialized raw Omni cost field is now:
  - `unit_cost_price`
- Confirmed the canonical emitted engine cost field remains:
  - `cost_price`
- Regenerated:
  - `data/omni/daily/2026-06-16_engine-stock-cost-by-sku.json`
  - `data/omni/daily/2026-06-16_engine-stock-listing-with-derived-cost.json`

## Coverage

Raw stock listings:

- `ANA_Stock Listing_CEN`: 8,427 / 8,439 rows with `unit_cost_price` > 0 = 99.86%
- `ANA_Stock Listing_EDN`: 8,429 / 8,441 rows with `unit_cost_price` > 0 = 99.86%
- `ANA_Stock Listing_GVS`: 8,429 / 8,441 rows with `unit_cost_price` > 0 = 99.86%
- Unique stock-listing SKUs with real cost: 8,429 / 8,441 = 99.86%

Engine outputs:

- `engine_stock_cost_by_sku`: 8,446 rows
  - `omni_report`: 8,429 = 99.80%
  - `sales_gross_profit_average`: 17 = fallback only
  - duplicate `stock_code` keys: 0
- `engine_stock_listing_with_derived_cost`: 25,321 rows
  - `omni_report`: 25,285 = 99.86%
  - `sales_gross_profit_average`: 18 = fallback only
  - `unavailable_from_current_omni_reports`: 18

## Cost Basis Check

Sample item:

- Stock code: `6007732017140`
- Description: `TUMMY FLUSH 250ML`
- Selling price excl VAT: `65.21`
- Raw `unit_cost_price`: `47.25`
- Selling excl - cost excl: `17.96`
- Realized GP per unit from `ANA_Most Popular Products GP`: `17.96`

This reconciles exactly on an excl-VAT basis.

## Implementation Notes

- Real Omni report cost is used first with `cost_source = "omni_report"` and `cost_basis = "latest"`.
- Sales GP-derived cost is now only the fallback when `unit_cost_price` is blank or zero.
- The SKU cost engine is keyed by `stock_code`; branch observations for the same SKU had no differing cost values in this pull.
