"""
直播剧本规划 API 路由 - LiveMirror
"""

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

from backend.services.script_planner import (
    get_service,
    ScriptDuration,
    ScriptSectionType,
    InteractionType,
    LiveScript
)

router = APIRouter(prefix="/api/planner", tags=["直播剧本规划"])

service = get_service()


# ============== 数据模型 ==============

class ScriptGenerateRequest(BaseModel):
    """生成剧本请求"""
    theme: str = Field(..., description="直播主题")
    duration: str = Field(..., description="直播时长：1h/2h/3h/4h")
    target_audience: Optional[str] = Field("所有人", description="目标观众")
    streamer_name: Optional[str] = Field("主播", description="主播名称")
    template_id: Optional[str] = Field(None, description="模板 ID")
    selected_products: Optional[List[str]] = Field(None, description="选中的产品 ID 列表")


class ScriptExportRequest(BaseModel):
    """导出剧本请求"""
    script_id: str = Field(..., description="剧本 ID")
    format: str = Field(..., description="导出格式：json/txt/pdf/word")
    output_path: Optional[str] = Field(None, description="输出路径")


class ProductAddRequest(BaseModel):
    """添加产品请求"""
    name: str = Field(..., description="产品名称")
    price: float = Field(..., description="直播价格")
    original_price: float = Field(..., description="原价")
    discount: str = Field(..., description="折扣描述")
    category: Optional[str] = Field(None, description="分类")
    selling_points: List[str] = Field(default=[], description="卖点列表")
    target_audience: Optional[str] = Field(None, description="目标人群")
    script_template: Optional[str] = Field(None, description="推荐话术")


# ============== 剧本生成接口 ==============

@router.post("/generate", summary="生成直播剧本")
async def generate_script(request: ScriptGenerateRequest):
    """生成完整直播剧本"""
    try:
        duration = ScriptDuration(request.duration)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"无效的时长：{e}")
    
    try:
        script = service.generate_script(
            theme=request.theme,
            duration=duration,
            target_audience=request.target_audience,
            streamer_name=request.streamer_name,
            template_id=request.template_id,
            selected_products=request.selected_products
        )
        
        return {
            "success": True,
            "message": "剧本生成成功",
            "data": {
                "script_id": script.script_id,
                "title": script.title,
                "duration": script.duration.value,
                "theme": script.theme,
                "generated_at": script.generated_at.isoformat(),
                "segments_count": len(script.segments),
                "products_count": len(script.products),
                "interactions_count": len(script.interactions),
                "emergency_plans_count": len(script.emergency_plans),
                "overall_flow": script.overall_flow
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"生成失败：{str(e)}")


@router.post("/generate/quick/{duration}", summary="快速生成剧本")
async def quick_generate_script(
    duration: str,
    theme: str = Query(..., description="直播主题"),
    template_id: Optional[str] = Query(None, description="模板 ID")
):
    """快速生成指定时长的剧本"""
    try:
        dur = ScriptDuration(duration)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效时长，支持：1h/2h/3h/4h")
    
    script = service.generate_script(
        theme=theme,
        duration=dur,
        template_id=template_id
    )
    
    return {
        "success": True,
        "message": "剧本生成成功",
        "data": {
            "script_id": script.script_id,
            "title": script.title,
            "duration": duration,
            "segments_count": len(script.segments)
        }
    }


# ============== 剧本查询接口 ==============

@router.get("/list", summary="查询剧本列表")
async def list_scripts(
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    offset: int = Query(0, ge=0, description="偏移量")
):
    """查询剧本列表"""
    scripts = service.list_scripts(limit, offset)
    
    return {
        "success": True,
        "data": {
            "scripts": [
                {
                    "script_id": s["script_id"],
                    "title": s["title"],
                    "duration": s["duration"],
                    "theme": s["theme"],
                    "generated_at": s["generated_at"],
                    "segments_count": len(s["segments"]),
                    "products_count": len(s["products"]),
                    "interactions_count": len(s["interactions"])
                }
                for s in scripts
            ],
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total": len(service.scripts)
            }
        }
    }


