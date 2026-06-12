# ONE LIFE HEALTH — CODEX HANDOFF 2026-06-11 (COMPLETE)

Repo: `clawdbot12345-ux/onelife-dashboard` · branch: `claude/onelife-health-review-lwvi3-c3yry2`
This single file contains everything. Two tasks, in this order.

═══════════════════════════════════════════════════════════════════
## TASK 1 — WIRE THE DISCOUNT-DEPENDENT KLAVIYO FLOWS (15 min, do first)
═══════════════════════════════════════════════════════════════════

Your previous pass reported "DISPENSARY10, STACK5 and STACK10 do not exist in
Shopify" and skipped wiring the flows that reference them. That finding was
wrong: you searched by discount TITLE. The codes exist and are ACTIVE under
descriptive titles. Verified 2026-06-11 via `codeDiscountNodeByCode`:

| Code | Terms | Shopify title |
|---|---|---|
| `FIRST10` | 10% off, min R500 cart | "FIRST10" |
| `STACK5` | 5% off, min 3 items | "Stack Discount 5%" |
| `STACK10` | 10% off, min 5 items | "Build Your Stack — 10% off any 5+ items" |
| `DISPENSARY10` | 10% off, min R600 cart | "Dispensary Protocol Bundle — 10% off stack" |

- Re-verify yourself with the Admin API query `codeDiscountNodeByCode(code: "...")`
  — never by title — then complete the flow/template wiring you deferred.
- When a template states a code's conditions, they must match the table above
  EXACTLY (e.g. never say "10% off any stack" without the R600 minimum for
  DISPENSARY10; STACK5 is 3+ ITEMS, not a rand minimum).
- Hard rules unchanged: do NOT touch Welcome Email 1 (it earns R97/recipient);
  never send anything to the full list (use Engaged 90d segment S3MAsK);
  free delivery threshold is R400 nationwide (never R900/R1,400); the team are
  "health consultants" (never coaches/pharmacists); 17 protocols (never 15);
  sign-off is Precious.
- Deliverable: confirmation of which flows/templates were wired, with flow IDs.

### Task 1 addendum — verified findings (Claude audit of the live Klaviyo account, 2026-06-11)
Direct inspection confirms exactly what remains. Work this list:

1. **6 of the 7 design-system templates are NOT wired into any sending flow.**
   Only Back in Stock (flow WT9YvU + template V8B7p5) is live. Welcome flow
   XZNrmz (last updated 9 Mar), Abandoned VAjbpG (22 Feb), Post-Purchase
   RpJP55 (5 May) and Win-Back 60 TGZYKa (5 May) are all still sending the
   OLD emails. Wire per reports/klaviyo-wiring-guide-2026-06-10.md:
   YdyAkd→Welcome #2, Y9SA46→Welcome #3, RpUzMu→Post-Purchase #2,
   TtqJqR→Abandoned #3, YatQ6s→Winback 90d, XkbgCw→Winback 120d. Note there
   is currently NO 90/120-day winback flow structure — extend Win-Back 60 v2
   (TGZYKa) with 90d and 120d emails or build the new flow per the guide.
   Welcome Email 1 stays untouched.
2. **Single opt-in was never configured.** List Xrk5jD ("Email List") is
   still `double_opt_in` — the owner explicitly requested single opt-in.
   Toggle in the Klaviyo UI (not available via API): Audience → Lists &
   Segments → Email List → Settings → Consent → single opt-in. Do the same
   for content lists TeSYf6 (Vivid Health) and WFPXyc (PCOS Interest).
   KEEP S44qNc (Text Messaging List) on double opt-in.
3. **4 of the 7 email hero images are over 1MB** (winback-90 1.14MB,
   post-purchase-02 1.13MB, welcome-02 1.16MB, welcome-03 1.10MB) — far too
   heavy for email on SA mobile data. Re-export all 7 at ≤300KB, 1240px
   wide, JPEG q80.
4. **All 7 hero `src` URLs point at THEME assets** (`/cdn/shop/t/41/assets/…`).
   If that draft theme is ever deleted, every email hero 404s forever. After
   compressing (item 3), upload the images to Klaviyo's own image hosting
   (or Shopify Files) and update the 7 templates' `src` to permanent URLs.
5. **Small copy fix while wiring:** template YdyAkd (Welcome #2) says
   "10% off bundled with DISPENSARY10" — add "(orders over R600)" to match
   the real code terms.
6. **One-line theme fix while you're in the theme:** `sections/slideshow.liquid`
   line ~142 hardcodes `data-autoplay="{% if template == 'index' %}false{% else %}…"`
   (perf-pass leftover) which froze the homepage hero. Claude shipped a JS
   shim in `snippets/whatsapp-float.liquid` that restores rotation; the
   proper fix is changing that attribute to
   `data-autoplay="{{ section.settings.auto_rotate }}"` and then DELETING
   the rotate() shim block from whatsapp-float.liquid. Do both or neither.
7. Verified clean — do NOT change: all 7 templates' brand facts (R400
   threshold, health consultants, 17 protocols, Precious sign-off), the
   STACK5/STACK10/FIRST10 terms as written, Friday template WQXytX, and
   Welcome Email 1.

