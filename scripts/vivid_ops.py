#!/usr/bin/env python3
"""Remote hands for the Vivid Health redesign session.

Modes (read from .github/triggers/vivid-ops JSON: {"mode": "...", ...}):

  pull   — fetch every Vivid product (full body_html/images/variants) into
           vivid/backend/products.json, list all themes' names/roles, list
           assets for the LIVE theme and the TARGET theme, and download any
           asset whose key mentions vivid (sections, templates, snippets)
           into vivid/backend/theme-<id>/. Sanitized; no tokens stored.

  apply  — apply staged changes:
           * vivid/backend/apply/product-updates.json:
               [{"id": 123, "title": "...", "body_html": "...", "tags": "..."}]
             Only provided fields are sent (REST PUT products/{id}.json).
           * vivid/backend/apply/theme-assets/<theme_id>/<asset key with __ for />
             Each file is PUT to that theme as the asset key.
           * vivid/backend/apply/pages.json:
               [{"title": "...", "handle": "...", "body_html": "...", "template_suffix": null}]
             Creates pages that don't exist yet (by handle); updates if exist.
           Writes vivid/backend/apply-result.json with per-item status.

The workflow commits changed files back to the branch afterwards.
"""
import glob
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API = "2025-01"
OUT = "vivid/backend"

def _cfg():
    trig = ".github/triggers/vivid-ops"
    if os.path.exists(trig):
        try:
            return json.loads(open(trig).read())
        except Exception:
            return {}
    return {}

CFG = _cfg()
STORE = (CFG.get("store") or os.environ.get("VIVID_STORE") or
         os.environ.get("SHOPIFY_STORE", "onelifehealth")).replace(".myshopify.com", "").strip()
BASE = f"https://{STORE}.myshopify.com"


def _client_credentials(cid, csec):
    body = urllib.parse.urlencode({
        "grant_type": "client_credentials", "client_id": cid, "client_secret": csec,
    }).encode()
    req = urllib.request.Request(
        f"{BASE}/admin/oauth/access_token", data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())["access_token"]


def _resolve_token():
    """Per-store credentials. For the dedicated Vivid store, VIVID_* wins;
    never fall back to the One Life token for a non-onelife store."""
    is_onelife = STORE == "onelifehealth"
    direct = [os.environ.get("VIVID_ADMIN_TOKEN")]
    if is_onelife:
        direct.append(os.environ.get("SHOPIFY_ADMIN_TOKEN"))
    for t in direct:
        if t and t.strip():
            return t.strip()
    pairs = [(os.environ.get("VIVID_CLIENT_ID"), os.environ.get("VIVID_CLIENT_SECRET"))]
    if is_onelife:
        pairs.append((os.environ.get("SHOPIFY_CLIENT_ID"), os.environ.get("SHOPIFY_CLIENT_SECRET")))
    for cid, csec in pairs:
        if cid and csec:
            try:
                return _client_credentials(cid.strip(), csec.strip())
            except Exception as e:  # noqa: BLE001
                print(f"client_credentials failed for {cid[:8]}…: {e}", file=sys.stderr)
    return None


TOKEN = _resolve_token()
if not TOKEN:
    print(f"ERROR: no working credentials for store {STORE}", file=sys.stderr)
    sys.exit(1)

HDRS = {"X-Shopify-Access-Token": TOKEN, "Accept": "application/json",
        "Content-Type": "application/json"}


def req(method, path, payload=None, retries=5):
    url = BASE + path
    data = json.dumps(payload).encode() if payload is not None else None
    for attempt in range(retries):
        r = urllib.request.Request(url, data=data, headers=HDRS, method=method)
        try:
            with urllib.request.urlopen(r, timeout=60) as resp:
                body = resp.read()
                return resp.status, json.loads(body) if body else {}, resp.headers.get("Link", "")
        except urllib.error.HTTPError as e:
            if e.code == 429:
                time.sleep(float(e.headers.get("Retry-After", "2")))
                continue
            try:
                detail = e.read().decode()[:500]
            except Exception:
                detail = ""
            return e.code, {"error": detail}, ""
        except Exception as e:  # noqa: BLE001
            if attempt == retries - 1:
                return 0, {"error": str(e)}, ""
            time.sleep(2)
    return 0, {"error": "retries exhausted"}, ""


