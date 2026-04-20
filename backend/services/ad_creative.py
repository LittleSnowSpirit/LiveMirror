"""
广告素材分析服务
LiveMirror Ad Creative Analysis Service

功能：
1. 广告素材上传和管理
2. 素材效果分析（点击/转化）
3. A/B 测试支持
4. 素材评分系统
5. 优秀素材推荐
6. 素材优化建议
"""

import uuid
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import json


class CreativeStatus(Enum):
    """素材状态"""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class ABTestStatus(Enum):
    """A/B 测试状态"""
    RUNNING = "running"
    COMPLETED = "completed"
    PAUSED = "paused"


@dataclass
class CreativeMetrics:
    """素材效果指标"""
    impressions: int = 0  # 展示次数
    clicks: int = 0  # 点击次数
    conversions: int = 0  # 转化次数
    spend: float = 0.0  # 花费
    revenue: float = 0.0  # 收入
    
    @property
    def ctr(self) -> float:
        """点击率"""
        return self.clicks / self.impressions if self.impressions > 0 else 0.0
    
    @property
    def cvr(self) -> float:
        """转化率"""
        return self.conversions / self.clicks if self.clicks > 0 else 0.0
    
    @property
    def cpc(self) -> float:
        """单次点击成本"""
        return self.spend / self.clicks if self.clicks > 0 else 0.0
    
    @property
    def cpa(self) -> float:
        """单次转化成本"""
        return self.spend / self.conversions if self.conversions > 0 else 0.0
    
    @property
    def roas(self) -> float:
        """广告支出回报率"""
        return self.revenue / self.spend if self.spend > 0 else 0.0
    
    def to_dict(self) -> Dict:
        return {
            **asdict(self),
            'ctr': self.ctr,
            'cvr': self.cvr,
            'cpc': self.cpc,
            'cpa': self.cpa,
            'roas': self.roas
        }


@dataclass
class AdCreative:
    """广告素材"""
    id: str
    name: str
    creative_type: str  # image, video, carousel, etc.
    file_path: str
    file_hash: str
    dimensions: Dict[str, int]  # {width, height}
    file_size: int
    status: CreativeStatus = CreativeStatus.DRAFT
    metrics: CreativeMetrics = field(default_factory=CreativeMetrics)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    ab_test_id: Optional[str] = None
    
    def update_metrics(self, metrics: CreativeMetrics):
        """更新素材效果数据"""
        self.metrics = metrics
        self.updated_at = datetime.now()
    
    def calculate_score(self) -> float:
        """计算素材评分 (0-100)"""
        score = 0.0
        
        # CTR 权重 30% - 基准：2% CTR 为满分 (行业优秀水平)
        ctr_score = min(self.metrics.ctr / 0.02, 1.0) * 100 * 0.3
        
        # CVR 权重 30% - 基准：5% CVR 为满分
        cvr_score = min(self.metrics.cvr / 0.05, 1.0) * 100 * 0.3
        
        # ROAS 权重 25% - 基准：ROAS 4.0 为满分
        roas_score = min(self.metrics.roas / 4.0, 1.0) * 100 * 0.25
        
        # 数据量权重 15% (展示次数越多，评分越可靠) - 基准：10000 次展示
        volume_score = min(self.metrics.impressions / 10000, 1.0) * 100 * 0.15
        
        score = ctr_score + cvr_score + roas_score + volume_score
        return round(score, 2)
    
    def to_dict(self) -> Dict:
        return {
            'id': self.id,
            'name': self.name,
            'creative_type': self.creative_type,
            'file_path': self.file_path,
            'file_hash': self.file_hash,
            'dimensions': self.dimensions,
            'file_size': self.file_size,
            'status': self.status.value,
            'metrics': self.metrics.to_dict(),
            'tags': self.tags,
            'metadata': self.metadata,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'ab_test_id': self.ab_test_id,
            'score': self.calculate_score()
        }


@dataclass
class ABTest:
    """A/B 测试"""
    id: str
    name: str
    creative_ids: List[str]
    status: ABTestStatus = ABTestStatus.RUNNING
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    winner_id: Optional[str] = None
    confidence_level: float = 0.0
    
    def determine_winner(self, creatives: Dict[str, AdCreative]) -> str:
        """根据效果数据确定获胜素材"""
        best_score = -1
        winner = None
        
        for creative_id in self.creative_ids:
            if creative_id in creatives:
                score = creatives[creative_id].calculate_score()
                if score > best_score:
                    best_score = score
                    winner = creative_id
        
        self.winner_id = winner
        self.status = ABTestStatus.COMPLETED
        self.end_time = datetime.now()
        return winner
    
    def to_dict(self, creatives: Optional[Dict[str, AdCreative]] = None) -> Dict:
        result = {
            'id': self.id,
            'name': self.name,
            'creative_ids': self.creative_ids,
            'status': self.status.value,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'winner_id': self.winner_id,
            'confidence_level': self.confidence_level
        }
        
        if creatives:
            result['creatives'] = [creatives[cid].to_dict() for cid in self.creative_ids if cid in creatives]
        
        return result


