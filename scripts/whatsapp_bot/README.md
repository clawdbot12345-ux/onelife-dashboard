# Onelife — WhatsApp Answering Bot

Answers customer WhatsApp messages for Onelife Health using **Claude**, with the
**Omni inventory system as the source of truth** for stock and price, and **hard
guardrails so it never gives medical advice**.

This directly addresses the support load of answering WhatsApp messages: most
messages are "do you have X / what does it cost / is it in stock at [branch]",
which the bot can answer accurately from Omni — while safely declining anything
clinical.

---

## How it answers (and why it's trustworthy on stock & price)

The bot never states stock or price from the model's own memory. Every
stock/price answer is produced by **calling a tool that reads Omni**:

```
customer WhatsApp message
        │
        ▼
  emergency check ──► serious symptoms? deterministic "see a doctor" reply (no model call)
        │
        ▼
  Claude (Opus 4.8) with tools:
     • search_inventory(query)   ─┐
     • get_product(sku)          ─┴─► OmniClient ─► live Omni API  (preferred)
        │                                         └► local snapshot (fallback)
        ▼
   reply sent back to WhatsApp
```

`OmniClient` (`omni_client.py`) is the single interface to the source of truth.
It has two backends and presents the same shape from both:

| Backend | When | Notes |
|---|---|---|
| **Live Omni API** | `ONELIFE_OMNI_API_URL` + `ONELIFE_OMNI_API_KEY` set | Real-time. Point `_live_search` / `_live_get` / `_normalise` at your Omni endpoints. |
| **Local snapshot** | otherwise (default) | Backed by `inventory_snapshot.json`, exported from the dashboard's embedded inventory (5,686 SKUs). Lets the bot run with zero Omni credentials, and is a safe degraded mode if Omni is unreachable. |

The system prompt tells Claude the data is either "live from Omni" or "a
snapshot as of <date>", so it can suggest confirming with the store when a
real-time guarantee matters.

---

## The medical-advice guardrails

Two layers (`guardrails.py`):

1. **System prompt (primary).** Claude is told it is a *retail* assistant, not a
   healthcare provider. It may say whether a product exists, its price, and
   whether it's in stock — but must **not** diagnose, recommend a product to
   treat/manage a condition, give dosing, or advise on interactions, pregnancy,
   or children's health. Those get a one-line decline + redirect to a pharmacist
   / healthcare provider / the in-store team.

2. **Deterministic safety net (defense-in-depth).**
   - `looks_like_emergency()` → the bot short-circuits with a "contact a doctor /
     emergency services" reply **without calling the model at all**.
   - `looks_like_medical_advice()` → a `<system-reminder>` is injected into the
     turn reinforcing the no-advice rule, so even a prompt-injection attempt or
     an edge case still hands off safely.

> "Do you stock magnesium glycinate and what's the price?" → answered from Omni.
> "What should I take for my anxiety?" → declined + redirected, but still happy
> to tell them what's in stock if they name a product.

Run the classifier's self-test:

```bash
python scripts/whatsapp_bot/guardrails.py
```

---

## Files

| File | Purpose |
|---|---|
| `export_inventory.py` | Extracts the inventory snapshot from `index.html` → `inventory_snapshot.json`. |
| `inventory.py` | Keyword search + SKU lookup over the snapshot. |
| `omni_client.py` | Source-of-truth adapter: live Omni API with snapshot fallback. |
| `guardrails.py` | System prompt + medical-advice / emergency classifiers. |
| `bot.py` | Core: Claude tool-use loop, prompt caching, the `answer()` entry point. |
| `cli.py` | Terminal tester (chat like a customer, no WhatsApp needed). |
| `webhook.py` | Flask server for Meta's WhatsApp Cloud API (verify + receive + reply). |
| `requirements.txt` | `anthropic`, `flask`. |

---

## Quick start (local test, no WhatsApp)

```bash
pip install -r scripts/whatsapp_bot/requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...
# optional — use the live source of truth instead of the snapshot:
#   export ONELIFE_OMNI_API_URL=https://omni.example.com/api
#   export ONELIFE_OMNI_API_KEY=...

python scripts/whatsapp_bot/cli.py
```

Try: `do you have berberine 90 caps and how much`, then
`what should I take for high blood pressure?` to see the guardrail.

---

## Connecting it to WhatsApp (Meta Cloud API)

1. Create a Meta app with the **WhatsApp** product and get a Business phone
   number. Note the **Phone Number ID**, a **Graph API token**, and the **App
   Secret**.
2. Set the environment and run the webhook:

   ```bash
   export ANTHROPIC_API_KEY=sk-ant-...
   export WHATSAPP_VERIFY_TOKEN=any-string-you-choose
   export WHATSAPP_APP_SECRET=<meta app secret>
   export WHATSAPP_TOKEN=<graph api token>
   export WHATSAPP_PHONE_NUMBER_ID=<phone number id>
   # optional Omni:
   #   export ONELIFE_OMNI_API_URL=... ONELIFE_OMNI_API_KEY=...

   python scripts/whatsapp_bot/webhook.py     # listens on :8080
   ```
3. Expose it publicly (e.g. `ngrok http 8080`) and, in the Meta dashboard, set
   the webhook **Callback URL** to `https://<your-host>/webhook` and the
   **Verify Token** to your `WHATSAPP_VERIFY_TOKEN`. Subscribe to the `messages`
   field.
4. Message the business number — the bot replies.

Incoming requests are signature-verified against `WHATSAPP_APP_SECRET`; the
server refuses unsigned traffic. The same design works with Twilio or another
BSP — only `webhook.py`'s receive/parse and `_send_whatsapp` need swapping.

> **Twilio note:** Twilio for WhatsApp posts `application/x-www-form-urlencoded`
> with `From`/`Body` fields and verifies via the `X-Twilio-Signature` header
> (not Meta's `X-Hub-Signature-256`). Use `bot.answer()` unchanged and replace
> the Meta-specific parsing/verification/send in `webhook.py`.

---

## Configuration reference

| Env var | Default | Purpose |
|---|---|---|
| `ANTHROPIC_API_KEY` | — | Required. |
| `ONELIFE_BOT_MODEL` | `claude-opus-4-8` | Model. Set to `claude-haiku-4-5` for a cheaper/faster high-volume option. |
| `ONELIFE_BOT_EFFORT` | `low` | Thinking/effort level (`low`/`medium`/`high`). |
| `ONELIFE_BOT_MAX_TOKENS` | `2048` | Max reply tokens. |
| `ONELIFE_OMNI_API_URL` / `ONELIFE_OMNI_API_KEY` | — | Enable the live Omni backend. |
| `WHATSAPP_VERIFY_TOKEN` / `WHATSAPP_APP_SECRET` / `WHATSAPP_TOKEN` / `WHATSAPP_PHONE_NUMBER_ID` | — | WhatsApp Cloud API (webhook only). |

---

## Notes & production hardening

- **History** is in-memory per sender (`webhook.py`). Move it to Redis/a DB so
  context survives restarts and scales across workers.
- **Prompt caching** is on: the system prompt + tool list are byte-stable, so
  every message after the first reuses the cached prefix.
- **Refresh the snapshot** alongside the daily dashboard refresh
  (`python scripts/whatsapp_bot/export_inventory.py`) — or just run with the
  live Omni backend, which is always current.
- The bot only handles **text** messages; other types get a polite nudge.
- Guardrails reduce risk but are not a compliance sign-off — have Onelife's
  pharmacist/owner review the system prompt wording before going live.
