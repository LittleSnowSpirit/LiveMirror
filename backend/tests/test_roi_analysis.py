"""
直播 ROI 分析服务测试 - LiveMirror
"""

import pytest
from datetime import datetime, timedelta
from backend.services.roi_analysis import (
    ROIAnalysisService,
    LiveSession,
    CostItem,
    RevenueItem,
    get_service,
    reset_service
)


class TestROIAnalysisService:
    """ROI 分析服务测试"""
    
    @pytest.fixture
    def service(self):
        """创建测试服务实例"""
        reset_service()
        # 使用唯一的数据目录避免污染
        import uuid
        test_id = str(uuid.uuid4())[:8]
        return ROIAnalysisService(data_dir=f"data/test_roi_{test_id}")
    
    @pytest.fixture
    def sample_session(self, service):
        """创建示例场次"""
        # 清除之前的数据
        service.sessions = []
        session = service.create_session(
            date="2026-04-08",
            start_time="19:00",
            end_time="22:00",
            category="general",
            costs=[
                {"type": "labor", "name": "主播", "amount": 500},
                {"type": "venue", "name": "场地租赁", "amount": 300},
                {"type": "promotion", "name": "广告投放", "amount": 200}
            ],
            revenues=[
                {"type": "gmv", "name": "商品销售", "amount": 5000},
                {"type": "profit", "name": "利润", "amount": 1000}
            ],
            notes="测试场次"
        )
        return session
    
    # ============== 测试成本核算 ==============
    
    def test_create_session(self, service):
        """测试创建场次"""
        session = service.create_session(
            date="2026-04-08",
            start_time="19:00",
            end_time="22:00",
            category="general",
            costs=[
                {"type": "labor", "name": "主播", "amount": 500},
                {"type": "venue", "name": "场地租赁", "amount": 300}
            ],
            revenues=[
                {"type": "gmv", "name": "销售", "amount": 3000}
            ]
        )
        
        assert session.session_id.startswith("session_")
        assert session.date == "2026-04-08"
        assert session.duration_minutes == 180
        assert len(session.costs) == 2
        assert len(session.revenues) == 1
    
    def test_total_cost_calculation(self, service, sample_session):
        """测试总成本计算"""
        total_cost = sample_session.total_cost()
        assert total_cost == 1000  # 500 + 300 + 200
    
    def test_cost_breakdown(self, service, sample_session):
        """测试成本分解"""
        breakdown = service.get_cost_breakdown(sample_session.session_id)
        
        assert breakdown is not None
        assert breakdown.get("labor") == 500
        assert breakdown.get("venue") == 300
        assert breakdown.get("promotion") == 200
    
    def test_multiple_cost_items(self, service):
        """测试多个同类成本项"""
        session = service.create_session(
            date="2026-04-08",
            start_time="19:00",
            end_time="21:00",
            costs=[
                {"type": "labor", "name": "主播", "amount": 300},
                {"type": "labor", "name": "助理", "amount": 200},
                {"type": "labor", "name": "运营", "amount": 200}
            ],
            revenues=[]
        )
        
        total_cost = session.total_cost()
        assert total_cost == 700
        
        breakdown = service.get_cost_breakdown(session.session_id)
        assert breakdown.get("labor") == 700
    
    # ============== 测试收益统计 ==============
    
    def test_gmv_calculation(self, service, sample_session):
        """测试 GMV 计算"""
        gmv = sample_session.gmv()
        assert gmv == 5000
    
    def test_revenue_calculation(self, service, sample_session):
        """测试总收益计算"""
        total_revenue = sample_session.total_revenue()
        assert total_revenue == 1000  # 使用利润项
    
    def test_revenue_from_gmv(self, service):
        """测试从 GMV 估算收益"""
        session = service.create_session(
            date="2026-04-08",
            start_time="19:00",
            end_time="21:00",
            costs=[{"type": "labor", "name": "主播", "amount": 500}],
            revenues=[{"type": "gmv", "name": "销售", "amount": 5000}]
        )
        
        # 应该使用 GMV * 20% 估算
        total_revenue = session.total_revenue()
        assert total_revenue == 1000  # 5000 * 0.2
    
    # ============== 测试 ROI 计算 ==============
    
    def test_roi_calculation(self, service, sample_session):
        """测试 ROI 计算"""
        roi = sample_session.roi()
        # ROI = (收益 - 成本) / 成本 * 100 = (1000 - 1000) / 1000 * 100 = 0%
        assert roi == 0.0
    
    def test_roi_positive(self, service):
        """测试正 ROI"""
        session = service.create_session(
            date="2026-04-08",
            start_time="19:00",
            end_time="21:00",
            costs=[{"type": "labor", "name": "主播", "amount": 500}],
            revenues=[{"type": "profit", "name": "利润", "amount": 1000}]
        )
        
        roi = session.roi()
        # ROI = (1000 - 500) / 500 * 100 = 100%
        assert roi == 100.0
    
    def test_roi_negative(self, service):
        """测试负 ROI"""
        session = service.create_session(
            date="2026-04-08",
            start_time="19:00",
            end_time="21:00",
            costs=[{"type": "labor", "name": "主播", "amount": 1000}],
            revenues=[{"type": "profit", "name": "利润", "amount": 500}]
        )
        
        roi = session.roi()
        # ROI = (500 - 1000) / 1000 * 100 = -50%
        assert roi == -50.0
    
    def test_roi_zero_cost(self, service):
        """测试零成本时的 ROI"""
        session = service.create_session(
            date="2026-04-08",
            start_time="19:00",
            end_time="21:00",
            costs=[],
            revenues=[{"type": "profit", "name": "利润", "amount": 1000}]
        )
        
        roi = session.roi()
        assert roi == 0.0
    
    def test_roi_metrics(self, service, sample_session):
        """测试 ROI 指标计算"""
        metrics = service.calculate_roi_metrics(sample_session.session_id)
        
        assert metrics is not None
        assert metrics.total_cost == 1000
        assert metrics.total_revenue == 1000
        assert metrics.gmv == 5000
        assert metrics.profit == 1000
        assert metrics.roi_percentage == 0.0
        assert metrics.roi_ratio == 1.0
    
    # ============== 测试对比分析 ==============
    
    def test_compare_sessions(self, service):
        """测试多场次对比"""
        # 清除之前的数据
        service.sessions = []
        # 创建两个场次
        session1 = service.create_session(
            date="2026-04-08",
            start_time="19:00",
            end_time="21:00",
            costs=[{"type": "labor", "name": "主播", "amount": 500}],
            revenues=[{"type": "profit", "name": "利润", "amount": 1000}]
        )
        
        session2 = service.create_session(
            date="2026-04-09",
            start_time="19:00",
            end_time="21:00",
            costs=[{"type": "labor", "name": "主播", "amount": 800}],
            revenues=[{"type": "profit", "name": "利润", "amount": 800}]
        )
        
        result = service.compare_sessions([session1.session_id, session2.session_id])
        
        assert result is not None
        assert len(result.sessions) == 2
        # session1 ROI = (1000-500)/500*100 = 100%
        # session2 ROI = (800-800)/800*100 = 0%
        assert result.best_roi_session == session1.session_id
        assert result.worst_roi_session == session2.session_id
        assert len(result.insights) > 0
    
    def test_compare_sessions_insufficient(self, service):
        """测试场次不足时的对比"""
        session = service.create_session(
            date="2026-04-08",
            start_time="19:00",
            end_time="21:00",
            costs=[],
            revenues=[]
        )
        
        result = service.compare_sessions([session.session_id])
        assert result is None
    
    def test_roi_trend(self, service):
        """测试 ROI 趋势"""
        # 创建多个场次
        for i in range(5):
            date = f"2026-04-{8+i:02d}"
            service.create_session(
                date=date,
                start_time="19:00",
                end_time="21:00",
                costs=[{"type": "labor", "name": "主播", "amount": 500 + i * 100}],
                revenues=[{"type": "profit", "name": "利润", "amount": 1000}]
            )
        
        trend = service.get_roi_trend(group_by="day")
        
        assert len(trend) == 5
        assert "period" in trend[0]
        assert "roi_percentage" in trend[0]
        assert "total_cost" in trend[0]
        assert "total_revenue" in trend[0]
    
    # ============== 测试优化建议 ==============
    
    def test_optimization_suggestions_high_labor(self, service):
        """测试人力成本过高的建议"""
        session = service.create_session(
            date="2026-04-08",
            start_time="19:00",
            end_time="21:00",
            costs=[
                {"type": "labor", "name": "主播", "amount": 800},
                {"type": "venue", "name": "场地", "amount": 100},
                {"type": "promotion", "name": "推广", "amount": 100}
            ],
            revenues=[{"type": "profit", "name": "利润", "amount": 500}]
        )
        
        suggestions = service.generate_optimization_suggestions(session.session_id)
        
        # 人力成本占比 80%，应该有高优先级建议
        labor_suggestions = [s for s in suggestions if s.category == "labor"]
        assert len(labor_suggestions) > 0
        assert labor_suggestions[0].priority == "high"
    
    def test_optimization_suggestions_negative_roi(self, service):
        """测试负 ROI 的建议"""
        session = service.create_session(
            date="2026-04-08",
            start_time="19:00",
            end_time="21:00",
            costs=[{"type": "labor", "name": "主播", "amount": 1000}],
            revenues=[{"type": "profit", "name": "利润", "amount": 500}]
        )
        
        suggestions = service.generate_optimization_suggestions(session.session_id)
        
        # 负 ROI 应该有整体优化建议
        overall_suggestions = [s for s in suggestions if s.category == "overall"]
        assert len(overall_suggestions) > 0
        assert overall_suggestions[0].priority == "high"
    
    def test_optimization_suggestions_low_roi(self, service):
        """测试低 ROI 的建议"""
        session = service.create_session(
            date="2026-04-08",
            start_time="19:00",
            end_time="21:00",
            costs=[{"type": "labor", "name": "主播", "amount": 800}],
            revenues=[{"type": "profit", "name": "利润", "amount": 1000}]
        )
        
        suggestions = service.generate_optimization_suggestions(session.session_id)
        
        # ROI 25%，应该有中优先级建议
        overall_suggestions = [s for s in suggestions if s.category == "overall"]
        assert len(overall_suggestions) > 0
    
    def test_optimization_suggestions_duration(self, service):
        """测试时长相关的建议"""
        # 短时长场次
        session1 = service.create_session(
            date="2026-04-08",
            start_time="20:00",
            end_time="20:30",
            costs=[{"type": "labor", "name": "主播", "amount": 200}],
            revenues=[{"type": "profit", "name": "利润", "amount": 300}]
        )
        
        suggestions = service.generate_optimization_suggestions(session1.session_id)
        
        duration_suggestions = [s for s in suggestions if s.category == "duration"]
        assert len(duration_suggestions) > 0
    
    # ============== 测试报告生成 ==============
    
    def test_generate_report(self, service):
        """测试生成报告"""
        # 清除之前的数据
        service.sessions = []
        # 创建多个场次
        for i in range(3):
            date = f"2026-04-{8+i:02d}"
            service.create_session(
                date=date,
                start_time="19:00",
                end_time="21:00",
                costs=[{"type": "labor", "name": "主播", "amount": 500}],
                revenues=[{"type": "profit", "name": "利润", "amount": 800 + i * 100}]
            )
        
        report = service.generate_report()
        
        assert "report_id" in report
        assert "generated_at" in report
        assert "summary" in report
        assert report["summary"]["total_sessions"] == 3
        assert "best_performer" in report
        assert "worst_performer" in report
        assert "optimization_suggestions" in report
    
    def test_generate_report_with_session_ids(self, service):
        """测试生成指定场次的报告"""
        # 创建多个场次
        session_ids = []
        for i in range(3):
            date = f"2026-04-{8+i:02d}"
            session = service.create_session(
                date=date,
                start_time="19:00",
                end_time="21:00",
                costs=[{"type": "labor", "name": "主播", "amount": 500}],
                revenues=[{"type": "profit", "name": "利润", "amount": 800}]
            )
            session_ids.append(session.session_id)
        
        # 只生成前两个场次的报告
        report = service.generate_report(session_ids[:2])
        
        assert report["summary"]["total_sessions"] == 2
    
    # ============== 测试 CRUD 操作 ==============
    
    def test_get_session(self, service, sample_session):
        """测试获取场次"""
        retrieved = service.get_session(sample_session.session_id)
        
        assert retrieved is not None
        assert retrieved.session_id == sample_session.session_id
        assert retrieved.date == sample_session.date
    
    def test_get_session_not_found(self, service):
        """测试获取不存在的场次"""
        retrieved = service.get_session("nonexistent_session")
        assert retrieved is None
    
    def test_list_sessions(self, service):
        """测试列出场次"""
        # 创建多个场次
        for i in range(5):
            date = f"2026-04-{8+i:02d}"
            service.create_session(
                date=date,
                start_time="19:00",
                end_time="21:00",
                costs=[],
                revenues=[]
            )
        
        sessions = service.list_sessions()
        assert len(sessions) >= 5
        
        # 按日期筛选
        sessions = service.list_sessions(start_date="2026-04-10")
        assert len(sessions) >= 3
        
        # 按分类筛选
        service.create_session(
            date="2026-04-15",
            start_time="19:00",
            end_time="21:00",
            category="beauty",
            costs=[],
            revenues=[]
        )
        
        sessions = service.list_sessions(category="beauty")
        assert len(sessions) >= 1
    
    def test_update_session(self, service, sample_session):
        """测试更新场次"""
        updated = service.update_session(
            sample_session.session_id,
            {"notes": "更新后的备注", "category": "beauty"}
        )
        
        assert updated is not None
        assert updated.notes == "更新后的备注"
        assert updated.category == "beauty"
    
    def test_delete_session(self, service):
        """测试删除场次"""
        # 创建新场次
        session = service.create_session(
            date="2026-04-08",
            start_time="19:00",
            end_time="21:00",
            costs=[],
            revenues=[]
        )
        
        success = service.delete_session(session.session_id)
        assert success is True
        
        retrieved = service.get_session(session.session_id)
        assert retrieved is None
    
    def test_delete_session_not_found(self, service):
        """测试删除不存在的场次"""
        success = service.delete_session("nonexistent_session")
        assert success is False
    
    # ============== 测试成本模板 ==============
    
    def test_cost_templates_initialized(self, service):
        """测试成本模板初始化"""
        assert "standard" in service.cost_templates
        assert "premium" in service.cost_templates
        assert "minimal" in service.cost_templates
    
    def test_cost_template_structure(self, service):
        """测试成本模板结构"""
        template = service.cost_templates["standard"]
        
        assert "name" in template
        assert "costs" in template
        assert "labor" in template["costs"]
        assert "venue" in template["costs"]
        assert "promotion" in template["costs"]


