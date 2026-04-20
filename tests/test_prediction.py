"""
LiveMirror Prediction Service Tests
直播预测服务测试
"""

import pytest
import sys
import os
from datetime import datetime, timedelta

# 添加 backend 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
from services.prediction import PredictionService


@pytest.fixture
def prediction_service():
    """预测服务测试夹具"""
    return PredictionService()


class TestGMVPrediction:
    """GMV 预测测试"""
    
    def test_predict_gmv_basic(self, prediction_service):
        """测试基础 GMV 预测"""
        result = prediction_service.predict_gmv(expected_viewers=5000)
        
        assert 'predicted_gmv' in result
        assert 'confidence_interval' in result
        assert 'avg_conversion_value' in result
        assert result['predicted_gmv'] > 0
        assert result['confidence_interval']['lower'] <= result['predicted_gmv']
        assert result['confidence_interval']['upper'] >= result['predicted_gmv']
    
    def test_predict_gmv_with_custom_confidence(self, prediction_service):
        """测试自定义置信度"""
        result_95 = prediction_service.predict_gmv(expected_viewers=5000, confidence=0.95)
        result_80 = prediction_service.predict_gmv(expected_viewers=5000, confidence=0.80)
        
        # 置信度越高，区间应该越宽
        interval_95 = result_95['confidence_interval']['upper'] - result_95['confidence_interval']['lower']
        interval_80 = result_80['confidence_interval']['upper'] - result_80['confidence_interval']['lower']
        
        assert interval_95 >= interval_80
    
    def test_predict_gmv_zero_viewers(self, prediction_service):
        """测试零观看人数的 GMV 预测"""
        result = prediction_service.predict_gmv(expected_viewers=0)
        
        assert result['predicted_gmv'] == 0
    
    def test_predict_gmv_large_audience(self, prediction_service):
        """测试大观众基数的 GMV 预测"""
        result = prediction_service.predict_gmv(expected_viewers=100000)
        
        assert result['predicted_gmv'] > 0
        assert result['predicted_gmv'] > prediction_service.predict_gmv(expected_viewers=1000)['predicted_gmv']


class TestViewersPrediction:
    """观看人数预测测试"""
    
    def test_predict_viewers_weekend(self, prediction_service):
        """测试周末观看人数预测"""
        result_sat = prediction_service.predict_viewers(day_of_week=5, hour=20)
        result_sun = prediction_service.predict_viewers(day_of_week=6, hour=20)
        
        assert 'predicted_viewers' in result_sat
        assert 'trend' in result_sat
        assert 'time_multiplier' in result_sat
        assert result_sat['predicted_viewers'] > 0
    
    def test_predict_viewers_weekday(self, prediction_service):
        """测试工作日观看人数预测"""
        result = prediction_service.predict_viewers(day_of_week=2, hour=20)
        
        assert result['predicted_viewers'] > 0
    
    def test_predict_viewers_peak_hours(self, prediction_service):
        """测试高峰时段观看人数"""
        result_peak = prediction_service.predict_viewers(day_of_week=5, hour=20)
        result_offpeak = prediction_service.predict_viewers(day_of_week=5, hour=3)
        
        # 高峰时段系数应该更高
        assert result_peak['time_multiplier'] >= result_offpeak['time_multiplier']
    
    def test_predict_viewers_trend(self, prediction_service):
        """测试趋势预测"""
        result = prediction_service.predict_viewers(day_of_week=5, hour=20)
        
        assert result['trend'] in ['increasing', 'decreasing', 'stable']


class TestConversionRatePrediction:
    """转化率预测测试"""
    
    def test_predict_conversion_basic(self, prediction_service):
        """测试基础转化率预测"""
        result = prediction_service.predict_conversion_rate()
        
        assert 'predicted_conversion_rate' in result
        assert 'predicted_conversion_rate_percent' in result
        assert result['predicted_conversion_rate'] > 0
        assert result['predicted_conversion_rate'] < 1  # 转化率应该小于 100%
    
    def test_predict_conversion_by_category(self, prediction_service):
        """测试不同类别的转化率"""
        beauty = prediction_service.predict_conversion_rate(product_category='beauty')
        electronics = prediction_service.predict_conversion_rate(product_category='electronics')
        
        # 美妆通常转化率更高
        assert beauty['predicted_conversion_rate'] >= electronics['predicted_conversion_rate']
    
    def test_predict_conversion_by_price(self, prediction_service):
        """测试不同价格区间的转化率"""
        low = prediction_service.predict_conversion_rate(price_range='low')
        high = prediction_service.predict_conversion_rate(price_range='high')
        
        # 低价通常转化率更高
        assert low['predicted_conversion_rate'] >= high['predicted_conversion_rate']


class TestTimeRecommendation:
    """最佳时间推荐测试"""
    
    def test_recommend_best_time_basic(self, prediction_service):
        """测试基础时间推荐"""
        result = prediction_service.recommend_best_time()
        
        assert 'recommended_day' in result
        assert 'recommended_hour' in result
        assert 'recommended_time_str' in result
        assert 'alternative_times' in result
        assert 0 <= result['recommended_day'] <= 6
        assert 0 <= result['recommended_hour'] <= 23
    
    def test_recommend_best_time_weekend_preference(self, prediction_service):
        """测试周末偏好推荐"""
        result = prediction_service.recommend_best_time()
        
        # 通常推荐周末
        assert result['recommended_day'] in [4, 5, 6]  # 周五到周日
    
    def test_recommend_best_time_evening_preference(self, prediction_service):
        """测试晚间偏好推荐"""
        result = prediction_service.recommend_best_time()
        
        # 通常推荐晚上
        assert 18 <= result['recommended_hour'] <= 22


