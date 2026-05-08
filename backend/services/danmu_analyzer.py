"""
弹幕情感分析引擎

核心功能：
1. 情感分类 — 关键词规则为主，AI 为辅
2. 情感曲线 — 按时间窗口聚合
3. 关键词提取 — jieba 分词 + Counter 统计词频
4. 互动指标 — 密度、波动、高光时刻
5. 话术-弹幕关联分析
"""

from __future__ import annotations

import logging
import math
import re
from collections import Counter
from typing import Any

from sqlalchemy.orm import Session

from models import AnalysisReport, Danmu, DanmuBatch

logger = logging.getLogger(__name__)

# ── 情感关键词词典 ──────────────────────────────────────────────

POSITIVE_WORDS: set[str] = {
    "好看", "厉害", "666", "太强了", "牛逼", "牛批", "爱了", "加油",
    "漂亮", "绝了", "神了", "nb", "yyds", "冲", "买它", "下单",
    "喜欢", "棒", "赞", "优秀", "完美", "惊艳", "舒服", "开心",
    "好听", "真香", "良心", "划算", "值", "可以的", "不错", "支持",
    "顶", "稳", "牛", "太好了", "真棒", "太帅了", "太美了",
    "可爱", "甜", "萌", "暖", "感动", "幸福", "快乐", "笑死",
    "哈哈", "哈哈哈", "笑", "乐", "笑嘻了", "起飞", "炸裂", "燃",
    "秀", "强", "猛", "无敌", "逆天", "封神", "牛逼plus",
}

NEGATIVE_WORDS: set[str] = {
    "难看", "无聊", "差评", "退了吧", "翻车", "垃圾", "恶心",
    "假的", "骗子", "智商税", "太贵了", "坑", "差劲", "失望",
    "尴尬", "难受", "吐了", "无语", "尬", "裂开", "崩了",
    "翻车", "事故", "翻了吧", "凉了", "完了", "废了", "烂",
    "黑心", "坑爹", "辣鸡", "破", "丑", "丑陋", "作呕",
    "退钱", "举报", "投诉", "取关", "再见", "走了", "拜拜",
    "不买", "不要", "别买", "踩雷", "翻大车",
}

QUESTION_PATTERNS: list[str] = [
    r"怎么买", r"多少钱", r"怎么下单", r"链接", r"有优惠",
    r"什么时候", r"在哪里", r"怎么用", r"好不好", r"怎么样",
    r"能.*吗", r"有没有", r"还.*吗", r"几号", r"色号",
]

# 停用词表
STOP_WORDS: set[str] = {
    "的", "了", "在", "是", "我", "有", "和", "就", "不", "人",
    "都", "一", "一个", "上", "也", "很", "到", "说", "要", "去",
    "你", "会", "着", "没有", "看", "好", "自己", "这", "他", "她",
    "吗", "把", "那", "它", "被", "从", "对", "但", "以", "这个",
    "什么", "怎么", "吧", "啊", "呢", "嗯", "哦", "哈", "呀",
    "么", "啦", "诶", "喂", "嘿", "噢", "嗯嗯", "哈哈哈",
    "可以", "就是", "还", "能", "吗", "么", "嘛", "嘻嘻",
    "哦哦", "噢噢", "啊啊", "嗯嗯嗯", "哈哈哈", "233",
    "emmm", "emm", "啊这", "好家伙", "确实", "真的",
}


# ── 情感分析核心 ──────────────────────────────────────────────

def _classify_sentiment(text: str) -> tuple[str, float]:
    """单条弹幕情感分类。返回 (sentiment, score)。

    规则优先：匹配积极/消极关键词，按命中数打分。
    """
    text_lower = text.lower()
    pos_hits = sum(1 for w in POSITIVE_WORDS if w in text_lower)
    neg_hits = sum(1 for w in NEGATIVE_WORDS if w in text_lower)
    is_question = any(re.search(p, text_lower) for p in QUESTION_PATTERNS)

    if pos_hits > 0 and neg_hits == 0:
        score = min(1.0, 0.4 + pos_hits * 0.2)
        return "positive", round(score, 3)
    if neg_hits > 0 and pos_hits == 0:
        score = max(-1.0, -0.4 - neg_hits * 0.2)
        return "negative", round(score, 3)
    if pos_hits > 0 and neg_hits > 0:
        # 混合情感 — 取净得分
        net = pos_hits - neg_hits
        score = max(-1.0, min(1.0, net * 0.25))
        if score > 0.1:
            return "positive", round(score, 3)
        if score < -0.1:
            return "negative", round(score, 3)
        return "neutral", 0.0
    if is_question:
        return "neutral", 0.0
    return "neutral", 0.0


