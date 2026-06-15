# Codex task: re-pull stock cost (field added; verify API serialization)

Date: 2026-06-15 (v2) · Supersedes the cost portion of the earlier request.

## Status
Johann added a cost column to `ANA_Stock Listing_CEN/_EDN/_GVS`. He tried two field names —
**"Unit Cost Price"** and **"Cost Price"** — both show the same value in the desktop preview.
Your last pull still returned the OLD schema (no cost field), and client-side cache-busting
didn't change it → the Omni **web/report service is serving a stale report definition**, or
the cost is a *layout/display* field that isn't in the report's serialized **data output**.

## Do
1. **Re-pull** `ANA_Stock Listing_CEN/_EDN/_GVS` (cache-busted/no-cache).
2. **Log the full set of JSON keys** for one row of each report to `data/omni/probe/` so we can
   see exactly what the API serializes now. Detect the cost field under any of these slugs:
   `cost_price`, `unit_cost_price`, `costprice`, `unit_cost`, `cost_excl`.
3. **If the cost field now appears:** make it canonical. Prefer real cost
   (`cost_source="omni_report"`); fall back to GP-derived only when it's blank/0. Recompute
   `engine_stock_cost_by_sku` (key by `stock_code` — cost is **company-wide / "Latest"**
   valuation per Omni Stock Options, so one value per SKU; tag `cost_basis:"latest"`) and
   `engine_stock_listing_with_derived_cost`. Confirm the cost is **excl VAT**.
4. **If it STILL doesn't appear:** that confirms a server-side issue, not our code. Report
   back so the human can act:
   - re-save the named `ANA_Stock Listing_*` reports, AND
   - restart the Omni web/report service (or clear its report cache), AND
   - ensure the cost is part of the report's **data/query columns**, not only the print layout.
5. Commit the updated daily JSON (+ probe key-dump) and **tell Claude the exact cost field
   name** you ended up with.

## Definition of done
Either: real cost flowing (coverage ~100%, `cost_source="omni_report"`) and field name
reported — or a clear key-dump proving the API still omits it, so the server-side fix can be
done. Dashboard auto-upgrades from the 72% derived baseline the moment real cost lands.
