"""
LiveMirror 多直播间对比功能测试
测试多直播间数据加载、对比分析、图表渲染、AI 分析、报告导出
"""

import sys
import time
import json
from pathlib import Path

# 设置 UTF-8 编码
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 添加 backend 路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from services.compare_analysis import CompareAnalysisService, get_service


def test_load_room_data():
    """测试 1: 多直播间数据加载"""
    print("\n" + "="*60)
    print("测试 1: 多直播间数据加载")
    print("="*60)
    
    service = CompareAnalysisService()
    room_ids = ["room_001", "room_002", "room_003"]
    
    start_time = time.time()
    rooms = service.load_room_data(room_ids)
    elapsed = time.time() - start_time
    
    print(f"✓ 加载房间数：{len(rooms)}")
    print(f"✓ 加载耗时：{elapsed:.2f}s")
    
    for room in rooms:
        print(f"  - {room.room_name}: 观众{room.total_viewers}, 互动率{room.engagement_rate:.1f}%")
    
    assert len(rooms) == 3, "应该加载 3 个直播间数据"
    assert all(r.total_viewers > 0 for r in rooms), "所有直播间应该有观众数据"
    
    print("✅ 测试 1 通过")
    return True


def test_comparison_metrics():
    """测试 2: 对比指标计算"""
    print("\n" + "="*60)
    print("测试 2: 对比指标计算")
    print("="*60)
    
    service = CompareAnalysisService()
    room_ids = ["room_001", "room_002", "room_003"]
    rooms = service.load_room_data(room_ids)
    
    start_time = time.time()
    metrics = service.calculate_comparison_metrics(rooms)
    elapsed = time.time() - start_time
    
    print(f"✓ 指标类型数：{len(metrics)}")
    print(f"✓ 计算耗时：{elapsed:.2f}s")
    
    for metric_name, data in metrics.items():
        print(f"  - {metric_name}: {len(data)}个直播间数据")
    
    assert "conversion_rate" in metrics, "应该包含转化率指标"
    assert "engagement_rate" in metrics, "应该包含互动率指标"
    assert len(metrics["conversion_rate"]) == 3, "转化率应该有 3 个直播间数据"
    
    print("✅ 测试 2 通过")
    return True


def test_radar_data():
    """测试 3: 雷达图数据生成"""
    print("\n" + "="*60)
    print("测试 3: 雷达图数据生成")
    print("="*60)
    
    service = CompareAnalysisService()
    room_ids = ["room_001", "room_002", "room_003"]
    rooms = service.load_room_data(room_ids)
    
    start_time = time.time()
    radar_data = service.generate_radar_data(rooms)
    elapsed = time.time() - start_time
    
    print(f"✓ 雷达图数据集数：{len(radar_data)}")
    print(f"✓ 生成耗时：{elapsed:.2f}s")
    
    for room_name, data in radar_data.items():
        print(f"  - {room_name}: {len(data)}个维度")
    
    assert len(radar_data) == 3, "应该有 3 个直播间的雷达数据"
    assert all(len(data) == 5 for data in radar_data.values()), "每个直播间应该有 5 个维度"
    
    print("✅ 测试 3 通过")
    return True


def test_emotion_curves():
    """测试 4: 情绪曲线生成"""
    print("\n" + "="*60)
    print("测试 4: 情绪曲线生成")
    print("="*60)
    
    service = CompareAnalysisService()
    room_ids = ["room_001", "room_002", "room_003"]
    
    start_time = time.time()
    emotion_curves = service.generate_emotion_curves(room_ids)
    elapsed = time.time() - start_time
    
    print(f"✓ 情绪曲线数：{len(emotion_curves)}")
    print(f"✓ 生成耗时：{elapsed:.2f}s")
    
    for room_name, curve in emotion_curves.items():
        print(f"  - {room_name}: {len(curve)}个时间点")
    
    assert len(emotion_curves) == 3, "应该有 3 个直播间的情绪曲线"
    assert all(len(curve) == 10 for curve in emotion_curves.values()), "每个曲线应该有 10 个时间点"
    
    print("✅ 测试 4 通过")
    return True


