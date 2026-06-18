# Klaviyo Program Audit — End-to-End — 2026-06-18

**Trigger:** A customer received a browse-abandonment "Still thinking about {{ product }}? 👀" email
minutes after searching, felt surveilled, and unsubscribed publicly. Owner wants assurance the
WHOLE program is consistent, classy, catchy, and won't over-mail or creep people out again.

**Scope:** All 25 live flows (definitions + 90-day performance), 90-day email campaigns,
lists/segments/consent, and 5 representative templates. Read-only. Conversion metric = Placed Order (WZAxyj).

---

## 1. Executive scorecard — "world-class" rating

| Pillar | Grade | One-line verdict |
|---|---|---|
| **Cadence & over-mail control** | 🔴 **D+** | Triple-stacked cart flows + duplicate win-backs can hit one person 5x/event; no account-level frequency cap; campaign clustering (5 sends/13 days to Engaged). |
| **Deliverability / annoyance** | 🔴 **D** | Unsub rates **1–2%** across recent campaigns AND key flows (Browse 2.1%, PCOS PP 1.6%, Cross-sell 1.6%) — 5–7x the <0.3% bar. Spam appearing (PCOS 0.16%). |
| **Templates & design** | 🟠 **C+** | Split program: new "2026 design system" templates are genuinely world-class; older "Flow Hero 20260531" templates carry **wrong delivery thresholds, off-brand code, old green, and the creepy headline**. |
| **Segmentation** | 🟢 **B+** | Excellent segment library (Engaged 90d, VIP, At-risk, buyer/geo/GLP-1); most campaigns now go to Engaged. Proven: Menopause→Engaged = 44% open, R5.6/recipient. |
| **Consent hygiene** | 🟠 **C** | Email List moved to **single opt-in**; sunset flow exists but is mistimed (US/Eastern), barely fires, and doesn't suppress. Complaint's "I never opted in" angle is plausible. |

**Bottom line:** The *building blocks* of a world-class program now exist (great Welcome economics, rich
segments, a beautiful 2026 template family, SMS consent-gating + quiet hours). But the program is **half-migrated**:
old assets contradict new ones, and there are **zero global guardrails** to stop over-mailing. The complaint
was a symptom, not a one-off.

---

## 2. The complaint — status: PARTIALLY fixed (one live bug remains)

Browse Abandonment v2 (`UMMzhC`) flow definition now shows the intended fixes are **LIVE**:
- ✅ Delay **2h → 24h** (profile timezone).
- ✅ Frequency cap: "not in this flow in last 30 days" (`$flow=UMMzhC` count=0 in 30d).
- ✅ Subject softened to **"Need a hand choosing?"** + preview "A gentle note from Precious".
- ✅ Still suppresses buyers/checkout-starters; smart sending ON.

🔴 **BUT the email body template (`TJiVpH`) still renders the creepy headline:**
`<h1>Still thinking about {{ event.Name }}?</h1>`. The subject was changed; the **on-open headline the
customer actually reads was not**. This must be rewritten to match the softened, consultant voice
(e.g. "A little help choosing, if it's useful"). Template also uses the **old green #1B5E20**, no "— Precious"
sign-off, and a `via.placeholder.com` image fallback that can render as a broken/grey box.

---

## 3. Cadence map (all live flows)

Delays are cumulative from trigger. SS = Smart Sending. "Cap" = in-flow/cross-flow frequency control.

