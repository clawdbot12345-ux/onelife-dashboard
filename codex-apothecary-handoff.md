# Onelife Health — Apothecary Launch + Klaviyo Cadence Fix

**Codex execution brief**
**Date:** 2026-06-04
**Owner:** One Life Health (onelife.co.za)

You're picking up an editorial + email-cadence handoff for One Life Health. Earlier today, 7 evergreen condition guides were published to the Shopify blog (renamed "The Apothecary"), and a Klaviyo cadence audit surfaced subscriber-fatigue signals. Below are the concrete tasks to execute, in priority order. Treat each as independently shippable.

---

## Context (skim, then act)

- **Shopify store:** onelifehealth.myshopify.com (onelife.co.za)
- **Current LIVE theme:** "Onelife Audit Sweep 2026-05-28", theme ID `185669910838`
- **Blog:** "The Apothecary" (handle still `health-wellness-hub` for URL stability), blog ID `120011424054`
- **Brand line:** *"South Africa's apothecary, since 1996."*
- **Brand colours:** forest `#1b4332` (primary), `#2d6a4f` (hover), `#7ec8a0` (mint accent)

---

## Shopify credentials

OAuth `client_credentials` grant against `https://onelifehealth.myshopify.com/admin/oauth/access_token`.

Retrieve the custom-app `client_id` and `client_secret` from the project's secret store (1Password / env vars / your existing Klaviyo+Shopify creds vault). They were last shared in the Claude Code session that created this brief — ask the project owner if you don't already have them loaded.

Use the resulting `shpat_*` token as `X-Shopify-Access-Token` for all Admin REST and GraphQL calls. Token TTL is 24 hours — refresh as needed.

---

## The 7 guides (live, need featured images + wiring)

| Article ID | Title | Handle |
|---|---|---|
| `613632016694` | Sleep & Recovery | `sleep-and-recovery-supplement-guide` |
| `613632049462` | Gut Health & Digestion | `gut-health-and-digestion-guide` |
| `613632082230` | Immunity | `immunity-supplements-year-round-defence` |
| `613632114998` | Stress & Mood | `stress-and-mood-supplement-guide` |
| `613632147766` | Energy & Vitality | `energy-and-vitality-beyond-the-coffee-crash` |
| `613632180534` | Women's Health | `womens-health-cycles-hormones-and-the-years-beyond` |
| `613632213302` | Joints & Mobility | `joints-and-mobility-move-without-compromise` |

URLs: `https://onelife.co.za/blogs/health-wellness-hub/{handle}`

---

# TASKS — execute in this order

## TASK 1 — Set article featured images (15 min)

Each guide currently has NO featured image. Use the **existing collection hero images** already in the theme assets — do NOT generate new images. Mapping:

| Article ID | Theme asset to use |
|---|---|
| `613632016694` | `assets/onelife-collection-sleep-relaxation-hero-1440.webp` |
| `613632049462` | `assets/onelife-collection-gut-health-hero-1440.webp` |
| `613632082230` | `assets/onelife-collection-immunity-hero-1440.webp` |
| `613632114998` | `assets/onelife-collection-stress-mood-hero-1440.webp` |
| `613632147766` | `assets/onelife-collection-energy-vitality-hero-1440.webp` |
| `613632180534` | `assets/onelife-collection-womens-health-hero-1440.webp` |
| `613632213302` | `assets/onelife-collection-joints-mobility-hero-1440.webp` |

**Implementation:** Articles need an image URL, not a theme asset path. Fastest path:

1. Upload each `.webp` from theme assets to Shopify Files (`POST /admin/api/2024-10/files.json` with the asset URL), OR
2. Fetch the asset CDN URL via theme assets API and pass that to:
   ```
   PUT /admin/api/2024-10/blogs/120011424054/articles/{id}.json
   { "article": { "id": ..., "image": { "src": "https://...", "alt": "..." } } }
   ```

Set descriptive alt text per guide, e.g. *"Onelife Health Sleep & Recovery guide cover"*.

**Verify:** each guide page should now show the hero image at the top + share with the correct `og:image`.

---

## TASK 2 — Add "The Apothecary" to main navigation (2 min, manual)

