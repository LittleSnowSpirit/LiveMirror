"""
LiveMirror Export Pro Service Tests
专业数据导出服务测试
"""

import pytest
import sys
import os
import json
from datetime import datetime

# 添加 backend 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
from services.export_pro import ExportProService, ExportFormat


@pytest.fixture
def export_service():
    """导出服务测试夹具"""
    return ExportProService()


@pytest.fixture
def sample_data():
    """示例测试数据"""
    return [
        {"id": 1, "name": "商品 A", "price": 99.9, "sales": 150},
        {"id": 2, "name": "商品 B", "price": 199.9, "sales": 80},
        {"id": 3, "name": "商品 C", "price": 299.9, "sales": 45},
        {"id": 4, "name": "商品 D", "price": 49.9, "sales": 300},
        {"id": 5, "name": "商品 E", "price": 149.9, "sales": 120}
    ]


class TestExportTemplates:
    """导出模板管理测试"""
    
    def test_init_default_templates(self, export_service):
        """测试初始化默认模板"""
        templates = export_service.list_templates()
        
        assert len(templates) > 0
        # 应该包含默认模板
        template_names = [t.name for t in templates]
        assert any("Excel" in name for name in template_names)
        assert any("Word" in name for name in template_names)
        assert any("PowerPoint" in name for name in template_names)
        assert any("PDF" in name for name in template_names)
    
    def test_create_template(self, export_service):
        """测试创建模板"""
        template = export_service.create_template(
            name="测试模板",
            format=ExportFormat.EXCEL,
            config={"key": "value"},
            description="测试描述"
        )
        
        assert template.name == "测试模板"
        assert template.format == ExportFormat.EXCEL
        assert template.config == {"key": "value"}
        assert template.description == "测试描述"
        assert template.enabled is True
        assert template.id.startswith("tpl_")
    
    def test_get_template(self, export_service):
        """测试获取模板"""
        created = export_service.create_template(
            name="获取测试",
            format=ExportFormat.WORD,
            config={}
        )
        
        retrieved = export_service.get_template(created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == created.name
    
    def test_get_template_not_found(self, export_service):
        """测试获取不存在的模板"""
        template = export_service.get_template("non_existent_id")
        
        assert template is None
    
    def test_list_templates_by_format(self, export_service):
        """测试按格式筛选模板"""
        # 创建不同格式的模板
        export_service.create_template(name="Excel 模板", format=ExportFormat.EXCEL, config={})
        export_service.create_template(name="PDF 模板", format=ExportFormat.PDF, config={})
        
        excel_templates = export_service.list_templates(format=ExportFormat.EXCEL)
        pdf_templates = export_service.list_templates(format=ExportFormat.PDF)
        
        assert len(excel_templates) >= 1
        assert len(pdf_templates) >= 1
        assert all(t.format == ExportFormat.EXCEL for t in excel_templates)
        assert all(t.format == ExportFormat.PDF for t in pdf_templates)
    
    def test_list_templates_enabled_only(self, export_service):
        """测试只获取启用的模板"""
        template = export_service.create_template(
            name="禁用模板",
            format=ExportFormat.CSV,
            config={}
        )
        template.enabled = False
        
        all_templates = export_service.list_templates()
        enabled_templates = export_service.list_templates(enabled_only=True)
        
        assert len(all_templates) > len(enabled_templates)
        assert all(t.enabled for t in enabled_templates)
    
    def test_update_template(self, export_service):
        """测试更新模板"""
        template = export_service.create_template(
            name="原名",
            format=ExportFormat.JSON,
            config={"old": "config"}
        )
        
        success = export_service.update_template(
            template.id,
            {"name": "新名", "description": "新描述"}
        )
        
        assert success is True
        updated = export_service.get_template(template.id)
        assert updated.name == "新名"
        assert updated.description == "新描述"
        assert updated.config == {"old": "config"}  # 配置未变
    
    def test_update_template_not_found(self, export_service):
        """测试更新不存在的模板"""
        success = export_service.update_template(
            "non_existent_id",
            {"name": "新名"}
        )
        
        assert success is False
    
    def test_delete_template(self, export_service):
        """测试删除模板"""
        template = export_service.create_template(
            name="待删除",
            format=ExportFormat.CUSTOM,
            config={}
        )
        
        success = export_service.delete_template(template.id)
        
        assert success is True
        assert export_service.get_template(template.id) is None
    
    def test_delete_template_not_found(self, export_service):
        """测试删除不存在的模板"""
        success = export_service.delete_template("non_existent_id")
        
        assert success is False


class TestExportJobs:
    """导出任务管理测试"""
    
    def test_create_job(self, export_service):
        """测试创建导出任务"""
        job = export_service.create_job(
            name="每日导出",
            format=ExportFormat.EXCEL,
            data_source="ticket_data",
            schedule="0 0 * * *"
        )
        
        assert job.name == "每日导出"
        assert job.format == ExportFormat.EXCEL
        assert job.data_source == "ticket_data"
        assert job.schedule == "0 0 * * *"
        assert job.enabled is True
        assert job.run_count == 0
        assert job.id.startswith("job_")
    
    def test_get_job(self, export_service):
        """测试获取导出任务"""
        created = export_service.create_job(
            name="获取测试",
            format=ExportFormat.PDF,
            data_source="test_data"
        )
        
        retrieved = export_service.get_job(created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == created.name
    
    def test_list_jobs_by_format(self, export_service):
        """测试按格式筛选任务"""
        export_service.create_job(name="Excel 任务", format=ExportFormat.EXCEL, data_source="data1")
        export_service.create_job(name="Word 任务", format=ExportFormat.WORD, data_source="data2")
        
        excel_jobs = export_service.list_jobs(format=ExportFormat.EXCEL)
        word_jobs = export_service.list_jobs(format=ExportFormat.WORD)
        
        assert len(excel_jobs) >= 1
        assert len(word_jobs) >= 1
        assert all(j.format == ExportFormat.EXCEL for j in excel_jobs)
        assert all(j.format == ExportFormat.WORD for j in word_jobs)
    
    def test_update_job(self, export_service):
        """测试更新导出任务"""
        job = export_service.create_job(
            name="原名",
            format=ExportFormat.CSV,
            data_source="old_source"
        )
        
        success = export_service.update_job(
            job.id,
            {"name": "新名", "schedule": "0 */2 * * *"}
        )
        
        assert success is True
        updated = export_service.get_job(job.id)
        assert updated.name == "新名"
        assert updated.schedule == "0 */2 * * *"
        assert updated.data_source == "old_source"  # 未变
    
    def test_delete_job(self, export_service):
        """测试删除导出任务"""
        job = export_service.create_job(
            name="待删除",
            format=ExportFormat.JSON,
            data_source="test"
        )
        
        success = export_service.delete_job(job.id)
        
        assert success is True
        assert export_service.get_job(job.id) is None
    
    def test_get_scheduled_jobs(self, export_service):
        """测试获取定时任务"""
        # 创建带调度的任务
        job1 = export_service.create_job(
            name="定时任务 1",
            format=ExportFormat.EXCEL,
            data_source="data1",
            schedule="0 0 * * *"
        )
        # 创建不带调度的任务
        job2 = export_service.create_job(
            name="手动任务",
            format=ExportFormat.PDF,
            data_source="data2"
        )
        
        scheduled = export_service.get_scheduled_jobs()
        
        assert len(scheduled) >= 1
        assert all(j.schedule is not None for j in scheduled)
        assert job1.id in [j.id for j in scheduled]
        assert job2.id not in [j.id for j in scheduled]


class TestExportData:
    """数据导出功能测试"""
    
    def test_export_excel(self, export_service, sample_data):
        """测试 Excel 导出"""
        template = export_service.create_template(
            name="Excel 测试模板",
            format=ExportFormat.EXCEL,
            config={"include_charts": True}
        )
        result = export_service.export_data(
            data=sample_data,
            format=ExportFormat.EXCEL,
            template=template
        )
        
        assert result["success"] is True
        assert result["format"] == "Excel"
        assert "output_path" in result
        assert result["output_path"].endswith(".xlsx")
        assert result["success"] is True  # 验证导出成功
    
    def test_export_word(self, export_service, sample_data):
        """测试 Word 导出"""
        template = export_service.create_template(
            name="Word 测试模板",
            format=ExportFormat.WORD,
            config={"include_cover": True, "include_toc": True}
        )
        result = export_service.export_data(
            data=sample_data,
            format=ExportFormat.WORD,
            template=template
        )
        
        assert result["success"] is True
        assert result["format"] == "Word"
        assert "output_path" in result
        assert result["output_path"].endswith(".docx")
    
    def test_export_powerpoint(self, export_service, sample_data):
        """测试 PowerPoint 导出"""
        template = export_service.create_template(
            name="PPT 测试模板",
            format=ExportFormat.POWERPOINT,
            config={"slide_layout": "corporate", "include_charts": True}
        )
        result = export_service.export_data(
            data=sample_data,
            format=ExportFormat.POWERPOINT,
            template=template
        )
        
        assert result["success"] is True
        assert result["format"] == "PowerPoint"
        assert "output_path" in result
        assert result["output_path"].endswith(".pptx")
    
    def test_export_pdf(self, export_service, sample_data):
        """测试 PDF 导出"""
        template = export_service.create_template(
            name="PDF 测试模板",
            format=ExportFormat.PDF,
            config={"page_size": "A4", "font_family": "Arial"}
        )
        result = export_service.export_data(
            data=sample_data,
            format=ExportFormat.PDF,
            template=template
        )
        
        assert result["success"] is True
        assert result["format"] == "PDF"
        assert "output_path" in result
        assert result["output_path"].endswith(".pdf")
    
    def test_export_csv(self, export_service, sample_data):
        """测试 CSV 导出"""
        template = export_service.create_template(
            name="CSV 测试模板",
            format=ExportFormat.CSV,
            config={"delimiter": ",", "encoding": "utf-8-sig"}
        )
        result = export_service.export_data(
            data=sample_data,
            format=ExportFormat.CSV,
            template=template
        )
        
        assert result["success"] is True
        assert result["format"] == "CSV"
        assert "output_path" in result
        assert result["output_path"].endswith(".csv")
    
    def test_export_json(self, export_service, sample_data):
        """测试 JSON 导出"""
        result = export_service.export_data(
            data=sample_data,
            format=ExportFormat.JSON
        )
        
        assert result["success"] is True
        assert result["format"] == "JSON"
        assert "output_path" in result
        assert result["output_path"].endswith(".json")
        
        # 验证 JSON 文件内容
        with open(result["output_path"], "r", encoding="utf-8") as f:
            exported_data = json.load(f)
        
        assert exported_data == sample_data
    
    def test_export_custom(self, export_service, sample_data):
        """测试自定义模板导出"""
        template = export_service.create_template(
            name="自定义测试模板",
            format=ExportFormat.CUSTOM,
            config={"template_type": "custom_report"}
        )
        result = export_service.export_data(
            data=sample_data,
            format=ExportFormat.CUSTOM,
            template=template
        )
        
        assert result["success"] is True
        assert result["format"] == "Custom"
        assert "output_path" in result
    
    def test_export_unsupported_format(self, export_service, sample_data):
        """测试不支持的导出格式"""
        result = export_service.export_data(
            data=sample_data,
            format="unsupported_format"
        )
        
        assert result["success"] is False
        assert "error" in result
        assert "不支持的导出格式" in result["error"]
    
    def test_export_with_template(self, export_service, sample_data):
        """测试使用模板导出"""
        # 创建模板
        template = export_service.create_template(
            name="测试导出模板",
            format=ExportFormat.EXCEL,
            config={"include_charts": True, "sheet_name": "测试表"}
        )
        
        result = export_service.export_data(
            data=sample_data,
            format=ExportFormat.EXCEL,
            template=template
        )
        
        assert result["success"] is True
        assert result["format"] == "Excel"


class TestRunJob:
    """执行导出任务测试"""
    
    def test_run_job_success(self, export_service, sample_data):
        """测试成功执行任务"""
        job = export_service.create_job(
            name="测试任务",
            format=ExportFormat.EXCEL,
            data_source="test_data"
        )
        
        initial_run_count = job.run_count
        initial_last_run = job.last_run
        
        result = export_service.run_job(job.id, sample_data)
        
        assert result["success"] is True
        assert job.run_count == initial_run_count + 1
        assert job.last_run is not None
        if initial_last_run:
            assert job.last_run > initial_last_run
    
    def test_run_job_not_found(self, export_service, sample_data):
        """测试执行不存在的任务"""
        result = export_service.run_job("non_existent_job", sample_data)
        
        assert result["success"] is False
        assert "error" in result
        assert "任务不存在" in result["error"]
    
    def test_run_job_with_template(self, export_service, sample_data):
        """测试使用模板执行任务"""
        template = export_service.create_template(
            name="任务模板",
            format=ExportFormat.PDF,
            config={"page_size": "A4"}
        )
        
        job = export_service.create_job(
            name="带模板任务",
            format=ExportFormat.PDF,
            data_source="test_data",
            template_id=template.id
        )
        
        result = export_service.run_job(job.id, sample_data)
        
        assert result["success"] is True
        assert result["format"] == "PDF"


class TestScheduledJobs:
    """定时任务调度测试"""
    
    def test_check_scheduled_jobs(self, export_service):
        """测试检查定时任务"""
        # 创建定时任务
        export_service.create_job(
            name="定时任务 1",
            format=ExportFormat.EXCEL,
            data_source="data1",
            schedule="0 0 * * *"
        )
        export_service.create_job(
            name="定时任务 2",
            format=ExportFormat.WORD,
            data_source="data2",
            schedule="0 */2 * * *"
        )
        
        results = export_service.check_and_run_scheduled_jobs()
        
        assert len(results) >= 2
        for result in results:
            assert "job_id" in result
            assert "name" in result
            assert "schedule" in result


class TestExportStatistics:
    """导出统计测试"""
    
    def test_export_info_file_created(self, export_service, sample_data):
        """测试导出信息文件创建"""
        result = export_service.export_data(
            data=sample_data,
            format=ExportFormat.EXCEL
        )
        
        assert result["success"] is True
        assert "info_path" in result
        
        # 验证信息文件存在且内容正确
        with open(result["info_path"], "r", encoding="utf-8") as f:
            info = json.load(f)
        
        assert info["format"] == "Excel"
        assert info["filename"] == result["output_path"]
        assert "exported_at" in info


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
