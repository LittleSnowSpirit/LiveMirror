"""
竞品监控 API 接口
"""

from fastapi import APIRouter, HTTPException, Query, Body
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from datetime import datetime
import asyncio

from ..services.competitor_monitor import (
    get_monitor_service,
    CompetitorInfo,
    LiveRoomData,
    AlertRule,
    Alert,
    ScriptSegment
)

router = APIRouter(prefix="/api/monitor", tags=["competitor-monitor"])


# ==================== 竞品管理 ====================

@router.get("/competitors", response_model=List[Dict])
async def list_competitors():
    """获取竞品列表"""
    service = get_monitor_service()
    competitors = service.list_competitors()
    return [{"id": c.id, "name": c.name, "platform": c.platform, 
             "room_id": c.room_id, "status": c.status, "added_at": c.added_at}
            for c in competitors]


@router.post("/competitors")
async def add_competitor(
    name: str = Body(..., description="竞品名称"),
    platform: str = Body(..., description="平台 (douyin/taobao/kuaishou)"),
    room_id: str = Body(..., description="直播间 ID")
):
    """添加竞品"""
    service = get_monitor_service()
    competitor = service.add_competitor(name, platform, room_id)
    return {
        "success": True,
        "data": {
            "id": competitor.id,
            "name": competitor.name,
            "platform": competitor.platform,
            "room_id": competitor.room_id,
            "status": competitor.status,
            "added_at": competitor.added_at
        }
    }


@router.delete("/competitors/{competitor_id}")
async def remove_competitor(competitor_id: str):
    """移除竞品"""
    service = get_monitor_service()
    success = service.remove_competitor(competitor_id)
    if not success:
        raise HTTPException(status_code=404, detail="竞品不存在")
    return {"success": True}


@router.get("/competitors/{competitor_id}")
async def get_competitor(competitor_id: str):
    """获取竞品信息"""
    service = get_monitor_service()
    competitor = service.get_competitor(competitor_id)
    if not competitor:
        raise HTTPException(status_code=404, detail="竞品不存在")
    return {
        "id": competitor.id,
        "name": competitor.name,
        "platform": competitor.platform,
        "room_id": competitor.room_id,
        "status": competitor.status,
        "added_at": competitor.added_at
    }


@router.put("/competitors/{competitor_id}/status")
async def update_competitor_status(
    competitor_id: str,
    status: str = Body(..., description="状态 (active/inactive)")
):
    """更新竞品状态"""
    service = get_monitor_service()
    competitor = service.get_competitor(competitor_id)
    if not competitor:
        raise HTTPException(status_code=404, detail="竞品不存在")
    
    competitor.status = status
    service._save_data()
    
    return {"success": True, "data": {"status": status}}


# ==================== 实时监控 ====================

@router.get("/status")
async def get_monitoring_status():
    """获取监控状态"""
    service = get_monitor_service()
    return {
        "is_monitoring": service.is_monitoring,
        "monitoring_interval": service.monitoring_interval,
        "competitor_count": len(service.competitors)
    }


@router.post("/start")
async def start_monitoring():
    """启动监控"""
    service = get_monitor_service()
    if service.is_monitoring:
        return {"success": True, "message": "监控已在运行"}
    
    # 在后台启动监控任务
    asyncio.create_task(service.start_monitoring())
    return {"success": True, "message": "监控已启动"}


@router.post("/stop")
async def stop_monitoring():
    """停止监控"""
    service = get_monitor_service()
    await service.stop_monitoring()
    return {"success": True, "message": "监控已停止"}


@router.get("/live-data/{competitor_id}")
async def get_live_data(competitor_id: str):
    """获取实时数据"""
    service = get_monitor_service()
    history = service.live_data_history.get(competitor_id, [])
    
    if not history:
        raise HTTPException(status_code=404, detail="暂无数据")
    
    latest = history[-1]
    return {
        "competitor_id": latest.competitor_id,
        "viewer_count": latest.viewer_count,
        "like_count": latest.like_count,
        "comment_count": latest.comment_count,
        "share_count": latest.share_count,
        "product_count": latest.product_count,
        "gmv": latest.gmv,
        "avg_watch_time": latest.avg_watch_time,
        "capture_time": latest.capture_time
    }


