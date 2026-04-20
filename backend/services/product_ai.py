"""
LiveMirror Product AI Service
智能选品服务 - AI 驱动的产品选择与决策分析
"""

import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import json
import os
from dataclasses import dataclass, asdict


@dataclass
class ProductScore:
    """产品评分数据结构"""
    product_id: str
    product_name: str
    category: str
    overall_score: float  # 综合评分 (0-100)
    market_score: float  # 市场热度评分
    competition_score: float  # 竞争程度评分 (越低越好)
    trend_score: float  # 趋势评分
    supply_risk_score: float  # 供应链风险评分 (越低越好)
    profit_score: float  # 利润空间评分
    recommendation: str  # 推荐等级
    analysis_date: str


class ProductAIService:
    """AI 智能选品服务"""
    
    def __init__(self):
        self.data_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'data', 'products.json'
        )
        self.trend_data_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'data', 'trends.json'
        )
        self._load_data()
    
    def _load_data(self):
        """加载产品数据和趋势数据"""
        # 产品数据库
        if os.path.exists(self.data_path):
            with open(self.data_path, 'r', encoding='utf-8') as f:
                self.products_db = json.load(f)
        else:
            self.products_db = self._generate_product_database()
        
        # 趋势数据
        if os.path.exists(self.trend_data_path):
            with open(self.trend_data_path, 'r', encoding='utf-8') as f:
                self.trends_db = json.load(f)
        else:
            self.trends_db = self._generate_trend_database()
    
    def _generate_product_database(self) -> List[Dict]:
        """生成模拟产品数据库"""
        categories = ['美妆', '服饰', '食品', '数码', '家居', '运动', '母婴', '宠物']
        
        products = []
        base_id = 1000
        
        for category in categories:
            for i in range(15):  # 每个类别 15 个产品
                product = {
                    'product_id': f'P{base_id}',
                    'product_name': f'{category}爆款产品{i+1}',
                    'category': category,
                    'base_price': np.random.randint(50, 500),
                    'cost_price': np.random.randint(20, 200),
                    'monthly_sales': np.random.randint(100, 10000),
                    'competition_level': np.random.uniform(0.3, 0.9),
                    'seasonal_factor': np.random.uniform(0.7, 1.3),
                    'supply_stability': np.random.uniform(0.6, 1.0),
                    'profit_margin': np.random.uniform(0.2, 0.6),
                    'growth_rate': np.random.uniform(-0.2, 0.5),
                    'customer_rating': np.random.uniform(3.5, 5.0),
                    'return_rate': np.random.uniform(0.02, 0.15),
                    'inventory_days': np.random.randint(7, 60),
                    'supplier_count': np.random.randint(1, 10),
                    'trend_score': np.random.uniform(0.4, 0.95)
                }
                products.append(product)
                base_id += 1
        
        return products
    
    def _generate_trend_database(self) -> Dict:
        """生成趋势数据库"""
        categories = ['美妆', '服饰', '食品', '数码', '家居', '运动', '母婴', '宠物']
        months = list(range(1, 13))
        
        trends = {
            'seasonal': {},
            'hot_keywords': [],
            'category_trends': {}
        }
        
        # 季节性趋势
        for category in categories:
            trends['seasonal'][category] = {
                month: round(np.random.uniform(0.5, 1.5), 2) 
                for month in months
            }
        
        # 热门关键词
        keywords = ['新品', '爆款', '网红', ' ins 风', '平替', '小众', '高端', '性价比']
        trends['hot_keywords'] = [
            {
                'keyword': kw,
                'search_volume': np.random.randint(10000, 500000),
                'growth_rate': round(np.random.uniform(-0.1, 0.8), 3),
                'competition': round(np.random.uniform(0.3, 0.9), 2)
            }
            for kw in keywords
        ]
        
        # 类别趋势
        for category in categories:
            trends['category_trends'][category] = {
                'current_score': round(np.random.uniform(0.4, 0.95), 3),
                '30d_change': round(np.random.uniform(-0.2, 0.4), 3),
                '90d_change': round(np.random.uniform(-0.3, 0.5), 3),
                'prediction_30d': round(np.random.uniform(0.3, 0.9), 3)
            }
        
        return trends
    
    def calculate_product_score(self, product: Dict) -> ProductScore:
        """
        计算产品综合评分
        
        多维度分析：
        - 市场热度 (30%)
        - 竞争程度 (20%)
        - 趋势分数 (20%)
        - 供应链风险 (15%)
        - 利润空间 (15%)
        """
        # 市场热度评分 (基于销量、增长率、评分)
        market_score = (
            min(product['monthly_sales'] / 10000, 1.0) * 0.4 +
            max(0, product['growth_rate']) * 0.3 +
            (product['customer_rating'] / 5.0) * 0.3
        ) * 100
        
        # 竞争程度评分 (越低越好，转换为正向分数)
        competition_score = (1 - product['competition_level']) * 100
        
        # 趋势评分
        trend_score = product['trend_score'] * 100
        
        # 供应链风险评分 (基于稳定性、供应商数量、库存天数)
        supply_risk = (
            (1 - product['supply_stability']) * 0.4 +
            (1 - min(product['supplier_count'] / 5, 1.0)) * 0.3 +
            min(product['inventory_days'] / 60, 1.0) * 0.3
        )
        supply_risk_score = (1 - supply_risk) * 100
        
        # 利润空间评分
        profit_score = product['profit_margin'] * 100
        
        # 综合评分 (加权平均)
        overall_score = (
            market_score * 0.30 +
            competition_score * 0.20 +
            trend_score * 0.20 +
            supply_risk_score * 0.15 +
            profit_score * 0.15
        )
        
        # 推荐等级
        if overall_score >= 80:
            recommendation = "强烈推荐"
        elif overall_score >= 65:
            recommendation = "推荐"
        elif overall_score >= 50:
            recommendation = "谨慎考虑"
        else:
            recommendation = "不推荐"
        
        return ProductScore(
            product_id=product['product_id'],
            product_name=product['product_name'],
            category=product['category'],
            overall_score=round(overall_score, 2),
            market_score=round(market_score, 2),
            competition_score=round(competition_score, 2),
            trend_score=round(trend_score, 2),
            supply_risk_score=round(supply_risk_score, 2),
            profit_score=round(profit_score, 2),
            recommendation=recommendation,
            analysis_date=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
    
    def analyze_competitors(self, product_id: str, category: str) -> Dict:
        """
        竞品选品分析
        
        分析同类产品的竞争情况
        """
        # 获取同类产品
        similar_products = [
            p for p in self.products_db 
            if p['category'] == category and p['product_id'] != product_id
        ]
        
        if not similar_products:
            return {'error': '未找到竞品'}
        
        # 计算竞争指标
        avg_price = np.mean([p['base_price'] for p in similar_products])
        avg_sales = np.mean([p['monthly_sales'] for p in similar_products])
        avg_competition = np.mean([p['competition_level'] for p in similar_products])
        
        # 找到目标产品
        target_product = next(
            (p for p in self.products_db if p['product_id'] == product_id), 
            None
        )
        
        if not target_product:
            return {'error': '产品不存在'}
        
        # 竞争分析
        price_advantage = (avg_price - target_product['base_price']) / avg_price
        sales_position = target_product['monthly_sales'] / avg_sales if avg_sales > 0 else 0
        
        # 市场份额估算
        total_market = sum([p['monthly_sales'] for p in similar_products]) + target_product['monthly_sales']
        market_share = target_product['monthly_sales'] / total_market if total_market > 0 else 0
        
        return {
            'product_id': product_id,
            'category': category,
            'total_competitors': len(similar_products),
            'avg_competitor_price': round(avg_price, 2),
            'avg_competitor_sales': int(avg_sales),
            'price_advantage_percent': round(price_advantage * 100, 2),
            'sales_position_ratio': round(sales_position, 3),
            'estimated_market_share': round(market_share * 100, 2),
            'competition_intensity': '高' if avg_competition > 0.7 else '中' if avg_competition > 0.4 else '低',
            'top_competitors': sorted(
                similar_products, 
                key=lambda x: x['monthly_sales'], 
                reverse=True
            )[:5]
        }
    
    def predict_trend(self, category: str, months_ahead: int = 3) -> Dict:
        """
        趋势预测 (季节性/热点)
        
        Args:
            category: 产品类别
            months_ahead: 预测月数
            
        Returns:
            趋势预测结果
        """
        current_month = datetime.now().month
        
        # 获取季节性趋势
        seasonal_trend = self.trends_db['seasonal'].get(category, {})
        
        # 获取类别趋势
        category_trend = self.trends_db['category_trends'].get(category, {
            'current_score': 0.5,
            '30d_change': 0,
            '90d_change': 0,
            'prediction_30d': 0.5
        })
        
        # 预测未来几个月的趋势
        predictions = []
        for i in range(1, months_ahead + 1):
            future_month = (current_month + i - 1) % 12 + 1
            seasonal_factor = seasonal_trend.get(future_month, 1.0)
            
            # 趋势预测 = 基础趋势 * 季节性因子
            base_prediction = category_trend['prediction_30d']
            predicted_score = min(1.0, max(0.0, base_prediction * seasonal_factor))
            
            predictions.append({
                'month': future_month,
                'month_name': f'{future_month}月',
                'seasonal_factor': seasonal_factor,
                'predicted_score': round(predicted_score, 3),
                'trend_direction': '上升' if predicted_score > category_trend['current_score'] else '下降'
            })
        
        # 热点关键词推荐
        hot_keywords = sorted(
            self.trends_db['hot_keywords'],
            key=lambda x: x['growth_rate'],
            reverse=True
        )[:5]
        
        # 整体趋势判断
        avg_prediction = np.mean([p['predicted_score'] for p in predictions])
        if avg_prediction > 0.7:
            trend_outlook = "乐观"
        elif avg_prediction > 0.5:
            trend_outlook = "平稳"
        else:
            trend_outlook = "谨慎"
        
        return {
            'category': category,
            'current_trend_score': category_trend['current_score'],
            '30d_change': category_trend['30d_change'],
            '90d_change': category_trend['90d_change'],
            'predictions': predictions,
            'avg_predicted_score': round(avg_prediction, 3),
            'trend_outlook': trend_outlook,
            'hot_keywords': hot_keywords,
            'seasonal_peak_month': max(seasonal_trend.items(), key=lambda x: x[1])[0] if seasonal_trend else None
        }
    
    def assess_supply_risk(self, product_id: str) -> Dict:
        """
        供应链风险评估
        
        评估产品的供应链稳定性和风险
        """
        product = next(
            (p for p in self.products_db if p['product_id'] == product_id),
            None
        )
        
        if not product:
            return {'error': '产品不存在'}
        
        # 风险因素分析
        supply_stability = product['supply_stability']
        supplier_count = product['supplier_count']
        inventory_days = product['inventory_days']
        return_rate = product['return_rate']
        
        # 风险评分 (0-100, 越低风险越高)
        stability_risk = (1 - supply_stability) * 40
        supplier_risk = max(0, (3 - supplier_count)) * 10  # 少于 3 个供应商有风险
        inventory_risk = min(inventory_days / 30, 2) * 15  # 库存超过 30 天有风险
        return_risk = return_rate * 100
        
        total_risk_score = stability_risk + supplier_risk + inventory_risk + return_risk
        risk_level_score = 100 - total_risk_score
        
        # 风险等级
        if risk_level_score >= 80:
            risk_level = "低风险"
            risk_color = "green"
        elif risk_level_score >= 60:
            risk_level = "中风险"
            risk_color = "yellow"
        elif risk_level_score >= 40:
            risk_level = "高风险"
            risk_color = "orange"
        else:
            risk_level = "极高风险"
            risk_color = "red"
        
        # 风险因素详情
        risk_factors = []
        if supply_stability < 0.7:
            risk_factors.append({
                'factor': '供应稳定性',
                'status': '警告',
                'value': round(supply_stability, 2),
                'suggestion': '寻找备用供应商'
            })
        if supplier_count < 3:
            risk_factors.append({
                'factor': '供应商数量',
                'status': '警告',
                'value': supplier_count,
                'suggestion': '拓展供应商渠道'
            })
        if inventory_days > 30:
            risk_factors.append({
                'factor': '库存周转',
                'status': '警告',
                'value': f'{inventory_days}天',
                'suggestion': '优化库存管理'
            })
        if return_rate > 0.1:
            risk_factors.append({
                'factor': '退货率',
                'status': '警告',
                'value': f'{return_rate*100:.1f}%',
                'suggestion': '提升产品质量'
            })
        
        return {
            'product_id': product_id,
            'product_name': product['product_name'],
            'risk_level': risk_level,
            'risk_level_score': round(risk_level_score, 2),
            'risk_color': risk_color,
            'risk_breakdown': {
                'stability_risk': round(stability_risk, 2),
                'supplier_risk': round(supplier_risk, 2),
                'inventory_risk': round(inventory_risk, 2),
                'return_risk': round(return_risk, 2)
            },
            'risk_factors': risk_factors,
            'supply_stability': supply_stability,
            'supplier_count': supplier_count,
            'inventory_days': inventory_days,
            'recommendations': [rf['suggestion'] for rf in risk_factors] if risk_factors else ['供应链状况良好']
        }
    
    def analyze_profit_margin(self, product_id: str) -> Dict:
        """
        利润空间分析
        
        详细分析产品的利润结构和空间
        """
        product = next(
            (p for p in self.products_db if p['product_id'] == product_id),
            None
        )
        
        if not product:
            return {'error': '产品不存在'}
        
        base_price = product['base_price']
        cost_price = product['cost_price']
        
        # 毛利润
        gross_profit = base_price - cost_price
        gross_margin = gross_profit / base_price if base_price > 0 else 0
        
        # 估算其他成本 (平台佣金、物流、营销等)
        platform_fee = base_price * 0.05  # 5% 平台佣金
        logistics_cost = base_price * 0.08  # 8% 物流成本
        marketing_cost = base_price * 0.10  # 10% 营销成本
        
        # 净利润
        total_costs = cost_price + platform_fee + logistics_cost + marketing_cost
        net_profit = base_price - total_costs
        net_margin = net_profit / base_price if base_price > 0 else 0
        
        # 利润评级
        if net_margin >= 0.30:
            profit_rating = "优秀"
            profit_color = "green"
        elif net_margin >= 0.20:
            profit_rating = "良好"
            profit_color = "blue"
        elif net_margin >= 0.10:
            profit_rating = "一般"
            profit_color = "yellow"
        else:
            profit_rating = "较差"
            profit_color = "red"
        
        # 成本结构
        cost_structure = {
            'product_cost': {
                'amount': round(cost_price, 2),
                'percent': round((cost_price / base_price) * 100, 1)
            },
            'platform_fee': {
                'amount': round(platform_fee, 2),
                'percent': 5.0
            },
            'logistics': {
                'amount': round(logistics_cost, 2),
                'percent': 8.0
            },
            'marketing': {
                'amount': round(marketing_cost, 2),
                'percent': 10.0
            },
            'gross_profit': {
                'amount': round(gross_profit, 2),
                'percent': round(gross_margin * 100, 1)
            },
            'net_profit': {
                'amount': round(net_profit, 2),
                'percent': round(net_margin * 100, 1)
            }
        }
        
        # 盈亏平衡分析
        break_even_units = 1  # 简化计算
        break_even_revenue = base_price * break_even_units
        
        return {
            'product_id': product_id,
            'product_name': product['product_name'],
            'base_price': base_price,
            'cost_price': cost_price,
            'gross_profit': round(gross_profit, 2),
            'gross_margin_percent': round(gross_margin * 100, 2),
            'net_profit': round(net_profit, 2),
            'net_margin_percent': round(net_margin * 100, 2),
            'profit_rating': profit_rating,
            'profit_color': profit_color,
            'cost_structure': cost_structure,
            'break_even_revenue': break_even_revenue,
            'monthly_profit_potential': round(net_profit * product['monthly_sales'], 2),
            'optimization_suggestions': self._get_profit_optimization_suggestions(net_margin, cost_structure)
        }
    
    def _get_profit_optimization_suggestions(self, net_margin: float, cost_structure: Dict) -> List[str]:
        """获取利润优化建议"""
        suggestions = []
        
        if net_margin < 0.20:
            suggestions.append("考虑优化采购成本，寻找更优惠的供应商")
            suggestions.append("评估营销投入产出比，优化广告投放策略")
        
        if cost_structure['product_cost']['percent'] > 50:
            suggestions.append("产品成本占比过高，建议重新谈判采购价格")
        
        if cost_structure['marketing']['percent'] > 15:
            suggestions.append("营销成本偏高，考虑优化渠道组合")
        
        if not suggestions:
            suggestions.append("利润结构健康，保持当前策略")
        
        return suggestions
    
    def generate_decision_report(self, product_id: str) -> Dict:
        """
        生成选品决策报告
        
        综合所有分析维度，生成完整的决策报告
        """
        product = next(
            (p for p in self.products_db if p['product_id'] == product_id),
            None
        )
        
        if not product:
            return {'error': '产品不存在'}
        
        # 获取各项分析结果
        score = self.calculate_product_score(product)
        competitor_analysis = self.analyze_competitors(product_id, product['category'])
        trend_prediction = self.predict_trend(product['category'])
        supply_risk = self.assess_supply_risk(product_id)
        profit_analysis = self.analyze_profit_margin(product_id)
        
        # 综合决策建议
        decision_factors = {
            'positive': [],
            'negative': [],
            'neutral': []
        }
        
        # 正面因素
        if score.overall_score >= 70:
            decision_factors['positive'].append(f"综合评分优秀 ({score.overall_score}分)")
        if score.profit_score >= 70:
            decision_factors['positive'].append(f"利润空间良好 ({score.profit_score}分)")
        if score.trend_score >= 70:
            decision_factors['positive'].append(f"市场趋势向好 ({score.trend_score}分)")
        if supply_risk['risk_level'] in ['低风险', '中风险']:
            decision_factors['positive'].append(f"供应链风险可控 ({supply_risk['risk_level']})")
        
        # 负面因素
        if score.competition_score < 50:
            decision_factors['negative'].append(f"竞争激烈 ({100-score.competition_score:.0f}分)")
        if supply_risk['risk_level'] in ['高风险', '极高风险']:
            decision_factors['negative'].append(f"供应链风险较高 ({supply_risk['risk_level']})")
        if profit_analysis['net_margin_percent'] < 15:
            decision_factors['negative'].append(f"净利润率偏低 ({profit_analysis['net_margin_percent']:.1f}%)")
        
        # 中性因素
        if '平稳' in trend_prediction['trend_outlook']:
            decision_factors['neutral'].append(f"市场趋势平稳")
        
        # 最终决策
        positive_count = len(decision_factors['positive'])
        negative_count = len(decision_factors['negative'])
        
        if positive_count >= 3 and negative_count == 0:
            final_decision = "强烈推荐"
            confidence = "高"
        elif positive_count >= 2 and negative_count <= 1:
            final_decision = "推荐"
            confidence = "中高"
        elif positive_count >= negative_count:
            final_decision = "谨慎推荐"
            confidence = "中"
        else:
            final_decision = "不推荐"
            confidence = "低"
        
        return {
            'product_id': product_id,
            'product_name': product['product_name'],
            'category': product['category'],
            'report_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'overall_score': score.overall_score,
            'score_breakdown': {
                'market_score': score.market_score,
                'competition_score': score.competition_score,
                'trend_score': score.trend_score,
                'supply_risk_score': score.supply_risk_score,
                'profit_score': score.profit_score
            },
            'competitor_analysis': competitor_analysis,
            'trend_prediction': trend_prediction,
            'supply_risk': supply_risk,
            'profit_analysis': profit_analysis,
            'decision_factors': decision_factors,
            'final_decision': final_decision,
            'confidence_level': confidence,
            'recommendation': score.recommendation,
            'key_insights': self._generate_key_insights(score, competitor_analysis, trend_prediction, supply_risk, profit_analysis)
        }
    
    def _generate_key_insights(self, score: ProductScore, competitor: Dict, 
                               trend: Dict, supply: Dict, profit: Dict) -> List[str]:
        """生成关键洞察"""
        insights = []
        
        # 市场洞察
        if score.market_score >= 80:
            insights.append(f"[Market] High market heat, monthly sales potential at {int(score.market_score * 100)} level")
        
        # 竞争洞察
        if competitor.get('estimated_market_share', 0) > 20:
            insights.append(f"[Competition] Occupies {competitor['estimated_market_share']:.1f}% market share, has competitive advantage")
        
        # 趋势洞察
        if trend['trend_outlook'] == '乐观':
            insights.append(f"[Trend] Optimistic trend for next 3 months, predicted score {trend['avg_predicted_score']:.2f}")
        
        # 供应链洞察
        if supply['risk_level'] == '低风险':
            insights.append("[Supply Chain] Stable supply chain, controllable risk")
        
        # 利润洞察
        if profit['net_margin_percent'] >= 25:
            insights.append(f"[Profit] Net profit margin {profit['net_margin_percent']:.1f}%, strong profitability")
        
        if not insights:
            insights.append("Further market research and data analysis needed")
        
        return insights
    
    def get_top_products(self, category: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """
        获取推荐产品 TOP 榜
        
        Args:
            category: 产品类别 (可选)
            limit: 返回数量限制
            
        Returns:
            评分最高的产品列表
        """
        # 筛选类别
        if category:
            products = [p for p in self.products_db if p['category'] == category]
        else:
            products = self.products_db
        
        # 计算所有产品评分
        scored_products = []
        for product in products:
            score = self.calculate_product_score(product)
            scored_products.append({
                'product': product,
                'score': asdict(score)
            })
        
        # 按综合评分排序
        scored_products.sort(key=lambda x: x['score']['overall_score'], reverse=True)
        
        # 返回 TOP N
        return scored_products[:limit]


# 全局服务实例
product_ai_service = ProductAIService()
