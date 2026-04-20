"""
LiveMirror Prediction Routes
直播预测 API 接口
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import sys
import os

# 添加父目录到路径以导入服务
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from services.prediction import prediction_service, PredictionService

router = APIRouter(prefix='/api/prediction', tags=['prediction'])


# ==================== Request Models ====================

class GMVPredictionRequest(BaseModel):
    """GMV 预测请求"""
    expected_viewers: int = Field(..., description="预期观看人数", ge=0)
    confidence: float = Field(default=0.85, description="置信度", ge=0.5, le=0.99)
    historical_gmv: Optional[List[int]] = Field(None, description="历史 GMV 数据")


class ViewersPredictionRequest(BaseModel):
    """观看人数预测请求"""
    day_of_week: int = Field(..., description="星期几 (0-6)", ge=0, le=6)
    hour: int = Field(..., description="小时 (0-23)", ge=0, le=23)


class ConversionRateRequest(BaseModel):
    """转化率预测请求"""
    product_category: str = Field(default='general', description="产品类别")
    price_range: str = Field(default='medium', description="价格区间")


class TimeRecommendationRequest(BaseModel):
    """时间推荐请求"""
    target_audience: str = Field(default='general', description="目标受众")
    duration_minutes: int = Field(default=120, description="预计时长 (分钟)", ge=30, le=480)


class AccuracyEvaluationRequest(BaseModel):
    """准确度评估请求"""
    predictions: List[Dict[str, Any]] = Field(..., description="预测值列表")
    actuals: List[Dict[str, Any]] = Field(..., description="实际值列表")


# ==================== Response Models ====================

class PredictionResponse(BaseModel):
    """预测响应"""
    success: bool
    data: Dict[str, Any]
    timestamp: str
    message: str = ""


# ==================== API Endpoints ====================

@router.get('/health', response_model=PredictionResponse)
async def health_check():
    """健康检查"""
    return PredictionResponse(
        success=True,
        data={'status': 'healthy', 'service': 'prediction'},
        timestamp=datetime.now().isoformat(),
        message="预测服务运行正常"
    )


@router.post('/predict/gmv', response_model=PredictionResponse)
async def predict_gmv(request: GMVPredictionRequest):
    """
    GMV 预测
    
    基于预期观看人数和历史数据预测 GMV
    """
    try:
        result = prediction_service.predict_gmv(
            expected_viewers=request.expected_viewers,
            historical_gmv=request.historical_gmv,
            confidence=request.confidence
        )
        
        return PredictionResponse(
            success=True,
            data=result,
            timestamp=datetime.now().isoformat(),
            message=f"预测 GMV: ¥{result['predicted_gmv']:,}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/predict/viewers', response_model=PredictionResponse)
async def predict_viewers(request: ViewersPredictionRequest):
    """
    观看人数预测
    
    基于时间段预测观看人数
    """
    try:
        result = prediction_service.predict_viewers(
            day_of_week=request.day_of_week,
            hour=request.hour
        )
        
        return PredictionResponse(
            success=True,
            data=result,
            timestamp=datetime.now().isoformat(),
            message=f"预测观看人数：{result['predicted_viewers']:,} 人"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/predict/conversion', response_model=PredictionResponse)
async def predict_conversion_rate(request: ConversionRateRequest):
    """
    转化率预测
    
    基于产品类别和价格区间预测转化率
    """
    try:
        result = prediction_service.predict_conversion_rate(
            product_category=request.product_category,
            price_range=request.price_range
        )
        
        return PredictionResponse(
            success=True,
            data=result,
            timestamp=datetime.now().isoformat(),
            message=f"预测转化率：{result['predicted_conversion_rate_percent']}%"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/recommend/time', response_model=PredictionResponse)
async def recommend_best_time(request: TimeRecommendationRequest):
    """
    最佳直播时间推荐
    
    基于历史数据推荐最佳直播时间
    """
    try:
        result = prediction_service.recommend_best_time(
            target_audience=request.target_audience,
            duration_minutes=request.duration_minutes
        )
        
        return PredictionResponse(
            success=True,
            data=result,
            timestamp=datetime.now().isoformat(),
            message=f"推荐时间：{result['recommended_time_str']}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/evaluate/accuracy', response_model=PredictionResponse)
async def evaluate_accuracy(request: AccuracyEvaluationRequest):
    """
    预测准确度评估
    
    评估预测模型的准确度
    """
    try:
        result = prediction_service.evaluate_accuracy(
            predictions=request.predictions,
            actuals=request.actuals
        )
        
        if 'error' in result:
            return PredictionResponse(
                success=False,
                data=result,
                timestamp=datetime.now().isoformat(),
                message=result['error']
            )
        
        return PredictionResponse(
            success=True,
            data=result,
            timestamp=datetime.now().isoformat(),
            message=f"整体准确度：{result.get('overall_accuracy', 0)}% ({result.get('rating', 'N/A')})"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/trend', response_model=PredictionResponse)
async def get_trend_data(
    days: int = Query(default=30, ge=7, le=90, description="天数")
):
    """
    获取趋势数据
    
    用于可视化图表的历史趋势数据
    """
    try:
        result = prediction_service.get_trend_data(days=days)
        
        return PredictionResponse(
            success=True,
            data=result,
            timestamp=datetime.now().isoformat(),
            message=f"获取{days}天趋势数据"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/sample', response_model=PredictionResponse)
async def generate_sample():
    """
    生成示例预测
    
    用于测试和演示的完整预测样本
    """
    try:
        result = prediction_service.generate_sample_prediction()
        
        return PredictionResponse(
            success=True,
            data=result,
            timestamp=datetime.now().isoformat(),
            message="示例预测生成成功"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/data/historical', response_model=PredictionResponse)
async def get_historical_data(
    limit: int = Query(default=30, ge=1, le=365, description="数据条数")
):
    """
    获取历史数据
    
    用于分析和训练的历史直播数据
    """
    try:
        data = prediction_service.historical_data[:limit]
        
        return PredictionResponse(
            success=True,
            data={
                'count': len(data),
                'records': data
            },
            timestamp=datetime.now().isoformat(),
            message=f"获取{len(data)}条历史数据"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ==================== 综合预测接口 ====================

@router.post('/predict/all', response_model=PredictionResponse)
async def predict_all(
    day_of_week: int = Field(..., description="星期几"),
    hour: int = Field(..., description="小时"),
    product_category: str = Field(default='general', description="产品类别"),
    price_range: str = Field(default='medium', description="价格区间")
):
    """
    综合预测
    
    一次性获取所有预测结果
    """
    try:
        # 预测观看人数
        viewers_result = prediction_service.predict_viewers(day_of_week, hour)
        
        # 预测 GMV
        gmv_result = prediction_service.predict_gmv(viewers_result['predicted_viewers'])
        
        # 预测转化率
        conversion_result = prediction_service.predict_conversion_rate(
            product_category, price_range
        )
        
        # 时间推荐
        time_result = prediction_service.recommend_best_time()
        
        return PredictionResponse(
            success=True,
            data={
                'viewers': viewers_result,
                'gmv': gmv_result,
                'conversion': conversion_result,
                'time_recommendation': time_result,
                'input_params': {
                    'day_of_week': day_of_week,
                    'hour': hour,
                    'product_category': product_category,
                    'price_range': price_range
                }
            },
            timestamp=datetime.now().isoformat(),
            message="综合预测完成"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
