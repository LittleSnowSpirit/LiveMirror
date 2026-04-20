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
        duration: Optional[str] = None
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
        
        Returns:
            完整的报告字典
        """
        # 计算摘要信息
        summary = self._calculate_summary(highlights, crashes)
        
        # 构建报告
        report = {
            "metadata": {
                "analysis_time": datetime.now().isoformat(),
                "total_duration": duration or self._calculate_duration(segments),
                "total_segments": len(segments),
                "model_version": self.model_version,
                "api_model": self.api_model
            },
            "segments": segments,
            "highlights": highlights,
            "crashes": crashes,
            "summary": summary
        }
        
        # 添加可选部分
        if attributions:
            report["attributions"] = attributions
        
        if suggestions:
            report["suggestions"] = suggestions
        
        return report
    
    def _calculate_summary(
        self,
        highlights: List[Dict[str, Any]],
        crashes: List[Dict[str, Any]]
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
            critical_crashes
        )
        
        # 生成关键洞察
        key_insights = self._generate_key_insights(
            highlights,
            crashes,
            total_highlights,
            total_crashes,
            critical_crashes
        )
        
        return {
            "total_highlights": total_highlights,
            "total_crashes": total_crashes,
            "critical_crashes": critical_crashes,
            "overall_score": overall_score,
            "key_insights": key_insights
        }
    
    def _calculate_overall_score(
        self,
        highlights: int,
        crashes: int,
        critical_crashes: int
    ) -> int:
        """
        计算综合得分
        
        算法：
        - 基础分 60 分
        - 每个爆点 +2 分（上限 +20 分）
        - 每个普通翻车 -3 分
        - 每个严重翻车 -8 分
        - 最终分数限制在 0-100
        """
        base_score = 60
        
        # 爆点加分
        highlight_bonus = min(highlights * 2, 20)
        
        # 翻车扣分
        normal_crashes = crashes - critical_crashes
        crash_penalty = normal_crashes * 3 + critical_crashes * 8
        
        score = base_score + highlight_bonus - crash_penalty
        score = max(0, min(100, score))
        
        return score
    
    def _generate_key_insights(
        self,
        highlights: List[Dict[str, Any]],
        crashes: List[Dict[str, Any]],
        total_highlights: int,
        total_crashes: int,
        critical_crashes: int
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
        
        # 如果没有洞察，提供默认建议
        if not insights:
            insights.append("直播话术平稳，可尝试增加互动和促单技巧")
        
        return insights[:5]  # 最多 5 条洞察
    
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
            "",
            "关键洞察",
            "-" * 40,
        ]
        
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
