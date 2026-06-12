# Omni reports v2 catalog

Generated: `2026-06-12T18:13:08Z`.

Basis: Mac Mini cached full Omni HTTP extracts from 2026-06-06 to 2026-06-09, plus live parameter tests against `Sales Analysis Johann Custom` on 2026-06-12. Credentials are not included in any artifact.

## Best reports for the engine

| priority | report | rows | why it matters | key columns | sample |
|---|---|---:|---|---|---|
| P0 | `ANA_Sales Analysis` | 123869 | Best immediate per-branch/per-item sales source; no document_date. | `reference, stock_code, stock_description, quantity, value_excl_after_discount, value_excl_before_discount, company_branch_code, warehouse_code, supplier_#` | `data/omni/reports-v2/samples/ana-sales-analysis.sample.json` |
| P0 | `ANA_Most Popular Products GP` | 11069 | Product/branch sales with gross profit. | `gross_profit, quantity, stock_code, company_branch_code, line_item_description, value_excl_after_discount, supplier_#` | `data/omni/reports-v2/samples/ana-most-popular-products-gp.sample.json` |
| P0 | `ANA_Stock Listing_EDN` | 8432 | Edenvale stock on hand by SKU. | `stock_code, stock_description, bar_code, unit_of_measure, pack, selling_price_excl, available, product_group, stock_category, supplier_#` | `data/omni/reports-v2/samples/ana-stock-listing-edn.sample.json` |
| P0 | `ANA_Stock Listing_GVS` | 8432 | Glen Village stock on hand by SKU. | `stock_code, stock_description, bar_code, unit_of_measure, pack, selling_price_excl, available, product_group, stock_category, supplier_#` | `data/omni/reports-v2/samples/ana-stock-listing-gvs.sample.json` |
| P0 | `ANA_Stock Listing_CEN` | 8430 | Centurion stock on hand by SKU. | `stock_code, stock_description, bar_code, unit_of_measure, pack, selling_price_excl, available, product_group, stock_category, supplier_#` | `data/omni/reports-v2/samples/ana-stock-listing-cen.sample.json` |
| P0 | `Daily Turnover EDEN` | 9 | Edenvale dated daily sales and GP. | `document_date, value_excl_after_discount, gross_profit` | `data/omni/reports-v2/samples/daily-turnover-eden.sample.json` |
| P0 | `Daily Turnover GVS` | 9 | Glen Village dated daily sales and GP. | `document_date, value_excl_after_discount, gross_profit` | `data/omni/reports-v2/samples/daily-turnover-gvs.sample.json` |
| P0 | `Daily Turnover One Life` | 8 | Centurion/HO dated daily sales and GP. | `document_date, value_excl_after_discount, gross_profit` | `data/omni/reports-v2/samples/daily-turnover-one-life.sample.json` |
| P1 | `Stock Turnover By Period - Columnar - with ave for last six months` | 14058 | SKU stock, turnover and last movement context. | `warehouse_code, warehouse_description, stock_code, stock_description, level, on_order, reserved, available, optimum_level, minimum_level, last_supplier, last_supplier_s_name` | `data/omni/reports-v2/samples/stock-turnover-by-period-columnar-with-ave-for-last-six-months.sample.json` |
| P1 | `Stock Export - wooCommerce - Levels Only` | 8432 | Online stock level feed by SKU. | `stock_code, available` | `data/omni/reports-v2/samples/stock-export-woocommerce-levels-only.sample.json` |
| P1 | `Stock Low GP Listing` | 8432 | Low-GP stock listing. | `supplier_#, stock_code, stock_description, level, selling_price_excl` | `data/omni/reports-v2/samples/stock-low-gp-listing.sample.json` |
| P1 | `Stock Price List with Supplier Price Comparison` | 8432 | Price and supplier comparison fields. | `stock_code, stock_description, excl_unit_selling_price, incl_unit_selling_price, last_supplier, last_supplier_s_name, last_sale_date, last_purchase_date` | `data/omni/reports-v2/samples/stock-price-list-with-supplier-price-comparison.sample.json` |
| P1 | `OL_PO_Generator_V6` | 8420 | Replenishment/order pressure by SKU. | `stock_code, stock_description, level, on_order, reserved, available, optimum_level, minimum_level, short, current_sales, movements_in, movements_out` | `data/omni/reports-v2/samples/ol-po-generator-v6.sample.json` |
| P1 | `Supplier Profitability` | 4603 | Supplier/item profitability. | `stock_code, stock_description, quantity, value_excl_after_discount, gross_profit` | `data/omni/reports-v2/samples/supplier-profitability.sample.json` |
| P1 | `Stock Turnover Analysis` | 4593 | SKU quantity/sales/GP turnover by financial year. | `financial_year, stock_type, stock_code, stock_description, quantity, value_excl_after_discount, gross_profit` | `data/omni/reports-v2/samples/stock-turnover-analysis.sample.json` |
| P1 | `Sales Analysis - Cross Tab` | 3668 | Document-date/week/product group trend source. | `period, customer_account, product_group_code, value_excl_after_discount, week_of_year, document_date` | `data/omni/reports-v2/samples/sales-analysis-cross-tab.sample.json` |
| P1 | `Stock Valuation - Slow movers 6 Months` | 1847 | Slow mover and stock valuation context. | `warehouse_code, supplier_#, last_moved, stock_code, stock_description, level` | `data/omni/reports-v2/samples/stock-valuation-slow-movers-6-months.sample.json` |
| P1 | `Warehouse Transfer Analysis` | 915 | Inter-branch transfer rows by SKU. | `source_warehouse_description, destination_warehouse, reference, stock_code, stock_description, delivered_qty, delivered_value_excl, internal_reference` | `data/omni/reports-v2/samples/warehouse-transfer-analysis.sample.json` |
| P1 | `Daily Sales Analysis` | 222 | Dated item/customer sales rows; redact customer fields before wider use. | `supplier_#, document_date, customer_name, bar_code, document_type, line_item_description, quantity, value_incl_after_discount` | `data/omni/reports-v2/samples/daily-sales-analysis.sample.json` |
| P1 | `Stock Reorder Report - Daily Material Requirements` | 213 | Warehouse reorder/material requirements. | `warehouse_code, warehouse_description, stock_code, stock_description, level, on_order, reserved, available, optimum_level, minimum_level, last_supplier, last_supplier_s_name` | `data/omni/reports-v2/samples/stock-reorder-report-daily-material-requirements.sample.json` |
| P1 | `Monthly Turnover Analysis` | 4 | Monthly financial period sales and GP. | `financial_year, period, count, value_excl_after_discount, gross_profit` | `data/omni/reports-v2/samples/monthly-turnover-analysis.sample.json` |

