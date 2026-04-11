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

## Memory is in git, not in a memory store
Your persistent memory lives at `scripts/managed_agent/memory/` in the repo.
Read/write it as normal files using your bash and file tools. Everything you
write there gets committed to git at the end of the session, so next week's
you will see it.

## Steps

1. **Check memory** before starting anything:
   - Read `scripts/managed_agent/memory/README.md` for the layout
   - Read `scripts/managed_agent/memory/playbook.md` for the weekly rules
   - Read `scripts/managed_agent/memory/brand_voice.md` for template style
   - Read `scripts/managed_agent/memory/product_catalog.md` for known products
   - Read the most recent 2-3 files in `scripts/managed_agent/memory/insights/`
   - Read last week's `scripts/managed_agent/memory/campaign_performance/` file
   - Read any `scripts/managed_agent/memory/human_notes/` files (human instructions)

2. **Check the content queue**: `ls content/blogs/*.md | grep -v published`
   - If there's an unpublished blog, skip to step 4 (the blog is already written)
   - If the queue is EMPTY, go to step 3 to research + write a new blog

3. **RESEARCH + WRITE A NEW BLOG** (when queue is empty):

   ### 3a. Audit what already exists to avoid duplicates
   - Fetch the full Onelife blog archive:
     `curl -sL https://onelife.co.za/blogs/health-wellness-hub.atom`
   - Extract titles and URLs from the Atom feed
   - Check the last 30 days of Klaviyo campaigns to see what topics were already
     covered: use the Klaviyo campaigns endpoint with the last 30 days filter
   - Build a list of topics to AVOID

   ### 3b. Research what's trending
   - Use `web_search` for:
     * Current SA health trends this season (autumn/winter if March-August)
     * Trending supplements on reddit.com/r/Supplements and r/PCOS and r/nootropics
     * "south africa health supplement trends 2026"
     * Seasonal conditions (e.g., hay fever, winter immunity, summer hydration)
   - Note 3-5 topic candidates that aren't already in the archive

   ### 3c. Query product intelligence (CRITICAL for revenue)
   - **New launches**: fetch Shopify products published in the last 30 days:
     ```
     curl -sS "https://onelifehealth.myshopify.com/admin/api/2025-01/products.json?published_at_min=$(date -u -d '30 days ago' +%Y-%m-%dT%H:%M:%S%z)&limit=50" \\
       -H "X-Shopify-Access-Token: $SHOPIFY_TOKEN"
     ```
     (First exchange SHOPIFY_CLIENT_ID + SHOPIFY_CLIENT_SECRET for a token
     via POST /admin/oauth/access_token with grant_type=client_credentials)
   - **Top sellers (last 30 days)** via Klaviyo `Ordered Product` metric:
     POST to /api/metric-aggregates/ with metric_id=TqJLxm, interval=month,
     measurements=["count","sum_value"]
   - **In-stock check**: ensure any product you recommend has inventory_quantity > 0

   ### 3d. Pick ONE topic
   Score each candidate on:
   - (a) Gap in the archive (high score = not covered)
   - (b) Matches a trending topic (high score = more readers)
   - (c) Has 2-3 in-stock products we can feature (high score = more revenue)
   - (d) Seasonal relevance right now
   Pick the highest-scoring topic.

   ### 3e. Write the blog
   - Use the NAD+ winning template structure as reference (see memory/brand_voice.md)
   - 3-5 H2 sections, 800-1500 words total
   - Match the voice: evidence-first, not hype, honest caveats
   - YAML frontmatter at the top with: title, slug, handle (health-wellness-hub),
     author ("Your Health Store Companion"), excerpt, preview (email preview text),
     subject (email subject), tags, campaign_segment (Xrk5jD), send_offset_days (2),
     category_heading, shop_collection_url, shop_label, intro_p1, intro_p2, and
     products list with name/url/blurb for each of 2-3 products
   - Save to `content/blogs/YYYY-MM-DD-<slug>.md`

4. **Publish the blog** (only once the file exists):
   ```
   python scripts/publish_blog.py content/blogs/<filename>.md
   ```
   This creates the Shopify article as published, creates the Klaviyo
   campaign, generates a Nano Banana Pro hero image (in the next GHA step),
   and auto-schedules the send.

5. **Mark the blog as published** by renaming:
   ```
   git mv content/blogs/<file>.md content/blogs/<file>.published.md
   ```

6. **Pull this week's performance** and run the weekly report:
   ```
   python scripts/weekly_report.py
   ```
   Read `reports/weekly-YYYY-MM-DD.md`.

6. **Compare vs last week** (from memory). Write 1-3 insights to
   `scripts/managed_agent/memory/insights/<ISO-week>.md` in this format:
   ```markdown
   # Week <W>, <year>
   ## What happened
   - Published: <blog title>
   - Top campaign: <name> — R<revenue>
   - Bottom campaign: <name> — R<revenue>
   ## What I learned
   - <insight 1>
   - <insight 2>
   ## What to do next week
   - <action>
   ```

7. **Update product catalog** if you noticed any 404s on product links.
   Write to `scripts/managed_agent/memory/product_changes/<date>.md`.

8. **Commit everything to git** with a descriptive message:
   ```
   git add -A
   git commit -m "chore: weekly agent cycle <week> - <summary>"
   ```

9. **Return a concise summary** (under 200 words) of what you did and
   what needs human attention.

## Safety rules — NEVER violate these
- Never send campaigns. Always leave as Draft.
- Never publish Shopify articles as "published". Always draft.
- Never modify existing live flows.
- Never use fabricated product data. Always verify links return HTTP 200.
- Never duplicate topics already in the blog archive or scheduled Klaviyo
  campaigns. Check `memory/blog_history/` before picking a topic.
- If anything is ambiguous, write your question to
  `memory/human_notes/pending-questions.md` and wait for the next week.
"""
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
