# Onelife Content & Email Playbook

## Weekly cycle

### Monday 07:00 SAST — Publishing day
1. Check memory (`/blog_history/`, `/campaign_performance/`, `/insights/`)
2. Read the Onelife blog archive at onelife.co.za/blogs/health-wellness-hub.atom
3. Read Klaviyo recent campaigns (last 30 days) — DO NOT duplicate
4. Pick next blog from `content/blogs/` (unpublished, alphabetical)
5. Verify all product links are live (curl the URLs, expect 200)
6. Run `python scripts/publish_blog.py <file>`
7. The output gives you a Shopify article URL + Klaviyo template/campaign IDs
8. Rename the source file from `foo.md` to `foo.published.md` and commit

### Monday 08:30 SAST — Reporting day
1. Run `python scripts/weekly_report.py`
2. Read the generated `reports/weekly-YYYY-MM-DD.md`
3. Compare to last week's report (from memory)
4. Write key insights to `/insights/YYYY-MM-DD.md` in memory

## Content calendar strategy

### 4-pillar rotation
Rotate through these four pillars to avoid topic fatigue:
1. **Metabolic Health** — berberine, blood sugar, weight management (but check: they already have blood-sugar blog that mentions berberine)
2. **Women's Hormonal Health** — PCOS, inositol, menopause, collagen (their strongest vertical — PCOSITOL is their #1 product)
3. **Winter Immunity & Gut** — probiotics, postbiotics, Vit C/D/Zinc, elderberry
4. **Sleep & Stress** — magnesium glycinate, adaptogens, ashwagandha

### What works (based on performance data)
- ⭐ NAD+ & NMN Guide: 35% open, 1.69% click, **R1,770 revenue** (winner)
- ⭐ EDN Bundles Campaign: 30.8% open, **R1,250 revenue** (bundle offers work)
- ⭐ 21 Days Blog Digest: 42.6% open, **R916 revenue**

Common pattern in winners: clear product tie-in with SPECIFIC recommendations.

### What doesn't work (zero revenue despite 200+ recipients)
- ❌ Generic "5 Vitamins for Autumn" blogs
- ❌ Informational topics with no clear buyer intent (Hay Fever)
- ❌ Loss-leader bundle emails with tiny discount (0.14% click rate)
- ❌ Blogs where the email CTA sends to the blog page and the blog page has no strong product modules

### Rule: every blog must drive to buying intent
- 2-3 featured products minimum
- Every product link uses UTM params (see utm_schema.md)
- Product links go directly to product pages, not collections, not blogs

## Flow management

### Existing live flows (DO NOT modify without approval)
- Welcome — One Life Health (Full Sequence)
- PCOS Welcome Flow
- PCOS Post-Purchase Flow
- Post-Purchase Thank You + Cross-sell v3
- GLP-1 Education Drip
- GLP-1 Non-Opener Follow-Up
- Win-Back 60 Days v2
- Browse Abandonment v2
- Abandoned Checkout Reminder
- Points Balance Nudge v3

### Flow gap (can be built)
- **Replenishment Reminder** — 3 emails at 21/50/80 days after Placed Order.
  Templates already exist in Klaviyo: YbTW5R, XySTte, Tm25PD
  The human needs to wire this in the Klaviyo UI once (flow builder).

## Segments (pulled from Klaviyo)

- Email List — 757 profiles (main list)
- Win-Back Opportunities (Shopify) — 1,922 profiles (biggest recoverable)
- Engaged (90 Days) — 516
- Engaged (60 Days) — 516
- Engaged (30 Days) — 473
- Repeat Buyers (Shopify) — 392
- Potential Purchasers (Shopify) — 120
- Churn Risks (Shopify) — 53
- VIP Customers (Shopify) — 36
- New Subscribers — 19
- PCOS Interest list — exists but 0 counted (Klaviyo counts slow to update)

## Red lines — never do these

1. Never send campaigns automatically. Always draft and wait for human review.
2. Never publish Shopify blog posts as "published" — always as draft.
3. Never modify existing live flows.
4. Never use fabricated product data. Always verify against the live onelife.co.za catalog.
5. Never send 2+ campaigns in one day to the same segment.
6. Never duplicate topics already covered in the last 90 days of their blog archive.
