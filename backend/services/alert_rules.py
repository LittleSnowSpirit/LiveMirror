"""
提醒规则定义
定义各种提醒规则和阈值配置
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from enum import Enum
import json


class AlertType(str, Enum):
    """提醒类型"""
    SENTIMENT_LOW = "sentiment_low"  # 低情绪预警
    SPEECH_RISK = "speech_risk"  # 话术风险
    AUDIENCE_LOSS = "audience_loss"  # 观众流失
    CONTROVERSY = "controversy"  # 争议预警
    HEAT_DROP = "heat_drop"  # 热度下降
    KEY_MOMENT = "key_moment"  # 关键时刻


class AlertLevel(str, Enum):
    """提醒级别"""
    INFO = "info"  # 信息
    WARNING = "warning"  # 警告
    CRITICAL = "critical"  # 严重


class AlertChannel(str, Enum):
    """推送渠道"""
    IN_APP = "in_app"  # 站内信
    EMAIL = "email"  # 邮件
    WECHAT = "wechat"  # 微信


@dataclass
class AlertRule:
    """提醒规则"""
    rule_id: str
    rule_name: str
    alert_type: AlertType
    level: AlertLevel
    description: str
    enabled: bool = True
    
    # 阈值配置
    thresholds: Dict[str, Any] = field(default_factory=dict)
    
    # 触发条件函数
    condition_func: Optional[Callable] = None
    
    # 推送渠道
    channels: List[AlertChannel] = field(default_factory=lambda: [AlertChannel.IN_APP])
    
    # 冷却时间（秒）- 避免重复提醒
    cooldown_seconds: int = 300
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "rule_id": self.rule_id,
            "rule_name": self.rule_name,
            "alert_type": self.alert_type.value,
            "level": self.level.value,
            "description": self.description,
            "enabled": self.enabled,
            "thresholds": self.thresholds,
            "channels": [c.value for c in self.channels],
            "cooldown_seconds": self.cooldown_seconds,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AlertRule":
        """从字典创建"""
        return cls(
            rule_id=data["rule_id"],
            rule_name=data["rule_name"],
            alert_type=AlertType(data["alert_type"]),
            level=AlertLevel(data["level"]),
            description=data["description"],
            enabled=data.get("enabled", True),
            thresholds=data.get("thresholds", {}),
            channels=[AlertChannel(c) for c in data.get("channels", ["in_app"])],
            cooldown_seconds=data.get("cooldown_seconds", 300),
        )


class AlertRuleManager:
    """提醒规则管理器"""
    
    def __init__(self):
        self.rules: Dict[str, AlertRule] = {}
        self._init_default_rules()
    
    def _init_default_rules(self):
        """初始化默认规则"""
        
        # 1. 低情绪预警规则
        self.add_rule(AlertRule(
            rule_id="sentiment_low_1",
            rule_name="低情绪预警 - 轻度",
            alert_type=AlertType.SENTIMENT_LOW,
            level=AlertLevel.WARNING,
            description="当负面情绪弹幕比例超过阈值时发出警告",
            thresholds={
                "negative_ratio_threshold": 0.3,  # 负面情绪比例阈值 30%
                "window_seconds": 60,  # 统计窗口 60 秒
                "min_danmu_count": 10,  # 最小弹幕数量
            },
            channels=[AlertChannel.IN_APP, AlertChannel.WECHAT],
            cooldown_seconds=300,
        ))
        
        self.add_rule(AlertRule(
            rule_id="sentiment_low_2",
            rule_name="低情绪预警 - 严重",
            alert_type=AlertType.SENTIMENT_LOW,
            level=AlertLevel.CRITICAL,
            description="当负面情绪弹幕比例严重超标时发出严重警告",
            thresholds={
                "negative_ratio_threshold": 0.5,  # 负面情绪比例阈值 50%
                "window_seconds": 60,
                "min_danmu_count": 10,
            },
            channels=[AlertChannel.IN_APP, AlertChannel.WECHAT, AlertChannel.EMAIL],
            cooldown_seconds=180,
        ))
        
        # 2. 话术风险规则
        self.add_rule(AlertRule(
            rule_id="speech_risk_1",
            rule_name="敏感词预警",
            alert_type=AlertType.SPEECH_RISK,
            level=AlertLevel.WARNING,
            description="当检测到敏感词或不当话术时发出警告",
            thresholds={
                "sensitive_words": [
                    "最", "第一", "绝对", "100%", " guaranteed", " guaranteed",
                    "治愈", "根治", "无效退款", "国家级", "世界级",
                ],
                "risk_phrases": [
                    "包治百病", "永不复发", "绝对有效", "百分百",
                ],
            },
            channels=[AlertChannel.IN_APP],
            cooldown_seconds=60,
        ))
        
        self.add_rule(AlertRule(
            rule_id="speech_risk_2",
            rule_name="翻车预警",
            alert_type=AlertType.SPEECH_RISK,
            level=AlertLevel.CRITICAL,
            description="当检测到严重违规话术时发出严重警告",
            thresholds={
                "critical_words": [
                    "骗局", "骗子", "假货", "假一赔十", "投诉", "举报",
                    "虚假宣传", "误导消费者", "违法",
                ],
            },
            channels=[AlertChannel.IN_APP, AlertChannel.WECHAT, AlertChannel.EMAIL],
            cooldown_seconds=30,
        ))
        
        # 3. 观众流失规则
        self.add_rule(AlertRule(
            rule_id="audience_loss_1",
            rule_name="观众流失预警 - 轻度",
            alert_type=AlertType.AUDIENCE_LOSS,
            level=AlertLevel.WARNING,
            description="当观众数量快速下降时发出警告",
            thresholds={
                "drop_ratio_threshold": 0.2,  # 下降比例 20%
                "window_seconds": 120,  # 统计窗口 2 分钟
                "min_viewers": 50,  # 最小观众数
            },
            channels=[AlertChannel.IN_APP, AlertChannel.WECHAT],
            cooldown_seconds=300,
        ))
        
        self.add_rule(AlertRule(
            rule_id="audience_loss_2",
            rule_name="观众流失预警 - 严重",
            alert_type=AlertType.AUDIENCE_LOSS,
            level=AlertLevel.CRITICAL,
            description="当观众数量急剧下降时发出严重警告",
            thresholds={
                "drop_ratio_threshold": 0.4,  # 下降比例 40%
                "window_seconds": 60,
                "min_viewers": 100,
            },
            channels=[AlertChannel.IN_APP, AlertChannel.WECHAT, AlertChannel.EMAIL],
            cooldown_seconds=180,
        ))
        
        # 4. 争议预警规则
        self.add_rule(AlertRule(
            rule_id="controversy_1",
            rule_name="争议预警",
            alert_type=AlertType.CONTROVERSY,
            level=AlertLevel.WARNING,
            description="当检测到大量争议性弹幕时发出警告",
            thresholds={
                "controversy_ratio_threshold": 0.25,  # 争议弹幕比例 25%
                "window_seconds": 60,
                "min_danmu_count": 20,
            },
            channels=[AlertChannel.IN_APP, AlertChannel.WECHAT],
            cooldown_seconds=300,
        ))
        
        # 5. 热度下降规则
        self.add_rule(AlertRule(
            rule_id="heat_drop_1",
            rule_name="热度下降预警",
            alert_type=AlertType.HEAT_DROP,
            level=AlertLevel.INFO,
            description="当弹幕热度显著下降时提醒",
            thresholds={
                "drop_ratio_threshold": 0.5,  # 下降比例 50%
                "window_seconds": 180,  # 统计窗口 3 分钟
                "min_danmu_count": 30,
            },
            channels=[AlertChannel.IN_APP],
            cooldown_seconds=600,
        ))
        
        # 6. 关键时刻规则
        self.add_rule(AlertRule(
            rule_id="key_moment_1",
            rule_name="关键时刻提醒",
            alert_type=AlertType.KEY_MOMENT,
            level=AlertLevel.INFO,
            description="当检测到直播关键时刻（高潮、抢购等）时提醒",
            thresholds={
                "heat_multiplier": 3.0,  # 热度倍数（超过平均 3 倍）
                "window_seconds": 30,
                "min_danmu_count": 50,
            },
            channels=[AlertChannel.IN_APP],
            cooldown_seconds=120,
        ))
    
    def add_rule(self, rule: AlertRule):
        """添加规则"""
        self.rules[rule.rule_id] = rule
    
    def get_rule(self, rule_id: str) -> Optional[AlertRule]:
        """获取规则"""
        return self.rules.get(rule_id)
    
    def get_all_rules(self) -> List[AlertRule]:
        """获取所有规则"""
        return list(self.rules.values())
    
    def get_enabled_rules(self) -> List[AlertRule]:
        """获取所有启用的规则"""
        return [rule for rule in self.rules.values() if rule.enabled]
    
    def get_rules_by_type(self, alert_type: AlertType) -> List[AlertRule]:
        """按类型获取规则"""
        return [
            rule for rule in self.rules.values()
            if rule.alert_type == alert_type and rule.enabled
        ]
    
    def update_rule(self, rule_id: str, updates: Dict[str, Any]) -> bool:
        """更新规则"""
        if rule_id not in self.rules:
            return False
        
        rule = self.rules[rule_id]
        for key, value in updates.items():
            if hasattr(rule, key):
                setattr(rule, key, value)
        
        return True
    
    def enable_rule(self, rule_id: str) -> bool:
        """启用规则"""
        return self.update_rule(rule_id, {"enabled": True})
    
    def disable_rule(self, rule_id: str) -> bool:
        """禁用规则"""
        return self.update_rule(rule_id, {"enabled": False})
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "rules": [rule.to_dict() for rule in self.rules.values()],
            "total_count": len(self.rules),
            "enabled_count": len(self.get_enabled_rules()),
        }
    
    def from_dict(self, data: Dict[str, Any]):
        """从字典加载"""
        self.rules = {}
        for rule_data in data.get("rules", []):
            rule = AlertRule.from_dict(rule_data)
            self.rules[rule.rule_id] = rule


# 单例实例
_rule_manager = None

def get_rule_manager() -> AlertRuleManager:
    """获取规则管理器单例"""
    global _rule_manager
    if _rule_manager is None:
        _rule_manager = AlertRuleManager()
    return _rule_manager
