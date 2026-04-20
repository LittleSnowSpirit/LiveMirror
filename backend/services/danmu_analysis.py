"""
弹幕分析服务
提供情感分析、热度分析、关联分析等功能
"""
import re
import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from collections import defaultdict
import math


class DanmuAnalysisService:
    """弹幕分析服务"""
    
    def __init__(self):
        # 情感词典（简化版）
        self.positive_words = {
            '好', '棒', '赞', '喜欢', '爱', '开心', '高兴', '满意', '不错', '优秀',
            '精彩', '厉害', '牛逼', '666', '哈哈', '嘻嘻', 'wow', ' amazing',
            '购买', '下单', '值得', '推荐', '好用', '实惠', '划算', '便宜',
            '漂亮', '美丽', '帅', '酷', '完美', '优秀', '支持', '加油'
        }
        
        self.negative_words = {
            '差', '烂', '垃圾', '失望', '难过', '生气', '讨厌', '不好', '垃圾',
            '贵', '坑', '骗', '假', '质量差', '没用', '浪费', '后悔', '差评',
            '太贵', '买不起', '不值', '坑人', '忽悠', '虚假', '骗人'
        }
        
        self.question_words = {
            '吗', '呢', '什么', '怎么', '如何', '多少', '哪里', '哪个', '谁',
            '为什么', '请问', '求', '有没有', '是不是', '能不能', '可以吗'
        }
        
        self.climax_indicators = {
            '抢', '秒', '没', '抢到了', '手慢无', '没了', '售罄', '售罄',
            '太快了', '抢不到', '已拍', '已买', '下单了', '付款了'
        }
        
        self.controversy_indicators = {
            '假的', '骗人', '忽悠', '质量差', '不值', '坑', '别买', '避雷',
            '假的吧', '真的吗', '怀疑', '不可能', '假的吧'
        }
    
    def analyze_sentiment(self, content: str) -> Tuple[str, float]:
        """
        分析弹幕情感
        
        Args:
            content: 弹幕内容
            
        Returns:
            (情感类型，情感分数) 情感分数范围 -1.0 到 1.0
        """
        content_lower = content.lower()
        
        positive_count = 0
        negative_count = 0
        question_count = 0
        
        # 统计情感词
        for word in self.positive_words:
            if word in content_lower:
                positive_count += 1
        
        for word in self.negative_words:
            if word in content_lower:
                negative_count += 1
        
        # 检测疑问句
        for word in self.question_words:
            if word in content_lower:
                question_count += 1
        
        # 计算情感分数
        total = positive_count + negative_count + 1  # +1 避免除零
        sentiment_score = (positive_count - negative_count) / total
        
        # 限制在 -1 到 1 之间
        sentiment_score = max(-1.0, min(1.0, sentiment_score))
        
        # 确定情感类型
        if sentiment_score > 0.2:
            sentiment = "positive"
        elif sentiment_score < -0.2:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        # 如果是疑问句，调整为中性或负面（取决于上下文）
        if question_count > 0 and sentiment == "positive":
            sentiment = "neutral"
            sentiment_score = min(sentiment_score, 0.3)
        
        return sentiment, round(sentiment_score, 3)
    
    def classify_danmu_type(self, content: str, sentiment: str, sentiment_score: float) -> str:
        """
        分类弹幕类型
        
        Args:
            content: 弹幕内容
            sentiment: 情感类型
            sentiment_score: 情感分数
            
        Returns:
            弹幕类型：normal, highlight, controversy, question, praise
        """
        content_lower = content.lower()
        
        # 检测疑问句
        for word in self.question_words:
            if word in content_lower:
                return "question"
        
        # 检测高潮/抢购
        for word in self.climax_indicators:
            if word in content_lower:
                return "highlight"
        
        # 检测争议
        for word in self.controversy_indicators:
            if word in content_lower:
                return "controversy"
        
        # 检测赞赏
        if sentiment == "positive" and sentiment_score > 0.5:
            return "praise"
        
        return "normal"
    
    def detect_key_danmu(self, content: str, sentiment_score: float, timestamp: float) -> Tuple[bool, Optional[str]]:
        """
        检测关键弹幕
        
        Args:
            content: 弹幕内容
            sentiment_score: 情感分数
            timestamp: 时间戳
            
        Returns:
            (是否关键弹幕，关键类型)
        """
        content_lower = content.lower()
        
        # 检测高潮
        for word in self.climax_indicators:
            if word in content_lower:
                return True, "climax"
        
        # 检测争议
        for word in self.controversy_indicators:
            if word in content_lower:
                return True, "controversy"
        
        # 检测赞赏关键词
        praise_words = {'超级', '完美', '太棒了', '牛逼', '666', '厉害', '优秀'}
        for word in praise_words:
            if word in content_lower:
                return True, "praise"
        
        # 极端情感
        if abs(sentiment_score) > 0.8:
            if sentiment_score > 0:
                return True, "praise"
            else:
                return True, "controversy"
        
        return False, None
    
    def analyze_heatmap(self, danmus: List[Dict], interval_seconds: int = 30) -> List[Dict]:
        """
        分析弹幕热度时间轴
        
        Args:
            danmus: 弹幕列表（每个元素包含 timestamp 等字段）
            interval_seconds: 时间间隔（秒）
            
        Returns:
            热度时间轴数据
        """
        if not danmus:
            return []
        
        # 找到时间范围
        timestamps = [d.get('timestamp', 0) for d in danmus]
        min_time = min(timestamps)
        max_time = max(timestamps)
        
        # 按时间间隔分组
        heat_data = defaultdict(lambda: {
            'count': 0,
            'positive': 0,
            'negative': 0,
            'neutral': 0,
            'key_danmu_count': 0
        })
        
        for danmu in danmus:
            ts = danmu.get('timestamp', 0)
            # 计算所属区间
            interval_idx = int((ts - min_time) / interval_seconds)
            interval_start = min_time + interval_idx * interval_seconds
            
            heat_data[interval_start]['count'] += 1
            
            # 统计情感
            sentiment = danmu.get('sentiment', 'neutral')
            if sentiment in heat_data[interval_start]:
                heat_data[interval_start][sentiment] += 1
            
            # 统计关键弹幕
            if danmu.get('is_key_danmu', False):
                heat_data[interval_start]['key_danmu_count'] += 1
        
        # 转换为列表格式
        timeline = []
        for interval_start in sorted(heat_data.keys()):
            data = heat_data[interval_start]
            timeline.append({
                'timestamp': interval_start,
                'timestamp_str': self._format_timestamp(interval_start),
                'count': data['count'],
                'positive': data['positive'],
                'negative': data['negative'],
                'neutral': data['neutral'],
                'key_danmu_count': data['key_danmu_count'],
                'heat_level': self._calculate_heat_level(data['count'])
            })
        
        return timeline
    
    def _calculate_heat_level(self, count: int) -> str:
        """计算热度等级"""
        if count >= 50:
            return "very_high"
        elif count >= 30:
            return "high"
        elif count >= 15:
            return "medium"
        elif count >= 5:
            return "low"
        else:
            return "very_low"
    
    def _format_timestamp(self, seconds: float) -> str:
        """格式化时间戳为 MM:SS 格式"""
        minutes = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{minutes:02d}:{secs:02d}"
    
    def correlate_with_speech(self, danmus: List[Dict], speech_segments: List[Dict]) -> Dict[str, Any]:
        """
        分析弹幕与话术的关联
        
        Args:
            danmus: 弹幕列表（每个元素包含 timestamp 等字段）
            speech_segments: 话术片段列表（包含 segment_id, timestamp, speech_types 等）
            
        Returns:
            关联分析结果
        """
        if not danmus or not speech_segments:
            return {
                'total_danmus': len(danmus),
                'correlated_danmus': 0,
                'correlation_rate': 0.0,
                'by_speech_type': {},
                'top_interactive_segments': []
            }
        
        # 为每个弹幕分配话术片段
        correlated_count = 0
        by_speech_type = defaultdict(lambda: {
            'count': 0,
            'positive': 0,
            'negative': 0,
            'neutral': 0,
            'avg_sentiment_score': 0.0,
            'sentiment_scores': []
        })
        
        segment_interactions = defaultdict(int)
        
        for danmu in danmus:
            danmu_ts = danmu.get('timestamp', 0)
            speech_segment_id = danmu.get('speech_segment_id')
            
            # 如果没有直接关联，查找时间最近的话术片段
            if not speech_segment_id:
                for segment in speech_segments:
                    seg_ts = segment.get('timestamp', 0)
                    # 假设话术片段影响范围为前后 30 秒
                    if abs(danmu_ts - seg_ts) <= 30:
                        speech_segment_id = segment.get('segment_id')
                        break
            
            if speech_segment_id:
                correlated_count += 1
                segment_interactions[speech_segment_id] += 1
                
                # 查找话术类型
                for segment in speech_segments:
                    if segment.get('segment_id') == speech_segment_id:
                        speech_types = segment.get('speech_types', ['unknown'])
                        for st in speech_types:
                            by_speech_type[st]['count'] += 1
                            sentiment = danmu.get('sentiment', 'neutral')
                            if sentiment in ['positive', 'negative', 'neutral']:
                                by_speech_type[st][sentiment] += 1
                            by_speech_type[st]['sentiment_scores'].append(
                                danmu.get('sentiment_score', 0.0)
                            )
                        break
        
        # 计算平均情感分数
        for st in by_speech_type:
            scores = by_speech_type[st]['sentiment_scores']
            if scores:
                by_speech_type[st]['avg_sentiment_score'] = round(sum(scores) / len(scores), 3)
            del by_speech_type[st]['sentiment_scores']  # 移除临时数据
        
        # 找出互动最多的话术片段
        top_segments = sorted(
            segment_interactions.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        top_interactive_segments = [
            {
                'segment_id': seg_id,
                'interaction_count': count
            }
            for seg_id, count in top_segments
        ]
        
        return {
            'total_danmus': len(danmus),
            'correlated_danmus': correlated_count,
            'correlation_rate': round(correlated_count / len(danmus), 3) if danmus else 0.0,
            'by_speech_type': dict(by_speech_type),
            'top_interactive_segments': top_interactive_segments
        }
    
    def generate_summary(self, danmus: List[Dict]) -> Dict[str, Any]:
        """
        生成弹幕分析摘要
        
        Args:
            danmus: 弹幕列表
            
        Returns:
            分析摘要
        """
        if not danmus:
            return {
                'total_count': 0,
                'sentiment_distribution': {},
                'type_distribution': {},
                'key_danmu_count': 0,
                'avg_sentiment_score': 0.0,
                'time_range': {'start': 0, 'end': 0}
            }
        
        # 统计
        sentiment_dist = defaultdict(int)
        type_dist = defaultdict(int)
        key_count = 0
        sentiment_scores = []
        timestamps = []
        
        for danmu in danmus:
            sentiment = danmu.get('sentiment', 'neutral')
            sentiment_dist[sentiment] += 1
            
            danmu_type = danmu.get('danmu_type', 'normal')
            type_dist[danmu_type] += 1
            
            if danmu.get('is_key_danmu', False):
                key_count += 1
            
            sentiment_scores.append(danmu.get('sentiment_score', 0.0))
            timestamps.append(danmu.get('timestamp', 0))
        
        return {
            'total_count': len(danmus),
            'sentiment_distribution': dict(sentiment_dist),
            'type_distribution': dict(type_dist),
            'key_danmu_count': key_count,
            'avg_sentiment_score': round(sum(sentiment_scores) / len(sentiment_scores), 3) if sentiment_scores else 0.0,
            'time_range': {
                'start': min(timestamps) if timestamps else 0,
                'end': max(timestamps) if timestamps else 0,
                'duration': max(timestamps) - min(timestamps) if timestamps else 0
            }
        }
    
    def parse_csv(self, file_content: str) -> List[Dict]:
        """
        解析 CSV 格式的弹幕数据
        
        支持的列：timestamp, content, username, user_level, like_count, reply_count
        
        Args:
            file_content: CSV 文件内容
            
        Returns:
            弹幕数据列表
        """
        lines = file_content.strip().split('\n')
        if len(lines) < 2:
            return []
        
        # 解析表头
        headers = [h.strip().lower() for h in lines[0].split(',')]
        
        danmus = []
        for line in lines[1:]:
            if not line.strip():
                continue
            
            values = line.split(',')
            if len(values) != len(headers):
                continue
            
            danmu = {}
            for i, header in enumerate(headers):
                value = values[i].strip()
                
                if header == 'timestamp':
                    danmu['timestamp'] = float(value)
                elif header == 'content':
                    danmu['content'] = value
                elif header == 'username':
                    danmu['username'] = value
                elif header == 'user_level':
                    danmu['user_level'] = int(value) if value else 1
                elif header == 'like_count':
                    danmu['like_count'] = int(value) if value else 0
                elif header == 'reply_count':
                    danmu['reply_count'] = int(value) if value else 0
                else:
                    danmu[header] = value
            
            if 'content' in danmu and 'timestamp' in danmu:
                danmus.append(danmu)
        
        return danmus
    
    def parse_json(self, file_content: str) -> List[Dict]:
        """
        解析 JSON 格式的弹幕数据
        
        Args:
            file_content: JSON 文件内容
            
        Returns:
            弹幕数据列表
        """
        try:
            data = json.loads(file_content)
            
            # 支持数组或包含 danmus 键的对象
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and 'danmus' in data:
                return data['danmus']
            elif isinstance(data, dict) and 'data' in data:
                return data['data']
            else:
                return []
        except json.JSONDecodeError:
            return []


# 单例服务实例
_danmu_service = None

def get_danmu_service() -> DanmuAnalysisService:
    """获取弹幕分析服务单例"""
    global _danmu_service
    if _danmu_service is None:
        _danmu_service = DanmuAnalysisService()
    return _danmu_service
