# Omni feed — probe analysis (2026-06-12)

## What we learned
- The endpoint is an **Omni Web Server v7.21.68.3389** REST interface. Saved custom reports are served as JSON at `/Report/{Report Name}` with `UserName/Password/CompanyName` query auth. Connectivity confirmed from the Mac Mini (and GitHub Actions runners should also reach it; cloud Claude sandbox cannot — port 59029).
- `Sales Analysis Johann Custom` returns sales **grouped by discount band only**: 5 rows, total R974,182.54 excl VAT before discount / **R949,038.78 after discount** (R25,143.76 discount given, ~2.6%). Period and scope (which stores? online included?) are not exposed in the payload — the report has no date/store/item dimensions.
- Format parameters (`Format=CSV/JSON/XML`) are ignored — always JSON. Discovery paths return the server banner only ("contact support for developer API"); there is no public report index.

## What this means for T2–T4
One aggregate number isn't enough. The engine needs three reports (or one parameterised report) out of Omni:
1. **Daily sales by branch/store** (date, branch, sales excl VAT, cost of sales → GP) — drives T2/T3/T4 scoreboard + baselines.
2. **Sales by item** (period, item code, description, brand/supplier, qty, sales, cost → GP%) — completes PRODUCT_MATRIX v1.0 and verifies Vivid GP 35–40% + Vivid revenue vs the R500k/mo target.
3. **Stock on hand by item by branch** — stock-reliability scoring + "never market what's out of stock".

Reports are defined in the Omni Accounts desktop client (report designer) and exposed to the web server by name — "Johann Custom" suggests a consultant (Johann?) set the existing one up and more named reports may already exist.

## Next actions
- Codex task queued: `codex-queue/2026-06-12_omni-reports-v2.md` (probe for other report names, test date/branch URL parameters, and/or get the 3 reports above defined in Omni).
- Once any per-store report responds: engine builds `scripts/fetch_omni.py` + scheduled workflow → SCOREBOARD auto-fills T2–T4 → stores dashboard view.
