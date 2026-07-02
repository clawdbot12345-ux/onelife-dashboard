# Codex Handoff — Round 1 (2026-07-01)

**Context:** Marketing strategy + audits landed on PR #22 (`claude/onelife-marketing-strategy-epal62`).
Claude has already shipped: Friday/Tuesday/Monthly email automation fixes with failure alerting, the
master email template (`scripts/email_template.py`), the Klaviyo flow audit, and five inert Klaviyo
assets (3 flow templates + 2 winback segments). This document is everything **Round 1** still needs
that requires store admin, Klaviyo UI, or platform access Claude doesn't have.

Source docs: `marketing-strategy-2026-07.md` (§3 Pillar 0, §12 Days 1–14) ·
`site-audit-2026-07-01.md` · `email-flow-fix-plan-2026-07-01.md` ·
`reports/flow-extension-build-2026-07-01.md` · `reports/flow-audit-2026-07-01.md`.

---

## 0. Access to restore/grant FIRST (unblocks everything else)

### 0.1 Shopify custom app — reinstall with these scopes 🔴 ROOT CAUSE
The custom app on `onelifehealth.myshopify.com` is uninstalled/revoked: every OAuth
client-credentials exchange returns `400 app_not_installed` (this silently killed the Friday
product email for 3 weeks). Reinstall (Settings → Apps and sales channels → Develop apps), and set
Admin API scopes to **at least**:

| Scope | Used by |
|---|---|
| `read_products`, `read_inventory` | friday_product_campaign.py, publish_blog.py stock checks, seo_audit.py |
| `write_products` | seo_fix_agent.py, slug/tag cleanup workflows |
| `read_content`, `write_content` | publish_blog.py (blog articles) |
| `read_legal_policies`, `write_legal_policies` | **update_shipping_policy.py — currently denied** (`ACCESS_DENIED` on both, run 2026-07-01) |
| `read_orders` | (optional, next round) per-product online sales for the dashboard refresh |

Then update the GitHub Actions secrets (**Settings → Secrets and variables → Actions**):
`SHOPIFY_ADMIN_TOKEN` (new Admin API access token — preferred; both Monday publish and the fixed
Friday workflow use it) and/or `SHOPIFY_CLIENT_ID` + `SHOPIFY_CLIENT_SECRET` (re-issued).

**Verify:** manually run the **Friday Product Email** workflow (Actions → Run workflow) — logs must
show `✓ Token acquired` (not the storefront-fallback warning).

### 0.2 Klaviyo MCP connector for Claude
Authorize the Klaviyo connector (`mcp.klaviyo.com`) in claude.ai → Settings → Connectors so Claude
can verify flow wiring and manage campaigns live instead of via Actions round-trips. The
`KLAVIYO_API_KEY` Actions secret already works — leave it.

### 0.3 GitHub Actions dispatch for Claude (optional QoL)
Claude's session token gets `403 Resource not accessible by integration` on
`workflow_dispatch`. If the Claude GitHub App can be granted **Actions: write**, do so; otherwise
the `.github/triggers/<name>` push-trigger pattern stays (works fine).

---

## 1. Shipping policy — fix the R400 contradiction 🔴 (site audit C1, CPA risk)

Sitewide promise: "FREE DELIVERY over R400 nationwide". `/policies/shipping-policy` still says free
over **R900 (Gauteng) / R1,400 (nationwide)**. Fix either way:

- **Fastest (2 min):** Shopify admin → Settings → Policies → Shipping policy → replace body with the
  HTML in `scripts/update_shipping_policy.py` (`NEW_BODY` constant — thresholds R400, sub-R400 rates
  R75 Gauteng / R130 national, timeframe unified to "1–5 working days, Gauteng usually 1–2").
- **Or after 0.1:** run the **Update Shipping Policy** workflow (it no-ops if the page already says R400).

**Verify:** `curl -s https://onelife.co.za/policies/shipping-policy | grep -c R400` ≥ 1 and no R900.

## 2. Klaviyo wiring — 15 minutes in the UI (assets already created)

Full steps with screenshots-level detail: `reports/flow-extension-build-2026-07-01.md`. Summary:

| # | Where | What |
|---|---|---|
| 2.1 | Flow `WY4cae` (Abandoned Checkout Consultant Check — 2026 design system) | Append: Wait 1d → Email (template `SCi9Vy` *Touch 2 — honest check-in*) → Wait 1d → Email (template `RZh7iV` *Touch 3 — STACK5*). Flow filter on both added emails: **Placed Order zero times since starting this flow**. Set both live. |
| 2.2 | New flow | Trigger: **Placed Order** metric → Wait 7d → Email (template `VA8SjT` *Post-Purchase Cross-sell*). Filter: Placed Order zero times since flow start. Set live. |
| 2.3 | Flow `R96wJV` (PCOS Post-Purchase) | Add trigger filter **Items contains Pcositol** (+ other PCOS SKUs). Today it fires on EVERY order — 302 wrong-audience sends in June, R0 revenue. |
| 2.4 | Winback catch-up | Clone **Win-Back 60 Days v2** → trigger **Added to segment `TaFWcM`** (*Lapsed 60–120d*) → live. Clone again for segment `WKxHdK` (*Lapsed 120d+*). Add "has not been in catch-up flow" filters to the two existing metric-triggered winback flows. This is how the 1,462 already-lapsed profiles finally get mailed. |
| 2.5 | Campaigns list | Find the drafted campaign for the **flu recovery** article (created Mon 2026-06-29 — its schedule call failed). Either schedule it or delete it. |

