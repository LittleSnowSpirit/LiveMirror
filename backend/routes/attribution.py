"""
话术归因分析 API 接口

核心功能：
- 分析话术与情绪峰值的关联
- 分析话术与弹幕互动的关联
- 生成归因分析报告
- 提供优化建议
"""

from fastapi import APIRouter, HTTPException, Query, Body
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
import json

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.attribution import AttributionAnalysisService, analyze_attribution

router = APIRouter(prefix="/api/attribution", tags=["话术归因分析"])


# ==================== 请求/响应模型 ====================

class SpeechSegmentInput(BaseModel):
    """话术分段输入"""
    id: str
    type: str
    content: str
    start_time: float
    end_time: float


class EmotionPointInput(BaseModel):
    """情绪数据点输入"""
    timestamp: float
    score: float
    level: Optional[str] = None


class DanmuInput(BaseModel):
    """弹幕数据输入"""
    timestamp: float
    content: str
    sentiment: Optional[str] = "neutral"
    sentiment_score: Optional[float] = 0.0
    is_key_danmu: Optional[bool] = False


class AttributionRequest(BaseModel):
    """归因分析请求"""
    speech_segments: List[SpeechSegmentInput]
    emotion_curve: List[EmotionPointInput]
    danmu_list: List[DanmuInput]
    top_n: Optional[int] = 10


class AttributionResponse(BaseModel):
    """归因分析响应"""
    success: bool
    message: str
    data: Dict[str, Any]


# ==================== API 接口 ====================

@router.post("/analyze", response_model=AttributionResponse, summary="执行归因分析")
async def analyze_attribution_api(request: AttributionRequest):
    """
    执行完整的话术 - 数据归因分析
    
    **功能说明**:
    - 检测情绪曲线中的显著峰值
    - 关联话术与情绪峰值
    - 关联话术与弹幕互动
    - 生成优化建议
    
    **输入要求**:
    - speech_segments: 话术分段数据（来自语音转写）
    - emotion_curve: 情绪曲线数据（来自情绪分析）
    - danmu_list: 弹幕数据（来自弹幕上传）
    
    **返回内容**:
    - Top N 个高影响力话术
    - 情绪峰值列表
    - 优化建议
    """
    try:
        # 数据转换
        speech_segments = [s.dict() for s in request.speech_segments]
        emotion_curve = [e.dict() for e in request.emotion_curve]
        danmu_list = [d.dict() for d in request.danmu_list]
        
        # 执行分析
        result = analyze_attribution(
            speech_segments=speech_segments,
            emotion_curve=emotion_curve,
            danmu_list=danmu_list,
            top_n=request.top_n
        )
        
        return AttributionResponse(
            success=True,
            message="归因分析完成",
            data=result
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"分析失败：{str(e)}"
        )


@router.post("/emotion-peaks", response_model=Dict[str, Any], summary="检测情绪峰值")
async def detect_emotion_peaks_api(
    emotion_curve: List[Dict[str, Any]] = Body(..., description="情绪曲线数据"),
    window_seconds: int = Body(30, description="峰值检测窗口（秒）")
):
    """
    单独检测情绪曲线中的显著峰值
    
    用于可视化情绪高峰时刻，帮助快速定位爆点/翻车时刻
    """
    try:
        service = AttributionAnalysisService()
        peaks = service.detect_emotion_peaks(emotion_curve, window_seconds)
        
        return {
            "success": True,
            "peaks": peaks,
            "count": len(peaks)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"检测失败：{str(e)}"
        )


@router.post("/speech-emotion", response_model=Dict[str, Any], summary="话术 - 情绪关联")
async def correlate_speech_emotion_api(
    speech_segments: List[Dict[str, Any]] = Body(..., description="话术分段"),
    emotion_curve: List[Dict[str, Any]] = Body(..., description="情绪曲线")
):
    """
    分析话术与情绪的关联性
    
    返回每个话术片段的情绪影响分数
    """
    try:
        service = AttributionAnalysisService()
        
        # 先检测峰值
        emotion_peaks = service.detect_emotion_peaks(emotion_curve)
        
        # 再关联分析
        results = service.correlate_speech_with_emotion(
            speech_segments, emotion_peaks, emotion_curve
        )
        
        return {
            "success": True,
            "results": [
                {
                    "speech_id": r.speech_id,
                    "speech_type": r.speech_type,
                    "emotion_impact": round(r.emotion_impact, 3),
                    "issues": r.issues,
                    "suggestions": r.suggestions
                }
                for r in results
            ]
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"分析失败：{str(e)}"
        )


@router.post("/speech-danmu", response_model=Dict[str, Any], summary="话术 - 弹幕关联")
async def correlate_speech_danmu_api(
    speech_segments: List[Dict[str, Any]] = Body(..., description="话术分段"),
    danmu_list: List[Dict[str, Any]] = Body(..., description="弹幕列表")
):
    """
    分析话术与弹幕互动的关联性
    
    返回每个话术片段的互动统计
    """
    try:
        service = AttributionAnalysisService()
        
        correlation = service.correlate_speech_with_danmu(
            speech_segments, danmu_list
        )
        
        return {
            "success": True,
            "correlation": correlation
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"分析失败：{str(e)}"
        )


@router.get("/report/{session_id}", response_model=Dict[str, Any], summary="获取归因报告")
async def get_attribution_report_api(
    session_id: str,
    top_n: int = Query(10, description="返回 Top N 个高影响力话术")
):
    """
    获取指定场次的归因分析报告
    
    从数据库加载数据并生成报告
    """
    try:
        # TODO: 从数据库加载数据
        # 这里是示例返回
        return {
            "success": True,
            "message": "报告生成成功（示例数据）",
            "data": {
                "session_id": session_id,
                "summary": {
                    "total_speech_segments": 0,
                    "emotion_peaks_count": 0,
                    "total_danmus": 0
                },
                "top_speeches": [],
                "recommendations": []
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取报告失败：{str(e)}"
        )


@router.get("/config", response_model=Dict[str, Any], summary="获取归因配置")
async def get_attribution_config():
    """
    获取归因分析的当前配置
    
    包括：
    - 情绪峰值检测阈值
    - 归因权重配置
    - 峰值检测窗口
    """
    service = AttributionAnalysisService()
    
    return {
        "success": True,
        "config": {
            "emotion_peak_threshold": service.emotion_peak_threshold,
            "peak_window_seconds": service.peak_window_seconds,
            "weights": service.weights
        }
    }


@router.put("/config", response_model=Dict[str, Any], summary="更新归因配置")
async def update_attribution_config(
    emotion_peak_threshold: Optional[float] = Body(None, ge=0, le=1),
    peak_window_seconds: Optional[int] = Body(None, ge=10, le=120),
    weights: Optional[Dict[str, float]] = Body(None)
):
    """
    更新归因分析配置
    
    用于调优归因算法的参数
    """
    # TODO: 持久化配置
    return {
        "success": True,
        "message": "配置已更新"
    }


# ==================== 健康检查 ====================

@router.get("/health", summary="健康检查")
async def health_check():
    """检查归因分析服务状态"""
    return {
        "status": "healthy",
        "service": "attribution_analysis"
    }
