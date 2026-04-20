# -*- coding: utf-8 -*-
"""
粉丝画像服务测试
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from backend.services.fan_profile import FanProfileService, run_tests


def test_basic_profile():
    """测试基础画像生成"""
    print("\n" + "=" * 60)
    print("Test 1: Basic Profile Generation")
    print("=" * 60)
    
    service = FanProfileService()
    result = service.get_basic_profile()
    
    assert 'total_fans' in result
    assert 'age_distribution' in result
    assert 'gender_distribution' in result
    assert 'city_distribution' in result
    assert result['total_fans'] == 1000
    
    print("[PASS] Total fans: {}".format(result['total_fans']))
    print("[PASS] Age distribution keys: {}".format(list(result['age_distribution'].keys())))
    print("[PASS] Gender distribution keys: {}".format(list(result['gender_distribution'].keys())))
    print("[PASS] City count: {}".format(len(result['city_distribution'])))
    
    return True


def test_activity_levels():
    """测试活跃度分层"""
    print("\n" + "=" * 60)
    print("Test 2: Activity Levels")
    print("=" * 60)
    
    service = FanProfileService()
    result = service.get_activity_levels()
    
    assert 'high_activity' in result
    assert 'medium_activity' in result
    assert 'low_activity' in result
    assert 'dormant' in result
    
    total_percentage = (
        result['high_activity']['percentage'] +
        result['medium_activity']['percentage'] +
        result['low_activity']['percentage'] +
        result['dormant']['percentage']
    )
    assert 99.9 <= total_percentage <= 100.1
    
    print("[PASS] High activity: {} ({}%)".format(
        result['high_activity']['count'],
        result['high_activity']['percentage']
    ))
    print("[PASS] Medium activity: {} ({}%)".format(
        result['medium_activity']['count'],
        result['medium_activity']['percentage']
    ))
    print("[PASS] Low activity: {} ({}%)".format(
        result['low_activity']['count'],
        result['low_activity']['percentage']
    ))
    print("[PASS] Dormant: {} ({}%)".format(
        result['dormant']['count'],
        result['dormant']['percentage']
    ))
    print("[PASS] Total percentage: {:.2f}%".format(total_percentage))
    
    return True


def test_ltv_calculation():
    """测试 LTV 计算"""
    print("\n" + "=" * 60)
    print("Test 3: LTV Calculation")
    print("=" * 60)
    
    service = FanProfileService()
    
    result = service.calculate_ltv()
    assert 'average_ltv' in result
    assert 'distribution' in result
    assert 'total_revenue' in result
    
    print("[PASS] Average LTV: Y{}".format(result['average_ltv']))
    print("[PASS] Total revenue: Y{}".format(result['total_revenue']))
    print("[PASS] VIP count: {}".format(result['distribution']['VIP']['count']))
    print("[PASS] High value count: {}".format(result['distribution']['high_value']['count']))
    print("[PASS] Medium value count: {}".format(result['distribution']['medium_value']['count']))
    print("[PASS] Low value count: {}".format(result['distribution']['low_value']['count']))
    
    single_result = service.calculate_ltv(fan_id=1)
    assert 'fan_id' in single_result
    assert 'ltv' in single_result
    assert 'tier' in single_result
    
    print("[PASS] Fan #1 LTV: Y{}".format(single_result['ltv']))
    print("[PASS] Fan #1 tier: {}".format(single_result['tier']))
    
    return True


def test_churn_warning():
    """测试流失预警"""
    print("\n" + "=" * 60)
    print("Test 4: Churn Warning")
    print("=" * 60)
    
    service = FanProfileService()
    result = service.get_churn_warning()
    
    assert 'total_at_risk' in result
    assert 'at_risk_percentage' in result
    assert 'risk_distribution' in result
    assert 'high_risk_fans' in result
    
    print("[PASS] Total at risk: {} ({}%)".format(
        result['total_at_risk'],
        result['at_risk_percentage']
    ))
    print("[PASS] High risk: {}".format(result['risk_distribution']['high']['count']))
    print("[PASS] Medium risk: {}".format(result['risk_distribution']['medium']['count']))
    print("[PASS] Low risk: {}".format(result['risk_distribution']['low']['count']))
    
    if result['high_risk_fans']:
        print("[PASS] High risk fans sample count: {}".format(len(result['high_risk_fans'])))
        first_fan = result['high_risk_fans'][0]
        print("  - Fan ID: {}".format(first_fan['fan_id']))
        print("  - Risk score: {}".format(first_fan['risk_score']))
        print("  - Risk factors: {}".format(', '.join(first_fan['risk_factors'])))
    
    return True


def test_growth_trend():
    """测试增长趋势"""
    print("\n" + "=" * 60)
    print("Test 5: Growth Trend")
    print("=" * 60)
    
    service = FanProfileService()
    result = service.get_growth_trend()
    
    assert 'monthly_data' in result
    assert 'growth_rates' in result
    assert 'total_growth' in result
    assert 'average_monthly_growth' in result
    
    print("[PASS] Total growth: {}".format(result['total_growth']))
    print("[PASS] Average monthly growth: {}".format(result['average_monthly_growth']))
    print("[PASS] Monthly data count: {}".format(len(result['monthly_data'])))
    print("[PASS] Growth rates count: {}".format(len(result['growth_rates'])))
    
    if result['monthly_data']:
        print("[PASS] Latest month: {} ({} fans)".format(
            result['monthly_data'][-1]['month'],
            result['monthly_data'][-1]['new_fans']
        ))
    
    return True


def test_interest_tags():
    """测试兴趣标签"""
    print("\n" + "=" * 60)
    print("Test 6: Interest Tags")
    print("=" * 60)
    
    service = FanProfileService()
    result = service.get_interest_tags()
    
    assert 'tags' in result
    assert 'top_tags' in result
    assert len(result['top_tags']) == 5
    
    print("[PASS] Top tags: {}".format(', '.join(result['top_tags'])))
    print("[PASS] Total tags: {}".format(len(result['tags'])))
    print("[PASS] Top 3 tags:")
    for i, tag in enumerate(result['tags'][:3], 1):
        print("  {}. {}: {} ({}%)".format(i, tag['name'], tag['count'], tag['percentage']))
    
    return True


def test_full_report():
    """测试完整报告"""
    print("\n" + "=" * 60)
    print("Test 7: Full Report")
    print("=" * 60)
    
    service = FanProfileService()
    result = service.get_full_profile_report()
    
    assert 'basic_profile' in result
    assert 'activity_levels' in result
    assert 'interest_tags' in result
    assert 'ltv_analysis' in result
    assert 'churn_warning' in result
    assert 'growth_trend' in result
    assert 'generated_at' in result
    
    print("[PASS] Report contains all modules")
    print("[PASS] Generated at: {}".format(result['generated_at']))
    print("[PASS] Total fans: {}".format(result['basic_profile']['total_fans']))
    print("[PASS] Average LTV: Y{}".format(result['ltv_analysis']['average_ltv']))
    print("[PASS] At-risk percentage: {}%".format(result['churn_warning']['at_risk_percentage']))
    
    return True


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("Fan Profile Analysis - Complete Test Suite")
    print("=" * 60)
    
    tests = [
        ("Basic Profile", test_basic_profile),
        ("Activity Levels", test_activity_levels),
        ("LTV Calculation", test_ltv_calculation),
        ("Churn Warning", test_churn_warning),
        ("Growth Trend", test_growth_trend),
        ("Interest Tags", test_interest_tags),
        ("Full Report", test_full_report)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result, None))
        except Exception as e:
            results.append((name, False, str(e)))
            print("[FAIL] Test failed: {}".format(e))
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result, _ in results if result)
    total = len(results)
    
    for name, result, error in results:
        status = "[PASS]" if result else "[FAIL]"
        print("{} - {}".format(status, name))
        if error:
            print("  Error: {}".format(error))
    
    print("\n" + "-" * 60)
    print("Total: {}/{} tests passed".format(passed, total))
    
    if passed == total:
        print("\n[SUCCESS] All tests passed!")
        return True
    else:
        print("\n[WARNING] {} tests failed".format(total - passed))
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
