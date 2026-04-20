"""
LiveMirror 实时分析快速测试
"""

import sys
import time
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from services.realtime_analysis import get_analysis_service

print("="*60)
print("LiveMirror 实时分析快速测试")
print("="*60)

# 获取服务
service = get_analysis_service()
session_id = "quick_test_session"

# 测试文本
test_texts = [
    "大家好，欢迎来到直播间！",
    "今天给大家带来超值福利。",
    "这个产品非常好用，价格也很优惠。",
    "限时限量，赶紧下单不要错过！"
]

print(f"\n测试 {len(test_texts)} 个片段...\n")

latencies = []
for i, text in enumerate(test_texts, 1):
    start = time.time()
    result = service.analyze_segment(session_id, text, audio_duration_ms=2000)
    latency = (time.time() - start) * 1000
    latencies.append(latency)
    
    print(f"片段 {i}:")
    print(f"  文本：{text}")
    print(f"  情绪：{result.sentiment} ({result.sentiment_score})")
    print(f"  延迟：{latency:.2f}ms")
    if result.suggestions:
        print(f"  建议：{result.suggestions[0]}")
    if result.risks:
        print(f"  风险：{result.risks[0]}")
    print()

# 统计
avg_latency = sum(latencies) / len(latencies)
max_latency = max(latencies)
min_latency = min(latencies)

print("="*60)
print("性能统计")
print("="*60)
print(f"平均延迟：{avg_latency:.2f}ms")
print(f"最大延迟：{max_latency:.2f}ms")
print(f"最小延迟：{min_latency:.2f}ms")
print(f"延迟要求：<3000ms")
print()

if max_latency < 3000:
    print("✅ 所有测试通过！延迟满足要求。")
else:
    print("❌ 部分测试延迟超出要求。")

# 服务统计
stats = service.get_performance_stats()
print(f"\n服务统计:")
print(f"  总分析数：{stats['total_analyses']}")
print(f"  平均延迟：{stats['avg_latency_ms']}ms")
print(f"  活跃会话：{stats['active_sessions']}")

print("\n" + "="*60)
print("测试完成！")
print("="*60)
