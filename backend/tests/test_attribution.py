"""
话术归因分析服务测试
"""

import pytest
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.attribution import (
    AttributionAnalysisService,
    analyze_attribution,
    AttributionResult
)


# ==================== 测试数据 ====================

@pytest.fixture
def sample_emotion_curve():
    """示例情绪曲线"""
    return [
        {"timestamp": 0, "score": 0.5, "level": "medium"},
        {"timestamp": 10, "score": 0.6, "level": "medium"},
        {"timestamp": 20, "score": 0.8, "level": "high"},
        {"timestamp": 30, "score": 0.95, "level": "very_high"},  # 峰值
        {"timestamp": 40, "score": 0.7, "level": "high"},
        {"timestamp": 50, "score": 0.5, "level": "medium"},
        {"timestamp": 60, "score": 0.6, "level": "medium"},
        {"timestamp": 70, "score": 0.85, "level": "high"},
        {"timestamp": 80, "score": 0.9, "level": "very_high"},  # 峰值
        {"timestamp": 90, "score": 0.6, "level": "medium"},
    ]


@pytest.fixture
def sample_speech_segments():
    """示例话术分段"""
    return [
        {
            "id": "speech_1",
            "type": "opening",
            "content": "欢迎大家来到直播间，今天给大家带来超值好物！",
            "start_time": 0,
            "end_time": 30
        },
        {
            "id": "speech_2",
            "type": "product_intro",
            "content": "这款产品真的超级好用，我亲自试用了一个月...",
            "start_time": 30,
            "end_time": 60
        },
        {
            "id": "speech_3",
            "type": "price_promotion",
            "content": "今天直播间特价，只要 99 元！还包邮！",
            "start_time": 60,
            "end_time": 90
        }
    ]


@pytest.fixture
def sample_danmu_list():
    """示例弹幕列表"""
    return [
        {"timestamp": 5, "content": "主播好！", "sentiment": "positive", "sentiment_score": 0.5},
        {"timestamp": 15, "content": "666", "sentiment": "positive", "sentiment_score": 0.8},
        {"timestamp": 25, "content": "真的好用吗？", "sentiment": "neutral", "sentiment_score": 0},
        {"timestamp": 32, "content": "已买！好用！", "sentiment": "positive", "sentiment_score": 0.9, "is_key_danmu": True},
        {"timestamp": 35, "content": "抢到了！", "sentiment": "positive", "sentiment_score": 0.95, "is_key_danmu": True},
        {"timestamp": 45, "content": "感觉一般般", "sentiment": "negative", "sentiment_score": -0.3},
        {"timestamp": 65, "content": "99 元太贵了", "sentiment": "negative", "sentiment_score": -0.5},
        {"timestamp": 75, "content": "划算！下单了", "sentiment": "positive", "sentiment_score": 0.8, "is_key_danmu": True},
        {"timestamp": 85, "content": "值得购买", "sentiment": "positive", "sentiment_score": 0.7},
    ]


# ==================== 情绪峰值检测测试 ====================

class TestEmotionPeakDetection:
    """情绪峰值检测测试"""
    
    def test_detect_peaks_basic(self, sample_emotion_curve):
        """测试基本峰值检测"""
        service = AttributionAnalysisService()
        peaks = service.detect_emotion_peaks(sample_emotion_curve)
        
        assert len(peaks) > 0
        assert all('timestamp' in p for p in peaks)
        assert all('score' in p for p in peaks)
        assert all('level' in p for p in peaks)
    
    def test_detect_peaks_threshold(self, sample_emotion_curve):
        """测试峰值阈值"""
        service = AttributionAnalysisService()
        peaks = service.detect_emotion_peaks(sample_emotion_curve)
        
        # 所有峰值应该超过阈值
        for peak in peaks:
            assert peak['score'] >= service.emotion_peak_threshold
    
    def test_detect_peaks_empty_curve(self):
        """测试空曲线"""
        service = AttributionAnalysisService()
        peaks = service.detect_emotion_peaks([])
        assert peaks == []
    
    def test_merge_nearby_peaks(self):
        """测试峰值合并"""
        service = AttributionAnalysisService()
        
        nearby_peaks = [
            {'timestamp': 30, 'score': 0.9, 'duration': 10, 'level': 'high'},
            {'timestamp': 35, 'score': 0.85, 'duration': 8, 'level': 'high'},
            {'timestamp': 60, 'score': 0.8, 'duration': 10, 'level': 'high'}
        ]
        
        merged = service._merge_nearby_peaks(nearby_peaks, min_gap=15)
        
        # 前两个峰值应该合并
        assert len(merged) == 2
        assert merged[0]['timestamp'] == 30  # 保留最高分的时间