═══════════════════════════════════════════════════════════════════
## TASK 2 — SITEWIDE LIFESTYLE IMAGERY (45 images, the main job)
═══════════════════════════════════════════════════════════════════

**Goal:** bring every page up to the visual standard of `/pages/vivid-health-story`
(the reference page — cinematic botanical hero, warm light, blank-label product).
A full visual walk of the live site (mobile 390px + desktop 1440px, every page)
found exactly where imagery is missing or wrong. This file lists **45 images**.

**rev 2:** every prompt below is now FULLY SELF-CONTAINED. Paste one prompt into
the image generator and get one finished image — no master block to prepend, no
assembly, no interpretation. Do not shorten, merge, or paraphrase the prompts.

**Repo / branch:** `clawdbot12345-ux/onelife-dashboard` → `claude/onelife-health-review-lwvi3-c3yry2`

## Theme workflow (critical)
- NEVER write to the live/published theme.
- Target theme: **"GROWTH BUILD 2026-06 — MOBILE V10 (ready to publish)"**
  (`gid://shopify/OnlineStoreTheme/186009518390`) — IF it is still UNPUBLISHED.
- If the owner has already published it, create a fresh duplicate of the current
  live theme (`themeDuplicate`), name it "GROWTH BUILD 2026-06 — IMAGERY <date>
  (ready to publish)", and upload there. The owner publishes fresh copies
  deliberately to bust Shopify's homepage cache.
- ⚠️ After `themeDuplicate`, poll the theme's `processing` field and WAIT until
  it is `false` before any `themeFilesUpsert`. Writes during processing return
  success but are silently clobbered (observed 2026-06-11).
- VERIFY EVERY UPLOAD: re-query each file's `checksumMd5` after upsert and
  confirm it changed. Report a filename→checksum table at the end.

## Export rules (apply to all 45)
- WebP quality 80 (JPEG q85 for the 10 collection images), strip metadata,
  every file under 350KB — SA mobile data costs are a conversion factor.
- Exact filenames as given. Exact pixel sizes as given.

## Standard negative prompt — append to EVERY generation, verbatim
> text, words, letters, numbers, typography, logo, watermark, signage, label
> copy, packaging text, extra fingers, deformed hands, plastic skin, doll-like
> faces, oversaturated HDR, harsh flash, sterile white studio background,
> illustration, 3D render, cartoon

---

## F1. Homepage "Featured Categories" tiles — 10 images 🔴 HIGHEST IMPACT

Current Shopify collection images are mismatched stock (the "Kids Health" tile
is balloons in a forest; "Home" is a house in a forest). **Size: 1200×1200
square, JPEG q85.** Upload: set as each collection's image via `collectionUpdate`
(or Admin → Products → Collections → [handle] → Collection image).

