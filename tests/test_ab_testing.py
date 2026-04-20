"""
LiveMirror A/B 测试功能测试
测试话术版本管理、流量分配、效果对比和统计显著性检验
"""

import pytest
import sys
from pathlib import Path

# 添加 backend 路径
sys.path.insert(0, str(Path(__file__).parent.parent / 'backend'))

from services.ab_testing import (
    ABTestingService,
    ScriptVariant,
    TestConfig,
    TestMetrics,
    StatisticalResult
)


@pytest.fixture
def service():
    """创建测试服务实例"""
    return ABTestingService()


class TestScriptVariantManagement:
    """测试话术版本管理"""
    
    def test_create_variant(self, service):
        """测试创建话术变体"""
        variant = service.create_variant(
            test_id="test_001",
            version="A",
            content="欢迎来到直播间！"
        )
        
        assert variant.id == "test_001_A"
        assert variant.version == "A"
        assert variant.content == "欢迎来到直播间！"
        assert variant.is_active == True
    
    def test_get_variant(self, service):
        """测试获取话术变体"""
        service.create_variant("test_001", "A", "内容 A")
        variant = service.get_variant("test_001", "A")
        
        assert variant is not None
        assert variant.version == "A"
    
    def test_get_nonexistent_variant(self, service):
        """测试获取不存在的话术"""
        variant = service.get_variant("test_001", "A")
        assert variant is None
    
    def test_update_variant(self, service):
        """测试更新话术变体"""
        service.create_variant("test_001", "A", "原始内容")
        variant = service.update_variant("test_001", "A", "更新后的内容")
        
        assert variant.content == "更新后的内容"
    
    def test_deactivate_variant(self, service):
        """测试停用话术变体"""
        service.create_variant("test_001", "A", "内容")
        success = service.deactivate_variant("test_001", "A")
        
        assert success == True
        variant = service.get_variant("test_001", "A")
        assert variant.is_active == False
    
    def test_list_variants(self, service):
        """测试列出所有话术变体"""
        service.create_variant("test_001", "A", "内容 A")
        service.create_variant("test_001", "B", "内容 B")
        service.create_variant("test_001", "C", "内容 C")
        
        variants = service.list_variants("test_001")
        assert len(variants) == 3
        
        versions = [v.version for v in variants]
        assert "A" in versions
        assert "B" in versions
        assert "C" in versions


class TestTestConfiguration:
    """测试 A/B 测试配置"""
    
    def test_create_test(self, service):
        """测试创建 A/B 测试"""
        config = service.create_test(
            name="开场话术测试",
            traffic_allocation={"A": 0.5, "B": 0.5}
        )
        
        assert config.name == "开场话术测试"
        assert config.is_active == True
        assert "A" in config.variants
        assert "B" in config.variants
        assert config.variants["A"] == 0.5
        assert config.variants["B"] == 0.5
    
    def test_create_test_invalid_traffic(self, service):
        """测试创建测试时流量分配无效"""
        with pytest.raises(ValueError) as exc_info:
            service.create_test(
                name="测试",
                traffic_allocation={"A": 0.6, "B": 0.6}
            )
        
        assert "流量分配总和必须为 1.0" in str(exc_info.value)
    
    def test_get_test(self, service):
        """测试获取测试配置"""
        service.create_test("测试", {"A": 0.5, "B": 0.5})
        test_id = list(service.test_configs.keys())[0]
        
        config = service.get_test(test_id)
        assert config is not None
        assert config.name == "测试"
    
    def test_update_traffic_allocation(self, service):
        """测试更新流量分配"""
        service.create_test("测试", {"A": 0.5, "B": 0.5})
        test_id = list(service.test_configs.keys())[0]
        
        success = service.update_traffic_allocation(
            test_id,
            {"A": 0.3, "B": 0.7}
        )
        
        assert success == True
        config = service.get_test(test_id)
        assert config.variants["A"] == 0.3
        assert config.variants["B"] == 0.7
    
    def test_stop_test(self, service):
        """测试停止测试"""
        service.create_test("测试", {"A": 0.5, "B": 0.5})
        test_id = list(service.test_configs.keys())[0]
        
        success = service.stop_test(test_id)
        assert success == True
        
        config = service.get_test(test_id)
        assert config.is_active == False
        assert config.end_time is not None


