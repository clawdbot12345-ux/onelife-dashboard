# NEEDS — open asks of Naadir, ranked by what they unblock

Last updated: 2026-06-12

| # | Ask | Unblocks | Status |
|---|---|---|---|
| 1 | **Omni ERP access** — ✅ GRANTED 2026-06-12 (web report server, read-only `analytic` user). Cloud sandbox can't reach port 59029 → ingestion runs via GitHub Actions (`omni-probe.yml`, then a scheduled sync). **Follow-ups:** (a) add repo secret `OMNI_REPORT_URL` so creds live nowhere visible, (b) recommend restricting/rotating that account later — it's exposed on a public IP. | T2–T4 baselines, GP% per SKU, product matrix | IN PROGRESS |
| 1b | ~~T1 deadline confirm~~ | — | ✅ RESOLVED 2026-06-12: Sep/Oct 2026 — engine paces to 31 Oct, Sep stretch |
| 2 | ~~Phase 0 interview~~ | — | ✅ COMPLETE 2026-06-12 (4 batches; minor leftovers: staff capacity hrs/week, per-store footfall, Centurion extended hours) |
| 3 | **Baseline definition decision** (BASELINES.md: TTM-avg×1.5 = R105.6k/mo, already touched — or May-2026×1.5 = R160.8k/mo stretch?) | Whether T1 is "consolidate" or "grow 50% from current run-rate" | OPEN — re-asked with batch 2 |
| 4 | ~~Budget month-1~~ | — | ✅ APPROVED 2026-06-12: R5k envelope, ≤R2k tests pre-approved |
| 5 | **Owner checkout actions** (carried from prior sessions): enable Apple Pay/Google Pay/Shop Pay; install Payflex or PayJustNow | Checkout completion 40%→60%, est. +R54k/mo — single highest-ROI action available | OPEN (pre-existing) |
| 6 | **Social logins handover** (FB/TikTok/IG — Naadir confirmed he'll provide; agency being cut from socials). Hand to Codex/Mac Mini keychain, not the repo/chat. Meta System User token still the better long-term path for ads+API posting. | Engine-run content across FB 24K / TikTok 10.6K / IG | IN PROGRESS — Naadir to deliver |
| 6b | ~~Omni probe execution~~ ✅ DONE 2026-06-12 — Codex ran it from the Mac Mini; server confirmed (Omni Web Server 7.21.68, JSON reports). **Next: `codex-queue/2026-06-12_omni-reports-v2.md`** — the existing report lacks date/store/item dimensions; need per-branch + per-item reports exposed (possibly via Johann, who built the current one). | T2–T4 baselines, Vivid GP, matrix v1.0 | IN PROGRESS — v2 task queued |
| 7 | **Google Business Profile manager access** (all 4 stores) | Local discovery engine for T2–T4, basically free | OPEN |
| 8 | **TikTok Business API** (or interim posting workflow) | Awareness engine distribution | OPEN |
| 9 | **Search Console access** | Branded-search baseline for T5, SEO gap tracking | OPEN |
| 10 | **WhatsApp Hub posting mechanism**: who posts today, and does the engine take over programming with a weekly content pack (Mon/Wed/Thu + VIP-exclusive early access)? Count confirmed: 410. | T5 — Hub is "terrible and not exclusive" per Naadir; fixing exclusivity is the whole growth mechanic | OPEN — proposed in batch 2 |
| 11 | **Telegram gateway wiring** (approvals → flag files) | Async approval loop per GROWTH_ENGINE.md execution model | OPEN — chat works as interim |

## Resolved
(none yet)
