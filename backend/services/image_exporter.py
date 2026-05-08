"""Image export service using Pillow."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from PIL import Image, ImageDraw, ImageFont

from config import settings

_EXPORT_DIR = Path(settings.upload_dir) / "exports"
_EXPORT_DIR.mkdir(parents=True, exist_ok=True)

_WIDTH = 1080
_HEIGHT = 1920


def _find_font(size: int) -> ImageFont.FreeTypeFont:
    candidates = [
        "/home/dev/.local/share/fonts/NotoSansCJKsc-Bold.otf",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except (IOError, OSError):
            continue
    try:
        return ImageFont.truetype("DejaVuSans-Bold.ttf", size)
    except (IOError, OSError):
        return ImageFont.load_default()


def _draw_gradient(draw: ImageDraw.ImageDraw, width: int, height: int) -> None:
    top_color = (15, 23, 42)
    bottom_color = (30, 41, 59)
    for y in range(height):
        ratio = y / height
        r = int(top_color[0] + (bottom_color[0] - top_color[0]) * ratio)
        g = int(top_color[1] + (bottom_color[1] - top_color[1]) * ratio)
        b = int(top_color[2] + (bottom_color[2] - top_color[2]) * ratio)
        draw.line([(0, y), (width, y)], fill=(r, g, b))


def _draw_text_centered(draw: ImageDraw.ImageDraw, text: str, y: int, font: ImageFont.FreeTypeFont, fill: tuple = (255, 255, 255)) -> int:
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    x = (_WIDTH - text_width) // 2
    draw.text((x, y), text, font=font, fill=fill)
    return bbox[3] - bbox[1]


def generate_report_image(task_id: str, report: dict) -> str:
    """Generate a 1080x1920 PNG report image and return the file path."""
    img = Image.new("RGB", (_WIDTH, _HEIGHT))
    draw = ImageDraw.Draw(img)

    _draw_gradient(draw, _WIDTH, _HEIGHT)

    font_large = _find_font(72)
    font_medium = _find_font(36)
    font_small = _find_font(24)
    font_tiny = _find_font(18)

    y = 120
    _draw_text_centered(draw, "LiveMirror", y, font_large, fill=(96, 165, 250))
    y += 100

    _draw_text_centered(draw, "直播复盘报告", y, font_medium)
    y += 80

    analysis = report.get("analysis", {})
    score = analysis.get("overall_score", "-")
    _draw_text_centered(draw, "综合得分", y, font_small, fill=(148, 163, 184))
    y += 40
    _draw_text_centered(draw, str(score), y, font_large, fill=(52, 211, 153))
    y += 120

    filename = report.get("filename", "-")
    duration = report.get("duration") or 0
    suggestions_count = len(report.get("suggestions", []))
    attribution_count = len(report.get("attribution_analysis", []))

    indicators = [
        ("文件", filename[:20]),
        ("时长", f"{duration:.0f}秒"),
        ("建议", str(suggestions_count)),
        ("归因", str(attribution_count)),
    ]

    card_width = 220
    card_height = 120
    total_width = len(indicators) * card_width + (len(indicators) - 1) * 20
    start_x = (_WIDTH - total_width) // 2

    for i, (label, value) in enumerate(indicators):
        x = start_x + i * (card_width + 20)
        draw.rounded_rectangle(
            [x, y, x + card_width, y + card_height],
            radius=12,
            fill=(30, 41, 59, 200),
            outline=(71, 85, 105),
        )
        _draw_text_centered(draw, value, y + 15, font_small, fill=(255, 255, 255))

        bbox = draw.textbbox((0, 0), value, font=font_small)
        val_height = bbox[3] - bbox[1]
        _draw_text_centered(draw, label, y + 20 + val_height, font_tiny, fill=(148, 163, 184))

    y += card_height + 60

    summary = report.get("summary_text", "")
    if summary:
        _draw_text_centered(draw, "摘要", y, font_medium, fill=(226, 232, 240))
        y += 50

        lines = []
        for i in range(0, len(summary), 28):
            lines.append(summary[i:i + 28])
        for line in lines[:6]:
            _draw_text_centered(draw, line, y, font_small, fill=(203, 213, 225))
            y += 36
        y += 30

    suggestions = report.get("suggestions", [])
    if suggestions:
        _draw_text_centered(draw, "优化建议", y, font_medium, fill=(226, 232, 240))
        y += 50
        for s in suggestions[:4]:
            title = s.get("title", "")
            priority = s.get("priority", "medium")
            color = {"high": (239, 68, 68), "medium": (251, 191, 36), "low": (52, 211, 153)}.get(priority, (203, 213, 225))
            draw.rounded_rectangle([80, y, _WIDTH - 80, y + 50], radius=8, fill=(30, 41, 59), outline=(71, 85, 105))
            draw.text((100, y + 12), f"[{priority}] {title[:25]}", font=font_small, fill=color)
            y += 60

    _draw_text_centered(draw, "Powered by LiveMirror", _HEIGHT - 80, font_tiny, fill=(100, 116, 139))

    output_path = _EXPORT_DIR / f"{task_id}_image.png"
    img.save(str(output_path), "PNG")
    return str(output_path)
