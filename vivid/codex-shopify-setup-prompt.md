# Codex prompt — Vivid Health Shopify store setup

## Setup

```bash
git clone https://github.com/clawdbot12345-ux/onelife-dashboard.git
cd onelife-dashboard
git checkout claude/vivid-health-shopify-redesign-KITNn
```

Everything you need is in this branch:
- **`vivid/theme/`** — Shopify Online Store 2.0 theme (Liquid sections, snippets, templates, settings_schema, locales, theme.js, base.css). Ready to push to a Shopify store.
- **`vivid/index.html`** — design reference / single-file prototype. **Do not deploy this file** — it's a design source of truth only. The Liquid theme already mirrors its design.
- **`vivid/data/products.json`** — the 52 Vivid SKUs with handles, ZAR prices, sizes, goals, forms, diet tags, availability, and Shopify CDN image URLs. Source for the catalogue import.
- **`vivid/strategy.md`** — the 90-day strategy doc. Read it for context on positioning and roadmap.

## Your task

Set up the Vivid Health Shopify store end-to-end so that **vividhealthsa.co.za** can eventually point to it. The Onelife Shopify store stays untouched.

You drive the work. The user (Naadir) approves credentials, registrations, and decisions. **Use `AskUserQuestion` at every gate listed below.** Do not sign up for anything, spend money, or take irreversible actions without explicit approval.

---

## Decisions already made — don't re-ask

- **Store identity:** new Shopify store, separate from the existing Onelife store. Suggested handle: `vivid-health`.
- **Plan:** Shopify Basic (~R450/mo) — sufficient to launch. Plus is not needed.
- **Payment processor:** **Payfast.** Register a Payfast merchant account, then connect to the Shopify store via the Payfast Shopify app.
- **Email marketing:** **Klaviyo, same account as Onelife.** Create a new **list** called "Vivid Health" inside the existing Klaviyo account. Install the Klaviyo Shopify integration on the Vivid store and point it at the new list.
- **Inventory source of truth:** **Onelife Omni.** Set up a daily inventory sync from Onelife Omni → Vivid Shopify store. Stock levels in Vivid Shopify should always mirror what Omni says is available.
- **Domain:** `vividhealthsa.co.za` is the production target — but **do not cut over DNS in this task**. The store should be reachable on `vivid-health.myshopify.com` only until the user approves the DNS switch in a separate task.
- **Currency/region:** ZAR, South Africa.
- **Tax:** prices include 15% VAT. Display prices VAT-inclusive.
- **Free delivery threshold:** R400.

---

## The plan, with gates

Each numbered step is a deliverable. Before each one, run the questions in the "Gate" subsection via `AskUserQuestion`.

### Step 1 — Create the Shopify store

**Gate 1.1:**
- Does Naadir already have a Shopify Partner account?
- Should the new store be created as a development store (free, can be transferred to production later) or a paid store from day one?
- Confirm the store handle: `vivid-health.myshopify.com` (or alternative).
- Confirm the store legal/business details — registered company name, VAT number, registered address (use the real Centurion address: 117 Galway Ave, Hennopspark, Centurion, 0157).

Once approved, walk Naadir through the signup at partners.shopify.com (or shopify.com directly). Wait until he confirms the store is created and he's logged into admin.

### Step 2 — Theme push

**Gate 2.1:**
- Confirm Naadir has installed Shopify CLI (`brew install shopify-cli` or via npm).
- Ask Naadir to run `shopify auth login` and `shopify theme dev --store=vivid-health.myshopify.com` once, to authenticate and verify access.

Once authenticated, push the theme:

```bash
cd vivid/theme
shopify theme push --store=vivid-health.myshopify.com --unpublished
```

Use `--unpublished` so the theme is uploaded as a draft (not live yet). Then preview, sanity-check, and only publish when Naadir approves.

**Gate 2.2** — after preview:
- Show Naadir the preview URL.
- Ask: any visual issues to fix before we publish?
- Ask: ready to publish? (Run `shopify theme publish` when approved.)

### Step 3 — Catalogue import (52 Vivid SKUs)

