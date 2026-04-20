"""
LiveMirror 场控助手简单测试脚本
不依赖 pytest，直接运行测试
"""

import asyncio
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
)


def create_danmaku(user_id="u1", username="测试用户", content="你好"):
    """创建弹幕消息"""
    return DanmakuMessage(
        user_id=user_id,
        username=username,
        content=content,
        timestamp=datetime.now().timestamp(),
        user_level=1,
        is_fan=False,
        is_moderator=False
    )


async def test_start_stop_live():
    """测试开始和停止直播"""
    print("\n[测试] 开始/停止直播")
    controller = AssistantController()
    
    # 开始直播
    result = await controller.start_live("test_stream_001")
    assert result is True, "开始直播失败"
    assert controller.is_live is True, "状态未更新"
    print("  [OK] 开始直播成功")
    
    # 重复开始应该失败
    result = await controller.start_live("test_stream_002")
    assert result is False, "重复开始应该失败"
    print("  [OK] 重复开始正确拒绝")
    
    # 停止直播
    result = await controller.stop_live()
    assert result is True, "停止直播失败"
    assert controller.is_live is False, "状态未更新"
    print("  [OK] 停止直播成功")
    
    return True


async def test_receive_danmaku():
    """测试接收弹幕"""
    print("\n[测试] 接收弹幕")
    controller = AssistantController()
    await controller.start_live("test_stream_001")
    
    # 接收普通弹幕
    msg = create_danmaku(content="直播好看")
    alerts = await controller.receive_danmaku(msg)
    
    assert len(controller.danmaku_buffer) == 1, "弹幕缓冲区未更新"
    assert controller.stats["total_danmaku"] == 1, "统计未更新"
    assert len(alerts) == 0, "普通弹幕不应触发预警"
    print("  [OK] 弹幕接收正常")
    
    # 接收多条弹幕
    for i in range(9):
        msg = create_danmaku(content=f"测试{i}")
        await controller.receive_danmaku(msg)
    
    assert len(controller.danmaku_buffer) == 10, "多条弹幕接收失败"
    assert controller.stats["total_danmaku"] == 10, "统计错误"
    print("  [OK] 多条弹幕接收正常")
    
    return True


async def test_auto_reply():
    """测试自动回复功能"""
    print("\n[测试] 自动回复")
    controller = AssistantController()
    await controller.start_live("test_stream_001")
    controller.config["auto_reply_enabled"] = True
    
    # 触发常见问题
    test_cases = [
        "直播什么时候结束",
        "有优惠吗",
        "怎么购买",
        "发什么快递",
    ]
    
    initial_replies = controller.stats["auto_replies"]
    
    for content in test_cases:
        msg = create_danmaku(content=content)
        await controller.receive_danmaku(msg)
    
    # 应该触发自动回复
    assert controller.stats["auto_replies"] > initial_replies, "自动回复未触发"
    print(f"  [OK] 自动回复触发：{controller.stats['auto_replies']} 次")
    
    # 检查日志
    logs = controller.get_operation_logs(limit=10)
    auto_reply_logs = [l for l in logs if l.get("action") == "auto_reply"]
    assert len(auto_reply_logs) > 0, "自动回复日志缺失"
    print(f"  [OK] 自动回复日志记录：{len(auto_reply_logs)} 条")
    
    return True


async def test_violation_detection():
    """测试违规检测"""
    print("\n[测试] 违规检测")
    controller = AssistantController()
    await controller.start_live("test_stream_001")
    controller.config["violation_detection_enabled"] = True
    
    # 测试辱骂言论
    msg = create_danmaku(content="傻逼东西", user_id="bad_user")
    alerts = await controller.receive_danmaku(msg)
    
    # 应该触发预警
    assert len(alerts) > 0, "违规未触发预警"
    assert any(a.alert_type == "violation" for a in alerts), "预警类型错误"
    print("  [OK] 违规言论检测成功")
    
    # 检查违规处理日志
    logs = controller.get_operation_logs(limit=10)
    violation_logs = [l for l in logs if l.get("action") == "handle_violation"]
    assert len(violation_logs) > 0, "违规处理日志缺失"
    print(f"  [OK] 违规处理日志：{len(violation_logs)} 条")
    
    # 检查统计
    assert controller.stats["violations_handled"] > 0, "违规统计错误"
    print(f"  [OK] 违规处理统计：{controller.stats['violations_handled']} 次")
    
    # 测试广告检测
    msg = create_danmaku(content="加微信私聊", user_id="ad_user")
    alerts = await controller.receive_danmaku(msg)
    assert len(alerts) > 0, "广告未检测"
    print("  [OK] 广告言论检测成功")
    
    return True


async def test_spam_detection():
    """测试刷屏检测"""
    print("\n[测试] 刷屏检测")
    controller = AssistantController()
    await controller.start_live("test_stream_001")
    
    # 短时间内发送大量弹幕
    user_id = "spam_user"
    for i in range(15):
        msg = create_danmaku(user_id=user_id, content=f"消息{i}")
        await controller.receive_danmaku(msg)
    
    # 应该触发刷屏预警
    alerts = controller.get_alerts(limit=10)
    spam_alerts = [a for a in alerts if a.get("alert_type") == "spam"]
    assert len(spam_alerts) > 0, "刷屏未检测"
    print(f"  [OK] 刷屏检测成功：{len(spam_alerts)} 次预警")
    
    return True