def next_page(link):
    for part in (link or "").split(","):
        if 'rel="next"' in part:
            import re
            m = re.search(r"page_info=([^&>]+)", part)
            if m:
                return m.group(1)
    return None


def fetch_vivid_products():
    products, seen = [], set()
    for vendor in ("VIVID HEALTH", "Vivid Health"):
        page_info = None
        while True:
            qs = {"limit": 250, "vendor": vendor}
            if page_info:
                qs = {"limit": 250, "page_info": page_info}
            code, data, link = req("GET", f"/admin/api/{API}/products.json?{urllib.parse.urlencode(qs)}")
            if code != 200:
                print(f"  vendor {vendor}: HTTP {code} {data}")
                break
            for p in data.get("products", []):
                if p["id"] not in seen:
                    seen.add(p["id"])
                    products.append(p)
            page_info = next_page(link)
            if not page_info:
                break
    # bundles may carry another vendor — catch by title
    page_info = None
    while True:
        qs = {"limit": 250, "title": "Vivid"}
        if page_info:
            qs = {"limit": 250, "page_info": page_info}
        code, data, link = req("GET", f"/admin/api/{API}/products.json?{urllib.parse.urlencode(qs)}")
        if code != 200:
            break
        for p in data.get("products", []):
            if p["id"] not in seen:
                seen.add(p["id"])
                products.append(p)
        page_info = next_page(link)
        if not page_info:
            break
    return products


def do_pull(cfg):
    os.makedirs(OUT, exist_ok=True)
    products = fetch_vivid_products()
    with open(f"{OUT}/products.json", "w") as f:
        json.dump(products, f, indent=1)
    print(f"pulled {len(products)} vivid products")

    code, tdata, _ = req("GET", f"/admin/api/{API}/themes.json")
    themes = tdata.get("themes", []) if code == 200 else []
    with open(f"{OUT}/themes.json", "w") as f:
        json.dump([{k: t.get(k) for k in ("id", "name", "role", "updated_at")} for t in themes], f, indent=1)

    live = next((t for t in themes if t.get("role") == "main"), None)
    target_id = cfg.get("target_theme_id")
    targets = [t for t in ([live] if live else [])]
    if target_id:
        t = next((x for x in themes if x["id"] == target_id), None)
        if t and t not in targets:
            targets.append(t)

    for t in targets:
        tid = t["id"]
        code, adata, _ = req("GET", f"/admin/api/{API}/themes/{tid}/assets.json")
        if code != 200:
            print(f"theme {tid}: assets list HTTP {code}")
            continue
        keys = [a["key"] for a in adata.get("assets", [])]
        with open(f"{OUT}/theme-{tid}-assets.txt", "w") as f:
            f.write("\n".join(sorted(keys)))
        want = [k for k in keys if ("vivid" in k.lower())]
        for extra in cfg.get("extra_assets", []):
            if extra in keys and extra not in want:
                want.append(extra)
        os.makedirs(f"{OUT}/theme-{tid}", exist_ok=True)
        for key in want:
            code, ad, _ = req("GET", f"/admin/api/{API}/themes/{tid}/assets.json?asset%5Bkey%5D={urllib.parse.quote(key)}")
            if code != 200:
                print(f"  {key}: HTTP {code}")
                continue
            asset = ad.get("asset", {})
            val = asset.get("value")
            fname = key.replace("/", "__")
            if val is not None:
                with open(f"{OUT}/theme-{tid}/{fname}", "w") as f:
                    f.write(val)
            else:
                with open(f"{OUT}/theme-{tid}/{fname}.b64info", "w") as f:
                    f.write(json.dumps({"key": key, "binary": True,
                                        "public_url": asset.get("public_url")}))
            print(f"  saved theme-{tid}/{fname}")
        print(f"theme {tid} ({t['name']}): {len(want)} vivid-ish assets of {len(keys)}")

    code, pdata, _ = req("GET", f"/admin/api/{API}/pages.json?limit=250")
    if code == 200:
        pages = [{"id": p["id"], "title": p["title"], "handle": p["handle"],
                  "template_suffix": p.get("template_suffix"),
                  "body_len": len(p.get("body_html") or ""),
                  "body_html": p.get("body_html")}
                 for p in pdata.get("pages", [])]
        with open(f"{OUT}/pages.json", "w") as f:
            json.dump(pages, f, indent=1)
        print(f"pulled {len(pages)} pages")
    for kind in ("smart_collections", "custom_collections"):
        code, cdata, _ = req("GET", f"/admin/api/{API}/{kind}.json?limit=250")
        if code == 200:
            with open(f"{OUT}/{kind}.json", "w") as f:
                json.dump(cdata.get(kind, []), f, indent=1)


