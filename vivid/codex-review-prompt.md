# Codex prompt — Review and fix the Vivid Health prototype

## Setup

```bash
git clone https://github.com/clawdbot12345-ux/onelife-dashboard.git
cd onelife-dashboard
git checkout claude/vivid-health-shopify-redesign-KITNn
```

The prototype is at `vivid/index.html` (~242KB single-file HTML/CSS/JS).
Product images: `vivid/assets/products/generated/` (260 files).
Banner images: `vivid/assets/banners/` (15 files).

## Task: Full QA review and fix

### 1. Image audit
- Verify every image path in the JS (HEROES mapping, BUNDLES, JOURNAL hero fields) resolves to an actual file on disk
- Check for any broken `src` attributes or paths that 404
- Report: X/Y images verified, list any failures

### 2. Mobile responsiveness (test at 375px, 768px, 1024px, 1440px)
- Open the file in a browser or use a headless browser
- Check: hero section fits viewport without horizontal scroll
- Check: product cards render in proper grid (1-col at 375, 2-col at 768, 3-col at 1024, 4-col at 1440)
- Check: hamburger menu appears below 1000px
- Check: sticky add-to-cart appears on mobile PDP
- Check: no horizontal overflow on any section
- Fix any overflow or layout issues found

### 3. JavaScript audit
- Check all functions are called and none are dead code
- Check all event handlers (onclick, onchange, onsubmit, onkeydown) reference existing functions
- Check the router handles all defined routes
- Check cart add/remove/update logic for edge cases
- Check search overlay filtering logic
- Check quiz flow for all possible answer combinations
- Fix any bugs found

### 4. CSS audit
- Check for orphaned selectors (classes defined in CSS but never used in HTML/JS)
- Check for duplicate/conflicting rules
- Check z-index stacking (nav, scrim, drawer, chat, FABs, search overlay)
- Check all @media breakpoints are in ascending order and don't conflict
- Verify design tokens (--bone, --paper, --forest, etc.) are used consistently
- Fix any issues found

### 5. Accessibility
- Every img needs an alt attribute
- Every button needs an aria-label
- Focus states on all interactive elements
- Color contrast ratio ≥ 4.5:1 for body text, ≥ 3:1 for large text
- Skip link works
- Fix any failures

### 6. Performance
- Flag any images over 500KB that should be compressed
- Check for render-blocking resources
- Suggest lazy-loading for below-fold images (most should already have loading="lazy")

### 7. Content accuracy
- Product count should be 52 everywhere (not 55)
- WhatsApp number should be 27713744910 everywhere
- No placeholder text (TODO, lorem ipsum, 27000000000)
- All footer links should resolve to working routes

## Output

After fixing all issues:
1. Commit with descriptive message
2. Push to the branch
3. Report: total issues found, total fixed, any that couldn't be fixed and why

Do NOT refactor the architecture or redesign anything. Only fix bugs, broken references, and consistency issues.
