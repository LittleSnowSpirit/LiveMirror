"""PDF report generator using reportlab."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Literal

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm, mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from config import settings

TemplateType = Literal["compact", "detailed", "data"]

_EXPORT_DIR = Path(settings.upload_dir) / "exports"
_EXPORT_DIR.mkdir(parents=True, exist_ok=True)

_FONT_REGISTERED = False
_FONT_NAME = "Helvetica"
_BOLD_FONT_NAME = "Helvetica-Bold"


def _register_chinese_font() -> None:
    global _FONT_REGISTERED, _FONT_NAME, _BOLD_FONT_NAME
    if _FONT_REGISTERED:
        return
    _FONT_REGISTERED = True

    candidates = [
        "/home/dev/.local/share/fonts/NotoSansCJKsc-Regular.otf",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    ]
    bold_candidates = [
        "/home/dev/.local/share/fonts/NotoSansCJKsc-Bold.otf",
        "/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    ]

    for path in candidates:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont("NotoSansCJK", path))
                _FONT_NAME = "NotoSansCJK"
                break
            except Exception:
                continue

    for path in bold_candidates:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont("NotoSansCJKBold", path))
                _BOLD_FONT_NAME = "NotoSansCJKBold"
                return
            except Exception:
                continue

    _BOLD_FONT_NAME = _FONT_NAME


def _build_styles() -> dict[str, ParagraphStyle]:
    _register_chinese_font()
    base = getSampleStyleSheet()

    title = ParagraphStyle(
        "LMTitle",
        parent=base["Title"],
        fontName=_BOLD_FONT_NAME,
        fontSize=20,
        leading=28,
        spaceAfter=12,
    )
    heading = ParagraphStyle(
        "LMHeading",
        parent=base["Heading2"],
        fontName=_BOLD_FONT_NAME,
        fontSize=14,
        leading=20,
        spaceBefore=16,
        spaceAfter=8,
    )
    body = ParagraphStyle(
        "LMBody",
        parent=base["Normal"],
        fontName=_FONT_NAME,
        fontSize=10,
        leading=16,
    )
    small = ParagraphStyle(
        "LMSmall",
        parent=base["Normal"],
        fontName=_FONT_NAME,
        fontSize=8,
        leading=12,
        textColor=colors.grey,
    )
    metric_value = ParagraphStyle(
        "LMMetricValue",
        fontName=_BOLD_FONT_NAME,
        fontSize=24,
        leading=30,
        alignment=1,
    )
    metric_label = ParagraphStyle(
        "LMMetricLabel",
        fontName=_FONT_NAME,
        fontSize=9,
        leading=12,
        alignment=1,
        textColor=colors.grey,
    )
    return {
        "title": title,
        "heading": heading,
        "body": body,
        "small": small,
        "metric_value": metric_value,
        "metric_label": metric_label,
    }


def _safe_text(text: str | None) -> str:
    if not text:
        return "-"
    return str(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _add_header(doc: SimpleDocTemplate, report: dict, styles: dict) -> list:
    elements = []
    elements.append(Paragraph("LiveMirror 直播复盘报告", styles["title"]))
    elements.append(Paragraph(f"文件: {_safe_text(report.get('filename'))}", styles["body"]))
    duration = report.get("duration") or 0
    elements.append(Paragraph(f"时长: {duration:.0f}秒", styles["body"]))
    elements.append(Spacer(1, 12))
    return elements


def _add_metrics_table(report: dict, styles: dict) -> list:
    analysis = report.get("analysis", {})
    score = analysis.get("overall_score", "-")
    suggestions = report.get("suggestions", [])
    attribution = report.get("attribution_analysis", [])

    metrics = [
        [Paragraph(str(score), styles["metric_value"]),
         Paragraph(str(len(suggestions)), styles["metric_value"]),
         Paragraph(str(len(attribution)), styles["metric_value"])],
        [Paragraph("综合得分", styles["metric_label"]),
         Paragraph("建议数", styles["metric_label"]),
         Paragraph("归因数", styles["metric_label"])],
    ]

    table = Table(metrics, colWidths=[5.5 * cm, 5.5 * cm, 5.5 * cm])
    table.setStyle(TableStyle([
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return [table, Spacer(1, 12)]


def _add_summary(report: dict, styles: dict) -> list:
    summary = report.get("summary_text") or "暂无摘要。"
    return [
        Paragraph("摘要", styles["heading"]),
        Paragraph(_safe_text(summary), styles["body"]),
        Spacer(1, 8),
    ]


def _add_suggestions(report: dict, styles: dict) -> list:
    suggestions = report.get("suggestions", [])
    if not suggestions:
        return []

    elements = [Paragraph("优化建议", styles["heading"])]
    rows = [["优先级", "标题", "描述"]]
    for s in suggestions[:10]:
        rows.append([
            _safe_text(s.get("priority", "medium")),
            _safe_text(s.get("title", "")),
            _safe_text(s.get("description", "")),
        ])

    table = Table(rows, colWidths=[2.5 * cm, 4 * cm, 10 * cm])
    table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), _FONT_NAME),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("FONTNAME", (0, 0), (-1, 0), _BOLD_FONT_NAME),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f0f0f0")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 8))
    return elements


def _add_attribution(report: dict, styles: dict) -> list:
    items = report.get("attribution_analysis", [])
    if not items:
        return []

    elements = [Paragraph("归因分析", styles["heading"])]
    rows = [["因素", "影响", "置信度"]]
    for item in items[:10]:
        rows.append([
            _safe_text(item.get("factor", "")),
            _safe_text(item.get("impact", "")),
            f"{item.get('confidence', 0):.2f}",
        ])

    table = Table(rows, colWidths=[5 * cm, 6 * cm, 3 * cm])
    table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), _FONT_NAME),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("FONTNAME", (0, 0), (-1, 0), _BOLD_FONT_NAME),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f0f0f0")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 8))
    return elements


def _add_transcription(report: dict, styles: dict) -> list:
    text = report.get("transcription")
    if not text:
        return []
    return [
        Paragraph("转写内容", styles["heading"]),
        Paragraph(_safe_text(text[:2000]), styles["body"]),
        Spacer(1, 8),
    ]


def _add_segments_table(report: dict, styles: dict) -> list:
    segments = report.get("segments", [])
    if not segments:
        return []

    elements = [Paragraph("话术片段", styles["heading"])]
    rows = [["时间", "内容"]]
    for seg in segments[:20]:
        start = seg.get("start", 0)
        rows.append([f"{start:.1f}s", _safe_text(seg.get("text", ""))])

    table = Table(rows, colWidths=[2.5 * cm, 14 * cm])
    table.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, -1), _FONT_NAME),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("FONTNAME", (0, 0), (-1, 0), _BOLD_FONT_NAME),
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#f0f0f0")),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.lightgrey),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    elements.append(table)
    return elements


def generate_pdf(task_id: str, report: dict, template: TemplateType = "compact") -> str:
    """Generate a PDF report and return the file path."""
    _register_chinese_font()
    styles = _build_styles()

    output_path = _EXPORT_DIR / f"{task_id}_{template}.pdf"
    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
    )

    elements = _add_header(doc, report, styles)

    if template == "compact":
        elements.extend(_add_metrics_table(report, styles))
        elements.extend(_add_summary(report, styles))
        elements.extend(_add_suggestions(report, styles))

    elif template == "detailed":
        elements.extend(_add_metrics_table(report, styles))
        elements.extend(_add_summary(report, styles))
        elements.extend(_add_suggestions(report, styles))
        elements.extend(_add_attribution(report, styles))
        elements.extend(_add_transcription(report, styles))
        elements.extend(_add_segments_table(report, styles))

    elif template == "data":
        elements.extend(_add_metrics_table(report, styles))
        elements.extend(_add_attribution(report, styles))
        elements.extend(_add_segments_table(report, styles))
        elements.extend(_add_suggestions(report, styles))

    doc.build(elements)
    return str(output_path)
