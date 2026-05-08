"""弹幕情感分析引擎测试"""

import pytest
import sys
import os

# 使用 SQLite 内存数据库测试
os.environ["DATABASE_URL"] = "sqlite://"

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.danmu_analyzer import (
    _classify_sentiment,
    _compute_emotion_curve,
    _extract_keywords,
    _compute_metrics,
    _find_highlights,
    _parse_time_to_seconds,
)


# ── 情感分类测试 ──────────────────────────────────────────────

class TestClassifySentiment:
    def test_positive_keywords(self):
        assert _classify_sentiment("好看！")[0] == "positive"
        assert _classify_sentiment("太厉害了")[0] == "positive"
        assert _classify_sentiment("666")[0] == "positive"
        assert _classify_sentiment("yyds")[0] == "positive"

    def test_negative_keywords(self):
        assert _classify_sentiment("垃圾")[0] == "negative"
        assert _classify_sentiment("太无聊了")[0] == "negative"
        assert _classify_sentiment("差评")[0] == "negative"

    def test_neutral(self):
        assert _classify_sentiment("今天天气怎么样")[0] == "neutral"
        assert _classify_sentiment("嗯")[0] == "neutral"

    def test_mixed_sentiment(self):
        sentiment, score = _classify_sentiment("好看但是太贵了")
        assert sentiment in ("positive", "negative", "neutral")
        assert -1.0 <= score <= 1.0

    def test_question_detected(self):
        sentiment, score = _classify_sentiment("怎么买？")
        assert sentiment == "neutral"

    def test_score_range(self):
        for text in ["爱了爱了爱了", "垃圾垃圾", "普通弹幕"]:
            _, score = _classify_sentiment(text)
            assert -1.0 <= score <= 1.0


# ── 情感曲线测试 ──────────────────────────────────────────────

class FakeDanmu:
    """模拟 Danmu 对象"""
    def __init__(self, timestamp: float, content: str, sentiment: str = "neutral", sentiment_score: float = 0.0):
        self.timestamp = timestamp
        self.content = content
        self.sentiment = sentiment
        self.sentiment_score = sentiment_score


class TestEmotionCurve:
    def test_empty(self):
        assert _compute_emotion_curve([]) == []

    def test_single_window(self):
        danmus = [
            FakeDanmu(0.0, "a", "positive", 0.8),
            FakeDanmu(5.0, "b", "negative", -0.5),
        ]
        curve = _compute_emotion_curve(danmus, window_seconds=10.0)
        assert len(curve) == 1
        assert curve[0]["count"] == 2

    def test_multiple_windows(self):
        danmus = [
            FakeDanmu(0.0, "a", "positive", 0.8),
            FakeDanmu(15.0, "b", "negative", -0.5),
            FakeDanmu(25.0, "c", "neutral", 0.0),
        ]
        curve = _compute_emotion_curve(danmus, window_seconds=10.0)
        assert len(curve) >= 2


# ── 关键词提取测试 ────────────────────────────────────────────

class TestKeywords:
    def test_basic_extraction(self):
        danmus = [
            FakeDanmu(0.0, "这个产品真的好看"),
            FakeDanmu(1.0, "好看好看太好看了"),
            FakeDanmu(2.0, "质量不错"),
        ]
        keywords = _extract_keywords(danmus, top_n=10)
        assert len(keywords) > 0
        assert all("word" in k and "count" in k for k in keywords)

    def test_stop_words_filtered(self):
        danmus = [FakeDanmu(0.0, "的了在是我")]
        keywords = _extract_keywords(danmus, top_n=10)
        words = [k["word"] for k in keywords]
        assert "的" not in words


# ── 互动指标测试 ──────────────────────────────────────────────

class TestMetrics:
    def test_empty(self):
        m = _compute_metrics([], 100.0)
        assert m["danmu_density"] == 0.0

    def test_density(self):
        danmus = [FakeDanmu(i, "text") for i in range(10)]
        m = _compute_metrics(danmus, 60.0)
        assert m["danmu_density"] == 10.0

    def test_distribution(self):
        danmus = [
            FakeDanmu(0, "a", "positive", 0.5),
            FakeDanmu(1, "b", "negative", -0.5),
            FakeDanmu(2, "c", "neutral", 0.0),
        ]
        m = _compute_metrics(danmus, 10.0)
        dist = m["sentiment_distribution"]
        assert abs(dist["positive"] - 1 / 3) < 0.01


# ── 高光时刻测试 ──────────────────────────────────────────────

class TestHighlights:
    def test_empty(self):
        assert _find_highlights([]) == []

    def test_top_n(self):
        danmus = [FakeDanmu(i, "text") for i in range(30)]
        highlights = _find_highlights(danmus, window_seconds=10.0, top_n=3)
        assert len(highlights) <= 3


# ── 时间解析测试 ──────────────────────────────────────────────

class TestParseTime:
    def test_float(self):
        assert _parse_time_to_seconds(10.5) == 10.5

    def test_hhmmss(self):
        assert _parse_time_to_seconds("01:30:00") == 5400.0

    def test_mmss(self):
        assert _parse_time_to_seconds("02:30") == 150.0

    def test_invalid(self):
        assert _parse_time_to_seconds("abc") == 0.0
