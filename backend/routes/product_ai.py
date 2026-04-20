"""
LiveMirror Product AI Routes
智能选品 API 接口
"""

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
import sys
import os

# 添加父目录到路径以导入服务
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from services.product_ai import product_ai_service, ProductAIService

router = APIRouter(prefix='/api/product-ai', tags=['product-ai'])


# ==================== Request Models ====================

class ProductScoreRequest(BaseModel):
    """产品评分请求"""
    product_id: str = Field(..., description="产品 ID")


class CompetitorAnalysisRequest(BaseModel):
    """竞品分析请求"""
    product_id: str = Field(..., description="产品 ID")
    category: str = Field(..., description="产品类别")


class TrendPredictionRequest(BaseModel):
    """趋势预测请求"""
    category: str = Field(..., description="产品类别")
    months_ahead: int = Field(default=3, description="预测月数", ge=1, le=12)


class SupplyRiskRequest(BaseModel):
    """供应链风险评估请求"""
    product_id: str = Field(..., description="产品 ID")


class ProfitAnalysisRequest(BaseModel):
    """利润分析请求"""
    product_id: str = Field(..., description="产品 ID")


class DecisionReportRequest(BaseModel):
    """决策报告请求"""
    product_id: str = Field(..., description="产品 ID")


class TopProductsRequest(BaseModel):
    """TOP 产品请求"""
    category: Optional[str] = Field(None, description="产品类别")
    limit: int = Field(default=10, description="返回数量", ge=1, le=50)


# ==================== Response Models ====================

class ProductAIResponse(BaseModel):
    """产品 AI 响应"""
    success: bool
    data: Dict[str, Any]
    timestamp: str
    message: str = ""


class ProductScoreData(BaseModel):
    """产品评分数据"""
    product_id: str
    product_name: str
    category: str
    overall_score: float
    market_score: float
    competition_score: float
    trend_score: float
    supply_risk_score: float
    profit_score: float
    recommendation: str
    analysis_date: str


# ==================== API Endpoints ====================

@router.get('/health', response_model=ProductAIResponse)
async def health_check():
    """健康检查"""
    return ProductAIResponse(
        success=True,
        data={'status': 'healthy', 'service': 'product-ai'},
        timestamp=datetime.now().isoformat(),
        message="智能选品服务运行正常"
    )