class AdCreativeService:
    """广告素材管理服务"""
    
    def __init__(self):
        self.creatives: Dict[str, AdCreative] = {}
        self.ab_tests: Dict[str, ABTest] = {}
        self.upload_dir = "uploads/creatives"
    
    def _generate_file_hash(self, file_content: bytes) -> str:
        """生成文件哈希值"""
        return hashlib.sha256(file_content).hexdigest()
    
    def upload_creative(
        self,
        name: str,
        creative_type: str,
        file_content: bytes,
        file_path: str,
        dimensions: Dict[str, int],
        file_size: int,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict] = None
    ) -> AdCreative:
        """上传广告素材"""
        creative_id = str(uuid.uuid4())
        file_hash = self._generate_file_hash(file_content)
        
        creative = AdCreative(
            id=creative_id,
            name=name,
            creative_type=creative_type,
            file_path=file_path,
            file_hash=file_hash,
            dimensions=dimensions,
            file_size=file_size,
            status=CreativeStatus.ACTIVE,
            tags=tags or [],
            metadata=metadata or {}
        )
        
        self.creatives[creative_id] = creative
        return creative
    
    def get_creative(self, creative_id: str) -> Optional[AdCreative]:
        """获取单个素材"""
        return self.creatives.get(creative_id)
    
    def list_creatives(
        self,
        status: Optional[CreativeStatus] = None,
        creative_type: Optional[str] = None,
        tags: Optional[List[str]] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[AdCreative]:
        """获取素材列表"""
        results = list(self.creatives.values())
        
        if status:
            results = [c for c in results if c.status == status]
        
        if creative_type:
            results = [c for c in results if c.creative_type == creative_type]
        
        if tags:
            results = [c for c in results if any(tag in c.tags for tag in tags)]
        
        # 按评分排序
        results.sort(key=lambda c: c.calculate_score(), reverse=True)
        
        return results[offset:offset + limit]
    
    def update_creative_status(self, creative_id: str, status: CreativeStatus) -> bool:
        """更新素材状态"""
        creative = self.creatives.get(creative_id)
        if creative:
            creative.status = status
            creative.updated_at = datetime.now()
            return True
        return False
    
    def update_metrics(
        self,
        creative_id: str,
        impressions: int = 0,
        clicks: int = 0,
        conversions: int = 0,
        spend: float = 0.0,
        revenue: float = 0.0
    ) -> bool:
        """更新素材效果数据"""
        creative = self.creatives.get(creative_id)
        if creative:
            metrics = CreativeMetrics(
                impressions=impressions,
                clicks=clicks,
                conversions=conversions,
                spend=spend,
                revenue=revenue
            )
            creative.update_metrics(metrics)
            return True
        return False
    
    def analyze_creative(self, creative_id: str) -> Optional[Dict]:
        """分析单个素材效果"""
        creative = self.creatives.get(creative_id)
        if not creative:
            return None
        
        metrics = creative.metrics
        score = creative.calculate_score()
        
        # 生成优化建议
        suggestions = self._generate_suggestions(creative)
        
        return {
            'creative': creative.to_dict(),
            'analysis': {
                'score': score,
                'performance_level': self._get_performance_level(score),
                'strengths': self._get_strengths(creative),
                'weaknesses': self._get_weaknesses(creative),
                'suggestions': suggestions
            }
        }
    
    def _get_performance_level(self, score: float) -> str:
        """根据评分获取表现等级"""
        if score >= 80:
            return "excellent"
        elif score >= 60:
            return "good"
        elif score >= 40:
            return "average"
        else:
            return "needs_improvement"
    
    def _get_strengths(self, creative: AdCreative) -> List[str]:
        """获取素材优势"""
        strengths = []
        metrics = creative.metrics
        
        if metrics.ctr > 0.02:
            strengths.append("点击率高于平均水平")
        if metrics.cvr > 0.05:
            strengths.append("转化率表现优秀")
        if metrics.roas > 3.0:
            strengths.append("广告支出回报率高")
        if metrics.impressions > 10000:
            strengths.append("数据量充足，评分可靠")
        
        return strengths
    
    def _get_weaknesses(self, creative: AdCreative) -> List[str]:
        """获取素材劣势"""
        weaknesses = []
        metrics = creative.metrics
        
        if metrics.ctr < 0.01:
            weaknesses.append("点击率偏低，需要优化素材吸引力")
        if metrics.cvr < 0.02:
            weaknesses.append("转化率较低，可能需要优化落地页")
        if metrics.roas < 2.0 and metrics.spend > 0:
            weaknesses.append("ROI 表现不佳，建议调整投放策略")
        if metrics.impressions < 1000:
            weaknesses.append("数据量不足，建议增加投放")
        
        return weaknesses
    
    def _generate_suggestions(self, creative: AdCreative) -> List[Dict]:
        """生成优化建议"""
        suggestions = []
        metrics = creative.metrics
        
        if metrics.ctr < 0.01:
            suggestions.append({
                'type': 'ctr',
                'priority': 'high',
                'suggestion': '优化素材视觉设计，增强吸引力',
                'actions': [
                    '尝试更醒目的配色方案',
                    '突出核心卖点',
                    '添加明确的行动号召 (CTA)'
                ]
            })
        
        if metrics.cvr < 0.02:
            suggestions.append({
                'type': 'cvr',
                'priority': 'high',
                'suggestion': '优化转化路径',
                'actions': [
                    '检查落地页加载速度',
                    '简化转化流程',
                    '确保素材与落地页内容一致'
                ]
            })
        
        if metrics.roas < 2.0 and metrics.spend > 0:
            suggestions.append({
                'type': 'roas',
                'priority': 'medium',
                'suggestion': '提高广告投资回报率',
                'actions': [
                    '优化目标受众定位',
                    '调整出价策略',
                    '测试不同投放时段'
                ]
            })
        
        if not suggestions:
            suggestions.append({
                'type': 'general',
                'priority': 'low',
                'suggestion': '保持当前策略，持续监控效果',
                'actions': [
                    '定期更新素材避免疲劳',
                    '尝试小幅 A/B 测试优化',
                    '关注行业趋势和竞品动态'
                ]
            })
        
        return suggestions
    
    def get_top_creatives(self, limit: int = 10, min_impressions: int = 100) -> List[AdCreative]:
        """获取优秀素材推荐"""
        qualified = [
            c for c in self.creatives.values()
            if c.metrics.impressions >= min_impressions and c.status == CreativeStatus.ACTIVE
        ]
        
        qualified.sort(key=lambda c: c.calculate_score(), reverse=True)
        return qualified[:limit]
    
    def create_ab_test(
        self,
        name: str,
        creative_ids: List[str]
    ) -> ABTest:
        """创建 A/B 测试"""
        if len(creative_ids) < 2:
            raise ValueError("A/B 测试至少需要 2 个素材")
        
        for cid in creative_ids:
            if cid not in self.creatives:
                raise ValueError(f"素材 {cid} 不存在")
        
        ab_test = ABTest(
            id=str(uuid.uuid4()),
            name=name,
            creative_ids=creative_ids
        )
        
        # 关联素材到测试
        for cid in creative_ids:
            self.creatives[cid].ab_test_id = ab_test.id
        
        self.ab_tests[ab_test.id] = ab_test
        return ab_test
    
    def get_ab_test(self, test_id: str) -> Optional[ABTest]:
        """获取 A/B 测试"""
        return self.ab_tests.get(test_id)
    
    def list_ab_tests(self, status: Optional[ABTestStatus] = None) -> List[ABTest]:
        """获取 A/B 测试列表"""
        tests = list(self.ab_tests.values())
        if status:
            tests = [t for t in tests if t.status == status]
        return tests
    
    def complete_ab_test(self, test_id: str) -> Optional[Dict]:
        """完成 A/B 测试并确定获胜者"""
        test = self.ab_tests.get(test_id)
        if not test:
            return None
        
        winner = test.determine_winner(self.creatives)
        
        # 计算置信度（简化版本）
        if test.creative_ids:
            winner_creative = self.creatives.get(winner)
            if winner_creative:
                # 基于样本量和效果差异计算置信度
                total_impressions = sum(
                    self.creatives[cid].metrics.impressions
                    for cid in test.creative_ids
                    if cid in self.creatives
                )
                test.confidence_level = min(0.5 + (total_impressions / 10000) * 0.5, 0.99)
        
        return test.to_dict(self.creatives)
    
    def get_ab_test_analysis(self, test_id: str) -> Optional[Dict]:
        """获取 A/B 测试分析报告"""
        test = self.ab_tests.get(test_id)
        if not test:
            return None
        
        creatives_data = []
        for cid in test.creative_ids:
            creative = self.creatives.get(cid)
            if creative:
                creatives_data.append({
                    'creative': creative.to_dict(),
                    'metrics': creative.metrics.to_dict(),
                    'score': creative.calculate_score()
                })
        
        # 排序
        creatives_data.sort(key=lambda x: x['score'], reverse=True)
        
        return {
            'test': test.to_dict(),
            'creatives': creatives_data,
            'winner': test.winner_id,
            'recommendation': f"建议使用素材 {test.winner_id}，其综合评分最高" if test.winner_id else "测试数据不足，无法确定获胜者"
        }
    
    def delete_creative(self, creative_id: str) -> bool:
        """删除素材"""
        if creative_id in self.creatives:
            del self.creatives[creative_id]
            return True
        return False
    
    def export_analytics(self, format: str = 'json') -> str:
        """导出分析数据"""
        data = {
            'creatives': [c.to_dict() for c in self.creatives.values()],
            'ab_tests': [t.to_dict(self.creatives) for t in self.ab_tests.values()],
            'exported_at': datetime.now().isoformat()
        }
        
        if format == 'json':
            return json.dumps(data, indent=2, ensure_ascii=False)
        else:
            return json.dumps(data, indent=2, ensure_ascii=False)


# 全局服务实例
creative_service = AdCreativeService()
