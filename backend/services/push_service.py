"""Web Push 通知服务。pywebpush 未安装或 VAPID 未配置时静默跳过。"""

from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from config import settings
from models import PushSubscription

logger = logging.getLogger(__name__)


def send_push_notification(
    db: Session,
    user_id: int,
    title: str,
    message: str,
    link: str | None = None,
) -> None:
    """发送 Web Push 通知。失败不阻塞主流程。"""
    if not settings.vapid_private_key or not settings.vapid_public_key:
        return

    try:
        from pywebpush import webpush, WebPushException  # noqa: F811
    except ImportError:
        logger.debug("pywebpush not installed, skipping push notification")
        return

    subscriptions = db.query(PushSubscription).filter(
        PushSubscription.user_id == user_id,
    ).all()

    if not subscriptions:
        return

    payload_data = {"title": title, "message": message, "link": link or ""}

    for sub in subscriptions:
        try:
            webpush(
                subscription_info={
                    "endpoint": sub.endpoint,
                    "keys": {"p256dh": sub.p256dh, "auth": sub.auth},
                },
                data=__import__("json").dumps(payload_data),
                vapid_private_key=settings.vapid_private_key,
                vapid_claims={"sub": settings.vapid_subject},
            )
        except WebPushException as exc:
            logger.warning("Push failed for subscription %s: %s", sub.id, exc)
            if getattr(exc, "response", None) and exc.response.status_code in (404, 410):
                db.delete(sub)
                db.commit()
        except Exception:
            logger.exception("Unexpected push error for subscription %s", sub.id)
