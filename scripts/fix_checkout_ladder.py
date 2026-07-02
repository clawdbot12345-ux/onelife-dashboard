#!/usr/bin/env python3
"""
Onelife — abandoned-checkout ladder fixes (customer complaint 2026-07-02:
repeat/fast flow emails; browse-abandonment was fixed manually, this closes
the same gaps on the checkout flows).

Safe changes (always applied):
  1. SN89LS (Touch 2/3 Companion): add the missing "not in this flow in the
     last 7 days" re-entry guard — without it a customer who starts checkout
     twice in a week gets both emails twice.
  2. SN89LS: second delay 1d -> 2d, so Touch 3 lands day 3 instead of
     colliding with the Consultant Check email + SMS on day 2.

Optional (EARLY_TOUCH=true): WY4cae (Consultant Check) delay 2d -> 4h so the
first touch lands in the high-recovery window. Off by default — owner call.

Uses PATCH /api/flows/{id} with attributes.definition. If the API rejects
definition updates, the script exits non-zero and prints the manual UI steps.
Backups of the original definitions are written to reports/flow-backups/.

Environment: KLAVIYO_API_KEY, EARLY_TOUCH (default false).
"""
import copy
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone

KLAVIYO_KEY = os.environ.get("KLAVIYO_API_KEY")
EARLY_TOUCH = os.environ.get("EARLY_TOUCH", "false").lower() == "true"
if not KLAVIYO_KEY:
    print("ERROR: KLAVIYO_API_KEY required", file=sys.stderr)
    sys.exit(1)

REVISIONS = ["2025-07-15.pre", "2025-04-15.pre", "2024-10-15.pre"]
TOUCH_FLOW = "SN89LS"
CONSULT_FLOW = "WY4cae"
NOT_IN_FLOW_7D = {"conditions": [{"type": "profile-not-in-flow",
                                  "timeframe_filter": {"type": "date", "operator": "in-the-last",
                                                       "unit": "day", "quantity": 7}}]}


def req(path, method="GET", body=None, revision=REVISIONS[0]):
    r = urllib.request.Request(
        "https://a.klaviyo.com/api" + path,
        data=json.dumps(body).encode() if body else None,
        headers={"Authorization": f"Klaviyo-API-Key {KLAVIYO_KEY}",
                 "accept": "application/vnd.api+json", "revision": revision,
                 **({"content-type": "application/vnd.api+json"} if body else {})},
        method=method)
    try:
        with urllib.request.urlopen(r, timeout=60) as resp:
            return resp.status, (json.loads(resp.read()) if resp.status != 204 else {})
    except urllib.error.HTTPError as e:
        return e.code, {"error": e.read().decode()[:500]}


def get_flow(flow_id):
    status, data = req(f"/flows/{flow_id}/?additional-fields[flow]=definition")
    if status != 200:
        print(f"✗ GET {flow_id}: {status} {json.dumps(data)[:300]}", file=sys.stderr)
        sys.exit(1)
    return data["data"]["attributes"]


def patch_definition(flow_id, definition, name, flow_status):
    # The API requires name + status alongside definition on PATCH
    body = {"data": {"type": "flow", "id": flow_id,
                     "attributes": {"name": name, "status": flow_status,
                                    "definition": definition}}}
    last = None
    for rev in REVISIONS:
        status, data = req(f"/flows/{flow_id}/", method="PATCH", body=body, revision=rev)
        if status in (200, 202, 204):
            print(f"  ✓ PATCH {flow_id} accepted (revision {rev})", file=sys.stderr)
            return True
        last = (rev, status, data)
    print(f"  ✗ PATCH {flow_id} rejected on all revisions; last: {last[0]} -> "
          f"{last[1]} {json.dumps(last[2])[:400]}", file=sys.stderr)
    return False


def to_create_definition(definition):
    """Convert a fetched definition (real ids) into create-shape (temporary ids)."""
    d = copy.deepcopy(definition)
    for a in d.get("actions", []):
        if "id" in a:
            a["temporary_id"] = str(a.pop("id"))
        links = a.get("links") or {}
        for k, v in list(links.items()):
            if v is not None:
                links[k] = str(v)
        msg = ((a.get("data") or {}).get("message") or {})
        msg.pop("id", None)
    if d.get("entry_action_id") is not None:
        d["entry_action_id"] = str(d["entry_action_id"])
    return d


def set_status(flow_id, status):
    st, data = req(f"/flows/{flow_id}/", method="PATCH",
                   body={"data": {"type": "flow", "id": flow_id,
                                  "attributes": {"status": status}}},
                   revision="2025-07-15")
    ok = st in (200, 202, 204)
    print(f"  {'✓' if ok else '✗'} status {flow_id} -> {status} ({st})", file=sys.stderr)
    if not ok:
        print(f"    {json.dumps(data)[:300]}", file=sys.stderr)
    return ok


