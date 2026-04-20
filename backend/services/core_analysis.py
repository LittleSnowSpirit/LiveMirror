"""Lightweight deterministic analysis used by the core upload pipeline."""

from __future__ import annotations

from collections import Counter
from typing import Any


SPEECH_KEYWORDS = {
    "opening": ["欢迎", "直播间", "大家好", "今天"],
    "product_intro": ["产品", "功能", "特点", "适合", "使用"],
    "price_promotion": ["优惠", "下单", "价格", "折扣", "限时"],
    "interaction": ["评论", "提问", "问题", "关注", "点赞"],
    "closing": ["购买", "拍下", "成交", "库存", "最后"],
}


def classify_segment(text: str) -> str:
    scores = {
        speech_type: sum(1 for keyword in keywords if keyword in text)
        for speech_type, keywords in SPEECH_KEYWORDS.items()
    }
    speech_type, score = max(scores.items(), key=lambda item: item[1])
    return speech_type if score > 0 else "normal"


def build_core_analysis(
    transcription: str,
    segments: list[dict[str, Any]],
    duration: float | None,
) -> dict[str, Any]:
    speech_items: list[dict[str, Any]] = []

    for segment in segments:
        text = str(segment.get("text", ""))
        speech_type = classify_segment(text)
        start = float(segment.get("start", 0.0) or 0.0)
        end = float(segment.get("end", start) or start)
        score = 0.72 if speech_type != "normal" else 0.55
        speech_items.append(
            {
                "id": str(segment.get("id", len(speech_items))),
                "type": speech_type,
                "content": text,
                "start_time": start,
                "end_time": end,
                "score": score,
                "suggestion": _suggestion_for(speech_type),
            }
        )

    distribution = Counter(item["type"] for item in speech_items)
    issue_count = sum(1 for item in speech_items if item["type"] == "normal")
    highlight_count = max(0, len(speech_items) - issue_count)

    suggestions = [
        {
            "category": "structure",
            "title": "保持清晰的讲解节奏",
            "description": "把欢迎、产品价值、优惠信息和互动引导拆成更明确的段落。",
            "priority": "medium",
        }
    ]
    if issue_count:
        suggestions.insert(
            0,
            {
                "category": "clarity",
                "title": "补充明确的话术意图",
                "description": "部分片段缺少清晰分类，可加入产品卖点、互动问题或成交引导。",
                "priority": "high",
            },
        )

    attribution = [
        {
            "factor": item["type"],
            "impact": "positive" if item["type"] != "normal" else "neutral",
            "evidence": item["content"][:120],
            "confidence": item["score"],
        }
        for item in speech_items[:5]
    ]

    return {
        "summary": {
            "totalDuration": duration or _duration_from_segments(segments),
            "totalSpeeches": len(speech_items),
            "avgEmotion": 0.62,
            "highlightCount": highlight_count,
            "issueCount": issue_count,
            "speechTypeDistribution": dict(distribution),
        },
        "timeline": [
            {
                "timestamp": float(item["start_time"]),
                "emotion": round(item["score"] * 2 - 1, 2),
                "label": item["type"],
            }
            for item in speech_items
        ],
        "speeches": [
            {
                "id": item["id"],
                "timestamp": item["start_time"],
                "duration": max(0.0, item["end_time"] - item["start_time"]),
                "content": item["content"],
                "type": "highlight" if item["type"] != "normal" else "issue",
                "emotion": round(item["score"] * 2 - 1, 2),
                "suggestion": item["suggestion"],
                "tags": [item["type"]],
            }
            for item in speech_items
        ],
        "speaking_techniques": speech_items,
        "attribution_analysis": attribution,
        "suggestions": suggestions,
        "summary_text": "本报告基于本地转写结果生成，重点关注话术结构、互动引导和成交表达。",
    }


def build_report_data(
    task_id: str,
    filename: str,
    transcription: str,
    segments: list[dict[str, Any]],
    duration: float | None,
    language: str | None,
    analysis: dict[str, Any],
) -> dict[str, Any]:
    return {
        "task_id": task_id,
        "filename": filename,
        "duration": duration,
        "language": language,
        "transcription": transcription,
        "segments": segments,
        "analysis": analysis,
        "summary": analysis.get("summary", {}),
        "timeline": analysis.get("timeline", []),
        "speeches": analysis.get("speeches", []),
        "speaking_techniques": analysis.get("speaking_techniques", []),
        "attribution_analysis": analysis.get("attribution_analysis", []),
        "suggestions": analysis.get("suggestions", []),
        "summary_text": analysis.get("summary_text", ""),
    }


def _duration_from_segments(segments: list[dict[str, Any]]) -> float:
    if not segments:
        return 0.0
    return max(float(segment.get("end", 0.0) or 0.0) for segment in segments)


def _suggestion_for(speech_type: str) -> str:
    return {
        "opening": "开场可以更快说明本场福利和适合人群。",
        "product_intro": "产品介绍建议绑定具体使用场景。",
        "price_promotion": "优惠话术要明确时间、库存或权益边界。",
        "interaction": "互动问题可以更具体，方便观众直接回答。",
        "closing": "成交引导要减少犹豫点，并补充信任证明。",
        "normal": "补充明确目的，让这段话承担欢迎、介绍、互动或成交中的一个角色。",
    }.get(speech_type, "保持表达清晰，并补充可执行的下一步。")
