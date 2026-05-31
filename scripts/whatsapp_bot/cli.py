#!/usr/bin/env python3
"""
Onelife — WhatsApp bot CLI tester

Chat with the bot in your terminal exactly as a WhatsApp customer would, without
needing WhatsApp or a webhook. Useful for trying guardrails and inventory
answers.

    export ANTHROPIC_API_KEY=sk-ant-...
    # optional: export ONELIFE_OMNI_API_URL=... ONELIFE_OMNI_API_KEY=...
    python scripts/whatsapp_bot/cli.py

Commands:  /reset  clear conversation    /quit  exit
"""
from __future__ import annotations

import os
import sys

from bot import get_bot


def main() -> int:
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY not set", file=sys.stderr)
        return 1

    bot = get_bot()
    print("Onelife WhatsApp bot — terminal tester")
    print(f"  inventory backend: {bot.omni.backend} (as of {bot.omni.data_as_of})")
    print("  commands: /reset  /quit\n")

    history: list[dict] = []
    while True:
        try:
            msg = input("you ▸ ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not msg:
            continue
        if msg == "/quit":
            break
        if msg == "/reset":
            history = []
            print("(conversation cleared)\n")
            continue

        reply = bot.answer(msg, history)
        # Persist the plain customer text + assistant reply for context.
        history.append({"role": "user", "content": msg})
        history.append({"role": "assistant", "content": reply.text})
        # Keep the window bounded.
        history[:] = history[-20:]

        tags = []
        if reply.emergency:
            tags.append("EMERGENCY")
        if reply.medical_flagged:
            tags.append("medical-guarded")
        if reply.used_tools:
            tags.append("tools:" + ",".join(reply.used_tools))
        suffix = f"   [{' | '.join(tags)}]" if tags else ""
        print(f"bot ▸ {reply.text}{suffix}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
