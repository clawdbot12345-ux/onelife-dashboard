# Onelife Health — Attribution Cleanup (UTM Tagging Across All Channels)

**Codex execution brief**
**Date:** 2026-06-04
**Owner:** One Life Health (onelife.co.za)

You're picking up an attribution-hygiene task. Right now, Shopify can't tell paid Google clicks apart from organic Google clicks — they all come through as `https://www.google.com/` because UTMs aren't consistently set across channels. Same problem with Klaviyo (some clicks attribute to "onelife" or get lost to direct) and Meta (no tagging at all).

This brief fixes that **permanently** in three platforms, then sets up a 30-day verification so we never have to estimate again.

---

## Context (skim, then act)

- **Shopify store:** onelifehealth.myshopify.com
- **Last 90 days revenue:** R283K across 472 orders
- **The attribution problem:** R171,250 of that comes through `https://www.google.com/` as a single bucket — we can't split paid vs organic without UTM/`gclid` tagging
- **Current ad spend:** ~R20K/month, majority Google, some Meta
- **Klaviyo email attribution (self-reported):** ~R46K over 90 days, but some shows up as "onelife" referrer in Shopify and the rest is lost to "(direct)"
- **The goal:** every click into onelife.co.za carries a UTM stamp so Shopify, GA4, Klaviyo, Google Ads and Meta Ads all agree

---

# TASKS — execute in this order

## TASK 1 — Klaviyo: enable account-wide UTM auto-tagging (5 min)

This is the biggest single fix. Klaviyo can stamp every link in every campaign + flow automatically.

**Steps:**

1. Klaviyo admin → click your account name (top-right) → **Settings → Other → UTM Tracking**
2. Enable **"Add UTM tracking parameters to links in marketing campaigns"**
3. Set these defaults:
   - `utm_source` → `klaviyo`
   - `utm_medium` → `email` (for SMS, also enable SMS toggle with `utm_medium=sms`)
   - `utm_campaign` → `{{ campaign.name|slugify }}`
   - `utm_content` → `{{ message.name|slugify }}` (optional, for tracking specific email variants)
4. Click **"Apply to Flows"** — Klaviyo gives you the option of also tagging existing flows. SAY YES — without this, only campaigns get tagged.
5. Save.

**Caveats:**

- Some campaigns may have manual UTMs already (e.g. links that hardcoded `?utm_campaign=...`). Klaviyo's auto-tagger won't override manual params. Audit the next 10 scheduled campaigns and remove any old manual UTMs that would conflict.
- Test: send a preview of any existing campaign to yourself, click a link, confirm it lands at `onelife.co.za/...?utm_source=klaviyo&utm_medium=email&utm_campaign=...`.

---

## TASK 2 — Google Ads: confirm auto-tagging is on + GA4 link is healthy (3 min)

Auto-tagging in Google Ads sets a `gclid` parameter on every paid click. Shopify uses `gclid` to identify paid Google traffic vs organic.

**Steps:**

1. Google Ads → **Tools → Setup → Account settings → Auto-tagging**
2. Confirm it's **ON**. If off, switch on. (This affects new clicks only; existing data isn't retroactively tagged.)
3. **Tools → Setup → Linked accounts → Google Analytics (GA4)**. Confirm the link to the Onelife GA4 property is healthy and "Auto-tagging" is also enabled on the GA4 side.
4. In GA4 → **Admin → Property → Google Ads links** → confirm the link is active and "Personalised advertising" + "Auto-tagging" are both ON.

**Verify:** After 24h, run this Shopify query in our Admin console:

```
FROM sales SHOW orders, total_sales GROUP BY order_referrer_url SINCE -1d UNTIL today ORDER BY total_sales DESC LIMIT 20
```

You should now see referrer URLs containing `?gclid=...` for paid clicks — distinct from plain `https://www.google.com/` which is organic.

---

## TASK 3 — Meta Ads: add URL parameters to every campaign (10 min)

Meta has no auto-tagging equivalent. UTMs have to be set per-campaign (or once at the Ads-Manager-account level if your account supports it).

**Steps:**

1. Meta Ads Manager → Campaigns → for EACH active campaign:
   - Edit → Ad Set → Tracking → **URL parameters**
   - Paste:
     ```
     utm_source=meta&utm_medium=cpc&utm_campaign={{campaign.name}}&utm_content={{ad.name}}&utm_term={{adset.name}}
     ```
2. For future campaigns, set this as a template at the ad-set level so it inherits automatically.
3. If running Instagram Stories/Reels specifically, you may want `utm_source=instagram` instead of `meta` — apply per campaign as appropriate.

**Caveat:** the `{{campaign.name}}`, `{{ad.name}}` are Meta's dynamic parameters — they auto-fill at click time. Don't replace them with hardcoded values.

---

## TASK 4 — Document the UTM convention (5 min, one-pager)

Add a Notion page or shared doc with the canonical UTM scheme so future ads/emails follow it:

| Channel | utm_source | utm_medium | utm_campaign |
|---|---|---|---|
| Klaviyo email | `klaviyo` | `email` | `{campaign-name-slug}` |
| Klaviyo SMS | `klaviyo` | `sms` | `{campaign-name-slug}` |
| Google Ads (paid search) | auto via gclid | — | — |
| Meta paid | `meta` | `cpc` | `{campaign-name}` |
| Instagram organic post | `instagram` | `social` | `{post-name}` |
| WhatsApp blast | `whatsapp` | `broadcast` | `{campaign-name}` |
| Influencer / partner | `partner` | `referral` | `{partner-name}` |
| Affiliate link | `affiliate` | `referral` | `{affiliate-id}` |
| QR codes / print | `qr` | `print` | `{material-name}` |
| Email signature link | `staff-signature` | `email` | `signature` |

