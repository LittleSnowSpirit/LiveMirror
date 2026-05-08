"""通知服务 — 创建、查询、标记已读，以及内存事件发射器。"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any, Callable, Coroutine

from sqlalchemy import func
from sqlalchemy.orm import Session

from models import Notification

logger = logging.getLogger(__name__)

# ── 事件发射器 ────────────────────────────────────────────────


class NotificationEmitter:
    """内存事件发射器，将同步 DB 回调桥接到异步 SSE/WS 推送。"""

    def __init__(self) -> None:
        self._subscribers: dict[int, list[Callable[[dict], Coroutine]]] = {}
        self._loop: asyncio.AbstractEventLoop | None = None

    def set_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop

    def subscribe(self, user_id: int, callback: Callable[[dict], Coroutine]) -> None:
        self._subscribers.setdefault(user_id, []).append(callback)

    def unsubscribe(self, user_id: int, callback: Callable[[dict], Coroutine]) -> None:
        cbs = self._subscribers.get(user_id)
        if cbs and callback in cbs:
            cbs.remove(callback)
            if not cbs:
                del self._subscribers[user_id]

    def emit(self, user_id: int, payload: dict) -> None:
        """同步调用：调度异步回调到事件循环。"""
        cbs = self._subscribers.get(user_id)
        if not cbs:
            return
        if self._loop is None:
            logger.warning("NotificationEmitter: no event loop set, skipping emit for user %d", user_id)
            return
        for cb in cbs:
            try:
                asyncio.run_coroutine_threadsafe(cb(payload), self._loop)
            except Exception:
                logger.exception("NotificationEmitter: failed to schedule callback for user %d", user_id)


emitter = NotificationEmitter()


# ── 通知 CRUD ─────────────────────────────────────────────────


def create_notification(
    db: Session,
    user_id: int,
    type: str,
    title: str,
    message: str,
    link: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> Notification:
    """创建通知并 emit 事件。不阻塞主流程。"""
    notification = Notification(
        user_id=user_id,
        type=type,
        title=title,
        message=message,
        link=link,
        metadata_=metadata,
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)

    try:
        unread_count = get_unread_count(db, user_id)
        emitter.emit(user_id, {
            "type": "notification",
            "notification": notification.to_dict(),
            "unread_count": unread_count,
        })
    except Exception:
        logger.exception("Failed to emit notification event for user %d", user_id)

    return notification


def get_notifications(
    db: Session,
    user_id: int,
    page: int = 1,
    page_size: int = 20,
    unread_only: bool = False,
    type: str | None = None,
) -> tuple[list[dict], int, int]:
    """返回 (通知列表, 总数, 未读数)。"""
    query = db.query(Notification).filter(Notification.user_id == user_id)
    if unread_only:
        query = query.filter(Notification.is_read == False)
    if type:
        query = query.filter(Notification.type == type)

    total = query.count()
    unread_count = get_unread_count(db, user_id)

    items = (
        query.order_by(Notification.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return [n.to_dict() for n in items], total, unread_count


def get_unread_count(db: Session, user_id: int) -> int:
    return db.query(func.count(Notification.id)).filter(
        Notification.user_id == user_id,
        Notification.is_read == False,
    ).scalar() or 0


def mark_notifications_read(db: Session, ids: list[int], user_id: int) -> None:
    db.query(Notification).filter(
        Notification.id.in_(ids),
        Notification.user_id == user_id,
    ).update({Notification.is_read: True}, synchronize_session=False)
    db.commit()


def mark_all_read(db: Session, user_id: int) -> None:
    db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.is_read == False,
    ).update({Notification.is_read: True}, synchronize_session=False)
    db.commit()


def delete_notification(db: Session, notification_id: int, user_id: int) -> bool:
    n = db.query(Notification).filter(
        Notification.id == notification_id,
        Notification.user_id == user_id,
    ).first()
    if not n:
        return False
    db.delete(n)
    db.commit()
    return True
