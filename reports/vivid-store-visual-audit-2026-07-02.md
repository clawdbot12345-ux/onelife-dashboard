# Vivid Health D2C Store — Visual & Commerce Audit
**Store:** https://hgywg0-w7.myshopify.com · Audited 2026-07-02 (Playwright, 1440×900 + 390×844) against the then-published theme "Vivid Health D2C Visual Fix 2026-06-04".

> **Status note (same day):** the "Best in Class (working draft 2026-06-06)" theme has since been **published**, which resolved several P0s below: Journal 404s (blog templates now exist), the empty `/pages/our-sourcing` (supplier cards now render), missing 404 page, single-image PDP galleries (now 5 thumbs), Subscribe & Save (buy box + `selling_plan` support now live), and the quiz logic (new 13.7KB version). Catalog fixes also applied: Agnus Castus title, 12 size-qualified duplicate titles. **Still open:** robots.txt serves empty, back-in-stock form not rendering on OOS PDPs, default search template, empty announcement bar, cart-drawer blank thumbnails, no reviews, no installment messaging, 16/58 products OOS, label-art issues. See `codex-vivid-handoff-2026-07-02.md` + `codex-vivid-design-direction.md` for ownership.

## 1. Brand system (verified rendering)

- **Palette (live `:root`):** paper `#FBF7EE` · bone `#F4EEE2` · cream `#EEE5D2` · ink `#0E1A14` · forest `#1F3D2E` · forest-deep `#142A1E` · moss `#466B4F` · sage `#A8B89B` · clay `#C3704B`. Applied consistently everywhere — genuinely cohesive.
- **Fonts:** Fraunces (display) + Inter (body), confirmed loaded, no fallback flashes.
- **Imagery:** AI-generated product photography, consistently art-directed (stone plinths, botanicals, warm light). Two blemishes: labels read "DIETARY SUPPLEMENT" (US wording) and the Agnus Castus bottle art says "ANGUS CASTUS" (typo baked into artwork).
- No genuine console errors.

## 2. Per-page (as audited, pre-theme-publish)

- **Homepage — 8/10 desktop, 6.5/10 mobile.** Strong hero/stat band/trust ticks/bundles/goal grid/founder band. Issues: empty announcement bar strip site-wide; LQIP blur on card heroes; all sections gated behind JS reveal animations; mobile FABs overlap hero CTAs; sticky CTA duplicates hero buttons; ~16.5k px long; the 3 homepage stack products have **zero images in Shopify**.
- **Collection /all-formulations — 7.5/10.** Good filters/sort/badges/pagination. Issues: 3 utility cards push first product ~1,400px down on mobile; sold-out items not de-prioritised; badge stacking.
- **PDPs — 7/10.** Exemplary VAT labelling ("R 301.88 incl. VAT"), strong tabs/copy/cross-sell/sticky ATC. Issues at audit time: no subscription UI (now fixed); 1-image gallery (now fixed); truncated junk bullet under ATC; **no review stars**; **no installment messaging**; disabled dead "Notify me when back" buttons; "sa made" typo; hero SKU Buffered C · 300 sold out — **16 of 58 products (28%) OOS**.
- **Quiz — 7/10 visual, 4/10 logic** (logic since replaced by the published theme — re-verify).
- **/pages/our-sourcing — was 1/10 (empty)** → now renders supplier cards after theme publish.
- **/pages/our-approach — 9/10.** Best copy on the site; needs 1–2 images.
- **/pages/about — 6/10.** Thin; no h1; the "Since 1996" heritage story missing.
- **/pages/compare-vivid — 8.5/10.** Minor typos ("Vivids approach", "you dont").
- **Cart — 7/10.** Drawer + free-shipping progress bar work; blank line-item thumbnails; no threshold cross-sell; `/cart` manual update.
- **Search — 2/10.** Function is good (description-level matches); template is raw default Shopify: unstyled input, `<ol>` list, no prices/ATC/brand.
- **Footer/links:** excellent footer; all header/footer links 200 except `/blogs/journal` (404 at audit time — fixed by theme publish).
- **Floating chat widget:** canned keyword bot presenting as live chat — label it as automated.

## 3. Ranked punch-list (status-annotated)

**P0**
1. ~~Empty our-sourcing page~~ ✅ theme publish
2. ~~Journal 404s~~ ✅ theme publish
3. Search template default Shopify — **open (Claude, code)**
4. ~~Subscribe & Save unsellable~~ ✅ theme publish (verify checkout end-to-end)
5. Back-in-stock: form exists in new theme but not rendering on OOS PDPs — **open (Claude, code)**; inventory decision on 28% OOS — **owner/Codex**

**P1**
6. No reviews anywhere — **Codex: install Judge.me**
7. No installment messaging — **Codex: install Payflex/PayJustNow → Claude adds PDP line**
8. ~~1-image galleries~~ ✅ — but label-panel macro shot still missing catalog-wide (**Codex imagery**)
9. Truncated junk bullet + "sa made" — **open (Claude)**
10. Empty announcement bar — **open (Claude)**
11. Cart drawer blank thumbnails + threshold cross-sell — **open (Claude)**
12. ~~Quiz logic~~ ✅ new theme — re-verify

**P2**
13. ~~Agnus Castus title~~ ✅ · label ART still says ANGUS CASTUS (**Codex**)
14. Mobile FAB overlap, sticky CTA duplication, page lengths — **open (Claude)**
15. ~~Bundle products no images~~ — **Codex imagery (§3.2 of design direction)**
16. About h1 + heritage content — **open (Claude copy + Codex imagery)**
17. "DIETARY SUPPLEMENT" label wording — **Codex**
18. Label the chat widget as automated — **open (Claude)**
19. LQIP/srcset sizes — **open (Claude)** + 720px exports (**Codex**)

## 4. Scorecard (at audit time)

Home 8 · Collection 7.5 · PDP 7 · Quiz 7 · Our approach 9 · Compare 8.5 · About 6 · Cart 7 · Our sourcing 1→fixed · Search 2. **Overall ~7/10** — premium visual system and copy; commerce depth and two broken surfaces dragged it down (roughly half resolved by the theme publish the same day).

*Screenshots: session scratchpad `vivid-store-audit/` (32 PNGs + results.json).*
