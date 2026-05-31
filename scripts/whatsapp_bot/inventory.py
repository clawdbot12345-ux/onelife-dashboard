#!/usr/bin/env python3
"""
Onelife — Local inventory index (snapshot-backed)

Loads ``inventory_snapshot.json`` (produced by ``export_inventory.py``) and
provides keyword search and SKU lookup over the ~5,700 SKU catalogue.

This is the *offline* implementation of the inventory source of truth. The
``OmniClient`` in ``omni_client.py`` uses this as a fallback when the live Omni
API is not configured, and presents the same shape to the bot either way.

Prices in the snapshot exclude VAT for ``sell_price_excl`` and include VAT for
``sell_price_incl`` — Onelife quotes customers the VAT-inclusive price, so the
bot surfaces ``sell_price_incl`` as "the price".
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Optional

SNAPSHOT_PATH = Path(__file__).resolve().parent / "inventory_snapshot.json"

# Words that carry no discriminating signal in a product-name search.
_STOPWORDS = {
    "the", "a", "an", "of", "for", "with", "and", "to", "in", "do", "you",
    "have", "any", "got", "is", "are", "i", "im", "my", "me", "please", "pls",
    "hi", "hello", "hey", "stock", "price", "cost", "much", "how", "what",
    "available", "buy", "want", "need", "looking", "tablets", "tabs", "caps",
    "capsules",
}

_TOKEN_RE = re.compile(r"[a-z0-9]+")


def _tokenize(text: str) -> list[str]:
    return [t for t in _TOKEN_RE.findall(text.lower()) if t]


class Inventory:
    """In-memory keyword index over the product snapshot."""

    def __init__(self, snapshot_path: Path = SNAPSHOT_PATH):
        data = json.loads(snapshot_path.read_text(encoding="utf-8"))
        self.generated_at: str = data.get("dashboard_generated_at", "")
        self.products: list[dict] = data.get("products", [])

        self._by_sku: dict[str, dict] = {}
        self._name_tokens: list[tuple[dict, set[str]]] = []
        for p in self.products:
            sku = str(p.get("sku", ""))
            if sku:
                self._by_sku[sku] = p
            tokens = set(_tokenize(p.get("name", "")))
            tokens.update(_tokenize(p.get("category", "")))
            self._name_tokens.append((p, tokens))

    # ── lookups ───────────────────────────────────────────────────────────
    def get_by_sku(self, sku: str) -> Optional[dict]:
        return self._by_sku.get(str(sku).strip())

    def search(self, query: str, limit: int = 8) -> list[dict]:
        """Rank products by how well their name matches the query terms.

        Scoring favours products that match more of the query's meaningful
        terms, with a bonus for in-stock items so the bot leads with things
        the customer can actually buy.
        """
        terms = [t for t in _tokenize(query) if t not in _STOPWORDS]
        if not terms:
            terms = _tokenize(query)  # fall back to everything if all stopwords
        if not terms:
            return []

        scored: list[tuple[float, dict]] = []
        for product, tokens in self._name_tokens:
            if not tokens:
                continue
            score = 0.0
            for term in terms:
                if term in tokens:
                    score += 2.0
                elif any(term in tok or tok in term for tok in tokens):
                    # partial / substring match (e.g. "magnesium" ~ "mag")
                    score += 1.0
            if score == 0:
                continue
            # Coverage bonus: matched all the meaningful terms.
            matched_terms = sum(
                1 for term in terms if any(term in tok or tok in term for tok in tokens)
            )
            score += matched_terms / max(len(terms), 1)
            # In-stock nudge.
            if (product.get("available") or 0) > 0:
                score += 0.5
            scored.append((score, product))

        scored.sort(key=lambda x: (-x[0], x[1].get("name", "")))
        return [p for _, p in scored[:limit]]


@lru_cache(maxsize=1)
def get_inventory() -> Inventory:
    """Process-wide singleton — the snapshot is loaded once."""
    return Inventory()


if __name__ == "__main__":
    import sys

    inv = get_inventory()
    q = " ".join(sys.argv[1:]) or "magnesium glycinate"
    print(f"Snapshot generated at: {inv.generated_at}  ({len(inv.products)} SKUs)")
    print(f"Search: {q!r}\n")
    for p in inv.search(q):
        stock = int(p.get("available") or 0)
        print(
            f"  {p['name']:<40} R{p.get('sell_price_incl', 0):>8.2f} incl  "
            f"| {'IN STOCK x'+str(stock) if stock > 0 else 'OUT OF STOCK':<14} "
            f"| {p.get('category', '')}"
        )
