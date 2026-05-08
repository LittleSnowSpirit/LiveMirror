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
    return quota
