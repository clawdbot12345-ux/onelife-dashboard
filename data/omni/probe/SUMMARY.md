# Omni probe results

Origin: `http://102.22.82.27:59029` (probed from Mac Mini local run)

| name | status | content-type | bytes | saved file |
|---|---|---|---|---|
| main-report | 200 | application/json | 827 | data/omni/probe/main-report.json |
| main-report-Format-CSV | 200 | application/json | 827 | data/omni/probe/main-report-Format-CSV.json |
| main-report-Format-JSON | 200 | application/json | 827 | data/omni/probe/main-report-Format-JSON.json |
| main-report-Format-XML | 200 | application/json | 827 | data/omni/probe/main-report-Format-XML.json |
| main-report-Export-CSV | 200 | application/json | 827 | data/omni/probe/main-report-Export-CSV.json |
| main-report-OutputFormat-CSV | 200 | application/json | 827 | data/omni/probe/main-report-OutputFormat-CSV.json |
| discoverd41d8cd98f | 200 | text/plain; charset=ISO-8859-1 | 80 | data/omni/probe/discoverd41d8cd98f.html |
| discoverReport | 200 | text/plain; charset=ISO-8859-1 | 80 | data/omni/probe/discoverReport.html |
| discoverReport | 500 | text/plain; charset=ISO-8859-1 | 90 | - |
| discoverReports | 200 | text/plain; charset=ISO-8859-1 | 80 | data/omni/probe/discoverReports.html |
| discoverReportList | 200 | text/plain; charset=ISO-8859-1 | 80 | data/omni/probe/discoverReportList.html |
| discoverReport-List | 500 | text/plain; charset=ISO-8859-1 | 26 | - |
| discoverapi | 200 | text/plain; charset=ISO-8859-1 | 80 | data/omni/probe/discoverapi.html |
| discoverapi-reports | 200 | text/plain; charset=ISO-8859-1 | 80 | data/omni/probe/discoverapi-reports.html |
| discoverhelp | 200 | text/plain; charset=ISO-8859-1 | 80 | data/omni/probe/discoverhelp.html |

## Reports v2 discovery - 2026-06-12

- Cataloged 38 cached successful JSON reports; 36 are meaningful for engine ingestion.
- Full catalog: `data/omni/reports-v2/CATALOG.md` and `data/omni/reports-v2/catalog.json`.
- Immediate per-branch/per-item source: `ANA_Sales Analysis`.
- Dated branch sources: `Daily Turnover One Life`, `Daily Turnover EDEN`, `Daily Turnover GVS`.
- Branch stock sources: `ANA_Stock Listing_CEN`, `ANA_Stock Listing_EDN`, `ANA_Stock Listing_GVS`.

| priority | report | rows | uses |
|---|---|---:|---|
| P0 | `ANA_Sales Analysis` | 123869 | item_branch_sales |
| P0 | `ANA_Most Popular Products GP` | 11069 | item_branch_gp_sales |
| P0 | `ANA_Stock Listing_EDN` | 8432 | branch_stock_on_hand |
| P0 | `ANA_Stock Listing_GVS` | 8432 | branch_stock_on_hand |
| P0 | `ANA_Stock Listing_CEN` | 8430 | branch_stock_on_hand |
| P0 | `Daily Turnover EDEN` | 9 | dated_branch_sales |
| P0 | `Daily Turnover GVS` | 9 | dated_branch_sales |
| P0 | `Daily Turnover One Life` | 8 | dated_branch_sales |
| P1 | `Stock Turnover By Period - Columnar - with ave for last six months` | 14058 | stock_turnover_inventory |
| P1 | `Stock Export - wooCommerce - Levels Only` | 8432 | online_stock_levels |
| P1 | `Stock Low GP Listing` | 8432 | margin_risk |
| P1 | `Stock Price List with Supplier Price Comparison` | 8432 | pricing_supplier_context |
| P1 | `OL_PO_Generator_V6` | 8420 | replenishment |
| P1 | `Supplier Profitability` | 4603 | supplier_gp |
| P1 | `Stock Turnover Analysis` | 4593 | sku_turnover_gp |
| P1 | `Sales Analysis - Cross Tab` | 3668 | dated_trend_sales |
| P1 | `Stock Valuation - Slow movers 6 Months` | 1847 | dead_stock |
| P1 | `Warehouse Transfer Analysis` | 915 | transfer_analysis |
| P1 | `Daily Sales Analysis` | 222 | dated_item_sales |
| P1 | `Stock Reorder Report - Daily Material Requirements` | 213 | replenishment_by_warehouse |
| P1 | `Monthly Turnover Analysis` | 4 | monthly_trend_sales |
