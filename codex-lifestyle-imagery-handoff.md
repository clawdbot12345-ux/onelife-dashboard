# Codex Handoff — Part F: Sitewide Lifestyle Imagery (2026-06-11)

**Goal:** bring every page up to the visual standard of `/pages/vivid-health-story`
(the reference page — cinematic botanical hero, warm light, blank-label product).
A full visual walk of the live site (mobile 390px + desktop 1440px, every page)
found exactly where imagery is missing or wrong. This file lists **45 images**,
each with its own generation prompt, exact filename, exact size, and exact
upload destination.

**Repo / branch:** `clawdbot12345-ux/onelife-dashboard` → `claude/onelife-health-review-lwvi3-c3yry2`
**Theme to upload to:** the *unpublished* staging theme **"GROWTH BUILD 2026-06 — LAUNCH READY"**
(`gid://shopify/OnlineStoreTheme/185971867958`) — same workflow as before; the
owner publishes when ready. Do NOT write to the live theme.

---

## F0. MASTER STYLE BLOCK — prepend to EVERY prompt below, verbatim

> Editorial lifestyle photograph for a premium South African apothecary and
> health store. Warm natural light (soft golden-hour or gentle morning window
> light), shallow depth of field, shot on a 35–50mm full-frame look. Palette:
> warm cream and linen surfaces (#F7F4ED), deep forest green accents (#1B4332),
> espresso-brown wood, muted sage. Props where relevant: amber glass supplement
> bottles and jars with COMPLETELY BLANK labels (no text, no logos), eucalyptus,
> rosemary, citrus, indigenous South African fynbos and protea, linen cloth,
> ceramic bowls, brass scoop. People, when present, are diverse South African
> adults with natural skin texture and anatomically correct hands. Absolutely
> NO text, NO typography, NO logos, NO brand names, NO labels with writing
> anywhere in the image. Consistent warm, slightly desaturated film-like colour
> grade across the whole set. High detail, photorealistic, no illustration look.

**Negative prompt for all:** text, words, letters, logo, watermark, label copy,
extra fingers, deformed hands, plastic skin, oversaturated HDR, stock-photo
glare, sterile white studio.

---

## F1. Homepage "Featured Categories" tiles — 10 images 🔴 HIGHEST VISUAL IMPACT

The homepage featured-category strip currently uses mismatched stock photos
(the "Kids Health" tile is balloons in a forest; "Home" is a house in a forest).
These are **Shopify collection images** — upload by setting the collection's
image in Admin → Products → Collections → [collection] → Edit → Collection
image (or via `collectionUpdate` mutation with the image).

**Size: 1200×1200 square. JPEG quality 85.**

| # | Collection handle | Prompt (after master block) |
|---|---|---|
| 1 | `health` | Overhead flat-lay of a daily supplement ritual on warm cream linen: three amber glass bottles (blank labels), a small ceramic dish holding soft-gel capsules, a sprig of rosemary, morning light raking across. |
| 2 | `conditions` | A caring close-up: mature South African woman's hands cupping a warm ceramic mug beside one amber supplement bottle (blank label) and a folded reading-glasses case on an espresso wood table; quiet, reassuring mood. |
| 3 | `beauty` | Macro beauty still life: collagen powder drifting from a brass scoop into a glass of water, catching light, beside a rose-quartz tone ceramic dish and a single protea bloom on cream linen. |
| 4 | `food` | Rustic pantry scene: glass jars of raw honey, rolled oats, chia seeds and dried rooibos (all jars blank), wooden spoons, on an espresso wood shelf with warm side-light. |
| 5 | `sport` | Athletic but warm: a fit South African man mid-30s seated on a gym bench by a window, towel around neck, shaking a blender bottle of vanilla protein shake (bottle blank), golden light through the window. |
| 6 | `kids` | A mother's hand giving a happy 6-year-old South African child a gummy vitamin at a sunlit breakfast table, glass of orange juice, soft focus kitchen behind — joyful, natural, NOT clinical. |
| 7 | `pets` | A golden retriever sitting attentively in a warm kitchen as its owner holds a small treat-style supplement; amber jar (blank label) on the counter; shallow depth of field. |
| 8 | `home` | Natural home & cleaning still life: glass amber spray bottle (blank), beeswax candle, folded linen cloths, eucalyptus stems in a ceramic vase on a cream shelf. |
| 9 | `food-superfoods` | Vibrant overhead of superfood bowls: spirulina powder, goji berries, cacao nibs, moringa, each in small ceramic bowls arranged on espresso wood, one brass spoon, dramatic-but-warm side light. |
| 10 | `vivid-health` | Hero product still: a cluster of amber supplement bottles (blank labels) on a forest-green linen backdrop with indigenous fynbos sprigs and dappled botanical shadow — premium, house-brand mood. |

**Filenames if uploading to theme instead:** `onelife-cat-{handle}-1200.jpg`.

## F2. Dispensary Protocols hub hero — 2 images

The hub (`/pages/dispensary-protocols`) opens on a flat dark-green text band.

- `onelife-protocols-hub-hero-2400.webp` — 2400×1000 (desktop)
- `onelife-protocols-hub-hero-1080.webp` — 1080×1350 (mobile portrait)

**Prompt:** Inside a warm apothecary dispensary at golden hour: a consultant's
hands (mid-frame, anatomically perfect) writing on a kraft-paper card beside a
small wooden tray holding five amber supplement bottles (blank labels), shelves
of jars softly blurred in the deep-green background; the mood of a pharmacist
preparing a personal prescription. Composition leaves the LEFT third calm and
uncluttered for overlay text.

## F3. The 17 protocol page heroes — 17 images

Each protocol page (`/pages/{handle}`) opens with a tinted gradient and no
imagery. Generate one wide hero per protocol. **Size: 2000×900.
Filename: `onelife-protocol-{handle}-hero-2000.webp`.** Compose every image
with the LEFT 40% calm/negative space (text overlays sit left), subject
weighted right. Keep the SAME apothecary grade; vary only scene + accent tone.

| Handle | Scene prompt (after master block) | Accent tone |
|---|---|---|
| `sleep-ritual` | Bedside table at dusk: amber bottle (blank), small ceramic cup of chamomile tea, lavender sprigs, linen bedding softly blurred behind, one warm lamp glow. | dusty lavender |
| `stress-reset` | A woman exhaling with eyes closed in a sunlit armchair, cup of herbal tea in hands, ashwagandha root and amber bottle on the side table. | warm sage |
| `winter-immunity` | Kitchen counter winter scene: halved oranges, fresh ginger, raw honey jar, echinacea stems, amber bottle (blank), steam rising from a mug, cool window light warmed by interior glow. | citrus amber |
| `gut-reset` | Morning kitchen: glass of kefir, bowl of live-culture yoghurt with berries, fermented vegetables in a jar, amber probiotic bottle (blank), bright clean morning light. | soft apricot |
| `joint-care` | Active senior South African man stretching outdoors at sunrise post-walk, knee sleeve visible, water bottle beside; warm rim light. | warm terracotta |
| `daily-energy` | Morning launch scene: espresso cup, running shoes by the door, amber bottle (blank) on the hallway table, hard morning sun streaks across cream wall. | golden yellow |
| `brain-focus` | A calm study desk: open (blank-paged) notebook, fountain pen, omega-3 amber bottle, glass of water, rosemary sprig, soft window light, everything precise and ordered. | deep teal |
| `heart-health` | Heart-warm kitchen: salmon fillet on a board, walnuts, olive oil in glass cruet, amber omega bottle (blank), deep green linen, rich warm light. | deep rose |
| `womens-hormonal` | A woman journaling at a sunlit table with herbal tea, evening-primrose blooms in a small vase, amber bottle (blank); calm, self-possessed mood. | soft blush |
| `mens-vitality` | A grounded man early-40s tying running shoes on outdoor steps at dawn, amber bottle and water flask beside him, strong warm side light. | forest green |
| `weight-management` | Balanced meal-prep flat lay: grilled chicken, leafy greens, avocado, measuring tape coiled NEATLY as a design element (not moralising), protein shaker (blank), bright honest light. | fresh green |
| `kids-foundation` | Two South African kids at a breakfast counter taking chewable vitamins with a parent, orange juice, playful warm morning chaos, genuine laughter. | sunshine orange |
| `skin-beauty` | Vanity still life: collagen jar (blank), facial roller, protea bloom, glass of water with citrus, morning light through sheer curtain onto cream marble. | rose gold |
| `mood-lift` | A person opening curtains to bright morning light, back to camera, sun flooding a cream bedroom; St John's Wort yellow flowers and amber bottle on the sill. | warm gold |
| `healthy-ageing` | Dignified portrait-adjacent scene: silver-haired South African couple laughing over tea in a garden, amber bottles on the tray, fynbos in the background, honeyed light. | bronze |
| `liver-detox` | Clean reset scene: glass teapot of green tea, milk-thistle flowers, lemon water, dandelion greens, amber bottle (blank) on pale wood, airy bright light. | crisp green |
| `glp1-companion` | Supportive, non-judgemental scene: a woman preparing a high-protein breakfast (eggs, Greek yoghurt, protein shake — blank bottle), amber supplement bottles arranged beside a weekly pill organiser, confident calm morning light. | steel blue |

**Bonus (same spec):** `onelife-protocol-pcos-support-hero-2000.webp` — a woman
mid-20s preparing a balanced breakfast bowl with seeds and berries, inositol-style
powder jar (blank) beside, spearmint tea, calm encouraging morning light. Accent: soft mint.

## F4. Homepage dispensary band background — 1 image

`onelife-dispensary-band-bg-1600.webp` — 1600×900, then darkened 60% in use.
**Prompt:** Extreme close-up texture shot inside a dark apothecary: out-of-focus
amber jars on deep-green-stained wooden shelves, one shaft of warm light, almost
abstract; must read as a TEXTURE (it sits behind white text at 35% opacity).
Very low contrast, no bright highlights.

## F5. Article topic banners — 16 images (covers all 125 articles)

The blog's article pages are text walls. The theme snippet
`snippets/article-guide-cta.liquid` already maps every article to one of 16
topics by keyword — generate ONE banner per topic, reusable across all articles
of that topic. **Size: 1600×640. Filename: `onelife-article-topic-{topic}-1600.webp`**
with topic slugs: `magnesium, omega3, vitamind, ashwagandha, collagen, probiotics,
sleep, stress, immunity, gut, glp1, energy, joints, skin, hormones, general`.

**Prompt pattern:** [master block] + "Wide editorial banner, subject weighted to
the RIGHT half, LEFT half calm negative space over cream linen for headline
overlay" + the matching scene:
- `magnesium` — magnesium glycinate capsules spilling from amber bottle beside dark leafy greens, pumpkin seeds, dark chocolate shards.
- `omega3` — golden fish-oil softgels in a ceramic dish, raw salmon, walnuts, flax.
- `vitamind` — sunlight streaming onto a windowsill with a single amber bottle and citrus.
- `ashwagandha` — ashwagandha root and powder on espresso wood, mortar and pestle, steam from tea.
- `collagen` — collagen powder mid-pour into water, glass catching light, protea.
- `probiotics` — kefir, kimchi jar, yoghurt bowl, amber bottle, bright kitchen.
- `sleep` — dusk bedside: lavender, linen, warm lamp, amber bottle.
- `stress` — exhale moment: tea in cupped hands, sage green tones.
- `immunity` — ginger, citrus, echinacea, honey, steam.
- `gut` — fermented foods spread, glass jars, morning light.
- `glp1` — high-protein breakfast prep with pill organiser, steel-blue accents.
- `energy` — espresso, running shoes, hard morning sun.
- `joints` — senior stretching at sunrise, terracotta warmth.
- `skin` — vanity marble, collagen jar, facial roller, rose light.
- `hormones` — journaling with evening primrose, blush tones.
- `general` — the signature apothecary counter: brass scale, amber jars, botanical shadow.

Upload all 16 to **theme assets** of the staging theme. Claude will wire them
into the article template (do not edit `article-guide-cta.liquid` yourself —
reply in the PR when uploaded and Claude wires the hero into `main-article.liquid`
keyed off the existing topic map).

---

## Already covered — do NOT regenerate
Homepage hero slides (5, desktop+mobile), Vivid story page hero, About hero,
Practitioner hero, Brands hero, Quiz hero, Subscribe (unboxing) hero, Store
locator hero, 3 store-page heroes, 13 collection landers, consultation banner,
the 7 Klaviyo email heroes (Part A), the 20 article-specific heroes (Part C),
and the top-50 product-photo pilot (Part D).

## Upload mechanics recap
- Theme assets: `themeFilesUpsert` with base64 `body: { type: BASE64, value }`
  to theme `gid://shopify/OnlineStoreTheme/185971867958` — verify EVERY upload
  by re-querying the file's `checksumMd5` (a previous agent silently dropped
  6 of 9 uploads).
- Collection images (F1): `collectionUpdate` with `image: { src }` after staging
  the file via `stagedUploadsCreate`, or set manually in Admin.
- WebP exports: quality 80, no metadata. Keep every file under 350KB
  (mobile data costs are a real conversion factor in SA).
