"""
LiveMirror Dashboard Routes
大屏数据接口路由
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Optional
import json
from datetime import datetime

from backend.services.dashboard import dashboard_service

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket 连接 - 实时推送直播数据
    """
    await dashboard_service.connect(websocket)
    try:
        while True:
            # 保持连接，接收客户端消息（可选）
            data = await websocket.receive_text()
            # 可以处理客户端请求，如切换布局、导出数据等
            try:
                message = json.loads(data)
                msg_type = message.get("type")
                
                if msg_type == "request_data":
                    # 客户端请求当前数据
                    await dashboard_service.send_data(
                        websocket, 
                        dashboard_service.get_current_data()
                    )
                elif msg_type == "reset":
                    # 重置数据
                    dashboard_service.reset_data()
                    await dashboard_service.broadcast({
                        "type": "reset",
                        "timestamp": datetime.now().isoformat(),
                        "data": dashboard_service.get_current_data()
                    })
            except json.JSONDecodeError:
                pass
    except WebSocketDisconnect:
        dashboard_service.disconnect(websocket)


@router.get("/data")
async def get_dashboard_data():
    """
    获取当前大屏数据（REST API）
    """
    return {
        "success": True,
        "timestamp": datetime.now().isoformat(),
        "data": dashboard_service.get_current_data()
    }


@router.post("/data/update")
async def update_dashboard_data(
    gmv: Optional[float] = Query(None),
    viewers: Optional[int] = Query(None),
    likes: Optional[int] = Query(None),
    comments: Optional[int] = Query(None),
    shares: Optional[int] = Query(None),
    orders: Optional[int] = Query(None)
):
    """
    手动更新大屏数据
    """
    update_params = {}
    if gmv is not None:
        update_params["gmv"] = gmv
    if viewers is not None:
        update_params["viewers"] = viewers
    if likes is not None:
        update_params["likes"] = likes
    if comments is not None:
        update_params["comments"] = comments
    if shares is not None:
        update_params["shares"] = shares
    if orders is not None:
        update_params["orders"] = orders
    
    if update_params:
        dashboard_service.update_data(**update_params)
    
    return {
        "success": True,
        "timestamp": datetime.now().isoformat(),
        "data": dashboard_service.get_current_data()
    }


@router.post("/data/reset")
async def reset_dashboard_data():
    """
    重置大屏数据
    """
    dashboard_service.reset_data()
    return {
        "success": True,
        "timestamp": datetime.now().isoformat(),
        "message": "Dashboard data reset"
    }


@router.get("/templates")
async def get_dashboard_templates():
    """
    获取可用的大屏模板列表
    """
    templates = [
        {
            "id": "default",
            "name": "默认布局",
            "description": "标准三栏布局，展示核心指标",
            "preview": "/templates/default.png"
        },
        {
            "id": "focus-gmv",
            "name": "GMV 焦点",
            "description": "突出显示 GMV 数据，适合促销场景",
            "preview": "/templates/focus-gmv.png"
        },
        {
            "id": "interaction",
            "name": "互动优先",
            "description": "强调互动数据（点赞、评论、分享）",
            "preview": "/templates/interaction.png"
        },
        {
            "id": "minimal",
            "name": "极简模式",
            "description": "简洁布局，只展示最关键指标",
            "preview": "/templates/minimal.png"
        }
    ]
    return {
        "success": True,
        "templates": templates
    }


@router.get("/export")
async def export_dashboard_data(format: str = Query("json", pattern="^(json|csv)$")):
    """
    导出大屏数据
    """
    data = dashboard_service.get_current_data()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    if format == "json":
        return {
            "success": True,
            "filename": f"dashboard_export_{timestamp}.json",
            "data": data,
            "format": "json"
        }
    elif format == "csv":
        # 转换为 CSV 格式
        csv_lines = ["metric,value"]
        for key, value in data.items():
            csv_lines.append(f"{key},{value}")
        
        return {
            "success": True,
            "filename": f"dashboard_export_{timestamp}.csv",
            "data": "\n".join(csv_lines),
            "format": "csv"
        }
