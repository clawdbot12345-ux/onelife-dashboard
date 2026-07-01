#!/usr/bin/env python3
"""
Onelife — Klaviyo flow trigger audit.

The June 2026 dashboard data shows three broken automations:
  - Win-Back 60 v2 and Win-Back 90/120: live but ZERO recipients in 30 days
    despite 1,462 at-risk profiles
  - PCOS Post-Purchase: 302 recipients, R0 revenue
  - Abandoned Checkout: only 36 recipients/month on ~349 started checkouts

This script dumps every live flow's status + trigger + entry conditions
(via the flow definition additional field) so the misconfiguration can be
identified precisely. Output: reports/flow-audit-<date>.md plus raw JSON.

Environment: KLAVIYO_API_KEY (read access to Flows is enough).
"""
import json
import os
import re
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone

KLAVIYO_KEY = os.environ.get("KLAVIYO_API_KEY")
if not KLAVIYO_KEY:
    print("ERROR: KLAVIYO_API_KEY required", file=sys.stderr)
    sys.exit(1)

HEADERS = {"Authorization": f"Klaviyo-API-Key {KLAVIYO_KEY}",
           "accept": "application/vnd.api+json", "revision": "2025-04-15"}
FOCUS = re.compile(r"win.?back|abandon|post.?purchase|checkout|replenish|sunset", re.I)


def get(url):
    req = urllib.request.Request(url, headers=HEADERS)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.loads(r.read())
    except urllib.error.HTTPError as e:
        print(f"  ERROR GET {url[:100]}: {e.code} {e.read().decode()[:300]}", file=sys.stderr)
        return None


def list_flows():
    flows, url = [], "https://a.klaviyo.com/api/flows/?page[size]=50"
    while url:
        page = get(url)
        if not page:
            break
        flows.extend(page.get("data", []))
        url = (page.get("links") or {}).get("next")
    return flows


def flow_definition(flow_id):
    return get(f"https://a.klaviyo.com/api/flows/{flow_id}/"
               f"?additional-fields[flow]={urllib.parse.quote('definition')}")


def summarize_definition(defn):
    """Pull the trigger + entry/profile filters out of a flow definition."""
    if not defn:
        return "definition unavailable"
    out = []
    triggers = defn.get("triggers") or []
    for t in triggers:
        out.append(f"trigger: {json.dumps(t, default=str)[:600]}")
    ep = defn.get("entry_action_id") or ""
    if ep:
        out.append(f"entry_action_id: {ep}")
    pf = defn.get("profile_filter")
    if pf:
        out.append(f"profile_filter: {json.dumps(pf, default=str)[:600]}")
    return "\n  ".join(out) if out else json.dumps(defn, default=str)[:800]


def main():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    flows = list_flows()
    print(f"Flows found: {len(flows)}", file=sys.stderr)

    lines = [f"# Klaviyo Flow Trigger Audit — {today}", "",
             f"{len(flows)} flows in the account. Focus flows (winback/abandon/"
             f"post-purchase/checkout/replenish/sunset) include full trigger detail.", ""]
    raw = {}
    lines.append("| Flow | Status | Trigger type | Created | Updated |")
    lines.append("|---|---|---|---|---|")
    focus_ids = []
    for f in flows:
        a = f.get("attributes", {})
        name = a.get("name", "?")
        lines.append(f"| {name} | {a.get('status','?')} | {a.get('trigger_type','?')} "
                     f"| {str(a.get('created','?'))[:10]} | {str(a.get('updated','?'))[:10]} |")
        if FOCUS.search(name):
            focus_ids.append((f.get("id"), name, a.get("status")))

    lines += ["", "## Focus flows — trigger detail", ""]
    for fid, name, status in focus_ids:
        detail = flow_definition(fid)
        defn = (((detail or {}).get("data") or {}).get("attributes") or {}).get("definition")
        raw[fid] = {"name": name, "definition": defn}
        lines += [f"### {name} (`{fid}`, {status})", "",
                  "```", summarize_definition(defn), "```", ""]

    os.makedirs("reports", exist_ok=True)
    md_path = f"reports/flow-audit-{today}.md"
    with open(md_path, "w") as fh:
        fh.write("\n".join(lines))
    with open(f"reports/flow-audit-{today}.json", "w") as fh:
        json.dump(raw, fh, indent=2, default=str)
    print(f"✓ Wrote {md_path} (+ raw JSON)")


if __name__ == "__main__":
    main()
