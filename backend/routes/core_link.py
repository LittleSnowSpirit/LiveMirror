"""Link analysis API — submit live replay URLs for analysis."""

from __future__ import annotations

import uuid
from datetime import date as date_type, timedelta

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import UsageRecord, UserQuota
from routes.core_auth import get_current_user
from services.database import create_task
from services.link_parser import get_link_info, is_supported_url
from services.task_queue import get_task_queue, process_link_task

router = APIRouter(prefix="/api", tags=["core-link"])


class AnalyzeLinkRequest(BaseModel):
    url: str


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


@router.post("/analyze-link")
async def analyze_link(
    body: AnalyzeLinkRequest,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    """Submit a link for background analysis."""
    url = body.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="URL is required.")

    if not is_supported_url(url):
        raise HTTPException(
            status_code=400,
            detail="Unsupported URL. Supported platforms: Douyin, Bilibili.",
        )

    user_id = _current_user.id if _current_user else 1
    quota = _get_or_create_quota(db, user_id)
    if quota.used_this_week >= quota.weekly_limit:
        raise HTTPException(
            status_code=429,
            detail=f"Weekly quota exhausted ({quota.weekly_limit}/{quota.weekly_limit}). Resets next Monday.",
        )

    task_id = str(uuid.uuid4())
    info = get_link_info(url)
    filename = info.title or f"link_{task_id[:8]}"

    create_task(
        db,
        task_id=task_id,
        filename=filename,
        file_path="",  # will be set after download
        file_size=0,
        source_type="link",
        source_url=url,
    )

    # Consume quota
    quota.used_this_week += 1
    usage = UsageRecord(user_id=user_id, task_id=task_id)
    db.add(usage)
    db.commit()

    get_task_queue().submit(task_id, process_link_task, task_id, url)

    return {
        "task_id": task_id,
        "filename": filename,
        "source_type": "link",
        "source_url": url,
        "status": "pending",
        "message": "Link accepted. Download and analysis has started.",
    }


@router.get("/link-info")
async def get_link_info_endpoint(
    url: str,
    _current_user=Depends(get_current_user),
):
    """Preview link metadata without downloading."""
    if not url.strip():
        raise HTTPException(status_code=400, detail="URL is required.")

    info = get_link_info(url)
    return {
        "success": info.error is None,
        "data": {
            "platform": info.platform,
            "video_id": info.video_id,
            "title": info.title,
            "duration": info.duration,
            "thumbnail_url": info.thumbnail_url,
            "uploader": info.uploader,
        },
        "error": info.error,
    }
