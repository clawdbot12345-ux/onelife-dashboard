#!/usr/bin/env python3
"""
Onelife — Inventory snapshot exporter

Pulls the embedded ``DASHBOARD_DATA.products.all`` array out of ``index.html``
and writes it to ``inventory_snapshot.json`` next to this script.

This snapshot is the WhatsApp bot's *offline* source of truth. In production the
bot prefers the live Omni API (see ``omni_client.py``); the snapshot is the
fallback used when Omni credentials aren't configured, and it lets the bot run
out of the box for local testing and demos.

The dashboard itself is refreshed daily by the GitHub Actions workflow, so this
snapshot can be regenerated on the same cadence (or in the same workflow):

    python scripts/whatsapp_bot/export_inventory.py

Each product record carries: sku, name, category, group, available (qty on
hand), cost_price, sell_price_excl, sell_price_incl, margin_pct, and
reorder_qty.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
INDEX_HTML = ROOT / "index.html"
OUT_PATH = Path(__file__).resolve().parent / "inventory_snapshot.json"


def _extract_balanced(text: str, open_idx: int, open_ch: str, close_ch: str) -> str:
    """Return the substring spanning a balanced bracket pair starting at open_idx.

    Walks the string respecting JS/JSON string literals so brackets inside
    strings don't throw off the depth count.
    """
    depth = 0
    in_str = False
    quote = ""
    escaped = False
    for i in range(open_idx, len(text)):
        ch = text[i]
        if in_str:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == quote:
                in_str = False
            continue
        if ch in ('"', "'"):
            in_str = True
            quote = ch
        elif ch == open_ch:
            depth += 1
        elif ch == close_ch:
            depth -= 1
            if depth == 0:
                return text[open_idx : i + 1]
    raise ValueError("Unbalanced brackets — could not extract array")


def extract_products(html: str) -> list:
    anchor = html.find('"products"')
    if anchor == -1:
        raise ValueError('Could not find "products" in index.html')
    all_key = html.find('"all"', anchor)
    if all_key == -1:
        raise ValueError('Could not find products."all" array')
    bracket = html.find("[", all_key)
    if bracket == -1:
        raise ValueError('Could not find opening bracket of "all" array')
    array_src = _extract_balanced(html, bracket, "[", "]")
    return json.loads(array_src)


def main() -> int:
    if not INDEX_HTML.exists():
        print(f"ERROR: {INDEX_HTML} not found", file=sys.stderr)
        return 1

    html = INDEX_HTML.read_text(encoding="utf-8")
    products = extract_products(html)

    # Keep only the fields the bot needs, and drop obvious non-products.
    cleaned = []
    for p in products:
        if not p.get("name"):
            continue
        cleaned.append(
            {
                "sku": p.get("sku", ""),
                "name": p.get("name", ""),
                "category": p.get("category", ""),
                "group": p.get("group", ""),
                "available": p.get("available", 0),
                "cost_price": p.get("cost_price", 0),
                "sell_price_excl": p.get("sell_price_excl", 0),
                "sell_price_incl": p.get("sell_price_incl", 0),
                "margin_pct": p.get("margin_pct", 0),
                "reorder_qty": p.get("reorder_qty", 0),
            }
        )

    # Pull the dashboard's "generated_at" so the bot can report data freshness.
    generated_at = ""
    g = html.find('"generated_at"')
    if g != -1:
        colon = html.find(":", g)
        q1 = html.find('"', colon)
        q2 = html.find('"', q1 + 1)
        if q1 != -1 and q2 != -1:
            generated_at = html[q1 + 1 : q2]

    snapshot = {
        "source": "index.html DASHBOARD_DATA.products.all",
        "dashboard_generated_at": generated_at,
        "product_count": len(cleaned),
        "products": cleaned,
    }
    OUT_PATH.write_text(json.dumps(snapshot, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote {len(cleaned)} products to {OUT_PATH}")
    print(f"Dashboard generated at: {generated_at or 'unknown'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
