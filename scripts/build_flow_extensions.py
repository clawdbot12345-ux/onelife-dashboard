#!/usr/bin/env python3
"""
Onelife — build flow-extension assets (owner decision 2026-07-01: extend the
Consultant Check flows rather than revive the drafted Standard flows).

Creates in Klaviyo, as inert assets (nothing is sent until wired + live):
  1. Template: Abandoned Checkout Touch 2 (48h honest check-in)
  2. Template: Abandoned Checkout Touch 3 (72h STACK5 nudge)
  3. Template: Post-Purchase Cross-sell (7 days after order)
  4. Segment: Winback Catch-Up — Lapsed 60–120d
  5. Segment: Winback Catch-Up — Lapsed 120d+
Then writes reports/flow-extension-build-<date>.md with IDs + the exact
Klaviyo UI wiring steps (flow-email wiring is deliberately manual — Klaviyo
discourages programmatic flow edits; same approach as
build_replenishment_flow.py, which shipped successfully).

Environment: KLAVIYO_API_KEY (Templates + Segments write).
Metric ID: WZAxyj = Placed Order (from reports/flow-audit-2026-07-01.md).
"""
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

import email_template

KLAVIYO_KEY = os.environ.get("KLAVIYO_API_KEY")
if not KLAVIYO_KEY:
    print("ERROR: KLAVIYO_API_KEY required", file=sys.stderr)
    sys.exit(1)

PLACED_ORDER = "WZAxyj"
CHECKOUT_URL = "{{ event.extra.checkout_url|default:'https://onelife.co.za/cart' }}"


def klaviyo(path, body, method="POST"):
    req = urllib.request.Request(
        "https://a.klaviyo.com/api" + path,
        data=json.dumps(body).encode(),
        headers={"Authorization": f"Klaviyo-API-Key {KLAVIYO_KEY}",
                 "Content-Type": "application/vnd.api+json",
                 "accept": "application/vnd.api+json", "revision": "2025-04-15"},
        method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read()) if r.status != 204 else {}
    except urllib.error.HTTPError as e:
        print(f"  ERROR {path}: {e.code} {e.read().decode()[:400]}", file=sys.stderr)
        return None


def make_template(name, html, text):
    res = klaviyo("/templates/", {"data": {"type": "template", "attributes": {
        "name": name, "editor_type": "CODE", "html": html, "text": text}}})
    if not res:
        return None
    tid = res["data"]["id"]
    print(f"  ✓ template {tid} — {name}", file=sys.stderr)
    return tid


def make_segment(name, groups):
    res = klaviyo("/segments/", {"data": {"type": "segment", "attributes": {
        "name": name, "definition": {"condition_groups": groups}}}})
    if not res:
        return None
    sid = res["data"]["id"]
    print(f"  ✓ segment {sid} — {name}", file=sys.stderr)
    return sid


def placed_order_condition(op, value, days=None):
    cond = {"type": "profile-metric", "metric_id": PLACED_ORDER,
            "measurement": "count",
            "measurement_filter": {"type": "numeric", "operator": op, "value": value}}
    if days:
        cond["timeframe_filter"] = {"type": "date", "operator": "in-the-last",
                                    "unit": "day", "quantity": days}
    return {"conditions": [cond]}


