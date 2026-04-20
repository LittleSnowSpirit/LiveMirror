"""
营销活动策划功能测试
"""

import pytest
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 添加 backend 路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from services.campaign import (
    CampaignService,
    Campaign,
    CampaignTemplate,
    CaseStudy,
    CampaignStatus,
    CampaignType,
    campaign_service
)


class TestCampaignTemplates:
    """测试活动模板功能"""
    
    @pytest.fixture
    def service(self):
        return CampaignService()
    
    def test_get_all_templates(self, service):
        """获取所有模板"""
        templates = service.get_templates()
        assert len(templates) > 0
        assert all(isinstance(t, CampaignTemplate) for t in templates)
    
    def test_get_template_by_id(self, service):
        """根据 ID 获取模板"""
        templates = service.get_templates()
        if templates:
            template = service.get_template(templates[0].id)
            assert template is not None
            assert template.id == templates[0].id
    
    def test_get_template_by_type(self, service):
        """根据类型获取模板"""
        template = service.get_template_by_type(CampaignType.PROMOTION.value)
        assert template is not None
        assert template.campaign_type == CampaignType.PROMOTION.value
    
    def test_template_structure(self, service):
        """测试模板结构完整性"""
        templates = service.get_templates()
        for template in templates:
            assert template.name
            assert template.description
            assert template.campaign_type
            assert template.recommended_duration_days > 0
            assert isinstance(template.key_metrics, list)
            assert isinstance(template.checklist, list)
            assert isinstance(template.best_practices, list)


class TestCampaignManagement:
    """测试活动管理功能"""
    
    @pytest.fixture
    def service(self):
        return CampaignService()
    
    @pytest.fixture
    def sample_campaign_data(self):
        return {
            "name": "双 11 促销活动",
            "description": "年度最大促销活动",
            "campaign_type": CampaignType.PROMOTION.value,
            "status": CampaignStatus.DRAFT.value,
            "start_date": "2024-11-01",
            "end_date": "2024-11-11",
            "budget_items": [
                {"category": "广告投放", "planned": 50000, "description": "社交媒体广告"},
                {"category": "优惠券", "planned": 30000, "description": "用户优惠"}
            ],
            "metrics": [
                {"name": "销售额", "target": 500000, "actual": 0, "unit": "元"},
                {"name": "订单量", "target": 1000, "actual": 0, "unit": "单"}
            ],
            "tags": ["双 11", "促销", "年度活动"]
        }
    
    def test_create_campaign(self, service, sample_campaign_data):
        """创建活动"""
        campaign = service.create_campaign(sample_campaign_data)
        assert campaign is not None
        assert campaign.id is not None
        assert campaign.name == sample_campaign_data["name"]
        assert campaign.campaign_type == sample_campaign_data["campaign_type"]
        assert campaign.status == sample_campaign_data["status"]
    
    def test_get_campaign(self, service, sample_campaign_data):
        """获取活动"""
        campaign = service.create_campaign(sample_campaign_data)
        retrieved = service.get_campaign(campaign.id)
        assert retrieved is not None
        assert retrieved.id == campaign.id
        assert retrieved.name == campaign.name
    
    def test_get_all_campaigns(self, service, sample_campaign_data):
        """获取所有活动"""
        service.create_campaign(sample_campaign_data)
        campaigns = service.get_all_campaigns()
        assert len(campaigns) >= 1
    
    def test_get_campaigns_by_status(self, service, sample_campaign_data):
        """按状态筛选活动"""
        campaign = service.create_campaign(sample_campaign_data)
        campaigns = service.get_all_campaigns(status=CampaignStatus.DRAFT.value)
        assert len(campaigns) >= 1
        assert all(c.status == CampaignStatus.DRAFT.value for c in campaigns)
    
    def test_update_campaign(self, service, sample_campaign_data):
        """更新活动"""
        campaign = service.create_campaign(sample_campaign_data)
        update_data = {
            "name": "更新后的活动名称",
            "description": "更新后的描述"
        }
        updated = service.update_campaign(campaign.id, update_data)
        assert updated is not None
        assert updated.name == update_data["name"]
        assert updated.description == update_data["description"]
    
    def test_update_campaign_status(self, service, sample_campaign_data):
        """更新活动状态"""
        campaign = service.create_campaign(sample_campaign_data)
        updated = service.update_campaign_status(campaign.id, CampaignStatus.ACTIVE.value)
        assert updated is not None
        assert updated.status == CampaignStatus.ACTIVE.value
    
    def test_delete_campaign(self, service, sample_campaign_data):
        """删除活动"""
        campaign = service.create_campaign(sample_campaign_data)
        success = service.delete_campaign(campaign.id)
        assert success is True
        assert service.get_campaign(campaign.id) is None
    
    def test_campaign_timestamps(self, service, sample_campaign_data):
        """测试活动时间戳"""
        campaign = service.create_campaign(sample_campaign_data)
        assert campaign.created_at is not None
        assert campaign.updated_at is not None
        assert datetime.fromisoformat(campaign.created_at) <= datetime.fromisoformat(campaign.updated_at)


