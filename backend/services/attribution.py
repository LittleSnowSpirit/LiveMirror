"""
话术 - 数据归因分析服务 - LiveMirror 核心功能

核心问题：哪些话术导致了观众情绪高峰/互动高峰？

归因维度：
1. 时间关联 - 话术与情绪/弹幕峰值的时间相关性
2. 语义关联 - 话术内容与观众反馈的语义相关性
3. 转化关联 - 话术与后续转化行为的相关性
"""

import json
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from collections import defaultdict
import math
from dataclasses import dataclass, asdict


@dataclass
class AttributionResult:
    """归因分析结果"""
    speech_id: str
    speech_type: str
    speech_content: str
    start_time: float
    end_time: float
    
    # 归因指标
    emotion_impact: float = 0.0  # 情绪影响分数 (0-1)
    engagement_impact: float = 0.0  # 互动影响分数 (0-1)
    conversion_impact: float = 0.0  # 转化影响分数 (0-1)
    
    # 综合评分
    overall_score: float = 0.0  # 综合归因分数 (0-100)
    confidence: float = 0.0  # 归因置信度 (0-1)
    
    # 归因详情
    peak_correlation: Optional[Dict] = None  # 峰值关联详情
    danmu_correlation: Optional[Dict] = None  # 弹幕关联详情
    
    # 问题诊断
    issues: List[str] = None
    suggestions: List[str] = None
    
    def __post_init__(self):
        if self.issues is None:
            self.issues = []
        if self.suggestions is None:
            self.suggestions = []


