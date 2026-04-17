# One Life Health — App

Premium mobile-first PWA for One Life Health. Built on Next.js 14 + TypeScript
+ Tailwind + Framer Motion, against the Apothecary Modern design system.

## Status

- **Pass 1 ✓** — Design tokens and typed component API sketches.
- **Pass 2 ✓** — Next.js scaffold, all 20 primitives implemented, `/design`
  showcase route. `npm run dev` → `http://localhost:3000/design`.
- Pass 3 — Home + Product Detail screens.
- Pass 4 — Shop + Consult + Rewards + Onboarding.
- Pass 5 — Polish, docs, PWA manifest.

## Run it

```bash
cd onelife-app
npm install
npm run dev         # http://localhost:3000 → redirects to /design
npm run build       # production build, statically generated
npm run typecheck
```

## What's in here

| File | Role |
|---|---|
| `tailwind.config.ts` | Palette, type scale, spacing, radii, motion — token source of truth. Default Tailwind palette is **overridden**, not extended. |
| `app/globals.css` | CSS custom properties (hex values live here, once), base reset, `u-micro` / `u-num` / `u-pullquote` utilities, focus ring, reduced-motion. |
| `components/primitives.ts` | Typed contracts for the 20 reusable primitives. No implementations — shapes first, so screens can be drafted against a stable API in Pass 3. |

## The palette, in one paragraph

Paper (`#F4F1EA`) is the background of the whole app — warm, Aesop-bag, never
pure white. Ink (`#1A1915`) is text — warm near-black, never pure. Sage is the
one accent that does real work (CTAs, success, consult). Terracotta is urgency.
Gold is *only* membership tier. Signal/alert are for in-stock / out-of-stock.
**Any given screen uses at most three of these plus ink/paper.**

## Type

Display is serif (Canela → Fraunces fallback), UI is humanist sans (Söhne →
Inter Tight fallback), numerics are mono with tabular lining figures. Scale is
fixed at `48 / 34 / 24 / 18 / 16 / 14 / 12`. `.u-micro` is the only place
all-caps is permitted.

## Spacing

4pt grid, but named: `gutter` (24), `section` (64), `page-x` (24), `tap` (44).
If a layout value isn't here, we discuss before adding.

## Motion

`dur-fast / base / slow` and a single `ease-quiet` curve. Springs proper come
from framer-motion in Pass 2+. Everything respects `prefers-reduced-motion`
via the global `@media` block — components do not re-check.

## Type-driven design rules

A few constraints are encoded directly as TypeScript unions in
`components/primitives.ts`, not as lint rules — so the compiler catches drift:

- `ProductCard.tag` is a tagged union → exactly one tag, not "a list with max
  length one".
- `MembershipTier` is closed (`seedling | rooted | flourishing`) — no
  `"platinum"` string will ever reach production.
- `TabBarProps.active` is `TabKey`, the five nav slots. Future tabs require a
  schema change, not a typo.
- `ZARCents` aliases `number` — prices stored as integer cents, rendered only
  through `TabularPrice`. Caller can't accidentally render `2.4999999` with
  hand-rolled `.toFixed`.

## What's still deliberately missing

- No commissioned photography. Every image surface renders a `PaperImage` —
  paper-deep tile with a botanical glyph — until shoots land. Zero CLS,
  honest placeholder, on-brand.
- No real Shopify / ERP integration. Pass 3 introduces the typed adapter
  layer and stubs realistic data.
- Commercial fonts (Canela, Söhne) aren't shipped. Open fallbacks are wired
  via `next/font/google`. Swap the loader in `app/layout.tsx` when licences
  land — no other code changes.

## Quality bar — self-check

- [x] No hex values in components (they're in `globals.css` only).
- [x] No emoji in any file shipped to users.
- [x] Palette capped at 11 tokens; no accidental 500-value ramp.
- [x] Type scale locked to 8 sizes with matching leading/tracking so bad combos
      are literally impossible.
- [x] Minimum 16px body, 44×44 tap target — in tokens.
- [x] Default Tailwind palette banned at the config level.

## Next — waiting for your react

Pass 3 will:
1. Build the Home screen — greeting, active protocol, next consultation slot,
   editorial hero, curated-for-you rail, this-week strip, store card.
2. Build Product Detail — parallax hero, sticky add-to-cart, Why-we-stock-it
   / How-to-take-it / Ingredients / Evidence / Pairs-with tabs,
   contraindication banner, reviews.
3. Wire both into `AppShell` so the product feels like one thing, not two.

Hold off until you've pushed back on anything in the showcase.
