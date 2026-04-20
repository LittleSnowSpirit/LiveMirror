"""
直播回放接口路由
提供录像管理、播放、剪辑和分享的 HTTP API
"""

from fastapi import APIRouter, HTTPException, Query, Request, Response, Header
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path
import os

from services.playback import get_playback_service

router = APIRouter(prefix="/api/playback", tags=["playback"])


# ==================== 数据模型 ====================

class RecordingCreate(BaseModel):
    """创建录像请求"""
    title: str
    streamer: str
    duration: int
    categories: List[str] = []
    tags: List[str] = []
    description: str = ""


class RecordingUpdate(BaseModel):
    """更新录像请求"""
    title: Optional[str] = None
    description: Optional[str] = None
    categories: Optional[List[str]] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None


class ClipCreate(BaseModel):
    """创建片段请求"""
    recording_id: str
    start_time: float
    end_time: float
    title: str
    description: str = ""


class ShareCreate(BaseModel):
    """创建分享请求"""
    recording_id: str
    expire_hours: int = 24


# ==================== 录像管理接口 ====================

@router.get("/recordings", summary="获取录像列表")
async def list_recordings(
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    offset: int = Query(0, ge=0, description="偏移量")
):
    """获取所有录像列表（分页）"""
    service = get_playback_service()
    recordings = service.get_all_recordings(limit=limit, offset=offset)
    return {
        "success": True,
        "data": recordings,
        "total": len(service._metadata_cache),
        "limit": limit,
        "offset": offset
    }


@router.get("/recordings/search", summary="搜索录像")
async def search_recordings(
    query: Optional[str] = Query(None, description="搜索关键词"),
    categories: Optional[str] = Query(None, description="分类筛选（逗号分隔）"),
    tags: Optional[str] = Query(None, description="标签筛选（逗号分隔）"),
    streamer: Optional[str] = Query(None, description="主播名称"),
    date_from: Optional[str] = Query(None, description="起始日期"),
    date_to: Optional[str] = Query(None, description="结束日期"),
    min_duration: Optional[int] = Query(None, ge=0, description="最小时长（秒）"),
    max_duration: Optional[int] = Query(None, ge=0, description="最大时长（秒）"),
    limit: int = Query(20, ge=1, le=100, description="返回数量"),
    offset: int = Query(0, ge=0, description="偏移量")
):
    """搜索和筛选录像"""
    service = get_playback_service()
    
    results = service.search_recordings(
        query=query,
        categories=categories.split(',') if categories else None,
        tags=tags.split(',') if tags else None,
        streamer=streamer,
        date_from=date_from,
        date_to=date_to,
        min_duration=min_duration,
        max_duration=max_duration,
        limit=limit,
        offset=offset
    )
    
    return {
        "success": True,
        "data": results,
        "total": len(results),
        "limit": limit,
        "offset": offset
    }


@router.get("/recordings/{recording_id}", summary="获取录像详情")
async def get_recording(recording_id: str):
    """获取单个录像的详细信息"""
    service = get_playback_service()
    recording = service.get_recording(recording_id)
    
    if not recording:
        raise HTTPException(status_code=404, detail="录像不存在")
    
    # 增加观看次数
    service.increment_view_count(recording_id)
    
    return {
        "success": True,
        "data": recording
    }


@router.post("/recordings", summary="上传录像")
async def create_recording(
    request: Request,
    title: str = Query(..., description="录像标题"),
    streamer: str = Query(..., description="主播名称"),
    duration: int = Query(..., description="时长（秒）"),
    categories: Optional[str] = Query(None, description="分类（逗号分隔）"),
    tags: Optional[str] = Query(None, description="标签（逗号分隔）"),
    description: str = Query("", description="描述")
):
    """上传新的录像文件"""
    service = get_playback_service()
    
    # 获取上传的文件
    form = await request.form()
    if 'file' not in form:
        raise HTTPException(status_code=400, detail="未找到视频文件")
    
    file = form['file']
    thumbnail = form.get('thumbnail')
    
    # 保存临时文件
    import tempfile
    import shutil
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name
    
    thumbnail_path = None
    if thumbnail:
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(thumbnail.filename).suffix) as tmp:
            shutil.copyfileobj(thumbnail.file, tmp)
            thumbnail_path = tmp.name
    
    try:
        recording = service.add_recording(
            file_path=tmp_path,
            title=title,
            streamer=streamer,
            duration=duration,
            categories=categories.split(',') if categories else [],
            tags=tags.split(',') if tags else [],
            description=description,
            thumbnail_path=thumbnail_path
        )
        
        return {
            "success": True,
            "data": recording,
            "message": "录像上传成功"
        }
    finally:
        # 清理临时文件
        try:
            os.unlink(tmp_path)
            if thumbnail_path:
                os.unlink(thumbnail_path)
        except Exception:
            pass