@router.get("/live-data/{competitor_id}/history")
async def get_live_data_history(
    competitor_id: str,
    start_time: Optional[str] = Query(None, description="开始时间"),
    end_time: Optional[str] = Query(None, description="结束时间"),
    limit: int = Query(100, ge=1, le=1000, description="记录数限制")
):
    """获取历史数据"""
    service = get_monitor_service()
    history = service.get_live_data_history(competitor_id, start_time, end_time, limit)
    
    return [{
        "competitor_id": d.competitor_id,
        "viewer_count": d.viewer_count,
        "like_count": d.like_count,
        "comment_count": d.comment_count,
        "share_count": d.share_count,
        "product_count": d.product_count,
        "gmv": d.gmv,
        "avg_watch_time": d.avg_watch_time,
        "capture_time": d.capture_time
    } for d in history]


# ==================== 告警规则管理 ====================

@router.get("/alert-rules", response_model=List[Dict])
async def list_alert_rules(competitor_id: Optional[str] = Query(None)):
    """获取告警规则列表"""
    service = get_monitor_service()
    rules = service.list_alert_rules(competitor_id)
    return [{
        "id": r.id,
        "name": r.name,
        "competitor_id": r.competitor_id,
        "rule_type": r.rule_type,
        "threshold": r.threshold,
        "comparison": r.comparison,
        "enabled": r.enabled,
        "created_at": r.created_at
    } for r in rules]


@router.post("/alert-rules")
async def add_alert_rule(
    name: str = Body(..., description="规则名称"),
    rule_type: str = Body(..., description="规则类型 (viewer_spike/script_plagiarism/gmv_threshold)"),
    threshold: float = Body(..., description="阈值"),
    comparison: str = Body("gt", description="比较方式 (gt/lt/eq/contains)"),
    competitor_id: str = Body("", description="竞品 ID（空表示所有）")
):
    """添加告警规则"""
    service = get_monitor_service()
    rule = service.add_alert_rule(name, rule_type, threshold, comparison, competitor_id)
    return {
        "success": True,
        "data": {
            "id": rule.id,
            "name": rule.name,
            "competitor_id": rule.competitor_id,
            "rule_type": rule.rule_type,
            "threshold": rule.threshold,
            "comparison": rule.comparison,
            "enabled": rule.enabled,
            "created_at": rule.created_at
        }
    }


@router.delete("/alert-rules/{rule_id}")
async def remove_alert_rule(rule_id: str):
    """移除告警规则"""
    service = get_monitor_service()
    success = service.remove_alert_rule(rule_id)
    if not success:
        raise HTTPException(status_code=404, detail="规则不存在")
    return {"success": True}


@router.put("/alert-rules/{rule_id}")
async def update_alert_rule(rule_id: str, **kwargs):
    """更新告警规则"""
    service = get_monitor_service()
    rule = service.update_alert_rule(rule_id, **kwargs)
    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在")
    return {
        "success": True,
        "data": {
            "id": rule.id,
            "name": rule.name,
            "competitor_id": rule.competitor_id,
            "rule_type": rule.rule_type,
            "threshold": rule.threshold,
            "comparison": rule.comparison,
            "enabled": rule.enabled
        }
    }


@router.post("/alert-rules/{rule_id}/toggle")
async def toggle_alert_rule(rule_id: str):
    """切换告警规则启用状态"""
    service = get_monitor_service()
    rule = service.get_alert_rule(rule_id) if hasattr(service, 'get_alert_rule') else None
    
    # 手动获取规则
    if rule_id not in service.alert_rules:
        raise HTTPException(status_code=404, detail="规则不存在")
    
    rule = service.alert_rules[rule_id]
    rule.enabled = not rule.enabled
    service._save_data()
    
    return {"success": True, "data": {"enabled": rule.enabled}}


# ==================== 告警记录 ====================

@router.get("/alerts", response_model=List[Dict])
async def list_alerts(
    competitor_id: Optional[str] = Query(None),
    alert_type: Optional[str] = Query(None),
    start_time: Optional[str] = Query(None),
    end_time: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000)
):
    """获取告警记录"""
    service = get_monitor_service()
    alerts = service.get_alerts(competitor_id, alert_type, start_time, end_time, limit)
    
    return [{
        "id": a.id,
        "rule_id": a.rule_id,
        "rule_name": a.rule_name,
        "competitor_id": a.competitor_id,
        "competitor_name": a.competitor_name,
        "alert_type": a.alert_type,
        "message": a.message,
        "current_value": a.current_value,
        "threshold": a.threshold,
        "triggered_at": a.triggered_at,
        "notified": a.notified
    } for a in alerts]


