# Codex Work-Order — Klaviyo Program Fixes (2026-06-18)

Source audit: `reports/klaviyo-audit-2026-06-18.md` (read it for evidence/numbers).
Account: One Life Health · onelife.co.za · Klaviyo · ZAR · sender info@onelife.co.za.
Conversion metric "Placed Order" = `WZAxyj`. Engaged-90d segment = `S3MAsK`.
Email List = `Xrk5jD` (single opt-in). Most edits are **Klaviyo UI** (flow timing,
filters, templates, account settings) — there is no flow-write API, so apply by hand
and verify in-app. Owner approval needed only for the account-settings toggles in §4.

## Canonical brand facts — EVERY template/subject must match these
Grep all live templates + scheduled subjects and make them consistent with:
- **Free delivery over R400 nationwide** · collect free at Centurion · Glen Village · Edenvale · since 1996.
- Brand green **#1b4332** (card/header), footer **#14291e**. Kill the old **#1B5E20 / #2e7d32**.
- Approved codes ONLY: **FIRST10, STACK5, STACK10, DISPENSARY10, REVIEW25**. `WELCOME10` is NOT approved.
- Sign-off **"— Precious / One Life Health Consultant · Centurion"**.
- Say **"consultants"** — never "pharmacists" or "coaches".
- Unsubscribe = liquid **`{% unsubscribe %}`**, never `{{ unsubscribe }}`.
- Georgia serif display H1; "Hi {{ first_name|default:'there' }} — Precious here…".
- **Gold-standard templates to clone/extend:** `UyBg38` (Cart Consultant), `WbpTF3` (Review Request).
  These are the ONLY template lineage going forward.

---

## P0 — stop the bleeding (this week)

1. **Browse Abandonment body is still creepy.** Flow `UMMzhC` timing is fixed, but its email
   template **`TJiVpH`** still renders `<h1>Still thinking about {{ event.Name }}?</h1>`.
   → Rewrite the body on the 2026 design system: remove that headline (use a light, helpful line
   e.g. "A little help choosing, if it's useful"), green #1b4332, add "— Precious", remove the
   `via.placeholder.com` image fallback (renders as a grey/broken box). **Done when:** preview shows
   no "still thinking" language, correct green, Precious sign-off, no broken image.

2. **De-conflict the 3 cart flows (same "Checkout Started" trigger).** `VAjbpG` (old, Smart Sending OFF)
   + `WY4cae` (2026 email) + `VSECqx` (2026 SMS) can stack to **5 touches per cart**.
   → Keep **WY4cae (email) + VSECqx (SMS)** as the ladder; **retire/disable VAjbpG**. Add cross-flow
   exclusion so they can't double-fire ("has not been in [sibling flow] in last 7 days"), and ensure
   **one SMS per cart**. Turn Smart Sending ON. **Done when:** a single test checkout enters exactly one
   email ladder + at most one SMS.

3. **Fix Welcome Email 1** (template **`UfSdB9`**, flow `XZNrmz`) — your top revenue asset, currently
   contradicting the website:
   - "Free delivery over R900 (Gauteng)/R1,400 (nationwide)" → **R400 nationwide**
   - code **WELCOME10** → **FIRST10** (or get WELCOME10 formally approved by owner)
   - green **#1B5E20 → #1b4332**; add **"— Precious"**; `{{ unsubscribe }}` → `{% unsubscribe %}`.

4. **Fix Replenishment email 1** (template **`VHbPFG`**, flow `TNBkZK`): "spend over **R600**" → **R400**;
   align green; add Precious sign-off.

5. **Pause or rebuild Post-Purchase Cross-sell v3** (`RpJP55`) — **R0 from 386 recipients at 1.58% unsub** =
   pure annoyance. Pause now; rebuild later with real dynamic "pairs-with-what-you-bought" product blocks.

6. **Fix the Sunset flow** (`YrtdaV`): delays currently run on **US/Eastern** → switch to
   **Africa/Johannesburg**; the final step only sets `Unengaged=true` and **never suppresses** → add a real
   action that removes unengaged profiles from marketing (unsubscribe/suppress or pull them out of all
   campaign segments). **Done when:** unengaged profiles actually stop receiving campaigns.

