# Handover → Codex (Klaviyo UI execution)

**From:** Claude (audit + API prep) · **Date:** 2026-05-30 · **Account:** One Life Health — Klaviyo `S86r7e` (ZAR, Africa/Johannesburg)
**Why you (Codex):** several finishing steps require the Klaviyo **UI** — the MCP API exposes no send/schedule-existing-campaign, no archive/delete, no create-segment, no bulk add-to-list, and won't reveal flow trigger-list bindings. Everything below is scoped, ordered, and guard-railed. Full analysis: `reports/klaviyo-audit-2026-05-30.md`.

---

## 🔒 GLOBAL GUARDRAILS (apply to every task)
1. **Consent only.** Never email a profile without email-marketing consent. All target segments below are consent-gated — keep it that way.
2. **Smart Sending ON** for every campaign (skips anyone emailed in the last ~16h). Never disable.
3. **One canonical brand name: "One Life Health"** (with spaces). Never "Onelife Health" / "OneLife". Domain stays `onelife.co.za`.
4. **Test before send.** Send a preview/test to an internal address and verify render, links, and unsubscribe before any real send.
5. **Never delete Sent campaigns** (reporting integrity). Deletion is limited to the explicit QA/test/scaffold IDs listed.
6. **Changing list membership must not re-trigger flows.** See Task 4 pre-reqs — this is the highest-risk step.
7. **Throttle** any send to a dormant/large segment (≥1k, or >60d unengaged): 25%/hr.
8. **Health-claims compliance (SAHPRA):** evidence-based, structure/function only; no disease cure/treatment claims.
9. **STOP & flag a human** if: any action would email more recipients than stated, bounce rate >2%, spam-complaint >0.1%, or a welcome/sunset flow shows a send spike after Task 4.

---

## KEY IDS

**Segments:** At-risk-60d `UQmNai` (~2,133) · Engaged-90d `S3MAsK` (~802) · VIP/High-LTV `UeXRQX` (98) · VIP 3+orders/R3k `TKAdBQ` · Engaged Browsers `TZ66NM` (27) · GLP-1/Metabolic `QZACej` · Buyer-Magnesium `RCDiHM` · Buyer-Joint `T7CaTr` · Glen Village proximity `RnHTNL` · Parkview proximity `S83cUp`
**Main list:** Email List `Xrk5jD` (~768)
**Re-engagement template:** `Xt4xgS` ("OL — Re-Engagement — We Miss You v2", branded "One Life Health")
**"Added to List" flows (trigger-risk for Task 4):** Welcome Full Sequence `XZNrmz` · PCOS Welcome `RAfNCq` · GLP-1 Education Drip `RtJHQe` · GLP-1 Non-Opener `VdQZxY` · Post-Purchase Edu Magnesium `RTHzQF` · Post-Purchase Edu Vitamin D `Unn2d2` · Sunset Unengaged `YrtdaV`
**Other flows:** Post-Purchase Thank-You + Cross-sell `RpJP55` (converting R0 — Task 5) · Win-Back 60d v2 `TGZYKa` · Replenishment `TNBkZK` · Abandoned Checkout `VAjbpG` · Browse Abandonment `UMMzhC`

---

