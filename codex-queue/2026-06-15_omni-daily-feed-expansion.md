# Codex task: expand the Omni daily feed (unlock the rest of the live dashboard)

Date: 2026-06-15 · Follow-up to the Omni pipeline (thank you — it's working and now
wired into the dashboard).
Unblocks: live Products / Stock Intelligence / Suppliers tabs, per-branch stock, and
restoring per-store transaction count + avg basket.

## Context
The Claude side now consumes Omni. `scripts/omni_dashboard_sync.py` reads
`data/omni/daily/*.json` and rewrites the dashboard's `stores{}` + KPIs live
(June MTD: store **R1,031,675**, GP **R346,781 / 33.6%**, Centurion 67% / EDN 17% / GVS 16%).

But `scripts/fetch_omni.py` only pulls **5 reports**:
`Daily Turnover One Life/EDEN/GVS`, `ANA_Most Popular Products GP`,
`Stock Export - wooCommerce - Levels Only`. So the rest of the dashboard is still on the
static March snapshot, and Daily Turnover gives **value + GP only** (no document count) —
which is why transaction count / avg basket are currently blank.

The Omni Web Server serves any saved report by name; the reports below are already
cataloged in `data/omni/reports-v2/CATALOG.md`. The output contract Claude consumes:
`data/omni/daily/{YYYY-MM-DD}_{slugified-report-name}.json`, top-level key = slugified
report name, value = list of row dicts (exactly what `fetch_omni.py` already writes).

## Steps (in order of payoff)

1. **Add a per-branch daily transaction count** (restores transaction_count + avg basket).
   - First check whether `Daily Sales Analysis` (P1, 222 rows, has `document_date` +
     document rows) can be aggregated to count documents per branch per day, OR whether
     `OL_Busy Times_*` rows carry a transaction/document count column.
   - If neither gives a clean daily per-branch count, define a new saved report
     **`Engine Daily Branch Transactions`** — columns: `document_date`, `company_branch_code`,
     `transaction_count` (distinct documents/tills), last 60 days.
   - Add it to `P0_REPORTS` in `fetch_omni.py`.

2. **Add the three per-branch stock listings to the daily pull** (live Products + per-branch
   stock + "in stock at your nearest store"):
   `ANA_Stock Listing_CEN`, `ANA_Stock Listing_EDN`, `ANA_Stock Listing_GVS`
   (~8,430 rows each; columns already cataloged: `stock_code, stock_description, bar_code,
   selling_price_excl, available, product_group, stock_category, supplier_#`). Append to
   `P0_REPORTS`.

3. **Add supplier + dead-stock reports** (live Suppliers tab + Capital-Trapped signal):
   `Supplier Profitability` (4,603 rows) and `Stock Valuation - Slow movers 6 Months`
   (1,847 rows). `OL_PO_Generator_V6` (8,420 rows) is a bonus for live replenishment.
   These can be a weekly cadence if daily is heavy.

4. **Data-quality fixes on the existing turnover feed:**
   - `Daily Turnover One Life` (Centurion) is returning **12 days vs 14** for EDN/GVS in
     June, and the latest 1–2 days look partial (R260–R665). Confirm whether those are
     genuinely closed days or a sync-timing gap, and fix the pull window/timing so MTD
     totals aren't understated.
   - Confirm the **scope** of `Daily Turnover One Life`: Centurion store only, or HO incl.
     warehouse/online? (Affects how we label/attribute it.)

5. **Confirm `OMNI_REPORT_URL` is set as a GitHub Actions repo secret.** `daily-refresh.yml`
   now has a best-effort `fetch_omni.py` step using `secrets.OMNI_REPORT_URL`; if the cloud
   runner can reach the server, the whole feed becomes cloud-autonomous (no Mac Mini
   dependency). If runners can't reach it, leave the Mac Mini bridge as the fetcher — the
   sync step reads whatever's committed either way.

6. Commit new samples + daily files; push. No need to touch `index.html` — Claude extends
   `omni_dashboard_sync.py` to consume the new files once they appear.

## Definition of done
- `data/omni/daily/` contains dated files for: a per-branch transaction count, the three
  `ANA_Stock Listing_*`, and `Supplier Profitability` + `Stock Valuation - Slow movers`.
- Centurion turnover day-count matches EDN/GVS (or the gap is explained).
- `OMNI_REPORT_URL` secret status confirmed (set / can't-reach-from-cloud).

Once these land, Claude wires Products, Stock Intelligence, Suppliers, and the
transaction/basket metrics to live Omni — same pattern as the stores block already shipped.
