"""
LiveMirror AI 分析模块 - 测试用例

测试模拟转写稿到分析报告的完整流程
"""

import json
import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_analysis.analyzer import LiveMirrorAnalyzer, create_analyzer
from ai_analysis.classifiers import KeywordClassifier, create_rule_analyzer
from ai_analysis.suggester import create_suggester
from ai_analysis.report_generator import create_report_generator


# 测试用转写稿（模拟直播带货场景）
TEST_TRANSCRIPT = """
00:00:00 哈喽大家好，欢迎来到小美的直播间！今天是我们的美妆专场，给宝宝们带来超多福利！
00:00:30 先给大家介绍一下今天的主打产品，这款精华液我自己已经用了三个月了，效果真的超级明显。
00:01:00 原价是 399 元，但是今天在直播间，只要 199！直接对半砍！
00:01:30 想要的宝宝赶紧扣 1 让我看到你们的热情！点赞到 1 万我们再加赠 100 单！
00:02:00 这款精华液是全网销量第一的，绝对有效，保证你用了之后皮肤水水嫩嫩的。
00:02:30 我跟你们说，别家那些都是假货，只有我们这里是官方授权，正品保证。
00:03:00 有些宝宝问敏感肌能不能用，我跟你说，100% 没问题，我闺蜜敏感肌用了都说好。
00:03:30 库存真的不多了，后台显示只剩 80 单了，卖完真的要等下个月补货。
00:04:00 来，我们倒计时 5 分钟，5 分钟后恢复原价，到时候别怪我没提醒你们哦。
00:04:30 哎呀这个价格我真的亏死了，但是为了冲销量，拼了！
00:05:00 有宝宝说之前买贵了，那个我也没办法，今天是特殊活动价。
00:05:30 好了，最后一波，3、2、1，上链接！
00:06:00 哇已经拍了 50 单了，宝宝们太给力了！还没拍的抓紧了！
00:06:30 这个产品我真的强烈推荐，不用你绝对会后悔的。
00:07:00 好了宝宝们，我们来看下一款产品...
"""

# 模拟数据变化点
TEST_DATA_CHANGES = [
    {
        "timestamp": "00:01:30",
        "type": "涨粉",
        "value": "+150",
        "description": "互动引导后粉丝增长"
    },
    {
        "timestamp": "00:03:30",
        "type": "爆单",
        "value": "+80",
        "description": "稀缺性营造后订单激增"
    },
    {
        "timestamp": "00:05:30",
        "type": "爆单",
        "value": "+200",
        "description": "倒计时促单后订单峰值"
    }
]


def test_keyword_classifier():
    """测试关键词分类器"""
    print("=" * 60)
    print("测试 1: 关键词分类器")
    print("=" * 60)
    
    classifier = KeywordClassifier()
    
    test_cases = [
        ("赶紧下单，手慢无！", ["促单话术", "稀缺性营造"]),
        ("原价 399，今天只要 199", ["价格锚点"]),
        ("我自己也在用，销量第一", ["信任背书"]),
        ("最便宜的产品，绝对有效", ["敏感词", "过度承诺"]),
        ("别家都是假货", ["贬低竞品"]),
    ]
    
    for text, expected_types in test_cases:
        result = classifier.classify_speech_type(text)
        crashes = classifier.detect_crashes(text)
        
        print(f"\n文本：{text}")
        print(f"话术类型：{[t.value for t in result]}")
        print(f"翻车类型：{[c.value for c in crashes]}")
        
        # 简单验证
        if expected_types:
            detected = [t.value for t in result] + [c.value for c in crashes]
            matches = any(exp in detected for exp in expected_types)
            print(f"[OK] 匹配预期：{matches}")
    
    print("\n[OK] 关键词分类器测试完成\n")


def test_rule_analyzer():
    """测试规则分析器"""
    print("=" * 60)
    print("测试 2: 规则分析器")
    print("=" * 60)
    
    analyzer = create_rule_analyzer()
    
    test_segments = [
        {"segment_id": 1, "content": "大家好，欢迎来到直播间", "start_time": "00:00:00"},
        {"segment_id": 2, "content": "赶紧下单，只剩最后 10 单", "start_time": "00:01:00"},
        {"segment_id": 3, "content": "全网第一，绝对有效", "start_time": "00:02:00"},
    ]
    
    priorities = analyzer.pre_filter_segments(test_segments)
    
    print(f"高优先级段落：{len(priorities['high_priority'])}")
    print(f"中优先级段落：{len(priorities['medium_priority'])}")
    print(f"低优先级段落：{len(priorities['low_priority'])}")
    
    # 测试快速分类
    result = analyzer.quick_classify("赶紧下单，全网第一，绝对有效")
    print(f"\n快速分类结果：{json.dumps(result, ensure_ascii=False, indent=2)}")
    
    print("\n[OK] 规则分析器测试完成\n")


