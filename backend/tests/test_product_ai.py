"""
LiveMirror Product AI Service Tests
智能选品服务测试
"""

import pytest
import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from services.product_ai import ProductAIService, product_ai_service


class TestProductAIService:
    """产品 AI 服务测试类"""
    
    @pytest.fixture
    def service(self):
        """创建服务实例"""
        return ProductAIService()
    
    @pytest.fixture
    def sample_product(self):
        """示例产品"""
        return {
            'product_id': 'P1001',
            'product_name': '美妆爆款产品 1',
            'category': '美妆',
            'base_price': 199,
            'cost_price': 80,
            'monthly_sales': 5000,
            'competition_level': 0.5,
            'seasonal_factor': 1.1,
            'supply_stability': 0.85,
            'profit_margin': 0.45,
            'growth_rate': 0.25,
            'customer_rating': 4.5,
            'return_rate': 0.05,
            'inventory_days': 25,
            'supplier_count': 5,
            'trend_score': 0.82
        }
    
    def test_calculate_product_score(self, service, sample_product):
        """测试产品评分计算"""
        score = service.calculate_product_score(sample_product)
        
        assert score.product_id == 'P1001'
        assert score.product_name == '美妆爆款产品 1'
        assert score.category == '美妆'
        assert 0 <= score.overall_score <= 100
        assert 0 <= score.market_score <= 100
        assert 0 <= score.competition_score <= 100
        assert 0 <= score.trend_score <= 100
        assert 0 <= score.supply_risk_score <= 100
        assert 0 <= score.profit_score <= 100
        assert score.recommendation in ['强烈推荐', '推荐', '谨慎考虑', '不推荐']
        
        print(f"✅ 产品评分测试通过")
        print(f"   综合评分：{score.overall_score}")
        print(f"   推荐等级：{score.recommendation}")
    
    def test_analyze_competitors(self, service):
        """测试竞品分析"""
        result = service.analyze_competitors('P1001', '美妆')
        
        assert 'error' not in result or result.get('error') is None
        assert 'total_competitors' in result
        assert 'avg_competitor_price' in result
        assert 'avg_competitor_sales' in result
        assert 'competition_intensity' in result
        
        print(f"✅ 竞品分析测试通过")
        print(f"   竞争对手数量：{result.get('total_competitors', 0)}")
        print(f"   竞争强度：{result.get('competition_intensity', '未知')}")
    
    def test_predict_trend(self, service):
        """测试趋势预测"""
        result = service.predict_trend('美妆', months_ahead=3)
        
        assert 'category' in result
        assert 'predictions' in result
        assert len(result['predictions']) == 3
        assert 'trend_outlook' in result
        assert result['trend_outlook'] in ['乐观', '平稳', '谨慎']
        assert 'hot_keywords' in result
        
        print(f"✅ 趋势预测测试通过")
        print(f"   类别：{result['category']}")
        print(f"   趋势展望：{result['trend_outlook']}")
        print(f"   平均预测分：{result['avg_predicted_score']}")
    
    def test_assess_supply_risk(self, service):
        """测试供应链风险评估"""
        result = service.assess_supply_risk('P1001')
        
        assert 'error' not in result or result.get('error') is None
        assert 'risk_level' in result
        assert result['risk_level'] in ['低风险', '中风险', '高风险', '极高风险']
        assert 'risk_level_score' in result
        assert 'risk_breakdown' in result
        assert 'recommendations' in result
        
        print(f"✅ 供应链风险评估测试通过")
        print(f"   风险等级：{result['risk_level']}")
        print(f"   风险评分：{result['risk_level_score']}")
    
    def test_analyze_profit_margin(self, service):
        """测试利润空间分析"""
        result = service.analyze_profit_margin('P1001')
        
        assert 'error' not in result or result.get('error') is None
        assert 'base_price' in result
        assert 'cost_price' in result
        assert 'gross_profit' in result
        assert 'net_profit' in result
        assert 'profit_rating' in result
        assert result['profit_rating'] in ['优秀', '良好', '一般', '较差']
        assert 'cost_structure' in result
        
        print(f"✅ 利润空间分析测试通过")
        print(f"   销售价格：¥{result['base_price']}")
        print(f"   净利润：¥{result['net_profit']}")
        print(f"   净利率：{result['net_margin_percent']:.1f}%")
        print(f"   利润评级：{result['profit_rating']}")
    
    def test_generate_decision_report(self, service):
        """测试决策报告生成"""
        result = service.generate_decision_report('P1001')
        
        assert 'error' not in result or result.get('error') is None
        assert 'product_id' in result
        assert 'overall_score' in result
        assert 'score_breakdown' in result
        assert 'competitor_analysis' in result
        assert 'trend_prediction' in result
        assert 'supply_risk' in result
        assert 'profit_analysis' in result
        assert 'decision_factors' in result
        assert 'final_decision' in result
        assert result['final_decision'] in ['强烈推荐', '推荐', '谨慎推荐', '不推荐']
        assert 'key_insights' in result
        
        print(f"✅ 决策报告生成测试通过")
        print(f"   产品：{result['product_name']}")
        print(f"   综合评分：{result['overall_score']}")
        print(f"   最终决策：{result['final_decision']}")
        print(f"   置信度：{result['confidence_level']}")
    
    def test_get_top_products(self, service):
        """测试获取 TOP 产品"""
        result = service.get_top_products(limit=10)
        
        assert len(result) <= 10
        assert all('product' in item and 'score' in item for item in result)
        
        # 验证按评分降序排列
        scores = [item['score']['overall_score'] for item in result]
        assert scores == sorted(scores, reverse=True)
        
        print(f"✅ TOP 产品测试通过")
        print(f"   获取产品数量：{len(result)}")
        if result:
            print(f"   TOP1 产品：{result[0]['score']['product_name']} ({result[0]['score']['overall_score']}分)")
    
    def test_get_top_products_by_category(self, service):
        """测试按类别获取 TOP 产品"""
        result = service.get_top_products(category='美妆', limit=5)
        
        assert len(result) <= 5
        assert all(item['product']['category'] == '美妆' for item in result)
        
        print(f"✅ 分类别 TOP 产品测试通过")
        print(f"   类别：美妆")
        print(f"   获取产品数量：{len(result)}")
    
    def test_score_consistency(self, service, sample_product):
        """测试评分一致性"""
        # 多次计算同一产品，结果应该一致
        score1 = service.calculate_product_score(sample_product)
        score2 = service.calculate_product_score(sample_product)
        
        assert score1.overall_score == score2.overall_score
        assert score1.market_score == score2.market_score
        assert score1.profit_score == score2.profit_score
        
        print(f"✅ 评分一致性测试通过")
    
    def test_invalid_product(self, service):
        """测试无效产品处理"""
        # 测试不存在的产品
        result = service.assess_supply_risk('INVALID_ID')
        assert 'error' in result
        
        result = service.analyze_profit_margin('INVALID_ID')
        assert 'error' in result
        
        print(f"✅ 无效产品处理测试通过")


