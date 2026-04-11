#!/usr/bin/env python3
"""
Onelife — Generate Blog Hero Images via Gemini 3 Pro Image (Nano Banana Pro)

Generates professional editorial hero images for Onelife blog posts and
uploads them to Shopify. Designed to run on a GitHub Actions runner (clean
IP, reaches Google) or locally on a developer machine.

Environment:
    GEMINI_API_KEY        Google AI Studio API key (AIza...)
    SHOPIFY_CLIENT_ID     Shopify Dev Dashboard app client ID
    SHOPIFY_CLIENT_SECRET Shopify Dev Dashboard app client secret
    SHOPIFY_STORE         Store handle (e.g. "onelifehealth")
    ARTICLE_IDS           Comma-separated article IDs (optional — defaults to 3 new blogs)

Usage:
    export GEMINI_API_KEY=AIza...
    export SHOPIFY_CLIENT_ID=6f58e9d...
    export SHOPIFY_CLIENT_SECRET=shpss_...
    export SHOPIFY_STORE=onelifehealth
    python scripts/generate_blog_images_gemini.py
"""
import base64
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
SHOPIFY_CLIENT_ID = os.environ.get("SHOPIFY_CLIENT_ID")
SHOPIFY_CLIENT_SECRET = os.environ.get("SHOPIFY_CLIENT_SECRET")
SHOPIFY_STORE = os.environ.get("SHOPIFY_STORE", "onelifehealth").replace(".myshopify.com", "")
GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-3-pro-image-preview")

if not GEMINI_API_KEY:
    print("ERROR: GEMINI_API_KEY not set", file=sys.stderr)
    sys.exit(1)
if not (SHOPIFY_CLIENT_ID and SHOPIFY_CLIENT_SECRET):
    print("ERROR: SHOPIFY_CLIENT_ID and SHOPIFY_CLIENT_SECRET required", file=sys.stderr)
    sys.exit(1)

# ─── Default blog targets and prompts ───
BLOG_IMAGE_SPECS = [
    {
        "article_id": 613049237814,
        "label": "Magnesium Glycinate",
        "prompt": (
            "Professional editorial product photography for a premium health supplement brand. "
            "A clean flat-lay composition from above showing three amber glass supplement bottles "
            "arranged on a soft cream linen textured surface. One bottle is open with small white "
            "capsules gently spilling onto the fabric. Fresh sage leaves, a single small smooth river "
            "stone in soft beige tones, and a minimalist ceramic dish beside the bottles. "
            "Soft natural morning light from the upper left creating gentle shadows. Shallow depth "
            "of field with sharp focus on the center bottle. Muted earthy palette: warm cream, soft "
            "sage green, natural wood tones. Generous negative space on the right side for potential "
            "text overlay. Premium wellness brand aesthetic reminiscent of Ritual or Seed Health. "
            "16:9 landscape format, photorealistic, ultra-high quality editorial photography."
        ),
        "alt": "Three premium magnesium glycinate supplement bottles in a flat-lay with sage leaves and natural morning light",
    },
    {
        "article_id": 613049270582,
        "label": "SA Winter Immunity",
        "prompt": (
            "Professional editorial wellness photography for a South African winter health blog. "
            "A warm cozy flat-lay featuring fresh oranges cut in half showing vibrant juicy flesh, "
            "whole lemons, a rustic hand-thrown ceramic mug of golden ginger turmeric tea with steam "
            "visibly rising, a small wooden board with raw honeycomb, fresh ginger root pieces, and "
            "a cinnamon stick. Arranged on a dark moody weathered wooden surface with a soft knitted "
            "sage green throw blanket draped in the background. Soft warm afternoon light from the "
            "side creating gentle shadows and highlighting the steam. Rich warm color palette: deep "
            "orange, golden yellow, sage green, warm wood tones. Shallow depth of field. 16:9 "
            "landscape format, photorealistic, premium editorial photography, ultra-high quality."
        ),
        "alt": "Cozy winter wellness flat-lay with oranges, lemons, ginger tea, honey, and a knitted throw",
    },
    {
        "article_id": 613049303350,
        "label": "Postbiotics",
        "prompt": (
            "Professional editorial product photography for a modern gut health brand. A minimalist "
            "artistic composition showing a clean white ceramic bowl of creamy probiotic yogurt "
            "drizzled with honey from a wooden dipper, fresh blueberries and blackberries scattered "
            "elegantly around, a small glass jar of fermented sauerkraut with its fork resting beside "
            "it, and a few small pieces of dark chocolate on a wooden board. Arranged on a light "
            "cream marble surface with soft morning light from the upper right creating gentle "
            "shadows. Shallow depth of field with sharp focus on the yogurt bowl. Modern wellness "
            "brand aesthetic: clean, minimal, earthy. Muted palette: cream, sage green, soft berry "
            "purple, warm gold accents. Generous negative space. 16:9 landscape format, "
            "photorealistic editorial quality, ultra-high resolution."
        ),
        "alt": "Modern gut health flat-lay with probiotic yogurt bowl, berries, sauerkraut, and honey",
    },
]


