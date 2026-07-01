#!/usr/bin/env python3
"""
Onelife — one-shot shipping-policy fix (site audit 2026-07-01, finding C1).

The storefront promises "FREE DELIVERY on orders over R400 nationwide" in the
announcement bar, popup, PDP and cart, but /policies/shipping-policy still
carried stale thresholds (free over R900 Gauteng / R1,400 nationwide). This
script rewrites the policy body via the Admin GraphQL API so the legal page
matches the promise customers buy against.

Environment:
    SHOPIFY_ADMIN_TOKEN   preferred (legacy shpat_ token)
    SHOPIFY_CLIENT_ID / SHOPIFY_CLIENT_SECRET  fallback (client credentials)
    SHOPIFY_STORE         default onelifehealth
    DRY_RUN=true          print current + new body, change nothing
Requires token scope: write_legal_policies.
"""
import json
import os
import sys
import urllib.parse
import urllib.request

SHOPIFY_STORE = os.environ.get("SHOPIFY_STORE", "onelifehealth").replace(".myshopify.com", "")
API_VERSION = "2025-01"
DRY_RUN = os.environ.get("DRY_RUN", "false").lower() == "true"

NEW_BODY = """<h2>Delivery &amp; Shipping Policy</h2>
<p>These terms outline the delivery policy for orders placed on <a href="https://onelife.co.za">onelife.co.za</a>.</p>

<h3>Free Delivery</h3>
<ul>
<li><strong>Free delivery nationwide on all orders over R400.</strong></li>
<li>Orders under R400: <strong>Gauteng R75</strong> flat rate · <strong>Rest of South Africa R130</strong> flat rate, calculated at checkout.</li>
<li><strong>Click &amp; Collect is always free</strong> at any of our three stores.</li>
</ul>

<h3>Payment &amp; Dispatch</h3>
<p>Orders placed and paid for on a working day before <strong>15:30</strong> will be dispatched the next working day, provided payment reflects in our account.</p>

<h3>Delivery Timeframe</h3>
<ul>
<li>Parcels are typically delivered within <strong>1–5 working days</strong> (Gauteng usually 1–2 working days).</li>
<li>You will receive an email with a waybill number and tracking link once dispatched.</li>
<li>If your parcel is delayed beyond 7–10 working days, contact us at <a href="mailto:orders@onelife.co.za">orders@onelife.co.za</a>.</li>
<li>Our courier cannot deliver to PO Boxes or post offices — please provide a physical delivery address.</li>
<li>Please ensure someone is available at the delivery address to receive and sign for the parcel.</li>
</ul>

<h3>Perishable Items</h3>
<ul>
<li>We will contact you after ordering any perishable item to confirm the best dispatch time.</li>
<li>Bread orders must be placed by <strong>Monday before 10:00</strong> for Wednesday dispatch.</li>
<li>Weekend perishable orders will be followed up on the next business day.</li>
</ul>

<h3>Click &amp; Collect &amp; In-Store Shopping</h3>
<p>All three stores are available for in-person shopping and Click &amp; Collect. Select Click &amp; Collect at checkout and we'll notify you when your order is ready — same-day for most orders.</p>
<ul>
<li><strong>Centurion:</strong> 117 Galway Ave, Hennopspark — 071 374 4910</li>
<li><strong>Glen Village:</strong> Glen Village Center South, Faerie Glen, Pretoria — 066 022 7457</li>
<li><strong>Edenvale:</strong> Shop 7, Green Valley Shopping Centre, Greenstone Hill, JHB — 077 356 0173</li>
</ul>

<h3>Questions?</h3>
<p>Email us at <a href="mailto:orders@onelife.co.za">orders@onelife.co.za</a> or visit any of our three stores.</p>"""


def get_token():
    override = os.environ.get("SHOPIFY_ADMIN_TOKEN")
    if override:
        return override
    cid, secret = os.environ.get("SHOPIFY_CLIENT_ID"), os.environ.get("SHOPIFY_CLIENT_SECRET")
    if not (cid and secret):
        return None
    body = urllib.parse.urlencode({
        "grant_type": "client_credentials", "client_id": cid, "client_secret": secret,
    }).encode()
    req = urllib.request.Request(
        f"https://{SHOPIFY_STORE}.myshopify.com/admin/oauth/access_token",
        data=body, headers={"Content-Type": "application/x-www-form-urlencoded"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read()).get("access_token")
    except urllib.error.HTTPError as e:
        print(f"✗ OAuth failed: {e.code} {e.read().decode()[:200]}", file=sys.stderr)
        return None


def graphql(token, query, variables=None):
    req = urllib.request.Request(
        f"https://{SHOPIFY_STORE}.myshopify.com/admin/api/{API_VERSION}/graphql.json",
        data=json.dumps({"query": query, "variables": variables or {}}).encode(),
        headers={"X-Shopify-Access-Token": token, "Content-Type": "application/json"},
        method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"✗ GraphQL HTTP {e.code}: {e.read().decode()[:400]}", file=sys.stderr)
        return None


def main():
    token = get_token()
    if not token:
        print("✗ No Shopify credentials available", file=sys.stderr)
        sys.exit(1)

    current = graphql(token, """
      query { shop { shopPolicies { type body } } }""")
    if current and not current.get("errors"):
        for p in current["data"]["shop"]["shopPolicies"]:
            if p["type"] == "SHIPPING_POLICY":
                print("── Current shipping policy (first 400 chars) ──", file=sys.stderr)
                print(p["body"][:400], file=sys.stderr)
                if "R400" in p["body"] and "R900" not in p["body"]:
                    print("Policy already mentions R400 and no R900 — nothing to do.")
                    return
    else:
        print(f"⚠ Could not read current policy: {json.dumps(current)[:300]}", file=sys.stderr)

    if DRY_RUN:
        print("DRY_RUN — new body below, no changes made:\n", file=sys.stderr)
        print(NEW_BODY)
        return

    result = graphql(token, """
      mutation UpdateShippingPolicy($body: String!) {
        shopPolicyUpdate(shopPolicy: {type: SHIPPING_POLICY, body: $body}) {
          shopPolicy { id type url }
          userErrors { code field message }
        }
      }""", {"body": NEW_BODY})

    if not result:
        sys.exit(1)
    if result.get("errors"):
        print(f"✗ GraphQL errors: {json.dumps(result['errors'])[:500]}", file=sys.stderr)
        sys.exit(1)
    payload = result["data"]["shopPolicyUpdate"]
    if payload["userErrors"]:
        print(f"✗ userErrors: {json.dumps(payload['userErrors'])}", file=sys.stderr)
        sys.exit(1)
    print(f"✓ Shipping policy updated: {payload['shopPolicy']['url']}")


if __name__ == "__main__":
    main()
