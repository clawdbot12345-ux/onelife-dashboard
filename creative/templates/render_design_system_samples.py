#!/usr/bin/env python3
"""Render One Life design-system template samples.

The image base layers are generated photorealistic raster assets. This script
copies those bases into the repo and composites deterministic brand, text, and
layout overlays for review.
"""

from __future__ import annotations

import json
import shutil
import textwrap
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / "creative" / "templates"
ASSET_DIR = ROOT / "_assets" / "generated-bases"

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
GENERATED_AT = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


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
    margin = max(28, int(w * 0.045))
    chip_w = max(205, int(w * 0.28))
    chip_h = max(58, int(chip_w * 0.25))
    radius = max(12, int(chip_h * 0.28))
    x1, y1 = margin, margin
    draw.rounded_rectangle((x1, y1, x1 + chip_w, y1 + chip_h), radius=radius, fill=DEEP + (244,), outline=GOLD + (210,), width=max(2, int(w * 0.002)))
    f1 = get_font(max(22, int(chip_h * 0.42)), "black")
    f2 = get_font(max(10, int(chip_h * 0.18)), "bold")
    draw.text((x1 + int(chip_w * 0.09), y1 + int(chip_h * 0.15)), "ONE LIFE", font=f1, fill=CREAM)
    draw.text((x1 + int(chip_w * 0.095), y1 + int(chip_h * 0.63)), "HEALTH STORE", font=f2, fill=(165, 218, 166))


def draw_footer(draw: ImageDraw.ImageDraw, w: int, h: int) -> None:
    footer_h = max(68, int(h * 0.067))
    y = h - footer_h
    draw.rectangle((0, y, w, h), fill=DEEP + (244,))
    draw.rectangle((0, y, w, y + max(4, int(h * 0.004))), fill=GOLD + (255,))
    fnt, lines, spacing = fit_font(draw, STORE_STRIP, int(w * 0.88), footer_h - 18, max(18, int(w * 0.025)), 14, "bold", 0.16)
    total_h = sum(text_bbox(draw, line, fnt)[1] for line in lines) + spacing * max(0, len(lines) - 1)
    yy = y + (footer_h - total_h) // 2
    for line in lines:
        tw, th = text_bbox(draw, line, fnt)
        draw.text(((w - tw) / 2, yy), line, font=fnt, fill=CREAM)
        yy += th + spacing


def draw_pager(draw: ImageDraw.ImageDraw, w: int, index: int, total: int) -> None:
    pill_w, pill_h = int(w * 0.15), 60
    x1, y1 = w - pill_w - 58, 58
    draw.rounded_rectangle((x1, y1, x1 + pill_w, y1 + pill_h), radius=18, fill=CREAM + (234,))
    text = f"{index}/{total}"
    fnt = get_font(28, "black")
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


def render_carousel_slide(slide: CarouselSlide, base_index: dict[str, Path], out_path: Path, index: int, total: int) -> None:
    w, h = 1080, 1920
    img = cover(base_index[slide.base], (w, h), (0.5, 0.5))
    overlay_gradient(img, 162, 148, 18)
    draw = ImageDraw.Draw(img)
    draw_logo(draw, w, h)
    draw_pager(draw, w, index, total)

    title_max_h = 260
    title_f, title_lines, title_spacing = fit_font(draw, slide.title, 900, title_max_h, 84, 52, "black", 0.18)
    draw_lines(draw, (68, 205), title_lines, title_f, CREAM, title_spacing, stroke_width=3, stroke_fill=BLACK)

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
        rounded_panel(draw, (panel_x, panel_y, panel_x + panel_w, panel_y + panel_h), fill=(9, 46, 31, 214), outline=GOLD + (170,))
        body_f, body_lines, body_spacing = fit_font(draw, slide.body, panel_w - 72, panel_h - 70, 44, 28, "bold", 0.2)
        draw_lines(draw, (panel_x + 36, panel_y + 34), body_lines, body_f, CREAM, body_spacing)
        if slide.diagram:
            draw_diagram(draw, w, panel_y + panel_h + 72, slide.diagram)

    draw_footer(draw, w, h)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(out_path, quality=94, subsampling=1)


