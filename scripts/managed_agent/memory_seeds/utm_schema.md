# UTM Parameter Schema

Every outbound link in every Onelife email must follow this UTM schema
exactly. Analyzify + GA4 use these to attribute sessions and revenue.

## Schema

```
?utm_source=klaviyo
&utm_medium=email
&utm_campaign=<slug-from-frontmatter>
&utm_content=<position-identifier>
```

## utm_content values

| Value | When to use |
|---|---|
| `blog-cta` | The main "Read the full guide →" button |
| `product-1`, `product-2`, `product-3` | Product module links (1-indexed) |
| `shop-collection` | The bottom "Shop [category]" link |
| `store-locator` | Any link to the physical store locator |

## Examples

```
https://onelife.co.za/blogs/health-wellness-hub/berberine-natures-ozempic
  ?utm_source=klaviyo
  &utm_medium=email
  &utm_campaign=berberine-natures-ozempic
  &utm_content=blog-cta
```

```
https://onelife.co.za/collections/brand-willow/products/willow-magnesium-glycinate-120-capsules
  ?utm_source=klaviyo
  &utm_medium=email
  &utm_campaign=magnesium-glycinate-vs-citrate-vs-orotate-south-africa
  &utm_content=product-1
```

## Where to see the data

- **Google Analytics 4** → Acquisition → Traffic Acquisition → filter by `source: klaviyo`
- **Analyzify dashboard** → Campaign Performance (filtered by email medium)
- **Klaviyo** → Campaign metrics (shows clicks + conversions natively)

## Do NOT

- Use `utm_source=email` (should be `klaviyo`)
- Use `utm_medium=campaign` (should be `email`)
- Use `&` before the first param (should be `?` or `&` depending on URL)
- Skip utm_content (breaks per-link attribution)
