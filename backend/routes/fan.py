"""
粉丝画像分析 API 路由
提供粉丝特征分析的 HTTP 接口
"""

from flask import Blueprint, jsonify, request
from backend.services.fan_profile import FanProfileService

# 创建蓝图
fan_bp = Blueprint('fan', __name__, url_prefix='/api/fan')

# 初始化服务
fan_service = FanProfileService()


@fan_bp.route('/profile/basic', methods=['GET'])
def get_basic_profile():
    """
    获取粉丝基础画像
    包含：年龄分布、性别比例、地区分布
    
    Returns:
        JSON: 基础画像数据
    """
    try:
        data = fan_service.get_basic_profile()
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@fan_bp.route('/profile/activity', methods=['GET'])
def get_activity_levels():
    """
    获取粉丝活跃度分层
    分为：高活跃、中活跃、低活跃、沉睡粉丝
    
    Returns:
        JSON: 活跃度分层数据
    """
    try:
        data = fan_service.get_activity_levels()
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@fan_bp.route('/profile/interests', methods=['GET'])
def get_interest_tags():
    """
    获取粉丝兴趣标签分布
    
    Returns:
        JSON: 兴趣标签数据
    """
    try:
        data = fan_service.get_interest_tags()
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@fan_bp.route('/profile/ltv', methods=['GET'])
def calculate_ltv():
    """
    计算粉丝生命周期价值 (LTV)
    
    Query Parameters:
        fan_id (int, optional): 指定粉丝 ID，不传则返回整体分布
    
    Returns:
        JSON: LTV 分析数据
    """
    try:
        fan_id = request.args.get('fan_id', type=int)
        data = fan_service.calculate_ltv(fan_id=fan_id)
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@fan_bp.route('/profile/churn', methods=['GET'])
def get_churn_warning():
    """
    获取粉丝流失预警
    
    Returns:
        JSON: 流失预警数据
    """
    try:
        data = fan_service.get_churn_warning()
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@fan_bp.route('/profile/growth', methods=['GET'])
def get_growth_trend():
    """
    获取粉丝增长趋势
    
    Returns:
        JSON: 增长趋势数据
    """
    try:
        data = fan_service.get_growth_trend()
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@fan_bp.route('/profile/full', methods=['GET'])
def get_full_profile():
    """
    获取完整的粉丝画像报告
    包含所有分析维度
    
    Returns:
        JSON: 完整画像报告
    """
    try:
        data = fan_service.get_full_profile_report()
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@fan_bp.route('/test', methods=['GET'])
def run_tests():
    """
    运行测试并返回结果
    
    Returns:
        JSON: 测试结果
    """
    try:
        from backend.services.fan_profile import run_tests as run_service_tests
        import io
        import sys
        
        # 捕获测试输出
        old_stdout = sys.stdout
        sys.stdout = buffer = io.StringIO()
        
        result = run_service_tests()
        
        sys.stdout = old_stdout
        output = buffer.getvalue()
        
        return jsonify({
            'success': True,
            'result': result,
            'output': output
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# 注册蓝图到主应用
def register_routes(app):
    """
    将粉丝画像路由注册到 Flask 应用
    
    Args:
        app: Flask 应用实例
    """
    app.register_blueprint(fan_bp)