Shopify Admin → Online Store → Navigation → Main menu → Add menu item:

- **Name:** The Apothecary
- **Link:** `/blogs/health-wellness-hub`
- **Position:** between "Brands" and "Stores"

(GraphQL also possible via `onlineStoreNavigation` mutations, but admin UI is faster.)

---

## TASK 3 — Verify the collection-guide-callout deployed correctly (5 min)

A snippet was added at `snippets/collection-guide-callout.liquid` and inserted into `templates/collection.json` between `lifestyle-hero` and `banner`. It silently renders nothing if the collection has no matching guide.

**Verify it shows on these 7 collections:**

- `/collections/sleep-relaxation`
- `/collections/gut-health`
- `/collections/immunity`
- `/collections/stress-mood`
- `/collections/energy-vitality`
- `/collections/womens-health`
- `/collections/joints-mobility`

**Should NOT show on** `/collections/all` or any other.

If it isn't rendering after a hard refresh: re-pull the snippet, confirm it has the `case collection.handle` block intact, and re-verify the section is in the template's `order` array.

---

## TASK 4 — Add a "Read the guide" CTA card at the END of each guide body (20 min)

Each guide currently ends with a short text paragraph linking to the matching collection. Replace that paragraph with a styled CTA card. Use this HTML block (swap collection slug + name per guide):

```html
<a href="/collections/{slug}" style="display:flex;align-items:center;gap:20px;margin:32px 0;padding:24px;background:linear-gradient(135deg,#1b4332,#2d6a4f);border-radius:14px;color:#fff;text-decoration:none;">
  <div style="flex:1;">
    <div style="font-size:11px;font-weight:700;letter-spacing:2px;text-transform:uppercase;opacity:.7;margin-bottom:6px;">Ready to shop?</div>
    <div style="font-size:18px;font-weight:700;margin-bottom:4px;">Browse the {Collection name} collection</div>
    <div style="font-size:13px;opacity:.85;">Every product mentioned in this guide, curated by our pharmacists. STACK5 takes 5% off any stack.</div>
  </div>
  <div style="font-size:28px;">→</div>
</a>
```

Update each article's `body_html` via:
```
PUT /admin/api/2024-10/blogs/120011424054/articles/{id}.json
```

**Collection slug + name mapping:**

| Guide | Collection slug | Display name |
|---|---|---|
| Sleep | `sleep-relaxation` | Sleep & Relaxation |
| Gut | `gut-health` | Gut Health |
| Immunity | `immunity` | Immunity |
| Stress | `stress-mood` | Stress & Mood |
| Energy | `energy-vitality` | Energy & Vitality |
| Women's | `womens-health` | Women's Health |
| Joints | `joints-mobility` | Joints & Mobility |

---

## TASK 5 — Klaviyo: cut broadcast cadence to 1/week for the wide list

The **"Email List"** segment (the main ~750 subscribers) is currently receiving ~2 emails/week of broadcast PLUS flow emails. Unsubscribe rate trending **0.3–0.87%** (industry healthy <0.2%).

**Action:**

- Audit the next 30 days of scheduled campaigns
- For any campaign sending to the "Email List", check the calendar
- If two campaigns within 7 days both target the wide list, reschedule one to hit only the **"Engaged 90d"** segment instead
- **Goal:** max 1 broadcast/week to "Email List", up to 2/week additional to "Engaged 90d" only

---

## TASK 6 — Klaviyo: stop broadcasting "Blog:" campaigns to the wide list

Looking at 90 days of data, every `Blog: X` campaign sent to the full Email List had:

- ~0 revenue (R0–R900 against 750 recipients)
- 0.5%+ unsubscribe rate
- Below-benchmark click rate

Educational content is fine — but it belongs to the engaged audience, not broadcast.

**Action:**

- Audit all upcoming scheduled campaigns with subject lines starting `Blog:` or tagged as educational
- Change recipient targeting from "Email List" to "Engaged 90d" segment ONLY
- For any past campaigns being repurposed, do the same

**Reserve the wide "Email List" for:**

- Monthly bundle promos (EDN-style)
- Friday Product Spotlights (highest revenue/unsub ratio in the last 90 days)
- Launch announcements (Vivid, GLP-1, etc.)

