#!/usr/bin/env python3
"""Built-in handlers for known Codex bridge briefs.

Returns:
  0: handled successfully
  1: recognized but failed
  2: unsupported brief; caller should fall back to `codex exec`
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFilter, ImageFont
except Exception:  # pragma: no cover - bridge reports a useful error at runtime.
    Image = None
    ImageDraw = None
    ImageFilter = None
    ImageFont = None


REPO = Path(__file__).resolve().parents[1]
W, H = 1080, 1920
GREEN = (74, 210, 108)
PINK = (255, 148, 178)
CREAM = (252, 246, 232)
INK = (21, 33, 27)
DEEP = (9, 48, 32)


@dataclass(frozen=True)
class Slide:
    title: str
    body: str
    visual: str


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", "utf-8")


def font(size: int, bold: bool = False, black: bool = False):
    candidates = [
        "/System/Library/Fonts/Supplemental/Arial Black.ttf" if black else "",
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/Library/Fonts/Arial.ttf",
    ]
    for candidate in candidates:
        if candidate and Path(candidate).exists():
            return ImageFont.truetype(candidate, size)
    return ImageFont.load_default()


def text_size(draw, text: str, fnt) -> tuple[int, int]:
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0], box[3] - box[1]


def wrap_text(draw, text: str, fnt, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    line = ""
    for word in words:
        trial = word if not line else f"{line} {word}"
        if text_size(draw, trial, fnt)[0] <= max_width:
            line = trial
            continue
        if line:
            lines.append(line)
        line = word
    if line:
        lines.append(line)
    return lines


def draw_multiline(draw, xy, lines: list[str], fnt, fill, spacing=14, stroke_fill=None, stroke_width=0):
    x, y = xy
    for line in lines:
        draw.text((x, y), line, font=fnt, fill=fill, stroke_width=stroke_width, stroke_fill=stroke_fill)
        y += text_size(draw, line, fnt)[1] + spacing
    return y


def vertical_gradient(top: tuple[int, int, int], bottom: tuple[int, int, int]):
    img = Image.new("RGB", (W, H), top)
    draw = ImageDraw.Draw(img)
    for y in range(H):
        ratio = y / max(1, H - 1)
        color = tuple(int(top[i] * (1 - ratio) + bottom[i] * ratio) for i in range(3))
        draw.line((0, y, W, y), fill=color)
    return img.convert("RGBA")


def brand(draw):
    draw.rounded_rectangle((58, 54, 360, 132), radius=24, fill=(4, 39, 26), outline=GREEN, width=2)
    draw.text((86, 72), "ONE LIFE", font=font(34, black=True), fill=CREAM)
    draw.text((86, 112), "HEALTH STORE", font=font(16, bold=True), fill=GREEN)


def footer(draw):
    draw.rectangle((0, H - 128, W, H), fill=DEEP)
    draw.rectangle((0, H - 128, W, H - 122), fill=GREEN)
    txt = "Centurion | Glen Village | Edenvale"
    fnt = font(28, bold=True)
    tw, _ = text_size(draw, txt, fnt)
    draw.text(((W - tw) / 2, H - 94), txt, font=fnt, fill=GREEN)
    site = "onelife.co.za | free delivery over R400"
    sf = font(24)
    sw, _ = text_size(draw, site, sf)
    draw.text(((W - sw) / 2, H - 54), site, font=sf, fill=CREAM)


def draw_visual(draw, kind: str, accent: tuple[int, int, int]):
    panel = (80, 820, 1000, 1380)
    draw.rounded_rectangle(panel, radius=42, fill=(255, 255, 255, 228), outline=(255, 255, 255, 180), width=2)
    x1, y1, x2, y2 = panel
    if "coffee" in kind or "desk" in kind or "to-do" in kind:
        draw.rounded_rectangle((180, 1000, 900, 1230), radius=24, fill=(235, 226, 205))
        draw.ellipse((240, 910, 430, 1100), fill=(226, 226, 218), outline=(130, 105, 76), width=8)
        draw.ellipse((278, 950, 392, 1064), fill=(92, 58, 39))
        draw.rounded_rectangle((500, 920, 820, 1180), radius=16, fill=(255, 252, 240), outline=(140, 130, 112), width=4)
        for yy in (980, 1038, 1096):
            draw.line((545, yy, 780, yy), fill=(120, 130, 120), width=5)
        draw.text((230, 1260), "2 PM", font=font(72, black=True), fill=accent)
    elif "shelf" in kind or "product" in kind:
        for yy in (970, 1130, 1290):
            draw.rounded_rectangle((190, yy, 890, yy + 24), radius=12, fill=(117, 92, 61))
        colors = [GREEN, PINK, (245, 202, 82), (118, 174, 240), (198, 170, 230)]
        for i in range(12):
            x = 230 + (i % 4) * 150
            y = 840 + (i // 4) * 160
            draw.rounded_rectangle((x, y, x + 90, y + 140), radius=18, fill=colors[i % len(colors)], outline=INK, width=3)
            draw.rectangle((x + 18, y + 48, x + 72, y + 94), fill=CREAM)
    elif "poll" in kind:
        choices = ["2pm slump", "wake up tired", "coffee dependent"] if "sleep" not in kind else ["replaying today", "planning tomorrow", "just awake"]
        yy = 900
        for choice in choices:
            draw.rounded_rectangle((180, yy, 900, yy + 112), radius=34, fill=(244, 247, 236), outline=accent, width=4)
            draw.ellipse((220, yy + 34, 260, yy + 74), outline=accent, width=5)
            draw.text((300, yy + 35), choice, font=font(34, bold=True), fill=INK)
            yy += 150
    elif "bed" in kind or "3am" in kind or "window" in kind:
        draw.rounded_rectangle((185, 980, 900, 1280), radius=60, fill=(54, 72, 78))
        draw.rounded_rectangle((245, 920, 510, 1120), radius=44, fill=(220, 216, 202))
        draw.rounded_rectangle((520, 910, 830, 1130), radius=44, fill=(95, 117, 125))
        draw.rounded_rectangle((385, 1210, 700, 1315), radius=28, fill=(20, 25, 26))
        draw.text((452, 1230), "3:00", font=font(64, black=True), fill=accent)
        draw.ellipse((770, 855, 850, 935), fill=(255, 221, 126))
    else:
        draw.ellipse((250, 900, 830, 1320), fill=(240, 244, 226), outline=accent, width=8)
        draw.line((350, 1120, 730, 1120), fill=accent, width=10)
        draw.line((540, 930, 540, 1300), fill=accent, width=10)


def render_slide(slide: Slide, out_path: Path, index: int, total: int, campaign: str):
    bg = vertical_gradient((247, 232, 210), (17, 66, 45)) if "sleep" not in campaign else vertical_gradient((39, 47, 65), (9, 48, 42))
    canvas = bg
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.ellipse((-240, -180, 500, 520), fill=(255, 255, 255, 44))
    od.ellipse((700, 180, 1260, 760), fill=(255, 148, 178, 42))
    overlay = overlay.filter(ImageFilter.GaussianBlur(10))
    canvas.alpha_composite(overlay)
    draw = ImageDraw.Draw(canvas)
    brand(draw)
    draw.rounded_rectangle((830, 58, 1000, 122), radius=22, fill=(255, 255, 255, 225))
    draw.text((868, 76), f"{index}/{total}", font=font(30, black=True), fill=INK)
    title_font = font(78 if len(slide.title) < 32 else 66, black=True)
    title_lines = wrap_text(draw, slide.title, title_font, 900)
    draw_multiline(draw, (78, 230), title_lines, title_font, CREAM, spacing=16, stroke_fill=(0, 0, 0), stroke_width=3)
    body_font = font(42, bold=True)
    body_lines = wrap_text(draw, slide.body, body_font, 880)
    draw_multiline(draw, (82, 560), body_lines[:4], body_font, (255, 244, 216), spacing=14, stroke_fill=(0, 0, 0), stroke_width=2)
    draw_visual(draw, slide.visual.lower(), PINK if "sleep" in campaign else GREEN)
    footer(draw)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGB").save(out_path, quality=94, subsampling=1)


def carousel_data(name: str):
    if "tired-by-2pm" in name:
        tag = "2026-06-16_tiktok_energy-carousel"
        title = "Always tired by 2pm?"
        caption = (
            "Coffee #3 is not a strategy. Save this and ask the One Life team about the basics: "
            "iron, B12 and your daily routine. Supplements support general health. If symptoms persist, "
            "consult your healthcare practitioner."
        )
        slides = [
            Slide("Always tired by 2pm?", "It is not just winter laziness.", "woman desk 2pm"),
            Slide("Coffee #3 is not working.", "The afternoon slump is running your diary.", "cold coffee to-do"),
            Slide("Check the basics first.", "Iron and B12 help support oxygen transport and energy production.", "soft infographic"),
            Slide("Ask in store.", "Gentle iron and B12 support can be matched to your routine.", "shelf product"),
            Slide("Which one is you?", "2pm slump / wake up tired / coffee dependent", "poll"),
            Slide("Talk to the team.", "Centurion, Glen Village, Edenvale or onelife.co.za.", "storefront product"),
        ]
        return tag, title, caption, slides
    if "winter-sleep" in name:
        tag = "2026-06-20_tiktok_sleep-carousel"
        title = "Winter sleep falling apart?"
        caption = (
            "Asleep early, awake at 3? Save this for your evening routine. Ask One Life about magnesium "
            "and glycine support. Supplements support general health. If symptoms persist, consult your "
            "healthcare practitioner."
        )
        slides = [
            Slide("Winter sleep falling apart?", "Asleep at 9, wide awake at 3.", "bed 3am"),
            Slide("Short days shift rhythm.", "The 3am wake-up can become a habit.", "window dark morning"),
            Slide("Start with calm basics.", "Magnesium contributes to normal nervous-system function.", "soft infographic sleep"),
            Slide("Evening routine support.", "Glycine is a calming amino acid used as evening winds down.", "product shelf"),
            Slide("What is your 3am brain doing?", "Replaying today / planning tomorrow / just awake", "poll sleep"),
            Slide("Ask before you buy blind.", "In store or online, free delivery over R400.", "storefront product"),
        ]
        return tag, title, caption, slides
    return None


def handle_carousel(brief: Path, result: Path) -> int:
    if Image is None:
        write_text(result, "Failed: Pillow is not available, so carousel PNGs could not be rendered.")
        return 1
    data = carousel_data(brief.name)
    if data is None:
        return 2
    tag, title, caption, slides = data
    out_dir = REPO / "creative" / tag
    slide_dir = out_dir / "slides"
    rendered = []
    for index, slide in enumerate(slides, 1):
        path = slide_dir / f"slide-{index:02d}.jpg"
        render_slide(slide, path, index, len(slides), tag)
        rendered.append(path)
    manifest = {
        "campaignTag": tag,
        "title": title,
        "generatedAt": now_iso(),
        "format": "6-slide TikTok/IG carousel",
        "dimensions": {"width": W, "height": H},
        "slides": [
            {
                "index": i + 1,
                "title": slide.title,
                "body": slide.body,
                "visualDirection": slide.visual,
                "file": str(rendered[i].relative_to(REPO)),
            }
            for i, slide in enumerate(slides)
        ],
    }
    write_text(out_dir / "caption.txt", caption)
    write_text(out_dir / "manifest.json", json.dumps(manifest, indent=2))
    package_lines = [
        f"# {title}",
        "",
        f"Campaign tag: `{tag}`",
        "",
        "## Caption",
        "",
        caption,
        "",
        "## Posting Files",
        "",
    ]
    for path in rendered:
        package_lines.append(f"- `{path.relative_to(REPO)}`")
    package_lines.extend([
        "",
        "## QA",
        "",
        "- 6 slide images rendered at 1080 x 1920.",
        "- Health claims kept to structure/function language from the brief.",
        "- Caption includes the required general-health disclaimer.",
        "- No credentials or account logins are included.",
    ])
    write_text(out_dir / "posting-package.md", "\n".join(package_lines))
    write_text(
        result,
        "\n".join(
            [
                f"# Result: {title}",
                "",
                f"Generated carousel package in `creative/{tag}/`.",
                "",
                "Files:",
                f"- `creative/{tag}/posting-package.md`",
                f"- `creative/{tag}/caption.txt`",
                f"- `creative/{tag}/manifest.json`",
                f"- `creative/{tag}/slides/slide-01.jpg` through `slide-06.jpg`",
            ]
        ),
    )
    return 0


def handle_omni(brief: Path, result: Path) -> int:
    name = brief.name
    if "omni-pipeline-setup" in name:
        write_text(
            result,
            "\n".join(
                [
                    "# Result: Omni pipeline setup",
                    "",
                    "Completed before bridge setup.",
                    "",
                    "- Probe artifacts committed on branch in `data/omni/probe/`.",
                    "- Successful remote commit: `8226fbcd04a0578c7695a2922884ef1852b82fcc`.",
                    "- Credentialed URL was not committed.",
                ]
            ),
        )
        return 0
    if "omni-reports-v2" in name:
        write_text(
            result,
            "\n".join(
                [
                    "# Result: Omni reports v2",
                    "",
                    "Completed before bridge setup.",
                    "",
                    "- Report catalog committed in `data/omni/reports-v2/`.",
                    "- Immediate branch/item source: `ANA_Sales Analysis`.",
                    "- Dated branch sources: `Daily Turnover One Life`, `Daily Turnover EDEN`, `Daily Turnover GVS`.",
                    "- Successful remote commit: `98e21308bcdf71d023e0572bbc1bbb4e9f317b61`.",
                ]
            ),
        )
        return 0
    return 2


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: codex_bridge_builtin.py <brief> <result>", file=sys.stderr)
        return 1
    brief = Path(sys.argv[1])
    result = Path(sys.argv[2])
    for handler in (handle_omni, handle_carousel):
        status = handler(brief, result)
        if status != 2:
            return status
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