**Gate 3.1:**
- Confirm with Naadir: do we want to import the products as-is from `vivid/data/products.json`, or pull live data from the Onelife Shopify store (since these same SKUs already exist there)?
- If pulling from Onelife: ask for an Onelife Shopify Admin API token with read-only access to products. Use it once for the migration, then have Naadir revoke it.

Either way:

1. Write a small Node script (`scripts/vivid-import.js`) that reads from the source and creates products via the Vivid store's GraphQL Admin API.
2. Map each Vivid SKU to:
   - Title, handle, description, vendor = "Vivid Health"
   - Variant: price (ZAR, VAT-inclusive), SKU, weight, requires_shipping=true
   - Inventory: leave at 0 — inventory sync (Step 6) will populate it
   - Images: upload from the existing Shopify CDN URLs in `products.json`
   - Tags: from the `goal`, `form`, `diet` fields in the JSON
   - Product type: "Supplement"
   - Status: draft (not published until everything else is wired)

**Gate 3.2** — after import:
- Show Naadir a list of the 52 created products in the Vivid admin.
- Ask: any product needing a manual fix before we proceed?

### Step 4 — Collections

Create the collections that match the prototype's "Shop by goal" navigation. From the source data (`vivid/data/products.json`), the goals are: gut, immunity, energy, stress, joints, women, men, daily.

For each goal, create a smart collection with the rule: `tag = <goal>`. Plus:
- "All formulations" (manual collection, all 52 products)
- "Bundles" (manual, just the 3 bundles once they exist)
- "Bestsellers" (manual, hand-picked by Naadir)

Use the existing banner imagery in `vivid/theme/assets/` for collection hero images.

**Gate 4.1:**
- Confirm the 8 goal collection handles match what the theme's nav expects (`gut`, `immunity`, etc.).
- Ask Naadir which products to feature in the "Bestsellers" manual collection.

### Step 5 — Payments (Payfast)

**Gate 5.1:**
- Does Naadir already have a Payfast merchant account, or does he need to register?
- If registering: ask for the registered business name + VAT number + bank details — but DO NOT submit the Payfast signup form yourself. Send Naadir to https://www.payfast.co.za/registration and have him complete it personally. (Payment processor signups require the real account holder to sign.)
- Once Payfast account exists, ask for: **Merchant ID**, **Merchant Key**, **Passphrase**.

Then in Shopify admin:
1. Install the Payfast Shopify app (Apps → Shopify App Store → search "Payfast Payments").
2. Configure with the 3 credentials Naadir provided.
3. Enable test mode first. Run a R1 test transaction yourself to verify the full flow (cart → checkout → Payfast hosted page → success → order created in Shopify).
4. Switch to live mode only after Naadir confirms the test order looks right.

**Gate 5.2** — after test transaction:
- Confirm the test order's amount, customer email, and order status all look correct.
- Ask: ready to enable live payments?

### Step 6 — Inventory sync from Onelife Omni

**Gate 6.1 — credentials and shape:**
- Ask Naadir what "Onelife Omni" actually is. Likely candidates: (a) the Onelife Shopify store itself (so Omni = Shopify Admin API); (b) a separate POS/inventory system like Lightspeed, Vend, or a custom system; (c) a third-party stock-management app. We need to know which.
- Ask for: API endpoint, auth method (API key / OAuth / session), the data format, and what "available stock" means (per-location, per-variant, total).
- Ask: should the sync respect retail-store reservations, or pull total chain-wide stock?

Once we know what Omni is:

1. Write `scripts/sync-vivid-inventory.js` — a Node script that:
   - Reads current stock from Omni for each of the 52 Vivid SKUs (matched by SKU code or barcode).
   - Reads current stock from Vivid Shopify via Inventory API.
   - Calculates the delta.
   - Calls Shopify `inventorySetOnHandQuantities` for any SKU where the count differs.
   - Logs every change to stdout for debugging.
   - Exits 0 on success, non-zero on any error.

2. Add a GitHub Actions workflow `.github/workflows/vivid-inventory-sync.yml`:
   - Runs daily at 04:00 SAST (02:00 UTC) — before stores open, to give the day a fresh stock baseline.
   - Also exposes `workflow_dispatch` for manual runs.
   - Reads credentials from repo secrets: `VIVID_SHOPIFY_ADMIN_TOKEN`, `ONELIFE_OMNI_API_KEY` (or whatever auth Omni needs).
   - Notifies on failure to a Slack webhook or email — ask Naadir which.

