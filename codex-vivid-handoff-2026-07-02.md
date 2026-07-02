# Codex Handoff — Vivid Health World-Class Build (2026-07-02)

**Context:** The owner asked for a complete Vivid Health audit + world-class redesign. Claude has shipped (PR #26, branch `claude/vivid-health-audit-redesign-9fmzon`): the full audit, the redesign blueprint, brand research, a hi-fi mockup, **and — via the `vivid claude review` app token (SHOPIFY_ADMIN_TOKEN secret) — live store fixes**: 50 product renames to the new 6-range architecture (typos NUTRITENT/Colest Control/Angus Castus fixed, `range:*` tags added, rollback in `vivid/backend/rename-backup.json`), corrected CoQ10/MSM copy, and a rebuilt Vivid landing snippet that renders prices/stock live (ghost SKU gone, price drift gone, emoji → SVG) applied to both the live theme and the 2026-07-02 draft theme.

**Read first:** `vivid-health-redesign-blueprint-2026-07-02.md` (the target state) · `vivid-health-audit-2026-07-02.md` (why) · `vivid/redesign-mockup.html` (what it should look like — open in a browser, toggle "Design notes") · `reports/vivid-feature-catalog-2026-07-02.md` (apps + pricing).

This document is ONLY what Claude could not do from here. Work top to bottom.

---

## 1. Verify Claude's applied changes (10 min) 🔴 FIRST

1. Open `https://onelife.co.za/collections/vivid-health` — confirm: product cards show the new "Vivid X — benefit · size" names, stack cards show live prices with SVG icons (no 🦠/🛡️ emoji), **Immunity Shield** stack contains *Buffered C 90* (not the 404 Advanced Buffered C 90) and adds to cart cleanly with VIVID10 applying 10%.
2. Spot-check PDPs: CoQ10 (`/products/vivid-health-vivid-body-coenzyme-q10-60-capsules`) must talk about cellular energy/heart — NOT probiotics; MSM 90 must have the new copy.
3. Check `vivid/backend/apply-result.json` on the branch for any non-2xx statuses and flag them.
4. If anything looks broken: the exact previous snippet contents are in `vivid/backend/theme-185669910838/` (pre-patch pulls) and old titles/tags in `vivid/backend/rename-backup.json`.

## 2. App scopes to add (Settings → Apps → Develop apps → vivid claude review) 🔴

Current scopes lack: **`read_locations`** (locations API returned 403 — needed for per-store stock features), **`read_files`/`write_files`** (Files API for uploading new bundle artwork), **`read_publications`/`write_publications`** (sales-channel publishing), and **`read_metaobjects`/`write_metaobjects`** (needed for the batch-COA lookup build). Add these + reinstall; no token rotation needed unless Shopify forces it (if it does, update the `SHOPIFY_ADMIN_TOKEN` Actions secret).

## 3. Bundle artwork with baked-in stale prices 🔴 (audit C6)

The 3 bundle products (Allergy R654 / Bone & Joint R929 / Rest & Focus R663) have hero images with OLD prices rendered into the artwork (R594.72 / R742.66 / R587.67-SAVE-R65). Regenerate the three images **without any price text** (keep the product-lineup composition), or crop the price band out. Claude can't generate/upload images from this session (no Files scope + no image generation). Source renders are on the product pages; repo prompts in `codex-image-prompts.md` follow the house style.

## 4. Domain & naming decision (owner call — present the options)

`vividhealth.co.za` is owned by an unrelated practitioner (Vivienne Pietersen — herbal/Rife/ultrasound practice, incl. cancer-adjacent claims: **brand-adjacency risk**). Options to put to the owner: (a) attempt to buy the domain; (b) `vivid.co.za` / `getvivid.co.za` / `vividhealth.shop` — check availability at a registrar; (c) keep Vivid as a flagship section of onelife.co.za (zero new SEO investment — the blueprint works either way). Blocked until decided: any dedicated-store launch, Search Console setup.

## 5. Draft store / theme intent (ask the owner, 1 question)

The store has 20 themes; the freshest unpublished one is `185669910838` "ONE LIFE HEALTH STORE — LIVE 2026-07-02". Confirm with the owner that this is the "draft" they meant for the Vivid redesign work. If they meant a *separate dev store*, get its myshopify domain + a token and add them as `VIVID_STORE` repo variable + a token secret — the `vivid-ops` workflow already supports it.

## 6. Batch-certificate (COA) programme — the flagship feature

1. **Owner/manufacturer:** request per-batch certificates of analysis (identity, potency, heavy metals, micro) from the SA contract manufacturer (MJ Labs / SA-Labs per the growth playbook). This is the highest-leverage phone call of the launch.
2. Once even ONE batch's PDF exists: hand it to Claude — the lookup page (metaobjects + a small section) is spec'd in the blueprint §6 and Claude can build it via the vivid-ops pipeline (needs the metaobject scopes from §2).
3. Next label print run: add the QR pointing at `/pages/batch-lookup?b=<batch>`.

## 7. Subscriptions (Appstle) — first mover window is open

Install **Appstle Subscriptions** (Business plan $30/mo), enable on the top 10 Vivid SKUs (Buffered C, 5-HTP, MSM, CoQ10, Immune Plus, Turmeric, Maca, Flexijoint, Tranquil, Omega Oil) at **10% off + free delivery**, cancellation-save flow ON, dunning ON. Then tell Claude — the PDP subscription widget styling and the landing-page Subscribe & Save band are designed in the mockup and Claude can build the theme side.

## 8. Reviews engine (same as Round-1 item 6 — still not done)

Judge.me: enable post-purchase review request (~14 days after fulfilment, REVIEW25 incentive) + backfill request to the last 60 days of orders. Every Vivid SKU shows "No reviews" — this single switch fixes the biggest premium-killer on the PDPs.

## 9. Payments & delivery (checkout-level, admin UI only)

Per blueprint §7: add **Payflex** and/or **PayJustNow** (Shopify plugins), **Ozow** as EFT option, and install **Bob Go** for Courier Guy + Pudo/Pargo pickup points. Also still open from Round 1: Meta + TikTok pixels via the channel apps, POPIA un-tick of pre-checked consent, checkout logo swap.

## 10. Explicitly owner-level (don't start without sign-off)

Price rounding across the range (odd cents like R170.77 are likely POS-sync artifacts — confirm the sync direction first or changes will be overwritten); retiring/restocking the 5 sold-out SKUs; Takealot billboard listing; the Founding-100 launch date; consultant photos/bios sign-off for the protocol pages.

---

## What Claude will do next (no action needed, listed so you don't duplicate)

Once scopes (§2) land: batch-lookup page build (after §6.2), "The honest bit" + accordion rollout across all 55 PDP descriptions, collection consolidation (`brand-vivid-health` → redirect to `vivid-health`), retiring the dead `?view=vivid-guide` template, and the draft-theme homepage sections per the mockup. Trigger channel: the `vivid-ops` workflow on the PR branch (pull/apply modes documented in `scripts/vivid_ops.py`).

## Definition of done for this round

- [ ] §1 verification pass on the live Vivid landing + 2 PDPs
- [ ] Scopes added to the vivid claude review app
- [ ] 3 bundle images re-exported without baked prices
- [ ] Domain options + theme-intent question put to the owner
- [ ] COA request sent to the manufacturer
- [ ] Appstle installed on top-10 Vivid SKUs
- [ ] Judge.me post-purchase requests live + 60-day backfill
- [ ] Payflex/PayJustNow + Ozow + Bob Go installed
