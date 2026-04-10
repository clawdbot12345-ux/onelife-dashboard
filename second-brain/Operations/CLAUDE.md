# Operations Pillar

This pillar holds day-to-day operational knowledge for running Onelife Health.

## Subdomains

- **stock/** — Inventory management, stockout risks, dead stock, reorder rules
- **procurement/** — Ordering processes, supplier lead times, PO management
- **pricing/** — Margin analysis, pricing strategy, discount policies

## When ingesting data here

1. Stock pages should flag risk levels: critical (≤5 units), warning (≤20), healthy (>20)
2. Procurement pages link to the relevant supplier in Business/Knowledge/suppliers/
3. Pricing pages include margin calculations excluding VAT
4. Always include YAML frontmatter with `source:` and `period:`
5. Tag with: `#stock`, `#procurement`, `#pricing`, `#operations`

## Key questions this pillar answers

- What's at risk of stocking out?
- What are we over-ordering?
- Which suppliers need follow-up on deliveries?
- Where are our margins under pressure?
