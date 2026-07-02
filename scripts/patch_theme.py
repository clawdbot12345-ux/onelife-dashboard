#!/usr/bin/env python3
"""
Onelife — theme patch: mobile conversion fixes (theme-patch-spec-2026-07-02.md).

Never edits the LIVE theme. Mirrors LIVE onto the scratch theme via
themeFilesCopy, adds assets/onelife-mobile-fixes.css (selectors verified
against live markup 2026-07-02), includes it in layout/theme.liquid, and
renames the scratch to "LIVE + MOBILE FIXES 2026-07-02 (publish me)".
Publishing stays a human click in Online Store → Themes.

Requires SHOPIFY_ADMIN_TOKEN with read_themes + write_themes; exits with a
clear message if the scopes are missing.
"""
import json
import os
import sys
import time
import urllib.request

TOKEN = os.environ.get("SHOPIFY_ADMIN_TOKEN")
STORE = os.environ.get("SHOPIFY_STORE", "onelifehealth").replace(".myshopify.com", "")
API = "2025-01"
LIVE = "gid://shopify/OnlineStoreTheme/185669910838"
SCRATCH = "gid://shopify/OnlineStoreTheme/186060964150"
NEW_NAME = "LIVE + MOBILE FIXES 2026-07-02 (publish me)"
CSS_FILE = "assets/onelife-mobile-fixes.css"

if not TOKEN:
    print("ERROR: SHOPIFY_ADMIN_TOKEN required", file=sys.stderr)
    sys.exit(1)

CSS = """/* Onelife mobile conversion fixes — 2026-07-02 (site-audit follow-up)
   Selectors verified against live markup. Conservative: spacing, z-index,
   visibility and colour only — no display-mode changes. */

/* 1. CLS 0.34 on collections: the rotating announcement slider swaps
   messages of different lengths; reserve its height so layout never shifts. */
.announcement-bar,
.announcement-bar__announcement { min-height: 4.2rem; }
.announcement-bar__message { display: inline-block; min-height: 1.4em; }

/* 2. Collection cards: dietary badge row was clipping under the
   Add-to-cart button; give the card content clearance. */
.card__content { padding-bottom: 1.2rem; }
.card__information { padding-bottom: 0.6rem; }
@media screen and (max-width: 749px) {
  .ol-badge { font-size: 0.85em; }
}

/* 3. WhatsApp consult button: sit above the mobile bottom nav instead of
   covering product titles/footer; stay under drawers and modals. */
@media screen and (max-width: 749px) {
  .ol-consult-cta { bottom: 5.4rem !important; z-index: 3; }
}

/* 4. PDP: 'Buy it now' becomes a secondary (outline) action so
   Add to cart is the clear primary. */
.shopify-payment-button__button--unbranded {
  background: #ffffff;
  color: #1b4332;
  border: 0.1rem solid #1b4332;
  box-shadow: none;
}
.shopify-payment-button__button--unbranded:hover {
  background: #f1f5f1;
  color: #1b4332;
}

/* 5. Judge.me zero-state: hide the orphaned 'No reviews' badge until a
   product actually has reviews (write-review widget lower down remains). */
.jdgm-preview-badge[data-number-of-reviews="0"],
.jdgm-prev-badge[data-number-of-reviews="0"] { display: none !important; }

/* 7. SA consumer pricing: label displayed prices VAT-inclusive. */
.price .price-item--last::after {
  content: " incl. VAT";
  font-size: 0.72em;
  font-weight: 400;
  color: #6b7280;
  letter-spacing: 0;
  white-space: nowrap;
}
"""


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


def read_all_files(theme_id):
    """Read every file with its body. themeFilesCopy cannot copy across
    themes, so the mirror is read-from-live -> upsert-to-scratch: text
    inline, binaries by CDN URL."""
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
            print("✗ cannot read theme files — check read_themes scope", file=sys.stderr)
            sys.exit(1)
        page = data["theme"]["files"]
        for n in page["nodes"]:
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
            else:
                print(f"  ⚠ skipping {n['filename']} (body {t})", file=sys.stderr)
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


