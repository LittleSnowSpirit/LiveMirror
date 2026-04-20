#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LiveMirror 广告素材分析系统 - 功能演示脚本

演示所有核心功能：
1. 素材上传
2. 效果分析
3. A/B 测试
4. 素材评分
5. 优化建议
6. 优秀素材推荐
"""

import sys
import io
from pathlib import Path

# 处理 Windows 控制台编码
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from backend.services.ad_creative import creative_service, CreativeStatus

def print_section(title):
    """打印章节标题"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)

def print_item(label, value, indent=0):
    """打印项目"""
    prefix = "  " * indent
    print(f"{prefix}{label}: {value}")

def demo_upload():
    """演示素材上传"""
    print_section("📤 1. 素材上传与管理")
    
    # 上传三个测试素材
    creatives = []
    
    # 素材 1 - 高表现
    c1 = creative_service.upload_creative(
        name="夏季促销 - 主图 A",
        creative_type="image",
        file_content=b"fake_image_data_1",
        file_path="uploads/summer_promo_a.jpg",
        dimensions={"width": 1080, "height": 1080},
        file_size=102400,
        tags=["促销", "夏季", "图片"]
    )
    creatives.append(c1)
    print_item(f"✅ 上传素材", f'"{c1.name}" (ID: {c1.id[:8]}...)')
    
    # 素材 2 - 中等表现
    c2 = creative_service.upload_creative(
        name="品牌形象视频",
        creative_type="video",
        file_content=b"fake_video_data_2",
        file_path="uploads/brand_video.mp4",
        dimensions={"width": 1920, "height": 1080},
        file_size=5120000,
        tags=["品牌", "视频"]
    )
    creatives.append(c2)
    print_item(f"✅ 上传素材", f'"{c2.name}" (ID: {c2.id[:8]}...)')
    
    # 素材 3 - 低表现
    c3 = creative_service.upload_creative(
        name="产品轮播展示",
        creative_type="carousel",
        file_content=b"fake_carousel_data_3",
        file_path="uploads/product_carousel.jpg",
        dimensions={"width": 1080, "height": 1080},
        file_size=204800,
        tags=["产品", "轮播"]
    )
    creatives.append(c3)
    print_item(f"✅ 上传素材", f'"{c3.name}" (ID: {c3.id[:8]}...)')
    
    return creatives

def demo_metrics(creatives):
    """演示效果数据更新"""
    print_section("📊 2. 效果数据追踪")
    
    # 为每个素材更新效果数据
    metrics_data = [
        # 高表现素材
        {"impressions": 50000, "clicks": 2500, "conversions": 150, "spend": 1000.0, "revenue": 5000.0},
        # 中等表现素材
        {"impressions": 30000, "clicks": 900, "conversions": 30, "spend": 800.0, "revenue": 2000.0},
        # 低表现素材
        {"impressions": 20000, "clicks": 200, "conversions": 5, "spend": 500.0, "revenue": 300.0},
    ]
    
    for i, creative in enumerate(creatives):
        data = metrics_data[i]
        creative_service.update_metrics(creative.id, **data)
        
        print_item(f"素材", f'"{creative.name}"')
        print_item("  展示量", f"{data['impressions']:,}", indent=1)
        print_item("  点击量", f"{data['clicks']:,}", indent=1)
        print_item("  转化量", f"{data['conversions']:,}", indent=1)
        print_item("  CTR", f"{data['clicks']/data['impressions']*100:.2f}%", indent=1)
        print_item("  CVR", f"{data['conversions']/data['clicks']*100:.2f}%", indent=1)
        print_item("  ROAS", f"{data['revenue']/data['spend']:.2f}", indent=1)
        print()

def demo_analysis(creatives):
    """演示素材分析"""
    print_section("🔍 3. 素材效果分析")
    
    for creative in creatives:
        analysis = creative_service.analyze_creative(creative.id)
        
        print_item(f"素材", f'"{creative.name}"')
        print_item("  综合评分", f"{analysis['analysis']['score']} / 100", indent=1)
        print_item("  表现等级", analysis['analysis']['performance_level'].upper(), indent=1)
        
        if analysis['analysis']['strengths']:
            print_item("  优势", "", indent=1)
            for strength in analysis['analysis']['strengths']:
                print_item("    ✓", strength, indent=2)
        
        if analysis['analysis']['weaknesses']:
            print_item("  待优化", "", indent=1)
            for weakness in analysis['analysis']['weaknesses']:
                print_item("    ⚠", weakness, indent=2)
        
        print_item("  优化建议", f"{len(analysis['analysis']['suggestions'])} 条", indent=1)
        print()