def render_carousel_set(
    campaign_tag: str,
    title: str,
    slides: list[CarouselSlide],
    base_index: dict[str, Path],
    out_dir: Path,
    mirror_out_dir: Path | None = None,
) -> dict:
    slide_dir = out_dir / "slides"
    rendered = []
    for i, slide in enumerate(slides, 1):
        path = slide_dir / f"slide-{i:02d}.jpg"
        render_carousel_slide(slide, base_index, path, i, len(slides))
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
    img = cover(base_index["store-advisor"], size, (0.5, 0.5))
    overlay_gradient(img, 122, 154, 18)
    draw = ImageDraw.Draw(img)
    draw_logo(draw, w, h)
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
    img = cover(base_index["poll-desk"], size, (0.5, 0.52))
    overlay_gradient(img, 150, 140, 14)
    draw = ImageDraw.Draw(img)
    draw_logo(draw, w, h)
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
    img = cover(base_index["vip-phone"], size, (0.5, 0.54))
    overlay_gradient(img, 156, 144, 12)
    draw = ImageDraw.Draw(img)
    draw_logo(draw, w, h)
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
    img = cover(base_index["store-online"], (w, h), (0.52, 0.52))
    overlay_gradient(img, 120, 128, 12)
    draw = ImageDraw.Draw(img)
    draw_logo(draw, w, h)
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
    overlay_gradient(img, 118, 126, 10)
    draw = ImageDraw.Draw(img)
    draw_logo(draw, w, h)
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
    img = cover(base_index["back-in-stock"], (w, h), (0.52, 0.52))
    overlay_gradient(img, 142, 144, 8)
    draw = ImageDraw.Draw(img)
    draw_logo(draw, w, h)
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
    img = cover(base_index["education-desk"], size, (0.5, 0.52))
    overlay_gradient(img, 132, 138, 10)
    draw = ImageDraw.Draw(img)
    draw_logo(draw, w, h)
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
    payload = {
        "templateId": template_id,
        "template": name,
        "generatedAt": GENERATED_AT,
        "sizes": sizes,
        "sampleFiles": [rel(file) for file in files],
        "baseLayerPolicy": "Image-model photorealistic raster base; deterministic text/logo/footer overlay.",
        "baseImages": [rel(ASSET_DIR / f"{base}.png") for base in bases],
        "copySlots": slots,
        "notes": notes,
        "secretScan": "No credentials, tokens, customer data, or account access material included.",
    }
    write_json(path, payload)


