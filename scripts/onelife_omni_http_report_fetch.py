#!/usr/bin/env python3
"""Fetch a One Life Omni JSON report over the Omni web server.

Credentials are read from environment variables or a full secret URL. The
sanitized audit output deliberately excludes usernames, passwords, query
strings, and host URLs.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any


WORKSPACE = Path(__file__).resolve().parents[1]
DEFAULT_REPORT = "ANA_Stock Listing_CEN"
DEFAULT_OUT_DIR = WORKSPACE / "tmp" / "omni-http-fetch"
DEFAULT_AUDIT_DIR = WORKSPACE / "audit-output" / "omni-http-fetch"


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "omni-report"


def build_url(args: argparse.Namespace) -> str:
    full_url = args.url or os.environ.get("ONELIFE_OMNI_HTTP_REPORT_URL", "")
    if full_url:
        return full_url

    host = (args.host or os.environ.get("ONELIFE_OMNI_HTTP_HOST", "")).rstrip("/")
    user = args.user or os.environ.get("ONELIFE_OMNI_HTTP_USER", "")
    password = args.password or os.environ.get("ONELIFE_OMNI_HTTP_PASSWORD", "")
    company = args.company or os.environ.get("ONELIFE_OMNI_COMPANY", "")
    missing = [
        name
        for name, value in {
            "ONELIFE_OMNI_HTTP_HOST": host,
            "ONELIFE_OMNI_HTTP_USER": user,
            "ONELIFE_OMNI_HTTP_PASSWORD": password,
            "ONELIFE_OMNI_COMPANY": company,
        }.items()
        if not value
    ]
    if missing:
        raise ValueError(f"Missing Omni HTTP settings: {', '.join(missing)}")

    report_path = urllib.parse.quote(args.report, safe="")
    query = urllib.parse.urlencode(
        {
            "UserName": user,
            "Password": password,
            "CompanyName": company,
        }
    )
    return f"{host}/Report/{report_path}?{query}"


def first_array(payload: Any) -> tuple[str | None, list[Any] | None]:
    if isinstance(payload, list):
        return None, payload
    if isinstance(payload, dict):
        for key, value in payload.items():
            if isinstance(value, list):
                return key, value
    return None, None


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, default=str) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch an Omni web-server JSON report.")
    parser.add_argument("--url", default="")
    parser.add_argument("--host", default="")
    parser.add_argument("--user", default="")
    parser.add_argument("--password", default="")
    parser.add_argument("--company", default="")
    parser.add_argument("--report", default=os.environ.get("ONELIFE_OMNI_REPORT_NAME", DEFAULT_REPORT))
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--audit-dir", type=Path, default=DEFAULT_AUDIT_DIR)
    args = parser.parse_args()

    try:
        url = build_url(args)
        request = urllib.request.Request(url, headers={"User-Agent": "onelife-omni-http-fetch/1.0"})
        with urllib.request.urlopen(request, timeout=90) as response:
            body = response.read()
            headers = dict(response.headers.items())

        payload = json.loads(body.decode("utf-8-sig"))
        top_key, rows = first_array(payload)
        out_path = args.out or args.out_dir / f"{slugify(args.report)}.json"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_bytes(body)

        response_date = headers.get("Date", "")
        if response_date:
            try:
                timestamp = parsedate_to_datetime(response_date).timestamp()
                os.utime(out_path, (timestamp, timestamp))
            except (TypeError, ValueError, OSError):
                pass

        report = {
            "ok": True,
            "report": args.report,
            "localPath": str(out_path),
            "bytes": len(body),
            "contentType": headers.get("Content-Type", ""),
            "date": response_date,
            "topKey": top_key,
            "rows": len(rows) if rows is not None else None,
            "generatedAt": datetime.now(timezone.utc).isoformat(),
        }
        write_json(args.audit_dir / "onelife-omni-http-report-fetch-latest.json", report)
        print(json.dumps(report, indent=2))
        return 0
    except urllib.error.HTTPError as error:
        message = f"HTTP {error.code}: {error.reason}"
    except Exception as error:  # noqa: BLE001 - CLI should emit sanitized operational errors.
        message = str(error)

    report = {
        "ok": False,
        "report": args.report,
        "reason": "fetch_failed",
        "message": message,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
    }
    write_json(args.audit_dir / "onelife-omni-http-report-fetch-latest.json", report)
    print(json.dumps(report, indent=2))
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