def demo_scoring(creatives):
    """演示评分系统"""
    print_section("⭐ 4. 素材评分系统")
    
    print_item("评分维度权重", "")
    print_item("  CTR 表现", "30%", indent=1)
    print_item("  CVR 表现", "30%", indent=1)
    print_item("  ROAS 表现", "25%", indent=1)
    print_item("  数据量可靠性", "15%", indent=1)
    print()
    
    print_item("表现等级标准", "")
    print_item("  优秀", "≥80 分", indent=1)
    print_item("  良好", "60-79 分", indent=1)
    print_item("  一般", "40-59 分", indent=1)
    print_item("  需优化", "<40 分", indent=1)
    print()
    
    print_item("素材评分排名", "")
    sorted_creatives = sorted(creatives, key=lambda c: c.calculate_score(), reverse=True)
    
    for i, creative in enumerate(sorted_creatives, 1):
        score = creative.calculate_score()
        medal = "🥇" if i == 1 else "🥈" if i == 2 else "🥉" if i == 3 else ""
        print_item(f"  {medal} #{i}", f'"{creative.name}" - {score}分', indent=1)

def demo_abtest(creatives):
    """演示 A/B 测试"""
    print_section("🧪 5. A/B 测试")
    
    # 创建 A/B 测试
    ab_test = creative_service.create_ab_test(
        name="夏季促销素材对比测试",
        creative_ids=[creatives[0].id, creatives[1].id]
    )
    
    print_item("✅ 创建 A/B 测试", f'"{ab_test.name}"')
    print_item("  测试 ID", ab_test.id[:8] + "...", indent=1)
    print_item("  参与素材", f"{len(ab_test.creative_ids)} 个", indent=1)
    print_item("  状态", ab_test.status.value, indent=1)
    print()
    
    # 完成测试
    print_item("⏹️ 完成测试", "")
    result = creative_service.complete_ab_test(ab_test.id)
    
    print_item("  测试状态", result['status'], indent=1)
    print_item("  获胜素材 ID", result['winner_id'][:8] + "...", indent=1)
    print_item("  置信度", f"{result['confidence_level']*100:.1f}%", indent=1)
    
    # 获取分析报告
    analysis = creative_service.get_ab_test_analysis(ab_test.id)
    print_item("  建议", analysis['recommendation'], indent=1)
    print()

def demo_recommendations():
    """演示优秀素材推荐"""
    print_section("🏆 6. 优秀素材推荐")
    
    top_creatives = creative_service.get_top_creatives(limit=3, min_impressions=100)
    
    print_item(f"推荐 Top {len(top_creatives)} 素材", "")
    
    for i, creative in enumerate(top_creatives, 1):
        print_item(f"  #{i}", f'"{creative.name}"', indent=1)
        print_item("    评分", creative.calculate_score(), indent=2)
        print_item("    CTR", f"{creative.metrics.ctr*100:.2f}%", indent=2)
        print_item("    ROAS", f"{creative.metrics.roas:.2f}", indent=2)

def demo_dashboard():
    """演示仪表板"""
    print_section("📈 7. 仪表板总览")
    
    all_creatives = list(creative_service.creatives.values())
    
    total_impressions = sum(c.metrics.impressions for c in all_creatives)
    total_clicks = sum(c.metrics.clicks for c in all_creatives)
    total_conversions = sum(c.metrics.conversions for c in all_creatives)
    total_spend = sum(c.metrics.spend for c in all_creatives)
    total_revenue = sum(c.metrics.revenue for c in all_creatives)
    
    print_item("总素材数", len(all_creatives))
    print_item("总展示量", f"{total_impressions:,}")
    print_item("总点击量", f"{total_clicks:,}")
    print_item("总转化量", f"{total_conversions:,}")
    print_item("总花费", f"¥{total_spend:,.2f}")
    print_item("总收入", f"¥{total_revenue:,.2f}")
    print_item("整体 CTR", f"{total_clicks/total_impressions*100:.2f}%" if total_impressions > 0 else "N/A")
    print_item("整体 CVR", f"{total_conversions/total_clicks*100:.2f}%" if total_clicks > 0 else "N/A")
    print_item("整体 ROAS", f"{total_revenue/total_spend:.2f}" if total_spend > 0 else "N/A")
    print()
    
    # 找出最佳素材
    best = max(all_creatives, key=lambda c: c.calculate_score())
    print_item("🏅 最佳表现素材", f'"{best.name}"')
    print_item("  评分", best.calculate_score(), indent=1)

def demo_export():
    """演示数据导出"""
    print_section("💾 8. 数据导出")
    
    export_data = creative_service.export_analytics(format='json')
    
    print_item("✅ 导出数据", "JSON 格式")
    print_item("  数据大小", f"{len(export_data)} 字节", indent=1)
    print_item("  包含内容", "素材列表 + A/B 测试 + 时间戳", indent=1)
    print()

def main():
    """主函数 - 运行所有演示"""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 15 + "LiveMirror 广告素材分析系统" + " " * 15 + "║")
    print("║" + " " * 18 + "功能演示脚本" + " " * 18 + "║")
    print("╚" + "═" * 58 + "╝")
    
    # 执行所有演示
    creatives = demo_upload()
    demo_metrics(creatives)
    demo_analysis(creatives)
    demo_scoring(creatives)
    demo_abtest(creatives)
    demo_recommendations()
    demo_dashboard()
    demo_export()
    
    print_section("✅ 演示完成")
    print("\n所有核心功能演示完毕！")
    print("运行测试：pytest tests/test_ad_creative.py -v")
    print("查看文档：cat README.md")
    print()

if __name__ == "__main__":
    main()