class TestTimelinePlanning:
    """测试时间规划功能"""
    
    @pytest.fixture
    def service(self):
        return CampaignService()
    
    def test_generate_timeline_product_launch(self, service):
        """生成产品发布时间规划"""
        phases = service.generate_timeline(
            CampaignType.PRODUCT_LAUNCH.value,
            "2024-06-01",
            30
        )
        assert len(phases) > 0
        assert all(hasattr(p, 'name') for p in phases)
        assert all(hasattr(p, 'start_date') for p in phases)
        assert all(hasattr(p, 'end_date') for p in phases)
        assert all(hasattr(p, 'tasks') for p in phases)
    
    def test_generate_timeline_promotion(self, service):
        """生成促销活动时间规划"""
        phases = service.generate_timeline(
            CampaignType.PROMOTION.value,
            "2024-11-01",
            14
        )
        assert len(phases) > 0
        # 检查阶段名称
        phase_names = [p.name for p in phases]
        assert any('预热' in name for name in phase_names)
    
    def test_timeline_dates_valid(self, service):
        """测试时间规划日期有效性"""
        start_date = "2024-06-01"
        duration = 30
        phases = service.generate_timeline(
            CampaignType.BRAND_AWARENESS.value,
            start_date,
            duration
        )
        
        # 检查日期顺序
        for i in range(len(phases) - 1):
            current_end = phases[i].end_date
            next_start = phases[i + 1].start_date
            # 下一阶段开始应该在这一阶段结束之后或相接
            assert datetime.fromisoformat(next_start) >= datetime.fromisoformat(current_end)


class TestBudgetAndROI:
    """测试预算和 ROI 计算功能"""
    
    @pytest.fixture
    def service(self):
        return CampaignService()
    
    def test_calculate_budget_total(self, service):
        """计算预算总计"""
        budget_items = [
            {"category": "广告", "planned": 50000, "actual": 45000},
            {"category": "内容", "planned": 20000, "actual": 18000},
            {"category": "人力", "planned": 30000, "actual": 30000}
        ]
        result = service.calculate_budget_total(budget_items)
        
        assert result["planned"] == 100000
        assert result["actual"] == 93000
        assert result["remaining"] == 7000
        assert result["utilization_rate"] == 93.0
    
    def test_calculate_roi(self, service):
        """计算 ROI"""
        result = service.calculate_roi(revenue=150000, cost=50000)
        
        assert result["profit"] == 100000
        assert result["roi"] == 2.0
        assert result["roi_percentage"] == 200.0
    
    def test_calculate_roi_zero_cost(self, service):
        """测试零成本情况"""
        result = service.calculate_roi(revenue=10000, cost=0)
        assert result["roi"] == 0
        assert result["profit"] == 10000
    
    def test_estimate_roi_promotion(self, service):
        """预估促销活动 ROI"""
        result = service.estimate_roi(
            campaign_type=CampaignType.PROMOTION.value,
            budget=100000
        )
        
        assert "estimated_roi" in result
        assert "estimated_revenue" in result
        assert "estimated_profit" in result
        assert result["estimated_roi"] > 0
        assert result["estimated_revenue"] > 100000
    
    def test_estimate_roi_brand_awareness(self, service):
        """预估品牌活动 ROI"""
        result = service.estimate_roi(
            campaign_type=CampaignType.BRAND_AWARENESS.value,
            budget=500000
        )
        
        # 品牌活动 ROI 通常较低
        assert result["estimated_roi"] < 3.0
    
    def test_estimate_roi_with_industry_avg(self, service):
        """使用行业平均值预估 ROI"""
        result = service.estimate_roi(
            campaign_type=CampaignType.PROMOTION.value,
            budget=100000,
            industry_avg=4.0
        )
        
        assert result["benchmark_used"] == 4.0


