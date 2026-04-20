"""
LiveMirror 场控接口路由
提供场控助手的 HTTP API 接口
"""

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import asyncio
import json
from datetime import datetime

from ..services.assistant_controller import (
    get_controller,
    DanmakuMessage,
    AlertLevel,
    ViolationType,
)

router = APIRouter(prefix="/api/controller", tags=["场控助手"])


# ============== 数据模型 ==============

class StartLiveRequest(BaseModel):
    """开始直播请求"""
    stream_id: str
    room_name: Optional[str] = None


class StopLiveRequest(BaseModel):
    """停止直播请求"""
    stream_id: str


class DanmakuRequest(BaseModel):
    """弹幕消息请求"""
    user_id: str
    username: str
    content: str
    user_level: int = 1
    is_fan: bool = False
    is_moderator: bool = False


class AutoReplyConfig(BaseModel):
    """自动回复配置"""
    enabled: bool
    custom_responses: Optional[Dict[str, str]] = None


class ViolationConfig(BaseModel):
    """违规检测配置"""
    enabled: bool
    custom_keywords: Optional[Dict[str, List[str]]] = None


class ManualActionRequest(BaseModel):
    """手动操作请求"""
    action: str  # "mute", "warn", "ban", "delete"
    user_id: str
    reason: str


# ============== 直播控制接口 ==============

@router.post("/live/start")
async def start_live(request: StartLiveRequest):
    """开始直播监控"""
    controller = get_controller()
    
    success = await controller.start_live(request.stream_id)
    
    if success:
        return JSONResponse({
            "code": 0,
            "message": "直播监控已启动",
            "data": {
                "stream_id": request.stream_id,
                "started_at": datetime.now().isoformat()
            }
        })
    else:
        raise HTTPException(status_code=400, detail="直播监控已在运行中")


@router.post("/live/stop")
async def stop_live(request: StopLiveRequest):
    """停止直播监控"""
    controller = get_controller()
    
    success = await controller.stop_live()
    
    if success:
        return JSONResponse({
            "code": 0,
            "message": "直播监控已停止",
            "data": {
                "stream_id": request.stream_id,
                "stopped_at": datetime.now().isoformat()
            }
        })
    else:
        raise HTTPException(status_code=400, detail="直播监控未运行")


@router.get("/live/status")
async def get_live_status():
    """获取直播状态"""
    controller = get_controller()
    status = controller.get_status()
    
    return JSONResponse({
        "code": 0,
        "data": status
    })


# ============== 弹幕处理接口 ==============

@router.post("/danmaku/receive")
async def receive_danmaku(request: DanmakuRequest):
    """接收弹幕消息"""
    controller = get_controller()
    
    if not controller.is_live:
        raise HTTPException(status_code=400, detail="未在直播中")
    
    message = DanmakuMessage(
        user_id=request.user_id,
        username=request.username,
        content=request.content,
        timestamp=datetime.now().timestamp(),
        user_level=request.user_level,
        is_fan=request.is_fan,
        is_moderator=request.is_moderator
    )
    
    alerts = await controller.receive_danmaku(message)
    
    return JSONResponse({
        "code": 0,
        "message": "弹幕已处理",
        "data": {
            "alerts": [
                {
                    "level": alert.level.value,
                    "message": alert.message,
                    "type": alert.alert_type,
                    "timestamp": alert.timestamp
                }
                for alert in alerts
            ]
        }
    })


@router.post("/danmaku/batch")
async def receive_batch_danmaku(messages: List[DanmakuRequest]):
    """批量接收弹幕"""
    controller = get_controller()
    
    if not controller.is_live:
        raise HTTPException(status_code=400, detail="未在直播中")
    
    all_alerts = []
    for msg_req in messages:
        message = DanmakuMessage(
            user_id=msg_req.user_id,
            username=msg_req.username,
            content=msg_req.content,
            timestamp=datetime.now().timestamp(),
            user_level=msg_req.user_level,
            is_fan=msg_req.is_fan,
            is_moderator=msg_req.is_moderator
        )
        alerts = await controller.receive_danmaku(message)
        all_alerts.extend(alerts)
    
    return JSONResponse({
        "code": 0,
        "message": f"已处理{len(messages)}条弹幕",
        "data": {
            "total_alerts": len(all_alerts),
            "alerts": [
                {
                    "level": alert.level.value,
                    "message": alert.message,
                    "type": alert.alert_type,
                    "user_id": alert.user_id,
                    "timestamp": alert.timestamp
                }
                for alert in all_alerts
            ]
        }
    })


# ============== 预警查询接口 ==============

@router.get("/alerts")
async def get_alerts(limit: int = 50, level: Optional[str] = None):
    """获取预警记录"""
    controller = get_controller()
    alerts = controller.get_alerts(limit)
    
    if level:
        alerts = [a for a in alerts if a.get("level") == level]
    
    return JSONResponse({
        "code": 0,
        "data": {
            "alerts": alerts,
            "total": len(alerts)
        }
    })


