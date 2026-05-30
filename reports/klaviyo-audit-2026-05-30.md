# Onelife Health — Klaviyo Email Marketing Audit

**Date:** 2026-05-30 · **Account:** `onelifehealth` (Klaviyo `S86r7e`) · **Currency:** ZAR · **Timezone:** Africa/Johannesburg
**Scope:** End-to-end audit of the live Klaviyo account — deliverability, campaigns, flows, list growth, segmentation, content, branding/design, compliance — benchmarked against leading health & wellness DTC brands.
**Data source:** Live Klaviyo API (via MCP), pulled 2026-05-30. Account has been active since ~20 Feb 2026, so "last 12 months" figures effectively cover **~3.5 months (Feb–May 2026)**.

---

## 0. TL;DR — the 10 things that matter

1. **🔴 The dashboard everyone looks at shows all zeros.** `DASHBOARD_DATA.klaviyo` and the narratives read "0 subscribers, 0 opens, R0 revenue." The live account is healthy and active. The daily refresh is silently publishing zeros. **Fix first — you are flying blind.**
2. **🟠 Your brand name is inconsistent in the inbox** — the "From" name flips between **"One Life Health"** and **"Onelife Health"**. Pick one (the domain is `onelife.co.za` → **"Onelife Health"**) and lock it everywhere.
3. **🟢 Flows are excellent and under-exploited.** Welcome flow: **54% open, ~24% conversion on email 1, R221 revenue/recipient.** Abandoned Checkout R19.77/recipient, Browse Abandonment R17.44/recipient.
4. **🟡 Campaigns get great opens (~30%) but weak clicks (1–2%) and almost no direct conversions** (0–2 orders each). Content is strong; targeting and CTAs are the problem.
5. **🟠 You're emailing the wrong (small) list.** Campaigns go to **"Email List" = 768 profiles**, but **"At-risk 60d" = 2,133 consented buyers** who aren't being reached. Thousands of opted-in customers are missing from your sends.
6. **🟡 Deliverability warning signs.** Several campaigns bounced **4–6%** (healthy is <2%). List hygiene + the new sunset flow need to actually run.
7. **🟢 Segmentation is well-built but barely used historically.** Good segments exist (VIP/High-LTV, Engaged-90d, GLP-1, store-proximity) — only the newest "JJA 2026" drafts finally target them.
8. **🟡 Post-Purchase Thank-You + Cross-sell flow = R0 (0 conversions)** despite 52% opens. Broken CTA/offer — fix or rebuild.
9. **🟢 Email design is genuinely good** (on-brand green, evidence-led, store/delivery footer, plain-text version) — but has a **preview-text-printed-in-body bug**, no product images, no reviews/social proof, and **no SMS** despite an SMS list existing.
10. **🧹 The account is messy.** Dozens of `[CODEX QA]`, `[CODEX LINK QA]`, `[CODEX INTERNAL TEST]` campaigns, ~10 junk QA lists, and many cancelled duplicate campaigns. Clean it up so reporting is trustworthy.

**Estimated email share of revenue today: ~10%** (≈R34k email-attributed vs ≈R341k total store revenue, Feb–May). Best-in-class wellness brands run **25–35%+**. The gap is the opportunity.

---

## ✅ Changes applied in this session (2026-05-30)

**Code (in this PR):**
- **Refresh script hardened** (`scripts/refresh_dashboard.py`): added a **zero-write guard** (aborts instead of publishing all-zeros when the API fetch fails), **bumped the API revision** `2024-10-15 → 2025-07-15`, and added a **reachable-base calculation** so the dashboard now exposes the 768-vs-consented gap (`marketable_consented_estimate`, `engaged_90d`, `at_risk_60d`) and calls it out in the narrative.

