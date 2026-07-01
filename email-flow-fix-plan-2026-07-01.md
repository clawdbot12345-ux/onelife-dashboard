# Klaviyo Flow Fix Plan — 2026-07-01

Based on `reports/flow-audit-2026-07-01.md` (trigger definitions pulled via API).
Metric IDs referenced: `WZAxyj` = Placed Order · `WnzuVG` = Checkout Started.

## 1. Winback — zero recipients explained (structural, not a bug)

Both winback flows are **metric-triggered on Placed Order** with the standard
"no order since flow start" filter. Correct design for the future, but
metric-triggered flows never backfill: anyone whose last order predates the
flow going live (Win-Back 60 v2 → ~2026-05-05; Win-Back 90/120 → 2026-06-11)
can never enter. The 1,462 at-risk profiles are permanently invisible to them.

**Fix (catch-up, one-time + continuous):**
1. Create segment `Winback Catch-Up — Lapsed 60d+`:
   Placed Order zero times in the last 60 days AND Placed Order at least once
   over all time AND not suppressed.
2. Clone "Win-Back 60 Days v2" → trigger: **Added to segment** (the new one).
   Set the clone LIVE **before** saving the segment definition (or immediately
   after creating the empty segment) so the initial population flows in.
3. Keep the existing metric-triggered flows live for customers lapsing later
   (add an exclusion so nobody gets both: profile not in the catch-up flow).
Expected: benchmark winback economics on 1,462 profiles ≈ R3–6k/mo initially.

## 2. PCOS Post-Purchase — fires on every order

Trigger is Placed Order with `trigger_filter: null` → all 302 June buyers got
PCOS content; R0 revenue is the predictable result.

**Fix:** Flow → trigger setup → add trigger filter:
`ItemNames contains "Pcositol"` (add the other PCOS SKUs/collection handles).
Alternatively re-point to a "Bought PCOS product" segment.

## 3. Abandoned checkout + post-purchase — the money flows are in draft

`Abandoned Checkout Reminder - Standard (Email & SMS)` (multi-touch) and
`Post-Purchase Thank You + Cross-sell v3` were both set to **draft on
2026-06-18**, leaving only the single-email "Consultant Check (2026 design
system)" variants live. Result: 36 abandoned-cart recipients/month on ~220
monthly abandoners; post-purchase revenue R0.

**Decision needed (owner):** either
- **(a) Revive the Standard flows** after re-skinning them to the 2026 design
  system, with mutual exclusions vs the Consultant Check flows so nobody is
  double-mailed (recommended — multi-touch abandoned cart is where the 3–5%
  recovery benchmark comes from); or
- **(b) Extend the Consultant Check flows** with 2nd/3rd touches (48h value
  email, 72h STACK5 nudge) and a post-purchase cross-sell branch.

## 4. Shipping policy scope (blocking the automated C1 fix)

`update-shipping-policy.yml` ran and was denied: the admin token lacks
`read_legal_policies` / `write_legal_policies`. When reinstalling the custom
app (already required — the `app_not_installed` OAuth failures), add both
scopes; then re-run the workflow (Actions → Update Shipping Policy). Until
then: paste the corrected text (see workflow script `NEW_BODY`, or the file
Claude delivered in chat) into Settings → Policies → Shipping policy.

## Status of the other focus flows (healthy)

- Welcome (Full Sequence): live, list-triggered — the top earner; untouched.
- Replenishment Reminder (API-created): live, earning; untouched.
- Browse Abandonment v2: live, earning; untouched.
- Sunset Unengaged: live (list-triggered).
