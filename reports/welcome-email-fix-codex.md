# Welcome email fix — Codex handoff

**Date:** 2026-06-19
**Branch / PR:** `claude/chat-regression-fix-c10vkk` → PR #21
**Status:** ready to apply (Codex has the live Klaviyo access; this session does not)

## Why this exists

The **live Welcome email** (Klaviyo flow `XZNrmz`, "Welcome — One Life Health
(Full Sequence)", Email 1) footer still advertises the **old** free-delivery
threshold — "Free delivery over R900 (Gauteng) | R1,400 (nationwide)". The real,
current promise, used on the site and in every other Onelife email/script, is
**"Free delivery over R400 nationwide | Collect free in store"**. So the single
email every new subscriber receives contradicts the store on its core promise.

The repo itself is already clean — every generator script and the brand-voice
memory say "R400". The wrong copy lives **only** in the live Klaviyo template.
A previous session (`claude/seo-audit-findings-2vnstq`) was about to fix it when
the Klaviyo connection dropped; this session has no Klaviyo connection or valid
API key, so it's handed to Codex.

## Mechanical helper (part 1 only)

`scripts/fix_welcome_email.py` (this branch) walks the Welcome flow's email
templates and applies tightly-bounded substitutions for the free-delivery line.
With `KLAVIYO_API_KEY` set:

```
python scripts/fix_welcome_email.py            # dump live templates + show diff
python scripts/fix_welcome_email.py --apply     # PATCH the free-delivery copy
```

It only touches the delivery-threshold line (product names / unrelated "R900"
amounts can't match) and is idempotent. The green/sign-off (part 2) is a manual
editor change.

## Codex prompt

```
Fix the LIVE Welcome email in Klaviyo. Do not touch any other flow.

TARGET
- Flow: "Welcome — One Life Health (Full Sequence)", flow id XZNrmz
- Email 1 (the high-converting first email, ~54% open). The bad copy is in its
  footer. Check Emails 2 & 3 in the same flow too and fix them if they carry the
  same footer.

THE FIX (two parts)

1) Free-delivery copy — the factual error (priority)
   The footer currently advertises the OLD threshold, e.g.:
     "Free delivery over R900 (Gauteng) | R1,400 (nationwide)"
   The real, current promise — used on the site and in every other Onelife
   email/script — is:
     "Free delivery over R400 nationwide | Collect free in store"
   Replace ONLY the delivery-threshold line. Do not change product names, prices,
   or any unrelated "R900"/"R1,400" amount. Update BOTH the HTML body and the
   plain-text version of the template.

2) Old green + sign-off
   Email 1 still uses an old brand green and an old sign-off. Bring them to the
   current brand standard used in the recent templates:
     - Header/CTA/heading green: #1B5E20 (per brand_voice.md). NOTE: the live site
       uses #1b4332 and there's a known inconsistency between the two — if you can
       confirm which the brand now wants, use that; otherwise match #1B5E20 to be
       consistent with the other live emails and FLAG the #1B5E20-vs-#1b4332
       question for the owner rather than guessing.
     - Sign-off: match the current template sign-off; keep it on-brand
       ("the Onelife team" / store list), no old company name variants.

LEAVE ALONE
- The discount code (WELCOME10 / FIRST10) — it's correct, don't change it.
- The flow trigger, timing, throttle, and schedule.

VERIFY BEFORE FINISHING
- Send a test of Email 1 to an internal inbox and confirm: footer reads
  "Free delivery over R400 nationwide", brand green is consistent, sign-off is
  correct, and the unsubscribe link still works.
- Report exactly which template id(s) you edited and paste the new footer line.

MECHANICAL HELPER (optional)
There's a script that does part 1 programmatically: scripts/fix_welcome_email.py
on branch claude/chat-regression-fix-c10vkk (PR #21). With KLAVIYO_API_KEY set,
run it with no args to dump the live templates + diff, then with --apply to PATCH
the free-delivery copy. The green/sign-off (part 2) is a manual editor change.
```

## Reference

- Canonical footer (brand_voice.md / all generator scripts):
  `Onelife Health stores: Centurion | Glen Village, Faerie Glen | Edenvale`
  `Free delivery over R400 nationwide | Collect free in store`
- Welcome flow id: `XZNrmz` · discount code in flow: WELCOME10/FIRST10 (correct — leave)
