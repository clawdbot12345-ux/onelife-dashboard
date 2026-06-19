#!/usr/bin/env python3
"""
Fix the live Welcome flow email copy in Klaviyo.

The Welcome flow (XZNrmz) Email 1 footer still advertises the *old* free-delivery
threshold ("Free delivery over R900 (Gauteng) | R1,400 (nationwide)"). The real,
current promise — used everywhere else on the site and in every other generated
email — is **"Free delivery over R400 nationwide"**. This contradicts the store
on the single email every new subscriber receives, so it needs correcting on the
live template.

This script walks the flow → email messages → their templates, then applies a
small set of conservative, well-bounded text substitutions (see REPLACEMENTS).

Safety model:
  * DUMP MODE (default): fetches and prints the full HTML/text of every email
    template in the flow, plus the distinct hex colours it uses and a preview of
    which substitutions *would* fire — but writes nothing. Use this to confirm
    the live wording before touching anything.
  * APPLY MODE (--apply): performs the substitutions and PATCHes each changed
    template. Prints a unified before/after diff for every template it writes.

A template is only ever PATCHed if at least one substitution actually changed its
content, so re-running is idempotent and a no-match run is a guaranteed no-op.

Environment:
    KLAVIYO_API_KEY  — required (Klaviyo private API key, Flows + Templates read,
                       Templates write)

Usage:
    python scripts/fix_welcome_email.py            # dump / dry-run, no writes
    python scripts/fix_welcome_email.py --apply     # apply + PATCH live templates
    python scripts/fix_welcome_email.py --flow XXXX # override the flow id
"""
import argparse
import difflib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

API_KEY = os.environ.get("KLAVIYO_API_KEY")
if not API_KEY:
    print("ERROR: KLAVIYO_API_KEY environment variable not set", file=sys.stderr)
    sys.exit(1)

BASE = "https://a.klaviyo.com/api"
HEADERS = {
    "accept": "application/vnd.api+json",
    "revision": "2025-07-15",
    "Authorization": f"Klaviyo-API-Key {API_KEY}",
}
DEFAULT_FLOW = "XZNrmz"  # Welcome — One Life Health (Full Sequence)

# ─── Substitutions ───────────────────────────────────────────────────────────
# Each entry is (compiled regex, replacement). They run in order against both the
# HTML and the plain-text body. Keep them tightly bounded so they can only touch
# the free-delivery footer line, never product names or unrelated "R900" amounts.
#
# Matches renderings like:
#   "Free delivery over R900 (Gauteng) | R1,400 (nationwide)"
#   "free delivery over R900 (Gauteng) | R1 400 (nationwide)"
#   "R900 Gauteng | R1,400 nationwide"
REPLACEMENTS = [
    (re.compile(
        r"[Ff]ree delivery over\s*R\s?900\s*\(?\s*Gauteng\s*\)?\s*[|\-/·•]?\s*"
        r"R\s?1[,\s]?400\s*\(?\s*nationwide\s*\)?",
    ), "Free delivery over R400 nationwide"),
    (re.compile(
        r"over\s*R\s?900\s*\(?\s*Gauteng\s*\)?\s*[|\-/·•]?\s*"
        r"R\s?1[,\s]?400\s*\(?\s*nationwide\s*\)?",
    ), "over R400 nationwide"),
    (re.compile(
        r"R\s?900\s*\(?\s*Gauteng\s*\)?\s*[|\-/·•]?\s*"
        r"R\s?1[,\s]?400\s*\(?\s*nationwide\s*\)?",
    ), "R400 nationwide"),
]

HEX_RE = re.compile(r"#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b")


# ─── HTTP ──────────────────────────────────────────────────────────────────--
def _request(method, path, body=None, retries=3):
    url = f"{BASE}{path}"
    data = json.dumps(body).encode() if body is not None else None
    headers = dict(HEADERS)
    if body is not None:
        headers["content-type"] = "application/vnd.api+json"
    for attempt in range(retries):
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                raw = resp.read()
                return json.loads(raw) if raw else {}
        except urllib.error.HTTPError as e:
            detail = e.read().decode()[:600]
            # 429 / 5xx are worth retrying; 4xx auth/permission errors are not.
            if e.code in (429, 500, 502, 503) and attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
            print(f"HTTP {e.code} on {method} {path}: {detail}", file=sys.stderr)
            raise
        except urllib.error.URLError as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
            print(f"Network error on {method} {path}: {e}", file=sys.stderr)
            raise


