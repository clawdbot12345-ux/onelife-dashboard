# Handover → Codex v2 (remaining items)

**Date:** 2026-05-30 · After re-audit (`reports/klaviyo-reaudit-2026-05-30.md`). Claude fixed everything possible via API/repo; the rest below needs the **Klaviyo UI, GitHub secrets, or DNS** — out of API reach.

**Done by Claude this round:** confirmed brand/list/scheduling are correct; verified the win-back is *Scheduled* (throttled 25%, 3 Jun, smart-sending on); merged the dashboard zero-write guard + API-revision fix to `main`. Carry over ALL global guardrails from `codex-handover-2026-05-30.md` (consent-only, Smart Sending on, "One Life Health", test-before-send, never delete Sent campaigns, throttle dormant, never re-trigger flows on list changes, SAHPRA claims, STOP if bounce >2% / spam >0.1%).

## 1. Dashboard data — DO FIRST 🔴
The live dashboard still shows **0 subscribers / R0** because the GitHub Actions `KLAVIYO_API_KEY` secret is broken/missing (root cause of the zeros).
- **Settings → Secrets and variables → Actions →** rotate **`KLAVIYO_API_KEY`** (scopes: Metrics, Campaigns, Flows, Lists, Segments, Profiles — all Read).
- **Actions → "Daily Dashboard Refresh" → Run workflow.**
- Confirm `index.html` now shows real numbers (Email List ≈ **3,087**, real open rate). The corrected script (now on `main`) will **abort instead of writing zeros** if the key fails — so if it's still zero, the key is still wrong.

## 2. Post-Purchase Thank-You + Cross-sell flow `RpJP55` 🔴
Still **0 conversions / R0** (last 7d, 61 recipients, 47% open, 3.3% click) despite Codex's edit.
- Open the flow → the cross-sell email → verify the product CTA links to a **live product/collection** (not a dead or blog URL), add a first-reorder incentive, test, and confirm conversions start. 47% open with 0 conversion = the click/offer path is broken, not the audience.

## 3. Stop & clean test/QA campaigns 🟠
- A **new** `[CODEX INTERNAL TEST] Win-back final` (2 recipients) was sent against the live account on 30 May. **Do not run INTERNAL TEST sends against production again** — use a dedicated seed list.
- Archive what's archivable of the `[CODEX LINK QA]` (×13) and `[CODEX INTERNAL TEST]` (×6) campaigns. (Most are *Sent* and can't be deleted — leave those; just stop creating more.)

## 4. Rename the "(clone)" scheduled campaigns 🟡
`Adaptogens … (clone)` (3 Jun) and `Postbiotics … (clone)` (10 Jun) → give proper names. Confirm no topic collides with a JJA send within ~5 days (currently fine). Rule: ~one topic/week to Engaged-90d.

## 5. Win-back monitoring (auto-sends 3 Jun) 🟡
Throttled 25%/hr to At-risk-60d. Watch **bounce (<2%)** and **spam (<0.1%)**; route non-openers into the **Sunset** flow; **do not resend** to non-openers.

## 6. Template uplift 🟢
Add **product-image blocks** + a **reviews/social-proof** block to the standard campaign template (save as Universal Content). Library templates are already clean of the preview-text bug; spot-check that no campaign-message template prints "Preview text:" in the body.

## 7. Deliverability 🟢
Confirm **SPF / DKIM / DMARC** aligned for `onelife.co.za` (Settings → Domains). Keep the Sunset flow live.

## Definition of done (v2)
- [ ] `KLAVIYO_API_KEY` rotated; refresh run; dashboard shows real numbers.
- [ ] Post-Purchase flow converting (>0) after CTA fix.
- [ ] No new INTERNAL TEST sends to production; QA campaigns archived where possible.
- [ ] "(clone)" campaigns renamed; no topic collisions.
- [ ] Win-back sent 3 Jun; bounce/spam within limits; non-openers → Sunset.
- [ ] Product + review blocks in standard template.
- [ ] SPF/DKIM/DMARC confirmed.
