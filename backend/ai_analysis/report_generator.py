"""
LiveMirror AI 分析模块 - 报告生成器
负责生成结构化的分析报告
"""

import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class AnalysisMetadata:
    """分析元数据"""
    analysis_time: str
    total_duration: str
    total_segments: int
    model_version: str
    api_model: str = "deepseek-chat"


@dataclass
class AnalysisSummary:
    """分析摘要"""
    total_highlights: int
    total_crashes: int
    critical_crashes: int
    overall_score: int
    key_insights: List[str]


class ReportGenerator:
    """分析报告生成器"""

    def __init__(self, model_version: str = "v1.0", api_model: str = "deepseek-chat"):
        self.model_version = model_version
        self.api_model = api_model

    def generate_report(
        self,
        segments: List[Dict[str, Any]],
        highlights: List[Dict[str, Any]],
        crashes: List[Dict[str, Any]],
        attributions: Optional[List[Dict[str, Any]]] = None,
        suggestions: Optional[List[Dict[str, Any]]] = None,
        duration: Optional[str] = None,
        rhythm_analysis: Optional[Dict[str, Any]] = None,
        engagement_metrics: Optional[Dict[str, Any]] = None,
        emotion_curve: Optional[Dict[str, Any]] = None,
        speech_diversity: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        生成完整的分析报告

        Args:
            segments: 分段列表
            highlights: 爆点列表
            crashes: 翻车点列表
            attributions: 归因分析列表（可选）
            suggestions: 优化建议列表（可选）
            duration: 总时长（可选）
            rhythm_analysis: 节奏分析（可选）
            engagement_metrics: 互动指标（可选）
            emotion_curve: 情绪曲线（可选）
            speech_diversity: 话术多样性（可选）

        Returns:
            完整的报告字典
        """
        # 计算摘要信息
        summary = self._calculate_summary(
            highlights, crashes,
            rhythm_analysis=rhythm_analysis,
            engagement_metrics=engagement_metrics,
            emotion_curve=emotion_curve,
            speech_diversity=speech_diversity,
        )

        # 构建报告
        report = {
            "metadata": {
                "analysis_time": datetime.now().isoformat(),
                "total_duration": duration or self._calculate_duration(segments),
                "total_segments": len(segments),
                "model_version": self.model_version,
                "api_model": self.api_model,
            },
            "segments": segments,
            "highlights": highlights,
            "crashes": crashes,
            "summary": summary,
        }

        # 添加可选部分
        if attributions:
            report["attributions"] = attributions

        if suggestions:
            report["suggestions"] = suggestions

        if rhythm_analysis:
            report["rhythm_analysis"] = rhythm_analysis

        if engagement_metrics:
            report["engagement_metrics"] = engagement_metrics

        if emotion_curve:
            report["emotion_curve"] = emotion_curve

        if speech_diversity:
            report["speech_diversity"] = speech_diversity

        return report
    
    def _calculate_summary(
        self,
        highlights: List[Dict[str, Any]],
        crashes: List[Dict[str, Any]],
        rhythm_analysis: Optional[Dict[str, Any]] = None,
        engagement_metrics: Optional[Dict[str, Any]] = None,
        emotion_curve: Optional[Dict[str, Any]] = None,
        speech_diversity: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """计算分析摘要"""
        total_highlights = len(highlights)
        total_crashes = len(crashes)
        critical_crashes = sum(
            1 for c in crashes
            if c.get("severity") == "critical" or c.get("risk_level", 0) >= 8
        )

        # 计算综合得分（0-100）
        overall_score = self._calculate_overall_score(
            total_highlights,
            total_crashes,
            critical_crashes,
            rhythm_analysis=rhythm_analysis,
            engagement_metrics=engagement_metrics,
            emotion_curve=emotion_curve,
            speech_diversity=speech_diversity,
        )

        # 生成关键洞察
        key_insights = self._generate_key_insights(
            highlights,
            crashes,
            total_highlights,
            total_crashes,
            critical_crashes,
            rhythm_analysis=rhythm_analysis,
            engagement_metrics=engagement_metrics,
            emotion_curve=emotion_curve,
            speech_diversity=speech_diversity,
        )

        return {
            "total_highlights": total_highlights,
            "total_crashes": total_crashes,
            "critical_crashes": critical_crashes,
            "overall_score": overall_score,
            "key_insights": key_insights,
        }

    def _calculate_overall_score(
        self,
        highlights: int,
        crashes: int,
        critical_crashes: int,
        rhythm_analysis: Optional[Dict[str, Any]] = None,
        engagement_metrics: Optional[Dict[str, Any]] = None,
        emotion_curve: Optional[Dict[str, Any]] = None,
        speech_diversity: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        计算综合得分

        算法：
        - 基础分 60 分
        - 每个爆点 +2 分（上限 +20 分）
        - 每个普通翻车 -3 分
        - 每个严重翻车 -8 分
        - 节奏分析加分（如有）：最高 +5 分
        - 互动指标加分（如有）：最高 +5 分
        - 情绪曲线加分（如有）：最高 +5 分
        - 话术多样性加分（如有）：最高 +5 分
        - 最终分数限制在 0-100
        """
        base_score = 60

        # 爆点加分
        highlight_bonus = min(highlights * 2, 20)

        # 翻车扣分
        normal_crashes = crashes - critical_crashes
        crash_penalty = normal_crashes * 3 + critical_crashes * 8

        score = base_score + highlight_bonus - crash_penalty

        # 新维度加分（各维度满分 100，映射到 0-5 的加分）
        dimension_scores = []
        for dim_data in [rhythm_analysis, engagement_metrics, emotion_curve, speech_diversity]:
            if dim_data and isinstance(dim_data.get("score"), (int, float)):
                dim_score = dim_data["score"]
                # 100 分 -> +5, 60 分 -> +1, <60 -> +0
                bonus = max(0, min(5, (dim_score - 50) / 10))
                score += bonus
                dimension_scores.append(dim_score)

        score = max(0, min(100, round(score)))

        return score
    
    def _generate_key_insights(
        self,
        highlights: List[Dict[str, Any]],
        crashes: List[Dict[str, Any]],
        total_highlights: int,
        total_crashes: int,
        critical_crashes: int,
        rhythm_analysis: Optional[Dict[str, Any]] = None,
        engagement_metrics: Optional[Dict[str, Any]] = None,
        emotion_curve: Optional[Dict[str, Any]] = None,
        speech_diversity: Optional[Dict[str, Any]] = None,
    ) -> List[str]:
        """生成关键洞察"""
        insights = []

        # 爆点分析
        if total_highlights > 0:
            # 统计爆点类型分布
            highlight_types = {}
            for h in highlights:
                h_type = h.get("type", "其他")
                highlight_types[h_type] = highlight_types.get(h_type, 0) + 1

            if highlight_types:
                top_type = max(highlight_types, key=highlight_types.get)
                insights.append(f"主要爆点类型：{top_type}（{highlight_types[top_type]}次）")

        # 翻车分析
        if total_crashes > 0:
            if critical_crashes > 0:
                insights.append(f"[警告] 发现{critical_crashes}个严重翻车点，需要优先处理")

            # 统计翻车类型分布
            crash_types = {}
            for c in crashes:
                c_type = c.get("type", "其他")
                crash_types[c_type] = crash_types.get(c_type, 0) + 1

            if crash_types:
                top_crash = max(crash_types, key=crash_types.get)
                insights.append(f"主要翻车类型：{top_crash}（{crash_types[top_crash]}次）")

        # 综合建议
        ratio = total_highlights / max(total_crashes, 1)
        if ratio > 2:
            insights.append("[优秀] 整体话术质量优秀，爆点远多于翻车点")
        elif ratio > 1:
            insights.append("[良好] 话术质量良好，可适当优化翻车点")
        else:
            insights.append("[注意] 翻车点较多，建议重点优化话术")

        # 节奏分析洞察
        if rhythm_analysis:
            rhythm_score = rhythm_analysis.get("score", 0)
            rhythm_rating = rhythm_analysis.get("overall_rating", "")
            if rhythm_score < 60:
                insights.append(f"[节奏] 直播节奏较差（{rhythm_rating}，{rhythm_score}分），建议优化开场-促单-收尾比例")
            elif rhythm_score < 75:
                insights.append(f"[节奏] 直播节奏一般（{rhythm_rating}，{rhythm_score}分），各阶段时间分配可进一步优化")
            else:
                insights.append(f"[节奏] 直播节奏{rhythm_rating}（{rhythm_score}分），节奏把控较好")

        # 互动密度洞察
        if engagement_metrics:
            ipm = engagement_metrics.get("interactions_per_minute", 0)
            eng_score = engagement_metrics.get("score", 0)
            if ipm < 1.0:
                insights.append(f"[互动] 互动引导密度偏低（{ipm:.1f}次/分钟），建议增加互动频次")
            elif ipm > 5.0:
                insights.append(f"[互动] 互动引导密度较高（{ipm:.1f}次/分钟），注意避免过度打扰")
            else:
                insights.append(f"[互动] 互动密度适中（{ipm:.1f}次/分钟），{engagement_metrics.get('rating', '')}")

            dead_zones = engagement_metrics.get("dead_zones", [])
            if dead_zones:
                insights.append(f"[互动] 发现{len(dead_zones)}段互动空白区，需注意连续引导")

        # 情绪曲线洞察
        if emotion_curve:
            trend = emotion_curve.get("overall_trend", "")
            emotion_score = emotion_curve.get("score", 0)
            if trend == "高开低走":
                insights.append("[情绪] 情绪高开低走，后半段观众热情下降，建议在中后段加强促单力度")
            elif trend == "持续低迷":
                insights.append("[情绪] 整场直播情绪低迷，建议增加互动和限时优惠来调动气氛")
            elif trend == "逐步升温":
                insights.append(f"[情绪] 情绪逐步升温（{emotion_score}分），节奏把控良好")

        # 话术多样性洞察
        if speech_diversity:
            diversity_score = speech_diversity.get("score", 0)
            richness = speech_diversity.get("vocabulary_richness", "")
            repeated = speech_diversity.get("repeated_phrases", [])
            if richness == "单一":
                insights.append(f"[话术] 话术多样性较差（{diversity_score}分），存在{len(repeated)}个高频重复表达")
            elif repeated:
                insights.append(f"[话术] 发现{len(repeated)}个重复话术，建议丰富表达方式")

        # 如果没有洞察，提供默认建议
        if not insights:
            insights.append("直播话术平稳，可尝试增加互动和促单技巧")

        return insights[:8]  # 最多 8 条洞察

    def generate_detailed_sections(
        self,
        report: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """
        生成结构化的详细分析段落，供前端渲染多维度详情。

        Args:
            report: 完整报告字典

        Returns:
            详细段落列表，每段包含 title / content / score / level
        """
        sections: List[Dict[str, Any]] = []

        summary = report.get("summary", {})
        rhythm = report.get("rhythm_analysis")
        engagement = report.get("engagement_metrics")
        emotion = report.get("emotion_curve")
        diversity = report.get("speech_diversity")

        # 基础指标段
        sections.append({
            "title": "核心指标",
            "content": (
                f"综合得分 {summary.get('overall_score', 0)}/100 | "
                f"爆点 {summary.get('total_highlights', 0)} 个 | "
                f"翻车 {summary.get('total_crashes', 0)} 个 | "
                f"严重翻车 {summary.get('critical_crashes', 0)} 个"
            ),
            "score": summary.get("overall_score", 0),
            "level": self._score_level(summary.get("overall_score", 0)),
        })

        # 节奏分析段
        if rhythm:
            phase_lines = []
            for phase in rhythm.get("phases", []):
                phase_lines.append(
                    f"  - {phase.get('phase', '?')}："
                    f"{phase.get('start_time', '?')} ~ {phase.get('end_time', '?')} "
                    f"({phase.get('proportion', '?')}) — {phase.get('evaluation', '')}"
                )
            content = f"节奏评分：{rhythm.get('score', 0)}/100（{rhythm.get('overall_rating', '?')}）\n"
            content += "\n".join(phase_lines)
            if rhythm.get("issues"):
                content += "\n问题：" + "；".join(rhythm["issues"])
            if rhythm.get("suggestions"):
                content += "\n建议：" + "；".join(rhythm["suggestions"])
            sections.append({
                "title": "节奏分析",
                "content": content,
                "score": rhythm.get("score", 0),
                "level": self._score_level(rhythm.get("score", 0)),
            })

        # 互动指标段
        if engagement:
            content = (
                f"互动评分：{engagement.get('score', 0)}/100（{engagement.get('rating', '?')}）\n"
                f"互动密度：{engagement.get('interactions_per_minute', 0):.1f} 次/分钟 | "
                f"总互动 {engagement.get('total_interactions', 0)} 次"
            )
            types = engagement.get("interaction_types", {})
            if types:
                content += "\n互动类型分布：" + "、".join(
                    f"{k}({v})" for k, v in types.items()
                )
            dead_zones = engagement.get("dead_zones", [])
            if dead_zones:
                content += f"\n互动空白区：{len(dead_zones)} 段"
                for dz in dead_zones[:3]:
                    content += f"\n  - {dz.get('start_time', '?')}~{dz.get('end_time', '?')}：{dz.get('description', '')}"
            sections.append({
                "title": "互动分析",
                "content": content,
                "score": engagement.get("score", 0),
                "level": self._score_level(engagement.get("score", 0)),
            })

        # 情绪曲线段
        if emotion:
            content = (
                f"情绪评分：{emotion.get('score', 0)}/100 | "
                f"整体趋势：{emotion.get('overall_trend', '?')}"
            )
            peaks = emotion.get("peak_moments", [])
            lows = emotion.get("low_moments", [])
            if peaks:
                content += f"\n情绪高点：{'、'.join(peaks[:3])}"
            if lows:
                content += f"\n情绪低点：{'、'.join(lows[:3])}"
            sections.append({
                "title": "情绪分析",
                "content": content,
                "score": emotion.get("score", 0),
                "level": self._score_level(emotion.get("score", 0)),
            })

        # 话术多样性段
        if diversity:
            content = (
                f"多样性评分：{diversity.get('score', 0)}/100 | "
                f"词汇丰富度：{diversity.get('vocabulary_richness', '?')}"
            )
            repeated = diversity.get("repeated_phrases", [])
            if repeated:
                content += f"\n高频重复表达（{len(repeated)} 个）："
                for rp in repeated[:5]:
                    content += (
                        f"\n  - \"{rp.get('phrase', '?')}\" x{rp.get('count', 0)} "
                        f"({rp.get('first_occurrence', '?')} ~ {rp.get('last_occurrence', '?')})"
                    )
            if diversity.get("suggestions"):
                content += "\n建议：" + "；".join(diversity["suggestions"])
            sections.append({
                "title": "话术多样性",
                "content": content,
                "score": diversity.get("score", 0),
                "level": self._score_level(diversity.get("score", 0)),
            })

        return sections

    @staticmethod
    def _score_level(score: int) -> str:
        """将分数映射为等级标签。"""
        if score >= 85:
            return "excellent"
        if score >= 70:
            return "good"
        if score >= 50:
            return "average"
        return "poor"
    
    def _calculate_duration(self, segments: List[Dict[str, Any]]) -> str:
        """从分段信息计算总时长"""
        if not segments:
            return "00:00:00"
        
        last_segment = segments[-1]
        return last_segment.get("end_time", "00:00:00")
    
    def to_json(self, report: Dict[str, Any], indent: int = 2) -> str:
        """将报告转换为 JSON 字符串"""
        return json.dumps(report, ensure_ascii=False, indent=indent)
    
    def save_report(self, report: Dict[str, Any], filepath: str) -> None:
        """保存报告到文件"""
        json_str = self.to_json(report)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(json_str)
    
    def generate_executive_summary(self, report: Dict[str, Any]) -> str:
        """
        生成执行摘要（人类可读格式）

        Args:
            report: 完整报告

        Returns:
            执行摘要文本
        """
        metadata = report.get("metadata", {})
        summary = report.get("summary", {})
        rhythm = report.get("rhythm_analysis")
        engagement = report.get("engagement_metrics")
        emotion = report.get("emotion_curve")
        diversity = report.get("speech_diversity")

        lines = [
            "=" * 60,
            "LiveMirror 直播话术分析报告",
            "=" * 60,
            "",
            f"分析时间：{metadata.get('analysis_time', 'N/A')}",
            f"直播时长：{metadata.get('total_duration', 'N/A')}",
            f"分段数量：{metadata.get('total_segments', 0)}",
            "",
            "核心指标",
            "-" * 40,
            f"综合得分：{summary.get('overall_score', 0)}/100",
            f"爆点数量：{summary.get('total_highlights', 0)}",
            f"翻车数量：{summary.get('total_crashes', 0)}",
            f"严重翻车：{summary.get('critical_crashes', 0)}",
        ]

        # 新维度摘要
        if rhythm:
            lines.extend([
                "",
                "节奏分析",
                "-" * 40,
                f"节奏评分：{rhythm.get('score', 0)}/100（{rhythm.get('overall_rating', 'N/A')}）",
            ])
            for phase in rhythm.get("phases", []):
                lines.append(
                    f"  {phase.get('phase', '?')}：{phase.get('proportion', '?')} — {phase.get('evaluation', '')}"
                )

        if engagement:
            lines.extend([
                "",
                "互动指标",
                "-" * 40,
                f"互动评分：{engagement.get('score', 0)}/100（{engagement.get('rating', 'N/A')}）",
                f"互动密度：{engagement.get('interactions_per_minute', 0):.1f} 次/分钟",
            ])

        if emotion:
            lines.extend([
                "",
                "情绪曲线",
                "-" * 40,
                f"情绪评分：{emotion.get('score', 0)}/100",
                f"整体趋势：{emotion.get('overall_trend', 'N/A')}",
            ])

        if diversity:
            lines.extend([
                "",
                "话术多样性",
                "-" * 40,
                f"多样性评分：{diversity.get('score', 0)}/100",
                f"词汇丰富度：{diversity.get('vocabulary_richness', 'N/A')}",
            ])

        lines.extend([
            "",
            "关键洞察",
            "-" * 40,
        ])

        for i, insight in enumerate(summary.get("key_insights", []), 1):
            lines.append(f"{i}. {insight}")

        lines.extend([
            "",
            "=" * 60,
        ])

        return "\n".join(lines)


def create_report_generator(
    model_version: str = "v1.0",
    api_model: str = "deepseek-chat"
) -> ReportGenerator:
    """工厂函数：创建报告生成器实例"""
    return ReportGenerator(model_version, api_model)
