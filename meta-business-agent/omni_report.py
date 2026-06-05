#!/usr/bin/env python3
"""
Fetch the Onelife Omni "Sales Analysis" report and turn it into the catalogue
price list, from a machine that can reach the Omni server.

The Omni report server (e.g. http://<host>:<port>/Report/...) is on Onelife's
internal network, so this must run somewhere with access to it — a store PC, a
machine on the office VPN, or a self-hosted CI runner on that network. It will
NOT work from a generic cloud server.

CREDENTIALS ARE NEVER STORED IN THIS FILE. Pass the full report URL (which
includes the username/password query string) via an environment variable:

    export ONELIFE_OMNI_REPORT_URL='http://HOST:PORT/Report/Sales%20Analysis%20Johann%20Custom?UserName=USER&Password=PASS&CompanyName=Onelife'
    python meta-business-agent/omni_report.py

What it does:
  1. Fetches the report URL.
  2. Saves the raw response to omni_report_raw.<ext> for inspection.
  3. Detects the format (CSV / HTML table / JSON) and prints a column preview.
  4. Best-effort: if it can find product-name and price columns, writes
     price-list.csv in the same shape as generate_catalogue.py.

If the auto-detected columns are wrong, send the printed preview (or the raw
file) and the column mapping can be tailored — the report's exact columns aren't
known until we see one real response.
"""
from __future__ import annotations

import csv
import io
import json
import os
import sys
import urllib.request
from html.parser import HTMLParser
from pathlib import Path

OUT_DIR = Path(__file__).resolve().parent
URL = os.environ.get("ONELIFE_OMNI_REPORT_URL", "")

# Candidate column-name fragments (lowercased) for auto-mapping.
NAME_HINTS = ("description", "product", "item", "name", "stock description")
PRICE_HINTS = ("incl", "selling", "sell price", "retail", "price")
QTY_HINTS = ("on hand", "soh", "qty", "available", "quantity", "stock on hand")
CAT_HINTS = ("category", "department", "group", "class")
SKU_HINTS = ("barcode", "sku", "code", "stock code")


class _TableParser(HTMLParser):
    """Extract the largest <table> as a list of rows (list of cell strings)."""

    def __init__(self) -> None:
        super().__init__()
        self.tables: list[list[list[str]]] = []
        self._cur: list[list[str]] | None = None
        self._row: list[str] | None = None
        self._cell: list[str] | None = None

    def handle_starttag(self, tag, attrs):
        if tag == "table":
            self._cur = []
        elif tag == "tr" and self._cur is not None:
            self._row = []
        elif tag in ("td", "th") and self._row is not None:
            self._cell = []

    def handle_endtag(self, tag):
        if tag == "table" and self._cur is not None:
            self.tables.append(self._cur)
            self._cur = None
        elif tag == "tr" and self._row is not None:
            self._cur.append(self._row)
            self._row = None
        elif tag in ("td", "th") and self._cell is not None:
            self._row.append(" ".join("".join(self._cell).split()))
            self._cell = None

    def handle_data(self, data):
        if self._cell is not None:
            self._cell.append(data)


def _fetch(url: str) -> tuple[bytes, str]:
    req = urllib.request.Request(url, headers={"User-Agent": "onelife-catalogue/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        return resp.read(), resp.headers.get("Content-Type", "")


def _pick(headers: list[str], hints: tuple[str, ...]) -> int | None:
    low = [h.lower() for h in headers]
    for hint in hints:
        for i, h in enumerate(low):
            if hint in h:
                return i
    return None


def _rows_to_catalogue(headers: list[str], rows: list[list[str]]) -> int:
    name_i = _pick(headers, NAME_HINTS)
    price_i = _pick(headers, PRICE_HINTS)
    if name_i is None or price_i is None:
        print("\n!! Could not auto-detect name/price columns.")
        print("   Detected headers:", headers)
        print("   Send these headers (or the raw file) to tailor the mapping.")
        return 0
    qty_i = _pick(headers, QTY_HINTS)
    cat_i = _pick(headers, CAT_HINTS)
    sku_i = _pick(headers, SKU_HINTS)
    print(
        f"\nColumn mapping → name='{headers[name_i]}', price='{headers[price_i]}', "
        f"qty={headers[qty_i] if qty_i is not None else '-'}, "
        f"category={headers[cat_i] if cat_i is not None else '-'}, "
        f"sku={headers[sku_i] if sku_i is not None else '-'}"
    )
    out = OUT_DIR / "price-list.csv"
    written = 0
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["name", "category", "price_incl_vat_zar", "in_stock", "qty_on_hand", "sku"])
        for r in rows:
            if len(r) <= max(name_i, price_i):
                continue
            name = r[name_i].strip()
            if not name:
                continue
            price_raw = r[price_i].replace("R", "").replace(",", "").strip()
            try:
                price = f"{float(price_raw):.2f}"
            except ValueError:
                price = price_raw
            qty = r[qty_i].strip() if qty_i is not None and len(r) > qty_i else ""
            try:
                in_stock = "yes" if float(qty.replace(",", "")) > 0 else "no"
            except ValueError:
                in_stock = ""
            w.writerow([
                name,
                r[cat_i].strip() if cat_i is not None and len(r) > cat_i else "",
                price,
                in_stock,
                qty,
                r[sku_i].strip() if sku_i is not None and len(r) > sku_i else "",
            ])
            written += 1
    print(f"Wrote {written} rows to {out.name}")
    return written


def main() -> int:
    if not URL:
        print("ERROR: set ONELIFE_OMNI_REPORT_URL (the full report URL incl. credentials).", file=sys.stderr)
        print("Keep it in your shell/secrets — do not hardcode it.", file=sys.stderr)
        return 1

    try:
        body, ctype = _fetch(URL)
    except Exception as e:  # noqa: BLE001
        print(f"ERROR fetching report: {e}", file=sys.stderr)
        print("Are you on a network that can reach the Omni server?", file=sys.stderr)
        return 2

    text = body.decode("utf-8", errors="replace")
    head = text.lstrip()[:1].lower()
    is_html = "html" in ctype.lower() or head == "<"
    is_json = "json" in ctype.lower() or head in "{["
    ext = "html" if is_html else "json" if is_json else "csv" if "," in text[:2000] else "txt"
    raw_path = OUT_DIR / f"omni_report_raw.{ext}"
    raw_path.write_bytes(body)
    print(f"Saved raw report: {raw_path.name}  (Content-Type: {ctype or 'unknown'}, {len(body)} bytes)")
    print("---- first 600 chars ----")
    print(text[:600])
    print("-------------------------")

    if is_json:
        print("\nLooks like JSON — inspect the structure and map fields, then reuse generate_catalogue.py.")
        try:
            data = json.loads(text)
            print("Top-level type:", type(data).__name__)
        except Exception:  # noqa: BLE001
            pass
        return 0

    if is_html:
        p = _TableParser()
        p.feed(text)
        if not p.tables:
            print("\nNo HTML <table> found — this may be a report-viewer shell that loads data via a follow-up request.")
            print("Open the URL in a browser, use the report's Export → CSV/Excel, and run generate_catalogue.py on that, or send me the export.")
            return 0
        biggest = max(p.tables, key=len)
        print(f"\nLargest HTML table: {len(biggest)} rows.")
        if len(biggest) >= 2:
            _rows_to_catalogue(biggest[0], biggest[1:])
        return 0

    # CSV
    reader = list(csv.reader(io.StringIO(text)))
    if len(reader) >= 2:
        _rows_to_catalogue(reader[0], reader[1:])
    else:
        print("\nCouldn't parse as CSV — inspect the raw file or send it over.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
