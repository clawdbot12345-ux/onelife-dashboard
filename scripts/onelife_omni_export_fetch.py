#!/usr/bin/env python3
"""Fetch the latest One Life Omni Automation export over SMB.

Secrets are read from environment variables or an auth file and are never
printed. The script preserves the remote export date from the filename/listing
so downstream stale-export checks do not mistake an old downloaded file for a
fresh export.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import tempfile
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path


WORKSPACE = Path(__file__).resolve().parents[1]
DEFAULT_OUT_DIR = WORKSPACE / "tmp" / "omni-smb-pull" / "Automation"
DEFAULT_AUDIT_DIR = WORKSPACE / "audit-output" / "omni-export-fetch"


@dataclass
class RemoteFile:
    name: str
    size: int | None = None
    mtime: datetime | None = None

    @property
    def filename_date(self) -> datetime | None:
        match = re.fullmatch(r"PO_(\d{2})-(\d{2})-(\d{2})\.csv", self.name, re.IGNORECASE)
        if not match:
            return None
        day, month, year = (int(part) for part in match.groups())
        return datetime(2000 + year, month, day, 4, 1, tzinfo=timezone.utc)

    @property
    def sort_date(self) -> datetime:
        return self.mtime or self.filename_date or datetime.min.replace(tzinfo=timezone.utc)


def run(command: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, text=True, capture_output=True, check=False)


def make_auth_file(args: argparse.Namespace) -> tempfile.NamedTemporaryFile[str] | None:
    if args.auth_file:
        return None
    password = os.environ.get("ONELIFE_OMNI_SMB_PASSWORD", "")
    if not password:
        return None
    auth = tempfile.NamedTemporaryFile("w", delete=False)
    auth.write(f"username = {args.user}\n")
    auth.write(f"password = {password}\n")
    if args.domain:
        auth.write(f"domain = {args.domain}\n")
    auth.flush()
    os.chmod(auth.name, 0o600)
    return auth


def smb_base(args: argparse.Namespace, auth_path: str) -> list[str]:
    return [
        "smbclient",
        f"//{args.host}/{args.share}",
        "-A",
        auth_path,
        "-m",
        args.smb_protocol,
    ]


def parse_listing(text: str) -> list[RemoteFile]:
    files: dict[str, RemoteFile] = {}
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        match = re.search(r"\b(PO_(?!EDITS)\d{2}-\d{2}-\d{2}\.csv)\b", line, re.IGNORECASE)
        if not match:
            continue
        name = match.group(1)
        size_match = re.search(r"\b(\d{2,})\b", line[match.end() :])
        size = int(size_match.group(1)) if size_match else None
        mtime = None
        for date_match in re.finditer(r"(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s+\w+\s+\d+\s+\d{1,2}:\d{2}:\d{2}\s+\d{4}", line):
            try:
                mtime = parsedate_to_datetime(date_match.group(0))
            except (TypeError, ValueError):
                mtime = None
        files[name] = RemoteFile(name=name, size=size, mtime=mtime)
    return sorted(files.values(), key=lambda item: item.sort_date, reverse=True)


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, default=str) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Fetch latest Omni PO export from SMB Automation share.")
    parser.add_argument("--host", default=os.environ.get("ONELIFE_OMNI_SMB_HOST", ""))
    parser.add_argument("--share", default=os.environ.get("ONELIFE_OMNI_SMB_SHARE", ""))
    parser.add_argument("--domain", default=os.environ.get("ONELIFE_OMNI_SMB_DOMAIN", ""))
    parser.add_argument("--user", default=os.environ.get("ONELIFE_OMNI_SMB_USER", ""))
    parser.add_argument("--auth-file", default=os.environ.get("ONELIFE_OMNI_SMB_AUTHFILE", ""))
    parser.add_argument("--smb-protocol", default=os.environ.get("ONELIFE_OMNI_SMB_PROTOCOL", "SMB3"))
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--audit-dir", type=Path, default=DEFAULT_AUDIT_DIR)
    parser.add_argument("--remote-name", default=os.environ.get("ONELIFE_OMNI_REMOTE_EXPORT", ""))
    parser.add_argument("--list-only", action="store_true")
    args = parser.parse_args()

    missing_settings = [
        name
        for name, value in {
            "ONELIFE_OMNI_SMB_HOST": args.host,
            "ONELIFE_OMNI_SMB_SHARE": args.share,
            "ONELIFE_OMNI_SMB_USER": args.user,
        }.items()
        if not value
    ]
    if missing_settings:
        report = {
            "ok": False,
            "reason": "missing_smb_settings",
            "required": missing_settings,
            "generatedAt": datetime.now(timezone.utc).isoformat(),
        }
        write_json(args.audit_dir / "onelife-omni-export-fetch-latest.json", report)
        print(json.dumps(report, indent=2))
        return 2

    auth_temp = make_auth_file(args)
    auth_path = args.auth_file or (auth_temp.name if auth_temp else "")
    if not auth_path:
        report = {
            "ok": False,
            "reason": "missing_smb_credentials",
            "required": ["ONELIFE_OMNI_SMB_PASSWORD or ONELIFE_OMNI_SMB_AUTHFILE"],
            "generatedAt": datetime.now(timezone.utc).isoformat(),
        }
        write_json(args.audit_dir / "onelife-omni-export-fetch-latest.json", report)
        print(json.dumps(report, indent=2))
        return 2

    try:
        list_result = run(smb_base(args, auth_path) + ["-c", "ls PO_*.csv"])
        if list_result.returncode != 0:
            raise RuntimeError((list_result.stderr or list_result.stdout).strip())
        remote_files = parse_listing(list_result.stdout)
        if not remote_files:
            raise RuntimeError("No PO_DD-MM-YY.csv files found in Automation share")
        selected = next((item for item in remote_files if item.name == args.remote_name), remote_files[0])
        report = {
            "ok": True,
            "mode": "list-only" if args.list_only else "fetch",
            "selected": {
                "name": selected.name,
                "size": selected.size,
                "mtime": selected.sort_date.isoformat(),
            },
            "available": [
                {"name": item.name, "size": item.size, "mtime": item.sort_date.isoformat()}
                for item in remote_files[:20]
            ],
            "generatedAt": datetime.now(timezone.utc).isoformat(),
        }
        if args.list_only:
            write_json(args.audit_dir / "onelife-omni-export-fetch-latest.json", report)
            print(json.dumps(report, indent=2))
            return 0

        args.out_dir.mkdir(parents=True, exist_ok=True)
        local_path = args.out_dir / selected.name
        latest_path = args.out_dir / "PO_latest.csv"
        fetch_result = run(smb_base(args, auth_path) + ["-c", f'lcd "{args.out_dir}"; get "{selected.name}" "{selected.name}"'])
        if fetch_result.returncode != 0:
            raise RuntimeError((fetch_result.stderr or fetch_result.stdout).strip())
        if local_path.exists():
            timestamp = selected.sort_date.timestamp()
            os.utime(local_path, (timestamp, timestamp))
            latest_path.write_bytes(local_path.read_bytes())
            os.utime(latest_path, (timestamp, timestamp))
        report["localPath"] = str(local_path)
        report["latestPath"] = str(latest_path)
        write_json(args.audit_dir / "onelife-omni-export-fetch-latest.json", report)
        print(json.dumps(report, indent=2))
        return 0
    except Exception as error:  # noqa: BLE001 - CLI should report sanitized operational failure.
        report = {
            "ok": False,
            "reason": "fetch_failed",
            "message": str(error),
            "generatedAt": datetime.now(timezone.utc).isoformat(),
        }
        write_json(args.audit_dir / "onelife-omni-export-fetch-latest.json", report)
        print(json.dumps(report, indent=2))
        return 1
    finally:
        if auth_temp:
            Path(auth_temp.name).unlink(missing_ok=True)


if __name__ == "__main__":
    raise SystemExit(main())
