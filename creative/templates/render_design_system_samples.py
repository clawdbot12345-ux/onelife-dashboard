#!/usr/bin/env python3
"""Render One Life design-system template samples.

The image base layers are generated photorealistic raster assets. This script
copies those bases into the repo and composites deterministic brand, text, and
layout overlays for review.
"""

from __future__ import annotations

import json
import math
import random
import shutil
import textwrap
import urllib.request
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont


REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / "creative" / "templates"
ASSET_DIR = ROOT / "_assets" / "generated-bases"
PACKSHOT_DIR = ROOT / "_assets" / "shopify-packshots"

PRIMARY = (27, 94, 32)
DEEP = (7, 46, 31)
GREEN = (55, 139, 74)
CREAM = (248, 242, 226)
WARM = (232, 218, 194)
INK = (24, 32, 27)
MUTED = (77, 87, 80)
GOLD = (199, 155, 88)
PINK = (203, 122, 126)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

STORE_STRIP = "Centurion | Glen Village | Edenvale · onelife.co.za | free delivery over R400"
AD_DISCLAIMER = "*This product is not intended to diagnose, treat, cure or prevent any disease."
GENERATED_AT = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


SHOPIFY_PRODUCTS = {
    "buffered-c-90": {
        "title": "VIVID HEALTH - IMMUNE - Buffered C 90 Capsules",
        "shortTitle": "Vivid Buffered C",
        "capsules": "90 CAPSULES",
        "handle": "vivid-health-immune-buffered-c-90-capsules",
        "sku": "6100000000117",
        "priceCents": 17077,
        "source": "https://onelife.co.za/products/vivid-health-immune-buffered-c-90-capsules",
        "image": "https://cdn.shopify.com/s/files/1/0682/9136/3126/files/IMG-5203.png?v=1695296559",
    },
    "immune-plus": {
        "title": "VIVID HEALTH - IMMUNE - Immune Plus 60 Capsules",
        "shortTitle": "Immune Plus",
        "capsules": "60 CAPSULES",
        "handle": "vivid-health-immune-immune-plus-60-capsules",
        "sku": "6009802226087",
        "priceCents": 12500,
        "source": "https://onelife.co.za/products/vivid-health-immune-immune-plus-60-capsules",
        "image": "https://cdn.shopify.com/s/files/1/0682/9136/3126/files/IMG-5194.png?v=1695296146",
    },
    "astragalus": {
        "title": "VIVID HEALTH - IMMUNE - Astragalus 60 Capsules",
        "shortTitle": "Astragalus",
        "capsules": "60 CAPSULES",
        "handle": "vivid-health-immune-astragalus-60-capsules",
        "sku": "6000000837402",
        "priceCents": 16400,
        "source": "https://onelife.co.za/products/vivid-health-immune-astragalus-60-capsules",
        "image": "https://cdn.shopify.com/s/files/1/0682/9136/3126/files/IMG-5196.png?v=1695296217",
    },
    "griffonia": {
        "title": "VIVID HEALTH - STAY VIVID - Griffonia (5-HTP) 60 Capsules",
        "shortTitle": "Griffonia",
        "capsules": "60 CAPSULES",
        "handle": "vivid-health-stay-vivid-griffonia-5-htp-60-capsules",
        "sku": "6100000000711",
        "priceCents": 27500,
        "source": "https://onelife.co.za/products/vivid-health-stay-vivid-griffonia-5-htp-60-capsules",
        "image": "https://cdn.shopify.com/s/files/1/0682/9136/3126/files/IMG-5222.png?v=1695298472",
    },
    "black-seed-oil": {
        "title": "HOLISTQ - Pure Cold Pressed Black Seed Oil - 120 Softgels",
        "shortTitle": "Black Seed Oil",
        "capsules": "120 SOFTGELS",
        "handle": "holistq-pure-cold-pressed-black-seed-oil-120-softgels",
        "sku": "",
        "priceCents": 49900,
        "source": "https://onelife.co.za/products/holistq-pure-cold-pressed-black-seed-oil-120-softgels",
        "image": "https://cdn.shopify.com/s/files/1/0682/9136/3126/files/71aneynGC2L._AC_SL1500_e71bfdf1-5220-425e-b3be-9c54b2de6187.jpg?v=1755072602",
    },
    "soft-iron": {
        "title": "ECO VALLEY NUTRITION - Soft Iron Boost - 60 Capsules",
        "shortTitle": "Soft Iron Boost",
        "capsules": "60 CAPSULES",
        "handle": "eco-valley-nutrition-soft-iron-boost-60-capsules",
        "sku": "",
        "priceCents": 23466,
        "source": "https://onelife.co.za/products/eco-valley-nutrition-soft-iron-boost-60-capsules",
        "image": "https://cdn.shopify.com/s/files/1/0682/9136/3126/files/F5F9E9BB-10D5-4E8C-901F-1D3C5D71EF2E.png?v=1692684402",
    },
    "b12": {
        "title": "WILLOW - Vitamin B12 - 30 Caps",
        "shortTitle": "Vitamin B12",
        "capsules": "30 CAPS",
        "handle": "willow-vitamin-b12-30-caps",
        "sku": "",
        "priceCents": 8900,
        "source": "https://onelife.co.za/products/willow-vitamin-b12-30-caps",
        "image": "https://cdn.shopify.com/s/files/1/0682/9136/3126/products/VitaminB12-30Caps.png?v=1679918709",
    },
    "glycine": {
        "title": "GOOD LIFE WELLNES - Glycine - 250G",
        "shortTitle": "Glycine",
        "capsules": "250G",
        "handle": "verhaki-nutrition-glycine-250g-powder",
        "sku": "",
        "priceCents": 14562,
        "source": "https://onelife.co.za/products/verhaki-nutrition-glycine-250g-powder",
        "image": "https://cdn.shopify.com/s/files/1/0682/9136/3126/files/Glycine3.jpg?v=1772110032",
    },
}


BASES = [
    {
        "id": "energy-desk",
        "prompt": "Premium warm South African home-office desk, winter afternoon light, woman shown over-shoulder, no close-up face, no text.",
    },
    {
        "id": "coffee-desk",
        "prompt": "Cold coffee, to-do list, laptop edge, warm winter home-office light, no people/faces, no readable writing.",
    },
    {
        "id": "supplement-mechanism",
        "prompt": "Blank-label supplements on elegant South African kitchen/home-office surface, negative space for educational diagram, no text.",
    },
    {
        "id": "store-advisor",
        "prompt": "Premium health-store interior, advisor/customer context shown without faces, blank-label bottles, no text/logos.",
    },
    {
        "id": "poll-desk",
        "prompt": "Smartphone with blank social poll interface on warm desk, tea, notebook, no logos/text/faces.",
    },
    {
        "id": "store-online",
        "prompt": "Premium South African health-store interior with laptop/tablet showing blank ecommerce page, no readable signage.",
    },
    {
        "id": "sleep-3am",
        "prompt": "Warm premium South African winter bedroom at 3am, bedside table and lamp, no people, no readable digits.",
    },
    {
        "id": "sleep-window",
        "prompt": "Dark early winter morning bedroom/window detail, premium Gauteng home, no people/text.",
    },
    {
        "id": "sleep-mechanism",
        "prompt": "Calm evening routine tabletop with blank-label supplements, chamomile, lavender, candle, no text/logos.",
    },
    {
        "id": "sleep-duo",
        "prompt": "Two blank-label supplement bottles on warm bedside table, premium evening routine scene, no text.",
    },
    {
        "id": "sleep-poll",
        "prompt": "Late-night bedside smartphone with blank poll interface, warm lamp, journal, no logos/text/faces.",
    },
    {
        "id": "vivid-packshot",
        "prompt": "Single white Vivid-style blank-label supplement bottle, vitamin C citrus, winter greenery, no text/logos.",
    },
    {
        "id": "vivid-trio",
        "prompt": "Three Vivid-style blank-label bottles on formulation bench, in-house production cues, no readable text.",
    },
    {
        "id": "bundle-stack",
        "prompt": "Three-product winter immunity bundle stack, blank labels, citrus/ginger/black seed accents, no text.",
    },
    {
        "id": "back-in-stock",
        "prompt": "Single blank-label bottle being placed back on elegant health-store shelf, hand visible, no face/text.",
    },
    {
        "id": "education-desk",
        "prompt": "Evidence-first wellness desk background, open book, notebook, tea, blank-label supplements, no readable text.",
    },
    {
        "id": "vip-phone",
        "prompt": "Premium WhatsApp VIP recruit scene, smartphone with blank messaging-style screen and green bubbles, no readable text.",
    },
]


def ensure_dirs() -> None:
    ASSET_DIR.mkdir(parents=True, exist_ok=True)


def copy_bases() -> dict[str, Path]:
    ensure_dirs()
    index = {}
    manifest = {
        "generatedAt": GENERATED_AT,
        "sourcePolicy": "Photorealistic image-model base layers copied into the repo; all text/logo/footer overlays are composited locally.",
        "items": [],
    }
    for item in BASES:
        dst = ASSET_DIR / f"{item['id']}.png"
        if not dst.exists():
            raise FileNotFoundError(
                f"{dst} is missing. Generate a new image-model base for {item['id']} and save it to this path before rendering."
            )
        index[item["id"]] = dst
        manifest["items"].append(
            {
                "id": item["id"],
                "file": rel(dst),
                "prompt": item["prompt"],
                "constraints": "No embedded text/logos; avoid close-up synthetic faces; suitable for One Life overlay templates.",
            }
        )
    write_json(ASSET_DIR / "manifest.json", manifest)
    return index


def rel(path: Path) -> str:
    return str(path.relative_to(REPO))


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", "utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", "utf-8")


def download_binary(url: str, dst: Path) -> None:
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() and dst.stat().st_size > 4096:
        return
    req = urllib.request.Request(url, headers={"User-Agent": "Codex One Life creative renderer"})
    with urllib.request.urlopen(req, timeout=40) as response:
        dst.write_bytes(response.read())


def ext_for_url(url: str) -> str:
    clean = url.split("?", 1)[0].lower()
    for ext in (".png", ".jpg", ".jpeg", ".webp"):
        if clean.endswith(ext):
            return ".jpg" if ext == ".jpeg" else ext
    return ".png"


def matte_packshot(src: Path, dst: Path, max_dim: int = 1800) -> None:
    """Remove border-connected light studio backgrounds while preserving label pixels."""
    im = Image.open(src).convert("RGBA")
    scale = min(1.0, max_dim / max(im.size))
    work = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.Resampling.LANCZOS)
    arr = np.array(work)
    rgb = arr[:, :, :3].astype(np.int16)
    sample = 20
    corners = np.concatenate(
        [
            rgb[:sample, :sample].reshape(-1, 3),
            rgb[:sample, -sample:].reshape(-1, 3),
            rgb[-sample:, :sample].reshape(-1, 3),
            rgb[-sample:, -sample:].reshape(-1, 3),
        ]
    )
    bg = corners.mean(axis=0)
    dist = np.sqrt(((rgb - bg) ** 2).sum(axis=2))
    candidate = dist < 24

    h, w = candidate.shape
    seen = np.zeros((h, w), dtype=bool)
    q: deque[tuple[int, int]] = deque()
    for x in range(w):
        for y in (0, h - 1):
            if candidate[y, x] and not seen[y, x]:
                seen[y, x] = True
                q.append((x, y))
    for y in range(h):
        for x in (0, w - 1):
            if candidate[y, x] and not seen[y, x]:
                seen[y, x] = True
                q.append((x, y))
    while q:
        x, y = q.popleft()
        for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if 0 <= nx < w and 0 <= ny < h and candidate[ny, nx] and not seen[ny, nx]:
                seen[ny, nx] = True
                q.append((nx, ny))

    alpha_arr = (~seen).astype(np.uint8) * 255
    row_counts = (alpha_arr > 0).sum(axis=1)
    if row_counts.max() > 0:
        core_start = int(h * 0.24)
        core_end = int(h * 0.76)
        core_width = max(1, int(np.percentile(row_counts[core_start:core_end][row_counts[core_start:core_end] > 0], 90))) if np.any(row_counts[core_start:core_end] > 0) else int(row_counts.max())
        for y in range(int(h * 0.88), h):
            if row_counts[y] > core_width * 1.22:
                alpha_arr[y, :] = 0
    alpha = Image.fromarray(alpha_arr, "L").filter(ImageFilter.GaussianBlur(0.75))
    alpha = alpha.point(lambda a: 0 if a < 18 else min(255, int(a * 1.12)))
    cut = work.copy()
    cut.putalpha(alpha)
    bbox = alpha.point(lambda a: 255 if a > 10 else 0).getbbox()
    if bbox:
        pad = max(2, int(min(cut.size) * 0.012))
        bbox = (
            max(0, bbox[0] - pad),
            max(0, bbox[1] - pad),
            min(cut.width, bbox[2] + pad),
            min(cut.height, bbox[3] + pad),
        )
        cut = cut.crop(bbox)
    dst.parent.mkdir(parents=True, exist_ok=True)
    cut.save(dst)