class TestTrafficAllocation:
    """测试流量分配"""
    
    def test_assign_user(self, service):
        """测试为用户分配版本"""
        service.create_test("测试", {"A": 0.5, "B": 0.5})
        test_id = list(service.test_configs.keys())[0]
        
        version = service.assign_user(test_id, "user_001")
        assert version in ["A", "B"]
    
    def test_assign_user_consistent(self, service):
        """测试用户分配一致性"""
        service.create_test("测试", {"A": 0.5, "B": 0.5})
        test_id = list(service.test_configs.keys())[0]
        
        version1 = service.assign_user(test_id, "user_001")
        version2 = service.assign_user(test_id, "user_001")
        
        assert version1 == version2  # 同一用户应该始终获得相同版本
    
    def test_get_assigned_version(self, service):
        """测试获取用户已分配版本"""
        service.create_test("测试", {"A": 0.5, "B": 0.5})
        test_id = list(service.test_configs.keys())[0]
        
        service.assign_user(test_id, "user_001")
        version = service.get_assigned_version("user_001")
        
        assert version is not None
        assert version in ["A", "B"]


class TestMetricsRecording:
    """测试效果数据记录"""
    
    def test_record_impression(self, service):
        """测试记录曝光"""
        service.create_test("测试", {"A": 0.5, "B": 0.5})
        test_id = list(service.test_configs.keys())[0]
        
        service.record_impression(test_id, "A", "user_001")
        service.record_impression(test_id, "A", "user_002")
        
        metrics = service.get_metrics(test_id, "A")
        assert metrics.impressions == 2
    
    def test_record_click(self, service):
        """测试记录点击"""
        service.create_test("测试", {"A": 0.5, "B": 0.5})
        test_id = list(service.test_configs.keys())[0]
        
        service.record_impression(test_id, "A", "user_001")
        service.record_click(test_id, "A", "user_001")
        
        metrics = service.get_metrics(test_id, "A")
        assert metrics.clicks == 1
    
    def test_record_conversion(self, service):
        """测试记录转化"""
        service.create_test("测试", {"A": 0.5, "B": 0.5})
        test_id = list(service.test_configs.keys())[0]
        
        service.record_conversion(test_id, "A", "user_001")
        service.record_conversion(test_id, "A", "user_002")
        
        metrics = service.get_metrics(test_id, "A")
        assert metrics.conversions == 2
    
    def test_record_interaction(self, service):
        """测试记录互动"""
        service.create_test("测试", {"A": 0.5, "B": 0.5})
        test_id = list(service.test_configs.keys())[0]
        
        service.record_interaction(test_id, "A", "user_001")
        
        metrics = service.get_metrics(test_id, "A")
        assert metrics.interactions == 1
    
    def test_record_watch_time(self, service):
        """测试记录观看时长"""
        service.create_test("测试", {"A": 0.5, "B": 0.5})
        test_id = list(service.test_configs.keys())[0]
        
        service.record_watch_time(test_id, "A", "user_001", 120.5)
        service.record_watch_time(test_id, "A", "user_002", 80.3)
        
        metrics = service.get_metrics(test_id, "A")
        assert abs(metrics.watch_time_seconds - 200.8) < 0.01


