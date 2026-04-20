"""
生成 ROI 分析示例数据 - LiveMirror
"""

from backend.services.roi_analysis import get_service, reset_service
import json
from datetime import datetime

# 重置服务
reset_service()
service = get_service()

# 创建示例场次数据
print("=== 创建示例直播场次 ===\n")

sample_sessions = [
    {
        "date": "2026-04-01",
        "start_time": "19:00",
        "end_time": "22:00",
        "category": "beauty",
        "costs": [
            {"type": "labor", "name": "主播", "amount": 600},
            {"type": "venue", "name": "场地租赁", "amount": 300},
            {"type": "promotion", "name": "抖音投放", "amount": 400}
        ],
        "revenues": [
            {"type": "gmv", "name": "商品销售", "amount": 8000},
            {"type": "profit", "name": "利润", "amount": 1600}
        ],
        "notes": "美妆专场，表现良好"
    },
    {
        "date": "2026-04-03",
        "start_time": "20:00",
        "end_time": "23:00",
        "category": "fashion",
        "costs": [
            {"type": "labor", "name": "主播", "amount": 800},
            {"type": "venue", "name": "场地租赁", "amount": 400},
            {"type": "promotion", "name": "小红书投放", "amount": 600},
            {"type": "equipment", "name": "设备租赁", "amount": 200}
        ],
        "revenues": [
            {"type": "gmv", "name": "服装销售", "amount": 12000},
            {"type": "profit", "name": "利润", "amount": 2400}
        ],
        "notes": "春季新品发布"
    },
    {
        "date": "2026-04-05",
        "start_time": "19:30",
        "end_time": "22:30",
        "category": "food",
        "costs": [
            {"type": "labor", "name": "主播", "amount": 500},
            {"type": "venue", "name": "厨房场地", "amount": 200},
            {"type": "promotion", "name": "微信群推广", "amount": 100}
        ],
        "revenues": [
            {"type": "gmv", "name": "食品销售", "amount": 5000},
            {"type": "profit", "name": "利润", "amount": 1200}
        ],
        "notes": "零食专场，成本低收益好"
    },
    {
        "date": "2026-04-07",
        "start_time": "18:00",
        "end_time": "21:00",
        "category": "electronics",
        "costs": [
            {"type": "labor", "name": "主播", "amount": 1000},
            {"type": "venue", "name": "展厅租赁", "amount": 800},
            {"type": "promotion", "name": "全平台投放", "amount": 1200},
            {"type": "equipment", "name": "展示设备", "amount": 500}
        ],
        "revenues": [
            {"type": "gmv", "name": "数码产品销售", "amount": 25000},
            {"type": "profit", "name": "利润", "amount": 3500}
        ],
        "notes": "数码专场，高成本高收益"
    },
    {
        "date": "2026-04-08",
        "start_time": "19:00",
        "end_time": "22:00",
        "category": "home",
        "costs": [
            {"type": "labor", "name": "主播", "amount": 500},
            {"type": "venue", "name": "场地租赁", "amount": 300},
            {"type": "promotion", "name": "朋友圈广告", "amount": 200}
        ],
        "revenues": [
            {"type": "gmv", "name": "家居用品销售", "amount": 6000},
            {"type": "profit", "name": "利润", "amount": 1000}
        ],
        "notes": "家居日用，稳定表现"
    }
]

# 创建场次
created_sessions = []
for session_data in sample_sessions:
    session = service.create_session(**session_data)
    created_sessions.append(session)
    roi = session.roi()
    print(f"[OK] {session.date} {session.category}: 成本 Y{session.total_cost()}, 收益 Y{session.total_revenue()}, ROI={roi:.2f}%")

print(f"\n共创建 {len(created_sessions)} 个场次")

# 计算并展示每个场次的 ROI 指标
print("\n=== ROI 指标详情 ===\n")
for session in created_sessions:
    metrics = service.calculate_roi_metrics(session.session_id)
    print(f"[DATA] {session.date} ({session.category})")
    print(f"   总成本：Y{metrics.total_cost:,.2f}")
    print(f"   总收益：Y{metrics.total_revenue:,.2f}")
    print(f"   GMV: Y{metrics.gmv:,.2f}")
    print(f"   利润：Y{metrics.profit:,.2f}")
    print(f"   ROI: {metrics.roi_percentage:.2f}%")
    print(f"   ROI 比率：{metrics.roi_ratio:.2f}")
    print()

# 对比分析
print("=== 场次对比分析 ===\n")
session_ids = [s.session_id for s in created_sessions]
comparison = service.compare_sessions(session_ids)

if comparison:
    print(f"[STATS] 平均 ROI: {comparison.average_roi:.2f}%")
    print(f"[BEST] 最佳场次：{comparison.best_roi_session} ({comparison.metrics[comparison.best_roi_session].roi_percentage:.2f}%)")
    print(f"[WORST] 最差场次：{comparison.worst_roi_session} ({comparison.metrics[comparison.worst_roi_session].roi_percentage:.2f}%)")
    print(f"[TREND] ROI 趋势：{comparison.roi_trend}")
    print("\n[INSIGHTS] 分析洞察:")
    for insight in comparison.insights:
        print(f"   - {insight}")

# 获取优化建议
print("\n=== 优化建议 ===\n")
for session in created_sessions[:3]:
    print(f"[SESSION] {session.date} ({session.category}):")
    suggestions = service.generate_optimization_suggestions(session.session_id)
    if suggestions:
        for i, s in enumerate(suggestions[:2], 1):
            print(f"   {i}. [{s.priority}] {s.suggestion}")
            print(f"      预期影响：{s.expected_impact}")
            if s.estimated_savings > 0:
                print(f"      预计节省：Y{s.estimated_savings:,.2f}")
    else:
        print("   暂无优化建议")
    print()

# 获取 ROI 趋势
print("=== ROI 趋势 ===\n")
trend = service.get_roi_trend(group_by="day")
for item in trend:
    print(f"{item['period']}: ROI={item['roi_percentage']:.2f}%, 成本 Y{item['total_cost']:,.2f}, 收益 Y{item['total_revenue']:,.2f}")

# 生成报告
print("\n=== 生成 ROI 分析报告 ===\n")
report = service.generate_report()

print(f"[REPORT] 报告 ID: {report['report_id']}")
print(f"[TIME] 生成时间：{report['generated_at']}")
print(f"\n[SUMMARY] 总体概览:")
print(f"   总场次：{report['summary']['total_sessions']}")
print(f"   总成本：Y{report['summary']['total_cost']:,.2f}")
print(f"   总收益：Y{report['summary']['total_revenue']:,.2f}")
print(f"   总 GMV: Y{report['summary']['total_gmv']:,.2f}")
print(f"   总利润：Y{report['summary']['total_profit']:,.2f}")
print(f"   整体 ROI: {report['summary']['overall_roi']:.2f}%")

print(f"\n[BEST] 最佳表现：{report['best_performer']['session_id']} (ROI: {report['best_performer']['roi']:.2f}%)")
print(f"[WORST] 最差表现：{report['worst_performer']['session_id']} (ROI: {report['worst_performer']['roi']:.2f}%)")

print(f"\n[SUGGESTIONS] 优化建议 ({len(report['optimization_suggestions'])} 条):")
for i, suggestion in enumerate(report['optimization_suggestions'][:5], 1):
    print(f"   {i}. {suggestion['suggestion']}")

print("\n[DONE] 示例数据生成完成！")
print(f"[PATH] 数据保存位置：{service.data_dir}")
