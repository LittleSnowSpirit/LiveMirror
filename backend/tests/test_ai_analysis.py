"""Tests for the AI analysis module: prompts, report generator, and analyzer."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure backend package is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from ai_analysis.prompts import (
    FULL_ANALYSIS_PROMPT,
    SYSTEM_ROLE,
    get_prompt,
)
from ai_analysis.report_generator import ReportGenerator, create_report_generator
from ai_analysis.analyzer import LiveMirrorAnalyzer, create_analyzer
from ai_analysis.classifiers import KeywordClassifier, RuleBasedAnalyzer
from ai_analysis.suggester import OptimizationSuggester


# ---------------------------------------------------------------------------
# Prompt templates
# ---------------------------------------------------------------------------


class TestPrompts:
    def test_system_role_includes_new_capabilities(self):
        assert "隐性问题" in SYSTEM_ROLE
        assert "节奏失控" in SYSTEM_ROLE
        assert "互动密度" in SYSTEM_ROLE

    def test_full_analysis_prompt_includes_new_dimensions(self):
        assert "节奏分析" in FULL_ANALYSIS_PROMPT
        assert "互动密度" in FULL_ANALYSIS_PROMPT
        assert "话术多样性" in FULL_ANALYSIS_PROMPT
        assert "情绪曲线" in FULL_ANALYSIS_PROMPT
        assert "rhythm_analysis" in FULL_ANALYSIS_PROMPT
        assert "engagement_metrics" in FULL_ANALYSIS_PROMPT
        assert "emotion_curve" in FULL_ANALYSIS_PROMPT
        assert "speech_diversity" in FULL_ANALYSIS_PROMPT

    def test_get_prompt_fills_variables(self):
        filled = get_prompt(
            "full_analysis",
            transcript="测试转写稿",
            data_changes="无",
        )
        assert "测试转写稿" in filled
        assert "无" in filled

    def test_get_prompt_unknown_template_raises(self):
        with pytest.raises(ValueError, match="Unknown template"):
            get_prompt("nonexistent_template")

    def test_all_templates_are_registered(self):
        for name in ("segmentation", "highlight_detection", "crash_detection",
                      "attribution", "suggestion", "full_analysis"):
            result = get_prompt(name, transcript="x", data_changes="x", segments="x",
                                analysis_results="x", crashes="x")
            assert isinstance(result, str)


# ---------------------------------------------------------------------------
# ReportGenerator
# ---------------------------------------------------------------------------


class TestReportGenerator:
    def setup_method(self):
        self.gen = ReportGenerator(model_version="v2.0", api_model="test-model")

    def test_generate_report_basic(self):
        segments = [
            {"segment_id": 1, "start_time": "00:00:00", "end_time": "00:00:45", "content": "开场"},
        ]
        highlights = [
            {"segment_id": 1, "type": "促单话术", "effectiveness_score": 8},
        ]
        crashes = [
            {"segment_id": 1, "type": "敏感词", "severity": "medium", "risk_level": 5},
        ]
        report = self.gen.generate_report(segments, highlights, crashes)

        assert "metadata" in report
        assert "summary" in report
        assert report["summary"]["total_highlights"] == 1
        assert report["summary"]["total_crashes"] == 1
        assert report["metadata"]["model_version"] == "v2.0"

    def test_generate_report_with_new_dimensions(self):
        rhythm = {"score": 80, "overall_rating": "良好", "phases": [], "issues": [], "suggestions": []}
        engagement = {"score": 72, "interactions_per_minute": 2.5, "rating": "良好"}
        emotion = {"score": 78, "overall_trend": "逐步升温"}
        diversity = {"score": 65, "vocabulary_richness": "一般", "repeated_phrases": []}

        report = self.gen.generate_report(
            segments=[],
            highlights=[],
            crashes=[],
            rhythm_analysis=rhythm,
            engagement_metrics=engagement,
            emotion_curve=emotion,
            speech_diversity=diversity,
        )

        assert "rhythm_analysis" in report
        assert "engagement_metrics" in report
        assert "emotion_curve" in report
        assert "speech_diversity" in report
        assert report["rhythm_analysis"]["score"] == 80

    def test_overall_score_with_dimensions(self):
        """Score should be higher when dimension scores are included."""
        # Baseline: no dimensions
        score_no_dim = self.gen._calculate_overall_score(5, 2, 0)

        # With dimensions
        score_with_dim = self.gen._calculate_overall_score(
            5, 2, 0,
            rhythm_analysis={"score": 80},
            engagement_metrics={"score": 75},
            emotion_curve={"score": 70},
            speech_diversity={"score": 65},
        )
        assert score_with_dim > score_no_dim

    def test_overall_score_bounded_0_100(self):
        # Many crashes -> score shouldn't go below 0
        score = self.gen._calculate_overall_score(0, 50, 50)
        assert 0 <= score <= 100

        # Many highlights + good dimensions -> score shouldn't exceed 100
        score = self.gen._calculate_overall_score(
            100, 0, 0,
            rhythm_analysis={"score": 100},
            engagement_metrics={"score": 100},
            emotion_curve={"score": 100},
            speech_diversity={"score": 100},
        )
        assert 0 <= score <= 100

    def test_key_insights_with_new_dimensions(self):
        insights = self.gen._generate_key_insights(
            highlights=[{"type": "促单话术"}],
            crashes=[],
            total_highlights=1,
            total_crashes=0,
            critical_crashes=0,
            rhythm_analysis={"score": 50, "overall_rating": "较差"},
            engagement_metrics={"interactions_per_minute": 0.5, "score": 40, "rating": "不足", "dead_zones": [{"start": "10:00"}]},
            emotion_curve={"overall_trend": "高开低走", "score": 55},
            speech_diversity={"score": 45, "vocabulary_richness": "单一", "repeated_phrases": [{"phrase": "test"}]},
        )
        assert len(insights) >= 4
        # Check rhythm insight present
        assert any("节奏" in i for i in insights)
        # Check engagement insight
        assert any("互动" in i for i in insights)
        # Check emotion insight
        assert any("情绪" in i for i in insights)
        # Check diversity insight
        assert any("话术" in i for i in insights)

    def test_generate_detailed_sections(self):
        report = {
            "summary": {"overall_score": 75, "total_highlights": 5, "total_crashes": 2, "critical_crashes": 0},
            "rhythm_analysis": {
                "score": 80,
                "overall_rating": "良好",
                "phases": [
                    {"phase": "开场", "start_time": "00:00", "end_time": "03:00", "proportion": "10%", "evaluation": "不错"},
                ],
                "issues": [], "suggestions": [],
            },
            "engagement_metrics": {
                "score": 70, "rating": "良好", "interactions_per_minute": 2.0,
                "total_interactions": 60, "interaction_types": {"question_prompts": 20},
                "dead_zones": [],
            },
            "emotion_curve": {
                "score": 75, "overall_trend": "逐步升温",
                "peak_moments": ["00:15:00"], "low_moments": [],
            },
            "speech_diversity": {
                "score": 60, "vocabulary_richness": "一般",
                "repeated_phrases": [{"phrase": "赶紧下单", "count": 3}],
                "suggestions": ["丰富话术"],
            },
        }
        sections = self.gen.generate_detailed_sections(report)
        titles = [s["title"] for s in sections]
        assert "核心指标" in titles
        assert "节奏分析" in titles
        assert "互动分析" in titles
        assert "情绪分析" in titles
        assert "话术多样性" in titles
        # Each section has score and level
        for section in sections:
            assert "score" in section
            assert "level" in section
            assert section["level"] in ("excellent", "good", "average", "poor")

    def test_score_level_mapping(self):
        assert ReportGenerator._score_level(90) == "excellent"
        assert ReportGenerator._score_level(75) == "good"
        assert ReportGenerator._score_level(55) == "average"
        assert ReportGenerator._score_level(30) == "poor"

    def test_executive_summary_includes_new_sections(self):
        report = {
            "metadata": {"analysis_time": "2024-01-01", "total_duration": "30:00", "total_segments": 10},
            "summary": {"overall_score": 75, "total_highlights": 5, "total_crashes": 2, "critical_crashes": 0, "key_insights": ["insight 1"]},
            "rhythm_analysis": {"score": 80, "overall_rating": "良好", "phases": [{"phase": "开场", "proportion": "10%", "evaluation": "ok"}]},
            "engagement_metrics": {"score": 70, "rating": "良好", "interactions_per_minute": 2.0},
            "emotion_curve": {"score": 75, "overall_trend": "升温"},
            "speech_diversity": {"score": 60, "vocabulary_richness": "一般"},
        }
        summary = self.gen.generate_executive_summary(report)
        assert "节奏分析" in summary
        assert "互动指标" in summary
        assert "情绪曲线" in summary
        assert "话术多样性" in summary

    def test_factory_function(self):
        gen = create_report_generator(model_version="v2.0", api_model="qwen-plus")
        assert gen.model_version == "v2.0"
        assert gen.api_model == "qwen-plus"


# ---------------------------------------------------------------------------
# Analyzer
# ---------------------------------------------------------------------------


class TestAnalyzer:
    def test_detect_backend_deepseek(self):
        assert LiveMirrorAnalyzer._detect_backend("deepseek-chat") == "deepseek"
        assert LiveMirrorAnalyzer._detect_backend("deepseek-coder") == "deepseek"

    def test_detect_backend_gpt(self):
        assert LiveMirrorAnalyzer._detect_backend("gpt-4") == "gpt"
        assert LiveMirrorAnalyzer._detect_backend("gpt-3.5-turbo") == "gpt"

    def test_detect_backend_dashscope(self):
        assert LiveMirrorAnalyzer._detect_backend("qwen-plus") == "dashscope"
        assert LiveMirrorAnalyzer._detect_backend("qwen-turbo") == "dashscope"
        assert LiveMirrorAnalyzer._detect_backend("dashscope-chat") == "dashscope"

    def test_init_dashscope_backend(self):
        analyzer = LiveMirrorAnalyzer(api_key="test-key", model="qwen-plus")
        assert analyzer._backend == "dashscope"

    def test_segment_transcript_with_timestamps(self):
        analyzer = create_analyzer(api_key=None, model="deepseek-chat", cost_optimization=False)
        transcript = (
            "00:00:00 大家好欢迎来到直播间，今天给大家带来超级好用的产品推荐\n"
            "00:00:30 今天给大家推荐的这款好物性价比非常高，值得入手\n"
            "00:01:00 这款产品我自己也在用，效果非常好推荐给大家\n"
        )
        segments = analyzer._segment_transcript(transcript)
        assert len(segments) == 3
        assert segments[0]["start_time"] == "00:00:00"
        assert segments[1]["start_time"] == "00:00:30"

    def test_segment_transcript_without_timestamps(self):
        analyzer = create_analyzer(api_key=None, model="deepseek-chat", cost_optimization=False)
        # Long enough text to produce at least one segment
        transcript = "这是一段没有时间戳的直播转写稿。" * 30
        segments = analyzer._segment_transcript(transcript, segment_duration=45)
        assert len(segments) >= 1
        assert segments[0]["start_time"] == "00:00:00"

    def test_analyze_with_mock_api_returns_full_report(self):
        """Test that analyze() produces a report with new dimensions when API returns them."""
        analyzer = create_analyzer(api_key="fake-key", model="deepseek-chat", cost_optimization=False)

        mock_api_result = {
            "segments": [
                {"segment_id": 1, "start_time": "00:00:00", "end_time": "00:00:45",
                 "content": "测试内容", "word_count": 4, "speech_type": "产品介绍",
                 "is_highlight": False, "is_crash": False}
            ],
            "highlights": [
                {"segment_id": 1, "timestamp": "00:00:30", "type": "促单话术",
                 "original_text": "测试内容", "effectiveness_score": 8, "analysis": "test"}
            ],
            "crashes": [],
            "rhythm_analysis": {
                "overall_rating": "良好", "score": 80,
                "phases": [{"phase": "开场", "start_time": "00:00", "end_time": "05:00",
                            "proportion": "10%", "evaluation": "不错"}],
                "issues": [], "suggestions": [],
            },
            "engagement_metrics": {
                "interactions_per_minute": 2.0, "total_interactions": 60,
                "interaction_types": {"question_prompts": 20},
                "rating": "良好", "score": 72, "dead_zones": [],
            },
            "emotion_curve": {
                "overall_trend": "逐步升温", "score": 78,
                "phases": [], "peak_moments": [], "low_moments": [],
            },
            "speech_diversity": {
                "score": 65, "repeated_phrases": [],
                "vocabulary_richness": "一般", "suggestions": [],
            },
            "attributions": [],
            "suggestions": [],
            "summary": {
                "total_highlights": 1, "total_crashes": 0,
                "critical_crashes": 0, "overall_score": 85,
                "key_insights": ["test insight"],
            },
        }

        transcript = "00:00:00 " + "这是一段测试直播转写稿。" * 10

        with patch.object(analyzer, "_call_ai_api", return_value=mock_api_result):
            report = analyzer.analyze(transcript)

        assert "rhythm_analysis" in report
        assert "engagement_metrics" in report
        assert "emotion_curve" in report
        assert "speech_diversity" in report
        assert report["rhythm_analysis"]["score"] == 80
        assert report["summary"]["overall_score"] > 0

    def test_analyze_graceful_api_failure(self):
        """When API returns None, rule-based analysis kicks in."""
        analyzer = create_analyzer(api_key="fake-key", model="deepseek-chat", cost_optimization=True)

        transcript = "00:00:00 " + "赶紧下单，最便宜的" * 10

        with patch.object(analyzer, "_call_ai_api", return_value=None):
            report = analyzer.analyze(transcript)

        # Should still produce a report with at least rule-based highlights/crashes
        assert "summary" in report
        assert report["summary"]["total_highlights"] >= 0


# ---------------------------------------------------------------------------
# KeywordClassifier (sanity)
# ---------------------------------------------------------------------------


class TestKeywordClassifier:
    def test_detects_promotion_keywords(self):
        clf = KeywordClassifier()
        types = clf.classify_speech_type("想要的赶紧扣 1，手慢无！")
        from ai_analysis.classifiers import SpeechType
        assert SpeechType.PROMOTION in types

    def test_detects_sensitive_words(self):
        clf = KeywordClassifier()
        crashes = clf.detect_crashes("这是全网最好的产品，绝对有效！")
        from ai_analysis.classifiers import CrashType
        assert CrashType.SENSITIVE_WORD in crashes or CrashType.OVER_PROMISE in crashes


# ---------------------------------------------------------------------------
# OptimizationSuggester (sanity)
# ---------------------------------------------------------------------------


class TestSuggester:
    def test_generate_suggestions_returns_versions(self):
        suggester = OptimizationSuggester()
        crash = {"segment_id": 1, "original_text": "这是全网最便宜的", "type": "敏感词"}
        suggestion = suggester.generate_suggestions(crash)
        assert len(suggestion.suggestions) == 3
        assert suggestion.suggestions[0].version == "A"
