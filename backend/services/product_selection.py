"""
供应链选品推荐服务
提供商品热度分析、竞品价格对比、利润率预估、季节性趋势分析等功能
"""

import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class ProductData:
    """商品数据模型"""
    id: str
    name: str
    category: str
    price: float
    cost: float
    supplier_id: str
    supplier_name: str
    supplier_rating: float
    sales_volume: int
    trend_score: float
    seasonality_factor: float
    profit_margin: float
    heat_score: float


@dataclass
class SelectionReport:
    """选品报告模型"""
    product_id: str
    product_name: str
    recommendation_score: float
    heat_analysis: Dict
    price_comparison: Dict
    profit_analysis: Dict
    seasonality_analysis: Dict
    supplier_evaluation: Dict
    summary: str


class ProductSelectionService:
    """选品推荐服务"""
    
    def __init__(self):
        self.products = self._init_sample_products()
    
    def _init_sample_products(self) -> List[Dict]:
        """初始化示例商品数据"""
        return [
            {
                "id": "P001",
                "name": "智能保温杯",
                "category": "家居用品",
                "base_price": 89.0,
                "base_cost": 35.0,
                "supplier_id": "S001",
                "supplier_name": "优质家居供应商",
                "base_sales": 5000,
            },
            {
                "id": "P002",
                "name": "无线蓝牙耳机",
                "category": "数码配件",
                "base_price": 199.0,
                "base_cost": 80.0,
                "supplier_id": "S002",
                "supplier_name": "数码精品厂",
                "base_sales": 12000,
            },
            {
                "id": "P003",
                "name": "便携式榨汁机",
                "category": "小家电",
                "base_price": 159.0,
                "base_cost": 65.0,
                "supplier_id": "S003",
                "supplier_name": "家电制造商",
                "base_sales": 8000,
            },
            {
                "id": "P004",
                "name": "瑜伽垫",
                "category": "运动健身",
                "base_price": 79.0,
                "base_cost": 25.0,
                "supplier_id": "S004",
                "supplier_name": "运动用品厂",
                "base_sales": 6500,
            },
            {
                "id": "P005",
                "name": "LED 化妆镜",
                "category": "美妆工具",
                "base_price": 129.0,
                "base_cost": 45.0,
                "supplier_id": "S005",
                "supplier_name": "美妆供应商",
                "base_sales": 9500,
            },
        ]
    
    def analyze_product_heat(self, product_id: str) -> Dict:
        """
        商品热度分析（全网数据）
        返回热度分数、搜索趋势、社交媒体讨论度等
        """
        product = next((p for p in self.products if p["id"] == product_id), None)
        if not product:
            return {"error": "Product not found"}
        
        # 模拟全网热度数据
        heat_data = {
            "heat_score": round(random.uniform(70, 95), 2),
            "search_trend": {
                "current_week": random.randint(8000, 15000),
                "last_week": random.randint(7000, 13000),
                "growth_rate": round(random.uniform(-5, 25), 2),
            },
            "social_media": {
                "mentions": random.randint(1000, 5000),
                "engagement_rate": round(random.uniform(2.5, 8.5), 2),
                "sentiment_score": round(random.uniform(0.6, 0.95), 2),
            },
            "platform_distribution": {
                "douyin": round(random.uniform(30, 50), 2),
                "xiaohongshu": round(random.uniform(20, 35), 2),
                "taobao": round(random.uniform(15, 30), 2),
                "others": round(random.uniform(5, 15), 2),
            },
            "category_ranking": random.randint(5, 50),
            "trend_status": "rising" if random.random() > 0.3 else "stable",
        }
        
        return heat_data
    
    def compare_competitor_prices(self, product_id: str) -> Dict:
        """
        竞品价格对比
        分析同类商品的价格区间、竞争优势等
        """
        product = next((p for p in self.products if p["id"] == product_id), None)
        if not product:
            return {"error": "Product not found"}
        
        base_price = product["base_price"]
        
        # 模拟竞品价格数据
        competitor_prices = [
            round(base_price * random.uniform(0.85, 1.15), 2)
            for _ in range(5)
        ]
        
        price_analysis = {
            "our_price": base_price,
            "competitor_prices": sorted(competitor_prices),
            "market_avg_price": round(sum(competitor_prices) / len(competitor_prices), 2),
            "price_position": "below_average" if base_price < sum(competitor_prices) / len(competitor_prices) else "above_average",
            "price_advantage": round(((sum(competitor_prices) / len(competitor_prices)) - base_price) / base_price * 100, 2),
            "lowest_competitor": min(competitor_prices),
            "highest_competitor": max(competitor_prices),
            "price_range": {
                "min": min(competitor_prices),
                "max": max(competitor_prices),
            },
        }
        
        return price_analysis
    
    def calculate_profit_margin(self, product_id: str) -> Dict:
        """
        利润率预估
        计算毛利润、净利润、ROI 等指标
        """
        product = next((p for p in self.products if p["id"] == product_id), None)
        if not product:
            return {"error": "Product not found"}
        
        price = product["base_price"]
        cost = product["base_cost"]
        
        # 模拟额外成本
        platform_fee = round(price * 0.05, 2)  # 平台佣金 5%
        shipping_cost = round(random.uniform(5, 15), 2)
        marketing_cost = round(random.uniform(3, 10), 2)
        
        gross_profit = price - cost
        gross_margin = round((gross_profit / price) * 100, 2)
        
        total_cost = cost + platform_fee + shipping_cost + marketing_cost
        net_profit = price - total_cost
        net_margin = round((net_profit / price) * 100, 2)
        
        roi = round((net_profit / total_cost) * 100, 2) if total_cost > 0 else 0
        
        profit_analysis = {
            "selling_price": price,
            "product_cost": cost,
            "platform_fee": platform_fee,
            "shipping_cost": shipping_cost,
            "marketing_cost": marketing_cost,
            "total_cost": round(total_cost, 2),
            "gross_profit": round(gross_profit, 2),
            "gross_margin_percent": gross_margin,
            "net_profit": round(net_profit, 2),
            "net_margin_percent": net_margin,
            "roi_percent": roi,
            "break_even_units": int(total_cost / (price - cost)) + 1 if price > cost else -1,
            "profitability_rating": "high" if net_margin > 30 else "medium" if net_margin > 15 else "low",
        }
        
        return profit_analysis
    
    def analyze_seasonality(self, product_id: str) -> Dict:
        """
        季节性趋势分析
        分析商品在不同季节/月份的销售表现
        """
        product = next((p for p in self.products if p["id"] == product_id), None)
        if not product:
            return {"error": "Product not found"}
        
        # 模拟季节性数据
        months = ["1 月", "2 月", "3 月", "4 月", "5 月", "6 月", 
                  "7 月", "8 月", "9 月", "10 月", "11 月", "12 月"]
        
        # 根据类别生成不同的季节模式
        category = product["category"]
        if category == "运动健身":
            base_factors = [0.7, 0.8, 1.0, 1.1, 1.2, 1.0, 0.9, 0.9, 1.1, 1.0, 0.9, 0.8]
        elif category == "小家电":
            base_factors = [1.2, 1.1, 1.0, 0.9, 0.9, 0.8, 0.8, 0.9, 1.0, 1.1, 1.3, 1.4]
        elif category == "数码配件":
            base_factors = [1.0, 0.9, 1.0, 1.0, 1.1, 1.0, 0.9, 1.0, 1.1, 1.2, 1.4, 1.3]
        else:
            base_factors = [1.0] * 12
        
        # 添加一些随机波动
        seasonal_factors = [round(f * random.uniform(0.9, 1.1), 2) for f in base_factors]
        
        peak_month_idx = seasonal_factors.index(max(seasonal_factors))
        low_month_idx = seasonal_factors.index(min(seasonal_factors))
        
        seasonality_analysis = {
            "monthly_factors": dict(zip(months, seasonal_factors)),
            "peak_season": months[peak_month_idx],
            "low_season": months[low_month_idx],
            "seasonality_strength": round(max(seasonal_factors) - min(seasonal_factors), 2),
            "current_month_factor": seasonal_factors[datetime.now().month - 1],
            "recommendation": "good_time" if seasonal_factors[datetime.now().month - 1] > 1.0 else "wait_for_peak",
            "yearly_trend": "stable",
            "next_peak": months[(peak_month_idx + 1) % 12] if peak_month_idx != 11 else months[0],
        }
        
        return seasonality_analysis
    
    def evaluate_supplier(self, supplier_id: str) -> Dict:
        """
        供应商评分系统
        评估供应商的综合能力
        """
        # 查找该供应商的所有产品
        supplier_products = [p for p in self.products if p["supplier_id"] == supplier_id]
        
        if not supplier_products:
            # 生成示例供应商数据
            supplier_products = [{"supplier_id": supplier_id}]
        
        # 模拟供应商评分
        supplier_evaluation = {
            "supplier_id": supplier_id,
            "supplier_name": supplier_products[0].get("supplier_name", "未知供应商"),
            "overall_rating": round(random.uniform(3.5, 5.0), 2),
            "quality_score": round(random.uniform(3.0, 5.0), 2),
            "delivery_score": round(random.uniform(3.5, 5.0), 2),
            "service_score": round(random.uniform(3.5, 5.0), 2),
            "price_competitiveness": round(random.uniform(3.0, 5.0), 2),
            "response_time_hours": random.randint(1, 24),
            "defect_rate_percent": round(random.uniform(0.1, 3.0), 2),
            "on_time_delivery_rate": round(random.uniform(85, 99), 2),
            "cooperation_years": random.randint(1, 10),
            "total_products": len(supplier_products),
            "certification": ["ISO9001", "CE", "RoHS"] if random.random() > 0.3 else ["ISO9001"],
            "risk_level": "low" if random.random() > 0.7 else "medium",
        }
        
        return supplier_evaluation
    
    def generate_selection_report(self, product_id: str) -> SelectionReport:
        """
        生成选品报告
        综合所有分析维度，生成完整的选品推荐报告
        """
        product = next((p for p in self.products if p["id"] == product_id), None)
        if not product:
            return SelectionReport(
                product_id=product_id,
                product_name="Unknown",
                recommendation_score=0,
                heat_analysis={},
                price_comparison={},
                profit_analysis={},
                seasonality_analysis={},
                supplier_evaluation={},
                summary="Product not found"
            )
        
        # 获取各项分析数据
        heat_analysis = self.analyze_product_heat(product_id)
        price_comparison = self.compare_competitor_prices(product_id)
        profit_analysis = self.calculate_profit_margin(product_id)
        seasonality_analysis = self.analyze_seasonality(product_id)
        supplier_evaluation = self.evaluate_supplier(product["supplier_id"])
        
        # 计算综合推荐分数
        heat_score = heat_analysis.get("heat_score", 50)
        profit_score = profit_analysis.get("net_margin_percent", 0) * 2
        seasonality_score = seasonality_analysis.get("current_month_factor", 1.0) * 50
        supplier_score = supplier_evaluation.get("overall_rating", 3.0) * 10
        price_advantage = price_comparison.get("price_advantage", 0)
        
        recommendation_score = round(
            (heat_score * 0.3 + 
             profit_score * 0.25 + 
             seasonality_score * 0.2 + 
             supplier_score * 0.15 +
             min(price_advantage, 20) * 0.1),
            2
        )
        
        # 生成总结
        if recommendation_score >= 80:
            summary = f"强烈推荐！{product['name']}在当前市场表现优异，利润空间充足，供应商可靠。"
        elif recommendation_score >= 60:
            summary = f"推荐考虑。{product['name']}具有不错的市场潜力，建议关注价格竞争力和季节因素。"
        else:
            summary = f"谨慎选择。{product['name']}当前市场表现一般，建议进一步优化或寻找替代品。"
        
        return SelectionReport(
            product_id=product_id,
            product_name=product["name"],
            recommendation_score=recommendation_score,
            heat_analysis=heat_analysis,
            price_comparison=price_comparison,
            profit_analysis=profit_analysis,
            seasonality_analysis=seasonality_analysis,
            supplier_evaluation=supplier_evaluation,
            summary=summary
        )
    
    def get_recommendations(self, min_score: float = 60.0, limit: int = 5) -> List[SelectionReport]:
        """
        获取推荐商品列表
        返回所有商品中推荐分数高于阈值的前 N 个
        """
        reports = []
        for product in self.products:
            report = self.generate_selection_report(product["id"])
            if report.recommendation_score >= min_score:
                reports.append(report)
        
        # 按推荐分数排序
        reports.sort(key=lambda x: x.recommendation_score, reverse=True)
        return reports[:limit]
    
    def get_all_products(self) -> List[Dict]:
        """获取所有商品列表"""
        return self.products


# 单例实例
_service_instance = None

def get_service() -> ProductSelectionService:
    """获取选品服务单例"""
    global _service_instance
    if _service_instance is None:
        _service_instance = ProductSelectionService()
    return _service_instance
