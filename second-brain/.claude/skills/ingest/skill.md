# /ingest — Process New Dashboard Data

Import updated dashboard data into the vault, creating or updating knowledge pages.

## When to use

Run each time a new dashboard data snapshot is available (typically monthly).

## Inputs

- Path to the new dashboard HTML file (defaults to `../index.html`)
- Period label (e.g., "April 2026")

## Steps

1. **Read new data** — Parse `DASHBOARD_DATA` and `NARRATIVES` from the source file.

2. **Diff against existing** — Compare new KPIs with existing store/supplier/product pages to identify what changed.

3. **Update store profiles** — For each store:
   - Append new period data to the existing page under a `## March 2026` → `## April 2026` section
   - Update the frontmatter `updated:` date and `period:`
   - Highlight significant changes (>10% swing in any KPI)

4. **Update supplier profiles** — For suppliers in the new data:
   - Update fill rates, PO values, and last order dates
   - Flag any supplier whose fill rate changed by >10 points
   - Create new profiles for suppliers not yet in the vault

5. **Update product intelligence** — Refresh:
   - Stockout risks (new products at ≤5 units)
   - Ordered-not-moving list (any new additions?)
   - Double-down list (new high-margin opportunities?)
   - Margin warnings (new or resolved?)

6. **Update online profile** — Refresh Shopify KPIs and top products.

7. **Generate new signals** — Create `Intelligence/Knowledge/signals/{period}-signals.md`.

8. **Generate period report** — Create `Intelligence/Knowledge/reports/{period}-overview.md`.

9. **Create trend pages** — If 2+ periods exist, generate:
   - `Intelligence/Knowledge/trends/revenue-trend.md`
   - `Intelligence/Knowledge/trends/supplier-fill-trend.md`
   - `Intelligence/Knowledge/trends/online-growth-trend.md`

10. **Rebuild manifests** — Update all MANIFEST.md files.

11. **Update memory.md** — Record what was ingested and key changes spotted.

## Cross-linking rules

- New signals link to the relevant store, supplier, or product page
- Trend pages link to the periods they compare
- Every new page links to at least one existing page
