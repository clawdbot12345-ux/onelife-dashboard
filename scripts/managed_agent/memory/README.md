# Onelife Agent — Git-Backed Memory

This directory IS the agent's persistent memory. Every session, the agent reads
from here at the start and writes new learnings at the end. Because it's
committed to git, memory survives across sessions and is fully auditable.

## Why file-based memory instead of Klaviyo research-preview memory stores?

Claude Managed Agents has a `memory_stores` feature, but it's gated behind a
research preview that our account doesn't have access to yet. File-based memory
in the repo gives us equivalent (actually better) functionality:

| Concern | Memory Store API | Git-backed files |
|---|---|---|
| Persistence across sessions | ✓ | ✓ |
| Searchable by agent | ✓ (memory_search tool) | ✓ (grep, find) |
| Versioned history | ✓ (memory_version API) | ✓ (git history) |
| Human-reviewable | via Console | ✓ (just read the files) |
| Editable by human | via Console | ✓ (just edit the file) |
| Available today | ✗ (research preview) | ✓ |

## Directory layout

```
memory/
├── README.md                    (this file — agent reads first)
├── brand_voice.md               copy of seed, agent can update
├── playbook.md                  copy of seed, agent can update
├── product_catalog.md           copy of seed, agent keeps fresh
├── utm_schema.md                copy of seed
├── blog_history/
│   ├── 2026-W15.md              what was published in week 15
│   └── ...
├── campaign_performance/
│   ├── 2026-W15.md              last week's metrics
│   └── ...
├── insights/
│   ├── 2026-W15.md              key takeaway, 1-3 bullets
│   └── ...
└── product_changes/
    ├── 2026-04-11.md            e.g., "Bio-Berberine discontinued, swap to..."
    └── ...
```

## How the agent uses this

At session start:
1. Read `README.md` (this file)
2. Read `playbook.md` for the current weekly cycle rules
3. Read `brand_voice.md` for template style
4. Read `product_catalog.md` for known products + gaps
5. Read the most recent 2-3 files in `insights/` for recent learnings
6. Read last week's `campaign_performance/` file to compare

At session end:
1. Write new `blog_history/<week>.md` with what was published
2. Write new `campaign_performance/<week>.md` with metrics
3. Write new `insights/<week>.md` with 1-3 key takeaways
4. Update `product_catalog.md` if products changed
5. Commit everything with a descriptive message

## Human edits

You can edit any file here any time. The agent will respect your changes on
the next session. If you want to tell the agent something specific, just add
a file at `memory/human_notes/YYYY-MM-DD.md` and it will read it.
