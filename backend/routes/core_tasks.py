"""Core task status API."""

from fastapi import APIRouter, Depends, HTTPException

from routes.core_auth import get_current_user
from services.database import get_db, get_task

router = APIRouter(prefix="/api/task", tags=["core-task"])


@router.get("/{task_id}")
async def get_task_status(task_id: str, _current_user=Depends(get_current_user)):
    db = next(get_db())
    try:
        task = get_task(db, task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found.")
        return {"task": task.to_dict()}
    finally:
        db.close()


@router.get("/{task_id}/progress")
async def get_task_progress(task_id: str, _current_user=Depends(get_current_user)):
    db = next(get_db())
    try:
        task = get_task(db, task_id)
        if task is None:
            raise HTTPException(status_code=404, detail="Task not found.")
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
    finally:
        db.close()