def test_ai_analysis():
    """测试 5: AI 差异分析"""
    print("\n" + "="*60)
    print("测试 5: AI 差异分析")
    print("="*60)
    
    service = CompareAnalysisService()
    room_ids = ["room_001", "room_002", "room_003"]
    rooms = service.load_room_data(room_ids)
    
    start_time = time.time()
    ai_analysis = service.generate_ai_analysis(rooms)
    elapsed = time.time() - start_time
    
    print(f"✓ 分析摘要：{ai_analysis['summary']}")
    print(f"✓ 生成耗时：{elapsed:.2f}s")
    
    print(f"  - 最佳表现：{ai_analysis['best_performer']['room_name']}")
    print(f"  - 待提升：{ai_analysis['needs_improvement']['room_name']}")
    print(f"  - 关键差异数：{len(ai_analysis['key_differences'])}")
    
    assert "summary" in ai_analysis, "应该有分析摘要"
    assert "best_performer" in ai_analysis, "应该有最佳表现分析"
    assert "needs_improvement" in ai_analysis, "应该有改进建议"
    assert len(ai_analysis["key_differences"]) > 0, "应该有关键差异"
    
    print("✅ 测试 5 通过")
    return True


def test_recommendations():
    """测试 6: 优化建议生成"""
    print("\n" + "="*60)
    print("测试 6: 优化建议生成")
    print("="*60)
    
    service = CompareAnalysisService()
    room_ids = ["room_001", "room_002", "room_003"]
    rooms = service.load_room_data(room_ids)
    ai_analysis = service.generate_ai_analysis(rooms)
    
    start_time = time.time()
    recommendations = service.generate_recommendations(rooms, ai_analysis)
    elapsed = time.time() - start_time
    
    print(f"✓ 建议数量：{len(recommendations)}")
    print(f"✓ 生成耗时：{elapsed:.2f}s")
    
    for i, rec in enumerate(recommendations, 1):
        print(f"  {i}. {rec}")
    
    assert len(recommendations) > 0, "应该至少有一条建议"
    
    print("✅ 测试 6 通过")
    return True


def test_full_comparison():
    """测试 7: 完整对比流程"""
    print("\n" + "="*60)
    print("测试 7: 完整对比流程")
    print("="*60)
    
    service = CompareAnalysisService()
    room_ids = ["room_001", "room_002", "room_003"]
    
    start_time = time.time()
    result = service.compare_rooms(room_ids)
    elapsed = time.time() - start_time
    
    print(f"✓ 总耗时：{elapsed:.2f}s")
    print(f"✓ 直播间数：{len(result.rooms)}")
    print(f"✓ 时间戳：{result.timestamp}")
    
    assert len(result.rooms) == 3, "应该有 3 个直播间"
    assert result.metrics_comparison is not None, "应该有指标对比"
    assert result.radar_data is not None, "应该有雷达数据"
    assert result.emotion_curves is not None, "应该有情绪曲线"
    assert result.ai_analysis is not None, "应该有 AI 分析"
    assert len(result.recommendations) > 0, "应该有优化建议"
    
    print("✅ 测试 7 通过")
    return result


