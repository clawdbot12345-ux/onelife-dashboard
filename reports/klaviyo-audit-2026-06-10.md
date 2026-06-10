# Klaviyo Email Marketing Audit — 2026-06-10
**Scope:** all flows, campaigns, templates, analytics (last 90 days), benchmarked
against best-in-class health/wellness DTC email (Ritual, AG1, Seed-tier programs).

## Headline numbers (90 days)
| Metric | One Life | Best-in-class benchmark | Verdict |
|---|---|---|---|
| Total email revenue | ~R51k (≈R17k/mo) | 25–35% of store revenue | **~3× upside** |
| Flow : campaign revenue split | 70 : 30 | 50–60 : 40–50 | Flows carry the program |
| Campaign open rate (full list) | 26–33% | 40–50% | Below |
| Campaign click rate | 0.6–4% | 2–3.5% | Mixed |
| Campaign revenue/recipient | ~R0–1.2 | R5–15 | **Weak** |
| Unsubscribe rate (recent sends) | **1–2%** | <0.3% | 🔴 List fatigue |
| Spam complaints | 0.45% on PCOS #2; 0.07% round-up | <0.1% | 🔴 Watch |

## What's WORKING (protect these)
1. **Welcome flow Email 1 — elite.** 56% open / 11% click / 11% conversion,
   **R97 revenue per recipient**, R16.9k from just 174 people. This is genuinely
   best-in-class performance.
2. **Browse Abandonment** — R21.5/recipient, 24.8% click-to-open. Healthy.
3. **Segmentation proves itself**: Menopause campaign to "Engaged 90d" = 44% open,
   6.2% click, R4.3k — vs full-list blog sends at 27% open and ~R0.
4. The "Precious" letter voice — authentic, differentiated, deliverability-friendly.

## What's BROKEN (the "analytics are not great" diagnosis)
1. **Campaigns are a content newsletter, not a revenue channel.** ~20 sends in 90
   days, almost all "Blog:" round-ups to the full list, generating ~R5k/mo total.
   No offers, no launches with urgency, no segment-targeted product pushes.
2. **List fatigue is visible and accelerating**: unsubscribe rates hit 1–2% on the
   two most recent sends (10× benchmark). The same ~750→3,000 people get every
   blog post. Spam complaints have started (PCOS #2 at 0.45% is danger territory).
3. **Post-Purchase cross-sell: R0 from 338 recipients.** The flow exists, opens
   fine (46%), sells nothing — no product blocks, no offer, weak CTA.
4. **Abandoned cart is leaking badly**: only 397 recipients in 90 days from a
   store doing 40k sessions/month. Trigger = Checkout Started only (misses
   add-to-cart abandoners); just 2 emails; "Email & SMS" in name but no SMS.
5. **Welcome emails 2 & 3 convert zero** (Email 1 does all the work).
6. **Replenishment is mistimed/weak**: 1–2% click; generic "reorder" with no
   product memory in the visible template.
7. **Flow library gaps vs best-in-class**: no live Winback (template written
   yesterday, flow not live), no review-request flow (ties to empty PDP reviews),
   no back-in-stock flow (the metric and site form exist!), no VIP/loyalty tier
   flow beyond birthday, no sunset enforcement at scale (6 recipients).
8. **~20 [CODEX TEST] campaigns pollute reporting.** Archive them.

## Template design audit
All recent templates are CODE-type single-column "letters from Precious":
green header + logo, paragraphs, one CTA, grey footer.
**Strengths:** voice, light weight, mobile-safe, consistent sign-off.
**Gaps vs best-in-class:**
- **Zero imagery** — even the weekly *Product Spotlight* has no product photo.
- **Wrong brand green** (#1B5E20 vs site #1b4332) and none of the new site design
  language (serif display, botanical, colour system).
- No dynamic product feeds/recommendations blocks anywhere.
- Inconsistent unsubscribe tags ({{ unsubscribe }} vs {% unsubscribe %}).

### 🔴 FIXED TODAY — live factual errors in automated emails
Three repo automation scripts (friday_product_campaign.py,
build_replenishment_flow.py, publish_blog.py + brand-voice memory files) were
injecting **"Free delivery over R900 (Gauteng) | R1,400 (nationwide)"** — the
real threshold is **R400 nationwide** — plus "functional health coaches" (banned
term; it's "health consultants") and "15 protocols" (it's 17). Every generated
email contradicted the website's core promise. **All generators fixed + this
Friday's already-generated Spotlight template (WQXytX) corrected (HTML + text).**

## The plan (priority order)
**Week 1 — stop the bleeding**
1. Default ALL campaigns to **Engaged 90d** (proven +16pts open, real revenue);
   full list only for major announcements. Cap full-list sends at 2/month.
2. Archive the 20 test campaigns.
3. Widen abandoned cart: add Added-to-Cart trigger branch + email 3 (social
   proof / consultant pick) + actual SMS step.
4. Rebuild Post-Purchase #2 as a real cross-sell: dynamic "pairs with what you
   bought" + protocol upsell + review ask (when Judge.me emails go live).

**Weeks 2–3 — cadence completion**
5. Turn on Winback flow (template exists) at 60/90/120d with escalating offer.
6. Back-in-stock flow (metric + site form already wired).
7. Welcome 2 rebuild: protocol-matcher (quiz CTA → their goal's stack);
   Welcome 3: social proof + Vivid story instead of bare code-expiry.
8. Campaign calendar: alternate value email (guides) with revenue email
   (protocol spotlight + offer) — one of each weekly to Engaged.

**Weeks 3–4 — the design system**
9. One master template family matching the new site: botanical header band,
   serif display H1, product card blocks WITH photos, protocol CTA banner
   (same component as the website articles), colour-coded category chips.
   Apply to all flows + the two recurring campaign generators.

Email should be R45–60k/mo within a quarter on current traffic — the Welcome
flow proves the audience converts when the email deserves it.
