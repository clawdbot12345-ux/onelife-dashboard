#!/usr/bin/env python3
"""
Onelife — Blog Article Expander + Internal Linker (Claude Opus 4.6)

Expands thin blog articles from ~650 words to 1,500+ words and adds
3-5 relevant internal product links per article.

Environment:
  ANTHROPIC_API_KEY / SHOPIFY_CLIENT_ID / SHOPIFY_CLIENT_SECRET
  BLOG_EXPAND_APPLY=true / BLOG_EXPAND_LIMIT=0
"""
import json, os, re, sys, time
import urllib.error, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path

ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY")
MODEL = os.environ.get("BLOG_MODEL", "claude-opus-4-6")
STORE = os.environ.get("SHOPIFY_STORE", "onelifehealth").replace(".myshopify.com", "")
API_VERSION = "2025-01"
APPLY = os.environ.get("BLOG_EXPAND_APPLY", "true").lower() == "true"
LIMIT = int(os.environ.get("BLOG_EXPAND_LIMIT", "0"))
MIN_WORDS = 1200  # Only expand articles shorter than this

if not ANTHROPIC_KEY:
    print("ERROR: ANTHROPIC_API_KEY required", file=sys.stderr); sys.exit(1)

SHOPIFY_HEADERS = {}

def get_token():
    cid = os.environ.get("SHOPIFY_CLIENT_ID"); cs = os.environ.get("SHOPIFY_CLIENT_SECRET")
    body = urllib.parse.urlencode({"grant_type":"client_credentials","client_id":cid,"client_secret":cs}).encode()
    req = urllib.request.Request(f"https://{STORE}.myshopify.com/admin/oauth/access_token",
        data=body, headers={"Content-Type":"application/x-www-form-urlencoded"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r: return json.loads(r.read())["access_token"]

def shopify_get(path):
    req = urllib.request.Request(f"https://{STORE}.myshopify.com/admin/api/{API_VERSION}{path}", headers=SHOPIFY_HEADERS)
    with urllib.request.urlopen(req, timeout=30) as r: return json.loads(r.read())

def shopify_put(path, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(f"https://{STORE}.myshopify.com/admin/api/{API_VERSION}{path}",
        data=data, headers={**SHOPIFY_HEADERS,"Content-Type":"application/json"}, method="PUT")
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=45) as r: time.sleep(0.5); return r.status
        except urllib.error.HTTPError as e:
            if e.code == 429: time.sleep(3); continue
            return e.code
    return -1

def claude(prompt, max_tokens=4000):
    body = {"model": MODEL, "max_tokens": max_tokens,
        "system": "You are an expert health and wellness content writer for Onelife Health, South Africa's leading health supermarket. Expand articles to be comprehensive, evidence-based, and SEO-optimised. Use South African English. Include practical advice. Add 3-5 internal links to relevant products using <a href=\"/collections/HANDLE\"> or <a href=\"/products/HANDLE\"> format. Use proper HTML headings (h2, h3), paragraphs, and lists. Return ONLY the expanded HTML content.",
        "messages": [{"role":"user","content": prompt}]}
    req = urllib.request.Request("https://api.anthropic.com/v1/messages", data=json.dumps(body).encode(),
        headers={"x-api-key":ANTHROPIC_KEY,"anthropic-version":"2023-06-01","content-type":"application/json"}, method="POST")
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                data = json.loads(r.read())
                return "".join(b["text"] for b in data.get("content",[]) if b.get("type")=="text")
        except urllib.error.HTTPError as e:
            if e.code in (429,529,500,503) and attempt < 2: time.sleep(5*(attempt+1)); continue
            return None
        except: time.sleep(5)
    return None

def strip_html(s):
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s or "")).strip()

def main():
    global SHOPIFY_HEADERS
    ROOT = Path(__file__).resolve().parent.parent
    REPORTS = ROOT / "reports"; REPORTS.mkdir(exist_ok=True)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    log_path = REPORTS / f"blog-expansion-{today}.log"

    done_ids = set()
    if log_path.exists():
        for line in log_path.read_text().splitlines():
            try:
                r = json.loads(line)
                if r.get("action") == "expanded": done_ids.add(r.get("id"))
            except: pass

    token = get_token()
    SHOPIFY_HEADERS = {"X-Shopify-Access-Token": token, "Accept": "application/json"}

    blogs = shopify_get("/blogs.json")
    articles = []
    for blog in blogs.get("blogs",[]):
        bid = blog["id"]
        arts = shopify_get(f"/blogs/{bid}/articles.json?limit=250")
        for a in arts.get("articles",[]):
            word_count = len(strip_html(a.get("body_html","")).split())
            if word_count < MIN_WORDS and a["id"] not in done_ids:
                articles.append((bid, a, word_count))

    if LIMIT: articles = articles[:LIMIT]
    print(f"Articles to expand: {len(articles)}", flush=True)
    print(f"APPLY: {APPLY}", flush=True)

    log_f = open(log_path, "a", buffering=1)
    ok = 0; fail = 0
    for i, (bid, art, wc) in enumerate(articles, 1):
        title = art.get("title","")
        body = art.get("body_html","")
        prompt = f"Expand this blog article to 1,500+ words. Keep the existing content but add depth, practical advice, and 3-5 internal product links.\n\nTitle: {title}\nCurrent word count: {wc}\nCurrent content:\n{body[:3000]}\n\nAvailable collections to link to: immunity, gut-health, energy-vitality, sleep-relaxation, stress-mood, joints-mobility, weight-management, skin-hair-nails, vitamins-minerals, herbal-supplements, probiotics, sports-nutrition, superfoods\n\nReturn the FULL expanded HTML article."
        expanded = claude(prompt)
        if not expanded or len(strip_html(expanded).split()) < wc:
            fail += 1; log_f.write(json.dumps({"action":"failed","id":art["id"],"title":title[:60],"ts":datetime.now(timezone.utc).isoformat()})+"\n"); continue
        if APPLY:
            s = shopify_put(f"/blogs/{bid}/articles/{art['id']}.json", {"article":{"id":art["id"],"body_html":expanded}})
            if s == 200:
                new_wc = len(strip_html(expanded).split())
                ok += 1; log_f.write(json.dumps({"action":"expanded","id":art["id"],"title":title[:60],"old_wc":wc,"new_wc":new_wc,"ts":datetime.now(timezone.utc).isoformat()})+"\n")
                print(f"  [{i}/{len(articles)}] {title[:40]} {wc}→{new_wc} words", flush=True)
            else:
                fail += 1
        else:
            ok += 1
        if i % 10 == 0: print(f"  [{i}/{len(articles)}] ok={ok} fail={fail}", flush=True)
        time.sleep(1)

    log_f.close()
    print(f"\n=== DONE: ok={ok} fail={fail} ===", flush=True)

if __name__ == "__main__": main()