class TestProductAIRoutes:
    """产品 AI 路由测试类"""
    
    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        from routes.product_ai import router as product_ai_router
        
        # 创建独立的应用只包含 product_ai 路由
        app = FastAPI(title="Product AI Test")
        app.include_router(product_ai_router)
        
        return TestClient(app)
    
    def test_health_check(self, client):
        """测试健康检查"""
        response = client.get('/api/product-ai/health')
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert data['data']['status'] == 'healthy'
        
        print(f"✅ 健康检查测试通过")
    
    def test_score_product(self, client):
        """测试产品评分接口"""
        response = client.post(
            '/api/product-ai/score/product',
            json={'product_id': 'P1001'}
        )
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'overall_score' in data['data']
        
        print(f"✅ 产品评分接口测试通过")
    
    def test_predict_trend_api(self, client):
        """测试趋势预测接口"""
        response = client.post(
            '/api/product-ai/predict/trend',
            json={'category': '美妆', 'months_ahead': 3}
        )
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'trend_outlook' in data['data']
        
        print(f"✅ 趋势预测接口测试通过")
    
    def test_get_categories(self, client):
        """测试获取类别接口"""
        response = client.get('/api/product-ai/categories')
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'categories' in data['data']
        assert len(data['data']['categories']) > 0
        
        print(f"✅ 获取类别接口测试通过")
    
    def test_top_products_api(self, client):
        """测试 TOP 产品接口"""
        response = client.post(
            '/api/product-ai/top/products',
            json={'limit': 10}
        )
        assert response.status_code == 200
        data = response.json()
        assert data['success'] is True
        assert 'products' in data['data']
        
        print(f"✅ TOP 产品接口测试通过")


def run_sample_analysis():
    """运行样本分析并展示结果"""
    print("\n" + "="*60)
    print("LiveMirror Intelligent Product Selection 2.0 - Sample Analysis")
    print("="*60)
    
    service = product_ai_service
    
    # 获取 TOP 5 产品
    print("\n[TOP 5 Recommended Products]:")
    print("-" * 60)
    top_products = service.get_top_products(limit=5)
    
    for i, item in enumerate(top_products, 1):
        score = item['score']
        print(f"\n{i}. {score['product_name']}")
        print(f"   类别：{score['category']}")
        print(f"   综合评分：{score['overall_score']}")
        print(f"   推荐等级：{score['recommendation']}")
        print(f"   市场热度：{score['market_score']} | 利润空间：{score['profit_score']}")
    
    # 生成详细决策报告
    print("\n\n[Detailed Decision Report Example]:")
    print("-" * 60)
    if top_products:
        top_product_id = top_products[0]['product']['product_id']
        report = service.generate_decision_report(top_product_id)
        
        print(f"\nProduct: {report['product_name']}")
        print(f"Category: {report['category']}")
        print(f"Overall Score: {report['overall_score']}")
        print(f"Final Decision: {report['final_decision']} (Confidence: {report['confidence_level']})")
        
        print(f"\nScore Breakdown:")
        for dim, val in report['score_breakdown'].items():
            print(f"   - {dim}: {val}")
        
        print(f"\nPositive Factors ({len(report['decision_factors']['positive'])}):")
        for factor in report['decision_factors']['positive']:
            print(f"   [+] {factor}")
        
        print(f"\nNegative Factors ({len(report['decision_factors']['negative'])}):")
        for factor in report['decision_factors']['negative']:
            print(f"   [-] {factor}")
        
        print(f"\nKey Insights:")
        for insight in report['key_insights']:
            print(f"   [*] {insight}")
    
    print("\n" + "="*60)
    print("Sample Analysis Complete")
    print("="*60 + "\n")


if __name__ == '__main__':
    # 运行样本分析
    run_sample_analysis()
