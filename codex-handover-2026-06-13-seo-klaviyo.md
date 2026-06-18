# Codex Handover — SEO + Klaviyo (2026-06-13)

From: Claude session (owner-authorised "do it all" run).
Repo: `clawdbot12345-ux/onelife-dashboard` · Branch with my changes:
`claude/seo-audit-findings-2vnstq` (PR #18). Store: onelife.co.za ·
**Live (MAIN) theme: 186060112182** ("ONE LIFE HEALTH STORE — AUDIT FIXES
2026-06-13").

**Cart add-to-cart alignment: you're already on it — I'm not touching it.**
See the one FYI in §4 so you don't lose time on the root cause.

---

## 🔴 0. DO FIRST — Browse Abandonment complaint (customer unsubscribed)

A customer got a "Still thinking about {{ product }}? 👀" email minutes after
searching the site, felt surveilled, and unsubscribed publicly. Owner wants it
fixed. **This is a 2-minute Klaviyo UI edit** — flow timing/filters are UI-only
(no API/MCP write exists, so neither Claude nor a script can push it).

Flow: **"Browse Abandonment v2" → ID `UMMzhC`** → https://www.klaviyo.com/flow/UMMzhC/edit
Full spec + research + sources: `reports/browse-abandonment-fix-2026-06-13.md`. TL;DR:
1. Time delay **2h → 72h (3 days)** (owner request).
2. **Add frequency cap — the real fix:** flow filter **"Has not been in this flow
   in the last 30 days."** This is what stops the "email every time I search".
3. Soften the subject (drop `Still thinking about {{ event.Name }}? 👀`) to a light,
   non-watching line; keep Smart Sending on.
4. Consent audit: the complainer felt they never opted in — review how profiles get
   email-marketing consent (single-opt-in Email List Xrk5jD, checkout) for POPIA.

Owner has the apology reply drafted (in chat) to send the customer.

---

## 1. What I already shipped (do NOT redo)

**Live on the store now (Admin API, owner client-credentials app — 0 errors):**
- **9 dietary/certification collection descriptions** (handles: vegan,
  vegetarian, gluten-free, sugar-free, dairy-free, keto, organic, halaal,
  kosher) — were blank.
- **109 placeholder product descriptions** ("contact us for more info")
  replaced with compliant, varied copy (brand + format + dietary tags + NAP +
  "check the label" note). Target list was the audit's `description_placeholder`
  findings.
- **18 product `apothecary.faq` metafields** seeded (every product featured in
  the blog campaigns) — see §3 for the mechanism.

**In the repo / PR #18:**
- Blog pipeline (`scripts/publish_blog.py`): tables, product-comparison table,
  FAQ + references, and JSON-LD — but **only Breadcrumb + FAQPage** (the theme
  already emits Article schema; I removed a BlogPosting duplicate I'd added).
- `scripts/seo_audit.py`: new article content checks; **no_schema check removed**
  (false positive vs theme-level schema).
- `content/{queue,blogs,published}/*.md`: added `faq:` + `references:` to 8
  articles.
- `content/email/review-request-precious.html`: ready-to-paste review email.
- `reports/seo-audit-2026-06-13.{md,json}`: fresh full-catalog audit.
- `reports/seo-audit-response-2026-06-13.md`: full session log.

---

## 2. KLAVIYO — blocked for me, needs you (UI access)

The hosted Klaviyo MCP in my session gates all **write** + **metrics** tools at
the gateway with no approval channel, so I could read but not act. All live
verified: 22 flows live (Welcome, Browse, 2× cart, Post-Purchase x-sell,
Replenishment, Winback 60/90-120, Back-in-stock, Sunset, full loyalty suite);
main Email List (Xrk5jD) is now single opt-in. Remaining gaps:

1. **Review-request flow (NEW — none exists).**
   - Template: paste `content/email/review-request-precious.html` (Templates →
     Code editor). CTA uses `{{ event.extra.review_url|default:'…/account' }}`.
   - Flow: trigger **Fulfilled Order** (or Placed Order + 10–14 day delay so the
     product's been used); filter out anyone who already reviewed; smart-sending
     on; send to engaged. Wire the CTA to the Judge.me review link if you pass it
     on the event.

2. **SMS (zero usage today).** Text Messaging List S44qNc exists (double opt-in)
   but no SMS has ever sent.
   - Register an SA sender number + consent in Klaviyo.
   - Add an SMS step to the cart flow **WY4cae** ("Abandoned Checkout Consultant
     Check") and to back-in-stock **WT9YvU**. Cart-recovery SMS is a top lever at
     ~R650 AOV.

3. **List-growth capture (the #1 lever — likely still broken).** As of the
   2026-06-10 audit: ~5 form views / 0 submissions in 3 months on 40k
   sessions/mo; Welcome flow (R97/recipient) got only 174 people in 90 days.
   - Build a Klaviyo signup **popup + footer embed + exit-intent** with FIRST10,
     wired to Email List **Xrk5jD**. This is Forms-UI + a theme placement.
   - **Verify the live numbers first**: metric "Subscribed to Email Marketing"
     and form submissions, last 30 days — confirm whether it recovered.

4. **Campaign discipline:** default sends to Engaged 90d (S3MAsK), cap full-list
   at ~2/mo, alternate value vs revenue emails. Quiz fires "Blog Quiz Result"
   but no flow consumes it (zero-party data wasted).

---

## 3. SEO — what's left (Shopify; I did the reachable parts)

- **Product FAQ rollout (scale beyond 18).** Mechanism: set metafield
  `namespace=apothecary, key=faq, type=json`, value = JSON list of `{q,a}`. The
  theme's `snippets/seo-product-schema.liquid` renders a visible FAQ accordion +
  FAQPage schema whenever it exists. My seeder is `/tmp/faq_seed.py` (pattern in
  PR history) — extend to top sellers / per-category FAQ sets. Keep answers
  honest, POPIA/SAHPRA-safe ("support", not "treat").
- **168 collections with no image** (audit `no_image`). Needs real image assets —
  I can't generate store imagery. Many map to existing theme heroes
  (`assets/onelife-collection-*-hero.jpg`); the long tail needs new art.
- **1,138 active-but-OOS products** (`active_but_oos`) — merchandising decision:
  hide/redirect vs restock. Not auto-toggled.
- **Theme Check lint** (email-signup-banner + header parser) — still needs a
  `shopify theme check` CLI pass; checklist in `codex-theme-fixes-2026-06-13.md`.
- Re-run `scripts/seo_audit.py` after changes to confirm deltas. NOTE: the
  theme already emits Article + Product JSON-LD, so ignore any body-level
  "schema" worry — don't add duplicate schema in product/article HTML.

---

## 4. FYI for your cart-alignment work (context only — it's yours)

The "Frequently Added" block is the **cart page `upsell` section** in
`templates/cart.json` (a `featured-collection`, `swipe_on_mobile: true`)
rendering `card-product`. With `quick_add: "standard"` the visible button is
**`.ol-card-action`**, which sits **inside `.card__information`**
(`flex:0 0 auto` in `assets/onelife-grid-fixes.css`), so 2- vs 3-line titles
misalign the buttons.

⚠️ **What NOT to do:** I tried scoping a `body.template-cart` rule that forced
`.card__information { display:flex; flex:1 1 auto }` + `margin-top:auto` on the
button. On the **mobile swipe slider** that collapsed the cards and **hid the
whole Frequently Added row**. I reverted it — `assets/onelife-grid-fixes.css` on
186060112182 is back to its original 13612-byte state (verified). A safe fix
likely needs equal-height handling that survives the slider, or clamping the
title height, verified in a real browser.

---

## Definition of done for you
- [ ] Review flow live (template + Fulfilled-Order trigger)
- [ ] SMS sender registered; SMS step in WY4cae + WT9YvU
- [ ] Signup forms live (popup/embed/exit-intent → Xrk5jD); signup rate verified
- [ ] Cart add-to-cart aligned (your task) + browser-verified
- [ ] Decision logged on 168 collection images + 1,138 active-OOS
- [ ] (Optional) FAQ metafields rolled out to top sellers
- [ ] PR #18 merged