@router.get("/{script_id}", summary="获取剧本详情")
async def get_script(script_id: str):
    """获取指定剧本的详细信息"""
    script = service.get_script(script_id)
    
    if not script:
        raise HTTPException(status_code=404, detail="剧本不存在")
    
    return {
        "success": True,
        "data": script
    }


@router.delete("/{script_id}", summary="删除剧本")
async def delete_script(script_id: str):
    """删除指定剧本"""
    success = service.delete_script(script_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="剧本不存在")
    
    return {
        "success": True,
        "message": "剧本删除成功"
    }


# ============== 剧本导出接口 ==============

@router.post("/export", summary="导出剧本")
async def export_script(request: ScriptExportRequest):
    """导出剧本为指定格式"""
    try:
        output_path = service.export_script(
            script_id=request.script_id,
            format=request.format,
            output_path=request.output_path
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    return {
        "success": True,
        "message": "剧本导出成功",
        "data": {
            "script_id": request.script_id,
            "format": request.format,
            "output_path": output_path
        }
    }


@router.get("/{script_id}/export/{format}", summary="快速导出剧本")
async def quick_export(script_id: str, format: str):
    """快速导出剧本"""
    try:
        output_path = service.export_script(script_id, format)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    return {
        "success": True,
        "data": {
            "output_path": output_path
        }
    }


# ============== 模板管理接口 ==============

@router.get("/templates", summary="查询模板列表")
async def get_templates():
    """获取所有可用模板"""
    templates = service.get_templates()
    
    return {
        "success": True,
        "data": {
            "templates": templates
        }
    }


# ============== 产品库管理接口 ==============

@router.get("/products", summary="查询产品库")
async def get_products(
    category: Optional[str] = Query(None, description="分类筛选")
):
    """获取产品库"""
    products = service.get_products(category)
    
    return {
        "success": True,
        "data": {
            "products": products
        }
    }


@router.post("/products", summary="添加产品")
async def add_product(request: ProductAddRequest):
    """添加产品到库"""
    product_data = request.dict()
    product_id = service.add_product(product_data)
    
    return {
        "success": True,
        "message": "产品添加成功",
        "data": {
            "product_id": product_id,
            "name": request.name
        }
    }


# ============== 统计接口 ==============

@router.get("/statistics", summary="获取统计信息")
async def get_statistics():
    """获取剧本系统使用统计"""
    return {
        "success": True,
        "data": service.get_statistics()
    }


# ============== 分段规划接口 ==============

@router.get("/{script_id}/segments", summary="获取剧本分段详情")
async def get_script_segments(script_id: str):
    """获取剧本的详细分段信息"""
    script = service.get_script(script_id)
    
    if not script:
        raise HTTPException(status_code=404, detail="剧本不存在")
    
    return {
        "success": True,
        "data": {
            "script_id": script_id,
            "title": script["title"],
            "duration": script["duration"],
            "segments": script["segments"],
            "timeline": [
                {
                    "time": seg["start_time"],
                    "title": seg["title"],
                    "type": seg["segment_type"],
                    "duration": seg["duration_minutes"]
                }
                for seg in script["segments"]
            ]
        }
    }


@router.get("/{script_id}/products", summary="获取产品上下架时间")
async def get_script_products(script_id: str):
    """获取剧本中的产品上下架时间规划"""
    script = service.get_script(script_id)
    
    if not script:
        raise HTTPException(status_code=404, detail="剧本不存在")
    
    return {
        "success": True,
        "data": {
            "script_id": script_id,
            "products": script["products"]
        }
    }


@router.get("/{script_id}/interactions", summary="获取互动环节")
async def get_script_interactions(script_id: str):
    """获取剧本中的互动环节设计"""
    script = service.get_script(script_id)
    
    if not script:
        raise HTTPException(status_code=404, detail="剧本不存在")
    
    return {
        "success": True,
        "data": {
            "script_id": script_id,
            "interactions": script["interactions"]
        }
    }


@router.get("/{script_id}/emergency", summary="获取应急预案")
async def get_script_emergency(script_id: str):
    """获取剧本的应急预案"""
    script = service.get_script(script_id)
    
    if not script:
        raise HTTPException(status_code=404, detail="剧本不存在")
    
    return {
        "success": True,
        "data": {
            "script_id": script_id,
            "emergency_plans": script["emergency_plans"]
        }
    }
