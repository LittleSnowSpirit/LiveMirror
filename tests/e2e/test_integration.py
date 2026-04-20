"""
LiveMirror 端到端集成测试

测试完整业务流程：
1. 归因分析完整流程
2. 建议生成完整流程
3. 趋势分析完整流程
4. 跨功能数据流测试
"""

import pytest
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.attribution import analyze_attribution
from backend.services.suggestion_engine import analyze_speech, SuggestionEngine
from backend.services.trend_analysis import TrendAnalysisService, SessionMetrics, analyze_growth


# ==================== 测试数据准备 ====================

@pytest.fixture
def sample_speech_segments():
    """示例话术分段数据"""
    return [
        {
            "id": f"speech_{i}",
            "type": speech_type,
            "content": content,
            "start_time": i * 30,
            "end_time": (i + 1) * 30
        }
        for i, (speech_type, content) in enumerate([
            ("opening", "欢迎大家来到直播间，今天给大家带来超值好物！"),
            ("product_intro", "这款产品我亲自用了一个月，效果真的很好"),
            ("price_promotion", "平时专柜卖 199，今天直播间只要 99 元！"),
            ("limited_offer", "只剩最后 100 单了！抢完就没有了！"),
            ("closing", "赶紧下单吧！不要犹豫了！")
        ])
    ]


@pytest.fixture
def sample_emotion_curve():
    """示例情绪曲线数据"""
    return [
        {
            "timestamp": i * 5,
            "score": 0.5 + 0.4 * (i % 5) / 4,
            "level": "medium"
        }
        for i in range(30)
    ]


@pytest.fixture
def sample_danmu_list():
    """示例弹幕数据"""
    return [
        {
            "timestamp": i * 5,
            "content": f"弹幕内容{i}",
            "sentiment": "positive" if i % 3 == 0 else ("negative" if i % 3 == 2 else "neutral"),
            "sentiment_score": 0.5 if i % 3 == 0 else (-0.3 if i % 3 == 2 else 0),
            "is_key_danmu": i % 10 == 0
        }
        for i in range(100)
    ]


