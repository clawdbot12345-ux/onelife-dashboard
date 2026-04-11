# Onelife Shopify — Exact Duplicate Dedup Breakdown

**Generated:** 2026-04-11 15:54 UTC
**Scope:** Live catalog only (`status=active` + `published_status=published`)
**Canonical rule:** images -> oldest -> highest stock -> lowest id
**Stock rule:** variant-level merge onto canonical by title key; unmatched stock flagged for manual review

## Summary

| Metric | Value |
|---|---:|
| Live products before dedup | 4,700 |
| Unique titles | 4,700 |
| Duplicate groups | 0 |
| **Products to archive** | **0** |
| **Products after dedup** | **4,700** |
| Stock units to transfer onto canonicals | 0 |
| Stock units flagged for manual review | 0 |
| Groups needing manual review | 0 |
| No-image edge-case groups | 0 |

### Duplicate group size distribution

| Group size | # groups | Products in these groups |
|---:|---:|---:|

### Canonical quality check

- Groups where the kept canonical HAS images: **0**
- Groups where NO member has an image (canonical chosen by stock/age): **0**

## Stock preservation plan

Before archiving, the apply script will transfer **0 units** of stock from soon-to-be-archived duplicates onto their canonical counterparts, variant-by-variant, matched on normalized variant title key.

**0 units** across **0 groups** could not be matched cleanly (variant title on the duplicate does not exist on the canonical). These are listed under 'Groups needing manual review' below and will NOT be auto-merged.

Variants with `inventory_quantity <= 0` are skipped entirely (no sellable stock to preserve).

## No-image edge-case groups

_None — every duplicate group has at least one member with images._

## Groups needing manual review (0 total — showing top 50 by unmatched qty)

_None — every duplicate variant matched a canonical variant cleanly._

## Sample of clean merges (top 20 by group size)

## Next step

This is a **DRY RUN** — nothing has been changed in Shopify yet.

The planned apply script (`scripts/dedup_apply.py`, requires explicit `APPLY=true`) will:

1. For each group, execute every queued variant transfer
   (POST `/inventory_levels/adjust.json` on the online location) BEFORE archiving.
2. Set every non-canonical product to `status=archived` via PUT `/products/:id`.
3. Create 301 redirects from archived handles to the canonical handle.
4. Log every action to `reports/dedup-applied-YYYY-MM-DD.log`.
5. Skip groups flagged as `needs_review` for unmatched variants, or (if the
   operator chooses) transfer the matched variants only and leave the rest.

All archiving is reversible: setting `status=active` restores the listing.
Inventory transfers are NOT reversible automatically — they are real Shopify writes.