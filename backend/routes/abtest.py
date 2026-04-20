"""
LiveMirror A/B 测试 API 路由
提供 RESTful 接口用于话术 A/B 测试管理
"""

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime

from ..services.ab_testing import ab_testing_service, ScriptVariant, TestConfig


router = APIRouter(prefix="/api/abtest", tags=["A/B 测试"])


# ========== 请求/响应模型 ==========

class CreateVariantRequest(BaseModel):
    """创建话术变体请求"""
    test_id: str
    version: str = Field(..., description="版本标识 (A/B/C)")
    content: str = Field(..., description="话术内容")


class VariantResponse(BaseModel):
    """话术变体响应"""
    id: str
    version: str
    content: str
    created_at: str
    is_active: bool


class CreateTestRequest(BaseModel):
    """创建测试请求"""
    name: str = Field(..., description="测试名称")
    traffic_allocation: Dict[str, float] = Field(
        ..., 
        description="流量分配，如 {'A': 0.5, 'B': 0.5}",
        example={"A": 0.5, "B": 0.5}
    )


class TestResponse(BaseModel):
    """测试配置响应"""
    test_id: str
    name: str
    variants: Dict[str, float]
    start_time: str
    end_time: Optional[str]
    is_active: bool


class UpdateTrafficRequest(BaseModel):
    """更新流量分配请求"""
    traffic_allocation: Dict[str, float]


class RecordEventRequest(BaseModel):
    """记录事件请求"""
    test_id: str
    version: str
    user_id: str


class MetricsResponse(BaseModel):
    """指标响应"""
    version: str
    impressions: int
    clicks: int
    conversions: int
    interactions: int
    watch_time_seconds: float
    click_rate: float
    conversion_rate: float
    interaction_rate: float
    avg_watch_time: float


class ComparisonResponse(BaseModel):
    """版本对比响应"""
    test_id: str
    comparison: Dict[str, Dict]


class SignificanceTestRequest(BaseModel):
    """显著性检验请求"""
    test_id: str
    metric: str = Field(default="conversion_rate", description="检验指标")


class SignificanceResponse(BaseModel):
    """显著性检验响应"""
    is_significant: bool
    p_value: float
    confidence_level: float
    winner: Optional[str]
    improvement: float


class RecommendationResponse(BaseModel):
    """推荐结果响应"""
    recommendation: str
    winning_version: Optional[str]
    content: Optional[str]
    improvement: Optional[str]
    confidence: Optional[str]
    message: Optional[str]


class ReportResponse(BaseModel):
    """测试报告响应"""
    test_id: str
    test_name: str
    status: str
    duration: Dict
    traffic_allocation: Dict[str, float]
    variants: List[Dict]
    comparison: Dict
    statistical_test: Dict
    recommendation: Optional[Dict]


# ========== 话术版本管理 ==========

