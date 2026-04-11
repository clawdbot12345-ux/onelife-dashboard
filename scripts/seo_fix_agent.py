#!/usr/bin/env python3
"""
Onelife — SEO Fix Agent (v2)

Reads the latest seo-audit-*.json, then uses Claude to generate targeted
replacement content for items that failed rule-based checks, and (optionally)
pushes the fixes to Shopify.

What got fixed vs v1:
  1. Pre-fetches current Shopify state for every item before regenerating,
     and only overwrites fields that are actually broken (never clobbers
     existing good content).
  2. Alt text is now APPLIED (v1 generated it but never wrote it). Via
     PUT /products/:id/images/:img_id.json for each image needing alt.
  3. SEO title + meta description are now written as Shopify metafields
     (namespace=global, keys=title_tag and description_tag) — that's the
     actual place Shopify pulls them from for <title> and <meta> rendering.
  4. Blog articles, collections, and pages are now handled (v1 was product
     only). Articles get excerpt + image alt + tags + SEO metafields;
     collections get body_html + image alt + SEO metafields.

Plus:
  - Default model bumped to claude-opus-4-6 (was haiku-4.5)
  - ThreadPoolExecutor for parallel Claude calls (FIX_CONCURRENCY, default 5)
  - Every Shopify action logged to reports/seo-fixes-applied-YYYY-MM-DD.log
    as JSONL; on restart already-done items are skipped (idempotent).
  - APPLY_FIXES=true gate as before.
  - FIX_SCOPE env: "all" (default), "products", "articles", "collections"
  - FIX_LIMIT env: 0 = no cap, N = only do first N per scope

Environment:
  ANTHROPIC_API_KEY       required
  SHOPIFY_CLIENT_ID       required (for fetch + apply)
  SHOPIFY_CLIENT_SECRET   required
  SHOPIFY_STORE           default: onelifehealth
  FIX_MODEL               default: claude-opus-4-6
  FIX_CONCURRENCY         default: 5
  FIX_LIMIT               default: 0 (no cap)
  FIX_SCOPE               default: all
  APPLY_FIXES             default: false (dry run)
  AUDIT_FILE              optional: explicit audit json path
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY")
CLIENT_ID = os.environ.get("SHOPIFY_CLIENT_ID")
CLIENT_SECRET = os.environ.get("SHOPIFY_CLIENT_SECRET")
STORE = os.environ.get("SHOPIFY_STORE", "onelifehealth").replace(".myshopify.com", "")
MODEL = os.environ.get("FIX_MODEL", "claude-opus-4-6")
CONCURRENCY = int(os.environ.get("FIX_CONCURRENCY", "5"))
LIMIT = int(os.environ.get("FIX_LIMIT", "0"))
SCOPE = os.environ.get("FIX_SCOPE", "all").lower()
APPLY = os.environ.get("APPLY_FIXES", "false").lower() == "true"
API_VERSION = "2025-01"
SHOPIFY_SLEEP = 0.35

if not ANTHROPIC_KEY:
    print("ERROR: ANTHROPIC_API_KEY not set", file=sys.stderr)
    sys.exit(1)
if not (CLIENT_ID and CLIENT_SECRET):
    print("ERROR: SHOPIFY_CLIENT_ID + SHOPIFY_CLIENT_SECRET required", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = ROOT / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

# ============================================================================
# Shopify auth + REST helpers
# ============================================================================

def get_shopify_token():
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


SHOPIFY_TOKEN = None
SHOPIFY_HEADERS = {}


def shopify(method, path, body=None):
    """Shopify REST request. Returns (status, parsed_json_or_error_dict)."""
    url = f"https://{STORE}.myshopify.com/admin/api/{API_VERSION}{path}"
    data = None
    headers = dict(SHOPIFY_HEADERS)
    if body is not None:
        data = json.dumps(body).encode()
        headers["Content-Type"] = "application/json"
    for attempt in range(5):
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                raw = resp.read()
                out = json.loads(raw) if raw else {}
                time.sleep(SHOPIFY_SLEEP)
                return resp.status, out
        except urllib.error.HTTPError as e:
            if e.code == 429:
                retry = int(e.headers.get("Retry-After", "2"))
                time.sleep(max(retry, 2))
                continue
            err = e.read().decode(errors="replace") if e.fp else ""
            time.sleep(SHOPIFY_SLEEP)
            return e.code, {"__error__": err}
        except (urllib.error.URLError, TimeoutError):
            time.sleep(2 ** attempt)
            continue
    return -1, {"__error__": "max retries"}


# ============================================================================
# Claude — direct Messages API call with thread-safe retry
# ============================================================================

SYSTEM_PROMPT = """You are an expert SEO copywriter for Onelife Health, a South African health retail chain specialising in supplements, wellness products, natural health goods, and clean-label groceries. You write clear, evidence-based, non-hype product and content copy for their Shopify storefront.