class TestAccuracyEvaluation:
    """准确度评估测试"""
    
    def test_evaluate_accuracy_basic(self, prediction_service):
        """测试基础准确度评估"""
        predictions = [
            {'gmv': 50000, 'viewers': 5000},
            {'gmv': 55000, 'viewers': 5500},
            {'gmv': 48000, 'viewers': 4800}
        ]
        actuals = [
            {'gmv': 51000, 'viewers': 5100},
            {'gmv': 54000, 'viewers': 5400},
            {'gmv': 49000, 'viewers': 4900}
        ]
        
        result = prediction_service.evaluate_accuracy(predictions, actuals)
        
        assert 'total_predictions' in result
        assert 'metrics' in result
        assert result['total_predictions'] == 3
    
    def test_evaluate_accuracy_perfect(self, prediction_service):
        """测试完美预测的准确度"""
        predictions = [
            {'gmv': 50000, 'viewers': 5000},
            {'gmv': 55000, 'viewers': 5500}
        ]
        actuals = predictions.copy()
        
        result = prediction_service.evaluate_accuracy(predictions, actuals)
        
        assert result['overall_accuracy'] == 100
        assert result['rating'] == '优秀'
    
    def test_evaluate_accuracy_mismatch(self, prediction_service):
        """测试数据不匹配的准确度评估"""
        predictions = [{'gmv': 50000}]
        actuals = [{'gmv': 50000}, {'gmv': 55000}]
        
        result = prediction_service.evaluate_accuracy(predictions, actuals)
        
        assert 'error' in result
    
    def test_evaluate_accuracy_empty(self, prediction_service):
        """测试空数据的准确度评估"""
        result = prediction_service.evaluate_accuracy([], [])
        
        assert 'error' in result


class TestTrendData:
    """趋势数据测试"""
    
    def test_get_trend_data_basic(self, prediction_service):
        """测试基础趋势数据"""
        result = prediction_service.get_trend_data(days=30)
        
        assert 'dates' in result
        assert 'gmv' in result
        assert 'viewers' in result
        assert 'conversion_rates' in result
        assert 'summary' in result
        assert len(result['dates']) <= 30
    
    def test_get_trend_data_custom_days(self, prediction_service):
        """测试自定义天数"""
        result_7 = prediction_service.get_trend_data(days=7)
        result_14 = prediction_service.get_trend_data(days=14)
        
        assert len(result_7['dates']) <= 7
        assert len(result_14['dates']) <= 14
    
    def test_get_trend_data_summary(self, prediction_service):
        """测试趋势数据摘要"""
        result = prediction_service.get_trend_data(days=30)
        
        assert 'total_gmv' in result['summary']
        assert 'avg_viewers' in result['summary']
        assert 'avg_conversion_rate' in result['summary']
        assert 'trend' in result['summary']
        assert result['summary']['trend'] in ['increasing', 'decreasing', 'stable']


class TestSamplePrediction:
    """示例预测测试"""
    
    def test_generate_sample_prediction(self, prediction_service):
        """测试生成示例预测"""
        result = prediction_service.generate_sample_prediction()
        
        assert 'timestamp' in result
        assert 'viewers_prediction' in result
        assert 'gmv_prediction' in result
        assert 'conversion_prediction' in result
        assert 'time_recommendation' in result
        assert 'trend_data' in result
        assert 'model_info' in result
        
        # 验证模型信息
        assert 'version' in result['model_info']
        assert 'data_points' in result['model_info']


class TestIntegration:
    """集成测试"""
    
    def test_full_prediction_workflow(self, prediction_service):
        """测试完整预测工作流"""
        # 1. 预测观看人数
        viewers_result = prediction_service.predict_viewers(day_of_week=5, hour=20)
        
        # 2. 基于观看人数预测 GMV
        gmv_result = prediction_service.predict_gmv(viewers_result['predicted_viewers'])
        
        # 3. 预测转化率
        conversion_result = prediction_service.predict_conversion_rate()
        
        # 4. 获取时间推荐
        time_result = prediction_service.recommend_best_time()
        
        # 5. 获取趋势数据
        trend_result = prediction_service.get_trend_data()
        
        # 验证所有结果
        assert viewers_result['predicted_viewers'] > 0
        assert gmv_result['predicted_gmv'] > 0
        assert conversion_result['predicted_conversion_rate'] > 0
        assert time_result['recommended_hour'] is not None
        assert len(trend_result['dates']) > 0
    
    def test_prediction_consistency(self, prediction_service):
        """测试预测一致性"""
        # 多次调用应该返回相似的结果（在合理范围内）
        results = [
            prediction_service.predict_gmv(expected_viewers=5000)['predicted_gmv']
            for _ in range(5)
        ]
        
        # 结果应该相同（因为是确定性计算）
        assert all(r == results[0] for r in results)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
