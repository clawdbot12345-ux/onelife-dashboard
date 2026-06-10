# CODEX HANDOFF — Email Imagery + Klaviyo Wiring + Photo Pipeline
**From:** Claude session 2026-06-10
**Repo:** `clawdbot12345-ux/onelife-dashboard`, branch `claude/onelife-health-review-lwvi3-c3yry2`
**Context files on that branch:** `reports/klaviyo-audit-2026-06-10.md` (the full audit) and `reports/klaviyo-wiring-guide-2026-06-10.md` (wiring steps + template-ID table)

## Mission
Claude rebuilt the Klaviyo program today: full audit, 7 new templates in the 2026
design system (correct brand facts, Engaged-90d targeting, new flow plan). What
Claude cannot do — and you can — is **generate the cinematic imagery** and do the
**Klaviyo UI flow wiring**. That's this brief.

## HARD BRAND RULES (any violation is a bug)
- Delivery: "Free delivery over R400 nationwide" (NEVER R900/R1,400)
- Team: "health consultants" (NEVER coaches/pharmacists)
- 17 consultant-signed protocols (never 15)
- Real codes only: FIRST10, DISPENSARY10, STACK5, STACK10
- Voice: Precious, honest apothecary, no hype
- DO NOT touch Welcome flow Email 1 (R97/recipient — it is sacred)
- NEVER send to the full Email List; campaigns target segment "Engaged 90d" (S3MAsK)

## Part A — Cinematic hero images INTO the 7 new templates

### Global art direction (same standard as the site set you built)
**Quality:** Cinematic studio — Thorne Research meets Tom Ford advertising. Shot on
Hasselblad/Phase One, shallow depth of field, dramatic but warm lighting, magazine
editorial quality. Photorealistic, zero AI artifacts.
**Hard rules:** NO text, logos, or typography in any image. Supplement bottles use
blank/unbranded labels (dark green glass with gold caps, amber glass, sleek white
jars). South African botanical props (moringa, rooibos, buchu, protea, turmeric).
Materials: slate, marble, walnut, linen. Palette: dark forest greens, warm golds,
charcoal, cream.
**Email-specific:** 1200×600px landscape. Centre-weighted composition (email heroes
are viewed at ~600px wide on mobile — the subject must read at small size; no
critical detail in outer 15% each side). Keep the top edge calm — the hero sits
directly under a dark green header band.

### The 7 heroes

**A1 — Welcome #2 "Which stack is yours?" (template YdyAkd)**
Overhead flat-lay on warm sage linen: four small product groupings arranged like a
menu — (sleep) amber bottle + dried lavender, (immunity) green bottle + sliced
citrus + ginger, (gut) white jar + kefir glass, (energy) amber bottle + coffee
beans + cacao. A woman's hands mid-arrangement entering frame from below. Bright,
optimistic morning light. Mood: "curated for me."

**A2 — Welcome #3 "Trust" (template Y9SA46)**
Eye-level cinematic across an apothecary counter: a warm consultant's hands passing
a single dark-green bottle to a customer's hands, walnut counter, blurred wooden
shelving with bottles behind, warm tungsten + soft daylight mix, f/1.8. Faces soft
or out of frame — the handover IS the story. Mood: thirty years of quiet expertise.

**A3 — Post-Purchase #2 "Pairs well" (template RpUzMu)**
Still life, 45°: two complementary bottles side by side on warm walnut — one dark
green with gold cap, one amber — almost touching, soft single shadow, a sprig of
rosemary bridging them. Golden-hour side light. Mood: things that belong together.

**A4 — Winback 90d "Your shelf misses you" (template YatQ6s)**
A nearly-empty amber supplement bottle on a sunlit windowsill, a few capsules left
visible through the glass, sheer linen curtain catching late-afternoon golden
light, soft bokeh garden beyond. Nostalgic, warm, gentle — NOT sad. Mood: it's
been a while.

**A5 — Winback 120d "Should we stop?" (template XkbgCw)**
Minimal and calm: one dark-green bottle alone on a clean oak floating shelf against
a warm cream wall, perfectly centred, soft diffuse daylight, generous breathing
room all around. Quietly dignified, zero pressure. Mood: the door stays open.

**A6 — Back in Stock "It's back" (template V8B7p5)**
A hand placing a dark-green gold-capped bottle front-and-centre on an apothecary
shelf between other bottles, slight motion energy, shallow focus on the placed
bottle, warm shop lighting with shelf glow. Mood: just landed, won't sit long.

**A7 — Abandoned Cart #3 "Second opinion" (template TtqJqR)**
Lifestyle over-shoulder: a phone held in a hand showing a blurred-out chat screen
(NO readable text/UI), beside it on the kitchen counter a small open kraft basket
with three unbranded supplement bottles, morning kitchen light, marble surface.
Mood: just ask us first.