# ==================== 话术 - 情绪关联测试 ====================

class TestSpeechEmotionCorrelation:
    """话术 - 情绪关联测试"""
    
    def test_correlate_basic(self, sample_speech_segments, sample_emotion_curve):
        """测试基本关联"""
        service = AttributionAnalysisService()
        emotion_peaks = service.detect_emotion_peaks(sample_emotion_curve)
        
        results = service.correlate_speech_with_emotion(
            sample_speech_segments, emotion_peaks, sample_emotion_curve
        )
        
        assert len(results) == len(sample_speech_segments)
        assert all(isinstance(r, AttributionResult) for r in results)
        assert all(hasattr(r, 'emotion_impact') for r in results)
    
    def test_emotion_impact_range(self, sample_speech_segments, sample_emotion_curve):
        """测试情绪影响分数范围"""
        service = AttributionAnalysisService()
        emotion_peaks = service.detect_emotion_peaks(sample_emotion_curve)
        
        results = service.correlate_speech_with_emotion(
            sample_speech_segments, emotion_peaks, sample_emotion_curve
        )
        
        for result in results:
            assert 0 <= result.emotion_impact <= 1


# ==================== 话术 - 弹幕关联测试 ====================

class TestSpeechDanmuCorrelation:
    """话术 - 弹幕关联测试"""
    
    def test_correlation_basic(self, sample_speech_segments, sample_danmu_list):
        """测试基本关联"""
        service = AttributionAnalysisService()
        
        correlation = service.correlate_speech_with_danmu(
            sample_speech_segments, sample_danmu_list
        )
        
        assert len(correlation) == len(sample_speech_segments)
        assert all('total_count' in c for c in correlation.values())
        assert all('engagement_rate' in c for c in correlation.values())
    
    def test_correlation_stats(self, sample_speech_segments, sample_danmu_list):
        """测试关联统计"""
        service = AttributionAnalysisService()
        
        correlation = service.correlate_speech_with_danmu(
            sample_speech_segments, sample_danmu_list
        )
        
        # speech_1 (0-30 秒) 应该有 3 条弹幕 (5s, 15s, 25s)
        assert correlation['speech_1']['total_count'] == 3
        
        # speech_2 (30-60 秒) 应该有 3 条弹幕 (32s, 35s, 45s)
        assert correlation['speech_2']['total_count'] == 3
        
        # speech_3 (60-90 秒) 应该有 3 条弹幕 (65s, 75s, 85s)
        assert correlation['speech_3']['total_count'] == 3


# ==================== 完整归因报告测试 ====================

