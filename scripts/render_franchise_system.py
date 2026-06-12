#!/usr/bin/env python3
"""Render One Life franchise creative from the decided Hybrid direction.

Outputs are intentionally local, deterministic composites:
- Light Editorial uses approved local raster/photo base plates plus crisp text overlays.
- Hub offer mode uses the approved dark cinematic world and real Shopify packshots.
"""

from __future__ import annotations

import json
import math
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont


REPO = Path(__file__).resolve().parents[1]
OUT = REPO / "creative" / "franchises"
BASE = REPO / "creative" / "templates" / "_assets" / "generated-bases"
PACK = REPO / "creative" / "templates" / "_assets" / "shopify-packshots"
EXISTING = REPO / "creative" / "templates" / "existing"
ARCHIVE = REPO / "creative" / "archive"

STORY = (1080, 1920)
SQUARE = (1080, 1080)
CREAM = (248, 243, 232)
WARM = (236, 224, 204)
INK = (29, 42, 34)
MUTED = (92, 95, 84)
GREEN = (22, 91, 54)
GREEN_2 = (83, 145, 77)
GOLD = (190, 145, 63)
PINK = (153, 87, 110)
BLACK = (8, 14, 11)
WHITE = (255, 255, 255)


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


GENERATED_AT = now_iso()


def rel(path: Path) -> str:
    return str(path.relative_to(REPO))


def write_json(path: Path, data: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", "utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", "utf-8")


def font(size: int, weight: str = "regular") -> ImageFont.FreeTypeFont:
    candidates = {
        "black": [
            "/System/Library/Fonts/Supplemental/Arial Black.ttf",
            "/System/Library/Fonts/Supplemental/Avenir Next Condensed.ttc",
        ],
        "bold": [
            "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
            "/System/Library/Fonts/Supplemental/Avenir Next.ttc",
        ],
        "regular": [
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/System/Library/Fonts/Supplemental/Avenir Next.ttc",
        ],
    }
    for candidate in candidates.get(weight, candidates["regular"]):
        if candidate and Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def text_box(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.ImageFont) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0], box[3] - box[1]


def wrap(draw: ImageDraw.ImageDraw, text: str, fnt: ImageFont.ImageFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    line = ""
    for word in words:
        trial = word if not line else f"{line} {word}"
        if text_box(draw, trial, fnt)[0] <= max_width:
            line = trial
        else:
            if line:
                lines.append(line)
            line = word
    if line:
        lines.append(line)
    return lines


def fit_lines(
    draw: ImageDraw.ImageDraw,
    text: str,
    max_width: int,
    max_height: int,
    start: int,
    minimum: int,
    weight: str,
    spacing_ratio: float = 0.18,
) -> tuple[ImageFont.ImageFont, list[str], int]:
    for size in range(start, minimum - 1, -2):
        fnt = font(size, weight)
        lines = wrap(draw, text, fnt, max_width)
        spacing = max(6, int(size * spacing_ratio))
        height = sum(text_box(draw, line, fnt)[1] for line in lines) + spacing * max(0, len(lines) - 1)
        if height <= max_height:
            return fnt, lines, spacing
    fnt = font(minimum, weight)
    return fnt, wrap(draw, text, fnt, max_width), max(5, int(minimum * spacing_ratio))


def draw_lines(
    draw: ImageDraw.ImageDraw,
    xy: tuple[int, int],
    lines: list[str],
    fnt: ImageFont.ImageFont,
    fill: tuple[int, int, int],
    spacing: int,
    align: str = "left",
    max_width: int | None = None,
) -> int:
    x, y = xy
    for line in lines:
        tw, th = text_box(draw, line, fnt)
        tx = x
        if align == "center" and max_width is not None:
            tx = x + (max_width - tw) // 2
        draw.text((tx, y), line, font=fnt, fill=fill)
        y += th + spacing
    return y


def cover(path: Path, size: tuple[int, int]) -> Image.Image:
    img = Image.open(path).convert("RGB")
    sw, sh = size
    scale = max(sw / img.width, sh / img.height)
    new = img.resize((math.ceil(img.width * scale), math.ceil(img.height * scale)), Image.Resampling.LANCZOS)
    left = (new.width - sw) // 2
    top = (new.height - sh) // 2
    return new.crop((left, top, left + sw, top + sh)).convert("RGBA")


def grade_light(path: Path, size: tuple[int, int], soften: bool = False) -> Image.Image:
    img = cover(path, size)
    if soften:
        img = img.filter(ImageFilter.GaussianBlur(1.4))
    img = ImageEnhance.Color(img).enhance(0.86)
    img = ImageEnhance.Brightness(img).enhance(1.06)
    veil = Image.new("RGBA", size, (248, 243, 232, 104))
    img.alpha_composite(veil)
    return img


def grade_dark(path: Path, size: tuple[int, int]) -> Image.Image:
    img = cover(path, size)
    img = ImageEnhance.Color(img).enhance(0.95)
    img = ImageEnhance.Brightness(img).enhance(0.72)
    shade = Image.new("RGBA", size, (0, 0, 0, 74))
    img.alpha_composite(shade)
    return img


def rounded(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], radius: int, fill, outline=None, width: int = 1) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def logo(draw: ImageDraw.ImageDraw, x: int, y: int, dark: bool = False) -> None:
    fill = (255, 255, 255, 226) if not dark else (8, 26, 18, 226)
    outline = (40, 119, 70, 220)
    rounded(draw, (x, y, x + 278, y + 78), 20, fill, outline, 2)
    draw.ellipse((x + 22, y + 18, x + 56, y + 52), outline=(152, 84, 164), width=4)
    draw.line((x + 30, y + 50, x + 55, y + 20), fill=GREEN_2, width=5)
    draw.text((x + 72, y + 16), "ONE LIFE", font=font(25, "black"), fill=GREEN if not dark else CREAM)
    draw.text((x + 72, y + 45), "HEALTH STORE", font=font(14, "bold"), fill=GREEN_2)


