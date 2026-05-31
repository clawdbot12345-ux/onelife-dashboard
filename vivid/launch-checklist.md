# Vivid Health Shopify launch checklist

Last updated: 2026-05-31

## Store

- [done] Shopify Basic store created and billing completed by Naadir.
- [done] Store admin: `https://admin.shopify.com/store/hgywg0-w7`
- [done] Current Shopify domain: `hgywg0-w7.myshopify.com`
- [done] Store name changed from `My Store` to `Vivid Health`.
- [done] Store contact email is `orders@vividhealthsa.co.za`.
- [done] External inbound email to `orders@vividhealthsa.co.za` is fixed: SpamExperts was routing Vivid mail to the wrong destination host and now routes to `mail.vividhealthsa.co.za`; Shopify verification now reaches Inbox/cPanel Track Delivery.
- [done] Store address updated from the CIPC details for `INTERLIFE WHOLESALERS (PTY) LTD`.
- [done] Shopify tax setting confirms product prices include sales tax/VAT.
- [done] Domestic standard shipping now has free delivery for orders `R400.00` and up.
- [done] Shopify business entity now shows `Vivid Health` with the Interlife/Company details behind it.
- [done] Store contact phone is saved in Shopify; latest Admin API readback confirms `+27 12 654 3740`.

## Theme

- [done] Claude Vivid theme pushed as unpublished draft theme `148718944342`.
- [done] Draft preview URL: `https://hgywg0-w7.myshopify.com?preview_theme_id=148718944342`
- [done] Theme editor: `https://hgywg0-w7.myshopify.com/admin/themes/148718944342/editor`
- [done] Theme assets copied in and template CTAs/collection handles wired.
- [done] Preview QA fixed visible font CSS and `category-grid` Liquid count errors.
- [done] Added launch content templates for standard pages, contact, and quiz.
- [done] Draft theme header/footer menus now use the Shopify navigation built for Vivid.
- [done] Authenticated draft-preview QA passed for home, quiz, contact, and shipping/returns pages.
- [done] Latest visual QA pass fixed duplicate Shopify section padding, Shopify rich-text heading spacing, missing product/bundle cards, goal collection links/counts, catalog filter spacing, mobile collection heading fit, and product/bundle/PDP image containment.
- [done] Latest QA screenshots/contact sheets are in `screenshots/vivid-theme-qa/`.
- [done] `shopify theme check` passes with 33 files and no offenses.
- [done] 2026-05-31 final PDP visual pass fixed the oversized packshot frame and invisible selected-variant text; patched theme was pushed to unpublished draft `148718944342`.
- [done] 2026-05-31 cart QA fixed the missing `/cart` route, added a cart page, and changed drawer shipping estimate from R79 to R100 so it matches checkout.
- [done] 2026-05-31 footer legal line now says Vivid Health is operated by Interlife Wholesalers (Pty) Ltd instead of implying Vivid Health is its own Pty Ltd.
- [pending] Theme remains unpublished until explicit launch approval.

## Catalogue

- [done] 52 supplement products imported as draft products.
- [done] 3 bundle placeholder products created as draft products.
- [done] All 55 products are vendor `Vivid Health`.
- [done] 315 product media items are READY in Shopify: 52 packshots, 260 generated product assets, and 3 bundle images.
- [done] Product SKUs resolved from public Onelife product data; no Onelife Admin token was used.
- [done] Launch-hold tags applied to the 2 Barley products and 3 bundle placeholders.
- [done] Products were activated and published to the Online Store channel on 2026-05-30 so the password-protected draft preview can render real catalog, collection, and PDP pages.
- [pending] Keep the store password-protected and the Vivid theme unpublished until payment, inventory, and launch approvals are complete.
- [pending] Bundle products are placeholders; final bundle mechanics still need app/order-flow configuration.

## Collections

- [done] 11 Vivid collections created.
- [done] Smart goal collections: `gut`, `immunity`, `energy`, `stress`, `joints`, `women`, `men`, `daily`.
- [done] Manual collections: `all-formulations`, `bundles`, `bestsellers`.
- [done] Current counts: all formulations 52, bundles 3, bestsellers 6, daily 20, energy 2, gut 5, immunity 10, joints 7, men 1, stress 4, women 3.

## Pages, Policies, And Navigation

- [done] Shopify pages created/updated for About, Contact, Quiz, Ingredient standards, Shipping and returns, POPIA, and FAQ.
- [done] Shopify policies updated for contact information, shipping, refunds, and terms of service.
- [pending] Shopify privacy policy is managed by Shopify's automatic privacy policy system and was not overwritten by script; latest text check found no bracket/TODO placeholders, but it still needs owner/legal review before public launch.
- [done] Main menu and footer menus created/updated for the draft site.

## Payments