def main():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # ── Templates ──
    t2_html = email_template.render_email(
        title="Your basket is still here",
        eyebrow="A quick check-in",
        campaign_slug="flow-ac-touch2",
        intro_html=("No pressure from this side — your basket is saved and waiting. "
                    "If you're unsure whether something in it is right for you, that's "
                    "exactly what we're here for. Ask us anything; we'll tell you "
                    "honestly, including when NOT to buy it."),
        cta={"label": "Pick up where you left off →", "href": CHECKOUT_URL},
        whatsapp_lead="Unsure about anything in your basket?",
        whatsapp_prefill="Hi Precious, I left something in my basket — is it right for me?")
    t2_text = ("Your basket is still here.\n\nUnsure about anything in it? WhatsApp us — "
               "we'll answer honestly, including when NOT to buy.\n\n"
               f"Pick up where you left off: https://onelife.co.za/cart\n\n{email_template.TEXT_FOOTER}")

    t3_html = email_template.render_email(
        title="Stacking up? Take 5% off",
        eyebrow="Last nudge, promise",
        campaign_slug="flow-ac-touch3",
        intro_html=("Your basket is still saved. If you're buying three or more items, "
                    "code <strong>STACK5</strong> takes 5% off the lot — and delivery is "
                    "free over R400 (or collect free in store, same day)."),
        cta={"label": "Finish checkout →", "href": CHECKOUT_URL},
        note_html=("<strong>STACK5</strong> — 5% off any 3+ items · "
                   "<strong>STACK10</strong> — 10% off 5+ items. Real codes, no games."),
        whatsapp_lead="Rather talk it through first?",
        whatsapp_prefill="Hi Precious, quick question before I check out")
    t3_text = ("Your basket is saved. STACK5 = 5% off any 3+ items; free delivery over R400.\n\n"
               f"Finish checkout: https://onelife.co.za/cart\n\n{email_template.TEXT_FOOTER}")

    pp_url = email_template.utm("https://onelife.co.za/pages/dispensary-protocols",
                                "flow-pp-crosssell", "protocols-cta")
    pp_html = email_template.render_email(
        title="How's it going with your order?",
        eyebrow="From the counter",
        campaign_slug="flow-pp-crosssell",
        intro_html=("You've had your order about a week now — this is usually when the "
                    "questions come up: with food or without, morning or evening, what "
                    "pairs well. Reply or WhatsApp me and I'll answer properly. And if "
                    "you're building a routine, the consultant-signed stacks below are "
                    "where I'd start."),
        cta={"label": "See the 17 consultant-signed stacks →", "href": pp_url},
        note_html=("Building a stack? <strong>STACK5</strong> takes 5% off any 3+ items, "
                   "<strong>DISPENSARY10</strong> 10% off protocol orders over R600."),
        whatsapp_lead="Questions about what you bought?",
        whatsapp_prefill="Hi Precious, I ordered last week — quick question")
    pp_text = ("A week in — questions usually come up now. WhatsApp us and we'll answer "
               "properly.\n\nConsultant-signed stacks: https://onelife.co.za/pages/dispensary-protocols\n\n"
               + email_template.TEXT_FOOTER)

    print("[1] Creating templates...", file=sys.stderr)
    t2 = make_template(f"[FLOW] Abandoned Checkout Touch 2 — honest check-in — {today}", t2_html, t2_text)
    t3 = make_template(f"[FLOW] Abandoned Checkout Touch 3 — STACK5 nudge — {today}", t3_html, t3_text)
    pp = make_template(f"[FLOW] Post-Purchase Cross-sell — from the counter — {today}", pp_html, pp_text)

    print("[2] Creating winback catch-up segments...", file=sys.stderr)
    seg_60 = make_segment("Winback Catch-Up — Lapsed 60–120d", [
        placed_order_condition("equals", 0, days=60),
        placed_order_condition("greater-than-or-equal", 1, days=120),
    ])
    seg_120 = make_segment("Winback Catch-Up — Lapsed 120d+", [
        placed_order_condition("equals", 0, days=120),
        placed_order_condition("greater-than-or-equal", 1, days=730),
    ])

    results = {"touch2_template": t2, "touch3_template": t3,
               "postpurchase_template": pp,
               "segment_lapsed_60_120": seg_60, "segment_lapsed_120plus": seg_120}
    ok = all(results.values())

    lines = [f"# Flow Extension Build — {today}", "",
             "Assets created in Klaviyo (inert until wired):", "",
             f"| Asset | ID |", "|---|---|"] + [
        f"| {k} | `{v or 'FAILED'}` |" for k, v in results.items()] + ["", """
## Wiring steps (Klaviyo UI, ~15 minutes)

### A. Abandoned checkout: extend "Abandoned Checkout Consultant Check — 2026 design system" (`WY4cae`)
1. Open the flow → after the existing email add **Time delay: 1 day**.
2. Add **Email** → Import template *[FLOW] Abandoned Checkout Touch 2*.
   On this email set flow filter: **Placed Order zero times since starting this flow**.
3. Add **Time delay: 1 day** → **Email** → template *[FLOW] Abandoned Checkout Touch 3*,
   same flow filter. Set both emails LIVE (top-right status per action).
4. Leave the SMS companion flow untouched.

### B. Post-purchase cross-sell (new flow, 3 minutes)
1. Create flow → **Metric trigger: Placed Order**.
2. Flow filter: **Placed Order zero times since starting this flow** (so a repeat
   purchase exits them) — and to avoid overlap: **has not been in flow PCOS
   Post-Purchase** (or rely on the PCOS trigger-filter fix below).
3. **Time delay: 7 days** → **Email** → template *[FLOW] Post-Purchase Cross-sell*.
4. Set live.

### C. PCOS Post-Purchase mistarget fix (`R96wJV`)
Open the flow → Trigger setup → add trigger filter:
**where Items contains Pcositol** (add other PCOS SKUs). Today it fires on
EVERY order — 302 wrong-audience sends in June, R0.

### D. Winback catch-up (uses the two new segments)
1. Clone **Win-Back 60 Days v2** → change trigger to **Added to segment:
   Winback Catch-Up — Lapsed 60–120d** → set LIVE. New segments populate
   shortly after creation; members entering the segment enter the flow.
2. Clone again for **Winback Catch-Up — Lapsed 120d+** (use the 90/120 flow's
   deeper-discount email if preferred) → set LIVE.
3. Keep the existing metric-triggered winback flows live for future lapses;
   add flow filter **has not been in** either catch-up flow to prevent doubles.
"""]
    os.makedirs("reports", exist_ok=True)
    path = f"reports/flow-extension-build-{today}.md"
    with open(path, "w") as fh:
        fh.write("\n".join(lines))
    print(f"{'✓' if ok else '⚠'} Wrote {path}")
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
