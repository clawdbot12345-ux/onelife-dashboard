# Codex Handover R3 — 2026-07-02
**Scope rule:** this list contains ONLY what Claude cannot execute (image
generation, Shopify admin-UI clicks, preview QA, external accounts). All
theme code, Liquid/CSS, Klaviyo API work, product-image wiring, pages and
copy are Claude's lane — do not duplicate.

## 1. Image generation — GPT-image-2.0 (the big job)
Follow `codex-image-artdirection-2026-07-02.md` exactly (visual system,
prompt templates, label-fidelity QA, naming). Priority order:
1. **Brief A** — product background unification, image-to-image with real
   packshots as input. Start: the 8 margin heroes, then top-100 sellers,
   then the Vivid range. QA every output against the checklist (label
   pixel-faithful, no invented text) before upload.
2. **Brief B** — 17 protocol editorial heroes (scenes 11–17: propose to
   Claude for sign-off before generating).
3. **Brief C** — Vivid brand stage. 4. **Brief D** — homepage hero.
5. **Brief E** — 10 wordmark concepts (direction material only; owner
   commissions a designer for the vector redraw).
**Protocol:** upload to Shopify Files with the specified names, in batches
of ~20 → ping Claude → Claude wires them into products/theme.

## 2. Theme preview QA + publish (recurring, per pass)
Claude ships passes as unpublished themes named "... (publish me)".
For each: run your preview visual audit (as done for the mobile-fixes
publish), spot-check the pass's change list on mobile, then publish.
**Next up: "PREMIUM PASS 1 — 2026-07-02 (publish me)"** — check: protocol
tiles now cream/green (no pastels), no emoji on quiz/goal cards, stat bar
gone from non-home pages, blue links gone, card hover motion works, nothing
visually broken. Publish if clean; report anomalies to Claude, don't fix
theme code yourself.

## 3. Shopify admin-UI settings (no API path on this plan)
1. **Checkout branding** (Settings → Checkout → Customize): cream
   background, deep-green (#10261F) buttons/accents/focus rings, current
   green wordmark at 2x resolution. Kills the default blue/purple at the
   money moment. 30 minutes, highest-value click in this document.
2. **Rewards page**: embed the real Smile launcher (Smile app settings) or
   rewrite the page copy to match reality; restyle teal gradient to brand.
3. **Analyzify**: open the support ticket asking why Google tag requests
   are injected while Google Ads/GA4 integrations show disconnected
   (double-gtag issue), and whether embeds can run async/deferred.

## 4. External accounts
1. **Google Ads** (after owner 2FA): Rhodes PMax script output saved to
   repo; ONE primary Purchase action; brand exclusions on PMax; pause
   "One Life Launch" (R233/purchase brand campaign) and the Maximise-Clicks
   Shopping campaign per reports/roas-analysis-june-2026.md.
2. **Klaviyo ↔ WhatsApp** (with owner): connect the WhatsApp Business
   number (Settings → WhatsApp), register templates per
   content/marketing/marketing-activation-sprint-2026-07.md Kit 2. Claude
   takes over flows/broadcasts once the channel shows connected.
3. **Creator discount codes**: create 10% codes named OL-[CREATORNAME] as
   creators are confirmed (admin → Discounts).

## Do NOT
- No theme code/CSS/Liquid edits (Claude's pipeline owns the theme).
- No Klaviyo flow/campaign/segment changes.
- No product data edits beyond uploading generated images to Files.
- Never publish a theme that fails your preview audit.

## Done ledger (context — don't redo)
Premium Pass 1 built & awaiting your QA/publish · discipline CSS + quiz
emoji strip shipped · art-direction brief committed · prices rounded (2,643)
· search boosts live · data hygiene done · checkout ladder + all flows
verified · GLP-1 series queued · activation sprint written.
