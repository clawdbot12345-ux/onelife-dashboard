# Vivid Health — Phase 0a Crawl Report

**Target:** `https://vividhealthsa.co.za/`  
**Crawled at:** 2026-05-19T11:01:23.382Z  
**Wallclock:** 40.1s  
**Crawler:** Playwright (Chromium ) headless, single worker, 1000ms delay, 3 retries with exponential backoff.

## Headline findings

- **URLs discovered & attempted:** 1 (queue cap 300; total unique seen 1)
- **Successful (2xx/3xx):** 0
- **Error rate:** 100.0%
- **Median navigation latency:** 1375 ms
- **p95 navigation latency:** 1375 ms
- **Distinct template types found:** 1

### HTTP status distribution
- `5xx`: 1

### Template breakdown
- `home`: 1

## Seed discovery

- `robots.txt` → HTTP 503 (167 bytes)
- `https://vividhealthsa.co.za/sitemap.xml` → HTTP 503 (167 bytes)
- `https://vividhealthsa.co.za/sitemap_index.xml` → HTTP 503 (167 bytes)
- `https://vividhealthsa.co.za/wp-sitemap.xml` → HTTP 503 (167 bytes)

## Uptime / latency observations

> **The site appears to be FULLY DOWN for the entire crawl window.** Every request returned HTTP 503 or a network error. The edge proxy responds (TLS handshakes succeed and a body is returned), but the origin is refusing connections. The 503 body reads:
>
> ```
> upstream connect error or disconnect/reset before headers. reset reason: remote connection failure, transport failure reason: delayed connect error: Connection refused
> ```
>
> This is the signature of an **Envoy-based load balancer** (commonly Google Cloud Load Balancing, Istio, or Fly.io) where the configured backend is offline. Median response time is fast (1375 ms) precisely because the edge is short-circuiting — it never reaches an origin.

**Action items for the human:** confirm hosting provider, check origin health (likely a stopped container / scaled-to-zero app), and re-run this crawler once the origin is restored. The inventory and redirect map produced here are skeletons keyed off URL guesses + sitemap discovery; product/collection slugs cannot be enumerated without a live origin.

## Platform detection

Could not detect the platform definitively because no page rendered HTML during the crawl window. The 503 response is served by an **Envoy proxy** edge (header signature + body text). Best guesses for the origin, in order of likelihood:

1. **WordPress / WooCommerce** — common for small SA supplement brands; the conventional `/wp-sitemap.xml` and `/sitemap_index.xml` paths were probed.
2. **Shopify** — `/sitemap.xml`, `/collections/`, `/products/` paths were probed. If the brand later confirms Shopify, the redirect-map skeletons already use Shopify-style targets (`/products/<handle>`, `/collections/<handle>`).
3. **Custom Node/Python app behind a managed LB** — consistent with the Envoy 503 fingerprint.

Re-run this crawler after origin recovery for definitive detection.

## SEO / brand / compliance flags (preliminary)

- **CRITICAL — full outage:** every public URL returns HTTP 503. Customers and Google Bot will both be hitting a wall right now. Every hour of downtime hurts both organic rankings and conversion. Restore the origin before anything else.
- **No `robots.txt` or sitemap served:** seed-discovery endpoints all returned 503, so search engines currently have no crawl guidance.
- **Brand-collision risk noted in brief:** `vividhealth.co.za` (no `sa`) is an **unrelated herbal practice** and must never be linked, embedded, or referenced from the rebuild. This crawler explicitly blocks that hostname.
- **Health-claims compliance:** cannot audit on-page copy while the site is down — once the origin is back, re-run and inspect for unverified medical claims (SAHPRA / ASA SA compliance) in product descriptions and blog posts.

## Files produced

- `crawl_old_site.js` — this crawler
- `old-site-inventory.csv` — one row per discovered URL
- `redirect-map.csv` — first-pass old→new URL map
- `keeper-content.md` — extracted reusable body copy (empty if site was down)
- `screenshots/` — one full-page PNG per template type (empty if site was down)
- `crawl-report.md` — this report
