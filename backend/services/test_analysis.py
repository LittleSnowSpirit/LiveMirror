"""
话术分析 Prompt 测试脚本
用于测试新 Prompt 的效果并对比分析结果
"""
import json
import sys
from pathlib import Path

# 修复 Windows 控制台编码
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.whisper import WhisperService, SPEECH_TYPES

# 测试用直播转录文本
TEST_TRANSCRIPT = """
哈喽大家好，欢迎来到小美的直播间！我是你们的主播小美，今天又和大家见面啦！
新进来的宝宝们点个关注不迷路，我们每天晚上 8 点准时开播哦！

今天给大家带来的是一款超级好用的补水保湿面霜，真的是我自用款！
这款是韩国进口的品牌，主要成分是玻尿酸和烟酰胺，深层补水的同时还能美白淡斑。
质地非常水润，一点都不油腻，油皮干皮都能用。

来，我给大家看一下质地，看，就是这样乳白色的，很水润。
抹在手背上给大家看，一抹就开了，吸收特别快，不粘腻。
闻一下味道，淡淡的清香，很好闻。

原价是 299 元一瓶，但是今天在我们直播间，只要 199 元！
而且今天下单还送价值 99 元的面膜一盒，5 片装的！
算下来相当于买一送一，超级划算！

只有 50 单库存哦，抢完就没有了。
来，倒计时 3 分钟，3 分钟后恢复原价！
想要的宝宝赶紧下单，不要犹豫！

有宝宝问敏感肌能用吗？
可以的，这款是温和配方，不含酒精和香精，敏感肌也完全适用。
而且我们有 7 天无理由退换，放心购买。

看一下这位买家的反馈，她用了两周，皮肤明显变白了，她自己都说效果太好了！
还有这位，说是用了一瓶，细纹都淡了很多，回购第三次了。

最后 10 单！真的最后 10 单了！
拍完下架，明天就没有这个价格了！
1、2、3，上链接！赶紧去拍！

下单的宝宝记得关注直播间，明天晚上 8 点我们还有更多福利！
明天会有一款新的精华液上架，也是超级优惠的价格！
谢谢大家，我们明天见！
"""


def run_test():
    """运行话术分析测试"""
    print("=" * 70)
    print("🧪 LiveMirror 话术分析 Prompt 测试")
    print("=" * 70)
    
    try:
        service = WhisperService()
    except ValueError as e:
        print(f"\n❌ 错误：{e}")
        print("\n请设置环境变量：")
        print("  Windows: set DASHSCOPE_API_KEY=your_api_key")
        print("  Linux/Mac: export DASHSCOPE_API_KEY=your_api_key")
        return None
    
    print("\n📝 测试文本长度:", len(TEST_TRANSCRIPT), "字符")
    print("\n📋 支持的话术类型:")
    for code, info in SPEECH_TYPES.items():
        print(f"   • {code}: {info['name']} - {info['description']}")
    
    print("\n" + "=" * 70)
    print("🚀 开始详细分析...")
    print("=" * 70)
    
    try:
        result = service.analyze_speech(TEST_TRANSCRIPT, detailed=True)
        
        print("\n✅ 分析成功！")
        print("\n📊 分析结果:")
        print(json.dumps(result, ensure_ascii=False, indent=2))
        
        print("\n" + "=" * 70)
        print("📄 人类可读报告:")
        print("=" * 70)
        report = service.generate_report(result)
        print(report)
        
        # 保存结果
        output_path = Path(__file__).parent / "test_result.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        print(f"\n💾 结果已保存到：{output_path}")
        
        return result
        
    except Exception as e:
        print(f"\n❌ 分析失败：{e}")
        import traceback
        traceback.print_exc()
        return None


def compare_prompts():
    """对比新旧 Prompt 的差异"""
    print("\n" + "=" * 70)
    print("📊 Prompt 优化对比")
    print("=" * 70)
    
    improvements = [
        {
            "方面": "话术类型覆盖",
            "优化前": "基础 3-5 种类型",
            "优化后": "10 种详细类型（开场白、产品介绍、价格优惠、限时限量、互动问答、使用演示、买家秀展示、促单成交、答疑、留人话术）",
            "提升": "覆盖更全面，识别更精准"
        },
        {
            "方面": "评分维度",
            "优化前": "单一评分或无评分",
            "优化后": "5 维评分（吸引力、清晰度、说服力、互动性、时机）+ 加权综合分",
            "提升": "多维度评估，更客观全面"
        },
        {
            "方面": "输出格式",
            "优化前": "自由文本或简单 JSON",
            "优化后": "结构化 JSON（包含分析摘要、分段详情、优化建议）",
            "提升": "便于程序处理和可视化展示"
        },
        {
            "方面": "分析深度",
            "优化前": "仅识别类型",
            "优化后": "类型识别 + 评分 + 亮点提取 + 改进建议 + 优先级排序",
            "提升": "从识别升级到诊断和优化"
        },
        {
            "方面": "模型选择",
            "优化前": "未指定或使用通用模型",
            "优化后": "通义千问 qwen-plus（中文理解能力强）",
            "提升": "更适合中文直播场景"
        }
    ]
    
    print("\n")
    for i, imp in enumerate(improvements, 1):
        print(f"{i}. {imp['方面']}")
        print(f"   优化前：{imp['优化前']}")
        print(f"   优化后：{imp['优化后']}")
        print(f"   提升：{imp['提升']}")
        print()
    
    print("=" * 70)


if __name__ == "__main__":
    # 运行对比分析
    compare_prompts()
    
    # 运行实际测试
    result = run_test()
    
    if result:
        print("\n" + "=" * 70)
        print("✅ 测试完成！")
        print("=" * 70)
    else:
        print("\n" + "=" * 70)
        print("⚠️ 测试未完成（可能缺少 API Key）")
        print("=" * 70)
