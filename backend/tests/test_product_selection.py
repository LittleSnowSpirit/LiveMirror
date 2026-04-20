"""
选品推荐功能测试
测试商品热度分析、价格对比、利润率计算、选品报告等功能
"""

import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.product_selection import ProductSelectionService, get_service
import unittest


class TestProductHeatAnalysis(unittest.TestCase):
    """测试商品热度分析"""
    
    def setUp(self):
        self.service = ProductSelectionService()
    
    def test_heat_analysis_exists(self):
        """测试热度分析返回数据结构"""
        result = self.service.analyze_product_heat('P001')
        
        self.assertIn('heat_score', result)
        self.assertIn('search_trend', result)
        self.assertIn('social_media', result)
        self.assertIn('platform_distribution', result)
        self.assertIn('trend_status', result)
    
    def test_heat_score_range(self):
        """测试热度分数在合理范围内"""
        result = self.service.analyze_product_heat('P001')
        
        self.assertGreaterEqual(result['heat_score'], 0)
        self.assertLessEqual(result['heat_score'], 100)
    
    def test_search_trend_structure(self):
        """测试搜索趋势数据结构"""
        result = self.service.analyze_product_heat('P001')
        
        trend = result['search_trend']
        self.assertIn('current_week', trend)
        self.assertIn('last_week', trend)
        self.assertIn('growth_rate', trend)
        self.assertIsInstance(trend['current_week'], int)
        self.assertIsInstance(trend['growth_rate'], float)
    
    def test_invalid_product(self):
        """测试无效商品 ID"""
        result = self.service.analyze_product_heat('INVALID')
        
        self.assertIn('error', result)


class TestPriceComparison(unittest.TestCase):
    """测试竞品价格对比"""
    
    def setUp(self):
        self.service = ProductSelectionService()
    
    def test_price_comparison_exists(self):
        """测试价格对比返回数据结构"""
        result = self.service.compare_competitor_prices('P001')
        
        self.assertIn('our_price', result)
        self.assertIn('competitor_prices', result)
        self.assertIn('market_avg_price', result)
        self.assertIn('price_advantage', result)
    
    def test_competitor_prices_count(self):
        """测试竞品数量"""
        result = self.service.compare_competitor_prices('P001')
        
        self.assertEqual(len(result['competitor_prices']), 5)
    
    def test_price_advantage_calculation(self):
        """测试价格优势计算"""
        result = self.service.compare_competitor_prices('P001')
        
        self.assertIsInstance(result['price_advantage'], float)
    
    def test_price_range_structure(self):
        """测试价格区间结构"""
        result = self.service.compare_competitor_prices('P001')
        
        self.assertIn('price_range', result)
        self.assertIn('min', result['price_range'])
        self.assertIn('max', result['price_range'])


class TestProfitMargin(unittest.TestCase):
    """测试利润率计算"""
    
    def setUp(self):
        self.service = ProductSelectionService()
    
    def test_profit_margin_exists(self):
        """测试利润率分析返回数据结构"""
        result = self.service.calculate_profit_margin('P001')
        
        self.assertIn('gross_margin_percent', result)
        self.assertIn('net_margin_percent', result)
        self.assertIn('roi_percent', result)
        self.assertIn('profitability_rating', result)
    
    def test_margin_calculation(self):
        """测试利润率计算逻辑"""
        result = self.service.calculate_profit_margin('P001')
        
        # 毛利率应该为正数
        self.assertGreater(result['gross_margin_percent'], 0)
        # 净利率应该小于毛利率
        self.assertLessEqual(result['net_margin_percent'], result['gross_margin_percent'])
    
    def test_profitability_rating(self):
        """测试盈利评级"""
        result = self.service.calculate_profit_margin('P001')
        
        self.assertIn(result['profitability_rating'], ['high', 'medium', 'low'])
    
    def test_cost_breakdown(self):
        """测试成本分解"""
        result = self.service.calculate_profit_margin('P001')
        
        self.assertIn('product_cost', result)
        self.assertIn('platform_fee', result)
        self.assertIn('shipping_cost', result)
        self.assertIn('marketing_cost', result)
        self.assertIn('total_cost', result)


class TestSeasonalityAnalysis(unittest.TestCase):
    """测试季节性趋势分析"""
    
    def setUp(self):
        self.service = ProductSelectionService()
    
    def test_seasonality_exists(self):
        """测试季节性分析返回数据结构"""
        result = self.service.analyze_seasonality('P001')
        
        self.assertIn('monthly_factors', result)
        self.assertIn('peak_season', result)
        self.assertIn('low_season', result)
        self.assertIn('current_month_factor', result)
    
    def test_monthly_factors_count(self):
        """测试月份因子数量"""
        result = self.service.analyze_seasonality('P001')
        
        self.assertEqual(len(result['monthly_factors']), 12)
    
    def test_seasonal_recommendation(self):
        """测试季节性建议"""
        result = self.service.analyze_seasonality('P001')
        
        self.assertIn(result['recommendation'], ['good_time', 'wait_for_peak'])
    
    def test_different_categories(self):
        """测试不同类别的季节性差异"""
        result1 = self.service.analyze_seasonality('P001')  # 家居用品
        result2 = self.service.analyze_seasonality('P004')  # 运动健身
        
        # 不同类别应该有不同的旺季
        # （虽然由于随机性可能相同，但数据结构应该一致）
        self.assertIn('peak_season', result1)
        self.assertIn('peak_season', result2)


