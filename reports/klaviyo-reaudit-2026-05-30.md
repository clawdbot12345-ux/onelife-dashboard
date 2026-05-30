# One Life Health — Klaviyo Re-Audit (post-Codex verification)

**Date:** 2026-05-30 (after Codex executed the handover; PR #7 merged) · **Account:** Klaviyo `S86r7e`
**Method:** live API re-pull, checked against `reports/codex-handover-2026-05-30.md` Definition of Done.

## Scorecard vs Definition of Done

| # | Item | Before | Now | Status |
|---|---|---|---|---|
| 1 | Win-back sent (throttled, At-risk) + scaffolds deleted | draft | **Sent to 2,087; v1/v2 deleted** | ✅ |
| 2 | Brand = "One Life Health" everywhere | mixed | **account sender = "One Life Health"; 48/48 campaigns "One Life Health"** | ✅ |
| 3 | Email List ≈ 2k (no welcome misfire) | 768 | **2,901**, Welcome flow only 12 recipients/7d (no spike) | ✅ |
| 4 | Post-Purchase Thank-You flow fixed | R0 | **R2,487 / 7d, 55% open, 3 conv** | ✅ |
| 5 | JJA drafts scheduled to Engaged-90d on their dates | drafts | **Scheduled Jun 5 – Aug 14** | ✅ (1 issue ↓) |
| 6 | QA/test + cancelled dupes purged; Sent kept | 76 campaigns, ~13 junk + 10 QA lists | **48 campaigns, 0 QA/test; lists down to 5 real** | ✅ |
| 7 | Templates de-bugged / branded | — | sender labels all correct | ◑ verify preview-text bug fix in UI |
| 8 | Deliverability / Sunset live | — | win-back bounce 2.1%, spam 0.096% | ◑ watch (see below) |

## Performance step-change
- **Win-back campaign:** 2,087 recipients · **41.8% open · 6.2% click · 27 orders · R18,343** — single biggest-earning email in the account's history (prior 3.5 months of campaigns combined ≈ R9k).
- **Flows (last 7 days):** Post-Purchase R2,487 · Replenishment R2,103 (10.3% conv) · Win-Back flow R1,548 · Welcome R690.
- **~R25k email-attributed revenue in one week** vs ~R34k in the *entire* prior 3.5 months. (Caveat: the win-back is a one-off dormant re-engagement; it won't repeat at that size — but the flow/segment foundation now compounds.)

## 🔴 New issue found — fix before 14 Aug
- **Duplicate scheduled campaign:** the **"JJA 2026 | 2026-08-14 | Nootropics & Brain Supplements"** campaign is **scheduled 6 times** for the same date/time (06:00 UTC) to **Engaged-90d**. Left as-is, that segment could receive the same email up to 6× on Aug 14 (Smart Sending mitigates but does not guarantee dedupe across separate campaigns).
  - **Action (UI / Codex):** delete **5 of the 6**, keep one. Verify no other JJA date has duplicates (all others are 1× and correct).

## 🟡 Watch / next
- **Win-back deliverability:** bounce 2.1% (just over 2%) and spam 0.096% (just under 0.1%) — normal for a long-dormant blast, but **do not re-send to its non-openers**; let the **Sunset flow** suppress non-engagers so reputation recovers.
- **Ongoing list hygiene:** Email List is now 2,901 incl. formerly-dormant buyers. Good that JJA campaigns target **Engaged-90d** (not the full list) — keep newsletters on engagement segments; rely on Welcome/Sunset for the rest.
- **Confirm in UI:** preview-text-in-body bug removed from templates (Task 8); product-image + review/social-proof blocks added to the standard template; SPF/DKIM/DMARC aligned (Task 9).
- **Dashboard refresh:** confirm the next 06:00 UTC run shows real numbers (secret rotation / Task 10) — the zero-write guard is already in place.

## Bottom line
Codex delivered: brand locked to **One Life Health**, list rebuilt **768 → 2,901** with no welcome-flow misfire, account de-cluttered, the dead post-purchase flow now earning, the content calendar scheduled to the right segment, and a re-engagement send that pulled **R18.3k**. One cleanup remains (5 duplicate Nootropics sends) plus routine deliverability monitoring.