# ─── Shopify auth (client credentials grant) ───
def get_shopify_token():
    url = f"https://{SHOPIFY_STORE}.myshopify.com/admin/oauth/access_token"
    body = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "client_id": SHOPIFY_CLIENT_ID,
        "client_secret": SHOPIFY_CLIENT_SECRET,
    }).encode()
    req = urllib.request.Request(url, data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read())["access_token"]


# ─── Gemini 3 Pro Image generation ───
def generate_image(prompt, aspect_ratio="16:9"):
    """Call Nano Banana Pro (gemini-3-pro-image-preview). Returns image bytes or raises."""
    url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
           f"{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}")
    body = {
        "contents": [{"role": "user", "parts": [{"text": prompt}]}],
        "generationConfig": {
            "responseModalities": ["IMAGE"],
            "imageConfig": {"aspectRatio": aspect_ratio},
        },
    }
    req = urllib.request.Request(url, data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    with urllib.request.urlopen(req, timeout=300) as resp:
        data = json.loads(resp.read())

    candidates = data.get("candidates", [])
    if not candidates:
        raise RuntimeError(f"No candidates in response: {json.dumps(data)[:500]}")
    parts = candidates[0].get("content", {}).get("parts", [])
    for part in parts:
        if "inlineData" in part:
            return base64.b64decode(part["inlineData"]["data"]), part["inlineData"].get("mimeType", "image/png")
    raise RuntimeError(f"No inlineData found: {json.dumps(parts)[:500]}")


# ─── Shopify blog image upload ───
def upload_image_to_article(shopify_token, article_id, img_bytes, mime_type, alt_text, filename="hero.png"):
    """PUT article with base64-encoded image attachment."""
    b64 = base64.b64encode(img_bytes).decode("ascii")
    body = {
        "article": {
            "id": article_id,
            "image": {
                "attachment": b64,
                "filename": filename,
                "alt": alt_text,
            }
        }
    }
    url = (f"https://{SHOPIFY_STORE}.myshopify.com/admin/api/2025-01/blogs/"
           f"120011424054/articles/{article_id}.json")
    req = urllib.request.Request(url,
        data=json.dumps(body).encode(),
        headers={
            "X-Shopify-Access-Token": shopify_token,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="PUT")
    with urllib.request.urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read())
        return result["article"]["image"]["src"]


# ─── Main ───
def main():
    print(f"[1/3] Getting Shopify access token...", file=sys.stderr)
    try:
        token = get_shopify_token()
        print(f"  ✓ Token: {token[:20]}...{token[-8:]}", file=sys.stderr)
    except Exception as e:
        print(f"  ✗ {e}", file=sys.stderr)
        sys.exit(1)

    # Optional: filter by ARTICLE_IDS env var
    target_ids = os.environ.get("ARTICLE_IDS", "").strip()
    if target_ids:
        wanted = {int(x.strip()) for x in target_ids.split(",")}
        specs = [s for s in BLOG_IMAGE_SPECS if s["article_id"] in wanted]
    else:
        specs = BLOG_IMAGE_SPECS

    results = []
    for i, spec in enumerate(specs):
        print(f"\n[2.{i+1}/{len(specs)}] {spec['label']} (article {spec['article_id']})", file=sys.stderr)
        print(f"  → Generating image with {GEMINI_MODEL}...", file=sys.stderr)
        try:
            img_bytes, mime = generate_image(spec["prompt"])
            print(f"  ✓ Generated: {len(img_bytes):,} bytes ({mime})", file=sys.stderr)
        except urllib.error.HTTPError as e:
            err = e.read().decode()[:500]
            print(f"  ✗ Gemini HTTP {e.code}: {err}", file=sys.stderr)
            results.append({"label": spec["label"], "ok": False, "error": f"gemini {e.code}"})
            continue
        except Exception as e:
            print(f"  ✗ Gemini error: {e}", file=sys.stderr)
            results.append({"label": spec["label"], "ok": False, "error": str(e)})
            continue

        print(f"  → Uploading to Shopify article {spec['article_id']}...", file=sys.stderr)
        try:
            cdn_url = upload_image_to_article(token, spec["article_id"], img_bytes, mime, spec["alt"])
            print(f"  ✓ Uploaded: {cdn_url}", file=sys.stderr)
            results.append({"label": spec["label"], "ok": True, "cdn_url": cdn_url})
        except urllib.error.HTTPError as e:
            err = e.read().decode()[:500]
            print(f"  ✗ Shopify HTTP {e.code}: {err}", file=sys.stderr)
            results.append({"label": spec["label"], "ok": False, "error": f"shopify {e.code}"})
        except Exception as e:
            print(f"  ✗ Shopify error: {e}", file=sys.stderr)
            results.append({"label": spec["label"], "ok": False, "error": str(e)})

        # Rate limit between Gemini calls
        if i < len(specs) - 1:
            time.sleep(2)

    print(f"\n[3/3] Summary:", file=sys.stderr)
    ok_count = sum(1 for r in results if r["ok"])
    print(f"  {ok_count}/{len(results)} succeeded", file=sys.stderr)
    for r in results:
        mark = "✓" if r["ok"] else "✗"
        if r["ok"]:
            print(f"  {mark} {r['label']}: {r['cdn_url']}", file=sys.stderr)
        else:
            print(f"  {mark} {r['label']}: {r['error']}", file=sys.stderr)

    print(json.dumps({"results": results}))
    if ok_count == 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