@router.get("/alerts/stats")
async def get_alerts_stats():
    """获取预警统计"""
    controller = get_controller()
    alerts = controller.get_alerts(limit=1000)
    
    stats = {
        "total": len(alerts),
        "by_level": {},
        "by_type": {},
    }
    
    for alert in alerts:
        level = alert.get("level", "unknown")
        alert_type = alert.get("alert_type", "unknown")
        
        stats["by_level"][level] = stats["by_level"].get(level, 0) + 1
        stats["by_type"][alert_type] = stats["by_type"].get(alert_type, 0) + 1
    
    return JSONResponse({
        "code": 0,
        "data": stats
    })


# ============== 情绪监控接口 ==============

@router.get("/emotion/current")
async def get_current_emotion():
    """获取当前观众情绪"""
    controller = get_controller()
    status = controller.get_status()
    
    return JSONResponse({
        "code": 0,
        "data": {
            "emotion": status.get("current_emotion"),
            "timestamp": datetime.now().isoformat()
        }
    })


@router.get("/emotion/trend")
async def get_emotion_trend(minutes: int = 10):
    """获取情绪趋势"""
    controller = get_controller()
    trend = controller.get_emotion_trend(minutes)
    
    return JSONResponse({
        "code": 0,
        "data": {
            "trend": trend,
            "period_minutes": minutes
        }
    })


# ============== 节奏建议接口 ==============

@router.get("/suggestions")
async def get_suggestions(limit: int = 10):
    """获取直播节奏建议"""
    controller = get_controller()
    suggestions = controller.get_suggestions(limit)
    
    return JSONResponse({
        "code": 0,
        "data": {
            "suggestions": suggestions,
            "total": len(suggestions)
        }
    })


@router.get("/suggestions/current")
async def get_current_suggestion():
    """获取当前最优先建议"""
    controller = get_controller()
    suggestions = controller.get_suggestions(limit=1)
    
    return JSONResponse({
        "code": 0,
        "data": {
            "suggestion": suggestions[0] if suggestions else None
        }
    })


# ============== 操作日志接口 ==============

@router.get("/logs")
async def get_operation_logs(limit: int = 50, action: Optional[str] = None):
    """获取操作日志"""
    controller = get_controller()
    logs = controller.get_operation_logs(limit)
    
    if action:
        logs = [l for l in logs if l.get("action") == action]
    
    return JSONResponse({
        "code": 0,
        "data": {
            "logs": logs,
            "total": len(logs)
        }
    })


@router.get("/logs/stats")
async def get_logs_stats():
    """获取日志统计"""
    controller = get_controller()
    status = controller.get_status()
    
    return JSONResponse({
        "code": 0,
        "data": {
            "stats": status.get("stats", {})
        }
    })


# ============== 配置管理接口 ==============

@router.get("/config")
async def get_config():
    """获取场控配置"""
    controller = get_controller()
    
    return JSONResponse({
        "code": 0,
        "data": {
            "config": controller.config
        }
    })


@router.put("/config/auto-reply")
async def update_auto_reply_config(config: AutoReplyConfig):
    """更新自动回复配置"""
    controller = get_controller()
    controller.config["auto_reply_enabled"] = config.enabled
    
    if config.custom_responses:
        controller.faq_responses.update(config.custom_responses)
    
    return JSONResponse({
        "code": 0,
        "message": "配置已更新"
    })


@router.put("/config/violation")
async def update_violation_config(config: ViolationConfig):
    """更新违规检测配置"""
    controller = get_controller()
    controller.config["violation_detection_enabled"] = config.enabled
    
    if config.custom_keywords:
        for vtype, keywords in config.custom_keywords.items():
            try:
                violation_type = ViolationType(vtype)
                controller.violation_keywords[violation_type].extend(keywords)
            except ValueError:
                pass
    
    return JSONResponse({
        "code": 0,
        "message": "配置已更新"
    })


# ============== 手动操作接口 ==============

@router.post("/action/manual")
async def manual_action(request: ManualActionRequest):
    """手动执行场控操作"""
    controller = get_controller()
    
    controller._log_operation("manual_action", {
        "action": request.action,
        "user_id": request.user_id,
        "reason": request.reason
    })
    
    return JSONResponse({
        "code": 0,
        "message": f"已执行手动操作：{request.action}"
    })


# ============== WebSocket 实时推送 ==============

@router.websocket("/ws")
async def controller_websocket(websocket: WebSocket):
    """场控 WebSocket 连接"""
    await websocket.accept()
    
    controller = get_controller()
    
    try:
        while True:
            # 接收客户端消息
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                msg_type = message.get("type")
                
                if msg_type == "subscribe":
                    # 订阅实时数据
                    subscribe_to = message.get("subscribe_to", [])
                    
                    # 启动推送任务
                    async def push_data():
                        while True:
                            try:
                                status = controller.get_status()
                                
                                push_data = {
                                    "type": "status_update",
                                    "data": status
                                }
                                
                                await websocket.send_json(push_data)
                                await asyncio.sleep(2)  # 每 2 秒推送一次
                            except Exception as e:
                                logger.error(f"推送数据失败：{e}")
                                break
                    
                    push_task = asyncio.create_task(push_data())
                    
                elif msg_type == "ping":
                    await websocket.send_json({"type": "pong"})
                    
            except json.JSONDecodeError:
                await websocket.send_json({
                    "type": "error",
                    "message": "无效的 JSON 格式"
                })
                
    except WebSocketDisconnect:
        logger.info("WebSocket 连接断开")
    except Exception as e:
        logger.error(f"WebSocket 错误：{e}")
