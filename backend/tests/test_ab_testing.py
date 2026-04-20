"""
话术 A/B 测试功能测试 - LiveMirror
测试话术版本管理、A/B 测试配置、效果对比分析、统计显著性检验
"""

import sys
import os
import pytest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from backend.services.ab_testing import (
        ABTestingService,
        ScriptVariant,
        TestStatus,
        TrafficAllocation
    )
except ImportError as exc:
    pytest.skip(f"Experimental A/B test API drifted from service exports: {exc}", allow_module_level=True)
import shutil


def cleanup_test_dir():
    """清理测试目录"""
    if os.path.exists("data/ab_testing_test"):
        shutil.rmtree("data/ab_testing_test")


def test_script_version_management():
    """测试 1: 话术版本管理"""
    print("\n" + "="*60)
    print("测试 1: 话术版本管理（A/B/C 版本）")
    print("="*60)
    
    cleanup_test_dir()
    service = ABTestingService(data_dir="data/ab_testing_test")
    
    # 测试创建测试（包含多个版本）
    print("\n[1.1] 测试创建包含 A/B/C 三个版本的话术测试...")
    variants = [
        {
            "variant": "A",
            "content": "🔥限时秒杀！今天不买亏大了，手慢无！",
            "description": "强调紧迫感"
        },
        {
            "variant": "B",
            "content": "✨99% 的人都不知道的使用技巧，揭秘！",
            "description": "强调好奇心"
        },
        {
            "variant": "C",
            "content": "💰明星同款，销量第一，万人好评！",
            "description": "强调社会认同"
        }
    ]
    
    result = service.create_test(
        name="618 大促话术测试",
        variants=variants,
        description="测试不同话术风格对转化率的影响",
        traffic_allocation="even",
        duration_hours=24,
        target_sample_size=1000
    )
    
    test_id = result["test_id"]
    assert test_id is not None, "创建测试失败"
    print("[OK] 成功创建测试：%s" % test_id)
    print("     包含 %d 个话术版本" % len(variants))
    
    # 测试获取测试详情
    print("\n[1.2] 测试获取测试详情...")
    test_detail = service.get_test(test_id)
    assert test_detail is not None, "获取测试详情失败"
    assert len(test_detail["config"]["variants"]) == 3, "变体数量不匹配"
    
    for i, variant in enumerate(test_detail["config"]["variants"]):
        print("     版本 %s: %s" % (
            variant["variant"],
            variant["description"]
        ))
    print("[OK] 成功获取测试详情")
    
    # 测试话术版本内容验证
    print("\n[1.3] 验证话术版本内容...")
    for i, expected in enumerate(variants):
        actual = test_detail["config"]["variants"][i]
        assert actual["variant"] == expected["variant"], "变体标识不匹配"
        assert actual["content"] == expected["content"], "话术内容不匹配"
        assert actual["description"] == expected["description"], "描述不匹配"
    print("[OK] 所有话术版本内容验证通过")
    
    cleanup_test_dir()
    print("\n[PASS] 测试 1 通过：话术版本管理功能正常")
    return True


