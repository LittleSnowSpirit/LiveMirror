"""
视频上传路由
支持视频文件上传、音频提取、转写分析
"""

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
import os
import shutil
from pathlib import Path
import sys

# 添加父目录到路径以导入模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db
from models import User
from services.video import VideoService, VideoProcessResult, get_service
from services.whisper_transcribe import get_service as get_whisper_service

router = APIRouter(prefix="/upload", tags=["视频上传"])

# ==================== 配置 ====================
# 上传目录
UPLOAD_DIR = Path(__file__).parent.parent / "uploads" / "videos"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# 最大文件大小：2GB
MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2GB

# 支持的视频格式
SUPPORTED_FORMATS = ["mp4", "avi", "mov", "mkv"]

# 视频服务实例
video_service = get_service()


# ==================== Pydantic 模型 ====================
class VideoUploadResponse(BaseModel):
    """视频上传响应"""
    success: bool
    message: str
    video_id: Optional[str] = None
    filename: str
    file_size: int
    duration: Optional[float] = None
    format: str
    audio_extracted: bool = False
    audio_path: Optional[str] = None
    transcription: Optional[str] = None
    processing_time: float
    created_at: datetime = Field(default_factory=datetime.utcnow)


class VideoInfo(BaseModel):
    """视频信息"""
    filename: str
    file_size: int
    duration: float
    format: str
    width: int
    height: int
    has_audio: bool


class TranscriptionRequest(BaseModel):
    """转写请求"""
    video_id: str
    model_size: str = "tiny"
    language: str = "zh"


# ==================== 工具函数 ====================
def save_uploaded_file(file: UploadFile, upload_dir: Path) -> Path:
    """
    保存上传的文件
    
    Args:
        file: 上传的文件对象
        upload_dir: 上传目录
    
    Returns:
        Path 保存的文件路径
    """
    # 生成唯一文件名
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    original_filename = Path(file.filename).name if file.filename else "unknown"
    safe_filename = f"{timestamp}_{original_filename}"
    
    file_path = upload_dir / safe_filename
    
    # 保存文件
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    return file_path


def transcribe_audio_async(audio_path: str, video_id: str):
    """
    异步转写音频（后台任务）
    
    Args:
        audio_path: 音频文件路径
        video_id: 视频 ID
    """
    try:
        print(f"[TRANSCRIBE] 开始后台转写视频 {video_id}...")
        
        whisper_service = get_whisper_service()
        result = whisper_service.transcribe(
            audio_path,
            model_size="tiny",
            language="zh"
        )
        
        print(f"[TRANSCRIBE] 视频 {video_id} 转写完成，文本长度：{len(result.text)}")
        
        # 这里可以将转写结果保存到数据库
        # 目前仅打印日志
        
    except Exception as e:
        print(f"[TRANSCRIBE] 视频 {video_id} 转写失败：{e}")


# ==================== 路由 ====================
@router.post("/video", response_model=VideoUploadResponse)
async def upload_video(
    file: UploadFile = File(..., description="视频文件"),
    background_tasks: BackgroundTasks = None,
    db: Session = Depends(get_db)
):
    """
    上传视频文件
    
    支持格式：MP4, AVI, MOV, MKV
    最大大小：2GB
    
    自动提取音频并进行转写分析
    """
    start_time = datetime.now()
    
    # 检查文件大小
    file_size = 0
    if hasattr(file, 'size') and file.size:
        file_size = file.size
    else:
        # 读取文件内容计算大小
        content = await file.read()
        file_size = len(content)
        # 重置文件指针
        file.file.seek(0)
        # 重新包装文件
        from io import BytesIO
        file.file = BytesIO(content)
    
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"文件大小超过限制 2GB（当前：{file_size / (1024*1024*1024):.2f}GB）"
        )
    
    # 检查文件格式
    filename = Path(file.filename).name if file.filename else "unknown"
    file_ext = Path(filename).suffix.lower().lstrip('.')
    
    if file_ext not in SUPPORTED_FORMATS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"不支持的视频格式：{file_ext}（支持：{', '.join(SUPPORTED_FORMATS)}）"
        )
    
    try:
        # 保存上传的文件
        print(f"[UPLOAD] 开始上传视频：{filename}, 大小：{file_size / (1024*1024):.2f} MB")
        video_path = save_uploaded_file(file, UPLOAD_DIR)
        print(f"[UPLOAD] 视频已保存到：{video_path}")
        
        # 处理视频（提取音频）
        print(f"[PROCESS] 开始处理视频...")
        result = video_service.process_video(
            str(video_path),
            extract_audio=True,
            cleanup_video=False
        )
        
        if not result.success:
            # 清理上传的文件
            if video_path.exists():
                video_path.unlink()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"视频处理失败：{result.error_message}"
            )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # 生成视频 ID
        video_id = video_path.stem
        
        # 如果提取了音频，添加后台转写任务
        audio_path = result.audio_path
        transcription = None
        
        if audio_path and background_tasks:
            # 添加后台转写任务
            background_tasks.add_task(transcribe_audio_async, audio_path, video_id)
            print(f"[UPLOAD] 已添加后台转写任务：{video_id}")
        
        response = VideoUploadResponse(
            success=True,
            message="视频上传成功",
            video_id=video_id,
            filename=filename,
            file_size=file_size,
            duration=result.video_info.duration if result.video_info else None,
            format=file_ext,
            audio_extracted=audio_path is not None,
            audio_path=audio_path,
            transcription=transcription,
            processing_time=processing_time
        )
        
        print(f"[UPLOAD] 视频上传完成：{filename}, 耗时：{processing_time:.2f}s")
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[UPLOAD] 上传失败：{e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上传失败：{str(e)}"
        )


