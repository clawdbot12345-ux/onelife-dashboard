# Klaviyo Wiring Guide — 15-minute owner session
All templates are built and waiting in your template library (search "2026 design system").
Klaviyo's API can't safely edit live flow structure, so these final connections are
click-work in the Klaviyo UI. Total: ~15 minutes.

## 1. Welcome flow (XZNrmz) — swap the two weak emails (3 min)
- Open the flow → Email 2 ("Top Picks") → Change template → **[FLOW v2] Welcome #2 — Which stack is yours?**
- Email 3 ("WELCOME10 Expiry") → Change template → **[FLOW v2] Welcome #3 — Why people trust the apothecary**
- ⚠️ Check which code the flow actually issues (WELCOME10 vs FIRST10) and make the
  template code box match — one of the two names is stale.
- Do NOT touch Email 1. It earns R97/recipient. It is sacred.

## 2. Post-Purchase flow (RpJP55) — revive the R0 cross-sell (2 min)
- Email 2 ("Post-Purchase Check-In") → Change template → **[FLOW v2] Post-Purchase #2 — Pairs well with your order**

## 3. Winback flow — NEW (4 min)
- Flows → Create → from scratch → Trigger: **Date-based on last Placed Order** is fiddly;
  simpler: Metric trigger "Placed Order" → Time delay 60 days → Conditional split
  "Placed Order zero times since starting this flow":
  - 60d: existing template **[FLOW] Winback 60d — We kept your spot (Precious)**
  - +30d, still no order: **[FLOW] Winback 90d — Your shelf misses you**
  - +30d, still no order: **[FLOW] Winback 120d — Should we stop emailing?**
- Smart Sending ON, set live.

## 4. Back in Stock flow — NEW (3 min)
- Flows → Create → Trigger: metric **Subscribed to Back in Stock**
- Single email, no delay: **[FLOW] Back in Stock — It's back**
- The website form + metric are already wired (theme back-in-stock snippet) — this
  is free money currently going nowhere.

## 5. Abandoned Checkout flow (VAjbpG) — widen + extend (3 min)
- Add Email 3 after a 24h delay: **[FLOW] Abandoned Cart #3 — A consultant can check your basket**
- Trigger gap: this flow only fires on Checkout Started. Create a parallel
  "Added to Cart Abandonment" flow → Trigger: Added to Cart → flow filter:
  "Checkout Started zero times since starting this flow" AND "Placed Order zero
  times since starting this flow" → 4h delay → reuse Email 1 template.
- The flow name promises SMS — either add the SMS step or rename the flow.

## 6. Campaign hygiene (2 min)
- Archive the ~20 campaigns named "[CODEX INTERNAL TEST]" / "[CODEX LINK QA]" /
  "[CODEX GPT IMAGE TEST]" — they pollute every report.
- New default audience for ALL campaigns: segment **Engaged 90d** (S3MAsK).
  (The two repo generators — Friday Spotlight & blog campaigns — already default
  to it as of today's commit.) Full list max 2×/month for true announcements.

## Codes sanity check
Live in templates: FIRST10 (welcome), DISPENSARY10 (protocols), STACK5/STACK10.
Verify all four exist in Shopify discounts and match these descriptions.

## Security note 🔐
A Klaviyo private API key was committed in `scripts/build_replenishment_flow.py`
(it returns 401 now — appears rotated, good). Remove the hardcoded fallback from
the script and keep keys only in env vars / GitHub secrets.
