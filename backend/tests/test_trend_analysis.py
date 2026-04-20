"""
趋势分析服务测试
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime, timedelta

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.trend_analysis import (
    TrendAnalysisService,
    SessionMetrics,
    analyze_growth
)


# ==================== 测试数据 ====================

@pytest.fixture
def sample_sessions():
    """示例场次数据（上升趋势）"""
    return [
        SessionMetrics(
            session_id=f'session_{i}',
            anchor_time=datetime(2026, 4, i+1),
            duration_minutes=120,
            viewer_count=1000 + i*100,
            danmu_count=500 + i*50,
            avg_emotion_score=0.6 + i*0.05,
            peak_emotion_score=0.8 + i*0.03,
            engagement_rate=20 + i*2,
            opening_score=65 + i*5,
            product_intro_score=70 + i*3,
            price_promotion_score=75 + i*4,
            closing_score=68 + i*2,
            overall_score=70 + i*5
        )
        for i in range(5)
    ]


@pytest.fixture
def declining_sessions():
    """示例场次数据（下降趋势）"""
    return [
        SessionMetrics(
            session_id=f'session_{i}',
            anchor_time=datetime(2026, 4, i+1),
            duration_minutes=120,
            viewer_count=1000 - i*100,
            danmu_count=500 - i*50,
            avg_emotion_score=0.8 - i*0.05,
            peak_emotion_score=0.9 - i*0.03,
            engagement_rate=30 - i*3,
            overall_score=80 - i*5
        )
        for i in range(5)
    ]


@pytest.fixture
def stable_sessions():
    """示例场次数据（平稳趋势）"""
    return [
        SessionMetrics(
            session_id=f'session_{i}',
            anchor_time=datetime(2026, 4, i+1),
            duration_minutes=120,
            viewer_count=1000,
            danmu_count=500,
            avg_emotion_score=0.7 + (i%2)*0.02,  # 小幅波动
            peak_emotion_score=0.85,
            engagement_rate=25,
            overall_score=75
        )
        for i in range(4)
    ]


# ==================== 趋势计算测试 ====================

class TestTrendCalculation:
    """趋势计算测试"""
    
    def test_calculate_trend_up(self, sample_sessions):
        """测试上升趋势检测"""
        service = TrendAnalysisService()
        values = [s.overall_score for s in sample_sessions]
        
        trend = service.calculate_trend(values)
        
        assert trend.direction == 'up'
        assert trend.change_rate > 0
        assert trend.significance in ['significant', 'moderate', 'slight']
    
    def test_calculate_trend_down(self, declining_sessions):
        """测试下降趋势检测"""
        service = TrendAnalysisService()
        values = [s.overall_score for s in declining_sessions]
        
        trend = service.calculate_trend(values)
        
        assert trend.direction == 'down'
        assert trend.change_rate < 0
    
    def test_calculate_trend_stable(self, stable_sessions):
        """测试平稳趋势检测"""
        service = TrendAnalysisService()
        values = [s.overall_score for s in stable_sessions]
        
        trend = service.calculate_trend(values)
        
        assert trend.direction == 'stable'
        assert abs(trend.change_rate) < 0.05
    
    def test_calculate_trend_insufficient_data(self):
        """测试数据不足"""
        service = TrendAnalysisService()
        
        trend = service.calculate_trend([0.7])
        
        assert trend.direction == 'stable'
        assert trend.change_rate == 0


# ==================== 显著变化检测测试 ====================

class TestSignificantChanges:
    """显著变化检测测试"""
    
    def test_detect_significant_changes(self):
        """测试显著变化检测"""
        service = TrendAnalysisService()
        
        # 有明显变化的数据
        values = [0.5, 0.55, 0.6, 0.85, 0.9]  # 第 3 到第 4 个点有显著变化
        
        changes = service.detect_significant_changes(values, threshold=0.2)
        
        assert len(changes) > 0
        assert any(c['change_rate'] > 0.2 for c in changes)
    
    def test_detect_no_significant_changes(self):
        """测试无显著变化"""
        service = TrendAnalysisService()
        
        # 平稳变化的数据
        values = [0.5, 0.52, 0.54, 0.56, 0.58]
        
        changes = service.detect_significant_changes(values, threshold=0.2)
        
        assert len(changes) == 0


# ==================== 情绪趋势分析测试 ====================

class TestEmotionTrendAnalysis:
    """情绪趋势分析测试"""
    
    def test_analyze_emotion_trend_basic(self, sample_sessions):
        """测试基本情绪趋势分析"""
        service = TrendAnalysisService()
        
        result = service.analyze_emotion_trend(sample_sessions)
        
        assert 'avg_emotion' in result
        assert 'peak_emotion' in result
        assert 'significant_changes' in result
        assert result['sessions_count'] == 5
    
    def test_analyze_emotion_trend_values(self, sample_sessions):
        """测试情绪趋势值"""
        service = TrendAnalysisService()
        
        result = service.analyze_emotion_trend(sample_sessions)
        
        avg_values = result['avg_emotion']['values']
        assert len(avg_values) == 5
        assert avg_values[0] < avg_values[-1]  # 上升趋势


# ==================== 话术质量趋势测试 ====================

class TestSpeechQualityTrend:
    """话术质量趋势测试"""
    
    def test_analyze_speech_quality_basic(self, sample_sessions):
        """测试基本话术质量趋势"""
        service = TrendAnalysisService()
        
        result = service.analyze_speech_quality_trend(sample_sessions)
        
        assert 'by_type' in result
        assert 'opening' in result['by_type']
        assert 'product_intro' in result['by_type']
        assert 'price_promotion' in result['by_type']
        assert 'closing' in result['by_type']
    
    def test_analyze_speech_quality_trends(self, sample_sessions):
        """测试各类话术趋势"""
        service = TrendAnalysisService()
        
        result = service.analyze_speech_quality_trend(sample_sessions)
        
        # 所有类型都应该是上升趋势
        for speech_type, data in result['by_type'].items():
            assert data['trend']['direction'] == 'up'


# ==================== 互动趋势测试 ====================

class TestEngagementTrend:
    """互动趋势测试"""
    
    def test_analyze_engagement_basic(self, sample_sessions):
        """测试基本互动趋势"""
        service = TrendAnalysisService()
        
        result = service.analyze_engagement_trend(sample_sessions)
        
        assert 'engagement_rate' in result
        assert 'danmu_count' in result
        assert result['sessions_count'] == 5


# ==================== 成长报告测试 ====================

class TestGrowthReport:
    """成长报告测试"""
    
    def test_generate_growth_report_basic(self, sample_sessions):
        """测试生成基本成长报告"""
        service = TrendAnalysisService()
        
        report = service.generate_growth_report(sample_sessions)
        
        assert report.period_start is not None
        assert report.period_end is not None
        assert report.total_sessions == 5
        assert report.overall_trend is not None
        assert report.top_improvements is not None
        assert report.summary is not None
        assert len(report.recommendations) > 0
    
    def test_generate_growth_report_upward(self, sample_sessions):
        """测试上升趋势的成长报告"""
        service = TrendAnalysisService()
        
        report = service.generate_growth_report(sample_sessions)
        
        # 上升趋势应该有正面总结
        assert report.overall_trend.direction == 'up'
        assert '进步' in report.summary or '上升' in report.summary
        assert len(report.top_improvements) > 0
    
    def test_generate_growth_report_declining(self, declining_sessions):
        """测试下降趋势的成长报告"""
        service = TrendAnalysisService()
        
        report = service.generate_growth_report(declining_sessions)
        
        # 下降趋势应该有警示
        assert report.overall_trend.direction == 'down'
        assert len(report.areas_to_work_on) > 0
    
    def test_generate_growth_report_empty(self):
        """测试空数据"""
        service = TrendAnalysisService()
        
        with pytest.raises(ValueError):
            service.generate_growth_report([])


# ==================== 便捷函数测试 ====================

class TestConvenienceFunctions:
    """便捷函数测试"""
    
    def test_analyze_growth(self, sample_sessions):
        """测试便捷分析函数"""
        result = analyze_growth(sample_sessions)
        
        assert isinstance(result, dict)
        assert 'overall_trend' in result
        assert 'summary' in result
        assert 'recommendations' in result


# ==================== 边界情况测试 ====================

class TestEdgeCases:
    """边界情况测试"""
    
    def test_single_session(self):
        """测试单场次"""
        service = TrendAnalysisService()
        
        sessions = [
            SessionMetrics(
                session_id='single',
                anchor_time=datetime(2026, 4, 1),
                duration_minutes=120,
                viewer_count=1000,
                danmu_count=500,
                avg_emotion_score=0.7,
                peak_emotion_score=0.85,
                engagement_rate=25,
                overall_score=75
            )
        ]
        
        # 单场次应该能生成报告，但趋势为平稳
        report = service.generate_growth_report(sessions)
        assert report.total_sessions == 1
        assert report.overall_trend.direction == 'stable'
    
    def test_two_sessions(self):
        """测试两场"""
        service = TrendAnalysisService()
        
        sessions = [
            SessionMetrics(
                session_id='s1',
                anchor_time=datetime(2026, 4, 1),
                duration_minutes=120,
                viewer_count=1000,
                danmu_count=500,
                avg_emotion_score=0.6,
                peak_emotion_score=0.8,
                engagement_rate=20,
                overall_score=70
            ),
            SessionMetrics(
                session_id='s2',
                anchor_time=datetime(2026, 4, 2),
                duration_minutes=120,
                viewer_count=1200,
                danmu_count=600,
                avg_emotion_score=0.75,
                peak_emotion_score=0.9,
                engagement_rate=28,
                overall_score=82
            )
        ]
        
        report = service.generate_growth_report(sessions)
        assert report.total_sessions == 2


# ==================== 性能测试 ====================

class TestPerformance:
    """性能测试"""
    
    def test_analysis_speed(self, sample_sessions):
        """测试分析速度"""
        import time
        
        start = time.time()
        
        # 分析 50 场次
        large_sessions = sample_sessions * 10
        
        service = TrendAnalysisService()
        service.generate_growth_report(large_sessions)
        
        elapsed = time.time() - start
        
        # 应该在 1 秒内完成
        assert elapsed < 1.0, f"分析耗时{elapsed:.2f}秒"


# ==================== 运行测试 ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
