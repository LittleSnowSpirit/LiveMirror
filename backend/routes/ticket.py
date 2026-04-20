"""
客服工单 API 接口
提供工单管理的 RESTful API
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime

from backend.services.ticket import ticket_service, TicketStatus, TicketPriority, TicketCategory


router = APIRouter(prefix="/api/tickets", tags=["tickets"])


# ==================== 请求/响应模型 ====================

class TicketCreateRequest(BaseModel):
    """工单创建请求"""
    title: str = Field(..., min_length=1, max_length=200, description="工单标题")
    description: str = Field(..., min_length=1, max_length=5000, description="工单描述")
    category: str = Field(..., description="工单分类")
    priority: str = Field(default="medium", description="工单优先级")
    assignee_id: Optional[str] = Field(None, description="指派人 ID")


class TicketMessageRequest(BaseModel):
    """工单消息请求"""
    content: str = Field(..., min_length=1, max_length=5000, description="消息内容")
    is_internal: bool = Field(default=False, description="是否内部消息")


class TicketAssignRequest(BaseModel):
    """工单分配请求"""
    assignee_id: str = Field(..., description="指派人 ID")


class TicketStatusUpdateRequest(BaseModel):
    """工单状态更新请求"""
    status: str = Field(..., description="工单状态")


class AutoReplyTemplateRequest(BaseModel):
    """自动回复模板请求"""
    name: str = Field(..., description="模板名称")
    trigger_keywords: List[str] = Field(..., description="触发关键词列表")
    response: str = Field(..., description="回复内容")


class TicketResponse(BaseModel):
    """工单响应"""
    id: str
    title: str
    description: str
    category: str
    priority: str
    status: str
    creator_id: str
    assignee_id: Optional[str]
    created_at: str
    updated_at: str
    resolved_at: Optional[str]
    closed_at: Optional[str]
    messages: List[Dict]
    tags: List[str]


class TicketListResponse(BaseModel):
    """工单列表响应"""
    tickets: List[TicketResponse]
    total: int
    limit: int
    offset: int


class StatisticsResponse(BaseModel):
    """统计报表响应"""
    total: int
    by_status: Dict[str, int]
    by_category: Dict[str, int]
    by_priority: Dict[str, int]
    avg_resolution_hours: float
    resolved_count: int
    closed_count: int


class AutoReplyResponse(BaseModel):
    """自动回复响应"""
    reply: Optional[str]
    matched_template: Optional[str]


# ==================== 工单管理接口 ====================

@router.post("", response_model=TicketResponse, summary="创建工单")
async def create_ticket(request: TicketCreateRequest):
    """
    创建新的客服工单
    
    - **title**: 工单标题
    - **description**: 工单详细描述
    - **category**: 工单分类 (technical/billing/account/feature/bug/other)
    - **priority**: 优先级 (low/medium/high/urgent)
    - **assignee_id**: 可选的指派人 ID
    """
    try:
        ticket = ticket_service.create_ticket(
            title=request.title,
            description=request.description,
            category=request.category,
            priority=request.priority,
            creator_id="user_001",  # TODO: 从认证信息获取
            assignee_id=request.assignee_id
        )
        return TicketResponse(**ticket.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("", response_model=TicketListResponse, summary="获取工单列表")
async def list_tickets(
    status: Optional[str] = Query(None, description="按状态筛选"),
    category: Optional[str] = Query(None, description="按分类筛选"),
    priority: Optional[str] = Query(None, description="按优先级筛选"),
    assignee_id: Optional[str] = Query(None, description="按指派人筛选"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    offset: int = Query(0, ge=0, description="偏移量")
):
    """
    获取工单列表，支持多种筛选条件
    
    - **status**: 工单状态 (new/assigned/in_progress/pending/resolved/closed)
    - **category**: 工单分类
    - **priority**: 优先级
    - **assignee_id**: 指派人 ID
    - **limit**: 每页返回数量 (1-100)
    - **offset**: 分页偏移量
    """
    tickets = ticket_service.list_tickets(
        status=status,
        category=category,
        priority=priority,
        assignee_id=assignee_id,
        limit=limit,
        offset=offset
    )
    
    return TicketListResponse(
        tickets=[TicketResponse(**t.to_dict()) for t in tickets],
        total=len(ticket_service.tickets),
        limit=limit,
        offset=offset
    )


@router.get("/{ticket_id}", response_model=TicketResponse, summary="获取工单详情")
async def get_ticket(ticket_id: str):
    """
    获取指定工单的详细信息
    """
    ticket = ticket_service.get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="工单不存在")
    return TicketResponse(**ticket.to_dict())


@router.put("/{ticket_id}/status", response_model=TicketResponse, summary="更新工单状态")
async def update_ticket_status(ticket_id: str, request: TicketStatusUpdateRequest):
    """
    更新工单状态
    
    - **status**: 新状态 (new/assigned/in_progress/pending/resolved/closed)
    """
    ticket = ticket_service.get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="工单不存在")
    
    # 验证状态
    valid_statuses = [s.value for s in TicketStatus]
    if request.status not in valid_statuses:
        raise HTTPException(
            status_code=400,
            detail=f"无效的状态值。有效值：{', '.join(valid_statuses)}"
        )
    
    success = ticket_service.update_ticket_status(ticket_id, request.status)
    if not success:
        raise HTTPException(status_code=500, detail="更新状态失败")
    
    updated_ticket = ticket_service.get_ticket(ticket_id)
    return TicketResponse(**updated_ticket.to_dict())


@router.post("/{ticket_id}/assign", response_model=TicketResponse, summary="分配工单")
async def assign_ticket(ticket_id: str, request: TicketAssignRequest):
    """
    将工单分配给指定客服人员
    """
    ticket = ticket_service.get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="工单不存在")
    
    success = ticket_service.assign_ticket(ticket_id, request.assignee_id)
    if not success:
        raise HTTPException(status_code=500, detail="分配工单失败")
    
    updated_ticket = ticket_service.get_ticket(ticket_id)
    return TicketResponse(**updated_ticket.to_dict())


@router.post("/{ticket_id}/messages", response_model=TicketResponse, summary="添加工单消息")
async def add_ticket_message(ticket_id: str, request: TicketMessageRequest):
    """
    添加工单消息（支持内部备注和客户回复）
    
    - **content**: 消息内容
    - **is_internal**: 是否为内部消息（客户不可见）
    """
    ticket = ticket_service.get_ticket(ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail="工单不存在")
    
    success = ticket_service.add_message(
        ticket_id=ticket_id,
        sender_id="agent_001",  # TODO: 从认证信息获取
        content=request.content,
        is_internal=request.is_internal
    )
    if not success:
        raise HTTPException(status_code=500, detail="添加消息失败")
    
    updated_ticket = ticket_service.get_ticket(ticket_id)
    return TicketResponse(**updated_ticket.to_dict())


@router.delete("/{ticket_id}", summary="删除工单")
async def delete_ticket(ticket_id: str):
    """
    删除指定工单（谨慎操作）
    """
    success = ticket_service.delete_ticket(ticket_id)
    if not success:
        raise HTTPException(status_code=404, detail="工单不存在")
    return {"message": "工单已删除"}


# ==================== 统计报表接口 ====================

@router.get("/statistics", response_model=StatisticsResponse, summary="获取统计报表")
async def get_statistics():
    """
    获取工单统计报表
    
    包含：
    - 工单总数
    - 按状态分布
    - 按分类分布
    - 按优先级分布
    - 平均解决时间
    - 已解决/已关闭数量
    """
    stats = ticket_service.get_statistics()
    return StatisticsResponse(**stats)


# ==================== 自动回复接口 ====================

@router.post("/auto-reply/check", response_model=AutoReplyResponse, summary="检查自动回复")
async def check_auto_reply(content: str = Query(..., description="消息内容")):
    """
    根据消息内容检查是否匹配自动回复模板
    """
    reply = ticket_service.get_auto_reply(content)
    return AutoReplyResponse(
        reply=reply,
        matched_template="已匹配模板" if reply else None
    )


@router.post("/auto-reply/templates", summary="添加自动回复模板")
async def add_auto_reply_template(request: AutoReplyTemplateRequest):
    """
    添加新的自动回复模板
    
    - **name**: 模板名称
    - **trigger_keywords**: 触发关键词列表
    - **response**: 回复内容
    """
    template = ticket_service.add_auto_reply_template(
        name=request.name,
        trigger_keywords=request.trigger_keywords,
        response=request.response
    )
    return {
        "id": template.id,
        "name": template.name,
        "trigger_keywords": template.trigger_keywords,
        "enabled": template.enabled
    }


@router.get("/auto-reply/templates", summary="获取自动回复模板列表")
async def list_auto_reply_templates():
    """
    获取所有自动回复模板
    """
    return [
        {
            "id": t.id,
            "name": t.name,
            "trigger_keywords": t.trigger_keywords,
            "response": t.response,
            "enabled": t.enabled
        }
        for t in ticket_service.auto_reply_templates
    ]
