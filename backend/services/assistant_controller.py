"""
LiveMirror 智能场控助手服务
实时辅助直播运营，提供弹幕监控、自动回复、违规处理、情绪分析和节奏建议
"""

import asyncio
import json
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import random

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AlertLevel(Enum):
    """预警等级"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class ViolationType(Enum):
    """违规类型"""
    SPAM = "spam"  # 刷屏
    ABUSE = "abuse"  # 辱骂
    ADVERTISEMENT = "advertisement"  # 广告
    SENSITIVE = "sensitive"  # 敏感内容
    OTHER = "other"  # 其他


@dataclass
class DanmakuMessage:
    """弹幕消息"""
    user_id: str
    username: str
    content: str
    timestamp: float
    user_level: int = 1
    is_fan: bool = False
    is_moderator: bool = False


@dataclass
class Alert:
    """预警消息"""
    level: AlertLevel
    message: str
    alert_type: str
    timestamp: float
    user_id: Optional[str] = None
    content: Optional[str] = None


@dataclass
class AudienceEmotion:
    """观众情绪状态"""
    positive: float = 0.0  # 积极
    neutral: float = 0.0   # 中性
    negative: float = 0.0  # 消极
    excited: float = 0.0   # 兴奋
    bored: float = 0.0     # 无聊
    timestamp: float = field(default_factory=lambda: datetime.now().timestamp())


@dataclass
class RhythmSuggestion:
    """直播节奏建议"""
    suggestion_type: str  # "promotion", "interaction", "break", "content"
    priority: int  # 1-5, 5 最高
    reason: str
    timing: str  # "now", "soon", "later"
    content: str


@dataclass
class ControllerLog:
    """场控操作日志"""
    timestamp: float
    action: str
    details: Dict[str, Any]
    operator: str = "auto"  # "auto" 或 "manual"


class AssistantController:
    """智能场控助手主服务"""
    
    def __init__(self):
        # 配置
        self.config = {
            "auto_reply_enabled": True,
            "violation_detection_enabled": True,
            "emotion_monitoring_enabled": True,
            "rhythm_suggestion_enabled": True,
        }
        
        # 常见问题自动回复库
        self.faq_responses = self._load_faq_responses()
        
        # 违规词库
        self.violation_keywords = self._load_violation_keywords()
        
        # 状态
        self.is_live = False
        self.current_stream_id: Optional[str] = None
        self.danmaku_buffer: List[DanmakuMessage] = []
        self.alerts: List[Alert] = []
        self.emotion_history: List[AudienceEmotion] = []
        self.suggestions: List[RhythmSuggestion] = []
        self.operation_logs: List[ControllerLog] = []
        
        # 统计
        self.stats = {
            "total_danmaku": 0,
            "auto_replies": 0,
            "violations_handled": 0,
            "alerts_triggered": 0,
        }
        
        # 异步任务
        self._monitor_task: Optional[asyncio.Task] = None
        self._emotion_task: Optional[asyncio.Task] = None
        self._rhythm_task: Optional[asyncio.Task] = None
        
        logger.info("AssistantController 初始化完成")
    
    def _load_faq_responses(self) -> Dict[str, str]:
        """加载常见问题回复库"""
        return {
            r"直播什么时候结束": "直播预计持续到晚上 10 点哦～",
            r"有优惠吗|便宜点|打折": "当前直播间有专属优惠券，点击直播间下方链接领取！",
            r"怎么购买|在哪里买": "点击直播间下方购物车图标就可以购买啦～",
            r"发什么快递|物流": "我们默认发顺丰快递，48 小时内发货哦～",
            r"有现货吗|什么时候发货": "都是现货哦，拍下后 48 小时内发货！",
            r"质量怎么样|好不好": "质量超好的！支持 7 天无理由退换～",
            r"主播看一下": "看到啦！感谢宝宝的支持～",
            r"在吗|有人吗": "在的在的！有什么问题尽管问～",
            r"多少钱|价格": "价格已经在购物车标注啦，还有直播间专属优惠哦～",
            r"尺码|大小": "尺码标准哦，按平时穿的拍就可以，不确定可以问客服～",
        }
    
    def _load_violation_keywords(self) -> Dict[ViolationType, List[str]]:
        """加载违规词库"""
        return {
            ViolationType.SPAM: ["哈哈哈", "666", "啊啊啊", "!!!", "???"],
            ViolationType.ABUSE: ["傻逼", "垃圾", "废物", "滚", "去死"],
            ViolationType.ADVERTISEMENT: ["加微信", "QQ", "私聊", "兼职", "刷单"],
            ViolationType.SENSITIVE: ["政治", "敏感", "违规", "封禁"],
        }
    
    async def start_live(self, stream_id: str) -> bool:
        """开始直播监控"""
        if self.is_live:
            logger.warning("已经在直播中")
            return False
        
        self.is_live = True
        self.current_stream_id = stream_id
        self.danmaku_buffer.clear()
        self.alerts.clear()
        self.stats = {k: 0 for k in self.stats}
        
        # 启动监控任务
        self._monitor_task = asyncio.create_task(self._danmaku_monitor_loop())
        self._emotion_task = asyncio.create_task(self._emotion_analysis_loop())
        self._rhythm_task = asyncio.create_task(self._rhythm_suggestion_loop())
        
        self._log_operation("start_live", {"stream_id": stream_id})
        logger.info(f"开始直播监控，stream_id: {stream_id}")
        return True
    
    async def stop_live(self) -> bool:
        """停止直播监控"""
        if not self.is_live:
            return False
        
        self.is_live = False
        
        # 停止监控任务
        for task in [self._monitor_task, self._emotion_task, self._rhythm_task]:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        self._log_operation("stop_live", {"stream_id": self.current_stream_id})
        logger.info("停止直播监控")
        return True
    
    async def receive_danmaku(self, message: DanmakuMessage) -> List[Alert]:
        """接收弹幕消息并处理"""
        if not self.is_live:
            return []
        
        self.danmaku_buffer.append(message)
        self.stats["total_danmaku"] += 1
        
        # 保持缓冲区大小
        if len(self.danmaku_buffer) > 1000:
            self.danmaku_buffer = self.danmaku_buffer[-500:]
        
        alerts = []
        
        # 1. 检测违规
        if self.config["violation_detection_enabled"]:
            violation_alert = await self._check_violation(message)
            if violation_alert:
                alerts.append(violation_alert)
        
        # 2. 检测异常行为（刷屏等）
        spam_alert = await self._check_spam_behavior(message)
        if spam_alert:
            alerts.append(spam_alert)
        
        # 3. 自动回复
        if self.config["auto_reply_enabled"]:
            await self._try_auto_reply(message)
        
        # 4. 记录预警
        for alert in alerts:
            self.alerts.append(alert)
            self.stats["alerts_triggered"] += 1
        
        return alerts
    
    async def _check_violation(self, message: DanmakuMessage) -> Optional[Alert]:
        """检查违规内容"""
        content = message.content.lower()
        
        for violation_type, keywords in self.violation_keywords.items():
            for keyword in keywords:
                if keyword.lower() in content:
                    # 执行处理（禁言/警告）
                    await self._handle_violation(message, violation_type)
                    
                    return Alert(
                        level=AlertLevel.CRITICAL if violation_type in [ViolationType.ABUSE, ViolationType.SENSITIVE] else AlertLevel.WARNING,
                        message=f"检测到{violation_type.value}言论",
                        alert_type="violation",
                        timestamp=datetime.now().timestamp(),
                        user_id=message.user_id,
                        content=message.content
                    )
        
        return None
    
    async def _handle_violation(self, message: DanmakuMessage, violation_type: ViolationType):
        """处理违规行为"""
        self.stats["violations_handled"] += 1
        
        # 模拟处理动作
        action = "mute" if violation_type in [ViolationType.ABUSE, ViolationType.SENSITIVE] else "warn"
        
        self._log_operation("handle_violation", {
            "user_id": message.user_id,
            "username": message.username,
            "violation_type": violation_type.value,
            "action": action,
            "content": message.content
        })
        
        logger.info(f"处理违规：{message.username} - {violation_type.value} - 动作：{action}")
    
    async def _check_spam_behavior(self, message: DanmakuMessage) -> Optional[Alert]:
        """检测刷屏行为"""
        recent_messages = [
            m for m in self.danmaku_buffer[-50:]
            if m.user_id == message.user_id
        ]
        
        # 短时间大量发言
        if len(recent_messages) > 10:
            time_span = recent_messages[-1].timestamp - recent_messages[0].timestamp
            if time_span < 60:  # 60 秒内超过 10 条
                return Alert(
                    level=AlertLevel.WARNING,
                    message=f"用户刷屏警告",
                    alert_type="spam",
                    timestamp=datetime.now().timestamp(),
                    user_id=message.user_id,
                    content=f"60 秒内发送{len(recent_messages)}条消息"
                )
        
        return None
    
    async def _try_auto_reply(self, message: DanmakuMessage):
        """尝试自动回复"""
        if message.is_moderator or message.user_level > 10:
            return  # 管理员和高等级用户不触发自动回复
        
        content = message.content
        for pattern, response in self.faq_responses.items():
            if re.search(pattern, content, re.IGNORECASE):
                # 发送自动回复
                await self._send_auto_reply(response, message)
                self.stats["auto_replies"] += 1
                break
    
    async def _send_auto_reply(self, response: str, original_message: DanmakuMessage):
        """发送自动回复"""
        self._log_operation("auto_reply", {
            "target_user": original_message.username,
            "response": response,
            "trigger": original_message.content
        })
        
        logger.info(f"自动回复 {original_message.username}: {response}")
    
    async def _danmaku_monitor_loop(self):
        """弹幕监控循环"""
        while self.is_live:
            await asyncio.sleep(1)
            # 实时统计
            recent_count = len([
                m for m in self.danmaku_buffer
                if datetime.now().timestamp() - m.timestamp < 60
            ])
            if recent_count > 100:
                logger.info(f"弹幕高峰：{recent_count}条/分钟")
    
    async def _emotion_analysis_loop(self):
        """观众情绪分析循环"""
        while self.is_live:
            await asyncio.sleep(10)  # 每 10 秒分析一次
            
            emotion = await self._analyze_current_emotion()
            self.emotion_history.append(emotion)
            
            # 保持历史记录
            if len(self.emotion_history) > 100:
                self.emotion_history = self.emotion_history[-50:]
            
            logger.info(f"情绪分析：积极{emotion.positive:.2f} 中性{emotion.neutral:.2f} 消极{emotion.negative:.2f}")
    
    async def _analyze_current_emotion(self) -> AudienceEmotion:
        """分析当前观众情绪"""
        recent_messages = [
            m for m in self.danmaku_buffer
            if datetime.now().timestamp() - m.timestamp < 60
        ]
        
        if not recent_messages:
            return AudienceEmotion()
        
        positive_keywords = ["好", "棒", "喜欢", "爱", "赞", "666", "哈哈", "开心"]
        negative_keywords = ["差", "烂", "讨厌", "烦", "无聊", "垃圾", "失望"]
        excited_keywords = ["！！！", "？？？", "啊啊啊", "哇", "天哪"]
        
        positive_count = sum(
            1 for m in recent_messages
            if any(kw in m.content for kw in positive_keywords)
        )
        negative_count = sum(
            1 for m in recent_messages
            if any(kw in m.content for kw in negative_keywords)
        )
        excited_count = sum(
            1 for m in recent_messages
            if any(kw in m.content for kw in excited_keywords)
        )
        
        total = len(recent_messages)
        
        return AudienceEmotion(
            positive=positive_count / total if total > 0 else 0,
            negative=negative_count / total if total > 0 else 0,
            neutral=1 - (positive_count + negative_count) / total if total > 0 else 0,
            excited=excited_count / total if total > 0 else 0,
            bored=0.0,  # 简化处理
            timestamp=datetime.now().timestamp()
        )
    
    async def _rhythm_suggestion_loop(self):
        """直播节奏建议循环"""
        while self.is_live:
            await asyncio.sleep(30)  # 每 30 秒生成建议
            
            suggestion = await self._generate_rhythm_suggestion()
            if suggestion:
                self.suggestions.append(suggestion)
                logger.info(f"节奏建议：{suggestion.suggestion_type} - {suggestion.reason}")
    
    async def _generate_rhythm_suggestion(self) -> Optional[RhythmSuggestion]:
        """生成直播节奏建议"""
        if not self.emotion_history:
            return None
        
        recent_emotion = self.emotion_history[-1]
        avg_emotion = AudienceEmotion(
            positive=sum(e.positive for e in self.emotion_history[-5:]) / min(len(self.emotion_history), 5),
            negative=sum(e.negative for e in self.emotion_history[-5:]) / min(len(self.emotion_history), 5),
            excited=sum(e.excited for e in self.emotion_history[-5:]) / min(len(self.emotion_history), 5),
        )
        
        # 情绪低落时建议互动
        if avg_emotion.positive < 0.3 and avg_emotion.negative > 0.3:
            return RhythmSuggestion(
                suggestion_type="interaction",
                priority=5,
                reason="观众情绪偏低，需要提升氛围",
                timing="now",
                content="建议进行抽奖或问答互动，提升观众参与度"
            )
        
        # 情绪高涨时建议促销
        if avg_emotion.positive > 0.6 and avg_emotion.excited > 0.4:
            return RhythmSuggestion(
                suggestion_type="promotion",
                priority=4,
                reason="观众情绪高涨，适合促销转化",
                timing="now",
                content="现在推出限时优惠，转化率会更高"
            )
        
        # 直播时长建议休息
        if len(self.operation_logs) > 0:
            first_log_time = self.operation_logs[0].timestamp
            duration_hours = (datetime.now().timestamp() - first_log_time) / 3600
            if duration_hours > 2 and int(duration_hours * 2) % 2 == 0:
                return RhythmSuggestion(
                    suggestion_type="break",
                    priority=3,
                    reason=f"已直播{duration_hours:.1f}小时，建议短暂休息",
                    timing="soon",
                    content="播放一段视频或音乐，主播休息 5 分钟"
                )
        
        return None
    
    def _log_operation(self, action: str, details: Dict[str, Any]):
        """记录操作日志"""
        log = ControllerLog(
            timestamp=datetime.now().timestamp(),
            action=action,
            details=details
        )
        self.operation_logs.append(log)
        
        # 保持日志数量
        if len(self.operation_logs) > 1000:
            self.operation_logs = self.operation_logs[-500:]
    
    def get_status(self) -> Dict[str, Any]:
        """获取当前状态"""
        return {
            "is_live": self.is_live,
            "stream_id": self.current_stream_id,
            "stats": self.stats.copy(),
            "recent_alerts": [asdict(a) for a in self.alerts[-10:]],
            "current_emotion": asdict(self.emotion_history[-1]) if self.emotion_history else None,
            "recent_suggestions": [asdict(s) for s in self.suggestions[-5:]],
            "recent_logs": [asdict(l) for l in self.operation_logs[-20:]],
        }
    
    def get_operation_logs(self, limit: int = 50) -> List[Dict[str, Any]]:
        """获取操作日志"""
        return [asdict(log) for log in self.operation_logs[-limit:]]
    
    def get_alerts(self, limit: int = 50) -> List[Dict[str, Any]]:
        """获取预警记录"""
        return [asdict(alert) for alert in self.alerts[-limit:]]
    
    def get_emotion_trend(self, minutes: int = 10) -> List[Dict[str, Any]]:
        """获取情绪趋势"""
        points = minutes * 6  # 每 10 秒一个点
        return [asdict(e) for e in self.emotion_history[-points:]]
    
    def get_suggestions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """获取节奏建议"""
        return [asdict(s) for s in self.suggestions[-limit:]]


# 全局单例
_controller_instance: Optional[AssistantController] = None

def get_controller() -> AssistantController:
    """获取场控助手实例"""
    global _controller_instance
    if _controller_instance is None:
        _controller_instance = AssistantController()
    return _controller_instance


if __name__ == "__main__":
    # 测试代码
    async def test():
        controller = get_controller()
        
        # 模拟开始直播
        await controller.start_live("test_stream_001")
        
        # 模拟接收弹幕
        test_messages = [
            DanmakuMessage("u1", "小明", "直播什么时候结束", datetime.now().timestamp()),
            DanmakuMessage("u2", "小红", "有优惠吗", datetime.now().timestamp()),
            DanmakuMessage("u3", "小黑", "傻逼东西", datetime.now().timestamp()),
            DanmakuMessage("u4", "小白", "666666", datetime.now().timestamp()),
        ]
        
        for msg in test_messages:
            alerts = await controller.receive_danmaku(msg)
            if alerts:
                print(f"触发预警：{alerts}")
        
        # 等待情绪分析
        await asyncio.sleep(15)
        
        # 获取状态
        status = controller.get_status()
        print(f"\n当前状态：{json.dumps(status, indent=2, ensure_ascii=False)}")
        
        # 停止直播
        await controller.stop_live()
    
    asyncio.run(test())
