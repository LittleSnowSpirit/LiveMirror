"""User quota, usage records, and profile API."""

import os
from datetime import date as date_type, timedelta, timezone
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from config import settings
from database import get_db
from models import User, UserQuota, UsageRecord
from routes.core_auth import get_current_user
from services.quota import get_or_create_quota

router = APIRouter(prefix="/api/user", tags=["core-user"])

_AVATAR_DIR = Path(settings.upload_dir) / "avatars"
_AVATAR_DIR.mkdir(parents=True, exist_ok=True)

_ALLOWED_AVATAR_TYPES = {"image/jpeg": ".jpg", "image/png": ".png"}
_MAX_AVATAR_SIZE = 2 * 1024 * 1024


@router.get("/quota")
async def get_user_quota(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user_id = current_user.id
    quota = get_or_create_quota(db, user_id)

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
    current_user=Depends(get_current_user),
):
    user_id = current_user.id
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


# ==================== Profile ====================


class ProfileUpdate(BaseModel):
    nickname: Optional[str] = None
    bio: Optional[str] = None


@router.get("/profile")
async def get_profile(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user_id = current_user.id
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")

    return {
        "success": True,
        "profile": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "nickname": user.nickname,
            "bio": user.bio,
            "avatar_url": user.avatar_url,
            "created_at": user.created_at.isoformat() if user.created_at else None,
        },
    }


@router.put("/profile")
async def update_profile(
    body: ProfileUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user_id = current_user.id
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")

    if body.nickname is not None:
        user.nickname = body.nickname
    if body.bio is not None:
        user.bio = body.bio

    db.commit()
    db.refresh(user)

    return {
        "success": True,
        "profile": {
            "id": user.id,
            "username": user.username,
            "nickname": user.nickname,
            "bio": user.bio,
            "avatar_url": user.avatar_url,
        },
    }


@router.post("/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user_id = current_user.id
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")

    content_type = file.content_type or ""
    if content_type not in _ALLOWED_AVATAR_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type. Allowed: jpg, png",
        )

    ext = _ALLOWED_AVATAR_TYPES[content_type]

    data = await file.read()
    if len(data) > _MAX_AVATAR_SIZE:
        raise HTTPException(status_code=400, detail="File size exceeds 2MB limit.")

    avatar_path = _AVATAR_DIR / f"{user_id}{ext}"
    avatar_path.write_bytes(data)

    avatar_url = f"/uploads/avatars/{user_id}{ext}"
    user.avatar_url = avatar_url
    db.commit()

    return {
        "success": True,
        "avatar_url": avatar_url,
    }
