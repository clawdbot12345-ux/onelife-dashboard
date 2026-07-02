#!/usr/bin/env python3
"""Structural validator for theme-overrides/ (premium pass 2).

Checks, per file:
  .liquid  — balanced {% if/unless/for/case/capture/form/comment/doc/style
             /javascript/stylesheet/schema %} pairs; {% schema %} body is
             valid JSON; every {% render 'name' %} target exists in
             reports/theme-src/ or theme-overrides/snippets/;
             balanced {{ }} / {% %} delimiters.
  .json    — valid JSON (after stripping the Shopify /* comment */ header).
  .css     — balanced braces, no unclosed comments.
  all      — no emoji codepoints.
Exit code 1 on any failure.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OVR = os.path.join(ROOT, "theme-overrides")
DUMP = os.path.join(ROOT, "reports", "theme-src")

EMOJI = re.compile(
    "[\U0001F000-\U0001FAFF"      # symbols & pictographs, incl. transport
    "\U0001F1E6-\U0001F1FF"       # regional indicators (flags)
    "☀-⛿"               # misc symbols
    "✀-➿"               # dingbats
    "️‍"                # variation selector-16, ZWJ
    "]"
)
# the utf8 hidden-input check mark is a Shopify form convention, not an emoji
EMOJI_ALLOW = ('value="✓"',)

PAIRED = ("if", "unless", "for", "case", "capture", "form", "comment",
          "doc", "style", "javascript", "stylesheet", "schema", "paginate",
          "tablerow")

fails = []


def fail(path, msg):
    fails.append(f"{os.path.relpath(path, ROOT)}: {msg}")


def known_snippets():
    """Snippet names proven to exist on the live theme: dumped snippet files,
    override snippet files, and every render target already used by dumped
    live-theme code (the dump is a filtered subset of the theme)."""
    names = set()
    for f in os.listdir(DUMP):
        if f.startswith("snippets__") and f.endswith(".liquid"):
            names.add(f[len("snippets__"):-len(".liquid")])
        if f.endswith((".liquid", ".json")):
            raw = open(os.path.join(DUMP, f), encoding="utf-8",
                       errors="replace").read()
            for m in re.finditer(r"\{%-?\s*render\s+['\"]([^'\"]+)['\"]",
                                 raw.replace("\\/", "/").replace("\\\"", "\"")):
                names.add(m.group(1))
    snipdir = os.path.join(OVR, "snippets")
    if os.path.isdir(snipdir):
        for f in os.listdir(snipdir):
            if f.endswith(".liquid"):
                names.add(f[:-len(".liquid")])
    return names


SNIPPETS = known_snippets()


def strip_comments(text):
    """Remove {% comment %}..{% endcomment %} and {% doc %}..{% enddoc %}."""
    text = re.sub(r"\{%-?\s*comment\s*-?%\}.*?\{%-?\s*endcomment\s*-?%\}",
                  "", text, flags=re.S)
    text = re.sub(r"\{%-?\s*doc\s*-?%\}.*?\{%-?\s*enddoc\s*-?%\}",
                  "", text, flags=re.S)
    return text


def check_liquid(path, raw):
    text = strip_comments(raw)
    # orphan Liquid openers: strip every well-formed {{...}} / {%...%} pair,
    # then any leftover opener is unclosed. Leftover closers are fine (JS/CSS
    # braces produce them legitimately).
    stripped = re.sub(r"\{\{.*?\}\}", "", text, flags=re.S)
    stripped = re.sub(r"\{%.*?%\}", "", stripped, flags=re.S)
    for orphan in ("{{", "{%"):
        if orphan in stripped:
            i = stripped.index(orphan)
            fail(path, f"unclosed {orphan} near: {stripped[i:i+60]!r}")
    # tag pairs
    tags = re.findall(r"\{%-?\s*(\w+)", text)
    from collections import Counter
    cnt = Counter(tags)
    for t in PAIRED:
        if cnt[t] != cnt["end" + t]:
            fail(path, f"{{% {t} %}} x{cnt[t]} vs {{% end{t} %}} x{cnt['end'+t]}")
    # schema JSON
    for m in re.finditer(r"\{%-?\s*schema\s*-?%\}(.*?)\{%-?\s*endschema\s*-?%\}",
                         raw, flags=re.S):
        try:
            json.loads(m.group(1))
        except Exception as e:
            fail(path, f"schema block invalid JSON: {e}")
    # render targets exist
    for m in re.finditer(r"\{%-?\s*render\s+['\"]([^'\"]+)['\"]", text):
        name = m.group(1)
        if name not in SNIPPETS:
            fail(path, f"render target not found in theme dump/overrides: '{name}'")


def check_json(path, raw):
    body = re.sub(r"^\s*/\*.*?\*/\s*", "", raw, flags=re.S)
    try:
        json.loads(body)
    except Exception as e:
        fail(path, f"invalid JSON: {e}")


def check_css(path, raw):
    if raw.count("{") != raw.count("}"):
        fail(path, f"unbalanced braces: {raw.count('{')} vs {raw.count('}')}")
    if raw.count("/*") != raw.count("*/"):
        fail(path, "unclosed CSS comment")


def check_emoji(path, raw):
    scrub = raw
    for allow in EMOJI_ALLOW:
        scrub = scrub.replace(allow, "")
    for i, line in enumerate(scrub.splitlines(), 1):
        hits = EMOJI.findall(line)
        if hits:
            fail(path, f"emoji at line {i}: {hits}")


def check_custom_liquid_json(path, raw):
    """Validate liquid embedded in JSON template custom_liquid settings."""
    body = re.sub(r"^\s*/\*.*?\*/\s*", "", raw, flags=re.S)
    try:
        data = json.loads(body)
    except Exception:
        return

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if k == "custom_liquid" and isinstance(v, str):
                    check_liquid(path, v)
                else:
                    walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(data)


def main():
    count = 0
    for root, _dirs, files in os.walk(OVR):
        for fn in sorted(files):
            path = os.path.join(root, fn)
            raw = open(path, encoding="utf-8").read()
            count += 1
            check_emoji(path, raw)
            if fn.endswith(".liquid"):
                check_liquid(path, raw)
            elif fn.endswith(".json"):
                check_json(path, raw)
                check_custom_liquid_json(path, raw)
            elif fn.endswith(".css"):
                check_css(path, raw)
    if fails:
        print(f"FAIL — {len(fails)} problem(s) in {count} files:")
        for f in fails:
            print("  •", f)
        sys.exit(1)
    print(f"OK — {count} override files pass all structural checks")


if __name__ == "__main__":
    main()
