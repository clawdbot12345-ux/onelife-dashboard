# Codex task: Omni feed round 2 — the last 3 things to light up every tab

Date: 2026-06-15 · Follow-up to the feed expansion (thank you — stock listings, supplier
profitability, slow-movers, PO generator, transactions + the quality audit all landed and
are consumed).
Unblocks: live Products, Categories, Stock Intelligence, and Suppliers tabs + store
transaction/basket metrics.

## What's now live (consumed by scripts/omni_dashboard_sync.py)
Stores (revenue + GP), and a live per-branch stock summary in `omni_sync`
(CEN 5,365 in-stock SKUs / R3.46M sell · EDN 2,969 / R1.53M · GVS 2,215 / R1.04M;
6,019 unique SKUs in stock).

## The 3 gaps blocking the remaining tabs

1. **Per-SKU cost / average cost** — biggest unlock.
   The `ANA_Stock Listing_*` reports expose `selling_price_excl` + `available` but **no
   cost**, so we can't compute margin, stock-value-at-cost, the ≥40% "double down" set, or
   the margin-warning / capital-trapped signals without erasing the existing real values.
   Please add average (or last) cost per SKU — either add a `cost_excl` / `average_cost`
   column to the three `ANA_Stock Listing_*` reports, or expose a `Stock Valuation with
   Cost` report (`stock_code, available, average_cost_excl, selling_price_excl`).
   → Unblocks: Products (`cost_price`, `margin_pct`, `stock_value_cost`), Categories
   (`avg_margin_pct`, `stock_value_cost`), Stock Intelligence, Capital Trapped.

2. **MTD per-branch transaction counts (incl. HO).**
   `Engine Daily Branch Transactions` currently sources the `OL_*_Busy Times_Yesterday`
   reports — single day, and HO came back 0 (a no-sync day). Switch/augment it to the
   month-to-date sources that already exist: `OL_HO_Busy Times_MTD`,
   `OL_EDN_Busy Times_MTD`, `OL_GVS_Busy Times_MTD`, emitting cumulative
   `transaction_count` (+ avg basket) per branch for the period.
   → Unblocks: store-card Transactions + Avg Basket (currently shown as GP instead).

3. **Purchase Orders + Goods-Received (GRV) by supplier**, plus a supplier master.
   The Suppliers tab needs PO value, received value, fill %, and outstanding — none are in
   the sales/GP feed. Also, `Supplier Profitability` rows have no `supplier_#`, so they
   can't be aggregated by supplier. Please expose: a PO/GRV report
   (`supplier_#, po_value_excl, grv_value_excl, fill_pct, outstanding_excl, order_count`)
   and a supplier master (`supplier_#, supplier_name`).
   → Unblocks: Suppliers tab (fill rate, outstanding, PO value) + supplier-level rollups.

## Output contract (unchanged)
Same as before: `data/omni/daily/{YYYY-MM-DD}_{slug}.json`, top-level key = slug, value =
list of row dicts. Add the report names to `P0_REPORTS` in `fetch_omni.py`; no `index.html`
work needed — Claude extends `omni_dashboard_sync.py` to consume them.

## Definition of done
Daily files present for: a cost-bearing stock report, MTD per-branch transactions (incl.
HO), and a PO/GRV report + supplier master. Then Claude wires Products, Categories, Stock
Intelligence, and Suppliers to live Omni in one pass.
