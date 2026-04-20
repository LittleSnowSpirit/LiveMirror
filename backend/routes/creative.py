"""
广告素材路由接口
LiveMirror Ad Creative Routes

提供 RESTful API 用于广告素材管理、效果分析、A/B 测试等功能
"""

from typing import Optional, List
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from datetime import datetime
import uuid

from backend.services.ad_creative import (
    creative_service,
    AdCreative,
    CreativeStatus,
    ABTestStatus,
    CreativeMetrics
)

router = APIRouter(prefix="/api/creative", tags=["ad-creative"])


# ==================== Pydantic Models ====================

class CreativeUploadResponse(BaseModel):
    """素材上传响应"""
    success: bool
    creative_id: str
    message: str
    creative: dict


class CreativeListResponse(BaseModel):
    """素材列表响应"""
    success: bool
    total: int
    creatives: List[dict]


class CreativeAnalysisResponse(BaseModel):
    """素材分析响应"""
    success: bool
    creative_id: str
    analysis: dict


class ABTestCreateRequest(BaseModel):
    """A/B 测试创建请求"""
    name: str = Field(..., min_length=1, max_length=100)
    creative_ids: List[str] = Field(..., min_length=2)


class ABTestResponse(BaseModel):
    """A/B 测试响应"""
    success: bool
    test: dict


class MetricsUpdateRequest(BaseModel):
    """效果数据更新请求"""
    impressions: int = Field(default=0, ge=0)
    clicks: int = Field(default=0, ge=0)
    conversions: int = Field(default=0, ge=0)
    spend: float = Field(default=0.0, ge=0)
    revenue: float = Field(default=0.0, ge=0)


class CreativeScoreResponse(BaseModel):
    """素材评分响应"""
    creative_id: str
    score: float
    performance_level: str
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[dict]


# ==================== 素材管理接口 ====================

@router.post("/upload", response_model=CreativeUploadResponse)
async def upload_creative(
    name: str = Form(...),
    creative_type: str = Form(...),
    file: UploadFile = File(...),
    tags: Optional[str] = Form(None),
    metadata: Optional[str] = Form(None)
):
    """
    上传广告素材
    
    - **name**: 素材名称
    - **creative_type**: 素材类型 (image, video, carousel)
    - **file**: 素材文件
    - **tags**: 标签列表 (JSON 字符串)
    - **metadata**: 元数据 (JSON 字符串)
    """
    import json
    
    try:
        # 读取文件内容
        file_content = await file.read()
        file_size = len(file_content)
        
        # 解析标签和元数据
        tag_list = json.loads(tags) if tags else []
        meta_dict = json.loads(metadata) if metadata else {}
        
        # 模拟文件保存（实际项目中需要保存到存储系统）
        file_path = f"uploads/creatives/{uuid.uuid4()}_{file.filename}"
        
        # 模拟尺寸信息（实际需要从文件中提取）
        dimensions = {"width": 1080, "height": 1080}
        
        # 上传素材
        creative = creative_service.upload_creative(
            name=name,
            creative_type=creative_type,
            file_content=file_content,
            file_path=file_path,
            dimensions=dimensions,
            file_size=file_size,
            tags=tag_list,
            metadata=meta_dict
        )
        
        return CreativeUploadResponse(
            success=True,
            creative_id=creative.id,
            message="素材上传成功",
            creative=creative.to_dict()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"上传失败：{str(e)}")


