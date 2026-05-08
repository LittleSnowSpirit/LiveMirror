"""
话术优化建议生成引擎 - LiveMirror 核心功能

核心能力：
1. 话术问题诊断（节奏/措辞/逻辑/情感）
2. Before/After 改写示例生成
3. 优秀话术推荐
4. 建议优先级排序
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
import re
from sqlalchemy.orm import Session
from models import ExcellentExample as ExcellentExampleModel


@dataclass
class Issue:
    """问题诊断"""
    type: str  # rhythm, emotion, interaction, logic, keywords
    severity: str  # high, medium, low
    title: str
    description: str
    evidence: Optional[str] = None


@dataclass
class Suggestion:
    """优化建议"""
    type: str
    priority: str  # high, medium, low
    title: str
    description: str
    example: Optional[str] = None
    expected_improvement: Optional[str] = None


@dataclass
class RewriteExample:
    """改写示例"""
    before: str
    after: str
    changes: List[str]
    expected_improvement: Dict[str, str]


@dataclass
class ExcellentExample:
    """优秀话术示例"""
    speech_type: str
    content: str
    score: float
    emotion_impact: float
    engagement_rate: float
    session_id: Optional[str] = None
    timestamp: Optional[float] = None


class SuggestionEngine:
    """话术优化建议生成引擎"""

    def __init__(self, db: Optional[Session] = None):
        # 话术类型最佳实践
        self.best_practices = {
            'opening': {
                'ideal_duration': (15, 45),  # 秒
                'should_include': ['欢迎词', '自我介绍', '今日亮点'],
                'emotion_target': 0.7,
                'engagement_target': 20  # 每分钟弹幕数
            },
            'product_intro': {
                'ideal_duration': (60, 180),
                'should_include': ['产品特点', '使用场景', '用户见证'],
                'emotion_target': 0.6,
                'engagement_target': 15
            },
            'price_promotion': {
                'ideal_duration': (30, 90),
                'should_include': ['价格对比', '优惠力度', '紧迫感'],
                'emotion_target': 0.8,
                'engagement_target': 30
            },
            'limited_offer': {
                'ideal_duration': (20, 60),
                'should_include': ['库存数量', '时间限制', '行动号召'],
                'emotion_target': 0.85,
                'engagement_target': 35
            },
            'closing': {
                'ideal_duration': (30, 90),
                'should_include': ['促单话术', '付款指引', '售后保障'],
                'emotion_target': 0.75,
                'engagement_target': 25
            }
        }
        
        # 情感词库
        self.emotion_words = {
            'strong': ['超级', '特别', '非常', '极其', '超级', '绝对', '一定'],
            'moderate': ['很', '挺', '比较', '相当'],
            'weak': ['有点', '稍微', '略微']
        }
        
        # 促销词库
        self.promotion_words = [
            '特价', '优惠', '折扣', '福利', '秒杀', '抢购', '限时', '限量',
            '立省', '直降', '买一送一', '包邮', '赠品'
        ]
        
        # 互动词库
        self.interaction_words = [
            '有没有', '想要吗', '喜欢吗', '是不是', '对不对',
            '扣 1', '扣 666', '评论区', '告诉我', '问一下'
        ]
    
    def diagnose_speech(
        self,
        speech: Dict[str, Any],
        metrics: Optional[Dict[str, float]] = None
    ) -> List[Issue]:
        """
        诊断话术问题
        
        Args:
            speech: 话术数据 {type, content, start_time, end_time, ...}
            metrics: 表现指标 {emotion_impact, engagement_rate, ...}
            
        Returns:
            问题列表
        """
        issues = []
        
        speech_type = speech.get('type', 'unknown')
        content = speech.get('content', '')
        duration = speech.get('end_time', 0) - speech.get('start_time', 0)
        
        # 1. 节奏问题诊断
        rhythm_issues = self._diagnose_rhythm(speech_type, duration, content)
        issues.extend(rhythm_issues)
        
        # 2. 情感表达诊断
        emotion_issues = self._diagnose_emotion(speech_type, content, metrics)
        issues.extend(emotion_issues)
        
        # 3. 互动元素诊断
        interaction_issues = self._diagnose_interaction(content)
        issues.extend(interaction_issues)
        
        # 4. 关键词使用诊断
        keyword_issues = self._diagnose_keywords(speech_type, content)
        issues.extend(keyword_issues)
        
        # 5. 逻辑结构诊断
        logic_issues = self._diagnose_logic(content)
        issues.extend(logic_issues)
        
        return issues
    
    def _diagnose_rhythm(
        self,
        speech_type: str,
        duration: float,
        content: str
    ) -> List[Issue]:
        """诊断节奏问题"""
        issues = []
        
        best_practice = self.best_practices.get(speech_type, {})
        ideal_duration = best_practice.get('ideal_duration', (30, 120))
        
        if duration > ideal_duration[1] * 1.5:
            issues.append(Issue(
                type='rhythm',
                severity='high',
                title='话术过长',
                description=f'当前时长{duration:.0f}秒，建议控制在{ideal_duration[1]}秒以内',
                evidence='观众注意力可能已经分散'
            ))
        elif duration > ideal_duration[1]:
            issues.append(Issue(
                type='rhythm',
                severity='medium',
                title='话术偏长',
                description=f'当前时长{duration:.0f}秒，建议精简到{ideal_duration[1]}秒左右',
                evidence='可以考虑拆分或删减冗余内容'
            ))
        elif duration < ideal_duration[0] * 0.5:
            issues.append(Issue(
                type='rhythm',
                severity='high',
                title='话术过短',
                description=f'当前时长{duration:.0f}秒，建议扩展到{ideal_duration[0]}秒以上',
                evidence='可能缺乏必要的细节和说服力'
            ))
        elif duration < ideal_duration[0]:
            issues.append(Issue(
                type='rhythm',
                severity='low',
                title='话术偏短',
                description=f'当前时长{duration:.0f}秒，可以适当扩展到{ideal_duration[0]}秒',
                evidence='可以加入更多细节或案例'
            ))
        
        return issues
    
    def _diagnose_emotion(
        self,
        speech_type: str,
        content: str,
        metrics: Optional[Dict[str, float]]
    ) -> List[Issue]:
        """诊断情感表达问题"""
        issues = []
        
        # 检查情感词使用
        emotion_count = sum(
            1 for word in self.emotion_words['strong']
            if word in content
        )
        
        if emotion_count == 0:
            issues.append(Issue(
                type='emotion',
                severity='medium',
                title='情感表达平淡',
                description='话术中缺少强烈的情感词',
                evidence='建议加入"超级"、"特别"、"绝对"等词增强情感'
            ))
        
        # 如果有指标数据，检查情绪影响
        if metrics:
            emotion_impact = metrics.get('emotion_impact', 0)
            best_practice = self.best_practices.get(speech_type, {})
            target = best_practice.get('emotion_target', 0.7)
            
            if emotion_impact < target * 0.5:
                issues.append(Issue(
                    type='emotion',
                    severity='high',
                    title='情绪影响力低',
                    description=f'情绪影响分数{emotion_impact:.2f}，远低于目标{target}',
                    evidence='观众情绪反应较弱，需要增强话术感染力'
                ))
            elif emotion_impact < target * 0.8:
                issues.append(Issue(
                    type='emotion',
                    severity='medium',
                    title='情绪影响力不足',
                    description=f'情绪影响分数{emotion_impact:.2f}，低于目标{target}',
                    evidence='可以适当增强情感表达'
                ))
        
        return issues
    
    def _diagnose_interaction(self, content: str) -> List[Issue]:
        """诊断互动元素问题"""
        issues = []
        
        # 检查是否包含互动词
        has_interaction = any(
            word in content for word in self.interaction_words
        )
        
        # 检查是否包含疑问句
        has_question = bool(re.search(r'[？?]', content))
        
        if not has_interaction and not has_question:
            issues.append(Issue(
                type='interaction',
                severity='medium',
                title='缺少互动元素',
                description='话术中没有引导观众互动',
                evidence='建议加入提问或互动引导，如"有没有想要的宝宝？"'
            ))
        
        return issues
    
    def _diagnose_keywords(
        self,
        speech_type: str,
        content: str
    ) -> List[Issue]:
        """诊断关键词使用问题"""
        issues = []
        
        if speech_type in ['price_promotion', 'limited_offer']:
            # 促销类话术检查促销词
            has_promotion = any(
                word in content for word in self.promotion_words
            )
            
            if not has_promotion:
                issues.append(Issue(
                    type='keywords',
                    severity='high',
                    title='缺少促销关键词',
                    description='价格优惠话术应包含促销相关词汇',
                    evidence='建议加入"特价"、"优惠"、"限时"等词'
                ))
        
        return issues
    
    def _diagnose_logic(self, content: str) -> List[Issue]:
        """诊断逻辑结构问题"""
        issues = []
        
        # 检查是否过短导致逻辑不完整
        if len(content) < 10:
            issues.append(Issue(
                type='logic',
                severity='high',
                title='内容过于简单',
                description='话术内容太短，可能缺乏完整逻辑',
                evidence='建议补充产品信息、使用场景或用户见证'
            ))
        
        # 检查是否有因果关系词
        cause_effect_words = ['因为', '所以', '因此', '由于', '导致']
        has_logic_connectors = any(word in content for word in cause_effect_words)
        
        # 这只是建议，不作为问题
        # if not has_logic_connectors:
        #     issues.append(Issue(...))
        
        return issues
    
    def generate_rewrite(
        self,
        speech: Dict[str, Any],
        issues: List[Issue]
    ) -> Optional[RewriteExample]:
        """
        生成改写示例
        
        Args:
            speech: 话术数据
            issues: 诊断出的问题
            
        Returns:
            改写示例（如果可改写）
        """
        speech_type = speech.get('type', 'unknown')
        original_content = speech.get('content', '')
        
        # 根据问题类型生成改写
        after_content = original_content
        changes = []
        
        for issue in issues:
            if issue.type == 'emotion':
                after_content, change = self._enhance_emotion(after_content, speech_type)
                if change:
                    changes.append(change)
            
            elif issue.type == 'interaction':
                after_content, change = self._add_interaction(after_content, speech_type)
                if change:
                    changes.append(change)
            
            elif issue.type == 'keywords' and speech_type in ['price_promotion', 'limited_offer']:
                after_content, change = self._add_promotion_words(after_content)
                if change:
                    changes.append(change)
        
        if not changes:
            return None
        
        # 计算预期提升
        expected_improvement = self._estimate_improvement(changes)
        
        return RewriteExample(
            before=original_content,
            after=after_content,
            changes=changes,
            expected_improvement=expected_improvement
        )
    
    def _enhance_emotion(self, content: str, speech_type: str) -> tuple:
        """增强情感表达"""
        changes = []
        
        # 在开头添加强情感词
        if not any(word in content for word in self.emotion_words['strong']):
            emotion_word = '超级' if speech_type == 'price_promotion' else '特别'
            content = emotion_word + content
            changes.append(f'添加情感词"{emotion_word}"')
        
        # 在结尾添加情感强调
        if not content.endswith('！'):
            content = content.rstrip('。.，,') + '！'
            changes.append('使用感叹号增强语气')
        
        return content, '增强情感表达' if changes else None
    
    def _add_interaction(self, content: str, speech_type: str) -> tuple:
        """添加互动元素"""
        # 在结尾添加互动问题
        interaction_questions = {
            'price_promotion': '这个价格香不香？想要的扣 1！',
            'product_intro': '有没有心动的宝宝？评论区告诉我！',
            'limited_offer': '手慢无哦！抢到的扣个 666！',
            'closing': '还在犹豫什么？赶紧下单吧！'
        }
        
        question = interaction_questions.get(speech_type, '有没有想要的？')
        content = content + ' ' + question
        return content, '添加互动引导'
    
    def _add_promotion_words(self, content: str) -> tuple:
        """添加促销关键词"""
        # 添加价格对比
        if '原价' not in content and '专柜' not in content:
            content = '平时专柜卖 XXX 的产品，' + content
            return content, '添加价格对比'
        
        # 添加紧迫感
        if '限时' not in content and '今天' not in content:
            content = '今天直播间福利，' + content
            return content, '添加紧迫感'
        
        return content, None
    
    def _estimate_improvement(self, changes: List[str]) -> Dict[str, str]:
        """预估改进效果"""
        improvements = {}
        
        if any('情感' in c for c in changes):
            improvements['emotion_impact'] = '+15~25%'
        
        if any('互动' in c for c in changes):
            improvements['engagement_rate'] = '+20~30%'
        
        if any('促销' in c or '价格' in c for c in changes):
            improvements['conversion_rate'] = '+10~20%'
        
        return improvements if improvements else {'overall': '+10~15%'}
    
    def recommend_excellent_examples(
        self,
        speech_type: str,
        limit: int = 3
    ) -> List[ExcellentExample]:
        """
        推荐优秀话术示例

        Args:
            speech_type: 话术类型
            limit: 返回数量

        Returns:
            优秀示例列表
        """
        if not self.db:
            return []

        # 从数据库查询，按 score 降序排列
        rows = (
            self.db.query(ExcellentExampleModel)
            .filter(ExcellentExampleModel.speech_type == speech_type)
            .order_by(ExcellentExampleModel.score.desc())
            .limit(limit)
            .all()
        )

        return [
            ExcellentExample(
                speech_type=row.speech_type,
                content=row.content,
                score=row.score,
                emotion_impact=row.emotion_impact,
                engagement_rate=row.engagement_rate,
                session_id=row.session_id,
                timestamp=row.timestamp
            )
            for row in rows
        ]
    
    def generate_suggestions(
        self,
        speech: Dict[str, Any],
        metrics: Optional[Dict[str, float]] = None
    ) -> List[Suggestion]:
        """
        生成完整的优化建议
        
        Args:
            speech: 话术数据
            metrics: 表现指标
            
        Returns:
            建议列表（按优先级排序）
        """
        # 1. 诊断问题
        issues = self.diagnose_speech(speech, metrics)
        
        # 2. 生成改写示例
        rewrite = self.generate_rewrite(speech, issues)
        
        # 3. 生成建议
        suggestions = []
        
        for issue in issues:
            priority = 'high' if issue.severity == 'high' else 'medium'
            
            suggestion = Suggestion(
                type=issue.type,
                priority=priority,
                title=issue.title,
                description=issue.description,
                example=issue.evidence
            )
            suggestions.append(suggestion)
        
        # 4. 如果有改写示例，添加建议
        if rewrite:
            improvement_str = ' + '.join(rewrite.expected_improvement.values())
            suggestions.append(Suggestion(
                type='rewrite',
                priority='high',
                title='参考改写示例',
                description=f'预期提升：{improvement_str}',
                example=rewrite.after
            ))
        
        # 5. 按优先级排序
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        suggestions.sort(key=lambda s: priority_order.get(s.priority, 3))
        
        return suggestions


# 便捷函数
def analyze_speech(
    speech: Dict[str, Any],
    metrics: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    便捷函数：完整分析话术
    
    Returns:
        {
            'issues': [...],
            'suggestions': [...],
            'rewrite_example': {...}
        }
    """
    engine = SuggestionEngine()
    
    issues = engine.diagnose_speech(speech, metrics)
    suggestions = engine.generate_suggestions(speech, metrics)
    rewrite = engine.generate_rewrite(speech, issues)
    
    return {
        'issues': [asdict(i) for i in issues],
        'suggestions': [asdict(s) for s in suggestions],
        'rewrite_example': asdict(rewrite) if rewrite else None
    }