Pin this in the team's shared workspace. Every new campaign uses these conventions.

---

## TASK 5 — 24h verification: confirm Klaviyo tags are landing (5 min)

The day after Task 1, run this query in Shopify Analytics:

```
FROM sales SHOW orders, total_sales GROUP BY order_referrer_url SINCE -1d UNTIL today ORDER BY total_sales DESC LIMIT 30
```

Expected: any orders from a Klaviyo click should now show a referrer URL containing `utm_source=klaviyo`. If you don't see any after 24–48h with active campaigns sending, the auto-tagging didn't apply — revisit Task 1, particularly the "Apply to Flows" step.

---

## TASK 6 — 30-day attribution report (the payoff)

Exactly 30 days after Tasks 1–3 are complete, run this consolidated attribution report by pulling these five numbers in parallel:

### 6a. Shopify (canonical revenue truth)

```
FROM sales SHOW orders, total_sales GROUP BY order_referrer_source, order_referrer_name SINCE -30d UNTIL today ORDER BY total_sales DESC
```

```
FROM sales SHOW orders, total_sales GROUP BY order_referrer_url SINCE -30d UNTIL today ORDER BY total_sales DESC LIMIT 50
```

The second query is where you'll see `gclid` and `utm_source=klaviyo` URLs spelled out. Bucket them in your report.

### 6b. GA4 (multi-touch view)

GA4 → Reports → Acquisition → Traffic acquisition → set date range 30d → secondary dimension **"Session source/medium"** → metric **"Purchase revenue"**.

Export to CSV.

### 6c. Klaviyo (self-attributed email/SMS revenue)

Use the Klaviyo metric aggregates API:

```
metricId = WZAxyj (Placed Order)
groupBy = ["$attributed_channel"]
measurements = ["sum_value", "count"]
startDate = 30 days ago
```

### 6d. Google Ads (paid Google revenue + spend)

Google Ads → Reports → Predefined reports → Campaign performance → date range 30d → columns: Cost, Conversions, Conversion value. Export CSV.

### 6e. Meta Ads Manager (paid Meta revenue + spend)

Ads Manager → Campaigns → date range 30d → columns: Amount spent, Purchases, Purchase conversion value (link-click attribution, 7-day click + 1-day view default).

### 6f. Build the consolidated table

Produce this table and post it to the team:

| Channel | Shopify revenue | GA4 revenue | Platform-claimed revenue | Spend | True ROAS |
|---|---|---|---|---|---|
| Google Paid | ? | ? | (Google Ads conv value) | (Google Ads cost) | (rev / cost) |
| Google Organic | ? | ? | — | 0 | — |
| Meta Paid | ? | ? | (Meta Ads conv value) | (Meta Ads spend) | (rev / spend) |
| Meta/Instagram Organic | ? | ? | — | 0 | — |
| Klaviyo Email | ? | ? | (Klaviyo $email_channel) | 0 | — |
| Klaviyo SMS | ? | ? | (Klaviyo $sms_channel) | 0 | — |
| Direct / Bookmark | ? | ? | — | 0 | — |
| Other (Bing, DDG, etc.) | ? | ? | — | 0 | — |
| **Total** | (Shopify total) | (GA4 total) | — | (total ad spend) | (blended ROAS) |

**Don't expect Shopify, GA4, and platform-claimed numbers to match exactly.** Industry-standard spread is 10–25%. What you're checking:

- Shopify total should be within 5% of bank-deposit truth
- Platform-claimed should be the highest (each platform over-claims)
- GA4 should be the middle ground (multi-touch attribution)
- The directional story should be consistent across all three

### 6g. The decisions this report unlocks

- **Google Ads ROAS:** if blended ROAS <2.5x → audit and trim worst-performing campaigns; if >4x → consider scaling spend
- **Meta Ads ROAS:** if <2x → likely waste, consider reallocating to Google
- **Klaviyo share:** target is 20–30% of revenue once flows are properly stacked; <15% means email is underused
- **Organic share:** baseline today is ~10%; The Apothecary content sprint should push to 20%+ over 6 months
- **Direct/untagged share:** should drop from ~20% to <10% after this cleanup. Anything still untagged is a new leak to investigate

---

# Definition of done

- [ ] Klaviyo UTM auto-tagging enabled, with flows included
- [ ] Klaviyo links visibly land with `?utm_source=klaviyo&...` (verified by clicking a preview)
- [ ] Google Ads auto-tagging on, GA4 link confirmed
- [ ] Paid Google clicks now arrive at Shopify with `?gclid=...` in referrer URL
- [ ] Every active Meta campaign has URL parameters set
- [ ] UTM convention is documented in a shared workspace
- [ ] 24-hour spot-check confirms Klaviyo tags are landing
- [ ] 30-day consolidated attribution report run and posted to team
- [ ] Recommendations from 6g flagged for owner review

---

# Notes

- **Historical attribution can't be retroactively fixed.** Pre-cleanup data stays muddled — this is forward-only. Don't compare pre-cleanup and post-cleanup numbers like-for-like.
- **The Klaviyo task is by far the biggest win.** Roughly R30–45K/month of revenue currently lands in Shopify's "direct/onelife" bucket because email clicks aren't tagged. Fixing that surfaces them as `klaviyo` properly.
- **Don't double-tag.** If a Klaviyo flow email already includes `utm_source=email` in the link, the auto-tagger will overwrite it depending on settings. Audit existing flow templates for hardcoded UTMs and strip them before enabling auto-tag.

Report back with what shipped and the 30-day attribution table.