class TestMetricsAnalysis:
    """测试效果对比分析"""
    
    def test_calculate_rates(self, service):
        """测试计算转化率/互动率"""
        service.create_test("测试", {"A": 0.5, "B": 0.5})
        test_id = list(service.test_configs.keys())[0]
        
        # 模拟数据
        service.metrics[test_id]["A"] = TestMetrics(
            version="A",
            impressions=1000,
            clicks=150,
            conversions=50,
            interactions=200,
            watch_time_seconds=120000
        )
        
        rates = service.calculate_rates(service.metrics[test_id]["A"])
        
        assert abs(rates["click_rate"] - 0.15) < 0.001
        assert abs(rates["conversion_rate"] - 0.05) < 0.001
        assert abs(rates["interaction_rate"] - 0.2) < 0.001
        assert abs(rates["avg_watch_time"] - 120.0) < 0.001
    
    def test_compare_versions(self, service):
        """测试版本对比"""
        service.create_test("测试", {"A": 0.5, "B": 0.5})
        test_id = list(service.test_configs.keys())[0]
        
        # 设置不同版本的数据
        service.metrics[test_id]["A"] = TestMetrics(
            version="A", impressions=1000, conversions=50
        )
        service.metrics[test_id]["B"] = TestMetrics(
            version="B", impressions=1000, conversions=80
        )
        
        comparison = service.compare_versions(test_id)
        
        assert "A" in comparison
        assert "B" in comparison
        assert comparison["A"]["rates"]["conversion_rate"] == 0.05
        assert comparison["B"]["rates"]["conversion_rate"] == 0.08


class TestStatisticalSignificance:
    """测试统计显著性检验"""
    
    def test_z_test_proportions(self, service):
        """测试两比例 Z 检验"""
        # A 版本：1000 次曝光，50 次转化 (5%)
        # B 版本：1000 次曝光，80 次转化 (8%)
        z, p_value = service.z_test_proportions(50, 1000, 80, 1000)
        
        assert z < 0  # B 优于 A，所以 A-B 为负
        assert p_value < 0.05  # 应该显著
    
    def test_z_test_no_significance(self, service):
        """测试无显著差异"""
        # 两个版本差异很小
        z, p_value = service.z_test_proportions(50, 1000, 52, 1000)
        
        assert p_value > 0.05  # 不显著
    
    def test_test_significance(self, service):
        """测试显著性检验"""
        service.create_test("测试", {"A": 0.5, "B": 0.5})
        test_id = list(service.test_configs.keys())[0]
        
        # 设置显著差异的数据
        service.metrics[test_id]["A"] = TestMetrics(
            version="A", impressions=1000, conversions=50
        )
        service.metrics[test_id]["B"] = TestMetrics(
            version="B", impressions=1000, conversions=100
        )
        
        result = service.test_significance(test_id)
        
        assert isinstance(result, StatisticalResult)
        assert result.winner == "B"
        assert result.improvement > 0
    
    def test_chi_square_test(self, service):
        """测试卡方检验"""
        observed = [50, 100]
        expected = [75, 75]
        
        chi_square, p_value = service.chi_square_test(observed, expected)
        
        assert chi_square > 0
        assert 0 <= p_value <= 1


class TestRecommendation:
    """测试优胜话术推荐"""
    
    def test_recommend_winner(self, service):
        """测试推荐优胜版本"""
        service.create_test("测试", {"A": 0.5, "B": 0.5})
        test_id = list(service.test_configs.keys())[0]
        
        # 创建变体
        service.create_variant(test_id, "A", "话术 A")
        service.create_variant(test_id, "B", "话术 B")
        
        # 设置 B 明显优于 A 的数据
        service.metrics[test_id]["A"] = TestMetrics(
            version="A", impressions=1000, conversions=50
        )
        service.metrics[test_id]["B"] = TestMetrics(
            version="B", impressions=1000, conversions=150
        )
        
        recommendation = service.recommend_winner(test_id)
        
        assert recommendation is not None
        assert recommendation["recommendation"] == "winner"
        assert recommendation["winning_version"] == "B"
    
    def test_recommend_inconclusive(self, service):
        """测试结果不确定时的推荐"""
        service.create_test("测试", {"A": 0.5, "B": 0.5})
        test_id = list(service.test_configs.keys())[0]
        
        # 设置差异很小的数据
        service.metrics[test_id]["A"] = TestMetrics(
            version="A", impressions=100, conversions=10
        )
        service.metrics[test_id]["B"] = TestMetrics(
            version="B", impressions=100, conversions=11
        )
        
        recommendation = service.recommend_winner(test_id)
        
        # 由于样本量小，可能不显著
        assert recommendation is not None


