# Codex task: add Outstanding Purchase Orders feed (supplier exposure)

Date: 2026-06-16
Unblocks: the Suppliers tab — rebuilt around real **supplier purchases (12-mo)** +
**outstanding-order exposure** (Johann built the report; grand total ties to the daily
dashboard's R179,060 Outstanding Orders).

## Why the metric changed
We were chasing a "fill rate", but open POs are undelivered *by definition* (Ordered Qty ≈
Outstanding Qty on open lines), so a fill % is meaningless. The right, real signals are:
(a) how much we buy from each supplier (12-mo, already have via ANA_Purchase analysis), and
(b) how much each supplier currently owes us undelivered, and how old it is.

## Do
1. Add **`ANA_Outstanding Purchase Orders`** to `fetch_omni.py`'s daily pull (use the one
   that includes **Supplier #** — columns: `supplier_#, supplier_name, document_date,
   reference, stock_code, line_item_description, ordered_qty, outstanding_qty_to_deliver,
   cost_price_excl, outstanding_delivery_value_excl`; the report already filters
   Outstanding Qty ≠ 0).
2. Build **`engine_supplier_outstanding`** aggregated per supplier:
   `supplier_#, supplier_name, outstanding_value_excl (sum), outstanding_qty (sum),
   ordered_qty (sum), line_count, po_count (distinct reference), oldest_doc_date (min),
   age_days (today − oldest)`. Sanity: the grand total of `outstanding_value_excl` should
   tie to ~**R179,060**.
3. Keep raw lines available too (for drill-down) and `ANA_Purchase analysis` unchanged
   (12-mo purchases per supplier).
4. Standard output contract (`data/omni/daily/{date}_{slug}.json`); commit; tell Claude the
   emitted field names.

## Then (Claude)
Rebuild the Suppliers tab: per supplier — 12-mo purchases (importance) + outstanding value +
oldest age (exposure) + line/PO counts; KPI = total outstanding exposure; "watch list" =
biggest + oldest outstanding. No fake fill rate. That closes the last operational tab.
