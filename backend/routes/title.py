"""
直播间标题优化 API 路由 - LiveMirror
"""

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

from backend.services.title_optimizer import (
    get_service,
    TitleCategory
)

router = APIRouter(prefix="/api/title", tags=["直播间标题优化"])

service = get_service()


# ============== 数据模型 ==============

class TitleGenerateRequest(BaseModel):
    """标题生成请求"""
    product: str = Field(..., description="产品名称/主题", min_length=1)
    category: str = Field(default="general", description="分类")
    count: int = Field(default=5, ge=1, le=10, description="生成数量")
    context: Optional[Dict[str, Any]] = Field(None, description="上下文信息")


class TitleScoreRequest(BaseModel):
    """标题评分请求"""
    title: str = Field(..., description="待评分标题", min_length=1)
    category: str = Field(default="general", description="分类")


class KeywordSuggestionRequest(BaseModel):
    """关键词建议请求"""
    title: str = Field(..., description="当前标题", min_length=1)
    category: str = Field(default="general", description="分类")


class ABTestCreateRequest(BaseModel):
    """A/B 测试创建请求"""
    title_a: str = Field(..., description="标题 A", min_length=1)
    title_b: str = Field(..., description="标题 B", min_length=1)
    category: str = Field(default="general", description="分类")
    duration_hours: int = Field(default=24, ge=1, le=168, description="测试时长（小时）")


class ABTestUpdateRequest(BaseModel):
    """A/B 测试更新请求"""
    variant: str = Field(..., description="变体：a 或 b", pattern="^[ab]$")
    views: int = Field(default=0, ge=0, description="展现量")
    clicks: int = Field(default=0, ge=0, description="点击量")
    conversions: int = Field(default=0, ge=0, description="转化量")


class HistoryAddRequest(BaseModel):
    """历史记录添加请求"""
    title: str = Field(..., description="标题", min_length=1)
    category: str = Field(default="general", description="分类")
    metrics: Optional[Dict[str, Any]] = Field(None, description="效果指标")


# ============== 标题生成接口 ==============

@router.post("/generate", summary="AI 生成标题")
async def generate_titles(request: TitleGenerateRequest):
    """AI 生成吸引人文案"""
    try:
        category = TitleCategory(request.category)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"无效的分类：{e}")
    
    titles = service.generate_titles(
        product=request.product,
        category=category,
        count=request.count,
        context=request.context
    )
    
    return {
        "success": True,
        "data": {
            "titles": titles,
            "count": len(titles),
            "category": request.category
        }
    }


@router.post("/score", summary="标题评分")
async def score_title(request: TitleScoreRequest):
    """标题评分系统（点击率预测）"""
    try:
        category = TitleCategory(request.category)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"无效的分类：{e}")
    
    score = service._calculate_score(request.title, category)
    
    return {
        "success": True,
        "data": {
            "title": request.title,
            "score": score,
            "category": request.category
        }
    }


@router.post("/score/batch", summary="批量标题评分")
async def score_titles_batch(
    titles: List[str] = Body(..., description="标题列表"),
    category: str = Body(default="general", description="分类")
):
    """批量评分多个标题"""
    try:
        category_obj = TitleCategory(category)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"无效的分类：{e}")
    
    results = []
    for title in titles:
        score = service._calculate_score(title, category_obj)
        results.append({
            "title": title,
            "score": score
        })
    
    # 按评分排序
    results.sort(key=lambda x: x["score"]["total"], reverse=True)
    
    return {
        "success": True,
        "data": {
            "results": results,
            "count": len(results),
            "category": category
        }
    }


# ============== 关键词优化接口 ==============

@router.post("/keywords/suggest", summary="获取关键词优化建议")
async def get_keyword_suggestions(request: KeywordSuggestionRequest):
    """关键词优化建议"""
    try:
        category = TitleCategory(request.category)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"无效的分类：{e}")
    
    suggestions = service.get_keyword_suggestions(request.title, category)
    
    return {
        "success": True,
        "data": {
            "title": request.title,
            "suggestions": suggestions,
            "category": request.category
        }
    }


@router.get("/keywords/list", summary="获取关键词库")
async def list_keywords(
    category: Optional[str] = Query(None, description="分类筛选")
):
    """获取关键词库"""
    keywords = service.keywords
    
    if category:
        keywords = {category: keywords.get(category, {})}
    
    return {
        "success": True,
        "data": {
            "keywords": keywords
        }
    }


# ============== A/B 测试接口 ==============

@router.post("/ab-test", summary="创建 A/B 测试")
async def create_ab_test(request: ABTestCreateRequest):
    """创建 A/B 测试"""
    try:
        category = TitleCategory(request.category)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"无效的分类：{e}")
    
    result = service.create_ab_test(
        title_a=request.title_a,
        title_b=request.title_b,
        category=category,
        duration_hours=request.duration_hours
    )
    
    return {
        "success": True,
        "data": result
    }


