"""
营销活动策划服务
提供活动策划、时间规划、预算 ROI 预估、效果追踪、复盘报告和案例库功能
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import json
import uuid


class CampaignStatus(Enum):
    """活动状态"""
    DRAFT = "draft"  # 草稿
    PLANNING = "planning"  # 规划中
    ACTIVE = "active"  # 进行中
    COMPLETED = "completed"  # 已完成
    CANCELLED = "cancelled"  # 已取消


class CampaignType(Enum):
    """活动类型"""
    PRODUCT_LAUNCH = "product_launch"  # 产品发布
    PROMOTION = "promotion"  # 促销活动
    BRAND_AWARENESS = "brand_awareness"  # 品牌宣传
    USER_ACQUISITION = "user_acquisition"  # 用户获取
    RETENTION = "retention"  # 用户留存
    SEASONAL = "seasonal"  # 季节性活动


@dataclass
class BudgetItem:
    """预算项目"""
    category: str  # 类别（广告、内容、人力等）
    planned: float  # 预算金额
    actual: float = 0.0  # 实际花费
    description: str = ""


@dataclass
class TimelinePhase:
    """活动时间阶段"""
    name: str  # 阶段名称
    start_date: str  # 开始日期 (ISO format)
    end_date: str  # 结束日期 (ISO format)
    tasks: List[str] = field(default_factory=list)  # 任务列表
    status: str = "pending"  # pending/in_progress/completed


@dataclass
class Metric:
    """效果指标"""
    name: str  # 指标名称
    target: float  # 目标值
    actual: float = 0.0  # 实际值
    unit: str = ""  # 单位
    trend: str = "stable"  # stable/up/down


@dataclass
class CampaignTemplate:
    """活动策划模板"""
    id: str
    name: str
    description: str
    campaign_type: str
    recommended_duration_days: int
    typical_budget_range: Dict[str, float]
    key_metrics: List[str]
    checklist: List[str]
    best_practices: List[str]


@dataclass
class Campaign:
    """营销活动"""
    id: str
    name: str
    description: str
    campaign_type: str
    status: str
    start_date: str
    end_date: str
    budget_items: List[Dict]
    timeline: List[Dict]
    metrics: List[Dict]
    created_at: str
    updated_at: str
    notes: str = ""
    tags: List[str] = field(default_factory=list)


@dataclass
class CaseStudy:
    """优秀活动案例"""
    id: str
    title: str
    campaign_type: str
    industry: str
    description: str
    objectives: List[str]
    strategies: List[str]
    results: Dict[str, Any]
    budget: float
    roi: float
    duration_days: int
    key_learnings: List[str]
    created_at: str


class CampaignService:
    """营销活动策划服务"""
    
    def __init__(self):
        self.campaigns: Dict[str, Campaign] = {}
        self.case_studies: Dict[str, CaseStudy] = {}
        self.templates: Dict[str, CampaignTemplate] = {}
        self._init_templates()
        self._init_sample_cases()
    
    def _init_templates(self):
        """初始化活动模板"""
        templates = [
            CampaignTemplate(
                id="tpl_product_launch",
                name="产品发布活动",
                description="新产品上市推广活动策划模板",
                campaign_type=CampaignType.PRODUCT_LAUNCH.value,
                recommended_duration_days=30,
                typical_budget_range={"min": 50000, "max": 500000},
                key_metrics=["曝光量", "点击率", "转化率", "销售额", "新用户数"],
                checklist=[
                    "确定产品定位和目标受众",
                    "制定传播策略和渠道",
                    "准备宣传素材和内容",
                    "安排媒体和 KOL 合作",
                    "设置数据追踪和分析",
                    "准备应急预案"
                ],
                best_practices=[
                    "提前 2-3 周开始预热",
                    "多渠道同步发布",
                    "设置明确转化路径",
                    "实时监测数据调整策略"
                ]
            ),
            CampaignTemplate(
                id="tpl_promotion",
                name="促销活动",
                description="折扣促销类活动策划模板",
                campaign_type=CampaignType.PROMOTION.value,
                recommended_duration_days=14,
                typical_budget_range={"min": 10000, "max": 200000},
                key_metrics=["销售额", "订单量", "客单价", "转化率", "ROI"],
                checklist=[
                    "确定促销力度和规则",
                    "计算利润空间和预算",
                    "准备活动页面和素材",
                    "设置库存预警",
                    "安排客服支持",
                    "准备物流方案"
                ],
                best_practices=[
                    "制造紧迫感（限时/限量）",
                    "简化参与流程",
                    "设置阶梯优惠提升客单",
                    "活动后及时复盘"
                ]
            ),
            CampaignTemplate(
                id="tpl_brand",
                name="品牌宣传活动",
                description="品牌知名度和形象提升活动模板",
                campaign_type=CampaignType.BRAND_AWARENESS.value,
                recommended_duration_days=60,
                typical_budget_range={"min": 100000, "max": 1000000},
                key_metrics=["品牌提及量", "社交媒体互动", "搜索指数", "媒体曝光"],
                checklist=[
                    "明确品牌传播主题",
                    "策划创意内容",
                    "选择传播渠道和媒介",
                    "制作高质量内容素材",
                    "安排 KOL/明星合作",
                    "设置舆情监测"
                ],
                best_practices=[
                    "保持品牌调性一致",
                    "注重内容质量而非数量",
                    "与受众情感共鸣",
                    "长期持续投入"
                ]
            ),
            CampaignTemplate(
                id="tpl_user_acquisition",
                name="用户获取活动",
                description="新用户拉新活动策划模板",
                campaign_type=CampaignType.USER_ACQUISITION.value,
                recommended_duration_days=21,
                typical_budget_range={"min": 30000, "max": 300000},
                key_metrics=["新增用户数", "获客成本", "注册转化率", "激活率"],
                checklist=[
                    "定义目标用户画像",
                    "选择获客渠道",
                    "设计拉新激励",
                    "优化注册流程",
                    "设置转化漏斗追踪",
                    "准备新用户引导"
                ],
                best_practices=[
                    "降低首次体验门槛",
                    "设置推荐奖励机制",
                    "A/B 测试优化转化",
                    "关注用户质量而非数量"
                ]
            ),
            CampaignTemplate(
                id="tpl_retention",
                name="用户留存活动",
                description="提升用户活跃和留存的活动模板",
                campaign_type=CampaignType.RETENTION.value,
                recommended_duration_days=30,
                typical_budget_range={"min": 20000, "max": 150000},
                key_metrics=["活跃用户数", "留存率", "使用时长", "复购率"],
                checklist=[
                    "分析用户行为数据",
                    "识别流失风险用户",
                    "设计召回策略",
                    "准备个性化内容",
                    "设置用户激励体系",
                    "安排推送节奏"
                ],
                best_practices=[
                    "基于用户分层精准运营",
                    "提供真实价值而非骚扰",
                    "建立长期用户关系",
                    "持续优化用户体验"
                ]
            )
        ]
        for tpl in templates:
            self.templates[tpl.id] = tpl
    
    def _init_sample_cases(self):
        """初始化示例案例"""
        cases = [
            CaseStudy(
                id="case_001",
                title="某美妆品牌双 11 营销活动",
                campaign_type=CampaignType.PROMOTION.value,
                industry="美妆",
                description="通过预售 + 直播 + 社交裂变组合策略，实现双 11 销售爆发",
                objectives=[
                    "双 11 期间销售额突破 5000 万",
                    "新增会员 10 万+",
                    "品牌搜索指数提升 200%"
                ],
                strategies=[
                    "提前 20 天开启预售锁定用户",
                    "头部主播直播带货",
                    "社交裂变拉新（邀请有礼）",
                    "会员专属优惠券"
                ],
                results={
                    "销售额": 58000000,
                    "新增会员": 125000,
                    "直播观看": 3500000,
                    "ROI": 4.2
                },
                budget=1200000,
                roi=4.83,
                duration_days=25,
                key_learnings=[
                    "预售策略有效锁定购买意向",
                    "直播是美妆品类核心转化渠道",
                    "会员运营贡献 60% 销售额",
                    "需提前备货避免断货"
                ],
                created_at=datetime.now().isoformat()
            ),
            CaseStudy(
                id="case_002",
                title="某 SaaS 产品用户增长案例",
                campaign_type=CampaignType.USER_ACQUISITION.value,
                industry="科技/SaaS",
                description="通过内容营销 + 免费试用 + 推荐计划实现低成本获客",
                objectives=[
                    "月新增付费用户 1000+",
                    "获客成本控制在 200 元以内",
                    "试用转付费率提升至 25%"
                ],
                strategies=[
                    "高质量内容营销（博客/白皮书）",
                    "14 天免费试用 + 产品引导",
                    "老用户推荐奖励计划",
                    "SEO+SEM 组合投放"
                ],
                results={
                    "新增付费用户": 1250,
                    "获客成本": 165,
                    "试用转付费率": 0.28,
                    "ROI": 3.5
                },
                budget=200000,
                roi=3.5,
                duration_days=30,
                key_learnings=[
                    "内容营销带来高质量线索",
                    "产品引导显著提升转化率",
                    "推荐计划获客成本最低",
                    "需要持续优化落地页"
                ],
                created_at=datetime.now().isoformat()
            ),
            CaseStudy(
                id="case_003",
                title="某新消费品牌品牌塑造案例",
                campaign_type=CampaignType.BRAND_AWARENESS.value,
                industry="新消费",
                description="通过跨界联名 + 社交媒体引爆品牌知名度",
                objectives=[
                    "品牌知名度提升至 60%",
                    "社交媒体粉丝增长 50 万",
                    "建立年轻化品牌形象"
                ],
                strategies=[
                    "与知名 IP 跨界联名",
                    "小红书/抖音内容种草",
                    "KOL/KOC 矩阵投放",
                    "用户 UGC 内容征集"
                ],
                results={
                    "品牌知名度": 0.65,
                    "社交媒体粉丝": 580000,
                    "话题曝光量": 200000000,
                    "ROI": 2.8
                },
                budget=800000,
                roi=2.8,
                duration_days=60,
                key_learnings=[
                    "跨界联名快速提升品牌调性",
                    "小红书是核心种草阵地",
                    "UGC 内容带来持续传播",
                    "品牌建设需要长期投入"
                ],
                created_at=datetime.now().isoformat()
            )
        ]
        for case in cases:
            self.case_studies[case.id] = case
    
    # ========== 模板管理 ==========
    
    def get_templates(self) -> List[CampaignTemplate]:
        """获取所有活动模板"""
        return list(self.templates.values())
    
    def get_template(self, template_id: str) -> Optional[CampaignTemplate]:
        """获取指定模板"""
        return self.templates.get(template_id)
    
    def get_template_by_type(self, campaign_type: str) -> Optional[CampaignTemplate]:
        """根据活动类型获取模板"""
        for tpl in self.templates.values():
            if tpl.campaign_type == campaign_type:
                return tpl
        return None
    
    # ========== 活动管理 ==========
    
    def create_campaign(self, data: Dict[str, Any]) -> Campaign:
        """创建新活动"""
        now = datetime.now().isoformat()
        campaign = Campaign(
            id=str(uuid.uuid4())[:8],
            name=data.get("name", "未命名活动"),
            description=data.get("description", ""),
            campaign_type=data.get("campaign_type", CampaignType.PROMOTION.value),
            status=data.get("status", CampaignStatus.DRAFT.value),
            start_date=data.get("start_date", ""),
            end_date=data.get("end_date", ""),
            budget_items=data.get("budget_items", []),
            timeline=data.get("timeline", []),
            metrics=data.get("metrics", []),
            created_at=now,
            updated_at=now,
            notes=data.get("notes", ""),
            tags=data.get("tags", [])
        )
        self.campaigns[campaign.id] = campaign
        return campaign
    
    def get_campaign(self, campaign_id: str) -> Optional[Campaign]:
        """获取指定活动"""
        return self.campaigns.get(campaign_id)
    
    def get_all_campaigns(self, status: Optional[str] = None) -> List[Campaign]:
        """获取所有活动（可按状态筛选）"""
        campaigns = list(self.campaigns.values())
        if status:
            campaigns = [c for c in campaigns if c.status == status]
        return campaigns
    
    def update_campaign(self, campaign_id: str, data: Dict[str, Any]) -> Optional[Campaign]:
        """更新活动"""
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            return None
        
        for key, value in data.items():
            if hasattr(campaign, key):
                setattr(campaign, key, value)
        
        campaign.updated_at = datetime.now().isoformat()
        self.campaigns[campaign_id] = campaign
        return campaign
    
    def delete_campaign(self, campaign_id: str) -> bool:
        """删除活动"""
        if campaign_id in self.campaigns:
            del self.campaigns[campaign_id]
            return True
        return False
    
    def update_campaign_status(self, campaign_id: str, status: str) -> Optional[Campaign]:
        """更新活动状态"""
        return self.update_campaign(campaign_id, {"status": status})
    
    # ========== 时间规划 ==========
    
    def generate_timeline(self, campaign_type: str, start_date: str, duration_days: int) -> List[TimelinePhase]:
        """根据活动类型和时长生成时间规划"""
        template = self.get_template_by_type(campaign_type)
        if not template:
            return []
        
        start = datetime.fromisoformat(start_date.replace('Z', '+00:00')) if 'T' in start_date else datetime.strptime(start_date, "%Y-%m-%d")
        phases = []
        
        # 根据活动类型生成不同阶段
        if campaign_type == CampaignType.PRODUCT_LAUNCH.value:
            phase_configs = [
                ("预热期", 0.2, ["市场调研", "素材准备", "媒体对接"]),
                ("发布期", 0.3, ["产品发布", "媒体曝光", "KOL 推广"]),
                ("爆发期", 0.3, ["集中投放", "直播活动", "用户转化"]),
                ("延续期", 0.2, ["口碑维护", "长尾传播", "数据复盘"])
            ]
        elif campaign_type == CampaignType.PROMOTION.value:
            phase_configs = [
                ("准备期", 0.2, ["规则制定", "页面搭建", "库存准备"]),
                ("预热期", 0.3, ["活动预告", "优惠券发放", "用户蓄水"]),
                ("活动期", 0.4, ["正式促销", "实时运营", "客服支持"]),
                ("收尾期", 0.1, ["订单处理", "数据汇总", "活动复盘"])
            ]
        else:
            phase_configs = [
                ("策划期", 0.25, ["目标设定", "策略制定", "资源准备"]),
                ("执行期", 0.5, ["内容制作", "渠道投放", "数据监测"]),
                ("优化期", 0.15, ["A/B 测试", "策略调整", "效果优化"]),
                ("复盘期", 0.1, ["数据汇总", "效果分析", "经验总结"])
            ]
        
        for i, (name, ratio, tasks) in enumerate(phase_configs):
            phase_days = int(duration_days * ratio)
            phase_start = start + timedelta(days=sum(int(duration_days * phase_configs[j][1]) for j in range(i)))
            phase_end = phase_start + timedelta(days=phase_days - 1)
            
            phases.append(TimelinePhase(
                name=name,
                start_date=phase_start.strftime("%Y-%m-%d"),
                end_date=phase_end.strftime("%Y-%m-%d"),
                tasks=tasks
            ))
        
        return phases
    
    # ========== 预算和 ROI ==========
    
    def calculate_budget_total(self, budget_items: List[Dict]) -> Dict[str, float]:
        """计算预算总计"""
        planned_total = sum(item.get("planned", 0) for item in budget_items)
        actual_total = sum(item.get("actual", 0) for item in budget_items)
        return {
            "planned": planned_total,
            "actual": actual_total,
            "remaining": planned_total - actual_total,
            "utilization_rate": (actual_total / planned_total * 100) if planned_total > 0 else 0
        }
    
    def calculate_roi(self, revenue: float, cost: float) -> Dict[str, float]:
        """计算 ROI"""
        if cost == 0:
            return {"roi": 0, "profit": revenue, "roi_percentage": 0}
        
        profit = revenue - cost
        roi = profit / cost
        return {
            "roi": roi,
            "profit": profit,
            "roi_percentage": roi * 100
        }
    
    def estimate_roi(self, campaign_type: str, budget: float, industry_avg: Optional[float] = None) -> Dict[str, Any]:
        """预估 ROI（基于行业平均水平）"""
        # 各行业平均 ROI 基准
        industry_benchmarks = {
            CampaignType.PRODUCT_LAUNCH.value: 2.5,
            CampaignType.PROMOTION.value: 3.5,
            CampaignType.BRAND_AWARENESS.value: 1.8,
            CampaignType.USER_ACQUISITION.value: 3.0,
            CampaignType.RETENTION.value: 5.0,
            CampaignType.SEASONAL.value: 4.0
        }
        
        benchmark = industry_avg or industry_benchmarks.get(campaign_type, 2.5)
        
        # 根据预算规模调整预期（预算越大 ROI 可能越低）
        scale_factor = 1.0
        if budget > 500000:
            scale_factor = 0.85
        elif budget > 100000:
            scale_factor = 0.95
        elif budget < 50000:
            scale_factor = 1.1
        
        estimated_roi = benchmark * scale_factor
        estimated_revenue = budget * estimated_roi
        
        return {
            "estimated_roi": estimated_roi,
            "estimated_revenue": estimated_revenue,
            "estimated_profit": estimated_revenue - budget,
            "confidence": "medium",
            "benchmark_used": benchmark,
            "recommendation": f"建议设置 ROI 目标在 {estimated_roi * 0.8:.1f} - {estimated_roi * 1.2:.1f} 之间"
        }
    
    # ========== 效果追踪 ==========
    
    def update_metrics(self, campaign_id: str, metrics_data: List[Dict]) -> Optional[Campaign]:
        """更新活动指标数据"""
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            return None
        
        # 更新指标
        for new_metric in metrics_data:
            found = False
            for metric in campaign.metrics:
                if metric.get("name") == new_metric.get("name"):
                    metric["actual"] = new_metric.get("actual", metric.get("actual", 0))
                    # 计算趋势
                    target = metric.get("target", 0)
                    actual = metric["actual"]
                    if target > 0:
                        rate = actual / target
                        if rate >= 1.0:
                            metric["trend"] = "up"
                        elif rate >= 0.8:
                            metric["trend"] = "stable"
                        else:
                            metric["trend"] = "down"
                    found = True
                    break
            
            if not found:
                campaign.metrics.append(new_metric)
        
        campaign.updated_at = datetime.now().isoformat()
        self.campaigns[campaign_id] = campaign
        return campaign
    
    def get_campaign_performance(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """获取活动效果报告"""
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            return None
        
        # 计算指标达成率
        metrics_summary = []
        overall_progress = 0
        
        for metric in campaign.metrics:
            target = metric.get("target", 0)
            actual = metric.get("actual", 0)
            progress = (actual / target * 100) if target > 0 else 0
            overall_progress += progress
            metrics_summary.append({
                "name": metric.get("name"),
                "target": target,
                "actual": actual,
                "progress": round(progress, 1),
                "trend": metric.get("trend", "stable"),
                "unit": metric.get("unit", "")
            })
        
        avg_progress = overall_progress / len(campaign.metrics) if campaign.metrics else 0
        
        # 预算执行情况
        budget_summary = self.calculate_budget_total(campaign.budget_items)
        
        return {
            "campaign_id": campaign_id,
            "campaign_name": campaign.name,
            "status": campaign.status,
            "overall_progress": round(avg_progress, 1),
            "metrics": metrics_summary,
            "budget": budget_summary,
            "timeline_progress": self._calculate_timeline_progress(campaign.timeline),
            "health_score": self._calculate_health_score(avg_progress, budget_summary.get("utilization_rate", 0))
        }
    
    def _calculate_timeline_progress(self, timeline: List[Dict]) -> Dict[str, Any]:
        """计算时间线进度"""
        if not timeline:
            return {"total_phases": 0, "completed": 0, "in_progress": 0, "pending": 0}
        
        completed = sum(1 for p in timeline if p.get("status") == "completed")
        in_progress = sum(1 for p in timeline if p.get("status") == "in_progress")
        pending = sum(1 for p in timeline if p.get("status") == "pending")
        
        return {
            "total_phases": len(timeline),
            "completed": completed,
            "in_progress": in_progress,
            "pending": pending,
            "progress_rate": round(completed / len(timeline) * 100, 1) if timeline else 0
        }
    
    def _calculate_health_score(self, metric_progress: float, budget_utilization: float) -> float:
        """计算活动健康度评分（0-100）"""
        # 指标进度权重 60%，预算执行权重 40%
        metric_score = min(metric_progress, 100) * 0.6
        # 预算执行率在 70-100% 之间得分最高
        if 70 <= budget_utilization <= 100:
            budget_score = 40
        elif budget_utilization < 70:
            budget_score = budget_utilization / 70 * 40
        else:
            budget_score = max(0, 40 - (budget_utilization - 100) * 0.5)
        
        return round(metric_score + budget_score, 1)
    
    # ========== 复盘报告 ==========
    
    def generate_review_report(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """生成活动复盘报告"""
        campaign = self.campaigns.get(campaign_id)
        if not campaign:
            return None
        
        performance = self.get_campaign_performance(campaign_id)
        budget_summary = self.calculate_budget_total(campaign.budget_items)
        
        # 计算实际 ROI
        total_revenue = sum(m.get("actual", 0) for m in campaign.metrics if "销售" in m.get("name", "") or "收入" in m.get("name", ""))
        roi_data = self.calculate_roi(total_revenue, budget_summary.get("actual", 0))
        
        # 生成亮点和不足
        highlights = []
        improvements = []
        
        for metric in performance.get("metrics", []):
            if metric["progress"] >= 100:
                highlights.append(f"{metric['name']} 达成目标 ({metric['progress']}%)")
            elif metric["progress"] < 80:
                improvements.append(f"{metric['name']} 未达预期 (仅{metric['progress']}%)")
        
        if budget_summary.get("utilization_rate", 0) < 90:
            highlights.append("预算控制良好")
        elif budget_summary.get("utilization_rate", 0) > 110:
            improvements.append("预算超支，需加强成本管控")
        
        # 生成建议
        recommendations = []
        if performance.get("overall_progress", 0) >= 100:
            recommendations.append("成功经验可复制到其他活动")
        if roi_data.get("roi", 0) > 3:
            recommendations.append("ROI 表现优秀，可考虑加大投入")
        elif roi_data.get("roi", 0) < 1:
            recommendations.append("ROI 偏低，需优化转化路径或降低成本")
        
        return {
            "campaign_id": campaign_id,
            "campaign_name": campaign.name,
            "campaign_type": campaign.campaign_type,
            "period": f"{campaign.start_date} 至 {campaign.end_date}",
            "summary": {
                "overall_progress": performance.get("overall_progress", 0),
                "health_score": performance.get("health_score", 0),
                "budget_total": budget_summary.get("actual", 0),
                "estimated_roi": roi_data.get("roi", 0),
                "estimated_profit": roi_data.get("profit", 0)
            },
            "highlights": highlights,
            "improvements": improvements,
            "recommendations": recommendations,
            "detailed_metrics": performance.get("metrics", []),
            "budget_breakdown": campaign.budget_items,
            "generated_at": datetime.now().isoformat()
        }
    
    # ========== 案例库 ==========
    
    def get_case_studies(self, campaign_type: Optional[str] = None, industry: Optional[str] = None) -> List[CaseStudy]:
        """获取案例（可筛选）"""
        cases = list(self.case_studies.values())
        
        if campaign_type:
            cases = [c for c in cases if c.campaign_type == campaign_type]
        if industry:
            cases = [c for c in cases if c.industry == industry]
        
        return cases
    
    def get_case_study(self, case_id: str) -> Optional[CaseStudy]:
        """获取指定案例"""
        return self.case_studies.get(case_id)
    
    def add_case_study(self, data: Dict[str, Any]) -> CaseStudy:
        """添加新案例"""
        case = CaseStudy(
            id=str(uuid.uuid4())[:8],
            title=data.get("title", "未命名案例"),
            campaign_type=data.get("campaign_type", ""),
            industry=data.get("industry", ""),
            description=data.get("description", ""),
            objectives=data.get("objectives", []),
            strategies=data.get("strategies", []),
            results=data.get("results", {}),
            budget=data.get("budget", 0),
            roi=data.get("roi", 0),
            duration_days=data.get("duration_days", 0),
            key_learnings=data.get("key_learnings", []),
            created_at=datetime.now().isoformat()
        )
        self.case_studies[case.id] = case
        return case
    
    def search_cases(self, keywords: List[str]) -> List[CaseStudy]:
        """搜索案例"""
        results = []
        for case in self.case_studies.values():
            search_text = f"{case.title} {case.description} {' '.join(case.strategies)} {' '.join(case.key_learnings)}".lower()
            if any(kw.lower() in search_text for kw in keywords):
                results.append(case)
        return results


# 单例服务实例
campaign_service = CampaignService()
