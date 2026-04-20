"""
提醒接口路由
提供提醒查询、配置、推送等功能
"""
from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from datetime import datetime

from services.alert_engine import get_alert_engine, AlertEngine
from services.alert_rules import get_rule_manager, AlertRuleManager, AlertChannel
from database import get_db
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


# ==================== Pydantic 模型 ====================

class AlertRuleUpdate(BaseModel):
    """规则更新模型"""
    enabled: Optional[bool] = None
    thresholds: Optional[Dict[str, Any]] = None
    channels: Optional[List[str]] = None
    cooldown_seconds: Optional[int] = None


class AlertPushConfig(BaseModel):
    """推送配置模型"""
    email: Optional[str] = None
    wechat_webhook: Optional[str] = None
    enabled_channels: Optional[List[str]] = None


class ManualAlertRequest(BaseModel):
    """手动触发提醒请求"""
    rule_id: str
    title: str
    message: str
    level: str = "info"
    data: Optional[Dict[str, Any]] = None


# ==================== 提醒查询接口 ====================

@router.get("/history")
def get_alert_history(
    limit: int = Query(50, ge=1, le=200),
    alert_type: Optional[str] = None,
    level: Optional[str] = None,
    unread_only: bool = False,
    engine: AlertEngine = Depends(get_alert_engine),
):
    """获取提醒历史"""
    alerts = engine.get_alert_history(
        limit=limit,
        alert_type=alert_type,
        level=level,
        unread_only=unread_only,
    )
    
    return {
        "success": True,
        "data": alerts,
        "total": len(alerts),
    }


@router.get("/unread/count")
def get_unread_count(
    engine: AlertEngine = Depends(get_alert_engine),
):
    """获取未读提醒数量"""
    count = engine.get_unread_count()
    
    return {
        "success": True,
        "data": {"count": count},
    }


@router.get("/stats")
def get_stats(
    engine: AlertEngine = Depends(get_alert_engine),
):
    """获取提醒统计"""
    stats = engine.get_stats()
    
    return {
        "success": True,
        "data": stats,
    }


@router.post("/read/{alert_id}")
def mark_as_read(
    alert_id: str,
    engine: AlertEngine = Depends(get_alert_engine),
):
    """标记提醒为已读"""
    success = engine.mark_as_read(alert_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="提醒不存在")
    
    return {
        "success": True,
        "message": "已标记为已读",
    }


@router.post("/read/all")
def mark_all_as_read(
    engine: AlertEngine = Depends(get_alert_engine),
):
    """全部标记为已读"""
    count = engine.mark_all_as_read()
    
    return {
        "success": True,
        "data": {"marked_count": count},
        "message": f"已标记 {count} 条提醒为已读",
    }


@router.delete("/history")
def clear_history(
    older_than_days: Optional[int] = Query(None, ge=1),
    engine: AlertEngine = Depends(get_alert_engine),
):
    """清理提醒历史"""
    engine.clear_history(older_than_days=older_than_days)
    
    return {
        "success": True,
        "message": "历史已清理",
    }


# ==================== 规则管理接口 ====================

@router.get("/rules")
def get_rules(
    enabled_only: bool = False,
    rule_manager: AlertRuleManager = Depends(get_rule_manager),
):
    """获取所有提醒规则"""
    if enabled_only:
        rules = rule_manager.get_enabled_rules()
    else:
        rules = rule_manager.get_all_rules()
    
    return {
        "success": True,
        "data": [rule.to_dict() for rule in rules],
        "total": len(rules),
    }


@router.get("/rules/{rule_id}")
def get_rule(
    rule_id: str,
    rule_manager: AlertRuleManager = Depends(get_rule_manager),
):
    """获取单个规则"""
    rule = rule_manager.get_rule(rule_id)
    
    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在")
    
    return {
        "success": True,
        "data": rule.to_dict(),
    }


@router.put("/rules/{rule_id}")
def update_rule(
    rule_id: str,
    updates: AlertRuleUpdate,
    rule_manager: AlertRuleManager = Depends(get_rule_manager),
):
    """更新规则配置"""
    rule = rule_manager.get_rule(rule_id)
    
    if not rule:
        raise HTTPException(status_code=404, detail="规则不存在")
    
    update_data = updates.dict(exclude_unset=True)
    success = rule_manager.update_rule(rule_id, update_data)
    
    if not success:
        raise HTTPException(status_code=500, detail="更新失败")
    
    return {
        "success": True,
        "message": "规则已更新",
        "data": rule.to_dict(),
    }


@router.post("/rules/{rule_id}/enable")
def enable_rule(
    rule_id: str,
    rule_manager: AlertRuleManager = Depends(get_rule_manager),
):
    """启用规则"""
    success = rule_manager.enable_rule(rule_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="规则不存在")
    
    return {
        "success": True,
        "message": "规则已启用",
    }


@router.post("/rules/{rule_id}/disable")
def disable_rule(
    rule_id: str,
    rule_manager: AlertRuleManager = Depends(get_rule_manager),
):
    """禁用规则"""
    success = rule_manager.disable_rule(rule_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="规则不存在")
    
    return {
        "success": True,
        "message": "规则已禁用",
    }


# ==================== 推送配置接口 ====================

