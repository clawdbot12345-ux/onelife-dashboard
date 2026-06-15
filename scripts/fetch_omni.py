#!/usr/bin/env python3
"""Daily Omni sync — fetches the P0 report set (see data/omni/reports-v2/CATALOG.md)
and maintains the cumulative per-branch daily turnover history that feeds
SCOREBOARD T2–T4. Runs on the Mac Mini via codex_bridge.sh (or any host that
can reach the Omni server). Env: OMNI_REPORT_URL (any valid report URL — only
its origin + credentials are used).
"""
import csv
import datetime
import json
import os
import re
import sys
import urllib.parse
import urllib.request

P0_REPORTS = [
    "Daily Turnover One Life",   # HO/Centurion, dated, with GP
    "Daily Turnover EDEN",
    "Daily Turnover GVS",
    "ANA_Most Popular Products GP",
    "Stock Export - wooCommerce - Levels Only",
    "ANA_Stock Listing_CEN",
    "ANA_Stock Listing_EDN",
    "ANA_Stock Listing_GVS",
    "Supplier Profitability",
    "Stock Valuation",
    "Stock Valuation - Slow movers 6 Months",
    "OL_PO_Generator_V6",
    "Purchase Orders",
    "ANA_Purchase analysis",
    "Stock Price List with Supplier Price Comparison",
    "Stock Reorder Report - Daily Material Requirements",
    "Supplier Payment Schedule",
]
BRANCH_OF = {"Daily Turnover One Life": "HO", "Daily Turnover EDEN": "EDN", "Daily Turnover GVS": "GVS"}
STOCK_LISTING_BRANCH = {
    "ANA_Stock Listing_CEN": "HO",
    "ANA_Stock Listing_EDN": "EDN",
    "ANA_Stock Listing_GVS": "GVS",
}
BRANCH_BUSY_YESTERDAY = {
    "OL_HO_Busy Times_Yesterday": "HO",
    "OL_EDN_Busy Times_Yesterday": "EDN",
    "OL_GVS_Busy Times_Yesterday": "GVS",
}
BRANCH_BUSY_MTD = {
    "OL_HO_Busy Times_MTD": "HO",
    "OL_EDN_Busy Times_MTD": "EDN",
    "OL_GVS_Busy Times_MTD": "GVS",
}
OUT = "data/omni/daily"
HISTORY = "data/omni/daily_turnover_history.csv"
TRANSACTION_HISTORY = "data/omni/daily_branch_transactions_history.csv"


def slugify(name):
    return re.sub(r"[^A-Za-z0-9]+", "-", name).strip("-").lower()


def snake_slug(name):
    return re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_").lower()


def report_url(origin, creds, name):
    return f"{origin}/Report/{urllib.parse.quote(name)}?{creds}"


def rows_from_payload(payload):
    return next(iter(payload.values())) if isinstance(payload, dict) else []


def fetch_report(origin, creds, name, timeout=240):
    url = report_url(origin, creds, name)
    with urllib.request.urlopen(urllib.request.Request(url), timeout=timeout) as r:
        payload = json.loads(r.read())
    rows = rows_from_payload(payload)
    return payload, rows


def write_daily(today, name, payload):
    slug = slugify(name)
    with open(f"{OUT}/{today}_{slug}.json", "w") as f:
        json.dump(payload, f)
    return f"{OUT}/{today}_{slug}.json"


def read_seen_pairs(path, columns):
    if not os.path.exists(path):
        return set()
    with open(path) as f:
        return {tuple(r.get(column, "") for column in columns) for r in csv.DictReader(f)}


def read_turnover_history(path):
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return {
            (row.get("branch", ""), row.get("document_date", "")): [
                row.get("branch", ""),
                row.get("document_date", ""),
                row.get("value_excl_after_discount", ""),
                row.get("gross_profit", ""),
            ]
            for row in csv.DictReader(f)
            if row.get("branch") and row.get("document_date")
        }


def csv_value(value):
    return "" if value is None else str(value)


def write_turnover_history(path, rows_by_key):
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["branch", "document_date", "value_excl_after_discount", "gross_profit"])
        writer.writerows(sorted(rows_by_key.values(), key=lambda r: (r[1], r[0])))


