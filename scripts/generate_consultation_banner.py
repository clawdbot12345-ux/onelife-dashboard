#!/usr/bin/env python3
"""One-shot: generate consultation banner image via Gemini + upload to Shopify theme assets."""
import os, json, base64, urllib.parse, urllib.request
STORE = "onelifehealth"
THEME_ID = 152982192438
GEMINI_KEY = os.environ["GEMINI_API_KEY"]

# Shopify auth
body = urllib.parse.urlencode({"grant_type":"client_credentials","client_id":os.environ["SHOPIFY_CLIENT_ID"],"client_secret":os.environ["SHOPIFY_CLIENT_SECRET"]}).encode()
req = urllib.request.Request(f"https://{STORE}.myshopify.com/admin/oauth/access_token", data=body, headers={"Content-Type":"application/x-www-form-urlencoded"}, method="POST")
token = json.loads(urllib.request.urlopen(req,timeout=30).read())["access_token"]
H = {"X-Shopify-Access-Token":token,"Accept":"application/json"}

prompt = (
    "Professional editorial lifestyle photography for a premium South African health and wellness store hero banner. "
    "A warm inviting scene: a wooden table with an open notebook, a pen, a cup of herbal tea with steam rising, "
    "several premium amber glass supplement bottles arranged neatly, fresh green herbs (rosemary, mint) in a small ceramic vase, "
    "and reading glasses resting on the notebook. Soft warm morning light streaming from a window on the left, golden highlights. "
    "Suggests expert health advice in a calm welcoming environment. "
    "Muted earthy palette: warm cream, sage green, natural wood, soft gold light. "
    "Shallow depth of field. Ultra high quality, photorealistic, 16:9 wide landscape. "
    "NO text, NO words, NO letters, NO numbers, NO brand names, NO human faces, NO hands."
)

url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image-preview:generateContent?key={GEMINI_KEY}"
body2 = json.dumps({"contents":[{"role":"user","parts":[{"text":prompt}]}],"generationConfig":{"responseModalities":["IMAGE"],"imageConfig":{"aspectRatio":"16:9"}}}).encode()
req = urllib.request.Request(url, data=body2, headers={"Content-Type":"application/json"}, method="POST")
print("Generating image...", flush=True)
with urllib.request.urlopen(req, timeout=300) as r:
    data = json.loads(r.read())
for part in data.get("candidates",[{}])[0].get("content",{}).get("parts",[]):
    if "inlineData" in part:
        img = base64.b64decode(part["inlineData"]["data"])
        mime = part["inlineData"].get("mimeType","image/png")
        break
else:
    print("No image"); exit(1)
ext = "jpg" if "jpg" in mime or "jpeg" in mime else "png"
print(f"Generated: {len(img):,} bytes ({mime})")

# Upload to theme assets
b64 = base64.b64encode(img).decode()
body3 = json.dumps({"asset":{"key":f"assets/consultation-banner.{ext}","attachment":b64}}).encode()
req = urllib.request.Request(f"https://{STORE}.myshopify.com/admin/api/2025-01/themes/{THEME_ID}/assets.json",
    data=body3, headers={**H,"Content-Type":"application/json"}, method="PUT")
with urllib.request.urlopen(req,timeout=60) as r:
    result = json.loads(r.read())
    print(f"Uploaded: {result.get('asset',{}).get('public_url','')}")
print("Done!")
