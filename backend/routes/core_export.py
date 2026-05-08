"""Core report export API."""

import json
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from sqlalchemy.orm import Session

from database import get_db
from routes.core_auth import get_current_user
from services.database import get_task

router = APIRouter(prefix="/api/export", tags=["core-export"])


@router.get("/{task_id}/pdf")
async def export_pdf(
    task_id: str,
    template: Literal["compact", "detailed", "data"] = Query("compact"),
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    task = get_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found.")
    if task.status != "completed":
        raise HTTPException(status_code=400, detail="Task is not completed.")

    report = task.report_data or {}
    from services.pdf_generator import generate_pdf

    file_path = generate_pdf(task_id, report, template)
    return FileResponse(
        path=file_path,
        media_type="application/pdf",
        filename=f"{task_id}_{template}.pdf",
    )


@router.get("/{task_id}/image")
async def export_image(
    task_id: str,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    task = get_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found.")
    if task.status != "completed":
        raise HTTPException(status_code=400, detail="Task is not completed.")

    report = task.report_data or {}
    from services.image_exporter import generate_report_image

    file_path = generate_report_image(task_id, report)
    return FileResponse(
        path=file_path,
        media_type="image/png",
        filename=f"{task_id}_report.png",
    )


@router.get("/{task_id}/{format}")
async def export_report(task_id: str, format: str, db: Session = Depends(get_db), _current_user=Depends(get_current_user)):
    task = get_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found.")
    if task.status != "completed":
        raise HTTPException(status_code=400, detail="Task is not completed.")

    report = task.report_data or {}
    normalized_format = format.lower()
    if normalized_format == "json":
        return JSONResponse(content=report)
    if normalized_format in {"markdown", "md"}:
        return PlainTextResponse(content=_to_markdown(report), media_type="text/markdown; charset=utf-8")
    raise HTTPException(status_code=400, detail="Unsupported export format. Use json or markdown.")


def _to_markdown(report: dict) -> str:
    analysis = report.get("analysis", {})
    suggestions = report.get("suggestions", [])
    attribution = report.get("attribution_analysis", [])
    segments = report.get("segments", [])

    lines = [
        "# LiveMirror 直播复盘报告",
        "",
        f"- 文件名: {report.get('filename', '-')}",
        f"- 时长: {report.get('duration') or 0:.1f} 秒",
        f"- 语言: {report.get('language') or '-'}",
        "",
        "## 摘要",
        "",
        report.get("summary_text") or "暂无摘要。",
        "",
        "## 转写",
        "",
        report.get("transcription") or "暂无转写。",
        "",
        "## 话术片段",
        "",
    ]

    for segment in segments:
        lines.append(f"- [{segment.get('start', 0):.1f}s] {segment.get('text', '')}")

    lines.extend(["", "## 归因分析", ""])
    for item in attribution:
        lines.append(f"- {item.get('factor')}: {item.get('impact')} ({item.get('confidence', 0):.2f})")

    lines.extend(["", "## 优化建议", ""])
    for item in suggestions:
        lines.append(f"- [{item.get('priority', 'medium')}] {item.get('title')}: {item.get('description')}")

    lines.extend(["", "## 原始分析 JSON", "", "```json", json.dumps(analysis, ensure_ascii=False, indent=2), "```"])
    return "\n".join(lines)
