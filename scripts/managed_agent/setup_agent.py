#!/usr/bin/env python3
"""
Onelife — Claude Managed Agent Setup (one-time)

Creates the Managed Agent, Environment, and Memory Store on the Claude
Platform. Run this once locally after getting your Anthropic API key.

Writes the resulting IDs to `scripts/managed_agent/.agent-ids.json` so the
runtime scripts (run_weekly_session.py, etc.) can reference them.

Environment:
    ANTHROPIC_API_KEY    required
    KLAVIYO_API_KEY      required (seeded into memory)

Usage:
    export ANTHROPIC_API_KEY=sk-ant-...
    export KLAVIYO_API_KEY=pk_...
    python scripts/managed_agent/setup_agent.py
"""
import json
import os
import sys
import urllib.request
from pathlib import Path

ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY")
KLAVIYO_KEY = os.environ.get("KLAVIYO_API_KEY")

if not ANTHROPIC_KEY:
    print("ERROR: ANTHROPIC_API_KEY not set", file=sys.stderr)
    print("Get one at: https://console.anthropic.com/settings/keys", file=sys.stderr)
    sys.exit(1)

BASE = "https://api.anthropic.com"
HEADERS = {
    "x-api-key": ANTHROPIC_KEY,
    "anthropic-version": "2023-06-01",
    "anthropic-beta": "managed-agents-2026-04-01",
    "content-type": "application/json",
}

def post(path, body):
    req = urllib.request.Request(f"{BASE}{path}",
        data=json.dumps(body).encode(),
        headers=HEADERS,
        method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"ERROR {e.code} on {path}: {e.read().decode()[:500]}", file=sys.stderr)
        return None

# ─── System prompt ───
SYSTEM_PROMPT = """You are the Onelife Health content & email marketing agent.

You are responsible for the weekly content→email→analytics pipeline for
Onelife Health, a South African health retail chain with 3 physical stores
(Centurion, Glen Village, Edenvale) and a Shopify online store at
onelife.co.za.

Your responsibilities:
1. Every Monday morning, publish the next unpublished blog from
   content/blogs/ to the Shopify blog
2. Create a matching Klaviyo email campaign (draft status, scheduled 2
   days out) that links to the blog and features 2-3 real products from
   the Onelife catalog
3. Match the Onelife brand voice exactly (see memory: brand_voice.md)
4. Every week, pull the last 7 days of campaign performance from Klaviyo
   and write a weekly report to reports/
5. Track every email link with UTM parameters (see memory: utm_schema.md)
6. Identify underperforming campaigns and propose fixes
7. Identify gaps in the content calendar (topics they haven't covered
   that are trending)
8. Never duplicate existing blog topics — always check the onelife.co.za
   blog archive and recent Klaviyo campaigns before proposing new content
9. Never send campaigns without human approval — always leave as Draft

You have access to:
- The Onelife repo (mounted as working directory)
- Klaviyo API via KLAVIYO_API_KEY env var
- Shopify Admin API via SHOPIFY_ADMIN_TOKEN env var (if set)
- Bash, file operations, web search, and a persistent memory store

Always:
- Check memory before starting any task (the agent may have written
  important context in a previous session)
- Write durable learnings to memory at the end of every session
- Use the real Onelife brand voice (dark green #1B5E20, logo, simple
  product list, no fake badges — see memory/brand_voice.md)
- Match the existing template style from the NAD+ winning campaign
- Prefer pulling real data from APIs over relying on pre-computed values

Never:
- Send campaigns without human approval
- Create flows programmatically (Klaviyo recommends against this)
- Duplicate blog topics that already exist or are scheduled
- Use fabricated product names, prices, or URLs — always verify against
  the live onelife.co.za catalog
"""

# ─── Create the agent ───
print("[1/3] Creating agent...", file=sys.stderr)
agent_body = {
    "name": "Onelife Health Content Agent",
    "model": "claude-sonnet-4-6",
    "system": SYSTEM_PROMPT,
    "tools": [
        {"type": "agent_toolset_20260401"}  # Full toolset: bash, files, web, mcp
    ],
}
agent = post("/v1/agents", agent_body)
if not agent:
    sys.exit(1)