@router.get("/list", response_model=CreativeListResponse)
async def list_creatives(
    status: Optional[str] = Query(None),
    creative_type: Optional[str] = Query(None),
    tags: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    获取素材列表
    
    - **status**: 筛选状态 (draft, active, paused, archived)
    - **creative_type**: 筛选类型
    - **tags**: 筛选标签
    - **limit**: 返回数量限制
    - **offset**: 偏移量
    """
    import json
    
    status_enum = CreativeStatus(status) if status else None
    tag_list = json.loads(tags) if tags else None
    
    creatives = creative_service.list_creatives(
        status=status_enum,
        creative_type=creative_type,
        tags=tag_list,
        limit=limit,
        offset=offset
    )
    
    return CreativeListResponse(
        success=True,
        total=len(creatives),
        creatives=[c.to_dict() for c in creatives]
    )


@router.get("/{creative_id}")
async def get_creative(creative_id: str):
    """获取单个素材详情"""
    creative = creative_service.get_creative(creative_id)
    
    if not creative:
        raise HTTPException(status_code=404, detail="素材不存在")
    
    return {
        "success": True,
        "creative": creative.to_dict()
    }


@router.put("/{creative_id}/status")
async def update_creative_status(
    creative_id: str,
    status: str = Form(...)
):
    """更新素材状态"""
    try:
        status_enum = CreativeStatus(status)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的状态值")
    
    success = creative_service.update_creative_status(creative_id, status_enum)
    
    if not success:
        raise HTTPException(status_code=404, detail="素材不存在")
    
    return {
        "success": True,
        "message": "状态更新成功",
        "creative_id": creative_id,
        "new_status": status
    }


@router.delete("/{creative_id}")
async def delete_creative(creative_id: str):
    """删除素材"""
    success = creative_service.delete_creative(creative_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="素材不存在")
    
    return {
        "success": True,
        "message": "素材已删除",
        "creative_id": creative_id
    }


# ==================== 效果分析接口 ====================

@router.post("/{creative_id}/metrics")
async def update_metrics(
    creative_id: str,
    metrics: MetricsUpdateRequest
):
    """更新素材效果数据"""
    success = creative_service.update_metrics(
        creative_id=creative_id,
        impressions=metrics.impressions,
        clicks=metrics.clicks,
        conversions=metrics.conversions,
        spend=metrics.spend,
        revenue=metrics.revenue
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="素材不存在")
    
    creative = creative_service.get_creative(creative_id)
    
    return {
        "success": True,
        "message": "效果数据更新成功",
        "metrics": creative.metrics.to_dict()
    }


@router.get("/{creative_id}/analyze", response_model=CreativeAnalysisResponse)
async def analyze_creative(creative_id: str):
    """
    分析单个素材效果
    
    返回详细的分析报告，包括：
    - 综合评分
    - 表现等级
    - 优势分析
    - 劣势分析
    - 优化建议
    """
    result = creative_service.analyze_creative(creative_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="素材不存在")
    
    return CreativeAnalysisResponse(
        success=True,
        creative_id=creative_id,
        analysis=result['analysis']
    )


@router.get("/{creative_id}/score")
async def get_creative_score(creative_id: str):
    """获取素材评分详情"""
    creative = creative_service.get_creative(creative_id)
    
    if not creative:
        raise HTTPException(status_code=404, detail="素材不存在")
    
    analysis = creative_service.analyze_creative(creative_id)
    
    return {
        "success": True,
        "creative_id": creative_id,
        "score": creative.calculate_score(),
        "performance_level": analysis['analysis']['performance_level'],
        "strengths": analysis['analysis']['strengths'],
        "weaknesses": analysis['analysis']['weaknesses'],
        "suggestions": analysis['analysis']['suggestions']
    }


@router.get("/top/recommended")
async def get_top_creatives(
    limit: int = Query(10, ge=1, le=50),
    min_impressions: int = Query(100, ge=0)
):
    """获取优秀素材推荐"""
    top_creatives = creative_service.get_top_creatives(
        limit=limit,
        min_impressions=min_impressions
    )
    
    return {
        "success": True,
        "total": len(top_creatives),
        "creatives": [c.to_dict() for c in top_creatives]
    }


@router.get("/export")
async def export_analytics(format: str = Query("json")):
    """导出分析数据"""
    data = creative_service.export_analytics(format=format)
    return JSONResponse(
        content=json.loads(data),
        media_type="application/json"
    )


# ==================== A/B 测试接口 ====================

@router.post("/ab-test", response_model=ABTestResponse)
async def create_ab_test(test_request: ABTestCreateRequest):
    """
    创建 A/B 测试
    
    - **name**: 测试名称
    - **creative_ids**: 参与测试的素材 ID 列表（至少 2 个）
    """
    try:
        ab_test = creative_service.create_ab_test(
            name=test_request.name,
            creative_ids=test_request.creative_ids
        )
        
        return ABTestResponse(
            success=True,
            test=ab_test.to_dict(creative_service.creatives)
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/ab-test/list")
async def list_ab_tests(status: Optional[str] = Query(None)):
    """获取 A/B 测试列表"""
    status_enum = ABTestStatus(status) if status else None
    tests = creative_service.list_ab_tests(status=status_enum)
    
    return {
        "success": True,
        "total": len(tests),
        "tests": [t.to_dict(creative_service.creatives) for t in tests]
    }


@router.get("/ab-test/{test_id}")
async def get_ab_test(test_id: str):
    """获取 A/B 测试详情"""
    test = creative_service.get_ab_test(test_id)
    
    if not test:
        raise HTTPException(status_code=404, detail="测试不存在")
    
    return {
        "success": True,
        "test": test.to_dict(creative_service.creatives)
    }


@router.post("/ab-test/{test_id}/complete")
async def complete_ab_test(test_id: str):
    """完成 A/B 测试并确定获胜者"""
    result = creative_service.complete_ab_test(test_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="测试不存在")
    
    return {
        "success": True,
        "message": "A/B 测试已完成",
        "test": result
    }


@router.get("/ab-test/{test_id}/analysis")
async def get_ab_test_analysis(test_id: str):
    """获取 A/B 测试分析报告"""
    result = creative_service.get_ab_test_analysis(test_id)
    
    if not result:
        raise HTTPException(status_code=404, detail="测试不存在")
    
    return {
        "success": True,
        "analysis": result
    }


# ==================== 批量操作接口 ====================

@router.post("/batch/metrics")
async def batch_update_metrics(metrics_list: List[dict]):
    """
    批量更新素材效果数据
    
    请求格式:
    [
        {"creative_id": "xxx", "impressions": 1000, "clicks": 50, ...},
        {"creative_id": "yyy", "impressions": 2000, "clicks": 100, ...}
    ]
    """
    results = []
    
    for item in metrics_list:
        creative_id = item.get('creative_id')
        if not creative_id:
            results.append({"success": False, "error": "缺少 creative_id"})
            continue
        
        success = creative_service.update_metrics(
            creative_id=creative_id,
            impressions=item.get('impressions', 0),
            clicks=item.get('clicks', 0),
            conversions=item.get('conversions', 0),
            spend=item.get('spend', 0.0),
            revenue=item.get('revenue', 0.0)
        )
        
        results.append({
            "success": success,
            "creative_id": creative_id
        })
    
    return {
        "success": True,
        "results": results,
        "total": len(results),
        "successful": sum(1 for r in results if r['success'])
    }


@router.get("/dashboard/summary")
async def get_dashboard_summary():
    """获取仪表板摘要数据"""
    all_creatives = list(creative_service.creatives.values())
    
    if not all_creatives:
        return {
            "success": True,
            "summary": {
                "total_creatives": 0,
                "active_creatives": 0,
                "total_impressions": 0,
                "total_clicks": 0,
                "total_conversions": 0,
                "total_spend": 0,
                "total_revenue": 0,
                "average_ctr": 0,
                "average_cvr": 0,
                "average_roas": 0,
                "top_performer": None
            }
        }
    
    total_impressions = sum(c.metrics.impressions for c in all_creatives)
    total_clicks = sum(c.metrics.clicks for c in all_creatives)
    total_conversions = sum(c.metrics.conversions for c in all_creatives)
    total_spend = sum(c.metrics.spend for c in all_creatives)
    total_revenue = sum(c.metrics.revenue for c in all_creatives)
    
    active_creatives = [c for c in all_creatives if c.status == CreativeStatus.ACTIVE]
    
    # 找出表现最好的素材
    top_performer = max(all_creatives, key=lambda c: c.calculate_score()) if all_creatives else None
    
    return {
        "success": True,
        "summary": {
            "total_creatives": len(all_creatives),
            "active_creatives": len(active_creatives),
            "total_impressions": total_impressions,
            "total_clicks": total_clicks,
            "total_conversions": total_conversions,
            "total_spend": round(total_spend, 2),
            "total_revenue": round(total_revenue, 2),
            "average_ctr": round(total_clicks / total_impressions, 4) if total_impressions > 0 else 0,
            "average_cvr": round(total_conversions / total_clicks, 4) if total_clicks > 0 else 0,
            "average_roas": round(total_revenue / total_spend, 2) if total_spend > 0 else 0,
            "top_performer": top_performer.to_dict() if top_performer else None
        }
    }
