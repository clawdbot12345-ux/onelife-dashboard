#!/usr/bin/env python3
"""
Onelife — Dedup Apply (DESTRUCTIVE BUT REVERSIBLE)

Reads reports/dedup-breakdown-YYYY-MM-DD.json and executes the merge plan
against live Shopify in three phases:

  Phase 1 — Stock transfers
    For every queued variant transfer in the plan, fetch the current stock
    of both source and canonical variants, set the canonical variant's
    inventory to (current_canonical + current_source), then set the source
    variant's inventory to 0. Uses POST /inventory_levels/set.json which
    writes absolute values (race-safer than adjust.json deltas).

  Phase 2 — Archive non-canonicals
    PUT /products/:id with status=archived for every product flagged as
    'archive' in the plan. This is fully reversible by setting the status
    back to 'active'.

  Phase 3 — 301 redirects
    For every archived product, POST /redirects.json to send the old
    /products/<handle> URL to the canonical's /products/<handle>. This
    preserves SEO and any existing backlinks. Skips gracefully if the
    redirect already exists (Shopify 422).

Gating:
  APPLY=true must be set in the environment or the script prints the plan
  and exits without any writes. This prevents accidental execution.

Resumability:
  Every action is appended to reports/dedup-applied-YYYY-MM-DD.log as
  JSONL. On re-run, previously-archived product_ids and previously-created
  redirects are skipped.

Usage:
  APPLY=true \\
  SHOPIFY_CLIENT_ID=... \\
  SHOPIFY_CLIENT_SECRET=... \\
  SHOPIFY_STORE=onelifehealth \\
      python3 scripts/dedup_apply.py \\
          [--plan reports/dedup-breakdown-2026-04-11.json] \\
          [--limit N] \\
          [--skip-redirects]
"""
import argparse
import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

STORE = os.environ.get("SHOPIFY_STORE", "onelifehealth").replace(".myshopify.com", "")
API_VERSION = "2025-01"
SLEEP_BETWEEN_CALLS = 0.5  # seconds; 2 req/sec under Shopify REST leak rate

HEADERS = {}  # populated in main()


def get_token():
    client_id = os.environ.get("SHOPIFY_CLIENT_ID")
    client_secret = os.environ.get("SHOPIFY_CLIENT_SECRET")
    if not (client_id and client_secret):
        print("ERROR: SHOPIFY_CLIENT_ID + SECRET required", file=sys.stderr)
        sys.exit(1)
    body = urllib.parse.urlencode({
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
    }).encode()
    req = urllib.request.Request(
        f"https://{STORE}.myshopify.com/admin/oauth/access_token",
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())["access_token"]


def api_request(method, path, body=None):
    """Make a Shopify REST request with 429 retry. Returns (status, body_json).

    On HTTP errors returns (status_code, {"__error__": body_text}).
    On network errors returns (-1, {"__error__": str(exc)}).
    """
    url = f"https://{STORE}.myshopify.com/admin/api/{API_VERSION}{path}"
    data = None
    req_headers = dict(HEADERS)
    if body is not None:
        data = json.dumps(body).encode()
        req_headers["Content-Type"] = "application/json"
    for attempt in range(5):
        req = urllib.request.Request(url, data=data, headers=req_headers, method=method)
        try:
            with urllib.request.urlopen(req, timeout=45) as resp:
                raw = resp.read()
                out = json.loads(raw) if raw else {}
                time.sleep(SLEEP_BETWEEN_CALLS)
                return resp.status, out
        except urllib.error.HTTPError as e:
            if e.code == 429:
                retry_after = int(e.headers.get("Retry-After", "2"))
                time.sleep(max(retry_after, 2))
                continue
            err_body = e.read().decode(errors="replace") if e.fp else ""
            time.sleep(SLEEP_BETWEEN_CALLS)
            return e.code, {"__error__": err_body}
        except (urllib.error.URLError, TimeoutError) as e:
            # transient network — back off and retry
            time.sleep(2 ** attempt)
            continue
    return -1, {"__error__": "max retries exceeded"}