def ensure_packshots() -> dict[str, Path]:
    PACKSHOT_DIR.mkdir(parents=True, exist_ok=True)
    items = []
    index: dict[str, Path] = {}
    for key, product in SHOPIFY_PRODUCTS.items():
        source_path = PACKSHOT_DIR / f"{key}-source{ext_for_url(product['image'])}"
        cutout_path = PACKSHOT_DIR / f"{key}-cutout.png"
        download_binary(product["image"], source_path)
        matte_packshot(source_path, cutout_path)
        index[key] = cutout_path
        items.append(
            {
                "id": key,
                "title": product["title"],
                "handle": product["handle"],
                "sku": product.get("sku", ""),
                "priceCents": product["priceCents"],
                "price": format_money(product["priceCents"]),
                "sourceProductPage": product["source"],
                "sourceImage": product["image"],
                "sourceFile": rel(source_path),
                "cutoutFile": rel(cutout_path),
                "policy": "Public Shopify packshot; border-connected matte removed locally; label pixels are not redrawn.",
            }
        )
    write_json(
        PACKSHOT_DIR / "manifest.json",
        {
            "generatedAt": GENERATED_AT,
            "source": "Public One Life Shopify product pages/CDN.",
            "items": items,
            "secretScan": "No credentials, customer data, admin tokens, or private API material included.",
        },
    )
    return index


def format_money(cents: int, force_cents: bool = False) -> str:
    if not force_cents and cents % 100 == 0:
        return f"R{cents // 100}"
    return f"R{cents / 100:.2f}"


def discounted_cents(cents: int, percent: int) -> int:
    return int(round(cents * (100 - percent) / 100))


def brighten(color: tuple[int, int, int], amount: int) -> tuple[int, int, int]:
    return tuple(min(255, c + amount) for c in color)


def font_path(weight: str = "regular") -> str:
    paths = {
        "black": [
            "/System/Library/Fonts/Supplemental/Arial Black.ttf",
            "/System/Library/Fonts/ArialHB.ttc",
        ],
        "bold": [
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/System/Library/Fonts/ArialHB.ttc",
        ],
        "regular": [
            "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
            "/System/Library/Fonts/Supplemental/Arial.ttf",
        ],
    }
    for candidate in paths.get(weight, paths["regular"]):
        if Path(candidate).exists():
            return candidate
    return paths["regular"][-1]


def get_font(size: int, weight: str = "regular") -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(font_path(weight), size)


def text_bbox(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.ImageFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0], box[3] - box[1]


def wrap_lines(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.ImageFont, max_width: int) -> list[str]:
    lines: list[str] = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        line = ""
        for word in words:
            trial = word if not line else f"{line} {word}"
            if text_bbox(draw, trial, fnt)[0] <= max_width:
                line = trial
                continue
            if line:
                lines.append(line)
            if text_bbox(draw, word, fnt)[0] <= max_width:
                line = word
            else:
                chunks = textwrap.wrap(word, width=max(4, int(max_width / max(8, fnt.size * 0.55))))
                lines.extend(chunks[:-1])
                line = chunks[-1] if chunks else word
        if line:
            lines.append(line)
    return lines


def fit_font(
    draw: ImageDraw.ImageDraw,
    text: str,
    max_width: int,
    max_height: int,
    start_size: int,
    min_size: int,
    weight: str = "regular",
    spacing_ratio: float = 0.24,
) -> tuple[ImageFont.FreeTypeFont, list[str], int]:
    for size in range(start_size, min_size - 1, -2):
        fnt = get_font(size, weight)
        lines = wrap_lines(draw, text, fnt, max_width)
        spacing = max(6, int(size * spacing_ratio))
        height = sum(text_bbox(draw, line, fnt)[1] for line in lines) + spacing * max(0, len(lines) - 1)
        if height <= max_height:
            return fnt, lines, spacing
    fnt = get_font(min_size, weight)
    return fnt, wrap_lines(draw, text, fnt, max_width), max(6, int(min_size * spacing_ratio))


def draw_lines(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    lines: list[str],
    fnt: ImageFont.ImageFont,
    fill: tuple[int, int, int] | tuple[int, int, int, int],
    spacing: int,
    stroke_width: int = 0,
    stroke_fill: tuple[int, int, int] = BLACK,
) -> int:
    x, y = xy
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill, stroke_width=stroke_width, stroke_fill=stroke_fill)
        y += text_bbox(draw, line, fnt)[1] + spacing
    return y


def cover(path: Path, size: tuple[int, int], anchor: tuple[float, float] = (0.5, 0.5)) -> Image.Image:
    src = Image.open(path).convert("RGB")
    w, h = size
    scale = max(w / src.width, h / src.height)
    resized = src.resize((int(src.width * scale + 0.5), int(src.height * scale + 0.5)), Image.Resampling.LANCZOS)
    left = int((resized.width - w) * anchor[0])
    top = int((resized.height - h) * anchor[1])
    return resized.crop((left, top, left + w, top + h)).convert("RGBA")


def overlay_gradient(img: Image.Image, top_alpha: int = 132, bottom_alpha: int = 118, mid_alpha: int = 10) -> None:
    w, h = img.size
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    px = layer.load()
    for y in range(h):
        t = y / max(1, h - 1)
        if t < 0.5:
            alpha = int(top_alpha * (1 - t * 2) + mid_alpha * (t * 2))
        else:
            alpha = int(mid_alpha * (1 - (t - 0.5) * 2) + bottom_alpha * ((t - 0.5) * 2))
        for x in range(w):
            px[x, y] = (0, 0, 0, alpha)
    img.alpha_composite(layer)


def draw_logo(draw: ImageDraw.ImageDraw, w: int, h: int) -> None:
    draw_cinematic_logo(draw, w, h)


def draw_footer(draw: ImageDraw.ImageDraw, w: int, h: int) -> None:
    draw_cinematic_footer(draw, w, h)


def draw_pager(draw: ImageDraw.ImageDraw, w: int, index: int, total: int) -> None:
    pill_w, pill_h = int(w * 0.13), 52
    x1, y1 = w - pill_w - 58, 128
    draw.rounded_rectangle((x1, y1, x1 + pill_w, y1 + pill_h), radius=18, fill=CREAM + (234,))
    text = f"{index}/{total}"
    fnt = get_font(24, "black")
    tw, th = text_bbox(draw, text, fnt)
    draw.text((x1 + (pill_w - tw) / 2, y1 + (pill_h - th) / 2 - 2), text, font=fnt, fill=DEEP)


def rounded_panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], fill=CREAM + (226,), outline=WHITE + (70,)) -> None:
    radius = max(16, int((box[3] - box[1]) * 0.1))
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=2)


def chip(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], text: str, fill=CREAM + (238,), outline=GOLD + (255,), text_fill=INK) -> None:
    draw.rounded_rectangle(box, radius=max(18, int((box[3] - box[1]) * 0.35)), fill=fill, outline=outline, width=3)
    emoji_prefixes = ("😴", "🥱", "☕", "👇")
    if text and text[0] in emoji_prefixes and Path("/System/Library/Fonts/Apple Color Emoji.ttc").exists():
        emoji = text[0]
        label = text[1:].strip()
        emoji_size = 48 if (box[3] - box[1]) < 140 else 64
        emoji_font = ImageFont.truetype("/System/Library/Fonts/Apple Color Emoji.ttc", emoji_size)
        emoji_w, emoji_h = text_bbox(draw, emoji, emoji_font)
        emoji_x = box[0] + 42
        emoji_y = box[1] + (box[3] - box[1] - emoji_h) / 2 - 2
        draw.text((emoji_x, emoji_y), emoji, font=emoji_font, embedded_color=True)
        label_box = (box[0] + 116, box[1], box[2] - 28, box[3])
        fnt, lines, spacing = fit_font(draw, label, label_box[2] - label_box[0], label_box[3] - label_box[1] - 20, 34, 20, "bold", 0.12)
        total_h = sum(text_bbox(draw, line, fnt)[1] for line in lines) + spacing * max(0, len(lines) - 1)
        yy = label_box[1] + (label_box[3] - label_box[1] - total_h) / 2 - 1
        for line in lines:
            draw.text((label_box[0], yy), line, font=fnt, fill=text_fill)
            yy += text_bbox(draw, line, fnt)[1] + spacing
        return
    fnt, lines, spacing = fit_font(draw, text, box[2] - box[0] - 44, box[3] - box[1] - 20, 36, 20, "bold", 0.12)
    total_h = sum(text_bbox(draw, line, fnt)[1] for line in lines) + spacing * max(0, len(lines) - 1)
    yy = box[1] + (box[3] - box[1] - total_h) / 2 - 1
    for line in lines:
        tw, th = text_bbox(draw, line, fnt)
        draw.text((box[0] + (box[2] - box[0] - tw) / 2, yy), line, font=fnt, fill=text_fill)
        yy += th + spacing


THEMES = {
    "green": {
        "deep": (3, 25, 16),
        "mid": (13, 58, 35),
        "accent": (214, 171, 82),
        "accent2": (110, 196, 72),
        "textAccent": (171, 221, 86),
        "cool": (45, 122, 79),
    },
    "vivid": {
        "deep": (3, 18, 31),
        "mid": (6, 52, 62),
        "accent": (222, 173, 78),
        "accent2": (121, 189, 242),
        "textAccent": (143, 202, 255),
        "cool": (58, 141, 153),
    },
    "copper": {
        "deep": (21, 20, 12),
        "mid": (55, 56, 31),
        "accent": (207, 136, 75),
        "accent2": (232, 183, 103),
        "textAccent": (229, 165, 102),
        "cool": (72, 109, 65),
    },
    "winter": {
        "deep": (4, 20, 26),
        "mid": (24, 67, 75),
        "accent": (207, 178, 108),
        "accent2": (151, 213, 226),
        "textAccent": (184, 225, 235),
        "cool": (70, 120, 134),
    },
}


def theme_palette(theme: str) -> dict[str, tuple[int, int, int]]:
    return THEMES.get(theme, THEMES["green"])