@pytest.fixture
def sample_sessions():
    """示例场次数据"""
    return [
        SessionMetrics(
            session_id=f"session_{i}",
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


# ==================== 场景 1：归因分析完整流程 ====================

class TestAttributionFullFlow:
    """归因分析完整流程测试"""
    
    def test_attribution_basic_flow(self, sample_speech_segments, sample_emotion_curve, sample_danmu_list):
        """测试基本归因分析流程"""
        # 执行归因分析
        result = analyze_attribution(
            speech_segments=sample_speech_segments,
            emotion_curve=sample_emotion_curve,
            danmu_list=sample_danmu_list,
            top_n=5
        )
        
        # 验证结果结构
        assert "summary" in result
        assert "top_speeches" in result
        assert "emotion_peaks" in result
        assert "recommendations" in result
        
        # 验证数据正确性
        assert result["summary"]["total_speech_segments"] == len(sample_speech_segments)
        assert result["summary"]["total_danmus"] == len(sample_danmu_list)
        assert len(result["top_speeches"]) <= 5
    
    def test_attribution_with_peaks(self, sample_speech_segments, sample_emotion_curve, sample_danmu_list):
        """测试带峰值的归因分析"""
        result = analyze_attribution(
            speech_segments=sample_speech_segments,
            emotion_curve=sample_emotion_curve,
            danmu_list=sample_danmu_list
        )
        
        # 应该有检测到峰值
        assert len(result["emotion_peaks"]) > 0
        
        # 峰值应该有正确的字段
        for peak in result["emotion_peaks"]:
            assert "timestamp" in peak
            assert "score" in peak
            assert "level" in peak
    
    def test_attribution_export_simulation(self, sample_speech_segments, sample_emotion_curve, sample_danmu_list):
        """模拟报告导出流程"""
        result = analyze_attribution(
            speech_segments=sample_speech_segments,
            emotion_curve=sample_emotion_curve,
            danmu_list=sample_danmu_list
        )
        
        # 模拟 JSON 导出
        json_str = json.dumps(result, ensure_ascii=False, indent=2)
        assert len(json_str) > 1000
        
        # 模拟 Markdown 导出
        md_content = self._generate_markdown_report(result)
        assert "归因分析报告" in md_content
        assert "Top" in md_content
        
    def _generate_markdown_report(self, result: dict) -> str:
        """生成 Markdown 报告（模拟）"""
        md = "# 归因分析报告\n\n"
        md += f"总话术数：{result['summary']['total_speech_segments']}\n"
        md += f"情绪峰值数：{result['summary']['emotion_peaks_count']}\n\n"
        md += "## Top 话术\n\n"
        for speech in result["top_speeches"]:
            md += f"- {speech['speech_type']}: {speech['overall_score']}分\n"
        return md


# ==================== 场景 2：建议生成完整流程 ====================

class TestSuggestionFullFlow:
    """建议生成完整流程测试"""
    
    def test_suggestion_diagnose_flow(self):
        """测试问题诊断流程"""
        speech = {
            "id": "test_1",
            "type": "price_promotion",
            "content": "这个产品 99 元",
            "start_time": 60,
            "end_time": 70
        }
        
        result = analyze_speech(speech)
        
        # 验证诊断结果
        assert "issues" in result
        assert "suggestions" in result
        assert "rewrite_example" in result
        
        # 应该诊断出问题
        assert len(result["issues"]) > 0
    
    def test_suggestion_rewrite_flow(self):
        """测试改写示例生成流程"""
        speech = {
            "id": "test_2",
            "type": "price_promotion",
            "content": "这个产品 99 元",
            "start_time": 60,
            "end_time": 70
        }
        
        result = analyze_speech(speech)
        
        # 验证改写示例
        assert result["rewrite_example"] is not None
        assert result["rewrite_example"]["before"] == speech["content"]
        assert len(result["rewrite_example"]["after"]) > len(speech["content"])
        assert len(result["rewrite_example"]["changes"]) > 0
    
    def test_suggestion_copy_function(self):
        """测试复制功能（模拟）"""
        speech = {
            "id": "test_3",
            "type": "price_promotion",
            "content": "这个产品 99 元",
            "start_time": 60,
            "end_time": 70
        }
        
        result = analyze_speech(speech)
        
        # 模拟复制
        after_content = result["rewrite_example"]["after"]
        assert isinstance(after_content, str)
        assert len(after_content) > 0
        
        # 验证内容可复制（无特殊字符）
        assert after_content.encode('utf-8')
    
    def test_suggestion_with_metrics(self):
        """测试带指标的建议生成"""
        speech = {
            "id": "test_4",
            "type": "price_promotion",
            "content": "这个产品 99 元",
            "start_time": 60,
            "end_time": 70
        }
        
        metrics = {
            "emotion_impact": 0.3,
            "engagement_rate": 10,
            "overall_score": 50
        }
        
        result = analyze_speech(speech, metrics)
        
        # 低指标应该诊断出更多问题
        assert len(result["issues"]) >= 3


# ==================== 场景 3：趋势分析完整流程 ====================

class TestTrendAnalysisFullFlow:
    """趋势分析完整流程测试"""
    
    def test_trend_multi_session(self, sample_sessions):
        """测试多场次趋势分析"""
        service = TrendAnalysisService()
        
        # 情绪趋势
        emotion_result = service.analyze_emotion_trend(sample_sessions)
        assert "avg_emotion" in emotion_result
        assert "peak_emotion" in emotion_result
        
        # 话术趋势
        speech_result = service.analyze_speech_quality_trend(sample_sessions)
        assert "by_type" in speech_result
        
        # 互动趋势
        engagement_result = service.analyze_engagement_trend(sample_sessions)
        assert "engagement_rate" in engagement_result
    
    def test_trend_growth_report(self, sample_sessions):
        """测试成长报告生成"""
        service = TrendAnalysisService()
        report = service.generate_growth_report(sample_sessions)
        
        # 验证报告结构
        assert report.period_start is not None
        assert report.period_end is not None
        assert report.total_sessions == 5
        assert report.overall_trend is not None
        assert report.summary is not None
        assert len(report.recommendations) > 0
    
    def test_trend_export_simulation(self, sample_sessions):
        """模拟趋势报告导出"""
        result = analyze_growth(sample_sessions)
        
        # 处理 datetime 序列化
        result_for_json = result.copy()
        if result_for_json.get('period_start'):
            result_for_json['period_start'] = result_for_json['period_start'].isoformat()
        if result_for_json.get('period_end'):
            result_for_json['period_end'] = result_for_json['period_end'].isoformat()
        
        # 模拟 JSON 导出
        json_str = json.dumps(result_for_json, ensure_ascii=False, indent=2)
        assert len(json_str) > 2000
        
        # 验证关键字段
        assert "overall_trend" in result
        assert "top_improvements" in result
        assert "recommendations" in result


# ==================== 场景 4：跨功能数据流测试 ====================

class TestDataFlowIntegration:
    """跨功能数据流测试"""
    
    def test_data_flow_attribution_to_suggestion(self, sample_speech_segments, sample_emotion_curve, sample_danmu_list):
        """测试归因分析到建议生成的数据流"""
        # 1. 执行归因分析
        attribution_result = analyze_attribution(
            speech_segments=sample_speech_segments,
            emotion_curve=sample_emotion_curve,
            danmu_list=sample_danmu_list
        )
        
        # 2. 从归因结果中提取话术
        top_speech = attribution_result["top_speeches"][0]
        
        # 3. 将话术传递给建议生成
        speech_for_suggestion = {
            "id": top_speech["speech_id"],
            "type": top_speech["speech_type"],
            "content": top_speech["speech_content"],
            "start_time": top_speech["start_time"],
            "end_time": top_speech["end_time"]
        }
        
        metrics = {
            "emotion_impact": top_speech["emotion_impact"],
            "engagement_impact": top_speech["engagement_impact"],
            "overall_score": top_speech["overall_score"]
        }
        
        # 4. 生成建议
        suggestion_result = analyze_speech(speech_for_suggestion, metrics)
        
        # 5. 验证数据流正确
        assert suggestion_result is not None
        assert "issues" in suggestion_result
        assert "suggestions" in suggestion_result
    
    def test_data_flow_to_trend_analysis(self, sample_sessions):
        """测试到趋势分析的数据流"""
        service = TrendAnalysisService()
        
        # 1. 分析情绪趋势
        emotion_result = service.analyze_emotion_trend(sample_sessions)
        
        # 2. 分析话术趋势
        speech_result = service.analyze_speech_quality_trend(sample_sessions)
        
        # 3. 生成成长报告（整合所有数据）
        report = service.generate_growth_report(sample_sessions)
        
        # 4. 验证数据一致性
        assert report.emotion_trend is not None
        assert report.total_sessions == len(sample_sessions)


# ==================== 场景 5：API 集成测试 ====================

class TestAPIIntegration:
    """API 集成测试（模拟）"""
    
    def test_all_api_endpoints_structure(self):
        """测试所有 API 端点结构"""
        # 验证 API 路由文件存在
        api_files = [
            "backend/routes/attribution.py",
            "backend/routes/suggestions.py",
            "backend/routes/trends.py"
        ]
        
        for file_path in api_files:
            full_path = Path(__file__).parent.parent.parent / file_path
            assert full_path.exists(), f"API 文件不存在：{file_path}"
    
    def test_api_error_handling(self):
        """测试 API 错误处理"""
        # 测试空数据
        result = analyze_attribution(
            speech_segments=[],
            emotion_curve=[],
            danmu_list=[]
        )
        
        # 应该能处理空数据
        assert result is not None
        assert result["summary"]["total_speech_segments"] == 0
    
    def test_api_response_format(self, sample_speech_segments, sample_emotion_curve, sample_danmu_list):
        """测试 API 响应格式"""
        result = analyze_attribution(
            speech_segments=sample_speech_segments,
            emotion_curve=sample_emotion_curve,
            danmu_list=sample_danmu_list
        )
        
        # 验证响应格式
        assert isinstance(result, dict)
        assert "summary" in result
        assert isinstance(result["summary"], dict)
        assert "top_speeches" in result
        assert isinstance(result["top_speeches"], list)


# ==================== 性能测试 ====================

class TestPerformanceIntegration:
    """集成性能测试"""
    
    def test_full_flow_performance(self, sample_speech_segments, sample_emotion_curve, sample_danmu_list):
        """测试完整流程性能"""
        import time
        
        start = time.time()
        
        # 1. 归因分析
        attribution_result = analyze_attribution(
            speech_segments=sample_speech_segments,
            emotion_curve=sample_emotion_curve,
            danmu_list=sample_danmu_list
        )
        
        # 2. 建议生成
        for speech in sample_speech_segments[:3]:
            analyze_speech(speech)
        
        # 3. 趋势分析
        service = TrendAnalysisService()
        sessions = [
            SessionMetrics(
                session_id=f"s{i}",
                anchor_time=datetime(2026, 4, i+1),
                duration_minutes=120,
                viewer_count=1000,
                danmu_count=500,
                avg_emotion_score=0.7,
                peak_emotion_score=0.85,
                engagement_rate=25,
                overall_score=75
            )
            for i in range(5)
        ]
        service.generate_growth_report(sessions)
        
        elapsed = time.time() - start
        
        # 完整流程应该在 2 秒内完成
        assert elapsed < 2.0, f"完整流程耗时{elapsed:.2f}秒，超过 2 秒阈值"


# ==================== 运行测试 ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
