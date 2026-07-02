#!/usr/bin/env python3
"""Probe the Shopify store the 'vivid claude review' custom app can reach.

Reports (sanitized — never prints tokens): shop identity, granted API scopes,
all themes (to locate the draft Vivid theme), product/page counts, locations.
Writes reports/vivid-store-probe.md + .json for the redesign session to read.

Auth resolution order:
  1. Direct Admin API tokens from any of several candidate secret names
  2. Client-credentials exchange (SHOPIFY_CLIENT_ID/SECRET) — dedup_analyzer pattern
Optionally probes a second store if VIVID_STORE is set (defaults to onelifehealth).
"""
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

API_VERSION = "2025-01"

TOKEN_CANDIDATES = [
    "SHOPIFY_ADMIN_TOKEN",
    "VIVID_ADMIN_TOKEN",
    "VIVID_SHOPIFY_TOKEN",
    "SHOPIFY_VIVID_TOKEN",
    "VIVID_CLAUDE_REVIEW_TOKEN",
]

STORES = []
for s in [os.environ.get("VIVID_STORE"), os.environ.get("SHOPIFY_STORE", "onelifehealth")]:
    if s:
        s = s.replace(".myshopify.com", "").strip()
        if s and s not in STORES:
            STORES.append(s)


def api(store, token, path, method="GET"):
    url = f"https://{store}.myshopify.com{path}"
    req = urllib.request.Request(
        url, headers={"X-Shopify-Access-Token": token, "Accept": "application/json"},
        method=method)
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        try:
            body = e.read().decode()[:300]
        except Exception:
            body = ""
        return e.code, {"error": body}
    except Exception as e:  # noqa: BLE001
        return 0, {"error": str(e)}


def client_credentials_token(store):
    if store == "onelifehealth":
        cid, csec = os.environ.get("SHOPIFY_CLIENT_ID"), os.environ.get("SHOPIFY_CLIENT_SECRET")
    else:
        cid, csec = os.environ.get("VIVID_CLIENT_ID"), os.environ.get("VIVID_CLIENT_SECRET")
    if not (cid and csec):
        return None, "no client id/secret set"
    body = urllib.parse.urlencode({
        "grant_type": "client_credentials", "client_id": cid, "client_secret": csec,
    }).encode()
    req = urllib.request.Request(
        f"https://{store}.myshopify.com/admin/oauth/access_token", data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())["access_token"], "client_credentials ok"
    except urllib.error.HTTPError as e:
        try:
            detail = e.read().decode()[:200]
        except Exception:
            detail = ""
        return None, f"client_credentials HTTP {e.code}: {detail}"
    except Exception as e:  # noqa: BLE001
        return None, f"client_credentials error: {e}"


