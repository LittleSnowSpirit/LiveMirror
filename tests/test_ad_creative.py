"""
广告素材分析功能测试
Test suite for Ad Creative Analysis

测试内容：
1. 素材上传
2. 效果分析
3. A/B 测试
4. 素材推荐
"""

import pytest
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.ad_creative import (
    AdCreativeService,
    AdCreative,
    CreativeStatus,
    ABTestStatus,
    CreativeMetrics
)


@pytest.fixture
def service():
    """创建服务实例"""
    return AdCreativeService()


@pytest.fixture
def sample_creatives(service):
    """创建测试素材"""
    creatives = []
    
    # 素材 1 - 高表现
    c1 = service.upload_creative(
        name="高表现图片广告",
        creative_type="image",
        file_content=b"fake_image_content_1",
        file_path="uploads/test1.jpg",
        dimensions={"width": 1080, "height": 1080},
        file_size=102400,
        tags=["促销", "图片", "高转化"]
    )
    service.update_metrics(
        c1.id,
        impressions=50000,
        clicks=2500,
        conversions=150,
        spend=1000.0,
        revenue=5000.0
    )
    creatives.append(c1)
    
    # 素材 2 - 中等表现
    c2 = service.upload_creative(
        name="中等表现视频广告",
        creative_type="video",
        file_content=b"fake_video_content_2",
        file_path="uploads/test2.mp4",
        dimensions={"width": 1920, "height": 1080},
        file_size=5120000,
        tags=["品牌", "视频"]
    )
    service.update_metrics(
        c2.id,
        impressions=30000,
        clicks=900,
        conversions=30,
        spend=800.0,
        revenue=2000.0
    )
    creatives.append(c2)
    
    # 素材 3 - 低表现
    c3 = service.upload_creative(
        name="低表现轮播广告",
        creative_type="carousel",
        file_content=b"fake_carousel_content_3",
        file_path="uploads/test3.jpg",
        dimensions={"width": 1080, "height": 1080},
        file_size=204800,
        tags=["产品", "轮播"]
    )
    service.update_metrics(
        c3.id,
        impressions=20000,
        clicks=200,
        conversions=5,
        spend=500.0,
        revenue=300.0
    )
    creatives.append(c3)
    
    return creatives


class TestCreativeUpload:
    """测试素材上传功能"""
    
    def test_upload_creative(self, service):
        """测试基本上传"""
        creative = service.upload_creative(
            name="测试素材",
            creative_type="image",
            file_content=b"test_content",
            file_path="uploads/test.jpg",
            dimensions={"width": 1080, "height": 1080},
            file_size=102400,
            tags=["测试", "图片"],
            metadata={"campaign": "test_campaign"}
        )
        
        assert creative is not None
        assert creative.name == "测试素材"
        assert creative.creative_type == "image"
        assert creative.status == CreativeStatus.ACTIVE
        assert "测试" in creative.tags
        assert creative.file_hash is not None
        assert len(creative.file_hash) == 64  # SHA256
    
    def test_upload_creative_with_tags(self, service):
        """测试带标签上传"""
        tags = ["促销", "新品", "限时优惠"]
        creative = service.upload_creative(
            name="带标签素材",
            creative_type="image",
            file_content=b"test",
            file_path="uploads/test.jpg",
            dimensions={"width": 1080, "height": 1080},
            file_size=1024,
            tags=tags
        )
        
        assert creative.tags == tags
    
    def test_get_creative(self, service):
        """测试获取单个素材"""
        creative = service.upload_creative(
            name="获取测试",
            creative_type="image",
            file_content=b"test",
            file_path="uploads/test.jpg",
            dimensions={"width": 1080, "height": 1080},
            file_size=1024
        )
        
        retrieved = service.get_creative(creative.id)
        assert retrieved is not None
        assert retrieved.id == creative.id
        assert retrieved.name == "获取测试"
    
    def test_get_nonexistent_creative(self, service):
        """测试获取不存在的素材"""
        retrieved = service.get_creative("nonexistent_id")
        assert retrieved is None
    
    def test_list_creatives(self, service, sample_creatives):
        """测试获取素材列表"""
        creatives = service.list_creatives()
        assert len(creatives) == 3
    
    def test_list_creatives_by_status(self, service, sample_creatives):
        """测试按状态筛选"""
        # 暂停一个素材
        service.update_creative_status(sample_creatives[0].id, CreativeStatus.PAUSED)
        
        active = service.list_creatives(status=CreativeStatus.ACTIVE)
        assert len(active) == 2
        
        paused = service.list_creatives(status=CreativeStatus.PAUSED)
        assert len(paused) == 1
    
    def test_list_creatives_by_type(self, service, sample_creatives):
        """测试按类型筛选"""
        images = service.list_creatives(creative_type="image")
        assert len(images) == 1
        
        videos = service.list_creatives(creative_type="video")
        assert len(videos) == 1
    
    def test_list_creatives_by_tags(self, service, sample_creatives):
        """测试按标签筛选"""
        tagged = service.list_creatives(tags=["促销"])
        assert len(tagged) == 1
        assert tagged[0].name == "高表现图片广告"
    
    def test_update_creative_status(self, service):
        """测试更新素材状态"""
        creative = service.upload_creative(
            name="状态测试",
            creative_type="image",
            file_content=b"test",
            file_path="uploads/test.jpg",
            dimensions={"width": 1080, "height": 1080},
            file_size=1024
        )
        
        assert creative.status == CreativeStatus.ACTIVE
        
        success = service.update_creative_status(creative.id, CreativeStatus.PAUSED)
        assert success is True
        
        updated = service.get_creative(creative.id)
        assert updated.status == CreativeStatus.PAUSED
    
    def test_delete_creative(self, service):
        """测试删除素材"""
        creative = service.upload_creative(
            name="删除测试",
            creative_type="image",
            file_content=b"test",
            file_path="uploads/test.jpg",
            dimensions={"width": 1080, "height": 1080},
            file_size=1024
        )
        
        success = service.delete_creative(creative.id)
        assert success is True
        
        deleted = service.get_creative(creative.id)
        assert deleted is None


