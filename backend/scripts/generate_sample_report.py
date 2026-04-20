"""
生成选品样本报告
用于展示选品推荐功能的效果
"""

import sys
import os
import json
from datetime import datetime

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.product_selection import get_service


def generate_sample_report():
    """生成选品样本报告"""
    service = get_service()
    
    print("=" * 70)
    print("LiveMirror Product Selection System - Sample Report")
    print("=" * 70)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # 获取推荐商品列表
    recommendations = service.get_recommendations(min_score=60.0, limit=5)
    
    print(f"\nFound {len(recommendations)} recommended products\n")
    
    for idx, report in enumerate(recommendations, 1):
        print("-" * 70)
        print(f"Recommendation #{idx}: {report.product_name}")
        print("-" * 70)
        print(f"Product ID: {report.product_id}")
        print(f"Recommendation Score: {report.recommendation_score}")
        print(f"Summary: {report.summary}")
        
        # 热度分析
        heat = report.heat_analysis
        print("\n[Heat Analysis]")
        print(f"   Heat Score: {heat.get('heat_score', 0)}")
        print(f"   Search Growth: {heat.get('search_trend', {}).get('growth_rate', 0)}%")
        print(f"   Social Mentions: {heat.get('social_media', {}).get('mentions', 0)}")
        print(f"   Trend Status: {heat.get('trend_status', 'unknown')}")
        
        # 价格对比
        price = report.price_comparison
        print("\n[Price Comparison]")
        print(f"   Our Price: Y{price.get('our_price', 0)}")
        print(f"   Market Avg: Y{price.get('market_avg_price', 0)}")
        print(f"   Price Advantage: {price.get('price_advantage', 0)}%")
        
        # 利润分析
        profit = report.profit_analysis
        print("\n[Profit Analysis]")
        print(f"   Gross Margin: {profit.get('gross_margin_percent', 0)}%")
        print(f"   Net Margin: {profit.get('net_margin_percent', 0)}%")
        print(f"   ROI: {profit.get('roi_percent', 0)}%")
        print(f"   Profitability: {profit.get('profitability_rating', 'unknown')}")
        
        # 季节性分析
        season = report.seasonality_analysis
        print("\n[Seasonality Analysis]")
        print(f"   Current Month Factor: {season.get('current_month_factor', 1.0)}")
        print(f"   Peak Season: {season.get('peak_season', '-')}")
        print(f"   Low Season: {season.get('low_season', '-')}")
        rec = 'Good time to sell' if season.get('recommendation') == 'good_time' else 'Wait for peak season'
        print(f"   Recommendation: {rec}")
        
        # 供应商评估
        supplier = report.supplier_evaluation
        print("\n[Supplier Evaluation]")
        print(f"   Supplier: {supplier.get('supplier_name', 'Unknown')}")
        print(f"   Overall Rating: {supplier.get('overall_rating', 0)}/5.0")
        print(f"   On-time Delivery: {supplier.get('on_time_delivery_rate', 0)}%")
        print(f"   Defect Rate: {supplier.get('defect_rate_percent', 0)}%")
        print(f"   Risk Level: {supplier.get('risk_level', 'unknown')}")
        
        print()
    
    print("=" * 70)
    print("End of Report")
    print("=" * 70)
    
    # 同时生成 JSON 格式的报告文件
    from dataclasses import asdict
    reports_data = {
        "generated_at": datetime.now().isoformat(),
        "total_recommendations": len(recommendations),
        "products": [asdict(report) for report in recommendations]
    }
    
    output_file = "backend/output/sample_selection_report.json"
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(reports_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n[INFO] JSON report saved to: {output_file}")
    
    return recommendations


if __name__ == '__main__':
    try:
        generate_sample_report()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
