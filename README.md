# Onelife Health — Retail Intelligence Dashboard

Self-contained single-file dashboard for Onelife Health's three stores and Shopify online store. Pulls live data from Klaviyo daily.

## View the dashboard

- **Interactive (HTML)**: [`index.html`](./index.html) — open directly in a browser, or view rendered via [raw.githack.com](https://raw.githack.com/clawdbot12345-ux/onelife-dashboard/main/index.html)
- **Print-friendly (PDF)**: [`onelife-dashboard.pdf`](./onelife-dashboard.pdf)
- **Live site (after enabling GitHub Pages)**: `https://clawdbot12345-ux.github.io/onelife-dashboard/`

## Tabs

1. **Overview** — KPIs, revenue trend, store comparison
2. **Products** — full sortable product catalog
3. **Stock Intelligence** — stockouts, slow movers, margin warnings
4. **Suppliers** — fill rates and PO value analysis
5. **Categories** — category-level breakdown
6. **Online** — Shopify metrics (live from Klaviyo integration)
7. **Email Marketing** — Klaviyo campaigns, flows, segments (live)
8. **Signals** — strategic alerts and narratives

## Automation

The dashboard auto-refreshes every day at **08:00 SAST** via GitHub Actions.

### Setup (one-time)

1. **Add the Klaviyo API key as a secret**:
   - Go to **Settings → Secrets and variables → Actions**
   - Click **New repository secret**
   - Name: `KLAVIYO_API_KEY`
   - Value: your Klaviyo private API key (`pk_...`)

2. **Enable GitHub Pages** (optional, for public hosting):
   - Go to **Settings → Pages**
   - Source: **GitHub Actions**
   - The deploy workflow will publish to `https://clawdbot12345-ux.github.io/onelife-dashboard/`

### Manual refresh

Go to the **Actions** tab → **Daily Dashboard Refresh** → **Run workflow**.

## Tech

- **Stack**: Vanilla HTML/CSS/JS + Chart.js — no build step, no frameworks
- **Data layer**: Embedded `DASHBOARD_DATA` JSON, refreshed daily by `scripts/refresh_dashboard.py`
- **PDF generation**: Headless Chrome via `scripts/generate_pdf.js`
- **AI integrations**: Shopify Dev MCP server + Klaviyo remote MCP server (see `.mcp.json`)

## Files

| File | Purpose |
|---|---|
| `index.html` | The entire dashboard (HTML + CSS + JS + data) |
| `onelife-dashboard.pdf` | Printable PDF export (regenerated daily) |
| `scripts/refresh_dashboard.py` | Pulls Klaviyo data and updates `DASHBOARD_DATA` |
| `scripts/generate_pdf.js` | Headless Chrome PDF renderer |
| `.github/workflows/daily-refresh.yml` | Cron job: refresh data + PDF every morning |
| `.github/workflows/deploy-pages.yml` | Publish to GitHub Pages on push to main |
| `.mcp.json` | MCP server config for Claude Code (Shopify + Klaviyo) |
| `CLAUDE.md` | Project context for AI-assisted development |