@router.post('/score/product', response_model=ProductAIResponse)
async def score_product(request: ProductScoreRequest):
    """
    产品评分
    
    对单个产品进行多维度 AI 评分
    """
    try:
        product = next(
            (p for p in product_ai_service.products_db if p['product_id'] == request.product_id),
            None
        )
        
        if not product:
            raise HTTPException(status_code=404, detail=f"产品 {request.product_id} 不存在")
        
        score = product_ai_service.calculate_product_score(product)
        
        return ProductAIResponse(
            success=True,
            data={
                'product_id': score.product_id,
                'product_name': score.product_name,
                'category': score.category,
                'overall_score': score.overall_score,
                'market_score': score.market_score,
                'competition_score': score.competition_score,
                'trend_score': score.trend_score,
                'supply_risk_score': score.supply_risk_score,
                'profit_score': score.profit_score,
                'recommendation': score.recommendation,
                'analysis_date': score.analysis_date
            },
            timestamp=datetime.now().isoformat(),
            message=f"产品评分完成：{score.recommendation} ({score.overall_score}分)"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/analyze/competitors', response_model=ProductAIResponse)
async def analyze_competitors(request: CompetitorAnalysisRequest):
    """
    竞品选品分析
    
    分析同类产品的竞争情况
    """
    try:
        result = product_ai_service.analyze_competitors(
            product_id=request.product_id,
            category=request.category
        )
        
        if 'error' in result:
            raise HTTPException(status_code=404, detail=result['error'])
        
        return ProductAIResponse(
            success=True,
            data=result,
            timestamp=datetime.now().isoformat(),
            message=f"竞品分析完成：共{result['total_competitors']}个竞争对手"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/predict/trend', response_model=ProductAIResponse)
async def predict_trend(request: TrendPredictionRequest):
    """
    趋势预测
    
    预测产品类别的未来趋势 (季节性/热点)
    """
    try:
        result = product_ai_service.predict_trend(
            category=request.category,
            months_ahead=request.months_ahead
        )
        
        return ProductAIResponse(
            success=True,
            data=result,
            timestamp=datetime.now().isoformat(),
            message=f"趋势预测完成：未来趋势{result['trend_outlook']}"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/assess/supply-risk', response_model=ProductAIResponse)
async def assess_supply_risk(request: SupplyRiskRequest):
    """
    供应链风险评估
    
    评估产品的供应链稳定性和风险
    """
    try:
        result = product_ai_service.assess_supply_risk(request.product_id)
        
        if 'error' in result:
            raise HTTPException(status_code=404, detail=result['error'])
        
        return ProductAIResponse(
            success=True,
            data=result,
            timestamp=datetime.now().isoformat(),
            message=f"供应链风险评估完成：{result['risk_level']}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/analyze/profit', response_model=ProductAIResponse)
async def analyze_profit(request: ProfitAnalysisRequest):
    """
    利润空间分析
    
    详细分析产品的利润结构和空间
    """
    try:
        result = product_ai_service.analyze_profit_margin(request.product_id)
        
        if 'error' in result:
            raise HTTPException(status_code=404, detail=result['error'])
        
        return ProductAIResponse(
            success=True,
            data=result,
            timestamp=datetime.now().isoformat(),
            message=f"利润分析完成：净利润率{result['net_margin_percent']:.1f}%"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/report/decision', response_model=ProductAIResponse)
async def generate_decision_report(request: DecisionReportRequest):
    """
    选品决策报告
    
    生成完整的选品决策报告，包含所有分析维度
    """
    try:
        result = product_ai_service.generate_decision_report(request.product_id)
        
        if 'error' in result:
            raise HTTPException(status_code=404, detail=result['error'])
        
        return ProductAIResponse(
            success=True,
            data=result,
            timestamp=datetime.now().isoformat(),
            message=f"决策报告生成完成：{result['final_decision']}"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post('/top/products', response_model=ProductAIResponse)
async def get_top_products(request: TopProductsRequest):
    """
    获取推荐产品 TOP 榜
    
    获取评分最高的产品列表
    """
    try:
        result = product_ai_service.get_top_products(
            category=request.category,
            limit=request.limit
        )
        
        return ProductAIResponse(
            success=True,
            data={
                'category': request.category or '全部',
                'total_count': len(result),
                'products': result
            },
            timestamp=datetime.now().isoformat(),
            message=f"获取 TOP {len(result)} 产品成功"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/categories', response_model=ProductAIResponse)
async def get_categories():
    """
    获取所有产品类别
    """
    try:
        categories = list(set([p['category'] for p in product_ai_service.products_db]))
        
        return ProductAIResponse(
            success=True,
            data={'categories': sorted(categories)},
            timestamp=datetime.now().isoformat(),
            message=f"共{len(categories)}个产品类别"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/product/{product_id}', response_model=ProductAIResponse)
async def get_product_detail(product_id: str):
    """
    获取产品详情
    
    获取单个产品的完整信息
    """
    try:
        product = next(
            (p for p in product_ai_service.products_db if p['product_id'] == product_id),
            None
        )
        
        if not product:
            raise HTTPException(status_code=404, detail=f"产品 {product_id} 不存在")
        
        return ProductAIResponse(
            success=True,
            data=product,
            timestamp=datetime.now().isoformat(),
            message=f"获取产品 {product['product_name']} 详情成功"
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get('/batch/score', response_model=ProductAIResponse)
async def batch_score_products(
    product_ids: str = Query(..., description="产品 ID 列表，逗号分隔"),
    category: Optional[str] = Query(None, description="产品类别")
):
    """
    批量产品评分
    
    对多个产品进行批量评分
    """
    try:
        ids = [id.strip() for id in product_ids.split(',')]
        
        results = []
        for product_id in ids:
            product = next(
                (p for p in product_ai_service.products_db if p['product_id'] == product_id),
                None
            )
            
            if product:
                score = product_ai_service.calculate_product_score(product)
                results.append({
                    'product_id': score.product_id,
                    'product_name': score.product_name,
                    'overall_score': score.overall_score,
                    'recommendation': score.recommendation
                })
        
        return ProductAIResponse(
            success=True,
            data={
                'total_requested': len(ids),
                'total_scored': len(results),
                'results': results
            },
            timestamp=datetime.now().isoformat(),
            message=f"批量评分完成：{len(results)}/{len(ids)} 个产品"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
