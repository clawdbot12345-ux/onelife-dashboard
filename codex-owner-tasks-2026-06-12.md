# ONE LIFE HEALTH — CODEX HANDOFF 2026-06-12 (OWNER-TASK INITIATION)

Repo: `clawdbot12345-ux/onelife-dashboard` · branch: `claude/onelife-health-review-lwvi3-c3yry2`
Store: onelife.co.za (Shopify admin: onelifehealth.myshopify.com) · Klaviyo account S86r7e

Mission: the owner has authorized you to execute this file END TO END —
do not stop to ask permission between tasks; only the clearly marked
OWNER-ONLY steps are out of scope. You have browser + admin access on this
machine. Produce the completion report at the end.

ACCESS PROTOCOL: all GitHub steps (merging PR #10, secrets, variables,
running workflows) happen on github.com in the browser and require an
account with ADMIN rights on this repo. If you hit a login wall or a
permissions error at any point, PAUSE and ask the owner to log into
GitHub on this machine — then continue. Same rule for Shopify or Klaviyo
sessions if they have expired.
Work the tasks IN THIS ORDER — it is sorted by revenue impact.
NOTE (owner decision 2026-06-12): payment gateways (Payflex/PayJustNow/Ozow)
are DEFERRED — do not install or configure any payment provider in this run.

Hard rules (unchanged): never write to the live theme (duplicate → edit →
owner publishes); do NOT touch Klaviyo Welcome Email 1; never send to the
full list (Engaged 90d segment S3MAsK only); free delivery threshold is R400
nationwide; "health consultants" never coaches/pharmacists; 17 protocols;
sign-off Precious. Verify every change after making it; report with evidence.

═══════════════════════════════════════════════════════════════════
## TASK 0 — ACTIVATE + END-TO-END TEST THE AUTOMATION  🔴 DO FIRST
═══════════════════════════════════════════════════════════════════
GitHub only runs scheduled workflows from the DEFAULT branch. Nothing is
live until the branch merges and the secrets exist. Then test the whole
chain with manual dispatches, in this exact order.

**0.1 Merge the branch.** PR #10 (branch
`claude/onelife-health-review-lwvi3-c3yry2`) is already marked ready for
review — merge it to the default branch. It contains only additive docs,
scripts and workflows — no theme or storefront code. If GitHub blocks the
merge, apply the ACCESS PROTOCOL above (ask the owner to log in), then
merge.

**0.2 Secrets & variables** (GitHub → Settings → Secrets and variables →
Actions):
- Secrets: confirm `KLAVIYO_API_KEY`; add `SHOPIFY_CLIENT_ID`,
  `SHOPIFY_CLIENT_SECRET`; add `ANTHROPIC_API_KEY` — the owner will hand
  you the key directly; paste it into the GitHub secret field and never
  echo it into logs, files, commits, or your report.
- Variables: `EMAIL_AUTOMATION_ENABLED` = `true`;
  `ARTICLE_WRITER_MODEL` = the model id the owner gives you (they have
  chosen their writer model).

**0.3 The end-to-end test, in order (Actions tab → Run workflow):**
1. **"Monthly Article Writer (Claude)"** → verify it opens a PR titled
   "Monthly Apothecary articles: …" containing 4 new files in
   content/queue/, products verified. LEAVE THE PR UNMERGED for the owner
   to review — its existence is the pass.
2. **"Monday Blog Publish"** → verify: (a) newest queue article is LIVE at
   onelife.co.za/blogs/health-wellness-hub/<slug> with the topic banner
   showing on-page AND as featured image in the blog listing; (b) a
   Klaviyo campaign exists for it, design-system styled, audience S3MAsK,
   scheduled next morning 09:00 SAST; (c) the repo got a bot commit moving
   the file to content/published/ and updating scripts/.digest_state.json.
3. **"Tuesday Education Email"** → verify it logs a SKIP (the publisher
   already handled this article) — the skip IS the pass; a duplicate
   campaign is a fail.
