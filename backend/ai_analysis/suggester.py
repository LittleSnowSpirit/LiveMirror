"""
LiveMirror AI 分析模块 - 优化建议生成器
针对翻车话术提供改写方案和优化建议
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
import json


@dataclass
class SuggestionVersion:
    """单个改写版本"""
    version: str  # A, B, C...
    rewritten_text: str
    improvement: str


@dataclass
class Suggestion:
    """优化建议数据结构"""
    segment_id: int
    original_text: str
    problem_type: str
    suggestions: List[SuggestionVersion]


class OptimizationSuggester:
    """优化建议生成器"""
    
    # 常见问题类型的改写策略
    REWRITE_STRATEGIES = {
        "敏感词": {
            "principle": "规避广告法禁用词，使用相对化表述",
            "examples": [
                ("最便宜", "性价比很高"),
                ("第一", "领先品牌"),
                ("绝对有效", "效果显著"),
                ("100% 见效", "大多数用户反馈有效"),
                ("顶级", "高品质"),
                ("国家级", "行业认可"),
            ]
        },
        "过度承诺": {
            "principle": "降低承诺强度，增加条件说明",
            "examples": [
                ("保证有效", "通常能看到改善"),
                ("一定成功", "有很大几率成功"),
                ("包治", "有助于改善"),
                ("根治", "从根源调理"),
                ("永不复发", "降低复发概率"),
            ]
        },
        "贬低竞品": {
            "principle": "聚焦自身优势，不直接攻击",
            "examples": [
                ("他家不行", "我们更注重"),
                ("别家都是假的", "我们坚持正品"),
                ("只有我们", "我们的特色是"),
                ("某某品牌垃圾", "我们选择更优质的"),
            ]
        },
        "负面情绪": {
            "principle": "转化为积极表达或幽默化解",
            "examples": [
                ("烦死了", "这个问题确实让人头疼"),
                ("真服了", "我理解大家的感受"),
                ("爱买不买", "大家可以理性选择"),
                ("不想说了", "我再多解释一下"),
            ]
        },
        "错误表述": {
            "principle": "提供准确信息，必要时澄清",
            "examples": [
                # 需要根据具体错误内容定制
            ]
        },
        "口误": {
            "principle": "自然纠正，保持流畅",
            "examples": [
                # 需要根据具体口误内容定制
            ]
        }
    }
    
    # 话术优化模板
    OPTIMIZATION_TEMPLATES = {
        "促单话术优化": [
            "原意：催促下单 → 优化：制造紧迫感但不过度施压",
            "示例：'喜欢的宝宝可以直接拍，库存有限哦' → '看到喜欢的可以先加入购物车，库存更新比较快'",
        ],
        "价格表述优化": [
            "原意：强调便宜 → 优化：强调价值",
            "示例：'全网最低' → '这个价格真的很有竞争力'",
        ],
        "效果描述优化": [
            "原意：绝对化效果 → 优化：相对化 + 用户反馈",
            "示例：'一定有效' → '很多老粉反馈效果不错'",
        ],
        "互动引导优化": [
            "原意：强制互动 → 优化：邀请式互动",
            "示例：'不点赞的不是真粉' → '喜欢的宝宝可以点个关注支持一下'",
        ]
    }
    
    def __init__(self):
        self.suggestions_cache = {}
    
    def generate_suggestions(
        self,
        crash: Dict[str, Any],
        context: Optional[str] = None
    ) -> Suggestion:
        """
        为翻车话术生成优化建议
        
        Args:
            crash: 翻车点信息字典
            context: 上下文信息（可选）
        
        Returns:
            Suggestion 对象
        """
        problem_type = crash.get("type", "其他")
        original_text = crash.get("original_text", "")
        segment_id = crash.get("segment_id", 0)
        
        # 获取改写策略
        strategy = self.REWRITE_STRATEGIES.get(problem_type, {
            "principle": "保持原意，优化表达",
            "examples": []
        })
        
        # 生成多个改写版本
        versions = self._generate_versions(
            original_text,
            problem_type,
            strategy,
            context
        )
        
        suggestion_versions = [
            SuggestionVersion(
                version=v["version"],
                rewritten_text=v["rewritten_text"],
                improvement=v["improvement"]
            )
            for v in versions
        ]
        
        return Suggestion(
            segment_id=segment_id,
            original_text=original_text,
            problem_type=problem_type,
            suggestions=suggestion_versions
        )
    
    def _generate_versions(
        self,
        original: str,
        problem_type: str,
        strategy: Dict,
        context: Optional[str]
    ) -> List[Dict[str, str]]:
        """生成多个改写版本"""
        versions = []
        
        # 版本 A：保守改写（最小改动）
        version_a = self._conservative_rewrite(original, problem_type, strategy)
        versions.append({
            "version": "A",
            "rewritten_text": version_a,
            "improvement": f"保守改写：{strategy.get('principle', '优化表达')}"
        })
        
        # 版本 B：平衡改写（适度优化）
        version_b = self._balanced_rewrite(original, problem_type, strategy, context)
        versions.append({
            "version": "B",
            "rewritten_text": version_b,
            "improvement": "平衡改写：在保持话术力度的同时规避风险"
        })
        
        # 版本 C：激进改写（完全重构）
        version_c = self._aggressive_rewrite(original, problem_type, strategy, context)
        versions.append({
            "version": "C",
            "rewritten_text": version_c,
            "improvement": "重构版本：完全规避问题，采用更安全的表达方式"
        })
        
        return versions
    
    def _conservative_rewrite(
        self,
        text: str,
        problem_type: str,
        strategy: Dict
    ) -> str:
        """保守改写：最小改动，替换敏感词"""
        result = text
        examples = strategy.get("examples", [])
        
        for old, new in examples:
            if old in result:
                result = result.replace(old, new)
        
        return result
    
    def _balanced_rewrite(
        self,
        text: str,
        problem_type: str,
        strategy: Dict,
        context: Optional[str]
    ) -> str:
        """平衡改写：适度优化，调整句式"""
        result = text
        
        # 常见模式替换
        replacements = [
            ("最", "非常"),
            ("第一", "领先"),
            ("绝对", "很"),
            ("一定", "通常"),
            ("保证", "努力"),
            ("所有", "大多数"),
            ("永远", "长期"),
        ]
        
        for old, new in replacements:
            result = result.replace(old, new)
        
        # 添加缓冲词
        if "效果" in result and "不" not in result:
            result = result.replace("效果", "效果（因人而异）")
        
        return result
    
    def _aggressive_rewrite(
        self,
        text: str,
        problem_type: str,
        strategy: Dict,
        context: Optional[str]
    ) -> str:
        """激进改写：完全重构话术"""
        # 根据问题类型生成完全不同的表述
        if problem_type == "敏感词":
            return "这款产品在我们的精选清单里，很多宝宝反馈都很满意"
        elif problem_type == "过度承诺":
            return "根据我们收集的用户反馈，大部分人都看到了不错的改善"
        elif problem_type == "贬低竞品":
            return "我们一直专注于做好自己的产品，品质大家有目共睹"
        elif problem_type == "负面情绪":
            return "我理解大家的顾虑，让我再详细解释一下"
        else:
            return "让我换个方式来说明这个问题"
    
    def generate_batch_suggestions(
        self,
        crashes: List[Dict[str, Any]]
    ) -> List[Suggestion]:
        """
        批量生成优化建议
        
        Args:
            crashes: 翻车点列表
        
        Returns:
            优化建议列表
        """
        suggestions = []
        for crash in crashes:
            suggestion = self.generate_suggestions(crash)
            suggestions.append(suggestion)
        
        return suggestions
    
    def to_dict(self, suggestion: Suggestion) -> Dict[str, Any]:
        """将 Suggestion 转换为字典"""
        return {
            "segment_id": suggestion.segment_id,
            "original_text": suggestion.original_text,
            "problem_type": suggestion.problem_type,
            "suggestions": [
                {
                    "version": v.version,
                    "rewritten_text": v.rewritten_text,
                    "improvement": v.improvement
                }
                for v in suggestion.suggestions
            ]
        }
    
    def to_json(self, suggestions: List[Suggestion], indent: int = 2) -> str:
        """将建议列表转换为 JSON 字符串"""
        data = {
            "suggestions": [self.to_dict(s) for s in suggestions]
        }
        return json.dumps(data, ensure_ascii=False, indent=indent)


def create_suggester() -> OptimizationSuggester:
    """工厂函数：创建建议生成器实例"""
    return OptimizationSuggester()
