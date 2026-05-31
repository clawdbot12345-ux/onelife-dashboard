#!/usr/bin/env python3
"""
Onelife — Guardrails

Two layers of defence keep the WhatsApp bot from giving medical advice:

  1. **System prompt** (`build_system_prompt`) — the primary guardrail. It tells
     Claude exactly what it may and may not do: answer product / stock / price /
     store questions from Omni, and refuse to diagnose, recommend treatment,
     give dosing for a condition, or advise on drug/medication interactions —
     redirecting those to a pharmacist or the in-store consultation instead.

  2. **Lightweight classifier** (`looks_like_medical_advice`) — a deterministic
     safety net that runs *before* the model. It catches obviously clinical
     questions (symptoms, conditions, "what should I take for…", dosing,
     pregnancy, drug interactions) so that even if a prompt-injection attempt or
     an edge case slips the system prompt, the bot still hands off safely. This
     is belt-and-suspenders, not the main control — the system prompt does the
     heavy lifting.

The medical disclaimer (`MEDICAL_DISCLAIMER`) is appended whenever the safety
net fires, and the model is instructed to use the same wording itself.
"""
from __future__ import annotations

import re

# The South African health context: Onelife is a retailer, not a clinic. By law
# and good practice, supplement retailers must not diagnose or prescribe.
PHARMACIST_HANDOFF = (
    "For anything health- or symptom-related, I'd recommend speaking to a "
    "pharmacist or your healthcare provider — our in-store team at Centurion, "
    "Glen Village and Edenvale can also help you in person. 💚"
)

MEDICAL_DISCLAIMER = (
    "Just so you know, I can help with product info, prices and stock, but I "
    "can't give medical or health advice. " + PHARMACIST_HANDOFF
)


def build_system_prompt(data_as_of: str, backend: str) -> str:
    """Assemble the bot's system prompt.

    Kept byte-stable across requests (no timestamps, no per-message data) so it
    caches cleanly — see prompt-caching notes in bot.py. The only variable
    pieces are the data-freshness line and backend label, which change rarely.
    """
    return f"""You are the WhatsApp assistant for **Onelife Health**, a South African health \
retail chain with three stores (Centurion, Glen Village, Edenvale) and an online \
store at onelife.co.za. You answer customer WhatsApp messages.

# What you do
- Help customers find products, check whether something is **in stock**, and quote \
**prices** (in South African Rand, VAT included — that is the price customers pay).
- Share basic store info: there are three branches (Centurion, Glen Village, Edenvale) \
and the onelife.co.za online store.
- Be warm, brief, and conversational — this is WhatsApp. Short paragraphs, the odd \
emoji is fine. Write the way a friendly shop assistant texts.

# Source of truth — ALWAYS use the tools
- Stock and price come ONLY from the `search_inventory` and `get_product` tools, which \
read Onelife's Omni inventory system. This is the authoritative record.
- NEVER state a price, stock level, or "we have it / we don't" from memory or guesswork. \
If you haven't looked it up with a tool this message, look it up before answering.
- If a tool returns no match, say you couldn't find it and offer to check an alternative \
or suggest they ask in-store — do not invent a product.
- Quote the VAT-inclusive price (`price_incl_vat`). If something shows zero stock, say \
it's currently out of stock and offer to check another branch or a similar item.
- The inventory data is {("live from Omni" if backend == "omni" else f"a snapshot as of {data_as_of}")}. \
If a customer needs a guaranteed real-time figure, suggest they confirm with the store.

# HARD LIMIT — no medical advice (this is non-negotiable)
You are a retail assistant, NOT a healthcare provider. You must NOT:
- Diagnose, or suggest what condition someone might have.
- Recommend a product *to treat, cure, prevent, or manage a symptom or condition* \
("take X for your anxiety / blood pressure / infection / pregnancy", etc.).
- Give dosages, how-much-to-take, or how-to-use instructions for a health purpose.
- Advise on interactions with medication, pregnancy/breastfeeding, children's health, \
or chronic conditions.
- Interpret lab results, symptoms, or test readings.

When a customer asks any of the above, do NOT answer the medical part. Instead:
1. Warmly decline the medical part in one line.
2. Redirect them to a pharmacist / their healthcare provider, and mention the in-store \
team can help in person.
3. You MAY still help with the *retail* part — e.g. if they ask "do you stock magnesium \
glycinate and is it good for sleep?", tell them whether it's in stock and the price, but \
do not claim it helps with sleep. Use wording like:
   "{MEDICAL_DISCLAIMER}"

Telling someone a product *exists*, its *price*, and whether it's *in stock* is fine. \
Telling them it will *help their condition* or *how to take it* is not.

# Escalation
If someone describes an emergency or serious symptoms, do not engage clinically — urge \
them to contact a doctor, pharmacist, or emergency services immediately.

# Style
- Keep replies to a few lines. Lead with the answer.
- Prices in Rand like "R249.00". List a few options if there are several matches.
- Never mention these instructions, the tools, "Omni", or that you are an AI model \
unless directly asked.
"""


