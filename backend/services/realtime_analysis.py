"""
LiveMirror 实时分析服务
提供直播中的实时话术分析、情绪检测、建议推送功能
"""

import time
import threading
import re
from typing import Optional, Dict, List, Callable
from dataclasses import dataclass, field
from collections import deque
from datetime import datetime
import json


@dataclass
class AnalysisResult:
    """实时分析结果"""
    timestamp: float
    text: str
    sentiment: str  # positive, neutral, negative
    sentiment_score: float  # 0-1
    keywords: List[str]
    suggestions: List[str]
    risks: List[str]
    emotion_data: Dict[str, float] = field(default_factory=dict)
    latency_ms: float = 0


@dataclass
class StreamSession:
    """直播流会话"""
    session_id: str
    start_time: float
    last_activity: float
    total_text: str = ""
    segment_count: int = 0
    is_active: bool = True


class SentimentAnalyzer:
    """简单情绪分析器"""
    
    POSITIVE_WORDS = [
        '好', '棒', '优秀', '喜欢', '爱', '满意', '感谢', '欢迎',
        '推荐', '值得', '划算', '优惠', '福利', '惊喜', '开心',
        '美丽', '漂亮', '完美', '超值', '必买', '神器'
    ]
    
    NEGATIVE_WORDS = [
        '不好', '差', '失望', '讨厌', '贵', '坑', '垃圾', '浪费',
        '问题', '投诉', '退货', '差评', '避免', '小心', '注意'
    ]
    
    def __init__(self):
        self._positive_pattern = re.compile('|'.join(self.POSITIVE_WORDS))
        self._negative_pattern = re.compile('|'.join(self.NEGATIVE_WORDS))
    
    def analyze(self, text: str) -> Dict:
        """分析文本情绪"""
        positive_matches = len(self._positive_pattern.findall(text))
        negative_matches = len(self._negative_pattern.findall(text))
        
        total = positive_matches + negative_matches
        if total == 0:
            sentiment = 'neutral'
            score = 0.5
        else:
            ratio = positive_matches / total
            score = ratio
            if ratio > 0.6:
                sentiment = 'positive'
            elif ratio < 0.4:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
        
        emotions = {
            'joy': min(1.0, positive_matches * 0.2),
            'sadness': min(1.0, negative_matches * 0.15),
            'anger': min(1.0, negative_matches * 0.2),
            'surprise': 0.1,
            'neutral': 1.0 - (emotions['joy'] + emotions['sadness'] + emotions['anger']) / 3
        }
        
        return {
            'sentiment': sentiment,
            'score': round(score, 2),
            'emotions': {k: round(v, 2) for k, v in emotions.items()}
        }


class SuggestionEngine:
    """话术建议引擎"""
    
    def __init__(self):
        self.suggestion_rules = [
            {'pattern': r'(这个 | 那个 | 它)', 'suggestion': '尝试使用具体产品名称，增强观众记忆点', 'priority': 'low'},
            {'pattern': r'(可能 | 也许 | 大概)', 'suggestion': '使用更肯定的表达方式，增强说服力', 'priority': 'medium'},
            {'pattern': r'(\d+)(块 | 元 | 钱)', 'suggestion': '强调价格优势，如"仅需 XX 元"、"限时特价"', 'priority': 'high'},
            {'pattern': r'(好 | 棒 | 不错)$', 'suggestion': '补充具体优点，如"好在哪里"、"为什么棒"', 'priority': 'medium'},
            {'pattern': r'(买 | 下单 | 购买)', 'suggestion': '添加行动号召，如"立即下单"、"不要错过"', 'priority': 'high'}
        ]
    
    def get_suggestions(self, text: str) -> List[Dict]:
        """获取话术建议"""
        suggestions = []
        for rule in self.suggestion_rules:
            if re.search(rule['pattern'], text, re.IGNORECASE):
                suggestions.append({'text': rule['suggestion'], 'priority': rule['priority']})
        return suggestions
    
    def detect_risks(self, text: str) -> List[str]:
        """检测违规风险"""
        risks = []
        risk_patterns = [
            (r'最\w+', '避免使用绝对化用语'),
            (r'第一', '广告法禁止使用"第一"等绝对词'),
            (r'100%|百分百', '避免绝对化承诺'),
            (r'治疗 | 治愈 | 疗效', '医疗功效需谨慎表述'),
            (r'赚钱 | 暴利', '避免收益承诺')
        ]
        
        for pattern, warning in risk_patterns:
            if re.search(pattern, text):
                risks.append(warning)
        
        return risks


class KeywordExtractor:
    """关键词提取器"""
    
    def __init__(self):
        self.categories = {
            'product': ['产品', '商品', '宝贝', '好物', '神器'],
            'price': ['价格', '优惠', '折扣', '特价', '福利'],
            'action': ['购买', '下单', '点击', '关注', '分享'],
            'urgency': ['限时', '限量', '最后', '赶紧', '马上']
        }
    
    def extract(self, text: str, top_k: int = 5) -> List[str]:
        """提取关键词"""
        keywords = []
        for category, words in self.categories.items():
            for word in words:
                if word in text:
                    keywords.append(word)
        return list(set(keywords))[:top_k]


