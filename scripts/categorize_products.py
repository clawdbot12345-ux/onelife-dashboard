#!/usr/bin/env python3
"""
Onelife — Comprehensive Product Categorization Agent (Claude Opus 4.6)

Sends every product to Claude in batches of 25 for intelligent multi-category
assignment. Claude reads the title, vendor, and description to assign products
to ALL relevant categories — not just keyword grep.

Categories cover the full store taxonomy:
  - Health Goals (immunity, gut, energy, sleep, stress, joints, weight, skin)
  - Health Conditions (heart, blood-sugar, liver, kidney, brain, eye, respiratory,
    hormonal, womens-health, mens-health, pregnancy)
  - Product Types (vitamins, herbal, probiotics, sports, essential-oils,
    homeopathic, superfoods, teas, food-pantry, beauty-topical, pet, home)
  - Dietary (vegan, organic, halaal, gluten-free, sugar-free, keto)

Each product gets tagged with "cat:<category-handle>" tags. Smart collections
are then created/updated to match on these tags.

Products also get a "featured:<category>" tag if Claude rates them as a
top-tier fit (score 9-10) for that category, so they sort to the top.

Environment:
  ANTHROPIC_API_KEY / SHOPIFY_CLIENT_ID / SHOPIFY_CLIENT_SECRET
  CAT_APPLY=true / CAT_LIMIT=0 / CAT_BATCH_SIZE=25 / CAT_MODEL=claude-opus-4-6
"""
import json, os, re, sys, threading, time
import urllib.error, urllib.parse, urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY")
MODEL = os.environ.get("CAT_MODEL", "claude-opus-4-6")
STORE = os.environ.get("SHOPIFY_STORE", "onelifehealth").replace(".myshopify.com", "")
API_VERSION = "2025-01"
APPLY = os.environ.get("CAT_APPLY", "true").lower() == "true"
LIMIT = int(os.environ.get("CAT_LIMIT", "0"))
BATCH_SIZE = int(os.environ.get("CAT_BATCH_SIZE", "25"))
SHOPIFY_SLEEP = 0.4

if not ANTHROPIC_KEY:
    print("ERROR: ANTHROPIC_API_KEY required", file=sys.stderr); sys.exit(1)

SHOPIFY_HEADERS = {}
_sh_lock = threading.Lock()
_sh_last = [0.0]

