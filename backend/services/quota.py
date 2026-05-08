"""Shared quota management utilities."""

from datetime import date as date_type, timedelta

from sqlalchemy.orm import Session

from models import UserQuota


def get_or_create_quota(db: Session, user_id: int, *, lock: bool = False) -> UserQuota:
    """Return the current-week quota row, creating or resetting it if needed.

    Args:
        db: Database session
        user_id: User ID
        lock: If True, use SELECT FOR UPDATE to prevent race conditions
    """
    today = date_type.today()
    monday = today - timedelta(days=today.weekday())

    query = db.query(UserQuota).filter(UserQuota.user_id == user_id)
    if lock:
        query = query.with_for_update()
    quota = query.first()

    if quota is None:
        quota = UserQuota(user_id=user_id, week_start_date=monday)
        db.add(quota)
        db.flush()
    elif quota.week_start_date != monday:
        quota.used_this_week = 0
        quota.week_start_date = monday
        db.flush()

    # 配额即将用完时发送通知（每周最多一次）
    if quota.used_this_week >= quota.weekly_limit - 1 and quota.weekly_limit > 1:
        _check_and_notify_quota_low(db, user_id, monday)

    return quota


def _check_and_notify_quota_low(db: Session, user_id: int, monday: date_type) -> None:
    """如果本周还没有发过 quota_low 通知，则发送一条。"""
    from datetime import datetime, timezone
    from models import Notification

    week_start_dt = datetime(monday.year, monday.month, monday.day, tzinfo=timezone.utc)
    existing = db.query(Notification).filter(
        Notification.user_id == user_id,
        Notification.type == "quota_low",
        Notification.created_at >= week_start_dt,
    ).first()
    if existing:
        return

    try:
        from services.notification_service import create_notification
        create_notification(
            db, user_id, "quota_low", "配额即将用完",
            "本周免费分析次数即将用完，下周一重置",
            link="/profile",
        )
    except Exception:
        pass
