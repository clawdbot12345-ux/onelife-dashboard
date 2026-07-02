# Codex Image Brief — WHY VIVID Pillars (3 hero shots)

These three vertical photographs replace the placeholder banners currently
sitting in the WHY VIVID section on the Vivid Health home page
(`vivid/index.html`, the `.why-vivid` section). Each pillar is a
full-bleed editorial card with type overlaid on a dark scrim.

## Art direction — overall

- **Format**: 3:4 vertical (1200×1600 minimum, 1800×2400 ideal)
- **Mood**: Editorial, calm, considered. Aesop / Apothékary / Necessaire
  energy. Not "wellness Instagram." Not corporate product photography.
- **Light**: Warm, single directional source, soft falloff. Late-afternoon
  window light or warm tungsten. No flat ringlight, no studio whiteout.
- **Palette**: Cohere to the brand — cream paper, sage greens,
  terracotta/clay, ochre highlights, deep forest shadows. Vivid's
  packaging is matte cream with a black label — keep the bottles
  recognisable but never the hero of the frame.
- **Tone**: Quiet confidence. Each image should feel like a single
  unstaged moment, not a composed marketing shot.
- **Bottom 40% of frame must read dark enough for white type to sit
  cleanly** — composition should give the type room to breathe at the
  bottom-left of the card. Plan the dark-fall accordingly.

## Shot 01 — "We put the dose on the bottle."

**Eyebrow on the card**: The receipt
**Headline overlaid**: We put the dose on the *bottle.*
**Pillar promise**: Every milligram on every label, named, not blended.

**Subject**: A single Vivid bottle, label rotated to face camera,
photographed on a precision lab scale (analytical balance with digital
readout visible — "0.81g" or similar dose-relevant number on the
display). Light wood or stone surface. One bottle, in focus. Background
slightly out, suggesting a working bench (paper notes, a pen, a glass
beaker far back — props barely visible).

**Composition**: Bottle centred slightly upper-third. Scale and readout
visible in the lower-left. Bottom-right of the frame falls into warm
shadow so type can sit cleanly over it. Slight high-angle, 20° down.

**Mood reference**: Scientific but human. Like a chef's mise en place,
not a forensics lab.

## Shot 02 — "Plants first. Always."

**Eyebrow on the card**: The source
**Headline overlaid**: Plants *first.* Always.
**Pillar promise**: Whole-plant extracts, vegetable capsules, nothing
imported in bulk and relabelled.

**Subject**: A flat-lay of a single Vivid bottle surrounded by the raw
botanical it's formulated from — turmeric root sliced open with curcumin
visible, or fresh mullein leaves, or dried saw palmetto berries. The
plant material is the protagonist; the bottle is a quiet anchor in the
composition.

**Composition**: Top-down, full bleed. Bottle in the lower-third,
botanical material flowing across the upper two-thirds and bleeding off
all four edges. Linen or unbleached paper backdrop. The bottom of the
frame is the darkest plane — type-friendly.

**Mood reference**: Herbalist's table, not Whole Foods marketing. Real
plants with imperfect edges. One bottle, intentionally placed.

## Shot 03 — "One bottle, one job."

**Eyebrow on the card**: The work
**Headline overlaid**: One bottle, *one job.*
**Pillar promise**: 52 formulations, each built for a specific outcome.
No hero ingredients chasing a trend.

**Subject**: A South African evening interior — kitchen counter or
bedside table — with a single Vivid bottle, a glass of water, and a
human element (a hand reaching, a worn book, a folded reading glasses
case). The bottle is in use, not on display. Implied story: somebody
takes this every night because it does what it says.

**Composition**: 35mm-ish lens, slightly off-axis, gives the scene
weight. The bottle is upper-third, the human element (hand or object)
lower-third. Warm tungsten light from a lamp. The lower portion of the
frame is intentionally darker so type sits cleanly.

**Mood reference**: A still from a film, not an advertisement. The
moment a habit becomes a routine.

## Technical requirements

- Output filenames: `pillar-01-dose.jpg`, `pillar-02-plants.jpg`,
  `pillar-03-outcome.jpg`
- Save to `vivid/assets/banners/`
- Format: JPEG, quality 88, 1800×2400 px
- Colour profile: sRGB, no embedded ICC larger than 4KB

## Wiring

Once delivered, swap three lines in `vivid/index.html` inside the
`.why-vivid-cards` block:

```diff
- <div class="why-card-bg" style="background-image:url('assets/banners/banner-group-bestsellers.jpg')"></div>
+ <div class="why-card-bg" style="background-image:url('assets/banners/pillar-01-dose.jpg')"></div>

- <div class="why-card-bg" style="background-image:url('assets/banners/banner-immunity.jpg')"></div>
+ <div class="why-card-bg" style="background-image:url('assets/banners/pillar-02-plants.jpg')"></div>

- <div class="why-card-bg" style="background-image:url('assets/banners/banner-hero-evening.jpg')"></div>
+ <div class="why-card-bg" style="background-image:url('assets/banners/pillar-03-outcome.jpg')"></div>
```

## What we're not asking for

- No people staring into the camera
- No stock-wellness imagery (women in white robes meditating, etc.)
- No bottles arranged like a chess set
- No "natural" cliches (forest backgrounds, dramatic mountain shots)
- No oversaturated "Instagram supplement" warm filter
- No watermarks, no overlaid graphics — we'll layer the type ourselves
