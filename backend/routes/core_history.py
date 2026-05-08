"""History API — paginated task history with filtering."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from models import Task
from routes.core_auth import get_current_user

router = APIRouter(prefix="/api/history", tags=["core-history"])


@router.get("")
async def list_history(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str | None = Query(None),
    search: str | None = Query(None),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    query = db.query(Task).filter(Task.user_id == current_user.id)

    if status:
        query = query.filter(Task.status == status)
    if search:
        escaped = search.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        query = query.filter(Task.filename.ilike(f"%{escaped}%", escape="\\"))

    total = query.count()
    items = (
        query.order_by(Task.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return {
        "success": True,
        "items": [
            {
                "task_id": t.task_id,
                "filename": t.filename,
                "status": t.status,
                "progress": t.progress,
                "file_size": t.file_size,
                "duration": t.duration,
                "created_at": t.created_at.isoformat() if t.created_at else None,
                "completed_at": t.completed_at.isoformat() if t.completed_at else None,
            }
            for t in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
    }
