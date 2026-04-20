"""
直播 ROI 分析服务 - LiveMirror
提供投入产出比分析、成本核算、收益统计、优化建议等功能
"""

import json
import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from enum import Enum
from dataclasses import dataclass, asdict, field


class CostType(Enum):
    """成本类型"""
    LABOR = "labor"           # 人力成本
    VENUE = "venue"           # 场地成本
    PROMOTION = "promotion"   # 推广成本
    EQUIPMENT = "equipment"   # 设备成本
    OTHER = "other"           # 其他成本


class RevenueType(Enum):
    """收益类型"""
    GMV = "gmv"               # 商品交易总额
    PROFIT = "profit"         # 利润
    COMMISSION = "commission" # 佣金


@dataclass
class CostItem:
    """成本项"""
    type: str
    name: str
    amount: float
    unit: str = "CNY"
    notes: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> "CostItem":
        return cls(**data)


@dataclass
class RevenueItem:
    """收益项"""
    type: str
    name: str
    amount: float
    unit: str = "CNY"
    notes: str = ""
    
    def to_dict(self) -> Dict:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> "RevenueItem":
        return cls(**data)


@dataclass
class LiveSession:
    """直播场次数据"""
    session_id: str
    date: str
    start_time: str
    end_time: str
    duration_minutes: int
    costs: List[CostItem] = field(default_factory=list)
    revenues: List[RevenueItem] = field(default_factory=list)
    category: str = "general"
    notes: str = ""
    
    def total_cost(self) -> float:
        """计算总成本"""
        return sum(item.amount for item in self.costs)
    
    def total_revenue(self) -> float:
        """计算总收益（利润）"""
        profit_items = [item for item in self.revenues if item.type == "profit"]
        if profit_items:
            return sum(item.amount for item in profit_items)
        # 如果没有利润项，使用 GMV * 利润率估算
        gmv_items = [item for item in self.revenues if item.type == "gmv"]
        if gmv_items:
            gmv = sum(item.amount for item in gmv_items)
            return gmv * 0.2  # 假设 20% 利润率
        return 0.0
    
    def gmv(self) -> float:
        """获取 GMV"""
        gmv_items = [item for item in self.revenues if item.type == "gmv"]
        return sum(item.amount for item in gmv_items) if gmv_items else 0.0
    
    def roi(self) -> float:
        """计算 ROI"""
        cost = self.total_cost()
        if cost == 0:
            return 0.0
        revenue = self.total_revenue()
        return ((revenue - cost) / cost) * 100
    
    def to_dict(self) -> Dict:
        return {
            **asdict(self),
            "total_cost": self.total_cost(),
            "total_revenue": self.total_revenue(),
            "gmv": self.gmv(),
            "roi": self.roi()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "LiveSession":
        costs = [CostItem.from_dict(c) for c in data.get("costs", [])]
        revenues = [RevenueItem.from_dict(r) for r in data.get("revenues", [])]
        return cls(
            session_id=data["session_id"],
            date=data["date"],
            start_time=data["start_time"],
            end_time=data["end_time"],
            duration_minutes=data["duration_minutes"],
            costs=costs,
            revenues=revenues,
            category=data.get("category", "general"),
            notes=data.get("notes", "")
        )


@dataclass
class ROIMetrics:
    """ROI 指标"""
    session_id: str
    date: str
    total_cost: float
    total_revenue: float
    gmv: float
    profit: float
    roi_percentage: float
    roi_ratio: float  # 收益/成本
    cost_breakdown: Dict[str, float]
    revenue_breakdown: Dict[str, float]
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class OptimizationSuggestion:
    """优化建议"""
    category: str
    priority: str  # high, medium, low
    suggestion: str
    expected_impact: str
    estimated_savings: float = 0.0
    implementation_difficulty: str = "medium"  # easy, medium, hard
    
    def to_dict(self) -> Dict:
        return asdict(self)


@dataclass
class ComparisonResult:
    """对比分析结果"""
    sessions: List[str]
    metrics: Dict[str, ROIMetrics]
    best_roi_session: str
    worst_roi_session: str
    average_roi: float
    roi_trend: str  # increasing, decreasing, stable
    insights: List[str]
    
    def to_dict(self) -> Dict:
        return {
            **asdict(self),
            "metrics": {k: v.to_dict() for k, v in self.metrics.items()}
        }


class ROIAnalysisService:
    """ROI 分析服务"""
    
    def __init__(self, data_dir: str = "data/roi_analysis"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 数据文件路径
        self.sessions_path = self.data_dir / "live_sessions.json"
        self.cost_templates_path = self.data_dir / "cost_templates.json"
        self.reports_path = self.data_dir / "reports.json"
        
        # 内存数据
        self.sessions: List[LiveSession] = []
        self.cost_templates: Dict[str, Dict] = {}
        self.reports: List[Dict] = []
        
        # 加载数据
        self._load_sessions()
        self._load_cost_templates()
        
        # 默认成本模板
        self._init_default_templates()
    
    def _load_sessions(self):
        """加载直播场次数据"""
        if self.sessions_path.exists():
            try:
                with open(self.sessions_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.sessions = [LiveSession.from_dict(s) for s in data]
            except Exception as e:
                print(f"加载场次数据失败：{e}")
                self.sessions = []
    
    def _save_sessions(self):
        """保存直播场次数据"""
        with open(self.sessions_path, "w", encoding="utf-8") as f:
            json.dump([s.to_dict() for s in self.sessions], f, ensure_ascii=False, indent=2)
    
    def _load_cost_templates(self):
        """加载成本模板"""
        if self.cost_templates_path.exists():
            try:
                with open(self.cost_templates_path, "r", encoding="utf-8") as f:
                    self.cost_templates = json.load(f)
            except Exception as e:
                print(f"加载成本模板失败：{e}")
                self.cost_templates = {}
    
    def _save_cost_templates(self):
        """保存成本模板"""
        with open(self.cost_templates_path, "w", encoding="utf-8") as f:
            json.dump(self.cost_templates, f, ensure_ascii=False, indent=2)
    
    def _init_default_templates(self):
        """初始化默认成本模板"""
        default_templates = {
            "standard": {
                "name": "标准直播",
                "costs": {
                    "labor": {"name": "人力成本", "amount": 500, "unit": "CNY"},
                    "venue": {"name": "场地成本", "amount": 300, "unit": "CNY"},
                    "promotion": {"name": "推广成本", "amount": 200, "unit": "CNY"}
                }
            },
            "premium": {
                "name": "精品直播",
                "costs": {
                    "labor": {"name": "人力成本", "amount": 1500, "unit": "CNY"},
                    "venue": {"name": "场地成本", "amount": 1000, "unit": "CNY"},
                    "promotion": {"name": "推广成本", "amount": 800, "unit": "CNY"},
                    "equipment": {"name": "设备成本", "amount": 500, "unit": "CNY"}
                }
            },
            "minimal": {
                "name": "简易直播",
                "costs": {
                    "labor": {"name": "人力成本", "amount": 200, "unit": "CNY"},
                    "venue": {"name": "场地成本", "amount": 0, "unit": "CNY"},
                    "promotion": {"name": "推广成本", "amount": 50, "unit": "CNY"}
                }
            }
        }
        
        for key, template in default_templates.items():
            if key not in self.cost_templates:
                self.cost_templates[key] = template
        
        self._save_cost_templates()
    
    def add_session(self, session: LiveSession) -> LiveSession:
        """添加直播场次"""
        self.sessions.append(session)
        self._save_sessions()
        return session
    
    def create_session(
        self,
        date: str,
        start_time: str,
        end_time: str,
        category: str = "general",
        costs: Optional[List[Dict]] = None,
        revenues: Optional[List[Dict]] = None,
        notes: str = ""
    ) -> LiveSession:
        """创建直播场次"""
        # 计算时长
        start = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M")
        end = datetime.strptime(f"{date} {end_time}", "%Y-%m-%d %H:%M")
        if end < start:
            end += timedelta(days=1)
        duration_minutes = int((end - start).total_seconds() / 60)
        
        # 生成 session_id
        session_id = f"session_{date}_{start_time.replace(':', '')}"
        
        # 创建成本项
        cost_items = []
        if costs:
            for cost in costs:
                cost_items.append(CostItem(
                    type=cost.get("type", "other"),
                    name=cost.get("name", "其他成本"),
                    amount=cost.get("amount", 0),
                    unit=cost.get("unit", "CNY"),
                    notes=cost.get("notes", "")
                ))
        
        # 创建收益项
        revenue_items = []
        if revenues:
            for revenue in revenues:
                revenue_items.append(RevenueItem(
                    type=revenue.get("type", "gmv"),
                    name=revenue.get("name", "收益"),
                    amount=revenue.get("amount", 0),
                    unit=revenue.get("unit", "CNY"),
                    notes=revenue.get("notes", "")
                ))
        
        session = LiveSession(
            session_id=session_id,
            date=date,
            start_time=start_time,
            end_time=end_time,
            duration_minutes=duration_minutes,
            costs=cost_items,
            revenues=revenue_items,
            category=category,
            notes=notes
        )
        
        return self.add_session(session)
    
    def get_session(self, session_id: str) -> Optional[LiveSession]:
        """获取直播场次"""
        for session in self.sessions:
            if session.session_id == session_id:
                return session
        return None
    
    def list_sessions(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[LiveSession]:
        """获取直播场次列表"""
        result = self.sessions
        
        if start_date:
            result = [s for s in result if s.date >= start_date]
        
        if end_date:
            result = [s for s in result if s.date <= end_date]
        
        if category:
            result = [s for s in result if s.category == category]
        
        return sorted(result, key=lambda s: s.date, reverse=True)
    
    def calculate_roi_metrics(self, session_id: str) -> Optional[ROIMetrics]:
        """计算 ROI 指标"""
        session = self.get_session(session_id)
        if not session:
            return None
        
        total_cost = session.total_cost()
        total_revenue = session.total_revenue()
        gmv = session.gmv()
        profit = total_revenue
        
        roi_percentage = session.roi()
        roi_ratio = total_revenue / total_cost if total_cost > 0 else 0
        
        # 成本分解
        cost_breakdown = {}
        for cost in session.costs:
            if cost.type not in cost_breakdown:
                cost_breakdown[cost.type] = 0
            cost_breakdown[cost.type] += cost.amount
        
        # 收益分解
        revenue_breakdown = {}
        for revenue in session.revenues:
            if revenue.type not in revenue_breakdown:
                revenue_breakdown[revenue.type] = 0
            revenue_breakdown[revenue.type] += revenue.amount
        
        return ROIMetrics(
            session_id=session_id,
            date=session.date,
            total_cost=total_cost,
            total_revenue=total_revenue,
            gmv=gmv,
            profit=profit,
            roi_percentage=roi_percentage,
            roi_ratio=roi_ratio,
            cost_breakdown=cost_breakdown,
            revenue_breakdown=revenue_breakdown
        )
    
    def get_cost_breakdown(self, session_id: str) -> Optional[Dict[str, float]]:
        """获取成本分解"""
        session = self.get_session(session_id)
        if not session:
            return None
        
        breakdown = {}
        for cost in session.costs:
            if cost.type not in breakdown:
                breakdown[cost.type] = 0
            breakdown[cost.type] += cost.amount
        
        return breakdown
    
    def generate_optimization_suggestions(self, session_id: str) -> List[OptimizationSuggestion]:
        """生成优化建议"""
        session = self.get_session(session_id)
        if not session:
            return []
        
        suggestions = []
        metrics = self.calculate_roi_metrics(session_id)
        if not metrics:
            return []
        
        total_cost = metrics.total_cost
        roi = metrics.roi_percentage
        
        # 分析成本结构
        cost_breakdown = metrics.cost_breakdown
        
        # 人力成本优化
        labor_cost = cost_breakdown.get("labor", 0)
        if labor_cost > total_cost * 0.5:
            suggestions.append(OptimizationSuggestion(
                category="labor",
                priority="high",
                suggestion="人力成本占比过高（超过 50%），建议优化人员配置或采用自动化方案",
                expected_impact="可降低人力成本 20-30%",
                estimated_savings=labor_cost * 0.25,
                implementation_difficulty="medium"
            ))
        
        # 场地成本优化
        venue_cost = cost_breakdown.get("venue", 0)
        if venue_cost > total_cost * 0.3:
            suggestions.append(OptimizationSuggestion(
                category="venue",
                priority="medium",
                suggestion="场地成本较高，建议考虑长期租赁或共享场地方案",
                expected_impact="可降低场地成本 15-25%",
                estimated_savings=venue_cost * 0.2,
                implementation_difficulty="easy"
            ))
        
        # 推广成本优化
        promotion_cost = cost_breakdown.get("promotion", 0)
        if promotion_cost > total_cost * 0.3:
            suggestions.append(OptimizationSuggestion(
                category="promotion",
                priority="high",
                suggestion="推广成本占比过高，建议优化投放策略，提高转化率",
                expected_impact="可提高 ROI 10-20%",
                estimated_savings=promotion_cost * 0.15,
                implementation_difficulty="hard"
            ))
        
        # ROI 低的情况
        if roi < 0:
            suggestions.append(OptimizationSuggestion(
                category="overall",
                priority="high",
                suggestion="当前 ROI 为负，建议重新评估直播策略或暂停直播",
                expected_impact="避免进一步亏损",
                estimated_savings=abs(metrics.profit - total_cost),
                implementation_difficulty="easy"
            ))
        elif roi < 50:
            suggestions.append(OptimizationSuggestion(
                category="overall",
                priority="medium",
                suggestion="ROI 偏低（低于 50%），建议优化成本结构或提高收益",
                expected_impact="可提高 ROI 20-40%",
                estimated_savings=0,
                implementation_difficulty="medium"
            ))
        
        # 时长优化
        if session.duration_minutes < 60:
            suggestions.append(OptimizationSuggestion(
                category="duration",
                priority="low",
                suggestion="直播时长较短，建议延长直播时间以提高收益",
                expected_impact="可能提高收益 10-30%",
                estimated_savings=0,
                implementation_difficulty="easy"
            ))
        elif session.duration_minutes > 240:
            suggestions.append(OptimizationSuggestion(
                category="duration",
                priority="low",
                suggestion="直播时长过长，人力成本增加，建议优化为多场次短时长",
                expected_impact="可降低人力成本 15-25%",
                estimated_savings=labor_cost * 0.2,
                implementation_difficulty="medium"
            ))
        
        return sorted(suggestions, key=lambda s: (
            {"high": 0, "medium": 1, "low": 2}[s.priority],
            -s.estimated_savings
        ))
    
    def compare_sessions(self, session_ids: List[str]) -> Optional[ComparisonResult]:
        """对比多场次 ROI"""
        if len(session_ids) < 2:
            return None
        
        metrics_dict = {}
        for session_id in session_ids:
            metrics = self.calculate_roi_metrics(session_id)
            if metrics:
                metrics_dict[session_id] = metrics
        
        if len(metrics_dict) < 2:
            return None
        
        # 找出最佳和最差 ROI
        roi_values = [(sid, m.roi_percentage) for sid, m in metrics_dict.items()]
        best_roi_session = max(roi_values, key=lambda x: x[1])[0]
        worst_roi_session = min(roi_values, key=lambda x: x[1])[0]
        
        # 计算平均 ROI
        average_roi = sum(m.roi_percentage for m in metrics_dict.values()) / len(metrics_dict)
        
        # 分析趋势
        sorted_metrics = sorted(metrics_dict.values(), key=lambda m: m.date)
        if len(sorted_metrics) >= 2:
            first_half = sorted_metrics[:len(sorted_metrics)//2]
            second_half = sorted_metrics[len(sorted_metrics)//2:]
            
            avg_first = sum(m.roi_percentage for m in first_half) / len(first_half)
            avg_second = sum(m.roi_percentage for m in second_half) / len(second_half)
            
            if avg_second > avg_first * 1.1:
                roi_trend = "increasing"
            elif avg_second < avg_first * 0.9:
                roi_trend = "decreasing"
            else:
                roi_trend = "stable"
        else:
            roi_trend = "stable"
        
        # 生成洞察
        insights = []
        
        best_metrics = metrics_dict[best_roi_session]
        worst_metrics = metrics_dict[worst_roi_session]
        
        insights.append(f"最佳 ROI 场次 ({best_roi_session}): {best_metrics.roi_percentage:.2f}%")
        insights.append(f"最差 ROI 场次 ({worst_roi_session}): {worst_metrics.roi_percentage:.2f}%")
        insights.append(f"ROI 差异：{best_metrics.roi_percentage - worst_metrics.roi_percentage:.2f}%")
        
        if best_metrics.total_cost < worst_metrics.total_cost:
            insights.append("低成本场次往往 ROI 更高，建议控制成本")
        
        if best_metrics.gmv > worst_metrics.gmv * 1.5:
            insights.append("高 GMV 场次 ROI 表现更好，建议提升销售额")
        
        if roi_trend == "increasing":
            insights.append("ROI 呈上升趋势，当前策略有效")
        elif roi_trend == "decreasing":
            insights.append("ROI 呈下降趋势，需要调整策略")
        else:
            insights.append("ROI 保持稳定，可继续当前策略")
        
        return ComparisonResult(
            sessions=session_ids,
            metrics=metrics_dict,
            best_roi_session=best_roi_session,
            worst_roi_session=worst_roi_session,
            average_roi=average_roi,
            roi_trend=roi_trend,
            insights=insights
        )
    
    def get_roi_trend(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        group_by: str = "day"  # day, week, month
    ) -> List[Dict]:
        """获取 ROI 趋势数据"""
        sessions = self.list_sessions(start_date, end_date)
        
        if not sessions:
            return []
        
        # 按时间分组
        grouped_data = {}
        
        for session in sessions:
            if group_by == "day":
                key = session.date
            elif group_by == "week":
                date = datetime.strptime(session.date, "%Y-%m-%d")
                key = date.strftime("%Y-W%W")
            elif group_by == "month":
                key = session.date[:7]  # YYYY-MM
            else:
                key = session.date
            
            if key not in grouped_data:
                grouped_data[key] = {"total_cost": 0, "total_revenue": 0, "count": 0}
            
            grouped_data[key]["total_cost"] += session.total_cost()
            grouped_data[key]["total_revenue"] += session.total_revenue()
            grouped_data[key]["count"] += 1
        
        # 计算 ROI
        trend_data = []
        for key, data in sorted(grouped_data.items()):
            roi = ((data["total_revenue"] - data["total_cost"]) / data["total_cost"] * 100) if data["total_cost"] > 0 else 0
            trend_data.append({
                "period": key,
                "total_cost": round(data["total_cost"], 2),
                "total_revenue": round(data["total_revenue"], 2),
                "roi_percentage": round(roi, 2),
                "session_count": data["count"]
            })
        
        return trend_data
    
    def generate_report(self, session_ids: Optional[List[str]] = None) -> Dict:
        """生成 ROI 分析报告"""
        if session_ids:
            sessions = [self.get_session(sid) for sid in session_ids if self.get_session(sid)]
        else:
            sessions = self.sessions
        
        if not sessions:
            return {"error": "没有可用的场次数据"}
        
        # 计算总体指标
        total_cost = sum(s.total_cost() for s in sessions)
        total_revenue = sum(s.total_revenue() for s in sessions)
        total_gmv = sum(s.gmv() for s in sessions)
        overall_roi = ((total_revenue - total_cost) / total_cost * 100) if total_cost > 0 else 0
        
        # 最佳和最差场次
        roi_values = [(s.session_id, s.roi()) for s in sessions]
        best_session = max(roi_values, key=lambda x: x[1])
        worst_session = min(roi_values, key=lambda x: x[1])
        
        # 成本分析
        cost_breakdown = {}
        for session in sessions:
            for cost in session.costs:
                if cost.type not in cost_breakdown:
                    cost_breakdown[cost.type] = 0
                cost_breakdown[cost.type] += cost.amount
        
        # 生成优化建议
        all_suggestions = []
        for session in sessions[:5]:  # 只分析前 5 场
            suggestions = self.generate_optimization_suggestions(session.session_id)
            all_suggestions.extend(suggestions)
        
        # 去重和排序建议
        unique_suggestions = {}
        for s in all_suggestions:
            if s.category not in unique_suggestions:
                unique_suggestions[s.category] = s
            elif s.estimated_savings > unique_suggestions[s.category].estimated_savings:
                unique_suggestions[s.category] = s
        
        report = {
            "report_id": f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_sessions": len(sessions),
                "total_cost": round(total_cost, 2),
                "total_revenue": round(total_revenue, 2),
                "total_gmv": round(total_gmv, 2),
                "total_profit": round(total_revenue - total_cost, 2),
                "overall_roi": round(overall_roi, 2)
            },
            "best_performer": {
                "session_id": best_session[0],
                "roi": round(best_session[1], 2)
            },
            "worst_performer": {
                "session_id": worst_session[0],
                "roi": round(worst_session[1], 2)
            },
            "cost_breakdown": cost_breakdown,
            "optimization_suggestions": [s.to_dict() for s in unique_suggestions.values()],
            "sessions": [s.to_dict() for s in sessions]
        }
        
        # 保存报告
        self.reports.append(report)
        with open(self.reports_path, "w", encoding="utf-8") as f:
            json.dump(self.reports, f, ensure_ascii=False, indent=2)
        
        return report
    
    def delete_session(self, session_id: str) -> bool:
        """删除直播场次"""
        for i, session in enumerate(self.sessions):
            if session.session_id == session_id:
                self.sessions.pop(i)
                self._save_sessions()
                return True
        return False
    
    def update_session(self, session_id: str, updates: Dict) -> Optional[LiveSession]:
        """更新直播场次"""
        session = self.get_session(session_id)
        if not session:
            return None
        
        # 应用更新
        for key, value in updates.items():
            if hasattr(session, key):
                setattr(session, key, value)
        
        self._save_sessions()
        return session


# 全局服务实例
_service: Optional[ROIAnalysisService] = None


def get_service() -> ROIAnalysisService:
    """获取 ROI 分析服务实例"""
    global _service
    if _service is None:
        _service = ROIAnalysisService()
    return _service


def reset_service():
    """重置服务实例（用于测试）"""
    global _service
    _service = None
