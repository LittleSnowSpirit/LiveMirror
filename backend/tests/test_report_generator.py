"""
报表生成服务测试 - LiveMirror
测试日报/周报/月报生成、导出、模板管理等功能
"""

import pytest
import json
from datetime import datetime, timedelta
from pathlib import Path

from backend.services.report_generator import (
    ReportGeneratorService,
    ReportType,
    ExportFormat,
    get_service,
    generate_daily_report,
    generate_weekly_report,
    generate_monthly_report
)


class TestReportGeneratorService:
    """报表生成服务测试"""
    
    @pytest.fixture
    def service(self):
        """创建测试服务实例"""
        return ReportGeneratorService(
            data_dir="data/test_reports",
            template_dir="backend/templates/report"
        )
    
    def test_init(self, service):
        """测试服务初始化"""
        assert service is not None
        assert service.data_dir.exists()
        assert service.template_dir.exists()
        assert service.templates is not None
    
    def test_generate_daily_report(self, service):
        """测试日报生成"""
        report = service.generate_report(ReportType.DAILY)
        
        assert report is not None
        assert report.report_id.startswith("daily_")
        assert report.report_type == ReportType.DAILY
        assert len(report.sections) > 0
        
        # 验证核心指标章节存在
        section_titles = [s.title for s in report.sections]
        assert "核心指标" in section_titles
        
        # 验证报表已保存
        assert report.report_id in service.reports
    
    def test_generate_weekly_report(self, service):
        """测试周报生成"""
        report = service.generate_report(ReportType.WEEKLY)
        
        assert report is not None
        assert report.report_id.startswith("weekly_")
        assert report.report_type == ReportType.WEEKLY
        
        # 验证周期为 7 天
        days = (report.period_end - report.period_start).days + 1
        assert days == 7
    
    def test_generate_monthly_report(self, service):
        """测试月报生成"""
        report = service.generate_report(ReportType.MONTHLY)
        
        assert report is not None
        assert report.report_id.startswith("monthly_")
        assert report.report_type == ReportType.MONTHLY
    
    def test_generate_report_with_custom_date(self, service):
        """测试指定日期生成报表"""
        start_date = datetime(2026, 4, 1)
        end_date = datetime(2026, 4, 1, 23, 59, 59)
        
        report = service.generate_report(
            ReportType.DAILY,
            start_date=start_date,
            end_date=end_date
        )
        
        assert report.period_start.date() == start_date.date()
        assert report.period_end.date() == end_date.date()
    
    def test_get_report(self, service):
        """测试获取报表详情"""
        # 先生成报表
        report = service.generate_report(ReportType.DAILY)
        
        # 获取报表
        retrieved = service.get_report(report.report_id)
        
        assert retrieved is not None
        assert retrieved["report_id"] == report.report_id
    
    def test_list_reports(self, service):
        """测试列出报表"""
        # 生成多个报表
        service.generate_report(ReportType.DAILY)
        service.generate_report(ReportType.WEEKLY)
        service.generate_report(ReportType.MONTHLY)
        
        reports = service.list_reports()
        
        assert len(reports) >= 3
        
        # 测试类型筛选
        daily_reports = service.list_reports(report_type=ReportType.DAILY)
        assert all(r["report_type"] == "daily" for r in daily_reports)
    
    def test_export_report_json(self, service, tmp_path):
        """测试导出 JSON 格式报表"""
        report = service.generate_report(ReportType.DAILY)
        
        output_path = tmp_path / "report.json"
        result_path = service.export_report(report.report_id, ExportFormat.JSON, str(output_path))
        
        assert Path(result_path).exists()
        
        with open(result_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        assert data["report_id"] == report.report_id
    
    def test_export_report_csv(self, service, tmp_path):
        """测试导出 CSV 格式报表"""
        report = service.generate_report(ReportType.DAILY)
        
        output_path = tmp_path / "report.csv"
        result_path = service.export_report(report.report_id, ExportFormat.CSV, str(output_path))
        
        assert Path(result_path).exists()
    
    def test_export_report_excel(self, service, tmp_path):
        """测试导出 Excel 格式报表"""
        report = service.generate_report(ReportType.DAILY)
        
        output_path = tmp_path / "report.xlsx"
        result_path = service.export_report(report.report_id, ExportFormat.EXCEL, str(output_path))
        
        # Excel 导出实际生成 CSV
        assert Path(result_path).exists()
        assert result_path.endswith('.csv')
    
    def test_export_report_pdf(self, service, tmp_path):
        """测试导出 PDF 格式报表"""
        report = service.generate_report(ReportType.DAILY)
        
        output_path = tmp_path / "report.pdf"
        result_path = service.export_report(report.report_id, ExportFormat.PDF, str(output_path))
        
        # PDF 导出实际生成 TXT（简化版）
        assert Path(result_path).exists()
        assert result_path.endswith('.txt')
    
    def test_create_template(self, service):
        """测试创建自定义模板"""
        template_id = service.create_template(
            name="测试模板",
            report_type=ReportType.DAILY,
            sections=[
                {"title": "测试章节", "metrics": ["metric1", "metric2"]}
            ]
        )
        
        assert template_id.startswith("custom_")
        assert template_id in service.templates
        assert service.templates[template_id]["name"] == "测试模板"
    
    def test_update_template(self, service):
        """测试更新模板"""
        template_id = service.create_template(
            name="原名称",
            report_type=ReportType.DAILY,
            sections=[]
        )
        
        success = service.update_template(template_id, {"name": "新名称"})
        
        assert success
        assert service.templates[template_id]["name"] == "新名称"
    
    def test_delete_template(self, service):
        """测试删除模板"""
        template_id = service.create_template(
            name="待删除模板",
            report_type=ReportType.DAILY,
            sections=[]
        )
        
        success = service.delete_template(template_id)
        
        assert success
        assert template_id not in service.templates
    
    def test_delete_default_template(self, service):
        """测试不能删除默认模板"""
        # 默认模板应该存在
        default_templates = [
            tid for tid, t in service.templates.items() 
            if t.get("is_default")
        ]
        
        if default_templates:
            template_id = default_templates[0]
            success = service.delete_template(template_id)
            assert not success  # 应该删除失败
    
    def test_list_templates(self, service):
        """测试列出模板"""
        templates = service.list_templates()
        
        assert len(templates) > 0
        
        # 测试类型筛选
        daily_templates = service.list_templates(report_type=ReportType.DAILY)
        assert all(t["type"] == "daily" for t in daily_templates)
    
    def test_create_schedule(self, service):
        """测试创建定时任务"""
        schedule_id = service.create_schedule(
            report_type=ReportType.DAILY,
            cron_expression="0 9 * * *",
            export_format=ExportFormat.PDF,
            send_email=True,
            email_recipients=["test@example.com"],
            send_wechat=False
        )
        
        assert schedule_id.startswith("schedule_")
        
        schedules = service.list_schedules()
        assert any(s["schedule_id"] == schedule_id for s in schedules)
    
    def test_update_schedule(self, service):
        """测试更新定时任务"""
        schedule_id = service.create_schedule(
            report_type=ReportType.DAILY,
            cron_expression="0 9 * * *"
        )
        
        success = service.update_schedule(schedule_id, {"enabled": False})
        
        assert success
        schedule = next(
            s for s in service.schedules 
            if s["schedule_id"] == schedule_id
        )
        assert schedule["enabled"] is False
    
    def test_delete_schedule(self):
        """测试删除定时任务"""
        # 使用独立的测试服务实例
        service = ReportGeneratorService(data_dir="data/test_reports_delete")
        
        schedule_id = service.create_schedule(
            report_type=ReportType.DAILY,
            cron_expression="0 9 * * *"
        )
        
        success = service.delete_schedule(schedule_id)
        
        assert success
        schedules = service.list_schedules()
        assert not any(s["schedule_id"] == schedule_id for s in schedules)
    
    def test_toggle_schedule(self, service):
        """测试启/停定时任务"""
        schedule_id = service.create_schedule(
            report_type=ReportType.DAILY,
            cron_expression="0 9 * * *"
        )
        
        schedule = next(
            s for s in service.schedules 
            if s["schedule_id"] == schedule_id
        )
        initial_state = schedule["enabled"]
        
        success = service.update_schedule(schedule_id, {"enabled": not initial_state})
        
        assert success
        schedule = next(
            s for s in service.schedules 
            if s["schedule_id"] == schedule_id
        )
        assert schedule["enabled"] == (not initial_state)
    
    def test_get_statistics(self, service):
        """测试获取统计信息"""
        # 生成一些报表
        service.generate_report(ReportType.DAILY)
        service.generate_report(ReportType.WEEKLY)
        
        stats = service.get_statistics()
        
        assert stats["total_reports"] >= 2
        assert "reports_by_type" in stats
        assert stats["total_templates"] > 0


class TestConvenienceFunctions:
    """便捷函数测试"""
    
    def test_generate_daily_report(self):
        """测试日报生成便捷函数"""
        report = generate_daily_report()
        assert report is not None
        assert report.report_type == ReportType.DAILY
    
    def test_generate_weekly_report(self):
        """测试周报生成便捷函数"""
        report = generate_weekly_report()
        assert report is not None
        assert report.report_type == ReportType.WEEKLY
    
    def test_generate_monthly_report(self):
        """测试月报生成便捷函数"""
        report = generate_monthly_report()
        assert report is not None
        assert report.report_type == ReportType.MONTHLY


class TestReportDataStructure:
    """报表数据结构测试"""
    
    @pytest.fixture
    def report(self):
        """创建测试报表"""
        service = ReportGeneratorService(data_dir="data/test_reports")
        return service.generate_report(ReportType.DAILY)
    
    def test_report_id_format(self, report):
        """测试报表 ID 格式"""
        assert "_" in report.report_id
        parts = report.report_id.split("_")
        assert len(parts) >= 3
    
    def test_report_period(self, report):
        """测试报表周期"""
        assert report.period_start <= report.period_end
        assert report.period_start <= datetime.now()
    
    def test_report_sections(self, report):
        """测试报表章节"""
        assert len(report.sections) > 0
        
        for section in report.sections:
            assert section.title
            assert isinstance(section.metrics, list)
            assert len(section.metrics) > 0
            
            for metric in section.metrics:
                assert metric.name
                assert metric.value is not None
    
    def test_report_summary(self, report):
        """测试报表摘要"""
        assert report.overall_summary
        assert "GMV" in report.overall_summary


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