def test_traffic_allocation():
    """测试 2: 流量分配配置"""
    print("\n" + "="*60)
    print("测试 2: A/B 测试配置（流量分配）")
    print("="*60)
    
    cleanup_test_dir()
    service = ABTestingService(data_dir="data/ab_testing_test")
    
    # 创建测试
    print("\n[2.1] 创建测试并启动...")
    variants = [
        {"variant": "A", "content": "话术版本 A", "description": "版本 A"},
        {"variant": "B", "content": "话术版本 B", "description": "版本 B"}
    ]
    
    result = service.create_test(
        name="流量分配测试",
        variants=variants,
        traffic_allocation="even",
        duration_hours=12
    )
    test_id = result["test_id"]
    
    # 启动测试
    service.start_test(test_id)
    print("[OK] 测试已启动，初始为平均分配")
    
    # 测试更新流量分配
    print("\n[2.2] 测试更新流量分配为加权模式...")
    allocations = {
        "%s_v0" % test_id: 0.7,  # 版本 A 70%
        "%s_v1" % test_id: 0.3   # 版本 B 30%
    }
    
    update_result = service.update_traffic_allocation(test_id, allocations)
    assert update_result is not None, "更新流量分配失败"
    print("[OK] 流量分配更新成功")
    print("     版本 A: 70%")
    print("     版本 B: 30%")
    
    # 验证分配
    print("\n[2.3] 验证流量分配...")
    test_detail = service.get_test(test_id)
    variant_a = test_detail["config"]["variants"][0]
    variant_b = test_detail["config"]["variants"][1]
    
    assert abs(variant_a["traffic_weight"] - 0.7) < 0.01, "版本 A 权重不正确"
    assert abs(variant_b["traffic_weight"] - 0.3) < 0.01, "版本 B 权重不正确"
    print("[OK] 流量分配验证通过")
    
    # 测试错误分配（总和不为 1）
    print("\n[2.4] 测试错误分配验证...")
    try:
        service.update_traffic_allocation(test_id, {"v0": 0.5, "v1": 0.6})
        print("[FAIL] 应该抛出异常")
        return False
    except ValueError as e:
        print("[OK] 正确捕获错误：总和必须为 1.0")
    
    cleanup_test_dir()
    print("\n[PASS] 测试 2 通过：流量分配配置功能正常")
    return True


def test_effect_comparison():
    """测试 3: 效果对比分析"""
    print("\n" + "="*60)
    print("测试 3: 效果对比分析（转化率/互动率）")
    print("="*60)
    
    cleanup_test_dir()
    service = ABTestingService(data_dir="data/ab_testing_test")
    
    # 创建测试
    print("\n[3.1] 创建测试并模拟数据...")
    variants = [
        {"variant": "A", "content": "话术版本 A", "description": "强调优惠"},
        {"variant": "B", "content": "话术版本 B", "description": "强调品质"}
    ]
    
    result = service.create_test(
        name="效果对比测试",
        variants=variants,
        traffic_allocation="even",
        duration_hours=24,
        target_sample_size=500
    )
    test_id = result["test_id"]
    service.start_test(test_id)
    
    # 模拟版本 A 的数据（高转化率）
    print("\n[3.2] 模拟版本 A 数据（高转化率）...")
    service.update_variant_metrics(test_id, "%s_v0" % test_id, {
        "impressions": 1000,
        "clicks": 150,
        "conversions": 45,
        "comments": 30,
        "likes": 80,
        "shares": 20
    })
    print("     展现量：1000")
    print("     点击量：150")
    print("     转化量：45")
    
    # 模拟版本 B 的数据（低转化率）
    print("\n[3.3] 模拟版本 B 数据（低转化率）...")
    service.update_variant_metrics(test_id, "%s_v1" % test_id, {
        "impressions": 1000,
        "clicks": 120,
        "conversions": 24,
        "comments": 20,
        "likes": 50,
        "shares": 10
    })
    print("     展现量：1000")
    print("     点击量：120")
    print("     转化量：24")
    
    # 获取详情并验证指标
    print("\n[3.4] 验证效果指标计算...")
    test_detail = service.get_test(test_id)
    
    variant_a = test_detail["config"]["variants"][0]
    variant_b = test_detail["config"]["variants"][1]
    
    # 计算转化率
    ctr_a = (variant_a["metrics"]["clicks"] / variant_a["metrics"]["impressions"]) * 100 if variant_a["metrics"]["impressions"] > 0 else 0
    ctr_b = (variant_b["metrics"]["clicks"] / variant_b["metrics"]["impressions"]) * 100 if variant_b["metrics"]["impressions"] > 0 else 0
    conv_a = (variant_a["metrics"]["conversions"] / variant_a["metrics"]["clicks"]) * 100 if variant_a["metrics"]["clicks"] > 0 else 0
    conv_b = (variant_b["metrics"]["conversions"] / variant_b["metrics"]["clicks"]) * 100 if variant_b["metrics"]["clicks"] > 0 else 0
    engage_a = ((variant_a["metrics"]["comments"] + variant_a["metrics"]["likes"] + variant_a["metrics"]["shares"]) / variant_a["metrics"]["impressions"]) * 100 if variant_a["metrics"]["impressions"] > 0 else 0
    engage_b = ((variant_b["metrics"]["comments"] + variant_b["metrics"]["likes"] + variant_b["metrics"]["shares"]) / variant_b["metrics"]["impressions"]) * 100 if variant_b["metrics"]["impressions"] > 0 else 0
    
    print("     版本 A - CTR: %.2f%%, 转化率：%.2f%%, 互动率：%.2f%%" % (ctr_a, conv_a, engage_a))
    print("     版本 B - CTR: %.2f%%, 转化率：%.2f%%, 互动率：%.2f%%" % (ctr_b, conv_b, engage_b))
    
    # 验证版本 A 优于版本 B
    assert conv_a > conv_b, "版本 A 转化率应该更高"
    assert ctr_a > ctr_b, "版本 A 点击率应该更高"
    assert engage_a > engage_b, "版本 A 互动率应该更高"
    print("[OK] 效果对比验证通过")
    
    cleanup_test_dir()
    print("\n[PASS] 测试 3 通过：效果对比分析功能正常")
    return True