## TASK 1 — Approve & send the scheduled win-back  ⭐ do first
**Campaign:** `01KSWCT5HA3Q80PY3AXT6RE24J` — "Re-Engagement — We Miss You (At-risk 60d) — SCHEDULED throttled [final]".
Already configured: audience **At-risk-60d** `UQmNai`, sender **"One Life Health"** `info@onelife.co.za`, template `Xt4xgS`, **throttle 25%/hr**, Smart Sending ON, scheduled **2026-06-03 08:00 SAST**. It is still a **Draft** (API can't push "send").
**Do:** open it → verify the above → send a **test to an internal inbox** → check the `{% unsubscribe %}` link + `WELCOMEBACK` free-delivery offer copy → **Review & Send** (keep the 3 Jun schedule + throttle).
**Guardrails:** do NOT swap the audience to a list; do NOT remove unsubscribe; confirm recipient count ≈ 2,133 before confirming.

## TASK 2 — Delete the two scaffold drafts
Delete **only** `01KSWBSGQWJ313VRDNDJZRTJ33` (v1, wrong brand) and `01KSWCK98YF340EVDPJ48Q528H` (v2, unscheduled). Leave the Task-1 final. (No other campaigns.)

## TASK 3 — Lock brand name to "One Life Health"
- **Settings → Account → default sender name** → "One Life Health" (currently "onelifehealth").
- Audit every **sender profile, template, flow email, footer, and image alt-text**; replace any "Onelife Health"/"OneLife" → **"One Life Health"**. Text only — don't alter the logo file, links, or the `onelife.co.za` domain.

## TASK 4 — Rebuild "Email List" to ~2k  ⚠️ HIGHEST RISK — follow order exactly
**Goal:** Email List `Xrk5jD` should contain all consented contacts (~2,900), not 768.
**PRE-REQ (do NOT skip):** adding profiles to a list re-fires "Added to List" flows. Before adding anyone, open each flow in KEY IDS → "Added to List" and check its **trigger list**:
- If it triggers on **Email List `Xrk5jD`**: add a flow **filter** so existing people don't re-enter — Welcome/PCOS/GLP-1/Post-Purchase-Edu: `Placed Order` **zero times over all time** *(or)* `Profile created on/after {today}`; **Sunset `YrtdaV`**: must NOT capture the freshly-added — gate it the same way or pause it during the import.
- If it triggers on a **different signup list**: no action needed for that flow.
**Then:** open segment **At-risk-60d `UQmNai`** → select all → **Manage → Add to list → Email List**. Repeat for **Engaged-90d `S3MAsK`**. (Klaviyo dedupes by profile.)
**After:** re-enable any paused flows; confirm Email List ≈ 2k; check Welcome & Sunset flow analytics show **no send spike** (guardrail #9).
**Ongoing-send guardrail:** because At-risk are unengaged, regular newsletters to the full list now include dormant addresses — keep the **Sunset flow** active and/or exclude `can_receive_email = false`/hard-bounced so deliverability stays clean.

## TASK 5 — Fix Post-Purchase Thank-You + Cross-sell flow (`RpJP55`) — converts R0 at 53% open
Rework the email(s): genuine "how to use what you bought" education → ONE relevant cross-sell with a first-reorder incentive → working product links + "One Life Health" branding. Test, then set live.

## TASK 6 — Schedule the "JJA 2026" content drafts (~12)
They use the consistent blog template and are dated Jun–Aug in their names. For each **Draft** (skip any "Cancelled" clones): audience **Engaged-90d `S3MAsK`** (add **At-risk-60d** only after Task 4), sender "One Life Health", Smart Sending ON → **schedule on the date in its name**. One send per date; do not schedule duplicates.

## TASK 7 — Account hygiene (delete test/QA + cancelled dupes)
- **Delete QA lists:** `RQabjA` `RpV9Fs` `SSzpQ2` `SuNYiq` `UJ63Ag` `UZKNGZ` `UZpyJB` `VFJRzV` `VGjHsn` `WgRE3v` `XQESHG` `XWpM59` `YdWDXY` (all `[CODEX QA]`).
- **Delete campaigns** whose names start with `[CODEX LINK QA]`, `[CODEX INTERNAL TEST]`, and the **Cancelled** duplicate blog drafts (e.g. the repeated "Vitamin D in SA", "Collagen", "Best Kids Vitamins" cancelled clones).
- **KEEP:** all **Sent** campaigns; real lists (Email List `Xrk5jD`, Text Messaging `S44qNc`, PCOS Interest `WFPXyc`, Vivid Health `TeSYf6`); all segments & live flows.

## TASK 8 — Template hygiene & uplift
- Rename "Clone of …" templates to `OL — [Type] — [Topic] — vN`.
- **Remove the preview-text-in-body bug**: templates (e.g. `THV5Z8`) literally print "Preview text: …" as a visible line — delete that line; set preview text only in the campaign's preview field.
- Add **product images** (Klaviyo product blocks) and a **reviews/social-proof** block to the standard campaign template; save reusable pieces as **Universal Content** blocks.

## TASK 9 — Deliverability
Confirm **DKIM/SPF/DMARC** aligned for `onelife.co.za` (Settings → Domains); keep bounce <2%, spam <0.1%; ensure **Sunset `YrtdaV`** is live.

## TASK 10 — (GitHub, not Klaviyo) refresh secret
Root cause of the all-zero dashboard: the GH Actions `KLAVIYO_API_KEY` secret/scopes. Rotate/verify (scopes: Metrics/Campaigns/Flows/Lists/Segments/Profiles Read). Script guard already added in this PR so it won't publish zeros again.

---

## DEFINITION OF DONE
- [ ] Win-back approved & sending throttled to At-risk-60d; scaffold drafts v1/v2 deleted.
- [ ] "One Life Health" everywhere; account sender name updated.
- [ ] Email List ≈ 2k, with **zero** welcome/sunset misfires confirmed.
- [ ] Post-Purchase Thank-You flow reworked & live.
- [ ] JJA drafts scheduled on their dates to Engaged-90d.
- [ ] QA/test lists & campaigns + cancelled dupes removed; Sent campaigns untouched.
- [ ] Templates de-bugged (no preview-text leak), product + review blocks added.
- [ ] SPF/DKIM/DMARC confirmed; Sunset live.
- [ ] `KLAVIYO_API_KEY` secret verified; next daily refresh shows real numbers.
