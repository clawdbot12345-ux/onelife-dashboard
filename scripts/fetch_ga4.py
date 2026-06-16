#!/usr/bin/env python3
"""Daily GA4 feed for the One Life dashboard.

Writes dated JSON files under data/ga4/daily/ with the same shape as the Omni
feed: {"slug": [row, ...]}. Authentication uses a GA4 service-account JSON from
GA4_SA_JSON, GA4_SA_JSON_FILE, GOOGLE_APPLICATION_CREDENTIALS, or --credentials.
"""

from __future__ import annotations

import argparse
import base64
import datetime as dt
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
import time
from typing import Any
from urllib import error, parse, request
from zoneinfo import ZoneInfo


DEFAULT_PROPERTY_ID = "525312444"
DEFAULT_TIMEZONE = "Africa/Johannesburg"
DEFAULT_CURRENCY = "ZAR"
DATA_BASE = "https://analyticsdata.googleapis.com/v1beta"
ADMIN_BASE = "https://analyticsadmin.googleapis.com/v1beta"
TOKEN_SCOPE = "https://www.googleapis.com/auth/analytics.readonly"
OUT_DIR = Path("data/ga4/daily")
CHANNELS_DOC = Path("data/ga4/CHANNELS.md")
ANALYSIS_DOC = Path("data/ga4/ANALYSIS.md")


class ApiError(RuntimeError):
    def __init__(self, message: str, status: int | None = None, body: Any = None):
        super().__init__(message)
        self.status = status
        self.body = body


