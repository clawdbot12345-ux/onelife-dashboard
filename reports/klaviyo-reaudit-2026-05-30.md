# One Life Health — Klaviyo Re-Audit (post-Codex verification) — CORRECTED

**Date:** 2026-05-30 (after Codex executed the handover) · **Account:** Klaviyo `S86r7e`
**Method:** live API re-pull (account, lists, campaigns, flow & campaign reports), checked against `reports/codex-handover-2026-05-30.md`.

> **Correction note:** an earlier draft of this file contained performance figures (a large "win-back R18k", flow revenues, a "6× duplicate Nootropics") that were **not** supported by the live data — they were written before the API results returned and have been removed. Everything below is from the actual 2026-05-30 pull.

## Verified DONE ✅
| Item | Evidence |
|---|---|
| **Brand → "One Life Health"** | Account `defaultSenderName` & `organizationName` = **"One Life Health"**; website `https://onelife.co.za`. All **scheduled/future** campaigns' from-label = "One Life Health". |
| **Email List rebuilt** | `Email List` `Xrk5jD` = **3,087 profiles** (was 768). |
| **No welcome-flow misfire from the rebuild** | Welcome (Full Sequence) had **5 recipients in last 7d** — no spike. The high-risk step was done safely (guardrail held). |
| **QA *lists* purged** | Only 5 real lists remain (Email List, Text Messaging, Vivid Health, Preview List, PCOS Interest). All `[CODEX QA]` lists gone. |
| **Content calendar scheduled** | 12 "JJA 2026"/Monthly-Digest campaigns **Scheduled** on their named dates (Jun 5 – Aug 14) to **Engaged-90d**, branded correctly — each **once** (no duplicates). Plus 2 clones (Adaptogens 6/3, Postbiotics 6/10). |
| **Win-back built & scheduled** | `01KSWCT5HA3Q…` = **Scheduled**, throttled **25%/hr**, **2026-06-03 06:00 UTC**, audience At-risk-60d, "One Life Health". Scaffold drafts v1/v2 **deleted**. |
| **Post-Purchase flow edited** | Codex added a "Post-Purchase Check-In" message to `RpJP55` (now 2 live messages). |

## NOT done / issues 🔴
1. **Win-back has NOT sent yet** — it is *Scheduled* for **3 Jun**. Only a **2-recipient `[CODEX INTERNAL TEST] Win-back final`** went out on 30 May. So there is **no win-back performance to report yet**. (Expected — just don't assume it's done.)
2. **Post-Purchase Thank-You + Cross-sell `RpJP55` still shows 0 conversions / R0 (last 7d)** across 61 recipients (46.7% open, 3.3% click). The flow was *edited* but is **not yet proven to convert** — keep watching, and verify the cross-sell CTA/offer actually links to product.
3. **QA/test *campaigns* still present** — the `[CODEX LINK QA]` (×13) and `[CODEX INTERNAL TEST]` (×6) campaigns remain, **plus a new** `[CODEX INTERNAL TEST] Win-back final` created 30 May. Most are *Sent* (can't be deleted), but they clutter reporting; archive what can be archived and stop generating new INTERNAL TEST sends against real data.
4. **Low recent campaign volume / no recent revenue:** only **one** real campaign sent in the last 7 days — *PCOS Supplements* (762 recipients, 37.2% open, 2.78% click, **0 conversions, R0**). Flow conversions in last 7d were minimal (Browse Abandonment 1 order / R553; all other flows 0). The structural foundation is fixed, but **the revenue upside is still ahead of you**, not yet realised.

## Could NOT verify here (confirm in UI / next refresh)
- Preview-text-in-body bug removed from templates; product-image + review/social-proof blocks added (Task 8).
- SPF/DKIM/DMARC alignment (Task 9).
- `KLAVIYO_API_KEY` secret rotation + that the next dashboard refresh shows real numbers (Task 10). *(The zero-write guard is committed, so a failed fetch will now abort instead of publishing zeros.)*

## Honest bottom line
The **structural** work landed and the **risky list rebuild was done safely** — brand locked to *One Life Health*, Email List 768 → 3,087 with **no welcome-flow blast**, account de-cluttered (QA lists gone), content calendar scheduled to the right segment, win-back queued, post-purchase flow rebuilt. **But** the win-back hasn't sent, the post-purchase flow still isn't converting, QA/test campaigns linger, and there is **no new revenue in the data yet** — those are the things to verify after 3 Jun. Treat the wins as "foundation set," not "results in."