| Flow (ID) | Trigger | Touches & timing | SS | Cap / targeting | Flags |
|---|---|---|---|---|---|
| **Welcome Full Seq** (XZNrmz) | Added to Email List | E@0h, E@3d, E@7d | ✅ | none; no "not a buyer" filter | ⭐ R60.9/recip, R16k. But template bugs (§5). |
| **Browse Abandon v2** (UMMzhC) | Viewed Product | E@24h | ✅ | 30d in-flow cap ✅; buyer/checkout suppressed | Body headline still creepy; 2.1% unsub. |
| **Abandoned Checkout – Std** (VAjbpG) | Checkout Started | SMS *or* E@4h → E@24h | ❌ | 7d re-entry + not-in-flow-7d (self only) | Overlaps WY4cae+VSECqx (same trigger). SS OFF. |
| **Cart Consultant 2026** (WY4cae) | Checkout Started | E@2d | ❌ | none vs other cart flows | **Duplicate trigger** w/ VAjbpG. New, R0 yet. |
| **Cart Consultant SMS** (VSECqx) | Checkout Started | SMS@2d | ❌ | SMS-consent gated ✅; quiet hours ✅; 7d re-entry | **3rd flow on same trigger**; 2nd SMS for same cart. |
| **Post-Purchase Cross-sell v3** (RpJP55) | Placed Order | E@3d, E@7d | ✅ | "not bought since" on email 2 only | 🔴 R0 from 386; 1.6% unsub. |
| **Replenishment** (TNBkZK) | Placed Order | E@21d, E@35d, E@65d | ✅ | none ("bought since" not checked) | Can mail people who already reordered. |
| **Review Request 2026** (YAQPN9) | Fulfilled Order | E@14d | ✅ | 90d re-entry cap ✅ | Clean. Good. |
| **Win-Back 60 v2** (TGZYKa) | Placed Order (inactive) | (60d cohort) | ✅ | — | **Duplicate win-back** vs SFMncG. |
| **Win-Back 90/120 2026** (SFMncG) | Placed Order | E@90d, E@120d | ✅ | none vs TGZYKa/Sunset | Overlaps 60-day win-back + Sunset window. |
| **Sunset Unengaged** (YrtdaV) | Unengaged segment | E@1d, E@8d, E@13d | ✅ | sets "Unengaged"=true only | 🔴 **US/Eastern** delays; no suppression action; ~2 recips. |
| **Back in Stock 2026** (WT9YvU) | Back in Stock | E@0h | ✅ | none (user-requested, OK) | Fine. Has SMS companion (XvPZee). |
| **PCOS Post-Purchase** (R96wJV) | Placed Order (PCOS) | E + 2 follow-ups | ✅ | — | 🔴 1.6% unsub, 0.16% spam. |
| PCOS Welcome (RAfNCq) | Added to PCOS list | low vol | — | — | 2 recips/90d. |
| GLP-1 Education Drip (RtJHQe) | Added to list | drip | — | — | 24 recips, 0 rev. |
| GLP-1 Non-Opener (VdQZxY) | Added to list | follow-up | — | — | 72 recips, 0 rev. |
| PP Education Magnesium/Vit D (RTHzQF/Unn2d2) | Added to list | edu | ✅ | — | ~1–4 recips — near-dead. |
| Loyalty: Points Nudge (VTh9RU), Birthday (VshsNQ), VIP Tier (T4RwQf), Points/Reward Expiring (XzPBKf/RxvUsE) | Metric | single nudges | mixed | — | Low volume; Points Nudge 45% open but R2/recip. |

