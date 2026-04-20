"""
LiveMirror 后端 API - 话术分析路由

提供直播话术分析的 HTTP API 接口
"""

import os
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

# 导入 AI 分析模块
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from ai_analysis import create_analyzer, LiveMirrorAnalyzer


# 创建路由
router = APIRouter(prefix="/analysis", tags=["话术分析"])

# 全局分析器实例（延迟初始化）
_analyzer: Optional[LiveMirrorAnalyzer] = None


def get_analyzer() -> LiveMirrorAnalyzer:
    """获取或创建分析器实例"""
    global _analyzer
    if _analyzer is None:
        api_key = os.getenv("DEEPSEEK_API_KEY")
        model = os.getenv("AI_MODEL", "deepseek-chat")
        _analyzer = create_analyzer(
            api_key=api_key,
            model=model,
            cost_optimization=True
        )
    return _analyzer


# 请求/响应模型
class DataChangePoint(BaseModel):
    """数据变化点"""
    timestamp: str = Field(..., description="时间戳 (HH:MM:SS)")
    type: str = Field(..., description="变化类型 (爆单/掉粉/涨粉/流失)")
    value: str = Field(..., description="变化值")
    description: Optional[str] = Field(None, description="描述")


class AnalysisRequest(BaseModel):
    """分析请求"""
    transcript: str = Field(..., description="直播转写稿全文")
    data_changes: Optional[List[DataChangePoint]] = Field(
        None, 
        description="数据变化点列表（可选）"
    )
    segment_duration: int = Field(
        45, 
        ge=30, 
        le=120, 
        description="分段时长（秒），默认 45 秒"
    )


class AnalysisResponse(BaseModel):
    """分析响应"""
    success: bool
    report: Dict[str, Any]
    message: str = "分析成功"


class AnalysisSummaryResponse(BaseModel):
    """分析摘要响应"""
    success: bool
    summary: Dict[str, Any]
    message: str = "获取成功"


# API 端点
@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_transcript(request: AnalysisRequest):
    """
    分析直播转写稿
    
    - **transcript**: 直播转写稿全文
    - **data_changes**: 数据变化点列表（可选）
    - **segment_duration**: 分段时长（秒）
    
    返回完整的分析报告，包括：
    - 话术分段
    - 爆点识别
    - 翻车识别
    - 归因分析
    - 优化建议
    """
    try:
        analyzer = get_analyzer()
        
        # 转换数据变化点格式
        data_changes = None
        if request.data_changes:
            data_changes = [
                {
                    "timestamp": dc.timestamp,
                    "type": dc.type,
                    "value": dc.value,
                    "description": dc.description
                }
                for dc in request.data_changes
            ]
        
        # 执行分析
        report = analyzer.analyze(
            transcript=request.transcript,
            data_changes=data_changes,
            segment_duration=request.segment_duration
        )
        
        return {
            "success": True,
            report: report,
            "message": "分析成功"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"分析失败：{str(e)}"
        )


@router.post("/analyze/summary", response_model=AnalysisSummaryResponse)
async def analyze_transcript_summary(request: AnalysisRequest):
    """
    分析直播转写稿（仅返回摘要）
    
    快速分析，只返回关键指标和洞察，不返回详细分段数据
    适用于列表页或快速预览场景
    """
    try:
        analyzer = get_analyzer()
        
        # 执行分析
        report = analyzer.analyze(
            transcript=request.transcript,
            data_changes=None,  # 摘要模式忽略数据变化
            segment_duration=request.segment_duration
        )
        
        # 提取摘要
        summary = {
            "metadata": report["metadata"],
            "summary": report["summary"]
        }
        
        return {
            "success": True,
            "summary": summary,
            "message": "分析成功"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"分析失败：{str(e)}"
        )


@router.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "analyzer_initialized": _analyzer is not None
    }


# 后台任务
async def background_analyze(
    task_id: str,
    transcript: str,
    data_changes: Optional[List[Dict]] = None
):
    """
    后台异步分析任务
    
    用于处理长转写稿，避免请求超时
    """
    try:
        analyzer = get_analyzer()
        report = analyzer.analyze(transcript, data_changes)
        
        # 保存结果到缓存/数据库
        # TODO: 实现结果存储
        
        return {"task_id": task_id, "status": "completed", "report": report}
        
    except Exception as e:
        return {"task_id": task_id, "status": "failed", "error": str(e)}


@router.post("/analyze/async")
async def analyze_transcript_async(
    request: AnalysisRequest,
    background_tasks: BackgroundTasks
):
    """
    异步分析直播转写稿
    
    适用于超长转写稿（>30 分钟）
    提交任务后立即返回 task_id，稍后查询结果
    """
    import uuid
    
    task_id = str(uuid.uuid4())
    
    # 转换数据变化点格式
    data_changes = None
    if request.data_changes:
        data_changes = [
            {
                "timestamp": dc.timestamp,
                "type": dc.type,
                "value": dc.value,
                "description": dc.description
            }
            for dc in request.data_changes
        ]
    
    # 添加后台任务
    background_tasks.add_task(
        background_analyze,
        task_id,
        request.transcript,
        data_changes
    )
    
    return {
        "success": True,
        "task_id": task_id,
        "message": "分析任务已提交，请稍后查询结果"
    }


@router.get("/analyze/task/{task_id}")
async def get_analysis_task(task_id: str):
    """
    查询异步分析任务状态
    
    TODO: 实现任务状态查询
    """
    # TODO: 从缓存/数据库查询任务状态
    return {
        "task_id": task_id,
        "status": "pending",
        "message": "任务状态查询功能开发中"
    }