class TestMetricsAnalysis:
    """测试效果分析功能"""
    
    def test_update_metrics(self, service):
        """测试更新效果数据"""
        creative = service.upload_creative(
            name="指标测试",
            creative_type="image",
            file_content=b"test",
            file_path="uploads/test.jpg",
            dimensions={"width": 1080, "height": 1080},
            file_size=1024
        )
        
        success = service.update_metrics(
            creative.id,
            impressions=10000,
            clicks=500,
            conversions=25,
            spend=200.0,
            revenue=800.0
        )
        
        assert success is True
        
        updated = service.get_creative(creative.id)
        assert updated.metrics.impressions == 10000
        assert updated.metrics.clicks == 500
        assert updated.metrics.conversions == 25
    
    def test_metrics_calculations(self, service):
        """测试指标计算"""
        creative = service.upload_creative(
            name="计算测试",
            creative_type="image",
            file_content=b"test",
            file_path="uploads/test.jpg",
            dimensions={"width": 1080, "height": 1080},
            file_size=1024
        )
        
        service.update_metrics(
            creative.id,
            impressions=10000,
            clicks=500,
            conversions=25,
            spend=200.0,
            revenue=800.0
        )
        
        metrics = creative.metrics
        assert metrics.ctr == 0.05  # 500/10000
        assert metrics.cvr == 0.05  # 25/500
        assert metrics.cpc == 0.4   # 200/500
        assert metrics.cpa == 8.0   # 200/25
        assert metrics.roas == 4.0  # 800/200
    
    def test_analyze_creative(self, service, sample_creatives):
        """测试素材分析"""
        analysis = service.analyze_creative(sample_creatives[0].id)
        
        assert analysis is not None
        assert 'creative' in analysis
        assert 'analysis' in analysis
        assert 'score' in analysis['analysis']
        assert 'performance_level' in analysis['analysis']
        assert 'strengths' in analysis['analysis']
        assert 'weaknesses' in analysis['analysis']
        assert 'suggestions' in analysis['analysis']
    
    def test_analyze_nonexistent(self, service):
        """测试分析不存在的素材"""
        analysis = service.analyze_creative("nonexistent")
        assert analysis is None
    
    def test_performance_level(self, service):
        """测试表现等级判定"""
        # 创建高表现素材
        high = service.upload_creative(
            name="高表现",
            creative_type="image",
            file_content=b"test",
            file_path="uploads/test.jpg",
            dimensions={"width": 1080, "height": 1080},
            file_size=1024
        )
        service.update_metrics(high.id, 50000, 2500, 150, 1000, 5000)
        
        analysis = service.analyze_creative(high.id)
        assert analysis['analysis']['performance_level'] in ['excellent', 'good']
    
    def test_generate_suggestions(self, service):
        """测试优化建议生成"""
        # 创建低表现素材
        low = service.upload_creative(
            name="低表现",
            creative_type="image",
            file_content=b"test",
            file_path="uploads/test.jpg",
            dimensions={"width": 1080, "height": 1080},
            file_size=1024
        )
        service.update_metrics(low.id, 1000, 5, 0, 100, 0)
        
        analysis = service.analyze_creative(low.id)
        assert len(analysis['analysis']['suggestions']) > 0


