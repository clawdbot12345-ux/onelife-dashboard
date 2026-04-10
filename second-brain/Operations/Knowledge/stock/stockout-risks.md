---
title: Stockout Risk Analysis
created: 2026-04-07
updated: 2026-04-07
tags: [stock, risk, operations, signal]
source: dashboard
period: 2026-03-01 to 2026-03-31
status: active
---

# Stockout Risk Analysis

**4,059 SKUs flagged at stockout risk** (≤5 units available). Of these, 50 are high-value products (>R500 excl VAT each).

## The Problem

Products at ≤5 units are one sale away from stockout. If a customer wants the product and we can't supply it, we lose both the sale and potentially the customer.

## High-Value Stockout Risks

50 products worth >R500 each are at ≤5 units. Some have no purchase order ever placed — they're being forgotten entirely.

Key items to reorder urgently:
- **FIRE BOWL 200MM** and similar high-value items with no or stale POs
- Products with high margin that are about to stock out — these are pure profit being left on the table

## Root Causes

1. **No PO placed** — some products have never been reordered
2. **Supplier non-delivery** — ordered but not received (see [[Operations/Knowledge/procurement/supplier-fill-rates]])
3. **PAR level issues** — reorder points not set or set too low
4. **Demand spikes** — unexpected sales velocity not caught in time

## Recommended Actions

1. Run through the 50 high-value items and place POs for any without active orders
2. Cross-reference with [[Operations/Knowledge/procurement/supplier-fill-rates]] — some stockouts may be caused by supplier fill issues
3. Set up PAR level alerts for anything with margin >40%
4. Review [[Operations/Knowledge/stock/double-down]] — ensure profit drivers don't appear here

## Links

- Supplier fill rates: [[Operations/Knowledge/procurement/supplier-fill-rates]]
- Products to push: [[Operations/Knowledge/stock/double-down]]
- Dead stock: [[Operations/Knowledge/stock/ordered-not-moving]]
- Signals: [[Intelligence/Knowledge/signals/march-2026-signals]]
