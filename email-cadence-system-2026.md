# One Life Health — Email Revenue System (2026-06-11)

The owner's ask: "we need Klaviyo to give us much bigger revenue numbers…
I still don't have proper cadence." This file IS the system: what runs
automatically, what each piece earns, and the targets it's accountable to.

## 1. The benchmark we're chasing (sourced 2026-06-11)

| Metric | Median DTC | Top performers | One Life today |
|---|---|---|---|
| Email % of online revenue (last-click) | 25–30% [Klaviyo, vendor] | 33%+ ($10M+ stores) | **~11% (R17k/R150k)** |
| Flow share of email revenue | ~41% from 5.3% of sends [Klaviyo 2026] | — | flows just rebuilt |
| Abandoned-cart RPR | $3.07 avg | $27+ top 10% | being measured |
| Welcome RPR | $2.35 avg | $21 top 10% | Welcome 1 = R97/recipient ✅ elite |

**Target: email = 25% of online revenue.** At R500k/mo online → R125k/mo
email. At R1m/mo → R250k/mo. Flows do ~60% of that lifting, campaigns 40%.

## 2. What runs automatically (no human in the loop)

| When | What | Engine |
|---|---|---|
| Always-on | Welcome ×3 · Abandoned Cart (+Consultant Check) · Browse · Post-Purchase · Win-Back 60 · **Win-Back 90/120 (new)** · **Back in Stock (new)** · Replenishment · Sunset · Smile ×4 · PCOS ×2 · GLP-1 ×2 | Klaviyo flows (21 live) |
| Tue 09:00 SAST | **Education digest** — newest Apothecary article, topic banner hero, matching protocol CTA | `.github/workflows/tuesday-blog-email.yml` → `scripts/tuesday_blog_digest.py` |
| Fri 09:00 SAST | **Product feature** — new launch → top seller → curated fallback, full design-system template | `.github/workflows/friday-product-email.yml` → `scripts/friday_product_campaign.py` |

Both campaign generators target **Engaged 90d (S3MAsK) only** — the
2026-06-10 audit showed full-list sends cost 1–2% unsubs per send. Smart
Sending is on, so nobody gets Tue + Fri + a flow email in the same window.
The Tuesday script never repeats an article (dedupe state committed to repo).

### Owner setup (once, ~5 minutes)
1. GitHub → Settings → Secrets and variables → Actions → confirm/add
   secrets: `KLAVIYO_API_KEY` (exists for the dashboard), `SHOPIFY_CLIENT_ID`,
   `SHOPIFY_CLIENT_SECRET` (and optional `GEMINI_API_KEY` for Friday heroes).
2. Same page → Variables → add `EMAIL_AUTOMATION_ENABLED` = `true`.
   Set it to `false` any time to stop the cadence instantly.
3. First run: Actions tab → run each workflow manually once → check the
   campaign appears in Klaviyo (it schedules 1–2 days out, so there is
   always a review window to cancel in the Klaviyo UI before send).

## 3. Monthly rhythm (human-led, 30 min/month)

- **1st week:** Protocol Spotlight — pick the seasonal protocol (winter =
  Winter Immunity), Claude drafts the campaign on request.
- **3rd week:** Social-proof email — once Judge.me reviews accumulate,
  "what customers said this month" (top 3 reviews + products).
- **Monthly check (5 min):** Klaviyo dashboard → is email revenue % climbing
  toward 25%? Are unsubs <0.3%/campaign? Is the list growing 500+/mo?

## 4. Template design policy (evidence-based, decided 2026-06-11)

Researched against AG1/Ritual/Seed teardowns + the only large-n A/B data
(HubSpot, 500M+ emails): **image-heavy emails CUT clicks (−21% CTR);
top supplement brands use functional/founder-narrative emails, not
cinematic lifestyle spreads** (Ritual's emails are 22KB). Policy:
- ONE hero image per email (current design system) — no more.
- Voice-of-Precious narrative body, text-first, real links not image buttons.
- Cinematic lifestyle imagery belongs on the SITE (where it converts
  browsers), not stacked into emails (where it costs clicks + deliverability).
- Worth testing later: a fully plain-text "from Precious" winback variant.

## 5. Revenue math to R1m/mo (email's contribution)

| Online revenue | Email @ 25% | Flows ~60% | Campaigns ~40% |
|---|---|---|---|
| R150k (now) | R37k | R22k | R15k |
| R500k (60–90d) | R125k | R75k | R50k |
| R1m (120–180d) | R250k | R150k | R100k |

Email doesn't create the traffic — it multiplies the list. The cadence
above only hits these numbers if list growth runs (signup form live ✅,
single opt-in ✅, target 500–1,000 subs/mo) and checkout stops leaking
(Payflex/Ozow installs — still the #1 owner action).