### Insertion
Upload each via Klaviyo image upload, then update each template's HTML: insert one
hero <tr> directly below the 4px accent-bar row —
`<tr><td><img src="..." width="620" alt="<one-line scene description>" style="display:block;width:100%;height:auto;"/></td></tr>`
Keep ALL copy, facts, links and the {% unsubscribe %} tag exactly as-is.

## Part B — Klaviyo wiring (15-min plan, fully specified)
**Where the referenced file lives:** GitHub repo `clawdbot12345-ux/onelife-dashboard`,
branch `claude/onelife-health-review-lwvi3-c3yry2`, path
`reports/klaviyo-wiring-guide-2026-06-10.md` (NOT yet on main — check out that
branch or `git fetch origin claude/onelife-health-review-lwvi3-c3yry2` first).
The owner may also paste the guide alongside this brief. Everything you need is
ALSO summarised in the steps below — the guide adds template-ID tables and the
security note, so read it if you have repo access, but these steps are complete:
1. Welcome flow XZNrmz: Email 2 → YdyAkd, Email 3 → Y9SA46. First verify in
   Shopify which discount actually exists (WELCOME10 vs FIRST10) and align the
   template code box + flow coupon to reality.
2. Post-Purchase RpJP55: Email 2 → RpUzMu.
3. NEW Winback flow: Placed Order trigger → 60d delay + no-order check →
   existing "Winback 60d" template → +30d → YatQ6s → +30d → XkbgCw. Smart
   Sending on. Live.
4. NEW Back in Stock flow: trigger metric "Subscribed to Back in Stock" →
   immediate email V8B7p5. Live. (Site form + metric already wired.)
5. Abandoned Checkout VAjbpG: add Email 3 (TtqJqR) after 24h; create parallel
   Added-to-Cart abandonment flow (4h delay, filters: no Checkout Started, no
   Placed Order since start) reusing Email 1's template; add the SMS step the
   flow name promises or rename the flow.
6. Archive every campaign named [CODEX INTERNAL TEST]/[CODEX LINK QA]/
   [CODEX GPT IMAGE TEST] (~20) — they pollute reporting.

## Part C — Article hero images (carried-over audit item)
~20 older articles still use screenshots ("Capture.png") or generic Unsplash as
featured images. Generate branded blog-series heroes (style: site's blog-XX
series), upload via Shopify Files, set as featured images. List the 20 by
checking articles whose featured image filename contains "Capture", "unsplash",
or is missing.

## Part D — Product photography pilot (top 50 sellers)
The site now uniforms product images via CSS multiply-blend; true premium needs
clean sources. Pilot: top 50 best-sellers (FROM sales SHOW orders GROUP BY
product_title LIMIT 50), run background removal/cleanup, re-upload as primary
product images at 1200×1200 on pure white. Before/after contact sheet for owner
review BEFORE overwriting — stage as additional images first.

## Report back
Per part: done/blocked, IDs/URLs touched, screenshots of 2 finished email
templates rendered, and the before/after contact sheet from Part D.

## Part E — LIST GROWTH ENGINE (added after deep-dive; HIGHEST PRIORITY OF ALL)
Measured reality: Klaviyo form views = 5 in 3 months, submissions = 0, new email
subscribers down to 5/month — on 40,000 sessions/month. Nothing else in this
brief matters as much as fixing this.
1. Build a Klaviyo onsite form set (Klaviyo UI → Sign-up forms): mobile-first
   popup (8s delay or 25% scroll, suppressed for existing profiles + 30d
   re-display rule), teaser tab, and exit-intent variant. Offer: FIRST10 — 10%
   off first order over R500. Style: match the 2026 design system (warm paper,
   forest green, serif headline "Join the apothecary list"). Two fields max
   (email; phone optional second step for future SMS).
2. Wire the THEME's existing capture points to Klaviyo (they currently barely
   feed it): footer newsletter, /#ol-community block, blog-email-capture snippet
   → submit to Klaviyo client API (public key S86r7e) list Xrk5jD.
3. Quiz pipeline: on quiz completion, push answers as Klaviyo profile properties
   (goal, etc.) + subscribe with consent checkbox; create a "Quiz Results" flow
   triggered on the Blog Quiz Result metric sending their matched protocol.
4. Flag for owner decision (do NOT change unilaterally): main list is double
   opt-in. Either optimize the confirmation email (2026 design, clear CTA) or
   owner approves single opt-in + sunset policy per POPIA appetite.
Success metric: ≥1,000 net new subscribers/month within 30 days of launch.
