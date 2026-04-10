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

## Automation

### Daily Data Refresh

The dashboard auto-refreshes every morning at **06:00 UTC (08:00 SAST)** via
GitHub Actions (`.github/workflows/daily-refresh.yml`). The workflow:

1. Runs `scripts/refresh_dashboard.py` to fetch the last 30 days of data
   from the Klaviyo API (including Shopify integration metrics)
2. Rewrites `DASHBOARD_DATA.shopify` and `DASHBOARD_DATA.klaviyo` in `index.html`
3. Regenerates the narratives with real insights
4. Runs `scripts/generate_pdf.js` to render a fresh `onelife-dashboard.pdf`
5. Commits and pushes the updated files back to the repo

Manual trigger: go to the **Actions** tab on GitHub and click "Run workflow"
on the "Daily Dashboard Refresh" workflow.

### Required Secret

Set the following GitHub Actions secret under **Settings → Secrets and variables → Actions**:

| Name | Value |
|---|---|
| `KLAVIYO_API_KEY` | Your Klaviyo private API key (`pk_...`) |

### GitHub Pages Deployment

The `.github/workflows/deploy-pages.yml` workflow auto-publishes `index.html`
to GitHub Pages whenever it changes on `main`. Enable Pages under
**Settings → Pages → Source: GitHub Actions** for the live dashboard URL to work.

## Key Patterns

- Currency: South African Rand (R), formatted via `fmtR(n)`
- All prices displayed excluding VAT
- Sorting: `makeSortable()` generic table sorting utility
- Status indicators: pill classes (`pill-green`, `pill-amber`, `pill-red`)
- Margins and fill rates are color-coded by threshold
