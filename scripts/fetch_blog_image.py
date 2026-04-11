#!/usr/bin/env python3
"""
Onelife — Blog Image Fetcher

Finds a relevant CC-licensed image via Openverse (no API key needed) and
uploads it to a Shopify article as the featured image.

Usage (standalone):
    python scripts/fetch_blog_image.py <article_id> "<search query>"

Or imported by publish_blog.py to auto-add images to new blogs.
"""
import json
import os
import sys
import urllib.request
import urllib.parse

OPENVERSE_UA = "OnelifeBlogPipeline/1.0 (info@onelife.co.za)"


def search_openverse(query, limit=10):
    """Search Openverse for landscape images matching the query."""
    params = urllib.parse.urlencode({
        "q": query,
        "format": "json",
        "page_size": limit,
    })
    req = urllib.request.Request(
        f"https://api.openverse.org/v1/images/?{params}",
        headers={"Accept": "application/json", "User-Agent": OPENVERSE_UA}
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"Openverse error {e.code}: {e.read().decode()[:200]}", file=sys.stderr)
        return None


def pick_best_image(results, query):
    """Pick the best landscape image from the results. Falls back gracefully."""
    if not results:
        return None

    def score(img):
        width = img.get("width") or 0
        height = img.get("height") or 0
        if width < 640 or height == 0:
            return -1
        aspect = width / height
        url = img.get("url", "")
        source_score = 10 if "staticflickr.com" in url else 5
        # Prefer landscape (aspect 1.2-2.5) but don't exclude others
        aspect_score = 0
        if 1.2 <= aspect <= 2.5:
            aspect_score = 50
        elif 1.0 <= aspect < 1.2:
            aspect_score = 20
        elif aspect > 2.5:
            aspect_score = 10
        return width + aspect_score + source_score * 10

    scored = [(score(img), img) for img in results]
    scored = [(s, img) for s, img in scored if s > 0]
    if not scored:
        return results[0] if results else None
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[0][1]


def attach_image_to_shopify_article(article_id, image_url, alt_text, shopify_token, store):
    """PATCH the Shopify article to set article.image.src.

    Shopify will fetch the remote URL and upload it to their CDN.
    """
    body = {
        "article": {
            "id": article_id,
            "image": {
                "src": image_url,
                "alt": alt_text,
            }
        }
    }
    url = f"https://{store}.myshopify.com/admin/api/2025-01/blogs/120011424054/articles/{article_id}.json"
    req = urllib.request.Request(
        url,
        data=json.dumps(body).encode(),
        headers={
            "X-Shopify-Access-Token": shopify_token,
            "Content-Type": "application/json",
            "Accept": "application/json",
        },
        method="PUT",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            result = json.loads(resp.read())
            return result["article"].get("image")
    except urllib.error.HTTPError as e:
        print(f"Shopify image attach error {e.code}: {e.read().decode()[:300]}", file=sys.stderr)
        return None


def get_shopify_token():
    """Helper for standalone use: exchange client credentials for access token."""
    override = os.environ.get("SHOPIFY_ADMIN_TOKEN")
    if override:
        return override
    client_id = os.environ.get("SHOPIFY_CLIENT_ID")
    client_secret = os.environ.get("SHOPIFY_CLIENT_SECRET")
    store = os.environ.get("SHOPIFY_STORE", "onelifehealth").replace(".myshopify.com", "")
    if not (client_id and client_secret):
        return None
    body = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }).encode()
    req = urllib.request.Request(
        f"https://{store}.myshopify.com/admin/oauth/access_token",
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read()).get("access_token")
    except urllib.error.HTTPError:
        return None


def fetch_and_attach(article_id, query, alt_text=None):
    """Main entry point. Returns (success, image_url_or_error)."""
    token = get_shopify_token()
    if not token:
        return False, "No Shopify token (set SHOPIFY_ADMIN_TOKEN or SHOPIFY_CLIENT_ID/SECRET)"
    store = os.environ.get("SHOPIFY_STORE", "onelifehealth").replace(".myshopify.com", "")

    results = search_openverse(query)
    if not results:
        return False, "Openverse search failed"
    picked = pick_best_image(results.get("results", []), query)
    if not picked:
        return False, "No suitable image found"

    image_url = picked.get("url")
    title = picked.get("title", "Wellness image")
    alt = alt_text or title[:140]

    print(f"  → picked: {title[:60]}", file=sys.stderr)
    print(f"     {picked.get('width')}x{picked.get('height')} from {picked.get('source','?')}", file=sys.stderr)
    print(f"     {image_url}", file=sys.stderr)

    attached = attach_image_to_shopify_article(article_id, image_url, alt, token, store)
    if attached:
        return True, attached.get("src")
    return False, "Shopify rejected the image"


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: fetch_blog_image.py <article_id> '<query>'", file=sys.stderr)
        sys.exit(1)
    article_id = int(sys.argv[1])
    query = sys.argv[2]
    ok, result = fetch_and_attach(article_id, query)
    if ok:
        print(f"✓ Image attached: {result}")
    else:
        print(f"✗ Failed: {result}")
        sys.exit(1)