@router.get("/ab-test/{test_id}", summary="获取 A/B 测试详情")
async def get_ab_test(test_id: str):
    """获取 A/B 测试详情"""
    try:
        test = service.get_ab_test(test_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    return {
        "success": True,
        "data": test
    }


@router.put("/ab-test/{test_id}", summary="更新 A/B 测试指标")
async def update_ab_test(test_id: str, request: ABTestUpdateRequest):
    """更新 A/B 测试指标"""
    try:
        result = service.update_ab_test_metrics(
            test_id=test_id,
            variant=request.variant,
            views=request.views,
            clicks=request.clicks,
            conversions=request.conversions
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    return {
        "success": True,
        "data": result
    }


@router.get("/ab-tests", summary="列出 A/B 测试")
async def list_ab_tests(
    status: Optional[str] = Query(None, description="状态筛选：active/completed")
):
    """列出 A/B 测试"""
    tests = service.list_ab_tests(status)
    
    return {
        "success": True,
        "data": {
            "tests": tests,
            "count": len(tests)
        }
    }


@router.delete("/ab-test/{test_id}", summary="删除 A/B 测试")
async def delete_ab_test(test_id: str):
    """删除 A/B 测试"""
    if test_id not in service.ab_tests:
        raise HTTPException(status_code=404, detail="A/B 测试不存在")
    
    del service.ab_tests[test_id]
    service._save_ab_tests()
    
    return {
        "success": True,
        "message": "A/B 测试已删除"
    }


# ============== 历史记录接口 ==============

@router.post("/history", summary="添加到历史记录")
async def add_to_history(request: HistoryAddRequest):
    """添加到历史记录"""
    try:
        category = TitleCategory(request.category)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"无效的分类：{e}")
    
    service.add_to_history(
        title=request.title,
        category=category,
        metrics=request.metrics
    )
    
    return {
        "success": True,
        "message": "已添加到历史记录"
    }


@router.get("/history", summary="获取历史记录")
async def get_history(
    category: Optional[str] = Query(None, description="分类筛选"),
    days: int = Query(30, ge=1, le=365, description="查询天数"),
    limit: int = Query(100, ge=1, le=1000, description="返回数量限制")
):
    """获取历史记录"""
    category_obj = None
    if category:
        try:
            category_obj = TitleCategory(category)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"无效的分类：{e}")
    
    history = service.get_history(
        category=category_obj,
        days=days,
        limit=limit
    )
    
    return {
        "success": True,
        "data": {
            "history": history,
            "count": len(history),
            "days": days
        }
    }


@router.get("/history/analyze", summary="分析历史记录")
async def analyze_history(
    days: int = Query(30, ge=1, le=365, description="分析天数")
):
    """分析历史记录"""
    analysis = service.analyze_history(days)
    
    return {
        "success": True,
        "data": analysis
    }


# ============== 行业最佳实践接口 ==============

@router.get("/best-practices/{category}", summary="获取行业最佳实践")
async def get_best_practices(category: str):
    """获取行业最佳实践参考"""
    try:
        category_obj = TitleCategory(category)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"无效的分类：{e}")
    
    practices = service.get_industry_best_practices(category_obj)
    
    return {
        "success": True,
        "data": {
            "category": category,
            "practices": practices
        }
    }


@router.get("/best-practices", summary="获取所有行业最佳实践")
async def get_all_best_practices():
    """获取所有行业最佳实践"""
    practices = {}
    for cat in TitleCategory:
        practices[cat.value] = service.get_industry_best_practices(cat)
    
    return {
        "success": True,
        "data": {
            "practices": practices
        }
    }


# ============== 模板管理接口 ==============

@router.get("/templates", summary="获取标题模板列表")
async def get_templates(
    category: Optional[str] = Query(None, description="分类筛选")
):
    """获取标题模板列表"""
    templates = service.templates
    
    if category:
        try:
            cat = TitleCategory(category)
            templates = [t for t in templates if t.category == cat or t.category == TitleCategory.GENERAL]
        except ValueError:
            pass
    
    return {
        "success": True,
        "data": {
            "templates": [
                {
                    "template": t.template,
                    "category": t.category.value,
                    "description": t.description,
                    "effectiveness_score": t.effectiveness_score
                }
                for t in templates
            ],
            "count": len(templates)
        }
    }


@router.post("/templates", summary="添加自定义模板")
async def add_template(
    template: str = Body(..., description="模板内容"),
    category: str = Body(default="general", description="分类"),
    description: str = Body(default="", description="模板描述")
):
    """添加自定义标题模板"""
    try:
        cat = TitleCategory(category)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"无效的分类：{e}")
    
    new_template = service.TitleTemplate(
        template=template,
        category=cat,
        description=description,
        effectiveness_score=0.75  # 新模板初始效果分数
    )
    
    service.templates.append(new_template)
    service._save_templates()
    
    return {
        "success": True,
        "message": "模板添加成功",
        "data": {
            "template": template,
            "category": category,
            "description": description
        }
    }