## Branch sales starting point

`ANA_Sales Analysis` is the immediate per-branch/per-item source. It has `company_branch_code`, `stock_code`, `stock_description`, `quantity`, `value_excl_after_discount`, `value_excl_before_discount`, `warehouse_code`, and `supplier_#`. It does not include `document_date`, so use it for product/branch mix and use branch-specific Daily Turnover reports for dated sales.

| branch | rows | sales excl after discount | share |
|---|---:|---:|---:|
| HO / Centurion (`HO`) | 86212 | 16182957.88 | 67.89% |
| Edenvale (`EDN`) | 18914 | 4143060.09 | 17.38% |
| Glen Village (`GVS`) | 18743 | 3509627.14 | 14.72% |

## Dated branch sales reports

- `Daily Turnover One Life`: Centurion/HO daily value and GP.
- `Daily Turnover EDEN`: Edenvale daily value and GP.
- `Daily Turnover GVS`: Glen Village daily value and GP.
- Avoid generic `Daily Turnover Analysis` for branch totals; existing dashboard notes flagged it as wrong/stale for the branch decision board.

## Parameter tests on Sales Analysis Johann Custom

| test | status | rows | bytes | changed vs base | params tested |
|---|---:|---:|---:|---|---|
| `base` | 200 | 5 | 827 | False | `` |
| `DateFrom_DateTo` | 200 | 5 | 827 | False | `DateFrom, DateTo` |
| `FromDate_ToDate` | 200 | 5 | 827 | False | `FromDate, ToDate` |
| `Branch_HO` | 200 | 5 | 827 | False | `Branch` |
| `Branch_EDN` | 200 | 5 | 827 | False | `Branch` |
| `Branch_GVS` | 200 | 5 | 827 | False | `Branch` |
| `CompanyBranchCode_HO` | 200 | 5 | 827 | False | `CompanyBranchCode` |
| `Warehouse_CEN` | 200 | 5 | 827 | False | `Warehouse` |
| `Period_2026_06` | 200 | 5 | 827 | False | `Period` |

None of the tested date/branch/period URL parameters changed `Sales Analysis Johann Custom`; use the saved reports above rather than parameterizing it.

## P2 / reference reports

| report | rows | note |
|---|---:|---|
| `Daily Turnover Analysis` | 491 | Generic daily turnover; do not use for branch totals. |
| `Detailed Cashup` | 3 | Narrow cashup fallback. |
| `OL - Cost Price Changes - Yesterday` | 328 | Cost-price change audit. |
| `OL - DASHBOARD -ALL- V31` | 6 | Module/status aggregate only. |
| `OL_Busy Times_MTD` | 10 | All-branch/system busy hours MTD. |
| `OL_Busy Times_Yesterday` | 9 | All-branch/system busy hours yesterday. |
| `OL_EDN_Busy Times_MTD` | 10 | Edenvale busy hours MTD. |
| `OL_GVS_Busy Times_MTD` | 9 | Glen Village busy hours MTD. |
| `OL_HO_Busy Times_MTD` | 9 | HO/Centurion busy hours MTD. |
| `Sales Analysis` | 18 | Small product/period result from prior Vivid probe. |
| `Sales Analysis GP% Report` | 1 | Single-row GP summary. |
| `Sales Analysis QTY Per Product - OLSHOP` | 18 | Tiny online product/supplier sales extract. |
| `Sales Analysis QTY Per Supplier` | 1 | Tiny supplier quantity aggregate. |
| `Supplier Payment Schedule` | 114 | Payables ageing; useful but not needed for T2-T4 baseline. |
| `Supplier Profitability Summary` | 1 | Very small aggregate supplier profitability summary. |

## Guess misses

- `Sales by Branch`
- `Branch Sales`
- `Daily Sales`
- `Sales by Item`
- `Stock on Hand`
- `Stock Analysis`
- `GP Analysis`
- `Sales Analysis Custom`
- `Sales Analysis Johann`
- `Engine Daily Branch Sales`
- `Engine Sales by Item`
- `Engine Stock on Hand`
- `Cashup Summary Totals`
- `Sales Analysis GP Report`
- `Daily Branch Sales`
- `Item Sales Analysis`
- `Branch Turnover`
- `Turnover by Branch`
- `Stock Listing`
