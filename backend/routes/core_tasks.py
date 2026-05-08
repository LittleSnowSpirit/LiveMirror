"""Core task status API."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from routes.core_auth import get_current_user
from services.database import get_task

router = APIRouter(prefix="/api/task", tags=["core-task"])


@router.get("/{task_id}")
async def get_task_status(task_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    task = get_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found.")
    if task.user_id is not None and task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden.")
    return {"task": task.to_dict()}


@router.get("/{task_id}/progress")
async def get_task_progress(task_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    task = get_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found.")
    if task.user_id is not None and task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden.")
    return {
        "task_id": task.task_id,
        "status": task.status,
        "progress": task.progress,
        "current_step": task.current_step,
        "provider": task.provider,
        "started_at": task.started_at.isoformat() if task.started_at else None,
        "completed": task.status in {"completed", "failed"},
        "error_message": task.error_message,
    }