---

## TASK 7 — Klaviyo: audit flow stacking + add suppression

**18 flows are LIVE.** An active customer can hit 4–6 emails/week between campaigns AND flows. Specifically risky overlaps:

- Welcome — One Life Health (Full Sequence)
- Post-Purchase Thank You + Cross-sell v3
- Post-Purchase Education — Magnesium v1
- Post-Purchase Education — Vitamin D v1
- Browse Abandonment v2
- Replenishment Reminder (API-created)
- Smile Loyalty × 4 flows (VIP Tier, Birthday, Points Expiring, Points Balance Nudge, Reward Expiring)

**Action:**

- Add a Klaviyo Flow filter on every Post-Purchase Education flow + Browse Abandonment + Replenishment + Smile Loyalty flows that says:
  > *"Suppress if profile received ≥2 flow emails in the last 7 days"*
- For Welcome series, ensure it pauses if user receives a campaign mid-flow
- For PCOS Welcome + PCOS Post-Purchase — ensure they don't both fire if someone joins a PCOS list and buys within 24h

---

## TASK 8 — Klaviyo: send a "We're sending less now" re-permission email

Build a Klaviyo campaign:

- **Audience:** profiles who unsubscribed from email marketing in the last 90 days (use metric `Unsubscribed from Email Marketing` with filter "last 90 days")
- **Subject:** "We took your feedback. Sending less now — want back in?"
- **Body:** short, honest, includes a one-click resubscribe CTA via a hosted preference form
- **Send time:** a Tuesday morning, 09:00 SAST

Recovery rates on these typically **5–10%**. Worth running.

---

## TASK 9 — Klaviyo: schedule the 7 guides as a 7-week drip

Build a recurring campaign series:

- **Audience:** "Engaged 90d" segment ONLY (do NOT broadcast to wide list)
- **Cadence:** Tuesday 10:00 SAST, weekly for 7 weeks
- **Order:** Sleep → Gut → Immunity → Stress → Energy → Women's → Joints
- **Each email:** a clean editorial template that previews the guide (~150 words), CTA to read full guide on site, secondary CTA to the matching collection with STACK5

**Subject line A/B test:**

- **Variant A:** *"What 30 years on the pharmacy floor taught us about {topic}"*
- **Variant B:** *"{Topic} supplements: a pharmacist's honest guide"*

---

## TASK 10 — Clean up Klaviyo campaign list

There are 24+ campaigns with names starting `[CODEX LINK QA]`, `[CODEX INTERNAL TEST]`, or `[CODEX GPT IMAGE TEST]` cluttering the campaign list.

**Action:** bulk-archive or delete via the Klaviyo Campaigns API. Filter by name contains `[CODEX`. Verify each has small recipient count (1–3) and zero business impact before deleting.

---

## TASK 11 — Tag every campaign properly

Existing campaigns have NO tags, which means reporting can't segment by type.

**Action:** bulk-tag all real (non-test) campaigns retroactively with one of:

- `educational-blog` — anything titled `Blog: X`
- `bundle-promo` — EDN bundles, March/April promos
- `product-spotlight` — Friday Product Spotlight series
- `launch` — Vivid Launch, GLP-1 Launch, etc.
- `seasonal` — Winter Immunity, etc.

Going forward, **set tags on creation** via the API.

---

# Definition of done

- [ ] All 7 guides have a featured image and an end-of-article CTA card
- [ ] "The Apothecary" appears in the main nav
- [ ] Guide callout renders on the 7 matched collection pages
- [ ] All upcoming "Blog:" Klaviyo campaigns target Engaged 90d only
- [ ] Flow filters added to prevent >2 flow emails in 7 days
- [ ] Re-permission email is queued
- [ ] 7-week guide drip is scheduled to Engaged 90d
- [ ] Test campaign clutter is archived
- [ ] All campaigns are tagged

---

# Execution priority

Ship in this order — items **1–4 are visible to customers and need to land before item 9** (the drip starts going out). Items **5–8 are commercial** — they stop the subscriber-LTV bleeding.

**Report back with what shipped vs what's outstanding.**
