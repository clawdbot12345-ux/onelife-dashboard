# Codex task: Omni ERP pipeline bootstrap — HIGH PRIORITY

Date: 2026-06-12 · From: Growth Engine (cloud Claude session) · Unblocks: T2–T4 store baselines, Vivid GP% verification, product matrix

## Context
Naadir granted access to the Omni ERP web report server (the "Sales Analysis Johann Custom" report URL he shared on 2026-06-12 — **get the URL directly from Naadir; do NOT commit it or its credentials anywhere in the repo**). The cloud Claude environment cannot reach port 59029 (egress limited to standard ports), so ingestion must run from GitHub Actions or the Mac Mini.

## Steps
1. Set the repo secret (one-time):
   ```
   gh secret set OMNI_REPORT_URL --repo clawdbot12345-ux/onelife-dashboard
   ```
   Paste the full report URL (including UserName/Password/CompanyName query params) when prompted.
2. Trigger the probe:
   ```
   gh workflow run omni-probe.yml --repo clawdbot12345-ux/onelife-dashboard --ref claude/end-to-end-goal-tdcj0f
   ```
3. Verify the run commits `data/omni/probe/SUMMARY.md` + response samples to the branch (it explores the main report, export-format variants, and likely report-index paths, credential-redacted).
4. **Faster alternative/addition:** if the Mac Mini can reach `102.22.82.27:59029` directly, run locally from the repo root and push:
   ```
   OMNI_REPORT_URL='<url from Naadir>' python3 scripts/omni_probe.py
   git add data/omni/probe && git commit -m "Omni probe results (local)" && git push origin claude/end-to-end-goal-tdcj0f
   ```
5. Bonus if time allows: in the Omni report UI, note the full list of available reports (names + parameters) and append them to `data/omni/probe/SUMMARY.md` — the engine will pick which to ingest daily and then design the per-store dashboard around them.

## Definition of done
`data/omni/probe/SUMMARY.md` exists on `claude/end-to-end-goal-tdcj0f` with ≥1 successful (HTTP 200) response from the report server. The cloud engine takes it from there (parser + scheduled sync + stores dashboard).

## Also queued: social login handover
Naadir is cutting the agency from socials. When he hands over logins (FB "One Life Health Supermarket" 24K / TikTok @onelifehealthstore 10.6K / IG @one_life_health_supermarket 1.4K), store them in the Mac Mini keychain — NOT in the repo — and confirm posting access works. Engine will start supplying weekly content packs (copy from engine, imagery via the existing gpt-image-2 pipeline).
