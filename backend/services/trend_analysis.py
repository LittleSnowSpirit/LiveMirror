"""
跨场次趋势分析服务 - LiveMirror 核心功能

核心能力：
1. 跨场次数据对比
2. 情绪/话术/互动趋势分析
3. 进步/退步识别
4. 成长报告生成
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import math


@dataclass
class SessionMetrics:
    """单场次指标"""
    session_id: str
    anchor_time: datetime
    duration_minutes: int
    viewer_count: int
    danmu_count: int
    avg_emotion_score: float
    peak_emotion_score: float
    engagement_rate: float
    overall_score: float
    
    # 话术质量分（按类型，带默认值）
    opening_score: Optional[float] = None
    product_intro_score: Optional[float] = None
    price_promotion_score: Optional[float] = None
    closing_score: Optional[float] = None


@dataclass
class TrendPoint:
    """趋势数据点"""
    session_id: str
    time: datetime
    value: float
    label: str


@dataclass
class TrendAnalysis:
    """趋势分析结果"""
    direction: str  # up, down, stable
    change_rate: float  # 变化率
    significance: str  # significant, moderate, slight
    description: str


@dataclass
class GrowthReport:
    """成长报告"""
    period_start: datetime
    period_end: datetime
    total_sessions: int
    
    # 整体趋势
    overall_trend: TrendAnalysis
    
    # 各方面趋势
    emotion_trend: TrendAnalysis
    engagement_trend: TrendAnalysis
    speech_quality_trend: TrendAnalysis
    
    # 进步最大的方面
    top_improvements: List[Dict[str, Any]]
    
    # 需要改进的方面
    areas_to_work_on: List[Dict[str, Any]]
    
    # 总结建议
    summary: str
    recommendations: List[str]


class TrendAnalysisService:
    """趋势分析服务"""
    
    def __init__(self):
        # 趋势判断阈值
        self.thresholds = {
            'significant_up': 0.15,      # 显著提升 15%
            'significant_down': -0.15,   # 显著下降 -15%
            'moderate_up': 0.05,         # 中等提升 5%
            'moderate_down': -0.05       # 中等下降 -5%
        }
    
    def calculate_trend(
        self,
        values: List[float],
        labels: Optional[List[str]] = None
    ) -> TrendAnalysis:
        """
        计算趋势（上升/下降/平稳）
        
        Args:
            values: 数值序列
            labels: 标签（用于描述）
            
        Returns:
            趋势分析结果
        """
        if len(values) < 2:
            return TrendAnalysis(
                direction='stable',
                change_rate=0,
                significance='slight',
                description='数据不足，无法判断趋势'
            )
        
        # 计算首尾对比
        first_half = values[:len(values)//2]
        second_half = values[len(values)//2:]
        
        avg_first = sum(first_half) / len(first_half)
        avg_second = sum(second_half) / len(second_half)
        
        if avg_first == 0:
            change_rate = 0
        else:
            change_rate = (avg_second - avg_first) / avg_first
        
        # 判断趋势方向
        if change_rate > self.thresholds['significant_up']:
            direction = 'up'
            significance = 'significant'
        elif change_rate > self.thresholds['moderate_up']:
            direction = 'up'
            significance = 'moderate'
        elif change_rate > 0:
            direction = 'up'
            significance = 'slight'
        elif change_rate < self.thresholds['significant_down']:
            direction = 'down'
            significance = 'significant'
        elif change_rate < self.thresholds['moderate_down']:
            direction = 'down'
            significance = 'moderate'
        else:
            direction = 'stable'
            significance = 'slight'
        
        # 生成描述
        description = self._generate_trend_description(
            direction, significance, change_rate, labels
        )
        
        return TrendAnalysis(
            direction=direction,
            change_rate=change_rate,
            significance=significance,
            description=description
        )
    
    def _generate_trend_description(
        self,
        direction: str,
        significance: str,
        change_rate: float,
        labels: Optional[List[str]] = None
    ) -> str:
        """生成趋势描述"""
        direction_map = {
            'up': '上升',
            'down': '下降',
            'stable': '平稳'
        }
        
        significance_map = {
            'significant': '显著',
            'moderate': '中等',
            'slight': '轻微'
        }
        
        direction_cn = direction_map.get(direction, '未知')
        significance_cn = significance_map.get(significance, '')
        
        change_percent = abs(change_rate * 100)
        
        if direction == 'stable':
            return f'整体保持{significance_cn}，波动幅度在{change_percent:.1f}%以内'
        else:
            return f'{direction_cn}{significance_cn}，变化幅度{change_percent:.1f}%'
    
    def detect_significant_changes(
        self,
        values: List[float],
        threshold: float = 0.2
    ) -> List[Dict[str, Any]]:
        """
        检测显著变化点
        
        Args:
            values: 数值序列
            threshold: 变化阈值（默认 20%）
            
        Returns:
            显著变化点列表
        """
        changes = []
        
        for i in range(1, len(values)):
            if values[i-1] == 0:
                continue
            
            change_rate = (values[i] - values[i-1]) / values[i-1]
            
            if abs(change_rate) >= threshold:
                changes.append({
                    'index': i,
                    'from_value': values[i-1],
                    'to_value': values[i],
                    'change_rate': change_rate,
                    'direction': 'up' if change_rate > 0 else 'down',
                    'severity': 'high' if abs(change_rate) > 0.4 else 'medium'
                })
        
        return changes
    
    def analyze_emotion_trend(
        self,
        sessions: List[SessionMetrics]
    ) -> Dict[str, Any]:
        """
        分析情绪趋势
        
        Args:
            sessions: 场次指标列表
            
        Returns:
            情绪趋势分析
        """
        if not sessions:
            return {'error': '无数据'}
        
        # 按时间排序
        sorted_sessions = sorted(sessions, key=lambda s: s.anchor_time)
        
        # 提取情绪分数
        avg_scores = [s.avg_emotion_score for s in sorted_sessions]
        peak_scores = [s.peak_emotion_score for s in sorted_sessions]
        
        # 计算趋势
        avg_trend = self.calculate_trend(avg_scores)
        peak_trend = self.calculate_trend(peak_scores)
        
        # 检测显著变化
        significant_changes = self.detect_significant_changes(avg_scores)
        
        return {
            'avg_emotion': {
                'values': avg_scores,
                'trend': asdict(avg_trend),
                'latest': avg_scores[-1] if avg_scores else 0
            },
            'peak_emotion': {
                'values': peak_scores,
                'trend': asdict(peak_trend),
                'latest': peak_scores[-1] if peak_scores else 0
            },
            'significant_changes': significant_changes,
            'sessions_count': len(sorted_sessions)
        }
    
    def analyze_speech_quality_trend(
        self,
        sessions: List[SessionMetrics]
    ) -> Dict[str, Any]:
        """
        分析话术质量趋势
        
        Args:
            sessions: 场次指标列表
            
        Returns:
            话术质量趋势分析
        """
        if not sessions:
            return {'error': '无数据'}
        
        sorted_sessions = sorted(sessions, key=lambda s: s.anchor_time)
        
        # 提取各类话术分数
        speech_types = {
            'opening': [],
            'product_intro': [],
            'price_promotion': [],
            'closing': []
        }
        
        for session in sorted_sessions:
            if session.opening_score is not None:
                speech_types['opening'].append(session.opening_score)
            if session.product_intro_score is not None:
                speech_types['product_intro'].append(session.product_intro_score)
            if session.price_promotion_score is not None:
                speech_types['price_promotion'].append(session.price_promotion_score)
            if session.closing_score is not None:
                speech_types['closing'].append(session.closing_score)
        
        # 计算各类话术趋势
        trends = {}
        for speech_type, scores in speech_types.items():
            if scores:
                trend = self.calculate_trend(scores)
                trends[speech_type] = {
                    'values': scores,
                    'trend': asdict(trend),
                    'latest': scores[-1] if scores else 0,
                    'avg': sum(scores) / len(scores)
                }
        
        return {
            'by_type': trends,
            'sessions_count': len(sorted_sessions)
        }
    
    def analyze_engagement_trend(
        self,
        sessions: List[SessionMetrics]
    ) -> Dict[str, Any]:
        """
        分析互动趋势
        
        Args:
            sessions: 场次指标列表
            
        Returns:
            互动趋势分析
        """
        if not sessions:
            return {'error': '无数据'}
        
        sorted_sessions = sorted(sessions, key=lambda s: s.anchor_time)
        
        # 提取互动率
        engagement_rates = [s.engagement_rate for s in sorted_sessions]
        danmu_counts = [s.danmu_count for s in sorted_sessions]
        
        # 计算趋势
        rate_trend = self.calculate_trend(engagement_rates)
        
        return {
            'engagement_rate': {
                'values': engagement_rates,
                'trend': asdict(rate_trend),
                'latest': engagement_rates[-1] if engagement_rates else 0
            },
            'danmu_count': {
                'values': danmu_counts,
                'avg': sum(danmu_counts) / len(danmu_counts) if danmu_counts else 0
            },
            'sessions_count': len(sorted_sessions)
        }
    
    def generate_growth_report(
        self,
        sessions: List[SessionMetrics]
    ) -> GrowthReport:
        """
        生成成长报告
        
        Args:
            sessions: 场次指标列表
            
        Returns:
            成长报告
        """
        if not sessions:
            raise ValueError("至少需要一场直播数据")
        
        # 按时间排序
        sorted_sessions = sorted(sessions, key=lambda s: s.anchor_time)
        
        # 计算各方面趋势
        emotion_analysis = self.analyze_emotion_trend(sorted_sessions)
        speech_analysis = self.analyze_speech_quality_trend(sorted_sessions)
        engagement_analysis = self.analyze_engagement_trend(sorted_sessions)
        
        # 计算整体趋势（综合评分）
        overall_scores = [s.overall_score for s in sorted_sessions]
        overall_trend = self.calculate_trend(overall_scores)
        
        # 识别进步最大的方面
        improvements = self._identify_improvements(
            emotion_analysis, speech_analysis, engagement_analysis
        )
        
        # 识别需要改进的方面
        areas_to_work = self._identify_areas_to_work(
            emotion_analysis, speech_analysis, engagement_analysis
        )
        
        # 生成总结和建议
        summary = self._generate_summary(overall_trend, improvements)
        recommendations = self._generate_recommendations(areas_to_work)
        
        return GrowthReport(
            period_start=sorted_sessions[0].anchor_time,
            period_end=sorted_sessions[-1].anchor_time,
            total_sessions=len(sorted_sessions),
            overall_trend=overall_trend,
            emotion_trend=emotion_analysis.get('avg_emotion', {}).get('trend', {}),
            engagement_trend=engagement_analysis.get('engagement_rate', {}).get('trend', {}),
            speech_quality_trend=speech_analysis,
            top_improvements=improvements,
            areas_to_work_on=areas_to_work,
            summary=summary,
            recommendations=recommendations
        )
    
    def _identify_improvements(
        self,
        emotion: Dict,
        speech: Dict,
        engagement: Dict
    ) -> List[Dict[str, Any]]:
        """识别进步最大的方面"""
        improvements = []
        
        # 情绪趋势
        if 'trend' in emotion.get('avg_emotion', {}):
            emotion_trend = emotion['avg_emotion']['trend']
            if emotion_trend.get('direction') == 'up':
                improvements.append({
                    'aspect': '情绪调动能力',
                    'change_rate': emotion_trend.get('change_rate', 0),
                    'description': f'情绪影响{emotion_trend.get("description", "")}'
                })
        
        # 话术趋势
        for speech_type, data in speech.get('by_type', {}).items():
            if data.get('trend', {}).get('direction') == 'up':
                type_names = {
                    'opening': '开场白',
                    'product_intro': '产品介绍',
                    'price_promotion': '价格优惠',
                    'closing': '促单成交'
                }
                improvements.append({
                    'aspect': f'{type_names.get(speech_type, speech_type)}话术',
                    'change_rate': data['trend'].get('change_rate', 0),
                    'description': f'话术质量{data["trend"].get("description", "")}'
                })
        
        # 互动趋势
        if 'trend' in engagement.get('engagement_rate', {}):
            engagement_trend = engagement['engagement_rate']['trend']
            if engagement_trend.get('direction') == 'up':
                improvements.append({
                    'aspect': '观众互动',
                    'change_rate': engagement_trend.get('change_rate', 0),
                    'description': f'互动率{engagement_trend.get("description", "")}'
                })
        
        # 按变化率排序
        improvements.sort(key=lambda x: x.get('change_rate', 0), reverse=True)
        
        return improvements[:3]  # 返回 Top 3
    
    def _identify_areas_to_work(
        self,
        emotion: Dict,
        speech: Dict,
        engagement: Dict
    ) -> List[Dict[str, Any]]:
        """识别需要改进的方面"""
        areas = []
        
        # 情绪趋势
        if 'trend' in emotion.get('avg_emotion', {}):
            emotion_trend = emotion['avg_emotion']['trend']
            if emotion_trend.get('direction') in ['down', 'stable']:
                areas.append({
                    'aspect': '情绪调动能力',
                    'severity': 'high' if emotion_trend.get('direction') == 'down' else 'medium',
                    'description': f'情绪表现{emotion_trend.get("description", "")}，需要加强'
                })
        
        # 话术趋势
        for speech_type, data in speech.get('by_type', {}).items():
            if data.get('trend', {}).get('direction') in ['down', 'stable']:
                type_names = {
                    'opening': '开场白',
                    'product_intro': '产品介绍',
                    'price_promotion': '价格优惠',
                    'closing': '促单成交'
                }
                areas.append({
                    'aspect': f'{type_names.get(speech_type, speech_type)}话术',
                    'severity': 'medium',
                    'description': f'话术质量{data["trend"].get("description", "")}'
                })
        
        # 互动趋势
        if 'trend' in engagement.get('engagement_rate', {}):
            engagement_trend = engagement['engagement_rate']['trend']
            if engagement_trend.get('direction') in ['down', 'stable']:
                areas.append({
                    'aspect': '观众互动',
                    'severity': 'medium',
                    'description': f'互动率{engagement_trend.get("description", "")}'
                })
        
        return areas
    
    def _generate_summary(
        self,
        overall_trend: TrendAnalysis,
        improvements: List[Dict[str, Any]]
    ) -> str:
        """生成总结"""
        if overall_trend.direction == 'up':
            base = '整体表现呈上升趋势，进步明显。'
        elif overall_trend.direction == 'down':
            base = '整体表现有所下滑，需要引起重视。'
        else:
            base = '整体表现保持稳定。'
        
        if improvements:
            top_improvement = improvements[0]
            base += f' 其中{top_improvement["aspect"]}进步最大，{top_improvement["description"]}。'
        
        return base
    
    def _generate_recommendations(
        self,
        areas_to_work: List[Dict[str, Any]]
    ) -> List[str]:
        """生成建议"""
        recommendations = []
        
        for area in areas_to_work[:3]:  # Top 3 问题
            if '情绪' in area['aspect']:
                recommendations.append('建议学习优秀主播的情绪调动技巧，增加情感词使用')
            elif '话术' in area['aspect']:
                recommendations.append(f'建议针对{area["aspect"]}进行专项练习，参考优秀案例')
            elif '互动' in area['aspect']:
                recommendations.append('建议增加互动环节设计，如提问、抽奖等')
        
        if not recommendations:
            recommendations.append('继续保持当前的直播风格，稳定发挥')
        
        return recommendations


# 便捷函数
def analyze_growth(
    sessions: List[SessionMetrics]
) -> Dict[str, Any]:
    """
    便捷函数：生成成长报告
    
    Returns:
        成长报告（字典格式）
    """
    service = TrendAnalysisService()
    report = service.generate_growth_report(sessions)
    return asdict(report)