class AttributionAnalysisService:
    """话术归因分析服务"""
    
    def __init__(self):
        # 情绪峰值检测阈值
        self.emotion_peak_threshold = 0.7  # 情绪分数阈值
        self.peak_window_seconds = 30  # 峰值检测窗口（秒）
        
        # 归因权重
        self.weights = {
            'emotion': 0.4,      # 情绪影响权重
            'engagement': 0.4,   # 互动影响权重
            'conversion': 0.2    # 转化影响权重
        }
    
    def detect_emotion_peaks(
        self, 
        emotion_curve: List[Dict[str, Any]], 
        window_seconds: int = 30
    ) -> List[Dict[str, Any]]:
        """
        检测情绪曲线中的显著峰值
        
        Args:
            emotion_curve: 情绪曲线数据 [{"timestamp": 10.5, "score": 0.8, "level": "high"}, ...]
            window_seconds: 峰值检测窗口（秒）
            
        Returns:
            峰值列表 [{"timestamp": 15.0, "score": 0.95, "duration": 10}, ...]
        """
        if not emotion_curve:
            return []
        
        peaks = []
        sorted_curve = sorted(emotion_curve, key=lambda x: x.get('timestamp', 0))
        
        # 滑动窗口检测峰值
        window_size = max(1, window_seconds // 10)  # 假设每 10 秒一个数据点
        
        for i in range(len(sorted_curve)):
            current_point = sorted_curve[i]
            current_score = current_point.get('score', 0)
            
            # 检查是否超过阈值
            if current_score < self.emotion_peak_threshold:
                continue
            
            # 检查是否是局部最大值
            start_idx = max(0, i - window_size // 2)
            end_idx = min(len(sorted_curve), i + window_size // 2)
            
            window_scores = [
                sorted_curve[j].get('score', 0) 
                for j in range(start_idx, end_idx)
            ]
            
            if current_score >= max(window_scores):
                # 计算峰值持续时间
                duration = self._estimate_peak_duration(
                    sorted_curve, i, window_size
                )
                
                peaks.append({
                    'timestamp': current_point.get('timestamp', 0),
                    'score': current_score,
                    'duration': duration,
                    'level': self._classify_peak_level(current_score)
                })
        
        # 去重（合并时间接近的峰值）
        peaks = self._merge_nearby_peaks(peaks, min_gap=15)
        
        return peaks
    
    def _estimate_peak_duration(
        self, 
        curve: List[Dict], 
        peak_idx: int, 
        window_size: int
    ) -> float:
        """估算峰值持续时间"""
        if not curve or peak_idx >= len(curve):
            return 0
        
        peak_time = curve[peak_idx].get('timestamp', 0)
        peak_score = curve[peak_idx].get('score', 0)
        
        # 向前查找
        start_time = peak_time
        for i in range(peak_idx, -1, -1):
            if curve[i].get('score', 0) < peak_score * 0.5:
                break
            start_time = curve[i].get('timestamp', start_time)
        
        # 向后查找
        end_time = peak_time
        for i in range(peak_idx, len(curve)):
            if curve[i].get('score', 0) < peak_score * 0.5:
                break
            end_time = curve[i].get('timestamp', end_time)
        
        return max(0, end_time - start_time)
    
    def _classify_peak_level(self, score: float) -> str:
        """分类峰值等级"""
        if score >= 0.9:
            return "very_high"
        elif score >= 0.8:
            return "high"
        elif score >= 0.7:
            return "medium"
        else:
            return "low"
    
    def _merge_nearby_peaks(
        self, 
        peaks: List[Dict], 
        min_gap: float = 15.0
    ) -> List[Dict]:
        """合并时间接近的峰值"""
        if not peaks:
            return []
        
        sorted_peaks = sorted(peaks, key=lambda x: x['timestamp'])
        merged = [sorted_peaks[0]]
        
        for peak in sorted_peaks[1:]:
            last_peak = merged[-1]
            time_gap = peak['timestamp'] - last_peak['timestamp']
            
            if time_gap < min_gap:
                # 合并峰值（取最高分）
                if peak['score'] > last_peak['score']:
                    last_peak['timestamp'] = peak['timestamp']
                    last_peak['score'] = peak['score']
                    last_peak['duration'] = peak['duration']
                    last_peak['level'] = peak['level']
            else:
                merged.append(peak)
        
        return merged
    
    def correlate_speech_with_emotion(
        self,
        speech_segments: List[Dict[str, Any]],
        emotion_peaks: List[Dict[str, Any]],
        emotion_curve: List[Dict[str, Any]]
    ) -> List[AttributionResult]:
        """
        关联话术与情绪峰值
        
        Args:
            speech_segments: 话术分段 [{"id": "1", "type": "opening", "content": "...", "start": 0, "end": 30}, ...]
            emotion_peaks: 情绪峰值列表
            emotion_curve: 完整情绪曲线
            
        Returns:
            归因分析结果列表
        """
        results = []
        
        for speech in speech_segments:
            speech_start = speech.get('start_time', 0)
            speech_end = speech.get('end_time', 0)
            speech_mid = (speech_start + speech_end) / 2
            
            # 计算情绪影响分数
            emotion_impact = self._calculate_emotion_impact(
                speech_start, speech_end, emotion_peaks, emotion_curve
            )
            
            # 创建归因结果
            result = AttributionResult(
                speech_id=speech.get('id', ''),
                speech_type=speech.get('type', 'unknown'),
                speech_content=speech.get('content', '')[:100],  # 截断
                start_time=speech_start,
                end_time=speech_end,
                emotion_impact=emotion_impact
            )
            
            # 诊断问题
            if emotion_impact < 0.3:
                result.issues.append("情绪影响力较低")
                result.suggestions.append("尝试增加情感表达或互动元素")
            
            results.append(result)
        
        return results
    
    def _calculate_emotion_impact(
        self,
        speech_start: float,
        speech_end: float,
        emotion_peaks: List[Dict],
        emotion_curve: List[Dict]
    ) -> float:
        """
        计算话术的情绪影响分数
        
        考虑因素：
        1. 话术期间的情绪平均值
        2. 话术后 30 秒内是否出现峰值
        3. 情绪上升趋势
        """
        # 1. 话术期间平均情绪
        speech_emotions = [
            p.get('score', 0) for p in emotion_curve
            if speech_start <= p.get('timestamp', 0) <= speech_end
        ]
        
        avg_emotion = sum(speech_emotions) / len(speech_emotions) if speech_emotions else 0
        
        # 2. 话术后峰值检测（延迟效应）
        post_window_start = speech_end
        post_window_end = speech_end + 30  # 30 秒延迟窗口
        
        post_peaks = [
            p for p in emotion_peaks
            if post_window_start <= p['timestamp'] <= post_window_end
        ]
        
        peak_bonus = 0
        if post_peaks:
            max_peak = max(post_peaks, key=lambda x: x['score'])
            peak_bonus = max_peak['score'] * 0.3  # 峰值奖励
        
        # 3. 情绪趋势（话术期间是否上升）
        trend_score = self._calculate_emotion_trend(
            emotion_curve, speech_start, speech_end
        )
        
        # 综合计算
        impact = (avg_emotion * 0.5) + peak_bonus + (trend_score * 0.2)
        
        return min(1.0, max(0.0, impact))
    
    def _calculate_emotion_trend(
        self,
        curve: List[Dict],
        start: float,
        end: float
    ) -> float:
        """计算情绪趋势（上升/下降）"""
        start_emotions = [
            p.get('score', 0) for p in curve
            if start <= p.get('timestamp', 0) <= start + (end - start) / 2
        ]
        
        end_emotions = [
            p.get('score', 0) for p in curve
            if start + (end - start) / 2 < p.get('timestamp', 0) <= end
        ]
        
        if not start_emotions or not end_emotions:
            return 0
        
        avg_start = sum(start_emotions) / len(start_emotions)
        avg_end = sum(end_emotions) / len(end_emotions)
        
        # 归一化到 0-1
        trend = (avg_end - avg_start + 1) / 2
        return min(1.0, max(0.0, trend))
    
    def correlate_speech_with_danmu(
        self,
        speech_segments: List[Dict[str, Any]],
        danmu_list: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        关联话术与弹幕互动
        
        Args:
            speech_segments: 话术分段
            danmu_list: 弹幕列表 [{"timestamp": 10.5, "content": "...", "sentiment": "positive"}, ...]
            
        Returns:
            话术 ID -> 弹幕关联统计
        """
        correlation = {}
        
        for speech in speech_segments:
            speech_id = speech.get('id', '')
            speech_start = speech.get('start_time', 0)
            speech_end = speech.get('end_time', 0)
            
            # 统计话术期间的弹幕
            related_danmus = [
                d for d in danmu_list
                if speech_start <= d.get('timestamp', 0) <= speech_end
            ]
            
            # 计算互动指标
            total_count = len(related_danmus)
            positive_count = sum(1 for d in related_danmus if d.get('sentiment') == 'positive')
            negative_count = sum(1 for d in related_danmus if d.get('sentiment') == 'negative')
            key_danmu_count = sum(1 for d in related_danmus if d.get('is_key_danmu', False))
            
            # 互动率（弹幕数 / 话术时长）
            duration = max(1, speech_end - speech_start)
            engagement_rate = total_count / duration * 60  # 每分钟弹幕数
            
            correlation[speech_id] = {
                'total_count': total_count,
                'positive_count': positive_count,
                'negative_count': negative_count,
                'key_danmu_count': key_danmu_count,
                'engagement_rate': round(engagement_rate, 2),
                'positive_ratio': round(positive_count / total_count, 2) if total_count > 0 else 0
            }
        
        return correlation
    
    def generate_attribution_report(
        self,
        speech_segments: List[Dict[str, Any]],
        emotion_curve: List[Dict[str, Any]],
        danmu_list: List[Dict[str, Any]],
        top_n: int = 10
    ) -> Dict[str, Any]:
        """
        生成完整的归因分析报告
        
        Args:
            speech_segments: 话术分段
            emotion_curve: 情绪曲线
            danmu_list: 弹幕列表
            top_n: 返回 Top N 个高影响力话术
            
        Returns:
            归因分析报告
        """
        # 1. 检测情绪峰值
        emotion_peaks = self.detect_emotion_peaks(emotion_curve)
        
        # 2. 话术 - 情绪关联
        emotion_results = self.correlate_speech_with_emotion(
            speech_segments, emotion_peaks, emotion_curve
        )
        
        # 3. 话术 - 弹幕关联
        danmu_correlation = self.correlate_speech_with_danmu(
            speech_segments, danmu_list
        )
        
        # 4. 计算综合评分
        for result in emotion_results:
            # 获取弹幕关联数据
            danmu_stats = danmu_correlation.get(result.speech_id, {})
            
            # 互动影响分数
            engagement_rate = danmu_stats.get('engagement_rate', 0)
            result.engagement_impact = min(1.0, engagement_rate / 10)  # 归一化
            
            # 综合评分
            result.overall_score = (
                result.emotion_impact * self.weights['emotion'] * 100 +
                result.engagement_impact * self.weights['engagement'] * 100
            )
            
            # 置信度（基于数据量）
            danmu_count = danmu_stats.get('total_count', 0)
            result.confidence = min(1.0, danmu_count / 20)  # 20 条弹幕为满分置信度
        
        # 5. 排序并取 Top N
        sorted_results = sorted(
            emotion_results, 
            key=lambda x: x.overall_score, 
            reverse=True
        )[:top_n]
        
        # 6. 生成报告
        report = {
            'summary': {
                'total_speech_segments': len(speech_segments),
                'emotion_peaks_count': len(emotion_peaks),
                'total_danmus': len(danmu_list),
                'analysis_timestamp': datetime.now().isoformat()
            },
            'top_speeches': [
                {
                    'speech_id': r.speech_id,
                    'speech_type': r.speech_type,
                    'speech_content': r.speech_content,
                    'start_time': r.start_time,
                    'end_time': r.end_time,
                    'overall_score': round(r.overall_score, 2),
                    'emotion_impact': round(r.emotion_impact, 3),
                    'engagement_impact': round(r.engagement_impact, 3),
                    'confidence': round(r.confidence, 3),
                    'issues': r.issues,
                    'suggestions': r.suggestions
                }
                for r in sorted_results
            ],
            'emotion_peaks': emotion_peaks,
            'recommendations': self._generate_recommendations(sorted_results)
        }
        
        return report
    
    def _generate_recommendations(
        self, 
        results: List[AttributionResult]
    ) -> List[Dict[str, str]]:
        """生成优化建议"""
        recommendations = []
        
        # 分析 Top 表现话术
        top_performers = [r for r in results if r.overall_score >= 70]
        low_performers = [r for r in results if r.overall_score < 40]
        
        if top_performers:
            best = top_performers[0]
            recommendations.append({
                'type': 'keep_doing',
                'priority': 'high',
                'title': f'保持{best.speech_type}的话术风格',
                'description': f'这类话术情绪影响分数达到{best.emotion_impact:.2f}，观众反响很好',
                'example': best.speech_content
            })
        
        if low_performers:
            recommendations.append({
                'type': 'improve',
                'priority': 'medium',
                'title': '优化低影响力话术',
                'description': f'发现{len(low_performers)}个话术片段影响力较低，建议增加互动或情感表达',
                'example': None
            })
        
        return recommendations


# 便捷函数
def analyze_attribution(
    speech_segments: List[Dict],
    emotion_curve: List[Dict],
    danmu_list: List[Dict],
    top_n: int = 10
) -> Dict[str, Any]:
    """
    便捷函数：执行完整的归因分析
    
    Args:
        speech_segments: 话术分段数据
        emotion_curve: 情绪曲线数据
        danmu_list: 弹幕数据
        top_n: 返回 Top N 个结果
        
    Returns:
        归因分析报告
    """
    service = AttributionAnalysisService()
    return service.generate_attribution_report(
        speech_segments, emotion_curve, danmu_list, top_n
    )
