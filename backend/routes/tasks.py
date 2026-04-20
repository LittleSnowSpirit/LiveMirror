"""
任务查询接口
"""
from fastapi import APIRouter, HTTPException, Path
from fastapi.responses import JSONResponse
from typing import Optional
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from schemas import TaskQueryResponse, TaskInfo, ErrorResponse
from services.database import get_db

router = APIRouter(prefix="/api/task", tags=["任务"])


@router.get("/{task_id}", response_model=TaskQueryResponse)
async def get_task_status(task_id: str = Path(..., description="任务 ID")):
    """
    查询任务状态
    
    - **task_id**: 任务 ID（上传时返回）
    - **返回**: 任务当前状态和进度
    """
    db = next(get_db())
    try:
        from models import Task
        task = db.query(Task).filter(Task.task_id == task_id).first()
        
        if not task:
            return JSONResponse(
                status_code=404,
                content=ErrorResponse(
                    error="任务不存在",
                    detail=f"未找到任务：{task_id}"
                ).model_dump()
            )
        
        return TaskQueryResponse(
            task=TaskInfo(
                task_id=task.task_id,
                filename=task.filename,
                file_size=task.file_size,
                duration=task.duration,
                status=task.status,
                progress=task.progress,
                created_at=task.created_at,
                updated_at=task.updated_at,
                completed_at=task.completed_at,
                error_message=task.error_message
            )
        )
    finally:
        db.close()


@router.get("/{task_id}/progress")
async def get_task_progress(task_id: str = Path(..., description="任务 ID")):
    """
    获取任务进度（简化版）
    
    返回纯进度信息，适合轮询
    """
    db = next(get_db())
    try:
        from models import Task
        task = db.query(Task).filter(Task.task_id == task_id).first()
        
        if not task:
            return JSONResponse(
                status_code=404,
                content={"error": "任务不存在"}
            )
        
        return {
            "task_id": task.task_id,
            "status": task.status,
            "progress": task.progress,
            "completed": task.status == "completed" or task.status == "failed"
        }
    finally:
        db.close()
