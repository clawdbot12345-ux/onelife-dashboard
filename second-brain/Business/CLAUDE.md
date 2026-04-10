# Business Pillar

This pillar holds commercial knowledge about Onelife Health's operations.

## Subdomains

- **stores/** — Per-store performance profiles (Centurion, Glen Village, Edenvale)
- **suppliers/** — Supplier profiles, fill rates, relationship notes
- **products/** — Product intelligence (movers, dead stock, margin analysis)
- **online/** — Shopify channel performance and strategy

## When ingesting data here

1. Create or update the relevant Knowledge page
2. Always include YAML frontmatter with `source: dashboard` and `period:`
3. Cross-link to related pages: stores link to their top suppliers, products link to their supplier
4. Update the MANIFEST.md in the relevant Knowledge subfolder
5. Tag with: `#store`, `#supplier`, `#product`, `#online`

## Key questions this pillar answers

- How is each store performing vs the others?
- Which suppliers are reliable and which are problematic?
- What products should we push, and which should we stop reordering?
- How is the online channel growing?