**Verify:** within 48h, Winback catch-up flows show recipients > 0; abandoned-checkout flow shows
3 emails in the timeline.

## 3. Pixels — Meta + TikTok 🔴 (site audit H1)

The site has GA4, Google Ads, Clarity, Klaviyo — **zero `fbq`, zero `ttq`**. R6k/mo of Meta+TikTok
ads ran with no measurement, no retargeting audiences possible.

1. Shopify admin → Sales channels: install **Facebook & Instagram** channel → connect the Meta
   Business account → enables the pixel + Conversions API. Note the Pixel ID.
2. Install the **TikTok** channel app → connect the TikTok for Business account → pixel + events.
3. Do NOT start any paid campaigns — measurement only (strategy holds paid social at R0 until
   pixels have 60 days of data).

**Verify:** `curl -s https://onelife.co.za | grep -c fbq` ≥ 1 and `grep -c ttq` ≥ 1 (or Meta Pixel
Helper / TikTok Pixel Helper browser extensions).

## 4. POPIA consent — un-tick pre-checked boxes (site audit M2)

1. Shopify admin → Settings → Checkout → Marketing options: set email marketing to
   **unchecked by default**.
2. Klaviyo → Sign-up forms → the "FIRST-ORDER OFFER" popup: consent checkbox must default to
   unchecked (April 2025 POPIA regs: "opt-out shall not constitute consent").

**Verify:** incognito checkout + popup both show unchecked boxes.

## 5. Checkout logo (site audit M1)

Shopify admin → Settings → Checkout → Branding: replace the legacy low-res purple "one Life" logo
with the current green "ONE LIFE HEALTH STORE" mark (same asset as the storefront header,
`OneLife_LOGO_51277c55…png`). Screenshot evidence: session file `checkout-step1-mobile.png`.

## 6. Reviews engine on (site audit H2)

Judge.me is installed but idle; the #1 best-seller shows "No reviews".
1. Judge.me → enable the **post-purchase review request** email (delay ~14 days after fulfilment),
   offer code **REVIEW25** (existing, real code).
2. Backfill: send review requests to the last 60 days of fulfilled orders.
3. Ensure Judge.me writes `aggregateRating` into product JSON-LD, then remove the theme's duplicate
   Product schema block (site audit M7) so Google picks one — the custom block with
   `shippingDetails` is the keeper.

**Verify:** PDP shows stars within 2 weeks; Google Rich Results test on a top PDP passes with rating.

## 7. Google Ads account hygiene (agency or owner, ~1 hour)

1. Run **Mike Rhodes' PMax script** (mikerhodes.com.au/scripts/pmax) — quantifies how much of the
   claimed 29.5× PMax ROAS is brand traffic. Attach output to the agency conversation.
2. Conversion actions: exactly ONE primary "Purchase" action (there are currently two — values may
   double-count). Set the second to Secondary.
3. Add brand exclusion list ("one life", "onelife", misspellings) to PMax.
4. Pause **"One Life Shopping"** (Maximise Clicks, 0.26% conv rate, R6.8k spend — buys clicks not
   buyers) pending the §4 restructure in `marketing-strategy-2026-07.md`.

## 8. Explicitly deferred to Round 2 (do not start)

BNPL (Payflex/PayJustNow) + Ozow · price rounding / VAT-incl labels (merchandising decision) ·
mobile pre-header collapse + vendor-field cleanup (theme PR) · refund-policy rewrite (needs owner's
return-window decision) · Pargo/Bob Go checkout options · WhatsApp VIP → API migration · subscriptions
app. All specced in `marketing-strategy-2026-07.md` §12 Days 15–60.

## Round-1 definition of done

- [ ] Custom app reinstalled with scopes; `SHOPIFY_ADMIN_TOKEN` secret updated; Friday workflow logs `✓ Token acquired`
- [ ] Live shipping policy says R400 (no R900/R1,400)
- [ ] Klaviyo: 2.1–2.5 wired; winback catch-up flows have recipients
- [ ] Meta + TikTok pixels firing on the storefront
- [ ] Consent boxes default unchecked (checkout + popup)
- [ ] Checkout shows the current green logo
- [ ] Judge.me post-purchase review requests live + 60-day backfill sent
- [ ] Google Ads: one primary Purchase action; brand exclusions on PMax; Rhodes script output saved
