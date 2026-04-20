"""
LiveMirror AI 分析模块

AI 驱动的直播话术分析系统，识别爆点和翻车点。
"""

from .analyzer import LiveMirrorAnalyzer, create_analyzer, analyze_transcript
from .prompts import get_prompt, SYSTEM_ROLE
from .classifiers import (
    KeywordClassifier,
    RuleBasedAnalyzer,
    create_classifier,
    create_rule_analyzer,
    SpeechType,
    CrashType,
    Severity
)
from .suggester import OptimizationSuggester, create_suggester
from .report_generator import ReportGenerator, create_report_generator

__version__ = "1.0.0"
__author__ = "LiveMirror Team"

__all__ = [
    # 主分析器
    "LiveMirrorAnalyzer",
    "create_analyzer",
    "analyze_transcript",
    
    # Prompt 模板
    "get_prompt",
    "SYSTEM_ROLE",
    
    # 分类器
    "KeywordClassifier",
    "RuleBasedAnalyzer",
    "create_classifier",
    "create_rule_analyzer",
    "SpeechType",
    "CrashType",
    "Severity",
    
    # 建议生成器
    "OptimizationSuggester",
    "create_suggester",
    
    # 报告生成器
    "ReportGenerator",
    "create_report_generator",
]
