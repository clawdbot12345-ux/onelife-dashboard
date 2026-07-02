#!/usr/bin/env python3
"""
Onelife — theme pipeline v2 (premium discipline pass).

Roles after the 2026-07-02 publish:
  MAIN    = 186060964150  "LIVE + MOBILE FIXES 2026-07-02" (published)
  SCRATCH = 185669910838  (previous live — safe to overwrite)

Modes (env MODE):
  dump  — fetch selected source files from MAIN into reports/theme-src/
          (so CSS/Liquid edits are written against real selectors/settings)
  patch — mirror MAIN -> SCRATCH (read+upsert), then apply every file under
          theme-overrides/ (repo) on top, rename SCRATCH for publishing.

Requires SHOPIFY_ADMIN_TOKEN (read_themes + write_themes).
"""
import json
import os
import sys
import time
import urllib.request

TOKEN = os.environ.get("SHOPIFY_ADMIN_TOKEN")
STORE = os.environ.get("SHOPIFY_STORE", "onelifehealth").replace(".myshopify.com", "")
API = "2025-01"
THEME_POOL = {"gid://shopify/OnlineStoreTheme/186060964150",
              "gid://shopify/OnlineStoreTheme/185669910838"}
MAIN = None      # resolved at runtime — publishes keep flipping the roles
SCRATCH = None
MODE = os.environ.get("MODE", "patch")
NEW_NAME = os.environ.get("NEW_NAME", "PREMIUM PASS 2 — (publish me)")
DUMP_DIR = "reports/theme-src"
OVERRIDES_DIR = "theme-overrides"

DUMP_PREFIXES = ("sections/", "snippets/")
DUMP_EXACT = {"layout/theme.liquid", "config/settings_data.json",
              "config/settings_schema.json", "templates/index.json",
              "templates/product.json", "assets/onelife-mobile-fixes.css"}
DUMP_MATCH = ("ol-", "card", "announcement", "header", "price",
              "buy-buttons", "main-product", "footer", "quiz",
              "cart-drawer", "cart-notification", "cart-items",
              "free-shipping", "shipping-threshold", "threshold",
              "tag-guide", "delivery-estimate", "trust", "store-stock")

if not TOKEN:
    print("ERROR: SHOPIFY_ADMIN_TOKEN required", file=sys.stderr)
    sys.exit(1)


def gql(query, variables=None):
    body = json.dumps({"query": query, "variables": variables or {}}).encode()
    for attempt in range(5):
        req = urllib.request.Request(
            f"https://{STORE}.myshopify.com/admin/api/{API}/graphql.json",
            data=body, headers={"X-Shopify-Access-Token": TOKEN,
                                "Content-Type": "application/json"}, method="POST")
        try:
            with urllib.request.urlopen(req, timeout=120) as resp:
                out = json.loads(resp.read())
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 4:
                time.sleep(4)
                continue
            print(f"HTTP {e.code}: {e.read().decode()[:300]}", file=sys.stderr)
            return None
        errs = out.get("errors") or []
        if any("THROTTLED" in str(e) for e in errs) and attempt < 4:
            time.sleep(4)
            continue
        if errs:
            print(f"GraphQL errors: {json.dumps(errs)[:500]}", file=sys.stderr)
            return None
        return out["data"]
    return None


def read_all_files(theme_id, want=None):
    """Read files (with bodies). want=None -> all; else filename filter set."""
    out, cursor = [], None
    while True:
        data = gql("""
          query($id: ID!, $cursor: String) {
            theme(id: $id) {
              files(first: 50, after: $cursor) {
                pageInfo { hasNextPage endCursor }
                nodes {
                  filename
                  body {
                    __typename
                    ... on OnlineStoreThemeFileBodyText { content }
                    ... on OnlineStoreThemeFileBodyUrl { url }
                    ... on OnlineStoreThemeFileBodyBase64 { contentBase64 }
                  }
                }
              }
            }
          }""", {"id": theme_id, "cursor": cursor})
        if not data or not data.get("theme"):
            print("✗ cannot read theme files", file=sys.stderr)
            sys.exit(1)
        page = data["theme"]["files"]
        for n in page["nodes"]:
            if want is not None and n["filename"] not in want:
                continue
            body = n.get("body") or {}
            t = body.get("__typename")
            if t == "OnlineStoreThemeFileBodyText":
                out.append({"filename": n["filename"],
                            "body": {"type": "TEXT", "value": body["content"]}})
            elif t == "OnlineStoreThemeFileBodyUrl":
                out.append({"filename": n["filename"],
                            "body": {"type": "URL", "value": body["url"]}})
            elif t == "OnlineStoreThemeFileBodyBase64":
                out.append({"filename": n["filename"],
                            "body": {"type": "BASE64", "value": body["contentBase64"]}})
        if not page["pageInfo"]["hasNextPage"]:
            return out
        cursor = page["pageInfo"]["endCursor"]