class TestAttributionReport:
    """归因报告测试"""
    
    def test_generate_report(self, sample_speech_segments, sample_emotion_curve, sample_danmu_list):
        """测试生成完整报告"""
        report = analyze_attribution(
            speech_segments=sample_speech_segments,
            emotion_curve=sample_emotion_curve,
            danmu_list=sample_danmu_list,
            top_n=3
        )
        
        assert 'summary' in report
        assert 'top_speeches' in report
        assert 'emotion_peaks' in report
        assert 'recommendations' in report
    
    def test_report_summary(self, sample_speech_segments, sample_emotion_curve, sample_danmu_list):
        """测试报告摘要"""
        report = analyze_attribution(
            speech_segments=sample_speech_segments,
            emotion_curve=sample_emotion_curve,
            danmu_list=sample_danmu_list
        )
        
        summary = report['summary']
        assert summary['total_speech_segments'] == len(sample_speech_segments)
        assert summary['total_danmus'] == len(sample_danmu_list)
        assert 'analysis_timestamp' in summary
    
    def test_top_speeches_sorting(self, sample_speech_segments, sample_emotion_curve, sample_danmu_list):
        """测试 Top 话术排序"""
        report = analyze_attribution(
            speech_segments=sample_speech_segments,
            emotion_curve=sample_emotion_curve,
            danmu_list=sample_danmu_list,
            top_n=3
        )
        
        top_speeches = report['top_speeches']
        assert len(top_speeches) <= 3
        
        # 验证按综合评分降序排列
        scores = [s['overall_score'] for s in top_speeches]
        assert scores == sorted(scores, reverse=True)
    
    def test_recommendations_generation(self, sample_speech_segments, sample_emotion_curve, sample_danmu_list):
        """测试建议生成"""
        report = analyze_attribution(
            speech_segments=sample_speech_segments,
            emotion_curve=sample_emotion_curve,
            danmu_list=sample_danmu_list
        )
        
        recommendations = report['recommendations']
        assert isinstance(recommendations, list)
        
        # 每个建议应该有基本字段
        for rec in recommendations:
            assert 'type' in rec
            assert 'priority' in rec
            assert 'title' in rec


# ==================== 边界情况测试 ====================

class TestEdgeCases:
    """边界情况测试"""
    
    def test_empty_speech_segments(self, sample_emotion_curve, sample_danmu_list):
        """测试空话术分段"""
        report = analyze_attribution(
            speech_segments=[],
            emotion_curve=sample_emotion_curve,
            danmu_list=sample_danmu_list
        )
        
        assert report['summary']['total_speech_segments'] == 0
        assert report['top_speeches'] == []
    
    def test_empty_danmu_list(self, sample_speech_segments, sample_emotion_curve):
        """测试空弹幕列表"""
        report = analyze_attribution(
            speech_segments=sample_speech_segments,
            emotion_curve=sample_emotion_curve,
            danmu_list=[]
        )
        
        assert report['summary']['total_danmus'] == 0
    
    def test_single_speech(self, sample_emotion_curve, sample_danmu_list):
        """测试单个话术"""
        single_speech = [
            {"id": "s1", "type": "opening", "content": "大家好", "start_time": 0, "end_time": 10}
        ]
        
        report = analyze_attribution(
            speech_segments=single_speech,
            emotion_curve=sample_emotion_curve,
            danmu_list=sample_danmu_list
        )
        
        assert len(report['top_speeches']) == 1


# ==================== 性能测试 ====================

class TestPerformance:
    """性能测试"""
    
    def test_analysis_speed(self, sample_emotion_curve, sample_danmu_list):
        """测试分析速度"""
        import time
        
        # 生成大量话术
        large_speech_segments = [
            {
                "id": f"speech_{i}",
                "type": "opening",
                "content": f"话术内容{i}",
                "start_time": i * 10,
                "end_time": (i + 1) * 10
            }
            for i in range(100)
        ]
        
        start_time = time.time()
        
        report = analyze_attribution(
            speech_segments=large_speech_segments,
            emotion_curve=sample_emotion_curve * 10,  # 扩大 10 倍
            danmu_list=sample_danmu_list * 10,
            top_n=10
        )
        
        elapsed = time.time() - start_time
        
        # 应该在 1 秒内完成
        assert elapsed < 1.0, f"分析耗时{elapsed:.2f}秒，超过 1 秒阈值"
        assert report['summary']['total_speech_segments'] == 100


# ==================== 运行测试 ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
