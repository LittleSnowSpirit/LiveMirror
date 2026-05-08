"""通知系统 REST API。"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from config import settings
from database import get_db
from models import PushSubscription, User
from routes.core_auth import get_current_user
from services.notification_service import (
    create_notification,
    delete_notification,
    get_notifications,
    get_unread_count,
    mark_all_read,
    mark_notifications_read,
)

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


class MarkReadBody(BaseModel):
    ids: list[int]


class PushSubscribeBody(BaseModel):
    endpoint: str
    keys: dict


class PushUnsubscribeBody(BaseModel):
    endpoint: str


@router.get("/")
async def list_notifications(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    unread_only: bool = False,
    type: str | None = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    items, total, unread_count = get_notifications(
        db, current_user.id, page=page, page_size=page_size, unread_only=unread_only, type=type,
    )
    return {
        "notifications": items,
        "total": total,
        "unread_count": unread_count,
        "page": page,
        "page_size": page_size,
    }


@router.get("/unread-count")
async def unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return {"unread_count": get_unread_count(db, current_user.id)}


@router.post("/mark-read")
async def mark_read(
    body: MarkReadBody,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    mark_notifications_read(db, body.ids, current_user.id)
    return {"success": True, "unread_count": get_unread_count(db, current_user.id)}


@router.post("/mark-all-read")
async def mark_all(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    mark_all_read(db, current_user.id)
    return {"success": True, "unread_count": 0}


@router.delete("/{notification_id}")
async def remove_notification(
    notification_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not delete_notification(db, notification_id, current_user.id):
        raise HTTPException(status_code=404, detail="Notification not found.")
    return {"success": True}


@router.post("/push-subscribe")
async def push_subscribe(
    body: PushSubscribeBody,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    existing = db.query(PushSubscription).filter(
        PushSubscription.endpoint == body.endpoint,
    ).first()
    if existing:
        if existing.user_id != current_user.id:
            existing.user_id = current_user.id
            db.commit()
        return {"success": True}

    sub = PushSubscription(
        user_id=current_user.id,
        endpoint=body.endpoint,
        p256dh=body.keys.get("p256dh", ""),
        auth=body.keys.get("auth", ""),
    )
    db.add(sub)
    db.commit()
    return {"success": True}


@router.delete("/push-subscribe")
async def push_unsubscribe(
    body: PushUnsubscribeBody,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    sub = db.query(PushSubscription).filter(
        PushSubscription.endpoint == body.endpoint,
        PushSubscription.user_id == current_user.id,
    ).first()
    if sub:
        db.delete(sub)
        db.commit()
    return {"success": True}


# VAPID 公钥端点（不需要认证，单独路由避免自动注入 get_current_user）
vapid_router = APIRouter(tags=["notifications-public"])


@vapid_router.get("/api/notifications/vapid-public-key")
async def get_vapid_public_key():
    """返回 VAPID 公钥，供前端订阅推送。"""
    return {"public_key": settings.vapid_public_key}
