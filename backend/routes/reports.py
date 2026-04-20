"""
报告数据接口
"""
from fastapi import APIRouter, Path, HTTPException
from fastapi.responses import JSONResponse
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from schemas import ReportResponse, ReportData, ErrorResponse
from services.database import get_db

router = APIRouter(prefix="/api/report", tags=["报告"])


@router.get("/{task_id}", response_model=ReportResponse)
async def get_report(task_id: str = Path(..., description="任务 ID")):
    """
    获取分析报告
    
    - **task_id**: 任务 ID
    - **返回**: 完整的分析报告数据
    
    报告包含：
    - 转写文字稿
    - 话术技巧分析
    - 归因分析
    - 改进建议
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
        
        # 检查任务是否完成
        if task.status == "pending" or task.status == "processing":
            return JSONResponse(
                status_code=400,
                content=ErrorResponse(
                    error="任务未完成",
                    detail=f"任务状态：{task.status}，进度：{task.progress}%",
                    task_id=task_id
                ).model_dump()
            )
        
        if task.status == "failed":
            return JSONResponse(
                status_code=400,
                content=ErrorResponse(
                    error="任务失败",
                    detail=task.error_message,
                    task_id=task_id
                ).model_dump()
            )
        
        # 构建报告数据
        report_data = task.report_data
        if not report_data:
            # 兼容旧数据格式
            report_data = {
                'task_id': task.task_id,
                'filename': task.filename,
                'duration': task.duration,
                'transcription': task.transcription,
                'segments': task.transcription_segments,
                'speaking_techniques': task.analysis_result.get('speaking_techniques', []) if task.analysis_result else [],
                'attribution_analysis': task.analysis_result.get('attribution_analysis', []) if task.analysis_result else [],
                'suggestions': task.analysis_result.get('suggestions', []) if task.analysis_result else [],
                'summary': task.analysis_result.get('summary', '') if task.analysis_result else '',
                'created_at': task.created_at.isoformat() if task.created_at else None
            }
        
        return ReportResponse(
            success=True,
            data=ReportData(**report_data)
        )
        
    finally:
        db.close()


@router.get("/{task_id}/transcription")
async def get_transcription(task_id: str = Path(..., description="任务 ID")):
    """
    仅获取转写文字稿
    
    适合只需要文字稿的场景
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
        
        if task.status in ["pending", "processing", "transcribing"]:
            return JSONResponse(
                status_code=400,
                content={"error": "转写未完成", "status": task.status, "progress": task.progress}
            )
        
        return {
            "task_id": task.task_id,
            "filename": task.filename,
            "transcription": task.transcription,
            "segments": task.transcription_segments,
            "duration": task.duration
        }
        
    finally:
        db.close()


@router.get("/{task_id}/analysis")
async def get_analysis(task_id: str = Path(..., description="任务 ID")):
    """
    仅获取分析结果（话术 + 归因）
    
    适合已获取转写文字稿，只需要分析结果的场景
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
        
        if task.status not in ["completed"]:
            return JSONResponse(
                status_code=400,
                content={"error": "分析未完成", "status": task.status, "progress": task.progress}
            )
        
        analysis = task.analysis_result or {}
        return {
            "task_id": task.task_id,
            "speaking_techniques": analysis.get('speaking_techniques', []),
            "attribution_analysis": analysis.get('attribution_analysis', []),
            "suggestions": analysis.get('suggestions', []),
            "summary": analysis.get('summary', '')
        }
        
    finally:
        db.close()