def footer(draw: ImageDraw.ImageDraw, w: int, h: int, dark: bool = False) -> None:
    fill = (255, 255, 255, 218) if not dark else (8, 20, 14, 226)
    txt = GREEN if not dark else CREAM
    rounded(draw, (52, h - 112, w - 52, h - 38), 22, fill, (191, 164, 96, 180), 2)
    line = "Centurion  |  Glen Village  |  Edenvale  |  onelife.co.za"
    fnt = font(25, "bold")
    tw, th = text_box(draw, line, fnt)
    draw.text(((w - tw) // 2, h - 90), line, font=fnt, fill=txt)
    disc = "*Supplements support general health. If symptoms persist, consult your healthcare practitioner."
    sf = font(15)
    sw, _ = text_box(draw, disc, sf)
    draw.text(((w - sw) // 2, h - 58), disc, font=sf, fill=(95, 101, 87) if not dark else (211, 202, 179))


def editorial_card(
    size: tuple[int, int],
    base: Path,
    eyebrow: str,
    title: str,
    body: str,
    role: str = "",
    slide: str = "",
    products: list[str] | None = None,
    options: list[str] | None = None,
    diagram: list[str] | None = None,
    accent: tuple[int, int, int] = GREEN,
) -> Image.Image:
    w, h = size
    img = grade_light(base, size)
    draw = ImageDraw.Draw(img, "RGBA")
    logo(draw, 58, 52)
    if slide:
        rounded(draw, (w - 178, 58, w - 58, 116), 18, (255, 255, 255, 224), accent + (190,), 2)
        pf = font(25, "black")
        tw, _ = text_box(draw, slide, pf)
        draw.text((w - 118 - tw // 2, 75), slide, font=pf, fill=accent)
    if role:
        rounded(draw, (58, 150, 58 + min(520, max(260, len(role) * 15)), 204), 16, (255, 255, 255, 230), accent + (160,), 2)
        draw.text((82, 164), role.upper(), font=font(20, "black"), fill=accent)

    panel_h = 610 if h > w else 520
    panel = (58, 230 if h > w else 168, w - 58, 230 + panel_h if h > w else 168 + panel_h)
    rounded(draw, panel, 34, (255, 255, 255, 224), (255, 255, 255, 160), 2)
    x1, y1, x2, y2 = panel
    draw.text((x1 + 38, y1 + 34), eyebrow.upper(), font=font(24, "black"), fill=accent)
    title_f, title_lines, title_spacing = fit_lines(draw, title, x2 - x1 - 76, 235 if h > w else 180, 73 if h > w else 56, 38, "black", 0.11)
    end = draw_lines(draw, (x1 + 38, y1 + 78), title_lines, title_f, INK, title_spacing)
    body_f, body_lines, body_spacing = fit_lines(draw, body, x2 - x1 - 76, y2 - end - 38, 36 if h > w else 30, 23, "bold", 0.18)
    draw_lines(draw, (x1 + 38, end + 28), body_lines, body_f, MUTED, body_spacing)

    if diagram:
        draw_diagram(draw, (96, panel[3] + 58, w - 96, panel[3] + 178), diagram, accent)
    if options:
        y = panel[3] + 52
        for opt in options:
            rounded(draw, (96, y, w - 96, y + 94), 28, (255, 255, 255, 232), accent + (180,), 2)
            draw.ellipse((130, y + 31, 162, y + 63), outline=accent + (220,), width=4)
            draw.text((190, y + 28), opt, font=font(30, "bold"), fill=INK)
            y += 120

    if products:
        draw_product_cluster(img, products, (w // 2, int(h * 0.73)), int(h * 0.19), accent)

    footer(draw, w, h)
    return img


def draw_diagram(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], labels: list[str], accent: tuple[int, int, int]) -> None:
    x1, y1, x2, y2 = box
    count = len(labels)
    gap = 22
    bw = (x2 - x1 - gap * (count - 1)) // count
    for i, label in enumerate(labels):
        bx1 = x1 + i * (bw + gap)
        rounded(draw, (bx1, y1, bx1 + bw, y2), 24, (255, 255, 255, 230), accent + (170,), 2)
        fnt, lines, spacing = fit_lines(draw, label, bw - 30, y2 - y1 - 28, 28, 17, "bold", 0.05)
        total_h = sum(text_box(draw, ln, fnt)[1] for ln in lines) + spacing * max(0, len(lines) - 1)
        draw_lines(draw, (bx1 + 15, y1 + (y2 - y1 - total_h) // 2), lines, fnt, INK, spacing, "center", bw - 30)


def product_image(product_id: str) -> Image.Image:
    path = PACK / f"{product_id}-cutout.png"
    return Image.open(path).convert("RGBA")


def draw_product_cluster(img: Image.Image, ids: list[str], center: tuple[int, int], height: int, accent: tuple[int, int, int]) -> None:
    draw = ImageDraw.Draw(img, "RGBA")
    cx, cy = center
    width = min(820, 230 * len(ids) + 90)
    rounded(draw, (cx - width // 2, cy + height // 2 - 42, cx + width // 2, cy + height // 2 + 34), 50, (255, 255, 255, 170), accent + (110,), 1)
    spacing = 170 if len(ids) > 2 else 210
    start = cx - spacing * (len(ids) - 1) // 2
    for i, pid in enumerate(ids):
        p = product_image(pid)
        ratio = height / p.height
        p = p.resize((int(p.width * ratio), height), Image.Resampling.LANCZOS)
        x = start + i * spacing - p.width // 2
        y = cy - p.height // 2
        shadow = Image.new("RGBA", p.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(shadow)
        sd.ellipse((15, p.height - 45, p.width - 15, p.height - 8), fill=(0, 0, 0, 70))
        img.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(8)), (x + 8, y + 16))
        img.alpha_composite(p, (x, y))


@dataclass(frozen=True)
class CarouselSlide:
    role: str
    base: Path
    eyebrow: str
    title: str
    body: str
    products: list[str] | None = None
    options: list[str] | None = None
    diagram: list[str] | None = None
    accent: tuple[int, int, int] = GREEN


ENERGY = [
    CarouselSlide("Hook", BASE / "energy-desk.png", "Symptom Saturday", "Always tired by 2pm?", 'It\'s not just "winter laziness".'),
    CarouselSlide("Pain", BASE / "coffee-desk.png", "Symptom Saturday", "Coffee #3 isn't working.", "The afternoon slump is running your diary."),
    CarouselSlide("Mechanism", BASE / "supplement-mechanism.png", "Symptom Saturday", "Low iron and B12", "Two common reasons women feel flat: they carry oxygen and power your cells' energy production.", diagram=["Iron", "B12", "Oxygen + cell energy support"]),
    CarouselSlide("Proof", BASE / "store-advisor.png", "Symptom Saturday", "Check the basics first.", "Gentle iron and B12 support, matched to you in store.", products=["soft-iron", "b12"]),
    CarouselSlide("Participation", BASE / "poll-desk.png", "Symptom Saturday", "Which one's you?", "Tell us below.", options=["2pm slump", "wake up tired", "coffee dependent"]),
    CarouselSlide("CTA", BASE / "store-online.png", "Symptom Saturday", "Talk to the team.", "Centurion, Glen Village or Edenvale — or onelife.co.za. Free delivery over R400.", products=["soft-iron", "b12"]),
]

SLEEP = [
    CarouselSlide("Hook", BASE / "sleep-3am.png", "Symptom Saturday", "Winter sleep falling apart?", "Asleep at 9, wide awake at 3.", accent=PINK),
    CarouselSlide("Pain", BASE / "sleep-window.png", "Symptom Saturday", "Short days scramble your rhythm.", "The 3am wake-up becomes a habit.", accent=PINK),
    CarouselSlide("Mechanism", BASE / "sleep-mechanism.png", "Symptom Saturday", "Evening wind-down basics", "Magnesium contributes to normal nervous-system function; glycine is the calming amino acid your body uses as evening winds down.", diagram=["Magnesium", "Glycine", "Evening support"], accent=PINK),
    CarouselSlide("Proof", BASE / "sleep-duo.png", "Symptom Saturday", "Customer favourites", "PrimeSelf Magnesium Complex and Good Life Glycine — ask the team which fits your evening routine.", products=["primeself-magnesium", "glycine"], accent=PINK),
    CarouselSlide("Participation", BASE / "sleep-poll.png", "Symptom Saturday", "What's your 3am brain doing?", "", options=["replaying today", "planning tomorrow", "just awake"], accent=PINK),
    CarouselSlide("CTA", BASE / "store-online.png", "Symptom Saturday", "In store or online.", "Centurion, Glen Village & Edenvale — or onelife.co.za, free delivery over R400.", products=["glycine"], accent=PINK),
]


def render_carousel(slides: list[CarouselSlide], out_dir: Path, title: str, caption: str) -> None:
    slide_dir = out_dir / "slides"
    files = []
    for idx, slide in enumerate(slides, 1):
        img = editorial_card(
            STORY,
            slide.base,
            slide.eyebrow,
            slide.title,
            slide.body,
            role=slide.role,
            slide=f"{idx}/6",
            products=slide.products,
            options=slide.options,
            diagram=slide.diagram,
            accent=slide.accent,
        )
        path = slide_dir / f"slide-{idx:02d}.jpg"
        path.parent.mkdir(parents=True, exist_ok=True)
        img.convert("RGB").save(path, quality=94, subsampling=1)
        files.append(path)
    manifest = {
        "title": title,
        "franchise": "Symptom Saturday",
        "generatedAt": GENERATED_AT,
        "direction": "One Life Hybrid / Light Editorial",
        "dimensions": {"width": STORY[0], "height": STORY[1]},
        "slides": [
            {
                "index": i + 1,
                "role": slide.role,
                "copy": f"{slide.title} {slide.body}".strip(),
                "baseImage": rel(slide.base),
                "file": rel(files[i]),
            }
            for i, slide in enumerate(slides)
        ],
        "captionDisclaimer": "Supplements support general health. If symptoms persist, consult your healthcare practitioner.",
    }
    write_json(out_dir / "manifest.json", manifest)
    write_text(out_dir / "caption.txt", caption)
    write_contact_sheet(out_dir / "contact-sheet.jpg", files, title)


HONEST_COPY = [
    'THE HONEST LABEL · Ep 1: Collagen — "Everyone\'s taking it. Should you?"',
    'What you\'ve heard: "erases wrinkles, fixes joints, full stop."',
    "What it can support: skin elasticity and normal joint cartilage function get support from consistent daily collagen with vitamin C.*",
    "What it won't do: replace sleep, sunscreen or strength training — and results take 8–12 weeks, not days.",
    "Is it for you? Best fit: 35+, consistent for 3 months, paired with vitamin C. Ask the team to match the right type.",
    "CTA: The honest answer is always free — in store at Centurion, Glen Village & Edenvale · onelife.co.za",
]


def render_honest_label() -> None:
    out = OUT / "the-honest-label"
    ep = out / "ep-01-collagen"
    bases = [
        EXISTING / "template-library-10" / "template-06-practitioner-counter.png",
        EXISTING / "template-library-10" / "template-01-morning-digestive-ritual.png",
        EXISTING / "imagegen-improve10x-reference-run" / "option-05-mobility-duo.png",
        BASE / "education-desk.png",
        EXISTING / "template-library-10" / "template-10-luxury-botanical-apothecary.png",
        BASE / "store-advisor.png",
    ]
    files = []
    roles = ["Masthead", "Claim", "Evidence", "Honest limits", "Best fit", "CTA"]
    for idx, copy in enumerate(HONEST_COPY, 1):
        if idx == 1:
            title = "THE HONEST LABEL"
            body = "Ep 1: Collagen — \"Everyone's taking it. Should you?\""
        elif idx == 6:
            title = "The honest answer is always free"
            body = "In store at Centurion, Glen Village & Edenvale · onelife.co.za"
        else:
            title, body = copy.split(": ", 1)
        img = editorial_card(STORY, bases[idx - 1], "The Honest Label", title, body, role=roles[idx - 1], slide=f"{idx}/6", accent=GREEN)
        path = ep / "slides" / f"slide-{idx:02d}.jpg"
        path.parent.mkdir(parents=True, exist_ok=True)
        img.convert("RGB").save(path, quality=94, subsampling=1)
        files.append(path)

    identity = editorial_card(SQUARE, EXISTING / "template-library-10" / "template-06-practitioner-counter.png", "Franchise identity", "THE HONEST LABEL", "Ingredient claims, translated without hype.", role="Tuesday franchise", accent=GREEN)
    identity_path = out / "identity-card.jpg"
    identity_path.parent.mkdir(parents=True, exist_ok=True)
    identity.convert("RGB").save(identity_path, quality=94, subsampling=1)
    write_contact_sheet(ep / "contact-sheet.jpg", files, "THE HONEST LABEL · Ep 1")
    write_json(
        out / "manifest.json",
        {
            "franchise": "THE HONEST LABEL",
            "generatedAt": GENERATED_AT,
            "direction": "One Life Hybrid / Light Editorial",
            "identityCard": rel(identity_path),
            "episode": {
                "title": "Collagen — what it can and can't do",
                "copyPolicy": "Slide copy rendered verbatim from codex-queue/03_2026-06-12_render-the-system.md.",
                "captionDisclaimer": "Supplements support general health. If symptoms persist, consult your healthcare practitioner.",
                "slides": [{"index": i + 1, "copy": HONEST_COPY[i], "file": rel(files[i])} for i in range(6)],
                "contactSheet": rel(ep / "contact-sheet.jpg"),
            },
        },
    )


def render_made_by_us() -> None:
    out = OUT / "made-by-us"
    identity = photo_frame_card(
        SQUARE,
        "MADE BY US",
        "Real people. Real shelves. Real standards.",
        ["FACTORY PHOTO", "STAFF PHOTO"],
        "Use this when the team has a real factory, shelf or staff image to anchor the story.",
    )
    story = photo_frame_card(
        STORY,
        "MADE BY US",
        "Behind the counter, not behind a script.",
        ["REAL PHOTO", "DETAIL PHOTO"],
        "Caption block: what we made, checked or packed today, and why it matters for customers.",
    )
    identity_path = out / "made-by-us-identity-card.jpg"
    story_path = out / "made-by-us-story-template.jpg"
    identity_path.parent.mkdir(parents=True, exist_ok=True)
    identity.convert("RGB").save(identity_path, quality=94, subsampling=1)
    story.convert("RGB").save(story_path, quality=94, subsampling=1)
    write_json(out / "manifest.json", {"franchise": "MADE BY US", "generatedAt": GENERATED_AT, "direction": "One Life Hybrid / Light Editorial", "files": [rel(identity_path), rel(story_path)]})


def photo_frame_card(size: tuple[int, int], title: str, subtitle: str, labels: list[str], caption: str) -> Image.Image:
    w, h = size
    img = grade_light(BASE / "store-advisor.png", size, True)
    draw = ImageDraw.Draw(img, "RGBA")
    logo(draw, 56, 52)
    panel = (56, 164, w - 56, h - 54)
    rounded(draw, panel, 38, (255, 255, 255, 226), (255, 255, 255, 150), 2)
    x1, y1, x2, y2 = panel
    draw.text((x1 + 42, y1 + 42), title, font=font(66 if h > w else 54, "black"), fill=GREEN)
    draw.text((x1 + 44, y1 + 120 if h > w else y1 + 104), subtitle, font=font(30 if h > w else 25, "bold"), fill=MUTED)
    frame_top = y1 + (210 if h > w else 174)
    frame_h = 470 if h > w else 330
    gap = 24
    frame_w = (x2 - x1 - 84 - gap) // 2
    for i, label in enumerate(labels[:2]):
        fx1 = x1 + 42 + i * (frame_w + gap)
        fy1 = frame_top
        rounded(draw, (fx1, fy1, fx1 + frame_w, fy1 + frame_h), 24, (239, 232, 216, 220), GOLD + (170,), 2)
        draw.line((fx1 + 28, fy1 + 34, fx1 + frame_w - 28, fy1 + frame_h - 34), fill=(196, 184, 160, 130), width=3)
        draw.line((fx1 + frame_w - 28, fy1 + 34, fx1 + 28, fy1 + frame_h - 34), fill=(196, 184, 160, 130), width=3)
        lf = font(27 if h > w else 21, "black")
        tw, th = text_box(draw, label, lf)
        draw.text((fx1 + (frame_w - tw) // 2, fy1 + (frame_h - th) // 2), label, font=lf, fill=GREEN)
    cap_y = frame_top + frame_h + 44
    rounded(draw, (x1 + 42, cap_y, x2 - 42, y2 - 42), 28, CREAM + (245,), GREEN + (135,), 2)
    fnt, lines, spacing = fit_lines(draw, caption, x2 - x1 - 132, y2 - cap_y - 82, 32 if h > w else 25, 18, "bold")
    draw_lines(draw, (x1 + 72, cap_y + 38), lines, fnt, INK, spacing)
    return img


def render_stack_of_week() -> None:
    out = OUT / "stack-of-the-week"
    img = grade_light(EXISTING / "template-library-10" / "template-09-performance-recovery-stack.png", SQUARE, True)
    draw = ImageDraw.Draw(img, "RGBA")
    logo(draw, 52, 48)
    rounded(draw, (52, 150, 1028, 1028), 36, (255, 255, 255, 228), (255, 255, 255, 150), 2)
    draw.text((96, 202), "STACK OF THE WEEK", font=font(58, "black"), fill=GREEN)
    draw.text((98, 274), "Real numbers from our stores", font=font(28, "bold"), fill=MUTED)
    stats = [("90D UNITS", "___"), ("GP%", "___"), ("BRANCH STOCK", "C __ · G __ · E __")]
    y = 344
    for label, value in stats:
        rounded(draw, (96, y, 984, y + 96), 24, CREAM + (245,), GOLD + (185,), 2)
        draw.text((128, y + 24), label, font=font(24, "black"), fill=GREEN)
        draw.text((470, y + 22), value, font=font(34, "black"), fill=INK)
        y += 118
    draw_product_cluster(img, ["soft-iron", "b12", "glycine"], (540, 800), 290, GOLD)
    path = out / "stack-of-the-week-data-card-template.jpg"
    path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(path, quality=94, subsampling=1)
    write_json(out / "manifest.json", {"franchise": "STACK OF THE WEEK", "generatedAt": GENERATED_AT, "direction": "One Life Hybrid / Light Editorial", "file": rel(path), "statSlots": ["90d units", "GP%", "branch stock"], "productSlots": 3})


def render_ask_one_life() -> None:
    out = OUT / "ask-one-life"
    img = grade_light(BASE / "store-advisor.png", SQUARE, True)
    draw = ImageDraw.Draw(img, "RGBA")
    logo(draw, 52, 48)
    rounded(draw, (52, 150, 1028, 1028), 36, (255, 255, 255, 229), (255, 255, 255, 150), 2)
    draw.text((96, 206), "ASK ONE LIFE", font=font(60, "black"), fill=GREEN)
    rounded(draw, (96, 298, 984, 472), 28, CREAM + (246,), GOLD + (170,), 2)
    q = '“Can I take this with what I already use?”'
    fnt, lines, spacing = fit_lines(draw, q, 820, 108, 40, 26, "black")
    draw_lines(draw, (130, 334), lines, fnt, INK, spacing)
    rounded(draw, (96, 520, 426, 900), 28, (238, 231, 214, 230), GOLD + (160,), 2)
    draw.line((132, 560, 390, 860), fill=(183, 172, 150, 150), width=3)
    draw.line((390, 560, 132, 860), fill=(183, 172, 150, 150), width=3)
    draw.text((150, 696), "STAFF PHOTO", font=font(27, "black"), fill=GREEN)
    rounded(draw, (456, 520, 984, 900), 28, (255, 255, 255, 218), GREEN + (130,), 2)
    body = "Bring the label in. We’ll check dose, timing and routine fit before you buy."
    bf, blines, bspacing = fit_lines(draw, body, 450, 300, 36, 24, "bold")
    draw_lines(draw, (492, 570), blines, bf, INK, bspacing)
    path = out / "ask-one-life-answer-card-template.jpg"
    path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(path, quality=94, subsampling=1)
    write_json(out / "manifest.json", {"franchise": "ASK ONE LIFE", "generatedAt": GENERATED_AT, "direction": "One Life Hybrid / Light Editorial", "file": rel(path), "slots": ["question quote", "staff answer", "real staff photo"]})


def render_hub_exclusive() -> None:
    out = OUT / "hub-exclusive"
    files = []
    for size, suffix in [(SQUARE, "square"), (STORY, "story")]:
        w, h = size
        img = grade_dark(ARCHIVE / "2026-07" / "01-approved-images" / "2026-07-02-zinc-nac-defence-bundle.png", size)
        draw = ImageDraw.Draw(img, "RGBA")
        logo(draw, 54, 52, dark=True)
        rounded(draw, (w - 378, 58, w - 54, 118), 20, (8, 14, 11, 226), GOLD + (230,), 2)
        draw.text((w - 342, 76), "HUB EXCLUSIVE", font=font(26, "black"), fill=GOLD)
        title_y = 180 if h > w else 160
        draw.text((72, title_y), "HUB-ONLY", font=font(72 if h > w else 56, "black"), fill=CREAM)
        draw.text((72, title_y + (76 if h > w else 62)), "DEAL DROP", font=font(92 if h > w else 72, "black"), fill=GREEN_2)
        rounded(draw, (72, title_y + (190 if h > w else 150), 530, title_y + (282 if h > w else 230)), 24, (0, 0, 0, 180), GOLD + (230,), 2)
        draw.text((106, title_y + (216 if h > w else 172)), "CODE SLOT: HUB10", font=font(32 if h > w else 27, "black"), fill=GOLD)
        draw_product_cluster(img, ["immune-plus", "buffered-c-90", "black-seed-oil"], (int(w * 0.68), int(h * 0.56)), int(h * (0.26 if h > w else 0.32)), GOLD)
        price_box = (72, int(h * 0.63), int(w * 0.55), int(h * 0.80))
        rounded(draw, price_box, 28, (0, 0, 0, 188), GOLD + (220,), 3)
        draw.text((price_box[0] + 34, price_box[1] + 28), "WAS R___", font=font(28 if h > w else 24, "bold"), fill=(220, 211, 186))
        draw.text((price_box[0] + 34, price_box[1] + 72), "NOW R___", font=font(62 if h > w else 48, "black"), fill=GREEN_2)
        draw.text((price_box[0] + 36, price_box[1] + 142 if h > w else price_box[1] + 126), "SAVE ___ / HUB ONLY", font=font(25 if h > w else 21, "black"), fill=GOLD)
        footer(draw, w, h, dark=True)
        path = out / f"hub-exclusive-deal-template-{suffix}.jpg"
        path.parent.mkdir(parents=True, exist_ok=True)
        img.convert("RGB").save(path, quality=94, subsampling=1)
        files.append(path)
    write_json(out / "manifest.json", {"franchise": "HUB EXCLUSIVE", "generatedAt": GENERATED_AT, "direction": "One Life Hybrid / dark offer mode", "ribbon": "HUB EXCLUSIVE", "codeSlot": "HUB10", "files": [rel(p) for p in files]})


def write_contact_sheet(path: Path, files: list[Path], title: str) -> None:
    thumbs = []
    for f in files:
        img = Image.open(f).convert("RGB")
        tw = 250
        th = round(img.height * (tw / img.width))
        thumbs.append((f, img.resize((tw, th), Image.Resampling.LANCZOS)))
    cols = 3
    pad = 28
    header = 82
    rows = math.ceil(len(thumbs) / cols)
    width = cols * 250 + (cols + 1) * pad
    height = header + rows * (max(t.height for _, t in thumbs) + 58) + pad
    canvas = Image.new("RGB", (width, height), (18, 27, 21))
    draw = ImageDraw.Draw(canvas)
    draw.text((pad, 26), title, font=font(34, "black"), fill=CREAM)
    for i, (f, thumb) in enumerate(thumbs):
        x = pad + (i % cols) * (250 + pad)
        y = header + (i // cols) * (thumb.height + 58)
        canvas.paste(thumb, (x, y))
        draw.rectangle((x - 2, y - 2, x + thumb.width + 2, y + thumb.height + 2), outline=GOLD, width=2)
        draw.text((x, y + thumb.height + 14), f.stem, font=font(17, "bold"), fill=CREAM)
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, quality=94)


def render_symptom_saturday() -> None:
    base = OUT / "symptom-saturday"
    render_carousel(
        ENERGY,
        base / "tired-by-2pm",
        "Always tired by 2pm?",
        "Coffee #3 isn't a strategy. Ask the One Life team about the basics: iron, B12 and your daily routine. Supplements support general health. If symptoms persist, consult your healthcare practitioner.",
    )
    render_carousel(
        SLEEP,
        base / "winter-sleep",
        "Winter sleep falling apart?",
        "Asleep early, awake at 3? Save this for your evening routine. Ask One Life about magnesium and glycine support. Supplements support general health. If symptoms persist, consult your healthcare practitioner.",
    )


TARGETS = {
    "symptom-saturday": render_symptom_saturday,
    "honest-label": render_honest_label,
    "made-by-us": render_made_by_us,
    "stack-of-week": render_stack_of_week,
    "ask-one-life": render_ask_one_life,
    "hub-exclusive": render_hub_exclusive,
}


def main(argv: list[str]) -> int:
    if len(argv) != 2 or argv[1] not in (set(TARGETS) | {"all"}):
        names = ", ".join(["all", *TARGETS.keys()])
        print(f"Usage: {Path(argv[0]).name} <{names}>", file=sys.stderr)
        return 2
    if argv[1] == "all":
        for fn in TARGETS.values():
            fn()
    else:
        TARGETS[argv[1]]()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
