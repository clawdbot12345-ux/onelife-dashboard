#!/usr/bin/env python3
"""
Onelife — Dietary Attribute Tagger (Claude Opus 4.6)

Reads every product's title, vendor, description, and existing tags,
then uses Claude to determine dietary attributes:
  - Vegan / Plant-Based
  - Organic / Certified Organic
  - Halaal
  - Gluten Free
  - Sugar Free
  - Keto Friendly
  - Dairy Free
  - Vegetarian
  - Proudly South African / SA Made
  - Cruelty Free
  - Non-GMO

Tags products with matching attributes so dietary smart collections
and product badges auto-populate.

Environment:
  ANTHROPIC_API_KEY / SHOPIFY_CLIENT_ID / SHOPIFY_CLIENT_SECRET
  DIET_APPLY=true / DIET_LIMIT=0 / DIET_BATCH_SIZE=30
"""
import json, os, re, sys, time
import urllib.error, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path

ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY")
MODEL = os.environ.get("DIET_MODEL", "claude-opus-4-6")
STORE = os.environ.get("SHOPIFY_STORE", "onelifehealth").replace(".myshopify.com", "")
API_VERSION = "2025-01"
APPLY = os.environ.get("DIET_APPLY", "true").lower() == "true"
LIMIT = int(os.environ.get("DIET_LIMIT", "0"))
BATCH_SIZE = int(os.environ.get("DIET_BATCH_SIZE", "30"))

if not ANTHROPIC_KEY:
    print("ERROR: ANTHROPIC_API_KEY required", file=sys.stderr); sys.exit(1)

SHOPIFY_HEADERS = {}

DIETARY_ATTRIBUTES = [
    "vegan", "organic", "halaal", "gluten-free", "sugar-free",
    "keto", "dairy-free", "vegetarian", "cruelty-free",
    "non-gmo", "proudly-south-african", "kosher",
]

SYSTEM_PROMPT = """You are a product dietary attribute classifier for Onelife Health, a South African health store. Your job is to determine which dietary/certification attributes apply to each product.

ONLY assign attributes you are CONFIDENT about based on the product name, brand, and description. If unsure, don't assign it.

Rules:
- "Vegan" = product contains no animal-derived ingredients. Supplements in capsules are NOT vegan unless stated. Plant-based proteins, plant extracts, herbal tinctures are typically vegan.
- "Organic" = product explicitly says organic in the name or is from a known organic brand (e.g. "Organic India", "Soaring Free")
- "Halaal" = only if explicitly stated or from a certified Halaal brand
- "Gluten-free" = supplements and capsules are generally gluten-free. Food items: only if stated.
- "Sugar-free" = supplements are generally sugar-free. Food items: only if stated.
- "Keto" = high fat, very low carb products. MCT oil, collagen, certain protein powders.
- "Dairy-free" = no milk, whey, casein. Most plant-based supplements qualify.
- "Vegetarian" = no meat/fish but may contain dairy/eggs. Most supplements qualify.
- "Cruelty-free" = not tested on animals. Most supplement brands qualify.
- "Kosher" = only if explicitly stated or from a known kosher-certified brand
- "Non-GMO" = only if explicitly stated
- "Proudly-south-african" = SA brand or manufactured in SA. Brands: Solal, Bioharmony, Natroceutics, Sally-Ann Creed, Go Natural, Soaring Free, The Real Thing, NeoGenesis, Faithful to Nature, A.Vogel SA, Willow, Green Pharm, Kura, etc.

Return ONLY a JSON array with one object per product:
[{"id": 12345, "attrs": ["vegan", "gluten-free", "dairy-free"]}, ...]
Products with NO attributes get an empty list: {"id": 67890, "attrs": []}"""


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


def claude(prompt, max_tokens=3000):
    body = {"model": MODEL, "max_tokens": max_tokens, "system": SYSTEM_PROMPT,
            "messages": [{"role":"user","content": prompt}]}
    req = urllib.request.Request("https://api.anthropic.com/v1/messages",
        data=json.dumps(body).encode(),
        headers={"x-api-key":ANTHROPIC_KEY,"anthropic-version":"2023-06-01","content-type":"application/json"},
        method="POST")
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                data = json.loads(r.read())
                text = "".join(b["text"] for b in data.get("content",[]) if b.get("type")=="text")
                text = re.sub(r"^```(?:json)?\n?","",text.strip())
                text = re.sub(r"\n?```$","",text)
                return json.loads(text)
        except urllib.error.HTTPError as e:
            if e.code in (429,529,500,503) and attempt < 2: time.sleep(5*(attempt+1)); continue
            print(f"  Claude {e.code}", file=sys.stderr); return None
        except: time.sleep(5)
    return None