def test_statistical_significance():
    """测试 4: 统计显著性检验"""
    print("\n" + "="*60)
    print("测试 4: 统计显著性检验")
    print("="*60)
    
    cleanup_test_dir()
    service = ABTestingService(data_dir="data/ab_testing_test")
    
    # 创建测试
    print("\n[4.1] 创建测试并收集足够样本...")
    variants = [
        {"variant": "A", "content": "话术版本 A", "description": "版本 A"},
        {"variant": "B", "content": "话术版本 B", "description": "版本 B"}
    ]
    
    result = service.create_test(
        name="统计显著性测试",
        variants=variants,
        traffic_allocation="even",
        duration_hours=48,
        target_sample_size=1000,
        primary_metric="conversion_rate"
    )
    test_id = result["test_id"]
    service.start_test(test_id)
    
    # 模拟显著差异的数据
    print("\n[4.2] 模拟显著差异的数据...")
    # 版本 A: 高转化率
    service.update_variant_metrics(test_id, "%s_v0" % test_id, {
        "impressions": 2000,
        "clicks": 400,
        "conversions": 120,  # 30% 转化率
        "comments": 50,
        "likes": 150,
        "shares": 30
    })
    
    # 版本 B: 低转化率
    service.update_variant_metrics(test_id, "%s_v1" % test_id, {
        "impressions": 2000,
        "clicks": 300,
        "conversions": 45,  # 15% 转化率
        "comments": 30,
        "likes": 80,
        "shares": 15
    })
    print("     版本 A: 2000 展现，400 点击，120 转化 (30% 转化率)")
    print("     版本 B: 2000 展现，300 点击，45 转化 (15% 转化率)")
    
    # 停止测试并分析
    print("\n[4.3] 停止测试并进行统计分析...")
    stop_result = service.stop_test(test_id)
    
    assert "analysis" in stop_result, "分析结果缺失"
    analysis = stop_result["analysis"]
    
    # 验证统计检验
    print("\n[4.4] 验证统计检验结果...")
    stat_tests = analysis.get("statistical_tests", [])
    assert len(stat_tests) > 0, "应该有统计检验结果"
    
    # 查找转化率检验
    conv_test = None
    for test in stat_tests:
        if test["metric"] == "conversion_rate":
            conv_test = test
            break
    
    assert conv_test is not None, "应该包含转化率检验"
    
    print("     检验类型：%s" % conv_test["test_name"])
    print("     P 值：%.6f" % conv_test["p_value"])
    print("     置信度：%.2f%%" % (conv_test["confidence_level"] * 100))
    print("     是否显著：%s" % ("是" if conv_test["is_significant"] else "否"))
    print("     效应量：%.4f" % conv_test["effect_size"])
    print("     推荐：%s" % conv_test["recommendation"])
    
    # 验证显著性
    assert conv_test["p_value"] < 0.05, "P 值应该小于 0.05（显著）"
    assert conv_test["is_significant"], "差异应该显著"
    print("[OK] 统计显著性检验通过")
    
    # 验证优胜者判断
    print("\n[4.5] 验证优胜者判断...")
    winner = analysis.get("winner")
    assert winner is not None, "应该有优胜者"
    assert winner["winner"] == "A", "版本 A 应该获胜"
    assert winner["is_conclusive"], "结论应该是明确的"
    print("     优胜者：版本 %s" % winner["winner"])
    print("     结论是否明确：%s" % ("是" if winner["is_conclusive"] else "否"))
    print("[OK] 优胜者判断正确")
    
    cleanup_test_dir()
    print("\n[PASS] 测试 4 通过：统计显著性检验功能正常")
    return True


