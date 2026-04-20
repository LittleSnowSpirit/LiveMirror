"""
敏感词管理 API 路由 - LiveMirror
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime

from backend.services.sensitive_words import (
    get_service,
    SensitiveWordCategory,
    SeverityLevel
)

router = APIRouter(prefix="/api/sensitive", tags=["敏感词管理"])

service = get_service()


# ============== 数据模型 ==============

class WordCreateRequest(BaseModel):
    """创建敏感词请求"""
    word: str = Field(..., description="敏感词内容", min_length=1)
    severity: str = Field(..., description="严重程度：warning/serious/banned")
    category: str = Field(default="general", description="分类")
    replacement: Optional[str] = Field(None, description="替换建议")
    reason: str = Field(default="", description="添加原因")


class WordUpdateRequest(BaseModel):
    """更新敏感词请求"""
    severity: Optional[str] = Field(None, description="严重程度")
    category: Optional[str] = Field(None, description="分类")
    replacement: Optional[str] = Field(None, description="替换建议")
    reason: Optional[str] = Field(None, description="添加原因")


class WordBatchRequest(BaseModel):
    """批量操作请求"""
    words: List[str] = Field(..., description="敏感词列表")
    severity: str = Field(..., description="严重程度")
    category: str = Field(default="general", description="分类")
    replacement: Optional[str] = Field(None, description="替换建议")
    reason: str = Field(default="", description="添加原因")


class DetectionRequest(BaseModel):
    """检测请求"""
    text: str = Field(..., description="待检测文本")
    realtime: bool = Field(default=False, description="是否实时检测模式")


class IndustryPackageRequest(BaseModel):
    """行业词包请求"""
    category: str = Field(..., description="行业分类")
    words: List[Dict[str, Any]] = Field(..., description="词包数据")


# ============== 词库管理接口 ==============

@router.post("/words", summary="添加敏感词")
async def add_word(request: WordCreateRequest):
    """添加单个敏感词"""
    try:
        severity = SeverityLevel(request.severity)
        category = SensitiveWordCategory(request.category)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"无效的参数：{e}")
    
    success = service.add_word(
        word=request.word,
        severity=severity,
        category=category,
        replacement=request.replacement,
        reason=request.reason
    )
    
    if not success:
        raise HTTPException(status_code=409, detail="该敏感词已存在")
    
    return {
        "success": True,
        "message": "敏感词添加成功",
        "data": {"word": request.word}
    }


@router.delete("/words/{word}", summary="删除敏感词")
async def remove_word(word: str):
    """删除指定敏感词"""
    success = service.remove_word(word)
    
    if not success:
        raise HTTPException(status_code=404, detail="敏感词不存在")
    
    return {
        "success": True,
        "message": "敏感词删除成功"
    }


@router.put("/words/{word}", summary="更新敏感词")
async def update_word(word: str, request: WordUpdateRequest):
    """更新敏感词信息"""
    if word not in service.word_library:
        raise HTTPException(status_code=404, detail="敏感词不存在")
    
    severity = SeverityLevel(request.severity) if request.severity else None
    category = SensitiveWordCategory(request.category) if request.category else None
    
    success = service.update_word(
        word=word,
        severity=severity,
        category=category,
        replacement=request.replacement,
        reason=request.reason
    )
    
    if not success:
        raise HTTPException(status_code=500, detail="更新失败")
    
    return {
        "success": True,
        "message": "敏感词更新成功",
        "data": service.get_word(word).to_dict()
    }


@router.get("/words", summary="查询敏感词列表")
async def list_words(
    category: Optional[str] = Query(None, description="分类筛选"),
    severity: Optional[str] = Query(None, description="级别筛选"),
    keyword: Optional[str] = Query(None, description="关键词搜索"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(50, ge=1, le=200, description="每页数量")
):
    """查询敏感词列表（支持筛选、搜索、分页）"""
    try:
        cat = SensitiveWordCategory(category) if category else None
        sev = SeverityLevel(severity) if severity else None
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"无效的参数：{e}")
    
    words, total = service.list_words(
        category=cat,
        severity=sev,
        keyword=keyword,
        page=page,
        page_size=page_size
    )
    
    return {
        "success": True,
        "data": {
            "words": words,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total": total,
                "total_pages": (total + page_size - 1) // page_size
            }
        }
    }


@router.get("/words/{word}", summary="获取敏感词详情")
async def get_word_detail(word: str):
    """获取单个敏感词详情"""
    entry = service.get_word(word)
    
    if not entry:
        raise HTTPException(status_code=404, detail="敏感词不存在")
    
    return {
        "success": True,
        "data": entry.to_dict()
    }


@router.post("/words/batch", summary="批量添加敏感词")
async def batch_add_words(request: WordBatchRequest):
    """批量添加敏感词"""
    try:
        severity = SeverityLevel(request.severity)
        category = SensitiveWordCategory(request.category)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"无效的参数：{e}")
    
    added = []
    skipped = []
    
    for word in request.words:
        if service.add_word(word, severity, category, request.replacement, request.reason):
            added.append(word)
        else:
            skipped.append(word)
    
    return {
        "success": True,
        "message": f"成功添加 {len(added)} 个，跳过 {len(skipped)} 个",
        "data": {
            "added": added,
            "skipped": skipped
        }
    }


# ============== 检测接口 ==============

@router.post("/detect", summary="检测敏感词")
async def detect(request: DetectionRequest):
    """检测文本中的敏感词"""
    if request.realtime:
        result = service.detect_realtime(request.text)
    else:
        hits = service.detect(request.text)
        result = {
            "text": request.text,
            "hits": hits,
            "has_sensitive": len(hits) > 0,
            "count": len(hits)
        }
    
    return {
        "success": True,
        "data": result
    }


@router.post("/detect/stream", summary="流式检测（用于语音转写）")
async def detect_stream(request: DetectionRequest):
    """流式检测 - 用于语音转写实时检测"""
    result = service.detect_realtime(request.text)
    
    # 返回简化结果，便于前端实时更新
    return {
        "success": True,
        "data": {
            "has_sensitive": result["has_sensitive"],
            "max_severity": result["max_severity"],
            "should_block": result["should_block"],
            "hit_count": len(result["hits"]),
            "hits": result["hits"][:10],  # 只返回前 10 个命中
            "timestamp": result["timestamp"]
        }
    }


# ============== 统计接口 ==============

@router.get("/statistics", summary="获取使用统计")
async def get_statistics():
    """获取敏感词使用统计"""
    return {
        "success": True,
        "data": service.get_statistics()
    }


@router.get("/statistics/categories", summary="获取分类统计")
async def get_category_stats():
    """获取各分类词库数量"""
    return {
        "success": True,
        "data": service.get_category_stats()
    }


@router.get("/statistics/daily", summary="获取每日统计")
async def get_daily_stats(
    days: int = Query(7, ge=1, le=30, description="查询天数")
):
    """获取最近 N 天的使用统计"""
    stats = service.get_statistics()
    daily = stats["daily_stats"]
    
    # 返回最近 N 天
    recent_days = dict(list(daily.items())[-days:])
    
    return {
        "success": True,
        "data": {
            "days": days,
            "stats": recent_days
        }
    }


# ============== 行业词包接口 ==============

@router.get("/industry-packages", summary="获取已安装行业词包")
async def get_industry_packages():
    """获取已安装的行业敏感词包"""
    return {
        "success": True,
        "data": service.get_industry_packages()
    }


@router.post("/industry-packages", summary="安装行业词包")
async def install_industry_package(request: IndustryPackageRequest):
    """安装行业敏感词包"""
    # 添加安装时间
    words_with_time = [
        {**w, "installed_at": datetime.now().isoformat()}
        for w in request.words
    ]
    
    success = service.install_industry_package(request.category, words_with_time)
    
    return {
        "success": True,
        "message": f"行业词包 [{request.category}] 安装成功",
        "data": {
            "category": request.category,
            "word_count": len(request.words)
        }
    }


@router.delete("/industry-packages/{category}", summary="卸载行业词包")
async def uninstall_industry_package(category: str):
    """卸载行业敏感词包"""
    if category not in service.industry_packages:
        raise HTTPException(status_code=404, detail="行业词包未安装")
    
    # 删除该分类下的所有词
    words_to_remove = [
        w.word for w in service.word_library.values()
        if w.category.value == category
    ]
    
    for word in words_to_remove:
        service.remove_word(word)
    
    del service.industry_packages[category]
    service._save_industry_packages()
    
    return {
        "success": True,
        "message": f"行业词包 [{category}] 卸载成功",
        "data": {
            "category": category,
            "removed_count": len(words_to_remove)
        }
    }


# ============== 导入导出接口 ==============

@router.get("/export", summary="导出词库")
async def export_library():
    """导出完整词库为 JSON"""
    return {
        "success": True,
        "data": {
            "library": json.loads(service.export_library()),
            "exported_at": datetime.now().isoformat()
        }
    }


@router.post("/import", summary="导入词库")
async def import_library(
    library: Dict[str, Any],
    merge: bool = Query(True, description="是否合并导入")
):
    """导入词库"""
    import json
    json_str = json.dumps(library)
    count = service.import_library(json_str, merge)
    
    return {
        "success": True,
        "message": f"成功导入 {count} 个敏感词",
        "data": {
            "imported_count": count
        }
    }


# ============== 预定义行业词包 ==============

BEAUTY_PACKAGE = [
    {"word": "美白祛斑", "severity": "serious", "replacement": "焕亮肌肤", "reason": "化妆品禁用医疗术语"},
    {"word": "抗衰老", "severity": "warning", "replacement": "紧致肌肤", "reason": "化妆品禁用医疗术语"},
    {"word": "治疗痤疮", "severity": "banned", "replacement": "改善痘痘", "reason": "化妆品不得宣称医疗功效"},
    {"word": "激素", "severity": "banned", "replacement": None, "reason": "禁用成分"},
    {"word": "干细胞", "severity": "banned", "replacement": None, "reason": "化妆品禁用成分"},
]

FOOD_PACKAGE = [
    {"word": "治疗", "severity": "serious", "replacement": "有助于", "reason": "食品不得宣称医疗功效"},
    {"word": "疗效", "severity": "serious", "replacement": "效果", "reason": "食品不得宣称医疗功效"},
    {"word": "预防", "severity": "serious", "replacement": "帮助", "reason": "食品不得宣称医疗功效"},
    {"word": "降血压", "severity": "banned", "replacement": None, "reason": "食品不得宣称医疗功效"},
    {"word": "降血糖", "severity": "banned", "replacement": None, "reason": "食品不得宣称医疗功效"},
    {"word": "抗癌", "severity": "banned", "replacement": None, "reason": "食品不得宣称医疗功效"},
]

CLOTHING_PACKAGE = [
    {"word": "100% 纯棉", "severity": "warning", "replacement": "优质棉", "reason": "需检测证明"},
    {"word": "永不褪色", "severity": "serious", "replacement": "色牢度高", "reason": "禁止绝对化承诺"},
    {"word": "抗菌", "severity": "serious", "replacement": "洁净", "reason": "需检测证明"},
    {"word": "防紫外线", "severity": "warning", "replacement": "防晒", "reason": "需检测证明"},
]


@router.post("/industry-packages/predefined/{category}", summary="安装预定义行业词包")
async def install_predefined_package(category: str):
    """安装预定义的行业敏感词包"""
    packages = {
        "beauty": BEAUTY_PACKAGE,
        "food": FOOD_PACKAGE,
        "clothing": CLOTHING_PACKAGE
    }
    
    if category not in packages:
        raise HTTPException(status_code=404, detail=f"未知的行业分类：{category}")
    
    words = packages[category]
    words_with_time = [
        {**w, "installed_at": datetime.now().isoformat()}
        for w in words
    ]
    
    success = service.install_industry_package(category, words_with_time)
    
    return {
        "success": True,
        "message": f"预定义行业词包 [{category}] 安装成功",
        "data": {
            "category": category,
            "word_count": len(words)
        }
    }


# 导入 json 用于导出功能
import json