class TestROIE2E:
    """ROI 分析端到端测试"""
    
    @pytest.fixture
    def service(self):
        """创建测试服务实例"""
        reset_service()
        import uuid
        test_id = str(uuid.uuid4())[:8]
        return ROIAnalysisService(data_dir=f"data/test_roi_e2e_{test_id}")
    
    def test_full_roi_workflow(self, service):
        """测试完整 ROI 分析流程"""
        # 清除之前的数据
        service.sessions = []
        # 1. 创建多个场次（确保正 ROI）
        sessions = []
        for i in range(5):
            date = f"2026-04-{8+i:02d}"
            session = service.create_session(
                date=date,
                start_time="19:00",
                end_time="22:00",
                category="general" if i % 2 == 0 else "beauty",
                costs=[
                    {"type": "labor", "name": "主播", "amount": 300 + i * 20},
                    {"type": "venue", "name": "场地", "amount": 100},
                    {"type": "promotion", "name": "推广", "amount": 100}
                ],
                revenues=[
                    {"type": "gmv", "name": "销售", "amount": 5000 + i * 500},
                    {"type": "profit", "name": "利润", "amount": 1000 + i * 200}
                ]
            )
            sessions.append(session)
        
        # 2. 计算每个场次的 ROI 指标
        metrics_list = []
        for session in sessions:
            metrics = service.calculate_roi_metrics(session.session_id)
            assert metrics is not None
            metrics_list.append(metrics)
        
        # 3. 获取趋势数据
        trend = service.get_roi_trend(group_by="day")
        assert len(trend) == 5
        
        # 4. 对比分析
        comparison = service.compare_sessions([s.session_id for s in sessions[:3]])
        assert comparison is not None
        # 由于利润>成本，ROI 应该为正
        assert comparison.average_roi > 0
        
        # 5. 生成优化建议
        for session in sessions[:2]:
            suggestions = service.generate_optimization_suggestions(session.session_id)
            assert isinstance(suggestions, list)
        
        # 6. 生成报告
        report = service.generate_report()
        assert report["summary"]["total_sessions"] == 5
        assert report["summary"]["total_cost"] > 0
        assert report["summary"]["total_revenue"] > 0
        
        print("\n=== ROI 分析报告 ===")
        print(f"总场次：{report['summary']['total_sessions']}")
        print(f"总成本：¥{report['summary']['total_cost']:,.2f}")
        print(f"总收益：¥{report['summary']['total_revenue']:,.2f}")
        print(f"总利润：¥{report['summary']['total_profit']:,.2f}")
        print(f"整体 ROI: {report['summary']['overall_roi']:.2f}%")
        print(f"最佳场次：{report['best_performer']['session_id']} ({report['best_performer']['roi']:.2f}%)")
        print(f"最差场次：{report['worst_performer']['session_id']} ({report['worst_performer']['roi']:.2f}%)")
        print(f"\n优化建议数量：{len(report['optimization_suggestions'])}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