### Over-mailing clusters (the structural risk)
1. **Checkout-Started cluster (3 flows, 1 trigger):** VAjbpG + WY4cae + VSECqx all fire off the same
   "Checkout Started" event with **no mutual exclusion**. A SMS-consented abandoner can receive, for ONE cart:
   SMS@4h + Email@4h (VAjbpG) → Email@24h (VAjbpG #2) → Email@2d (WY4cae) → SMS@2d (VSECqx) =
   **up to 5 touches across 3 flows**. This is exactly how "creepy / too much" complaints are born.
2. **Placed-Order cluster:** A single purchase can enter Cross-sell + Replenishment + Review + Win-Back +
   PCOS-PP simultaneously. Individually paced, but with no account cap a buyer could get a steady drip
   for months with no ceiling.
3. **Duplicate win-backs:** Win-Back 60 (TGZYKa) and Win-Back 90/120 (SFMncG) both run off purchase
   inactivity — consolidate to one 60/90/120 ladder.

---

## 4. Performance (last 90 days, Placed Order conversion)

### Stars — protect
| Flow | Recip | Open | Click | Conv | Rev/recip | Revenue |
|---|---|---|---|---|---|---|
| **Welcome Full Seq** (XZNrmz) | 264 | 48.9% | 9.2% | 6.9% | **R60.9** | **R15,955** |
| Abandoned Checkout Std (VAjbpG) | 407 | 39.7% | 4.5% | 1.8% | R13.4 | R5,359 |
| Browse Abandon v2 (UMMzhC) | 381 | 28.9% | 8.0% | 2.4% | R19.1 | R7,127 |

Welcome alone = ~70% of total flow revenue. The audience converts when the email earns it — the
constraint is list growth (prior audit: ~174–264 enter/90d), not the asset.

### 🔴 Annoyance / deliverability flags (unsub > 0.3% or spam > 0.1%)
| Flow / send | Unsub | Spam | Note |
|---|---|---|---|
| Browse Abandonment v2 | **2.14%** | 0 | Volume + creepy headline → high opt-out. |
| PCOS Post-Purchase (agg) | **1.58%** | **0.16%** | Spam in danger zone; message 1 (U6Vf9g) 1.66% unsub + spam. |
| Post-Purchase Cross-sell v3 | **1.58%** | 0 | **And R0 revenue** — pure annoyance, no upside. |
| Replenishment email 2 | 0.90% | 0 | — |

### 🔴 Dead / near-dead (0 revenue or <5 recipients — review or pause)
Cross-sell v3 (R0/386), GLP-1 Drip (R0/24), GLP-1 Non-Opener (R0/72), PP Education Magnesium (4),
PP Education Vit D (1), PCOS Welcome (2), Birthday (6), Cart Consultant 2026 (11 — too new to judge).

### Campaigns — list fatigue is real and NOT improving
~22 real sends/90d. Wins: shift to **Engaged 90d** is happening, and segmented sends perform
(Menopause→Engaged 44% open / R5.6 rev/recip; PCOS→Engaged 40.8% open).
**But unsub rates on recent campaigns are 1–2%:**
- Jun 5 Friday Spotlight (Engaged) — **1.98% unsub**
- Jun 13 winter-sleep (Engaged) — 1.33% · Jun 16 winter-vitamin (Engaged) — 1.40%
- Jun 3 Adaptogens (full list, 3,065) — 1.00% · Jun 10 round-up — 0.93%
- **Clustering:** Jun 5, 10, 13, 16, 17 = 5 sends in 13 days to the same Engaged segment (Jun 13+16+17
  within 4 days). Even "engaged" people churn at this frequency.
- Revenue/recipient on most campaigns is **R0–R1.6** — still a content newsletter, not a revenue channel.

**Reporting hygiene:** ~20+ `[CODEX TEST]` / `[LINK QA]` campaigns still pollute reports (prior audit
said archive — not done), plus dozens of **Cancelled** "Apothecary Guide Drip / Monthly Digest / JJA"
duplicates created/cancelled *today* (2026-06-18) — a scheduling script is thrashing and should be fixed.

---

## 5. Template design audit (5 inspected)

Two clearly different generations are live simultaneously — this is the core "not consistent / not classy" issue.

**🟢 World-class — the "2026 design system" family** (Cart Consultant `UyBg38`, Review Request `WbpTF3`):
correct brand green **#1b4332** + dark footer #14291e, **serif Georgia display H1**, accent rule,
"Hi {{first_name}} — Precious here…", **"— Precious / One Life Health Consultant · Centurion"** sign-off,
correct **"Free delivery over R400 nationwide"**, WhatsApp basket-check CTA, `{% unsubscribe %}`,
"Family-owned since 1996". This is the standard to roll everywhere.

**🔴 Off-brand & buggy — the older "Flow Hero Refresh 20260531" family:**
| Template | Bugs (all LIVE) |
|---|---|
| **Welcome Email 1** (`UfSdB9`) ⭐ top asset | Footer **"Free delivery over R900 (Gauteng) / R1,400 (nationwide)"** — WRONG (R400); code **WELCOME10** (off-list; the flow's own email 3 uses FIRST10); green **#1B5E20**; no "— Precious"; `{{ unsubscribe }}` tag; generic "we" voice. |
| **Browse Abandonment** (`TJiVpH`) | Headline **"Still thinking about {{ event.Name }}?"** (the complaint line); green #1B5E20; no Precious; placeholder-image fallback. |
| **Replenishment #1** (`VHbPFG`) | "Spend over **R600** for free nationwide delivery" — WRONG (R400); greens #1B5E20/#2e7d32; no Precious sign-off; "based on your last order" but no real product memory. |

**Consequence:** **three different delivery thresholds (R400 ✅, R600, R900/R1400), two greens, and an
off-list code are live at once.** The Welcome flow — the single most valuable, most-seen automation —
contradicts the website's core R400 promise on every send. (Prior audit reported these R900/R1400 fixes
shipped; they regressed or this template was missed.)

---

## 6. Consent & list hygiene

- **Lists:** Email List `Xrk5jD` = **single opt-in** (changed since last audit); Text Messaging `S44qNc` =
  double opt-in; Vivid Health single; PCOS Interest single; Preview double.
- **The complaint's "I never opted in" angle is credible.** Single opt-in + browse abandonment firing on a
  *Viewed Product* (no purchase intent) means someone who merely browsed and got onto the list somehow
  receives behavioral marketing. POPIA expects clear, demonstrable consent for marketing.
- **Sunset is broken as a safety net:** delays run on **US/Eastern** (brand is Africa/Johannesburg),
  only ~2–6 recipients in 90d, and the final step just sets `Unengaged=true` — **it never removes/suppresses
  from marketing.** So unengaged profiles keep getting campaigns → the 1–2% campaign unsub rate.
- **SMS:** consent-gating and quiet hours are correctly set on all SMS steps (VAjbpG, VSECqx) — good. But
  two flows can still SMS the same cart.

---

## 7. Prioritized fix list

### P0 — stop the bleeding (this week)
1. **Rewrite Browse Abandonment body** (`TJiVpH`): kill the "Still thinking about…" headline; rebuild on the
   2026 design system (green #1b4332, Precious sign-off, remove placeholder-image fallback). The flow is fixed;
   the email isn't.
2. **De-conflict the 3 cart flows.** Pick ONE recovery ladder. Recommended: retire/disable VAjbpG (old, SS off),
   keep WY4cae (email) + VSECqx (SMS) as the 2026 ladder, and add cross-flow exclusion ("not in the other cart
   flow in 7 days") + a single SMS so no cart triggers 2 texts.
3. **Fix Welcome Email 1** (`UfSdB9`): R900/R1400 → **R400 nationwide**; WELCOME10 → **FIRST10** (or formally
   add WELCOME10 to the approved list); green → #1b4332; add "— Precious"; `{{unsubscribe}}` → `{% unsubscribe %}`.
4. **Fix Replenishment #1** (`VHbPFG`): R600 → **R400**; align green + add Precious sign-off.
5. **Pause or rebuild Post-Purchase Cross-sell v3** — R0 from 386 at 1.6% unsub is pure annoyance.
6. **Fix the Sunset flow:** switch delays to Africa/Johannesburg, and add a real suppression/unsubscribe action
   at the end (or move unengaged out of all campaign segments). Then enforce it.
7. **Archive the ~20 [CODEX TEST]/[LINK QA] campaigns** and fix the scheduler creating/cancelling dozens of
   duplicate "Guide Drip/Digest" campaigns daily.

### P1 — guardrails & consolidation (2–3 weeks)
8. Implement the **Global annoyance guardrails** (§8).
9. **Merge duplicate win-backs** (TGZYKa + SFMncG) into one 60/90/120 ladder with a single Sunset hand-off.
10. **Add "has not purchased since flow start"** to every Replenishment step so reorderers stop receiving it.
11. **Cap campaign cadence:** max ~2 marketing campaigns/week to Engaged; max 2 full-list/month. Space the
    current 5-in-13-days clustering.
12. **Brand-term sweep:** subject "…What Our **Pharmacists** Actually Recommend" violates voice rules
    (must be "consultants"). Grep all live subjects/templates for "pharmacist", "coach", and the wrong R-values.

### P2 — finish world-class (3–4 weeks)
13. **Migrate ALL flow templates onto the 2026 design system**; retire the "Flow Hero 20260531" family so there
    is one template lineage, one green, one footer, one R400 line.
14. Add **dynamic product blocks** to Cross-sell + Replenishment (real "pairs with / reorder what you bought").
15. **Consent decision:** keep single opt-in only with strict sunset enforcement (above) + suppression, OR add a
    confirmed-opt-in step for behavioral (browse) marketing. Require **engaged-in-90d** on Browse Abandonment.
16. Revive list-growth engine (signup forms — still the #1 ceiling on the Welcome flow's revenue).

---

## 8. Global annoyance guardrails (so this can't recur)

These are account/structural controls, mostly absent today:

1. **Account-level frequency cap** (Klaviyo Settings → set a max): **≤ 3–4 marketing emails / 7 days per profile**,
   applied to flows + campaigns. Single biggest protection against the over-mail clusters in §3.
2. **Global Smart Sending ON** for all marketing (currently OFF on the cart flows) — prevents same-profile
   double-sends within ~16h.
3. **Cross-flow exclusion on shared triggers:** any two flows on the same metric (Checkout Started, Placed Order)
   must carry "not in [sibling flow] in last N days" filters. No two flows should be able to fire for one event.
4. **Engaged-only defaults:** behavioral/promo flows + all campaigns default to **Engaged 90d** (`S3MAsK`);
   full list reserved for ≤2 announcements/month. Browse Abandonment specifically should require engaged-90d.
5. **Browse/abandon caps:** Browse = 30-day in-flow cap (done) + 24h delay (done); cart ladder = one consolidated
   sequence with its own cap.
6. **SMS guardrails (already partly in place — keep):** consent-gated, quiet hours ON, one text per cart, and add
   an SMS-specific weekly cap.
7. **Enforced sunset + suppression:** working sunset (SAST timezone) that actually removes unengaged profiles
   from sending — this is what keeps campaign unsub/spam down long-term.
8. **One template system, one set of brand facts** (R400, #1b4332, approved codes, "— Precious", "consultants")
   so no send can contradict the website again.

---

## Appendix — IDs
Stars: Welcome `XZNrmz`. Cart cluster: `VAjbpG` (retire) / `WY4cae` / `VSECqx`. Browse `UMMzhC` (body tmpl `TJiVpH`).
Cross-sell `RpJP55` (pause). Replenishment `TNBkZK` (tmpl `VHbPFG`). Sunset `YrtdaV`. Win-backs `TGZYKa`+`SFMncG`.
Welcome tmpl `UfSdB9`. Gold-standard tmpls: `UyBg38`, `WbpTF3`. Engaged segment `S3MAsK`. Email List `Xrk5jD` (single opt-in).
