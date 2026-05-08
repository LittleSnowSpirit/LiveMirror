"""Core report API."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from routes.core_auth import get_current_user
from services.database import get_task

router = APIRouter(prefix="/api/report", tags=["core-report"])


@router.get("/{task_id}")
async def get_report(task_id: str, db: Session = Depends(get_db), _current_user=Depends(get_current_user)):
    task = get_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found.")
    if task.status == "failed":
        raise HTTPException(status_code=400, detail=task.error_message or "Task failed.")
    if task.status != "completed":
        return {
            "success": False,
            "task": task.to_dict(),
            "message": "Task is still processing.",
        }

    report = task.report_data or {}
    return {
        "success": True,
        "data": report,
    }
