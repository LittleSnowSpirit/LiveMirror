"""
选品推荐 API 接口
提供商品热度分析、价格对比、利润率计算等 HTTP 接口
"""

from flask import Blueprint, jsonify, request
from typing import Dict, Any
from ..services.product_selection import get_service, ProductSelectionService

# 创建 Blueprint
product_bp = Blueprint('product', __name__, url_prefix='/api/product')


def _json_response(data: Any, status: int = 200) -> tuple:
    """统一的 JSON 响应格式"""
    return jsonify({
        "code": status,
        "data": data,
        "message": "success" if status == 200 else "error"
    }), status


@product_bp.route('/list', methods=['GET'])
def get_product_list():
    """
    获取商品列表
    GET /api/product/list
    """
    try:
        service = get_service()
        products = service.get_all_products()
        return _json_response(products)
    except Exception as e:
        return _json_response({"error": str(e)}, 500)


@product_bp.route('/<product_id>/heat', methods=['GET'])
def get_product_heat(product_id: str):
    """
    获取商品热度分析
    GET /api/product/{product_id}/heat
    """
    try:
        service = get_service()
        heat_data = service.analyze_product_heat(product_id)
        
        if "error" in heat_data:
            return _json_response(heat_data, 404)
        
        return _json_response(heat_data)
    except Exception as e:
        return _json_response({"error": str(e)}, 500)


@product_bp.route('/<product_id>/price-comparison', methods=['GET'])
def get_price_comparison(product_id: str):
    """
    获取竞品价格对比
    GET /api/product/{product_id}/price-comparison
    """
    try:
        service = get_service()
        price_data = service.compare_competitor_prices(product_id)
        
        if "error" in price_data:
            return _json_response(price_data, 404)
        
        return _json_response(price_data)
    except Exception as e:
        return _json_response({"error": str(e)}, 500)


@product_bp.route('/<product_id>/profit', methods=['GET'])
def get_profit_margin(product_id: str):
    """
    获取利润率分析
    GET /api/product/{product_id}/profit
    """
    try:
        service = get_service()
        profit_data = service.calculate_profit_margin(product_id)
        
        if "error" in profit_data:
            return _json_response(profit_data, 404)
        
        return _json_response(profit_data)
    except Exception as e:
        return _json_response({"error": str(e)}, 500)


@product_bp.route('/<product_id>/seasonality', methods=['GET'])
def get_seasonality(product_id: str):
    """
    获取季节性趋势分析
    GET /api/product/{product_id}/seasonality
    """
    try:
        service = get_service()
        seasonality_data = service.analyze_seasonality(product_id)
        
        if "error" in seasonality_data:
            return _json_response(seasonality_data, 404)
        
        return _json_response(seasonality_data)
    except Exception as e:
        return _json_response({"error": str(e)}, 500)


@product_bp.route('/supplier/<supplier_id>', methods=['GET'])
def get_supplier_evaluation(supplier_id: str):
    """
    获取供应商评分
    GET /api/product/supplier/{supplier_id}
    """
    try:
        service = get_service()
        supplier_data = service.evaluate_supplier(supplier_id)
        
        if "error" in supplier_data:
            return _json_response(supplier_data, 404)
        
        return _json_response(supplier_data)
    except Exception as e:
        return _json_response({"error": str(e)}, 500)


@product_bp.route('/<product_id>/report', methods=['GET'])
def get_selection_report(product_id: str):
    """
    获取选品报告
    GET /api/product/{product_id}/report
    """
    try:
        service = get_service()
        report = service.generate_selection_report(product_id)
        
        # 将 dataclass 转换为字典
        from dataclasses import asdict
        report_dict = asdict(report)
        
        return _json_response(report_dict)
    except Exception as e:
        return _json_response({"error": str(e)}, 500)


@product_bp.route('/recommendations', methods=['GET'])
def get_recommendations():
    """
    获取推荐商品列表
    GET /api/product/recommendations?min_score=60&limit=5
    """
    try:
        min_score = float(request.args.get('min_score', 60.0))
        limit = int(request.args.get('limit', 5))
        
        service = get_service()
        reports = service.get_recommendations(min_score=min_score, limit=limit)
        
        from dataclasses import asdict
        reports_list = [asdict(report) for report in reports]
        
        return _json_response(reports_list)
    except Exception as e:
        return _json_response({"error": str(e)}, 500)


@product_bp.route('/batch-analysis', methods=['POST'])
def batch_analysis():
    """
    批量分析商品
    POST /api/product/batch-analysis
    Body: {"product_ids": ["P001", "P002", ...]}
    """
    try:
        data = request.get_json()
        product_ids = data.get('product_ids', [])
        
        if not product_ids:
            return _json_response({"error": "product_ids is required"}, 400)
        
        service = get_service()
        results = []
        
        for product_id in product_ids:
            report = service.generate_selection_report(product_id)
            from dataclasses import asdict
            results.append(asdict(report))
        
        return _json_response(results)
    except Exception as e:
        return _json_response({"error": str(e)}, 500)


# 注册 Blueprint 的辅助函数
def register_routes(app):
    """将路由注册到 Flask 应用"""
    app.register_blueprint(product_bp)
