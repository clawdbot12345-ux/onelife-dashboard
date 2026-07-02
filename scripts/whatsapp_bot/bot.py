#!/usr/bin/env python3
"""
Onelife — WhatsApp answering bot (core)

Turns a customer WhatsApp message into a reply, using Claude with two tools that
read the Omni inventory (the source of truth), and with hard guardrails against
giving medical advice.

Flow per message:
  1. Emergency red-flag check → deterministic safe reply, no model call.
  2. Otherwise call Claude (Opus 4.8 by default) with the `search_inventory` and
     `get_product` tools in a manual agentic loop. Stock/price answers come only
     from the tools.
  3. If the message looked clinical, a system-reminder is injected to reinforce
     the no-medical-advice rule (belt-and-suspenders with the system prompt).

The system prompt and tool list are kept byte-stable and prompt-cached, so each
message after the first only pays full price for the new turn.

Env:
  ANTHROPIC_API_KEY        required
  ONELIFE_BOT_MODEL        optional (default: claude-opus-4-8)
  ONELIFE_BOT_EFFORT       optional (default: low)
  ONELIFE_OMNI_API_URL     optional — enables the live Omni backend
  ONELIFE_OMNI_API_KEY     optional
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field

import anthropic

from guardrails import (
    EMERGENCY_REPLY,
    build_system_prompt,
    looks_like_emergency,
    looks_like_medical_advice,
)
from omni_client import OmniClient

MODEL = os.environ.get("ONELIFE_BOT_MODEL", "claude-opus-4-8")
EFFORT = os.environ.get("ONELIFE_BOT_EFFORT", "low")
MAX_TOKENS = int(os.environ.get("ONELIFE_BOT_MAX_TOKENS", "2048"))
MAX_TOOL_ITERATIONS = 4

TOOLS = [
    {
        "name": "search_inventory",
        "description": (
            "Search Onelife's Omni inventory by product name or keyword. Returns "
            "matching products with their SKU, price (VAT inclusive and "
            "exclusive), and current stock level. Call this whenever a customer "
            "asks whether something is available, what it costs, or to find a "
            "product. This is the authoritative source for stock and price."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Product name or keywords, e.g. 'magnesium glycinate' or 'vitamin c 1000'.",
                }
            },
            "required": ["query"],
        },
    },
    {
        "name": "get_product",
        "description": (
            "Look up a single product by its exact SKU / barcode in the Omni "
            "inventory. Use after search_inventory when you need the precise "
            "stock and price for one specific item."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "sku": {"type": "string", "description": "The product SKU or barcode."}
            },
            "required": ["sku"],
        },
    },
]

_MEDICAL_REMINDER = (
    "<system-reminder>This customer message appears health- or symptom-related. "
    "Do NOT give medical advice, diagnosis, dosing, or treatment/interaction "
    "guidance. You may still tell them whether items are in stock and their "
    "price. Decline the medical part in one line and redirect them to a "
    "pharmacist or their healthcare provider.</system-reminder>"
)


@dataclass
class BotReply:
    text: str
    used_tools: list[str] = field(default_factory=list)
    medical_flagged: bool = False
    emergency: bool = False
    backend: str = "snapshot"


class OnelifeBot:
    def __init__(self) -> None:
        self.client = anthropic.Anthropic()
        self.omni = OmniClient()
        # Cached, byte-stable system prompt (data_as_of/backend change rarely).
        self.system_prompt = build_system_prompt(self.omni.data_as_of, self.omni.backend)

    # ── tool execution ────────────────────────────────────────────────────
    def _run_tool(self, name: str, tool_input: dict) -> str:
        if name == "search_inventory":
            results = self.omni.search_products(str(tool_input.get("query", "")))
            return json.dumps({"results": results}) if results else json.dumps(
                {"results": [], "note": "No matching products found."}
            )
        if name == "get_product":
            product = self.omni.get_product(str(tool_input.get("sku", "")))
            return json.dumps(product) if product else json.dumps(
                {"error": "No product with that SKU."}
            )
        return json.dumps({"error": f"Unknown tool {name}"})

    # ── main entry point ──────────────────────────────────────────────────
    def answer(self, message: str, history: list[dict] | None = None) -> BotReply:
        """Answer one customer message. `history` is prior [{role, content}] turns."""
        if looks_like_emergency(message):
            return BotReply(
                text=EMERGENCY_REPLY, emergency=True, backend=self.omni.backend
            )

        medical = looks_like_medical_advice(message)
        user_content = (_MEDICAL_REMINDER + "\n\n" + message) if medical else message

        messages: list[dict] = list(history or [])
        messages.append({"role": "user", "content": user_content})

        used_tools: list[str] = []
        final_text = ""

        for _ in range(MAX_TOOL_ITERATIONS):
            response = self.client.messages.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                thinking={"type": "adaptive"},
                output_config={"effort": EFFORT},
                system=[
                    {
                        "type": "text",
                        "text": self.system_prompt,
                        "cache_control": {"type": "ephemeral"},
                    }
                ],
                tools=TOOLS,
                messages=messages,
            )

            if response.stop_reason == "tool_use":
                messages.append({"role": "assistant", "content": response.content})
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        used_tools.append(block.name)
                        result = self._run_tool(block.name, block.input)
                        tool_results.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": result,
                            }
                        )
                messages.append({"role": "user", "content": tool_results})
                continue

            # end_turn (or anything else) — collect the text and stop.
            final_text = "".join(
                b.text for b in response.content if b.type == "text"
            ).strip()
            break

        if not final_text:
            final_text = (
                "Sorry, I had trouble with that one — could you rephrase, or pop "
                "into one of our stores and the team will help you out? 💚"
            )

        return BotReply(
            text=final_text,
            used_tools=used_tools,
            medical_flagged=medical,
            backend=self.omni.backend,
        )


_BOT: OnelifeBot | None = None


def get_bot() -> OnelifeBot:
    global _BOT
    if _BOT is None:
        _BOT = OnelifeBot()
    return _BOT
