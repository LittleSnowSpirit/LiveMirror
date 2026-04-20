"""
直播间装修 API 接口
提供装修管理的 RESTful API
"""

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any

from backend.services.decorator import decorator_service, DecoratorScheme, DecoratorElement


router = APIRouter(prefix="/api/decorator", tags=["decorator"])


# ==================== 请求/响应模型 ====================

class ElementBase(BaseModel):
    """元素基础模型"""
    element_type: str = Field(..., description="元素类型 (background/sticker/text/image)")
    name: str = Field(..., description="元素名称")
    x: float = Field(default=0, description="X 坐标")
    y: float = Field(default=0, description="Y 坐标")
    width: float = Field(default=100, description="宽度")
    height: float = Field(default=100, description="高度")
    rotation: float = Field(default=0, description="旋转角度")
    opacity: float = Field(default=1.0, ge=0, le=1, description="透明度")
    z_index: int = Field(default=0, description="层级")
    visible: bool = Field(default=True, description="是否可见")
    locked: bool = Field(default=False, description="是否锁定")


class BackgroundElementRequest(ElementBase):
    """背景元素请求"""
    element_type: str = "background"
    image_url: str = Field(default="", description="背景图片 URL")
    color: str = Field(default="#FFFFFF", description="背景颜色")
    fit_mode: str = Field(default="cover", description="适配模式 (cover/contain/fill/stretch)")


class StickerElementRequest(ElementBase):
    """贴纸元素请求"""
    element_type: str = "sticker"
    image_url: str = Field(default="", description="贴纸图片 URL")
    category: str = Field(default="default", description="贴纸分类")


class TextElementRequest(ElementBase):
    """文字元素请求"""
    element_type: str = "text"
    content: str = Field(default="文字", description="文字内容")
    font_family: str = Field(default="Arial", description="字体")
    font_size: int = Field(default=32, description="字体大小")
    font_weight: str = Field(default="normal", description="字体粗细")
    font_style: str = Field(default="normal", description="字体样式")
    color: str = Field(default="#000000", description="文字颜色")
    background_color: str = Field(default="transparent", description="背景颜色")
    text_align: str = Field(default="left", description="对齐方式")
    line_height: float = Field(default=1.5, description="行高")
    letter_spacing: float = Field(default=0, description="字间距")


class SchemeCreateRequest(BaseModel):
    """装修方案创建请求"""
    name: str = Field(..., min_length=1, max_length=100, description="方案名称")
    room_id: str = Field(default="", description="直播间 ID")


class SchemeUpdateRequest(BaseModel):
    """装修方案更新请求"""
    name: Optional[str] = Field(None, description="方案名称")
    background: Optional[Dict] = Field(None, description="背景元素")
    elements: Optional[List[Dict]] = Field(None, description="装饰元素列表")


class ElementUpdateRequest(BaseModel):
    """元素更新请求"""
    x: Optional[float] = Field(None, description="X 坐标")
    y: Optional[float] = Field(None, description="Y 坐标")
    width: Optional[float] = Field(None, description="宽度")
    height: Optional[float] = Field(None, description="高度")
    rotation: Optional[float] = Field(None, description="旋转角度")
    opacity: Optional[float] = Field(None, description="透明度")
    visible: Optional[bool] = Field(None, description="是否可见")
    locked: Optional[bool] = Field(None, description="是否锁定")
    # Text specific
    content: Optional[str] = Field(None, description="文字内容")
    font_size: Optional[int] = Field(None, description="字体大小")
    color: Optional[str] = Field(None, description="颜色")


class SchemeResponse(BaseModel):
    """装修方案响应"""
    id: str
    name: str
    room_id: str
    background: Optional[Dict]
    elements: List[Dict]
    created_at: str
    updated_at: str
    is_active: bool


class SchemeListResponse(BaseModel):
    """装修方案列表响应"""
    schemes: List[SchemeResponse]
    total: int


class PresetResponse(BaseModel):
    """装修预设响应"""
    id: str
    name: str
    description: str
    category: str
    thumbnail_url: str
    elements: List[Dict]
    usage_count: int


class StickerResponse(BaseModel):
    """贴纸响应"""
    id: str
    name: str
    category: str
    url: str
    tags: List[str]


class PreviewResponse(BaseModel):
    """预览响应"""
    scheme_id: str
    preview_url: str
    elements_count: int
    has_background: bool


# ==================== 装修方案接口 ====================

