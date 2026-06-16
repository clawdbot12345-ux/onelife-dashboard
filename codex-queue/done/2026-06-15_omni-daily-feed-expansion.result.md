# Codex result: Omni daily feed expansion

Date: 2026-06-15
Branch: `claude/end-to-end-goal-tdcj0f`

## Done

- Expanded `scripts/fetch_omni.py` P0 daily feed with:
  - `ANA_Stock Listing_CEN`
  - `ANA_Stock Listing_EDN`
  - `ANA_Stock Listing_GVS`
  - `Supplier Profitability`
  - `Stock Valuation - Slow movers 6 Months`
  - `OL_PO_Generator_V6` bonus replenishment feed
- Added branch-yesterday busy-time pulls:
  - `OL_HO_Busy Times_Yesterday`
  - `OL_EDN_Busy Times_Yesterday`
  - `OL_GVS_Busy Times_Yesterday`
- Added derived `Engine Daily Branch Transactions` output from branch busy-time counts.
- Added idempotent history CSV:
  - `data/omni/daily_branch_transactions_history.csv`
- Added turnover quality audit output:
  - `data/omni/daily/2026-06-15_turnover-quality-audit.json`
- Patched `.github/workflows/daily-refresh.yml` with a best-effort `fetch_omni.py` step using `secrets.OMNI_REPORT_URL`.
- Patched workflow commit step to include:
  - `data/omni/daily`
  - `data/omni/daily_turnover_history.csv`
  - `data/omni/daily_branch_transactions_history.csv`

## Generated daily files

Required files now exist in `data/omni/daily/`:

- `2026-06-15_engine-daily-branch-transactions.json` - 3 rows
- `2026-06-15_ana-stock-listing-cen.json` - 8,439 rows
- `2026-06-15_ana-stock-listing-edn.json` - 8,441 rows
- `2026-06-15_ana-stock-listing-gvs.json` - 8,441 rows
- `2026-06-15_supplier-profitability.json` - 4,707 rows
- `2026-06-15_stock-valuation-slow-movers-6-months.json` - 1,870 rows

Additional useful files:

- `2026-06-15_ol-po-generator-v6.json` - 8,429 rows
- `2026-06-15_ol-ho-busy-times-yesterday.json` - 0 rows
- `2026-06-15_ol-edn-busy-times-yesterday.json` - 7 rows
- `2026-06-15_ol-gvs-busy-times-yesterday.json` - 4 rows
- `2026-06-15_turnover-quality-audit.json` - 1 audit row

## Derived branch transactions

`2026-06-15_engine-daily-branch-transactions.json` contains transaction counts for `2026-06-14`:

| branch | transaction_count | value_excl_after_discount | average_basket_ex_vat | source |
|---|---:|---:|---:|---|
| `HO` | 0 | 0.00 |  | `OL_HO_Busy Times_Yesterday` |
| `EDN` | 24 | 8,956.00 | 373.17 | `OL_EDN_Busy Times_Yesterday` |
| `GVS` | 16 | 7,667.50 | 479.22 | `OL_GVS_Busy Times_Yesterday` |

Notes:

- EDN/GVS busy-time value totals match the daily turnover values for 2026-06-14, so this is a clean per-branch transaction-count source for those branches.
- HO returned 0 rows for 2026-06-14. The turnover audit also shows HO missing 2026-06-07 and 2026-06-14, both Sundays. This looks like branch no-trade/closed-day behavior rather than a pull-window truncation.
- `Daily Sales Analysis` was checked but is not a clean transaction source: it has line rows and no document/reference id in the cataloged/live shape.

## Turnover quality

`2026-06-15_turnover-quality-audit.json` says:

- `HO` / `Daily Turnover One Life`: 12 rows, `2026-06-01` to `2026-06-13`, missing `2026-06-07` and `2026-06-14`.
- `EDN`: 14 rows, `2026-06-01` to `2026-06-14`, no missing dates.
- `GVS`: 14 rows, `2026-06-01` to `2026-06-14`, no missing dates.
- No sub-R1,000 low-value partial rows found in the turnover feeds.

Scope note:

- `Daily Turnover One Life` is still treated as `HO` / Centurion because the cataloged `ANA_Sales Analysis` branch summary maps `HO` to HO/Centurion. The turnover feed itself does not expose warehouse/channel split, so do not label it as online/warehouse unless Omni adds that dimension.

## Secret / cloud status

- GitHub secret `OMNI_REPORT_URL` is set on `clawdbot12345-ux/onelife-dashboard`.
- `gh secret list` reports `OMNI_REPORT_URL` updated at `2026-06-12T18:21:15Z`.
- I could not dispatch `omni-probe.yml` from GitHub Actions because that workflow file is not present on the default branch yet. After this branch is merged, the patched `daily-refresh.yml` can test cloud reachability; if it fails, the Mac Mini bridge remains the fetcher.

## Validation

- `python3 -m py_compile scripts/fetch_omni.py` passed.
- `.github/workflows/daily-refresh.yml` parsed successfully with Ruby YAML.
- History CSV duplicate check passed:
  - `data/omni/daily_turnover_history.csv`: 40 rows, 0 duplicate branch/date keys.
  - `data/omni/daily_branch_transactions_history.csv`: 3 rows, 0 duplicate branch/date keys.