7. **Reporting hygiene:** archive the ~20 `[CODEX TEST]`/`[LINK QA]` campaigns, and fix the scheduler that
   created/cancelled dozens of duplicate "Apothecary Guide Drip / Monthly Digest / JJA" campaigns on
   2026-06-18 (it's thrashing — find the script/automation and stop the loop).

---

## P1 — guardrails & consolidation (2–3 weeks)

8. **Implement the Global annoyance guardrails in §4 below.** (Highest-leverage of everything here.)
9. **Merge the duplicate win-backs** `TGZYKa` (60d) + `SFMncG` (90/120d) into ONE 60/90/120 ladder with a
   single clean hand-off to Sunset (no overlapping windows).
10. **Replenishment:** add "has not purchased since flow start" to every step so re-orderers stop getting it.
11. **Campaign cadence cap:** max ~**2 marketing campaigns/week to Engaged**; max **2 full-list/month**. Space
    the current clustering (it hit 5 sends in 13 days). Default every campaign to **Engaged 90d (`S3MAsK`)**.
12. **Brand-term sweep:** fix the subject "…What Our **Pharmacists** Actually Recommend" → "consultants".
    Grep all live subjects + templates for "pharmacist", "coach", "R600", "R900", "R1,400", "WELCOME10",
    "#1B5E20" and fix every hit.

---

## P2 — finish world-class (3–4 weeks)

13. **Migrate ALL flow/campaign templates onto the 2026 design system** (`UyBg38`/`WbpTF3` lineage); retire the
    "Flow Hero Refresh 20260531" family so there is one green, one footer, one R400 line, one sign-off.
14. **Dynamic product blocks** in Cross-sell + Replenishment (real reorder/pairing, not generic copy).
15. **Consent decision (POPIA):** either keep single opt-in **with** the fixed/enforced Sunset + suppression
    above, OR add a confirmed-opt-in step for behavioral (browse) marketing. Add **"engaged in last 90 days"**
    as a required filter on Browse Abandonment (`UMMzhC`).
16. **Revive the list-growth engine** (signup forms: popup + embed + exit-intent → `Xrk5jD`) — still the #1
    ceiling on Welcome-flow revenue (see SEO/Klaviyo handover).

---

## §4 — Global annoyance guardrails (owner approves the account toggles)

These structural controls are mostly ABSENT today and are what stop a complaint like this recurring:
1. **Account-level frequency cap** (Klaviyo → Settings): **≤ 3–4 marketing emails / 7 days per profile**,
   applied to flows + campaigns. ← single biggest protection.
2. **Global Smart Sending ON** for all marketing (currently OFF on the cart flows).
3. **Cross-flow exclusion on shared triggers:** any two flows on the same metric (Checkout Started, Placed
   Order) must carry "not in [sibling flow] in last N days". No two flows fire for one event.
4. **Engaged-only defaults:** behavioral/promo flows + all campaigns default to Engaged 90d (`S3MAsK`);
   full list reserved for ≤2 announcements/month.
5. **Browse/abandon caps:** Browse = 30-day in-flow cap (done) + 24h delay (done); cart = one consolidated ladder.
6. **SMS guardrails (keep what's good):** consent-gated + quiet hours ON (already set); one text per cart; add a
   weekly SMS cap.
7. **Enforced Sunset (SAST) with real suppression** — keeps long-term campaign unsub/spam down.
8. **One template system + one set of brand facts** so no send can contradict the website again.

---

## Definition of done
- [ ] Browse body (`TJiVpH`) rewritten — no "still thinking", correct brand, no broken image
- [ ] Cart flows de-conflicted to 1 email + 1 SMS ladder, Smart Sending ON, cross-flow exclusion
- [ ] Welcome Email 1 (`UfSdB9`) + Replenishment (`VHbPFG`) brand facts corrected (R400, code, green, Precious, unsub tag)
- [ ] Cross-sell `RpJP55` paused (or rebuilt with product blocks)
- [ ] Sunset `YrtdaV` on SAST + actually suppresses; unengaged stop getting campaigns
- [ ] Test/duplicate campaigns archived; thrashing scheduler stopped
- [ ] Account frequency cap + global Smart Sending live (owner approved)
- [ ] Win-backs merged; Replenishment "not purchased since" added; campaign cadence capped
- [ ] Brand-term sweep clean (no pharmacist/coach/R600/R900/WELCOME10/#1B5E20 live)
- [ ] All flow templates on the 2026 design system; Browse requires engaged-90d
- [ ] Spot-check: one test profile cannot exceed the weekly cap across all flows+campaigns