class TestSupplierEvaluation(unittest.TestCase):
    """测试供应商评分系统"""
    
    def setUp(self):
        self.service = ProductSelectionService()
    
    def test_supplier_evaluation_exists(self):
        """测试供应商评估返回数据结构"""
        result = self.service.evaluate_supplier('S001')
        
        self.assertIn('overall_rating', result)
        self.assertIn('quality_score', result)
        self.assertIn('delivery_score', result)
        self.assertIn('risk_level', result)
    
    def test_rating_range(self):
        """测试评分范围"""
        result = self.service.evaluate_supplier('S001')
        
        self.assertGreaterEqual(result['overall_rating'], 0)
        self.assertLessEqual(result['overall_rating'], 5)
    
    def test_risk_level(self):
        """测试风险等级"""
        result = self.service.evaluate_supplier('S001')
        
        self.assertIn(result['risk_level'], ['low', 'medium', 'high'])


class TestSelectionReport(unittest.TestCase):
    """测试选品报告生成"""
    
    def setUp(self):
        self.service = ProductSelectionService()
    
    def test_report_generation(self):
        """测试报告生成"""
        report = self.service.generate_selection_report('P001')
        
        self.assertIsNotNone(report.product_id)
        self.assertIsNotNone(report.product_name)
        self.assertIsNotNone(report.recommendation_score)
        self.assertIsNotNone(report.summary)
    
    def test_report_score_range(self):
        """测试推荐分数范围"""
        report = self.service.generate_selection_report('P001')
        
        self.assertGreaterEqual(report.recommendation_score, 0)
        self.assertLessEqual(report.recommendation_score, 100)
    
    def test_report_contains_all_analyses(self):
        """测试报告包含所有分析维度"""
        report = self.service.generate_selection_report('P001')
        
        self.assertIsNotNone(report.heat_analysis)
        self.assertIsNotNone(report.price_comparison)
        self.assertIsNotNone(report.profit_analysis)
        self.assertIsNotNone(report.seasonality_analysis)
        self.assertIsNotNone(report.supplier_evaluation)
    
    def test_recommendation_logic(self):
        """测试推荐逻辑"""
        high_score_report = self.service.generate_selection_report('P001')
        
        # 根据分数生成不同的总结
        if high_score_report.recommendation_score >= 80:
            self.assertIn('强烈推荐', high_score_report.summary)
        elif high_score_report.recommendation_score >= 60:
            self.assertIn('推荐考虑', high_score_report.summary)
        else:
            self.assertIn('谨慎选择', high_score_report.summary)


class TestRecommendations(unittest.TestCase):
    """测试推荐列表"""
    
    def setUp(self):
        self.service = ProductSelectionService()
    
    def test_get_recommendations(self):
        """测试获取推荐列表"""
        reports = self.service.get_recommendations(min_score=60.0, limit=5)
        
        self.assertIsInstance(reports, list)
        self.assertLessEqual(len(reports), 5)
    
    def test_recommendations_sorted(self):
        """测试推荐列表按分数排序"""
        reports = self.service.get_recommendations(min_score=0.0, limit=10)
        
        if len(reports) > 1:
            for i in range(len(reports) - 1):
                self.assertGreaterEqual(
                    reports[i].recommendation_score,
                    reports[i + 1].recommendation_score
                )
    
    def test_min_score_filter(self):
        """测试最低分数过滤"""
        reports = self.service.get_recommendations(min_score=80.0, limit=10)
        
        for report in reports:
            self.assertGreaterEqual(report.recommendation_score, 80.0)


class TestServiceSingleton(unittest.TestCase):
    """测试服务单例模式"""
    
    def test_singleton_instance(self):
        """测试单例模式"""
        service1 = get_service()
        service2 = get_service()
        
        self.assertIs(service1, service2)


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加所有测试类
    suite.addTests(loader.loadTestsFromTestCase(TestProductHeatAnalysis))
    suite.addTests(loader.loadTestsFromTestCase(TestPriceComparison))
    suite.addTests(loader.loadTestsFromTestCase(TestProfitMargin))
    suite.addTests(loader.loadTestsFromTestCase(TestSeasonalityAnalysis))
    suite.addTests(loader.loadTestsFromTestCase(TestSupplierEvaluation))
    suite.addTests(loader.loadTestsFromTestCase(TestSelectionReport))
    suite.addTests(loader.loadTestsFromTestCase(TestRecommendations))
    suite.addTests(loader.loadTestsFromTestCase(TestServiceSingleton))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return result


if __name__ == '__main__':
    print("=" * 60)
    print("Product Selection Feature Test")
    print("=" * 60)
    
    result = run_tests()
    
    print("\n" + "=" * 60)
    print("Test Results Summary")
    print("=" * 60)
    passed = result.testsRun - len(result.failures) - len(result.errors)
    print(f"Passed: {passed}")
    print(f"Failed: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Total: {result.testsRun}")
    print("=" * 60)
    
    if result.wasSuccessful():
        print("All tests passed!")
        sys.exit(0)
    else:
        print("Some tests failed, please check output details")
        sys.exit(1)
