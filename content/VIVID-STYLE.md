# The Vivid Journal — house style (used by humans AND the vivid-article-writer workflow)

Voice: **the formulator**, not the shop assistant. Vivid Health is the SA brand
that puts exact milligrams on the label and shows its sourcing. The Journal
reads like a formulator explaining their decisions: evidence-led, calm,
specific numbers, zero hype. Where One Life's Apothecary voice is Precious
behind the counter, Vivid's voice is the person who chose the dose.

Rules (violations are bugs):
- **SAHPRA low-risk wording only**: supplements "support / assist / help /
  maintain". Never "treat", "cure", "prevent" a disease. No medical claims.
- **Exact doses always**: never "high strength" without the number. If a
  studied dose differs from ours, say so — honesty IS the brand.
- **Cite forms**: "magnesium glycinate", "calcium ascorbate", "KSM-66
  ashwagandha root extract, 5% withanolides" — the form is the story.
- **One honest limitation per article**: what the ingredient won't do, who
  shouldn't bother, or when to see a professional. Non-negotiable.
- SA context: winter is June–August, ZAR prices incl. VAT, Centurion
  manufacturing, Southern-African sourcing where true.
- Store facts: free delivery over R400 · 30-day money-back · WhatsApp
  consultation · the quiz at /pages/quiz · curated stacks save 10%.
- Internal links: link the matching /pages/ingredients-* and
  /pages/conditions-* pages where they exist, and 2–4 live products.
- **PRODUCTS MUST BE REAL AND IN STOCK on hgywg0-w7.myshopify.com** — verify
  against the live store before queueing; never invent a handle or price.
- No competitor naming. No "Precious" persona — that's the One Life voice.
- Sign-off: "— The Vivid formulation desk".

Structure per article (700–1,000 words):
1. A formulation decision or a number as the hook (2–3 sentences).
2. The mechanism in plain language (why the thing happens).
3. What the evidence actually supports — with doses.
4. The honest limitation paragraph.
5. Close: matching product(s)/stack, soft CTA to the quiz or a WhatsApp consult.

Frontmatter must match scripts/vivid_publish_blog.py exactly:
```
---
title: ...
slug: kebab-case-url
excerpt: one sentence, ≤160 chars
tags: comma, separated, tags
products:
  - handle: live-product-handle
    name: Product Name
    price: R123
---
```
Queue: `content/vivid-queue/YYYY-MM-slug.md` → published weekly (oldest
first) by `.github/workflows/vivid-blog-publish.yml` to the **Journal** blog
on hgywg0-w7.myshopify.com, then moved to `content/vivid-published/`.