def strip_html(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s or "")).strip()


def fetch_all():
    all_p = []; page_info = None
    while True:
        if page_info: params = {"limit":250,"page_info":page_info}
        else: params = {"limit":250,"status":"active","published_status":"published",
                        "fields":"id,title,tags,vendor,body_html,product_type"}
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
    REPORTS = ROOT / "reports"; REPORTS.mkdir(exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    log_path = REPORTS / f"dietary-tagging-{today}.log"

    done_ids = set()
    if log_path.exists():
        for line in log_path.read_text().splitlines():
            try:
                r = json.loads(line)
                if r.get("action") == "tagged": done_ids.add(r.get("id"))
            except: pass

    token = get_token()
    SHOPIFY_HEADERS = {"X-Shopify-Access-Token": token, "Accept": "application/json"}

    print("Fetching products...", flush=True)
    products = fetch_all()
    # Only process products not yet tagged
    targets = [p for p in products if p["id"] not in done_ids]
    if LIMIT: targets = targets[:LIMIT]
    print(f"Total: {len(products)}, to process: {len(targets)}", flush=True)
    print(f"APPLY: {APPLY}", flush=True)

    batches = [targets[i:i+BATCH_SIZE] for i in range(0, len(targets), BATCH_SIZE)]
    print(f"Batches: {len(batches)} (size {BATCH_SIZE})", flush=True)

    log_f = open(log_path, "a", buffering=1)
    log_f.write(json.dumps({"action":"run_start","total":len(targets),"apply":APPLY,"ts":datetime.now(timezone.utc).isoformat()}) + "\n")

    tagged = 0; failed = 0
    for bi, batch in enumerate(batches, 1):
        # Build prompt
        prods_text = ""
        for p in batch:
            desc = strip_html(p.get("body_html",""))[:150]
            prods_text += f'\n  {{"id":{p["id"]},"title":"{p.get("title","")[:80]}","vendor":"{p.get("vendor","")[:30]}","desc":"{desc}"}}'

        prompt = f"Classify these {len(batch)} products for dietary attributes:\n[{prods_text}\n]\n\nReturn JSON array."
        result = claude(prompt)

        if not result or not isinstance(result, list):
            failed += len(batch)
            print(f"  [{bi}/{len(batches)}] FAILED", flush=True)
            time.sleep(2); continue

        result_map = {item["id"]: item.get("attrs", []) for item in result if isinstance(item, dict)}

        for p in batch:
            pid = p["id"]
            attrs = result_map.get(pid, [])
            if not attrs:
                log_f.write(json.dumps({"action":"tagged","id":pid,"attrs":[],"ts":datetime.now(timezone.utc).isoformat()}) + "\n")
                tagged += 1
                continue

            # Filter to valid attributes only
            valid_attrs = [a for a in attrs if a in DIETARY_ATTRIBUTES]
            if not valid_attrs:
                log_f.write(json.dumps({"action":"tagged","id":pid,"attrs":[],"ts":datetime.now(timezone.utc).isoformat()}) + "\n")
                tagged += 1
                continue

            if APPLY:
                current_tags = p.get("tags","") or ""
                current_set = {t.strip().lower() for t in current_tags.split(",") if t.strip()}
                new_tags = [a for a in valid_attrs if a not in current_set]
                if new_tags:
                    all_tags = current_tags + ", " + ", ".join(new_tags) if current_tags else ", ".join(new_tags)
                    s, resp = shopify("PUT", f"/products/{pid}.json", {"product":{"id":pid,"tags":all_tags}})
                    if s == 200:
                        tagged += 1
                        log_f.write(json.dumps({"action":"tagged","id":pid,"attrs":valid_attrs,"new_tags":new_tags,"ts":datetime.now(timezone.utc).isoformat()}) + "\n")
                    else:
                        failed += 1
                else:
                    tagged += 1
                    log_f.write(json.dumps({"action":"tagged","id":pid,"attrs":valid_attrs,"new_tags":0,"ts":datetime.now(timezone.utc).isoformat()}) + "\n")
            else:
                tagged += 1
                log_f.write(json.dumps({"action":"dryrun","id":pid,"attrs":valid_attrs,"ts":datetime.now(timezone.utc).isoformat()}) + "\n")

        if bi % 5 == 0 or bi == len(batches):
            print(f"  [{bi}/{len(batches)}] tagged={tagged} failed={failed}", flush=True)
        time.sleep(1)

    log_f.write(json.dumps({"action":"run_end","tagged":tagged,"failed":failed,"ts":datetime.now(timezone.utc).isoformat()}) + "\n")
    log_f.close()
    print(f"\n=== DONE: tagged={tagged} failed={failed} ===", flush=True)


if __name__ == "__main__":
    main()
