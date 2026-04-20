"""
提醒规则引擎
负责监控数据、触发规则、发送提醒
"""
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
from collections import deque, defaultdict
import asyncio
import logging

from .alert_rules import (
    AlertRule, AlertRuleManager, AlertType, AlertLevel, AlertChannel,
    get_rule_manager
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Alert:
    """提醒实例"""
    
    def __init__(
        self,
        alert_id: str,
        rule: AlertRule,
        title: str,
        message: str,
        level: AlertLevel,
        data: Dict[str, Any] = None,
    ):
        self.alert_id = alert_id
        self.rule = rule
        self.title = title
        self.message = message
        self.level = level
        self.data = data or {}
        self.created_at = datetime.utcnow()
        self.read = False
        self.sent_channels: List[AlertChannel] = []
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "alert_id": self.alert_id,
            "rule_id": self.rule.rule_id,
            "rule_name": self.rule.rule_name,
            "alert_type": self.rule.alert_type.value,
            "title": self.title,
            "message": self.message,
            "level": self.level.value,
            "data": self.data,
            "created_at": self.created_at.isoformat(),
            "read": self.read,
            "sent_channels": [c.value for c in self.sent_channels],
        }


class AlertEngine:
    """提醒引擎"""
    
    def __init__(self, rule_manager: AlertRuleManager = None):
        self.rule_manager = rule_manager or get_rule_manager()
        
        # 数据缓存 - 用于实时监控
        self.danmu_buffer: deque = deque(maxlen=1000)  # 弹幕缓冲区
        self.viewer_count_history: deque = deque(maxlen=300)  # 观众数历史（5 分钟）
        
        # 提醒历史
        self.alert_history: List[Alert] = []
        self.alert_counter = 0
        
        # 冷却追踪 - 避免重复提醒
        self.last_alert_time: Dict[str, datetime] = {}
        
        # 回调函数 - 用于发送通知
        self.send_notification_callback = None
        
        # 基线数据 - 用于计算相对变化
        self.baseline_danmu_rate = 0.0  # 基础弹幕速率
        self.baseline_viewer_count = 0  # 基础观众数
        self.baseline_calculated = False
    
    def set_notification_callback(self, callback):
        """设置通知发送回调"""
        self.send_notification_callback = callback
    
    def add_danmu(self, danmu: Dict[str, Any]):
        """添加弹幕到缓冲区"""
        self.danmu_buffer.append({
            **danmu,
            "received_at": datetime.utcnow(),
        })
        
        # 更新基线
        if not self.baseline_calculated and len(self.danmu_buffer) >= 100:
            self._calculate_baseline()
    
    def update_viewer_count(self, count: int):
        """更新观众数量"""
        self.viewer_count_history.append({
            "count": count,
            "timestamp": datetime.utcnow(),
        })
        
        # 更新基线
        if not self.baseline_calculated and len(self.viewer_count_history) >= 60:
            self._calculate_baseline()
    
    def _calculate_baseline(self):
        """计算基线数据"""
        if len(self.danmu_buffer) >= 100:
            # 计算平均弹幕速率
            danmus = list(self.danmu_buffer)
            if len(danmus) >= 2:
                time_span = (
                    danmus[-1]["received_at"] - danmus[0]["received_at"]
                ).total_seconds()
                if time_span > 0:
                    self.baseline_danmu_rate = len(danmus) / time_span
        
        if len(self.viewer_count_history) >= 60:
            # 计算平均观众数
            counts = [v["count"] for v in self.viewer_count_history]
            self.baseline_viewer_count = sum(counts) // len(counts)
        
        self.baseline_calculated = True
        logger.info(
            f"基线计算完成：弹幕速率={self.baseline_danmu_rate:.2f}/s, "
            f"观众数={self.baseline_viewer_count}"
        )
    
    def check_all_rules(self) -> List[Alert]:
        """检查所有规则"""
        triggered_alerts = []
        
        for rule in self.rule_manager.get_enabled_rules():
            alert = self._check_rule(rule)
            if alert:
                triggered_alerts.append(alert)
        
        return triggered_alerts
    
    def _check_rule(self, rule: AlertRule) -> Optional[Alert]:
        """检查单个规则"""
        # 检查冷却时间
        if not self._check_cooldown(rule):
            return None
        
        # 根据规则类型检查
        alert = None
        
        if rule.alert_type == AlertType.SENTIMENT_LOW:
            alert = self._check_sentiment_low(rule)
        elif rule.alert_type == AlertType.SPEECH_RISK:
            alert = self._check_speech_risk(rule)
        elif rule.alert_type == AlertType.AUDIENCE_LOSS:
            alert = self._check_audience_loss(rule)
        elif rule.alert_type == AlertType.CONTROVERSY:
            alert = self._check_controversy(rule)
        elif rule.alert_type == AlertType.HEAT_DROP:
            alert = self._check_heat_drop(rule)
        elif rule.alert_type == AlertType.KEY_MOMENT:
            alert = self._check_key_moment(rule)
        
        if alert:
            self._record_alert(alert)
        
        return alert
    
    def _check_cooldown(self, rule: AlertRule) -> bool:
        """检查冷却时间"""
        last_time = self.last_alert_time.get(rule.rule_id)
        if last_time:
            elapsed = (datetime.utcnow() - last_time).total_seconds()
            if elapsed < rule.cooldown_seconds:
                return False
        return True
    
    def _check_sentiment_low(self, rule: AlertRule) -> Optional[Alert]:
        """检查低情绪预警"""
        thresholds = rule.thresholds
        window_seconds = thresholds.get("window_seconds", 60)
        negative_threshold = thresholds.get("negative_ratio_threshold", 0.3)
        min_count = thresholds.get("min_danmu_count", 10)
        
        # 获取窗口内的弹幕
        window_danmus = self._get_danmus_in_window(window_seconds)
        
        if len(window_danmus) < min_count:
            return None
        
        # 统计负面情绪
        negative_count = sum(
            1 for d in window_danmus
            if d.get("sentiment") == "negative"
        )
        
        negative_ratio = negative_count / len(window_danmus)
        
        if negative_ratio >= negative_threshold:
            return Alert(
                alert_id=self._generate_alert_id(),
                rule=rule,
                title="⚠️ 低情绪预警",
                message=f"过去{window_seconds}秒内，负面情绪弹幕比例达到{negative_ratio:.1%}（阈值：{negative_threshold:.1%}）",
                level=rule.level,
                data={
                    "negative_count": negative_count,
                    "total_count": len(window_danmus),
                    "negative_ratio": negative_ratio,
                    "window_seconds": window_seconds,
                },
            )
        
        return None
    
    def _check_speech_risk(self, rule: AlertRule) -> Optional[Alert]:
        """检查话术风险"""
        thresholds = rule.thresholds
        
        # 获取最近的弹幕（用于检测观众反应）
        recent_danmus = self._get_danmus_in_window(30)
        
        # 检测敏感词（从弹幕中检测观众对敏感话术的反应）
        sensitive_words = thresholds.get("sensitive_words", [])
        critical_words = thresholds.get("critical_words", [])
        risk_phrases = thresholds.get("risk_phrases", [])
        
        detected_words = []
        detected_phrases = []
        
        for danmu in recent_danmus:
            content = danmu.get("content", "").lower()
            
            for word in sensitive_words:
                if word.lower() in content:
                    detected_words.append(word)
            
            for word in critical_words:
                if word.lower() in content:
                    detected_words.append(word)
            
            for phrase in risk_phrases:
                if phrase.lower() in content:
                    detected_phrases.append(phrase)
        
        # 如果检测到严重违规词
        if critical_words and any(
            any(cw.lower() in d.get("content", "").lower() for d in recent_danmus)
            for cw in critical_words
        ):
            return Alert(
                alert_id=self._generate_alert_id(),
                rule=rule,
                title="🚨 翻车预警",
                message=f"检测到严重违规话术反应：{', '.join(set(detected_words))}",
                level=AlertLevel.CRITICAL,
                data={
                    "detected_words": list(set(detected_words)),
                    "detected_phrases": list(set(detected_phrases)),
                },
            )
        
        # 如果检测到敏感词
        if detected_words or detected_phrases:
            return Alert(
                alert_id=self._generate_alert_id(),
                rule=rule,
                title="⚠️ 敏感词预警",
                message=f"检测到敏感话术反应：{', '.join(set(detected_words + detected_phrases))}",
                level=rule.level,
                data={
                    "detected_words": list(set(detected_words)),
                    "detected_phrases": list(set(detected_phrases)),
                },
            )
        
        return None
    
    def _check_audience_loss(self, rule: AlertRule) -> Optional[Alert]:
        """检查观众流失"""
        thresholds = rule.thresholds
        window_seconds = thresholds.get("window_seconds", 120)
        drop_threshold = thresholds.get("drop_ratio_threshold", 0.2)
        min_viewers = thresholds.get("min_viewers", 50)
        
        # 获取窗口内的观众数据
        window_viewers = self._get_viewers_in_window(window_seconds)
        
        if len(window_viewers) < 2:
            return None
        
        # 计算观众变化
        first_count = window_viewers[0]["count"]
        last_count = window_viewers[-1]["count"]
        
        if first_count < min_viewers:
            return None
        
        drop_ratio = (first_count - last_count) / first_count
        
        if drop_ratio >= drop_threshold:
            return Alert(
                alert_id=self._generate_alert_id(),
                rule=rule,
                title="📉 观众流失预警",
                message=f"过去{window_seconds}秒内，观众数量从{first_count}下降到{last_count}（下降{drop_ratio:.1%}）",
                level=rule.level,
                data={
                    "initial_count": first_count,
                    "current_count": last_count,
                    "drop_count": first_count - last_count,
                    "drop_ratio": drop_ratio,
                    "window_seconds": window_seconds,
                },
            )
        
        return None
    
    def _check_controversy(self, rule: AlertRule) -> Optional[Alert]:
        """检查争议预警"""
        thresholds = rule.thresholds
        window_seconds = thresholds.get("window_seconds", 60)
        controversy_threshold = thresholds.get("controversy_ratio_threshold", 0.25)
        min_count = thresholds.get("min_danmu_count", 20)
        
        # 获取窗口内的弹幕
        window_danmus = self._get_danmus_in_window(window_seconds)
        
        if len(window_danmus) < min_count:
            return None
        
        # 统计争议弹幕
        controversy_count = sum(
            1 for d in window_danmus
            if d.get("danmu_type") == "controversy" or d.get("key_type") == "controversy"
        )
        
        controversy_ratio = controversy_count / len(window_danmus)
        
        if controversy_ratio >= controversy_threshold:
            return Alert(
                alert_id=self._generate_alert_id(),
                rule=rule,
                title="⚠️ 争议预警",
                message=f"过去{window_seconds}秒内，争议性弹幕比例达到{controversy_ratio:.1%}（阈值：{controversy_threshold:.1%}）",
                level=rule.level,
                data={
                    "controversy_count": controversy_count,
                    "total_count": len(window_danmus),
                    "controversy_ratio": controversy_ratio,
                    "window_seconds": window_seconds,
                },
            )
        
        return None
    
    def _check_heat_drop(self, rule: AlertRule) -> Optional[Alert]:
        """检查热度下降"""
        thresholds = rule.thresholds
        window_seconds = thresholds.get("window_seconds", 180)
        drop_threshold = thresholds.get("drop_ratio_threshold", 0.5)
        min_count = thresholds.get("min_danmu_count", 30)
        
        if not self.baseline_calculated or self.baseline_danmu_rate == 0:
            return None
        
        # 获取窗口内的弹幕
        window_danmus = self._get_danmus_in_window(window_seconds)
        
        if len(window_danmus) < min_count:
            return None
        
        # 计算当前速率
        if len(window_danmus) >= 2:
            time_span = (
                window_danmus[-1]["received_at"] - window_danmus[0]["received_at"]
            ).total_seconds()
            if time_span <= 0:
                return None
            current_rate = len(window_danmus) / time_span
        else:
            return None
        
        # 计算下降比例
        drop_ratio = (self.baseline_danmu_rate - current_rate) / self.baseline_danmu_rate
        
        if drop_ratio >= drop_threshold:
            return Alert(
                alert_id=self._generate_alert_id(),
                rule=rule,
                title="📉 热度下降提醒",
                message=f"弹幕热度从{self.baseline_danmu_rate:.1f}/s下降到{current_rate:.1f}/s（下降{drop_ratio:.1%}）",
                level=rule.level,
                data={
                    "baseline_rate": self.baseline_danmu_rate,
                    "current_rate": current_rate,
                    "drop_ratio": drop_ratio,
                    "window_seconds": window_seconds,
                },
            )
        
        return None
    
    def _check_key_moment(self, rule: AlertRule) -> Optional[Alert]:
        """检查关键时刻"""
        thresholds = rule.thresholds
        window_seconds = thresholds.get("window_seconds", 30)
        heat_multiplier = thresholds.get("heat_multiplier", 3.0)
        min_count = thresholds.get("min_danmu_count", 50)
        
        if not self.baseline_calculated or self.baseline_danmu_rate == 0:
            return None
        
        # 获取窗口内的弹幕
        window_danmus = self._get_danmus_in_window(window_seconds)
        
        if len(window_danmus) < min_count:
            return None
        
        # 计算当前速率
        if len(window_danmus) >= 2:
            time_span = (
                window_danmus[-1]["received_at"] - window_danmus[0]["received_at"]
            ).total_seconds()
            if time_span <= 0:
                return None
            current_rate = len(window_danmus) / time_span
        else:
            return None
        
        # 检查是否超过基线倍数
        if current_rate >= self.baseline_danmu_rate * heat_multiplier:
            # 统计高潮弹幕
            climax_count = sum(
                1 for d in window_danmus
                if d.get("key_type") == "climax" or d.get("danmu_type") == "highlight"
            )
            
            return Alert(
                alert_id=self._generate_alert_id(),
                rule=rule,
                title="🔥 关键时刻",
                message=f"弹幕热度激增至{current_rate:.1f}/s（基线的{current_rate/self.baseline_danmu_rate:.1f}倍）",
                level=rule.level,
                data={
                    "baseline_rate": self.baseline_danmu_rate,
                    "current_rate": current_rate,
                    "heat_multiplier": current_rate / self.baseline_danmu_rate,
                    "climax_count": climax_count,
                    "window_seconds": window_seconds,
                },
            )
        
        return None
    
    def _get_danmus_in_window(self, window_seconds: int) -> List[Dict]:
        """获取窗口内的弹幕"""
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=window_seconds)
        
        return [
            d for d in self.danmu_buffer
            if d.get("received_at", now) >= cutoff
        ]
    
    def _get_viewers_in_window(self, window_seconds: int) -> List[Dict]:
        """获取窗口内的观众数据"""
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=window_seconds)
        
        return [
            v for v in self.viewer_count_history
            if v.get("timestamp", now) >= cutoff
        ]
    
    def _generate_alert_id(self) -> str:
        """生成提醒 ID"""
        self.alert_counter += 1
        return f"alert_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}_{self.alert_counter:04d}"
    
    def _record_alert(self, alert: Alert):
        """记录提醒"""
        self.alert_history.append(alert)
        self.last_alert_time[alert.rule.rule_id] = datetime.utcnow()
        
        logger.info(
            f"[{alert.level.value.upper()}] {alert.title}: {alert.message}"
        )
        
        # 发送通知
        if self.send_notification_callback:
            asyncio.create_task(
                self.send_notification_callback(alert)
            )
    
    def get_alert_history(
        self,
        limit: int = 50,
        alert_type: str = None,
        level: str = None,
        unread_only: bool = False,
    ) -> List[Dict]:
        """获取提醒历史"""
        alerts = self.alert_history
        
        # 过滤
        if alert_type:
            alerts = [
                a for a in alerts
                if a.rule.alert_type.value == alert_type
            ]
        
        if level:
            alerts = [a for a in alerts if a.level.value == level]
        
        if unread_only:
            alerts = [a for a in alerts if not a.read]
        
        # 排序（最新的在前）
        alerts = sorted(alerts, key=lambda a: a.created_at, reverse=True)
        
        # 限制数量
        alerts = alerts[:limit]
        
        return [a.to_dict() for a in alerts]
    
    def mark_as_read(self, alert_id: str) -> bool:
        """标记为已读"""
        for alert in self.alert_history:
            if alert.alert_id == alert_id:
                alert.read = True
                return True
        return False
    
    def mark_all_as_read(self) -> int:
        """全部标记为已读"""
        count = 0
        for alert in self.alert_history:
            if not alert.read:
                alert.read = True
                count += 1
        return count
    
    def get_unread_count(self) -> int:
        """获取未读数量"""
        return sum(1 for a in self.alert_history if not a.read)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        by_type = defaultdict(int)
        by_level = defaultdict(int)
        
        for alert in self.alert_history:
            by_type[alert.rule.alert_type.value] += 1
            by_level[alert.level.value] += 1
        
        return {
            "total_alerts": len(self.alert_history),
            "unread_count": self.get_unread_count(),
            "by_type": dict(by_type),
            "by_level": dict(by_level),
            "baseline": {
                "danmu_rate": self.baseline_danmu_rate,
                "viewer_count": self.baseline_viewer_count,
                "calculated": self.baseline_calculated,
            },
        }
    
    def clear_history(self, older_than_days: int = None):
        """清理历史"""
        if older_than_days:
            cutoff = datetime.utcnow() - timedelta(days=older_than_days)
            self.alert_history = [
                a for a in self.alert_history
                if a.created_at >= cutoff
            ]
        else:
            self.alert_history = []


# 单例实例
_alert_engine = None

def get_alert_engine() -> AlertEngine:
    """获取提醒引擎单例"""
    global _alert_engine
    if _alert_engine is None:
        _alert_engine = AlertEngine()
    return _alert_engine
