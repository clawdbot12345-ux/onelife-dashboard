# Codex task: confirm live cost is flowing, then Claude wires the tabs

Date: 2026-06-16
Status: Johann fixed it — the *analytic* API operator simply lacked "Stock Cost Price"
view rights in Omni. He enabled it; `unit_cost_price` now populates for all items on
`ANA_Stock Listing_CEN/_EDN/_GVS`. (No report change / no OWS restart. And note for future:
Omni's REST API returns whatever columns are in the report layout *that the operator has
rights to see* — there's no separate "serialisation" flag.)

## Do
1. **Re-pull** `ANA_Stock Listing_CEN/_EDN/_GVS`. Your fetcher already detects
   `unit_cost_price` (it's in the accepted field list), so it should populate now.
2. In `engine_stock_cost_by_sku` / `engine_stock_listing_with_derived_cost`: confirm the
   real cost is now used — `cost_source = "omni_report"` for the populated rows, derived
   only as fallback. Key by `stock_code` (cost is company-wide / "Latest" valuation).
3. **Confirm the cost basis is excl VAT** (selling price is excl; cost should match — verify
   against one item's GP: selling_excl − cost_excl ≈ realized GP from Most Popular Products).
4. Report: the % of stock SKUs now with real cost (`omni_report`), and the exact emitted
   field name, then commit the refreshed daily JSON.

## Then (Claude)
Once the committed `data/omni/daily/*` carry real cost, Claude wires **Products,
Categories, and Stock-Intelligence** live at ~100% coverage — real margins, stock value at
cost, the high-margin "double-down" set, and dead-stock valuation — using the same sync
pattern already shipped for the stores layer. No further work needed from Codex on cost.
