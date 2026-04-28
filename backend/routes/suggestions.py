"""
话术优化建议 API 接口

功能：
- 话术问题诊断
- 生成改写示例
- 推荐优秀话术
"""

from fastapi import APIRouter, HTTPException, Query, Body, Depends
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from dataclasses import asdict

from services.suggestion_engine import (
    SuggestionEngine,
    analyze_speech,
    RewriteExample,
    ExcellentExample
)
from routes.core_auth import get_current_user

router = APIRouter(
    prefix="/api/suggestions",
    tags=["话术优化建议"],
    dependencies=[Depends(get_current_user)],
)


# ==================== 请求/响应模型 ====================

class SpeechInput(BaseModel):
    """话术输入"""
    id: str
    type: str
    content: str
    start_time: float
    end_time: float


class MetricsInput(BaseModel):
    """表现指标"""
    emotion_impact: Optional[float] = None
    engagement_rate: Optional[float] = None
    overall_score: Optional[float] = None


class SuggestionRequest(BaseModel):
    """建议请求"""
    speech: SpeechInput
    metrics: Optional[MetricsInput] = None


# ==================== API 接口 ====================

@router.post("/diagnose", response_model=Dict[str, Any], summary="诊断话术问题")
async def diagnose_speech_api(request: SuggestionRequest):
    """
    诊断单个话术的问题
    
    **功能**:
    - 节奏问题（过长/过短）
    - 情感表达（平淡/过度）
    - 互动元素（缺少引导）
    - 关键词使用（缺少促销词）
    - 逻辑结构（不完整）
    
    **返回**:
    - 问题列表（按严重程度排序）
    """
    try:
        engine = SuggestionEngine()
        
        speech_data = request.speech.dict()
        metrics = request.metrics.dict() if request.metrics else None
        
        issues = engine.diagnose_speech(speech_data, metrics)
        
        return {
            "success": True,
            "issues": [asdict(i) for i in issues],
            "count": len(issues)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"诊断失败：{str(e)}"
        )


@router.post("/rewrite", response_model=Dict[str, Any], summary="生成改写示例")
async def generate_rewrite_api(request: SuggestionRequest):
    """
    生成话术改写示例
    
    **功能**:
    - Before/After 对比
    - 改动说明
    - 预期效果提升
    
    **返回**:
    - 改写示例（如果有改进空间）
    """
    try:
        engine = SuggestionEngine()
        
        speech_data = request.speech.dict()
        metrics = request.metrics.dict() if request.metrics else None
        
        # 先诊断问题
        issues = engine.diagnose_speech(speech_data, metrics)
        
        # 生成改写
        rewrite = engine.generate_rewrite(speech_data, issues)
        
        if not rewrite:
            return {
                "success": True,
                "message": "当前话术已经很好，无需改进",
                "rewrite": None
            }
        
        return {
            "success": True,
            "rewrite": {
                "before": rewrite.before,
                "after": rewrite.after,
                "changes": rewrite.changes,
                "expected_improvement": rewrite.expected_improvement
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"改写失败：{str(e)}"
        )


@router.post("/analyze", response_model=Dict[str, Any], summary="完整分析")
async def analyze_speech_api(request: SuggestionRequest):
    """
    完整的话术分析
    
    **功能**:
    - 问题诊断
    - 优化建议
    - 改写示例
    - 优秀案例推荐
    
    **返回**:
    - 完整的分析报告
    """
    try:
        speech_data = request.speech.dict()
        metrics = request.metrics.dict() if request.metrics else None
        
        result = analyze_speech(speech_data, metrics)
        
        # 推荐优秀案例
        engine = SuggestionEngine()
        excellent_examples = engine.recommend_excellent_examples(
            speech_data.get('type', 'unknown'),
            limit=2
        )
        
        result['excellent_examples'] = [
            asdict(e) for e in excellent_examples
        ]
        
        return {
            "success": True,
            "data": result
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"分析失败：{str(e)}"
        )


@router.get("/excellent-examples", response_model=Dict[str, Any], summary="优秀话术推荐")
async def get_excellent_examples_api(
    speech_type: str = Query(..., description="话术类型"),
    limit: int = Query(3, ge=1, le=10, description="返回数量")
):
    """
    推荐优秀话术示例
    
    **话术类型**:
    - opening: 开场白
    - product_intro: 产品介绍
    - price_promotion: 价格优惠
    - limited_offer: 限时限量
    - closing: 促单成交
    """
    try:
        engine = SuggestionEngine()
        examples = engine.recommend_excellent_examples(speech_type, limit)
        
        return {
            "success": True,
            "examples": [asdict(e) for e in examples],
            "count": len(examples)
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取失败：{str(e)}"
        )


@router.post("/batch-analyze", response_model=Dict[str, Any], summary="批量分析")
async def batch_analyze_api(
    speeches: List[SpeechInput] = Body(..., description="话术列表"),
    metrics_list: Optional[List[MetricsInput]] = Body(None, description="指标列表")
):
    """
    批量分析多个话术
    
    **返回**:
    - 每个话术的分析结果
    - 汇总统计
    """
    try:
        results = []
        total_issues = 0
        high_priority_count = 0
        
        for i, speech in enumerate(speeches):
            metrics = metrics_list[i].dict() if metrics_list and i < len(metrics_list) else None
            
            result = analyze_speech(speech.dict(), metrics)
            results.append({
                "speech_id": speech.id,
                "analysis": result
            })
            
            total_issues += len(result['issues'])
            high_priority_count += sum(
                1 for s in result['suggestions'] if s.priority == 'high'
            )
        
        return {
            "success": True,
            "results": results,
            "summary": {
                "total_speeches": len(speeches),
                "total_issues": total_issues,
                "high_priority_issues": high_priority_count
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"批量分析失败：{str(e)}"
        )


# ==================== 健康检查 ====================

@router.get("/health", summary="健康检查")
async def health_check():
    """检查建议生成服务状态"""
    return {
        "status": "healthy",
        "service": "suggestion_engine"
    }