@router.put("/recordings/{recording_id}", summary="更新录像")
async def update_recording(recording_id: str, updates: RecordingUpdate):
    """更新录像元数据"""
    service = get_playback_service()
    
    recording = service.update_recording(recording_id, updates.dict(exclude_unset=True))
    if not recording:
        raise HTTPException(status_code=404, detail="录像不存在")
    
    return {
        "success": True,
        "data": recording,
        "message": "录像更新成功"
    }


@router.delete("/recordings/{recording_id}", summary="删除录像")
async def delete_recording(recording_id: str):
    """删除录像及其相关文件"""
    service = get_playback_service()
    
    if not service.delete_recording(recording_id):
        raise HTTPException(status_code=404, detail="录像不存在")
    
    return {
        "success": True,
        "message": "录像删除成功"
    }


# ==================== 视频播放接口 ====================

@router.get("/recordings/{recording_id}/stream", summary="流式播放录像")
async def stream_recording(recording_id: str, range: str = Header(None)):
    """
    流式播放录像视频
    支持 HTTP Range 请求，实现视频拖拽播放
    """
    service = get_playback_service()
    recording = service.get_recording(recording_id)
    
    if not recording:
        raise HTTPException(status_code=404, detail="录像不存在")
    
    video_path = Path(recording['file_path'])
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="视频文件不存在")
    
    # 增加观看次数
    service.increment_view_count(recording_id)
    
    # 返回文件响应（FastAPI 自动处理 Range 请求）
    return FileResponse(
        path=str(video_path),
        media_type="video/mp4",
        filename=recording['file_name']
    )


@router.get("/recordings/{recording_id}/thumbnail", summary="获取录像缩略图")
async def get_thumbnail(recording_id: str):
    """获取录像缩略图"""
    service = get_playback_service()
    recording = service.get_recording(recording_id)
    
    if not recording:
        raise HTTPException(status_code=404, detail="录像不存在")
    
    thumbnail_path = recording.get('thumbnail_path')
    if not thumbnail_path or not Path(thumbnail_path).exists():
        # 返回默认缩略图或 404
        raise HTTPException(status_code=404, detail="缩略图不存在")
    
    return FileResponse(
        path=thumbnail_path,
        media_type="image/jpeg"
    )


# ==================== 片段剪辑接口 ====================

@router.get("/recordings/{recording_id}/clips", summary="获取录像片段列表")
async def list_clips(recording_id: str):
    """获取指定录像的所有片段"""
    service = get_playback_service()
    
    # 检查录像是否存在
    if not service.get_recording(recording_id):
        raise HTTPException(status_code=404, detail="录像不存在")
    
    clips = service.get_clips(recording_id)
    return {
        "success": True,
        "data": clips,
        "total": len(clips)
    }


@router.post("/clips", summary="创建录像片段")
async def create_clip(clip: ClipCreate):
    """创建新的录像片段"""
    service = get_playback_service()
    
    # 检查原录像是否存在
    if not service.get_recording(clip.recording_id):
        raise HTTPException(status_code=404, detail="原录像不存在")
    
    # 验证时间范围
    if clip.start_time >= clip.end_time:
        raise HTTPException(status_code=400, detail="开始时间必须小于结束时间")
    
    original = service.get_recording(clip.recording_id)
    if clip.end_time > original['duration']:
        raise HTTPException(status_code=400, detail="结束时间超出录像时长")
    
    clip_data = service.create_clip(
        recording_id=clip.recording_id,
        start_time=clip.start_time,
        end_time=clip.end_time,
        title=clip.title,
        description=clip.description
    )
    
    return {
        "success": True,
        "data": clip_data,
        "message": "片段创建成功"
    }


