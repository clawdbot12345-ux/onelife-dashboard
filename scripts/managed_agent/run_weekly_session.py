#!/usr/bin/env python3
"""
Onelife — Weekly Managed Agent Session

Launches a session on the Claude Managed Agents platform with the Onelife
content agent + environment + memory store, and streams the agent's work.

Runs the weekly content→email→analytics cycle:
  1. Agent checks memory for context from last week
  2. Picks next unpublished blog from content/blogs/
  3. Publishes to Shopify + creates Klaviyo draft campaign
  4. Pulls last 7 days of campaign performance
  5. Writes reports/weekly-YYYY-MM-DD.md
  6. Writes learnings back to memory for next week

Environment:
    ANTHROPIC_API_KEY    required
    KLAVIYO_API_KEY      required
    SHOPIFY_ADMIN_TOKEN  optional

Usage:
    python scripts/managed_agent/run_weekly_session.py
"""
import json
import os
import sys
import urllib.request
from pathlib import Path

ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY")
if not ANTHROPIC_KEY:
    print("ERROR: ANTHROPIC_API_KEY not set", file=sys.stderr)
    sys.exit(1)

IDS_PATH = Path(__file__).parent / ".agent-ids.json"
if not IDS_PATH.exists():
    print(f"ERROR: {IDS_PATH} not found. Run setup_agent.py first.", file=sys.stderr)
    sys.exit(1)

ids = json.loads(IDS_PATH.read_text())
AGENT_ID = ids["agent_id"]
ENV_ID = ids["environment_id"]
MEMORY_STORE_ID = ids.get("memory_store_id")

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
        print(f"ERROR {e.code}: {e.read().decode()[:500]}", file=sys.stderr)
        return None

# ─── Create session ───
print("Creating session...", file=sys.stderr)
session_body = {
    "agent": AGENT_ID,
    "environment_id": ENV_ID,
    "title": "Weekly Content & Email Cycle",
}
if MEMORY_STORE_ID:
    session_body["resources"] = [{
        "type": "memory_store",
        "memory_store_id": MEMORY_STORE_ID,
        "access": "read_write",
        "prompt": "Onelife content agent memory. Contains brand voice, published blog history, campaign performance learnings, and product catalog references. Check before starting any task.",
    }]

session = post("/v1/sessions", session_body)
if not session:
    sys.exit(1)
session_id = session["id"]
print(f"  ✓ Session: {session_id}", file=sys.stderr)

# ─── Weekly task prompt ───
weekly_task = """Run the weekly content & email marketing cycle for Onelife Health.

Steps:
1. Check memory for context from previous sessions. Pay attention to:
   - Last week's published blog and its performance (if known)
   - Any updated product catalog info
   - User preference notes

2. Read content/blogs/ and find the next unpublished blog
   (filename doesn't end in .published.md). If there are no unpublished
   blogs left, propose 3 new topics based on:
   - Gaps in their existing blog archive
   - Current search trends (use web_search)
   - Products in their catalog that need more visibility
   And write the new blogs to content/blogs/ with proper YAML frontmatter.

3. Publish the next blog by running:
     python scripts/publish_blog.py content/blogs/<filename>.md
   This creates the Shopify article (draft) and Klaviyo campaign (draft).

4. Pull the last 7 days of campaign performance from the Klaviyo API
   and run:
     python scripts/weekly_report.py
   Read the resulting reports/weekly-YYYY-MM-DD.md and extract key insights.

5. Compare this week's performance to last week's (from memory).
   Identify what's working, what's regressing, and what the single
   most important thing to do next is.

6. Write learnings to memory:
   - /blog_history/<week>.md — what was published, what worked
   - /campaign_performance/<week>.md — the weekly metrics
   - /insights/<week>.md — 1-3 key insights for future sessions

7. Commit all changes to git with a descriptive message.

8. Return a concise summary of what you did and what needs human
   attention (e.g., campaigns to review, underperformers to fix).

Safety rules:
- Never send campaigns without human approval — always leave as Draft
- Never publish the Shopify article as "published" — always leave as draft
- Never modify existing live flows
- If you're unsure about something, write it to memory and wait for human input next week
"""

# ─── Send the task and stream the response ───
print("\nSending weekly task to agent...\n", file=sys.stderr)
print("=" * 60, file=sys.stderr)

send_body = {
    "events": [
        {
            "type": "user.message",
            "content": [{"type": "text", "text": weekly_task}]
        }
    ]
}

req = urllib.request.Request(f"{BASE}/v1/sessions/{session_id}/events",
    data=json.dumps(send_body).encode(),
    headers=HEADERS,
    method="POST")
try:
    with urllib.request.urlopen(req, timeout=60) as resp:
        pass
except urllib.error.HTTPError as e:
    print(f"Failed to send event: {e.code} {e.read().decode()[:300]}", file=sys.stderr)
    sys.exit(1)

# ─── Open SSE stream ───
stream_url = f"{BASE}/v1/sessions/{session_id}/stream"
stream_req = urllib.request.Request(stream_url, headers={**HEADERS, "Accept": "text/event-stream"})
try:
    with urllib.request.urlopen(stream_req, timeout=None) as resp:
        buffer = ""
        for line in resp:
            line = line.decode().rstrip()
            if not line.startswith("data: "):
                continue
            try:
                event = json.loads(line[6:])
            except json.JSONDecodeError:
                continue
            etype = event.get("type")
            if etype == "agent.message":
                for block in event.get("content", []):
                    if block.get("type") == "text":
                        print(block.get("text", ""), end="", flush=True)
            elif etype == "agent.tool_use":
                print(f"\n[Tool: {event.get('name')}]", flush=True)
            elif etype == "session.status_idle":
                print("\n\n[Agent finished]", flush=True)
                break
            elif etype == "agent.error":
                print(f"\n[ERROR] {event.get('error', {}).get('message')}", flush=True)
except KeyboardInterrupt:
    print("\n[Interrupted by user]", file=sys.stderr)

print(f"\nSession: {session_id}", file=sys.stderr)
print(f"View at: https://console.anthropic.com/agents/sessions/{session_id}", file=sys.stderr)