def cinematic_canvas(size: tuple[int, int], theme: str = "green", seed: str = "default", base: Image.Image | None = None) -> Image.Image:
    w, h = size
    pal = theme_palette(theme)
    if base is None:
        img = Image.new("RGBA", (w, h), pal["deep"] + (255,))
    else:
        img = base.resize(size, Image.Resampling.LANCZOS).convert("RGBA")
    arr = np.zeros((h, w, 4), dtype=np.uint8)
    yy = np.linspace(0, 1, h)[:, None]
    xx = np.linspace(0, 1, w)[None, :]
    vignette = np.clip(1.18 - ((xx - 0.56) ** 2 * 1.7 + (yy - 0.48) ** 2 * 1.2), 0.28, 1)
    for channel, (a, b) in enumerate(zip(pal["deep"], pal["mid"])):
        arr[:, :, channel] = np.clip((a * (1 - yy) + b * yy) * vignette, 0, 255)
    arr[:, :, 3] = 255
    grad = Image.fromarray(arr, "RGBA")
    img = Image.blend(img, grad, 0.74 if base else 1.0)
    draw = ImageDraw.Draw(img, "RGBA")
    rng = random.Random(seed)

    # Vertical golden rim light.
    beam_x = int(w * (0.66 + rng.random() * 0.14))
    for i in range(42):
        x = beam_x + int((i - 21) * w * 0.003)
        alpha = max(0, 42 - abs(i - 21) * 2)
        draw.line((x, 0, x - int(w * 0.16), h), fill=pal["accent"] + (alpha,), width=max(1, int(w * 0.002)))

    # Botanical silhouettes and bokeh-like light dust.
    for _ in range(28):
        x = rng.randint(-int(w * 0.1), int(w * 1.06))
        y = rng.randint(0, int(h * 0.82))
        length = rng.randint(int(w * 0.055), int(w * 0.18))
        angle = rng.uniform(-1.2, 1.2)
        alpha = rng.randint(28, 82)
        color = brighten(pal["mid"], rng.randint(0, 34))
        x2 = x + int(math.cos(angle) * length)
        y2 = y + int(math.sin(angle) * length)
        draw.line((x, y, x2, y2), fill=color + (alpha,), width=max(2, int(w * 0.004)))
        for j in range(3):
            lx = x + int((j + 1) * (x2 - x) / 4)
            ly = y + int((j + 1) * (y2 - y) / 4)
            r = rng.randint(int(w * 0.014), int(w * 0.035))
            draw.ellipse((lx - r, ly - r // 2, lx + r, ly + r // 2), fill=color + (alpha // 2,))
    for _ in range(85):
        x = rng.randint(0, w - 1)
        y = rng.randint(int(h * 0.08), int(h * 0.93))
        r = rng.choice([1, 1, 2, 2, 3])
        alpha = rng.randint(34, 150)
        draw.ellipse((x - r, y - r, x + r, y + r), fill=pal["accent"] + (alpha,))
    img = img.filter(ImageFilter.GaussianBlur(0.25))
    draw = ImageDraw.Draw(img, "RGBA")

    # Cinematic foreground vignette.
    vign = Image.new("L", (w, h), 0)
    vd = ImageDraw.Draw(vign)
    vd.rectangle((0, 0, w, h), fill=170)
    vd.ellipse((-int(w * 0.24), -int(h * 0.08), int(w * 1.22), int(h * 1.02)), fill=0)
    vign = vign.filter(ImageFilter.GaussianBlur(int(min(w, h) * 0.12)))
    img.alpha_composite(Image.new("RGBA", (w, h), (0, 0, 0, 0)))
    img = Image.composite(Image.new("RGBA", (w, h), (0, 0, 0, 165)), img, vign)
    return img


def grade_lifestyle(base_path: Path, size: tuple[int, int], theme: str, seed: str) -> Image.Image:
    base = cover(base_path, size, (0.5, 0.5))
    img = cinematic_canvas(size, theme, seed, base)
    overlay_gradient(img, 172, 166, 24)
    return img


def draw_cinematic_logo(draw: ImageDraw.ImageDraw, w: int, h: int) -> None:
    chip_w = max(230, int(w * 0.27))
    chip_h = max(64, int(chip_w * 0.29))
    x1, y1 = max(34, int(w * 0.045)), max(28, int(h * 0.026))
    draw.rounded_rectangle(
        (x1, y1, x1 + chip_w, y1 + chip_h),
        radius=int(chip_h * 0.22),
        fill=(3, 32, 21, 232),
        outline=GOLD + (230,),
        width=max(2, int(w * 0.0025)),
    )
    f1 = get_font(max(20, int(chip_h * 0.38)), "black")
    f2 = get_font(max(9, int(chip_h * 0.17)), "bold")
    draw.text((x1 + int(chip_w * 0.08), y1 + int(chip_h * 0.14)), "ONE LIFE", font=f1, fill=(151, 226, 94))
    draw.text((x1 + int(chip_w * 0.08), y1 + int(chip_h * 0.56)), "HEALTH STORE", font=f2, fill=CREAM)


def draw_campaign_ribbon(draw: ImageDraw.ImageDraw, w: int, h: int, text: str, theme: str = "green") -> None:
    pal = theme_palette(theme)
    margin = max(34, int(w * 0.045))
    ribbon_w = min(int(w * 0.39), max(270, int(len(text) * w * 0.018)))
    ribbon_h = max(58, int(h * 0.046))
    x1 = w - margin - ribbon_w
    y1 = max(30, int(h * 0.03))
    draw.rounded_rectangle((x1, y1, x1 + ribbon_w, y1 + ribbon_h), radius=ribbon_h // 2, fill=(2, 18, 13, 210), outline=pal["accent"] + (240,), width=3)
    f = get_font(max(22, int(ribbon_h * 0.39)), "black")
    tw, th = text_bbox(draw, text, f)
    draw.text((x1 + (ribbon_w - tw) / 2, y1 + (ribbon_h - th) / 2 - 2), text, font=f, fill=WHITE)


def draw_capsule_pill(draw: ImageDraw.ImageDraw, xy: tuple[int, int], text: str, w: int, theme: str = "green") -> None:
    pal = theme_palette(theme)
    x, y = xy
    pill_w = max(int(w * 0.27), len(text) * int(w * 0.016))
    pill_h = max(50, int(w * 0.055))
    draw.rounded_rectangle((x, y, x + pill_w, y + pill_h), radius=pill_h // 2, fill=(238, 198, 91, 245), outline=CREAM + (220,), width=2)
    f = get_font(max(22, int(pill_h * 0.42)), "black")
    tw, th = text_bbox(draw, text, f)
    draw.text((x + (pill_w - tw) / 2, y + (pill_h - th) / 2 - 2), text, font=f, fill=(4, 19, 12))
    draw.line((x + int(pill_w * 0.06), y + pill_h - 4, x + int(pill_w * 0.94), y + pill_h - 4), fill=pal["accent2"] + (120,), width=2)


def draw_star_bullets(draw: ImageDraw.ImageDraw, x: int, y: int, width: int, bullets: list[str], theme: str, size: int) -> int:
    pal = theme_palette(theme)
    f = get_font(size, "bold")
    yy = y
    for bullet in bullets:
        draw.text((x, yy), "*", font=get_font(size + 8, "black"), fill=pal["accent2"])
        lines = wrap_lines(draw, bullet, f, width - 42)
        yy = draw_lines(draw, (x + 42, yy + 4), lines, f, CREAM, max(5, int(size * 0.18)), stroke_width=1, stroke_fill=BLACK)
        yy += max(12, int(size * 0.26))
    return yy


def draw_price_block(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    was: str,
    now: str,
    save: str,
    theme: str = "green",
) -> None:
    pal = theme_palette(theme)
    x1, y1, x2, y2 = box
    bw, bh = x2 - x1, y2 - y1
    draw.rounded_rectangle((x1, y1, x2, y2), radius=max(18, int((y2 - y1) * 0.08)), fill=(1, 18, 12, 216), outline=pal["accent"] + (250,), width=3)
    cx = (x1 + x2) // 2
    f_label = get_font(max(15, int(bh * 0.085)), "black")
    f_now = get_font(max(30, min(int(bh * 0.32), int(bw * 0.17))), "black")
    f_save = get_font(max(14, int(bh * 0.105)), "black")
    was_text = f"WAS  {was}"
    tw, th = text_bbox(draw, was_text, f_label)
    draw.text((cx - tw / 2, y1 + int((y2 - y1) * 0.12)), was_text, font=f_label, fill=WHITE)
    line_y = y1 + int((y2 - y1) * 0.12) + th // 2
    draw.line((cx + tw * 0.12, line_y, cx + tw * 0.46, line_y), fill=(236, 36, 60, 255), width=max(3, int((y2 - y1) * 0.018)))
    now_label = "NOW"
    tw, th = text_bbox(draw, now_label, f_label)
    draw.text((cx - tw / 2, y1 + int((y2 - y1) * 0.33)), now_label, font=f_label, fill=pal["accent"])
    tw, th = text_bbox(draw, now, f_now)
    draw.text((cx - tw / 2, y1 + int((y2 - y1) * 0.47)), now, font=f_now, fill=pal["textAccent"], stroke_width=1, stroke_fill=BLACK)
    save_h = int((y2 - y1) * 0.16)
    save_w = int((x2 - x1) * 0.68)
    sy = y2 - int((y2 - y1) * 0.22)
    sx = cx - save_w // 2
    draw.rounded_rectangle((sx, sy, sx + save_w, sy + save_h), radius=save_h // 2, fill=(32, 133, 56, 242), outline=pal["accent"] + (210,), width=2)
    tw, th = text_bbox(draw, save, f_save)
    draw.text((cx - tw / 2, sy + (save_h - th) / 2 - 1), save, font=f_save, fill=WHITE)


def draw_validity_bar(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], text: str, theme: str) -> None:
    pal = theme_palette(theme)
    x1, y1, x2, y2 = box
    draw.rounded_rectangle((x1, y1, x2, y2), radius=int((y2 - y1) * 0.34), fill=(0, 0, 0, 128), outline=pal["accent"] + (180,), width=2)
    f = get_font(max(18, int((y2 - y1) * 0.36)), "bold")
    tw, th = text_bbox(draw, text, f)
    draw.text((x1 + (x2 - x1 - tw) / 2, y1 + (y2 - y1 - th) / 2 - 1), text, font=f, fill=CREAM)


def draw_compact_price_strip(
    draw: ImageDraw.ImageDraw,
    box: tuple[int, int, int, int],
    was: str,
    now: str,
    save: str,
    theme: str,
) -> None:
    pal = theme_palette(theme)
    x1, y1, x2, y2 = box
    draw.rounded_rectangle((x1, y1, x2, y2), radius=18, fill=(1, 18, 12, 224), outline=pal["accent"] + (230,), width=3)
    label = get_font(19, "black")
    now_font = get_font(30, "black")
    save_font = get_font(16, "bold")
    draw.text((x1 + 22, y1 + 13), f"WAS {was}", font=label, fill=WHITE)
    draw.line((x1 + 88, y1 + 25, x1 + 166, y1 + 25), fill=(236, 36, 60, 255), width=3)
    draw.text((x1 + 22, y1 + 40), "NOW", font=label, fill=pal["accent"])
    draw.text((x1 + 92, y1 + 32), now, font=now_font, fill=pal["textAccent"], stroke_width=1, stroke_fill=BLACK)
    tw, th = text_bbox(draw, save, save_font)
    draw.text((x2 - tw - 18, y2 - th - 12), save, font=save_font, fill=CREAM)


def draw_roundels(draw: ImageDraw.ImageDraw, y: int, labels: list[str], w: int, theme: str) -> None:
    pal = theme_palette(theme)
    count = len(labels)
    gap = max(18, int(w * 0.025))
    r = max(38, min(54, int(w * 0.048)))
    total_w = count * (r * 2) + (count - 1) * gap
    start = (w - total_w) // 2
    f_icon = get_font(max(24, int(r * 0.62)), "black")
    f_label = get_font(max(12, int(r * 0.26)), "bold")
    icons = ["+", "C", "Z", "✓", "5"]
    for i, label in enumerate(labels):
        cx = start + r + i * (2 * r + gap)
        draw.ellipse((cx - r, y - r, cx + r, y + r), fill=(7, 43, 30, 220), outline=pal["accent"] + (245,), width=3)
        icon = icons[i % len(icons)]
        tw, th = text_bbox(draw, icon, f_icon)
        draw.text((cx - tw / 2, y - th / 2 - 3), icon, font=f_icon, fill=pal["accent2"])
        lines = wrap_lines(draw, label.upper(), f_label, int(r * 2.8))
        yy = y + r + 12
        for line in lines[:2]:
            tw, th = text_bbox(draw, line, f_label)
            draw.text((cx - tw / 2, yy), line, font=f_label, fill=CREAM)
            yy += th + 3


def draw_roundels_between(draw: ImageDraw.ImageDraw, y: int, labels: list[str], x1: int, x2: int, theme: str) -> None:
    pal = theme_palette(theme)
    count = len(labels)
    available = max(220, x2 - x1)
    gap = max(12, int(available * 0.035))
    r = max(34, min(50, int((available - gap * (count - 1)) / (count * 2))))
    total_w = count * (r * 2) + (count - 1) * gap
    start = x1 + (available - total_w) // 2
    f_icon = get_font(max(22, int(r * 0.58)), "black")
    f_label = get_font(max(10, int(r * 0.24)), "bold")
    icons = ["+", "C", "Z", "✓", "5"]
    for i, label in enumerate(labels):
        cx = start + r + i * (2 * r + gap)
        draw.ellipse((cx - r, y - r, cx + r, y + r), fill=(7, 43, 30, 220), outline=pal["accent"] + (245,), width=3)
        icon = icons[i % len(icons)]
        tw, th = text_bbox(draw, icon, f_icon)
        draw.text((cx - tw / 2, y - th / 2 - 3), icon, font=f_icon, fill=pal["accent2"])
        lines = wrap_lines(draw, label.upper(), f_label, int(r * 2.7))
        yy = y + r + 10
        for line in lines[:2]:
            tw, th = text_bbox(draw, line, f_label)
            draw.text((cx - tw / 2, yy), line, font=f_label, fill=CREAM)
            yy += th + 3


def draw_cta_bar(draw: ImageDraw.ImageDraw, w: int, h: int, y: int, text: str, theme: str) -> None:
    pal = theme_palette(theme)
    x1 = int(w * 0.08)
    x2 = int(w * 0.92)
    bar_h = max(68, int(h * 0.055))
    draw.rounded_rectangle((x1, y, x2, y + bar_h), radius=bar_h // 2, fill=pal["accent"] + (246,), outline=CREAM + (230,), width=2)
    circle_r = int(bar_h * 0.62)
    cx = x1 + circle_r
    cy = y + bar_h // 2
    draw.ellipse((cx - circle_r, cy - circle_r, cx + circle_r, cy + circle_r), fill=(4, 45, 30, 238), outline=CREAM + (230,), width=3)
    cart = "□"
    cf = get_font(max(26, int(circle_r * 0.72)), "black")
    tw, th = text_bbox(draw, cart, cf)
    draw.text((cx - tw / 2, cy - th / 2 - 3), cart, font=cf, fill=pal["accent"])
    f = get_font(max(26, int(bar_h * 0.39)), "black")
    tw, th = text_bbox(draw, text, f)
    draw.text((x1 + circle_r * 2 + 22, y + (bar_h - th) / 2 - 1), text, font=f, fill=(5, 22, 14))


def draw_cinematic_footer(draw: ImageDraw.ImageDraw, w: int, h: int) -> None:
    footer_h = max(88, int(h * 0.074))
    y = h - footer_h
    draw.rectangle((0, y, w, h), fill=(1, 24, 17, 238))
    draw.line((int(w * 0.06), y + 4, int(w * 0.94), y + 4), fill=GOLD + (230,), width=2)
    f = get_font(max(17, int(w * 0.018)), "bold")
    tw, th = text_bbox(draw, STORE_STRIP, f)
    while tw > w * 0.88 and f.size > 12:
        f = get_font(f.size - 1, "bold")
        tw, th = text_bbox(draw, STORE_STRIP, f)
    draw.text(((w - tw) / 2, y + int(footer_h * 0.22)), STORE_STRIP, font=f, fill=CREAM)
    df = get_font(max(12, int(w * 0.014)), "regular")
    tw, th = text_bbox(draw, AD_DISCLAIMER, df)
    while tw > w * 0.9 and df.size > 10:
        df = get_font(df.size - 1, "regular")
        tw, th = text_bbox(draw, AD_DISCLAIMER, df)
    draw.text(((w - tw) / 2, h - th - int(footer_h * 0.13)), AD_DISCLAIMER, font=df, fill=(205, 190, 152))


def paste_packshot(
    img: Image.Image,
    packshots: dict[str, Path],
    product_id: str,
    center: tuple[int, int],
    target_h: int,
    z: float = 1.0,
) -> tuple[int, int, int, int]:
    product = Image.open(packshots[product_id]).convert("RGBA")
    scale = target_h / product.height
    size = (max(1, int(product.width * scale)), max(1, int(product.height * scale)))
    product = product.resize(size, Image.Resampling.LANCZOS)
    x = int(center[0] - product.width / 2)
    y = int(center[1] - product.height / 2)
    draw = ImageDraw.Draw(img, "RGBA")
    shadow_w = int(product.width * 0.82 * z)
    shadow_h = max(18, int(product.height * 0.055 * z))
    sx = center[0]
    sy = y + product.height - int(shadow_h * 0.35)
    draw.ellipse((sx - shadow_w // 2, sy - shadow_h // 2, sx + shadow_w // 2, sy + shadow_h // 2), fill=(0, 0, 0, 124))
    img.alpha_composite(product, (x, y))
    return (x, y, x + product.width, y + product.height)


def draw_pedestal(draw: ImageDraw.ImageDraw, center: tuple[int, int], width: int, theme: str) -> None:
    pal = theme_palette(theme)
    cx, cy = center
    h = max(30, int(width * 0.13))
    draw.ellipse((cx - width // 2, cy - h, cx + width // 2, cy + h), fill=(13, 38, 27, 232), outline=pal["accent"] + (240,), width=3)
    draw.rectangle((cx - width // 2, cy - h // 2, cx + width // 2, cy + h), fill=(18, 43, 30, 225))
    draw.ellipse((cx - width // 2, cy - h, cx + width // 2, cy + h // 2), fill=(26, 55, 35, 246), outline=pal["accent"] + (245,), width=3)
    draw.ellipse((cx - width // 3, cy - h // 2, cx + width // 3, cy + h // 3), fill=pal["accent"] + (44,))


def draw_display_title(draw: ImageDraw.ImageDraw, xy: tuple[int, int], lines: tuple[str, str], max_width: int, theme: str, size: int) -> int:
    pal = theme_palette(theme)
    x, y = xy
    f = get_font(size, "black")
    first, second = lines
    first_lines = wrap_lines(draw, first, f, max_width)
    y = draw_lines(draw, (x, y), first_lines, f, WHITE, max(6, int(size * 0.1)), stroke_width=2, stroke_fill=BLACK)
    second_lines = wrap_lines(draw, second, f, max_width)
    y = draw_lines(draw, (x, y + int(size * 0.04)), second_lines, f, pal["textAccent"], max(6, int(size * 0.1)), stroke_width=2, stroke_fill=BLACK)
    return y


@dataclass(frozen=True)
class CarouselSlide:
    role: str
    base: str
    title: str
    body: str
    full_copy: str
    options: tuple[str, ...] = ()
    diagram: tuple[str, ...] = ()


ENERGY_SLIDES = [
    CarouselSlide("Hook", "energy-desk", "Always tired by 2pm?", "It's not just \"winter laziness\".", "Always tired by 2pm? It's not just \"winter laziness\"."),
    CarouselSlide("Pain", "coffee-desk", "Coffee #3 isn't working.", "The afternoon slump is running your diary.", "Coffee #3 isn't working. The afternoon slump is running your diary."),
    CarouselSlide(
        "Mechanism",
        "supplement-mechanism",
        "Low iron and B12",
        "are two of the most common reasons women feel flat — they carry oxygen and power your cells' energy production.",
        "Low iron and B12 are two of the most common reasons women feel flat — they carry oxygen and power your cells' energy production.",
        diagram=("Iron", "B12", "Oxygen + cell energy support"),
    ),
    CarouselSlide(
        "Proof",
        "store-advisor",
        "Check the basics first.",
        "Our team helps customers check the basics first — gentle iron (Eco Valley Soft Iron Boost) and B12 support, matched to you in store.",
        "Our team helps customers check the basics first — gentle iron (Eco Valley Soft Iron Boost) and B12 support, matched to you in store.",
    ),
    CarouselSlide(
        "Participation",
        "poll-desk",
        "Which one's you:",
        "Tell us below.",
        "Which one's you: 😴 2pm slump / 🥱 wake up tired / ☕ coffee dependent? Tell us below.",
        options=("😴 2pm slump", "🥱 wake up tired", "☕ coffee dependent"),
    ),
    CarouselSlide(
        "CTA",
        "store-online",
        "Talk to the team.",
        "Talk to the team at Centurion, Glen Village or Edenvale — or onelife.co.za (free delivery over R400).",
        "Talk to the team at Centurion, Glen Village or Edenvale — or onelife.co.za (free delivery over R400).",
    ),
]

SLEEP_SLIDES = [
    CarouselSlide("Hook", "sleep-3am", "Winter sleep falling apart?", "Asleep at 9, wide awake at 3.", "Winter sleep falling apart? Asleep at 9, wide awake at 3."),
    CarouselSlide("Pain", "sleep-window", "Short days scramble your rhythm.", "The 3am wake-up becomes a habit.", "Short days scramble your rhythm — and the 3am wake-up becomes a habit."),
    CarouselSlide(
        "Mechanism",
        "sleep-mechanism",
        "Evening wind-down basics",
        "Magnesium contributes to normal nervous-system function; glycine is the calming amino acid your body uses as evening winds down.",
        "Magnesium contributes to normal nervous-system function; glycine is the calming amino acid your body uses as evening winds down.",
        diagram=("Magnesium", "Glycine", "Evening routine support"),
    ),
    CarouselSlide(
        "Proof",
        "sleep-duo",
        "Customer favourites",
        "PrimeSelf Magnesium Complex and Good Life Glycine — ask the team which fits your evening routine.",
        "Customer favourites: PrimeSelf Magnesium Complex and Good Life Glycine — ask the team which fits your evening routine.",
    ),
    CarouselSlide(
        "Participation",
        "sleep-poll",
        "What's your 3am brain doing?",
        "",
        "What's your 3am brain doing — replaying today, planning tomorrow, or just… awake? 👇",
        options=("replaying today", "planning tomorrow", "just… awake"),
    ),
    CarouselSlide(
        "CTA",
        "store-online",
        "In store or online.",
        "In store at Centurion, Glen Village & Edenvale — or onelife.co.za, free delivery over R400.",
        "In store at Centurion, Glen Village & Edenvale — or onelife.co.za, free delivery over R400.",
    ),
]


def draw_diagram(draw: ImageDraw.ImageDraw, w: int, y: int, items: tuple[str, ...]) -> None:
    if not items:
        return
    x = int(w * 0.09)
    box_w = int(w * 0.24)
    gap = int(w * 0.035)
    h = 98
    for i, label in enumerate(items):
        bx = x + i * (box_w + gap)
        bw = box_w if i < 2 else int(w * 0.33)
        chip(draw, (bx, y, bx + bw, y + h), label, fill=WHITE + (226,), outline=GOLD + (255,), text_fill=DEEP)
        if i < len(items) - 1:
            ax = bx + bw + 10
            ay = y + h // 2
            draw.line((ax, ay, ax + gap - 20, ay), fill=GOLD + (255,), width=5)
            draw.polygon([(ax + gap - 20, ay - 10), (ax + gap - 20, ay + 10), (ax + gap - 4, ay)], fill=GOLD + (255,))


def render_carousel_slide(
    slide: CarouselSlide,
    base_index: dict[str, Path],
    packshots: dict[str, Path],
    out_path: Path,
    index: int,
    total: int,
) -> None:
    w, h = 1080, 1920
    theme = "winter" if slide.base.startswith("sleep") else "green"
    img = grade_lifestyle(base_index[slide.base], (w, h), theme, f"{slide.base}-{index}")
    draw = ImageDraw.Draw(img)
    draw_cinematic_logo(draw, w, h)
    draw_campaign_ribbon(draw, w, h, slide.role.upper(), theme)
    draw_pager(draw, w, index, total)

    title_max_h = 260
    title_f, title_lines, title_spacing = fit_font(draw, slide.title, 900, title_max_h, 84, 52, "black", 0.18)
    draw_lines(draw, (68, 210), title_lines, title_f, CREAM, title_spacing, stroke_width=3, stroke_fill=BLACK)

    if slide.role in {"Mechanism", "Proof"}:
        product_ids = ("soft-iron", "b12") if "iron" in slide.full_copy.lower() or "b12" in slide.full_copy.lower() else ("glycine", "griffonia")
        draw_pedestal(draw, (760, 1280), 430, theme)
        paste_packshot(img, packshots, product_ids[0], (670, 1120), 460, 0.9)
        paste_packshot(img, packshots, product_ids[1], (860, 1160), 410, 0.85)

    if slide.options:
        if slide.body:
            body_f, body_lines, body_spacing = fit_font(draw, slide.body, 850, 92, 40, 26, "bold", 0.15)
            end_y = draw_lines(draw, (76, 510), body_lines, body_f, CREAM, body_spacing, stroke_width=2, stroke_fill=BLACK)
        else:
            end_y = 500
        y = max(720, end_y + 120)
        for option in slide.options:
            chip(draw, (108, y, 972, y + 106), option, fill=CREAM + (235,), outline=GOLD + (255,), text_fill=DEEP)
            y += 136
    else:
        panel_x, panel_y = 62, 520
        panel_w = 956
        panel_h = 340 if len(slide.body) < 110 else 430
        rounded_panel(draw, (panel_x, panel_y, panel_x + panel_w, panel_y + panel_h), fill=(2, 23, 16, 222), outline=theme_palette(theme)["accent"] + (190,))
        body_f, body_lines, body_spacing = fit_font(draw, slide.body, panel_w - 72, panel_h - 70, 44, 28, "bold", 0.2)
        draw_lines(draw, (panel_x + 36, panel_y + 34), body_lines, body_f, CREAM, body_spacing)
        if slide.diagram:
            draw_diagram(draw, w, panel_y + panel_h + 72, slide.diagram)

    draw_cinematic_footer(draw, w, h)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(out_path, quality=94, subsampling=1)


def render_carousel_set(
    campaign_tag: str,
    title: str,
    slides: list[CarouselSlide],
    base_index: dict[str, Path],
    packshots: dict[str, Path],
    out_dir: Path,
    mirror_out_dir: Path | None = None,
) -> dict:
    slide_dir = out_dir / "slides"
    rendered = []
    for i, slide in enumerate(slides, 1):
        path = slide_dir / f"slide-{i:02d}.jpg"
        render_carousel_slide(slide, base_index, packshots, path, i, len(slides))
        rendered.append(path)
        if mirror_out_dir:
            mirror = mirror_out_dir / "slides" / path.name
            mirror.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(path, mirror)
    manifest = {
        "campaignTag": campaign_tag,
        "title": title,
        "generatedAt": GENERATED_AT,
        "templateId": "T01",
        "format": "6-slide TikTok/IG carousel",
        "dimensions": {"width": 1080, "height": 1920},
        "baseLayerPolicy": "Photorealistic image-model raster base per slide; text/logo/footer composited after generation.",
        "slides": [
            {
                "index": i + 1,
                "role": slide.role,
                "copy": slide.full_copy,
                "baseImage": rel(base_index[slide.base]),
                "file": rel(rendered[i]),
            }
            for i, slide in enumerate(slides)
        ],
    }
    write_json(out_dir / "manifest.json", manifest)
    if mirror_out_dir:
        mirror_manifest = dict(manifest)
        mirror_manifest["slides"] = [
            dict(item, file=rel(mirror_out_dir / "slides" / Path(item["file"]).name))
            for item in manifest["slides"]
        ]
        write_json(mirror_out_dir / "manifest.json", mirror_manifest)
    return manifest


def render_monday_hero(packshots: dict[str, Path], out: Path, size: tuple[int, int], cta: str) -> None:
    w, h = size
    theme = "green"
    pal = theme_palette(theme)
    img = cinematic_canvas(size, theme, f"monday-hero-{cta}-{w}x{h}")
    draw = ImageDraw.Draw(img, "RGBA")
    draw_cinematic_logo(draw, w, h)
    draw_campaign_ribbon(draw, w, h, "MONDAY OFFER", theme)

    is_story = h > w
    title_size = 78 if is_story else 58
    title_x = int(w * 0.07)
    title_y = int(h * (0.15 if is_story else 0.18))
    draw.text((title_x, title_y - int(title_size * 0.72)), "MONDAY OFFER", font=get_font(max(26, int(title_size * 0.35)), "black"), fill=pal["accent"])
    draw.line((title_x, title_y - int(title_size * 0.18), title_x + int(w * 0.14), title_y - int(title_size * 0.18)), fill=pal["accent"], width=4)
    draw.line((title_x + int(w * 0.16), title_y - int(title_size * 0.18), title_x + int(w * 0.31), title_y - int(title_size * 0.18)), fill=pal["accent2"], width=4)
    title_end = draw_display_title(draw, (title_x, title_y), ("BUFFERED C", "90s"), int(w * (0.58 if is_story else 0.52)), theme, title_size)
    draw_capsule_pill(draw, (title_x, title_end + 22), "90 CAPSULES", w, theme)

    product_h = int(h * 0.45) if is_story else int(h * 0.49)
    product_center = (int(w * (0.70 if is_story else 0.72)), int(h * (0.53 if is_story else 0.54)))
    draw_pedestal(draw, (product_center[0], int(product_center[1] + product_h * 0.46)), int(product_h * 0.78), theme)
    paste_packshot(img, packshots, "buffered-c-90", product_center, product_h)

    limited_y = int(h * (0.46 if is_story else 0.39))
    lf = get_font(max(24, int(w * 0.027)), "black")
    draw.text((title_x, limited_y), "LIMITED WEEK OFFER", font=lf, fill=pal["accent2"])
    bullets = (
        [
            "Daily vitamin C support for the immune system*",
            "Buffered calcium ascorbate, gentle on routine*",
            "Vivid Health, made in South Africa",
        ]
        if is_story
        else [
            "Immune support*",
            "Gentle buffered C*",
            "SA-made Vivid",
        ]
    )
    draw_star_bullets(draw, title_x, limited_y + int(h * 0.035), int(w * (0.47 if is_story else 0.43)), bullets, theme, max(20, int(w * (0.026 if is_story else 0.024))))

    was = SHOPIFY_PRODUCTS["buffered-c-90"]["priceCents"]
    now = discounted_cents(was, 10)
    save = was - now
    if is_story:
        price_box = (int(w * 0.06), int(h * 0.62), int(w * 0.50), int(h * 0.80))
        valid_box = (int(w * 0.08), int(h * 0.815), int(w * 0.48), int(h * 0.855))
        roundel_y = int(h * 0.735)
        cta_y = int(h * 0.865)
    else:
        price_box = (int(w * 0.06), int(h * 0.57), int(w * 0.48), int(h * 0.80))
        valid_box = (int(w * 0.08), int(h * 0.815), int(w * 0.48), int(h * 0.86))
        roundel_y = int(h * 0.78)
        cta_y = int(h * 0.865)
    draw_price_block(draw, price_box, format_money(was, True), format_money(now, True), f"SAVE {format_money(save, True)} / 10%", theme)
    draw_validity_bar(draw, valid_box, "VALID 15 JUN TO 21 JUN 2026", theme)
    draw_roundels_between(draw, roundel_y, ["Vitamin C", "Gentle", "90 caps", "Daily support"], int(w * 0.52), int(w * 0.94), theme)
    draw_cta_bar(draw, w, h, cta_y, cta, theme)
    draw_cinematic_footer(draw, w, h)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(out, quality=94, subsampling=1)


def draw_product_row_panel(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], rows: list[tuple[str, str]], theme: str, title: str = "LIVE PRODUCT SLOTS") -> None:
    pal = theme_palette(theme)
    x1, y1, x2, y2 = box
    draw.rounded_rectangle((x1, y1, x2, y2), radius=max(18, int((y2 - y1) * 0.08)), fill=CREAM + (234,), outline=pal["accent"] + (220,), width=3)
    tf = get_font(max(18, int((y2 - y1) * 0.11)), "black")
    draw.text((x1 + 28, y1 + 22), title, font=tf, fill=DEEP)
    f = get_font(max(16, int((y2 - y1) * 0.085)), "bold")
    yy = y1 + int((y2 - y1) * 0.32)
    for name, price in rows:
        draw.text((x1 + 30, yy), name, font=f, fill=INK)
        tw, th = text_bbox(draw, price, f)
        draw.text((x2 - tw - 30, yy), price, font=f, fill=DEEP)
        yy += int((y2 - y1) * 0.17)
        draw.line((x1 + 28, yy - 10, x2 - 28, yy - 10), fill=(196, 171, 118, 120), width=1)


def render_vivid_day_cinematic(packshots: dict[str, Path], out: Path, size: tuple[int, int]) -> None:
    w, h = size
    theme = "vivid"
    img = cinematic_canvas(size, theme, f"vivid-day-{w}x{h}")
    draw = ImageDraw.Draw(img, "RGBA")
    draw_cinematic_logo(draw, w, h)
    draw_campaign_ribbon(draw, w, h, "VIVID WEDNESDAY", theme)
    is_story = h > w
    title_x = int(w * 0.07)
    title_y = int(h * (0.17 if is_story else 0.19))
    draw.text((title_x, title_y - 54), "VIVID WEDNESDAY", font=get_font(max(28, int(w * 0.032)), "black"), fill=theme_palette(theme)["accent"])
    draw_display_title(draw, (title_x, title_y), ("VIVID IMMUNE", "SPOTLIGHT"), int(w * 0.58), theme, 76 if is_story else 56)
    draw_capsule_pill(draw, (title_x, int(h * (0.38 if is_story else 0.39))), "MADE IN-HOUSE", w, theme)
    bullets = [
        "Immune Plus, Buffered C and Astragalus*",
        "Vivid Health house range, SA made",
        "Ask the team which fits your routine",
    ]
    draw_star_bullets(draw, title_x, int(h * (0.45 if is_story else 0.47)), int(w * 0.48), bullets, theme, max(20, int(w * 0.025)))
    base_y = int(h * (0.69 if is_story else 0.65))
    draw_pedestal(draw, (int(w * 0.68), base_y + 120), int(w * 0.45), theme)
    paste_packshot(img, packshots, "immune-plus", (int(w * 0.56), base_y - 40), int(h * (0.25 if is_story else 0.30)), 0.8)
    paste_packshot(img, packshots, "buffered-c-90", (int(w * 0.70), base_y - 80), int(h * (0.29 if is_story else 0.34)), 0.9)
    paste_packshot(img, packshots, "astragalus", (int(w * 0.82), base_y - 30), int(h * (0.25 if is_story else 0.29)), 0.8)
    rows = [
        ("Immune Plus", format_money(SHOPIFY_PRODUCTS["immune-plus"]["priceCents"])),
        ("Buffered C 90s", format_money(SHOPIFY_PRODUCTS["buffered-c-90"]["priceCents"], True)),
        ("Astragalus", format_money(SHOPIFY_PRODUCTS["astragalus"]["priceCents"])),
    ]
    draw_product_row_panel(draw, (int(w * 0.07), int(h * 0.70), int(w * 0.51), int(h * 0.84)), rows, theme, "VIVID RANGE")
    draw_roundels(draw, int(h * 0.84), ["SA made", "Immune", "Routine", "Value"], w, theme)
    draw_cta_bar(draw, w, h, int(h * 0.885), "IN-STORE ONLY • WHILE STOCKS LAST", theme)
    draw_cinematic_footer(draw, w, h)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(out, quality=94, subsampling=1)


def render_bundle_cinematic(packshots: dict[str, Path], out: Path, size: tuple[int, int]) -> None:
    w, h = size
    theme = "copper"
    img = cinematic_canvas(size, theme, f"bundle-{w}x{h}")
    draw = ImageDraw.Draw(img, "RGBA")
    draw_cinematic_logo(draw, w, h)
    draw_campaign_ribbon(draw, w, h, "THURSDAY BUNDLE", theme)
    title_x = int(w * 0.07)
    title_y = int(h * (0.17 if h > w else 0.19))
    draw_display_title(draw, (title_x, title_y), ("WINTER IMMUNITY", "STACK"), int(w * 0.62), theme, 72 if h > w else 54)
    draw_capsule_pill(draw, (title_x, int(h * (0.36 if h > w else 0.39))), "3 PRODUCT STACK", w, theme)
    bullets = [
        "Vivid Immune Plus + Buffered C*",
        "Black Seed Oil stack slot",
        "Per-item and bundle price slots",
    ]
    draw_star_bullets(draw, title_x, int(h * (0.43 if h > w else 0.47)), int(w * 0.47), bullets, theme, max(20, int(w * 0.024)))
    base_y = int(h * (0.68 if h > w else 0.66))
    draw_pedestal(draw, (int(w * 0.70), base_y + 135), int(w * 0.50), theme)
    paste_packshot(img, packshots, "immune-plus", (int(w * 0.55), base_y - 10), int(h * (0.24 if h > w else 0.29)), 0.82)
    paste_packshot(img, packshots, "buffered-c-90", (int(w * 0.70), base_y - 70), int(h * (0.29 if h > w else 0.34)), 0.9)
    paste_packshot(img, packshots, "black-seed-oil", (int(w * 0.84), base_y + 5), int(h * (0.23 if h > w else 0.28)), 0.78)
    rows = [
        ("Immune Plus", format_money(SHOPIFY_PRODUCTS["immune-plus"]["priceCents"])),
        ("Buffered C 90s", format_money(SHOPIFY_PRODUCTS["buffered-c-90"]["priceCents"], True)),
        ("Black Seed Oil", format_money(SHOPIFY_PRODUCTS["black-seed-oil"]["priceCents"])),
        ("Bundle price", "R___"),
    ]
    draw_product_row_panel(draw, (int(w * 0.07), int(h * 0.68), int(w * 0.53), int(h * 0.86)), rows, theme, "PRICE SLOTS")
    draw_cta_bar(draw, w, h, int(h * 0.885), "SHOP ONLINE • FREE DELIVERY OVER R400", theme)
    draw_cinematic_footer(draw, w, h)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(out, quality=94, subsampling=1)


def render_product_alert(packshots: dict[str, Path], out: Path, size: tuple[int, int], product_id: str, headline: tuple[str, str], ribbon: str, theme: str, cta: str) -> None:
    w, h = size
    img = cinematic_canvas(size, theme, f"{product_id}-{headline}-{w}x{h}")
    draw = ImageDraw.Draw(img, "RGBA")
    draw_cinematic_logo(draw, w, h)
    draw_campaign_ribbon(draw, w, h, ribbon, theme)
    title_x = int(w * 0.07)
    title_y = int(h * (0.22 if h <= w else 0.17))
    draw_display_title(draw, (title_x, title_y), headline, int(w * 0.58), theme, 68 if h > w else 56)
    draw_capsule_pill(draw, (title_x, int(h * (0.40 if h > w else 0.42))), SHOPIFY_PRODUCTS[product_id]["capsules"], w, theme)
    draw_star_bullets(
        draw,
        title_x,
        int(h * (0.48 if h > w else 0.50)),
        int(w * 0.47),
        ["Real Shopify packshot", "Label kept pixel-faithful", "Copy slot ready for weekly use"],
        theme,
        max(19, int(w * 0.024)),
    )
    center = (int(w * 0.71), int(h * (0.55 if h > w else 0.58)))
    product_h = int(h * (0.38 if h > w else 0.44))
    draw_pedestal(draw, (center[0], int(center[1] + product_h * 0.46)), int(product_h * 0.75), theme)
    paste_packshot(img, packshots, product_id, center, product_h)
    draw_cta_bar(draw, w, h, int(h * 0.865), cta, theme)
    draw_cinematic_footer(draw, w, h)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(out, quality=94, subsampling=1)


def render_email_hero_cinematic(packshots: dict[str, Path], out: Path) -> None:
    w, h = 1200, 600
    theme = "green"
    img = cinematic_canvas((w, h), theme, "email-buffered-c")
    draw = ImageDraw.Draw(img, "RGBA")
    draw_cinematic_logo(draw, w, h)
    draw_campaign_ribbon(draw, w, h, "MONDAY HERO", theme)
    draw_display_title(draw, (72, 148), ("BUFFERED C", "10% OFF"), 540, theme, 58)
    draw_capsule_pill(draw, (72, 282), "90 CAPSULES", w, theme)
    was = SHOPIFY_PRODUCTS["buffered-c-90"]["priceCents"]
    now = discounted_cents(was, 10)
    save = was - now
    draw_compact_price_strip(draw, (72, 350, 470, 430), format_money(was, True), format_money(now, True), f"SAVE {format_money(save, True)} / 10%", theme)
    draw_pedestal(draw, (860, 485), 390, theme)
    paste_packshot(img, packshots, "buffered-c-90", (860, 320), 430)
    draw_cta_bar(draw, w, h, 438, "SHOP ONLINE • FREE DELIVERY OVER R400", theme)
    draw_cinematic_footer(draw, w, h)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(out, quality=94, subsampling=1)


def draw_headline_block(
    draw: ImageDraw.ImageDraw,
    title: str,
    subtitle: str,
    box: tuple[int, int, int, int],
    title_size: int,
    subtitle_size: int,
    light: bool = True,
) -> None:
    x1, y1, x2, y2 = box
    title_color = CREAM if light else DEEP
    sub_color = (246, 237, 212) if light else MUTED
    title_f, title_lines, title_spacing = fit_font(draw, title, x2 - x1, int((y2 - y1) * 0.55), title_size, max(26, title_size // 2), "black", 0.16)
    yy = draw_lines(draw, (x1, y1), title_lines, title_f, title_color, title_spacing, stroke_width=2 if light else 0, stroke_fill=BLACK)
    if subtitle:
        sub_f, sub_lines, sub_spacing = fit_font(draw, subtitle, x2 - x1, y2 - yy, subtitle_size, max(18, subtitle_size // 2), "bold", 0.18)
        draw_lines(draw, (x1, yy + 18), sub_lines, sub_f, sub_color, sub_spacing, stroke_width=1 if light else 0, stroke_fill=BLACK)


def render_offer_card(base_index: dict[str, Path], out: Path, size: tuple[int, int], template_id: str, mode: str) -> None:
    w, h = size
    img = cover(base_index["vivid-packshot"], size, (0.54, 0.48))
    overlay_gradient(img, 154, 150, 14)
    draw = ImageDraw.Draw(img)
    draw_logo(draw, w, h)
    draw_headline_block(
        draw,
        "Monday Hero",
        "Vivid Buffered C\n10% off this week",
        (int(w * 0.07), int(h * 0.18), int(w * 0.72), int(h * 0.44)),
        int(w * 0.075),
        int(w * 0.038),
    )
    badge_r = int(min(w, h) * 0.12)
    cx, cy = int(w * 0.78), int(h * 0.29)
    draw.ellipse((cx - badge_r, cy - badge_r, cx + badge_r, cy + badge_r), fill=GOLD + (244,), outline=CREAM + (230,), width=4)
    f = get_font(max(26, int(w * 0.043)), "black")
    txt = "10%\nOFF"
    lines = txt.splitlines()
    total = sum(text_bbox(draw, line, f)[1] for line in lines) + 6
    yy = cy - total / 2
    for line in lines:
        tw, th = text_bbox(draw, line, f)
        draw.text((cx - tw / 2, yy), line, font=f, fill=DEEP)
        yy += th + 6
    panel_h = max(126, int(h * 0.15))
    rounded_panel(draw, (int(w * 0.07), h - panel_h - int(h * 0.1), int(w * 0.93), h - int(h * 0.1)), fill=CREAM + (230,), outline=GOLD + (180,))
    small = "Price slot: R___  |  Product packshot slot  |  Made in-house story optional"
    sf, lines, spacing = fit_font(draw, small, int(w * 0.78), panel_h - 38, int(w * 0.027), 17, "bold", 0.15)
    draw_lines(draw, (int(w * 0.11), h - panel_h - int(h * 0.1) + 28), lines, sf, DEEP, spacing)
    draw_footer(draw, w, h)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(out, quality=94, subsampling=1)


def render_vivid_day(base_index: dict[str, Path], out: Path, size: tuple[int, int]) -> None:
    w, h = size
    img = cover(base_index["vivid-trio"], size, (0.48, 0.54))
    overlay_gradient(img, 144, 138, 12)
    draw = ImageDraw.Draw(img)
    draw_logo(draw, w, h)
    draw_headline_block(
        draw,
        "Vivid Day",
        "Made in-house.\nBuilt for everyday value.",
        (int(w * 0.07), int(h * 0.18), int(w * 0.75), int(h * 0.44)),
        int(w * 0.08),
        int(w * 0.036),
    )
    y = int(h * 0.61)
    labels = ["Immune Plus", "Buffered C", "Astragalus"]
    for label in labels:
        chip(draw, (int(w * 0.08), y, int(w * 0.48), y + int(h * 0.065)), label, fill=CREAM + (228,), outline=GOLD + (230,), text_fill=DEEP)
        y += int(h * 0.079)
    draw_footer(draw, w, h)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(out, quality=94, subsampling=1)


def render_bundle(base_index: dict[str, Path], out: Path, size: tuple[int, int]) -> None:
    w, h = size
    img = cover(base_index["bundle-stack"], size, (0.5, 0.52))
    overlay_gradient(img, 150, 152, 12)
    draw = ImageDraw.Draw(img)
    draw_logo(draw, w, h)
    draw_headline_block(
        draw,
        "Winter Immunity Stack",
        "2-3 product bundle\nwith per-item price slots",
        (int(w * 0.07), int(h * 0.16), int(w * 0.78), int(h * 0.45)),
        int(w * 0.064),
        int(w * 0.034),
    )
    panel = (int(w * 0.07), int(h * 0.62), int(w * 0.93), int(h * 0.86))
    rounded_panel(draw, panel, fill=CREAM + (230,), outline=GOLD + (185,))
    rows = ["Vivid Immune Plus  R___", "Vivid Buffered C  R___", "Black Seed Oil  R___", "Bundle price  R___"]
    f = get_font(max(20, int(w * 0.028)), "bold")
    yy = panel[1] + int(h * 0.025)
    for row in rows:
        draw.text((panel[0] + 32, yy), row, font=f, fill=DEEP)
        yy += int(h * 0.044)
    draw_footer(draw, w, h)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(out, quality=94, subsampling=1)


def render_proof(base_index: dict[str, Path], out: Path, size: tuple[int, int]) -> None:
    w, h = size
    img = grade_lifestyle(base_index["store-advisor"], size, "green", f"proof-{w}x{h}")
    draw = ImageDraw.Draw(img)
    draw_logo(draw, w, h)
    draw_campaign_ribbon(draw, w, h, "PROOF", "green")
    photo = (int(w * 0.07), int(h * 0.18), int(w * 0.93), int(h * 0.56))
    rounded_panel(draw, photo, fill=(255, 255, 255, 42), outline=CREAM + (180,))
    f = get_font(max(22, int(w * 0.026)), "black")
    placeholder = "REAL STORE / STAFF PHOTO SLOT"
    tw, th = text_bbox(draw, placeholder, f)
    draw.text((photo[0] + (photo[2] - photo[0] - tw) / 2, photo[1] + (photo[3] - photo[1] - th) / 2), placeholder, font=f, fill=CREAM, stroke_width=2, stroke_fill=BLACK)
    panel = (int(w * 0.07), int(h * 0.59), int(w * 0.93), int(h * 0.86))
    rounded_panel(draw, panel, fill=CREAM + (235,), outline=GOLD + (180,))
    quote = "“The team helped me compare the basics without a hard sell.”"
    qf, qlines, qspacing = fit_font(draw, quote, panel[2] - panel[0] - 60, int((panel[3] - panel[1]) * 0.58), int(w * 0.042), 22, "black", 0.16)
    yy = draw_lines(draw, (panel[0] + 30, panel[1] + 28), qlines, qf, DEEP, qspacing)
    stars = "★★★★★"
    sf = get_font(max(24, int(w * 0.038)), "black")
    draw.text((panel[0] + 30, yy + 18), stars, font=sf, fill=GOLD)
    note = "Use only Naadir-supplied real staff/store photos."
    nf = get_font(max(15, int(w * 0.019)), "bold")
    draw.text((panel[0] + 30, panel[3] - 38), note, font=nf, fill=MUTED)
    draw_footer(draw, w, h)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(out, quality=94, subsampling=1)


def render_poll(base_index: dict[str, Path], out: Path, size: tuple[int, int]) -> None:
    w, h = size
    img = grade_lifestyle(base_index["poll-desk"], size, "winter", f"poll-{w}x{h}")
    draw = ImageDraw.Draw(img)
    draw_logo(draw, w, h)
    draw_campaign_ribbon(draw, w, h, "COMMUNITY POLL", "winter")
    draw_headline_block(
        draw,
        "What knocks you flat every winter?",
        "Tell us what you want the team to unpack next.",
        (int(w * 0.07), int(h * 0.18), int(w * 0.92), int(h * 0.46)),
        int(w * 0.062),
        int(w * 0.031),
    )
    y = int(h * 0.58)
    for option in ["Office cold", "School germs", "Running on empty"]:
        chip(draw, (int(w * 0.1), y, int(w * 0.9), y + int(h * 0.07)), option, fill=CREAM + (235,), outline=GOLD + (255,), text_fill=DEEP)
        y += int(h * 0.09)
    draw_footer(draw, w, h)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(out, quality=94, subsampling=1)


def render_vip(base_index: dict[str, Path], out: Path, size: tuple[int, int]) -> None:
    w, h = size
    img = grade_lifestyle(base_index["vip-phone"], size, "green", f"vip-{w}x{h}")
    draw = ImageDraw.Draw(img)
    draw_logo(draw, w, h)
    draw_campaign_ribbon(draw, w, h, "VIP HUB", "green")
    draw_headline_block(
        draw,
        "VIP gets it first",
        "Hub-only first look\nbefore public socials.",
        (int(w * 0.07), int(h * 0.18), int(w * 0.82), int(h * 0.46)),
        int(w * 0.074),
        int(w * 0.036),
    )
    panel = (int(w * 0.08), int(h * 0.64), int(w * 0.92), int(h * 0.84))
    rounded_panel(draw, panel, fill=CREAM + (232,), outline=GOLD + (190,))
    text = "WhatsApp join CTA slot\nReply JOIN or ask in store"
    f, lines, spacing = fit_font(draw, text, panel[2] - panel[0] - 60, panel[3] - panel[1] - 46, int(w * 0.043), 22, "black", 0.18)
    draw_lines(draw, (panel[0] + 30, panel[1] + 28), lines, f, DEEP, spacing)
    draw_footer(draw, w, h)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(out, quality=94, subsampling=1)


def render_gbp(base_index: dict[str, Path], out: Path) -> None:
    w, h = 1200, 900
    img = grade_lifestyle(base_index["store-online"], (w, h), "green", "gbp-offer")
    draw = ImageDraw.Draw(img)
    draw_logo(draw, w, h)
    draw_campaign_ribbon(draw, w, h, "GBP OFFER", "green")
    panel = (int(w * 0.08), int(h * 0.22), int(w * 0.62), int(h * 0.78))
    rounded_panel(draw, panel, fill=CREAM + (236,), outline=GOLD + (190,))
    draw_headline_block(
        draw,
        "Centurion Offer",
        "Store name slot\nOffer slot\nValid date slot",
        (panel[0] + 34, panel[1] + 38, panel[2] - 34, panel[3] - 30),
        58,
        30,
        light=False,
    )
    draw_footer(draw, w, h)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(out, quality=94, subsampling=1)


def render_email_header(base_index: dict[str, Path], out: Path) -> None:
    w, h = 1200, 600
    img = cover(base_index["vivid-packshot"], (w, h), (0.54, 0.5))
    img = cinematic_canvas((w, h), "vivid", "email-header", img)
    draw = ImageDraw.Draw(img)
    draw_logo(draw, w, h)
    draw_campaign_ribbon(draw, w, h, "EMAIL HERO", "vivid")
    draw_headline_block(
        draw,
        "Winter Hero: Buffered C",
        "Single hero image slot for email.\nKeep product list in HTML below.",
        (int(w * 0.07), int(h * 0.24), int(w * 0.68), int(h * 0.68)),
        58,
        28,
    )
    draw_footer(draw, w, h)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(out, quality=94, subsampling=1)


def render_back_stock(base_index: dict[str, Path], out: Path) -> None:
    w, h = 1080, 1080
    img = grade_lifestyle(base_index["back-in-stock"], (w, h), "vivid", "back-stock")
    draw = ImageDraw.Draw(img)
    draw_logo(draw, w, h)
    draw_campaign_ribbon(draw, w, h, "BACK IN STOCK", "vivid")
    draw_headline_block(
        draw,
        "It's back",
        "Product name slot\nRestock alert frame",
        (int(w * 0.07), int(h * 0.19), int(w * 0.78), int(h * 0.46)),
        78,
        33,
    )
    chip(draw, (int(w * 0.56), int(h * 0.64), int(w * 0.91), int(h * 0.74)), "Back in stock", fill=GOLD + (242,), outline=CREAM + (230,), text_fill=DEEP)
    draw_footer(draw, w, h)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(out, quality=94, subsampling=1)


def render_education(base_index: dict[str, Path], out: Path, size: tuple[int, int]) -> None:
    w, h = size
    img = grade_lifestyle(base_index["education-desk"], size, "green", f"education-{w}x{h}")
    draw = ImageDraw.Draw(img)
    draw_logo(draw, w, h)
    draw_campaign_ribbon(draw, w, h, "MYTH BUST", "green")
    panel = (int(w * 0.07), int(h * 0.2), int(w * 0.93), int(h * 0.78))
    rounded_panel(draw, panel, fill=CREAM + (236,), outline=GOLD + (190,))
    draw_headline_block(
        draw,
        "Myth",
        "“All magnesium is the same.”",
        (panel[0] + 36, panel[1] + 34, panel[2] - 36, panel[1] + int((panel[3] - panel[1]) * 0.38)),
        int(w * 0.06),
        int(w * 0.034),
        light=False,
    )
    line_y = panel[1] + int((panel[3] - panel[1]) * 0.46)
    draw.line((panel[0] + 36, line_y, panel[2] - 36, line_y), fill=GOLD + (255,), width=4)
    draw_headline_block(
        draw,
        "Truth",
        "Different forms suit different routines.\nAsk the team which fits yours.",
        (panel[0] + 36, line_y + 32, panel[2] - 36, panel[3] - 32),
        int(w * 0.055),
        int(w * 0.029),
        light=False,
    )
    draw_footer(draw, w, h)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(out, quality=94, subsampling=1)


def render_winter_overlay(out: Path, size: tuple[int, int]) -> None:
    w, h = size
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    band_h = max(18, int(h * 0.024))
    draw.rectangle((0, 0, w, band_h), fill=GOLD + (190,))
    draw.rectangle((0, h - band_h, w, h), fill=GOLD + (190,))
    for i in range(5):
        x = int(w * 0.72) + i * int(w * 0.055)
        y = int(h * 0.08) + i * int(h * 0.018)
        draw.line((x, y, x + int(w * 0.18), y + int(h * 0.09)), fill=CREAM + (160,), width=max(2, int(w * 0.004)))
        draw.line((x + int(w * 0.08), y - int(h * 0.02), x + int(w * 0.12), y + int(h * 0.10)), fill=CREAM + (110,), width=max(1, int(w * 0.002)))
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out)


def render_overlay_preview(base_index: dict[str, Path], overlay: Path, out: Path, size: tuple[int, int]) -> None:
    img = cover(base_index["bundle-stack"], size, (0.5, 0.52))
    overlay_gradient(img, 130, 132, 14)
    img.alpha_composite(Image.open(overlay).convert("RGBA"))
    draw = ImageDraw.Draw(img)
    draw_logo(draw, *size)
    draw_headline_block(
        draw,
        "SA winter frame",
        "Seasonal overlay for T01-T04",
        (int(size[0] * 0.07), int(size[1] * 0.18), int(size[0] * 0.86), int(size[1] * 0.45)),
        int(size[0] * 0.064),
        int(size[0] * 0.034),
    )
    draw_footer(draw, *size)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(out, quality=94, subsampling=1)


def manifest_for(template_id: str, name: str, sizes: list[str], files: list[Path], bases: list[str], notes: list[str], slots: list[str]) -> None:
    path = ROOT / template_id / "sample" / "manifest.json"
    base_images = []
    source_products = []
    for base in bases:
        if base in SHOPIFY_PRODUCTS:
            base_images.append(rel(PACKSHOT_DIR / f"{base}-cutout.png"))
            source_products.append(
                {
                    "id": base,
                    "title": SHOPIFY_PRODUCTS[base]["title"],
                    "price": format_money(SHOPIFY_PRODUCTS[base]["priceCents"], True),
                    "source": SHOPIFY_PRODUCTS[base]["source"],
                    "image": SHOPIFY_PRODUCTS[base]["image"],
                }
            )
        else:
            base_images.append(rel(ASSET_DIR / f"{base}.png"))
    payload = {
        "templateId": template_id,
        "template": name,
        "generatedAt": GENERATED_AT,
        "sizes": sizes,
        "sampleFiles": [rel(file) for file in files],
        "baseLayerPolicy": "Cinematic raster background with deterministic brand/text overlays; public Shopify packshots are composited after local matte extraction and labels are not redrawn.",
        "baseImages": base_images,
        "copySlots": slots,
        "notes": notes,
        "secretScan": "No credentials, tokens, customer data, or account access material included.",
    }
    if source_products:
        payload["sourceProducts"] = source_products
    write_json(path, payload)


def render_samples(base_index: dict[str, Path], packshots: dict[str, Path]) -> None:
    # T01: sample carousels and mirrored production rerenders.
    t01 = ROOT / "T01" / "sample"
    energy = render_carousel_set(
        "2026-06-16_tiktok_energy-carousel",
        "Always tired by 2pm?",
        ENERGY_SLIDES,
        base_index,
        packshots,
        t01 / "energy-carousel",
        REPO / "creative" / "2026-06-16_tiktok_energy-carousel",
    )
    sleep = render_carousel_set(
        "2026-06-20_tiktok_sleep-carousel",
        "Winter sleep falling apart?",
        SLEEP_SLIDES,
        base_index,
        packshots,
        t01 / "sleep-carousel",
        REPO / "creative" / "2026-06-20_tiktok_sleep-carousel",
    )
    manifest_for(
        "T01",
        "Carousel master — 6 slide roles",
        ["1080x1920"],
        [Path(item["file"]) if Path(item["file"]).is_absolute() else REPO / item["file"] for item in energy["slides"] + sleep["slides"]],
        ["energy-desk", "coffee-desk", "supplement-mechanism", "store-advisor", "poll-desk", "store-online", "sleep-3am", "sleep-window", "sleep-mechanism", "sleep-duo", "sleep-poll", "soft-iron", "b12", "glycine", "griffonia"],
        [
            "Includes full sample rerenders for both week-1 carousels.",
            "Production carousel folders were replaced with the same T01 sample render outputs.",
            "Mechanism/proof slides add real public Shopify packshot cutouts where product copy names products.",
            "All slides include the mandatory product disclaimer footer.",
        ],
        ["hook", "pain", "mechanism", "proof", "participation", "cta", "pager", "footer"],
    )

    # T02
    files = []
    cta_variants = {
        "instore": "IN-STORE ONLY • WHILE STOCKS LAST",
        "online": "SHOP ONLINE • FREE DELIVERY OVER R400",
    }
    for label, size in [("square", (1080, 1080)), ("story", (1080, 1920))]:
        for cta_id, cta in cta_variants.items():
            path = ROOT / "T02" / "sample" / f"t02-monday-hero-{label}-{cta_id}.jpg"
            render_monday_hero(packshots, path, size, cta)
            files.append(path)
            if cta_id == "instore":
                legacy_path = ROOT / "T02" / "sample" / f"t02-monday-hero-{label}.jpg"
                shutil.copy2(path, legacy_path)
                files.append(legacy_path)
    manifest_for(
        "T02",
        "Monday Hero offer card",
        ["1080x1080", "1080x1920"],
        files,
        ["buffered-c-90"],
        [
            "Week-1 Monday Hero sample: Vivid Buffered C 90s, 10% off, valid 15-21 Jun 2026.",
            "Live Shopify price checked from public product data: WAS R170.77, NOW R153.69, SAVE R17.08 / 10%.",
            "Includes both CTA variants: in-store and online. Legacy square/story filenames mirror the in-store CTA.",
        ],
        ["product", "offerPercent", "wasPrice", "nowPrice", "saveBadge", "dateRange", "ctaVariant", "disclaimer"],
    )

    # T03
    files = []
    for label, size in [("square", (1080, 1080)), ("story", (1080, 1920))]:
        path = ROOT / "T03" / "sample" / f"t03-vivid-day-{label}.jpg"
        render_vivid_day_cinematic(packshots, path, size)
        files.append(path)
    manifest_for(
        "T03",
        "Vivid Day",
        ["1080x1080", "1080x1920"],
        files,
        ["immune-plus", "buffered-c-90", "astragalus"],
        ["Vivid-branded blue/teal/gold frame with real Shopify packshot trio and in-house story/product slots."],
        ["story", "product1", "product2", "product3", "priceSlots", "cta", "disclaimer"],
    )

    # T04
    files = []
    for label, size in [("square", (1080, 1080)), ("story", (1080, 1920))]:
        path = ROOT / "T04" / "sample" / f"t04-bundle-stack-{label}.jpg"
        render_bundle_cinematic(packshots, path, size)
        files.append(path)
    manifest_for(
        "T04",
        "Bundle/Stack card",
        ["1080x1080", "1080x1920"],
        files,
        ["immune-plus", "buffered-c-90", "black-seed-oil"],
        ["Dark green/copper multi-product pedestal with real Shopify packshots and per-item/bundle price slots."],
        ["bundleName", "itemNames", "itemPrices", "bundlePrice", "dateRange", "cta", "disclaimer"],
    )

    # T05
    files = []
    for label, size in [("square", (1080, 1080)), ("story", (1080, 1920))]:
        path = ROOT / "T05" / "sample" / f"t05-proof-review-{label}.jpg"
        render_proof(base_index, path, size)
        files.append(path)
    manifest_for(
        "T05",
        "Proof/review",
        ["1080x1080", "1080x1920"],
        files,
        ["store-advisor"],
        ["Sample uses a visible real-photo slot. Do not publish with generated people presented as staff."],
        ["photo", "quote", "stars", "store", "cta"],
    )

    # T06
    path = ROOT / "T06" / "sample" / "t06-community-poll-story.jpg"
    render_poll(base_index, path, (1080, 1920))
    manifest_for(
        "T06",
        "Community/poll story",
        ["1080x1920"],
        [path],
        ["poll-desk"],
        ["Question slot plus 2-3 option chips."],
        ["question", "option1", "option2", "option3", "cta"],
    )

    # T07
    files = []
    for label, size in [("square", (1080, 1080)), ("story", (1080, 1920))]:
        path = ROOT / "T07" / "sample" / f"t07-hub-vip-{label}.jpg"
        render_vip(base_index, path, size)
        files.append(path)
    manifest_for(
        "T07",
        "Hub VIP recruit card",
        ["1080x1080", "1080x1920"],
        files,
        ["vip-phone"],
        ["WhatsApp join CTA and first-look mechanic explainer slots."],
        ["headline", "mechanic", "joinCta", "storeNote"],
    )

    # T08
    path = ROOT / "T08" / "sample" / "t08-gbp-offer-post.jpg"
    render_product_alert(
        packshots,
        path,
        (1200, 900),
        "buffered-c-90",
        ("CENTURION", "OFFER SLOT"),
        "GBP OFFER",
        "green",
        "SHOP ONLINE • FREE DELIVERY OVER R400",
    )
    manifest_for(
        "T08",
        "GBP offer post",
        ["1200x900"],
        [path],
        ["buffered-c-90"],
        ["Per-store variant slots for Google Business Profile posts, rendered in the cinematic product-offer style."],
        ["storeName", "offer", "validDates", "product", "cta", "disclaimer"],
    )

    # T09
    path = ROOT / "T09" / "sample" / "t09-email-hero-header.jpg"
    render_email_hero_cinematic(packshots, path)
    manifest_for(
        "T09",
        "Email hero header",
        ["1200x600"],
        [path],
        ["buffered-c-90"],
        ["Monday Hero email header using the live Shopify Vivid Buffered C 90s packshot and 10% offer math."],
        ["headline", "subhead", "product", "wasPrice", "nowPrice", "ctaContext", "disclaimer"],
    )

    # T10
    path = ROOT / "T10" / "sample" / "t10-back-in-stock-alert.jpg"
    render_product_alert(
        packshots,
        path,
        (1080, 1080),
        "griffonia",
        ("IT'S BACK", "GRIFFONIA"),
        "BACK IN STOCK",
        "vivid",
        "IN-STORE ONLY • WHILE STOCKS LAST",
    )
    manifest_for(
        "T10",
        "Back-in-stock alert",
        ["1080x1080"],
        [path],
        ["griffonia"],
        ["Product plus 'it's back' frame with real Shopify packshot and blue Vivid Wednesday styling."],
        ["product", "restockLine", "cta", "disclaimer"],
    )

    # T11
    files = []
    for label, size in [("square", (1080, 1080)), ("story", (1080, 1920))]:
        path = ROOT / "T11" / "sample" / f"t11-education-myth-bust-{label}.jpg"
        render_education(base_index, path, size)
        files.append(path)
    manifest_for(
        "T11",
        "Education quote/myth-bust card",
        ["1080x1080", "1080x1920"],
        files,
        ["education-desk"],
        ["Text-led education layout for FB/IG posts."],
        ["myth", "truth", "sourceNote", "cta"],
    )

    # T12
    story = ROOT / "T12" / "sample" / "t12-sa-winter-story-overlay.png"
    square = ROOT / "T12" / "sample" / "t12-sa-winter-square-overlay.png"
    preview = ROOT / "T12" / "sample" / "t12-sa-winter-preview.jpg"
    render_winter_overlay(story, (1080, 1920))
    render_winter_overlay(square, (1080, 1080))
    render_overlay_preview(base_index, story, preview, (1080, 1920))
    manifest_for(
        "T12",
        "Seasonal campaign frame — SA winter",
        ["overlay 1080x1920", "overlay 1080x1080"],
        [story, square, preview],
        ["bundle-stack"],
        ["Transparent seasonal accent layer for T01-T04 plus a rendered preview."],
        ["season", "accentColor", "overlayOpacity"],
    )

    write_library_readme()
    write_caption_and_package_updates()


def write_caption_and_package_updates() -> None:
    packages = [
        {
            "dir": REPO / "creative" / "2026-06-16_tiktok_energy-carousel",
            "title": "Always tired by 2pm?",
            "caption": "Coffee #3 is not a strategy. Save this and ask the One Life team about the basics: iron, B12 and your daily routine. Supplements support general health. If symptoms persist, consult your healthcare practitioner.",
        },
        {
            "dir": REPO / "creative" / "2026-06-20_tiktok_sleep-carousel",
            "title": "Winter sleep falling apart?",
            "caption": "Asleep early, awake at 3? Save this for your evening routine. Ask One Life about magnesium and glycine support. Supplements support general health. If symptoms persist, consult your healthcare practitioner.",
        },
    ]
    for pkg in packages:
        out_dir = pkg["dir"]
        write_text(out_dir / "caption.txt", pkg["caption"])
        lines = [
            f"# {pkg['title']}",
            "",
            f"Campaign tag: `{out_dir.name}`",
            "",
            "## Caption",
            "",
            pkg["caption"],
            "",
            "## Posting Files",
            "",
        ]
        for i in range(1, 7):
            lines.append(f"- `{rel(out_dir / 'slides' / f'slide-{i:02d}.jpg')}`")
        lines.extend(
            [
                "",
                "## QA",
                "",
                "- Re-rendered with T01 carousel master.",
                "- Base layer is photorealistic image-model raster imagery, not vector placeholder art.",
                "- Text, logo chip, pager, and footer were composited after generation for crisp typography.",
                "- Health claims kept to the compliance-approved copy from the brief.",
                "- Caption includes the required general-health disclaimer.",
                "- No credentials or account logins are included.",
            ]
        )
        write_text(out_dir / "posting-package.md", "\n".join(lines))


def write_library_readme() -> None:
    readme = f"""# One Life Design System Template Library v1

Generated: {GENERATED_AT}

This library is a sample-review gate for the 12 standing social/email templates in `codex-queue/2026-06-12_design-system-templates.md`.

## Standing Brand Frame

- ICP: women 35-50, upper-class/high-LSM, Gauteng.
- Visual base: cinematic raster backgrounds in the locked reference-ad style: moody botanical set, pedestal staging, gold rim light, particles, shallow-depth grading.
- Product policy: public Shopify packshots are downloaded from One Life product pages/CDN, locally matted, and composited after the background pass. Labels are not AI-redrawn.
- Overlay: logo chip top-left, campaign ribbon top-right, high-contrast condensed display hooks, CTA bar where relevant, store strip, and mandatory disclaimer footer.
- Store strip: `{STORE_STRIP}`.
- Product disclaimer: `{AD_DISCLAIMER}`.
- Avoid: gym-bro aesthetics, US-suburbia stock look, close-up synthetic faces, fake staff photos, and AI-generated text burned into base imagery.

## Template Samples

| ID | Template | Sample folder |
|---|---|---|
| T01 | Carousel master - 6 slide roles | `creative/templates/T01/sample/` |
| T02 | Monday Hero offer card | `creative/templates/T02/sample/` |
| T03 | Vivid Day | `creative/templates/T03/sample/` |
| T04 | Bundle/Stack card | `creative/templates/T04/sample/` |
| T05 | Proof/review | `creative/templates/T05/sample/` |
| T06 | Community/poll story | `creative/templates/T06/sample/` |
| T07 | Hub VIP recruit card | `creative/templates/T07/sample/` |
| T08 | GBP offer post | `creative/templates/T08/sample/` |
| T09 | Email hero header | `creative/templates/T09/sample/` |
| T10 | Back-in-stock alert | `creative/templates/T10/sample/` |
| T11 | Education quote/myth-bust card | `creative/templates/T11/sample/` |
| T12 | SA winter seasonal overlay | `creative/templates/T12/sample/` |

## Review Notes

- T01 includes both week-1 carousel rerenders and those same files were copied into the live campaign folders.
- T02 includes Vivid Buffered C 90s, 10% off, valid 15-21 Jun 2026, with both in-store and online CTA variants.
- Live price used for T02: WAS R170.77, NOW R153.69, SAVE R17.08 / 10%, from the public Shopify product data.
- T05 is intentionally marked as a real-photo slot. Do not publish generated people as One Life staff.
- Packshot manifest: `creative/templates/_assets/shopify-packshots/manifest.json`.
- No secrets, credentials, customer fields, or account access artifacts are included.
"""
    write_text(ROOT / "README.md", readme)


def validate_outputs() -> None:
    expected = {
        "T01": [(1080, 1920)] * 12,
        "T02": [(1080, 1080), (1080, 1080), (1080, 1080), (1080, 1920), (1080, 1920), (1080, 1920)],
        "T03": [(1080, 1080), (1080, 1920)],
        "T04": [(1080, 1080), (1080, 1920)],
        "T05": [(1080, 1080), (1080, 1920)],
        "T06": [(1080, 1920)],
        "T07": [(1080, 1080), (1080, 1920)],
        "T08": [(1200, 900)],
        "T09": [(1200, 600)],
        "T10": [(1080, 1080)],
        "T11": [(1080, 1080), (1080, 1920)],
        "T12": [(1080, 1920), (1080, 1080), (1080, 1920)],
    }
    report = {"generatedAt": GENERATED_AT, "items": []}
    for tid, dims in expected.items():
        manifest = json.loads((ROOT / tid / "sample" / "manifest.json").read_text("utf-8"))
        files = [REPO / f for f in manifest["sampleFiles"]]
        if len(files) != len(dims):
            raise AssertionError(f"{tid}: expected {len(dims)} files, found {len(files)}")
        for file, dim in zip(files, dims):
            im = Image.open(file)
            if im.size != dim:
                raise AssertionError(f"{file}: expected {dim}, found {im.size}")
            report["items"].append({"file": rel(file), "size": im.size, "mode": im.mode})
    write_json(ROOT / "validation-report.json", report)


def main() -> None:
    base_index = copy_bases()
    packshots = ensure_packshots()
    render_samples(base_index, packshots)
    validate_outputs()


if __name__ == "__main__":
    main()
