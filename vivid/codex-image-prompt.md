# Codex prompt — Generate uniform product imagery for all 55 Vivid Health SKUs

Copy this entire prompt into a new Claude Code session (Codex) that has access to:
- The Shopify MCP server (connected to the Onelife store at onelife.co.za)
- Image generation capabilities (Claude image generation / Image 2.0)

---

## Context

Vivid Health is a South African supplement brand with 55 SKUs sold on onelife.co.za
under the "VIVID HEALTH" vendor name. We're building a standalone Shopify store at
vividhealthsa.co.za and need uniform, premium product imagery across all 55 products.

The brand has a category-color label system:
- **Immune Health** = peach/coral (#FF8C6B) — Allergy Control, Mullein, Astragalus, Buffered C, L-Lysine, Quercetin, Immune Plus
- **Physical Health** = forest green (#4A7C59) — Bone Supreme, MSM, Flexijoint, Joint Relief, Omega Oil, Liver & Kidney
- **Women's Health** = dusty plum (#8B5E6B) — Maca, Sage, Angus Castus
- **Mental Health** = deep blue (#4A6FA5) — Griffonia 5-HTP, Tranquil, GABA, Liquorice Root
- **Gut Health** = warm clay (#B87333) — Black Walnut, Clove, Wormwood, Colon Flush
- **Nutrient Health** = sage green (#6B8E6B) — Turmeric, Cayenne, Moringa, Spirulina, Apple Cider, Barley Grass, CoQ10, D-Ribose, L-Glutamine, Garcinia, Colest Control, Epsom Salt, DMAE, Turmeric Plus
- **Men's Health** = earth/charcoal (#5C5347) — Prosta Care

Each product bottle is white with a color band matching its category,
the "VIVID HEALTH" wordmark in white on the color band, the product
name below, and a category icon badge with capsule count.

## Task

### Step 1: Extract all Vivid product images from Shopify

Use the Shopify MCP tools to query the Onelife store:

```
Search products with vendor "VIVID HEALTH" on the connected store.
For each product, extract:
- Product title
- Product handle
- All image URLs (featured image + additional images)
- Product type / tags
- Price
```

Save the extracted data to `vivid/data/shopify-images.json`.

### Step 2: Generate images per product

**CRITICAL — Cinematic photography direction (applies to ALL formats below)**

Every image must follow these rules to achieve true studio/cinematic quality:

1. **Dramatic directional lighting.** Use a strong key light from the left or right side (never flat/even). Visible shadow fall-off across the bottle and surface. Rim light separating the bottle from the background. The lighting should look like a single window or studio strobe — NOT diffused ambient.

2. **Shallow depth of field.** Shoot at f/2.8 or wider. The product bottle is tack-sharp. Background props are soft and dreamy with visible bokeh circles. This is the #1 thing that separates cinematic from catalog.

3. **Angle variety across the set.** For each product's 4 images (A-D), use a DIFFERENT angle:
   - Image A: front-on hero, slightly below eye level (heroic angle)
   - Image B: top-down 90-degree flat-lay
   - Image C: extreme close-up macro, 15-degree angle on the ingredient
   - Image D: 3/4 angle with the person, product at arm's length toward camera

4. **One "imperfect" prop element per shot.** One herb sprig slightly out of frame. Honey mid-drip. A leaf caught mid-fall. A lemon half-squeezed with juice visible. This makes it feel styled by a human, not placed by an algorithm.

5. **Contact shadows must be physically convincing.** The bottle sits ON the surface with a real shadow. No floating. The shadow should show the direction of the key light.

6. **Color grading:** warm highlights (slightly golden), cool shadows (slightly blue-green). This is the "cinematic" color science. Avoid flat neutral white balance.

7. **Resolution:** 1200x1500px (4:5 portrait) for product cards, 1920x1080px (16:9 landscape) for hero/banner images.

---

For EACH of the 55 Vivid Health products, generate these images:

**Image A — Hero product shot (primary card image)**
Prompt pattern:
```
Cinematic product photography of a white supplement bottle labeled
"VIVID HEALTH" with a [CATEGORY COLOR] color band. Product name
"[PRODUCT NAME]" on the label. Category badge "[CATEGORY NAME]" with
icon. [CAPSULE COUNT] capsules. The bottle sits on a natural stone
podium against a [SCENE BACKGROUND]. Strong directional key light
from the left with visible shadow fall-off. Rim light on the right
edge of the bottle. Shot on medium format camera at f/2.8, background
props beautifully out of focus with visible bokeh. One botanical prop
element slightly out of frame. Warm golden highlights, cool blue-green
shadows. No text overlays outside the label. 1200x1500px.
```

Scene backgrounds by category:
- Immune Health: soft cream linen with dried lavender sprigs
- Physical Health: dark green forest backdrop with stone podium
- Women's Health: dusty rose velvet with warm golden light
- Mental Health: deep blue evening bedroom scene, bedside table
- Gut Health: earthy botanical scene with herbs and roots
- Nutrient Health: bright morning kitchen, natural wood surface
- Men's Health: dark leather and wood masculine setting

**Image B — Lifestyle context shot**
Prompt pattern:
```
Cinematic top-down flat-lay photograph, shot at f/2.8 on a 50mm lens.
A white supplement bottle labeled "VIVID HEALTH [PRODUCT NAME]" with
[CATEGORY COLOR] band lies slightly angled on a [SURFACE]. Surrounded
by [LIFESTYLE PROPS], with one element slightly out of frame and one
element in slight motion (dripping honey, falling petal, steam rising).
Strong directional light from upper-left creating long diagonal shadows.
Background props soft with visible bokeh. Warm highlights, cool shadows.
Premium editorial supplement brand photography. 1200x1500px.
```

Lifestyle props by category:
- Immune Health: fresh citrus slices, eucalyptus, honey jar mid-drip
- Physical Health: yoga mat edge, resistance band, rosemary sprig
- Women's Health: dried flowers, journal, herbal tea with steam rising
- Mental Health: glass of water, open book, candle with soft glow
- Gut Health: fresh herbs, mortar and pestle, lemon half-squeezed
- Nutrient Health: avocado half, greens, smoothie bowl
- Men's Health: leather watch, black coffee, dark wood grain

**Image C — Ingredient close-up**
Prompt pattern:
```
Extreme macro close-up of [RAW INGREDIENT] — the active ingredient in
Vivid Health [PRODUCT NAME]. [INGREDIENT DESCRIPTION]. Shot at f/2.0
on a macro lens, 15-degree low angle. The raw ingredient fills 70% of
the frame with incredible texture detail. A white supplement bottle with
[CATEGORY COLOR] band is visible but completely out of focus in the
background (heavy bokeh). Single dramatic side light creating deep
shadows and texture on the ingredient surface. Warm cinematic color
grade. 1200x1500px.
```

**Image D — AI influencer / person-holding-product shot**
Prompt pattern:
```
Cinematic portrait photograph of a [DEMOGRAPHIC] person holding a white
supplement bottle labeled "VIVID HEALTH [PRODUCT NAME]" with a
[CATEGORY COLOR] label band toward the camera at 3/4 angle. The person
is [ACTIVITY CONTEXT]. Shot at f/2.0, the person's face is slightly
soft while the product label is tack-sharp (focus on the product).
Strong natural window light from one side creating dramatic shadow on
the opposite side of the face. Warm golden skin tones. Background
heavily blurred with visible bokeh. The scene feels candid and
aspirational, not posed. 1200x1500px.
```

Demographics and contexts by category:
- Immune Health: woman 30s, morning kitchen with citrus + tea
- Physical Health: athletic man/woman 35-45, post-workout with towel, Pilates studio
- Women's Health: woman 30-40, serene morning breakfast scene with granola + lemon water
- Mental Health: person 30s, evening bedroom reading scene, warm lamp light
- Gut Health: woman 25-35, bright kitchen preparing herbs
- Nutrient Health: diverse person 30s, outdoor morning light, active lifestyle
- Men's Health: man 35-50, modern home office or morning routine

**Image E — Before/after transformation split (for key products)**
Generate ONLY for these high-impact products:
- Griffonia 5-HTP: "Restless Nights → Restful Nights" (blue cold vs warm lamp)
- Allergy Control: "Allergy Season → Breathing Easy" (sneezing vs outdoors smiling)
- MSM / Flexijoint: "Stiff Joints → Moving Freely" (holding knee vs active hiking)
- Tranquil: "Stressed Days → Calm Evenings" (work stress vs relaxed evening)
- Maca: "Low Energy → Rooted Energy" (fatigued vs vibrant morning)
- Buffered C: "Catching Everything → Building Immunity" (sick in bed vs healthy active)

Each before/after uses a vertical split layout:
- Left side: "BEFORE" with cold/blue tones, problem state
- Right side: "AFTER" with warm/golden tones, resolved state
- Product bottle centered between the two panels
- Before: 4 problem bullet points with X marks
- After: 4 benefit bullet points with checkmarks
- Bottom: brand tagline

**Image F — Product infographic (benefits + trust badges)**
Generate for ALL 55 products. Layout:
```
Top: VIVID HEALTH wordmark in category color
Large headline: "[BENEFIT HEADLINE]." e.g. "Strong Bones. Active Life."
Right side: product bottle on stone podium with botanical props
Left side: 3 benefit pills with icons (category-colored icons):
  - [Benefit 1] with icon + short description
  - [Benefit 2] with icon + short description
  - [Benefit 3] with icon + short description
Green "SHOP NOW" button
Bottom strip: 4 trust badges (Premium Ingredients, Science Backed,
  Quality Assured, Easy Daily Routine)
Footer bar: category tagline
```

**Image G — "Them vs Us" competitive comparison**
Generate for the 10 highest-value SKUs. Layout:
```
Top: "THEM VS US — The clear choice for [benefit]"
Left half (dark grey/charcoal): "THEM" column with 3 weakness points
  shown as grey circle icons (Calcium only, Basic support, etc.)
Right half (category color gradient): "US" column with product bottle +
  3 strength points as green circle icons (Calcium + D3 + K2 + Mg, etc.)
Central "VS" divider circle
```

**Image H — "From Clutter to Calm" brand before/after**
Generate 3 variants. Layout:
```
Headline: "FROM CLUTTER TO CALM" or "FROM SCATTERED TO SORTED"
Subline: "Your daily wellness routine, refined."
Left photo: messy supplement shelf — generic amber bottles scattered,
  blister packs, cardboard boxes, loose capsules
Right photo: clean marble shelf with Vivid products neatly arranged,
  color-coded, with boxes behind bottles
Footer: "Available at Onelife"
```

**Image I — Morning kitchen lifestyle (multi-product hero)**
Generate 3 variants showing 3-5 Vivid products on a marble kitchen
counter with morning props (steaming coffee mug, glass of water,
eucalyptus sprig, linen napkin). Warm natural light. Headline overlay:
"WELLNESS THAT FITS YOUR DAY" + "Premium daily support. House brand value."
+ testimonial quote. Footer: "VIVID HEALTH - Available at Onelife"

**Image J — "Onelife House Brand. Built Better." collection hero**
Generate for the Onelife.co.za collection page. 4 core products +
boxes arranged on stone/marble. Trust badge callouts floating around
the products: "Trusted by Onelife customers", "Premium wellness essentials",
"Clear routines, clean shelf". Footer: "Shop Vivid Health at Onelife"

### Step 3: Upload to Shopify

For each generated image:
1. Upload to the Vivid Shopify store's Files section
2. Attach as product images to the corresponding product
3. Set Image A as the featured/primary image

### Step 4: Save locally

Also save all generated images to `vivid/assets/products/generated/`
with the naming convention:
```
{product-handle}-hero.jpg
{product-handle}-lifestyle.jpg
{product-handle}-ingredient.jpg
```

### Step 5: Update the prototype

Update `vivid/index.html`:
- Replace the HEROES and CATEGORY_HEROES mappings with the new
  per-product generated images
- Every product should now have its OWN hero image (no more category
  fallbacks needed)
- Update the PDP gallery to show all 3 images per product

## Product list (55 SKUs)

Handle | Name | Category | Key ingredient for Image C
---|---|---|---
mullein-60 | Mullein | Immune | Dried mullein leaves
clove-60 | Clove | Gut | Whole clove buds
colon-flush-120 | Colon Flush | Gut | Magnesium oxide powder
turmeric-300 | Turmeric | Nutrient | Fresh turmeric root, sliced
cayenne-300 | Cayenne | Nutrient | Red cayenne peppers
liver-kidney-90 | Liver & Kidney | Physical | Milk thistle flower heads
black-walnut-60 | Black Walnut | Gut | Green black walnut hulls
wormwood-60 | Wormwood | Gut | Artemisia annua leaves
maca-60 | Maca | Women | Raw maca root, cross-sectioned
flexijoint-advanced-120 | Flexijoint Advanced | Physical | Glucosamine crystals
d-ribose-150 | D-Ribose | Nutrient | White crystalline ribose powder
bone-supreme-120 | Bone Supreme | Physical | Calcium + boron mineral specimens
omega-oil-90 | Omega Oil | Nutrient | Golden fish oil capsules spilling
prosta-care-60 | Prosta Care | Men | Saw palmetto berries
allergy-control-60 | Allergy Control | Immune | Elderberry flowers + quercetin powder
colon-flush-powder-135 | Colon Flush Powder | Gut | Magnesium oxide powder
colest-control-60 | Colest Control | Nutrient | Red yeast rice grains
astragalus-60 | Astragalus | Immune | Dried astragalus root slices
l-glutamine-500 | L-Glutamine | Nutrient | White amino acid powder
l-lysine-60 | L-Lysine | Immune | White lysine crystals
buffered-c-300 | Buffered C | Immune | Orange segments + calcium ascorbate powder
tranquil-60 | Tranquil | Mental | Dried passionflower + valerian root
sage-60 | Sage | Women | Fresh sage leaves
msm-90 | MSM | Physical | White crystalline MSM powder
msm-500 | MSM Powder | Physical | White crystalline MSM powder with scoop
msm-300 | MSM | Physical | MSM crystals close-up
liquorice-root-60 | Liquorice Root | Mental | Dried liquorice root sticks
joint-relief-60 | Joint Relief | Physical | Cissus quadrangularis stem
garcinia-cambogia-60 | Garcinia Cambogia | Nutrient | Green garcinia fruit, halved
cayenne-90 | Cayenne | Nutrient | Dried red cayenne peppers
cayenne-250g | Cayenne Powder | Nutrient | Cayenne powder in wooden bowl
buffered-c-90 | Buffered C | Immune | Calcium ascorbate powder + orange peel
buffered-c-150g | Buffered C Powder | Immune | Buffered C powder with measuring spoon
apple-cider-90 | Apple Cider Vinegar | Nutrient | Apple cider vinegar with mother, in glass jar
turmeric-plus-60 | Turmeric Plus | Nutrient | Turmeric root + black peppercorns
advanced-buffered-c-300 | Advanced Buffered C | Immune | Zinc tablets + vitamin C powder + citrus bioflavonoids
spirulina-250g | Spirulina Powder | Nutrient | Deep green spirulina powder
quercetin-complex-60 | Quercetin Complex | Immune | Yellow quercetin powder + bromelain crystals
omega-oil-300 | Omega Oil | Nutrient | Fish oil soft gel capsules, golden
msm-150g | MSM Powder | Physical | MSM powder with measuring scoop
moringa-300 | Moringa | Nutrient | Fresh moringa leaves on branch
immune-plus-60 | Immune Plus | Immune | Olive leaf + echinacea flower
griffonia-5htp-60 | Griffonia (5-HTP) | Mental | Griffonia simplicifolia seed pods
gaba-150g | GABA Powder | Mental | White GABA powder
flexijoint-300 | Flexijoint | Physical | Glucosamine + chondroitin powder
epsom-salt-1kg | Epsom Salt | Nutrient | Epsom salt crystals in bath bowl
dmae-150g | DMAE Powder | Nutrient | DMAE white powder
coq10-60 | Coenzyme Q10 | Nutrient | Orange CoQ10 powder/crystals
bone-supreme-500 | Bone Supreme | Physical | Calcium mineral with vitamin D3 drops
barley-grass-300 | Barley Grass | Nutrient | Young green barley grass shoots
barley-grass-200g | Barley Grass Powder | Nutrient | Barley grass powder, vibrant green
angus-castus-60 | Angus Castus | Women | Chasteberry (vitex) berries on branch

## Quality requirements

- All images must be 1200x1500px (4:5 ratio) to match the card aspect
- Consistent white balance across all photos
- The Vivid bottle design must be CONSISTENT across all renders — same
  bottle shape, same label layout, same font treatment
- No AI artifacts (extra fingers, warped text, inconsistent label text)
- If the image gen can't render label text accurately, use a plain white
  bottle with a solid color band (no text) and note which images need
  manual label overlay
- Save originals at highest quality available

## After completion

Commit all images and data changes, push to the branch
`claude/vivid-health-shopify-redesign-KITNn`, and note which images
(if any) have label text issues that need manual correction.
