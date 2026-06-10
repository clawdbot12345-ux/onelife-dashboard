# CODEX HANDOFF — Email Imagery + Klaviyo Wiring + Photo Pipeline
**From:** Claude session 2026-06-10 · **Repo context:** reports/klaviyo-audit-2026-06-10.md + reports/klaviyo-wiring-guide-2026-06-10.md

## Mission
Claude rebuilt the Klaviyo program today: full audit, 7 new templates in the 2026
design system (correct brand facts, Engaged-90d targeting, new flow plan). What
Claude cannot do — and you can — is **generate the cinematic imagery** and do the
**Klaviyo UI flow wiring**. That's this brief.

## HARD BRAND RULES (any violation is a bug)
- Delivery: "Free delivery over R400 nationwide" (NEVER R900/R1,400)
- Team: "health consultants" (NEVER coaches/pharmacists)
- 17 consultant-signed protocols (never 15)
- Real codes only: FIRST10, DISPENSARY10, STACK5, STACK10
- Voice: Precious, honest apothecary, no hype
- DO NOT touch Welcome flow Email 1 (R97/recipient — it is sacred)
- NEVER send to the full Email List; campaigns target segment "Engaged 90d" (S3MAsK)

## Part A — Cinematic hero images INTO the 7 new templates
The new templates are deliberately image-light. Add one cinematic hero band each
(1200×600, under the logo header, full-width, descriptive alt text). Match the
established Onelife photography style you created for the site (warm botanical,
amber-hour light, real hands/textures — see vivid/assets/lifestyle/onelife-prompts/
manifest.json for the style language).

| Template (Klaviyo ID) | Hero concept |
|---|---|
| Welcome #2 — Which stack is yours? (YdyAkd) | Overhead apothecary counter, 4 small product groupings on linen, morning light |
| Welcome #3 — Trust (Y9SA46) | Storefront/consultation moment, consultant's hands passing a bottle across counter |
| Post-Purchase #2 — Pairs well (RpUzMu) | Two complementary bottles side by side on warm wood, soft shadow |
| Winback 90d (YatQ6s) | A nearly-empty supplement bottle on a windowsill, nostalgic golden light |
| Winback 120d (XkbgCw) | Quiet minimal shelf with one bottle, calm and unpressured |
| Back in Stock (V8B7p5) | Shelf being restocked, hand placing bottle front-and-centre |
| Abandoned Cart #3 (TtqJqR) | Phone showing WhatsApp chat beside an open basket of supplements |
Use Klaviyo's image upload, then update each template's HTML (keep ALL copy,
facts, links and the {% unsubscribe %} tag exactly as-is — insert the hero <tr>
only). Templates are CODE type.

## Part B — Klaviyo wiring (15-min plan, fully specified)
Execute reports/klaviyo-wiring-guide-2026-06-10.md exactly:
1. Welcome flow XZNrmz: Email 2 → YdyAkd, Email 3 → Y9SA46. First verify in
   Shopify which discount actually exists (WELCOME10 vs FIRST10) and align the
   template code box + flow coupon to reality.
2. Post-Purchase RpJP55: Email 2 → RpUzMu.
3. NEW Winback flow: Placed Order trigger → 60d delay + no-order check →
   existing "Winback 60d" template → +30d → YatQ6s → +30d → XkbgCw. Smart
   Sending on. Live.
4. NEW Back in Stock flow: trigger metric "Subscribed to Back in Stock" →
   immediate email V8B7p5. Live. (Site form + metric already wired.)
5. Abandoned Checkout VAjbpG: add Email 3 (TtqJqR) after 24h; create parallel
   Added-to-Cart abandonment flow (4h delay, filters: no Checkout Started, no
   Placed Order since start) reusing Email 1's template; add the SMS step the
   flow name promises or rename the flow.
6. Archive every campaign named [CODEX INTERNAL TEST]/[CODEX LINK QA]/
   [CODEX GPT IMAGE TEST] (~20) — they pollute reporting.

## Part C — Article hero images (carried-over audit item)
~20 older articles still use screenshots ("Capture.png") or generic Unsplash as
featured images. Generate branded blog-series heroes (style: site's blog-XX
series), upload via Shopify Files, set as featured images. List the 20 by
checking articles whose featured image filename contains "Capture", "unsplash",
or is missing.

## Part D — Product photography pilot (top 50 sellers)
The site now uniforms product images via CSS multiply-blend; true premium needs
clean sources. Pilot: top 50 best-sellers (FROM sales SHOW orders GROUP BY
product_title LIMIT 50), run background removal/cleanup, re-upload as primary
product images at 1200×1200 on pure white. Before/after contact sheet for owner
review BEFORE overwriting — stage as additional images first.

## Report back
Per part: done/blocked, IDs/URLs touched, screenshots of 2 finished email
templates rendered, and the before/after contact sheet from Part D.
