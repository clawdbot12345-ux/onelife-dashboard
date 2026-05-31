#!/usr/bin/env python3
"""
Onelife — Omni inventory adapter (the source of truth)

Omni is Onelife's retail/POS system and the *authoritative* record of what is in
stock and what it costs. The WhatsApp bot must answer stock and price questions
from Omni, never from the model's own memory.

This adapter gives the bot one stable interface — ``search_products`` and
``get_product`` — over two backends:

  1. **Live Omni API** (preferred). Enabled when ``ONELIFE_OMNI_API_URL`` and
     ``ONELIFE_OMNI_API_KEY`` are set. Talks to Omni over HTTPS.
  2. **Local snapshot** (fallback). Uses ``inventory.py`` backed by the daily
     dashboard export. Lets the bot run with zero Omni credentials for local
     testing, demos, and as a degraded mode if Omni is unreachable.

The live wire format will differ per Omni deployment, so the HTTP calls live
behind ``_live_search`` / ``_live_get`` and the response mapping behind
``_normalise`` — point those at your Omni endpoints and the rest of the bot is
unchanged. Both backends return records in the same normalised shape:

    {
      "sku": str, "name": str, "category": str,
      "in_stock": bool, "available": int,
      "price_incl_vat": float, "price_excl_vat": float,
      "source": "omni" | "snapshot",
    }
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Optional

from inventory import get_inventory

OMNI_API_URL = os.environ.get("ONELIFE_OMNI_API_URL", "").rstrip("/")
OMNI_API_KEY = os.environ.get("ONELIFE_OMNI_API_KEY", "")
OMNI_TIMEOUT = float(os.environ.get("ONELIFE_OMNI_TIMEOUT", "8"))


class OmniError(RuntimeError):
    pass


class OmniClient:
    def __init__(self) -> None:
        self.live = bool(OMNI_API_URL and OMNI_API_KEY)
        self._inv = None if self.live else get_inventory()

    @property
    def backend(self) -> str:
        return "omni" if self.live else "snapshot"

    @property
    def data_as_of(self) -> str:
        """Human-readable freshness string for the snapshot backend."""
        if self.live:
            return "live"
        return self._inv.generated_at if self._inv else "unknown"

    # ── public interface used by the bot's tools ──────────────────────────
    def search_products(self, query: str, limit: int = 8) -> list[dict]:
        if self.live:
            try:
                return [self._normalise(r) for r in self._live_search(query, limit)]
            except OmniError:
                # Fail safe: degrade to the snapshot rather than guessing.
                self._ensure_snapshot()
        return [self._from_snapshot(p) for p in self._inv.search(query, limit)]

    def get_product(self, sku: str) -> Optional[dict]:
        if self.live:
            try:
                raw = self._live_get(sku)
                return self._normalise(raw) if raw else None
            except OmniError:
                self._ensure_snapshot()
        p = self._inv.get_by_sku(sku)
        return self._from_snapshot(p) if p else None

    # ── live Omni backend ─────────────────────────────────────────────────
    def _live_search(self, query: str, limit: int) -> list[dict]:
        params = urllib.parse.urlencode({"q": query, "limit": limit})
        body = self._request("GET", f"/products/search?{params}")
        # Adjust to your Omni payload shape:
        return body.get("results", body if isinstance(body, list) else [])

    def _live_get(self, sku: str) -> Optional[dict]:
        body = self._request("GET", f"/products/{urllib.parse.quote(str(sku))}")
        return body or None

    def _request(self, method: str, path: str) -> dict | list:
        url = f"{OMNI_API_URL}{path}"
        req = urllib.request.Request(
            url,
            method=method,
            headers={
                "Authorization": f"Bearer {OMNI_API_KEY}",
                "Accept": "application/json",
            },
        )
        try:
            with urllib.request.urlopen(req, timeout=OMNI_TIMEOUT) as resp:
                return json.loads(resp.read())
        except (urllib.error.URLError, TimeoutError, ValueError) as e:
            raise OmniError(f"Omni request failed: {e}") from e

    def _normalise(self, raw: dict) -> dict:
        """Map a live Omni record into the bot's normalised shape.

        Tweak the field names on the right-hand side to match your Omni API.
        """
        available = int(raw.get("quantity_on_hand", raw.get("available", 0)) or 0)
        price_incl = float(raw.get("price_incl_vat", raw.get("retail_price", 0)) or 0)
        price_excl = float(
            raw.get("price_excl_vat", round(price_incl / 1.15, 2) if price_incl else 0)
        )
        return {
            "sku": str(raw.get("sku", raw.get("barcode", ""))),
            "name": raw.get("name", raw.get("description", "")),
            "category": raw.get("category", raw.get("department", "")),
            "in_stock": available > 0,
            "available": available,
            "price_incl_vat": price_incl,
            "price_excl_vat": price_excl,
            "source": "omni",
        }

    # ── snapshot backend ──────────────────────────────────────────────────
    def _ensure_snapshot(self) -> None:
        if self._inv is None:
            self._inv = get_inventory()

    def _from_snapshot(self, p: dict) -> dict:
        available = int(p.get("available") or 0)
        return {
            "sku": str(p.get("sku", "")),
            "name": p.get("name", ""),
            "category": p.get("category", ""),
            "in_stock": available > 0,
            "available": available,
            "price_incl_vat": float(p.get("sell_price_incl") or 0),
            "price_excl_vat": float(p.get("sell_price_excl") or 0),
            "source": "snapshot",
        }


if __name__ == "__main__":
    import sys

    client = OmniClient()
    print(f"Backend: {client.backend} (data as of {client.data_as_of})\n")
    for r in client.search_products(" ".join(sys.argv[1:]) or "vitamin c"):
        print(
            f"  [{r['sku']}] {r['name']:<36} R{r['price_incl_vat']:>8.2f} "
            f"| {'in stock x'+str(r['available']) if r['in_stock'] else 'out of stock'}"
        )