def upsert_batch(files):
    data = gql("""
      mutation($theme: ID!, $files: [OnlineStoreThemeFilesUpsertFileInput!]!) {
        themeFilesUpsert(themeId: $theme, files: $files) {
          upsertedThemeFiles { filename }
          userErrors { field message }
        }
      }""", {"theme": SCRATCH, "files": files})
    if not data:
        return 0, ["request failed"]
    payload = data["themeFilesUpsert"]
    return len(payload.get("upsertedThemeFiles") or []), payload.get("userErrors") or []


def wanted_for_dump(filename):
    if filename in DUMP_EXACT:
        return True
    if filename.startswith(DUMP_PREFIXES):
        return any(m in filename for m in DUMP_MATCH)
    return False


def mode_dump():
    print("[dump] listing MAIN files...", file=sys.stderr)
    names_data, cursor, names = None, None, []
    while True:
        names_data = gql("""
          query($id: ID!, $cursor: String) {
            theme(id: $id) { files(first: 250, after: $cursor) {
              pageInfo { hasNextPage endCursor } nodes { filename } } }
          }""", {"id": MAIN, "cursor": cursor})
        page = names_data["theme"]["files"]
        names += [n["filename"] for n in page["nodes"]]
        if not page["pageInfo"]["hasNextPage"]:
            break
        cursor = page["pageInfo"]["endCursor"]
    want = {n for n in names if wanted_for_dump(n)}
    print(f"[dump] fetching {len(want)}/{len(names)} files", file=sys.stderr)
    files = read_all_files(MAIN, want=want)
    os.makedirs(DUMP_DIR, exist_ok=True)
    written = 0
    for f in files:
        if f["body"]["type"] != "TEXT":
            continue
        path = os.path.join(DUMP_DIR, f["filename"].replace("/", "__"))
        with open(path, "w") as fh:
            fh.write(f["body"]["value"])
        written += 1
    print(f"✓ dumped {written} text files to {DUMP_DIR}/")


def mode_patch():
    print("[patch 1/3] mirroring MAIN -> SCRATCH...", file=sys.stderr)
    files = read_all_files(MAIN)
    copied = 0
    for i in range(0, len(files), 10):
        n, errs = upsert_batch(files[i:i + 10])
        copied += n
        if errs:
            print(f"  batch {i//10}: {json.dumps(errs)[:300]}", file=sys.stderr)
        time.sleep(0.3)
    print(f"  mirrored {copied}/{len(files)}", file=sys.stderr)
    if copied < len(files) * 0.98:
        print("✗ mirror incomplete — aborting", file=sys.stderr)
        sys.exit(1)

    print("[patch 2/3] applying theme-overrides/ ...", file=sys.stderr)
    overrides = []
    for root, _dirs, fnames in os.walk(OVERRIDES_DIR):
        for fn in fnames:
            path = os.path.join(root, fn)
            rel = os.path.relpath(path, OVERRIDES_DIR)
            with open(path) as fh:
                overrides.append({"filename": rel,
                                  "body": {"type": "TEXT", "value": fh.read()}})
    if not overrides:
        print("✗ no overrides found", file=sys.stderr)
        sys.exit(1)
    applied = 0
    for i in range(0, len(overrides), 5):
        n, errs = upsert_batch(overrides[i:i + 5])
        applied += n
        if errs:
            print(f"  override errs: {json.dumps(errs)[:400]}", file=sys.stderr)
        time.sleep(0.3)
    print(f"  applied {applied}/{len(overrides)} overrides", file=sys.stderr)
    if applied < len(overrides):
        sys.exit(1)

    print("[patch 3/3] renaming...", file=sys.stderr)
    gql("""mutation($id: ID!, $name: String!) {
      themeUpdate(id: $id, input: {name: $name}) {
        theme { id name } userErrors { field message } } }""",
        {"id": SCRATCH, "name": NEW_NAME})
    print(f"✓ THEME READY: '{NEW_NAME}'")


def resolve_roles():
    global MAIN, SCRATCH
    data = gql("query { themes(first: 5, roles: [MAIN]) { nodes { id name } } }")
    nodes = (((data or {}).get("themes") or {}).get("nodes")) or []
    if not nodes:
        print("✗ cannot resolve MAIN theme", file=sys.stderr)
        sys.exit(1)
    MAIN = nodes[0]["id"]
    others = THEME_POOL - {MAIN}
    if MAIN in THEME_POOL and others:
        SCRATCH = next(iter(others))
    else:
        print(f"✗ MAIN {MAIN} not in known pool — refusing to guess a scratch",
              file=sys.stderr)
        sys.exit(1)
    print(f"roles: MAIN={MAIN} ('{nodes[0]['name']}') SCRATCH={SCRATCH}",
          file=sys.stderr)


if __name__ == "__main__":
    resolve_roles()
    (mode_dump if MODE == "dump" else mode_patch)()