class TestCreativeScoring:
    """测试素材评分系统"""
    
    def test_calculate_score(self, service):
        """测试评分计算"""
        creative = service.upload_creative(
            name="评分测试",
            creative_type="image",
            file_content=b"test",
            file_path="uploads/test.jpg",
            dimensions={"width": 1080, "height": 1080},
            file_size=1024
        )
        
        service.update_metrics(
            creative.id,
            impressions=10000,
            clicks=500,
            conversions=50,
            spend=200.0,
            revenue=1000.0
        )
        
        score = creative.calculate_score()
        assert 0 <= score <= 100
    
    def test_score_ranking(self, service, sample_creatives):
        """测试评分排序"""
        creatives = service.list_creatives()
        
        # 验证按评分降序排列
        for i in range(len(creatives) - 1):
            assert creatives[i].calculate_score() >= creatives[i + 1].calculate_score()
    
    def test_top_creatives(self, service, sample_creatives):
        """测试优秀素材推荐"""
        top = service.get_top_creatives(limit=2, min_impressions=100)
        
        assert len(top) <= 2
        assert all(c.metrics.impressions >= 100 for c in top)


class TestABTesting:
    """测试 A/B 测试功能"""
    
    def test_create_ab_test(self, service, sample_creatives):
        """测试创建 A/B 测试"""
        creative_ids = [sample_creatives[0].id, sample_creatives[1].id]
        
        ab_test = service.create_ab_test(
            name="测试对比",
            creative_ids=creative_ids
        )
        
        assert ab_test is not None
        assert ab_test.name == "测试对比"
        assert len(ab_test.creative_ids) == 2
        assert ab_test.status == ABTestStatus.RUNNING
        
        # 验证素材关联
        for cid in creative_ids:
            creative = service.get_creative(cid)
            assert creative.ab_test_id == ab_test.id
    
    def test_create_ab_test_insufficient(self, service, sample_creatives):
        """测试创建 A/B 测试 - 素材不足"""
        with pytest.raises(ValueError, match="至少需要 2 个素材"):
            service.create_ab_test(
                name="无效测试",
                creative_ids=[sample_creatives[0].id]
            )
    
    def test_create_ab_test_nonexistent(self, service):
        """测试创建 A/B 测试 - 素材不存在"""
        with pytest.raises(ValueError, match="不存在"):
            service.create_ab_test(
                name="无效测试",
                creative_ids=["nonexistent1", "nonexistent2"]
            )
    
    def test_get_ab_test(self, service, sample_creatives):
        """测试获取 A/B 测试"""
        ab_test = service.create_ab_test(
            name="获取测试",
            creative_ids=[sample_creatives[0].id, sample_creatives[1].id]
        )
        
        retrieved = service.get_ab_test(ab_test.id)
        assert retrieved is not None
        assert retrieved.id == ab_test.id
    
    def test_list_ab_tests(self, service, sample_creatives):
        """测试获取 A/B 测试列表"""
        service.create_ab_test(
            name="测试 1",
            creative_ids=[sample_creatives[0].id, sample_creatives[1].id]
        )
        service.create_ab_test(
            name="测试 2",
            creative_ids=[sample_creatives[1].id, sample_creatives[2].id]
        )
        
        tests = service.list_ab_tests()
        assert len(tests) == 2
    
    def test_complete_ab_test(self, service, sample_creatives):
        """测试完成 A/B 测试"""
        ab_test = service.create_ab_test(
            name="完成测试",
            creative_ids=[sample_creatives[0].id, sample_creatives[1].id]
        )
        
        result = service.complete_ab_test(ab_test.id)
        
        assert result is not None
        assert result['status'] == 'completed'
        assert result['winner_id'] is not None
        
        # 高表现素材应该获胜
        assert result['winner_id'] == sample_creatives[0].id
    
    def test_ab_test_analysis(self, service, sample_creatives):
        """测试 A/B 测试分析报告"""
        ab_test = service.create_ab_test(
            name="分析测试",
            creative_ids=[sample_creatives[0].id, sample_creatives[1].id]
        )
        
        analysis = service.get_ab_test_analysis(ab_test.id)
        
        assert analysis is not None
        assert 'test' in analysis
        assert 'creatives' in analysis
        assert 'winner' in analysis
        assert 'recommendation' in analysis


class TestExport:
    """测试数据导出功能"""
    
    def test_export_analytics(self, service, sample_creatives):
        """测试导出分析数据"""
        export_data = service.export_analytics(format='json')
        
        assert export_data is not None
        assert isinstance(export_data, str)
        
        import json
        data = json.loads(export_data)
        
        assert 'creatives' in data
        assert 'ab_tests' in data
        assert 'exported_at' in data
        assert len(data['creatives']) == 3


class TestDashboard:
    """测试仪表板功能"""
    
    def test_dashboard_metrics(self, service, sample_creatives):
        """测试仪表板指标汇总"""
        all_creatives = list(service.creatives.values())
        
        total_impressions = sum(c.metrics.impressions for c in all_creatives)
        total_clicks = sum(c.metrics.clicks for c in all_creatives)
        
        assert total_impressions == 100000  # 50000 + 30000 + 20000
        assert total_clicks == 3600  # 2500 + 900 + 200


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
