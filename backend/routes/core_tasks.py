"""Core task status API."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import AnalysisReport, Danmu, DanmuBatch
from routes.core_auth import get_current_user
from services.database import get_task

router = APIRouter(prefix="/api/task", tags=["core-task"])


def _check_task_owner(task, current_user):
    if task.user_id is not None and task.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden.")


@router.get("/{task_id}")
async def get_task_status(task_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    task = get_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found.")
    _check_task_owner(task, current_user)
    return {"task": task.to_dict()}


@router.get("/{task_id}/progress")
async def get_task_progress(task_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    task = get_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found.")
    _check_task_owner(task, current_user)
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


@router.delete("/{task_id}")
async def delete_task(task_id: str, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    task = get_task(db, task_id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found.")
    _check_task_owner(task, current_user)

    # 删除关联的分析报告、弹幕数据
    db.query(AnalysisReport).filter(AnalysisReport.task_id == task_id).delete()
    db.query(Danmu).filter(Danmu.batch_id == task_id).delete()
    db.query(DanmuBatch).filter(DanmuBatch.batch_id == task_id).delete()

    db.delete(task)
    return {"success": True, "task_id": task_id}
