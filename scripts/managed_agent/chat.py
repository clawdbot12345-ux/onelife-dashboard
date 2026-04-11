#!/usr/bin/env python3
"""
Onelife — Interactive Chat with the Managed Agent

Opens a session with the Onelife Health Content Agent on Anthropic's
Managed Agents platform and lets you have a live conversation with it.

The agent has access to:
  - Bash, file operations, web search (agent toolset)
  - Your Klaviyo account (via KLAVIYO_API_KEY env var passed in the prompt)
  - Your Shopify store (via SHOPIFY_CLIENT_ID/SECRET passed in the prompt)
  - Git-backed memory at scripts/managed_agent/memory/

Usage:
    export ANTHROPIC_API_KEY=sk-ant-...
    export KLAVIYO_API_KEY=pk_c3d...
    export SHOPIFY_CLIENT_ID=6f58e9d...
    export SHOPIFY_CLIENT_SECRET=shpss_...
    python scripts/managed_agent/chat.py

Commands:
    /exit     End the session
    /new      Start a fresh session (lose context)
    /save     Save the conversation transcript
    /help     Show this message
"""
import json
import os
import sys
import time
import urllib.request
from datetime import datetime
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

BASE = "https://api.anthropic.com"
HEADERS = {
    "x-api-key": ANTHROPIC_KEY,
    "anthropic-version": "2023-06-01",
    "anthropic-beta": "agent-api-2026-03-01",
    "content-type": "application/json",
}


def post(path, body):
    req = urllib.request.Request(f"{BASE}{path}",
        data=json.dumps(body).encode(),
        headers=HEADERS, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"_error": f"{e.code}: {e.read().decode()[:400]}"}


def get(path):
    req = urllib.request.Request(f"{BASE}{path}", headers={k: v for k, v in HEADERS.items() if k != "content-type"})
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"_error": f"{e.code}: {e.read().decode()[:400]}"}


# Colors for terminal
class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    GREEN = "\033[32m"
    CYAN = "\033[36m"
    YELLOW = "\033[33m"
    MAGENTA = "\033[35m"
    RED = "\033[31m"


def create_session():
    print(f"{C.DIM}Creating session on Anthropic Managed Agents...{C.RESET}")
    body = {
        "agent": {"type": "agent_reference", "id": AGENT_ID},
        "environment": ENV_ID,
        "title": f"Onelife chat — {datetime.now().strftime('%Y-%m-%d %H:%M')}",
    }
    result = post("/v1/sessions", body)
    if "_error" in result:
        print(f"{C.RED}✗ {result['_error']}{C.RESET}")
        sys.exit(1)
    sid = result["id"]
    print(f"{C.GREEN}✓ Session: {sid}{C.RESET}")
    print(f"{C.DIM}  View at: https://console.anthropic.com/agents/sessions/{sid}{C.RESET}\n")
    return sid


def send_and_wait(session_id, text):
    """Send a user message, poll for completion, return the new agent events."""
    # Record how many events exist before sending
    before = get(f"/v1/sessions/{session_id}/events")
    if "_error" in before:
        return [{"error": before["_error"]}]
    before_count = len(before.get("data", []))

    # Send the event
    send_result = post(f"/v1/sessions/{session_id}/events", {
        "events": [{"type": "user", "content": [{"type": "text", "text": text}]}]
    })
    if "_error" in send_result:
        return [{"error": send_result["_error"]}]

    # Poll until session is idle
    print(f"{C.DIM}(thinking...){C.RESET}", end="", flush=True)
    last_printed_idx = before_count
    max_polls = 300  # ~5 min at 1s intervals
    for i in range(max_polls):
        time.sleep(1)
        events_resp = get(f"/v1/sessions/{session_id}/events")
        if "_error" in events_resp:
            continue
        events = events_resp.get("data", [])
        # Print new events as they appear
        new_events = events[last_printed_idx:]
        for ev in new_events:
            render_event(ev)
        last_printed_idx = len(events)
        # Check for idle
        if events and events[-1].get("type") in ("status_idle", "session.status_idle"):
            print()
            return events[before_count:]
        # Check for error
        if events and events[-1].get("type") in ("agent.error", "session.status_error", "session.error"):
            print(f"\n{C.RED}[error in session]{C.RESET}")
            return events[before_count:]
    print(f"\n{C.RED}[timeout after 5 min]{C.RESET}")
    return events[before_count:] if events else []