@router.get("/video/{video_id}")
async def get_video_info(video_id: str):
    """
    获取视频信息
    
    Args:
        video_id: 视频 ID
    """
    # 查找视频文件
    video_files = list(UPLOAD_DIR.glob(f"{video_id}.*"))
    
    if not video_files:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"视频未找到：{video_id}"
        )
    
    video_path = video_files[0]
    
    try:
        info = video_service.get_video_info(str(video_path))
        
        return {
            "success": True,
            "video_id": video_id,
            "info": {
                "filename": info.filename,
                "file_size": info.file_size,
                "duration": info.duration,
                "format": info.format,
                "width": info.width,
                "height": info.height,
                "has_audio": info.has_audio
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取视频信息失败：{str(e)}"
        )


@router.post("/video/{video_id}/transcribe")
async def transcribe_video(
    video_id: str,
    request: TranscriptionRequest,
    background_tasks: BackgroundTasks = None
):
    """
    转写视频音频
    
    Args:
        video_id: 视频 ID
        request: 转写请求
    """
    # 查找视频文件
    video_files = list(UPLOAD_DIR.glob(f"{video_id}.*"))
    
    if not video_files:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"视频未找到：{video_id}"
        )
    
    video_path = video_files[0]
    
    try:
        # 提取音频
        print(f"[TRANSCRIBE] 开始转写视频：{video_id}")
        audio_path = video_service.extract_audio(str(video_path))
        
        # 转写音频
        whisper_service = get_whisper_service()
        result = whisper_service.transcribe(
            audio_path,
            model_size=request.model_size,
            language=request.language
        )
        
        return {
            "success": True,
            "video_id": video_id,
            "transcription": {
                "text": result.text,
                "segments": result.segments,
                "language": result.language,
                "model_size": result.model_size,
                "processing_time": result.total_time
            }
        }
        
    except Exception as e:
        print(f"[TRANSCRIBE] 转写失败：{e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"转写失败：{str(e)}"
        )


@router.delete("/video/{video_id}")
async def delete_video(video_id: str):
    """
    删除视频文件
    
    Args:
        video_id: 视频 ID
    """
    # 查找视频文件
    video_files = list(UPLOAD_DIR.glob(f"{video_id}.*"))
    
    if not video_files:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"视频未找到：{video_id}"
        )
    
    try:
        # 删除视频文件
        for video_path in video_files:
            video_path.unlink()
            print(f"[DELETE] 已删除视频：{video_path}")
        
        # 删除关联的音频文件
        audio_dir = Path(video_service.temp_dir) / "livemirror_video"
        if audio_dir.exists():
            audio_files = list(audio_dir.glob(f"{video_id}.*"))
            for audio_path in audio_files:
                audio_path.unlink()
                print(f"[DELETE] 已删除音频：{audio_path}")
        
        return {
            "success": True,
            "message": f"视频 {video_id} 已删除"
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除失败：{str(e)}"
        )


@router.get("/supported-formats")
async def get_supported_formats():
    """获取支持的视频格式"""
    return {
        "success": True,
        "formats": SUPPORTED_FORMATS,
        "max_file_size": MAX_FILE_SIZE,
        "max_file_size_human": "2GB"
    }
