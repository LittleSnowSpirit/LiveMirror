"""
LiveMirror AI 分析模块 - 话术分类器
负责对话术进行类型分类和特征识别
"""

import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class SpeechType(Enum):
    """话术类型枚举"""
    PRODUCT_INTRO = "产品介绍"
    PROMOTION = "促单话术"
    INTERACTION = "互动引导"
    TRUST_BUILDING = "信任背书"
    PAIN_POINT = "痛点打击"
    SCARCITY = "稀缺性营造"
    PRICE_ANCHOR = "价格锚点"
    CASUAL = "闲聊"
    OTHER = "其他"


class CrashType(Enum):
    """翻车类型枚举"""
    SENSITIVE_WORD = "敏感词"
    WRONG_INFO = "错误表述"
    AWKWARD_SILENCE = "冷场"
    NEGATIVE_EMOTION = "负面情绪"
    CONTROVERSIAL = "争议言论"
    OVER_PROMISE = "过度承诺"
    COMPETITOR_BASHING = "贬低竞品"
    SPEECH_ERROR = "口误"


class Severity(Enum):
    """严重程度枚举"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Highlight:
    """爆点数据结构"""
    segment_id: int
    timestamp: str
    type: str
    original_text: str
    effectiveness_score: int
    analysis: str


@dataclass
class Crash:
    """翻车点数据结构"""
    segment_id: int
    timestamp: str
    type: str
    severity: str
    original_text: str
    problem: str
    risk_level: int


class KeywordClassifier:
    """基于关键词的话术分类器"""
    
    # 爆点关键词库
    HIGHLIGHT_KEYWORDS = {
        SpeechType.PROMOTION: [
            "赶紧下单", "快去拍", "想要的扣", "手慢无", "最后一波",
            "倒计时", "马上截单", "抓紧", "别犹豫", "直接拍"
        ],
        SpeechType.SCARCITY: [
            "限量", "绝版", "只剩", "最后", "独家", "稀缺",
            "卖完", "补货", "库存不多", "售完即止"
        ],
        SpeechType.PRICE_ANCHOR: [
            "原价", "今天只要", "立减", "优惠", "折扣", "券后价",
            "比平时", "省了", "划算", "性价比"
        ],
        SpeechType.TRUST_BUILDING: [
            "我自己也在用", "销量", "回购", "好评", "推荐",
            "正品", "保证", "放心", "口碑", "老粉"
        ],
        SpeechType.PAIN_POINT: [
            "是不是经常", "有没有遇到", "困扰", "烦恼", "痛点",
            "解决", "改善", "告别", "不再"
        ],
        SpeechType.INTERACTION: [
            "点赞", "评论", "关注", "分享", "扣 1", "弹幕",
            "互动", "抽奖", "福利", "粉丝"
        ]
    }
    
    # 翻车关键词库
    CRASH_KEYWORDS = {
        CrashType.SENSITIVE_WORD: [
            "最", "第一", "顶级", "绝对", "100%", " guaranteed",
            "国家级", "世界级", "首选", "唯一"
        ],
        CrashType.OVER_PROMISE: [
            "保证有效", "一定", "肯定", "绝对没问题", "包治",
            "根治", "永不", "完全", "彻底"
        ],
        CrashType.NEGATIVE_EMOTION: [
            "烦死了", "真服了", "气死我了", "不想说了", "随便吧",
            "爱买不买", "无语", "累了"
        ],
        CrashType.COMPETITOR_BASHING: [
            "他家不行", "别家都是", "只有我们", "别人都",
            "某某品牌", "垃圾", "骗人"
        ]
    }
    
    def __init__(self):
        self.highlight_patterns = self._compile_patterns(self.HIGHLIGHT_KEYWORDS)
        self.crash_patterns = self._compile_patterns(self.CRASH_KEYWORDS)
    
    def _compile_patterns(self, keyword_dict: Dict) -> Dict:
        """编译正则表达式模式"""
        compiled = {}
        for category, keywords in keyword_dict.items():
            # 转义关键词并创建正则模式
            escaped = [re.escape(kw) for kw in keywords]
            pattern = "|".join(escaped)
            compiled[category] = re.compile(f"({pattern})", re.IGNORECASE)
        return compiled
    
    def classify_speech_type(self, text: str) -> List[SpeechType]:
        """
        识别话术类型（可能多种）
        
        Args:
            text: 话术文本
        
        Returns:
            识别出的话术类型列表
        """
        detected_types = []
        for speech_type, pattern in self.highlight_patterns.items():
            if pattern.search(text):
                detected_types.append(speech_type)
        
        # 如果没有检测到特定类型，默认为闲聊
        if not detected_types:
            # 检查是否为闲聊（短文本、无明确意图）
            if len(text) < 50:
                detected_types.append(SpeechType.CASUAL)
            else:
                detected_types.append(SpeechType.OTHER)
        
        return detected_types
    
    def detect_crashes(self, text: str) -> List[CrashType]:
        """
        检测翻车类型
        
        Args:
            text: 话术文本
        
        Returns:
            检测出的翻车类型列表
        """
        detected_crashes = []
        for crash_type, pattern in self.crash_patterns.items():
            if pattern.search(text):
                detected_crashes.append(crash_type)
        
        return detected_crashes
    
    def calculate_risk_level(self, crashes: List[CrashType]) -> int:
        """
        计算风险等级（1-10）
        
        Args:
            crashes: 翻车类型列表
        
        Returns:
            风险等级分数
        """
        if not crashes:
            return 0
        
        # 不同翻车类型的权重
        weights = {
            CrashType.SENSITIVE_WORD: 8,
            CrashType.OVER_PROMISE: 7,
            CrashType.CONTROVERSIAL: 9,
            CrashType.COMPETITOR_BASHING: 6,
            CrashType.NEGATIVE_EMOTION: 5,
            CrashType.WRONG_INFO: 7,
            CrashType.SPEECH_ERROR: 3,
            CrashType.AWKWARD_SILENCE: 2
        }
        
        total_weight = sum(weights.get(crash, 5) for crash in crashes)
        # 归一化到 1-10
        risk_level = min(10, max(1, int(total_weight / len(crashes))))
        
        return risk_level
    
    def determine_severity(self, risk_level: int) -> Severity:
        """
        根据风险等级确定严重程度
        
        Args:
            risk_level: 风险等级（1-10）
        
        Returns:
            严重程度枚举
        """
        if risk_level >= 8:
            return Severity.CRITICAL
        elif risk_level >= 6:
            return Severity.HIGH
        elif risk_level >= 4:
            return Severity.MEDIUM
        else:
            return Severity.LOW


class RuleBasedAnalyzer:
    """基于规则的预分析器（用于降低 API 调用成本）"""
    
    def __init__(self):
        self.keyword_classifier = KeywordClassifier()
    
    def pre_filter_segments(self, segments: List[Dict[str, Any]]) -> Dict[str, List[Dict]]:
        """
        预筛选需要深入分析的段落
        
        Args:
            segments: 分段后的话术列表
        
        Returns:
            分类后的段落字典（high_priority, medium_priority, low_priority）
        """
        priorities = {
            "high_priority": [],      # 需要详细 AI 分析
            "medium_priority": [],    # 可简化分析
            "low_priority": []        # 可跳过或仅做基础分类
        }
        
        for segment in segments:
            content = segment.get("content", "")
            
            # 高优先级：包含明显的爆点/翻车关键词
            highlights = self.keyword_classifier.classify_speech_type(content)
            crashes = self.keyword_classifier.detect_crashes(content)
            
            if crashes or len(highlights) >= 2:
                priorities["high_priority"].append(segment)
            elif highlights or len(content) > 200:
                priorities["medium_priority"].append(segment)
            else:
                priorities["low_priority"].append(segment)
        
        return priorities
    
    def quick_classify(self, text: str) -> Dict[str, Any]:
        """
        快速分类（不调用 AI API）
        
        Args:
            text: 话术文本
        
        Returns:
            分类结果字典
        """
        speech_types = self.keyword_classifier.classify_speech_type(text)
        crash_types = self.keyword_classifier.detect_crashes(text)
        risk_level = self.keyword_classifier.calculate_risk_level(crash_types)
        
        return {
            "speech_types": [st.value for st in speech_types],
            "crash_types": [ct.value for ct in crash_types],
            "risk_level": risk_level,
            "is_potential_highlight": len(speech_types) > 0 and speech_types[0] != SpeechType.CASUAL,
            "is_potential_crash": len(crash_types) > 0
        }


def create_classifier() -> KeywordClassifier:
    """工厂函数：创建分类器实例"""
    return KeywordClassifier()


def create_rule_analyzer() -> RuleBasedAnalyzer:
    """工厂函数：创建规则分析器实例"""
    return RuleBasedAnalyzer()