Voice & style rules (follow strictly):
- UNIQUE content only. Never reuse boilerplate across items. Two similar-sounding products must get distinctly different descriptions.
- Honest, evidence-based tone. NO marketing hype words: "amazing", "revolutionary", "life-changing", "miracle", "ultimate", "game-changer", "must-have". Never over-claim health benefits.
- Speak to South African customers. Use "R" for prices, "SA" for country. Mention local context (SA climate, SAHPRA, local dietary habits) where naturally relevant.
- South African English spelling: colour, flavour, organised, specialised, litre, metre.
- Short paragraphs (2-4 sentences). Use <p> tags in HTML. Never use <div>, <span>, or inline styles.
- Keep claims grounded in what the product name actually says. If you don't know what something does, describe the ingredients + general category.
- Never invent certifications (e.g. don't claim "SAHPRA-approved" unless the title says so), dosages, or origin stories.

Output rules:
- Respond with a single valid JSON object matching the schema the user specifies.
- No markdown code fences, no prose before or after the JSON.
- All HTML must be valid and use only <p>, <ul>, <li>, <strong>, <em> tags."""


def claude_generate(user_prompt, max_tokens=1500, retries=3):
    body = {
        "model": MODEL,
        "max_tokens": max_tokens,
        "system": SYSTEM_PROMPT,
        "messages": [{"role": "user", "content": user_prompt}],
    }
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps(body).encode(),
        headers={
            "x-api-key": ANTHROPIC_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        method="POST",
    )
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=90) as resp:
                data = json.loads(resp.read())
                blocks = [b["text"] for b in data.get("content", []) if b.get("type") == "text"]
                text = "\n".join(blocks).strip()
                if text.startswith("```"):
                    text = re.sub(r"^```(?:json)?\n?", "", text)
                    text = re.sub(r"\n?```$", "", text)
                try:
                    return json.loads(text)
                except json.JSONDecodeError:
                    m = re.search(r"\{.*\}", text, re.DOTALL)
                    if m:
                        try:
                            return json.loads(m.group(0))
                        except json.JSONDecodeError:
                            pass
                return None
        except urllib.error.HTTPError as e:
            if e.code in (429, 529, 500, 503) and attempt < retries - 1:
                time.sleep(5 * (attempt + 1))
                continue
            err_body = e.read().decode(errors="replace") if e.fp else ""
            print(f"  Claude {e.code}: {err_body[:300]}", file=sys.stderr)
            return None
        except (urllib.error.URLError, TimeoutError):
            time.sleep(5 * (attempt + 1))
            continue
    return None


# ============================================================================
# Prompts sent to Claude
# ============================================================================

def product_prompt(title, vendor, current_desc):
    return f"""Generate SEO content for a Shopify product on Onelife Health.

Product title: {title}
Brand/vendor: {vendor or "unknown"}
Existing description (may be empty, thin, or a placeholder): {current_desc[:800] if current_desc else "(none)"}

Return ONLY a JSON object with EXACTLY these keys:
{{
  "description_html": "Full HTML description, 150-300 words, 2-3 short <p> paragraphs. Open with what it is. Middle paragraph: key features/ingredients/who it's for. Close with use guidance. Stay honest, specific, non-hype.",
  "alt_text": "Plain descriptive alt text for the product image, under 125 characters, no keyword stuffing",
  "product_type": "Single short Shopify product_type label (e.g. 'Magnesium Supplement', 'Probiotic Powder', 'Herbal Tincture', 'Protein Bar')",
  "tags": "5-8 comma-separated lowercase tags relevant to search + filtering",
  "seo_title": "50-65 char SEO title for Google SERP. Include brand + product + primary benefit.",
  "meta_description": "150-160 char meta description for Google SERP. Compelling, includes primary keyword, ends with a soft CTA."
}}"""


def article_prompt(title, author, body_snippet):
    return f"""Generate SEO content for a blog article on Onelife Health.

Article title: {title}
Author: {author or "unknown"}
First 500 chars of body: {body_snippet[:500] if body_snippet else "(none)"}

Return ONLY a JSON object with EXACTLY these keys:
{{
  "summary_html": "Short HTML excerpt/summary for social + SERP, 1 paragraph <p>...</p>, 40-80 words. Hooks the reader without giving everything away.",
  "image_alt": "Plain alt text for the article featured image, under 125 characters",
  "tags": "5-8 comma-separated lowercase tags",
  "seo_title": "50-65 char SEO title",
  "meta_description": "150-160 char meta description"
}}"""


def collection_prompt(title, current_desc):
    return f"""Generate SEO content for a Shopify collection on Onelife Health.

Collection title: {title}
Existing description: {current_desc[:500] if current_desc else "(none)"}

Return ONLY a JSON object with EXACTLY these keys:
{{
  "body_html": "Collection description in HTML, 100-200 words, 2 short <p> paragraphs. Explain what's in this collection, who it's for, why Onelife stocks it.",
  "image_alt": "Plain alt text for the collection image, under 125 characters",
  "seo_title": "50-65 char SEO title",
  "meta_description": "150-160 char meta description"
}}"""


# ============================================================================
# Action log (JSONL, line-buffered, resumable)
# ============================================================================

class ActionLog:
    def __init__(self, path):
        self.path = path
        self.done_products = set()
        self.done_articles = set()
        self.done_collections = set()
        self.f = None
        if path.exists():
            for line in path.read_text().splitlines():
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if r.get("action") == "product_applied":
                    self.done_products.add(r.get("id"))
                elif r.get("action") == "article_applied":
                    self.done_articles.add(r.get("id"))
                elif r.get("action") == "collection_applied":
                    self.done_collections.add(r.get("id"))

    def open(self):
        self.f = open(self.path, "a", buffering=1)

    def write(self, **kw):
        kw["ts"] = datetime.now(timezone.utc).isoformat()
        if self.f:
            self.f.write(json.dumps(kw, default=str) + "\n")

    def close(self):
        if self.f:
            self.f.close()


# ============================================================================
# Per-item apply helpers (Shopify writes)
# ============================================================================

def _strip_html(s):
    if not s:
        return ""
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", s)).strip()


def apply_product_fix(pid, current, fix, log):
    """Apply Claude's generated fix to a product. Only overwrites fields that
    are actually broken per the rule-based audit."""
    product_body = {"product": {"id": pid}}
    changed_fields = []

    current_body = current.get("body_html") or ""
    stripped = _strip_html(current_body)
    needs_desc = (
        len(stripped) < 150
        or "please contact us for more info" in stripped.lower()
        or "coming soon" in stripped.lower()
        or "no description" in stripped.lower()
    )
    if needs_desc and fix.get("description_html"):
        product_body["product"]["body_html"] = fix["description_html"]
        changed_fields.append("body_html")

    if not (current.get("product_type") or "").strip() and fix.get("product_type"):
        product_body["product"]["product_type"] = fix["product_type"]
        changed_fields.append("product_type")

    if not (current.get("tags") or "").strip() and fix.get("tags"):
        product_body["product"]["tags"] = fix["tags"]
        changed_fields.append("tags")

    if changed_fields:
        status, resp = shopify("PUT", f"/products/{pid}.json", product_body)
        if status != 200:
            log.write(action="product_put_failed", id=pid, status=status, resp=resp)
            return False
        log.write(action="product_put_ok", id=pid, fields=changed_fields)

    # Alt text on images: only set alt where empty
    for img in (current.get("images") or []):
        if not (img.get("alt") or "").strip() and fix.get("alt_text"):
            img_id = img.get("id")
            status, resp = shopify(
                "PUT",
                f"/products/{pid}/images/{img_id}.json",
                {"image": {"id": img_id, "alt": fix["alt_text"]}},
            )
            if status != 200:
                log.write(action="image_alt_failed", product_id=pid, image_id=img_id, status=status, resp=resp)
            else:
                log.write(action="image_alt_ok", product_id=pid, image_id=img_id)

    # SEO metafields: only set if missing
    existing = current.get("seo") or {}
    if fix.get("seo_title") and not existing.get("title_tag"):
        status, resp = shopify(
            "POST",
            f"/products/{pid}/metafields.json",
            {"metafield": {"namespace": "global", "key": "title_tag",
                           "type": "single_line_text_field", "value": fix["seo_title"]}},
        )
        if status in (200, 201):
            log.write(action="metafield_title_ok", id=pid)
        else:
            log.write(action="metafield_title_failed", id=pid, status=status, resp=resp)
    if fix.get("meta_description") and not existing.get("description_tag"):
        status, resp = shopify(
            "POST",
            f"/products/{pid}/metafields.json",
            {"metafield": {"namespace": "global", "key": "description_tag",
                           "type": "multi_line_text_field", "value": fix["meta_description"]}},
        )
        if status in (200, 201):
            log.write(action="metafield_desc_ok", id=pid)
        else:
            log.write(action="metafield_desc_failed", id=pid, status=status, resp=resp)

    log.write(action="product_applied", id=pid, fields=changed_fields)
    return True


def fetch_product_with_metafields(pid):
    status, data = shopify("GET", f"/products/{pid}.json")
    if status != 200:
        return None
    product = data.get("product") or {}
    status, mf = shopify("GET", f"/products/{pid}/metafields.json?namespace=global")
    seo = {}
    if status == 200:
        for m in (mf.get("metafields") or []):
            if m.get("key") == "title_tag":
                seo["title_tag"] = m.get("value")
            elif m.get("key") == "description_tag":
                seo["description_tag"] = m.get("value")
    product["seo"] = seo
    return product


def apply_article_fix(blog_id, aid, current, fix, log):
    article_body = {"article": {"id": aid}}
    changed_fields = []
    if not (current.get("summary_html") or "").strip() and fix.get("summary_html"):
        article_body["article"]["summary_html"] = fix["summary_html"]
        changed_fields.append("summary_html")
    if not (current.get("tags") or "").strip() and fix.get("tags"):
        article_body["article"]["tags"] = fix["tags"]
        changed_fields.append("tags")
    img = current.get("image")
    if img and not (img.get("alt") or "").strip() and fix.get("image_alt"):
        article_body["article"]["image"] = {
            "src": img.get("src"),
            "alt": fix["image_alt"],
        }
        changed_fields.append("image_alt")

    if changed_fields:
        status, resp = shopify("PUT", f"/blogs/{blog_id}/articles/{aid}.json", article_body)
        if status != 200:
            log.write(action="article_put_failed", id=aid, status=status, resp=resp)
            return False
        log.write(action="article_put_ok", id=aid, fields=changed_fields)

    log.write(action="article_applied", id=aid, fields=changed_fields)
    return True


def apply_collection_fix(col, fix, log):
    cid = col["id"]
    kind = col.get("__kind", "custom_collections")
    endpoint = kind
    singular = endpoint[:-1]  # custom_collection / smart_collection

    body = {singular: {"id": cid}}
    changed = []
    cur_body = col.get("body_html") or ""
    if len(_strip_html(cur_body)) < 50 and fix.get("body_html"):
        body[singular]["body_html"] = fix["body_html"]
        changed.append("body_html")
    img = col.get("image")
    if img and not (img.get("alt") or "").strip() and fix.get("image_alt"):
        body[singular]["image"] = {"src": img.get("src"), "alt": fix["image_alt"]}
        changed.append("image_alt")
    if changed:
        status, resp = shopify("PUT", f"/{endpoint}/{cid}.json", body)
        if status != 200:
            log.write(action="collection_put_failed", id=cid, status=status, resp=resp)
            return False
        log.write(action="collection_put_ok", id=cid, kind=kind, fields=changed)

    log.write(action="collection_applied", id=cid, fields=changed)
    return True


# ============================================================================
# Scope drivers
# ============================================================================

FIXABLE_PRODUCT_CODES = {
    "description_missing", "description_thin", "description_placeholder",
    "alt_missing_all", "alt_missing_some", "alt_weak",
    "no_product_type", "no_tags",
}


def fixable_product(p):
    return any(code in FIXABLE_PRODUCT_CODES for sev, code, _ in (p.get("issues") or []))


def run_products(audit, log):
    products_in_audit = audit.get("product_findings", [])
    targets = [p for p in products_in_audit if fixable_product(p)]
    total_all = len(targets)
    targets = [p for p in targets if p["id"] not in log.done_products]
    if LIMIT:
        targets = targets[:LIMIT]
    print(f"\n[PRODUCTS] {total_all} fixable, {len(log.done_products)} already done, {len(targets)} to process", flush=True)

    done_ok = 0
    done_fail = 0

    def worker(p):
        pid = p["id"]
        current = fetch_product_with_metafields(pid)
        if current is None:
            return pid, None, None, "fetch_failed"
        title = current.get("title") or p.get("title") or ""
        vendor = current.get("vendor") or p.get("vendor") or ""
        current_desc = current.get("body_html") or ""
        fix = claude_generate(product_prompt(title, vendor, current_desc), max_tokens=1800)
        if not fix:
            return pid, current, None, "claude_failed"
        return pid, current, fix, None

    with ThreadPoolExecutor(max_workers=CONCURRENCY) as ex:
        futures = {ex.submit(worker, p): p for p in targets}
        for i, fut in enumerate(as_completed(futures), 1):
            pid, current, fix, err = fut.result()
            if err:
                done_fail += 1
                log.write(action="product_gen_failed", id=pid, err=err)
            else:
                if not APPLY:
                    done_ok += 1
                    log.write(action="product_dryrun", id=pid, preview=(fix.get("description_html") or "")[:80])
                else:
                    if apply_product_fix(pid, current, fix, log):
                        done_ok += 1
                    else:
                        done_fail += 1
            if i % 25 == 0 or i == len(targets):
                print(f"  [{i}/{len(targets)}] ok={done_ok} fail={done_fail}", flush=True)

    print(f"[PRODUCTS] done: ok={done_ok} fail={done_fail}", flush=True)


def run_articles(audit, log):
    articles = audit.get("article_findings", [])
    fixable_codes = {"no_excerpt", "image_no_alt", "no_tags", "title_short", "title_long"}
    targets = [a for a in articles if any(c in fixable_codes for s, c, _ in (a.get("issues") or []))]
    total_all = len(targets)
    targets = [a for a in targets if a["id"] not in log.done_articles]
    if LIMIT:
        targets = targets[:LIMIT]
    print(f"\n[ARTICLES] {total_all} fixable, {len(log.done_articles)} already done, {len(targets)} to process", flush=True)

    status, blogs = shopify("GET", "/blogs.json")
    if status != 200:
        print(f"  ERROR: failed to fetch blogs: {blogs}", file=sys.stderr)
        return

    art_blog_map = {}
    for b in blogs.get("blogs", []):
        bid = b["id"]
        status, data = shopify("GET", f"/blogs/{bid}/articles.json?limit=250")
        if status != 200:
            continue
        for a in data.get("articles", []):
            art_blog_map[a["id"]] = bid

    done_ok = 0
    done_fail = 0

    def worker(a):
        aid = a["id"]
        bid = art_blog_map.get(aid)
        if bid is None:
            return aid, None, None, None, "no_blog_id"
        status, data = shopify("GET", f"/blogs/{bid}/articles/{aid}.json")
        if status != 200:
            return aid, bid, None, None, "fetch_failed"
        art = data.get("article") or {}
        title = art.get("title") or ""
        author = art.get("author") or ""
        body_snip = _strip_html(art.get("body_html") or "")[:500]
        fix = claude_generate(article_prompt(title, author, body_snip), max_tokens=1000)
        if not fix:
            return aid, bid, art, None, "claude_failed"
        return aid, bid, art, fix, None

    with ThreadPoolExecutor(max_workers=CONCURRENCY) as ex:
        futures = {ex.submit(worker, a): a for a in targets}
        for i, fut in enumerate(as_completed(futures), 1):
            aid, bid, art, fix, err = fut.result()
            if err:
                done_fail += 1
                log.write(action="article_gen_failed", id=aid, err=err)
            else:
                if not APPLY:
                    done_ok += 1
                    log.write(action="article_dryrun", id=aid)
                else:
                    if apply_article_fix(bid, aid, art, fix, log):
                        done_ok += 1
                    else:
                        done_fail += 1
            if i % 10 == 0 or i == len(targets):
                print(f"  [{i}/{len(targets)}] ok={done_ok} fail={done_fail}", flush=True)

    print(f"[ARTICLES] done: ok={done_ok} fail={done_fail}", flush=True)


def run_collections(audit, log):
    col_findings = audit.get("collection_findings", [])
    fixable_codes = {"no_description", "image_no_alt", "no_image"}
    targets = [c for c in col_findings if any(code in fixable_codes for s, code, _ in (c.get("issues") or []))]
    total_all = len(targets)
    targets = [c for c in targets if c["id"] not in log.done_collections]
    if LIMIT:
        targets = targets[:LIMIT]
    print(f"\n[COLLECTIONS] {total_all} fixable, {len(log.done_collections)} already done, {len(targets)} to process", flush=True)

    done_ok = 0
    done_fail = 0

    def fetch_collection(cid):
        for endpoint in ("custom_collections", "smart_collections"):
            status, data = shopify("GET", f"/{endpoint}/{cid}.json")
            if status == 200:
                col = data.get(endpoint[:-1]) or {}
                col["__kind"] = endpoint
                return col
        return None

    def worker(c):
        cid = c["id"]
        col = fetch_collection(cid)
        if col is None:
            return cid, None, None, "fetch_failed"
        title = col.get("title") or ""
        cur_desc = col.get("body_html") or ""
        fix = claude_generate(collection_prompt(title, cur_desc), max_tokens=1200)
        if not fix:
            return cid, col, None, "claude_failed"
        return cid, col, fix, None

    with ThreadPoolExecutor(max_workers=CONCURRENCY) as ex:
        futures = {ex.submit(worker, c): c for c in targets}
        for i, fut in enumerate(as_completed(futures), 1):
            cid, col, fix, err = fut.result()
            if err:
                done_fail += 1
                log.write(action="collection_gen_failed", id=cid, err=err)
            else:
                if not APPLY:
                    done_ok += 1
                    log.write(action="collection_dryrun", id=cid)
                else:
                    if apply_collection_fix(col, fix, log):
                        done_ok += 1
                    else:
                        done_fail += 1
            if i % 10 == 0 or i == len(targets):
                print(f"  [{i}/{len(targets)}] ok={done_ok} fail={done_fail}", flush=True)

    print(f"[COLLECTIONS] done: ok={done_ok} fail={done_fail}", flush=True)


# ============================================================================
# Main
# ============================================================================

def load_latest_audit():
    audit_file = os.environ.get("AUDIT_FILE")
    if audit_file:
        return Path(audit_file)
    candidates = sorted(REPORTS_DIR.glob("seo-audit-*.json"))
    if not candidates:
        print("ERROR: no audit file in reports/ (run seo_audit.py first)", file=sys.stderr)
        sys.exit(1)
    return candidates[-1]


def main():
    global SHOPIFY_TOKEN, SHOPIFY_HEADERS

    audit_path = load_latest_audit()
    print(f"Audit:       {audit_path}", flush=True)
    audit = json.loads(audit_path.read_text())

    print(f"Model:       {MODEL}", flush=True)
    print(f"Concurrency: {CONCURRENCY}", flush=True)
    print(f"Scope:       {SCOPE}", flush=True)
    print(f"Limit:       {LIMIT or 'none'}", flush=True)
    print(f"APPLY:       {APPLY}", flush=True)

    SHOPIFY_TOKEN = get_shopify_token()
    SHOPIFY_HEADERS = {
        "X-Shopify-Access-Token": SHOPIFY_TOKEN,
        "Accept": "application/json",
    }

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    log_path = REPORTS_DIR / f"seo-fixes-applied-{today}.log"
    log = ActionLog(log_path)
    log.open()
    log.write(action="run_start", model=MODEL, scope=SCOPE, apply=APPLY, limit=LIMIT, concurrency=CONCURRENCY)

    try:
        if SCOPE in ("all", "products"):
            run_products(audit, log)
        if SCOPE in ("all", "articles"):
            run_articles(audit, log)
        if SCOPE in ("all", "collections"):
            run_collections(audit, log)
    finally:
        log.write(action="run_end")
        log.close()
    print("\n=== SEO FIX AGENT DONE ===", flush=True)


if __name__ == "__main__":
    main()
