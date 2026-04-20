"""
LiveMirror 场控助手测试
测试实时监控、自动回复、违规处理、节奏建议等功能
"""

import asyncio
import pytest
import sys
from datetime import datetime
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.assistant_controller import (
    AssistantController,
    DanmakuMessage,
    AlertLevel,
    ViolationType,
    get_controller,
)


class TestAssistantController:
    """场控助手测试类"""
    
    @pytest.fixture
    async def controller(self):
        """创建控制器实例"""
        controller = AssistantController()
        yield controller
        # 清理
        if controller.is_live:
            await controller.stop_live()
    
    @pytest.fixture
    def sample_danmaku(self):
        """示例弹幕"""
        def create_danmaku(user_id="u1", username="测试用户", content="你好"):
            return DanmakuMessage(
                user_id=user_id,
                username=username,
                content=content,
                timestamp=datetime.now().timestamp(),
                user_level=1,
                is_fan=False,
                is_moderator=False
            )
        return create_danmaku
    
    async def test_start_stop_live(self, controller):
        """测试开始和停止直播"""
        # 开始直播
        result = await controller.start_live("test_stream_001")
        assert result is True
        assert controller.is_live is True
        assert controller.current_stream_id == "test_stream_001"
        
        # 重复开始应该失败
        result = await controller.start_live("test_stream_002")
        assert result is False
        
        # 停止直播
        result = await controller.stop_live()
        assert result is True
        assert controller.is_live is False
    
    async def test_receive_danmaku(self, controller, sample_danmaku):
        """测试接收弹幕"""
        await controller.start_live("test_stream_001")
        
        # 接收普通弹幕
        msg = sample_danmaku(content="直播好看")
        alerts = await controller.receive_danmaku(msg)
        
        assert len(controller.danmaku_buffer) == 1
        assert controller.stats["total_danmaku"] == 1
        assert len(alerts) == 0  # 普通弹幕不应触发预警
    
    async def test_auto_reply(self, controller, sample_danmaku):
        """测试自动回复功能"""
        await controller.start_live("test_stream_001")
        controller.config["auto_reply_enabled"] = True
        
        # 触发常见问题
        msg = sample_danmaku(content="直播什么时候结束")
        initial_replies = controller.stats["auto_replies"]
        
        await controller.receive_danmaku(msg)
        
        # 应该触发自动回复
        assert controller.stats["auto_replies"] > initial_replies
        
        # 检查日志
        logs = controller.get_operation_logs(limit=5)
        auto_reply_logs = [l for l in logs if l.action == "auto_reply"]
        assert len(auto_reply_logs) > 0
    
    async def test_violation_detection(self, controller, sample_danmaku):
        """测试违规检测"""
        await controller.start_live("test_stream_001")
        controller.config["violation_detection_enabled"] = True
        
        # 测试辱骂言论
        msg = sample_danmaku(content="傻逼东西", user_id="bad_user")
        alerts = await controller.receive_danmaku(msg)
        
        # 应该触发预警
        assert len(alerts) > 0
        assert any(a.alert_type == "violation" for a in alerts)
        
        # 检查违规处理日志
        logs = controller.get_operation_logs(limit=5)
        violation_logs = [l for l in logs if l.action == "handle_violation"]
        assert len(violation_logs) > 0
        
        # 检查统计
        assert controller.stats["violations_handled"] > 0
    
    async def test_spam_detection(self, controller, sample_danmaku):
        """测试刷屏检测"""
        await controller.start_live("test_stream_001")
        
        # 短时间内发送大量弹幕
        user_id = "spam_user"
        for i in range(15):
            msg = sample_danmaku(
                user_id=user_id,
                content=f"消息{i}"
            )
            await controller.receive_danmaku(msg)
        
        # 应该触发刷屏预警
        alerts = controller.get_alerts(limit=10)
        spam_alerts = [a for a in alerts if a.get("alert_type") == "spam"]
        assert len(spam_alerts) > 0
    
    async def test_emotion_analysis(self, controller, sample_danmaku):
        """测试情绪分析"""
        await controller.start_live("test_stream_001")
        
        # 发送积极弹幕
        for i in range(10):
            msg = sample_danmaku(content="好棒！喜欢！666")
            await controller.receive_danmaku(msg)
        
        # 等待情绪分析
        await asyncio.sleep(2)
        
        # 获取情绪数据
        status = controller.get_status()
        emotion = status.get("current_emotion")
        
        assert emotion is not None
        assert emotion["positive"] > 0
        
        # 获取情绪趋势
        trend = controller.get_emotion_trend(minutes=1)
        assert len(trend) > 0
    
    async def test_rhythm_suggestion(self, controller, sample_danmaku):
        """测试节奏建议"""
        await controller.start_live("test_stream_001")
        
        # 模拟情绪数据
        from services.assistant_controller import AudienceEmotion
        
        # 添加低情绪数据
        low_emotion = AudienceEmotion(
            positive=0.1,
            neutral=0.3,
            negative=0.6,
            excited=0.0,
            timestamp=datetime.now().timestamp()
        )
        controller.emotion_history = [low_emotion] * 10
        
        # 生成建议
        suggestion = await controller._generate_rhythm_suggestion()
        
        # 应该建议互动
        assert suggestion is not None
        assert suggestion.suggestion_type == "interaction"
        assert suggestion.priority >= 4
    
    async def test_get_status(self, controller, sample_danmaku):
        """测试获取状态"""
        await controller.start_live("test_stream_001")
        
        # 发送一些弹幕
        for i in range(5):
            msg = sample_danmaku(content=f"测试{i}")
            await controller.receive_danmaku(msg)
        
        # 获取状态
        status = controller.get_status()
        
        assert status["is_live"] is True
        assert status["stream_id"] == "test_stream_001"
        assert status["stats"]["total_danmaku"] == 5
        assert "recent_logs" in status
    
    async def test_operation_logs(self, controller, sample_danmaku):
        """测试操作日志"""
        await controller.start_live("test_stream_001")
        
        # 执行一些操作
        await controller.receive_danmaku(sample_danmaku(content="你好"))
        controller._log_operation("test_action", {"key": "value"})
        
        # 获取日志
        logs = controller.get_operation_logs(limit=10)
        
        assert len(logs) > 0
        assert any(log["action"] == "start_live" for log in logs)
        assert any(log["action"] == "test_action" for log in logs)
    
    async def test_alerts_filtering(self, controller, sample_danmaku):
        """测试预警筛选"""
        await controller.start_live("test_stream_001")
        
        # 触发不同类型的预警
        msg1 = sample_danmaku(content="傻逼", user_id="user1")
        msg2 = sample_danmaku(content="垃圾", user_id="user2")
        
        await controller.receive_danmaku(msg1)
        await controller.receive_danmaku(msg2)
        
        # 获取所有预警
        all_alerts = controller.get_alerts(limit=50)
        assert len(all_alerts) > 0
        
        # 按等级筛选
        critical_alerts = controller.get_alerts(limit=50)
        critical_alerts = [a for a in critical_alerts if a.get("level") == "critical"]
        assert len(critical_alerts) > 0


