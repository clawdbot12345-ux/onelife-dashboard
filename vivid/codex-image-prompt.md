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

### Step 2: Generate 3 uniform images per product

For EACH of the 55 Vivid Health products, generate 3 images using
image generation:

**Image A — Hero product shot (primary card image)**
Prompt pattern:
```
Professional product photography of a white supplement bottle labeled
"VIVID HEALTH" with a [CATEGORY COLOR] color band. Product name
"[PRODUCT NAME]" on the label. Category badge "[CATEGORY NAME]" with
icon. [CAPSULE COUNT] capsules. The bottle sits on a natural stone
podium against a [SCENE BACKGROUND]. Soft natural lighting, shallow
depth of field, editorial magazine quality. Shot on medium format
camera. No text overlays outside the label.
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
Lifestyle flat-lay photograph featuring a white supplement bottle
labeled "VIVID HEALTH [PRODUCT NAME]" with [CATEGORY COLOR] band.
Surrounded by [LIFESTYLE PROPS]. Morning natural light, top-down
angle, linen or marble surface. Premium editorial supplement brand
photography. Warm tones.
```

Lifestyle props by category:
- Immune Health: fresh citrus slices, eucalyptus, honey jar
- Physical Health: yoga mat edge, resistance band, rosemary
- Women's Health: dried flowers, journal, herbal tea
- Mental Health: glass of water, book, candle, nightstand
- Gut Health: fresh herbs, mortar and pestle, lemon
- Nutrient Health: avocado, greens, smoothie bowl
- Men's Health: leather watch, coffee, dark wood

**Image C — Ingredient close-up**
Prompt pattern:
```
Close-up still life of [RAW INGREDIENT] — the active ingredient in
Vivid Health [PRODUCT NAME]. [INGREDIENT DESCRIPTION]. Shot on macro
lens with shallow depth of field. Natural light. The raw ingredient
dominates the frame. A small white supplement bottle is visible but
out of focus in the background. Premium editorial photography.
```

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
