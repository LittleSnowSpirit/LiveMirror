"""User quota and usage records API."""

from datetime import date as date_type, timedelta, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database import get_db
from models import UserQuota, UsageRecord

router = APIRouter(prefix="/api/user", tags=["core-user"])


def _get_or_create_quota(db: Session, user_id: int) -> UserQuota:
    """Return the current-week quota row, creating one if it does not exist."""
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


@router.get("/quota")
async def get_user_quota(
    db: Session = Depends(get_db),
    _current_user=None,
):
    user_id = _current_user.id if _current_user else 1
    quota = _get_or_create_quota(db, user_id)

    today = date_type.today()
    monday = today - timedelta(days=today.weekday())
    next_monday = monday + timedelta(days=7)

    return {
        "success": True,
        "quota": {
            "weekly_limit": quota.weekly_limit,
            "used_this_week": quota.used_this_week,
            "remaining": max(0, quota.weekly_limit - quota.used_this_week),
            "reset_at": next_monday.isoformat(),
        },
    }


@router.get("/usage")
async def get_user_usage(
    db: Session = Depends(get_db),
    _current_user=None,
):
    user_id = _current_user.id if _current_user else 1
    records = (
        db.query(UsageRecord)
        .filter(UsageRecord.user_id == user_id)
        .order_by(UsageRecord.created_at.desc())
        .limit(50)
        .all()
    )

    return {
        "success": True,
        "records": [r.to_dict() for r in records],
    }