class TestViolationKeywords:
    """违规词库测试"""
    
    def test_violation_types(self):
        """测试违规类型枚举"""
        assert ViolationType.SPAM.value == "spam"
        assert ViolationType.ABUSE.value == "abuse"
        assert ViolationType.ADVERTISEMENT.value == "advertisement"
        assert ViolationType.SENSITIVE.value == "sensitive"
    
    def test_default_keywords(self):
        """测试默认违规词库"""
        controller = AssistantController()
        
        assert ViolationType.SPAM in controller.violation_keywords
        assert ViolationType.ABUSE in controller.violation_keywords
        assert len(controller.violation_keywords[ViolationType.ABUSE]) > 0


async def run_tests():
    """运行所有测试"""
    print("=" * 60)
    print("LiveMirror 场控助手测试")
    print("=" * 60)
    
    test_instance = TestAssistantController()
    
    # 创建控制器
    controller = AssistantController()
    
    tests = [
        ("开始/停止直播", test_instance.test_start_stop_live(controller)),
        ("接收弹幕", test_instance.test_receive_danmaku(controller, lambda **kw: DanmakuMessage(**kw))),
        ("自动回复", test_instance.test_auto_reply(controller, lambda **kw: DanmakuMessage(**kw))),
        ("违规检测", test_instance.test_violation_detection(controller, lambda **kw: DanmakuMessage(**kw))),
        ("刷屏检测", test_instance.test_spam_detection(controller, lambda **kw: DanmakuMessage(**kw))),
        ("情绪分析", test_instance.test_emotion_analysis(controller, lambda **kw: DanmakuMessage(**kw))),
        ("节奏建议", test_instance.test_rhythm_suggestion(controller, lambda **kw: DanmakuMessage(**kw))),
        ("获取状态", test_instance.test_get_status(controller, lambda **kw: DanmakuMessage(**kw))),
        ("操作日志", test_instance.test_operation_logs(controller, lambda **kw: DanmakuMessage(**kw))),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_coro in tests:
        try:
            # 重置控制器
            controller = AssistantController()
            await test_coro
            print(f"✅ {test_name}: 通过")
            passed += 1
        except Exception as e:
            print(f"❌ {test_name}: 失败 - {e}")
            failed += 1
    
    print("=" * 60)
    print(f"测试结果：{passed} 通过，{failed} 失败")
    print("=" * 60)
    
    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(run_tests())
    sys.exit(0 if success else 1)