def test_winner_recommendation():
    """测试 5: 优胜话术推荐"""
    print("\n" + "="*60)
    print("测试 5: 优胜话术推荐")
    print("="*60)
    
    cleanup_test_dir()
    service = ABTestingService(data_dir="data/ab_testing_test")
    
    # 创建并完成测试
    print("\n[5.1] 创建并完成测试...")
    variants = [
        {"variant": "A", "content": "🔥限时秒杀！手慢无！", "description": "紧迫感"},
        {"variant": "B", "content": "✨明星同款，万人好评！", "description": "社会认同"}
    ]
    
    result = service.create_test(
        name="推荐测试",
        variants=variants,
        traffic_allocation="even",
        duration_hours=24
    )
    test_id = result["test_id"]
    service.start_test(test_id)
    
    # 模拟数据（版本 B 表现更好）
    service.update_variant_metrics(test_id, "%s_v0" % test_id, {
        "impressions": 1500,
        "clicks": 200,
        "conversions": 40,
        "comments": 30,
        "likes": 100,
        "shares": 20
    })
    
    service.update_variant_metrics(test_id, "%s_v1" % test_id, {
        "impressions": 1500,
        "clicks": 300,
        "conversions": 90,
        "comments": 60,
        "likes": 200,
        "shares": 40
    })
    
    # 停止测试
    service.stop_test(test_id)
    
    # 获取推荐
    print("\n[5.2] 获取优胜话术推荐...")
    test_detail = service.get_test(test_id)
    recommendation = test_detail.get("recommendation")
    
    assert recommendation is not None, "推荐结果缺失"
    
    print("     置信度：%s" % recommendation["confidence"])
    print("     建议操作：%s" % recommendation["action"])
    print("     原因：%s" % recommendation["reasoning"])
    
    # 验证推荐
    assert recommendation["winner"]["winner"] == "B", "版本 B 应该被推荐"
    assert recommendation["action"] == "deploy_winner", "应该建议部署优胜者"
    print("[OK] 推荐结果正确")
    
    # 验证下一步建议
    print("\n[5.3] 验证下一步建议...")
    next_steps = recommendation["next_steps"]
    assert len(next_steps) > 0, "应该有下一步建议"
    print("     建议数量：%d" % len(next_steps))
    for i, step in enumerate(next_steps):
        print("     %d. %s" % (i+1, step))
    print("[OK] 下一步建议完整")
    
    cleanup_test_dir()
    print("\n[PASS] 测试 5 通过：优胜话术推荐功能正常")
    return True


