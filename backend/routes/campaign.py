"""
营销活动策划 API 接口
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Optional, Any
from pydantic import BaseModel
from datetime import datetime

# 导入服务
import sys
sys.path.append('..')
from services.campaign import (
    campaign_service,
    Campaign,
    CampaignTemplate,
    CaseStudy,
    CampaignStatus,
    CampaignType
)

router = APIRouter(prefix="/api/campaigns", tags=["营销活动"])


# ========== Pydantic 模型 ==========

class CampaignCreate(BaseModel):
    name: str
    description: str = ""
    campaign_type: str = "promotion"
    status: str = "draft"
    start_date: str
    end_date: str
    budget_items: List[Dict] = []
    timeline: List[Dict] = []
    metrics: List[Dict] = []
    notes: str = ""
    tags: List[str] = []


class CampaignUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None
    budget_items: Optional[List[Dict]] = None
    timeline: Optional[List[Dict]] = None
    metrics: Optional[List[Dict]] = None
    notes: Optional[str] = None
    tags: Optional[List[str]] = None


class MetricUpdate(BaseModel):
    metrics: List[Dict]


class TimelineGenerate(BaseModel):
    campaign_type: str
    start_date: str
    duration_days: int


class BudgetCalculation(BaseModel):
    budget_items: List[Dict]


class ROIEstimation(BaseModel):
    campaign_type: str
    budget: float
    industry_avg: Optional[float] = None


class CaseStudyCreate(BaseModel):
    title: str
    campaign_type: str
    industry: str
    description: str
    objectives: List[str] = []
    strategies: List[str] = []
    results: Dict[str, Any] = {}
    budget: float = 0
    roi: float = 0
    duration_days: int = 0
    key_learnings: List[str] = []


# ========== 模板接口 ==========

@router.get("/templates", response_model=List[Dict])
async def get_templates():
    """获取所有活动策划模板"""
    templates = campaign_service.get_templates()
    return [template.__dict__ for template in templates]


@router.get("/templates/{template_id}", response_model=Dict)
async def get_template(template_id: str):
    """获取指定模板详情"""
    template = campaign_service.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    return template.__dict__


@router.get("/templates/type/{campaign_type}", response_model=Dict)
async def get_template_by_type(campaign_type: str):
    """根据活动类型获取模板"""
    template = campaign_service.get_template_by_type(campaign_type)
    if not template:
        raise HTTPException(status_code=404, detail="该类型模板不存在")
    return template.__dict__


# ========== 活动管理接口 ==========

@router.post("", response_model=Dict)
async def create_campaign(campaign_data: CampaignCreate):
    """创建新营销活动"""
    campaign = campaign_service.create_campaign(campaign_data.dict())
    return {"success": True, "campaign": campaign.__dict__}


@router.get("", response_model=List[Dict])
async def get_campaigns(status: Optional[str] = Query(None)):
    """获取所有活动（可按状态筛选）"""
    campaigns = campaign_service.get_all_campaigns(status=status)
    return [c.__dict__ for c in campaigns]


@router.get("/{campaign_id}", response_model=Dict)
async def get_campaign(campaign_id: str):
    """获取指定活动详情"""
    campaign = campaign_service.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="活动不存在")
    return campaign.__dict__


@router.put("/{campaign_id}", response_model=Dict)
async def update_campaign(campaign_id: str, campaign_data: CampaignUpdate):
    """更新活动"""
    update_data = {k: v for k, v in campaign_data.dict().items() if v is not None}
    campaign = campaign_service.update_campaign(campaign_id, update_data)
    if not campaign:
        raise HTTPException(status_code=404, detail="活动不存在")
    return {"success": True, "campaign": campaign.__dict__}


@router.delete("/{campaign_id}", response_model=Dict)
async def delete_campaign(campaign_id: str):
    """删除活动"""
    success = campaign_service.delete_campaign(campaign_id)
    if not success:
        raise HTTPException(status_code=404, detail="活动不存在")
    return {"success": True}


@router.patch("/{campaign_id}/status", response_model=Dict)
async def update_campaign_status(campaign_id: str, status: str):
    """更新活动状态"""
    valid_statuses = [s.value for s in CampaignStatus]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"无效状态，可选：{valid_statuses}")
    
    campaign = campaign_service.update_campaign_status(campaign_id, status)
    if not campaign:
        raise HTTPException(status_code=404, detail="活动不存在")
    return {"success": True, "campaign": campaign.__dict__}


# ========== 时间规划接口 ==========

@router.post("/timeline/generate", response_model=List[Dict])
async def generate_timeline(data: TimelineGenerate):
    """生成活动时间规划"""
    phases = campaign_service.generate_timeline(
        data.campaign_type,
        data.start_date,
        data.duration_days
    )
    return [p.__dict__ for p in phases]


# ========== 预算和 ROI 接口 ==========

@router.post("/budget/calculate", response_model=Dict)
async def calculate_budget(data: BudgetCalculation):
    """计算预算总计"""
    result = campaign_service.calculate_budget_total(data.budget_items)
    return result


@router.post("/roi/calculate", response_model=Dict)
async def calculate_roi(revenue: float, cost: float):
    """计算 ROI"""
    return campaign_service.calculate_roi(revenue, cost)


@router.post("/roi/estimate", response_model=Dict)
async def estimate_roi(data: ROIEstimation):
    """预估 ROI"""
    return campaign_service.estimate_roi(
        data.campaign_type,
        data.budget,
        data.industry_avg
    )


# ========== 效果追踪接口 ==========

@router.put("/{campaign_id}/metrics", response_model=Dict)
async def update_metrics(campaign_id: str, data: MetricUpdate):
    """更新活动指标数据"""
    campaign = campaign_service.update_metrics(campaign_id, data.metrics)
    if not campaign:
        raise HTTPException(status_code=404, detail="活动不存在")
    return {"success": True, "campaign": campaign.__dict__}


@router.get("/{campaign_id}/performance", response_model=Dict)
async def get_campaign_performance(campaign_id: str):
    """获取活动效果报告"""
    performance = campaign_service.get_campaign_performance(campaign_id)
    if not performance:
        raise HTTPException(status_code=404, detail="活动不存在")
    return performance


# ========== 复盘报告接口 ==========

@router.get("/{campaign_id}/review", response_model=Dict)
async def generate_review_report(campaign_id: str):
    """生成活动复盘报告"""
    report = campaign_service.generate_review_report(campaign_id)
    if not report:
        raise HTTPException(status_code=404, detail="活动不存在")
    return report


# ========== 案例库接口 ==========

@router.get("/cases", response_model=List[Dict])
async def get_case_studies(
    campaign_type: Optional[str] = Query(None),
    industry: Optional[str] = Query(None)
):
    """获取案例库（可筛选）"""
    cases = campaign_service.get_case_studies(campaign_type=campaign_type, industry=industry)
    return [c.__dict__ for c in cases]


@router.get("/cases/{case_id}", response_model=Dict)
async def get_case_study(case_id: str):
    """获取指定案例详情"""
    case = campaign_service.get_case_study(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="案例不存在")
    return case.__dict__


@router.post("/cases", response_model=Dict)
async def add_case_study(case_data: CaseStudyCreate):
    """添加新案例"""
    case = campaign_service.add_case_study(case_data.dict())
    return {"success": True, "case": case.__dict__}


@router.get("/cases/search", response_model=List[Dict])
async def search_cases(keywords: str = Query(..., description="搜索关键词，多个用逗号分隔")):
    """搜索案例"""
    keyword_list = [k.strip() for k in keywords.split(",")]
    cases = campaign_service.search_cases(keyword_list)
    return [c.__dict__ for c in cases]


# ========== 统计概览接口 ==========

@router.get("/stats/overview", response_model=Dict)
async def get_stats_overview():
    """获取活动统计概览"""
    all_campaigns = campaign_service.get_all_campaigns()
    
    stats = {
        "total_campaigns": len(all_campaigns),
        "by_status": {},
        "by_type": {},
        "total_budget": 0,
        "avg_roi": 0
    }
    
    for campaign in all_campaigns:
        # 按状态统计
        status = campaign.status
        stats["by_status"][status] = stats["by_status"].get(status, 0) + 1
        
        # 按类型统计
        ctype = campaign.campaign_type
        stats["by_type"][ctype] = stats["by_type"].get(ctype, 0) + 1
        
        # 预算总计
        budget_summary = campaign_service.calculate_budget_total(campaign.budget_items)
        stats["total_budget"] += budget_summary.get("actual", 0)
    
    # 计算平均 ROI（从已完成活动中）
    completed = [c for c in all_campaigns if c.status == CampaignStatus.COMPLETED.value]
    if completed:
        rois = []
        for c in completed:
            perf = campaign_service.get_campaign_performance(c.id)
            if perf:
                rois.append(perf.get("health_score", 0))
        stats["avg_roi"] = sum(rois) / len(rois) if rois else 0
    
    return stats