def render_samples(base_index: dict[str, Path]) -> None:
    # T01: sample carousels and mirrored production rerenders.
    t01 = ROOT / "T01" / "sample"
    energy = render_carousel_set(
        "2026-06-16_tiktok_energy-carousel",
        "Always tired by 2pm?",
        ENERGY_SLIDES,
        base_index,
        t01 / "energy-carousel",
        REPO / "creative" / "2026-06-16_tiktok_energy-carousel",
    )
    sleep = render_carousel_set(
        "2026-06-20_tiktok_sleep-carousel",
        "Winter sleep falling apart?",
        SLEEP_SLIDES,
        base_index,
        t01 / "sleep-carousel",
        REPO / "creative" / "2026-06-20_tiktok_sleep-carousel",
    )
    manifest_for(
        "T01",
        "Carousel master — 6 slide roles",
        ["1080x1920"],
        [Path(item["file"]) if Path(item["file"]).is_absolute() else REPO / item["file"] for item in energy["slides"] + sleep["slides"]],
        ["energy-desk", "coffee-desk", "supplement-mechanism", "store-advisor", "poll-desk", "store-online", "sleep-3am", "sleep-window", "sleep-mechanism", "sleep-duo", "sleep-poll"],
        [
            "Includes full sample rerenders for both week-1 carousels.",
            "Production carousel folders were replaced with the same T01 sample render outputs.",
            "Mechanism slides use clean diagram overlays on photographic backdrops.",
        ],
        ["hook", "pain", "mechanism", "proof", "participation", "cta", "pager", "footer"],
    )

    # T02
    files = []
    for label, size in [("square", (1080, 1080)), ("story", (1080, 1920))]:
        path = ROOT / "T02" / "sample" / f"t02-monday-hero-{label}.jpg"
        render_offer_card(base_index, path, size, "T02", label)
        files.append(path)
    manifest_for(
        "T02",
        "Monday Hero offer card",
        ["1080x1080", "1080x1920"],
        files,
        ["vivid-packshot"],
        ["Uses generated blank-label packshot as sample-only; replace with approved product packshot when available."],
        ["product", "offerPercent", "price", "dateRange", "cta"],
    )

    # T03
    files = []
    for label, size in [("square", (1080, 1080)), ("story", (1080, 1920))]:
        path = ROOT / "T03" / "sample" / f"t03-vivid-day-{label}.jpg"
        render_vivid_day(base_index, path, size)
        files.append(path)
    manifest_for(
        "T03",
        "Vivid Day",
        ["1080x1080", "1080x1920"],
        files,
        ["vivid-trio"],
        ["Vivid-branded frame with in-house story and product trio slots."],
        ["story", "product1", "product2", "product3", "cta"],
    )

    # T04
    files = []
    for label, size in [("square", (1080, 1080)), ("story", (1080, 1920))]:
        path = ROOT / "T04" / "sample" / f"t04-bundle-stack-{label}.jpg"
        render_bundle(base_index, path, size)
        files.append(path)
    manifest_for(
        "T04",
        "Bundle/Stack card",
        ["1080x1080", "1080x1920"],
        files,
        ["bundle-stack"],
        ["2-3 product stack layout with per-item and bundle-price slots."],
        ["bundleName", "itemNames", "itemPrices", "bundlePrice", "dateRange"],
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
    render_gbp(base_index, path)
    manifest_for(
        "T08",
        "GBP offer post",
        ["1200x900"],
        [path],
        ["store-online"],
        ["Per-store variant slots for Google Business Profile posts."],
        ["storeName", "offer", "validDates", "cta"],
    )

    # T09
    path = ROOT / "T09" / "sample" / "t09-email-hero-header.jpg"
    render_email_header(base_index, path)
    manifest_for(
        "T09",
        "Email hero header",
        ["1200x600"],
        [path],
        ["vivid-packshot"],
        ["One hero image only; body/product list remains in email HTML per existing email design system."],
        ["headline", "subhead", "product", "ctaContext"],
    )

    # T10
    path = ROOT / "T10" / "sample" / "t10-back-in-stock-alert.jpg"
    render_back_stock(base_index, path)
    manifest_for(
        "T10",
        "Back-in-stock alert",
        ["1080x1080"],
        [path],
        ["back-in-stock"],
        ["Product plus 'it's back' frame."],
        ["product", "restockLine", "cta"],
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
- Visual base: photorealistic image-model raster, warm premium South African contexts.
- Overlay: logo chip top-left, high-contrast bold sans hooks, pager where relevant, and the store-strip footer.
- Footer text: `{STORE_STRIP}`.
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
- T05 is intentionally marked as a real-photo slot. Do not publish generated people as One Life staff.
- Product imagery in this sample set is generated blank-label packshot-style art for template approval only. Replace with approved real packshots when publishing product-specific offers.
- No secrets, credentials, customer fields, or account access artifacts are included.
"""
    write_text(ROOT / "README.md", readme)


def validate_outputs() -> None:
    expected = {
        "T01": [(1080, 1920)] * 12,
        "T02": [(1080, 1080), (1080, 1920)],
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
    render_samples(base_index)
    validate_outputs()


if __name__ == "__main__":
    main()