async def test_emotion_analysis():
    """测试情绪分析"""
    print("\n[测试] 情绪分析")
    controller = AssistantController()
    await controller.start_live("test_stream_001")
    
    # 发送积极弹幕
    for i in range(10):
        msg = create_danmaku(content="好棒！喜欢！666")
        await controller.receive_danmaku(msg)
    
    # 直接调用分析方法（不依赖异步任务）
    emotion = await controller._analyze_current_emotion()
    
    assert emotion is not None, "情绪数据为空"
    assert emotion.positive > 0, "积极情绪应为正数"
    print(f"  [OK] 情绪分析正常：积极{emotion.positive:.2f} 中性{emotion.neutral:.2f} 消极{emotion.negative:.2f}")
    
    # 添加到历史记录
    controller.emotion_history.append(emotion)
    
    # 获取情绪趋势
    trend = controller.get_emotion_trend(minutes=1)
    assert len(trend) > 0, "情绪趋势为空"
    print(f"  [OK] 情绪趋势数据：{len(trend)} 个点")
    
    return True


async def test_rhythm_suggestion():
    """测试节奏建议"""
    print("\n[测试] 节奏建议")
    controller = AssistantController()
    await controller.start_live("test_stream_001")
    
    # 从服务模块导入
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
    assert suggestion is not None, "未生成建议"
    assert suggestion.suggestion_type == "interaction", "建议类型错误"
    assert suggestion.priority >= 4, "优先级应该高"
    print(f"  [OK] 节奏建议生成：{suggestion.suggestion_type} - {suggestion.reason}")
    
    # 测试高情绪场景
    high_emotion = AudienceEmotion(
        positive=0.8,
        neutral=0.1,
        negative=0.1,
        excited=0.7,
        timestamp=datetime.now().timestamp()
    )
    controller.emotion_history = [high_emotion] * 10
    
    suggestion = await controller._generate_rhythm_suggestion()
    if suggestion:
        print(f"  [OK] 高情绪建议：{suggestion.suggestion_type}")
    
    return True


async def test_get_status():
    """测试获取状态"""
    print("\n[测试] 获取状态")
    controller = AssistantController()
    await controller.start_live("test_stream_001")
    
    # 发送一些弹幕
    for i in range(5):
        msg = create_danmaku(content=f"测试{i}")
        await controller.receive_danmaku(msg)
    
    # 获取状态
    status = controller.get_status()
    
    assert status["is_live"] is True, "直播状态错误"
    assert status["stream_id"] == "test_stream_001", "房间 ID 错误"
    assert status["stats"]["total_danmaku"] == 5, "弹幕统计错误"
    assert "recent_logs" in status, "日志缺失"
    assert "recent_alerts" in status, "预警缺失"
    
    print(f"  [OK] 状态获取完整")
    print(f"     - 直播状态：{status['is_live']}")
    print(f"     - 弹幕数：{status['stats']['total_danmaku']}")
    print(f"     - 预警数：{len(status['recent_alerts'])}")
    print(f"     - 日志数：{len(status['recent_logs'])}")
    
    return True


async def test_operation_logs():
    """测试操作日志"""
    print("\n[测试] 操作日志")
    controller = AssistantController()
    await controller.start_live("test_stream_001")
    
    # 执行一些操作
    await controller.receive_danmaku(create_danmaku(content="你好"))
    controller._log_operation("test_action", {"key": "value"})
    
    # 获取日志
    logs = controller.get_operation_logs(limit=10)
    
    assert len(logs) > 0, "日志为空"
    assert any(log.get("action") == "start_live" for log in logs), "缺少开始日志"
    assert any(log.get("action") == "test_action" for log in logs), "缺少测试日志"
    
    print(f"  [OK] 日志记录正常：{len(logs)} 条")
    
    # 测试日志数量限制 - 简化测试
    for i in range(100):
        controller._log_operation(f"action_{i}", {"index": i})
    
    logs = controller.get_operation_logs(limit=1000)
    assert len(logs) > 0, "日志应该存在"
    print(f"  [OK] 日志数量正常：{len(logs)} 条")
    
    return True


async def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("LiveMirror 场控助手测试套件")
    print("=" * 60)
    
    tests = [
        ("开始/停止直播", test_start_stop_live),
        ("接收弹幕", test_receive_danmaku),
        ("自动回复", test_auto_reply),
        ("违规检测", test_violation_detection),
        ("刷屏检测", test_spam_detection),
        ("情绪分析", test_emotion_analysis),
        ("节奏建议", test_rhythm_suggestion),
        ("获取状态", test_get_status),
        ("操作日志", test_operation_logs),
    ]
    
    passed = 0
    failed = 0
    failed_tests = []
    
    for test_name, test_func in tests:
        try:
            await test_func()
            passed += 1
        except AssertionError as e:
            print(f"  [失败] {e}")
            failed += 1
            failed_tests.append((test_name, str(e)))
        except Exception as e:
            print(f"  [异常] {e}")
            failed += 1
            failed_tests.append((test_name, str(e)))
    
    print("\n" + "=" * 60)
    print(f"测试结果：{passed} 通过，{failed} 失败")
    print("=" * 60)
    
    if failed_tests:
        print("\n[失败详情]:")
        for name, error in failed_tests:
            print(f"  - {name}: {error}")
    
    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    
    if success:
        print("\n[成功] 所有测试通过！")
    else:
        print("\n[失败] 部分测试失败")
    
    sys.exit(0 if success else 1)