def _compute_emotion_curve(
    danmus: list[Danmu],
    window_seconds: float = 10.0,
) -> list[dict[str, Any]]:
    """按时间窗口聚合情感曲线。"""
    if not danmus:
        return []

    min_t = danmus[0].timestamp
    max_t = danmus[-1].timestamp
    buckets: dict[int, list[Danmu]] = {}

    for d in danmus:
        idx = int((d.timestamp - min_t) / window_seconds)
        buckets.setdefault(idx, []).append(d)

    curve: list[dict[str, Any]] = []
    for idx in sorted(buckets):
        group = buckets[idx]
        scores = [d.sentiment_score for d in group]
        avg_score = sum(scores) / len(scores) if scores else 0.0
        curve.append({
            "time": round(min_t + idx * window_seconds, 1),
            "count": len(group),
            "score": round(avg_score, 3),
            "positive": sum(1 for d in group if d.sentiment == "positive"),
            "negative": sum(1 for d in group if d.sentiment == "negative"),
            "neutral": sum(1 for d in group if d.sentiment == "neutral"),
        })

    return curve


def _extract_keywords(danmus: list[Danmu], top_n: int = 50) -> list[dict[str, Any]]:
    """jieba 分词 + Counter 统计词频。"""
    try:
        import jieba
    except ImportError:
        logger.warning("jieba 未安装，跳过关键词提取")
        return []

    word_counter: Counter[tuple[str, str]] = Counter()
    for d in danmus:
        words = jieba.lcut(d.content)
        for word in words:
            word = word.strip()
            if len(word) < 2 or word in STOP_WORDS:
                continue
            if re.match(r"^[\d\s\W]+$", word):
                continue
            # 记录词和它出现时的主流情感
            word_counter[word] += 1

    # 统计每个词的主流情感
    word_sentiments: dict[str, Counter[str]] = {}
    for d in danmus:
        words = set(jieba.lcut(d.content))
        for word in words:
            word = word.strip()
            if len(word) < 2 or word in STOP_WORDS:
                continue
            if re.match(r"^[\d\s\W]+$", word):
                continue
            word_sentiments.setdefault(word, Counter())[d.sentiment] += 1

    results: list[dict[str, Any]] = []
    for word, count in word_counter.most_common(top_n):
        sent_counter = word_sentiments.get(word, Counter())
        dominant = sent_counter.most_common(1)[0][0] if sent_counter else "neutral"
        results.append({"word": word, "count": count, "sentiment": dominant})

    return results


def _compute_metrics(danmus: list[Danmu], total_duration: float) -> dict[str, Any]:
    """互动指标。"""
    if not danmus or total_duration <= 0:
        return {
            "danmu_density": 0.0,
            "sentiment_volatility": 0.0,
            "sentiment_distribution": {"positive": 0, "negative": 0, "neutral": 0},
            "total_count": 0,
        }

    scores = [d.sentiment_score for d in danmus]
    mean_score = sum(scores) / len(scores)
    variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
    std_dev = math.sqrt(variance)

    density = len(danmus) / (total_duration / 60.0)  # 条/分钟

    pos = sum(1 for d in danmus if d.sentiment == "positive")
    neg = sum(1 for d in danmus if d.sentiment == "negative")
    neu = sum(1 for d in danmus if d.sentiment == "neutral")
    total = len(danmus)

    return {
        "danmu_density": round(density, 2),
        "sentiment_volatility": round(std_dev, 3),
        "sentiment_distribution": {
            "positive": round(pos / total, 3),
            "negative": round(neg / total, 3),
            "neutral": round(neu / total, 3),
        },
        "total_count": total,
    }


