# /onboard — Initial Vault Setup

Scaffold the Onelife Second Brain vault and import initial data from the dashboard.

## When to use

Run once when setting up a new vault, or to reset and re-import from scratch.

## Steps

1. **Verify structure** — Ensure all pillar folders, subfolders, and CLAUDE.md files exist:
   ```
   Business/{Inbox,Projects,Knowledge/{stores,suppliers,products,online}}
   Intelligence/{Inbox,Projects,Knowledge/{signals,trends,reports}}
   Operations/{Inbox,Projects,Knowledge/{stock,procurement,pricing}}
   ```

2. **Read dashboard data** — Open `../index.html` and parse the `DASHBOARD_DATA` and `NARRATIVES` objects.

3. **Generate store profiles** — For each store (centurion, glen_village, edenvale), create:
   - `Business/Knowledge/stores/{store-name}.md` with KPIs, daily sales summary, and narrative

4. **Generate supplier profiles** — From `DASHBOARD_DATA.suppliers`, create:
   - `Business/Knowledge/suppliers/{supplier-code}.md` for top 20 suppliers by PO value
   - Include: order count, PO value, GRV value, fill %, SKU count, last order date

5. **Generate product intelligence** — From `DASHBOARD_DATA.products`, create:
   - `Operations/Knowledge/stock/stockout-risks.md` — Products at ≤5 units
   - `Operations/Knowledge/stock/ordered-not-moving.md` — Repeatedly ordered but not selling
   - `Operations/Knowledge/stock/double-down.md` — High-margin, well-stocked products to push
   - `Operations/Knowledge/pricing/margin-warnings.md` — Low/negative margin products

6. **Generate online profile** — From `DASHBOARD_DATA.shopify`, create:
   - `Business/Knowledge/online/shopify-channel.md` with KPIs and top products

7. **Generate signals** — From `NARRATIVES.signals`, create:
   - `Intelligence/Knowledge/signals/march-2026-signals.md` with actionable items

8. **Generate initial report** — Combine all narratives into:
   - `Intelligence/Knowledge/reports/march-2026-overview.md`

9. **Build manifests** — Run `/lint` to generate all MANIFEST.md files.

10. **Update memory.md** — Record the onboarding session.

## Output

A fully populated vault with cross-linked knowledge pages ready for querying.
