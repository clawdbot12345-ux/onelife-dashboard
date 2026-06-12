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

### The 7 heroes — copy-paste generation prompts
Each block below is a complete, self-contained prompt for your image generator.
Generate at 1200×600 (or 2400×1200 downscaled). After generating, QA against:
no text/logos/labels, no AI artifacts on hands, subject readable at 600px wide.

**A1 — Welcome #2 (template YdyAkd)**
PROMPT: "Photorealistic cinematic studio photograph, overhead flat-lay on warm
sage-green linen: four small supplement groupings arranged like a tasting menu —
an amber glass bottle with dried lavender sprigs; a dark green glass bottle with
gold cap beside sliced orange and fresh ginger root; a sleek white jar next to a
small glass of kefir; a second amber bottle with scattered coffee beans and cacao
nibs. A Black woman's hands with neat natural nails entering frame from the
bottom edge, mid-arrangement. All bottle labels blank/unbranded. Bright optimistic
morning window light, soft shadows, shot on Phase One, f/4, magazine editorial
quality. Landscape 2:1, subject centre-weighted, calm uncluttered top edge.
No text, no logos, no typography anywhere."

**A2 — Welcome #3 (template Y9SA46)**
PROMPT: "Photorealistic cinematic photograph, eye-level across a walnut apothecary
counter: a warm-toned consultant's hands gently passing a single dark green glass
supplement bottle with gold cap into a customer's open hands, faces out of frame,
blurred wooden apothecary shelving stocked with amber bottles behind, warm
tungsten light mixed with soft daylight, shallow depth of field f/1.8, Hasselblad
look, editorial warmth, the handover is the story. Blank unbranded label.
Landscape 2:1, centre-weighted. No text, no logos, no typography."

**A3 — Post-Purchase #2 (template RpUzMu)**
PROMPT: "Photorealistic still life, 45-degree angle: two complementary supplement
bottles side by side almost touching on warm walnut wood — one dark green glass
with gold cap, one amber glass — a single fresh rosemary sprig bridging the two
caps, one soft unified shadow, golden-hour side light raking across the wood
grain, Phase One macro clarity, premium editorial. Blank unbranded labels.
Landscape 2:1, centred pair, generous calm margins. No text, no logos."

**A4 — Winback 90d (template YatQ6s)**
PROMPT: "Photorealistic cinematic photograph: a nearly-empty amber glass
supplement bottle standing on a white-painted wooden windowsill, five or six
golden capsules visible through the glass at the bottom, sheer linen curtain
catching late-afternoon golden light, soft out-of-focus green garden beyond the
window, dust motes in the light beam, nostalgic and warm — NOT melancholic.
f/2, Hasselblad. Blank unbranded label. Landscape 2:1, bottle slightly
left-of-centre with glowing window light filling the frame. No text, no logos."

**A5 — Winback 120d (template XkbgCw)**
PROMPT: "Photorealistic minimal still life: one dark green glass supplement
bottle with gold cap, perfectly centred on a clean light-oak floating shelf
against a warm cream plaster wall, soft diffuse daylight from the left, gentle
shadow, enormous calm negative space all around, quiet dignified mood, premium
gallery aesthetic, Phase One sharpness. Blank unbranded label. Landscape 2:1.
No text, no logos, no other objects."

**A6 — Back in Stock (template V8B7p5)**
PROMPT: "Photorealistic cinematic photograph: a hand placing a dark green glass
supplement bottle with gold cap front-and-centre into a gap on a warm wooden
apothecary shelf, flanked by slightly out-of-focus amber and white bottles,
subtle motion energy in the gesture, shallow focus locked on the placed bottle,
warm shop lighting with a soft shelf glow, editorial retail warmth, f/2.2.
All labels blank/unbranded. Landscape 2:1, hero bottle centred.
No text, no logos, no typography."

**A7 — Abandoned Cart #3 (template TtqJqR)**
PROMPT: "Photorealistic lifestyle photograph, over-the-shoulder: a hand holding
a smartphone showing a softly blurred green-and-white chat interface (completely
unreadable, no legible UI or text), beside it on a white marble kitchen counter
a small open kraft-paper basket holding three unbranded supplement bottles (dark
green, amber, white), fresh morning kitchen light, shallow depth keeping phone
and basket in focus, warm domestic editorial mood, f/2.8. Landscape 2:1,
phone left-of-centre, basket right. No readable text anywhere, no logos."

### Insertion
Upload each via Klaviyo image upload, then update each template's HTML: insert one
hero <tr> directly below the 4px accent-bar row —
`<tr><td><img src="..." width="620" alt="<one-line scene description>" style="display:block;width:100%;height:auto;"/></td></tr>`
Keep ALL copy, facts, links and the {% raw %}{% unsubscribe %}{% endraw %} tag exactly as-is.

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
4. OWNER HAS DECIDED — execute: switch the main Email List (Xrk5jD) to
   **single opt-in** (Klaviyo → Lists & Segments → Email List → Settings →
   Consent → Single opt-in). Also switch the content lists (Vivid Health TeSYf6,
   PCOS Interest WFPXyc) to single opt-in. KEEP the Text Messaging List (S44qNc)
   double opt-in — SMS compliance. Compensate with hygiene: confirm the Sunset
   Unengaged flow is live and feeding suppressions, so single opt-in never rots
   deliverability.
Success metric: ≥1,000 net new subscribers/month within 30 days of launch.
