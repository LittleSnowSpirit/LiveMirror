"""
Pydantic 模型定义（请求/响应 Schema）
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class TaskStatus(str, Enum):
    """任务状态枚举"""
    PENDING = "pending"
    PROCESSING = "processing"
    TRANSCRIBING = "transcribing"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"


# ============ 上传相关 ============

class UploadResponse(BaseModel):
    """上传响应"""
    task_id: str
    filename: str
    file_size: int
    status: str
    message: str = "文件上传成功，开始处理"


# ============ 任务查询相关 ============

class TaskInfo(BaseModel):
    """任务信息"""
    task_id: str
    filename: str
    file_size: int
    duration: Optional[float] = None
    status: str
    progress: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class TaskQueryResponse(BaseModel):
    """任务查询响应"""
    task: TaskInfo


# ============ 报告相关 ============

class SpeakingTechnique(BaseModel):
    """话术技巧"""
    name: str
    description: str
    timestamp: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)


class AttributionItem(BaseModel):
    """归因项"""
    factor: str
    impact: str
    evidence: str
    confidence: float = Field(ge=0.0, le=1.0)


class Suggestion(BaseModel):
    """改进建议"""
    category: str
    title: str
    description: str
    priority: str = Field(pattern="^(high|medium|low)$")


class ReportData(BaseModel):
    """报告数据"""
    task_id: str
    filename: str
    duration: Optional[float] = None
    
    # 转写结果
    transcription: Optional[str] = None
    segments: Optional[List[Dict[str, Any]]] = None
    
    # 话术分析
    speaking_techniques: Optional[List[SpeakingTechnique]] = None
    
    # 归因分析
    attribution_analysis: Optional[List[AttributionItem]] = None
    
    # 改进建议
    suggestions: Optional[List[Suggestion]] = None
    
    # 总结
    summary: Optional[str] = None
    
    created_at: datetime


class ReportResponse(BaseModel):
    """报告响应"""
    success: bool
    data: Optional[ReportData] = None
    error: Optional[str] = None


# ============ 错误响应 ============

class ErrorResponse(BaseModel):
    """错误响应"""
    success: bool = False
    error: str
    detail: Optional[str] = None
    task_id: Optional[str] = None
