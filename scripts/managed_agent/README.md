# Onelife — Claude Managed Agent

This directory holds the setup and runtime for the Onelife content agent,
deployed to [Claude Managed Agents](https://platform.claude.com/docs/en/managed-agents/overview) (Anthropic's agent platform, launched April 8, 2026).

## Why Managed Agents vs GitHub Actions

We use **both**, for different jobs:

| Concern | GitHub Actions | Managed Agent |
|---|---|---|
| Daily data refresh | ✓ (simple cron script) | — |
| PDF regeneration | ✓ | — |
| Weekly blog publish + performance review | trigger | ✓ (runs the actual agent work) |
| Persistent memory across sessions | ✗ | ✓ (memory stores) |
| Multi-step reasoning (decide topic → write → QA → publish) | ✗ | ✓ |
| Access to full tool harness (bash, web, files, MCP) | — | ✓ |

The weekly agent cycle is triggered by GitHub Actions cron (`.github/workflows/managed-agent-weekly.yml`), which POSTs to Claude Managed Agents API to create a session. The agent then does the actual work in a sandboxed container with access to persistent memory.

## First-time setup (one-time, ~10 minutes)

### Prerequisites

1. **Anthropic API key** — get one at [console.anthropic.com/settings/keys](https://console.anthropic.com/settings/keys)
2. **Klaviyo API key** — you already have this (`pk_c3d...`)
3. **(Optional) Memory store access** — the `memory_store` feature is in research preview. [Request access](https://claude.com/form/claude-managed-agents) if you want persistent memory from day 1. The agent will still work without it — each session will just be "ephemeral".

### Step 1 — Run the setup script locally (not in GitHub Actions)

```bash
export ANTHROPIC_API_KEY=sk-ant-...
export KLAVIYO_API_KEY=pk_c3d588d7e95567d363e4772f227ea548ec
python scripts/managed_agent/setup_agent.py
```

This will:
1. Create the Managed Agent (`Onelife Health Content Agent`) with the full agent toolset
2. Create the cloud environment with unrestricted networking (needed for Klaviyo/Shopify)
3. Create a memory store (if your account has access)
4. Seed the memory store with brand voice, product catalog, playbook, and UTM schema
5. Save the resulting IDs to `scripts/managed_agent/.agent-ids.json`

The IDs file is committed to the repo so the weekly workflow can find them.

### Step 2 — Add the Anthropic API key to GitHub Secrets

1. Go to **Settings → Secrets and variables → Actions → New repository secret**
2. Name: `ANTHROPIC_API_KEY`
3. Value: your `sk-ant-...` key

### Step 3 — Test a manual session

```bash
python scripts/managed_agent/run_weekly_session.py
```

This creates a session, sends the weekly task prompt, and streams the agent's work to stdout. You'll see the agent check memory, pick a blog, run publish_blog.py, etc.

### Step 4 — Let the scheduled workflow take over

The `.github/workflows/managed-agent-weekly.yml` workflow runs every **Monday at 07:00 SAST** and launches a session automatically. You don't need to do anything else.

## Directory structure

```
scripts/managed_agent/
├── README.md                    (this file)
├── setup_agent.py               one-time setup
├── run_weekly_session.py        runtime: create session + stream
├── .agent-ids.json              created by setup — agent/env/memory IDs
└── memory_seeds/
    ├── brand_voice.md           how emails should look and sound
    ├── playbook.md              weekly cycle + red lines
    ├── product_catalog.md       known top sellers + gaps
    └── utm_schema.md            link tagging schema
```

## Memory evolution

Each week, the agent writes new files to the memory store:

```
memory_store/
├── brand_voice.md               (seed — rarely changes)
├── playbook.md                  (seed)
├── product_catalog.md           (seed — agent may update when products change)
├── utm_schema.md                (seed)
├── blog_history/
│   ├── 2026-W15.md              what was published week 15
│   ├── 2026-W16.md              ...
│   └── ...
├── campaign_performance/
│   ├── 2026-W15.md              weekly metrics, top/bottom performers
│   └── ...
└── insights/
    ├── 2026-W15.md              key insight from that week
    └── ...
```

The agent checks these on every session before starting work. If it notices
a campaign from 2 weeks ago underperformed, it can adjust the next blog's
template/subject/product selection accordingly.

## Costs

Claude Managed Agents pricing: **$0.08 per session-hour** of active runtime (as of April 2026).

Expected weekly cycle runtime: ~15-30 minutes per session → ~$0.02-$0.04 per week → roughly **$1-2 per month** for fully autonomous weekly content operations.

Plus usual Claude API token costs for the model (Sonnet 4.6) — typically $2-5 per weekly session depending on how much work the agent does.

## Safety rules (baked into the system prompt)

1. Never send campaigns automatically — always leave as Draft
2. Never publish Shopify articles as "published" — always draft
3. Never modify existing live flows
4. Never use fabricated product data
5. Never duplicate existing blog topics
6. Always write learnings to memory for next week
7. Always commit changes to git with a clear message

## Troubleshooting

**Memory store creation fails (HTTP 403):** The memory feature is in research preview. [Request access](https://claude.com/form/claude-managed-agents). Until then, the agent runs without persistent memory — each session starts fresh and reads context from the git repo files instead.

**Session hangs or times out:** Check the session URL printed at the end — you can view the full trace at `https://console.anthropic.com/agents/sessions/<session_id>`.

**Agent creates duplicate campaigns:** Check `/insights/` in memory. The playbook tells the agent to check Klaviyo's recent campaigns before creating new ones — if it's missing this step, update `memory_seeds/playbook.md` and re-seed.
