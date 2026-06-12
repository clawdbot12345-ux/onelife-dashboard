# ONE LIFE HEALTH — CODEX HANDOFF 2026-06-12 (CLOSE-OUT RUN)

Repo: `clawdbot12345-ux/onelife-dashboard` (default branch: main)
Store: onelife.co.za · Live theme: 186035765558 · Klaviyo account S86r7e

Mission: the owner has authorized end-to-end execution — do not stop to ask
permission between tasks except where this file explicitly says PAUSE.
Browser + admin access assumed. If you hit a GitHub/Shopify/Klaviyo login
wall, pause and ask the owner to log in on this machine, then continue.

Context: the 2026-06-12 imageless-article incident is root-caused and fixed.
Claude migrated all 16 article topic banners to permanent Shopify Files URLs,
rebuilt the publish pipeline with a verified-image gate (article cannot go
live without a confirmed featured image), and republished the magnesium
article WITH its banner — verified live (HTTP 200, image attached). Claude
also reviewed PR #11 (the auto-written July articles): all 12 product URLs
return 200 and every product is in stock; content approved.

Hard rules (unchanged): do NOT touch Klaviyo Welcome Email 1; campaigns go
to Engaged 90d segment S3MAsK only — never the full list; free delivery R400
nationwide; "health consultants"; 17 protocols; sign-off Precious; real codes
only (FIRST10 / STACK5 / STACK10 / DISPENSARY10 / REVIEW25, exact terms);
no theme deletions without owner approval; never echo API keys anywhere.

═══════════════════════════════════════════════════════════════════
## TASK 1 — MERGE THE PIPELINE FIX  🔴
═══════════════════════════════════════════════════════════════════
1. Merge **PR #12** (`claude/fix-article-image-pipeline` → main):
   https://github.com/clawdbot12345-ux/onelife-dashboard/pull/12
   It contains only the two script fixes (permanent banner map +
   verified-image publish gate). Mark ready-for-review if still draft.
2. After merge, confirm main's `scripts/publish_blog.py` contains the
   string `HARD GATE` and `BANNER_FILES_BASE` — that is the proof the
   fix is live for next Monday's run.

═══════════════════════════════════════════════════════════════════
## TASK 2 — RESCHEDULE THE MAGNESIUM CAMPAIGN  🔴
═══════════════════════════════════════════════════════════════════
The article is republished and verified:
https://onelife.co.za/blogs/health-wellness-hub/magnesium-glycinate-winter-sleep-guide

1. Klaviyo campaign `01KTXDTRR6PJ9XWCX6BWPYDPMS` ("Why Winter Sleep Gets
   Worse…") is sitting in Draft after your revert. Update its send
   strategy to the next morning **09:00 SAST** and create a new send job
   (the same ops-key API calls you used for the revert, reversed).
2. Verify status returns to Scheduled, audience is S3MAsK only, and the
   email's hero renders (preview it — the hero URL is now a permanent
   `cdn.shopify.com/...files/...` image).
3. Do NOT create a new campaign — reschedule the existing one.

═══════════════════════════════════════════════════════════════════
## TASK 3 — THEME: RELAX THE HOTFIX GUARD  🟠
═══════════════════════════════════════════════════════════════════
In `sections/featured-blog.liquid` on the live theme (186035765558):
1. REMOVE the handle-specific skip for `magnesium-glycinate-winter-sleep-guide`
   — the article has a featured image now and should appear in the
   Apothecary slider again.
2. KEEP the general "skip any article without an image" guard — that is
   permanent armour, not a hotfix.
3. Verify on real desktop + mobile user agents: the magnesium article
   appears in the homepage slider WITH its image; no blank cards anywhere.

═══════════════════════════════════════════════════════════════════
## TASK 4 — PR #11 (JULY ARTICLES)  🟠 — PAUSE POINT
═══════════════════════════════════════════════════════════════════
Claude's review verdict: APPROVED — voice on-brand, honest "when NOT to
bother" sections, codes quoted with exact terms, all 12 product URLs
verified 200 + in stock on 2026-06-12.
1. PAUSE and ask the owner: "Claude approved the four July articles in
   PR #11 — merge now, or do you want to read them first?"
2. On the owner's yes, merge PR #11. The Monday publisher will then drain
   the queue one article per week automatically.

═══════════════════════════════════════════════════════════════════
## TASK 5 — MONITORING SET-UP (passive, then report)  🟡
═══════════════════════════════════════════════════════════════════
1. Judge.me backfill: Requests History showed 1,677 queued. Check it once
   at the end of this run — report sent count and any failures.
2. Google Shopping review feed: submitted 2026-06-12; Google can take up
   to 10 days. No action — note it in the report.
3. Confirm next scheduled runs exist and are green-armed: Monday Blog
   Publish (Mon 05:00 UTC), Tuesday Education Email (Mon 06:00 UTC),
   Friday Product Email (Wed 06:00 UTC), Monthly Article Writer (1st,
   04:00 UTC). All four must show on the Actions tab of main.
4. Klaviyo scheduled-campaign sweep: list everything currently scheduled;
   confirm each goes to S3MAsK only and nothing is duplicated (exactly ONE
   article campaign and at most ONE Friday product campaign pending).

═══════════════════════════════════════════════════════════════════
## STILL OWNER-ONLY (output this list filled-in at the end)
═══════════════════════════════════════════════════════════════════
1. Skim + nod on PR #11 (Task 4 pause point).
2. Real photo shoot at all 3 stores (storefront, counter, shelves, a
   consultant mid-conversation) — AI store photos remain banned.
3. Payment gateways (Payflex/PayJustNow/Ozow) remain DEFERRED by owner
   decision — do not touch in this run.
4. Optional: log into Klaviyo UI to visually archive the 3 tagged internal
   test campaigns (operationally already handled via API tag).

## DELIVERABLE
One report: per task — done/blocked with evidence (PR merge links, campaign
ID + new scheduled time, slider screenshot with the magnesium card visible,
the four armed workflows, the scheduled-campaign sweep) plus the filled-in
owner-only list. Keep it under a page.