@router.get("/alerts/{alert_id}")
async def get_alert(alert_id: str):
    """获取告警详情"""
    service = get_monitor_service()
    for alert in service.alerts:
        if alert.id == alert_id:
            return {
                "id": alert.id,
                "rule_id": alert.rule_id,
                "rule_name": alert.rule_name,
                "competitor_id": alert.competitor_id,
                "competitor_name": alert.competitor_name,
                "alert_type": alert.alert_type,
                "message": alert.message,
                "current_value": alert.current_value,
                "threshold": alert.threshold,
                "triggered_at": alert.triggered_at,
                "notified": alert.notified,
                "notification_channels": alert.notification_channels
            }
    raise HTTPException(status_code=404, detail="告警不存在")


# ==================== 话术监控 ====================

@router.get("/scripts/{competitor_id}")
async def get_script_segments(
    competitor_id: str,
    limit: int = Query(50, ge=1, le=100)
):
    """获取话术片段"""
    service = get_monitor_service()
    segments = service.get_script_segments(competitor_id, limit)
    
    return [{
        "competitor_id": s.competitor_id,
        "content": s.content,
        "timestamp": s.timestamp,
        "similarity_score": s.similarity_score
    } for s in segments]


@router.post("/scripts/own")
async def add_own_script(script: str = Body(..., description="己方话术")):
    """添加己方话术"""
    service = get_monitor_service()
    service.add_own_script(script)
    return {"success": True, "message": "话术已添加"}


@router.get("/scripts/own")
async def list_own_scripts():
    """获取己方话术列表"""
    service = get_monitor_service()
    return {"scripts": service.own_scripts}


# ==================== 通知配置 ====================

@router.get("/notification-config")
async def get_notification_config():
    """获取通知配置"""
    service = get_monitor_service()
    return service.notification_config


@router.put("/notification-config/{channel}")
async def update_notification_config(
    channel: str,
    config: Dict[str, Any] = Body(..., description="配置内容")
):
    """更新通知配置"""
    service = get_monitor_service()
    service.update_notification_config(channel, config)
    return {"success": True, "message": f"{channel} 配置已更新"}


@router.post("/notification/test/{channel}")
async def test_notification(channel: str):
    """测试通知"""
    service = get_monitor_service()
    
    # 创建测试告警
    test_alert = Alert(
        id="test",
        rule_id="test",
        rule_name="测试告警",
        competitor_id="test",
        competitor_name="测试竞品",
        alert_type="test",
        message="这是一条测试告警消息",
        current_value=0,
        threshold=0,
        triggered_at=datetime.now().isoformat()
    )
    
    if channel == "email":
        await service._send_email_notification(test_alert)
    elif channel == "wechat":
        await service._send_wechat_notification(test_alert)
    else:
        raise HTTPException(status_code=400, detail="不支持的通知渠道")
    
    return {"success": True, "message": f"测试通知已发送到 {channel}"}


# ==================== 动态追踪 ====================

@router.post("/track/product")
async def track_product(
    competitor_id: str = Body(..., description="竞品 ID"),
    product_info: Dict = Body(..., description="产品信息")
):
    """追踪新品"""
    service = get_monitor_service()
    service.track_new_product(competitor_id, product_info)
    return {"success": True, "message": "新品已记录"}


@router.post("/track/activity")
async def track_activity(
    competitor_id: str = Body(..., description="竞品 ID"),
    activity_info: Dict = Body(..., description="活动信息")
):
    """追踪活动"""
    service = get_monitor_service()
    service.track_activity(competitor_id, activity_info)
    return {"success": True, "message": "活动已记录"}


# ==================== 统计信息 ====================

@router.get("/stats")
async def get_stats():
    """获取统计信息"""
    service = get_monitor_service()
    
    # 计算统计数据
    total_alerts = len(service.alerts)
    alerts_by_type = {}
    for alert in service.alerts:
        alerts_by_type[alert.alert_type] = alerts_by_type.get(alert.alert_type, 0) + 1
    
    return {
        "competitor_count": len(service.competitors),
        "rule_count": len(service.alert_rules),
        "total_alerts": total_alerts,
        "alerts_by_type": alerts_by_type,
        "is_monitoring": service.is_monitoring
    }
