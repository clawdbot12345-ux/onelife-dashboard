# Vivid Health — 10/10 Design Direction (for Codex)
**2026-07-02 · Companion to `codex-vivid-handoff-2026-07-02.md`.** Claude owns theme code; **Codex owns imagery + admin-side design assets.** This is the complete art direction: regenerate to this spec and nothing else. Current design audit scores per page are in the PR (overall ~7/10); this document is the path to 10.

---

## 1. The one design law

**Vivid's premium is restraint + proof.** The reference point is the profitable middle of the world-class spectrum (Ritual / Wild Nutrition / Aesop-grade discipline — see `reports/vivid-worldclass-teardowns-2026-07-02.md`): calm surfaces, exact numbers, no discount-red, no urgency theatre, no emoji. Every asset must look like it was made by the same hand on the same day. When in doubt: quieter, warmer, more specific.

## 2. Locked brand tokens (verified rendering live — do not drift)

| Token | Value | Use |
|---|---|---|
| Paper | `#FBF7EE` | Page background |
| Bone | `#F4EEE2` | Cards, alt bands |
| Cream | `#EEE5D2` | Deep bands |
| Ink | `#0E1A14` | Text, dark bands |
| Forest | `#1F3D2E` | Primary brand, CTAs |
| Forest deep | `#142A1E` | Hover, footer |
| Moss | `#466B4F` | Accents, eyebrows |
| Sage | `#A8B89B` | Soft accents |
| Clay | `#C3704B` | The single warm accent — sparingly |
| Type | **Fraunces** (display) + **Inter** (UI/body) | Never a third face |

Imagery palette must live inside this world: warm paper/stone neutrals, deep botanical greens, one clay-warm note. **Never**: pure white studio sweeps, cold blue light, red, neon, glossy plastic feel.

## 3. The imagery system (Codex regenerates to this spec)

**Global art direction:** natural South African warmth — travertine/sandstone plinths, raw linen, indigenous botanicals (buchu, rooibos sprigs, aloe, cancer bush where visually apt), directional late-afternoon Highveld light with soft long shadows, shallow depth of field. Consistent camera height per shot type. Matte, tactile, editorial — closer to a cookbook than a pharmacy.

**Technical spec for every asset:** master at 2048px long edge · export WebP ≤ 250KB (plus a 720px card size ≤ 80KB) · consistent 3:4 for PDP gallery, 1:1 for cards, 16:9 (2400×1350) for heroes/banners · filenames `vivid-{handle}-{shot}.webp` (e.g. `vivid-buffered-c-90-label.webp`) — no `IMG_xxxx`. Bottle label must always be tack-sharp and legible.

### 3.1 Product gallery — 5 shots per SKU, same order storewide (58 SKUs)
1. **Front hero** — bottle centred on travertine, paper backdrop, 3:4. The existing generated series is close; keep its look but fix §3.4 label issues.
2. **Label panel macro** — straight-on, fills frame, every milligram readable. *This is the brand thesis in one image and currently doesn't exist for any SKU.* Highest priority shot in this entire document.
3. **Texture** — open bottle / capsules or powder spilling on stone, macro, shallow DOF.
4. **In-hand lifestyle** — diverse SA hands, natural light kitchen/bathroom context, bottle label toward camera.
5. **Scale + pairing** — bottle beside its natural stack partner(s) and a everyday object for size.

### 3.2 Zero-image emergencies (blank today — do these first)
- **The 3 bundle/stack products** (Comrades Recovery, Perimenopause Essentials, Highveld Hay-fever): group compositions — 3 bottles stepped on stone, one prop telling the story (running shoes' toe / linen + sage / fynbos sprig). 1:1 + 3:4.
- **Cart-drawer thumbnails render blank** — Claude's code fix, but verify each product's featured image is square-cropped sensibly after regeneration.

### 3.3 Site furniture set
- Homepage hero (16:9 desktop + 4:5 mobile crop-safe): full range lineup, dawn light — an evolution of the current hero, same composition language.
- 6 collection/goal banners (Immunity, Gut, Sleep & Stress, Body, Women, Nourishment): one botanical macro each on the range's undertone.
- Quiz, consultation, sourcing, about, journal headers (16:9): sourcing = raw ingredients + supplier paperwork on a workbench; about = the Centurion team/counter if a real photo exists — **one real human photo is worth three generated ones here**.
- Journal article headers for the 3 queued posts (winter immune / sleep decision tree / read-a-label): still-life matching each topic, same series style.
- Email/OG share image 1200×628.

### 3.4 Label artwork corrections (before any re-render)
1. **"ANGUS CASTUS" → "AGNUS CASTUS"** on the bottle art (product title is already fixed; the art still carries the typo).
2. **"DIETARY SUPPLEMENT" → "HEALTH SUPPLEMENT"** (US wording → SA-appropriate) across all label renders.
3. Keep the existing label design system exactly (white jar, colour-coded range band, VIVID HEALTH wordmark) — these two text fixes only.

### 3.5 Generation prompt template (adapt per shot)
> "Premium supplement product photography, [SHOT TYPE] of a white supplement jar with [RANGE COLOUR] label reading 'VIVID HEALTH — [PRODUCT]', on warm travertine stone against a soft paper-cream background (#FBF7EE), indigenous South African botanicals ([BOTANICAL]) softly out of focus, directional warm late-afternoon light, long soft shadows, shallow depth of field, matte editorial style, muted deep-green and warm-neutral palette, photorealistic, no text overlays, no watermarks, label text sharp and legible"

Negative/avoid: clinical white sweep, blue tint, red, gloss, lens flare, fake bokeh discs, extra fingers, garbled label text (re-roll until label text is clean or comp the real label art over the render).

## 4. Page-level 10/10 bar (who fixes what)

| Surface | To 10/10 | Owner |
|---|---|---|
| Homepage | New hero + bundle imagery (§3.2/3.3); announcement bar filled ("Free delivery over R400 · 30-day money-back"); LQIP blur fixed with 720px card sizes | Codex imagery · Claude code |
| Collection | Goal banners; sold-out cards dimmed with "Notify me"; utility cards moved below product row on mobile | Codex imagery · Claude code |
| PDP | 5-shot gallery live (esp. label macro); truncated junk bullet removed; "sa made" → "SA-made"; installment line once Payflex lands | Codex imagery · Claude code |
| Quiz | Header image; logic already replaced by published theme — verify | Codex imagery · Claude verify |
| Sourcing/About/Approach | Headers + one real team photo; approach page gets 2 stills so it isn't a text wall | Codex |
| Search | Branded grid restyle (code) | Claude |
| Cart | Thumbnails + "R120 from free delivery" nudge styling | Claude |
| Journal | 3 article headers + ongoing 1/week to match publisher cadence | Codex |
| 404 | Keep — copy is already 10/10 ("That bottle isn't on this shelf") | — |

## 5. Design QA gate (run before calling anything done)

1. Every image passes the squint test: same series, same light, same world?
2. Label legible at 720px card size?
3. Zero emoji, zero red, zero countdowns, max two typefaces anywhere?
4. Mobile: nothing overlaps the hero CTAs (FAB stack currently does — Claude fixing); no page over ~12,000px.
5. File hygiene: WebP, ≤250KB masters, `vivid-*` names.
6. The wordmark, label band colour and site accent for a range all match.

**Delivery:** upload via Shopify admin (Files + product media, replacing — not appending — old renders), or commit to `vivid/assets/store/` on the PR branch and Claude pushes them through the pipeline. Post progress on PR #26.