def get(path):
    return _request("GET", path)


# ─── Flow walking ─────────────────────────────────────────────────────────--
def email_messages_for_flow(flow_id):
    """Return [(action_id, message_id, message_name)] for every email message."""
    out = []
    actions = get(f"/flows/{flow_id}/flow-actions/")
    for action in actions.get("data", []):
        if action["attributes"].get("action_type") != "SEND_EMAIL":
            continue
        aid = action["id"]
        msgs = get(f"/flow-actions/{aid}/flow-messages/")
        for m in msgs.get("data", []):
            out.append((aid, m["id"], m["attributes"].get("name", "")))
    return out


def template_for_message(message_id):
    """Resolve the template a flow message renders. Returns (template_id, attrs)."""
    inc = get(f"/flow-messages/{message_id}/?include=template")
    tmpl = None
    for item in inc.get("included", []) or []:
        if item.get("type") == "template":
            tmpl = item
            break
    if tmpl is None:
        # Fall back to the relationship endpoint.
        rel = get(f"/flow-messages/{message_id}/template/")
        tmpl = rel.get("data")
    if not tmpl:
        return None, None
    return tmpl["id"], tmpl.get("attributes", {})


def apply_subs(content):
    """Return (new_content, n_changes) after running every replacement."""
    if not content:
        return content, 0
    n = 0
    for pattern, repl in REPLACEMENTS:
        content, count = pattern.subn(repl, content)
        n += count
    return content, n


def short_diff(old, new, label):
    old_lines = (old or "").splitlines()
    new_lines = (new or "").splitlines()
    diff = [
        ln for ln in difflib.unified_diff(
            old_lines, new_lines, fromfile=f"{label} (before)",
            tofile=f"{label} (after)", lineterm="",
        )
    ]
    # Keep only the changed hunks (unified_diff already does); cap noise.
    return "\n".join(diff)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true",
                    help="PATCH the live templates (default: dump/dry-run only)")
    ap.add_argument("--flow", default=DEFAULT_FLOW, help="Flow id (default: Welcome)")
    args = ap.parse_args()

    flow = get(f"/flows/{args.flow}/")
    fattrs = flow["data"]["attributes"]
    print(f"Flow {args.flow}: {fattrs.get('name')!r}  status={fattrs.get('status')}")

    messages = email_messages_for_flow(args.flow)
    if not messages:
        print("No email messages found in flow.", file=sys.stderr)
        sys.exit(1)
    print(f"Found {len(messages)} email message(s).\n")

    patched = 0
    for idx, (aid, mid, mname) in enumerate(messages, 1):
        tid, attrs = template_for_message(mid)
        print(f"── Email {idx}: message {mid} ({mname!r}) → template {tid}")
        if not tid:
            print("   (no resolvable template; skipping)\n")
            continue

        html = attrs.get("html") or ""
        text = attrs.get("text") or ""
        colours = sorted(set(HEX_RE.findall(html)))
        print(f"   editor_type={attrs.get('editor_type')}  name={attrs.get('name')!r}")
        print(f"   distinct hex colours: {', '.join(colours) if colours else '(none)'}")

        new_html, n_html = apply_subs(html)
        new_text, n_text = apply_subs(text)
        total = n_html + n_text

        if total == 0:
            print("   no free-delivery substitutions matched.\n")
            if not args.apply:
                # In dump mode, surface the footer area so we can eyeball wording.
                for needle in ("Free delivery", "free delivery", "R900", "R1,400", "R1 400"):
                    i = html.find(needle)
                    if i != -1:
                        print(f"   ↳ context for {needle!r}: …{html[max(0,i-40):i+90]}…")
                        break
            continue

        print(f"   substitutions: html={n_html} text={n_text}")
        print(short_diff(html, new_html, "html"))
        if n_text:
            print(short_diff(text, new_text, "text"))

        if not args.apply:
            print("   [dry-run] not writing. Re-run with --apply to PATCH.\n")
            continue

        body = {"data": {"type": "template", "id": tid, "attributes": {}}}
        if n_html:
            body["data"]["attributes"]["html"] = new_html
        if n_text:
            body["data"]["attributes"]["text"] = new_text
        _request("PATCH", f"/templates/{tid}/", body)
        patched += 1
        print(f"   ✓ PATCHed template {tid}\n")

    if args.apply:
        print(f"Done. Patched {patched} template(s).")
    else:
        print("Dry-run complete. No changes written.")


if __name__ == "__main__":
    main()
