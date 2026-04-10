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
- Tab-based navigation with 8 views: Overview, Products, Stock Intelligence, Suppliers, Categories, Online, Email Marketing, Signals
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

## Klaviyo Email Marketing Integration

The dashboard includes a dedicated Email Marketing tab powered by Klaviyo data:
- Subscriber metrics, open/click rates, email-attributed revenue
- Automated flow performance (Welcome, Abandoned Cart, Post-Purchase, Winback)
- Campaign history with open rate, click rate, revenue attribution
- Customer segment analysis (VIP, Supplement Subscribers, Lapsed, etc.)
- AI-suggested campaigns based on product data and segment insights

The **Klaviyo MCP Server** is configured in `.mcp.json` (requires `PRIVATE_API_KEY`).
Once activated, Claude can:
- Create and schedule email campaigns directly in Klaviyo
- Design on-brand email templates
- Analyze campaign and flow performance with live data
- Manage subscriber segments and profiles

### Klaviyo API Key Setup
1. Go to Klaviyo > Settings > API Keys
2. Create a Private API key with scopes: Campaigns (Full), Templates (Full), Profiles (Full), Segments (Full), Lists (Read), Metrics (Read), Events (Full), Images (Full)
3. Add the key to `.mcp.json` under `klaviyo.env.PRIVATE_API_KEY`

## Key Patterns

- Currency: South African Rand (R), formatted via `fmtR(n)`
- All prices displayed excluding VAT
- Sorting: `makeSortable()` generic table sorting utility
- Status indicators: pill classes (`pill-green`, `pill-amber`, `pill-red`)
- Margins and fill rates are color-coded by threshold