def reorder_hero_images():
    """Move each product's *-hero image to position 1 (fixes og:image and
    demotes the old cold studio masters)."""
    products = fetch_vivid_products()
    moved = 0
    for p in products:
        imgs = p.get("images") or []
        if len(imgs) < 2:
            continue
        hero = next((i for i in imgs if "-hero" in (i.get("src") or "").rsplit("/", 1)[-1].lower()), None)
        if hero and imgs[0]["id"] != hero["id"]:
            code, d, _ = req("PUT", f"/admin/api/{API}/products/{p['id']}/images/{hero['id']}.json",
                             {"image": {"id": hero["id"], "position": 1}})
            if 200 <= code < 300:
                moved += 1
            else:
                print(f"  reorder {p['handle']}: HTTP {code}")
            time.sleep(0.55)
    print(f"hero images moved to position 1: {moved}")


def do_apply(cfg):
    results = []
    pu_path = f"{OUT}/apply/product-updates.json"
    if os.path.exists(pu_path):
        updates = json.load(open(pu_path))
        for u in updates:
            pid = u.pop("id")
            payload = {"product": {"id": pid, **u}}
            code, data, _ = req("PUT", f"/admin/api/{API}/products/{pid}.json", payload)
            results.append({"type": "product", "id": pid, "status": code,
                            "fields": list(u.keys()),
                            "error": data.get("error") or data.get("errors")})
            print(f"product {pid}: {code} {list(u.keys())}")
            time.sleep(0.55)

    for path in sorted(glob.glob(f"{OUT}/apply/theme-assets/*/*")):
        parts = path.split("/")
        tid = parts[-2]
        key = parts[-1].replace("__", "/")
        value = open(path).read()
        code, data, _ = req("PUT", f"/admin/api/{API}/themes/{tid}/assets.json",
                            {"asset": {"key": key, "value": value}})
        results.append({"type": "asset", "theme": tid, "key": key, "status": code,
                        "error": data.get("error") or data.get("errors")})
        print(f"asset {tid}/{key}: {code}")
        time.sleep(0.55)

    pg_path = f"{OUT}/apply/pages.json"
    if os.path.exists(pg_path):
        code, existing, _ = req("GET", f"/admin/api/{API}/pages.json?limit=250")
        by_handle = {p["handle"]: p for p in existing.get("pages", [])} if code == 200 else {}
        for page in json.load(open(pg_path)):
            h = page.get("handle")
            if h in by_handle:
                pid = by_handle[h]["id"]
                code, data, _ = req("PUT", f"/admin/api/{API}/pages/{pid}.json",
                                    {"page": {"id": pid, **page}})
                results.append({"type": "page-update", "handle": h, "status": code,
                                "error": data.get("error") or data.get("errors")})
            else:
                code, data, _ = req("POST", f"/admin/api/{API}/pages.json", {"page": page})
                results.append({"type": "page-create", "handle": h, "status": code,
                                "error": data.get("error") or data.get("errors")})
            print(f"page {h}: {code}")
            time.sleep(0.55)

    os.makedirs(OUT, exist_ok=True)
    with open(f"{OUT}/apply-result.json", "w") as f:
        json.dump(results, f, indent=1)
    bad = [r for r in results if not (200 <= (r["status"] or 0) < 300)]
    print(f"applied {len(results)} ops, {len(bad)} failed")
    if cfg.get("reorder_hero_images"):
        reorder_hero_images()


