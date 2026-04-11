#!/usr/bin/env python3
"""
Onelife — SEO Fix Agent

Takes the output of seo_audit.py and uses Claude Haiku 4.5 to generate
high-quality replacement content for products that failed rule-based checks.

Three modes:
  1. DRAFT MODE (default): generates proposed fixes to a review file
  2. SAMPLE MODE: generates fixes for N products (for review)
  3. APPLY MODE: actually pushes the fixes to Shopify via Admin API

Environment:
  ANTHROPIC_API_KEY       — required
  SHOPIFY_CLIENT_ID       — required
  SHOPIFY_CLIENT_SECRET   — required
  AUDIT_FILE              — path to seo-audit-YYYY-MM-DD.json (default: latest)
  FIX_SAMPLE_SIZE         — 0 = all, >0 = first N fixable products (default: 20)
  APPLY_FIXES             — "true" to actually push to Shopify (default: "false")
  FIX_MODEL               — default claude-haiku-4-5-20251001

Usage:
  # Dry run on 20 products:
  python scripts/seo_fix_agent.py

  # Dry run on all products:
  FIX_SAMPLE_SIZE=0 python scripts/seo_fix_agent.py

  # Actually apply fixes to 20 products:
  FIX_SAMPLE_SIZE=20 APPLY_FIXES=true python scripts/seo_fix_agent.py
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY")
CLIENT_ID = os.environ.get("SHOPIFY_CLIENT_ID")
CLIENT_SECRET = os.environ.get("SHOPIFY_CLIENT_SECRET")
STORE = os.environ.get("SHOPIFY_STORE", "onelifehealth").replace(".myshopify.com", "")
SAMPLE_SIZE = int(os.environ.get("FIX_SAMPLE_SIZE", "20"))
APPLY = os.environ.get("APPLY_FIXES", "false").lower() == "true"
MODEL = os.environ.get("FIX_MODEL", "claude-haiku-4-5-20251001")
API_VERSION = "2025-01"

if not ANTHROPIC_KEY:
    print("ERROR: ANTHROPIC_API_KEY not set", file=sys.stderr)
    sys.exit(1)
if APPLY and not (CLIENT_ID and CLIENT_SECRET):
    print("ERROR: SHOPIFY_CLIENT_ID + SECRET required for APPLY mode", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).resolve().parent.parent
REPORTS_DIR = ROOT / "reports"


# ─── Load audit JSON ───
def load_latest_audit():
    audit_file = os.environ.get("AUDIT_FILE")
    if audit_file:
        return Path(audit_file)
    # Find the most recent audit file
    candidates = sorted(REPORTS_DIR.glob("seo-audit-*.json"))
    if not candidates:
        print("ERROR: No audit files found in reports/", file=sys.stderr)
        sys.exit(1)
    return candidates[-1]


# ─── Anthropic Messages API ───
def claude_call(system_prompt, user_prompt, max_tokens=1500):
    body = {
        "model": MODEL,
        "max_tokens": max_tokens,
        "system": system_prompt,
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
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read())
                text_blocks = [b["text"] for b in data.get("content", []) if b.get("type") == "text"]
                return "\n".join(text_blocks)
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 2:
                time.sleep(5)
                continue
            print(f"  Claude API error {e.code}: {e.read().decode()[:300]}", file=sys.stderr)
            return None
    return None


# ─── Shopify token for apply mode ───
def get_shopify_token():
    url = f"https://{STORE}.myshopify.com/admin/oauth/access_token"
    body = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }).encode()
    req = urllib.request.Request(url, data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())["access_token"]


# ─── Fix generation ───
SYSTEM_PROMPT = """You are an expert SEO copywriter for Onelife Health, a South African health retail chain specialising in supplements, wellness products, and natural health goods. Your job is to generate high-quality, unique, SEO-optimised product content based on minimal input (product title + vendor).

Rules:
- Every output must be UNIQUE — never copy boilerplate text across products
- Use evidence-based, honest, non-hype tone (no "amazing", "revolutionary", "life-changing")
- Speak to South African customers (mention local context when relevant, use "R" for prices, "SA" for country)
- Descriptions should be 150-300 words, structured with 2-3 short paragraphs
- Include natural keyword usage (not stuffing)
- Image alt text should describe the product visually in under 125 characters
- Product type should be a short category label (e.g. "Magnesium Supplement", "Probiotic Powder")
- Tags should be 5-8 comma-separated keywords relevant to search queries
- Always respond in valid JSON matching the schema the user specifies"""


def generate_fixes_for_product(title, vendor, handle, existing_desc=None):
    """Ask Claude to generate all missing SEO fields for a product."""
    user_prompt = f"""Generate SEO content for this product on Onelife Health's Shopify store.

Product title: {title}
Vendor/brand: {vendor or "Unknown"}
URL handle: {handle or "?"}
Existing description (if any): {existing_desc or "(none)"}

Return a JSON object with exactly these keys:
{{
  "description_html": "<p>Full product description as HTML, 150-300 words, 2-3 paragraphs. Use <p> tags. Include what it is, key benefits, who it's for, how to use. Be specific and honest. DO NOT invent claims you can't support from the product name.</p>",
  "alt_text": "Short descriptive alt text for the product image, under 125 characters",
  "product_type": "Single short category label",
  "tags": "tag1, tag2, tag3, tag4, tag5",
  "seo_title": "Optional 50-60 char SEO title if the product title itself is weak (leave blank if title is already good)",
  "meta_description": "Short compelling 150-160 char meta description for search results"
}}

