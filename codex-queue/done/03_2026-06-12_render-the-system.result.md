# Render-the-system result

Executed `codex-queue/03_2026-06-12_render-the-system.md` using the decided One Life Hybrid direction. No approval round-trip was requested.

## Completed outputs

1. Symptom Saturday carousels x2
   - `creative/franchises/symptom-saturday/tired-by-2pm/`
   - `creative/franchises/symptom-saturday/winter-sleep/`
   - Each has 6 slides, `caption.txt`, `manifest.json`, and `contact-sheet.jpg`.

2. THE HONEST LABEL identity + episode 1
   - `creative/franchises/the-honest-label/identity-card.jpg`
   - `creative/franchises/the-honest-label/ep-01-collagen/`
   - Episode has 6 slides and a contact sheet.
   - Manifest copy check passed: slide copy matches the brief verbatim.

3. MADE BY US identity card + story template
   - `creative/franchises/made-by-us/made-by-us-identity-card.jpg`
   - `creative/franchises/made-by-us/made-by-us-story-template.jpg`

4. STACK OF THE WEEK data card
   - `creative/franchises/stack-of-the-week/stack-of-the-week-data-card-template.jpg`
   - Includes real-numbers stat slots and a 3-product stack slot.

5. ASK ONE LIFE answer card
   - `creative/franchises/ask-one-life/ask-one-life-answer-card-template.jpg`
   - Includes question quote, staff answer, and real-photo frame slots.

6. Hub-only deal bespoke ad template
   - `creative/franchises/hub-exclusive/hub-exclusive-deal-template-square.jpg`
   - `creative/franchises/hub-exclusive/hub-exclusive-deal-template-story.jpg`
   - Includes `HUB EXCLUSIVE` ribbon and `HUB10` code slot.

## Renderer

- Added `scripts/render_franchise_system.py`.
- Added public Shopify PrimeSelf Magnesium packshot assets for the sleep carousel proof slide:
  - `creative/templates/_assets/shopify-packshots/primeself-magnesium-source.webp`
  - `creative/templates/_assets/shopify-packshots/primeself-magnesium-cutout.png`
  - Updated `creative/templates/_assets/shopify-packshots/manifest.json`.

## Commits pushed

- `772ef28` Render Symptom Saturday franchise carousels
- `323a0ab` Render Honest Label franchise episode
- `f720da9` Render Made By Us franchise templates
- `332127d` Render Stack of the Week data card
- `076aebe` Render Ask One Life answer card
- `34323e9` Render Hub exclusive deal templates