def fetch_online_location_id(plan):
    """Return (location_id, label) for the online warehouse.

    Strategy 1: GET /locations.json (needs read_locations scope).
    Strategy 2: probe via a known variant's inventory_levels (only needs
                read_inventory, which the analyzer already uses).
    """
    status, data = api_request("GET", "/locations.json")
    if status == 200:
        locations = [L for L in data.get("locations", []) if L.get("active")]
        if len(locations) == 1:
            return locations[0]["id"], locations[0].get("name", "")
        for L in locations:
            if "online" in (L.get("name") or "").lower():
                return L["id"], L["name"]
        if locations:
            return locations[0]["id"], locations[0]["name"]

    # Fall back: probe a known variant
    print("  /locations.json unavailable; probing via variant inventory_levels...",
          file=sys.stderr)
    probe_variant_id = None
    for g in plan["merge_plan"]:
        if g["merge"]["transfers"]:
            probe_variant_id = g["merge"]["transfers"][0]["from_variant_id"]
            break
    if probe_variant_id is None:
        # Fall back further: fetch one archive product's first variant
        for g in plan["merge_plan"]:
            if g["archive"]:
                arch_id = g["archive"][0]["id"]
                s, d = api_request("GET", f"/products/{arch_id}.json")
                if s == 200:
                    variants = d.get("product", {}).get("variants") or []
                    if variants:
                        probe_variant_id = variants[0]["id"]
                        break
    if probe_variant_id is None:
        print("ERROR: could not find any variant to probe for location_id",
              file=sys.stderr)
        sys.exit(1)

    s, d = api_request("GET", f"/variants/{probe_variant_id}.json")
    if s != 200:
        print(f"ERROR: variant probe failed: {d}", file=sys.stderr)
        sys.exit(1)
    inv_item = d["variant"]["inventory_item_id"]
    s, d = api_request("GET", f"/inventory_levels.json?inventory_item_ids={inv_item}")
    if s != 200:
        print(f"ERROR: inventory_levels probe failed: {d}", file=sys.stderr)
        sys.exit(1)
    levels = d.get("inventory_levels", [])
    if not levels:
        print("ERROR: no inventory_levels returned for probe item", file=sys.stderr)
        sys.exit(1)
    return levels[0]["location_id"], f"(probed via variant {probe_variant_id})"


