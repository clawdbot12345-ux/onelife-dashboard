# Codex Image Brief — Vivid pages imagery (consultation + 4 guides)

The new Vivid pages shipped without hero imagery (live now at
`/pages/consultation` and `/pages/guide-*` on
`hgywg0-w7.myshopify.com`). This brief specifies one hero image per
page plus the consultation-page in-body banner. Codex (or whichever
image tool — Gemini Nano Banana Pro, Midjourney, FLUX, or a real
photographer) should produce them, upload to Shopify Files, then patch
each page body to insert the image at the top.

## Brand art-direction baseline

Apply to every shot below. Same baseline as
`vivid/codex-pillars-prompt.md`:

- **Mood:** Editorial, calm, considered. Aesop / Apothékary energy.
  Not "wellness Instagram." Not stock photography.
- **Light:** Warm, single directional source, soft falloff. Late-
  afternoon window light or warm tungsten. No flat ringlight.
- **Palette:** Cream paper, sage greens, terracotta/clay, ochre
  highlights, deep forest shadows. Vivid bottles where they appear are
  matte cream with a black label — recognisable but never the hero of
  the frame.
- **Composition:** Leave breathing room around the focal subject.
  Aspect 3:2 (landscape) for in-body hero images, 16:7 for full-bleed
  banners. The bottom-left quadrant must read dark enough that white
  type can sit cleanly over it on the consultation page.
- **No people staring at camera.** No "wellness influencer" framing.
  Single hand or torso visible at most.

## Output spec

- **Format:** JPEG, sRGB, quality 88
- **Dimensions:**
  - Hero (landscape, 3:2 ratio): 1800×1200 px
  - Consultation banner (16:7): 2000×875 px
- **File names + Shopify Files keys** (lowercase, kebab-case):
  - `page-consultation-hero.jpg` (2000×875, banner format)
  - `page-guide-magnesium-sleep-hero.jpg`
  - `page-guide-omega3-brain-health-hero.jpg`
  - `page-guide-ashwagandha-stress-hero.jpg`
  - `page-guide-vitamin-d3-immunity-hero.jpg`

## Shot briefs

### 1. `page-consultation-hero.jpg` — banner

**Subject:** A warm overhead shot of a notepad, pen, half-drunk
mug of tea, a single Vivid bottle (matte cream label visible),
a worn copy of a herbal-medicine reference book, and a hand
reaching for the pen. Late-afternoon window light coming from
the top-right.

**Mood:** "Someone has been listened to and someone is writing
things down." Not clinical. Not a clinic. Could be a kitchen
table or a living-room desk. The naturopath consultation feels
human, not medical.

**Composition:** 16:7 banner, hand and pen in the lower-third
right, mug and bottle in centre, notepad spans most of the
frame, soft shadow gradient bottom-right that white type can
sit cleanly over. Implied story: a 15-minute call that's
actually about you.

### 2. `page-guide-magnesium-sleep-hero.jpg`

**Subject:** A bedside-table still life at dusk. A glass of
water, the Vivid Tranquil bottle (label visible, lying on its
side casually), an unwound watch, a paperback novel face-down,
a single mineral chunk (representing magnesium — a piece of
selenite or amethyst or any pale crystalline mineral works).
Soft pool of warm lamp light from above-frame.

**Mood:** End of day. The room is calming, not posed. Real
domestic, not hotel-room.

**Composition:** Top-down or 30°-down angle. Lamp shadows
falling across the table. Lower-third bottle, upper two-thirds
the rest.

### 3. `page-guide-omega3-brain-health-hero.jpg`

**Subject:** A flat-lay of fresh sardines on a slate or marble
surface, alongside the Vivid Omega Oil bottle (label up),
sprigs of fresh parsley, a wedge of lemon, and a small glass
of golden oil. No human element.

**Mood:** Cold-kitchen, food-photography. The fish is the
subject; the supplement is the supporting cast. Implies the
real source — actual fish, not a marketing chart.

**Composition:** Top-down, 3:2 landscape. Fish dominates the
left two-thirds, bottle + oil glass in the right third. Cool
natural light from the side.

### 4. `page-guide-ashwagandha-stress-hero.jpg`

**Subject:** A botanical still-life of raw ashwagandha root
(the actual gnarled Withania somnifera root — looks like a
pale, knotted parsnip), beside a small mortar and pestle with
some ground root inside, on a linen cloth. Subtle morning
light from the side.

**Mood:** Apothecary table. Suggests centuries-of-use without
being orientalist or kitsch. Quiet, knowing.

**Composition:** 3:2 landscape. Root in the centre-left, mortar
in the lower-right. Loose cloth folds in the background.
Earthy, dusty palette — taupes, off-whites, the soft sage of
the leaves if any are present.

### 5. `page-guide-vitamin-d3-immunity-hero.jpg`

**Subject:** Early-morning South African outdoor scene —
specifically a kitchen or windowsill view looking out onto a
sunny Gauteng garden, with the warm yellow light streaming
through a window onto a wooden surface holding a Vivid bottle
and a single Cape gooseberry, lemon, or sliced naartjie
(seasonal SA citrus).

**Mood:** Local, specific, climatic. Not generic "sunshine"
stock. The light is the protagonist — D3 is what your skin
makes from this exact morning light.

**Composition:** 3:2 landscape. Window edge in the top-third
casting a hard light-line across the frame. Bottle and fruit
in the lower-third, partially in the light beam, partially in
shadow.

## Wiring once delivered

Upload each file to Shopify Files. Then patch each page's body to
prepend a `<figure>` block referencing the uploaded image. The
publish script supports re-running:

```bash
node scripts/vivid-publish-content.mjs
```

Update the page-body strings in `scripts/vivid-publish-content.mjs`
(or in the equivalent local `vivid/data/pages/*.html` source files)
to begin with:

```html
<figure class="page-hero">
  <img src="https://cdn.shopify.com/.../page-consultation-hero.jpg"
       alt="…short alt text…" width="2000" height="875"
       loading="eager" fetchpriority="high">
</figure>
```

For the consultation page the figure goes BEFORE the `<h2>` heading.
For the four guide pages it goes BEFORE the `<p class="lede">`.

## CSS already in place

`vivid/theme/assets/base.css` already styles `.page-rte img` to full
width with rounded corners and a 1px border. No additional CSS work
needed — the figures will render correctly on first load.

## What we're not asking for

- No people staring into the camera
- No "naturopath in a white coat with a clipboard" tropes
- No iStock-grade smiling-woman-with-supplement-bottle shots
- No mortar-and-pestle clichés with chamomile flowers
- No overlaid text in the images themselves — typography lives in the
  page template
- No watermarks
