"""
LiveMirror 场控助手演示数据生成
生成样本数据展示场控功能
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from services.assistant_controller import (
    AssistantController,
    DanmakuMessage,
)


async def generate_demo_data():
    """生成演示数据"""
    print("=" * 60)
    print("LiveMirror 场控助手 - 演示数据生成")
    print("=" * 60)
    
    controller = AssistantController()
    
    # 开始直播
    await controller.start_live("demo_stream_20260409")
    print("\n[直播开始] demo_stream_20260409")
    
    # 模拟观众弹幕
    demo_users = [
        ("user_001", "小明"),
        ("user_002", "小红"),
        ("user_003", "小黑"),
        ("user_004", "小白"),
        ("user_005", "小蓝"),
        ("user_006", "小绿"),
        ("user_007", "小紫"),
        ("user_008", "小橙"),
    ]
    
    demo_messages = [
        # 正常弹幕
        ("直播开始了！", "normal"),
        ("主播好！", "normal"),
        ("今天卖什么？", "normal"),
        ("好期待！", "normal"),
        ("666", "normal"),
        ("哈哈哈", "normal"),
        
        # 常见问题（触发自动回复）
        ("直播什么时候结束", "faq"),
        ("有优惠吗", "faq"),
        ("怎么购买", "faq"),
        ("发什么快递", "faq"),
        ("有现货吗", "faq"),
        ("质量怎么样", "faq"),
        
        # 积极情绪
        ("好棒！", "positive"),
        ("喜欢！", "positive"),
        ("太棒了！！！", "positive"),
        ("买买买！", "positive"),
        ("已下单", "positive"),
        
        # 违规言论（触发处理）
        ("傻逼东西", "violation"),
        ("垃圾产品", "violation"),
        ("加微信私聊", "violation"),
        ("兼职刷单", "violation"),
    ]
    
    print("\n[模拟弹幕]")
    
    # 发送弹幕
    for i, (content, msg_type) in enumerate(demo_messages):
        user_id, username = demo_users[i % len(demo_users)]
        
        msg = DanmakuMessage(
            user_id=user_id,
            username=username,
            content=content,
            timestamp=datetime.now().timestamp(),
            user_level=5 if msg_type == "positive" else 1,
            is_fan=msg_type == "positive",
            is_moderator=False
        )
        
        alerts = await controller.receive_danmaku(msg)
        
        status = "正常"
        if alerts:
            status = f"预警：{alerts[0].alert_type}"
        
        print(f"  {username}: {content} [{status}]")
        
        # 模拟时间间隔
        await asyncio.sleep(0.1)
    
    # 模拟刷屏
    print("\n[模拟刷屏]")
    spam_user = ("spam_user", "刷屏王")
    for i in range(15):
        msg = DanmakuMessage(
            user_id=spam_user[0],
            username=spam_user[1],
            content=f"消息{i}",
            timestamp=datetime.now().timestamp(),
        )
        alerts = await controller.receive_danmaku(msg)
        if alerts:
            print(f"  {spam_user[1]}: 触发刷屏预警")
            break
    
    # 等待情绪分析
    print("\n[情绪分析]")
    await asyncio.sleep(1)
    
    # 直接分析情绪
    emotion = await controller._analyze_current_emotion()
    controller.emotion_history.append(emotion)
    print(f"  积极：{emotion.positive:.2f}")
    print(f"  中性：{emotion.neutral:.2f}")
    print(f"  消极：{emotion.negative:.2f}")
    print(f"  兴奋：{emotion.excited:.2f}")
    
    # 生成节奏建议
    print("\n[节奏建议]")
    suggestion = await controller._generate_rhythm_suggestion()
    if suggestion:
        print(f"  类型：{suggestion.suggestion_type}")
        print(f"  优先级：{suggestion.priority}")
        print(f"  原因：{suggestion.reason}")
        print(f"  建议：{suggestion.content}")
    else:
        print("  暂无建议")
    
    # 获取完整状态
    print("\n[完整状态]")
    status = controller.get_status()
    
    print(f"  直播状态：{'直播中' if status['is_live'] else '未直播'}")
    print(f"  弹幕总数：{status['stats']['total_danmaku']}")
    print(f"  自动回复：{status['stats']['auto_replies']} 次")
    print(f"  违规处理：{status['stats']['violations_handled']} 次")
    print(f"  预警触发：{status['stats']['alerts_triggered']} 次")
    
    # 获取操作日志
    print("\n[操作日志样本]")
    logs = controller.get_operation_logs(limit=5)
    for log in logs:
        print(f"  {log['action']}: {log.get('details', {})}")
    
    # 获取预警记录
    print("\n[预警记录样本]")
    alerts = controller.get_alerts(limit=5)
    for alert in alerts:
        level = alert.get('level', 'unknown')
        if hasattr(level, 'value'):
            level = level.value
        print(f"  [{level}] {alert['alert_type']}: {alert['message']}")
    
    # 保存为 JSON
    demo_data = {
        "stream_info": {
            "stream_id": controller.current_stream_id,
            "started_at": datetime.now().isoformat(),
        },
        "statistics": status["stats"],
        "emotion": {
            "positive": emotion.positive,
            "neutral": emotion.neutral,
            "negative": emotion.negative,
            "excited": emotion.excited,
        },
        "suggestions": [suggestion] if suggestion else [],
        "recent_logs": logs,
        "recent_alerts": [
            {
                "level": a.get("level").value if hasattr(a.get("level"), "value") else str(a.get("level")),
                "message": a.get("message"),
                "type": a.get("alert_type"),
                "timestamp": a.get("timestamp"),
            }
            for a in alerts
        ],
        "sample_danmaku": [
            {
                "user": "小明",
                "content": "直播什么时候结束",
                "auto_reply": "直播预计持续到晚上 10 点哦～"
            },
            {
                "user": "小黑",
                "content": "傻逼东西",
                "action": "禁言"
            },
            {
                "user": "刷屏王",
                "content": "消息 0-14",
                "action": "刷屏警告"
            }
        ]
    }
    
    output_file = Path(__file__).parent / "demo_data.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(demo_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n[数据已保存] {output_file}")
    
    # 停止直播
    await controller.stop_live()
    print("\n[直播结束]")
    
    print("\n" + "=" * 60)
    print("演示数据生成完成！")
    print("=" * 60)
    
    return demo_data


if __name__ == "__main__":
    demo_data = asyncio.run(generate_demo_data())
    
    # 打印 JSON
    print("\n演示数据预览:")
    print(json.dumps(demo_data, ensure_ascii=False, indent=2))