@router.post("/schemes", response_model=SchemeResponse, summary="创建装修方案")
async def create_scheme(request: SchemeCreateRequest):
    """
    创建新的装修方案
    
    - **name**: 方案名称
    - **room_id**: 可选的直播间 ID
    """
    try:
        scheme = decorator_service.create_scheme(
            name=request.name,
            room_id=request.room_id
        )
        return SchemeResponse(**scheme.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/schemes", response_model=SchemeListResponse, summary="获取装修方案列表")
async def list_schemes(
    room_id: Optional[str] = Query(None, description="按直播间 ID 筛选")
):
    """
    获取装修方案列表
    
    - **room_id**: 可选的直播间 ID 筛选
    """
    schemes = decorator_service.list_schemes(room_id=room_id)
    return SchemeListResponse(
        schemes=[SchemeResponse(**s.to_dict()) for s in schemes],
        total=len(schemes)
    )


@router.get("/schemes/{scheme_id}", response_model=SchemeResponse, summary="获取装修方案详情")
async def get_scheme(scheme_id: str):
    """
    获取指定装修方案的详细信息
    """
    scheme = decorator_service.get_scheme(scheme_id)
    if not scheme:
        raise HTTPException(status_code=404, detail="装修方案不存在")
    return SchemeResponse(**scheme.to_dict())


@router.put("/schemes/{scheme_id}", response_model=SchemeResponse, summary="更新装修方案")
async def update_scheme(scheme_id: str, request: SchemeUpdateRequest):
    """
    更新装修方案
    
    - **name**: 方案名称
    - **background**: 背景元素配置
    - **elements**: 装饰元素列表
    """
    scheme = decorator_service.get_scheme(scheme_id)
    if not scheme:
        raise HTTPException(status_code=404, detail="装修方案不存在")
    
    updates = {}
    if request.name is not None:
        updates['name'] = request.name
    if request.background is not None:
        updates['background'] = request.background
    if request.elements is not None:
        updates['elements'] = request.elements
    
    success = decorator_service.update_scheme(scheme_id, updates)
    if not success:
        raise HTTPException(status_code=500, detail="更新方案失败")
    
    updated_scheme = decorator_service.get_scheme(scheme_id)
    return SchemeResponse(**updated_scheme.to_dict())


@router.delete("/schemes/{scheme_id}", summary="删除装修方案")
async def delete_scheme(scheme_id: str):
    """
    删除指定装修方案
    """
    success = decorator_service.delete_scheme(scheme_id)
    if not success:
        raise HTTPException(status_code=404, detail="装修方案不存在")
    return {"message": "装修方案已删除"}


@router.post("/schemes/{scheme_id}/apply", response_model=SchemeResponse, summary="应用装修方案")
async def apply_scheme(scheme_id: str):
    """
    应用装修方案到直播间
    
    会将此方案设置为活跃状态
    """
    scheme = decorator_service.get_scheme(scheme_id)
    if not scheme:
        raise HTTPException(status_code=404, detail="装修方案不存在")
    
    success = decorator_service.apply_scheme(scheme_id)
    if not success:
        raise HTTPException(status_code=500, detail="应用方案失败")
    
    updated_scheme = decorator_service.get_scheme(scheme_id)
    return SchemeResponse(**updated_scheme.to_dict())


@router.get("/schemes/active", response_model=Optional[SchemeResponse], summary="获取当前活跃方案")
async def get_active_scheme():
    """
    获取当前正在应用的装修方案
    """
    scheme = decorator_service.get_active_scheme()
    if not scheme:
        return None
    return SchemeResponse(**scheme.to_dict())


@router.post("/schemes/{scheme_id}/elements", response_model=SchemeResponse, summary="添加装饰元素")
async def add_element(scheme_id: str, element: Dict = Body(...)):
    """
    向装修方案添加装饰元素
    
    元素类型支持：sticker, text, image
    """
    scheme = decorator_service.get_scheme(scheme_id)
    if not scheme:
        raise HTTPException(status_code=404, detail="装修方案不存在")
    
    # 根据元素类型创建对应的元素对象
    element_type = element.get('element_type', 'sticker')
    if element_type == 'text':
        from backend.services.decorator import TextElement
        elem = TextElement.from_dict(element)
    elif element_type == 'sticker':
        from backend.services.decorator import StickerElement
        elem = StickerElement.from_dict(element)
    else:
        elem = DecoratorElement.from_dict(element)
    
    scheme.add_element(elem)
    return SchemeResponse(**scheme.to_dict())


@router.put("/schemes/{scheme_id}/elements/{element_id}", response_model=SchemeResponse, summary="更新装饰元素")
async def update_element(scheme_id: str, element_id: str, updates: ElementUpdateRequest):
    """
    更新装修方案中的装饰元素属性
    """
    scheme = decorator_service.get_scheme(scheme_id)
    if not scheme:
        raise HTTPException(status_code=404, detail="装修方案不存在")
    
    update_dict = {k: v for k, v in updates.dict().items() if v is not None}
    success = scheme.update_element(element_id, update_dict)
    if not success:
        raise HTTPException(status_code=404, detail="元素不存在")
    
    return SchemeResponse(**scheme.to_dict())


@router.delete("/schemes/{scheme_id}/elements/{element_id}", response_model=SchemeResponse, summary="删除装饰元素")
async def delete_element(scheme_id: str, element_id: str):
    """
    从装修方案中删除装饰元素
    """
    scheme = decorator_service.get_scheme(scheme_id)
    if not scheme:
        raise HTTPException(status_code=404, detail="装修方案不存在")
    
    success = scheme.remove_element(element_id)
    if not success:
        raise HTTPException(status_code=404, detail="元素不存在")
    
    return SchemeResponse(**scheme.to_dict())


# ==================== 装修预设接口 ====================

@router.get("/presets", response_model=List[PresetResponse], summary="获取装修预设列表")
async def list_presets(
    category: Optional[str] = Query(None, description="按分类筛选")
):
    """
    获取所有装修预设模板
    
    - **category**: 可选的分类筛选 (default/festival/promotion/minimal/gaming)
    """
    presets = decorator_service.get_presets(category=category)
    return [PresetResponse(**p.to_dict()) for p in presets]


@router.get("/presets/{preset_id}", response_model=PresetResponse, summary="获取装修预设详情")
async def get_preset(preset_id: str):
    """
    获取指定装修预设的详细信息
    """
    preset = next((p for p in decorator_service.presets if p.id == preset_id), None)
    if not preset:
        raise HTTPException(status_code=404, detail="装修预设不存在")
    return PresetResponse(**preset.to_dict())


@router.post("/schemes/{scheme_id}/apply-preset/{preset_id}", response_model=SchemeResponse, summary="应用装修预设")
async def apply_preset_to_scheme(scheme_id: str, preset_id: str):
    """
    将装修预设应用到指定方案
    
    会覆盖方案现有的所有元素
    """
    success = decorator_service.apply_preset(preset_id, scheme_id)
    if not success:
        raise HTTPException(status_code=400, detail="应用预设失败")
    
    scheme = decorator_service.get_scheme(scheme_id)
    return SchemeResponse(**scheme.to_dict())


# ==================== 贴纸库接口 ====================

@router.get("/stickers", response_model=List[StickerResponse], summary="获取贴纸库")
async def list_stickers(
    category: Optional[str] = Query(None, description="按分类筛选"),
    keyword: Optional[str] = Query(None, description="关键词搜索")
):
    """
    获取贴纸库
    
    - **category**: 可选的分类筛选 (festival/promotion/decoration/emoji/gaming)
    - **keyword**: 可选的关键词搜索
    """
    if keyword:
        stickers = decorator_service.search_stickers(keyword)
    else:
        stickers = decorator_service.get_sticker_library(category=category)
    
    return [StickerResponse(**s) for s in stickers]


@router.get("/sticker-categories", summary="获取贴纸分类列表")
async def list_sticker_categories():
    """
    获取所有贴纸分类
    """
    categories = list(set(s['category'] for s in decorator_service.sticker_library))
    return {
        "categories": [
            {"id": cat, "name": get_category_name(cat), "count": len([s for s in decorator_service.sticker_library if s['category'] == cat])}
            for cat in categories
        ]
    }


def get_category_name(category: str) -> str:
    """获取分类中文名"""
    names = {
        "default": "默认",
        "festival": "节日庆典",
        "promotion": "促销活动",
        "decoration": "装饰元素",
        "emoji": "表情符号",
        "gaming": "游戏直播",
        "minimal": "简约风格"
    }
    return names.get(category, category)


# ==================== 预览接口 ====================

@router.get("/schemes/{scheme_id}/preview", response_model=PreviewResponse, summary="生成装修预览")
async def generate_preview(scheme_id: str):
    """
    生成装修方案的预览
    
    返回预览 URL 和方案信息
    """
    scheme = decorator_service.get_scheme(scheme_id)
    if not scheme:
        raise HTTPException(status_code=404, detail="装修方案不存在")
    
    # 生成预览 URL（实际项目中应生成真实预览图）
    preview_url = f"/api/decorator/previews/{scheme_id}.png"
    
    return PreviewResponse(
        scheme_id=scheme_id,
        preview_url=preview_url,
        elements_count=len(scheme.elements),
        has_background=scheme.background is not None
    )


# ==================== 导入导出接口 ====================

@router.get("/schemes/{scheme_id}/export", summary="导出装修方案")
async def export_scheme(scheme_id: str):
    """
    导出装修方案为 JSON 格式
    """
    json_data = decorator_service.export_scheme(scheme_id)
    if not json_data:
        raise HTTPException(status_code=404, detail="装修方案不存在")
    
    from fastapi.responses import Response
    return Response(
        content=json_data,
        media_type="application/json",
        headers={"Content-Disposition": f"attachment; filename=scheme_{scheme_id}.json"}
    )


@router.post("/schemes/import", response_model=SchemeResponse, summary="导入装修方案")
async def import_scheme(
    json_data: str = Body(..., embed=True, description="JSON 格式的方案数据"),
    name: Optional[str] = Body(None, embed=True, description="方案名称（可选）")
):
    """
    从 JSON 导入装修方案
    """
    scheme = decorator_service.import_scheme(json_data, name=name or "")
    if not scheme:
        raise HTTPException(status_code=400, detail="导入失败，JSON 格式不正确")
    
    return SchemeResponse(**scheme.to_dict())