@router.get("/push/config")
def get_push_config():
    """获取推送配置"""
    # TODO: 从数据库或配置文件加载
    return {
        "success": True,
        "data": {
            "email": None,
            "wechat_webhook": None,
            "enabled_channels": ["in_app"],
        },
    }


@router.put("/push/config")
def update_push_config(
    config: AlertPushConfig,
):
    """更新推送配置"""
    # TODO: 保存到数据库或配置文件
    logger.info(f"更新推送配置：{config.dict()}")
    
    return {
        "success": True,
        "message": "推送配置已更新",
        "data": config.dict(),
    }


# ==================== 手动触发接口 ====================

@router.post("/trigger")
def trigger_manual_alert(
    request: ManualAlertRequest,
    background_tasks: BackgroundTasks,
    engine: AlertEngine = Depends(get_alert_engine),
):
    """手动触发提醒（用于测试）"""
    from services.alert_rules import AlertRule, AlertType, AlertLevel
    
    rule = engine.rule_manager.get_rule(request.rule_id)
    
    if not rule:
        # 创建临时规则
        rule = AlertRule(
            rule_id=request.rule_id,
            rule_name="手动触发",
            alert_type=AlertType.SENTIMENT_LOW,
            level=AlertLevel(request.level),
            description="手动触发的测试提醒",
            enabled=True,
        )
    
    alert = engine._record_alert(
        type(engine).Alert(
            alert_id=engine._generate_alert_id(),
            rule=rule,
            title=request.title,
            message=request.message,
            level=AlertLevel(request.level),
            data=request.data or {},
        )
    )
    
    return {
        "success": True,
        "message": "提醒已触发",
    }


# ==================== 实时监控接口 ====================

@router.post("/danmu")
def receive_danmu(
    danmu: Dict[str, Any],
    background_tasks: BackgroundTasks,
    engine: AlertEngine = Depends(get_alert_engine),
):
    """接收弹幕数据（用于实时监控）"""
    # 添加到引擎
    engine.add_danmu(danmu)
    
    # 异步检查规则
    background_tasks.add_task(_check_rules_async, engine)
    
    return {
        "success": True,
        "message": "弹幕已接收",
    }


@router.post("/viewers")
def update_viewers(
    count: int,
    background_tasks: BackgroundTasks,
    engine: AlertEngine = Depends(get_alert_engine),
):
    """更新观众数量"""
    engine.update_viewer_count(count)
    
    # 异步检查规则
    background_tasks.add_task(_check_rules_async, engine)
    
    return {
        "success": True,
        "message": "观众数已更新",
    }


async def _check_rules_async(engine: AlertEngine):
    """异步检查规则"""
    try:
        alerts = engine.check_all_rules()
        if alerts:
            logger.info(f"触发了 {len(alerts)} 条提醒")
    except Exception as e:
        logger.error(f"检查规则时出错：{e}")


# ==================== 推送通知接口 ====================

@router.post("/push/test")
async def test_push(
    channel: str = Query("in_app"),
    engine: AlertEngine = Depends(get_alert_engine),
):
    """测试推送功能"""
    from services.alert_rules import AlertRule, AlertType, AlertLevel
    
    rule = AlertRule(
        rule_id="test_push",
        rule_name="推送测试",
        alert_type=AlertType.SENTIMENT_LOW,
        level=AlertLevel.INFO,
        description="测试推送功能",
        enabled=True,
        channels=[AlertChannel(channel)],
    )
    
    alert = engine.Alert(
        alert_id=engine._generate_alert_id(),
        rule=rule,
        title="🧪 推送测试",
        message=f"这是一条测试提醒，推送渠道：{channel}",
        level=AlertLevel.INFO,
        data={"test": True, "channel": channel},
    )
    
    # 记录提醒
    engine.alert_history.append(alert)
    
    # 发送通知
    if engine.send_notification_callback:
        await engine.send_notification_callback(alert)
    
    return {
        "success": True,
        "message": f"测试提醒已发送到 {channel}",
    }


# ==================== 初始化推送回调 ====================

async def send_notification(alert):
    """发送通知回调"""
    from services.alert_rules import AlertChannel
    
    # 站内信 - 直接记录
    if AlertChannel.IN_APP in alert.sent_channels or not alert.sent_channels:
        logger.info(f"[站内信] {alert.title}: {alert.message}")
    
    # 邮件
    if AlertChannel.EMAIL in alert.channels:
        await _send_email_notification(alert)
    
    # 微信
    if AlertChannel.WECHAT in alert.channels:
        await _send_wechat_notification(alert)
    
    # 标记已发送渠道
    for channel in alert.channels:
        if channel not in alert.sent_channels:
            alert.sent_channels.append(channel)


async def _send_email_notification(alert):
    """发送邮件通知"""
    # TODO: 实现邮件发送
    logger.info(f"[邮件通知] {alert.title}: {alert.message}")
    pass


async def _send_wechat_notification(alert):
    """发送微信通知"""
    # TODO: 实现微信推送
    logger.info(f"[微信通知] {alert.title}: {alert.message}")
    pass


# 设置回调
_alert_engine_instance = get_alert_engine()
_alert_engine_instance.set_notification_callback(send_notification)