def _find_highlights(
    danmus: list[Danmu],
    window_seconds: float = 10.0,
    top_n: int = 5,
) -> list[dict[str, Any]]:
    """高光时刻：密度 Top N 时间段。"""
    if not danmus:
        return []

    min_t = danmus[0].timestamp
    buckets: dict[int, list[Danmu]] = {}
    for d in danmus:
        idx = int((d.timestamp - min_t) / window_seconds)
        buckets.setdefault(idx, []).append(d)

    sorted_buckets = sorted(buckets.items(), key=lambda x: len(x[1]), reverse=True)
    highlights: list[dict[str, Any]] = []
    for idx, group in sorted_buckets[:top_n]:
        scores = [d.sentiment_score for d in group]
        highlights.append({
            "time": round(min_t + idx * window_seconds, 1),
            "count": len(group),
            "avg_score": round(sum(scores) / len(scores), 3),
            "sample_danmus": [d.content for d in group[:5]],
        })

    return highlights


# ── 公开接口 ──────────────────────────────────────────────────

def analyze_danmu_batch(db: Session, batch_id: str) -> dict[str, Any]:
    """对整个批次弹幕做情感分析。

    流程：
    1. 查询批次下所有弹幕
    2. 规则情感分类，写入 sentiment + sentiment_score
    3. 聚合情感曲线（10 秒窗口）
    4. jieba 关键词提取 Top 50
    5. 互动指标
    6. 结果写入 AnalysisReport
    """
    danmus = (
        db.query(Danmu)
        .filter(Danmu.batch_id == batch_id)
        .order_by(Danmu.timestamp.asc())
        .all()
    )
    if not danmus:
        return {"error": "该批次无弹幕数据", "batch_id": batch_id}

    # ── Step 1: 情感分类 ──
    for d in danmus:
        sentiment, score = _classify_sentiment(d.content)
        d.sentiment = sentiment
        d.sentiment_score = score
    db.flush()

    # ── Step 2: 情感曲线 ──
    emotion_curve = _compute_emotion_curve(danmus, window_seconds=10.0)

    # ── Step 3: 关键词 ──
    keywords = _extract_keywords(danmus, top_n=50)

    # ── Step 4: 互动指标 ──
    total_duration = (danmus[-1].timestamp - danmus[0].timestamp) or 1.0
    metrics = _compute_metrics(danmus, total_duration)

    # ── Step 5: 高光时刻 ──
    highlights = _find_highlights(danmus, window_seconds=10.0, top_n=5)

    result = {
        "batch_id": batch_id,
        "emotion_curve": emotion_curve,
        "keywords": keywords,
        "metrics": metrics,
        "highlights": highlights,
        "status": "completed",
    }

    # ── Step 6: 写入 AnalysisReport ──
    report = db.query(AnalysisReport).filter(
        AnalysisReport.batch_id == batch_id
    ).first()
    if report is None:
        report = AnalysisReport(batch_id=batch_id, report_data={})
        db.add(report)
    report_data = report.report_data or {}
    report_data["danmu_analysis"] = result
    report.report_data = report_data

    db.flush()
    return result


