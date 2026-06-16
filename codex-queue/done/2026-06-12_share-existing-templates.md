# Codex task: share your existing template library + June/July ads (DO THIS BEFORE the design-system build)

Naadir says you already have ~10 built templates (Monday Hero, Wednesday Vivid, Thursday Bundle designs) and produced June + July ads. Claude needs to see them to reconcile the T01–T12 library spec with what exists — extend, don't rebuild.

## Steps
1. Commit your existing template inventory to `creative/templates/existing/`:
   - One sample render per template (latest/best version)
   - `MANIFEST.md`: template name → purpose/day → sizes → variable slots (product, price, dates, theme) → anything parameterised
2. Commit the recent ad output to `creative/archive/2026-06/` and `creative/archive/2026-07/` (the Mon/Wed/Thu ads you produced for those months). If volume is large, the 12–20 most representative are enough.
3. Note in the manifest which templates already map to the T-numbers in `2026-06-12_design-system-templates.md` (e.g. yours = T02 Monday Hero) and which T-numbers have no existing equivalent (likely: T01 carousel, T05 proof, T06 poll story, T07 Hub recruit, T08 GBP, T09 email hero, T10 back-in-stock, T11 education card).
4. Push. Claude will then issue a reconciled v2 of the template spec: existing templates become standing immediately (Naadir has effectively already approved them by using them), new ones follow the sample-review gate.

Keep file sizes reasonable (JPG/PNG ≤500KB each is fine). No secrets/credentials in manifests.
