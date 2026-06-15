#!/usr/bin/env python3
"""Omni ERP report-server probe.

Fetches the owner-supplied report URL, then explores the server to discover
what other reports/endpoints exist and which export formats work. Writes all
findings (credential-redacted) to data/omni/probe/ for the Growth Engine to
design the ingestion pipeline and stores dashboard around.

Env: OMNI_REPORT_URL — full report URL including UserName/Password/CompanyName
query params. Never commit that URL; this script redacts it from all output.
"""
import hashlib
import os
import re
import sys
import urllib.parse
import urllib.request

OUT_DIR = "data/omni/probe"
MAX_SAVE = 400_000  # bytes of body to keep per response


def redact(text: str) -> str:
    text = re.sub(r"(UserName=)[^&\s\"']+", r"\1REDACTED", text, flags=re.I)
    text = re.sub(r"(Password=)[^&\s\"']+", r"\1REDACTED", text, flags=re.I)
    return text


def fetch(url: str, timeout: int = 90):
    req = urllib.request.Request(url, headers={"User-Agent": "OneLifeGrowthEngine/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read(MAX_SAVE + 1)
            return r.status, dict(r.headers), body
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read(MAX_SAVE + 1) if e.fp else b""
    except Exception as e:  # connection errors, timeouts
        return None, {}, str(e).encode()


def slug(s: str) -> str:
    s = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-")[:80]
    return s or hashlib.md5(s.encode()).hexdigest()[:10]


def main():
    base_url = os.environ.get("OMNI_REPORT_URL", "").strip()
    if not base_url:
        print("FATAL: OMNI_REPORT_URL env var not set (dispatch input or repo secret).")
        sys.exit(1)

    os.makedirs(OUT_DIR, exist_ok=True)
    p = urllib.parse.urlparse(base_url)
    origin = f"{p.scheme}://{p.netloc}"
    creds_qs = p.query  # UserName/Password/CompanyName

    targets = [("main-report", base_url)]
    # Export-format variants on the main report
    for fmt in ("Format=CSV", "Format=JSON", "Format=XML", "Export=CSV", "OutputFormat=CSV"):
        targets.append((f"main-report-{slug(fmt)}", f"{base_url}&{fmt}"))
    # Discovery paths — report index candidates
    for path in ("/", "/Report", "/Report/", "/Reports", "/ReportList", "/Report/List", "/api", "/api/reports", "/help"):
        targets.append((f"discover{slug(path) or '-root'}", f"{origin}{path}?{creds_qs}"))

    summary = ["# Omni probe results", "", f"Origin: `{origin}` (probed from GitHub Actions runner)", "",
               "| name | status | content-type | bytes | saved file |", "|---|---|---|---|---|"]
    link_pool = set()

    for name, url in targets:
        status, headers, body = fetch(url)
        ctype = headers.get("Content-Type", "?") if headers else "?"
        ext = ".json" if "json" in str(ctype) else ".csv" if "csv" in str(ctype) else ".xml" if "xml" in str(ctype) else ".html"
        fname = f"{OUT_DIR}/{name}{ext}"
        text = redact(body.decode("utf-8", errors="replace"))
        saved = "-"
        if status and body and status < 500:
            with open(fname, "w", encoding="utf-8") as f:
                f.write(text[:MAX_SAVE])
            saved = fname
            # harvest hrefs/report names for the summary
            for m in re.findall(r'href=["\']([^"\']+)["\']|Report/([^"\'<>\s?]+)', text):
                link_pool.add(redact((m[0] or m[1])[:200]))
        line = f"| {name} | {status} | {ctype} | {len(body)} | {saved} |"
        summary.append(line)
        print(line)

    if link_pool:
        summary += ["", "## Links / report names harvested", ""]
        summary += [f"- `{l}`" for l in sorted(link_pool)[:200]]

    with open(f"{OUT_DIR}/SUMMARY.md", "w", encoding="utf-8") as f:
        f.write("\n".join(summary) + "\n")
    print(f"\nWrote {OUT_DIR}/SUMMARY.md")


if __name__ == "__main__":
    main()