### F1.1 — collection `health`
> Photorealistic editorial lifestyle photograph, overhead flat-lay, 50mm
> full-frame look, shallow depth of field. A daily supplement ritual arranged
> on warm cream linen cloth (#F7F4ED tone): three amber glass supplement
> bottles of different heights with completely blank label-free surfaces, a
> small handmade ceramic dish holding golden softgel capsules, one sprig of
> fresh rosemary, a brass teaspoon. Soft golden morning light raking from the
> left, long gentle shadows, slightly desaturated warm film-like colour grade
> with deep forest green (#1B4332) accents in the shadows. Calm, premium
> apothecary mood. Absolutely no text, no logos, no writing on any surface.

### F1.2 — collection `conditions`
> Photorealistic editorial lifestyle photograph, close-up at 50mm, shallow
> depth of field. A mature South African woman's hands with natural skin
> texture cupping a warm handmade ceramic mug of herbal tea at an espresso-
> brown wooden table; beside the mug one amber glass supplement bottle with a
> completely blank label and a folded pair of reading glasses. Soft warm
> window light from the right, quiet reassuring mood, slightly desaturated
> warm film grade, cream and deep-green palette. Hands anatomically perfect.
> Absolutely no text, no logos, no writing anywhere.

### F1.3 — collection `beauty`
> Photorealistic macro beauty still life, 90mm macro look. Fine collagen
> powder drifting from a small brass scoop into a tall glass of water,
> catching warm backlight mid-pour; beside it a rose-toned ceramic dish and a
> single South African protea bloom on cream linen (#F7F4ED). Soft golden
> hour light, sparkling particles, shallow depth of field, slightly
> desaturated warm film grade. Premium, feminine, clean. Absolutely no text,
> no logos, no labels with writing.

### F1.4 — collection `food`
> Photorealistic rustic pantry still life, 35mm look, eye level. Espresso-
> brown wooden shelf holding glass jars of raw honey, rolled oats, chia seeds
> and loose rooibos tea — all jars completely label-free — with two worn
> wooden spoons and a folded linen cloth. Warm side light from a window
> camera-left, gentle shadows, slightly desaturated warm film grade, cream
> and forest-green palette. Honest, wholesome, premium farm-pantry mood.
> Absolutely no text, no logos, no writing on any jar.

### F1.5 — collection `sport`
> Photorealistic editorial lifestyle photograph, 35mm look. A fit South
> African man in his mid-30s with natural skin texture, seated on a wooden
> gym bench beside a large window, towel around his neck, mid-shake of a
> blender bottle containing a vanilla protein shake — bottle completely
> blank, no markings. Golden hour light flooding through the window, dust
> motes in the beam, warm slightly desaturated film grade with deep green
> tones in the background. Strong but warm mood, not a sterile gym ad. Hands
> anatomically perfect. Absolutely no text, no logos anywhere.

### F1.6 — collection `kids`
> Photorealistic editorial lifestyle photograph, 35mm look, natural candid
> feel. A South African mother's hand giving a single gummy vitamin to a
> laughing 6-year-old child at a sunlit breakfast table with a glass of
> orange juice; soft-focus warm kitchen behind. Gentle morning window light,
> joyful genuine expressions, natural skin texture, warm slightly
> desaturated film grade, cream and soft green palette. Warm family mood,
> NOT clinical. Hands anatomically perfect. Absolutely no text, no logos, no
> packaging with writing.

### F1.7 — collection `pets`
> Photorealistic editorial lifestyle photograph, 35mm look. A golden
> retriever sitting attentively in a warm cream-toned kitchen, looking up at
> its owner's hand holding a small treat-style supplement; on the counter
> behind, one amber glass jar with a completely blank label. Soft warm
> window light, shallow depth of field on the dog's face, warm slightly
> desaturated film grade. Loving, calm mood. Absolutely no text, no logos,
> no writing anywhere.

### F1.8 — collection `home`
> Photorealistic natural-home still life, 50mm look. On a cream-painted
> wooden shelf: one amber glass spray bottle with a completely blank label, a
> beeswax pillar candle, a neat stack of folded natural linen cloths, and
> eucalyptus stems in a handmade ceramic vase. Soft diffused morning light,
> gentle botanical shadows on the wall, warm slightly desaturated film
> grade, cream (#F7F4ED) and sage palette. Clean, calm, toxin-free home
> mood. Absolutely no text, no logos, no writing on any container.

### F1.9 — collection `food-superfoods`
> Photorealistic overhead food still life, 50mm look. Small handmade ceramic
> bowls arranged on dark espresso wood, each holding a vivid superfood:
> deep-green spirulina powder, red goji berries, raw cacao nibs, green
> moringa powder; one brass spoon resting between bowls, a dusting of powder
> on the wood. Dramatic but warm side light, rich saturated naturals against
> the dark wood, slightly desaturated warm film grade overall. Premium,
> vibrant, appetising. Absolutely no text, no logos, no packaging.

### F1.10 — collection `vivid-health`
> Photorealistic premium product still life, 50mm look. A tight cluster of
> five amber glass supplement bottles of varying heights, every label surface
> completely blank, standing on deep forest-green linen (#1B4332 tone) with
> sprigs of indigenous South African fynbos beside them; dappled botanical
> shadow falling across the scene as if through leaves. Warm directional
> light, deep green and amber palette, slightly desaturated premium film
> grade. House-brand hero mood — quiet confidence. Absolutely no text, no
> logos, no writing anywhere.

---

## F2. Dispensary Protocols hub hero — 2 images

Upload to theme assets. Composition note: LEFT third must stay calm/uncluttered
— headline text overlays there.

### F2.1 — `onelife-protocols-hub-hero-2400.webp` (2400×1000)
> Photorealistic editorial photograph inside a warm apothecary dispensary at
> golden hour, 35mm look, wide cinematic crop. Mid-frame right: a health
> consultant's hands (anatomically perfect, natural skin) writing with a
> fountain pen on a blank kraft-paper card beside a small wooden tray holding
> five amber glass supplement bottles with completely blank labels; behind,
> shelves of amber jars softly blurred into a deep forest-green darkness
> (#1B4332). One warm shaft of light from camera-right. The LEFT third of the
> frame is calm, dark and uncluttered for text overlay. Mood: a pharmacist
> preparing a personal prescription — intimate, trustworthy, premium. Warm
> slightly desaturated film grade. Absolutely no readable writing anywhere,
> the kraft card shows only indistinct pen strokes, no text, no logos.

### F2.2 — `onelife-protocols-hub-hero-1080.webp` (1080×1350 portrait)
> Photorealistic editorial photograph inside a warm apothecary dispensary at
> golden hour, 35mm look, vertical portrait crop. Centered lower-half: a
> health consultant's hands (anatomically perfect) writing with a fountain
> pen on a blank kraft-paper card beside a wooden tray of five amber glass
> supplement bottles with completely blank labels; shelves of amber jars
> softly blurred into deep forest-green darkness behind. One warm light
> shaft from upper right; the TOP third of the frame is calm and dark for
> text overlay. Intimate, trustworthy, premium apothecary mood, warm
> slightly desaturated film grade. No readable writing anywhere — only
> indistinct pen strokes on the card. No text, no logos.

---

## F3. The 17 protocol page heroes (+1 bonus) — 2000×900 each

Upload to theme assets. **Filename pattern: `onelife-protocol-{handle}-hero-2000.webp`.**
Every image: subject weighted RIGHT, the LEFT 40% calm negative space for text
overlay. All share the same DNA: photorealistic, 35–50mm full-frame look,
shallow depth of field, warm natural light, slightly desaturated warm film
grade, cream/forest-green/espresso palette, blank-label amber bottles, perfect
hands, NO text/logos/writing anywhere.

### F3.1 — `onelife-protocol-sleep-ritual-hero-2000.webp`
> Photorealistic editorial photograph, 50mm look, wide 2000×900 crop, subject
> weighted to the RIGHT half, left 40% of frame calm and softly out of focus
> for text overlay. A bedside table at dusk: one amber glass supplement
> bottle with a completely blank label, a small ceramic cup of chamomile tea
> with gentle steam, fresh lavender sprigs, washed linen bedding softly
> blurred behind, one warm low lamp glowing amber. Dusty lavender and warm
> cream palette over deep shadow, slightly desaturated film grade. Quiet,
> sleepy, safe mood. Absolutely no text, no logos, no writing.

### F3.2 — `onelife-protocol-stress-reset-hero-2000.webp`
> Photorealistic editorial photograph, 35mm look, wide 2000×900 crop, subject
> weighted RIGHT, left 40% calm for text overlay. A South African woman in
> her 30s, eyes closed mid-exhale, seated in a sunlit linen armchair holding
> a warm cup of herbal tea with both hands (anatomically perfect); on the
> side table an amber supplement bottle with a completely blank label and a
> piece of dried ashwagandha root. Warm sage-green and cream palette, soft
> window light, slightly desaturated film grade. Mood of release and calm.
> No text, no logos, no writing anywhere.

### F3.3 — `onelife-protocol-winter-immunity-hero-2000.webp`
> Photorealistic editorial photograph, 50mm look, wide 2000×900 crop, subject
> weighted RIGHT, left 40% calm for text overlay. A winter kitchen counter:
> halved oranges, fresh ginger root, a small open jar of raw honey with a
> wooden dipper, echinacea stems, one amber supplement bottle with a
> completely blank label, steam rising from a hot mug. Cool blue window
> light from outside warmed by golden interior light, citrus-amber accents,
> slightly desaturated warm film grade. Cosy defence-against-winter mood. No
> text, no logos, no writing.

### F3.4 — `onelife-protocol-gut-reset-hero-2000.webp`
> Photorealistic editorial photograph, 50mm look, wide 2000×900 crop, subject
> weighted RIGHT, left 40% calm for text overlay. A bright morning kitchen:
> a glass of kefir, a ceramic bowl of live-culture yoghurt topped with
> berries, a fermentation jar of vegetables, and one amber probiotic bottle
> with a completely blank label on a pale wood counter. Clean bright morning
> window light, soft apricot and cream palette, slightly desaturated warm
> film grade. Fresh, light, digestive-health mood. No text, no logos.

### F3.5 — `onelife-protocol-joint-care-hero-2000.webp`
> Photorealistic editorial photograph, 35mm look, wide 2000×900 crop, subject
> weighted RIGHT, left 40% calm sky/garden for text overlay. An active
> silver-haired South African man in his 60s stretching his leg on outdoor
> steps at sunrise after a walk, knee support sleeve visible, steel water
> bottle (blank, unmarked) beside him. Warm terracotta rim light from the
> low sun, natural skin texture, slightly desaturated warm film grade.
> Capable, dignified, active-ageing mood. No text, no logos anywhere.

### F3.6 — `onelife-protocol-daily-energy-hero-2000.webp`
> Photorealistic editorial photograph, 35mm look, wide 2000×900 crop, subject
> weighted RIGHT, left 40% calm wall for text overlay. A morning launch
> scene in a cream hallway: a fresh espresso cup on a wooden side table next
> to one amber supplement bottle with a completely blank label, running
> shoes placed by the door, hard golden morning sun streaking across the
> wall in long diagonal beams. Golden yellow and cream palette, slightly
> desaturated warm film grade. Energetic start-of-day mood. No text, no
> logos, no writing.

### F3.7 — `onelife-protocol-brain-focus-hero-2000.webp`
> Photorealistic editorial photograph, 50mm look, wide 2000×900 crop, subject
> weighted RIGHT, left 40% calm for text overlay. A precise, calm study
> desk: an open notebook with BLANK pages, a fountain pen aligned beside it,
> one amber omega-3 bottle with a completely blank label, a glass of water,
> a sprig of rosemary. Soft window light, deep teal and cream palette,
> everything ordered and minimal, slightly desaturated warm film grade.
> Clear-headed deep-work mood. Absolutely no text — notebook pages are
> empty. No logos.

### F3.8 — `onelife-protocol-heart-health-hero-2000.webp`
> Photorealistic editorial food photograph, 50mm look, wide 2000×900 crop,
> subject weighted RIGHT, left 40% calm deep-green linen for text overlay. A
> heart-healthy kitchen scene: a fresh salmon fillet on a wooden board,
> shelled walnuts, olive oil in a clear glass cruet (unmarked), and one
> amber omega supplement bottle with a completely blank label, all on deep
> forest-green linen. Rich warm directional light, deep rose and green
> palette, slightly desaturated warm film grade. Nourishing, substantial
> mood. No text, no logos, no writing.

### F3.9 — `onelife-protocol-womens-hormonal-hero-2000.webp`
> Photorealistic editorial photograph, 35mm look, wide 2000×900 crop, subject
> weighted RIGHT, left 40% calm for text overlay. A South African woman in
> her 30s journaling at a sunlit table — notebook pages BLANK, pen mid-
> stroke (hands anatomically perfect) — with a cup of herbal tea, yellow
> evening-primrose blooms in a small ceramic vase, and one amber supplement
> bottle with a completely blank label. Soft blush and cream palette, gentle
> window light, slightly desaturated warm film grade. Self-possessed, calm,
> in-control mood. No readable writing anywhere, no logos.

### F3.10 — `onelife-protocol-mens-vitality-hero-2000.webp`
> Photorealistic editorial photograph, 35mm look, wide 2000×900 crop, subject
> weighted RIGHT, left 40% calm dawn sky for text overlay. A grounded South
> African man in his early 40s tying running-shoe laces on outdoor stone
> steps at dawn (hands anatomically perfect, natural skin texture); beside
> him one amber supplement bottle with a completely blank label and a steel
> water flask, both unmarked. Strong warm side light, deep forest-green and
> amber palette, slightly desaturated warm film grade. Quiet strength mood.
> No text, no logos anywhere.

### F3.11 — `onelife-protocol-weight-management-hero-2000.webp`
> Photorealistic overhead editorial food photograph, 50mm look, wide
> 2000×900 crop, subjects weighted RIGHT, left 40% calm pale-wood surface
> for text overlay. A balanced meal-prep flat-lay: grilled chicken breast
> sliced on a board, fresh leafy greens, halved avocado, a glass meal-prep
> container, a protein shaker bottle completely blank and unmarked, and a
> soft measuring tape coiled neatly as a quiet design element — NOT wrapped
> around anything. Bright honest daylight, fresh green and cream palette,
> slightly desaturated warm film grade. Supportive, practical, zero shame
> mood. No text, no logos.

### F3.12 — `onelife-protocol-kids-foundation-hero-2000.webp`
> Photorealistic editorial photograph, 35mm look, wide 2000×900 crop,
> subjects weighted RIGHT, left 40% calm kitchen wall for text overlay. Two
> South African children laughing at a breakfast counter while a parent
> hands one a chewable vitamin; glasses of orange juice, playful genuine
> warm morning chaos, natural skin textures and anatomically perfect hands.
> Sunshine-orange and cream palette, bright soft morning light, slightly
> desaturated warm film grade. Joyful family-foundation mood, NOT clinical.
> No text, no logos, no packaging with writing.

### F3.13 — `onelife-protocol-skin-beauty-hero-2000.webp`
> Photorealistic editorial still life, 50mm look, wide 2000×900 crop, subject
> weighted RIGHT, left 40% calm marble for text overlay. A morning vanity
> scene on cream marble: an open glass jar of collagen powder (completely
> blank, unmarked), a rose-quartz facial roller, a single protea bloom, a
> glass of citrus-infused water; sheer curtain diffusing golden morning
> light. Rose-gold and cream palette, soft glow, slightly desaturated warm
> film grade. Radiant, unhurried self-care mood. No text, no logos.

### F3.14 — `onelife-protocol-mood-lift-hero-2000.webp`
> Photorealistic editorial photograph, 35mm look, wide 2000×900 crop, subject
> weighted RIGHT, left 40% bright calm wall for text overlay. A person seen
> from behind opening curtains to flooding morning sunlight in a cream
> bedroom — silhouette rim-lit gold; on the windowsill, yellow St John's
> Wort flowers in a small glass and one amber supplement bottle with a
> completely blank label. Warm gold and cream palette, hopeful rising-light
> mood, slightly desaturated warm film grade. No text, no logos anywhere.

### F3.15 — `onelife-protocol-healthy-ageing-hero-2000.webp`
> Photorealistic editorial photograph, 35mm look, wide 2000×900 crop,
> subjects weighted RIGHT, left 40% calm garden bokeh for text overlay. A
> dignified silver-haired South African couple laughing together over tea at
> a garden table in honeyed late-afternoon light; on the wooden tray, two
> amber supplement bottles with completely blank labels; indigenous fynbos
> softly blurred behind. Bronze and cream palette, natural skin texture,
> deep genuine joy, slightly desaturated warm film grade. Vital, warm,
> aspirational ageing. No text, no logos.

### F3.16 — `onelife-protocol-liver-detox-hero-2000.webp`
> Photorealistic editorial still life, 50mm look, wide 2000×900 crop, subject
> weighted RIGHT, left 40% calm pale wood for text overlay. A clean reset
> scene: a clear glass teapot of green tea mid-pour into a glass cup, purple
> milk-thistle flowers, a glass of lemon water, fresh dandelion greens, and
> one amber supplement bottle with a completely blank label on pale
> bleached wood. Airy bright diffused light, crisp green and cream palette,
> slightly desaturated warm film grade. Light, clean, fresh-start mood. No
> text, no logos.

### F3.17 — `onelife-protocol-glp1-companion-hero-2000.webp`
> Photorealistic editorial photograph, 35mm look, wide 2000×900 crop, subject
> weighted RIGHT, left 40% calm for text overlay. A confident South African
> woman in her 40s preparing a high-protein breakfast in a bright kitchen:
> eggs in a pan, a bowl of Greek yoghurt, a protein shake in a completely
> blank unmarked shaker; beside the hob, two amber supplement bottles with
> completely blank labels arranged next to a weekly pill organiser with
> UNLABELLED compartments. Steel-blue and warm cream palette, calm capable
> morning light, natural skin and perfect hands, slightly desaturated warm
> film grade. Supportive, non-judgemental, in-control mood. No text, no
> logos, no readable markings anywhere.

### F3.18 (bonus) — `onelife-protocol-pcos-support-hero-2000.webp`
> Photorealistic editorial photograph, 35mm look, wide 2000×900 crop, subject
> weighted RIGHT, left 40% calm for text overlay. A South African woman in
> her mid-20s preparing a balanced breakfast bowl — Greek yoghurt topped
> with mixed seeds and berries — beside a glass jar of fine white inositol-
> style powder, completely blank and unmarked, and a cup of spearmint tea
> with fresh mint leaves. Soft mint-green and cream palette, encouraging
> calm morning light, natural skin texture and perfect hands, slightly
> desaturated warm film grade. Hopeful, taking-charge mood. No text, no
> logos anywhere.

---

## F4. Homepage dispensary band background — 1 image

### F4.1 — `onelife-dispensary-band-bg-1600.webp` (1600×900)
> Photorealistic abstract texture photograph, 85mm look, heavily defocused.
> Inside a dark apothecary: out-of-focus amber glass jars on deep green-
> stained wooden shelves (#1B4332 tones), one soft warm shaft of light
> falling diagonally; everything reads as pure atmosphere and bokeh — no
> object in sharp focus. VERY low contrast, no bright highlights, dark
> overall exposure: this image sits BEHIND white text at 35% opacity, so it
> must stay quiet and even. Deep green, espresso and dim amber palette,
> slightly desaturated film grade. No text, no logos, no readable shapes.

---

## F5. Article topic banners — 16 images (covers all 125 articles)

**Size: 1600×640. Filename: `onelife-article-topic-{slug}-1600.webp`.**
Upload to THEME ASSETS only with these exact filenames, then reply in the PR —
Claude wires them into the article template keyed off the existing topic map.
Do NOT edit `article-guide-cta.liquid` or `main-article.liquid` yourself.
Shared composition law for all 16: subject weighted to the RIGHT half; the LEFT
half is calm cream linen (#F7F4ED) negative space for the headline overlay.

### F5.1 — `onelife-article-topic-magnesium-1600.webp`
> Photorealistic wide editorial banner photograph, 50mm look, 1600×640 crop.
> Subject weighted to the RIGHT half, LEFT half calm cream linen (#F7F4ED)
> negative space for headline text. On the right: white magnesium capsules
> spilling from a tipped amber glass bottle with a completely blank label,
> beside dark leafy greens, a small pile of pumpkin seeds and two shards of
> dark chocolate on espresso wood. Warm directional light, slightly
> desaturated warm film grade, deep green accents. No text, no logos, no
> writing anywhere.

### F5.2 — `onelife-article-topic-omega3-1600.webp`
> Photorealistic wide editorial banner photograph, 50mm look, 1600×640 crop.
> Subject weighted RIGHT, LEFT half calm cream linen negative space for
> headline text. On the right: translucent golden fish-oil softgels glowing
> in backlight inside a small ceramic dish, beside a fresh salmon portion on
> parchment, shelled walnuts and a spoonful of flaxseed. Warm low side
> light, amber and cream palette, slightly desaturated warm film grade. No
> text, no logos, no writing.

### F5.3 — `onelife-article-topic-vitamind-1600.webp`
> Photorealistic wide editorial banner photograph, 35mm look, 1600×640 crop.
> Subject weighted RIGHT, LEFT half calm sunlit cream wall for headline
> text. On the right: a windowsill in full morning sun — one amber glass
> supplement bottle with a completely blank label casting a long shadow,
> halved citrus fruit, a leafy houseplant edge. Strong golden sunbeam,
> dust motes visible in the light, warm slightly desaturated film grade.
> Sunshine-vitamin mood. No text, no logos.

### F5.4 — `onelife-article-topic-ashwagandha-1600.webp`
> Photorealistic wide editorial banner photograph, 50mm look, 1600×640 crop.
> Subject weighted RIGHT, LEFT half calm cream linen negative space for
> headline text. On the right: dried ashwagandha roots and a small mound of
> fine beige powder on espresso wood beside a stone mortar and pestle and a
> cup of golden tea with rising steam. Earthy ochre, sage and cream
> palette, warm side light, slightly desaturated warm film grade. Grounded
> adaptogen mood. No text, no logos.

### F5.5 — `onelife-article-topic-collagen-1600.webp`
> Photorealistic wide editorial banner photograph, 90mm macro look, 1600×640
> crop. Subject weighted RIGHT, LEFT half calm cream linen for headline
> text. On the right: collagen powder pouring from a brass scoop into a
> tall glass of water, the stream catching warm backlight with visible
> sparkle, a single protea bloom beside the glass. Rose-gold and cream
> palette, shallow depth of field, slightly desaturated warm film grade. No
> text, no logos.

### F5.6 — `onelife-article-topic-probiotics-1600.webp`
> Photorealistic wide editorial banner photograph, 50mm look, 1600×640 crop.
> Subject weighted RIGHT, LEFT half calm cream linen for headline text. On
> the right: a bright ferment still life — a glass of kefir, a jar of
> red-cabbage kimchi (jar unmarked), a bowl of yoghurt, and one amber
> probiotic bottle with a completely blank label on pale wood in clean
> morning kitchen light. Fresh apricot and cream palette, slightly
> desaturated warm film grade. No text, no logos, no writing on jars.

### F5.7 — `onelife-article-topic-sleep-1600.webp`
> Photorealistic wide editorial banner photograph, 50mm look, 1600×640 crop.
> Subject weighted RIGHT, LEFT half calm dim cream wall for headline text.
> On the right: a dusk bedside scene — lavender sprigs across washed linen,
> a low warm lamp glow, a ceramic cup of chamomile tea, one amber
> supplement bottle with a completely blank label. Dusty lavender and warm
> amber palette over soft shadow, slightly desaturated film grade. Sleepy,
> safe mood. No text, no logos.

### F5.8 — `onelife-article-topic-stress-1600.webp`
> Photorealistic wide editorial banner photograph, 35mm look, 1600×640 crop.
> Subject weighted RIGHT, LEFT half calm cream linen for headline text. On
> the right: a close exhale moment — a woman's hands (anatomically perfect,
> natural skin) cupping a steaming mug of herbal tea in a sunlit linen
> armchair, sage-green throw blanket. Soft sage and cream palette, gentle
> window light, slightly desaturated warm film grade. Release-of-tension
> mood. No text, no logos.

### F5.9 — `onelife-article-topic-immunity-1600.webp`
> Photorealistic wide editorial banner photograph, 50mm look, 1600×640 crop.
> Subject weighted RIGHT, LEFT half calm cream linen for headline text. On
> the right: a winter immunity still life — halved oranges, fresh ginger,
> echinacea stems, an open jar of raw honey with dipper, steam rising from
> a hot mug. Citrus-amber and cream palette, cool window light warmed by
> interior glow, slightly desaturated warm film grade. No text, no logos.

### F5.10 — `onelife-article-topic-gut-1600.webp`
> Photorealistic wide editorial banner photograph, 50mm look, 1600×640 crop.
> Subject weighted RIGHT, LEFT half calm cream linen for headline text. On
> the right: a fermented-foods spread on pale wood — sauerkraut and kimchi
> in unmarked glass jars, a bowl of berries on yoghurt, a glass of
> kombucha — bright fresh morning light. Soft apricot, green and cream
> palette, slightly desaturated warm film grade. Light digestive-health
> mood. No text, no logos, no jar labels.

### F5.11 — `onelife-article-topic-glp1-1600.webp`
> Photorealistic wide editorial banner photograph, 35mm look, 1600×640 crop.
> Subject weighted RIGHT, LEFT half calm cream linen for headline text. On
> the right: a high-protein breakfast in preparation — eggs in a pan, Greek
> yoghurt bowl, an unmarked blank protein shaker — beside a weekly pill
> organiser with unlabelled compartments and two amber supplement bottles
> with completely blank labels. Steel-blue and warm cream palette, calm
> capable morning light, slightly desaturated warm film grade. Supportive,
> non-judgemental mood. No text, no logos, no readable markings.

### F5.12 — `onelife-article-topic-energy-1600.webp`
> Photorealistic wide editorial banner photograph, 35mm look, 1600×640 crop.
> Subject weighted RIGHT, LEFT half calm cream wall with sun streaks for
> headline text. On the right: an espresso cup with crema beside one amber
> supplement bottle with a completely blank label on a wooden hallway
> table, running shoes by the door behind, hard golden morning sunbeams
> raking diagonally. Golden yellow and cream palette, energetic morning
> mood, slightly desaturated warm film grade. No text, no logos.

### F5.13 — `onelife-article-topic-joints-1600.webp`
> Photorealistic wide editorial banner photograph, 35mm look, 1600×640 crop.
> Subject weighted RIGHT, LEFT half calm warm sky for headline text. On the
> right: a silver-haired South African man stretching on outdoor steps at
> sunrise after a walk, knee sleeve visible, unmarked steel water bottle
> beside him, warm terracotta rim light, natural skin texture. Dignified
> active mood, slightly desaturated warm film grade. No text, no logos.

### F5.14 — `onelife-article-topic-skin-1600.webp`
> Photorealistic wide editorial banner photograph, 50mm look, 1600×640 crop.
> Subject weighted RIGHT, LEFT half calm cream marble for headline text. On
> the right: a vanity still life — open unmarked glass jar of collagen
> powder, rose-quartz facial roller, protea bloom, glass of citrus water,
> sheer-curtain-diffused golden light. Rose-gold and cream palette,
> radiant unhurried mood, slightly desaturated warm film grade. No text,
> no logos.

### F5.15 — `onelife-article-topic-hormones-1600.webp`
> Photorealistic wide editorial banner photograph, 35mm look, 1600×640 crop.
> Subject weighted RIGHT, LEFT half calm cream linen for headline text. On
> the right: a woman journaling at a sunlit table — notebook pages BLANK,
> hands anatomically perfect — with herbal tea, yellow evening-primrose
> blooms in a ceramic vase, one amber supplement bottle with a completely
> blank label. Soft blush and cream palette, self-possessed calm mood,
> slightly desaturated warm film grade. No readable writing, no logos.

### F5.16 — `onelife-article-topic-general-1600.webp`
> Photorealistic wide editorial banner photograph, 50mm look, 1600×640 crop.
> Subject weighted RIGHT, LEFT half calm cream linen for headline text. On
> the right: the signature apothecary counter — a vintage brass balance
> scale, rows of amber glass jars with completely blank labels, dried
> botanicals hanging, dappled leaf-shadow falling across espresso wood.
> Deep green, amber and cream palette, warm directional light, slightly
> desaturated warm film grade. Timeless trusted-apothecary mood. No text,
> no logos, no writing anywhere.

---

## Already covered — do NOT regenerate
Homepage hero slides (5, desktop+mobile), Vivid story page hero, About hero,
Practitioner hero, Brands hero, Quiz hero, Subscribe (unboxing) hero, Store
locator hero, 3 store-page heroes, 13 collection landers, consultation banner,
the 7 Klaviyo email heroes (Part A), the 20 article-specific heroes (Part C),
and the top-50 product-photo pilot (Part D).

## Upload mechanics recap
- Theme assets: `themeFilesUpsert` with base64 `body: { type: BASE64, value }`
  — verify EVERY upload by re-querying the file's `checksumMd5` (a previous
  agent silently delivered 3 of 9 uploads).
- Collection images (F1): `collectionUpdate` with `image: { src }` after
  staging via `stagedUploadsCreate`, or set manually in Admin.
- Deliverable: filename→checksum table for all 45, the theme ID used, and
  screenshots of the homepage category strip, the GLP-1 protocol hero, and
  one article banner in place.