agent_id = agent["id"]
agent_version = agent.get("version", 1)
print(f"  ✓ Agent ID: {agent_id} (version {agent_version})", file=sys.stderr)

# ─── Create the environment ───
print("[2/3] Creating environment...", file=sys.stderr)
env_body = {
    "name": "onelife-content-env",
    "config": {
        "type": "cloud",
        "networking": {"type": "unrestricted"},  # needs web access for Klaviyo/Shopify
    }
}
env = post("/v1/environments", env_body)
if not env:
    sys.exit(1)
environment_id = env["id"]
print(f"  ✓ Environment ID: {environment_id}", file=sys.stderr)

# ─── Create the memory store (research preview — may require access) ───
print("[3/3] Creating memory store...", file=sys.stderr)
store_body = {
    "name": "Onelife Content Memory",
    "description": "Persistent memory for the Onelife content agent. Contains brand voice, published blog history, campaign performance learnings, product catalog references, and user preferences.",
}
store = post("/v1/memory_stores", store_body)
memory_store_id = None
if store:
    memory_store_id = store["id"]
    print(f"  ✓ Memory store ID: {memory_store_id}", file=sys.stderr)
else:
    print("  ⚠ Memory store creation failed — this feature is in research preview.", file=sys.stderr)
    print("    Request access at: https://claude.com/form/claude-managed-agents", file=sys.stderr)
    print("    The agent will still work without persistent memory (session-only).", file=sys.stderr)

# ─── Seed the memory store with initial context ───
if memory_store_id:
    print("\nSeeding memory store with initial context...", file=sys.stderr)
    ROOT = Path(__file__).resolve().parent.parent.parent
    seeds = [
        ("/brand_voice.md", (ROOT / "scripts/managed_agent/memory_seeds/brand_voice.md").read_text() if (ROOT / "scripts/managed_agent/memory_seeds/brand_voice.md").exists() else ""),
        ("/product_catalog.md", (ROOT / "scripts/managed_agent/memory_seeds/product_catalog.md").read_text() if (ROOT / "scripts/managed_agent/memory_seeds/product_catalog.md").exists() else ""),
        ("/utm_schema.md", (ROOT / "scripts/managed_agent/memory_seeds/utm_schema.md").read_text() if (ROOT / "scripts/managed_agent/memory_seeds/utm_schema.md").exists() else ""),
        ("/playbook.md", (ROOT / "scripts/managed_agent/memory_seeds/playbook.md").read_text() if (ROOT / "scripts/managed_agent/memory_seeds/playbook.md").exists() else ""),
    ]
    for path, content in seeds:
        if not content:
            continue
        body = {"path": path, "content": content}
        req = urllib.request.Request(f"{BASE}/v1/memory_stores/{memory_store_id}/memories",
            data=json.dumps(body).encode(), headers=HEADERS, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                print(f"  ✓ Seeded {path}", file=sys.stderr)
        except urllib.error.HTTPError as e:
            print(f"  ✗ Failed to seed {path}: {e.code} — {e.read().decode()[:200]}", file=sys.stderr)

# ─── Save IDs for runtime scripts ───
out_path = Path(__file__).parent / ".agent-ids.json"
out = {
    "agent_id": agent_id,
    "agent_version": agent_version,
    "environment_id": environment_id,
    "memory_store_id": memory_store_id,
}
out_path.write_text(json.dumps(out, indent=2))
print(f"\n✓ Saved IDs to {out_path}", file=sys.stderr)

print("\n" + "=" * 60, file=sys.stderr)
print("SETUP COMPLETE", file=sys.stderr)
print("=" * 60, file=sys.stderr)
print(f"  Agent:       {agent_id}", file=sys.stderr)
print(f"  Environment: {environment_id}", file=sys.stderr)
print(f"  Memory:      {memory_store_id or 'not created (research preview)'}", file=sys.stderr)
print(f"\nNext: run scripts/managed_agent/run_weekly_session.py to kick off a session.", file=sys.stderr)

print(json.dumps(out))
