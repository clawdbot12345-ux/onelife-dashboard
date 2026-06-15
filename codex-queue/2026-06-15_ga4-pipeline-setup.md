# Codex task: GA4 pipeline — web acquisition, funnel & attribution feed

Date: 2026-06-15
Unblocks: the marketing/acquisition + on-site funnel + true online attribution layer of the
decision cockpit (the one data source not yet wired). Mirrors the Omni pipeline you built.

## Goal
Stand up a daily GA4 feed into `data/ga4/daily/` so the dashboard sync can consume it —
same output contract as Omni: `data/ga4/daily/{YYYY-MM-DD}_{slug}.json`, top-level key =
slug, value = list of row dicts. Add a `scripts/fetch_ga4.py` (GA4 Data API, service-account
auth) + a step in `daily-refresh.yml`. Credentials via a GitHub secret — never commit them.

## Access (the one human step)
- Use the GA4 **Data API v1** with a **Google service account**. Codex: create the service
  account + JSON key in Google Cloud and enable the Analytics Data API.
- A human with GA4 admin must (a) add the service-account email as a **Viewer** under
  GA4 Admin → Property Access Management, and (b) give us the **GA4 property ID**.
- Store the key + property ID as repo secrets: `GA4_SA_JSON`, `GA4_PROPERTY_ID`.
  (If a **BigQuery export** is already enabled on the property, that's an acceptable
  alternative source — note which you used.)

## Reports to pull (GA4 Data API runReport; last 90 days daily + one trailing-12-month run)

1. **`ga4_acquisition_daily`** — dims: `date, sessionDefaultChannelGroup, sessionSource,
   sessionMedium`; metrics: `sessions, totalUsers, newUsers, engagedSessions, conversions,
   totalRevenue`.
2. **`ga4_ecommerce_funnel_daily`** — dims: `date`; metrics: `sessions, itemsViewed,
   addToCarts, checkouts, ecommercePurchases, purchaseRevenue` (+ `sessionConversionRate`).
   Optionally also split by `sessionDefaultChannelGroup`.
3. **`ga4_top_products`** — dims: `itemName, itemId`; metrics: `itemsViewed, addToCarts,
   itemsPurchased, itemRevenue`. (Gives the "viewed-but-not-bought" signal Klaviyo can't.)
4. **`ga4_landing_pages`** — dims: `landingPagePlusQueryString`; metrics: `sessions,
   engagedSessions, conversions, purchaseRevenue`. (Which content/PDPs drive entries.)
5. **`ga4_geo`** — dims: `city, region`; metrics: `sessions, conversions, purchaseRevenue`.
   (SA cities — Centurion/Pretoria/JHB store-proximity vs online.)
6. **`ga4_devices`** — dims: `deviceCategory`; metrics: `sessions, sessionConversionRate,
   purchaseRevenue`.

## Channel-grouping correctness (important — known issue)
Earlier work flagged misclassification (PayFast referral, Gmail, and account/login traffic
landing in a "google-unclassified" bucket). Please apply the corrected channel grouping so
acquisition numbers are trustworthy: exclude internal/account/checkout-return referrals
(e.g. PayFast) from acquisition, and map Gmail/email-app referrals to Email. Document the
mapping in `data/ga4/CHANNELS.md`.

## Definition of done
- `scripts/fetch_ga4.py` runs with `GA4_SA_JSON` + `GA4_PROPERTY_ID`, writes the six dated
  JSON files, committed to your branch.
- A short `data/ga4/ANALYSIS.md` noting property, timezone, currency (ZAR), date range, and
  the channel mapping applied.
- `daily-refresh.yml` calls it (best-effort, like the Omni step).
- No `index.html` work — Claude builds the consumer (`omni_dashboard_sync.py` sibling) once
  the files land.

## Notes for Claude (on completion)
- Confirm GA4 currency/timezone (expect ZAR / Africa/Johannesburg) so it reconciles with
  Shopify + Omni excl-VAT figures (GA4 revenue is typically incl-VAT — note the basis).