- [done] Payfast account is activated and dashboard access works for `orders@vividhealthsa.co.za`.
- [done] Payfast Shopify integration is enabled in the Payfast dashboard.
- [done] Payfast app is installed on the Vivid Shopify store.
- [done] Shopify payment provider `Payfast` is active with Test mode off.
- [done] 2026-05-31 Payfast dashboard login works and still shows the Vivid account as pending verification.
- [done] 2026-05-31 checkout smoke test passed up to the final Pay Now step: Wormwood added to basket, `/cart` rendered, checkout loaded, shipping rates showed R100/R150, Payfast appeared, and Pay Now was enabled. Pay Now was not clicked.
- [done] Payfast registration was started as a Company account for `orders@vividhealthsa.co.za`.
- [done] Payfast business, registered address, and banking details were completed from the supplied CIPC/VAT/business context and bank proof.
- [done] Proof of banking details for Interlife/Vivid was supplied and staged locally as sensitive material at `credentials/vivid-payfast-bank-proof-interlife.pdf`.
- [done] Payfast account-holder and UBO registration steps were submitted after Naadir supplied the required KYC details and authorized the terms/confirmation checkboxes.
- [done] Payfast showed "Your registration was successful" and said it sent an activation email.
- [done] Payfast activation/reset emails now reach the repaired `orders@vividhealthsa.co.za` mailbox.
- [done] Support request sent from `orders@vividhealthsa.co.za` to `support@payfast.io` on 2026-05-30 at 15:46 SAST asking Payfast to resend/advise on activation.
- [done] CIPC verification document was uploaded to Payfast and submitted for review.
- [pending] Payfast dashboard still shows account pending verification after document submission.
- [blocked] R1 Payfast test transaction has not been run.
- [blocked] Do not open the store publicly until Payfast verification clears and a successful checkout/test order is reviewed.

## Inventory

- [done] `scripts/sync-vivid-inventory.js` created.
- [done] `scripts/onelife_omni_export_fetch.py` added for SMB export fetches without printing credentials.
- [done] `scripts/onelife_omni_http_report_fetch.py` added for the Omni web-server JSON report without hardcoding credentials.
- [done] `.github/workflows/vivid-inventory-sync.yml` added for a daily 04:00 SAST sync and manual dispatch.
- [done] Initial GitHub CLI workflow-scope blocker was bypassed: `.github/workflows/vivid-inventory-sync.yml` is now present on PR branch `claude/vivid-shopify-setup`.
- [done] Workflow now supports the Omni HTTP JSON stock report or the older SMB export fallback.
- [done] Workflow now supports Shopify's current Dev Dashboard client-credentials flow and still accepts a static `VIVID_SHOPIFY_ADMIN_TOKEN` if one is ever issued.
- [done] Fresh Omni HTTP stock report fetched from `ANA_Stock Listing_CEN` on 2026-05-30.
- [done] Inventory applied to Shopify for the matched Vivid supplement SKUs.
- [done] Post-apply dry run verified `0` remaining differences for matched products.
- [done] Later 2026-05-30 refresh applied the only two fresh Omni deltas, then post-apply dry run again verified `0` remaining differences for matched products.
- [done] Inventory sync now treats the two launch-hold Barley SKU mismatches as allowed skips and still fails on any unexpected blocking skip.
- [done] Latest fresh Omni dry run on 2026-05-30 reports `ok: true`, `changes: 0`, `allowedSkipped: 2`, and `blockingSkipped: 0`.
- [pending] Resolve the two Barley SKU mismatches before publishing those two products:
  - Barley Grass, Shopify SKU `6000000622305`
  - Barley Grass Powder, Shopify SKU `6100000001565`
- [done] GitHub Actions secret `ONELIFE_OMNI_HTTP_REPORT_URL` added for the CEN stock report endpoint.
- [done] Shopify Dev Dashboard app `Vivid Inventory Sync` created, scoped to product/inventory/location access, released, and installed on the Vivid Shopify store.
- [done] Local secret file created at `credentials/vivid-shopify-client-credentials.env` for the Vivid Shopify client credentials.
- [done] GitHub repo secrets `VIVID_SHOPIFY_CLIENT_ID` and `VIVID_SHOPIFY_CLIENT_SECRET` set for `clawdbot12345-ux/onelife-dashboard`.
- [done] Shopify client-credentials token exchange tested successfully without printing the token; returned a 24-hour Admin API token for the requested inventory sync scopes.
- [done] Local inventory dry run using client credentials on 2026-05-30 at 23:12 SAST reports `ok: true`, `changes: 0`, `allowedSkipped: 2`, and `blockingSkipped: 0`.
- [done] GitHub workflow file `.github/workflows/vivid-inventory-sync.yml` was added to PR branch `claude/vivid-shopify-setup` via GitHub connector after CLI auth could not get `workflow` scope interactively.
- [done] 2026-05-31 fresh Omni HTTP dry run against `tmp/omni-http-fetch/ana-stock-listing-cen.json` reports `ok: true`, `changes: 0`, `allowedSkipped: 2`, `blockingSkipped: 0`, and `staleExport: false`.
- [pending] Add repo/local secrets for fallback paths only if needed:
  - HTTP components: `ONELIFE_OMNI_HTTP_HOST`, `ONELIFE_OMNI_HTTP_USER`, `ONELIFE_OMNI_HTTP_PASSWORD`, `ONELIFE_OMNI_COMPANY`
  - SMB: `ONELIFE_OMNI_SMB_HOST`, `ONELIFE_OMNI_SMB_SHARE`, `ONELIFE_OMNI_SMB_DOMAIN`, `ONELIFE_OMNI_SMB_USER`, `ONELIFE_OMNI_SMB_PASSWORD`