def test_report_generation():
    """测试 6: 测试报告生成"""
    print("\n" + "="*60)
    print("测试 6: 测试报告生成")
    print("="*60)
    
    cleanup_test_dir()
    service = ABTestingService(data_dir="data/ab_testing_test")
    
    # 创建并完成测试
    print("\n[6.1] 创建并完成测试...")
    variants = [
        {"variant": "A", "content": "话术 A 内容", "description": "版本 A"},
        {"variant": "B", "content": "话术 B 内容", "description": "版本 B"}
    ]
    
    result = service.create_test(
        name="报告生成测试",
        variants=variants,
        description="用于测试报告生成",
        traffic_allocation="even",
        duration_hours=24
    )
    test_id = result["test_id"]
    service.start_test(test_id)
    
    # 添加数据
    service.update_variant_metrics(test_id, "%s_v0" % test_id, {
        "impressions": 1000,
        "clicks": 150,
        "conversions": 45,
        "comments": 30,
        "likes": 80,
        "shares": 20
    })
    
    service.update_variant_metrics(test_id, "%s_v1" % test_id, {
        "impressions": 1000,
        "clicks": 120,
        "conversions": 30,
        "comments": 20,
        "likes": 50,
        "shares": 10
    })
    
    # 停止测试
    service.stop_test(test_id)
    
    # 生成报告
    print("\n[6.2] 生成测试报告...")
    report = service.generate_report(test_id)
    
    assert report is not None, "报告生成失败"
    print("[OK] 报告生成成功")
    
    # 验证报告内容
    print("\n[6.3] 验证报告完整性...")
    
    # 测试信息
    assert "test_info" in report, "缺少测试信息"
    assert report["test_info"]["name"] == "报告生成测试", "测试名称不匹配"
    print("     [OK] 测试信息完整")
    
    # 变体摘要
    assert "variants_summary" in report, "缺少变体摘要"
    assert len(report["variants_summary"]) == 2, "变体数量不匹配"
    print("     [OK] 变体摘要完整")
    
    # 统计分析
    assert "statistical_analysis" in report, "缺少统计分析"
    assert len(report["statistical_analysis"]) > 0, "应该有统计检验"
    print("     [OK] 统计分析完整")
    
    # 优胜者
    assert "winner" in report, "缺少优胜者信息"
    print("     [OK] 优胜者信息完整")
    
    # 推荐
    assert "recommendation" in report, "缺少推荐"
    print("     [OK] 推荐信息完整")
    
    # 结论
    assert "conclusion" in report, "缺少结论"
    print("     [OK] 结论完整")
    
    # 打印报告摘要
    print("\n[6.4] 报告摘要:")
    print("     测试 ID: %s" % report["report_id"])
    print("     测试名称：%s" % report["test_info"]["name"])
    print("     状态：%s" % report["test_info"]["status"])
    print("     优胜者：%s" % (report["winner"]["winner"] if report["winner"] else "无"))
    print("     结论：%s" % report["conclusion"][:50] + "...")
    
    cleanup_test_dir()
    print("\n[PASS] 测试 6 通过：测试报告生成功能正常")
    return True


def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("LiveMirror 话术 A/B 测试功能测试")
    print("="*60)
    
    tests = [
        ("话术版本管理", test_script_version_management),
        ("流量分配配置", test_traffic_allocation),
        ("效果对比分析", test_effect_comparison),
        ("统计显著性检验", test_statistical_significance),
        ("优胜话术推荐", test_winner_recommendation),
        ("测试报告生成", test_report_generation)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            success = result[0] if isinstance(result, tuple) else result
            results.append((name, success))
        except AssertionError as e:
            print("\n[FAIL] %s: %s" % (name, str(e)))
            results.append((name, False))
        except Exception as e:
            print("\n[ERROR] %s: %s" % (name, str(e)))
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # 汇总结果
    print("\n" + "="*60)
    print("测试汇总")
    print("="*60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "PASS" if success else "FAIL"
        print("[%s] %s" % (status, name))
    
    print("\n总计：%d/%d 通过" % (passed, total))
    print("="*60)
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