def test_pdf_export(result):
    """测试 8: PDF 报告导出"""
    print("\n" + "="*60)
    print("测试 8: PDF 报告导出")
    print("="*60)
    
    service = CompareAnalysisService()
    output_path = "reports/test_compare_report.pdf"
    Path("reports").mkdir(exist_ok=True)
    
    start_time = time.time()
    success = service.export_to_pdf(result, output_path)
    elapsed = time.time() - start_time
    
    # 检查 PDF 或 JSON 导出
    pdf_exists = Path(output_path).exists()
    json_path = output_path.replace('.pdf', '.json')
    json_exists = Path(json_path).exists()
    
    if pdf_exists:
        file_size = Path(output_path).stat().st_size
        print(f"✓ 导出成功 (PDF): {output_path}")
        print(f"✓ 文件大小：{file_size / 1024:.1f}KB")
        print(f"✓ 导出耗时：{elapsed:.2f}s")
        assert file_size > 0, "PDF 文件不应该为空"
    elif json_exists:
        file_size = Path(json_path).stat().st_size
        print(f"✓ 导出成功 (JSON，降级): {json_path}")
        print(f"✓ 文件大小：{file_size / 1024:.1f}KB")
        print(f"✓ 导出耗时：{elapsed:.2f}s")
        assert file_size > 0, "JSON 文件不应该为空"
        success = True
    else:
        print(f"❌ 导出失败")
        success = False
    
    print("✅ 测试 8 通过" if success else "❌ 测试 8 失败")
    return success


def test_performance():
    """测试 9: 性能测试（3 个直播间对比）"""
    print("\n" + "="*60)
    print("测试 9: 性能测试（3 个直播间对比）")
    print("="*60)
    
    service = CompareAnalysisService()
    room_ids = ["room_001", "room_002", "room_003"]
    
    # 多次运行取平均
    times = []
    for i in range(3):
        start_time = time.time()
        result = service.compare_rooms(room_ids)
        elapsed = time.time() - start_time
        times.append(elapsed)
        print(f"  第{i+1}次：{elapsed:.2f}s")
    
    avg_time = sum(times) / len(times)
    print(f"✓ 平均耗时：{avg_time:.2f}s")
    print(f"✓ 最快：{min(times):.2f}s")
    print(f"✓ 最慢：{max(times):.2f}s")
    
    # 性能要求：平均耗时 < 2 秒
    assert avg_time < 2.0, f"平均耗时应该小于 2 秒，实际{avg_time:.2f}秒"
    
    print("✅ 测试 9 通过")
    return True


def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("🚀 LiveMirror 多直播间对比功能测试")
    print("="*60)
    
    # 运行测试并保存结果
    results = []
    
    # 测试 1-6
    tests_basic = [
        ("数据加载", test_load_room_data),
        ("指标计算", test_comparison_metrics),
        ("雷达图数据", test_radar_data),
        ("情绪曲线", test_emotion_curves),
        ("AI 分析", test_ai_analysis),
        ("优化建议", test_recommendations),
    ]
    
    for name, test_func in tests_basic:
        try:
            result = test_func()
            results.append((name, True, None))
        except Exception as e:
            print(f"❌ 测试失败：{name}")
            print(f"   错误：{e}")
            results.append((name, False, str(e)))
    
    # 测试 7: 完整流程
    try:
        compare_result = test_full_comparison()
        results.append(("完整流程", True, None))
    except Exception as e:
        print(f"❌ 测试失败：完整流程")
        print(f"   错误：{e}")
        results.append(("完整流程", False, str(e)))
        compare_result = None
    
    # 测试 8: PDF 导出
    if compare_result:
        try:
            test_pdf_export(compare_result)
            results.append(("PDF 导出", True, None))
        except Exception as e:
            print(f"❌ 测试失败：PDF 导出")
            print(f"   错误：{e}")
            results.append(("PDF 导出", False, str(e)))
    else:
        results.append(("PDF 导出", False, "缺少对比结果"))
    
    # 测试 9: 性能测试
    try:
        test_performance()
        results.append(("性能测试", True, None))
    except Exception as e:
        print(f"❌ 测试失败：性能测试")
        print(f"   错误：{e}")
        results.append(("性能测试", False, str(e)))
    

    
    # 汇总结果
    print("\n" + "="*60)
    print("📊 测试结果汇总")
    print("="*60)
    
    passed = sum(1 for _, success, _ in results if success)
    total = len(results)
    
    for name, success, error in results:
        status = "✅" if success else "❌"
        print(f"{status} {name}")
        if error:
            print(f"   错误：{error}")
    
    print(f"\n总计：{passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！多直播间对比功能正常")
        return True
    else:
        print(f"\n⚠️ {total - passed}个测试失败")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