def test_suggester():
    """测试优化建议生成器"""
    print("=" * 60)
    print("测试 3: 优化建议生成器")
    print("=" * 60)
    
    suggester = create_suggester()
    
    test_crashes = [
        {
            "segment_id": 3,
            "timestamp": "00:02:00",
            "type": "敏感词",
            "original_text": "全网第一，绝对有效",
            "severity": "high",
            "risk_level": 8
        },
        {
            "segment_id": 5,
            "timestamp": "00:04:00",
            "type": "过度承诺",
            "original_text": "不用你绝对会后悔的",
            "severity": "medium",
            "risk_level": 6
        }
    ]
    
    suggestions = suggester.generate_batch_suggestions(test_crashes)
    
    for suggestion in suggestions:
        print(f"\n段落 {suggestion.segment_id}:")
        print(f"原文：{suggestion.original_text}")
        print(f"问题类型：{suggestion.problem_type}")
        print("改写建议：")
        for version in suggestion.suggestions:
            print(f"  版本{version.version}: {version.rewritten_text}")
            print(f"    改进：{version.improvement}")
    
    print("\n[OK] 优化建议生成器测试完成\n")


def test_report_generator():
    """测试报告生成器"""
    print("=" * 60)
    print("测试 4: 报告生成器")
    print("=" * 60)
    
    generator = create_report_generator()
    
    # 模拟数据
    segments = [
        {
            "segment_id": 1,
            "start_time": "00:00:00",
            "end_time": "00:00:45",
            "content": "大家好，欢迎来到直播间",
            "word_count": 50,
            "speech_type": "闲聊",
            "is_highlight": False,
            "is_crash": False
        }
    ]
    
    highlights = [
        {
            "segment_id": 2,
            "timestamp": "00:01:00",
            "type": "促单话术",
            "original_text": "赶紧下单",
            "effectiveness_score": 8,
            "analysis": "紧迫感营造到位"
        }
    ]
    
    crashes = [
        {
            "segment_id": 3,
            "timestamp": "00:02:00",
            "type": "敏感词",
            "severity": "high",
            "original_text": "全网第一",
            "problem": "使用广告法禁用词",
            "risk_level": 8
        }
    ]
    
    report = generator.generate_report(
        segments=segments,
        highlights=highlights,
        crashes=crashes
    )
    
    print("报告摘要：")
    print(f"  总分：{report['summary']['overall_score']}/100")
    print(f"  爆点：{report['summary']['total_highlights']}")
    print(f"  翻车：{report['summary']['total_crashes']}")
    print(f"  关键洞察：{report['summary']['key_insights']}")
    
    # 测试执行摘要
    summary_text = generator.generate_executive_summary(report)
    print("\n执行摘要：")
    print(summary_text)
    
    print("\n[OK] 报告生成器测试完成\n")


def test_full_analysis():
    """测试完整分析流程（无 API 降级模式）"""
    print("=" * 60)
    print("测试 5: 完整分析流程（规则分析降级模式）")
    print("=" * 60)
    
    # 不配置 API Key，使用规则分析降级
    analyzer = create_analyzer(
        api_key=None,  # 无 API Key
        model="deepseek-chat",
        cost_optimization=True
    )
    
    report = analyzer.analyze(
        transcript=TEST_TRANSCRIPT,
        data_changes=TEST_DATA_CHANGES
    )
    
    print("\n完整分析报告：")
    print(f"  分析时间：{report['metadata']['analysis_time']}")
    print(f"  总分段数：{report['metadata']['total_segments']}")
    print(f"  综合得分：{report['summary']['overall_score']}/100")
    print(f"  爆点数量：{report['summary']['total_highlights']}")
    print(f"  翻车数量：{report['summary']['total_crashes']}")
    print(f"  严重翻车：{report['summary']['critical_crashes']}")
    
    print("\n关键洞察：")
    for i, insight in enumerate(report['summary']['key_insights'], 1):
        print(f"  {i}. {insight}")
    
    if report.get('highlights'):
        print("\n爆点示例：")
        for h in report['highlights'][:3]:
            print(f"  - [{h['timestamp']}] {h['type']}: {h['original_text'][:50]}...")
    
    if report.get('crashes'):
        print("\n翻车点示例：")
        for c in report['crashes'][:3]:
            print(f"  - [{c['timestamp']}] {c['type']} ({c['severity']}): {c['original_text'][:50]}...")
    
    if report.get('suggestions'):
        print("\n优化建议示例：")
        for s in report['suggestions'][:2]:
            print(f"  段落{s['segment_id']}: {s['problem_type']}")
            print(f"    原文：{s['original_text'][:50]}...")
            print(f"    建议 A: {s['suggestions'][0]['rewritten_text']}")
    
    # 保存报告
    output_path = Path(__file__).parent / "test_report.json"
    analyzer.save_report(report, str(output_path))
    print(f"\n[INFO] 报告已保存至：{output_path}")
    
    print("\n[OK] 完整分析流程测试完成\n")


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("LiveMirror AI 分析模块 - 测试套件")
    print("=" * 60 + "\n")
    
    try:
        test_keyword_classifier()
        test_rule_analyzer()
        test_suggester()
        test_report_generator()
        test_full_analysis()
        
        print("\n" + "=" * 60)
        print("所有测试通过！")
        print("=" * 60 + "\n")
        
        return True
        
    except Exception as e:
        print(f"\n[FAIL] 测试失败：{e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
