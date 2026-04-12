#!/usr/bin/env python3
"""
Onelife — Duplicate Description Rewriter (Claude Opus 4.6)

Finds products sharing identical descriptions and rewrites each one
to be unique while preserving the product's specific details.
Keeps the first product in each cluster unchanged, rewrites the rest.

Environment:
  ANTHROPIC_API_KEY / SHOPIFY_CLIENT_ID / SHOPIFY_CLIENT_SECRET
  DUP_APPLY=true / DUP_LIMIT=0 / DUP_MODEL=claude-opus-4-6
"""
import json, os, re, sys, time
import urllib.error, urllib.parse, urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY")
MODEL = os.environ.get("DUP_MODEL", "claude-opus-4-6")
STORE = os.environ.get("SHOPIFY_STORE", "onelifehealth").replace(".myshopify.com", "")
API_VERSION = "2025-01"
APPLY = os.environ.get("DUP_APPLY", "true").lower() == "true"
LIMIT = int(os.environ.get("DUP_LIMIT", "0"))

if not ANTHROPIC_KEY:
    print("ERROR: ANTHROPIC_API_KEY required", file=sys.stderr); sys.exit(1)

SHOPIFY_HEADERS = {}

def get_token():
    cid = os.environ.get("SHOPIFY_CLIENT_ID"); cs = os.environ.get("SHOPIFY_CLIENT_SECRET")
    body = urllib.parse.urlencode({"grant_type":"client_credentials","client_id":cid,"client_secret":cs}).encode()
    req = urllib.request.Request(f"https://{STORE}.myshopify.com/admin/oauth/access_token",
        data=body, headers={"Content-Type":"application/x-www-form-urlencoded"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r: return json.loads(r.read())["access_token"]

def shopify(method, path, body=None):
    url = f"https://{STORE}.myshopify.com/admin/api/{API_VERSION}{path}"
    data = json.dumps(body).encode() if body else None
    hdrs = dict(SHOPIFY_HEADERS)
    if data: hdrs["Content-Type"] = "application/json"
    for attempt in range(5):
        req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                time.sleep(0.4); return r.status, json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                try: wait = float(e.headers.get("Retry-After","2"))
                except: wait = 2
                time.sleep(max(wait, 2**attempt)); continue
            return e.code, {"__error__": e.read().decode()[:200]}
        except: time.sleep(2**attempt)
    return -1, {}

def claude(prompt, max_tokens=1500):
    body = {"model": MODEL, "max_tokens": max_tokens, "system": "You are an expert SEO copywriter for Onelife Health, a South African health store. Write unique, evidence-based product descriptions. South African English. 150-300 words. No hype. Return ONLY the HTML description (using <p> tags), no JSON, no markdown.",
            "messages": [{"role":"user","content": prompt}]}
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=json.dumps(body).encode(),
        headers={"x-api-key":ANTHROPIC_KEY,"anthropic-version":"2023-06-01","content-type":"application/json"}, method="POST")
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                data = json.loads(r.read())
                return "".join(b["text"] for b in data.get("content",[]) if b.get("type")=="text")
        except urllib.error.HTTPError as e:
            if e.code in (429,529,500,503) and attempt < 2: time.sleep(5*(attempt+1)); continue
            print(f"  Claude {e.code}", file=sys.stderr); return None
        except: time.sleep(5); continue
    return None

def strip_html(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s or "")).strip()

def fetch_all():
    all_p = []; page_info = None
    while True:
        if page_info: params = {"limit":250,"page_info":page_info}
        else: params = {"limit":250,"status":"active","published_status":"published","fields":"id,title,handle,body_html,vendor,product_type"}
        url = f"https://{STORE}.myshopify.com/admin/api/{API_VERSION}/products.json?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers=SHOPIFY_HEADERS)
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read()); link = r.headers.get("Link","")
        products = data.get("products",[])
        if not products: break
        all_p.extend(products)
        page_info = None
        for part in link.split(","):
            if 'rel="next"' in part:
                m = re.search(r"page_info=([^&>]+)", part)
                if m: page_info = m.group(1)
        if not page_info: break
        time.sleep(0.4)
    return all_p

def main():
    global SHOPIFY_HEADERS
    ROOT = Path(__file__).resolve().parent.parent
    REPORTS = ROOT / "reports"
    REPORTS.mkdir(exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    log_path = REPORTS / f"dedup-descriptions-{today}.log"

    done_ids = set()
    if log_path.exists():
        for line in log_path.read_text().splitlines():
            try:
                r = json.loads(line)
                if r.get("action") == "rewritten": done_ids.add(r.get("id"))
            except: pass

    token = get_token()
    SHOPIFY_HEADERS = {"X-Shopify-Access-Token": token, "Accept": "application/json"}

    print("Fetching products...", flush=True)
    products = fetch_all()
    print(f"Total: {len(products)}", flush=True)

    desc_map = defaultdict(list)
    for p in products:
        text = strip_html(p.get("body_html",""))
        if text and len(text) > 50:
            desc_map[text].append(p)

    duplicates = {k: v for k, v in desc_map.items() if len(v) >= 2}
    to_rewrite = []
    for text, prods in duplicates.items():
        for p in prods[1:]:  # Keep first, rewrite rest
            if p["id"] not in done_ids:
                to_rewrite.append(p)

    if LIMIT: to_rewrite = to_rewrite[:LIMIT]
    print(f"Clusters: {len(duplicates)}, to rewrite: {len(to_rewrite)}", flush=True)
    print(f"APPLY: {APPLY}", flush=True)

    log_f = open(log_path, "a", buffering=1)
    ok = 0; fail = 0
    for i, p in enumerate(to_rewrite, 1):
        title = p.get("title",""); vendor = p.get("vendor",""); ptype = p.get("product_type","")
        prompt = f"Write a UNIQUE product description for:\nTitle: {title}\nBrand: {vendor}\nType: {ptype}\n\nThis product currently shares its description with other products which hurts SEO. Write a completely unique 150-300 word description using <p> tags. Be specific to THIS product."
        new_desc = claude(prompt)
        if not new_desc:
            fail += 1; log_f.write(json.dumps({"action":"failed","id":p["id"],"title":title[:60],"ts":datetime.now(timezone.utc).isoformat()})+"\n"); continue
        if APPLY:
            s, resp = shopify("PUT", f"/products/{p['id']}.json", {"product":{"id":p["id"],"body_html":new_desc}})
            if s == 200:
                ok += 1; log_f.write(json.dumps({"action":"rewritten","id":p["id"],"title":title[:60],"ts":datetime.now(timezone.utc).isoformat()})+"\n")
            else:
                fail += 1; log_f.write(json.dumps({"action":"put_failed","id":p["id"],"status":s,"ts":datetime.now(timezone.utc).isoformat()})+"\n")
        else:
            ok += 1; log_f.write(json.dumps({"action":"dryrun","id":p["id"],"ts":datetime.now(timezone.utc).isoformat()})+"\n")
        if i % 25 == 0 or i == len(to_rewrite):
            print(f"  [{i}/{len(to_rewrite)}] ok={ok} fail={fail}", flush=True)
        time.sleep(0.5)

    log_f.close()
    print(f"\n=== DONE: ok={ok} fail={fail} ===", flush=True)

if __name__ == "__main__": main()
