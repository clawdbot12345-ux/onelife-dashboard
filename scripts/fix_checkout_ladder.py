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
import time
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
    for attempt in range(4):
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
            if e.code == 429 and attempt < 3:
                time.sleep(2 * (attempt + 1))
                continue
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
        # API rule: delay_until_* only valid when unit is 'days'
        if a.get("type") == "time-delay" and a["data"].get("unit") != "days":
            a["data"].pop("delay_until_weekdays", None)
            a["data"].pop("delay_until_time", None)
    if d.get("entry_action_id") is not None:
        d["entry_action_id"] = str(d["entry_action_id"])
    return d


def find_flows_by_name(name):
    out, url = [], "/flows/?page[size]=50"
    while url:
        st, data = req(url)
        if st != 200:
            break
        for f in (data or {}).get("data", []):
            if f["attributes"]["name"] == name:
                out.append((f["id"], f["attributes"]["status"],
                            f["attributes"].get("created", "")))
        nxt = ((data or {}).get("links") or {}).get("next")
        url = nxt.replace("https://a.klaviyo.com/api", "") if nxt else None
    return out


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
        time.sleep(3)  # create endpoint throttles aggressively
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

    # ── Touch 2/3 flow: ensure exactly ONE live copy, with guard + day-3 spacing ──
    touch_name = get_flow(TOUCH_FLOW)["name"]
    copies = find_flows_by_name(touch_name)
    live = sorted([c for c in copies if c[1] == "live"], key=lambda c: c[2])
    print(f"  '{touch_name}': {len(copies)} copies, {len(live)} live", file=sys.stderr)

    def has_guard(defn):
        groups = (defn.get("profile_filter") or {}).get("condition_groups") or []
        return any(c.get("type") == "profile-not-in-flow"
                   for g in groups for c in g.get("conditions", []))

    def fixed_spacing(defn):
        delays = [a for a in defn.get("actions", []) if a.get("type") == "time-delay"]
        return len(delays) >= 2 and delays[1]["data"].get("value", 0) >= 2

    # keep the oldest live copy that is fully correct; draft all other live copies
    keeper = None
    for fid, _, _ in live:
        defn = get_flow(fid)["definition"]
        if has_guard(defn) and fixed_spacing(defn):
            keeper = fid
            break
    if keeper:
        for fid, _, _ in live:
            if fid != keeper:
                print(f"  deduping extra live copy {fid}", file=sys.stderr)
                ok = set_status(fid, "draft") and ok
        print(f"  ✓ touch flow correct + unique: {keeper}", file=sys.stderr)
    elif live:
        # no correct live copy: fix the oldest live one via create-and-swap
        fid = live[0][0]
        attrs = get_flow(fid)
        d = attrs["definition"]
        backup(fid, d)
        new = copy.deepcopy(d)
        if not has_guard(new):
            groups = (new.get("profile_filter") or {}).get("condition_groups") or []
            groups.append(copy.deepcopy(NOT_IN_FLOW_7D))
            new["profile_filter"] = {"condition_groups": groups}
        delays = [a for a in new.get("actions", []) if a.get("type") == "time-delay"]
        if len(delays) >= 2 and delays[1]["data"].get("value") == 1:
            delays[1]["data"]["value"] = 2
        applied = patch_definition(fid, new, attrs["name"], attrs["status"]) \
            or replace_flow(fid, attrs["name"], new)
        for other, _, _ in live[1:]:
            applied = set_status(other, "draft") and applied
        ok = applied and ok
    else:
        print("  ✗ no live touch flow found — investigate", file=sys.stderr)
        ok = False

    # ── Consultant Check: optional 4h early touch (idempotent by name) ──
    if EARLY_TOUCH:
        consult_name = get_flow(CONSULT_FLOW)["name"]
        copies2 = sorted([c for c in find_flows_by_name(consult_name) if c[1] == "live"],
                         key=lambda c: c[2])
        print(f"  '{consult_name}': {len(copies2)} live", file=sys.stderr)

        def is_early(defn):
            entry = next((a for a in defn.get("actions", [])
                          if a.get("type") == "time-delay"), None)
            return bool(entry) and entry["data"].get("unit") == "hours"

        keeper2 = None
        for fid, _, _ in copies2:
            if is_early(get_flow(fid)["definition"]):
                keeper2 = fid
                break
        if keeper2:
            for fid, _, _ in copies2:
                if fid != keeper2:
                    ok = set_status(fid, "draft") and ok
            print(f"  ✓ consultant early-touch correct + unique: {keeper2}", file=sys.stderr)
        elif copies2:
            fid = copies2[0][0]
            attrs2 = get_flow(fid)
            d2 = attrs2["definition"]
            backup(fid, d2)
            new2 = copy.deepcopy(d2)
            entry = next((a for a in new2.get("actions", [])
                          if a.get("type") == "time-delay"), None)
            if entry and entry["data"].get("unit") == "days":
                entry["data"]["unit"] = "hours"
                entry["data"]["value"] = 4
                entry["data"].pop("delay_until_weekdays", None)
                entry["data"].pop("delay_until_time", None)
                print("  + consultant-check delay -> 4h", file=sys.stderr)
                applied2 = patch_definition(fid, new2, attrs2["name"], attrs2["status"]) \
                    or replace_flow(fid, attrs2["name"], new2)
                for other, _, _ in copies2[1:]:
                    applied2 = set_status(other, "draft") and applied2
                ok = applied2 and ok
            else:
                print(f"  {fid}: delay not in expected state, skipping", file=sys.stderr)
        else:
            print("  ✗ no live consultant flow found — investigate", file=sys.stderr)
            ok = False

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
