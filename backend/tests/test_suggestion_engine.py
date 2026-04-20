"""
话术优化建议引擎测试
"""

import pytest
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.suggestion_engine import (
    SuggestionEngine,
    analyze_speech
)


# ==================== 测试数据 ====================

@pytest.fixture
def sample_speech():
    """示例话术"""
    return {
        'id': 'test_speech_1',
        'type': 'price_promotion',
        'content': '这个产品 99 元',
        'start_time': 60,
        'end_time': 70
    }


@pytest.fixture
def good_speech():
    """优秀话术示例"""
    return {
        'id': 'test_speech_2',
        'type': 'price_promotion',
        'content': '平时专柜卖 199 的产品，今天直播间福利价只要 99！立省 100 块！只有今天这个价格！',
        'start_time': 60,
        'end_time': 90
    }


@pytest.fixture
def sample_metrics():
    """示例指标"""
    return {
        'emotion_impact': 0.45,
        'engagement_rate': 15,
        'overall_score': 60
    }


# ==================== 问题诊断测试 ====================

class TestDiagnosis:
    """问题诊断测试"""
    
    def test_diagnose_rhythm_too_short(self, sample_speech):
        """测试节奏诊断 - 话术过短"""
        engine = SuggestionEngine()
        issues = engine.diagnose_speech(sample_speech)
        
        rhythm_issues = [i for i in issues if i.type == 'rhythm']
        assert len(rhythm_issues) > 0
        assert any('过短' in i.title for i in rhythm_issues)
    
    def test_diagnose_rhythm_good(self, good_speech):
        """测试节奏诊断 - 话术时长合适"""
        engine = SuggestionEngine()
        issues = engine.diagnose_speech(good_speech)
        
        rhythm_issues = [i for i in issues if i.type == 'rhythm']
        # 优秀话术不应该有严重的节奏问题
        assert not any(i.severity == 'high' for i in rhythm_issues)
    
    def test_diagnose_emotion_weak(self, sample_speech):
        """测试情感诊断 - 情感表达弱"""
        engine = SuggestionEngine()
        issues = engine.diagnose_speech(sample_speech)
        
        emotion_issues = [i for i in issues if i.type == 'emotion']
        assert len(emotion_issues) > 0
        assert any('平淡' in i.title or '缺少' in i.title for i in emotion_issues)
    
    def test_diagnose_emotion_strong(self, good_speech):
        """测试情感诊断 - 情感表达强"""
        engine = SuggestionEngine()
        issues = engine.diagnose_speech(good_speech)
        
        emotion_issues = [i for i in issues if i.type == 'emotion']
        # 优秀话术情感问题应该较少
        assert len(emotion_issues) <= 1
    
    def test_diagnose_interaction_missing(self, sample_speech):
        """测试互动诊断 - 缺少互动"""
        engine = SuggestionEngine()
        issues = engine.diagnose_speech(sample_speech)
        
        interaction_issues = [i for i in issues if i.type == 'interaction']
        assert len(interaction_issues) > 0
    
    def test_diagnose_with_low_metrics(self, sample_speech, sample_metrics):
        """测试低指标时的诊断"""
        engine = SuggestionEngine()
        issues = engine.diagnose_speech(sample_speech, sample_metrics)
        
        # 应该诊断出更多情绪问题
        emotion_issues = [i for i in issues if i.type == 'emotion']
        assert len(emotion_issues) >= 1


# ==================== 改写生成测试 ====================

class TestRewriteGeneration:
    """改写生成测试"""
    
    def test_generate_rewrite_basic(self, sample_speech):
        """测试基本改写生成"""
        engine = SuggestionEngine()
        issues = engine.diagnose_speech(sample_speech)
        rewrite = engine.generate_rewrite(sample_speech, issues)
        
        assert rewrite is not None
        assert rewrite.before == sample_speech['content']
        assert len(rewrite.after) > len(rewrite.before)
        assert len(rewrite.changes) > 0
    
    def test_generate_rewrite_changes(self, sample_speech):
        """测试改写内容变化"""
        engine = SuggestionEngine()
        issues = engine.diagnose_speech(sample_speech)
        rewrite = engine.generate_rewrite(sample_speech, issues)
        
        # 改写后应该包含情感词或互动元素
        assert (
            any(word in rewrite.after for word in ['超级', '特别', '非常']) or
            '！' in rewrite.after
        )
    
    def test_generate_rewrite_expected_improvement(self, sample_speech):
        """测试预期提升"""
        engine = SuggestionEngine()
        issues = engine.diagnose_speech(sample_speech)
        rewrite = engine.generate_rewrite(sample_speech, issues)
        
        assert rewrite.expected_improvement
        assert len(rewrite.expected_improvement) > 0
    
    def test_no_rewrite_needed(self, good_speech):
        """测试不需要改写的情况"""
        engine = SuggestionEngine()
        issues = engine.diagnose_speech(good_speech)
        
        # 优秀话术的问题应该很少
        assert len(issues) <= 2