def load_log(log_path):
    """Parse the applied log to extract already-done archive ids and
    already-created redirect paths, so re-runs are idempotent."""
    archived_ids = set()
    redirect_paths = set()
    if not log_path.exists():
        return archived_ids, redirect_paths
    with open(log_path) as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            if rec.get("phase") == 2 and rec.get("action") == "archived":
                archived_ids.add(rec.get("product_id"))
            elif rec.get("phase") == 3 and rec.get("action") == "redirect_created":
                redirect_paths.add(rec.get("from_path"))
    return archived_ids, redirect_paths


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--plan", default=None, help="Path to dedup-breakdown-*.json (defaults to today's)")
    p.add_argument("--limit", type=int, default=None, help="Only process first N archives (for canary)")
    p.add_argument("--skip-redirects", action="store_true", help="Skip phase 3 (redirects)")
    return p.parse_args()


def main():
    global HEADERS
    args = parse_args()
    apply_mode = os.environ.get("APPLY") == "true"

    ROOT = Path(__file__).resolve().parent.parent
    REPORTS_DIR = ROOT / "reports"
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Locate plan
    if args.plan:
        plan_path = Path(args.plan)
    else:
        plan_path = REPORTS_DIR / f"dedup-breakdown-{today}.json"
    if not plan_path.exists():
        # Fall back to most recent breakdown
        candidates = sorted(REPORTS_DIR.glob("dedup-breakdown-*.json"), reverse=True)
        if not candidates:
            print(f"ERROR: no plan file found", file=sys.stderr)
            sys.exit(1)
        plan_path = candidates[0]
    print(f"Plan:    {plan_path}")
    plan = json.loads(plan_path.read_text())

    log_path = REPORTS_DIR / f"dedup-applied-{today}.log"
    archived_ids, redirect_paths = load_log(log_path)
    if archived_ids or redirect_paths:
        print(f"Resume:  {len(archived_ids):,} products already archived, {len(redirect_paths):,} redirects already created")

    # Summary
    total_groups = len(plan["merge_plan"])
    total_archive = plan["products_to_archive"]
    total_transfers = sum(len(g["merge"]["transfers"]) for g in plan["merge_plan"])
    total_transfer_qty = plan["total_transfer_qty"]
    print(f"Groups:  {total_groups:,}")
    print(f"Archive: {total_archive:,} products")
    print(f"Stock:   {total_transfers} transfers, {total_transfer_qty} units planned")
    print(f"APPLY:   {apply_mode}")

    # Auth + location
    token = get_token()
    HEADERS = {"X-Shopify-Access-Token": token, "Accept": "application/json"}
    loc_id, loc_name = fetch_online_location_id(plan)
    print(f"Location: {loc_id} ({loc_name})")
    print()

    if not apply_mode:
        print("DRY RUN — set APPLY=true to execute. No writes made.")
        return

    # Open log for append, line-buffered
    log_f = open(log_path, "a", buffering=1)

    def log(**kwargs):
        kwargs["ts"] = datetime.now(timezone.utc).isoformat()
        log_f.write(json.dumps(kwargs, default=str) + "\n")

    log(phase=0, action="run_start", plan=str(plan_path), location_id=loc_id,
        total_groups=total_groups, total_archive=total_archive,
        limit=args.limit, skip_redirects=args.skip_redirects)

    # ====================================================================
    # Phase 1: stock transfers
    # ====================================================================
    print("=== Phase 1: stock transfers ===")
    transfers_done = 0
    transfers_skipped = 0
    transfers_failed = 0
    for g in plan["merge_plan"]:
        merge = g["merge"]
        if not merge["transfers"]:
            continue
        for t in merge["transfers"]:
            src_var_id = t["from_variant_id"]
            dst_var_id = t["to_variant_id"]
            # Fetch current state of both variants
            s1, src_data = api_request("GET", f"/variants/{src_var_id}.json")
            s2, dst_data = api_request("GET", f"/variants/{dst_var_id}.json")
            if s1 != 200 or s2 != 200:
                transfers_failed += 1
                log(phase=1, action="transfer_fetch_failed", transfer=t,
                    src_status=s1, dst_status=s2)
                continue
            src_v = src_data["variant"]
            dst_v = dst_data["variant"]
            src_item = src_v["inventory_item_id"]
            dst_item = dst_v["inventory_item_id"]
            src_qty = src_v.get("inventory_quantity") or 0
            dst_qty = dst_v.get("inventory_quantity") or 0
            if src_qty <= 0:
                transfers_skipped += 1
                log(phase=1, action="transfer_skipped_src_empty",
                    transfer=t, src_qty=src_qty)
                continue
            new_dst = dst_qty + src_qty
            # Step A: set canonical to new_dst
            sA, rA = api_request("POST", "/inventory_levels/set.json", {
                "location_id": loc_id,
                "inventory_item_id": dst_item,
                "available": new_dst,
            })
            if sA not in (200, 201):
                transfers_failed += 1
                log(phase=1, action="transfer_set_canonical_failed",
                    transfer=t, status=sA, response=rA)
                continue
            # Step B: zero source
            sB, rB = api_request("POST", "/inventory_levels/set.json", {
                "location_id": loc_id,
                "inventory_item_id": src_item,
                "available": 0,
            })
            if sB not in (200, 201):
                # Canonical already has the stock; source not zeroed.
                # Log + continue. Source will get archived soon, which
                # freezes the stock regardless.
                log(phase=1, action="transfer_zero_src_failed_canonical_ok",
                    transfer=t, status=sB, response=rB,
                    canonical_new_qty=new_dst, src_still_has=src_qty)
            transfers_done += 1
            log(phase=1, action="transfer_ok",
                from_variant=src_var_id, to_variant=dst_var_id,
                src_item=src_item, dst_item=dst_item,
                qty_moved=src_qty, canonical_new_qty=new_dst)
            print(f"  transferred {src_qty} units  variant {src_var_id} -> {dst_var_id}")
    print(f"Phase 1 done: {transfers_done} ok, {transfers_skipped} skipped, {transfers_failed} failed")
    print()

    # ====================================================================
    # Phase 2: archive non-canonical products
    # ====================================================================
    print("=== Phase 2: archive non-canonical products ===")

    # Flatten to (archive_id, archive_handle, canonical_id, canonical_handle)
    archive_list = []
    for g in plan["merge_plan"]:
        canon = g["canonical"]
        for a in g["archive"]:
            archive_list.append((a["id"], a["handle"], canon["id"], canon["handle"]))

    # Optional canary
    if args.limit is not None:
        archive_list = archive_list[: args.limit]
    total = len(archive_list)
    print(f"Target: {total:,} products to archive")

    archived_ok = 0
    archived_skip = 0
    archived_fail = 0
    consecutive_fail = 0
    ABORT_AFTER_CONSECUTIVE_FAILS = 5  # fail fast on scope/auth errors
    for i, (arch_id, arch_handle, canon_id, canon_handle) in enumerate(archive_list, 1):
        if arch_id in archived_ids:
            archived_skip += 1
            continue
        status, resp = api_request("PUT", f"/products/{arch_id}.json", {
            "product": {"id": arch_id, "status": "archived"},
        })
        if status == 200:
            archived_ok += 1
            consecutive_fail = 0
            log(phase=2, action="archived", product_id=arch_id,
                handle=arch_handle, canonical_id=canon_id)
        else:
            archived_fail += 1
            consecutive_fail += 1
            log(phase=2, action="archive_failed", product_id=arch_id,
                handle=arch_handle, status=status, response=resp)
            if consecutive_fail >= ABORT_AFTER_CONSECUTIVE_FAILS:
                print(f"  ABORTING: {consecutive_fail} consecutive failures "
                      f"(likely scope/auth issue). Last error: {status} {resp}",
                      file=sys.stderr)
                log(phase=2, action="aborted_consecutive_fails",
                    at_index=i, consecutive=consecutive_fail,
                    last_status=status, last_response=resp)
                break
        if i % 100 == 0 or i == total:
            print(f"  {i:>5}/{total} | ok={archived_ok} skip={archived_skip} fail={archived_fail}")
    print(f"Phase 2 done: {archived_ok} archived, {archived_skip} resumed-skip, {archived_fail} failed")
    print()

    # ====================================================================
    # Phase 3: 301 redirects
    # ====================================================================
    if args.skip_redirects:
        print("=== Phase 3: SKIPPED (--skip-redirects) ===")
    else:
        print("=== Phase 3: create 301 redirects ===")
        red_ok = 0
        red_skip = 0
        red_fail = 0
        for i, (arch_id, arch_handle, canon_id, canon_handle) in enumerate(archive_list, 1):
            from_path = f"/products/{arch_handle}"
            to_path = f"/products/{canon_handle}"
            if from_path == to_path:
                red_skip += 1
                continue
            if from_path in redirect_paths:
                red_skip += 1
                continue
            status, resp = api_request("POST", "/redirects.json", {
                "redirect": {"path": from_path, "target": to_path},
            })
            if status in (200, 201):
                red_ok += 1
                log(phase=3, action="redirect_created",
                    from_path=from_path, to_path=to_path)
            elif status == 422:
                # Path already redirected in Shopify (not in our log);
                # treat as success.
                red_skip += 1
                log(phase=3, action="redirect_already_exists",
                    from_path=from_path, to_path=to_path, response=resp)
            else:
                red_fail += 1
                log(phase=3, action="redirect_failed",
                    from_path=from_path, to_path=to_path,
                    status=status, response=resp)
            if i % 100 == 0 or i == total:
                print(f"  {i:>5}/{total} | ok={red_ok} skip={red_skip} fail={red_fail}")
        print(f"Phase 3 done: {red_ok} created, {red_skip} skipped, {red_fail} failed")
    print()

    log(phase=0, action="run_end",
        transfers_done=transfers_done, transfers_failed=transfers_failed,
        archived_ok=archived_ok, archived_fail=archived_fail)
    log_f.close()
    print("=== ALL DONE ===")


if __name__ == "__main__":
    main()
