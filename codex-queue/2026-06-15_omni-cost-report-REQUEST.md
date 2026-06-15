# Omni report request (merchant action — Omni desktop)

Date: 2026-06-15 · For: whoever maintains the Omni Accounts reports (Johann / accountant).
Why: this is the single biggest unlock for the live dashboard. Codex has already probed the
web API — the cost reports below **do not exist as saved reports yet**, so they must be
created/exposed once in the Omni desktop client. Omni already has the data (it computes
gross profit), it just isn't exposed by name to the web server.

## What we need (pick the easiest of these)

**Option 1 (preferred, smallest change):** add an **average cost (excl VAT)** column to the
existing `ANA_Stock Listing_CEN / _EDN / _GVS` reports. New column, e.g. `average_cost_excl`
(unit average/weighted cost). That's it.

**Option 2:** create one new saved report **`Engine Stock Cost`** with columns:
`stock_code, average_cost_excl` (one row per SKU; branch-agnostic is fine).

Either way, expose it to the Omni web server by name (same as the existing reports) so it's
reachable at `/Report/{name}?<credentials>`.

## Why it matters
Cost per SKU unlocks, on the dashboard: real product margins, stock value **at cost**, the
"double-down" high-margin set, margin warnings, and capital-trapped (dead stock) valuation —
i.e. the Products, Categories, and Stock-Intelligence tabs go fully live. Today we only have
cost for the ~72% of SKUs that have *sold* (derived from sales GP); a true cost report takes
that to ~100%.

## After it exists
Tell Codex the report name; Codex adds it to `fetch_omni.py`'s P0 set (one line), and the
dashboard sync (`scripts/omni_dashboard_sync.py`) consumes it automatically — coverage rises
from 72% to ~100% with no further code changes.

## What does NOT need this
GRV / fill-rate is a separate gap (no goods-received report is exposed). If a
GRV-by-supplier report can be added at the same time
(`supplier_#, grv_value_excl` per period), the Suppliers tab fill-rate also goes live.

## Optional 3rd report (for anomaly detection — nice to have)
**`Engine Returns`** — returns / credit notes by branch and date:
`document_date, company_branch_code, return_value_excl, reason (if available)`. Powers
return-rate anomaly alerts and a true net-sales figure per store.

---
### The complete Omni ask (so IT builds it once)
1. **Per-SKU average cost** (critical) — Report 1 above.
2. **GRV by supplier** (fill rates) — see note above.
3. **Returns by branch/date** (optional — anomaly detection).

Everything else we need from Omni is already flowing (daily turnover + GP, per-branch stock,
item sales + GP, purchase orders, payables, MTD transactions/busy-times, slow-movers,
reorder requirements).