class TestReportGeneration:
    """测试测试报告生成"""
    
    def test_generate_report(self, service):
        """测试生成测试报告"""
        service.create_test("开场话术测试", {"A": 0.5, "B": 0.5})
        test_id = list(service.test_configs.keys())[0]
        
        # 创建变体
        service.create_variant(test_id, "A", "欢迎来到直播间！")
        service.create_variant(test_id, "B", "嗨大家好！")
        
        # 记录一些数据
        service.record_impression(test_id, "A", "user_1")
        service.record_conversion(test_id, "A", "user_1")
        service.record_impression(test_id, "B", "user_2")
        service.record_conversion(test_id, "B", "user_2")
        
        report = service.generate_report(test_id)
        
        assert report["test_id"] == test_id
        assert report["test_name"] == "开场话术测试"
        assert "variants" in report
        assert "comparison" in report
        assert "statistical_test" in report
        assert "recommendation" in report
    
    def test_export_report_json(self, service):
        """测试导出 JSON 格式报告"""
        service.create_test("测试", {"A": 0.5, "B": 0.5})
        test_id = list(service.test_configs.keys())[0]
        
        content = service.export_report(test_id, format="json")
        
        assert isinstance(content, str)
        assert test_id in content
    
    def test_export_report_markdown(self, service):
        """测试导出 Markdown 格式报告"""
        service.create_test("测试", {"A": 0.5, "B": 0.5})
        test_id = list(service.test_configs.keys())[0]
        
        content = service.export_report(test_id, format="markdown")
        
        assert isinstance(content, str)
        assert "# A/B 测试报告" in content


class TestIntegration:
    """集成测试"""
    
    def test_full_ab_test_workflow(self, service):
        """测试完整的 A/B 测试流程"""
        # 1. 创建测试
        config = service.create_test(
            name="直播开场话术优化",
            traffic_allocation={"A": 0.4, "B": 0.4, "C": 0.2}
        )
        test_id = config.test_id
        
        # 2. 创建话术变体
        service.create_variant(test_id, "A", "欢迎来到直播间，今天有超值优惠！")
        service.create_variant(test_id, "B", "嗨大家好，我是你们的主播！")
        service.create_variant(test_id, "C", "各位观众朋友们好！")
        
        # 3. 分配用户
        for i in range(100):
            version = service.assign_user(test_id, f"user_{i}")
            assert version in ["A", "B", "C"]
        
        # 4. 记录效果数据
        for i in range(100):
            version = service.get_assigned_version(f"user_{i}")
            service.record_impression(test_id, version, f"user_{i}")
            
            # 模拟不同的转化率
            if version == "A" and i % 5 == 0:
                service.record_conversion(test_id, version, f"user_{i}")
            elif version == "B" and i % 3 == 0:
                service.record_conversion(test_id, version, f"user_{i}")
            elif version == "C" and i % 10 == 0:
                service.record_conversion(test_id, version, f"user_{i}")
        
        # 5. 对比分析
        comparison = service.compare_versions(test_id)
        assert len(comparison) == 3
        
        # 6. 统计检验
        significance = service.test_significance(test_id)
        assert isinstance(significance, StatisticalResult)
        
        # 7. 获取推荐
        recommendation = service.recommend_winner(test_id)
        assert recommendation is not None
        
        # 8. 生成报告
        report = service.generate_report(test_id)
        assert report["test_name"] == "直播开场话术优化"
        
        # 9. 导出报告
        json_report = service.export_report(test_id, "json")
        md_report = service.export_report(test_id, "markdown")
        
        assert "直播开场话术优化" in json_report
        assert "# A/B 测试报告" in md_report
        
        print("\n" + "="*60)
        print("📊 A/B 测试完整流程测试通过！")
        print("="*60)
        print(f"测试 ID: {test_id}")
        print(f"测试名称：{report['test_name']}")
        print(f"状态：{report['status']}")
        print(f"变体数量：{len(report['variants'])}")
        print(f"统计显著：{report['statistical_test']['is_significant']}")
        if report['recommendation']:
            print(f"推荐结果：{report['recommendation']['recommendation']}")
            if report['recommendation'].get('winning_version'):
                print(f"优胜版本：{report['recommendation']['winning_version']}")
        print("="*60)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
