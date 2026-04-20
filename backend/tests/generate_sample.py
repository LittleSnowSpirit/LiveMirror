# -*- coding: utf-8 -*-
"""
生成粉丝画像样本报告
"""

import sys
import os
import json

# Add workspace root to path
workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, workspace_root)

from services.fan_profile import FanProfileService

def generate_sample():
    service = FanProfileService()
    report = service.get_full_profile_report()
    
    print("=" * 60)
    print("Fan Profile Sample Report")
    print("=" * 60)
    
    print("\n[1] Basic Profile")
    print("-" * 40)
    basic = report['basic_profile']
    print("Total Fans: {}".format(basic['total_fans']))
    print("\nAge Distribution:")
    for age, data in basic['age_distribution'].items():
        print("  {}: {} ({}%)".format(age, data['count'], data['percentage']))
    
    print("\nGender Distribution:")
    for gender, data in basic['gender_distribution'].items():
        print("  {}: {} ({}%)".format(gender, data['count'], data['percentage']))
    
    print("\nTop 5 Cities:")
    for i, (city, data) in enumerate(list(basic['city_distribution'].items())[:5], 1):
        print("  {}. {}: {} ({}%)".format(i, city, data['count'], data['percentage']))
    
    print("\n[2] Activity Levels")
    print("-" * 40)
    activity = report['activity_levels']
    print("High Activity: {} ({}%)".format(
        activity['high_activity']['count'],
        activity['high_activity']['percentage']
    ))
    print("Medium Activity: {} ({}%)".format(
        activity['medium_activity']['count'],
        activity['medium_activity']['percentage']
    ))
    print("Low Activity: {} ({}%)".format(
        activity['low_activity']['count'],
        activity['low_activity']['percentage']
    ))
    print("Dormant: {} ({}%)".format(
        activity['dormant']['count'],
        activity['dormant']['percentage']
    ))
    
    print("\n[3] Interest Tags (Top 5)")
    print("-" * 40)
    interests = report['interest_tags']
    for i, tag in enumerate(interests['tags'][:5], 1):
        print("  {}. {}: {} ({}%)".format(i, tag['name'], tag['count'], tag['percentage']))
    
    print("\n[4] LTV Analysis")
    print("-" * 40)
    ltv = report['ltv_analysis']
    print("Average LTV: Y{}".format(ltv['average_ltv']))
    print("Total Revenue: Y{}".format(ltv['total_revenue']))
    print("\nValue Distribution:")
    for tier, data in ltv['distribution'].items():
        print("  {}: {} ({}%)".format(tier, data['count'], data['percentage']))
    
    print("\n[5] Churn Warning")
    print("-" * 40)
    churn = report['churn_warning']
    print("Total At Risk: {} ({}%)".format(
        churn['total_at_risk'],
        churn['at_risk_percentage']
    ))
    print("High Risk: {}".format(churn['risk_distribution']['high']['count']))
    print("Medium Risk: {}".format(churn['risk_distribution']['medium']['count']))
    print("Low Risk: {}".format(churn['risk_distribution']['low']['count']))
    
    if churn['high_risk_fans']:
        print("\nTop 3 High Risk Fans:")
        for fan in churn['high_risk_fans'][:3]:
            print("  Fan #{}: Score={}, Days Inactive={}, Factors={}".format(
                fan['fan_id'],
                fan['risk_score'],
                fan['days_inactive'],
                ', '.join(fan['risk_factors'])
            ))
    
    print("\n[6] Growth Trend")
    print("-" * 40)
    growth = report['growth_trend']
    print("Total Growth: {}".format(growth['total_growth']))
    print("Average Monthly Growth: {}".format(growth['average_monthly_growth']))
    print("\nRecent 6 Months:")
    for month in growth['monthly_data'][-6:]:
        print("  {}: {} fans".format(month['month'], month['new_fans']))
    
    print("\n" + "=" * 60)
    print("Report Generated: {}".format(report['generated_at']))
    print("=" * 60)
    
    # Save to file
    output_path = os.path.join(os.path.dirname(__file__), 'fan_profile_sample.txt')
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("Fan Profile Sample Report\n")
        f.write("=" * 60 + "\n\n")
        f.write("Total Fans: {}\n".format(basic['total_fans']))
        f.write("Average LTV: Y{}\n".format(ltv['average_ltv']))
        f.write("Total Revenue: Y{}\n".format(ltv['total_revenue']))
        f.write("At-Risk Percentage: {}%\n".format(churn['at_risk_percentage']))
        f.write("Generated: {}\n".format(report['generated_at']))
    
    print("\nSample saved to: {}".format(output_path))

if __name__ == '__main__':
    generate_sample()