4. **Workflow reconciliation (critical):** the default branch already has
   a LEGACY Friday workflow ("Friday Product Campaign") which you ran on
   2026-06-12 — after merging PR #10 there will be TWO Friday workflows
   calling the same script = double emails. DELETE the legacy workflow
   file from the default branch, keep "Friday Product Email". Then: a
   Friday campaign is ALREADY scheduled for this week from your earlier
   run — do NOT dispatch another one; verify next week's fires on cron.
5. Let the scheduled sends GO OUT — do not cancel them. Report all
   campaign IDs, the live article URL, and screenshots of one rendered
   email preview from Klaviyo.

The automation map after this task (the only human steps are starred):
Claude writes monthly → *owner merges article PR* → Monday robot publishes
+ schedules Tuesday email → Wednesday robot schedules Friday email → flows
run always-on → *owner glances at scheduled campaigns when curious*.

═══════════════════════════════════════════════════════════════════
## TASK 1 — REVIEWS ENGINE: activate the dormant Judge.me install  🔴
═══════════════════════════════════════════════════════════════════
Judge.me is ALREADY INSTALLED but dormant — PDPs show "No reviews" and no
request emails go out. This is the #1 remaining trust gap. Evidence: first
5 reviews = up to +270% purchase likelihood (Spiegel/Northwestern).
Configure ALL of the following in the Judge.me admin:

1. **Plan check:** confirm which plan is active. The features below need
   the Awesome plan (~$15/mo). If on Free, upgrade if a card is on file
   (owner pre-approved); otherwise flag and configure what Free allows.

2. **Review request email (the engine):**
   - Trigger: **14 days after fulfilment** (supplements need trial time).
   - Resend once after 7 days to non-openers. One request per order.
   - Exclude refunded/cancelled orders.
   - Sender "Precious at One Life Health", reply-to hello@onelife.co.za.
   - Style to the design system: deep green #1b4332 header with the logo,
     cream #f4f1ea background, Georgia serif heading, sign-off "— Precious".
   - Copy direction: "How's the [product] treating you?" — ask for honest
     feedback, mention the R25 thank-you, one tap per star.
   - **Ask for photo reviews** in the email (photo reviews convert best).

3. **Incentive (owner pre-approved):** create Shopify discount **REVIEW25**
   = R25 off, min purchase R250, one use per customer, and wire it as the
   Judge.me review-completion coupon (sent automatically after any review).

