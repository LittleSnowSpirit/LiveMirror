"""
直播 ROI 分析 API 路由 - LiveMirror
"""

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime

from backend.services.roi_analysis import (
    get_service,
    LiveSession,
    CostItem,
    RevenueItem
)

router = APIRouter(prefix="/api/roi", tags=["ROI 分析"])

service = get_service()


# ============== 数据模型 ==============

class CostItemRequest(BaseModel):
    """成本项请求"""
    type: str = Field(..., description="成本类型：labor/venue/promotion/equipment/other")
    name: str = Field(..., description="成本名称")
    amount: float = Field(..., description="金额", ge=0)
    unit: str = Field(default="CNY", description="货币单位")
    notes: str = Field(default="", description="备注")


class RevenueItemRequest(BaseModel):
    """收益项请求"""
    type: str = Field(..., description="收益类型：gmv/profit/commission")
    name: str = Field(..., description="收益名称")
    amount: float = Field(..., description="金额", ge=0)
    unit: str = Field(default="CNY", description="货币单位")
    notes: str = Field(default="", description="备注")


class CreateSessionRequest(BaseModel):
    """创建场次请求"""
    date: str = Field(..., description="日期 (YYYY-MM-DD)")
    start_time: str = Field(..., description="开始时间 (HH:MM)")
    end_time: str = Field(..., description="结束时间 (HH:MM)")
    category: str = Field(default="general", description="分类")
    costs: Optional[List[CostItemRequest]] = Field(default=None, description="成本项列表")
    revenues: Optional[List[RevenueItemRequest]] = Field(default=None, description="收益项列表")
    notes: str = Field(default="", description="备注")
    
    @validator('date')
    def validate_date(cls, v):
        try:
            datetime.strptime(v, "%Y-%m-%d")
        except ValueError:
            raise ValueError("日期格式必须为 YYYY-MM-DD")
        return v
    
    @validator('start_time', 'end_time')
    def validate_time(cls, v):
        try:
            datetime.strptime(v, "%H:%M")
        except ValueError:
            raise ValueError("时间格式必须为 HH:MM")
        return v


class UpdateSessionRequest(BaseModel):
    """更新场次请求"""
    date: Optional[str] = Field(None, description="日期 (YYYY-MM-DD)")
    start_time: Optional[str] = Field(None, description="开始时间 (HH:MM)")
    end_time: Optional[str] = Field(None, description="结束时间 (HH:MM)")
    category: Optional[str] = Field(None, description="分类")
    costs: Optional[List[CostItemRequest]] = Field(None, description="成本项列表")
    revenues: Optional[List[RevenueItemRequest]] = Field(None, description="收益项列表")
    notes: Optional[str] = Field(None, description="备注")


class CompareSessionsRequest(BaseModel):
    """对比场次请求"""
    session_ids: List[str] = Field(..., description="场次 ID 列表", min_items=2)


class TrendRequest(BaseModel):
    """趋势请求"""
    start_date: Optional[str] = Field(None, description="开始日期 (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="结束日期 (YYYY-MM-DD)")
    group_by: str = Field(default="day", description="分组方式：day/week/month")


# ============== ROI 分析接口 ==============

@router.post("/sessions", summary="创建直播场次")
async def create_session(request: CreateSessionRequest):
    """创建新的直播场次记录"""
    try:
        costs = [c.dict() for c in request.costs] if request.costs else None
        revenues = [r.dict() for r in request.revenues] if request.revenues else None
        
        session = service.create_session(
            date=request.date,
            start_time=request.start_time,
            end_time=request.end_time,
            category=request.category,
            costs=costs,
            revenues=revenues,
            notes=request.notes
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"创建失败：{str(e)}")
    
    return {
        "success": True,
        "data": session.to_dict()
    }


@router.get("/sessions", summary="获取场次列表")
async def list_sessions(
    start_date: Optional[str] = Query(None, description="开始日期"),
    end_date: Optional[str] = Query(None, description="结束日期"),
    category: Optional[str] = Query(None, description="分类")
):
    """获取直播场次列表"""
    try:
        sessions = service.list_sessions(start_date, end_date, category)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败：{str(e)}")
    
    return {
        "success": True,
        "data": [s.to_dict() for s in sessions],
        "total": len(sessions)
    }


@router.get("/sessions/{session_id}", summary="获取场次详情")
async def get_session(session_id: str):
    """获取单个场次详情"""
    session = service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="场次不存在")
    
    return {
        "success": True,
        "data": session.to_dict()
    }


