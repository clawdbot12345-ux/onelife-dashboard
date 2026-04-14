#!/usr/bin/env python3
"""
Onelife — Dawn theme backup + duplicate

1. Finds the Dawn theme in the Onelife Shopify store (match by name).
2. Pulls every asset via the REST Admin API and writes it to
   scripts/shopify-theme-backup/dawn-backup-YYYY-MM-DD/<key>
   (text assets by value, binary assets decoded from `attachment`).
   A BINARY_ASSETS_MANIFEST.txt lists every binary file written.
3. Calls the GraphQL `themeDuplicate` mutation to create an unpublished
   copy named "Dawn Backup YYYY-MM-DD" in the store.

Environment:
  SHOPIFY_CLIENT_ID
  SHOPIFY_CLIENT_SECRET
  SHOPIFY_STORE=onelifehealth            (default)
  DAWN_THEME_NAME=Dawn                   (override if the theme is renamed)
  DUPLICATE_NAME=Dawn Backup YYYY-MM-DD  (override the new theme's name)
  SKIP_DUPLICATE=1                       (backup only, no themeDuplicate call)
  SKIP_BACKUP=1                          (duplicate only, no local snapshot)
"""
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

CLIENT_ID = os.environ.get("SHOPIFY_CLIENT_ID")
CLIENT_SECRET = os.environ.get("SHOPIFY_CLIENT_SECRET")
STORE = os.environ.get("SHOPIFY_STORE", "onelifehealth").replace(".myshopify.com", "")
THEME_NAME = os.environ.get("DAWN_THEME_NAME", "Dawn")
API_VERSION = "2025-01"

if not (CLIENT_ID and CLIENT_SECRET):
    print("ERROR: SHOPIFY_CLIENT_ID + SECRET required", file=sys.stderr)
    sys.exit(1)

TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")
DUPLICATE_NAME = os.environ.get("DUPLICATE_NAME", f"Dawn Backup {TODAY}")
BACKUP_DIR = Path(__file__).resolve().parent / "shopify-theme-backup" / f"dawn-backup-{TODAY}"


def get_token():
    body = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }).encode()
    req = urllib.request.Request(
        f"https://{STORE}.myshopify.com/admin/oauth/access_token",
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())["access_token"]


TOKEN = get_token()
HEADERS = {"X-Shopify-Access-Token": TOKEN, "Accept": "application/json"}


def rest(path, params=None, method="GET", body=None, retries=5):
    url = f"https://{STORE}.myshopify.com/admin/api/{API_VERSION}{path}"
    if params:
        url += ("&" if "?" in url else "?") + urllib.parse.urlencode(params)
    data = json.dumps(body).encode() if body is not None else None
    headers = dict(HEADERS)
    if body is not None:
        headers["Content-Type"] = "application/json"
    for attempt in range(retries):
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(int(e.headers.get("Retry-After", "2")))
                continue
            if e.code >= 500 and attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
            raise
    raise RuntimeError(f"REST call failed after {retries} attempts: {method} {path}")


def graphql(query, variables=None):
    req = urllib.request.Request(
        f"https://{STORE}.myshopify.com/admin/api/{API_VERSION}/graphql.json",
        data=json.dumps({"query": query, "variables": variables or {}}).encode(),
        headers={**HEADERS, "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=60) as r:
        out = json.loads(r.read())
    if "errors" in out:
        raise RuntimeError(f"GraphQL error: {out['errors']}")
    return out["data"]


def find_dawn_theme():
    themes = rest("/themes.json")["themes"]
    # Exact name match first, then case-insensitive contains.
    for t in themes:
        if t["name"] == THEME_NAME:
            return t
    for t in themes:
        if THEME_NAME.lower() in t["name"].lower():
            return t
    raise SystemExit(
        f"ERROR: no theme matching {THEME_NAME!r}. Candidates: "
        + ", ".join(f"{t['name']} (id={t['id']}, role={t['role']})" for t in themes)
    )


def pull_theme(theme):
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    listing = rest(f"/themes/{theme['id']}/assets.json")["assets"]
    print(f"Backing up {len(listing)} assets from {theme['name']} (id={theme['id']}) → {BACKUP_DIR}")

    binary_manifest = []
    for i, meta in enumerate(listing, 1):
        key = meta["key"]
        dest = BACKUP_DIR / key
        dest.parent.mkdir(parents=True, exist_ok=True)
        # Fetch full asset (listing only gives metadata).
        resp = rest(f"/themes/{theme['id']}/assets.json", params={"asset[key]": key})
        asset = resp["asset"]
        if asset.get("value") is not None:
            dest.write_text(asset["value"], encoding="utf-8")
        elif asset.get("attachment"):
            raw = base64.b64decode(asset["attachment"])
            dest.write_bytes(raw)
            binary_manifest.append(f"{key}\t{len(raw)} bytes")
        else:
            print(f"  WARN: {key} has neither value nor attachment; skipping")
        if i % 25 == 0 or i == len(listing):
            print(f"  [{i}/{len(listing)}] {key}")
        # light rate limit: ~5 req/s
        time.sleep(0.2)

    (BACKUP_DIR / "BINARY_ASSETS_MANIFEST.txt").write_text(
        "\n".join(binary_manifest) + ("\n" if binary_manifest else ""),
        encoding="utf-8",
    )
    meta = {
        "source_theme": {"id": theme["id"], "name": theme["name"], "role": theme["role"]},
        "snapshot_date": TODAY,
        "asset_count": len(listing),
        "binary_asset_count": len(binary_manifest),
        "api_version": API_VERSION,
    }
    (BACKUP_DIR / "snapshot.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    print(f"Backup complete: {len(listing)} assets, {len(binary_manifest)} binary")
    return meta


def duplicate_theme(theme):
    # themeDuplicate exists in 2024-10+; use GraphQL for the clean path.
    gid = f"gid://shopify/OnlineStoreTheme/{theme['id']}"
    query = """
    mutation ThemeDuplicate($id: ID!, $name: String!) {
      themeDuplicate(id: $id, name: $name) {
        theme { id name role }
        userErrors { field message }
      }
    }
    """
    data = graphql(query, {"id": gid, "name": DUPLICATE_NAME})
    result = data["themeDuplicate"]
    if result["userErrors"]:
        raise RuntimeError(f"themeDuplicate userErrors: {result['userErrors']}")
    new = result["theme"]
    print(f"Duplicated theme → {new['name']} (id={new['id']}, role={new['role']})")
    return new


def main():
    theme = find_dawn_theme()
    print(f"Found source theme: {theme['name']} (id={theme['id']}, role={theme['role']})")

    snapshot = None
    if os.environ.get("SKIP_BACKUP") != "1":
        snapshot = pull_theme(theme)

    duplicate = None
    if os.environ.get("SKIP_DUPLICATE") != "1":
        duplicate = duplicate_theme(theme)

    summary = {"source": theme, "snapshot": snapshot, "duplicate": duplicate}
    print(json.dumps(summary, indent=2, default=str))


if __name__ == "__main__":
    main()