def replace_flow(old_id, old_name, new_definition):
    """Create corrected clone (draft) -> draft old -> live new. Ordered so a
    partial failure can only cause a send gap, never duplicate sends."""
    create_body = {"data": {"type": "flow", "attributes": {
        "name": old_name, "definition": to_create_definition(new_definition)}}}
    created = None
    for rev in REVISIONS:
        st, data = req("/flows/", method="POST", body=create_body, revision=rev)
        if st in (200, 201):
            created = data["data"]["id"]
            print(f"  ✓ created replacement flow {created} (revision {rev})", file=sys.stderr)
            break
        print(f"  create attempt ({rev}): {st} {json.dumps(data)[:300]}", file=sys.stderr)
    if not created:
        return False
    if not set_status(old_id, "draft"):
        print(f"  ⚠ old flow {old_id} still live — leaving new flow {created} in draft "
              f"to avoid duplicates; draft {old_id} manually then set {created} live",
              file=sys.stderr)
        return False
    if not set_status(created, "live"):
        print(f"  ⚠ SEND GAP: {old_id} drafted but {created} not live — set "
              f"https://www.klaviyo.com/flow/{created}/edit live manually", file=sys.stderr)
        return False
    print(f"  ✓ replaced {old_id} with {created} (old drafted, new live)", file=sys.stderr)
    return True


def backup(flow_id, definition):
    os.makedirs("reports/flow-backups", exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    path = f"reports/flow-backups/{flow_id}-{ts}.json"
    with open(path, "w") as fh:
        json.dump(definition, fh, indent=2)
    print(f"  backup: {path}", file=sys.stderr)


def main():
    ok = True

    # ── SN89LS: re-entry guard + day-3 spacing ──
    attrs = get_flow(TOUCH_FLOW)
    d = attrs["definition"]
    backup(TOUCH_FLOW, d)
    new = copy.deepcopy(d)
    groups = (new.get("profile_filter") or {}).get("condition_groups") or []
    has_guard = any(c.get("type") == "profile-not-in-flow"
                    for g in groups for c in g.get("conditions", []))
    if not has_guard:
        groups.append(copy.deepcopy(NOT_IN_FLOW_7D))
        new["profile_filter"] = {"condition_groups": groups}
        print("  + re-entry guard (not in flow, 7 days)", file=sys.stderr)
    delays = [a for a in new.get("actions", []) if a.get("type") == "time-delay"]
    if len(delays) >= 2 and delays[1]["data"].get("unit") == "days" \
            and delays[1]["data"].get("value") == 1:
        delays[1]["data"]["value"] = 2
        print("  + second delay 1d -> 2d (Touch 3 lands day 3)", file=sys.stderr)
    if new != d:
        applied = patch_definition(TOUCH_FLOW, new, attrs["name"], attrs["status"])
        if not applied:
            print("  PATCH unsupported — falling back to create-and-swap", file=sys.stderr)
            applied = replace_flow(TOUCH_FLOW, attrs["name"], new)
        ok = applied and ok
    else:
        print(f"  {TOUCH_FLOW}: nothing to change", file=sys.stderr)

    # ── WY4cae: optional early touch ──
    if EARLY_TOUCH:
        attrs2 = get_flow(CONSULT_FLOW)
        d2 = attrs2["definition"]
        backup(CONSULT_FLOW, d2)
        new2 = copy.deepcopy(d2)
        entry = next((a for a in new2.get("actions", [])
                      if a.get("type") == "time-delay"), None)
        if entry and (entry["data"].get("unit"), entry["data"].get("value")) == ("days", 2):
            entry["data"]["unit"] = "hours"
            entry["data"]["value"] = 4
            print("  + consultant-check delay 2d -> 4h", file=sys.stderr)
            ok = patch_definition(CONSULT_FLOW, new2, attrs2["name"], attrs2["status"]) and ok
        else:
            print(f"  {CONSULT_FLOW}: delay not in expected state, skipping", file=sys.stderr)

    if not ok:
        print("\nMANUAL FALLBACK (Klaviyo UI):", file=sys.stderr)
        print(f"1. https://www.klaviyo.com/flow/{TOUCH_FLOW}/edit -> Trigger setup -> "
              "add profile filter: 'has NOT been in this flow in the last 7 days'; "
              "change the second Time Delay from 1 day to 2 days.", file=sys.stderr)
        if EARLY_TOUCH:
            print(f"2. https://www.klaviyo.com/flow/{CONSULT_FLOW}/edit -> first Time "
                  "Delay: 2 days -> 4 hours.", file=sys.stderr)
        sys.exit(1)
    print("✓ ladder fixes applied")


if __name__ == "__main__":
    main()
