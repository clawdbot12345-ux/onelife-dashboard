# ONE LIFE HEALTH — CODEX HANDOFF 2026-06-12 (OWNER-TASK INITIATION)

Repo: `clawdbot12345-ux/onelife-dashboard` · branch: `claude/onelife-health-review-lwvi3-c3yry2`
Store: onelife.co.za (Shopify admin: onelifehealth.myshopify.com) · Klaviyo account S86r7e

Mission: initiate every remaining revenue-blocking task that has been waiting
on the owner. You have browser + admin access; do everything below except the
clearly marked OWNER-ONLY steps, and produce the completion report at the end.
Work the tasks IN THIS ORDER — it is sorted by revenue impact.
NOTE (owner decision 2026-06-12): payment gateways (Payflex/PayJustNow/Ozow)
are DEFERRED — do not install or configure any payment provider in this run.

Hard rules (unchanged): never write to the live theme (duplicate → edit →
owner publishes); do NOT touch Klaviyo Welcome Email 1; never send to the
full list (Engaged 90d segment S3MAsK only); free delivery threshold is R400
nationwide; "health consultants" never coaches/pharmacists; 17 protocols;
sign-off Precious. Verify every change after making it; report with evidence.

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

9. **Backfill (the kick-start):** bulk-send review requests for the last
   **90 days of fulfilled orders** — capped at one email per customer,
   spread over 3 days so replies don't spike. This alone should seed the
   first 30–60 reviews within two weeks.

10. **POPIA guard:** reviewers must NOT be auto-subscribed to marketing
    lists — leave any "add reviewers to newsletter" option OFF.

═══════════════════════════════════════════════════════════════════
## TASK 2 — KLAVIYO: verify/finish the Welcome + Post-Purchase wiring  🔴
═══════════════════════════════════════════════════════════════════
Claude's API audit cannot see flow-message template assignments. In the
Klaviyo UI:
1. Open flow XZNrmz (Welcome — Full Sequence). Check email #2 and #3:
   do they render the 2026 design system ("Which stack is yours?" /
   "Thirty years behind the counter")? If not, swap in templates YdyAkd
   (Welcome #2) and Y9SA46 (Welcome #3). Email #1 MUST NOT BE TOUCHED.
2. Open flow RpJP55 (Post-Purchase v3). Check email #2 renders "What pairs
   well with your order"; if not, swap in template RpUzMu.
3. Screenshot each flow's message list as evidence.

═══════════════════════════════════════════════════════════════════
## TASK 3 — SWITCH ON THE EMAIL CADENCE AUTOMATION  🔴
═══════════════════════════════════════════════════════════════════
The repo now has two scheduled campaign generators (see
email-cadence-system-2026.md):
1. GitHub repo → Settings → Secrets and variables → Actions:
   - Confirm secret `KLAVIYO_API_KEY` exists (used by daily-refresh).
   - Add secrets `SHOPIFY_CLIENT_ID` and `SHOPIFY_CLIENT_SECRET` (the same
     credentials you used for Shopify API work; if you don't hold them,
     flag for owner).
   - Add repository **variable** `EMAIL_AUTOMATION_ENABLED` = `true`.
2. Actions tab → run "Tuesday Education Email" manually → verify a campaign
   appears in Klaviyo named "[AUTO] Tuesday Digest — …", scheduled, audience
   = segment S3MAsK only. Same for "Friday Product Email".
3. Do NOT cancel the scheduled sends — they are the system working. Report
   both campaign IDs and their scheduled times.

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
3. In Klaviyo, archive the orphaned pre-2026 templates that are no longer
   attached to any flow or campaign (list them first; do not delete).

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