def do_apply_prices(cfg):
    """Apply a price-rounding plan CSV (variant-level) with a drift check."""
    import csv as _csv
    plan = cfg.get("plan", "reports/price-rounding/plan-2026-07-02T125406Z.csv")
    rows = list(_csv.DictReader(open(plan)))
    print(f"plan rows: {len(rows)} against {STORE}")
    results, counts = [], {"applied": 0, "already": 0, "drifted": 0, "failed": 0}
    for i, r in enumerate(rows):
        vid = r["variant_id"].split("/")[-1]
        code, data, _ = req("GET", f"/admin/api/{API}/variants/{vid}.json")
        if code != 200:
            counts["failed"] += 1
            results.append({"vid": vid, "status": f"get {code}"})
            continue
        cur = data["variant"]["price"]
        try:
            if abs(float(cur) - float(r["new_price"])) < 0.005:
                counts["already"] += 1
                continue
            if abs(float(cur) - float(r["old_price"])) > 0.005:
                counts["drifted"] += 1
                results.append({"vid": vid, "status": "drifted", "live": cur,
                                "plan_old": r["old_price"]})
                continue
        except ValueError:
            counts["failed"] += 1
            results.append({"vid": vid, "status": "bad number", "live": cur})
            continue
        payload = {"variant": {"id": int(vid), "price": r["new_price"]}}
        if (r.get("new_compare_at") or "").strip():
            payload["variant"]["compare_at_price"] = r["new_compare_at"]
        code2, d2, _ = req("PUT", f"/admin/api/{API}/variants/{vid}.json", payload)
        if 200 <= code2 < 300:
            counts["applied"] += 1
        else:
            counts["failed"] += 1
            results.append({"vid": vid, "status": f"put {code2}",
                            "error": d2.get("error") or d2.get("errors")})
        if i % 100 == 0:
            print(f"  {i}/{len(rows)} {counts}")
        time.sleep(0.30)
    out = {"counts": counts, "issues": results[:500]}
    os.makedirs("reports/price-rounding", exist_ok=True)
    with open("reports/price-rounding/apply-result.json", "w") as f:
        json.dump(out, f, indent=1)
    print(f"DONE {counts}")


def do_publish(cfg):
    tid = cfg.get("theme_id")
    if not tid:
        print("publish: theme_id required", file=sys.stderr)
        sys.exit(1)
    code, before, _ = req("GET", f"/admin/api/{API}/themes.json")
    prev_main = next((t["id"] for t in before.get("themes", []) if t.get("role") == "main"), None)
    code, data, _ = req("PUT", f"/admin/api/{API}/themes/{tid}.json",
                        {"theme": {"id": tid, "role": "main"}})
    result = {"published": tid, "status": code, "previous_main": prev_main,
              "error": data.get("error") or data.get("errors")}
    os.makedirs(OUT, exist_ok=True)
    with open(f"{OUT}/publish-result.json", "w") as f:
        json.dump(result, f, indent=1)
    print(json.dumps(result))


def main():
    cfg = CFG
    mode = cfg.get("mode", "pull")
    print(f"store={STORE}")
    print(f"mode={mode} cfg={ {k: v for k, v in cfg.items() if k != 'mode'} }")
    if mode == "pull":
        do_pull(cfg)
    elif mode == "apply":
        do_apply(cfg)
    elif mode == "publish":
        do_publish(cfg)
    elif mode == "apply_prices":
        do_apply_prices(cfg)
    else:
        print(f"unknown mode {mode}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
