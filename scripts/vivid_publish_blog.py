#!/usr/bin/env python3
"""Publish one queued markdown article to the Vivid Health store's Journal.

Usage: python3 scripts/vivid_publish_blog.py content/vivid-queue/2026-07-foo.md

Auth: VIVID_CLIENT_ID + VIVID_CLIENT_SECRET (client credentials) or
VIVID_ADMIN_TOKEN, against VIVID_STORE (default hgywg0-w7).
Finds the blog with handle 'journal' (falls back to the first blog),
creates the article published, prints the URL. The workflow moves the
file to content/vivid-published/ afterwards.

Frontmatter: title, slug, excerpt, tags, products (list of handle/name/price).
Markdown subset: #/##/### headings, **bold**, *italic*, [links](), lists,
tables, paragraphs — same conventions as scripts/publish_blog.py.
"""
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

API = "2025-01"
STORE = (os.environ.get("VIVID_STORE") or "hgywg0-w7").replace(".myshopify.com", "").strip()
BASE = f"https://{STORE}.myshopify.com"


def get_token():
    t = (os.environ.get("VIVID_ADMIN_TOKEN") or "").strip()
    if t:
        return t
    cid = (os.environ.get("VIVID_CLIENT_ID") or "").strip()
    csec = (os.environ.get("VIVID_CLIENT_SECRET") or "").strip()
    if not (cid and csec):
        sys.exit("ERROR: VIVID_ADMIN_TOKEN or VIVID_CLIENT_ID+SECRET required")
    body = urllib.parse.urlencode({
        "grant_type": "client_credentials", "client_id": cid, "client_secret": csec,
    }).encode()
    req = urllib.request.Request(
        f"{BASE}/admin/oauth/access_token", data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"}, method="POST")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())["access_token"]


TOKEN = None


def api(method, path, payload=None):
    url = BASE + path
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={
        "X-Shopify-Access-Token": TOKEN, "Content-Type": "application/json",
        "Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return r.status, json.loads(r.read() or b"{}")
    except urllib.error.HTTPError as e:
        return e.code, {"error": e.read().decode()[:400]}


# ---------- frontmatter + markdown (conventions from publish_blog.py) ----------

def parse(md):
    m = re.match(r"^---\n(.*?)\n---\n(.*)$", md, re.S)
    if not m:
        sys.exit("ERROR: missing frontmatter")
    raw, body = m.group(1), m.group(2)
    fm, cur_list, cur_key = {}, None, None
    for line in raw.split("\n"):
        if re.match(r"^\s*-\s+handle:", line) and cur_key:
            cur_list.append({"handle": line.split("handle:", 1)[1].strip()})
        elif re.match(r"^\s+(name|price):", line) and cur_list:
            k, v = line.strip().split(":", 1)
            cur_list[-1][k] = v.strip()
        elif re.match(r"^[A-Za-z_]+:", line):
            k, v = line.split(":", 1)
            k, v = k.strip(), v.strip().strip('"').strip("'")
            if v == "":
                cur_key, cur_list = k, []
                fm[k] = cur_list
            else:
                fm[k] = v
                cur_key, cur_list = None, None
    return fm, body


def _inline(t):
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"<em>\1</em>", t)
    t = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', t)
    return t


def md_to_html(body):
    out, para, in_list = [], [], False

    def flush_para():
        nonlocal para
        if para:
            out.append("<p>" + _inline(" ".join(para)) + "</p>")
            para = []

    def close_list():
        nonlocal in_list
        if in_list:
            out.append("</ul>")
            in_list = False

    lines = body.split("\n")
    i = 0
    while i < len(lines):
        line = lines[i].rstrip()
        if re.match(r"^\|.+\|$", line) and i + 1 < len(lines) and re.match(r"^\|[\s\-:|]+\|$", lines[i + 1].rstrip()):
            flush_para(); close_list()
            headers = [c.strip() for c in line.strip("|").split("|")]
            out.append('<table><thead><tr>' + "".join(f"<th>{_inline(h)}</th>" for h in headers) + "</tr></thead><tbody>")
            i += 2
            while i < len(lines) and re.match(r"^\|.+\|$", lines[i].rstrip()):
                cells = [c.strip() for c in lines[i].rstrip().strip("|").split("|")]
                out.append("<tr>" + "".join(f"<td>{_inline(c)}</td>" for c in cells) + "</tr>")
                i += 1
            out.append("</tbody></table>")
            continue
        if line.startswith("### "):
            flush_para(); close_list(); out.append(f"<h3>{_inline(line[4:])}</h3>")
        elif line.startswith("## "):
            flush_para(); close_list(); out.append(f"<h2>{_inline(line[3:])}</h2>")
        elif line.startswith("# "):
            flush_para(); close_list(); out.append(f"<h2>{_inline(line[2:])}</h2>")
        elif re.match(r"^[-*] ", line):
            flush_para()
            if not in_list:
                out.append("<ul>")
                in_list = True
            out.append(f"<li>{_inline(line[2:])}</li>")
        elif line.strip() == "":
            flush_para(); close_list()
        else:
            para.append(line.strip())
        i += 1
    flush_para(); close_list()
    return "\n".join(out)


def render_products(products):
    if not products:
        return ""
    cards = []
    for p in products:
        h = p.get("handle", "")
        cards.append(
            f'<div style="border:1px solid #E4DCC9;border-radius:12px;padding:16px 18px;margin:10px 0;background:#FBF7EE">'
            f'<strong>{p.get("name", h)}</strong>'
            f'<span style="float:right;font-weight:600">{p.get("price", "")}</span><br>'
            f'<a href="/products/{h}">View product →</a></div>')
    return ('<h3>From the range</h3>' + "".join(cards) +
            '<p><em>All prices include VAT. Not sure what you need? '
            '<a href="/pages/quiz">Take the 2-minute quiz</a> or '
            '<a href="/pages/consultation">book a consultation</a>.</em></p>')


def verify_products(products):
    ok = []
    for p in products or []:
        h = p.get("handle", "")
        try:
            with urllib.request.urlopen(f"{BASE}/products/{h}.js", timeout=20) as r:
                data = json.loads(r.read())
                if data.get("available") is False:
                    print(f"  ⚠ {h} exists but SOLD OUT — dropping from card list")
                    continue
                ok.append(p)
        except Exception:
            print(f"  ⚠ product {h} not found on storefront — dropping")
    return ok


def main():
    global TOKEN
    if len(sys.argv) < 2:
        sys.exit("usage: vivid_publish_blog.py <content/vivid-queue/file.md>")
    fm, body = parse(open(sys.argv[1]).read())
    for k in ("title", "slug", "excerpt"):
        if not fm.get(k):
            sys.exit(f"ERROR: frontmatter missing {k}")

    TOKEN = get_token()
    print("✓ Token acquired")

    code, blogs = api("GET", f"/admin/api/{API}/blogs.json")
    if code != 200:
        sys.exit(f"ERROR: blogs.json HTTP {code}: {blogs}")
    blog = next((b for b in blogs["blogs"] if b["handle"] == "journal"),
                (blogs["blogs"] or [None])[0])
    if not blog:
        sys.exit("ERROR: store has no blog")
    print(f"✓ Blog: {blog['handle']} ({blog['id']})")

    products = verify_products(fm.get("products"))
    html = md_to_html(body) + render_products(products)
    html += '<p>— The Vivid formulation desk</p>'

    payload = {"article": {
        "title": fm["title"],
        "handle": fm["slug"],
        "body_html": html,
        "tags": fm.get("tags", ""),
        "summary_html": f"<p>{fm['excerpt']}</p>",
        "published": True,
    }}
    code, res = api("POST", f"/admin/api/{API}/blogs/{blog['id']}/articles.json", payload)
    if code not in (200, 201):
        sys.exit(f"ERROR: article create HTTP {code}: {res}")
    art = res["article"]
    url = f"{BASE}/blogs/{blog['handle']}/{art['handle']}"
    print(f"✓ Published: {url}")
    with open("vivid-blog-last-published.txt", "w") as f:
        f.write(url + "\n")


if __name__ == "__main__":
    main()