- [pending] Run the GitHub workflow once after PR merge/secret check, then spot-check 5-10 SKUs.

## API Access For Claude Review

- [done] Dedicated Shopify Dev Dashboard app `Vivid Claude Review` created and installed on the Vivid store.
- [done] Active app version `claude-review-1` released with scoped review/theme access: `read_products`, `read_inventory`, `read_locations`, `read_publications`, `read_content`, `read_online_store_navigation`, `read_legal_policies`, `read_themes`, `write_theme_code`, and `write_themes`.
- [done] The app intentionally does not have customer, order, payout, payment, discount, shipping-write, or "all orders" scopes.
- [done] Client credentials were saved locally at `credentials/vivid-claude-review-shopify.env`; the client secret was not printed into docs or chat.
- [done] Client-credentials token exchange tested successfully; GraphQL readback confirms app `Vivid Claude Review`, the granted scopes, and both Shopify themes.

## Klaviyo

- [done] Separate Vivid Klaviyo account created under the existing login.
- [done] Vivid Klaviyo account ID: `RLcBwa`.
- [done] Vivid Klaviyo plan: Free.
- [done] Vivid Shopify native integration enabled for `hgywg0-w7.myshopify.com`.
- [done] Shopify historical sync completed in the Vivid Klaviyo account.
- [done] Shopify app embed enabled and saved in Shopify theme editor.
- [done] Storefront source confirms the Klaviyo app pixel is configured with Vivid account `RLcBwa`.
- [done] Shopify subscriber list renamed to `Vivid Health`.
- [done] Vivid list ID in the new account: `Vh2ne6`.
- [done] Shopify app `Klaviyo: Email Marketing & SMS` installed on the Vivid Shopify store.
- [done] Vivid list-specific sender override now persists as `Vivid Health <info@vividhealthsa.co.za>`.
- [done] Added Klaviyo branded sending-domain DNS records in Afrihost for `send.vividhealthsa.co.za`.
- [done] DNS now resolves the Klaviyo `send.vividhealthsa.co.za` NS records and root verification TXT record.
- [pending] Klaviyo branded sending domain is verifying in Klaviyo UI; Klaviyo says DNS can take up to 48 hours.
- [done] Created Klaviyo draft flows: Welcome Series, Browse Abandonment, Customer Winback, Customer Thank You, and Post-Purchase Followup.
- [done] Final Klaviyo flows-list check showed all 5 flows as `Draft`.
- [blocked] Abandoned Checkout was not created because Klaviyo shows the recommendation as API-incomplete and with Live actions.
- [pending] Latest UI recheck could not switch into the Vivid Klaviyo account without a Klaviyo login prompt, so sending-domain status and test sends still need a Vivid Klaviyo UI login.
- [pending] 2026-05-31 UI recheck still lands on the Klaviyo login page for `switch_to=RLcBwa`; DNS records resolve, but Klaviyo UI verification/test sends remain blocked by login.
- [pending] Send and review a Vivid test email from `info@vividhealthsa.co.za` before activating emails.
- [pending] Send and review test emails before activating flows.

## Domain

- [done] DNS cutover checklist written at `vivid/dns-cutover-checklist.md`.
- [done] Added `vividhealthsa.co.za` and `www.vividhealthsa.co.za` as custom domains in Shopify; Shopify Admin reports SSL enabled.
- [pending] Public DNS still points both apex and `www` to the existing Afrihost hosting IP, so the live website has not been cut over.
- [pending] Do not cut over `vividhealthsa.co.za` until Naadir explicitly approves a separate live DNS task.

## Final launch blockers

- Payfast account verification review and successful checkout/test order.
- Barley SKU mapping confirmation before public launch; the two Barley products still carry launch-hold tags.
- Run the first remote inventory workflow and spot-check 5-10 SKUs.
- Shopify privacy policy needs owner/legal review because it remains Shopify-managed automatic text.
- Klaviyo branded sending domain verification, plus flow test sends.
- Explicit approval to publish the Vivid theme/remove password protection.
- Explicit approval to cut over DNS.
