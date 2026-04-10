# Onelife Health — Retail Intelligence Dashboard

## Project Overview

A self-contained retail intelligence dashboard for **Onelife Health**, a South African health retail chain with three physical stores (Centurion, Glen Village, Edenvale) and a Shopify online store.

## Tech Stack

- **Single-file architecture**: Everything lives in `index.html` (~87K lines)
- **Vanilla HTML/CSS/JS** — no frameworks, no build system
- **Chart.js 4.4.3** via CDN for data visualization
- **Dark theme** using CSS custom properties

## Architecture

- `DASHBOARD_DATA` — embedded JSON object containing all store, product, supplier, and Shopify data
- `NARRATIVES` — pre-written business intelligence summaries per tab
- Tab-based navigation with 7 views: Overview, Products, Stock Intelligence, Suppliers, Categories, Online, Signals
- All rendering happens client-side via `initXXX()` functions on `DOMContentLoaded`

## Shopify Integration

The dashboard includes a Shopify Online tab with:
- Order count, revenue (excl VAT), AOV, discount rate
- Daily order & revenue breakdown
- Top products by revenue contribution

Data is currently static/embedded (pre-calculated), not fetched live from the Shopify API.

## Shopify AI Toolkit

This project is configured with the **Shopify Dev MCP Server** (see `.mcp.json`). This provides:
- Access to Shopify documentation and API schemas
- Real-time code validation against Shopify's schemas
- Store management capabilities via CLI

## Key Patterns

- Currency: South African Rand (R), formatted via `fmtR(n)`
- All prices displayed excluding VAT
- Sorting: `makeSortable()` generic table sorting utility
- Status indicators: pill classes (`pill-green`, `pill-amber`, `pill-red`)
- Margins and fill rates are color-coded by threshold
