#!/usr/bin/env python3
"""
Onelife — WhatsApp Cloud API webhook

A minimal Flask server that connects the bot to WhatsApp via Meta's WhatsApp
Cloud API. Handles the two things the Cloud API needs:

  GET  /webhook   verification handshake (Meta calls this once when you save the
                  webhook URL in the Meta dashboard).
  POST /webhook   incoming customer messages — verified by signature, passed to
                  the bot, and answered by sending a reply back through the Graph
                  API.

Conversation history is kept in memory per sender for simplicity. For
production, swap `_HISTORY` for a real store (Redis, a DB) so context survives
restarts and scales across workers.

Env:
  ANTHROPIC_API_KEY            required (used by the bot)
  WHATSAPP_VERIFY_TOKEN        required — the token you type into the Meta dashboard
  WHATSAPP_APP_SECRET          required — Meta app secret, for signature verification
  WHATSAPP_TOKEN               required — Graph API access token (to send replies)
  WHATSAPP_PHONE_NUMBER_ID     required — your WhatsApp Business phone number ID
  PORT                         optional (default 8080)

Run:
  pip install -r scripts/whatsapp_bot/requirements.txt
  python scripts/whatsapp_bot/webhook.py
  # expose locally with e.g. `ngrok http 8080`, then point the Meta webhook at it.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import sys
import urllib.request

from flask import Flask, request

from bot import get_bot

VERIFY_TOKEN = os.environ.get("WHATSAPP_VERIFY_TOKEN", "")
APP_SECRET = os.environ.get("WHATSAPP_APP_SECRET", "")
GRAPH_TOKEN = os.environ.get("WHATSAPP_TOKEN", "")
PHONE_NUMBER_ID = os.environ.get("WHATSAPP_PHONE_NUMBER_ID", "")
GRAPH_API = "https://graph.facebook.com/v21.0"

app = Flask(__name__)

# Per-sender conversation history. Replace with Redis/DB for production.
_HISTORY: dict[str, list[dict]] = {}
_MAX_TURNS = 20


def _verify_signature(raw_body: bytes) -> bool:
    """Validate Meta's X-Hub-Signature-256 header against the app secret."""
    if not APP_SECRET:
        # No secret configured — refuse rather than trust unsigned traffic.
        return False
    sig = request.headers.get("X-Hub-Signature-256", "")
    if not sig.startswith("sha256="):
        return False
    expected = "sha256=" + hmac.new(
        APP_SECRET.encode(), raw_body, hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(sig, expected)


def _send_whatsapp(to: str, text: str) -> None:
    """Send a text message back to the customer via the Graph API."""
    payload = json.dumps(
        {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "text",
            "text": {"body": text[:4096]},  # WhatsApp body limit
        }
    ).encode()
    req = urllib.request.Request(
        f"{GRAPH_API}/{PHONE_NUMBER_ID}/messages",
        data=payload,
        headers={
            "Authorization": f"Bearer {GRAPH_TOKEN}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            resp.read()
    except Exception as e:  # noqa: BLE001 — log and move on; never crash the webhook
        print(f"[send error] {e}", file=sys.stderr)


@app.get("/webhook")
def verify():
    """Meta verification handshake."""
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge", "")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "forbidden", 403


@app.post("/webhook")
def incoming():
    raw = request.get_data()
    if not _verify_signature(raw):
        return "invalid signature", 403

    data = request.get_json(silent=True) or {}
    bot = get_bot()

    for entry in data.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            for msg in value.get("messages", []):
                if msg.get("type") != "text":
                    # Only text is handled; politely deflect other types.
                    sender = msg.get("from", "")
                    if sender:
                        _send_whatsapp(
                            sender,
                            "Hi! I can help with product info, prices and stock — "
                            "please send me a text message. 💚",
                        )
                    continue

                sender = msg["from"]
                body = msg.get("text", {}).get("body", "")
                history = _HISTORY.setdefault(sender, [])

                reply = bot.answer(body, history)

                history.append({"role": "user", "content": body})
                history.append({"role": "assistant", "content": reply.text})
                _HISTORY[sender] = history[-_MAX_TURNS:]

                _send_whatsapp(sender, reply.text)

    # Always 200 quickly so Meta doesn't retry.
    return "ok", 200


@app.get("/health")
def health():
    bot = get_bot()
    return {"status": "ok", "inventory_backend": bot.omni.backend}, 200


if __name__ == "__main__":
    missing = [
        name
        for name, val in {
            "WHATSAPP_VERIFY_TOKEN": VERIFY_TOKEN,
            "WHATSAPP_APP_SECRET": APP_SECRET,
            "WHATSAPP_TOKEN": GRAPH_TOKEN,
            "WHATSAPP_PHONE_NUMBER_ID": PHONE_NUMBER_ID,
        }.items()
        if not val
    ]
    if missing:
        print(f"WARNING: missing env vars: {', '.join(missing)}", file=sys.stderr)
        print("The server will start but can't verify or send until these are set.", file=sys.stderr)

    port = int(os.environ.get("PORT", "8080"))
    app.run(host="0.0.0.0", port=port)
