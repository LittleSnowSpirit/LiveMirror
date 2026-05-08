"""弹幕数据 API"""

from __future__ import annotations

from datetime import date as date_type, timedelta
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from config import settings
from database import get_db
from models import AnalysisReport, DanmuBatch, UsageRecord, UserQuota
from routes.core_auth import get_current_user
from services.danmu_service import (
    batch_insert_danmus,
    get_danmu_batch_detail,
    get_danmu_batches,
    get_danmu_by_batch,
)

router = APIRouter(prefix="/api/danmu", tags=["core-danmu"])

_ALLOWED_EXTENSIONS = {"json", "csv"}
_CHUNK_SIZE = 1024 * 1024


def _get_or_create_quota(db: Session, user_id: int) -> UserQuota:
    """Return the current-week quota row, creating one if needed."""
    today = date_type.today()
    monday = today - timedelta(days=today.weekday())

    quota = db.query(UserQuota).filter(UserQuota.user_id == user_id).first()
    if quota is None:
        quota = UserQuota(user_id=user_id, week_start_date=monday)
        db.add(quota)
        db.commit()
        db.refresh(quota)
    elif quota.week_start_date != monday:
        quota.used_this_week = 0
        quota.week_start_date = monday
        db.commit()
        db.refresh(quota)
    return quota


@router.post("/upload")
async def upload_danmu(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """上传弹幕文件（CSV/JSON），解析并入库。"""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename.")

    extension = Path(file.filename).suffix.lower().lstrip(".")
    if extension not in _ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: {', '.join(sorted(_ALLOWED_EXTENSIONS))}",
        )

    safe_name = Path(file.filename).name
    danmu_dir = Path(settings.upload_dir) / "danmu"
    danmu_dir.mkdir(parents=True, exist_ok=True)
    save_path = danmu_dir / safe_name

    try:
        with save_path.open("wb") as buffer:
            while True:
                chunk = file.file.read(_CHUNK_SIZE)
                if not chunk:
                    break
                buffer.write(chunk)
    except Exception as exc:
        save_path.unlink(missing_ok=True)
        raise HTTPException(status_code=500, detail="Failed to save uploaded file.") from exc
    finally:
        file.file.close()

    if save_path.stat().st_size == 0:
        save_path.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    batch = batch_insert_danmus(
        db=db,
        user_id=current_user.id,
        file_path=str(save_path),
        file_format=extension,
        filename=safe_name,
    )

    return {
        "batch_id": batch.id,
        "total_count": batch.total_count,
        "success_count": batch.success_count,
        "failed_count": batch.failed_count,
    }


@router.get("/batches")
async def list_batches(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """获取当前用户的弹幕批次列表。"""
    batches = get_danmu_batches(db, current_user.id)
    return {"batches": [b.to_dict() for b in batches]}


@router.get("/batch/{batch_id}")
async def batch_detail(
    batch_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """获取单个批次详情及其弹幕。"""
    batch = get_danmu_batch_detail(db, batch_id)
    if not batch or batch.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Batch not found.")

    danmus = get_danmu_by_batch(db, batch.id)
    result = batch.to_dict()
    result["danmus"] = [d.to_dict() for d in danmus]
    return result


# ── 弹幕分析 API ──────────────────────────────────────────────


def _run_danmu_analysis(batch_id: str) -> None:
    """后台线程：执行弹幕情感分析。"""
    from database import SessionLocal
    from services.danmu_analyzer import analyze_danmu_batch

    db = SessionLocal()
    try:
        analyze_danmu_batch(db, batch_id)
        db.commit()
    except Exception:
        db.rollback()
        import logging
        logging.getLogger(__name__).exception("Danmu analysis failed for batch %s", batch_id)
    finally:
        db.close()


@router.post("/batch/{batch_id}/analyze")
async def trigger_danmu_analysis(
    batch_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """触发弹幕情感分析（后台执行）。"""
    batch = db.query(DanmuBatch).filter(DanmuBatch.batch_id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found.")
    if batch.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden.")

    # 配额检查
    quota = _get_or_create_quota(db, current_user.id)
    if quota.used_this_week >= quota.weekly_limit:
        raise HTTPException(
            status_code=429,
            detail=f"Weekly quota exhausted ({quota.weekly_limit}/{quota.weekly_limit}). Resets next Monday.",
        )

    # 消耗配额
    quota.used_this_week += 1
    usage = UsageRecord(user_id=current_user.id)
    db.add(usage)
    db.commit()

    background_tasks.add_task(_run_danmu_analysis, batch_id)
    return {"status": "processing", "batch_id": batch_id}


@router.get("/analysis/{batch_id}")
async def get_danmu_analysis(
    batch_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """获取弹幕分析结果（含 ECharts 格式数据）。"""
    batch = db.query(DanmuBatch).filter(DanmuBatch.batch_id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found.")
    if batch.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden.")

    report = db.query(AnalysisReport).filter(
        AnalysisReport.task_id == batch_id
    ).first()

    if not report or not report.report_data:
        return {"status": "pending", "batch_id": batch_id}

    danmu_data = report.report_data.get("danmu_analysis")
    if not danmu_data:
        return {"status": "pending", "batch_id": batch_id}

    # 添加 ECharts 格式数据
    from services.danmu_analyzer import format_for_echarts
    danmu_data["echarts"] = format_for_echarts(danmu_data)
    return danmu_data


@router.get("/analysis/{batch_id}/correlation")
async def get_speech_danmu_correlation(
    batch_id: str,
    task_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """获取话术-弹幕关联分析数据（含 ECharts 格式）。"""
    batch = db.query(DanmuBatch).filter(DanmuBatch.batch_id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found.")
    if batch.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden.")

    # 先检查缓存
    report = db.query(AnalysisReport).filter(
        AnalysisReport.task_id == batch_id
    ).first()

    correlations = None
    if report and report.report_data:
        correlations = report.report_data.get("speech_danmu_correlation")

    if not correlations:
        from services.danmu_analyzer import correlate_speech_danmu
        result = correlate_speech_danmu(db, task_id, batch_id)
        db.commit()
        correlations = result.get("correlations", [])
    else:
        result = {
            "task_id": task_id,
            "batch_id": batch_id,
            "correlations": correlations,
            "status": "completed",
        }

    # 添加 ECharts 格式
    from services.danmu_analyzer import _format_correlation_echarts
    result["echarts"] = _format_correlation_echarts(correlations)
    return result


@router.get("/analysis/{batch_id}/keywords")
async def get_danmu_keywords(
    batch_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """获取弹幕关键词及词频（含 ECharts 格式）。"""
    batch = db.query(DanmuBatch).filter(DanmuBatch.batch_id == batch_id).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch not found.")
    if batch.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden.")

    report = db.query(AnalysisReport).filter(
        AnalysisReport.task_id == batch_id
    ).first()

    if not report or not report.report_data:
        return {"status": "pending", "batch_id": batch_id}

    danmu_data = report.report_data.get("danmu_analysis", {})
    keywords = danmu_data.get("keywords", [])

    # 添加 ECharts 格式
    from services.danmu_analyzer import _format_keywords_echarts
    return {
        "batch_id": batch_id,
        "keywords": keywords,
        "echarts": _format_keywords_echarts(keywords),
        "status": "completed",
    }
