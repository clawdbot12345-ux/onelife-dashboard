# Vivid Health DNS cutover checklist

Last updated: 2026-05-30

## Current state

- Production target domain: `vividhealthsa.co.za`
- Shopify store: `hgywg0-w7.myshopify.com`
- Shopify admin: `https://admin.shopify.com/store/hgywg0-w7`
- `vividhealthsa.co.za` has been added inside Shopify and currently shows as needing DNS setup.
- Public website DNS was not cut over during setup.
- Afrihost mailboxes exist for `orders@`, `info@`, and `admin@` on `vividhealthsa.co.za`; keep existing MX/TXT mail records intact during cutover.
- Klaviyo sender-domain records for `send.vividhealthsa.co.za` were added in Afrihost separately from the Shopify website cutover.
- DNS snapshot before Shopify website cutover: `output/vivid-afrihost-dns-snapshot-20260530.md`.

## DNS records for Shopify

Set these only when Naadir explicitly approves the live domain cutover:

| Host | Type | Value |
| --- | --- | --- |
| `@` | `A` | `23.227.38.65` |
| `www` | `CNAME` | `shops.myshopify.com` |

Do not change MX, SPF, DKIM, DMARC, or other email-related records unless Afrihost or Shopify gives a specific reason.

## Pre-cutover checks

- Draft theme has been published or an explicit launch theme is selected.
- Products intended for sale have been activated and assigned to Online Store.
- Payfast is configured, test mode passed, and live mode is explicitly approved.
- Inventory sync has had at least one successful fresh run from Omni to Vivid Shopify.
- Klaviyo Shopify integration is connected to the `Vivid Health` list and test emails have been reviewed.
- Store password is intentionally disabled for launch, or intentionally left enabled for a soft launch.
- Shopify Domains page has `vividhealthsa.co.za` and `www.vividhealthsa.co.za` added.

## Cutover steps

1. Lower DNS TTL at Afrihost to 300 seconds where possible.
2. Add or update the apex `A` record to `23.227.38.65`.
3. Add or update the `www` CNAME to `shops.myshopify.com`.
4. Leave all mail records unchanged.
5. In Shopify admin, go to Settings -> Domains and confirm both apex and `www` show connected.
6. Wait for Shopify SSL provisioning to finish.
7. Set the primary domain in Shopify to the preferred public URL.

## Verification

- `https://vividhealthsa.co.za` loads the Vivid storefront.
- `https://www.vividhealthsa.co.za` redirects to the primary domain.
- Product page, collection page, cart, and checkout all load.
- Payfast appears correctly at checkout.
- Test order confirmation emails render with the Vivid brand.
- Afrihost mail still receives mail for `orders@vividhealthsa.co.za`.

## Rollback

If cutover fails, restore the prior apex and `www` records in Afrihost. Keep a screenshot/export of the existing DNS zone before changing anything. Email rollback should not be needed if MX/TXT records are left untouched.