4. **Widgets — on a DUPLICATE of the live theme** (name it "GROWTH BUILD —
   REVIEWS <date> (ready to publish)"; never edit live):
   - PDP: star badge under the product title (the theme already reserves
     space — legacy CSS styles `[id*="judge_me_badge"]`; make it render),
     full Review Widget below the description.
   - Star ratings on product cards in collection grids.
   - Match the design system: cream #faf7f0 backgrounds, #1b4332 accents,
     no Judge.me branding colours. Screenshot PDP before/after.
   - Prepare (hidden/disabled for now) a homepage "What customers say"
     carousel section — Claude will switch it on once reviews ≥10.

5. **Q&A:** enable Judge.me Questions & Answers on PDPs — supplements are
   a question-heavy category. Route new-question notifications to
   hello@onelife.co.za so a consultant answers (answers signed "Precious,
   One Life Health Consultant").

6. **Moderation & replies:** auto-publish ALL ratings (authenticity beats
   curation), but set email notification on every ≤3-star review so the
   team replies publicly within 48h as Precious.

7. **SEO + Google:** enable Judge.me rich snippets (review stars in Google
   results) and the **Google Shopping product ratings** integration — this
   feeds star ratings into the Merchant Center free listings.

8. **All-reviews page:** enable Judge.me's all-reviews page, add it to the
   footer Information menu as "Customer Reviews".

9. **Backfill (the kick-start) — OWNER DECISION MADE 2026-06-12:** the
   3-day spread is dropped; Judge.me's immediate scheduling is approved.
   SEND the 90-day backfill now (one email per customer). Also finish the
   two leftovers from your last run: (a) complete the Google Shopping
   product-ratings feed once the Google & YouTube channel app loads —
   retry it; if the app page stays blank, flag it with a screenshot;
   (b) the rich email body edit that resisted Chrome — retry once via a
   different browser profile; if it still resists, the subject/title
   changes already shipped are sufficient.

10. **POPIA guard:** reviewers must NOT be auto-subscribed to marketing
    lists — leave any "add reviewers to newsletter" option OFF.

═══════════════════════════════════════════════════════════════════
## TASK 2 — KLAVIYO WIRING: ✅ COMPLETE (verified 2026-06-12)
═══════════════════════════════════════════════════════════════════
Done in your previous run: Welcome #2/#3 (YdyAkd→SCVRYn, Y9SA46→XizdxN)
and Post-Purchase #2 (RpUzMu→TD6cbs) assigned; Welcome Email 1 untouched.
Nothing further here.

═══════════════════════════════════════════════════════════════════
## TASK 3 — EMAIL CADENCE: covered by Task 0  ✅
═══════════════════════════════════════════════════════════════════
Superseded — Task 0 activates and tests the full cadence (secrets,
variables, and all four workflow dispatches). Nothing further here.

═══════════════════════════════════════════════════════════════════
## TASK 4 — SUBSCRIPTIONS GROUNDWORK (no app install yet)  🟡
═══════════════════════════════════════════════════════════════════
Shopify Payments is unavailable in SA and PayFast does NOT support Shopify's
Subscriptions API, so the gateway question decides everything:
1. Research + confirm (provider docs and/or support contact): does
   **Paystack** support Shopify Subscriptions API recurring charges for SA
   merchants? Does **Peach Payments**? Get a written/documented yes/no each.
2. Draft (do not send) the owner's enquiry email to the viable provider(s)
   requesting recurring-billing activation for onelife.co.za.
3. Report the verdict + recommendation (Appstle vs Seal on the viable
   gateway, or the Klaviyo "reminder autoship" fallback that works today).

═══════════════════════════════════════════════════════════════════
## TASK 5 — HOUSEKEEPING (quick)  🟡
═══════════════════════════════════════════════════════════════════
1. `sections/slideshow.liquid` on the next theme duplicate you make (Task 1
   step 4): change line ~142 `data-autoplay="{% if template == 'index'
   %}false{% else %}{{ section.settings.auto_rotate }}{% endif %}"` to
   `data-autoplay="{{ section.settings.auto_rotate }}"`, then DELETE the
   rotate() shim block from snippets/whatsapp-float.liquid. Both or neither.
2. Archive/label the 3 sent internal Klaviyo test campaigns in the UI so
   they stop polluting campaign analytics.
3. Klaviyo template cleanup: done in your previous run (0 pre-2026
   orphans) — skip.
4. **Fragile asset URL fix:** `assets/onelife-lifestyle-clarity-runtime.js`
   hardcodes a theme-numbered CDN URL
   (`/cdn/shop/t/38/assets/onelife-quiz-hero-banner-1440.webp`). It still
   serves today, but theme-numbered URLs die when that theme is deleted —
   upload the image to Shopify admin → Content → Files (permanent
   `/cdn/shop/files/` URL) and update the JS to point there (on a theme
   duplicate, owner publishes).

═══════════════════════════════════════════════════════════════════
## OWNER-ONLY LIST (output this filled-in at the end of your run)
═══════════════════════════════════════════════════════════════════
1. Publish the next theme duplicate once Tasks 1.4 + 5.1 land on it.
2. Phone photo shoot at all 3 stores (storefront, counter, shelves, a
   consultant mid-conversation) — for store pages + About. AI store photos
   are banned: they must be real.
3. Any credential Codex could not access (flag precisely).

## DELIVERABLE
One report: per task — done/blocked, evidence (IDs, screenshots, URLs),
and the filled-in owner-only list. Keep it under a page.