@router.get("/clips/{clip_id}/stream", summary="流式播放片段")
async def stream_clip(clip_id: str, range: str = Header(None)):
    """
    流式播放录像片段
    通过 Range 头实现片段播放
    """
    service = get_playback_service()
    clips = service.get_clips()
    
    clip = None
    for c in clips:
        if c['id'] == clip_id:
            clip = c
            break
    
    if not clip:
        raise HTTPException(status_code=404, detail="片段不存在")
    
    video_path = Path(clip['source_file'])
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="视频文件不存在")
    
    # 计算字节的 range（假设固定码率，简化处理）
    # 实际生产环境需要更精确的计算
    original_duration = service.get_recording(clip['original_recording_id'])['duration']
    file_size = video_path.stat().st_size
    
    start_byte = int((clip['start_time'] / original_duration) * file_size)
    end_byte = int((clip['end_time'] / original_duration) * file_size) - 1
    
    # 返回带 range 的文件响应
    headers = {
        "Content-Range": f"bytes {start_byte}-{end_byte}/{file_size}",
        "Accept-Ranges": "bytes"
    }
    
    return FileResponse(
        path=str(video_path),
        media_type="video/mp4",
        headers=headers
    )


# ==================== 分享功能接口 ====================

@router.post("/share", summary="生成分享链接")
async def create_share(share: ShareCreate):
    """生成录像分享令牌"""
    service = get_playback_service()
    
    recording = service.get_recording(share.recording_id)
    if not recording:
        raise HTTPException(status_code=404, detail="录像不存在")
    
    token = service.generate_share_token(share.recording_id, share.expire_hours)
    
    # 构建分享 URL（实际使用时需要替换为真实域名）
    share_url = f"/playback/share/{token}"
    
    return {
        "success": True,
        "data": {
            "share_token": token,
            "share_url": share_url,
            "expires_in_hours": share.expire_hours
        },
        "message": "分享链接生成成功"
    }


@router.get("/share/{share_token}", summary="通过分享令牌获取录像")
async def get_shared_recording(share_token: str):
    """通过分享令牌访问录像"""
    service = get_playback_service()
    
    recording = service.get_by_share_token(share_token)
    if not recording:
        raise HTTPException(status_code=404, detail="分享链接无效或已过期")
    
    # 增加分享观看次数
    service.increment_view_count(recording['id'])
    
    return {
        "success": True,
        "data": recording
    }


@router.get("/share/{share_token}/stream", summary="流式播放分享的录像")
async def stream_shared_recording(share_token: str, range: str = Header(None)):
    """流式播放分享的录像"""
    service = get_playback_service()
    
    recording = service.get_by_share_token(share_token)
    if not recording:
        raise HTTPException(status_code=404, detail="分享链接无效或已过期")
    
    video_path = Path(recording['file_path'])
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="视频文件不存在")
    
    return FileResponse(
        path=str(video_path),
        media_type="video/mp4",
        filename=recording['file_name']
    )


# ==================== 统计和元数据接口 ====================

@router.get("/statistics", summary="获取统计信息")
async def get_statistics():
    """获取回放系统的统计信息"""
    service = get_playback_service()
    stats = service.get_statistics()
    
    return {
        "success": True,
        "data": stats
    }


@router.get("/categories", summary="获取所有分类")
async def get_categories():
    """获取所有录像分类"""
    service = get_playback_service()
    categories = service.get_categories()
    
    return {
        "success": True,
        "data": categories
    }


@router.get("/tags", summary="获取所有标签")
async def get_tags():
    """获取所有录像标签"""
    service = get_playback_service()
    tags = service.get_tags()
    
    return {
        "success": True,
        "data": tags
    }
