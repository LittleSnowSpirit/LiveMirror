"""
LiveMirror 话术 A/B 测试服务
提供话术版本管理、流量分配、效果分析和统计显著性检验
"""

import random
import math
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum


class ScriptVersion(Enum):
    """话术版本枚举"""
    A = "A"
    B = "B"
    C = "C"


@dataclass
class ScriptVariant:
    """话术变体"""
    id: str
    version: str
    content: str
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True


@dataclass
class TestConfig:
    """A/B 测试配置"""
    test_id: str
    name: str
    variants: Dict[str, float]  # version -> traffic_allocation (0-1)
    start_time: datetime
    end_time: Optional[datetime] = None
    is_active: bool = True


@dataclass
class TestMetrics:
    """测试指标"""
    version: str
    impressions: int = 0  # 曝光次数
    clicks: int = 0  # 点击次数
    conversions: int = 0  # 转化次数
    interactions: int = 0  # 互动次数
    watch_time_seconds: float = 0.0  # 总观看时长


@dataclass
class StatisticalResult:
    """统计检验结果"""
    is_significant: bool
    p_value: float
    confidence_level: float
    winner: Optional[str]
    improvement: float  # 相对提升百分比


class ABTestingService:
    """A/B 测试服务"""
    
    def __init__(self):
        self.variants: Dict[str, ScriptVariant] = {}
        self.test_configs: Dict[str, TestConfig] = {}
        self.metrics: Dict[str, Dict[str, TestMetrics]] = {}  # test_id -> version -> metrics
        self.user_assignments: Dict[str, str] = {}  # user_id -> assigned version
    
    # ========== 话术版本管理 ==========
    
    def create_variant(self, test_id: str, version: str, content: str) -> ScriptVariant:
        """创建话术变体"""
        variant_id = f"{test_id}_{version}"
        variant = ScriptVariant(
            id=variant_id,
            version=version,
            content=content
        )
        self.variants[variant_id] = variant
        
        # 初始化指标
        if test_id not in self.metrics:
            self.metrics[test_id] = {}
        self.metrics[test_id][version] = TestMetrics(version=version)
        
        return variant
    
    def get_variant(self, test_id: str, version: str) -> Optional[ScriptVariant]:
        """获取话术变体"""
        variant_id = f"{test_id}_{version}"
        return self.variants.get(variant_id)
    
    def update_variant(self, test_id: str, version: str, content: str) -> Optional[ScriptVariant]:
        """更新话术变体"""
        variant = self.get_variant(test_id, version)
        if variant:
            variant.content = content
        return variant
    
    def deactivate_variant(self, test_id: str, version: str) -> bool:
        """停用话术变体"""
        variant = self.get_variant(test_id, version)
        if variant:
            variant.is_active = False
            return True
        return False
    
    def list_variants(self, test_id: str) -> List[ScriptVariant]:
        """列出测试的所有话术变体"""
        prefix = f"{test_id}_"
        return [v for v in self.variants.values() if v.id.startswith(prefix)]
    
    # ========== A/B 测试配置 ==========
    
    def create_test(self, name: str, traffic_allocation: Dict[str, float]) -> TestConfig:
        """创建 A/B 测试"""
        test_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # 验证流量分配总和为 1
        total = sum(traffic_allocation.values())
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"流量分配总和必须为 1.0，当前为 {total}")
        
        config = TestConfig(
            test_id=test_id,
            name=name,
            variants=traffic_allocation,
            start_time=datetime.now()
        )
        self.test_configs[test_id] = config
        self.metrics[test_id] = {}
        
        # 为每个版本初始化指标
        for version in traffic_allocation.keys():
            self.metrics[test_id][version] = TestMetrics(version=version)
        
        return config
    
    def get_test(self, test_id: str) -> Optional[TestConfig]:
        """获取测试配置"""
        return self.test_configs.get(test_id)
    
    def update_traffic_allocation(self, test_id: str, traffic_allocation: Dict[str, float]) -> bool:
        """更新流量分配"""
        config = self.get_test(test_id)
        if not config:
            return False
        
        total = sum(traffic_allocation.values())
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"流量分配总和必须为 1.0，当前为 {total}")
        
        config.variants = traffic_allocation
        return True
    
    def stop_test(self, test_id: str) -> bool:
        """停止测试"""
        config = self.get_test(test_id)
        if not config:
            return False
        
        config.is_active = False
        config.end_time = datetime.now()
        return True
    
    # ========== 流量分配 ==========
    
    def assign_user(self, test_id: str, user_id: str) -> Optional[str]:
        """为用户分配测试版本"""
        config = self.get_test(test_id)
        if not config or not config.is_active:
            return None
        
        # 检查是否已有分配
        if user_id in self.user_assignments:
            return self.user_assignments[user_id]
        
        # 基于用户 ID 进行一致性哈希分配
        hash_value = hash(user_id) % 100
        cumulative = 0
        
        for version, allocation in config.variants.items():
            cumulative += allocation * 100
            if hash_value < cumulative:
                self.user_assignments[user_id] = version
                return version
        
        # 默认返回第一个版本
        first_version = list(config.variants.keys())[0]
        self.user_assignments[user_id] = first_version
        return first_version
    
    def get_assigned_version(self, user_id: str) -> Optional[str]:
        """获取用户已分配的版本"""
        return self.user_assignments.get(user_id)
    
    # ========== 效果数据记录 ==========
    
    def record_impression(self, test_id: str, version: str, user_id: str):
        """记录曝光"""
        if test_id in self.metrics and version in self.metrics[test_id]:
            self.metrics[test_id][version].impressions += 1
    
    def record_click(self, test_id: str, version: str, user_id: str):
        """记录点击"""
        if test_id in self.metrics and version in self.metrics[test_id]:
            self.metrics[test_id][version].clicks += 1
    
    def record_conversion(self, test_id: str, version: str, user_id: str):
        """记录转化"""
        if test_id in self.metrics and version in self.metrics[test_id]:
            self.metrics[test_id][version].conversions += 1
    
    def record_interaction(self, test_id: str, version: str, user_id: str):
        """记录互动"""
        if test_id in self.metrics and version in self.metrics[test_id]:
            self.metrics[test_id][version].interactions += 1
    
    def record_watch_time(self, test_id: str, version: str, user_id: str, seconds: float):
        """记录观看时长"""
        if test_id in self.metrics and version in self.metrics[test_id]:
            self.metrics[test_id][version].watch_time_seconds += seconds
    
    # ========== 效果对比分析 ==========
    
    def get_metrics(self, test_id: str, version: str) -> Optional[TestMetrics]:
        """获取版本指标"""
        if test_id in self.metrics and version in self.metrics[test_id]:
            return self.metrics[test_id][version]
        return None
    
    def calculate_rates(self, metrics: TestMetrics) -> Dict[str, float]:
        """计算转化率/互动率"""
        impressions = max(metrics.impressions, 1)  # 避免除零
        
        return {
            "click_rate": metrics.clicks / impressions,
            "conversion_rate": metrics.conversions / impressions,
            "interaction_rate": metrics.interactions / impressions,
            "avg_watch_time": metrics.watch_time_seconds / impressions if impressions > 0 else 0
        }
    
    def compare_versions(self, test_id: str) -> Dict[str, Dict]:
        """对比所有版本的效果"""
        if test_id not in self.metrics:
            return {}
        
        results = {}
        for version, metrics in self.metrics[test_id].items():
            rates = self.calculate_rates(metrics)
            results[version] = {
                "metrics": asdict(metrics),
                "rates": rates
            }
        
        return results
    
    # ========== 统计显著性检验 ==========
    
    def chi_square_test(self, observed: List[int], expected: List[float]) -> Tuple[float, float]:
        """卡方检验"""
        if len(observed) != len(expected):
            raise ValueError("观察值和期望值数量必须相同")
        
        chi_square = sum((o - e) ** 2 / e for o, e in zip(observed, expected) if e > 0)
        
        # 简化 p 值计算（自由度 = len - 1）
        df = len(observed) - 1
        p_value = self._chi_square_p_value(chi_square, df)
        
        return chi_square, p_value
    
    def _chi_square_p_value(self, chi_square: float, df: int) -> float:
        """计算卡方分布的 p 值（近似）"""
        # 使用简化的近似方法
        if df <= 0 or chi_square < 0:
            return 1.0
        
        # 对于常见显著性水平的阈值
        critical_values = {
            1: {0.05: 3.841, 0.01: 6.635, 0.001: 10.828},
            2: {0.05: 5.991, 0.01: 9.210, 0.001: 13.816},
            3: {0.05: 7.815, 0.01: 11.345, 0.001: 16.266},
        }
        
        if df in critical_values:
            if chi_square > critical_values[df][0.001]:
                return 0.001
            elif chi_square > critical_values[df][0.01]:
                return 0.01
            elif chi_square > critical_values[df][0.05]:
                return 0.05
            else:
                return 0.5
        else:
            # 简化处理
            if chi_square > df * 3:
                return 0.05
            return 0.5
    
    def z_test_proportions(self, x1: int, n1: int, x2: int, n2: int) -> Tuple[float, float]:
        """两比例 Z 检验"""
        if n1 == 0 or n2 == 0:
            return 0, 1.0
        
        p1 = x1 / n1
        p2 = x2 / n2
        p_pooled = (x1 + x2) / (n1 + n2)
        
        if p_pooled == 0 or p_pooled == 1:
            return 0, 1.0
        
        se = math.sqrt(p_pooled * (1 - p_pooled) * (1/n1 + 1/n2))
        if se == 0:
            return 0, 1.0
        
        z = (p1 - p2) / se
        # 简化 p 值计算
        p_value = 2 * (1 - self._normal_cdf(abs(z)))
        
        return z, p_value
    
    def _normal_cdf(self, x: float) -> float:
        """标准正态分布累积分布函数（近似）"""
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))
    
    def test_significance(self, test_id: str, metric: str = "conversion_rate") -> StatisticalResult:
        """检验测试显著性"""
        if test_id not in self.metrics or len(self.metrics[test_id]) < 2:
            return StatisticalResult(
                is_significant=False,
                p_value=1.0,
                confidence_level=0.0,
                winner=None,
                improvement=0.0
            )
        
        versions_data = []
        for version, metrics in self.metrics[test_id].items():
            rates = self.calculate_rates(metrics)
            value = rates.get(metric, 0)
            impressions = metrics.impressions
            versions_data.append((version, value, impressions))
        
        if len(versions_data) < 2:
            return StatisticalResult(
                is_significant=False,
                p_value=1.0,
                confidence_level=0.0,
                winner=None,
                improvement=0.0
            )
        
        # 找到最佳版本
        best_version = max(versions_data, key=lambda x: x[1])
        baseline = versions_data[0]
        
        # 计算相对提升
        if baseline[1] > 0:
            improvement = (best_version[1] - baseline[1]) / baseline[1]
        else:
            improvement = 0.0
        
        # Z 检验（对比最佳和基准）
        if metric == "conversion_rate":
            best_metrics = self.metrics[test_id][best_version[0]]
            baseline_metrics = self.metrics[test_id][baseline[0]]
            z, p_value = self.z_test_proportions(
                best_metrics.conversions, best_metrics.impressions,
                baseline_metrics.conversions, baseline_metrics.impressions
            )
        else:
            # 简化处理
            p_value = 0.1
        
        is_significant = p_value < 0.05
        confidence_level = 1 - p_value
        
        winner = best_version[0] if is_significant else None
        
        return StatisticalResult(
            is_significant=is_significant,
            p_value=p_value,
            confidence_level=confidence_level,
            winner=winner,
            improvement=improvement
        )
    
    # ========== 优胜话术推荐 ==========
    
    def recommend_winner(self, test_id: str) -> Optional[Dict]:
        """推荐优胜话术"""
        comparison = self.compare_versions(test_id)
        if not comparison:
            return None
        
        significance = self.test_significance(test_id)
        
        # 找出转化率最高的版本
        best_version = None
        best_rate = -1
        
        for version, data in comparison.items():
            conv_rate = data["rates"]["conversion_rate"]
            if conv_rate > best_rate:
                best_rate = conv_rate
                best_version = version
        
        if not best_version or not significance.is_significant:
            return {
                "recommendation": "inconclusive",
                "message": "测试结果不显著，建议继续测试或增加样本量",
                "best_version": best_version,
                "confidence": significance.confidence_level
            }
        
        variant = self.get_variant(test_id, best_version)
        return {
            "recommendation": "winner",
            "winning_version": best_version,
            "content": variant.content if variant else None,
            "improvement": f"{significance.improvement * 100:.2f}%",
            "confidence": f"{significance.confidence_level * 100:.2f}%",
            "p_value": significance.p_value
        }
    
    # ========== 测试报告生成 ==========
    
    def generate_report(self, test_id: str) -> Dict:
        """生成测试报告"""
        config = self.get_test(test_id)
        if not config:
            return {"error": "测试不存在"}
        
        comparison = self.compare_versions(test_id)
        significance = self.test_significance(test_id)
        recommendation = self.recommend_winner(test_id)
        
        report = {
            "test_id": test_id,
            "test_name": config.name,
            "status": "active" if config.is_active else "completed",
            "duration": {
                "start": config.start_time.isoformat(),
                "end": config.end_time.isoformat() if config.end_time else None
            },
            "traffic_allocation": config.variants,
            "variants": [],
            "comparison": comparison,
            "statistical_test": {
                "is_significant": significance.is_significant,
                "p_value": significance.p_value,
                "confidence_level": significance.confidence_level,
                "winner": significance.winner,
                "improvement": f"{significance.improvement * 100:.2f}%"
            },
            "recommendation": recommendation
        }
        
        # 添加变体详情
        for version in config.variants.keys():
            variant = self.get_variant(test_id, version)
            if variant:
                report["variants"].append({
                    "version": version,
                    "content": variant.content,
                    "is_active": variant.is_active
                })
        
        return report
    
    def export_report(self, test_id: str, format: str = "json") -> str:
        """导出测试报告"""
        import json
        
        report = self.generate_report(test_id)
        
        if format == "json":
            return json.dumps(report, indent=2, ensure_ascii=False)
        elif format == "markdown":
            return self._format_report_markdown(report)
        else:
            return json.dumps(report, indent=2, ensure_ascii=False)
    
    def _format_report_markdown(self, report: Dict) -> str:
        """格式化为 Markdown 报告"""
        lines = [
            f"# A/B 测试报告：{report['test_name']}",
            f"",
            f"**测试 ID:** {report['test_id']}",
            f"**状态:** {report['status']}",
            f"**时间:** {report['duration']['start']} - {report['duration']['end'] or '进行中'}",
            f"",
            f"## 流量分配",
        ]
        
        for version, allocation in report['traffic_allocation'].items():
            lines.append(f"- 版本 {version}: {allocation * 100:.1f}%")
        
        lines.extend([
            f"",
            f"## 效果对比",
            f"",
        ])
        
        for version, data in report['comparison'].items():
            metrics = data['metrics']
            rates = data['rates']
            lines.extend([
                f"### 版本 {version}",
                f"- 曝光：{metrics['impressions']}",
                f"- 点击：{metrics['clicks']} (点击率：{rates['click_rate'] * 100:.2f}%)",
                f"- 转化：{metrics['conversions']} (转化率：{rates['conversion_rate'] * 100:.2f}%)",
                f"- 互动：{metrics['interactions']} (互动率：{rates['interaction_rate'] * 100:.2f}%)",
                f"- 平均观看时长：{rates['avg_watch_time']:.2f}秒",
                f"",
            ])
        
        lines.extend([
            f"## 统计显著性",
            f"- p 值：{report['statistical_test']['p_value']:.4f}",
            f"- 置信度：{report['statistical_test']['confidence_level'] * 100:.2f}%",
            f"- 显著：{'是' if report['statistical_test']['is_significant'] else '否'}",
            f"",
            f"## 推荐结果",
        ])
        
        if report['recommendation']:
            rec = report['recommendation']
            if rec['recommendation'] == 'winner':
                lines.extend([
                    f"🏆 **优胜版本：{rec['winning_version']}**",
                    f"- 相对提升：{rec['improvement']}",
                    f"- 置信度：{rec['confidence']}",
                    f"",
                    f"**话术内容:**",
                    f"> {rec['content']}",
                ])
            else:
                lines.append(f"⚠️ {rec['message']}")
        
        return "\n".join(lines)


# 全局服务实例
ab_testing_service = ABTestingService()