@router.post("/variants", response_model=VariantResponse, summary="创建话术变体")
async def create_variant(request: CreateVariantRequest):
    """创建新的话术变体"""
    try:
        variant = ab_testing_service.create_variant(
            test_id=request.test_id,
            version=request.version,
            content=request.content
        )
        return VariantResponse(
            id=variant.id,
            version=variant.version,
            content=variant.content,
            created_at=variant.created_at.isoformat(),
            is_active=variant.is_active
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/variants/{test_id}", response_model=List[VariantResponse], summary="获取话术变体列表")
async def list_variants(test_id: str):
    """获取指定测试的所有话术变体"""
    variants = ab_testing_service.list_variants(test_id)
    return [
        VariantResponse(
            id=v.id,
            version=v.version,
            content=v.content,
            created_at=v.created_at.isoformat(),
            is_active=v.is_active
        )
        for v in variants
    ]


@router.get("/variants/{test_id}/{version}", response_model=VariantResponse, summary="获取话术变体")
async def get_variant(test_id: str, version: str):
    """获取指定版本的话术"""
    variant = ab_testing_service.get_variant(test_id, version)
    if not variant:
        raise HTTPException(status_code=404, detail="话术变体不存在")
    
    return VariantResponse(
        id=variant.id,
        version=variant.version,
        content=variant.content,
        created_at=variant.created_at.isoformat(),
        is_active=variant.is_active
    )


@router.put("/variants/{test_id}/{version}", response_model=VariantResponse, summary="更新话术变体")
async def update_variant(test_id: str, version: str, content: str = Body(..., embed=True)):
    """更新话术内容"""
    variant = ab_testing_service.update_variant(test_id, version, content)
    if not variant:
        raise HTTPException(status_code=404, detail="话术变体不存在")
    
    return VariantResponse(
        id=variant.id,
        version=variant.version,
        content=variant.content,
        created_at=variant.created_at.isoformat(),
        is_active=variant.is_active
    )


@router.delete("/variants/{test_id}/{version}", summary="停用话术变体")
async def deactivate_variant(test_id: str, version: str):
    """停用指定版本的话术"""
    success = ab_testing_service.deactivate_variant(test_id, version)
    if not success:
        raise HTTPException(status_code=404, detail="话术变体不存在")
    
    return {"message": "话术变体已停用"}


# ========== A/B 测试配置 ==========

@router.post("/tests", response_model=TestResponse, summary="创建 A/B 测试")
async def create_test(request: CreateTestRequest):
    """创建新的 A/B 测试"""
    try:
        config = ab_testing_service.create_test(
            name=request.name,
            traffic_allocation=request.traffic_allocation
        )
        return TestResponse(
            test_id=config.test_id,
            name=config.name,
            variants=config.variants,
            start_time=config.start_time.isoformat(),
            end_time=None,
            is_active=config.is_active
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/tests/{test_id}", response_model=TestResponse, summary="获取测试配置")
async def get_test(test_id: str):
    """获取测试配置"""
    config = ab_testing_service.get_test(test_id)
    if not config:
        raise HTTPException(status_code=404, detail="测试不存在")
    
    return TestResponse(
        test_id=config.test_id,
        name=config.name,
        variants=config.variants,
        start_time=config.start_time.isoformat(),
        end_time=config.end_time.isoformat() if config.end_time else None,
        is_active=config.is_active
    )


@router.put("/tests/{test_id}/traffic", response_model=TestResponse, summary="更新流量分配")
async def update_traffic(test_id: str, request: UpdateTrafficRequest):
    """更新测试的流量分配"""
    try:
        success = ab_testing_service.update_traffic_allocation(
            test_id,
            request.traffic_allocation
        )
        if not success:
            raise HTTPException(status_code=404, detail="测试不存在")
        
        config = ab_testing_service.get_test(test_id)
        return TestResponse(
            test_id=config.test_id,
            name=config.name,
            variants=config.variants,
            start_time=config.start_time.isoformat(),
            end_time=config.end_time.isoformat() if config.end_time else None,
            is_active=config.is_active
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/tests/{test_id}/stop", response_model=TestResponse, summary="停止测试")
async def stop_test(test_id: str):
    """停止正在进行的测试"""
    success = ab_testing_service.stop_test(test_id)
    if not success:
        raise HTTPException(status_code=404, detail="测试不存在")
    
    config = ab_testing_service.get_test(test_id)
    return TestResponse(
        test_id=config.test_id,
        name=config.name,
        variants=config.variants,
        start_time=config.start_time.isoformat(),
        end_time=config.end_time.isoformat() if config.end_time else None,
        is_active=config.is_active
    )


# ========== 流量分配 ==========

@router.post("/assign", summary="分配用户到测试版本")
async def assign_user(test_id: str = Query(...), user_id: str = Query(...)):
    """为用户分配测试版本"""
    version = ab_testing_service.assign_user(test_id, user_id)
    if not version:
        raise HTTPException(status_code=404, detail="测试不存在或已停止")
    
    return {
        "test_id": test_id,
        "user_id": user_id,
        "assigned_version": version
    }


@router.get("/assignment/{user_id}", summary="获取用户分配版本")
async def get_assignment(user_id: str, test_id: str = Query(...)):
    """获取用户已分配的版本"""
    version = ab_testing_service.get_assigned_version(user_id)
    if not version:
        raise HTTPException(status_code=404, detail="用户未分配")
    
    return {
        "user_id": user_id,
        "test_id": test_id,
        "version": version
    }


# ========== 效果数据记录 ==========

@router.post("/events/impression", summary="记录曝光事件")
async def record_impression(request: RecordEventRequest):
    """记录话术曝光"""
    ab_testing_service.record_impression(request.test_id, request.version, request.user_id)
    return {"status": "success", "event": "impression"}


@router.post("/events/click", summary="记录点击事件")
async def record_click(request: RecordEventRequest):
    """记录点击"""
    ab_testing_service.record_click(request.test_id, request.version, request.user_id)
    return {"status": "success", "event": "click"}


@router.post("/events/conversion", summary="记录转化事件")
async def record_conversion(request: RecordEventRequest):
    """记录转化"""
    ab_testing_service.record_conversion(request.test_id, request.version, request.user_id)
    return {"status": "success", "event": "conversion"}


@router.post("/events/interaction", summary="记录互动事件")
async def record_interaction(request: RecordEventRequest):
    """记录互动"""
    ab_testing_service.record_interaction(request.test_id, request.version, request.user_id)
    return {"status": "success", "event": "interaction"}


@router.post("/events/watch_time", summary="记录观看时长")
async def record_watch_time(
    test_id: str = Query(...),
    version: str = Query(...),
    user_id: str = Query(...),
    seconds: float = Query(...)
):
    """记录观看时长"""
    ab_testing_service.record_watch_time(test_id, version, user_id, seconds)
    return {"status": "success", "event": "watch_time", "seconds": seconds}


# ========== 效果对比分析 ==========

@router.get("/metrics/{test_id}/{version}", response_model=MetricsResponse, summary="获取版本指标")
async def get_metrics(test_id: str, version: str):
    """获取指定版本的详细指标"""
    metrics = ab_testing_service.get_metrics(test_id, version)
    if not metrics:
        raise HTTPException(status_code=404, detail="版本指标不存在")
    
    rates = ab_testing_service.calculate_rates(metrics)
    return MetricsResponse(
        version=metrics.version,
        impressions=metrics.impressions,
        clicks=metrics.clicks,
        conversions=metrics.conversions,
        interactions=metrics.interactions,
        watch_time_seconds=metrics.watch_time_seconds,
        click_rate=rates["click_rate"],
        conversion_rate=rates["conversion_rate"],
        interaction_rate=rates["interaction_rate"],
        avg_watch_time=rates["avg_watch_time"]
    )


@router.get("/compare/{test_id}", response_model=ComparisonResponse, summary="对比版本效果")
async def compare_versions(test_id: str):
    """对比所有版本的效果"""
    comparison = ab_testing_service.compare_versions(test_id)
    if not comparison:
        raise HTTPException(status_code=404, detail="测试不存在")
    
    return ComparisonResponse(
        test_id=test_id,
        comparison=comparison
    )


# ========== 统计显著性检验 ==========

@router.post("/significance", response_model=SignificanceResponse, summary="统计显著性检验")
async def test_significance(request: SignificanceTestRequest):
    """执行统计显著性检验"""
    result = ab_testing_service.test_significance(
        test_id=request.test_id,
        metric=request.metric
    )
    return SignificanceResponse(
        is_significant=result.is_significant,
        p_value=result.p_value,
        confidence_level=result.confidence_level,
        winner=result.winner,
        improvement=result.improvement
    )


# ========== 优胜话术推荐 ==========

@router.get("/recommend/{test_id}", response_model=RecommendationResponse, summary="获取优胜推荐")
async def recommend_winner(test_id: str):
    """获取优胜话术推荐"""
    result = ab_testing_service.recommend_winner(test_id)
    if not result:
        raise HTTPException(status_code=404, detail="测试不存在")
    
    return RecommendationResponse(**result)


# ========== 测试报告生成 ==========

@router.get("/report/{test_id}", response_model=ReportResponse, summary="获取测试报告")
async def get_report(test_id: str):
    """获取完整的测试报告"""
    report = ab_testing_service.generate_report(test_id)
    if "error" in report:
        raise HTTPException(status_code=404, detail=report["error"])
    
    return ReportResponse(**report)


@router.get("/report/{test_id}/export", summary="导出测试报告")
async def export_report(
    test_id: str,
    format: str = Query(default="json", description="导出格式：json 或 markdown")
):
    """导出测试报告"""
    try:
        content = ab_testing_service.export_report(test_id, format)
        return {
            "test_id": test_id,
            "format": format,
            "content": content
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
