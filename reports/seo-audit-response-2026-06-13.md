# SEO Audit — Response to Codex Findings (2026-06-13)

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

## 3. Theme Check lint debt (email-signup-banner + header parser) ⏳ HANDOFF
## 4. Add-to-cart alignment inconsistent ⏳ HANDOFF
**Both live in the Shopify theme (186035765558), which is not in this repo.**
Precise, apply-ready fixes (exact CSS for the equal-height/bottom-pinned CTA, and
the Theme Check offense-by-offense checklist) are in
`codex-theme-fixes-2026-06-13.md`. Editing the live production theme needs owner
sign-off + browser verification, so it's staged as a brief rather than applied
blind from here.