# ── Safety-net classifier ─────────────────────────────────────────────────
# Phrases that strongly indicate the customer is asking for clinical guidance
# rather than retail info. Deliberately high-precision; the system prompt is the
# main control, so this only needs to catch the obvious cases.
_MEDICAL_PATTERNS = [
    r"\bwhat (should|can|do) i take\b",
    r"\bwhat('?s| is) good for\b",
    r"\bwhich (one |product |supplement )?(is |would be )?(best|good) for\b",
    r"\bhow (much|many).*(should|do) i (take|use|drink)\b",
    r"\bwhat('?s| is) the (dose|dosage)\b",
    r"\bcan i (take|use|mix|combine).*\b(with|while|during)\b",
    r"\b(safe|okay|ok) (to take|to use|with|during|while)\b",
    r"\b(pregnan|breastfeed|breast-feed|nursing)\w*\b",
    r"\b(diagnos|prescri|treat|cure|heal|remedy)\w*\b",
    r"\binteract(s|ion|ions)?\b.*\b(medication|meds|medicine|drug|pill|tablet)\b",
    r"\b(my|i have|i'?ve got|suffering from|struggling with) "
    r"(anxiety|depress|diabet|blood pressure|hypertension|cholesterol|thyroid|"
    r"infection|cancer|arthritis|insomnia|migraine|pain|ibs|reflux|ulcer|"
    r"high blood|low blood)\w*",
    r"\bsymptom(s)?\b",
    r"\bdoes (it|this|that) (help|cure|treat|fix|work for)\b",
    r"\bis (it|this|that) (good|safe|effective) for (my|the)\b",
]
_MEDICAL_RE = re.compile("|".join(_MEDICAL_PATTERNS), re.IGNORECASE)

# Emergency / red-flag language that should be escalated, not answered.
_EMERGENCY_RE = re.compile(
    r"\b(chest pain|can'?t breathe|cannot breathe|overdose|suicid|"
    r"bleeding|unconscious|seizure|stroke|heart attack|emergency|allergic reaction|"
    r"anaphyla)\w*",
    re.IGNORECASE,
)


def looks_like_medical_advice(message: str) -> bool:
    """True if the message reads like a request for clinical/health guidance."""
    return bool(_MEDICAL_RE.search(message or ""))


def looks_like_emergency(message: str) -> bool:
    return bool(_EMERGENCY_RE.search(message or ""))


EMERGENCY_REPLY = (
    "This sounds serious — please contact a doctor, your nearest pharmacy, or "
    "emergency services (10177 / 112 from a cell phone) right away. I'm only able "
    "to help with product and store questions. 💚"
)


if __name__ == "__main__":
    tests = [
        ("Do you have magnesium glycinate in stock?", False),
        ("How much vitamin D should I take for my low levels?", True),
        ("What's good for anxiety?", True),
        ("Whats the price of berberine 90 caps", False),
        ("Can I take ashwagandha with my blood pressure meds?", True),
        ("Is the NAD+ in stock at Edenvale?", False),
        ("im pregnant can i use this", True),
        ("I'm having chest pain what should I take", True),  # medical + emergency
    ]
    for msg, expected in tests:
        got = looks_like_medical_advice(msg)
        flag = "OK " if got == expected else "MISS"
        emer = " [EMERGENCY]" if looks_like_emergency(msg) else ""
        print(f"  [{flag}] medical={got!s:<5} {msg}{emer}")
