# GA4 daily feed analysis

- Property ID: `525312444`
- Property name: `One Life Health`
- Timezone: `Africa/Johannesburg` (confirmed from GA4 Admin API)
- Currency: `ZAR` (confirmed from GA4 Admin API)
- Initial/feed run date: `2026-06-16`
- Daily reports cover the last 90 complete local days: `2026-03-18` to `2026-06-15`
- Trailing product report covers: `2025-06-16` to `2026-06-15`
- `ga4_landing_pages` is capped to the top 5,000 rows by purchase revenue so daily Git commits stay practical despite query-string variants.
- Revenue basis: GA4 revenue is treated as an online attribution/funnel signal and is typically incl-VAT. Shopify and Omni remain the money-ledger sources for final margin reporting.

## Files emitted

- `ga4_acquisition_daily`: 1,914 rows
- `ga4_devices`: 4 rows
- `ga4_ecommerce_funnel_daily`: 90 rows
- `ga4_geo`: 2,993 rows
- `ga4_landing_pages`: 5,000 rows
- `ga4_top_products`: 4,489 rows

## Channel mapping

`ga4_acquisition_daily` preserves GA4's raw `session_default_channel_group` and adds:

- `corrected_channel_group`
- `include_in_acquisition`
- `channel_correction_reason`

See `data/ga4/CHANNELS.md` for the exact PayFast/internal/account exclusion and Gmail/email-app-to-Email rules.

## API metric names

- `ga4_acquisition_daily` metrics requested as: sessions, totalUsers, newUsers, engagedSessions, conversions, totalRevenue
- `ga4_devices` metrics requested as: sessions, sessionConversionRate, purchaseRevenue
- `ga4_ecommerce_funnel_daily` metrics requested as: sessions, itemsViewed, addToCarts, checkouts, ecommercePurchases, purchaseRevenue, sessionConversionRate
- `ga4_geo` metrics requested as: sessions, conversions, purchaseRevenue
- `ga4_landing_pages` metrics requested as: sessions, engagedSessions, conversions, purchaseRevenue
- `ga4_top_products` metrics requested as: itemsViewed, itemsAddedToCart, itemsPurchased, itemRevenue
