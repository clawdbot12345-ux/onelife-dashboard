# Codex Brief — Image Generation Art Direction (GPT-image-2.0)
**Goal:** one photographic language across the entire store. Claude wires
everything into the theme/products once assets exist; Codex generates + QAs
+ uploads to Shopify Files with the exact naming below.

## THE VISUAL SYSTEM (north star — every image obeys this)
- **Palette:** deep green `#10261F` / `#2D6A4F` · cream `#FAF7F0` · warm
  stone `#EDE7DA` · muted brass/gold accent. Nothing candy, nothing neon.
- **Light:** soft directional window light from upper-left ~35°, warm
  (golden-hour temperature), gentle falloff, ONE soft shadow to lower-right.
- **Surfaces:** warm stone / cream plaster tabletop for product work; deep
  matte green backdrop for hero/editorial.
- **Props (sparingly, max 2 per image):** SA botanicals — rooibos sprigs,
  buchu, protea, rosemary; amber glass; brass scoop; raw linen.
- **Mood in one line:** *"the apothecary counter at golden hour."*
- **Never:** emoji styling, plastic gradients, stock-photo smiles, added
  text/typography inside images, purple/teal casts.

## BRIEF A — Product background unification (THE moat move, do first)
**Technique: image-to-image EDIT, never text-to-image.** Input = the
existing real packshot. The label must remain pixel-faithful — AI-invented
label text is a product-misrepresentation risk. Reject any output where
label text warped, reflowed, or "improved".

Prompt template (per product, attach source image):
> "Keep this exact product completely unchanged — same label, same text,
> same proportions, same colors. Replace ONLY the background and surface:
> place the product standing on a warm stone surface (#EDE7DA) against a
> soft cream gradient background (#FAF7F0), lit by soft warm window light
> from the upper left at ~35°, casting one gentle soft shadow to the lower
> right. Photorealistic, premium apothecary product photography, square
> 2048×2048, product occupies ~70% of frame height, centered."

QA checklist per image (reject & retry on any fail): label text identical
and legible · no added text anywhere · bottle/jar geometry unchanged ·
shadow direction lower-right · background within palette.

Batch order: (1) the 45–52% margin heroes (Celtic Salt, Lugols, K2 MK7,
Lions Mane, Sea Moss Gel, NeoMag, Castor Oil, MSM), (2) top-100 sellers from
the dashboard, (3) full Vivid range, (4) everything else opportunistically.
Naming: `pp-{product-handle}.jpg` → upload to Shopify Files. Then attach as
the product's FIRST image (keep original supplier shots after it).

## BRIEF B — 17 Protocol editorial heroes (text-to-image, no products)
Format: 1600×900 + a 1080×1350 crop each. NO text in image. Same system.
One-line scene per protocol:
1. Sleep Ritual — moonlit linen bedding, amber glass jar, lavender sprig, dark green wall
2. Winter Immunity — steaming ceramic mug, citrus halves, rooibos, frosted window light
3. Stress Reset — single protea in amber vase, open journal, warm shadow play
4. Gut Reset — kefir glass, fennel fronds, stone mortar on cream linen
5. Heart Health — olive branch, deep red rooibos tea, brass scale detail
6. Daily Energy — morning light streak across stone, coffee-adjacent warmth, green ferns
7. Joint Care — hands at rest on linen, rosemary sprig, warm oil in amber bottle
8. Skin & Beauty — cream textures, rose quartz light, botanical oil droplets on stone
9. Women's Hormonal — evening primrose flowers, soft cyclical shadows, warm cream
10. GLP-1 Companion — balanced plate motif (protein, greens), measuring spoon, calm order
11–17. (remaining protocols: same system; derive scene from the protocol name,
propose to Claude for sign-off before generating.)
Naming: `protocol-{slug}-hero.jpg`.

## BRIEF C — Vivid house-brand stage
1. **Lineup hero:** full Vivid range in a row on deep matte green, dramatic
   low-key lighting, brass accent — 2400×1200. (image-to-image from real
   renders if possible; labels faithful.)
2. **3 lifestyle scenes:** morning counter, gym bag + towel, bedside table —
   one Vivid product each (image-to-image, label preserved).
3. **Texture macros:** capsule spill on stone, powder swirl — text-to-image OK.
Naming: `vivid-stage-{n}.jpg`.

## BRIEF D — Homepage hero replacement
Replace the phone-mockup slide. One shot: hands (brown skin, no face)
passing a wrapped amber bottle across a wooden counter, botanical shadows,
golden hour, deep green apron in soft-focus background. 2800×1600 + mobile
1080×1620 crop. `home-hero-counter.jpg`.

## BRIEF E — Wordmark CONCEPTS (exploration only — final goes to a designer)
10 concepts: serif "One Life" wordmark + small-caps "APOTHECARY · EST. 1996"
descriptor; optional engraved mark (mortar & pestle / protea / botanical
sprig) in a thin-line etching style; cream/deep-green/brass only. Square,
on cream. These are DIRECTION material for a human designer to redraw as
vector — never ship AI raster as the logo. Naming: `wordmark-concept-{n}.png`.

## ICONS — do NOT generate
Replace all emoji with a consistent thin-line icon library (Phosphor or
Lucide, 1.5px stroke, brand green). Claude handles this in the theme pass.

## Codex also owns (not image work)
- **Checkout branding (30 min, Settings → Checkout → Customize):** cream
  background, deep-green buttons/accents, the current green wordmark at
  proper resolution — kill the default blue/purple. (Full rebrand lands
  when the new wordmark ships.)
- Rewards page: embed the actual Smile launcher or rewrite the copy to
  match reality; restyle the teal gradient to brand.
- Upload cadence: batch of 20 → ping Claude → wiring pass.