3. Run the script once manually with verbose logging. Show Naadir the output. Have him spot-check 5–10 SKUs against the Onelife floor.

**Gate 6.2** — after first sync:
- Confirm the stock levels in Vivid admin match what Naadir expects to see.
- Confirm the GitHub Action's daily schedule is what he wants (or earlier/later).

### Step 7 — Klaviyo

**Gate 7.1:**
- Ask Naadir for the Klaviyo private API key (the one already in `.mcp.json` should work, but confirm).
- Confirm: same Klaviyo account, new list named "Vivid Health".

Then:
1. Create the "Vivid Health" list via Klaviyo API.
2. In Shopify admin → Apps → install the Klaviyo Shopify integration (https://apps.shopify.com/klaviyo-email-marketing).
3. Configure it to point at the Vivid Health list, not the Onelife list.
4. Set up the four core flows on the Vivid list: Welcome (10% off code), Abandoned Cart (2-step), Post-Purchase (review request + cross-sell), Winback (60 days inactive).
5. Use the existing email design tokens from `vivid/theme/assets/base.css` for any custom branded templates.

**Gate 7.2** — flows configured:
- Ask Naadir to send himself a test email through each flow before going live.

### Step 8 — Domain configuration (DO NOT CUT OVER)

**Gate 8.1:**
- Confirm: the store is to be reachable on `vivid-health.myshopify.com` only until Naadir explicitly approves the DNS switch.
- Add `vividhealthsa.co.za` as a custom domain in Shopify admin → Settings → Domains, but **do not change the registrar's A record** in this task. Output the DNS records that will be needed (Shopify gives an A record `23.227.38.65` + a CNAME `shops.myshopify.com`), and put them in a doc at `vivid/dns-cutover-checklist.md` for the future cutover task.

This is the only gate where the answer is "no action required from Naadir until later". Just produce the doc.

### Step 9 — Pre-launch checklist

Compile a single doc at `vivid/launch-checklist.md` that lists:
- ✅/❌ for every step above
- Outstanding items requiring Naadir to action
- DNS cutover plan (TTL, expected propagation, rollback if needed)
- Test orders placed + outcomes
- Klaviyo flows active vs draft
- Inventory sync first successful run timestamp

---

## Out of scope — DO NOT do these in this task

- ❌ Do not touch the existing Onelife Shopify store, its theme, its products, or its DNS in any way.
- ❌ Do not change vividhealthsa.co.za DNS records. That's a separate task once everything else is signed off.
- ❌ Do not publish the theme until Gate 2.2 approval.
- ❌ Do not publish individual products until Gate 3.2 approval (keep status=draft on import).
- ❌ Do not enable live Payfast until Gate 5.2 approval.
- ❌ Do not sign up for Payfast / Shopify / any paid service on Naadir's behalf — he registers; you configure.

---

## Acceptance criteria

By end of this task:

1. `vivid-health.myshopify.com` (or chosen handle) exists, theme published, 52 products live in draft, 11 collections live.
2. Payfast tested with at least one R1 transaction that completed end-to-end.
3. Klaviyo Vivid Health list exists, Shopify integration wired, 4 core flows configured.
4. Daily inventory sync running on GitHub Actions, with a successful first run logged.
5. `vivid/launch-checklist.md` committed to the repo with every step's status.
6. `vivid/dns-cutover-checklist.md` committed with the DNS records needed for the eventual cutover.
7. All credentials stored as GitHub repo secrets — never committed in plaintext.

Confirm each acceptance criterion with Naadir via `AskUserQuestion` before declaring done.

---

## Communication style

Speak plainly. Don't narrate every keystroke — just report at gates. If something doesn't go as expected, stop and ask rather than improvise. Naadir wants to be in control of irreversible actions; he's happy for you to drive everything else.

When you ask a question, give him the context, your recommendation, and the trade-off. Make it easy for him to say "do it your way" or pick a specific alternative.

Push to a feature branch — don't push to `main`. Suggested branch: `claude/vivid-shopify-setup`.
