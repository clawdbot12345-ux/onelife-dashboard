# /lint — Monthly Vault Audit

Audit the vault for structural issues, stale data, and inconsistencies.

## When to use

Run monthly, or before a major reporting cycle.

## Checks

### 1. Structural integrity
- Every `.md` file in Knowledge/ folders has valid YAML frontmatter
- Every file has at least one `[[wikilink]]` to another page (no orphans)
- Every wikilink target exists (no broken links)
- Every Knowledge subfolder has a MANIFEST.md

### 2. Freshness
- Flag any page where `updated:` is older than 45 days as `status: stale`
- Flag any signal page older than 30 days — signals should be resolved or escalated
- Check that `memory.md` has been updated in the last 30 days

### 3. Manifest accuracy
- Rebuild all MANIFEST.md files from actual folder contents
- Report any pages that were in the manifest but deleted, or exist but weren't in the manifest

### 4. Consistency
- Check that store revenue figures across pages are consistent for the same period
- Check that supplier fill rates match between Business and Operations pages
- Flag any contradictions between signal pages and the data they reference

### 5. Tag hygiene
- List all tags used across the vault
- Flag tags used only once (likely a typo or inconsistency)
- Ensure core tags are present: `#store`, `#supplier`, `#product`, `#signal`, `#trend`, `#report`

## Output

Generate a lint report at `Intelligence/Knowledge/reports/lint-{date}.md`:

```markdown
---
title: Vault Lint Report — {date}
created: {date}
tags: [lint, meta, report]
source: lint
status: active
---

# Vault Lint Report — {date}

## Summary
- Total pages: X
- Healthy: X
- Issues found: X

## Broken Links
- [[page]] → [[missing-target]]

## Orphaned Pages
- [[page-with-no-links]]

## Stale Pages
- [[page]] — last updated {date}

## Contradictions
- ...

## Tag Report
| Tag | Count |
|-----|-------|
| #store | X |
| ...

## Actions Required
1. ...
```

## Post-lint

- Update `memory.md` with lint results
- If critical issues found, create an Inbox item in the relevant pillar