CATEGORIES = {
    # Health Goals
    "immunity": "Immunity & Cold Season — products for immune support, colds, flu, sinus, allergies",
    "gut-health": "Gut Health & Digestion — probiotics, digestive enzymes, gut repair, IBS, bloating",
    "energy-vitality": "Energy & Vitality — B vitamins, iron, CoQ10, adaptogens for energy, fatigue support",
    "sleep-relaxation": "Sleep & Relaxation — sleep aids, calming supplements, magnesium, melatonin, valerian",
    "stress-mood": "Stress & Mood — ashwagandha, adaptogens, mood support, anxiety, omega-3, St John's Wort",
    "joints-mobility": "Joints & Mobility — glucosamine, collagen, turmeric, MSM, anti-inflammatory, bone health",
    "weight-management": "Weight Management — appetite control, fat burners, meal replacements, keto, detox",
    "skin-hair-nails": "Skin, Hair & Nails — collagen, biotin, beauty supplements, anti-aging",
    # Health Conditions
    "heart-cardiovascular": "Heart & Cardiovascular — CoQ10, omega-3, blood pressure, cholesterol, hawthorn",
    "blood-sugar": "Blood Sugar & Diabetes — chromium, berberine, gymnema, cinnamon, glucose support",
    "liver-detox": "Liver & Detox — milk thistle, NAC, liver support, detox, cleanse",
    "kidney-urinary": "Kidney & Urinary — cranberry, D-mannose, kidney support, bladder, UTI",
    "brain-cognitive": "Brain & Cognitive — lion's mane, ginkgo, phosphatidylserine, memory, focus, ADHD",
    "eye-health": "Eye Health — lutein, zeaxanthin, bilberry, vision support",
    "respiratory": "Respiratory — lung support, bronchial, asthma support, NAC, mullein",
    "hormonal-balance": "Hormonal Balance — DIM, vitex, maca, thyroid, adrenal, hormone support",
    "womens-health": "Women's Health — menopause, menstrual, PCOS, fertility, iron, folate, pregnancy",
    "mens-health": "Men's Health — prostate, testosterone, saw palmetto, zinc, virility",
    "kids-health": "Kids Health — children's vitamins, kids probiotics, kids immune, baby supplements",
    # Product Types
    "vitamins-minerals": "Vitamins & Minerals — multivitamins, single vitamins, mineral supplements",
    "herbal-supplements": "Herbal Supplements — tinctures, herbal extracts, traditional herbal remedies",
    "probiotics": "Probiotics & Fermented — probiotic capsules, kefir, kombucha, fermented foods",
    "sports-nutrition": "Sports Nutrition — protein powder, pre-workout, BCAAs, creatine, recovery",
    "essential-oils": "Essential Oils & Aromatherapy — pure essential oils, carrier oils, diffuser blends",
    "homeopathic": "Homeopathic Remedies — homeopathic drops, tissue salts, Schuessler salts",
    "superfoods": "Superfoods — spirulina, chlorella, maca, moringa, wheatgrass, raw powders",
    "teas-beverages": "Teas & Beverages — herbal teas, rooibos, green tea, health drinks, coffee alternatives",
    "food-pantry": "Food & Pantry — healthy groceries, snacks, baking, condiments, cooking oils, spices",
    "beauty-topical": "Beauty & Topical — skincare creams, serums, body care, natural deodorant, lip balm",
    "pet-health": "Pet Health — pet supplements, pet probiotics, animal health",
    "healthy-home": "Healthy Home — cleaning products, air purifiers, water filters, eco home",
}

SYSTEM_PROMPT = """You are a product categorization expert for Onelife Health, a South African health retail store with 10,000+ products. Your job is to assign each product to ALL relevant categories from the provided taxonomy.

Rules:
- A product can belong to MULTIPLE categories (e.g. a collagen supplement fits both "joints-mobility" AND "skin-hair-nails" AND "beauty-topical")
- Only assign categories that genuinely fit. Don't force products into categories where they don't belong.
- For each assignment, give a relevance score 1-10 (10 = perfect fit, core product for that category)
- Products scoring 9-10 are "featured" — they should appear at the top of that collection
- If a product doesn't fit ANY category, return an empty list
- Respond with ONLY a JSON array, no markdown, no explanation"""


