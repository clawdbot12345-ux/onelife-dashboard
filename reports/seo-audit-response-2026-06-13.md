# SEO Audit — Response to Codex Findings (2026-06-13)

## Live execution log (2026-06-13, owner-authorised "do it all")
Applied directly to the live store via the Admin API (owner client-credentials app):

- **9 dietary/certification collection pages** got proper SEO descriptions
  (Vegan, Vegetarian, Gluten Free, Sugar Free, Dairy Free, Keto, Organic,
  Halaal, Kosher) — high-intent category pages that were blank. ✓ verified.
- **109 placeholder product descriptions** ("contact us for more info") replaced
  with honest, varied, POPIA/SAHPRA-safe copy generated from real attributes
  (brand, format, dietary tags) + NAP/free-delivery + "check the label" note.
  0 errors. ✓ The store's worst indexed-thin-content liability is cleared.
- **Fresh full-catalog audit** saved: `reports/seo-audit-2026-06-13.{md,json}`.
- **Corrected my own PR #18**: the theme already emits Article + Product + FAQ
  JSON-LD (`seo-jsonld-article.liquid` / `seo-product-schema.liquid`), so the
  pipeline no longer duplicates Article schema and the auditor no longer
  false-flags "no_schema".
- **Review-request email** written (`content/email/review-request-precious.html`)
  to fill the missing review flow.

Blocked from here (need owner / Klaviyo UI): Klaviyo *write* MCP tools
(create template/flow) and the metrics API are gated on an approval the chat
"yes" doesn't satisfy. So: review-flow assembly, SMS sender registration,
signup-form (popup/embed) build, and the live signup/SMS numbers all need a
Klaviyo-UI / browser pass. The 168 collection images need real assets.

---


Mapping each item from the Codex site/SEO audit to what shipped on branch
`claude/seo-audit-findings`.

## 1. Blog SEO/content audit failing the newest articles ✅ FIXED (in-repo)
**Finding:** newest articles too short, missing product links/tables, FAQ,
references, schema/content blocks.

**Root cause:** the publish pipeline's `md_to_html` was minimal — it dropped
tables and emitted **no** structured data, FAQ, references or comparison table.
So even well-written articles shipped as thin HTML with no schema.

**Shipped — `scripts/publish_blog.py` (systemic, helps every future article):**
- Pipe-table support in `md_to_html` (tables now render instead of being dropped).
- `render_product_table()` — auto-builds an on-page **comparison table with
  internal product links** from the same `products:` frontmatter the email uses.
- `render_faq_section()` + **FAQPage JSON-LD** from a new `faq:` frontmatter key.
- `render_references()` — numbered, `rel="nofollow"` external **citations** from
  a new `references:` key (E-E-A-T for health content).
- `build_jsonld()` — **BlogPosting + BreadcrumbList (+ FAQPage)** structured data
  embedded in the article body (no theme change needed).
- `build_article_html()` assembles schema → prose → table → FAQ → references.

**Shipped — content:** added `faq:` (3 Q&As) + `references:` (3 sources each) to
all 7 queued articles + the published magnesium-sleep source. Sources are real
authoritative landing pages (NIH ODS fact sheets, Examine.com, SADAG, NICD) —
no fabricated study citations.

**Shipped — `scripts/seo_audit.py`:** `check_article` now also flags
`body_short` (<600 words), `no_internal_product_links`, `no_comparison_table`,
`no_schema`, `no_faq`, `no_references` — so the next audit verifies the fix and
catches regressions. Verified: enriched articles pass clean; thin articles flag.

> **Already-live articles:** re-running `publish_blog.py` on their source (or the
> next scheduled run for queued ones) re-publishes them with the new blocks. The
> newest queued articles will go out correct automatically.

## 2. GA4 join readiness weak at ~10% ✅ DIAGNOSTIC SHIPPED (rest is ops)
**Finding:** attribution backend works but GA4 join readiness ~10%; channel
reporting needs cleanup.

**Shipped — `scripts/weekly_business_report.py`:** new **"Attribution hygiene —
GA4 join readiness"** section + flag. Each week it computes the share of orders
carrying a UTM/click-id stamp that can be reconciled to a GA4 session vs the
direct/unknown/unclassified bucket, and raises a flag below 50%. This makes the
metric tracked and the cleanup verifiable week over week.

**Still ops (not code):** the actual lift comes from finishing the UTM cleanup in
`codex-attribution-cleanup.md` — Klaviyo account-wide auto-tagging (incl. flows),
Google Ads auto-tagging + GA4 link, Meta URL params. Those are platform-settings
tasks, not repo changes.

## 4. Add-to-cart alignment inconsistent ✅ FIXED LIVE
Root-caused and fixed on the live Shopify theme (current MAIN is **186060112182**,
not the old 186035765558). The "Frequently Added" block is the cart page's
`featured-collection` upsell; its `card-product` cards render the visible
**Add to cart** as `.ol-card-action` *inside* `.card__information`, which the
existing CSS left unpinned — so 2-line vs 3-line titles misaligned the buttons.

A `body.template-cart`-scoped rule (zero impact elsewhere) was appended to
`assets/onelife-grid-fixes.css` and **applied directly to the live theme** via
the Admin API (owner-supplied client-credentials app), verified live. Details +
exact CSS + one-line revert: `codex-theme-fixes-2026-06-13.md`.

## 3. Theme Check lint debt (email-signup-banner + header parser) ⏳ HANDOFF
Requires running `shopify theme check` (CLI), which isn't available in this
remote environment, so I haven't blind-edited working header/banner Liquid.
Codex flagged these as *old, unrelated* lint debt that *passed browser
verification* — i.e. hygiene, not a live regression. The offense-by-offense
checklist (UnusedAssign, parser-blocking script → add `defer`, deprecated
`img_url`, etc.) is in `codex-theme-fixes-2026-06-13.md` for a CLI pass.