def correlate_speech_danmu(
    db: Session,
    task_id: str,
    batch_id: str,
) -> dict[str, Any]:
    """将弹幕时间线与转写文本时间线对齐。

    分析：
    - 哪些话术引发了弹幕密度高峰
    - 哪些话术引发了正面/负面情绪爆发
    - 话术与弹幕的时滞分析
    """
    from models import Task

    task = db.query(Task).filter(Task.task_id == task_id).first()
    if not task:
        return {"error": "任务不存在", "task_id": task_id}

    segments = task.transcription_segments or []
    if not segments:
        return {"error": "任务无转写分段数据", "task_id": task_id}

    danmus = (
        db.query(Danmu)
        .filter(Danmu.batch_id == batch_id)
        .order_by(Danmu.timestamp.asc())
        .all()
    )
    if not danmus:
        return {"error": "该批次无弹幕数据", "batch_id": batch_id}

    # 确保弹幕已有情感分析
    if all(d.sentiment == "neutral" and d.sentiment_score == 0.0 for d in danmus):
        for d in danmus:
            sentiment, score = _classify_sentiment(d.content)
            d.sentiment = sentiment
            d.sentiment_score = score
        db.flush()

    # ── 对齐分析 ──
    correlations: list[dict[str, Any]] = []
    for seg in segments:
        # 解析话术时间窗口
        seg_start = _parse_time_to_seconds(seg.get("start_time", seg.get("start", 0)))
        seg_end = _parse_time_to_seconds(seg.get("end_time", seg.get("end", 0)))
        if seg_end <= seg_start:
            seg_end = seg_start + 10.0

        # 扩展窗口：话术结束后 5 秒内弹幕也算关联
        window_end = seg_end + 5.0

        # 筛选时间窗口内的弹幕
        related = [
            d for d in danmus
            if seg_start <= d.timestamp <= window_end
        ]

        if not related:
            correlations.append({
                "speech_text": seg.get("text", seg.get("content", ""))[:100],
                "speech_time": seg_start,
                "danmu_count": 0,
                "avg_score": 0.0,
                "peak_score": 0.0,
                "positive_ratio": 0.0,
                "negative_ratio": 0.0,
            })
            continue

        scores = [d.sentiment_score for d in related]
        pos = sum(1 for d in related if d.sentiment == "positive")
        neg = sum(1 for d in related if d.sentiment == "negative")
        total = len(related)

        # 找到情感峰值弹幕
        peak_danmu = max(related, key=lambda d: abs(d.sentiment_score))

        # 时滞分析：话术开始到弹幕峰值的时间差
        peak_time = peak_danmu.timestamp
        lag = round(peak_time - seg_start, 1)

        correlations.append({
            "speech_text": seg.get("text", seg.get("content", ""))[:100],
            "speech_time": seg_start,
            "danmu_count": total,
            "avg_score": round(sum(scores) / len(scores), 3),
            "peak_score": round(peak_danmu.sentiment_score, 3),
            "positive_ratio": round(pos / total, 3),
            "negative_ratio": round(neg / total, 3),
            "lag_seconds": lag,
            "sample_danmus": [d.content for d in related[:3]],
        })

    # 按弹幕数排序，找出最能引发互动的话术
    correlations.sort(key=lambda x: x["danmu_count"], reverse=True)

    # 保存到报告
    report = db.query(AnalysisReport).filter(
        AnalysisReport.batch_id == batch_id
    ).first()
    if report is None:
        report = AnalysisReport(batch_id=batch_id, report_data={})
        db.add(report)
    report_data = report.report_data or {}
    report_data["speech_danmu_correlation"] = correlations
    report.report_data = report_data
    db.flush()

    return {
        "task_id": task_id,
        "batch_id": batch_id,
        "correlations": correlations,
        "status": "completed",
    }


def _parse_time_to_seconds(time_val: Any) -> float:
    """将时间值转为秒数。支持 float、int、str (HH:MM:SS)。"""
    if isinstance(time_val, (int, float)):
        return float(time_val)
    if isinstance(time_val, str):
        parts = time_val.split(":")
        try:
            if len(parts) == 3:
                return int(parts[0]) * 3600 + int(parts[1]) * 60 + float(parts[2])
            if len(parts) == 2:
                return int(parts[0]) * 60 + float(parts[1])
            return float(time_val)
        except (ValueError, IndexError):
            return 0.0
    return 0.0


# ── ECharts 数据格式转换 ──────────────────────────────────────

