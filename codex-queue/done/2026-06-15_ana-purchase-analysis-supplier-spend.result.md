# Codex result: ANA_Purchase analysis supplier spend

Date: 2026-06-15
Branch: `claude/end-to-end-goal-tdcj0f`

## Done

- Added `ANA_Purchase analysis` to the daily Omni P0 pull.
- Generated `data/omni/daily/2026-06-15_ana-purchase-analysis.json`.
- Extended `engine_supplier_master` with:
  - `supplier_account_no`
  - stock-linked `supplier_#`
  - raw `purchase_supplier_#`
  - `supplier_name`
  - `linked_to_stock`
- Rebuilt `engine_supplier_po_grv` using:
  - `Purchase Orders` for ordered value and order count.
  - `ANA_Purchase analysis` for actual received/invoiced purchase spend.
  - `Supplier Payment Schedule` for outstanding/payables context.
- Added `engine_supplier_purchase_coverage` with linked/unlinked supplier spend coverage.

## Source report

`ANA_Purchase analysis` is live and returned 394 rows with:

`supplier_#`, `supplier_name`, `supplier_account_no`, `value_excl_after_discount`

The join key is:

`normalized supplier_account_no == normalized stock supplier_#`

Normalization is uppercase + trim. The purchase report's numeric `supplier_#` is emitted as `purchase_supplier_#` but is not used for joining.

## Generated outputs

- `data/omni/daily/2026-06-15_ana-purchase-analysis.json` - 394 rows
- `data/omni/daily/2026-06-15_engine-supplier-master.json` - 318 rows
- `data/omni/daily/2026-06-15_engine-supplier-po-grv.json` - 235 rows
- `data/omni/daily/2026-06-15_engine-supplier-purchase-coverage.json` - 1 summary row

## Coverage summary

From `engine_supplier_purchase_coverage`:

- Purchase supplier count: 231
- Linked to stock supplier codes: 212
- Linked purchase value excl: R16,160,563.44
- Unlinked supplier count: 19
- Unlinked purchase value excl: R2,401,913.40

Largest unlinked suppliers by net purchase value:

- `EMALINI` - Emalini Enterprises - R591,854.07
- `EDNR` - EDN RENT Spring Mountain Investments (Pty) Ltd - R477,074.86
- `DWM` - DIGIWAZ MEDIA - R262,200.00
- `METRO` - METROPROP PTY LTD GVS - R241,658.21
- `EDEN` - (IMPERIAL) SOLGAR - EDEN PHARMA SA PRY LTD - R230,862.04

## Fill-rate proxy

`engine_supplier_po_grv` now emits:

- `po_value_excl`
- `received_invoiced_value_excl`
- `fill_rate_proxy`
- `fill_rate_proxy_basis`
- `linked_to_stock`

The proxy is:

`received_invoiced_value_excl / po_value_excl`

It is explicitly not true GRV. The field `grv_value_excl` remains `null`, and `fill_pct` remains `null`, because Omni has not exposed a true GRV-by-supplier source.

## Validation

- `python3 -m py_compile scripts/fetch_omni.py` passed.
- `.github/workflows/daily-refresh.yml` parsed successfully.
- Full local fetch with `OMNI_REPORT_URL` completed.
- History duplicate checks passed:
  - `data/omni/daily_turnover_history.csv`: 43 rows, 0 duplicate branch/date keys.
  - `data/omni/daily_branch_transactions_history.csv`: 3 rows, 0 duplicate branch/date keys.
