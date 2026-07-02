# Codex Completion Note - Vivid Health Closing Round, 2026-07-02

Branch: `claude/vivid-health-audit-redesign-9fmzon`
Store checked: `hgywg0-w7.myshopify.com` only. One Life store was not touched.

## Task 1 - Label Panels

Completed in branch assets:

- Committed 51 handle-mapped label panels to `vivid/assets/store/label-panels/`.
- Destination count: 51 files.
- Size gate: every file is under 250KB; largest checked file is 228,338 bytes.
- OCR gate: staged destination files checked clean for both banned strings:
  - `ANGUS CASTUS`: 0 hits
  - `DIETARY SUPPLEMENT`: 0 hits

## Task 2 - Corrected Stack Heroes

Completed in branch assets:

- Committed corrected 1:1 and 3:4 stack crops to `vivid/assets/store/stacks/`.
- `comrades-recovery-stack`: Turmeric Plus, MSM, L-Glutamine.
- `highveld-hayfever-stack`: Quercetin Complex, Mullein, Buffered C.
- `perimenopause-essentials`: Agnus Castus, Sage, Maca, Griffonia (5-HTP).
- OCR gate: final stack files checked clean for both banned strings:
  - `ANGUS CASTUS`: 0 hits
  - `DIETARY SUPPLEMENT`: 0 hits

## Task 3 - Admin / App Launch Items

Admin items 1-3 were probed against the Vivid store and are blocked by merchant/admin access limits:

1. Subscriptions billing app
   - Current Vivid app token can read products and selling-plan groups, but there are 0 selling-plan groups.
   - `subscriptionContracts` is access denied with the current token, so recurring billing and a test subscription checkout cannot be proved from this app credential.
   - Requires merchant/admin UI installation and checkout test for Shopify Subscriptions, Recharge, Appstle, or the owner's chosen billing app.

2. Judge.me reviews
   - Current app scopes are limited to `read_products`, `read_inventory`, `read_locations`, and `write_inventory`.
   - The token cannot inspect or install merchant apps (`appInstallations` is access denied).
   - Requires merchant/admin UI install of Judge.me and enabling post-purchase review requests. After that, Claude can remove the hardcoded sample block.

3. Inventory
   - Vivid API audit found 58 products and 22 sold out, including `Buffered C · 300 capsules`.
   - The token has `write_inventory` but not `write_products`, so Codex cannot hide/unpublish sold-out products.
   - Inventory restock could not be applied because the expected Omni export directory is missing locally: `tmp/omni-smb-pull/Automation`.
   - To complete this item, provide a fresh Omni export for the Vivid SKUs or add `write_products` scope if the owner wants sold-out products hidden.

Items 4-10 remain scheduled admin/commercial follow-ups from the v4 handoff: payments, Klaviyo, pixels, price rounding, domain, shipping-rate validation, and COAs.