def ensure_csv(path, header):
    if not os.path.exists(path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", newline="") as f:
            csv.writer(f).writerow(header)


def num(value):
    try:
        return float(value or 0)
    except (TypeError, ValueError):
        return 0.0


def blank(value):
    return value is None or value == ""


def normalized_name(value):
    return re.sub(r"[^a-z0-9]+", " ", str(value or "").lower()).strip()


def normalized_code(value):
    return str(value or "").strip().upper()


def build_transaction_rows(transaction_sources, document_date, source_map):
    rows = []
    for report_name, branch in source_map.items():
        source_rows = transaction_sources.get(report_name) or []
        transaction_count = sum(int(num(row.get("count"))) for row in source_rows)
        value_excl = round(sum(num(row.get("value_excl_after_discount")) for row in source_rows), 2)
        rows.append(
            {
                "document_date": document_date,
                "company_branch_code": branch,
                "transaction_count": transaction_count,
                "value_excl_after_discount": value_excl,
                "average_basket_ex_vat": round(value_excl / transaction_count, 2) if transaction_count else None,
                "source_report": report_name,
                "source_rows": len(source_rows),
            }
        )
    return rows


def build_mtd_transaction_rows(transaction_sources, today):
    period_start = today.replace(day=1).isoformat()
    period_end = today.isoformat()
    rows = []
    for row in build_transaction_rows(transaction_sources, period_end, BRANCH_BUSY_MTD):
        row["period_start"] = period_start
        row["period_end"] = period_end
        row["snapshot_date"] = period_end
        row["period_type"] = "month_to_date"
        row.pop("document_date", None)
        rows.append(row)
    return rows


def cost_lookup_from_sales(rows):
    grouped = {}
    for row in rows:
        stock_code = row.get("stock_code")
        quantity = num(row.get("quantity"))
        if blank(stock_code) or not quantity:
            continue
        value_excl = num(row.get("value_excl_after_discount"))
        gross_profit = num(row.get("gross_profit"))
        cost_excl = value_excl - gross_profit
        bucket = grouped.setdefault(
            stock_code,
            {
                "stock_code": stock_code,
                "stock_description": row.get("line_item_description") or row.get("stock_description"),
                "quantity_sold": 0.0,
                "value_excl_after_discount": 0.0,
                "gross_profit": 0.0,
            },
        )
        bucket["quantity_sold"] += quantity
        bucket["value_excl_after_discount"] += value_excl
        bucket["gross_profit"] += gross_profit
    lookup = {}
    for stock_code, row in grouped.items():
        quantity = row["quantity_sold"]
        value_excl = row["value_excl_after_discount"]
        gross_profit = row["gross_profit"]
        cost_excl = value_excl - gross_profit
        lookup[stock_code] = {
            "stock_code": stock_code,
            "stock_description": row["stock_description"],
            "quantity_sold": round(quantity, 4),
            "value_excl_after_discount": round(value_excl, 2),
            "gross_profit": round(gross_profit, 2),
            "cost_price": round(cost_excl / quantity, 2) if quantity else None,
            "average_cost_excl": round(cost_excl / quantity, 2) if quantity else None,
            "sales_margin_pct": round(gross_profit / value_excl * 100, 2) if value_excl else None,
            "source_report": "ANA_Most Popular Products GP",
            "cost_source": "sales_gross_profit_average",
            "cost_basis": "sales_gross_profit_average",
        }
    return lookup


def row_cost_price(row):
    for field in (
        "cost_price",
        "unit_cost_price",
        "costprice",
        "unit_cost",
        "cost_excl",
        "cost_price_excl",
        "average_cost",
        "average_cost_excl",
    ):
        value = num(row.get(field))
        if value:
            return value
    return None


def cost_lookup_from_stock_reports(stock_sources):
    grouped = {}
    for report_name, rows in stock_sources.items():
        for row in rows or []:
            stock_code = row.get("stock_code")
            cost_price = row_cost_price(row)
            if blank(stock_code) or cost_price is None:
                continue
            bucket = grouped.setdefault(
                stock_code,
                {
                    "stock_code": stock_code,
                    "stock_description": row.get("stock_description"),
                    "cost_values": [],
                    "source_reports": set(),
                },
            )
            bucket["cost_values"].append(cost_price)
            bucket["source_reports"].add(report_name)
    lookup = {}
    for stock_code, row in grouped.items():
        cost_price = round(sum(row["cost_values"]) / len(row["cost_values"]), 2)
        lookup[stock_code] = {
            "stock_code": stock_code,
            "stock_description": row.get("stock_description"),
            "cost_price": cost_price,
            "average_cost_excl": cost_price,
            "quantity_sold": None,
            "value_excl_after_discount": None,
            "gross_profit": None,
            "sales_margin_pct": None,
            "source_report": sorted(row["source_reports"]),
            "cost_source": "omni_report",
            "cost_basis": "latest",
            "cost_observation_count": len(row["cost_values"]),
        }
    return lookup


def merge_cost_lookups(sales_cost_lookup, stock_cost_lookup):
    merged = dict(sales_cost_lookup)
    merged.update(stock_cost_lookup)
    return merged


def build_stock_cost_rows(cost_lookup):
    return sorted(cost_lookup.values(), key=lambda row: row["stock_code"])


def build_stock_listing_with_cost(stock_sources, cost_lookup):
    rows = []
    for report_name, branch in STOCK_LISTING_BRANCH.items():
        for row in stock_sources.get(report_name) or []:
            stock_code = row.get("stock_code")
            cost = cost_lookup.get(stock_code) if stock_code else None
            real_row_cost = row_cost_price(row)
            available = num(row.get("available"))
            selling_price = num(row.get("selling_price_excl"))
            if real_row_cost is not None:
                cost_price = real_row_cost
                cost_source = "omni_report"
                cost_basis = "latest"
                cost_quantity_sold = None
            elif cost:
                cost_price = cost.get("cost_price") or cost.get("average_cost_excl")
                cost_source = cost.get("cost_source") or cost.get("cost_basis")
                cost_basis = cost.get("cost_basis")
                cost_quantity_sold = cost.get("quantity_sold")
            else:
                cost_price = None
                cost_source = "unavailable_from_current_omni_reports"
                cost_basis = None
                cost_quantity_sold = None
            margin_pct = None
            if cost_price is not None and selling_price:
                margin_pct = round((selling_price - cost_price) / selling_price * 100, 2)
            rows.append(
                {
                    "company_branch_code": branch,
                    "source_report": report_name,
                    "stock_code": stock_code,
                    "stock_description": row.get("stock_description"),
                    "supplier_#": row.get("supplier_#"),
                    "product_group": row.get("product_group"),
                    "stock_category": row.get("stock_category"),
                    "available": row.get("available"),
                    "selling_price_excl": row.get("selling_price_excl"),
                    "cost_price": cost_price,
                    "average_cost_excl": cost_price,
                    "stock_value_cost": round(available * cost_price, 2) if cost_price is not None else None,
                    "gross_margin_pct_at_selling": margin_pct,
                    "cost_source": cost_source,
                    "cost_basis": cost_basis,
                    "cost_quantity_sold": cost_quantity_sold,
                }
            )
    return rows


def add_supplier(master, supplier_code, supplier_name, source_report):
    supplier_code = normalized_code(supplier_code)
    if blank(supplier_code) and blank(supplier_name):
        return
    name_key = f"name::{normalized_name(supplier_name)}" if not blank(supplier_name) else None
    if not blank(supplier_code):
        key = supplier_code
        if key not in master and name_key in master:
            master[key] = master.pop(name_key)
    else:
        key = name_key
        for existing_key, existing in master.items():
            if normalized_name(existing.get("supplier_name")) == normalized_name(supplier_name):
                key = existing_key
                break
    row = master.setdefault(
        key,
        {"supplier_#": supplier_code or None, "supplier_name": supplier_name or None, "source_reports": set()},
    )
    if blank(row.get("supplier_#")) and not blank(supplier_code):
        row["supplier_#"] = supplier_code
    if blank(row.get("supplier_name")) and not blank(supplier_name):
        row["supplier_name"] = supplier_name
    row["source_reports"].add(source_report)


def build_supplier_master(report_rows):
    master = {}
    stock_supplier_codes = set()
    for report_name in STOCK_LISTING_BRANCH:
        for row in report_rows.get(report_name) or []:
            supplier_code = normalized_code(row.get("supplier_#"))
            if supplier_code:
                stock_supplier_codes.add(supplier_code)
            add_supplier(master, supplier_code, None, report_name)
    for report_name in ("Stock Price List with Supplier Price Comparison", "Stock Reorder Report - Daily Material Requirements"):
        for row in report_rows.get(report_name) or []:
            add_supplier(master, row.get("last_supplier"), row.get("last_supplier_s_name"), report_name)
    for row in report_rows.get("Stock Valuation - Slow movers 6 Months") or []:
        add_supplier(master, row.get("supplier_#"), None, "Stock Valuation - Slow movers 6 Months")
    for row in report_rows.get("Purchase Orders") or []:
        add_supplier(master, row.get("supplier_account_no"), None, "Purchase Orders")
    purchase_supplier_numbers = {}
    for row in report_rows.get("ANA_Purchase analysis") or []:
        account_no = normalized_code(row.get("supplier_account_no"))
        if not account_no:
            continue
        add_supplier(master, account_no, row.get("supplier_name"), "ANA_Purchase analysis")
        if not blank(row.get("supplier_#")):
            purchase_supplier_numbers[account_no] = row.get("supplier_#")
    for row in report_rows.get("Supplier Payment Schedule") or []:
        add_supplier(master, None, row.get("supplier_name"), "Supplier Payment Schedule")
    rows = []
    for row in master.values():
        supplier_code = normalized_code(row.get("supplier_#"))
        linked_to_stock = bool(supplier_code and supplier_code in stock_supplier_codes)
        rows.append(
            {
                "supplier_account_no": supplier_code or None,
                "supplier_#": supplier_code if linked_to_stock else None,
                "purchase_supplier_#": purchase_supplier_numbers.get(supplier_code),
                "supplier_name": row.get("supplier_name"),
                "linked_to_stock": linked_to_stock,
                "source_reports": sorted(row["source_reports"]),
            }
        )
    return sorted(rows, key=lambda row: (row.get("supplier_account_no") or "", row.get("supplier_name") or ""))


def supplier_master_indexes(supplier_master):
    by_account = {
        normalized_code(row.get("supplier_account_no")): row
        for row in supplier_master
        if row.get("supplier_account_no")
    }
    by_name = {
        normalized_name(row.get("supplier_name")): row
        for row in supplier_master
        if row.get("supplier_name")
    }
    return by_account, by_name


def build_supplier_po_grv(po_rows, purchase_rows, payment_rows, supplier_master):
    by_account, by_name = supplier_master_indexes(supplier_master)
    rows_by_supplier = {}

    def bucket_for(account_no, supplier_name=None):
        account_no = normalized_code(account_no)
        master_row = by_account.get(account_no) if account_no else None
        key = account_no or f"name::{normalized_name(supplier_name)}"
        bucket = rows_by_supplier.setdefault(
            key,
            {
                "supplier_account_no": account_no or None,
                "supplier_#": master_row.get("supplier_#") if master_row else None,
                "purchase_supplier_#": master_row.get("purchase_supplier_#") if master_row else None,
                "supplier_name": supplier_name or (master_row.get("supplier_name") if master_row else None),
                "linked_to_stock": bool(master_row.get("linked_to_stock")) if master_row else False,
                "po_value_excl": 0.0,
                "received_invoiced_value_excl": 0.0,
                "grv_value_excl": None,
                "fill_rate_proxy": None,
                "fill_rate_proxy_basis": "ana_purchase_analysis_received_invoiced_div_purchase_orders_ordered",
                "outstanding_excl": None,
                "outstanding_incl": None,
                "order_count": set(),
                "ordered_qty": 0.0,
                "source_reports": set(),
                "coverage_note": "Fill rate is a proxy: ANA_Purchase analysis invoices + credit notes divided by Purchase Orders ordered value; it is not true GRV.",
            },
        )
        if supplier_name and not bucket.get("supplier_name"):
            bucket["supplier_name"] = supplier_name
        return bucket

    for row in po_rows:
        bucket = bucket_for(row.get("supplier_account_no"))
        bucket["po_value_excl"] += num(row.get("value_excl_after_discount"))
        bucket["ordered_qty"] += num(row.get("ordered_qty"))
        bucket["source_reports"].add("Purchase Orders")
        if row.get("reference"):
            bucket["order_count"].add(row.get("reference"))

    for row in purchase_rows:
        bucket = bucket_for(row.get("supplier_account_no"), row.get("supplier_name"))
        bucket["received_invoiced_value_excl"] += num(row.get("value_excl_after_discount"))
        bucket["source_reports"].add("ANA_Purchase analysis")

    for row in payment_rows:
        supplier_name = row.get("supplier_name")
        master_row = by_name.get(normalized_name(supplier_name))
        bucket = bucket_for(master_row.get("supplier_account_no") if master_row else None, supplier_name)
        outstanding_incl = num(row.get("outstanding_incl"))
        bucket["outstanding_excl"] = round(outstanding_incl / 1.15, 2) if outstanding_incl else 0
        bucket["outstanding_incl"] = row.get("outstanding_incl")
        bucket["source_reports"].add("Supplier Payment Schedule")

    rows = []
    for bucket in rows_by_supplier.values():
        po_value_excl = round(bucket["po_value_excl"], 2)
        received_value_excl = round(bucket["received_invoiced_value_excl"], 2)
        fill_rate_proxy = round(received_value_excl / po_value_excl, 4) if po_value_excl else None
        rows.append(
            {
                "supplier_account_no": bucket["supplier_account_no"],
                "supplier_#": bucket["supplier_#"],
                "purchase_supplier_#": bucket["purchase_supplier_#"],
                "supplier_name": bucket["supplier_name"],
                "linked_to_stock": bucket["linked_to_stock"],
                "po_value_excl": po_value_excl,
                "received_invoiced_value_excl": received_value_excl,
                "grv_value_excl": bucket["grv_value_excl"],
                "fill_pct": None,
                "fill_rate_proxy": fill_rate_proxy,
                "fill_rate_proxy_basis": bucket["fill_rate_proxy_basis"],
                "outstanding_excl": bucket["outstanding_excl"],
                "outstanding_incl": bucket["outstanding_incl"],
                "order_count": len(bucket["order_count"]),
                "ordered_qty": round(bucket["ordered_qty"], 4),
                "source_reports": sorted(bucket["source_reports"]),
                "coverage_note": bucket["coverage_note"],
            }
        )
    return sorted(rows, key=lambda row: (row.get("supplier_account_no") or "", row.get("supplier_name") or ""))


def build_supplier_purchase_coverage(purchase_rows, supplier_master):
    by_account, _ = supplier_master_indexes(supplier_master)
    grouped = {}
    for row in purchase_rows:
        account_no = normalized_code(row.get("supplier_account_no"))
        if not account_no:
            continue
        bucket = grouped.setdefault(
            account_no,
            {
                "supplier_account_no": account_no,
                "supplier_name": row.get("supplier_name"),
                "purchase_value_excl": 0.0,
                "linked_to_stock": bool((by_account.get(account_no) or {}).get("linked_to_stock")),
            },
        )
        bucket["purchase_value_excl"] += num(row.get("value_excl_after_discount"))
    unlinked = [row for row in grouped.values() if not row["linked_to_stock"]]
    linked = [row for row in grouped.values() if row["linked_to_stock"]]
    return [
        {
            "source_report": "ANA_Purchase analysis",
            "join_key": "normalized supplier_account_no == normalized stock supplier_#",
            "supplier_count": len(grouped),
            "linked_supplier_count": len(linked),
            "linked_purchase_value_excl": round(sum(row["purchase_value_excl"] for row in linked), 2),
            "unlinked_supplier_count": len(unlinked),
            "unlinked_purchase_value_excl": round(sum(row["purchase_value_excl"] for row in unlinked), 2),
            "unlinked_suppliers": sorted(
                [
                    {
                        "supplier_account_no": row["supplier_account_no"],
                        "supplier_name": row.get("supplier_name"),
                        "purchase_value_excl": round(row["purchase_value_excl"], 2),
                    }
                    for row in unlinked
                ],
                key=lambda row: abs(row["purchase_value_excl"]),
                reverse=True,
            ),
        }
    ]


def turnover_quality_audit(turnover_rows):
    all_dates = sorted(
        {
            row.get("document_date")
            for rows in turnover_rows.values()
            for row in rows
            if row.get("document_date")
        }
    )
    branch_rows = {}
    for report_name, branch in BRANCH_OF.items():
        rows = turnover_rows.get(report_name) or []
        dates = sorted(row.get("document_date") for row in rows if row.get("document_date"))
        low_value_rows = [
            {
                "document_date": row.get("document_date"),
                "value_excl_after_discount": row.get("value_excl_after_discount"),
                "gross_profit": row.get("gross_profit"),
            }
            for row in rows
            if num(row.get("value_excl_after_discount")) and num(row.get("value_excl_after_discount")) < 1000
        ]
        branch_rows[branch] = {
            "source_report": report_name,
            "row_count": len(rows),
            "first_date": dates[0] if dates else None,
            "latest_date": dates[-1] if dates else None,
            "missing_vs_union": [date for date in all_dates if date not in set(dates)],
            "low_value_rows_under_1000": low_value_rows,
        }
    return {
        "turnover_quality_audit": [
            {
                "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "union_dates": all_dates,
                "branch_rows": branch_rows,
                "scope_note": "Daily Turnover One Life is treated as HO/Centurion because the cataloged ANA branch source maps HO to Centurion/HO; the turnover feed does not expose warehouse/channel split.",
            }
        ]
    }


def main():
    base = os.environ.get("OMNI_REPORT_URL", "").strip()
    if not base:
        sys.exit("FATAL: OMNI_REPORT_URL not set")
    p = urllib.parse.urlparse(base)
    origin, creds = f"{p.scheme}://{p.netloc}", p.query
    today_date = datetime.date.today()
    today = today_date.isoformat()
    yesterday = (today_date - datetime.timedelta(days=1)).isoformat()
    os.makedirs(OUT, exist_ok=True)

    # load existing history keys to make appends idempotent
    ensure_csv(HISTORY, ["branch", "document_date", "value_excl_after_discount", "gross_profit"])
    turnover_history = read_turnover_history(HISTORY)
    ensure_csv(TRANSACTION_HISTORY, ["branch", "document_date", "transaction_count", "value_excl_after_discount", "average_basket_ex_vat"])
    seen_transactions = read_seen_pairs(TRANSACTION_HISTORY, ["branch", "document_date"])

    turnover_updates = 0
    new_transaction_rows = []
    report_rows = {}
    turnover_rows = {}
    for name in P0_REPORTS:
        try:
            payload, rows = fetch_report(origin, creds, name)
        except Exception as e:
            print(f"[fetch_omni] {name}: FAILED {e}")
            continue
        report_rows[name] = rows
        write_daily(today, name, payload)
        print(f"[fetch_omni] {name}: {len(rows)} rows")
        if name in BRANCH_OF:
            turnover_rows[name] = rows
            b = BRANCH_OF[name]
            for row in rows:
                key = (b, row.get("document_date", ""))
                if key[1]:
                    next_row = [
                        b,
                        csv_value(key[1]),
                        csv_value(row.get("value_excl_after_discount", "")),
                        csv_value(row.get("gross_profit", "")),
                    ]
                    if turnover_history.get(key) != next_row:
                        turnover_history[key] = next_row
                        turnover_updates += 1

    sales_cost_lookup = cost_lookup_from_sales(report_rows.get("ANA_Most Popular Products GP") or [])
    stock_cost_lookup = cost_lookup_from_stock_reports(
        {report_name: report_rows.get(report_name) for report_name in STOCK_LISTING_BRANCH}
    )
    cost_lookup = merge_cost_lookups(sales_cost_lookup, stock_cost_lookup)
    stock_cost_rows = build_stock_cost_rows(cost_lookup)
    write_daily(today, "Engine Stock Cost By SKU", {"engine_stock_cost_by_sku": stock_cost_rows})
    print(f"[fetch_omni] Engine Stock Cost By SKU: {len(stock_cost_rows)} rows")

    stock_with_cost_rows = build_stock_listing_with_cost(report_rows, cost_lookup)
    write_daily(today, "Engine Stock Listing With Derived Cost", {"engine_stock_listing_with_derived_cost": stock_with_cost_rows})
    print(f"[fetch_omni] Engine Stock Listing With Derived Cost: {len(stock_with_cost_rows)} rows")

    supplier_master_rows = build_supplier_master(report_rows)
    write_daily(today, "Engine Supplier Master", {"engine_supplier_master": supplier_master_rows})
    print(f"[fetch_omni] Engine Supplier Master: {len(supplier_master_rows)} rows")

    supplier_po_grv_rows = build_supplier_po_grv(
        report_rows.get("Purchase Orders") or [],
        report_rows.get("ANA_Purchase analysis") or [],
        report_rows.get("Supplier Payment Schedule") or [],
        supplier_master_rows,
    )
    write_daily(today, "Engine Supplier PO GRV", {"engine_supplier_po_grv": supplier_po_grv_rows})
    print(f"[fetch_omni] Engine Supplier PO GRV: {len(supplier_po_grv_rows)} rows")

    supplier_purchase_coverage = build_supplier_purchase_coverage(
        report_rows.get("ANA_Purchase analysis") or [],
        supplier_master_rows,
    )
    write_daily(today, "Engine Supplier Purchase Coverage", {"engine_supplier_purchase_coverage": supplier_purchase_coverage})
    print(f"[fetch_omni] Engine Supplier Purchase Coverage: {len(supplier_purchase_coverage)} rows")

    transaction_sources = {}
    for name in BRANCH_BUSY_YESTERDAY:
        try:
            payload, rows = fetch_report(origin, creds, name)
        except Exception as e:
            print(f"[fetch_omni] {name}: FAILED {e}")
            payload, rows = {snake_slug(name): []}, []
        write_daily(today, name, payload)
        transaction_sources[name] = rows
        print(f"[fetch_omni] {name}: {len(rows)} rows")

    derived_rows = build_transaction_rows(transaction_sources, yesterday, BRANCH_BUSY_YESTERDAY)
    write_daily(today, "Engine Daily Branch Transactions", {"engine_daily_branch_transactions": derived_rows})
    print(f"[fetch_omni] Engine Daily Branch Transactions: {len(derived_rows)} rows for {yesterday}")
    for row in derived_rows:
        key = (row["company_branch_code"], row["document_date"])
        if key not in seen_transactions:
            new_transaction_rows.append(
                [
                    row["company_branch_code"],
                    row["document_date"],
                    row["transaction_count"],
                    row["value_excl_after_discount"],
                    row["average_basket_ex_vat"] if row["average_basket_ex_vat"] is not None else "",
                ]
            )
            seen_transactions.add(key)

    mtd_transaction_sources = {}
    for name in BRANCH_BUSY_MTD:
        try:
            payload, rows = fetch_report(origin, creds, name)
        except Exception as e:
            print(f"[fetch_omni] {name}: FAILED {e}")
            payload, rows = {snake_slug(name): []}, []
        write_daily(today, name, payload)
        mtd_transaction_sources[name] = rows
        print(f"[fetch_omni] {name}: {len(rows)} rows")

    mtd_rows = build_mtd_transaction_rows(mtd_transaction_sources, today_date)
    write_daily(today, "Engine MTD Branch Transactions", {"engine_mtd_branch_transactions": mtd_rows})
    print(f"[fetch_omni] Engine MTD Branch Transactions: {len(mtd_rows)} rows")

    audit_payload = turnover_quality_audit(turnover_rows)
    write_daily(today, "Turnover Quality Audit", audit_payload)

    if turnover_updates:
        write_turnover_history(HISTORY, turnover_history)
    if new_transaction_rows:
        with open(TRANSACTION_HISTORY, "a", newline="") as f:
            csv.writer(f).writerows(sorted(new_transaction_rows, key=lambda r: (r[1], r[0])))
    print(f"[fetch_omni] upserted {turnover_updates} turnover rows to {HISTORY}")
    print(f"[fetch_omni] appended {len(new_transaction_rows)} new transaction rows to {TRANSACTION_HISTORY}")


if __name__ == "__main__":
    main()