Return ONLY the JSON object, no markdown code blocks, no explanations."""

    response = claude_call(SYSTEM_PROMPT, user_prompt, max_tokens=1500)
    if not response:
        return None
    # Strip markdown code blocks if the model wrapped the response
    response = response.strip()
    if response.startswith("```"):
        response = re.sub(r"^```(?:json)?\n?", "", response)
        response = re.sub(r"\n?```$", "", response)
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        # Try to extract JSON object from the response
        match = re.search(r"\{.*\}", response, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
    print(f"  ⚠ Could not parse JSON response", file=sys.stderr)
    return None


# ─── Filter fixable products ───
FIXABLE_CODES = {
    "description_missing", "description_thin", "description_placeholder",
    "alt_missing_all", "alt_missing_some", "alt_weak",
    "title_allcaps", "title_short", "title_long",
    "no_product_type", "no_tags",
}


def is_fixable(product_finding):
    """A product is fixable if at least one of its issues is in FIXABLE_CODES."""
    return any(code in FIXABLE_CODES for sev, code, _ in product_finding.get("issues", []))


# ─── Apply fixes via Shopify ───
def apply_fix_to_shopify(token, product_id, fix):
    """PUT the product with updated fields."""
    body = {"article": {"id": product_id}}
    # Actually PRODUCT update
    product_body = {
        "product": {
            "id": product_id,
        }
    }
    if fix.get("description_html"):
        product_body["product"]["body_html"] = fix["description_html"]
    if fix.get("product_type"):
        product_body["product"]["product_type"] = fix["product_type"]
    if fix.get("tags"):
        product_body["product"]["tags"] = fix["tags"]

    url = f"https://{STORE}.myshopify.com/admin/api/{API_VERSION}/products/{product_id}.json"
    req = urllib.request.Request(url,
        data=json.dumps(product_body).encode(),
        headers={
            "X-Shopify-Access-Token": token,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="PUT")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            result = json.loads(r.read())
            return True
    except urllib.error.HTTPError as e:
        print(f"    Shopify PUT error {e.code}: {e.read().decode()[:200]}", file=sys.stderr)
        return False


# ─── Main ───
def main():
    audit_path = load_latest_audit()
    print(f"Loading audit: {audit_path}", file=sys.stderr)
    audit = json.loads(audit_path.read_text())

    products = audit.get("product_findings", [])
    fixable = [p for p in products if is_fixable(p)]
    print(f"Total products in audit: {len(products):,}", file=sys.stderr)
    print(f"Fixable products (with issues we can rewrite): {len(fixable):,}", file=sys.stderr)

    # Apply sample limit
    if SAMPLE_SIZE and SAMPLE_SIZE > 0:
        target = fixable[:SAMPLE_SIZE]
        print(f"Processing first {SAMPLE_SIZE} fixable products (sample mode)", file=sys.stderr)
    else:
        target = fixable
        print(f"Processing ALL {len(target):,} fixable products (full mode)", file=sys.stderr)

    # Get Shopify token if applying
    shopify_token = None
    if APPLY:
        print(f"\n⚠ APPLY MODE: fixes will be PUSHED to Shopify\n", file=sys.stderr)
        shopify_token = get_shopify_token()

    # Generate fixes
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    fixes_path = REPORTS_DIR / f"seo-fixes-{today}.jsonl"
    applied_count = 0
    failed_count = 0
    skipped_count = 0

    with open(fixes_path, "a") as out_f:
        for i, p in enumerate(target, 1):
            title = p.get("title", "")
            handle = p.get("handle", "")
            vendor = p.get("vendor", "")
            product_id = p.get("id")

            # Get existing description from the audit (it's in product_findings)
            existing_desc = None  # The audit doesn't carry body_html through — would need to re-fetch
            # Skip this for now, Claude can generate from title alone

            issue_codes = [code for sev, code, _ in p.get("issues", [])]
            print(f"\n[{i}/{len(target)}] {title[:55]}", file=sys.stderr)
            print(f"  Issues: {', '.join(issue_codes)}", file=sys.stderr)

            fix = generate_fixes_for_product(title, vendor, handle, existing_desc)
            if not fix:
                print(f"  ⚠ Claude returned nothing — skipping", file=sys.stderr)
                skipped_count += 1
                continue

            record = {
                "product_id": product_id,
                "title": title,
                "handle": handle,
                "issues_before": issue_codes,
                "fix": fix,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "applied": False,
            }

            if APPLY:
                success = apply_fix_to_shopify(shopify_token, product_id, fix)
                record["applied"] = success
                if success:
                    print(f"  ✓ Applied to Shopify product {product_id}", file=sys.stderr)
                    applied_count += 1
                else:
                    failed_count += 1
            else:
                print(f"  ✓ Fix generated (dry run)", file=sys.stderr)
                print(f"    Preview: {fix.get('description_html','')[:120]}...", file=sys.stderr)

            out_f.write(json.dumps(record) + "\n")
            time.sleep(0.5)  # gentle rate limit

    # Final report
    print(f"\n═══ SEO FIX AGENT COMPLETE ═══", file=sys.stderr)
    print(f"  Fixes generated: {len(target) - skipped_count}", file=sys.stderr)
    if APPLY:
        print(f"  Applied to Shopify: {applied_count}", file=sys.stderr)
        print(f"  Failed: {failed_count}", file=sys.stderr)
    print(f"  Skipped: {skipped_count}", file=sys.stderr)
    print(f"\n  Fixes file: {fixes_path}", file=sys.stderr)
    if not APPLY:
        print(f"\n  To apply these fixes, re-run with APPLY_FIXES=true", file=sys.stderr)


if __name__ == "__main__":
    main()