def b64url(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def json_compact(value: Any) -> str:
    return json.dumps(value, separators=(",", ":"), sort_keys=True)


def sign_rs256(private_key_pem: str, signing_input: bytes) -> bytes:
    openssl = "/usr/bin/openssl"
    if not Path(openssl).exists():
        openssl = "openssl"

    key_path = None
    try:
        with tempfile.NamedTemporaryFile("w", delete=False) as key_file:
            key_file.write(private_key_pem)
            key_path = key_file.name
        os.chmod(key_path, 0o600)
        proc = subprocess.run(
            [openssl, "dgst", "-sha256", "-sign", key_path],
            input=signing_input,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if proc.returncode != 0:
            raise ApiError(f"OpenSSL signing failed: {proc.stderr.decode('utf-8', 'replace')}")
        return proc.stdout
    finally:
        if key_path:
            try:
                os.remove(key_path)
            except FileNotFoundError:
                pass


def load_service_account(args: argparse.Namespace) -> dict[str, Any]:
    path_value = args.credentials or os.environ.get("GA4_SA_JSON_FILE") or os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if path_value:
        return json.loads(Path(path_value).read_text("utf-8"))

    raw = os.environ.get("GA4_SA_JSON", "").strip()
    if not raw:
        raise ApiError("Missing GA4 service account. Set GA4_SA_JSON, GA4_SA_JSON_FILE, or GOOGLE_APPLICATION_CREDENTIALS.")

    if raw.startswith("{"):
        return json.loads(raw)

    try:
        decoded = base64.b64decode(raw).decode("utf-8")
        return json.loads(decoded)
    except Exception as exc:  # noqa: BLE001 - keep credential parsing error concise
        raise ApiError("GA4_SA_JSON was not valid JSON or base64-encoded JSON.") from exc


def service_account_token(info: dict[str, Any], scope: str) -> dict[str, Any]:
    required = ["client_email", "private_key", "token_uri"]
    missing = [key for key in required if not info.get(key)]
    if missing:
        raise ApiError(f"Service-account JSON missing required keys: {', '.join(missing)}")

    now = int(time.time())
    header = {"alg": "RS256", "typ": "JWT"}
    claims = {
        "iss": info["client_email"],
        "scope": scope,
        "aud": info["token_uri"],
        "iat": now,
        "exp": now + 3600,
    }
    signing_input = (
        b64url(json_compact(header).encode("utf-8"))
        + "."
        + b64url(json_compact(claims).encode("utf-8"))
    ).encode("ascii")
    signature = sign_rs256(info["private_key"], signing_input)
    assertion = signing_input.decode("ascii") + "." + b64url(signature)
    body = parse.urlencode(
        {
            "grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
            "assertion": assertion,
        }
    ).encode("utf-8")
    req = request.Request(
        info["token_uri"],
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    try:
        with request.urlopen(req, timeout=30) as resp:
            token = json.loads(resp.read().decode("utf-8"))
    except error.HTTPError as exc:
        raise ApiError("OAuth token exchange failed", exc.code, safe_http_body(exc)) from exc
    token["client_email"] = info["client_email"]
    return token


def safe_http_body(exc: error.HTTPError) -> Any:
    raw = exc.read().decode("utf-8", "replace")
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw[:2000]


def http_json(method: str, url: str, token: str | None = None, body: Any | None = None) -> Any:
    data = None
    headers = {"Accept": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = request.Request(url, data=data, headers=headers, method=method)
    try:
        with request.urlopen(req, timeout=60) as resp:
            raw = resp.read().decode("utf-8")
    except error.HTTPError as exc:
        raise ApiError(f"{method} {url} failed", exc.code, safe_http_body(exc)) from exc
    if not raw:
        return {}
    return json.loads(raw)


def snake_case(value: str) -> str:
    value = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", value)
    value = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", value)
    return re.sub(r"[^a-zA-Z0-9]+", "_", value).strip("_").lower()


def ga_date(value: str) -> str:
    if re.fullmatch(r"\d{8}", value or ""):
        return f"{value[:4]}-{value[4:6]}-{value[6:8]}"
    return value


def metric_value(name: str, value: str) -> int | float:
    number = float(value or 0)
    if name in {
        "sessions",
        "total_users",
        "new_users",
        "engaged_sessions",
        "conversions",
        "items_viewed",
        "add_to_carts",
        "checkouts",
        "ecommerce_purchases",
        "items_purchased",
    }:
        return int(round(number))
    return round(number, 6)


class MetricSpec:
    def __init__(self, output_name: str, *api_names: str):
        self.output_name = output_name
        self.api_names = list(api_names or [output_name])


class ReportSpec:
    def __init__(
        self,
        slug: str,
        dimensions: list[str],
        metrics: list[MetricSpec],
        start_date: str,
        end_date: str,
        limit: int = 10000,
        max_rows: int | None = None,
        order_bys: list[dict[str, Any]] | None = None,
    ):
        self.slug = slug
        self.dimensions = dimensions
        self.metrics = metrics
        self.start_date = start_date
        self.end_date = end_date
        self.limit = limit
        self.max_rows = max_rows
        self.order_bys = order_bys or []


def report_body(spec: ReportSpec, api_metrics: list[str], offset: int = 0, limit: int | None = None) -> dict[str, Any]:
    body: dict[str, Any] = {
        "dateRanges": [{"startDate": spec.start_date, "endDate": spec.end_date}],
        "dimensions": [{"name": name} for name in spec.dimensions],
        "metrics": [{"name": name} for name in api_metrics],
        "limit": str(limit or spec.limit),
        "offset": str(offset),
    }
    if spec.order_bys:
        body["orderBys"] = spec.order_bys
    return body


def run_report(token: str, property_id: str, spec: ReportSpec) -> tuple[list[dict[str, Any]], list[str]]:
    api_metrics = [metric.api_names[0] for metric in spec.metrics]
    rows: list[dict[str, Any]] = []
    offset = 0
    while True:
        if spec.max_rows is not None and len(rows) >= spec.max_rows:
            break
        remaining = spec.max_rows - len(rows) if spec.max_rows is not None else spec.limit
        page_limit = min(spec.limit, remaining)
        body = report_body(spec, api_metrics, offset, page_limit)
        try:
            report = http_json("POST", f"{DATA_BASE}/properties/{property_id}:runReport", token, body)
        except ApiError as exc:
            if exc.status == 400 and "conversions" in api_metrics and any("keyEvents" in m.api_names for m in spec.metrics):
                api_metrics = ["keyEvents" if value == "conversions" else value for value in api_metrics]
                rows = []
                offset = 0
                continue
            raise

        for row in report.get("rows", []) or []:
            output: dict[str, Any] = {}
            for index, dimension_name in enumerate(spec.dimensions):
                value = row.get("dimensionValues", [{}])[index].get("value", "")
                key = snake_case(dimension_name)
                output[key] = ga_date(value) if dimension_name == "date" else value
            for index, metric in enumerate(spec.metrics):
                raw = row.get("metricValues", [{}])[index].get("value", "0")
                output[snake_case(metric.output_name)] = metric_value(snake_case(metric.output_name), raw)
            if spec.slug == "ga4_acquisition_daily":
                apply_channel_correction(output)
            rows.append(output)
            if spec.max_rows is not None and len(rows) >= spec.max_rows:
                break

        returned = len(report.get("rows", []) or [])
        row_count = int(report.get("rowCount") or 0)
        offset += returned
        if (
            returned == 0
            or returned < page_limit
            or offset >= row_count
            or (spec.max_rows is not None and len(rows) >= spec.max_rows)
        ):
            break
    return rows, api_metrics


def normalized(value: str) -> str:
    return str(value or "").strip().lower()


def contains_any(value: str, needles: list[str]) -> bool:
    return any(needle in value for needle in needles)


def apply_channel_correction(row: dict[str, Any]) -> None:
    default_group = row.get("session_default_channel_group") or "(not set)"
    source = normalized(row.get("session_source", ""))
    medium = normalized(row.get("session_medium", ""))
    combined = f"{source} {medium}"

    internal_needles = [
        "payfast",
        "payment.payfast",
        "checkout",
        "accounts.shopify",
        "customer-account",
        "customer_accounts",
        "shop.app",
        "myshopify",
        "onelife.co.za",
        "www.onelife.co.za",
        "accounts.google.com",
    ]
    email_needles = [
        "email",
        "e-mail",
        "newsletter",
        "klaviyo",
        "gmail",
        "mail.google",
        "googlemail",
        "outlook",
        "hotmail",
        "icloud",
        "mail.yahoo",
        "yahoo mail",
        "webmail",
        "l.wl.co",
    ]

    if contains_any(combined, internal_needles):
        row["corrected_channel_group"] = "Excluded - internal/payment"
        row["include_in_acquisition"] = False
        row["channel_correction_reason"] = "internal_account_checkout_or_payment_referral"
    elif contains_any(combined, email_needles):
        row["corrected_channel_group"] = "Email"
        row["include_in_acquisition"] = True
        row["channel_correction_reason"] = "email_app_or_klaviyo_referral"
    else:
        row["corrected_channel_group"] = default_group
        row["include_in_acquisition"] = True
        row["channel_correction_reason"] = ""


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", "utf-8")


def subtract_twelve_months_plus_one(end_date: dt.date) -> dt.date:
    try:
        prior_year_same_day = end_date.replace(year=end_date.year - 1)
    except ValueError:
        prior_year_same_day = end_date.replace(year=end_date.year - 1, day=28)
    return prior_year_same_day + dt.timedelta(days=1)


def property_details(token: str, property_id: str) -> dict[str, Any]:
    try:
        return http_json("GET", f"{ADMIN_BASE}/properties/{property_id}", token)
    except ApiError as exc:
        return {"error": str(exc), "status": exc.status}


def write_channels_doc() -> None:
    CHANNELS_DOC.parent.mkdir(parents=True, exist_ok=True)
    CHANNELS_DOC.write_text(
        """# GA4 channel correction

The raw GA4 `sessionDefaultChannelGroup` is preserved in `session_default_channel_group`.
The dashboard should use `corrected_channel_group` and only count rows where
`include_in_acquisition` is `true` for acquisition reporting.

## Rules

| Rule | Match | Output |
| --- | --- | --- |
| Internal/payment exclusion | Source or medium contains PayFast, checkout, customer account, Shopify account, Shop app, myshopify, onelife.co.za, or accounts.google.com | `corrected_channel_group = "Excluded - internal/payment"`, `include_in_acquisition = false` |
| Email app correction | Source or medium contains email, e-mail, newsletter, Klaviyo, Gmail, mail.google, googlemail, Outlook, Hotmail, iCloud, Yahoo Mail, webmail, or l.wl.co | `corrected_channel_group = "Email"`, `include_in_acquisition = true` |
| Default | No correction match | Keep GA4's `session_default_channel_group`, `include_in_acquisition = true` |

These rules correct known One Life issues where PayFast/account/login returns
polluted acquisition and Gmail/email-app referrals landed outside Email.
""",
        "utf-8",
    )


def write_analysis_doc(
    *,
    property_id: str,
    property_info: dict[str, Any],
    run_date: dt.date,
    daily_start: dt.date,
    daily_end: dt.date,
    trailing_start: dt.date,
    trailing_end: dt.date,
    counts: dict[str, int],
    metric_aliases: dict[str, list[str]],
) -> None:
    timezone = property_info.get("timeZone") or DEFAULT_TIMEZONE
    currency = property_info.get("currencyCode") or DEFAULT_CURRENCY
    display_name = property_info.get("displayName") or "One Life GA4 property"
    admin_note = "confirmed from GA4 Admin API" if not property_info.get("error") else "expected from prior One Life GA4 audit; Admin property read was unavailable"
    rows = "\n".join(f"- `{slug}`: {count:,} rows" for slug, count in sorted(counts.items()))
    aliases = "\n".join(
        f"- `{slug}` metrics requested as: {', '.join(values)}" for slug, values in sorted(metric_aliases.items())
    )
    ANALYSIS_DOC.parent.mkdir(parents=True, exist_ok=True)
    ANALYSIS_DOC.write_text(
        f"""# GA4 daily feed analysis

- Property ID: `{property_id}`
- Property name: `{display_name}`
- Timezone: `{timezone}` ({admin_note})
- Currency: `{currency}` ({admin_note})
- Initial/feed run date: `{run_date.isoformat()}`
- Daily reports cover the last 90 complete local days: `{daily_start.isoformat()}` to `{daily_end.isoformat()}`
- Trailing product report covers: `{trailing_start.isoformat()}` to `{trailing_end.isoformat()}`
- `ga4_landing_pages` is capped to the top 5,000 rows by purchase revenue so daily Git commits stay practical despite query-string variants.
- Revenue basis: GA4 revenue is treated as an online attribution/funnel signal and is typically incl-VAT. Shopify and Omni remain the money-ledger sources for final margin reporting.

## Files emitted

{rows}

## Channel mapping

`ga4_acquisition_daily` preserves GA4's raw `session_default_channel_group` and adds:

- `corrected_channel_group`
- `include_in_acquisition`
- `channel_correction_reason`

See `data/ga4/CHANNELS.md` for the exact PayFast/internal/account exclusion and Gmail/email-app-to-Email rules.

## API metric names

{aliases}
""",
        "utf-8",
    )


def specs_for_dates(daily_start: dt.date, daily_end: dt.date, trailing_start: dt.date, trailing_end: dt.date) -> list[ReportSpec]:
    daily_start_s = daily_start.isoformat()
    daily_end_s = daily_end.isoformat()
    trailing_start_s = trailing_start.isoformat()
    trailing_end_s = trailing_end.isoformat()
    return [
        ReportSpec(
            "ga4_acquisition_daily",
            ["date", "sessionDefaultChannelGroup", "sessionSource", "sessionMedium"],
            [
                MetricSpec("sessions"),
                MetricSpec("totalUsers"),
                MetricSpec("newUsers"),
                MetricSpec("engagedSessions"),
                MetricSpec("conversions", "conversions", "keyEvents"),
                MetricSpec("totalRevenue"),
            ],
            daily_start_s,
            daily_end_s,
            order_bys=[{"dimension": {"dimensionName": "date"}}],
        ),
        ReportSpec(
            "ga4_ecommerce_funnel_daily",
            ["date"],
            [
                MetricSpec("sessions"),
                MetricSpec("itemsViewed"),
                MetricSpec("addToCarts"),
                MetricSpec("checkouts"),
                MetricSpec("ecommercePurchases"),
                MetricSpec("purchaseRevenue"),
                MetricSpec("sessionConversionRate"),
            ],
            daily_start_s,
            daily_end_s,
            order_bys=[{"dimension": {"dimensionName": "date"}}],
        ),
        ReportSpec(
            "ga4_top_products",
            ["itemName", "itemId"],
            [
                MetricSpec("itemsViewed"),
                MetricSpec("addToCarts", "itemsAddedToCart"),
                MetricSpec("itemsPurchased"),
                MetricSpec("itemRevenue"),
            ],
            trailing_start_s,
            trailing_end_s,
            order_bys=[{"metric": {"metricName": "itemRevenue"}, "desc": True}],
        ),
        ReportSpec(
            "ga4_landing_pages",
            ["landingPagePlusQueryString"],
            [
                MetricSpec("sessions"),
                MetricSpec("engagedSessions"),
                MetricSpec("conversions", "conversions", "keyEvents"),
                MetricSpec("purchaseRevenue"),
            ],
            daily_start_s,
            daily_end_s,
            max_rows=5000,
            order_bys=[{"metric": {"metricName": "purchaseRevenue"}, "desc": True}],
        ),
        ReportSpec(
            "ga4_geo",
            ["city", "region"],
            [
                MetricSpec("sessions"),
                MetricSpec("conversions", "conversions", "keyEvents"),
                MetricSpec("purchaseRevenue"),
            ],
            daily_start_s,
            daily_end_s,
            order_bys=[{"metric": {"metricName": "purchaseRevenue"}, "desc": True}],
        ),
        ReportSpec(
            "ga4_devices",
            ["deviceCategory"],
            [
                MetricSpec("sessions"),
                MetricSpec("sessionConversionRate"),
                MetricSpec("purchaseRevenue"),
            ],
            daily_start_s,
            daily_end_s,
            order_bys=[{"metric": {"metricName": "purchaseRevenue"}, "desc": True}],
        ),
    ]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fetch One Life GA4 daily dashboard feeds.")
    parser.add_argument("--property-id", default=os.environ.get("GA4_PROPERTY_ID", DEFAULT_PROPERTY_ID))
    parser.add_argument("--credentials", help="Path to a GA4 service-account JSON file.")
    parser.add_argument("--timezone", default=DEFAULT_TIMEZONE)
    parser.add_argument("--run-date", help="Local run date for file names, YYYY-MM-DD. Defaults to today in the store timezone.")
    parser.add_argument("--end-date", help="Last reporting date, YYYY-MM-DD. Defaults to yesterday in the store timezone.")
    parser.add_argument("--daily-days", type=int, default=90)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    tz = ZoneInfo(args.timezone)
    local_today = dt.datetime.now(tz).date()
    run_date = dt.date.fromisoformat(args.run_date) if args.run_date else local_today
    daily_end = dt.date.fromisoformat(args.end_date) if args.end_date else local_today - dt.timedelta(days=1)
    daily_start = daily_end - dt.timedelta(days=args.daily_days - 1)
    trailing_end = daily_end
    trailing_start = subtract_twelve_months_plus_one(trailing_end)

    info = load_service_account(args)
    token_info = service_account_token(info, TOKEN_SCOPE)
    token = token_info["access_token"]
    property_info = property_details(token, args.property_id)

    write_channels_doc()
    counts: dict[str, int] = {}
    metric_aliases: dict[str, list[str]] = {}
    for spec in specs_for_dates(daily_start, daily_end, trailing_start, trailing_end):
        rows, api_metrics = run_report(token, args.property_id, spec)
        path = OUT_DIR / f"{run_date.isoformat()}_{spec.slug}.json"
        write_json(path, {spec.slug: rows})
        counts[spec.slug] = len(rows)
        metric_aliases[spec.slug] = api_metrics
        print(f"Wrote {path} ({len(rows)} rows)")

    write_analysis_doc(
        property_id=args.property_id,
        property_info=property_info,
        run_date=run_date,
        daily_start=daily_start,
        daily_end=daily_end,
        trailing_start=trailing_start,
        trailing_end=trailing_end,
        counts=counts,
        metric_aliases=metric_aliases,
    )
    print(f"Wrote {ANALYSIS_DOC}")
    print(f"Wrote {CHANNELS_DOC}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