# ==================== 优秀案例推荐测试 ====================

class TestExcellentExamples:
    """优秀案例推荐测试"""
    
    def test_recommend_price_promotion(self):
        """测试价格优惠话术推荐"""
        engine = SuggestionEngine()
        examples = engine.recommend_excellent_examples('price_promotion', limit=2)
        
        assert len(examples) <= 2
        assert all(e.speech_type == 'price_promotion' for e in examples)
        assert all(e.score >= 80 for e in examples)
    
    def test_recommend_product_intro(self):
        """测试产品介绍话术推荐"""
        engine = SuggestionEngine()
        examples = engine.recommend_excellent_examples('product_intro', limit=2)
        
        assert len(examples) <= 2
        assert all(e.speech_type == 'product_intro' for e in examples)
    
    def test_recommend_unknown_type(self):
        """测试未知话术类型"""
        engine = SuggestionEngine()
        examples = engine.recommend_excellent_examples('unknown_type', limit=2)
        
        # 未知类型应该返回空列表
        assert len(examples) == 0


# ==================== 完整分析测试 ====================

class TestCompleteAnalysis:
    """完整分析测试"""
    
    def test_analyze_speech_basic(self, sample_speech):
        """测试基本分析"""
        result = analyze_speech(sample_speech)
        
        assert 'issues' in result
        assert 'suggestions' in result
        assert 'rewrite_example' in result
    
    def test_analyze_speech_issues_count(self, sample_speech):
        """测试问题数量"""
        result = analyze_speech(sample_speech)
        
        # 差的话术应该有多个问题
        assert len(result['issues']) >= 3
    
    def test_analyze_speech_suggestions_priority(self, sample_speech):
        """测试建议优先级"""
        result = analyze_speech(sample_speech)
        
        # 应该有高优先级建议
        high_priority = [s for s in result['suggestions'] if s.get('priority') == 'high']
        assert len(high_priority) > 0
    
    def test_analyze_speech_with_metrics(self, sample_speech, sample_metrics):
        """测试带指标的分析"""
        result = analyze_speech(sample_speech, sample_metrics)
        
        # 带低指标应该诊断出更多问题
        assert len(result['issues']) >= 4
    
    def test_analyze_good_speech(self, good_speech):
        """测试优秀话术分析"""
        result = analyze_speech(good_speech)
        
        # 优秀话术问题应该少很多
        assert len(result['issues']) <= 2


# ==================== 边界情况测试 ====================

class TestEdgeCases:
    """边界情况测试"""
    
    def test_empty_content(self):
        """测试空内容"""
        speech = {
            'id': 'empty',
            'type': 'opening',
            'content': '',
            'start_time': 0,
            'end_time': 0
        }
        
        result = analyze_speech(speech)
        
        # 应该诊断出内容过于简单的问题
        assert len(result['issues']) > 0
        assert any('简单' in i['title'] or '过短' in i['title'] for i in result['issues'])
    
    def test_very_long_speech(self):
        """测试超长话术"""
        speech = {
            'id': 'long',
            'type': 'product_intro',
            'content': '这个产品很好 ' * 100,
            'start_time': 0,
            'end_time': 600  # 10 分钟
        }
        
        result = analyze_speech(speech)
        
        # 应该诊断出话术过长的问题
        assert any('过长' in i['title'] for i in result['issues'])
    
    def test_unknown_speech_type(self, sample_speech):
        """测试未知话术类型"""
        speech = sample_speech.copy()
        speech['type'] = 'unknown_type'
        
        result = analyze_speech(speech)
        
        # 不应该报错，但建议可能较少
        assert 'issues' in result
        assert 'suggestions' in result


# ==================== 性能测试 ====================

class TestPerformance:
    """性能测试"""
    
    def test_analysis_speed(self, sample_speech):
        """测试分析速度"""
        import time
        
        start = time.time()
        
        # 分析 100 次
        for _ in range(100):
            analyze_speech(sample_speech)
        
        elapsed = time.time() - start
        
        # 每次分析应该 < 10ms
        assert elapsed < 1.0, f"100 次分析耗时{elapsed:.2f}秒"


# ==================== 运行测试 ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