def probe_store(store):
    out = {"store": f"{store}.myshopify.com", "auth": None, "auth_source": None}
    token = None
    is_onelife = store == "onelifehealth"
    candidates = TOKEN_CANDIDATES if is_onelife else [
        "VIVID_ADMIN_TOKEN", "VIVID_SHOPIFY_TOKEN", "VIVID_CLAUDE_REVIEW_TOKEN"]
    for name in candidates:
        val = os.environ.get(name, "").strip()
        if not val:
            continue
        code, shop = api(store, val, f"/admin/api/{API_VERSION}/shop.json")
        if code == 200:
            token, out["auth_source"] = val, f"secret {name}"
            out["shop"] = {k: shop["shop"].get(k) for k in (
                "name", "myshopify_domain", "domain", "plan_display_name", "shop_owner",
                "email", "currency", "country_name", "created_at")}
            break
        out.setdefault("token_attempts", []).append({name: code})
    if not token:
        cc, note = client_credentials_token(store)
        out.setdefault("token_attempts", []).append({"client_credentials": note})
        if cc:
            code, shop = api(store, cc, f"/admin/api/{API_VERSION}/shop.json")
            if code == 200:
                token, out["auth_source"] = cc, "client_credentials"
                out["shop"] = {k: shop["shop"].get(k) for k in (
                    "name", "myshopify_domain", "domain", "plan_display_name", "shop_owner",
                    "email", "currency", "country_name", "created_at")}
    if not token:
        out["auth"] = "FAILED"
        return out, None
    out["auth"] = "OK"

    # Always test the client-credentials path too (independent of token auth)
    cid = os.environ.get("SHOPIFY_CLIENT_ID" if store == "onelifehealth" else "VIVID_CLIENT_ID", "")
    cc, note = client_credentials_token(store)
    out["client_credentials"] = {
        "stored_client_id_prefix": cid[:8] if cid else None,
        "works": bool(cc),
        "note": note,
    }

    code, scopes = api(store, token, "/admin/oauth/access_scopes.json")
    out["scopes"] = sorted(s["handle"] for s in scopes.get("access_scopes", [])) if code == 200 else f"HTTP {code}"

    code, themes = api(store, token, f"/admin/api/{API_VERSION}/themes.json")
    if code == 200:
        out["themes"] = [{k: t.get(k) for k in ("id", "name", "role", "updated_at", "created_at", "processing")}
                         for t in themes.get("themes", [])]
    else:
        out["themes"] = f"HTTP {code}"

    for label, path in [
        ("products_count", f"/admin/api/{API_VERSION}/products/count.json"),
        ("pages_count", f"/admin/api/{API_VERSION}/pages/count.json"),
        ("collections_smart_count", f"/admin/api/{API_VERSION}/smart_collections/count.json"),
        ("collections_custom_count", f"/admin/api/{API_VERSION}/custom_collections/count.json"),
        ("locations", f"/admin/api/{API_VERSION}/locations.json"),
    ]:
        code, data = api(store, token, path)
        if code == 200:
            if label == "locations":
                out[label] = [{"name": loc.get("name"), "active": loc.get("active")}
                              for loc in data.get("locations", [])]
            else:
                out[label] = data.get("count")
        else:
            out[label] = f"HTTP {code}"
    return out, token


def main():
    results = []
    for store in STORES:
        res, _ = probe_store(store)
        results.append(res)
        print(f"{res['store']}: auth={res['auth']} via {res.get('auth_source')}")

    os.makedirs("reports", exist_ok=True)
    with open("reports/vivid-store-probe.json", "w") as f:
        json.dump(results, f, indent=2)

    lines = ["# Vivid store probe", ""]
    for r in results:
        lines.append(f"## {r['store']} — auth {r['auth']} ({r.get('auth_source')})")
        if r["auth"] != "OK":
            lines.append(f"- attempts: {r.get('token_attempts')}")
            lines.append("")
            continue
        s = r.get("shop", {})
        lines.append(f"- Shop: **{s.get('name')}** · domain {s.get('domain')} · plan {s.get('plan_display_name')} · {s.get('currency')} · created {s.get('created_at')}")
        lines.append(f"- Scopes: `{', '.join(r['scopes']) if isinstance(r['scopes'], list) else r['scopes']}`")
        lines.append(f"- Products: {r.get('products_count')} · Pages: {r.get('pages_count')} · Collections: {r.get('collections_smart_count')} smart + {r.get('collections_custom_count')} custom")
        lines.append(f"- Locations: {r.get('locations')}")
        lines.append("- Themes:")
        if isinstance(r.get("themes"), list):
            for t in r["themes"]:
                lines.append(f"  - `{t['id']}` **{t['name']}** — role={t['role']} · updated {t['updated_at']}")
        else:
            lines.append(f"  - {r.get('themes')}")
        lines.append("")
    with open("reports/vivid-store-probe.md", "w") as f:
        f.write("\n".join(lines))
    print("wrote reports/vivid-store-probe.{md,json}")


if __name__ == "__main__":
    main()
