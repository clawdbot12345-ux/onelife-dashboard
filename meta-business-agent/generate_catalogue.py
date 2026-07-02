#!/usr/bin/env python3
"""
Generate the catalogue / price-list files to feed Meta's WhatsApp Business AI.

Reuses the inventory snapshot exported for the custom bot
(``scripts/whatsapp_bot/inventory_snapshot.json``) so there is a single source
of product data. Produces two files in this directory:

  price-list.csv             — every product (name, category, VAT-incl price,
                               in-stock flag, qty, SKU). Compact; upload this as
                               the AI's product knowledge.
  price-list-by-category.md  — in-stock products grouped by category, human
                               readable. Use as a reference / secondary upload.

Prices are VAT-inclusive (what the customer pays). Regenerate whenever the
dashboard snapshot is refreshed:

    python meta-business-agent/generate_catalogue.py
"""
from __future__ import annotations

import csv
import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SNAPSHOT = ROOT / "scripts" / "whatsapp_bot" / "inventory_snapshot.json"
OUT_DIR = Path(__file__).resolve().parent
CSV_OUT = OUT_DIR / "price-list.csv"
MD_OUT = OUT_DIR / "price-list-by-category.md"


def main() -> int:
    data = json.loads(SNAPSHOT.read_text(encoding="utf-8"))
    products = data.get("products", [])
    generated = data.get("dashboard_generated_at", "unknown")

    # Sort for stable, readable output.
    products.sort(key=lambda p: (p.get("category", ""), p.get("name", "")))

    # ── CSV (all products) ────────────────────────────────────────────────
    with CSV_OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(
            ["name", "category", "price_incl_vat_zar", "in_stock", "qty_on_hand", "sku"]
        )
        for p in products:
            qty = int(p.get("available") or 0)
            w.writerow(
                [
                    p.get("name", ""),
                    p.get("category", ""),
                    f"{float(p.get('sell_price_incl') or 0):.2f}",
                    "yes" if qty > 0 else "no",
                    qty,
                    p.get("sku", ""),
                ]
            )

    # ── Markdown (in-stock, grouped by category) ──────────────────────────
    by_cat: dict[str, list[dict]] = defaultdict(list)
    in_stock_total = 0
    for p in products:
        if int(p.get("available") or 0) > 0:
            by_cat[p.get("category", "Uncategorised")].append(p)
            in_stock_total += 1

    lines = [
        "# Onelife Health — Product price list (in-stock items)",
        "",
        f"_Snapshot from the retail system, generated {generated}. "
        "Prices are in South African Rand, VAT included. Stock changes through "
        "the day — always confirm availability with the store before promising "
        "a customer an item is available._",
        "",
        f"**In-stock products listed: {in_stock_total}**",
        "",
    ]
    for cat in sorted(by_cat):
        lines.append(f"## {cat}")
        lines.append("")
        for p in sorted(by_cat[cat], key=lambda x: x.get("name", "")):
            price = float(p.get("sell_price_incl") or 0)
            lines.append(f"- {p.get('name', '')} — R{price:.2f}")
        lines.append("")

    MD_OUT.write_text("\n".join(lines), encoding="utf-8")

    print(f"Wrote {CSV_OUT.name}: {len(products)} products")
    print(f"Wrote {MD_OUT.name}: {in_stock_total} in-stock products across {len(by_cat)} categories")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