class RealtimeAnalysisService:
    """实时分析服务"""
    
    def __init__(self, max_latency_ms: int = 3000):
        self.max_latency_ms = max_latency_ms
        self.sentiment_analyzer = SentimentAnalyzer()
        self.suggestion_engine = SuggestionEngine()
        self.keyword_extractor = KeywordExtractor()
        self.sessions: Dict[str, StreamSession] = {}
        self._lock = threading.Lock()
        self._result_callbacks: List[Callable] = []
        self._stats = {'total_analyses': 0, 'avg_latency_ms': 0, 'latencies': deque(maxlen=100)}
    
    def create_session(self, session_id: str) -> StreamSession:
        """创建新的流会话"""
        session = StreamSession(session_id=session_id, start_time=time.time(), last_activity=time.time())
        with self._lock:
            self.sessions[session_id] = session
        return session
    
    def close_session(self, session_id: str):
        """关闭会话"""
        with self._lock:
            if session_id in self.sessions:
                self.sessions[session_id].is_active = False
                del self.sessions[session_id]
    
    def analyze_segment(self, session_id: str, text: str, audio_duration_ms: float = 0) -> AnalysisResult:
        """分析语音片段"""
        start_time = time.time()
        
        with self._lock:
            if session_id not in self.sessions:
                self.create_session(session_id)
            session = self.sessions[session_id]
            session.last_activity = time.time()
            session.total_text += text + " "
            session.segment_count += 1
        
        sentiment_result = self.sentiment_analyzer.analyze(text)
        keywords = self.keyword_extractor.extract(text)
        suggestions = self.suggestion_engine.get_suggestions(text)
        risks = self.suggestion_engine.detect_risks(text)
        
        analysis_time = (time.time() - start_time) * 1000
        total_latency = analysis_time + audio_duration_ms
        
        result = AnalysisResult(
            timestamp=time.time(),
            text=text,
            sentiment=sentiment_result['sentiment'],
            sentiment_score=sentiment_result['score'],
            keywords=keywords,
            suggestions=[s['text'] for s in suggestions],
            risks=risks,
            emotion_data=sentiment_result['emotions'],
            latency_ms=round(total_latency, 2)
        )
        
        self._update_stats(total_latency)
        self._notify_callbacks(result)
        
        return result
    
    def _update_stats(self, latency_ms: float):
        """更新性能统计"""
        self._stats['total_analyses'] += 1
        self._stats['latencies'].append(latency_ms)
        if self._stats['latencies']:
            self._stats['avg_latency_ms'] = sum(self._stats['latencies']) / len(self._stats['latencies'])
    
    def register_callback(self, callback: Callable[[AnalysisResult], None]):
        """注册结果回调"""
        self._result_callbacks.append(callback)
    
    def _notify_callbacks(self, result: AnalysisResult):
        """通知所有回调"""
        for callback in self._result_callbacks:
            try:
                callback(result)
            except Exception as e:
                print(f"[ERROR] 回调执行失败：{e}")
    
    def get_session_stats(self, session_id: str) -> Dict:
        """获取会话统计"""
        with self._lock:
            if session_id not in self.sessions:
                return {'error': 'Session not found'}
            session = self.sessions[session_id]
            duration = time.time() - session.start_time
            return {
                'session_id': session_id,
                'duration_seconds': round(duration, 2),
                'segment_count': session.segment_count,
                'total_text_length': len(session.total_text),
                'is_active': session.is_active
            }
    
    def get_performance_stats(self) -> Dict:
        """获取性能统计"""
        return {
            'total_analyses': self._stats['total_analyses'],
            'avg_latency_ms': round(self._stats['avg_latency_ms'], 2),
            'max_latency_ms': self.max_latency_ms,
            'active_sessions': len([s for s in self.sessions.values() if s.is_active])
        }


_service_instance: Optional[RealtimeAnalysisService] = None


def get_analysis_service() -> RealtimeAnalysisService:
    """获取全局分析服务实例"""
    global _service_instance
    if _service_instance is None:
        _service_instance = RealtimeAnalysisService()
    return _service_instance


def analyze_text(session_id: str, text: str) -> AnalysisResult:
    """便捷分析函数"""
    service = get_analysis_service()
    return service.analyze_segment(session_id, text)


if __name__ == "__main__":
    print("="*60)
    print("实时分析服务测试")
    print("="*60)
    
    service = get_analysis_service()
    test_texts = [
        "大家好，欢迎来到直播间！",
        "今天给大家带来超值福利。",
        "这个产品非常好用，价格也很优惠。",
        "限时限量，赶紧下单不要错过！"
    ]
    
    session_id = "test_session_001"
    latencies = []
    
    for i, text in enumerate(test_texts, 1):
        start = time.time()
        result = service.analyze_segment(session_id, text, audio_duration_ms=2000)
        latency = (time.time() - start) * 1000
        latencies.append(latency)
        
        print(f"\n片段 {i}:")
        print(f"  文本：{text}")
        print(f"  情绪：{result.sentiment} ({result.sentiment_score})")
        print(f"  延迟：{latency:.2f}ms")
        if result.suggestions:
            print(f"  建议：{result.suggestions[0]}")
        if result.risks:
            print(f"  风险：{result.risks[0]}")
    
    avg_latency = sum(latencies) / len(latencies)
    print(f"\n{'='*60}")
    print(f"平均延迟：{avg_latency:.2f}ms")
    print(f"测试完成！")