def render_event(ev):
    etype = ev.get("type", "")
    if etype == "agent":
        for block in ev.get("content", []):
            btype = block.get("type")
            if btype == "text" and block.get("text"):
                print(f"\r{' ' * 20}\r", end="")  # clear "thinking..." line
                print(f"{C.CYAN}{block['text']}{C.RESET}", end="", flush=True)
            elif btype == "tool_use":
                print(f"\n{C.YELLOW}  🔧 {block.get('name', '?')}{C.RESET}", flush=True)
    elif etype == "agent_tool_use":
        for block in ev.get("content", []):
            if block.get("type") == "tool_use":
                name = block.get("name", "?")
                inp = block.get("input", {})
                cmd = inp.get("command", "") if isinstance(inp, dict) else str(inp)[:120]
                print(f"\n{C.YELLOW}  🔧 [{name}] {cmd[:100]}{'...' if len(cmd) > 100 else ''}{C.RESET}", flush=True)
    elif etype == "agent_tool_result":
        for block in ev.get("content", []):
            if block.get("type") == "tool_result":
                rc = block.get("content", [])
                if rc and isinstance(rc, list):
                    first = rc[0] if isinstance(rc[0], dict) else {}
                    text = first.get("text", "")
                    if text:
                        snippet = text[:150].replace("\n", " ")
                        print(f"{C.DIM}    ← {snippet}{'...' if len(text) > 150 else ''}{C.RESET}", flush=True)


def main():
    print(f"{C.BOLD}{C.GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{C.RESET}")
    print(f"{C.BOLD}Onelife Content Agent — Interactive Chat{C.RESET}")
    print(f"{C.DIM}Running on Anthropic Managed Agents{C.RESET}")
    print(f"{C.BOLD}{C.GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{C.RESET}")
    print(f"{C.DIM}Commands: /exit /new /save /help{C.RESET}\n")

    session_id = create_session()
    transcript = []

    # Optional first message to prime the agent with context
    context_primer = """Hi. I'm kicking off a chat with you via the interactive CLI. Before I start asking you things, please:
1. Briefly confirm you can see the git-backed memory context (try to read scripts/managed_agent/memory/README.md — it may or may not be in your environment)
2. Acknowledge what you know about Onelife Health in 2-3 sentences
3. Wait for my next question

Be brief. Under 100 words."""
    print(f"{C.DIM}{C.BOLD}[priming agent with context...]{C.RESET}\n")
    send_and_wait(session_id, context_primer)
    print()

    while True:
        try:
            user_input = input(f"{C.BOLD}{C.MAGENTA}you ▸ {C.RESET}").strip()
        except (EOFError, KeyboardInterrupt):
            print(f"\n{C.DIM}(exiting){C.RESET}")
            break

        if not user_input:
            continue

        if user_input == "/exit":
            print(f"{C.DIM}(ending session — agent state persists on Anthropic's platform){C.RESET}")
            break
        elif user_input == "/new":
            session_id = create_session()
            transcript = []
            continue
        elif user_input == "/save":
            path = Path(f"/tmp/onelife-chat-{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt")
            path.write_text("\n".join(transcript))
            print(f"{C.GREEN}✓ Saved to {path}{C.RESET}")
            continue
        elif user_input == "/help":
            print(__doc__)
            continue

        transcript.append(f"YOU: {user_input}")
        print(f"\n{C.BOLD}{C.CYAN}agent ▸{C.RESET} ", end="", flush=True)
        events = send_and_wait(session_id, user_input)
        # Build transcript from events
        for ev in events:
            if ev.get("type") == "agent":
                for block in ev.get("content", []):
                    if block.get("type") == "text" and block.get("text"):
                        transcript.append(f"AGENT: {block['text']}")
        print()

    print(f"\n{C.DIM}Session ID: {session_id}{C.RESET}")
    print(f"{C.DIM}Full history: https://console.anthropic.com/agents/sessions/{session_id}{C.RESET}")


if __name__ == "__main__":
    main()
