# Codex Handoff — Vivid Health Store (hgywg0-w7.myshopify.com) · v2, 2026-07-02

**⚠️ Supersedes the earlier version of this file.** History: Claude briefly applied
Vivid fixes to the One Life store by mistake; **everything on
onelifehealth.myshopify.com was fully rolled back the same hour** (60/60 restore
ops verified live). Since then ALL work targets the dedicated Vivid store
**hgywg0-w7.myshopify.com** via `VIVID_CLIENT_ID`/`VIVID_CLIENT_SECRET`.
**Do not touch the One Life store for anything Vivid-related.**

**State as of this handoff (all on PR #26, branch `claude/vivid-health-audit-redesign-9fmzon`):**
- Full audit + world-class blueprint + brand research + hi-fi mockup (docs in repo root and `reports/`)
- Vivid store: "Best in Class" theme **published** (fixed Journal 404s, empty
  sourcing page, missing 404 template; Subscribe & Save buy box + 5-image
  galleries + new quiz now live) · catalog fixed (Agnus Castus typo, 12
  size-qualified duplicate titles)
- Autonomous **Vivid Journal blog engine** built: weekly publisher + monthly
  Claude article writer + 3 validated launch articles in `content/vivid-queue/`
- Remote-hands pipeline: `scripts/vivid_ops.py` + `.github/workflows/vivid-ops.yml`
  (pull / apply / publish modes, per-store credential isolation)

Claude continues to own all THEME/CODE work through that pipeline (robots.txt fix,
back-in-stock form on OOS PDPs, search template restyle, announcement bar, cart
drawer thumbnails, quiz polish). This document is ONLY what Codex should do.

---

## 1. Merge PR #26 🔴 (unblocks the schedules)

Review + merge https://github.com/clawdbot12345-ux/onelife-dashboard/pull/26.
Scheduled workflows (weekly Journal publish, monthly article writer) only run
from the default branch, so nothing automates until this merges. The PR also
contains the One Life rollback record — merging changes nothing on either store.

## 2. Flip the blog engine on (2 min)

1. Repo **Settings → Secrets and variables → Actions → Variables**: add
   `VIVID_BLOG_ENABLED = true`.
2. Optional immediate test: **Actions → "Vivid Journal Publish" → Run
   workflow** — it pops the oldest of the 3 queued articles, publishes it to
   the store's Journal, and archives it. Verify the article renders at
   `https://hgywg0-w7.myshopify.com/blogs/journal`.
3. Editorial: skim the 3 queued articles in `content/vivid-queue/` — merging
   the PR is sign-off for these; future months arrive as PRs from the
   "Monthly Vivid Article Writer" workflow for review.

## 3. Vivid store admin (needs the Shopify admin UI)

| # | Task | Why |
|---|---|---|
| 3.1 🔴 | **Inventory decision: 16 of 58 products are sold out (28%)**, incl. hero SKU Buffered C · 300. Restock or temporarily hide — a launch catalog can't be a third unavailable | Biggest conversion blocker found in the visual audit |
| 3.2 🔴 | **Payments**: confirm the gateway lineup (site shows text pills VISA/MASTERCARD/PAYFAST/EFT). Install **Payflex** and/or **PayJustNow** + **Ozow**. Claude will then add PDP installment messaging ("4 × R107") via theme code | SA BNPL = up to +30% AOV at these price points |
| 3.3 🔴 | **Reviews app**: install **Judge.me** ($15/mo) on the Vivid store; enable post-purchase request emails from day one | Zero reviews anywhere; homepage already claims customer favourites |
| 3.4 | **Klaviyo for Vivid**: the site promises a WELCOME 10% signup — connect a Klaviyo account (or confirm which ESP) so the popup/email capture actually feeds something. Add its private key as repo secret `VIVID_KLAVIYO_API_KEY` and Claude wires the publisher's campaign step like One Life's | Email capture currently goes nowhere useful |
| 3.5 | **Pixels before launch**: GA4 + Meta + TikTok channel apps on the Vivid store | Don't repeat One Life's un-measured-ads history |
| 3.6 | **Price ownership**: odd-cent prices (R189.76, R301.88, R1,251.20) look like sync/conversion artifacts. Confirm whether a POS/ERP owns Vivid store prices; if not, approve rounding to R5/R10 and Claude applies it via API | Blueprint §3 pricing hygiene |
| 3.7 | **Domain decision**: vividhealth.co.za is owned by an unrelated practitioner (brand-risk adjacency — see audit §5). Buy it, or register an alternative (vivid.co.za / getvivid.co.za / vividhealth.shop), connect it to the store | Blocks launch + SEO |
| 3.8 | **Label artwork fixes for the next render/print run**: (a) the Agnus Castus bottle art still reads "ANGUS CASTUS" (title is fixed; art isn't); (b) labels say "DIETARY SUPPLEMENT" — US wording; SA regulatory tone is complementary medicine/health supplement | Print-level credibility |
| 3.9 | **Shipping check**: cart shows estimated R100 shipping and a R400 free-shipping bar — confirm rates in Settings → Shipping match the promise | Trust: the No.1 One Life audit finding was a shipping contradiction; don't import it |

## 3b. Design to 10/10 — imagery regeneration 🔴

Owner directive: everything design-side must reach 10/10. Full art direction,
shot lists, prompt templates, label-art corrections and the per-page QA gate
are in **`codex-vivid-design-direction.md`** — regenerate imagery to that spec
(start with the label-panel macros and the 3 image-less bundle products).

## 4. Batch-certificate programme (flagship feature — owner + manufacturer)

Request per-batch COAs (identity, potency, heavy metals, micro) from the
contract manufacturer. The moment one PDF exists, hand it over — Claude builds
the batch-lookup page (the store's PDP FAQ already promises independent batch
testing, so the paper trail needs to exist).

## 5. Explicitly NOT for Codex (Claude owns, in flight)

robots.txt serving empty · back-in-stock form not rendering on OOS PDPs ·
default search template restyle · empty announcement bar · cart drawer blank
thumbnails · quiz logic polish · PDP installment line (after 3.2) ·
Klaviyo wiring in the publisher (after 3.4).

## Definition of done for this round

- [ ] PR #26 merged
- [ ] `VIVID_BLOG_ENABLED=true` set; first Journal article published and rendering
- [ ] OOS decision executed (restock list or hide)
- [ ] Payflex/PayJustNow + Ozow live at checkout
- [ ] Judge.me installed, post-purchase requests on
- [ ] Klaviyo connected + `VIVID_KLAVIYO_API_KEY` secret added
- [ ] GA4/Meta/TikTok pixels installed
- [ ] Price-ownership answer + rounding approval (or veto) recorded on the PR
- [ ] Domain chosen/connected
- [ ] COA request sent to manufacturer