def get_shopify_token():
    cid = os.environ.get("SHOPIFY_CLIENT_ID")
    cs = os.environ.get("SHOPIFY_CLIENT_SECRET")
    body = urllib.parse.urlencode({"grant_type":"client_credentials","client_id":cid,"client_secret":cs}).encode()
    req = urllib.request.Request(f"https://{STORE}.myshopify.com/admin/oauth/access_token",
        data=body, headers={"Content-Type":"application/x-www-form-urlencoded"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())["access_token"]


def shopify_throttle():
    with _sh_lock:
        now = time.time()
        if now - _sh_last[0] < SHOPIFY_SLEEP:
            time.sleep(SHOPIFY_SLEEP - (now - _sh_last[0]))
        _sh_last[0] = time.time()


def shopify(method, path, body=None):
    shopify_throttle()
    url = f"https://{STORE}.myshopify.com/admin/api/{API_VERSION}{path}"
    data = json.dumps(body).encode() if body else None
    hdrs = dict(SHOPIFY_HEADERS)
    if data: hdrs["Content-Type"] = "application/json"
    for attempt in range(5):
        req = urllib.request.Request(url, data=data, headers=hdrs, method=method)
        try:
            with urllib.request.urlopen(req, timeout=45) as r:
                return r.status, json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code == 429:
                try: wait = float(e.headers.get("Retry-After","2"))
                except: wait = 2
                time.sleep(max(wait, 2 ** attempt))
                continue
            return e.code, {"__error__": e.read().decode()[:200]}
        except (urllib.error.URLError, TimeoutError):
            time.sleep(2 ** attempt)
    return -1, {}


def claude_call(user_prompt, max_tokens=2000):
    body = {"model": MODEL, "max_tokens": max_tokens,
            "system": SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": user_prompt}]}
    req = urllib.request.Request("https://api.anthropic.com/v1/messages",
        data=json.dumps(body).encode(),
        headers={"x-api-key": ANTHROPIC_KEY, "anthropic-version": "2023-06-01",
                 "content-type": "application/json"}, method="POST")
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                data = json.loads(r.read())
                text = "".join(b["text"] for b in data.get("content",[]) if b.get("type")=="text")
                text = re.sub(r"^```(?:json)?\n?","",text.strip())
                text = re.sub(r"\n?```$","",text)
                return json.loads(text)
        except urllib.error.HTTPError as e:
            if e.code in (429,529,500,503) and attempt < 2:
                time.sleep(5*(attempt+1)); continue
            print(f"  Claude {e.code}: {e.read().decode()[:200]}", file=sys.stderr)
            return None
        except (json.JSONDecodeError, urllib.error.URLError, TimeoutError) as ex:
            if attempt < 2: time.sleep(5); continue
            print(f"  Claude error: {ex}", file=sys.stderr)
            return None
    return None


def fetch_all_products():
    all_prods = []
    page_info = None
    while True:
        if page_info:
            params = {"limit":250,"page_info":page_info}
        else:
            params = {"limit":250,"status":"active","published_status":"published",
                      "fields":"id,title,tags,product_type,vendor,body_html"}
        url = f"https://{STORE}.myshopify.com/admin/api/{API_VERSION}/products.json?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers=SHOPIFY_HEADERS)
        with urllib.request.urlopen(req, timeout=60) as r:
            data = json.loads(r.read())
            link = r.headers.get("Link","")
        prods = data.get("products",[])
        if not prods: break
        all_prods.extend(prods)
        page_info = None
        for part in link.split(","):
            if 'rel="next"' in part:
                m = re.search(r"page_info=([^&>]+)", part)
                if m: page_info = m.group(1)
        if not page_info: break
        time.sleep(0.4)
    return all_prods


def strip_html(s):
    return re.sub(r"\s+"," ",re.sub(r"<[^>]+>"," ",s or "")).strip()


def build_batch_prompt(products):
    cat_list = "\n".join(f"  - {handle}: {desc}" for handle, desc in CATEGORIES.items())
    prods_text = ""
    for p in products:
        desc = strip_html(p.get("body_html",""))[:200]
        prods_text += f'\n  {{"id":{p["id"]},"title":"{p.get("title","")[:100]}","vendor":"{p.get("vendor","")[:40]}","type":"{p.get("product_type","")[:40]}","desc":"{desc[:150]}"}}'

    return f"""Categorize these {len(products)} products into the relevant categories.

CATEGORIES:
{cat_list}

PRODUCTS:
[{prods_text}
]

Return a JSON array with one object per product:
[
  {{"id": 12345, "categories": [{{"cat": "immunity", "score": 9}}, {{"cat": "vitamins-minerals", "score": 7}}]}},
  ...
]

Rules:
- Assign ALL fitting categories, not just one
- Score 9-10 = perfect core product, 7-8 = good fit, 5-6 = partial fit, below 5 = don't include
- Food items like spices, herbs for cooking, snack bars go to "food-pantry"
- Essential oils go to "essential-oils" (and also relevant health goals)
- Homeopathic products go to "homeopathic" (and relevant conditions)
- If a product truly doesn't fit any category, return empty categories list
- Return ONLY the JSON array"""


def main():
    global SHOPIFY_HEADERS
    ROOT = Path(__file__).resolve().parent.parent
    REPORTS = ROOT / "reports"
    REPORTS.mkdir(exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    log_path = REPORTS / f"categorization-{today}.log"

    token = get_shopify_token()
    SHOPIFY_HEADERS = {"X-Shopify-Access-Token": token, "Accept": "application/json"}

    # Resume
    done_ids = set()
    if log_path.exists():
        for line in log_path.read_text().splitlines():
            try:
                r = json.loads(line)
                if r.get("action") == "product_tagged":
                    done_ids.add(r.get("id"))
            except: pass

    print(f"Model: {MODEL}", flush=True)
    print(f"APPLY: {APPLY}", flush=True)
    print(f"Batch size: {BATCH_SIZE}", flush=True)
    print(f"Already done: {len(done_ids)}", flush=True)

    print("Fetching products...", flush=True)
    products = fetch_all_products()
    print(f"Total: {len(products)}", flush=True)

    targets = [p for p in products if p["id"] not in done_ids]
    if LIMIT:
        targets = targets[:LIMIT]
    print(f"To process: {len(targets)}", flush=True)

    log_f = open(log_path, "a", buffering=1)
    def log(**kw):
        kw["ts"] = datetime.now(timezone.utc).isoformat()
        log_f.write(json.dumps(kw, default=str) + "\n")

    log(action="run_start", model=MODEL, total=len(targets), batch_size=BATCH_SIZE, apply=APPLY)

    # Process in batches
    batches = [targets[i:i+BATCH_SIZE] for i in range(0, len(targets), BATCH_SIZE)]
    print(f"Batches: {len(batches)}", flush=True)

    tagged = 0
    failed = 0
    for bi, batch in enumerate(batches, 1):
        prompt = build_batch_prompt(batch)
        result = claude_call(prompt, max_tokens=3000)

        if not result or not isinstance(result, list):
            failed += len(batch)
            log(action="batch_failed", batch=bi, count=len(batch))
            print(f"  [{bi}/{len(batches)}] FAILED (Claude returned None)", flush=True)
            time.sleep(2)
            continue

        # Map results by product ID
        result_map = {}
        for item in result:
            if isinstance(item, dict) and "id" in item:
                result_map[item["id"]] = item.get("categories", [])

        # Apply tags
        for p in batch:
            pid = p["id"]
            cats = result_map.get(pid, [])
            if not cats:
                log(action="product_uncategorized", id=pid, title=p.get("title","")[:60])
                continue

            # Build new tags
            new_tags = []
            for c in cats:
                cat_handle = c.get("cat","")
                score = c.get("score", 0)
                if cat_handle in CATEGORIES:
                    new_tags.append(f"cat:{cat_handle}")
                    if score >= 9:
                        new_tags.append(f"featured:{cat_handle}")

            if not new_tags:
                continue

            if APPLY:
                current_tags = p.get("tags","") or ""
                current_set = {t.strip() for t in current_tags.split(",") if t.strip()}
                to_add = [t for t in new_tags if t not in current_set]
                if to_add:
                    all_tags = current_tags + ", " + ", ".join(to_add) if current_tags else ", ".join(to_add)
                    s, resp = shopify("PUT", f"/products/{pid}.json", {"product":{"id":pid,"tags":all_tags}})
                    if s == 200:
                        tagged += 1
                        log(action="product_tagged", id=pid, cats=[c["cat"] for c in cats], tags_added=len(to_add))
                    else:
                        failed += 1
                        log(action="tag_failed", id=pid, status=s)
                else:
                    tagged += 1
                    log(action="product_tagged", id=pid, cats=[c["cat"] for c in cats], tags_added=0, note="already_tagged")
            else:
                tagged += 1
                log(action="product_dryrun", id=pid, cats=[c["cat"] for c in cats])

        print(f"  [{bi}/{len(batches)}] tagged={tagged} failed={failed}", flush=True)
        time.sleep(1)

    log(action="run_end", tagged=tagged, failed=failed)
    log_f.close()
    print(f"\n=== CATEGORIZATION DONE: tagged={tagged} failed={failed} ===", flush=True)


if __name__ == "__main__":
    main()