@router.put("/sessions/{session_id}", summary="更新场次")
async def update_session(session_id: str, request: UpdateSessionRequest):
    """更新直播场次信息"""
    updates = request.dict(exclude_unset=True)
    session = service.update_session(session_id, updates)
    
    if not session:
        raise HTTPException(status_code=404, detail="场次不存在")
    
    return {
        "success": True,
        "data": session.to_dict()
    }


@router.delete("/sessions/{session_id}", summary="删除场次")
async def delete_session(session_id: str):
    """删除直播场次"""
    success = service.delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="场次不存在")
    
    return {
        "success": True,
        "message": "删除成功"
    }


@router.get("/sessions/{session_id}/metrics", summary="获取 ROI 指标")
async def get_roi_metrics(session_id: str):
    """计算并获取场次 ROI 指标"""
    session = service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="场次不存在")
    
    metrics = service.calculate_roi_metrics(session_id)
    
    return {
        "success": True,
        "data": metrics.to_dict()
    }


@router.get("/sessions/{session_id}/cost-breakdown", summary="获取成本分解")
async def get_cost_breakdown(session_id: str):
    """获取场次成本分解"""
    session = service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="场次不存在")
    
    breakdown = service.get_cost_breakdown(session_id)
    
    return {
        "success": True,
        "data": breakdown
    }


@router.get("/sessions/{session_id}/suggestions", summary="获取优化建议")
async def get_optimization_suggestions(session_id: str):
    """生成并获取优化建议"""
    session = service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="场次不存在")
    
    suggestions = service.generate_optimization_suggestions(session_id)
    
    return {
        "success": True,
        "data": [s.to_dict() for s in suggestions]
    }


@router.post("/compare", summary="对比多场次 ROI")
async def compare_sessions(request: CompareSessionsRequest):
    """对比多个场次的 ROI 数据"""
    result = service.compare_sessions(request.session_ids)
    
    if not result:
        raise HTTPException(status_code=400, detail="需要至少 2 个有效场次进行对比")
    
    return {
        "success": True,
        "data": result.to_dict()
    }


@router.post("/trend", summary="获取 ROI 趋势")
async def get_roi_trend(request: TrendRequest):
    """获取 ROI 趋势数据"""
    try:
        trend_data = service.get_roi_trend(
            start_date=request.start_date,
            end_date=request.end_date,
            group_by=request.group_by
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"查询失败：{str(e)}")
    
    return {
        "success": True,
        "data": trend_data
    }


@router.post("/report", summary="生成 ROI 报告")
async def generate_report(session_ids: Optional[List[str]] = Body(None)):
    """生成 ROI 分析报告"""
    try:
        report = service.generate_report(session_ids)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成报告失败：{str(e)}")
    
    return {
        "success": True,
        "data": report
    }


@router.get("/templates/cost", summary="获取成本模板")
async def get_cost_templates():
    """获取预设成本模板"""
    return {
        "success": True,
        "data": service.cost_templates
    }


@router.post("/sessions/batch", summary="批量创建场次")
async def batch_create_sessions(sessions: List[CreateSessionRequest]):
    """批量创建直播场次"""
    created = []
    for request in sessions:
        try:
            costs = [c.dict() for c in request.costs] if request.costs else None
            revenues = [r.dict() for r in request.revenues] if request.revenues else None
            
            session = service.create_session(
                date=request.date,
                start_time=request.start_time,
                end_time=request.end_time,
                category=request.category,
                costs=costs,
                revenues=revenues,
                notes=request.notes
            )
            created.append(session.to_dict())
        except Exception as e:
            continue
    
    return {
        "success": True,
        "data": created,
        "created_count": len(created)
    }