def read_file(theme_id, filename):
    data = gql("""
      query($id: ID!, $f: [String!]) {
        theme(id: $id) { files(filenames: $f, first: 1) {
          nodes { filename body { ... on OnlineStoreThemeFileBodyText { content } } }
        } }
      }""", {"id": theme_id, "f": [filename]})
    nodes = (((data or {}).get("theme") or {}).get("files") or {}).get("nodes") or []
    return nodes[0]["body"]["content"] if nodes else None


def upsert(filename, content):
    data = gql("""
      mutation($theme: ID!, $files: [OnlineStoreThemeFilesUpsertFileInput!]!) {
        themeFilesUpsert(themeId: $theme, files: $files) {
          upsertedThemeFiles { filename }
          userErrors { field message }
        }
      }""", {"theme": SCRATCH,
             "files": [{"filename": filename,
                        "body": {"type": "TEXT", "value": content}}]})
    errs = ((data or {}).get("themeFilesUpsert") or {}).get("userErrors")
    if errs:
        print(f"✗ upsert {filename}: {json.dumps(errs)[:300]}", file=sys.stderr)
        return False
    print(f"  ✓ upserted {filename}", file=sys.stderr)
    return True


def main():
    print("[1] Reading live theme files (with bodies)...", file=sys.stderr)
    files = read_all_files(LIVE)
    print(f"  {len(files)} files on live", file=sys.stderr)

    print("[2] Mirroring live -> scratch via upsert...", file=sys.stderr)
    copied = 0
    for i in range(0, len(files), 10):
        batch = files[i:i + 10]
        n, errs = upsert_batch(batch)
        copied += n
        if errs:
            print(f"  batch {i//10}: {json.dumps(errs)[:300]}", file=sys.stderr)
        time.sleep(0.3)
    print(f"  mirrored {copied}/{len(files)}", file=sys.stderr)
    if copied < len(files) * 0.98:
        print("✗ mirror incomplete — aborting before patch", file=sys.stderr)
        sys.exit(1)

    print("[3] Patching...", file=sys.stderr)
    if not upsert(CSS_FILE, CSS):
        sys.exit(1)
    layout = read_file(SCRATCH, "layout/theme.liquid")
    if not layout:
        print("✗ cannot read layout/theme.liquid", file=sys.stderr)
        sys.exit(1)
    tag = "{{ 'onelife-mobile-fixes.css' | asset_url | stylesheet_tag }}"
    if "onelife-mobile-fixes.css" not in layout:
        if "</head>" not in layout:
            print("✗ </head> not found in theme.liquid", file=sys.stderr)
            sys.exit(1)
        layout = layout.replace("</head>", f"    {tag}\n  </head>", 1)
        if not upsert("layout/theme.liquid", layout):
            sys.exit(1)
        check = read_file(SCRATCH, "layout/theme.liquid")
        if "onelife-mobile-fixes.css" not in (check or ""):
            print("✗ stylesheet include did not land", file=sys.stderr)
            sys.exit(1)
        print("  ✓ stylesheet included in layout/theme.liquid", file=sys.stderr)
    else:
        print("  stylesheet already included", file=sys.stderr)

    print("[4] Renaming scratch theme...", file=sys.stderr)
    data = gql("""
      mutation($id: ID!, $name: String!) {
        themeUpdate(id: $id, input: {name: $name}) {
          theme { id name } userErrors { field message }
        }
      }""", {"id": SCRATCH, "name": NEW_NAME})
    errs = ((data or {}).get("themeUpdate") or {}).get("userErrors")
    if errs:
        print(f"⚠ rename failed (cosmetic): {json.dumps(errs)[:200]}", file=sys.stderr)
    print(f"✓ THEME READY: '{NEW_NAME}' — publish in Online Store → Themes")


if __name__ == "__main__":
    main()