**Live Klaviyo account (safe / reversible — nothing sent):**
- **Built a draft re-engagement campaign** — *"Re-Engagement — We Miss You (At-risk 60d) — DRAFT for review"* (campaign `01KSWBSGQWJ313VRDNDJZRTJ33`) targeting the **At-risk-60d segment (2,133 consented buyers who currently receive no campaigns)** — directly closing the 768-vs-2k reach gap.
- **New on-brand template** *"OL — Re-Engagement — We Miss You"* (`Xt4xgS`): correct **"Onelife Health"** branding, single hero CTA, welcome-back free-delivery incentive, store footer, compliant unsubscribe, `{{ first_name }}` personalisation.
- Left as a **Draft** (no send strategy) so you review/approve before it goes out — and so it can be **throttled** (recommend 25%/hr) to protect deliverability when sending to a long-dormant segment.

**Requires you / the team (no API available, or outward-facing):**
- Rotate/verify the GitHub Actions `KLAVIYO_API_KEY` secret + scopes (root cause of the zeros).
- Set the **account default sender name to "Onelife Health"** (Settings → Account; can't be changed via API).
- **Send/approve** the re-engagement draft (outward-facing — left for you).
- Make **Engaged-90d + At-risk-60d** (or a new "Email Marketing Consent = subscribed" segment) the standard campaign audience instead of "Email List."
- Archive the `[CODEX QA]` / test campaigns & lists (no archive/delete API exposed).

---

## 1. Account snapshot (live)

| Item | Value |
|---|---|
| Main list ("Email List") | **768 profiles**, double opt-in |
| Consented base (implied by segments) | **2,000+** (At-risk-60d alone = 2,133 consented buyers) |
| New email subscribers / month | ~23 (Feb) → 26 (Mar) → 44 (Apr) → 19 (May, partial). **Slow growth (~30/mo).** |
| Live flows | **18** |
| Segments | 10 (well-constructed) |
| Sender | `info@onelife.co.za`, label **"One Life Health" / "Onelife Health"** (inconsistent) |
| Integrations | Shopify, Smile Loyalty & Rewards, custom API events (blog tracking, quiz) |
| Store revenue Feb–May 2026 | R65.4k → R73.1k → R101.0k → R101.5k = **~R341k**; orders 80→94→193→162 |

**Read:** the store is growing nicely and the foundations (flows, segments, loyalty, blog-event tracking) are surprisingly mature for a 3-month-old setup. The problem is **activation and hygiene**, not absence of infrastructure.

---

## 2. Critical issues (fix this week)

### 2.1 🔴 Dashboard is publishing zeros
- **Symptom:** `index.html` → `DASHBOARD_DATA.klaviyo` / `DASHBOARD_DATA.shopify` and both narratives are all `0`. (e.g. *"You have 0 active email subscribers… 0 opens (0% open rate)… Email-attributed revenue: R0."*)
- **Root cause:** `scripts/refresh_dashboard.py` has no failure guard. If the Klaviyo calls fail wholesale (expired/missing `KLAVIYO_API_KEY` secret, or the pinned `revision: 2024-10-15` being rejected), every helper returns `None` → defaults to `0`, and the script **still rewrites the HTML with zeros** (it only `sys.exit(1)`s when the key env var is absent, not when fetches fail).
- **Proof it's a pipeline bug, not an empty account:** the same data pulls cleanly via the Klaviyo MCP (newer API revision).
- **Recommended fixes:**
  1. Add a sanity guard before writing: `if total_subscribers == 0 and recv == 0 and not campaign_reports: sys.exit(1)` (fail loudly, keep last good data).
  2. Verify the GitHub Actions `KLAVIYO_API_KEY` secret is present and has scopes: Metrics(Read), Campaigns(Read), Flows(Read), Lists(Read), Segments(Read), Profiles(Read).
  3. Bump `revision` to a current date (e.g. `2025-07-15` or later) and log non-200 responses as a hard error.
  4. Add a CI assertion / alert when a refresh produces a >50% drop in subscribers or revenue vs the prior committed value.

### 2.2 🟠 Brand-name inconsistency
The "From" label and in-copy name alternate between **"One Life Health"** and **"Onelife Health"** across campaigns (and the subject of one even differs from its own from-label). The domain, logo, and footer use **"Onelife Health"** (one word). The "From" name is the single most-seen piece of brand in the inbox and a recognised driver of open rate and spam-folder trust.
- **Action:** Standardise to **"Onelife Health"** everywhere — sender profiles, templates, flow messages, footers, alt text. Add it to a brand style note so future content doesn't drift.

### 2.3 🟠 Campaigns target the small list, not the consented base
Every historical campaign's audience = **"Email List" (768)**. Meanwhile **2,133 consented buyers** sit in "At-risk 60d" (and the broader Engaged-90d segment is 802). Many buyers opt in at Shopify checkout but never land on "Email List," so they receive **flows but no campaigns** — which is partly *why* they drift to "at-risk."
- **Action:** Build a master **"All Consented (Email)"** sending segment (email marketing consent = subscribed), and target campaigns at engagement-tiered segments off that base, not the legacy list.

---

## 3. Performance analysis

### 3.1 Deliverability
| Metric | Onelife | Healthy target |
|---|---|---|
| Delivery rate | 94–99.7% (varies) | >99% |
| Bounce rate | **0.3% – 6.1%** (several sends 4–6%) | <2% (ideally <1%) |
| Spam complaint rate | ~0% | <0.1% ✅ |
| Unsubscribe rate | 0.1–1.0% | <0.2–0.3% (some sends high) |

**Issue:** the high-bounce sends (e.g. 6.1%, 4.2%, 4.4%) indicate stale/unverified addresses entering sends. Repeated >2% bounce erodes sender reputation for *everyone*.
**Actions:** (1) Make sure the **Sunset Unengaged** flow (created 5 May) is actually live and suppressing; (2) add a **bounce/invalid suppression** + never email addresses that hard-bounced; (3) confirm DKIM/SPF/DMARC are aligned on `onelife.co.za`; (4) consider a one-time list-validation pass.

### 3.2 Campaigns (Feb–May, ~22 real sends)
- **Open rate:** ~27–43% (mostly ~30%). **Strong**, even allowing for Apple MPP inflation.
- **Click rate:** **0.5–4.2%, typically 1–2%.** **Weak** — this is the core campaign problem.
- **Click-to-open:** ~3–8%. Low — opens aren't converting to clicks.
- **Direct conversions:** typically **0–2 orders per campaign**; total campaign-attributed revenue ≈ **R9,079** across all sends.
- **Best performers (signal):**
  - *"Can't sleep? Here's what's actually worth trying"* — **4.17% click / 12.5% CTOR** (best CTR; problem-led subject, no emoji).
  - *"Friday Product Spotlight — Herbamare"* — **R3.41 revenue/recipient** (highest; single-product focus converts).
  - *"Magnesium Forms"* — 3.7% click. Specific, useful, single-topic.
- **Read:** great hooks get the open; then a single blog link (or a wall of product links) fails to drive clicks/sales. **Campaigns are content-rich but commerce-poor.**

**Actions:**
1. **One email = one job.** Lead with a single hero offer/product and one primary CTA above the fold; move "read the full guide" to secondary.
2. **Add product cards with images, prices, ratings, and "Add to cart"** (Klaviyo product blocks) — current emails are text-link lists with *no product imagery*.
3. **Segment by topic intent** (e.g. send Magnesium content to magnesium buyers/browsers) rather than blasting all 768.
4. **A/B test subject + CTA**; bank the winners. Problem-led, no-emoji subjects are out-performing "Blog: …" and emoji subjects.
5. **Tighten send cadence to the engaged**, suppress the chronically unopened.

### 3.3 Flows (the strength)
| Flow | Recipients | Open | Click | Conv | Rev/recipient | Revenue |
|---|---|---|---|---|---|---|
| **Welcome (Full Sequence)** | 121 | **54%** | 10.8% | **10.8%** | **R97.7** (email 1: R221) | **R11,730** |
| Abandoned Checkout (Email+SMS) | 252 | 47% | 5.7% | 2.4% | R19.77 | R4,883 |
| Browse Abandonment v2 | 205 | 33% | 6.9% | 2.0% | R17.44 | R3,523 |
| PCOS Post-Purchase | 217 | 44% | 2.8% | 1.4% | R8.72 | R1,884 |
| Points Balance Nudge | 187 | 51% | 5.5% | 0.5% | R3.82 | R694 |
| **Post-Purchase Thank-You + Cross-sell** | 160 | **53%** | 4.5% | **0%** | **R0** | **R0** |
| GLP-1 Education Drip | 19 | 47% | 0% | 0% | R0 | R0 |
| GLP-1 Non-Opener Follow-up | 47 | 49% | 4.3% | 0% | R0 | R0 |

**Total flow-attributed revenue ≈ R25,369** (≈74% of email revenue, from ~26% of email volume). Flows are doing the heavy lifting — exactly as it should be, but the *mix* is thin.

**Actions:**
1. **Fix Post-Purchase Thank-You + Cross-sell (R0 at 53% opens).** The audience is reading and not converting — broken CTA, irrelevant cross-sell, or no incentive. Rebuild with: genuine "how to use it" education (matches your strong post-purchase education drafts) → a *relevant* cross-sell with a first-reorder incentive.
2. **Build a true Replenishment/Subscription flow.** You sell consumables (magnesium, vitamin D, collagen) with predictable run-out. A "Replenishment Reminder" exists but barely shows volume — make it dose-aware (e.g. 30/60/90-cap packs → remind at ~80% depletion) and add a one-tap reorder. This is the single biggest LTV lever for a supplement store.
3. **Win-Back has no profiles wired in** (the narrative's win-back segment is empty). Build a 3-step win-back off "At-risk 60d (2,133)" → escalate offer. Even 2% × ~R600 AOV ≈ **R25k** recoverable.
4. **GLP-1 drips get opens but zero clicks/conv** — add concrete product bundles + dosing guidance and a clear CTA; this is a high-intent, high-margin niche.
5. **Add post-purchase review-request** (feeds social proof you currently lack).

### 3.4 Revenue attribution summary
- Flows ≈ **R25.4k** · Campaigns ≈ **R9.1k** · Email total ≈ **R34.5k**
- Store total (Feb–May) ≈ **R341k** → **email ≈ 10% of revenue**.
- **Benchmark: 25–35%+** for mature wellness DTC. Closing half that gap ≈ **+R25–40k/quarter** at current traffic.

---

## 4. List growth & segmentation

**Growth:** ~30 new subs/month is low for the traffic implied by 193 orders/month. The site clearly has signup forms (Form events exist) but capture is weak.
**Actions:** stronger signup incentive (first-order % or free-delivery threshold unlock), a **quiz-based capture** (you already fire `Blog Quiz Result` events — turn it into a "find your supplement" lead magnet), exit-intent + post-purchase consent, and in-store QR → email/SMS capture across Centurion / Glen Village / Edenvale.

**Segments (good, underused):**
| Segment | Size | Note |
|---|---|---|
| At-risk 60d | **2,133** | Big disengaged/win-back pool; main suppression + win-back target |
| Engaged 90d | 802 | Your real "send campaigns here" core |
| VIP / High-LTV (3+ orders or >R2,500) | 98 | Deserves its own VIP track + early access |
| GLP-1 / Metabolic | — | High-intent niche; under-monetised |
| Store-proximity (Glen Village, Parkview) | — | **Local-event / click-and-collect** potential, unused |
| Engaged Browsers (no purchase) | 27 | Too tight (≥3 views/30d) — loosen to ≥1 |
| Buyer — Magnesium / Joint Mobility | — | Topic cross-sell targeting |

**Actions:** wire campaigns to **Engaged-90d** as default; create a **VIP** lifecycle (early access, samples, loyalty perks); use **proximity segments** for store events & click-and-collect; build **replenishment/cross-sell** off the Buyer-X segments.

---

## 5. Content & topics

**Strengths (keep doing):**
- **Genuinely SA-localized & credible:** *"what our pharmacists actually recommend," "Gauteng winters," "the Highveld's worst allergy months,"* real dosing, "no hype, no miracle claims." This is your differentiator vs generic global brands.
- **Strong, curiosity/problem-led subject lines:** *"Still tired after sleeping? It might not be your sleep," "You take magnesium. The type still decides the result," "Berberine — Is 'Nature's Ozempic' actually worth the hype?"*
- **Good topical breadth & timeliness:** seasonal immunity, sleep, gut health, women's health, kids, longevity (NAD+/NMN), trend-jacking (GLP-1, berberine, creatine-for-women).
- **Forward planning:** the "JJA 2026" calendar of drafts targeting Engaged-90d is exactly the right direction.

**Gaps:**
- **Too education-heavy, not enough commerce.** Most sends are "Blog: …" with one link. Balance toward the **80/20 rule** (80% value / 20% promo) *but make the 20% real* — bundles, hero products, limited offers, restocks.
- **No social proof / UGC / reviews** anywhere. Add review stars, testimonials, "best-seller in [category]," pharmacist quotes.
- **No clear seasonal/promo calendar tied to revenue moments** (payday sends ~25th–1st, Black Friday, Jan "reset," winter immunity peak). The "Fuel went up, your delivery didn't" campaign shows you *can* do timely promo well — do more.
- **Emoji-in-subject inconsistency** — your best CTRs came from clean, no-emoji, problem-led subjects. Standardise.

---

## 6. Branding & design

**Reviewed flagship template ("Winter Immunity Stack"):**
- ✅ On-brand deep green (`#1B5E20`), logo header, clean single-column 600px, mobile-friendly table layout.
- ✅ Evidence-led copy with real dosing and pharmacist framing.
- ✅ Footer with **store list + free-delivery thresholds (R900 Gauteng / R1,400 nationwide)** and a working unsubscribe.
- ✅ Proper plain-text alternative (good for deliverability).
- 🐛 **Preview text is printed as a visible line inside the body** (*"Preview text: Three supplements…"*) — remove; set it as the actual Klaviyo preview field only.
- ❌ **No product images** — text links only. Add product cards (image, price, rating, button).
- ❌ **No trust signals**: no review stars, no "third-party tested," no certifications/ingredient-transparency badges, no founder/pharmacist photo.
- ❌ **Template names are junk** ("Clone of RVvcuD") — adopt a naming convention (`OL — [Type] — [Topic] — vN`).
- ❌ **No SMS** despite a Text Messaging list existing — at least add SMS to Abandoned Checkout & Welcome (you already have the Email+SMS abandoned flow as a template).

**Brand system to formalise:** logo lockup + "Onelife Health" wordmark, primary green + accent palette, heading/body type, button style, product-card component, standard footer (stores, delivery, social, unsubscribe, physical address — already compliant), and a reusable hero/review block. Bank these as **Universal Content blocks** so every email is consistent.

---

## 7. Compliance (health claims) — high level

Supplements are regulated; email copy is marketing and is in scope.
- **South Africa:** SAHPRA regulates complementary/health-supplement claims; the ARP/Code of Advertising Practice prohibits unsubstantiated health claims. Avoid implying diagnosis/treatment/cure of disease.
- **Tone to keep:** your current "structure/function + evidence + dosing, no miracle claims" style is the right register. Keep claims tied to credible evidence ("two clinical trials have shown…") and avoid disease-cure language (e.g. around GLP-1/Ozempic adjacency, PCOS, immunity).
- **Action:** add a light **claims-review checklist** to the content workflow, and a standard disclaimer line in the footer ("These statements have not been evaluated by SAHPRA; not intended to diagnose, treat, cure or prevent any disease"). Keep affiliate/pharmacist credentials accurate.

*(Confirm specifics with your regulatory contact — this is guidance, not legal advice.)*

---

## 8. Benchmark vs leading health & wellness brands

> Competitive benchmark detail (Klaviyo Health & Wellness vertical figures + named-brand tactics with citations) is being compiled by a parallel research pass and will be appended in §8.1. Summary positioning below.

**Where Onelife stands today vs best-in-class supplement DTC (Ritual, AG1, HUM, Seed, Care/of, Thorne, etc.):**

| Dimension | Best-in-class | Onelife today | Gap |
|---|---|---|---|
| Email % of revenue | 25–35%+ | ~10% | **Large** |
| Welcome series | 4–6 emails, story + science + offer + social proof | 1 strong sequence, converting well | Extend & add SMS |
| Subscription/replenishment | Core LTV engine (auto-reorder, discounts) | Reminder flow, low volume | **Biggest miss** |
| Social proof / reviews | Reviews, UGC, clinical/3rd-party testing front-and-centre | None in email | **Large** |
| Personalisation/quiz | "Find your formula" quizzes drive capture + segmentation | Quiz events fire; not used as lead magnet | Activate |
| SMS | Tight email+SMS lifecycle | SMS list exists, unused | Activate |
| Education-led content | 80/20 value/promo, expert voice | Strong education, weak commerce | Rebalance |
| Local/retail integration | (N/A for pure DTC) | 3 stores + proximity segments unused | **Your unique edge** |

**Onelife's unfair advantages to lean into:** real pharmacists/coaches (authority most DTC brands fake), three physical stores (events, click-and-collect, local segmentation), genuine SA localisation, and a loyalty program already integrated (Smile). Best-in-class brands would *kill* for the retail + practitioner credibility you already have and aren't using in email.

---

## 9. Prioritised roadmap

### NOW (this week)
1. **Fix the refresh pipeline** (guard against zero-writes; verify secret/scopes; bump API revision). *Restores trustworthy reporting.*
2. **Standardise brand name → "Onelife Health"** across senders/templates/flows.
3. **Fix Post-Purchase Thank-You + Cross-sell flow** (R0 → real CTA/incentive).
4. **Remove the preview-text-in-body bug** from templates.
5. **Archive QA/test clutter** ([CODEX *], junk lists, cancelled dupes).

### NEXT (2–4 weeks)
6. **Build "All Consented" + engagement-tiered sending segments;** point campaigns at Engaged-90d.
7. **Launch list-hygiene + sunset** properly; get bounce <2%.
8. **Add product cards w/ images + reviews/social proof** to the email template system (Universal Content blocks).
9. **Build the Replenishment/Subscription flow** (dose-aware, one-tap reorder) and a **3-step Win-Back** off At-risk-60d (2,133).
10. **Turn on SMS** for Welcome + Abandoned Checkout.

### LATER (1–3 months)
11. **VIP lifecycle** (early access, perks) for the 98 high-LTV profiles.
12. **Quiz lead magnet** ("find your supplement") → capture + auto-segment.
13. **Local/retail program**: store-event invites, click-and-collect, proximity sends.
14. **Seasonal/promo calendar** aligned to payday + winter immunity + BF + Jan reset.
15. **Stand up SMS + email reporting in the (now-fixed) dashboard;** track email % of revenue toward 25%.

**Target:** move email from ~10% → **20%+ of revenue within one quarter**, primarily via replenishment, win-back, better-targeted campaigns, and reviews/social proof — without buying more traffic.

---

## Appendix A — Live flow inventory (18)
Welcome (Full Sequence) · Abandoned Checkout (Email+SMS) · Browse Abandonment v2 · Post-Purchase Thank-You + Cross-sell v3 · Post-Purchase Education (Magnesium, Vitamin D) · PCOS Welcome · PCOS Post-Purchase · GLP-1 Education Drip · GLP-1 Non-Opener Follow-up · Replenishment Reminder · Win-Back 60 Days v2 · Sunset Unengaged · Points Balance Nudge · Smile Loyalty (VIP Tier, Birthday, Points Expiring, Reward Expiring).

## Appendix B — Hygiene cleanup list
- Campaigns: archive all `[CODEX LINK QA]`, `[CODEX INTERNAL TEST]`, and `Cancelled`/duplicate blog drafts.
- Lists: delete `[CODEX QA] …` link-tracking & flow-test lists (~10), `Preview List`.
- Templates: rename all "Clone of …" templates to the `OL — …` convention.

## Appendix C — Method & caveats
Pulled live via Klaviyo MCP on 2026-05-30. Campaign/flow reports use send-date attribution (conversion metric = Placed Order, Shopify). Metric-aggregate revenue uses event-time and is not directly comparable to report figures. "12-month" windows ≈ 3.5 months of actual account history. Revenue-share is an approximation across slightly different time windows.
