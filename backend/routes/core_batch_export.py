"""Batch export API — download multiple reports as a ZIP."""

import io
import json
import zipfile
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import Task

router = APIRouter(prefix="/api/batch-export", tags=["core-batch-export"])


class BatchExportRequest(BaseModel):
    task_ids: list[str]
    format: Literal["json", "markdown"] = "json"


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

    return "\n".join(lines)


@router.post("")
async def batch_export(
    request: BatchExportRequest,
    db: Session = Depends(get_db),
    _current_user=None,
):
    if not request.task_ids:
        raise HTTPException(status_code=400, detail="No task IDs provided.")

    tasks = (
        db.query(Task)
        .filter(Task.task_id.in_(request.task_ids))
        .all()
    )

    if not tasks:
        raise HTTPException(status_code=404, detail="No matching tasks found.")

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for task in tasks:
            report = task.report_data or {}
            ext = "json" if request.format == "json" else "md"
            filename = f"{task.task_id}_{task.filename.rsplit('.', 1)[0]}.{ext}"

            if request.format == "json":
                content = json.dumps(report, ensure_ascii=False, indent=2).encode("utf-8")
            else:
                content = _to_markdown(report).encode("utf-8")

            zf.writestr(filename, content)

    buf.seek(0)
    return StreamingResponse(
        buf,
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=batch_export.zip"},
    )
