"""Share link API."""

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import ShareLink
from routes.core_auth import get_current_user
from services.database import get_task

router = APIRouter(prefix="/api", tags=["core-share"])


class CreateShareRequest(BaseModel):
    task_id: str
    template_config: Optional[str] = None
    expires_in_days: Optional[int] = None


@router.post("/share")
async def create_share(
    body: CreateShareRequest,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    task = get_task(db, body.task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found.")
    if task.status != "completed":
        raise HTTPException(status_code=400, detail="Task is not completed.")

    expires_at = None
    if body.expires_in_days and body.expires_in_days > 0:
        expires_at = datetime.now(timezone.utc) + timedelta(days=body.expires_in_days)

    share = ShareLink(
        task_id=body.task_id,
        template_config=body.template_config,
        expires_at=expires_at,
        user_id=_current_user.id,
    )
    db.add(share)
    db.flush()
    db.refresh(share)

    return {"success": True, "share": share.to_dict()}


@router.get("/share/{token}")
async def get_share(
    token: str,
    access_code: str = Query(..., description="4-digit access code"),
    db: Session = Depends(get_db),
):
    share = db.query(ShareLink).filter(ShareLink.token == token).first()
    if share is None:
        raise HTTPException(status_code=404, detail="Share link not found.")

    if share.expires_at and share.expires_at < datetime.now(timezone.utc):
        raise HTTPException(status_code=410, detail="Share link has expired.")

    if share.access_code != access_code:
        raise HTTPException(status_code=403, detail="Invalid access code.")

    share.view_count += 1
    db.flush()

    task = get_task(db, share.task_id)
    report_data = task.report_data if task and task.report_data else {}

    return {
        "success": True,
        "share": share.to_dict(),
        "report": report_data,
    }


@router.delete("/share/{token}")
async def delete_share(
    token: str,
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    share = db.query(ShareLink).filter(ShareLink.token == token).first()
    if share is None:
        raise HTTPException(status_code=404, detail="Share link not found.")

    if share.user_id != _current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to delete this share link.")

    db.delete(share)
    db.flush()

    return {"success": True, "message": "Share link deleted."}


@router.get("/shares")
async def list_shares(
    db: Session = Depends(get_db),
    _current_user=Depends(get_current_user),
):
    shares = (
        db.query(ShareLink)
        .filter(ShareLink.user_id == _current_user.id)
        .order_by(ShareLink.created_at.desc())
        .all()
    )

    return {
        "success": True,
        "shares": [s.to_dict() for s in shares],
    }
