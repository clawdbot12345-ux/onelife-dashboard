# One Life Health — App

Pass 1 deliverable: design system tokens + typed component API sketches.
This is **not** a running app yet. Pass 2 wires up Next.js and the `/design`
showcase route; passes 3–5 build the six hero screens, then polish.

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

## What's deliberately missing

- No package.json / lockfile yet — avoids committing dep choices that review
  might change (react 18 vs 19, tailwind 3 vs 4).
- No components/\*.tsx implementations — Pass 2.
- No `/design` route — Pass 2.
- No icons, no fonts, no images — those come with the showcase route where we
  can see them in context.

## Quality bar — self-check

- [x] No hex values in components (they're in `globals.css` only).
- [x] No emoji in any file shipped to users.
- [x] Palette capped at 11 tokens; no accidental 500-value ramp.
- [x] Type scale locked to 8 sizes with matching leading/tracking so bad combos
      are literally impossible.
- [x] Minimum 16px body, 44×44 tap target — in tokens.
- [x] Default Tailwind palette banned at the config level.

## Next — waiting for your react

Pass 2 will:
1. Add `package.json`, `next.config.js`, `tsconfig.json`.
2. Implement the 20 primitives against the contracts above.
3. Ship `/design` — a Storybook-style showcase route with every token,
   component, and state visible on one page.

Hold off on the showcase until you've pushed back on anything in this pass.
