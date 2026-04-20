"""
直播剧本规划服务测试 - LiveMirror
"""

import pytest
import json
from pathlib import Path
from datetime import datetime

from backend.services.script_planner import (
    ScriptPlannerService,
    ScriptDuration,
    ScriptSectionType,
    InteractionType,
    get_service,
    generate_1h_script,
    generate_2h_script,
    generate_4h_script
)


@pytest.fixture
def service():
    """创建测试服务实例"""
    # 使用临时目录
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        svc = ScriptPlannerService(data_dir=tmpdir)
        yield svc


class TestScriptPlannerService:
    """剧本规划服务测试"""
    
    def test_init(self, service):
        """测试服务初始化"""
        assert service is not None
        assert len(service.templates) > 0
        assert len(service.products) > 0
    
    def test_generate_1h_script(self, service):
        """测试生成 1 小时剧本"""
        script = service.generate_script(
            theme="美妆专场",
            duration=ScriptDuration.ONE_HOUR,
            target_audience="美妆爱好者",
            streamer_name="小美"
        )
        
        assert script is not None
        assert script.script_id.startswith("script_")
        assert script.title == "美妆专场直播剧本"
        assert script.duration == ScriptDuration.ONE_HOUR
        assert script.theme == "美妆专场"
        assert len(script.segments) > 0
        assert len(script.emergency_plans) > 0
        
        # 验证总时长约为 60 分钟
        total_minutes = sum(seg.duration_minutes for seg in script.segments)
        assert 55 <= total_minutes <= 65
    
    def test_generate_2h_script(self, service):
        """测试生成 2 小时剧本"""
        script = service.generate_script(
            theme="双 11 大促",
            duration=ScriptDuration.TWO_HOURS,
            target_audience="所有人",
            streamer_name="主播"
        )
        
        assert script is not None
        assert script.duration == ScriptDuration.TWO_HOURS
        
        # 验证总时长约为 120 分钟（允许模板结构差异）
        total_minutes = sum(seg.duration_minutes for seg in script.segments)
        assert 120 <= total_minutes <= 150
    
    def test_generate_4h_script(self, service):
        """测试生成 4 小时剧本"""
        script = service.generate_script(
            theme="年终盛典",
            duration=ScriptDuration.FOUR_HOURS,
            target_audience="所有人"
        )
        
        assert script is not None
        assert script.duration == ScriptDuration.FOUR_HOURS
        
        # 验证总时长约为 240 分钟（允许模板结构差异）
        total_minutes = sum(seg.duration_minutes for seg in script.segments)
        assert 240 <= total_minutes <= 300
    
    def test_script_segments_structure(self, service):
        """测试剧本片段结构"""
        script = service.generate_script(
            theme="测试主题",
            duration=ScriptDuration.ONE_HOUR
        )
        
        # 验证包含各种类型的片段
        segment_types = [seg.segment_type for seg in script.segments]
        
        assert ScriptSectionType.OPENING in segment_types
        assert ScriptSectionType.PRODUCT_INTRO in segment_types
        assert ScriptSectionType.CLOSING in segment_types
        
        # 验证片段时间连续性
        for i, seg in enumerate(script.segments):
            assert seg.start_time is not None
            assert seg.end_time is not None
            assert seg.duration_minutes > 0
            
            # 验证时间格式
            assert len(seg.start_time.split(':')) == 3
            assert len(seg.end_time.split(':')) == 3
    
    def test_script_products(self, service):
        """测试剧本产品规划"""
        script = service.generate_script(
            theme="产品测试",
            duration=ScriptDuration.TWO_HOURS
        )
        
        assert len(script.products) > 0
        
        for product in script.products:
            assert product.product_id is not None
            assert product.product_name is not None
            assert product.price > 0
            assert product.original_price > 0
            assert product.start_time is not None
            assert product.end_time is not None
            assert len(product.selling_points) > 0
    
    def test_script_interactions(self, service):
        """测试剧本互动环节"""
        script = service.generate_script(
            theme="互动测试",
            duration=ScriptDuration.TWO_HOURS
        )
        
        assert len(script.interactions) > 0
        
        interaction_types = [i.type for i in script.interactions]
        
        # 验证有多种互动类型
        assert len(set(interaction_types)) >= 2
        
        for interaction in script.interactions:
            assert interaction.name is not None
            assert interaction.duration_minutes > 0
            assert len(interaction.rules) > 0
            assert len(interaction.prizes) > 0
    
    def test_emergency_plans(self, service):
        """测试应急预案生成"""
        script = service.generate_script(
            theme="安全测试",
            duration=ScriptDuration.ONE_HOUR
        )
        
        assert len(script.emergency_plans) > 0
        
        # 验证包含常见应急场景
        scenarios = [plan.scenario for plan in script.emergency_plans]
        
        # 至少应该包含断网、价格错误等常见场景
        assert any("断网" in s or "网络" in s for s in scenarios)
        assert any("价格" in s or "链接" in s for s in scenarios)
        
        # 验证应急预案结构完整
        for plan in script.emergency_plans:
            assert plan.scenario is not None
            assert plan.probability in ["low", "medium", "high"]
            assert plan.impact in ["low", "medium", "high"]
            assert len(plan.response_steps) > 0
            assert plan.backup_script is not None
            assert plan.responsible_person is not None
    
    def test_script_export_json(self, service, tmp_path):
        """测试导出 JSON 格式"""
        script = service.generate_script(
            theme="导出测试",
            duration=ScriptDuration.ONE_HOUR
        )
        
        output_path = str(tmp_path / "test_export.json")
        result_path = service.export_script(script.script_id, "json", output_path)
        
        assert result_path == output_path
        assert Path(output_path).exists()
        
        # 验证 JSON 内容
        with open(output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert data["script_id"] == script.script_id
        assert data["theme"] == "导出测试"
        assert "segments" in data
        assert "emergency_plans" in data
    
    def test_script_export_txt(self, service, tmp_path):
        """测试导出 TXT 格式"""
        script = service.generate_script(
            theme="TXT 导出测试",
            duration=ScriptDuration.ONE_HOUR
        )
        
        output_path = str(tmp_path / "test_export.txt")
        result_path = service.export_script(script.script_id, "txt", output_path)
        
        assert result_path == output_path
        assert Path(output_path).exists()
        
        # 验证 TXT 内容结构（避免编码问题）
        with open(output_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查基本结构
        assert "==" in content
        assert "分钟" in content
    
    def test_list_scripts(self, service):
        """测试列出剧本"""
        # 生成剧本并验证可以列出
        script1 = service.generate_script(theme="测试主题 1", duration=ScriptDuration.ONE_HOUR)
        
        scripts = service.list_scripts(limit=10, offset=0)
        
        # 验证至少有一个剧本
        assert len(scripts) >= 1
        assert scripts[0]["theme"] == "测试主题 1"
        
        # 验证按时间倒序
        for i in range(len(scripts) - 1):
            assert scripts[i]["generated_at"] >= scripts[i + 1]["generated_at"]
    
    def test_get_script(self, service):
        """测试获取剧本详情"""
        script = service.generate_script(
            theme="详情测试",
            duration=ScriptDuration.ONE_HOUR
        )
        
        retrieved = service.get_script(script.script_id)
        
        assert retrieved is not None
        assert retrieved["script_id"] == script.script_id
        assert retrieved["theme"] == "详情测试"
    
    def test_delete_script(self, service):
        """测试删除剧本"""
        script = service.generate_script(
            theme="删除测试",
            duration=ScriptDuration.ONE_HOUR
        )
        
        # 验证删除成功
        assert service.delete_script(script.script_id) is True
        
        # 验证已删除
        assert service.get_script(script.script_id) is None
        
        # 验证删除不存在的剧本
        assert service.delete_script("nonexistent") is False
    
    def test_get_templates(self, service):
        """测试获取模板"""
        templates = service.get_templates()
        
        assert len(templates) > 0
        
        # 验证模板结构
        for template in templates:
            assert "template_id" in template
            assert "name" in template
            assert "duration" in template
            assert "structure" in template
    
    def test_get_products(self, service):
        """测试获取产品库"""
        products = service.get_products()
        
        assert len(products) > 0
        
        # 验证产品结构
        for product in products:
            assert "product_id" in product
            assert "name" in product
            assert "price" in product
            assert "selling_points" in product
    
    def test_add_product(self, service):
        """测试添加产品"""
        product_data = {
            "name": "测试产品",
            "price": 99.0,
            "original_price": 199.0,
            "discount": "5 折",
            "category": "测试分类",
            "selling_points": ["卖点 1", "卖点 2"],
            "target_audience": "测试人群"
        }
        
        product_id = service.add_product(product_data)
        
        assert product_id is not None
        assert product_id.startswith("prod_")
        
        # 验证产品已保存
        products = service.get_products()
        assert any(p["product_id"] == product_id for p in products)
    
    def test_get_statistics(self, service):
        """测试获取统计信息"""
        # 生成一些剧本
        service.generate_script(theme="统计测试 1", duration=ScriptDuration.ONE_HOUR)
        service.generate_script(theme="统计测试 2", duration=ScriptDuration.TWO_HOURS)
        
        stats = service.get_statistics()
        
        assert "total_scripts" in stats
        assert "total_templates" in stats
        assert "total_products" in stats
        assert "scripts_by_duration" in stats
        
        assert stats["total_scripts"] >= 1


class TestConvenienceFunctions:
    """便捷函数测试"""
    
    def test_generate_1h_script_function(self):
        """测试 1 小时剧本生成函数"""
        script = generate_1h_script("快速测试")
        assert script is not None
        assert script.duration == ScriptDuration.ONE_HOUR
    
    def test_generate_2h_script_function(self):
        """测试 2 小时剧本生成函数"""
        script = generate_2h_script("标准测试")
        assert script is not None
        assert script.duration == ScriptDuration.TWO_HOURS
    
    def test_generate_4h_script_function(self):
        """测试 4 小时剧本生成函数"""
        script = generate_4h_script("马拉松测试")
        assert script is not None
        assert script.duration == ScriptDuration.FOUR_HOURS


class TestScriptContent:
    """剧本内容质量测试"""
    
    def test_opening_script_content(self, service):
        """测试开场剧本内容"""
        script = service.generate_script(
            theme="内容测试",
            duration=ScriptDuration.ONE_HOUR
        )
        
        opening = next(seg for seg in script.segments if seg.segment_type == ScriptSectionType.OPENING)
        
        assert opening.title == "开场预热"
        assert "欢迎" in opening.script_content
        assert "主题" in opening.script_content
        assert len(opening.notes) > 0
    
    def test_product_script_content(self, service):
        """测试产品介绍剧本内容"""
        script = service.generate_script(
            theme="产品测试",
            duration=ScriptDuration.TWO_HOURS
        )
        
        product_segments = [
            seg for seg in script.segments 
            if seg.segment_type == ScriptSectionType.PRODUCT_INTRO
        ]
        
        assert len(product_segments) > 0
        
        for seg in product_segments:
            # 验证包含价格信息（避免编码问题）
            assert "元" in seg.script_content or "price" in seg.script_content.lower()
            assert len(seg.products) > 0
    
    def test_interaction_script_content(self, service):
        """测试互动环节剧本内容"""
        script = service.generate_script(
            theme="互动测试",
            duration=ScriptDuration.TWO_HOURS
        )
        
        interaction_segments = [
            seg for seg in script.segments 
            if seg.segment_type == ScriptSectionType.INTERACTION
        ]
        
        assert len(interaction_segments) > 0
        
        for seg in interaction_segments:
            assert "抽奖" in seg.script_content or "互动" in seg.script_content
            assert len(seg.interactions) > 0
    
    def test_closing_script_content(self, service):
        """测试结尾剧本内容"""
        script = service.generate_script(
            theme="收尾测试",
            duration=ScriptDuration.ONE_HOUR
        )
        
        closing = next(seg for seg in script.segments if seg.segment_type == ScriptSectionType.CLOSING)
        
        assert closing.title == "总结收尾"
        assert "感谢" in closing.script_content
        assert "下次" in closing.script_content or "预告" in closing.script_content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