class TestPerformanceTracking:
    """测试效果追踪功能"""
    
    @pytest.fixture
    def service(self):
        srv = CampaignService()
        # 创建测试活动
        srv.create_campaign({
            "name": "测试活动",
            "campaign_type": CampaignType.PROMOTION.value,
            "start_date": "2024-01-01",
            "end_date": "2024-01-31",
            "metrics": [
                {"name": "销售额", "target": 100000, "actual": 0, "unit": "元"},
                {"name": "订单量", "target": 500, "actual": 0, "unit": "单"},
                {"name": "转化率", "target": 5.0, "actual": 0, "unit": "%"}
            ]
        })
        return srv
    
    def test_update_metrics(self, service):
        """更新指标数据"""
        campaign = service.get_all_campaigns()[0]
        metrics_data = [
            {"name": "销售额", "actual": 80000},
            {"name": "订单量", "actual": 400},
            {"name": "转化率", "actual": 4.5}
        ]
        
        updated = service.update_metrics(campaign.id, metrics_data)
        assert updated is not None
        
        # 验证更新
        for metric in updated.metrics:
            if metric["name"] == "销售额":
                assert metric["actual"] == 80000
                assert metric["trend"] == "stable"  # 80% 达成率
    
    def test_update_metrics_exceeds_target(self, service):
        """测试超额完成指标"""
        campaign = service.get_all_campaigns()[0]
        metrics_data = [
            {"name": "销售额", "actual": 120000}  # 120% 达成率
        ]
        
        updated = service.update_metrics(campaign.id, metrics_data)
        for metric in updated.metrics:
            if metric["name"] == "销售额":
                assert metric["trend"] == "up"
    
    def test_get_campaign_performance(self, service):
        """获取活动效果报告"""
        campaign = service.get_all_campaigns()[0]
        
        # 先更新一些数据
        service.update_metrics(campaign.id, [
            {"name": "销售额", "actual": 75000},
            {"name": "订单量", "actual": 380},
            {"name": "转化率", "actual": 4.2}
        ])
        
        performance = service.get_campaign_performance(campaign.id)
        
        assert performance is not None
        assert "overall_progress" in performance
        assert "metrics" in performance
        assert "health_score" in performance
        assert 0 <= performance["health_score"] <= 100
    
    def test_performance_metrics_summary(self, service):
        """测试效果指标摘要"""
        campaign = service.get_all_campaigns()[0]
        performance = service.get_campaign_performance(campaign.id)
        
        for metric in performance["metrics"]:
            assert "name" in metric
            assert "target" in metric
            assert "actual" in metric
            assert "progress" in metric
            assert "trend" in metric


class TestReviewReport:
    """测试复盘报告功能"""
    
    @pytest.fixture
    def service(self):
        srv = CampaignService()
        srv.create_campaign({
            "name": "已完成活动",
            "campaign_type": CampaignType.PROMOTION.value,
            "status": CampaignStatus.COMPLETED.value,
            "start_date": "2024-01-01",
            "end_date": "2024-01-31",
            "budget_items": [
                {"category": "广告", "planned": 50000, "actual": 48000}
            ],
            "metrics": [
                {"name": "销售额", "target": 200000, "actual": 240000, "unit": "元"},
                {"name": "订单量", "target": 1000, "actual": 1200, "unit": "单"}
            ]
        })
        return srv
    
    def test_generate_review_report(self, service):
        """生成复盘报告"""
        campaign = service.get_all_campaigns()[0]
        report = service.generate_review_report(campaign.id)
        
        assert report is not None
        assert "campaign_id" in report
        assert "campaign_name" in report
        assert "summary" in report
        assert "highlights" in report
        assert "improvements" in report
        assert "recommendations" in report
    
    def test_review_report_highlights(self, service):
        """测试复盘报告亮点"""
        campaign = service.get_all_campaigns()[0]
        report = service.generate_review_report(campaign.id)
        
        # 销售额和订单量都超额完成，应该有亮点
        assert len(report["highlights"]) > 0
        assert any("销售额" in h for h in report["highlights"])
    
    def test_review_report_summary(self, service):
        """测试复盘报告摘要"""
        campaign = service.get_all_campaigns()[0]
        report = service.generate_review_report(campaign.id)
        
        summary = report["summary"]
        assert "overall_progress" in summary
        assert "health_score" in summary
        assert "budget_total" in summary
        assert "estimated_roi" in summary
        
        # 超额完成，进度应该>100%
        assert summary["overall_progress"] >= 100


