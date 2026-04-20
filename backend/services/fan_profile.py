"""
粉丝画像分析服务
提供粉丝特征深度分析功能
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import random
import math


class FanProfileService:
    """粉丝画像服务类"""
    
    def __init__(self):
        # 模拟粉丝数据
        self.fans_data = self._generate_mock_fans()
    
    def _generate_mock_fans(self) -> List[Dict[str, Any]]:
        """生成模拟粉丝数据"""
        fans = []
        cities = ['北京', '上海', '广州', '深圳', '杭州', '成都', '武汉', '西安', '南京', '重庆']
        interests = ['科技', '娱乐', '体育', '美食', '旅游', '时尚', '教育', '财经', '健康', '游戏']
        
        for i in range(1000):
            fan = {
                'id': i + 1,
                'age': random.randint(18, 65),
                'gender': random.choice(['male', 'female']),
                'city': random.choice(cities),
                'follow_date': datetime.now() - timedelta(days=random.randint(1, 365)),
                'last_active': datetime.now() - timedelta(days=random.randint(0, 90)),
                'interaction_count': random.randint(0, 500),
                'purchase_count': random.randint(0, 50),
                'total_spent': random.uniform(0, 10000),
                'interests': random.sample(interests, random.randint(1, 4)),
                'engagement_score': random.uniform(0, 100),
            }
            fans.append(fan)
        
        return fans
    
    def get_basic_profile(self) -> Dict[str, Any]:
        """
        获取粉丝基础画像
        包含：年龄分布、性别比例、地区分布
        """
        age_groups = {'18-24': 0, '25-34': 0, '35-44': 0, '45-54': 0, '55+': 0}
        gender_count = {'male': 0, 'female': 0}
        city_count = {}
        
        for fan in self.fans_data:
            # 年龄分组
            age = fan['age']
            if 18 <= age <= 24:
                age_groups['18-24'] += 1
            elif 25 <= age <= 34:
                age_groups['25-34'] += 1
            elif 35 <= age <= 44:
                age_groups['35-44'] += 1
            elif 45 <= age <= 54:
                age_groups['45-54'] += 1
            else:
                age_groups['55+'] += 1
            
            # 性别统计
            gender_count[fan['gender']] += 1
            
            # 地区统计
            city = fan['city']
            city_count[city] = city_count.get(city, 0) + 1
        
        total = len(self.fans_data)
        
        return {
            'total_fans': total,
            'age_distribution': {
                k: {'count': v, 'percentage': round(v / total * 100, 2)}
                for k, v in age_groups.items()
            },
            'gender_distribution': {
                k: {'count': v, 'percentage': round(v / total * 100, 2)}
                for k, v in gender_count.items()
            },
            'city_distribution': {
                k: {'count': v, 'percentage': round(v / total * 100, 2)}
                for k, v in sorted(city_count.items(), key=lambda x: x[1], reverse=True)[:10]
            }
        }
    
    def get_activity_levels(self) -> Dict[str, Any]:
        """
        获取粉丝活跃度分层
        分为：高活跃、中活跃、低活跃、沉睡粉丝
        """
        activity_levels = {
            'high': [],      # 高活跃：最近 7 天内活跃，互动次数>100
            'medium': [],    # 中活跃：最近 30 天内活跃，互动次数>50
            'low': [],       # 低活跃：最近 90 天内活跃，互动次数>10
            'dormant': []    # 沉睡粉丝：90 天以上未活跃
        }
        
        now = datetime.now()
        
        for fan in self.fans_data:
            days_inactive = (now - fan['last_active']).days
            interactions = fan['interaction_count']
            
            if days_inactive <= 7 and interactions > 100:
                activity_levels['high'].append(fan['id'])
            elif days_inactive <= 30 and interactions > 50:
                activity_levels['medium'].append(fan['id'])
            elif days_inactive <= 90 and interactions > 10:
                activity_levels['low'].append(fan['id'])
            else:
                activity_levels['dormant'].append(fan['id'])
        
        total = len(self.fans_data)
        
        return {
            'high_activity': {
                'count': len(activity_levels['high']),
                'percentage': round(len(activity_levels['high']) / total * 100, 2),
                'fan_ids': activity_levels['high'][:20]  # 只返回前 20 个示例
            },
            'medium_activity': {
                'count': len(activity_levels['medium']),
                'percentage': round(len(activity_levels['medium']) / total * 100, 2),
                'fan_ids': activity_levels['medium'][:20]
            },
            'low_activity': {
                'count': len(activity_levels['low']),
                'percentage': round(len(activity_levels['low']) / total * 100, 2),
                'fan_ids': activity_levels['low'][:20]
            },
            'dormant': {
                'count': len(activity_levels['dormant']),
                'percentage': round(len(activity_levels['dormant']) / total * 100, 2),
                'fan_ids': activity_levels['dormant'][:20]
            }
        }
    
    def get_interest_tags(self) -> Dict[str, Any]:
        """
        获取粉丝兴趣标签分布
        """
        interest_count = {}
        
        for fan in self.fans_data:
            for interest in fan['interests']:
                interest_count[interest] = interest_count.get(interest, 0) + 1
        
        total = len(self.fans_data)
        
        # 按关注度排序
        sorted_interests = sorted(interest_count.items(), key=lambda x: x[1], reverse=True)
        
        return {
            'tags': [
                {
                    'name': interest,
                    'count': count,
                    'percentage': round(count / total * 100, 2)
                }
                for interest, count in sorted_interests
            ],
            'top_tags': [interest for interest, _ in sorted_interests[:5]]
        }
    
    def calculate_ltv(self, fan_id: Optional[int] = None) -> Dict[str, Any]:
        """
        计算粉丝生命周期价值 (LTV)
        
        LTV = 平均购买金额 × 购买频率 × 平均生命周期
        
        粉丝价值分层：
        - VIP: LTV > 5000
        - 高价值：2000 < LTV <= 5000
        - 中价值：500 < LTV <= 2000
        - 低价值：LTV <= 500
        """
        if fan_id:
            # 计算单个粉丝的 LTV
            fan = next((f for f in self.fans_data if f['id'] == fan_id), None)
            if not fan:
                return {'error': 'Fan not found'}
            
            # 简化 LTV 计算
            avg_purchase_value = fan['total_spent'] / max(fan['purchase_count'], 1)
            purchase_frequency = fan['purchase_count'] / max((datetime.now() - fan['follow_date']).days / 30, 1)
            avg_lifespan_months = 12  # 假设平均生命周期 12 个月
            
            ltv = avg_purchase_value * purchase_frequency * avg_lifespan_months
            
            if ltv > 5000:
                tier = 'VIP'
            elif ltv > 2000:
                tier = 'high_value'
            elif ltv > 500:
                tier = 'medium_value'
            else:
                tier = 'low_value'
            
            return {
                'fan_id': fan_id,
                'ltv': round(ltv, 2),
                'tier': tier,
                'total_spent': round(fan['total_spent'], 2),
                'purchase_count': fan['purchase_count']
            }
        else:
            # 计算整体粉丝 LTV 分布
            ltv_distribution = {'VIP': 0, 'high_value': 0, 'medium_value': 0, 'low_value': 0}
            total_ltv = 0
            
            for fan in self.fans_data:
                avg_purchase_value = fan['total_spent'] / max(fan['purchase_count'], 1)
                purchase_frequency = fan['purchase_count'] / max((datetime.now() - fan['follow_date']).days / 30, 1)
                avg_lifespan_months = 12
                
                ltv = avg_purchase_value * purchase_frequency * avg_lifespan_months
                total_ltv += ltv
                
                if ltv > 5000:
                    ltv_distribution['VIP'] += 1
                elif ltv > 2000:
                    ltv_distribution['high_value'] += 1
                elif ltv > 500:
                    ltv_distribution['medium_value'] += 1
                else:
                    ltv_distribution['low_value'] += 1
            
            total = len(self.fans_data)
            
            return {
                'average_ltv': round(total_ltv / total, 2),
                'distribution': {
                    k: {'count': v, 'percentage': round(v / total * 100, 2)}
                    for k, v in ltv_distribution.items()
                },
                'total_revenue': round(sum(f['total_spent'] for f in self.fans_data), 2)
            }
    
    def get_churn_warning(self) -> Dict[str, Any]:
        """
        获取粉丝流失预警
        基于活跃度下降、互动减少等指标
        """
        at_risk_fans = []
        
        now = datetime.now()
        
        for fan in self.fans_data:
            days_inactive = (now - fan['last_active']).days
            engagement_score = fan['engagement_score']
            
            risk_score = 0
            risk_factors = []
            
            # 风险因素 1: 长时间未活跃
            if days_inactive > 60:
                risk_score += 40
                risk_factors.append('long_inactive')
            elif days_inactive > 30:
                risk_score += 20
                risk_factors.append('moderate_inactive')
            
            # 风险因素 2: 互动分数低
            if engagement_score < 30:
                risk_score += 30
                risk_factors.append('low_engagement')
            elif engagement_score < 50:
                risk_score += 15
                risk_factors.append('moderate_engagement')
            
            # 风险因素 3: 互动次数少
            if fan['interaction_count'] < 20:
                risk_score += 30
                risk_factors.append('low_interaction')
            
            # 判断风险等级
            if risk_score >= 70:
                risk_level = 'high'
            elif risk_score >= 40:
                risk_level = 'medium'
            elif risk_score >= 20:
                risk_level = 'low'
            else:
                risk_level = 'none'
            
            if risk_level != 'none':
                at_risk_fans.append({
                    'fan_id': fan['id'],
                    'risk_level': risk_level,
                    'risk_score': risk_score,
                    'risk_factors': risk_factors,
                    'days_inactive': days_inactive,
                    'engagement_score': round(engagement_score, 2)
                })
        
        # 按风险分数排序
        at_risk_fans.sort(key=lambda x: x['risk_score'], reverse=True)
        
        risk_summary = {
            'high': [f for f in at_risk_fans if f['risk_level'] == 'high'],
            'medium': [f for f in at_risk_fans if f['risk_level'] == 'medium'],
            'low': [f for f in at_risk_fans if f['risk_level'] == 'low']
        }
        
        total = len(self.fans_data)
        
        return {
            'total_at_risk': len(at_risk_fans),
            'at_risk_percentage': round(len(at_risk_fans) / total * 100, 2),
            'risk_distribution': {
                'high': {
                    'count': len(risk_summary['high']),
                    'percentage': round(len(risk_summary['high']) / total * 100, 2)
                },
                'medium': {
                    'count': len(risk_summary['medium']),
                    'percentage': round(len(risk_summary['medium']) / total * 100, 2)
                },
                'low': {
                    'count': len(risk_summary['low']),
                    'percentage': round(len(risk_summary['low']) / total * 100, 2)
                }
            },
            'high_risk_fans': risk_summary['high'][:20]  # 返回前 20 个高风险粉丝
        }
    
    def get_growth_trend(self) -> Dict[str, Any]:
        """
        获取粉丝增长趋势
        按月份统计新增粉丝数
        """
        monthly_growth = {}
        
        for fan in self.fans_data:
            month_key = fan['follow_date'].strftime('%Y-%m')
            monthly_growth[month_key] = monthly_growth.get(month_key, 0) + 1
        
        # 按月份排序
        sorted_months = sorted(monthly_growth.keys())
        
        # 计算增长率
        growth_rates = []
        for i in range(1, len(sorted_months)):
            prev_month = sorted_months[i - 1]
            curr_month = sorted_months[i]
            prev_count = monthly_growth[prev_month]
            curr_count = monthly_growth[curr_month]
            
            growth_rate = ((curr_count - prev_count) / max(prev_count, 1)) * 100
            growth_rates.append({
                'month': curr_month,
                'new_fans': curr_count,
                'growth_rate': round(growth_rate, 2)
            })
        
        return {
            'monthly_data': [
                {'month': month, 'new_fans': count}
                for month, count in monthly_growth.items()
            ],
            'growth_rates': growth_rates,
            'total_growth': sum(monthly_growth.values()),
            'average_monthly_growth': round(sum(monthly_growth.values()) / max(len(monthly_growth), 1), 2)
        }
    
    def get_full_profile_report(self) -> Dict[str, Any]:
        """
        获取完整的粉丝画像报告
        包含所有分析维度
        """
        return {
            'basic_profile': self.get_basic_profile(),
            'activity_levels': self.get_activity_levels(),
            'interest_tags': self.get_interest_tags(),
            'ltv_analysis': self.calculate_ltv(),
            'churn_warning': self.get_churn_warning(),
            'growth_trend': self.get_growth_trend(),
            'generated_at': datetime.now().isoformat()
        }


# 测试函数
def run_tests():
    """运行粉丝画像服务测试"""
    print("=" * 60)
    print("粉丝画像服务测试")
    print("=" * 60)
    
    service = FanProfileService()
    
    # 测试 1: 基础画像生成
    print("\n[测试 1] 基础画像生成")
    basic = service.get_basic_profile()
    print(f"✓ 总粉丝数：{basic['total_fans']}")
    print(f"✓ 年龄分布：{basic['age_distribution']}")
    print(f"✓ 性别分布：{basic['gender_distribution']}")
    print(f"✓ 地区分布 (前 5): {list(basic['city_distribution'].items())[:5]}")
    
    # 测试 2: 活跃度分层
    print("\n[测试 2] 活跃度分层")
    activity = service.get_activity_levels()
    print(f"✓ 高活跃：{activity['high_activity']['count']} ({activity['high_activity']['percentage']}%)")
    print(f"✓ 中活跃：{activity['medium_activity']['count']} ({activity['medium_activity']['percentage']}%)")
    print(f"✓ 低活跃：{activity['low_activity']['count']} ({activity['low_activity']['percentage']}%)")
    print(f"✓ 沉睡粉丝：{activity['dormant']['count']} ({activity['dormant']['percentage']}%)")
    
    # 测试 3: LTV 计算
    print("\n[测试 3] LTV 计算")
    ltv = service.calculate_ltv()
    print(f"✓ 平均 LTV: {ltv['average_ltv']}")
    print(f"✓ 总营收：{ltv['total_revenue']}")
    print(f"✓ 价值分布：{ltv['distribution']}")
    
    # 测试单个粉丝 LTV
    single_ltv = service.calculate_ltv(fan_id=1)
    print(f"✓ 粉丝#1 LTV: {single_ltv}")
    
    # 测试 4: 流失预警
    print("\n[测试 4] 流失预警")
    churn = service.get_churn_warning()
    print(f"✓ 风险粉丝总数：{churn['total_at_risk']} ({churn['at_risk_percentage']}%)")
    print(f"✓ 高风险：{churn['risk_distribution']['high']['count']}")
    print(f"✓ 中风险：{churn['risk_distribution']['medium']['count']}")
    print(f"✓ 低风险：{churn['risk_distribution']['low']['count']}")
    if churn['high_risk_fans']:
        print(f"✓ 高风险粉丝示例：{churn['high_risk_fans'][:3]}")
    
    # 测试 5: 增长趋势
    print("\n[测试 5] 增长趋势")
    growth = service.get_growth_trend()
    print(f"✓ 总增长：{growth['total_growth']}")
    print(f"✓ 月均增长：{growth['average_monthly_growth']}")
    print(f"✓ 月度数据 (前 5): {growth['monthly_data'][:5]}")
    
    # 测试 6: 兴趣标签
    print("\n[测试 6] 兴趣标签")
    interests = service.get_interest_tags()
    print(f"✓ 热门标签：{interests['top_tags']}")
    print(f"✓ 标签分布 (前 5): {interests['tags'][:5]}")
    
    print("\n" + "=" * 60)
    print("所有测试完成！✓")
    print("=" * 60)
    
    return True


if __name__ == '__main__':
    run_tests()