def _format_emotion_curve_echarts(curve: list[dict[str, Any]]) -> dict[str, Any]:
    """将情感曲线转为 ECharts 折线图格式。

    返回:
        {
          "xAxis": { "data": ["0s", "10s", ...] },
          "series": [
            { "name": "情感分数", "type": "line", "data": [...] },
            { "name": "弹幕数", "type": "bar", "data": [...] },
            { "name": "积极", "type": "bar", "stack": "sentiment", "data": [...] },
            { "name": "消极", "type": "bar", "stack": "sentiment", "data": [...] },
            { "name": "中性", "type": "bar", "stack": "sentiment", "data": [...] },
          ]
        }
    """
    if not curve:
        return {"xAxis": {"data": []}, "series": []}

    x_data = [f"{int(p['time'])}s" for p in curve]
    return {
        "xAxis": {"data": x_data},
        "series": [
            {
                "name": "情感分数",
                "type": "line",
                "smooth": True,
                "yAxisIndex": 0,
                "data": [p["score"] for p in curve],
            },
            {
                "name": "弹幕数",
                "type": "bar",
                "yAxisIndex": 1,
                "data": [p["count"] for p in curve],
            },
            {
                "name": "积极",
                "type": "bar",
                "stack": "sentiment",
                "yAxisIndex": 1,
                "itemStyle": {"color": "#67C23A"},
                "data": [p["positive"] for p in curve],
            },
            {
                "name": "消极",
                "type": "bar",
                "stack": "sentiment",
                "yAxisIndex": 1,
                "itemStyle": {"color": "#F56C6C"},
                "data": [p["negative"] for p in curve],
            },
            {
                "name": "中性",
                "type": "bar",
                "stack": "sentiment",
                "yAxisIndex": 1,
                "itemStyle": {"color": "#909399"},
                "data": [p["neutral"] for p in curve],
            },
        ],
    }


def _format_keywords_echarts(keywords: list[dict[str, Any]]) -> dict[str, Any]:
    """将关键词转为 ECharts 词云/柱状图格式。

    返回:
        {
          "bar": { "xAxis": { "data": [...] }, "series": [{ "data": [...] }] },
          "cloud": { "data": [{ "name": "...", "value": 100 }] }
        }
    """
    if not keywords:
        return {"bar": {"xAxis": {"data": []}, "series": [{"data": []}]}, "cloud": {"data": []}}

    top20 = keywords[:20]
    bar = {
        "xAxis": {"data": [k["word"] for k in top20]},
        "series": [{
            "name": "词频",
            "type": "bar",
            "data": [k["count"] for k in top20],
        }],
    }

    cloud = {
        "data": [{"name": k["word"], "value": k["count"]} for k in keywords],
    }

    return {"bar": bar, "cloud": cloud}


def _format_correlation_echarts(correlations: list[dict[str, Any]]) -> dict[str, Any]:
    """将话术-弹幕关联数据转为 ECharts 格式。

    返回:
        {
          "xAxis": { "data": ["话术1", "话术2", ...] },
          "series": [
            { "name": "弹幕数", "type": "bar", "data": [...] },
            { "name": "情感均分", "type": "line", "data": [...] },
          ]
        }
    """
    if not correlations:
        return {"xAxis": {"data": []}, "series": []}

    # 取弹幕数 Top 15 话术
    top = sorted(correlations, key=lambda x: x["danmu_count"], reverse=True)[:15]
    labels = [
        c["speech_text"][:12] + ("..." if len(c["speech_text"]) > 12 else "")
        for c in top
    ]

    return {
        "xAxis": {"data": labels},
        "series": [
            {
                "name": "弹幕数",
                "type": "bar",
                "yAxisIndex": 0,
                "data": [c["danmu_count"] for c in top],
            },
            {
                "name": "情感均分",
                "type": "line",
                "smooth": True,
                "yAxisIndex": 1,
                "data": [c["avg_score"] for c in top],
            },
        ],
    }


def format_for_echarts(analysis_result: dict[str, Any]) -> dict[str, Any]:
    """将分析结果转换为前端 ECharts 直接消费的格式。

    返回: { "emotion_curve_echarts", "keywords_echarts", ... }
    """
    echarts: dict[str, Any] = {}

    curve = analysis_result.get("emotion_curve", [])
    echarts["emotion_curve"] = _format_emotion_curve_echarts(curve)

    keywords = analysis_result.get("keywords", [])
    echarts["keywords"] = _format_keywords_echarts(keywords)

    return echarts