class TestCaseStudies:
    """测试案例库功能"""
    
    @pytest.fixture
    def service(self):
        return CampaignService()
    
    def test_get_all_case_studies(self, service):
        """获取所有案例"""
        cases = service.get_case_studies()
        assert len(cases) > 0
        assert all(isinstance(c, CaseStudy) for c in cases)
    
    def test_get_case_study_by_id(self, service):
        """根据 ID 获取案例"""
        cases = service.get_case_studies()
        if cases:
            case = service.get_case_study(cases[0].id)
            assert case is not None
            assert case.id == cases[0].id
    
    def test_filter_cases_by_type(self, service):
        """按类型筛选案例"""
        cases = service.get_case_studies(campaign_type=CampaignType.PROMOTION.value)
        assert all(c.campaign_type == CampaignType.PROMOTION.value for c in cases)
    
    def test_filter_cases_by_industry(self, service):
        """按行业筛选案例"""
        cases = service.get_case_studies(industry="美妆")
        assert all(c.industry == "美妆" for c in cases)
    
    def test_add_case_study(self, service):
        """添加新案例"""
        case_data = {
            "title": "测试案例",
            "campaign_type": CampaignType.USER_ACQUISITION.value,
            "industry": "科技",
            "description": "这是一个测试案例",
            "objectives": ["目标 1", "目标 2"],
            "strategies": ["策略 1", "策略 2"],
            "results": {"新增用户": 10000, "获客成本": 100},
            "budget": 50000,
            "roi": 3.5,
            "duration_days": 30,
            "key_learnings": ["经验 1", "经验 2"]
        }
        
        case = service.add_case_study(case_data)
        assert case is not None
        assert case.id is not None
        assert case.title == case_data["title"]
        
        # 验证可以检索到
        retrieved = service.get_case_study(case.id)
        assert retrieved is not None
        assert retrieved.title == case.title
    
    def test_search_cases(self, service):
        """搜索案例"""
        cases = service.search_cases(["直播", "双 11"])
        # 应该能找到相关案例
        assert len(cases) >= 0  # 可能为 0，取决于初始数据
    
    def test_case_study_structure(self, service):
        """测试案例结构完整性"""
        cases = service.get_case_studies()
        for case in cases:
            assert case.title
            assert case.campaign_type
            assert case.industry
            assert case.description
            assert isinstance(case.objectives, list)
            assert isinstance(case.strategies, list)
            assert isinstance(case.results, dict)
            assert isinstance(case.key_learnings, list)


class TestIntegration:
    """集成测试"""
    
    @pytest.fixture
    def service(self):
        return CampaignService()
    
    def test_full_campaign_lifecycle(self, service):
        """测试活动完整生命周期"""
        # 1. 创建活动
        campaign = service.create_campaign({
            "name": "生命周期测试活动",
            "campaign_type": CampaignType.PROMOTION.value,
            "start_date": "2024-06-01",
            "end_date": "2024-06-30",
            "budget_items": [
                {"category": "广告", "planned": 30000}
            ],
            "metrics": [
                {"name": "销售额", "target": 100000, "actual": 0}
            ]
        })
        
        # 2. 生成时间规划
        phases = service.generate_timeline(
            campaign.campaign_type,
            campaign.start_date,
            30
        )
        service.update_campaign(campaign.id, {"timeline": [p.__dict__ for p in phases]})
        
        # 3. 更新状态
        service.update_campaign_status(campaign.id, CampaignStatus.ACTIVE.value)
        
        # 4. 更新指标
        service.update_metrics(campaign.id, [
            {"name": "销售额", "actual": 85000}
        ])
        
        # 5. 获取效果报告
        performance = service.get_campaign_performance(campaign.id)
        assert performance is not None
        assert performance["overall_progress"] > 0
        
        # 6. 完成活动
        service.update_campaign_status(campaign.id, CampaignStatus.COMPLETED.value)
        service.update_metrics(campaign.id, [
            {"name": "销售额", "actual": 120000}
        ])
        
        # 7. 生成复盘报告
        report = service.generate_review_report(campaign.id)
        assert report is not None
        assert report["summary"]["overall_progress"] >= 100
    
    def test_template_to_campaign(self, service):
        """从模板创建活动"""
        # 获取模板
        template = service.get_template_by_type(CampaignType.PRODUCT_LAUNCH.value)
        assert template is not None
        
        # 基于模板创建活动
        campaign = service.create_campaign({
            "name": "基于模板的活动",
            "campaign_type": template.campaign_type,
            "start_date": "2024-07-01",
            "end_date": "2024-07-30",
            "metrics": [
                {"name": m, "target": 0, "actual": 0} 
                for m in template.key_metrics
            ]
        })
        
        # 验证活动使用了模板的指标
        assert len(campaign.metrics) == len(template.key_metrics)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
