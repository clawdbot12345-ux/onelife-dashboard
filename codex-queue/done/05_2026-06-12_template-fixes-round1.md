# Codex task: TEMPLATE FIXES from creative-director QA (before Naadir's final sign-off)

QA of `creative/templates/existing/` vs the references in `creative/templates/reference/`: **right direction — structure, packshots, and price math (R170.77→R153.69 = exactly 10% ✓) are good.** Four fixes required across the family, then re-commit the same three samples:

1. **Layout collisions (T03, T04 — blocking):** text overlaps packshots on T03 ("SA m…", "your ro…" cut off; price table clipped); CTA bar is half-hidden behind elements on BOTH T03 and T04. Nothing may overlap the CTA bar, bullets, or price table — reflow product cluster right/smaller or text column narrower.
2. **Icon roundels:** one roundel renders an empty missing-glyph box (T02 "daily support", T03/T04 same). Use real drawn icons (leaf, shield, moon, capsule…) like the references — never font glyphs.
3. **Background depth:** flat vector leaf-blob backgrounds don't match the references' photographic cinematic botanic depth (bokeh, golden rim light, shallow DOF). Replace the background layer with image-model-rendered botanical environments per the references; keep the text/layout layer as-is. Ground products with real shadows (no white blob under T02's tub).
4. **COMPLIANCE FAIL (T04 — blocking):** the Black Seed Oil "7X HIGHER THYMOQUINONE for Enhanced Relief & Support / 60 DAYS SUPPLY" badge is fabricated marketing copy — comparative potency + "relief" claims we never wrote. Remove it. Only copy from Claude's briefs goes on ads, ever. If the real product label carries such text, the label may show, but no invented badges.

Re-render T02/T03/T04 samples with these fixes → commit to the same paths → Claude re-QAs → Naadir gives final sign-off (`approvals/granted/designs.flag`). The carousel re-renders (T01) follow the same background-depth standard.
