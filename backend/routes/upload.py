"""
音频上传接口
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import uuid
import os
import shutil
from pathlib import Path
from loguru import logger
from datetime import datetime
import sys
import asyncio

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings
from schemas import UploadResponse, ErrorResponse
from services.database import get_db, create_task, update_task_status, update_task_duration
from services.audio import audio_processor
from services.whisper import whisper_service

router = APIRouter(prefix="/api/upload", tags=["上传"])


def _run_async_task(task_id: str, file_path: str, filename: str):
    """
    在线程中运行异步任务
    
    使用新的事件循环来避免与主循环冲突
    """
    import asyncio
    
    # 创建新的事件循环
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        loop.run_until_complete(process_audio_task(task_id, file_path, filename))
    except Exception as e:
        logger.error(f"[线程任务失败] {task_id}: {e}")
    finally:
        loop.close()


async def process_audio_task(task_id: str, file_path: str, filename: str):
    """
    后台处理音频任务
    
    流程：
    1. 获取音频时长
    2. 转换为 WAV 格式
    3. 调用 Whisper API 转写
    4. 分析话术技巧
    5. 生成归因报告
    """
    from services.database import (
        update_task_transcription,
        update_task_analysis
    )
    
    # 创建新的数据库会话
    db = next(get_db())
    try:
        logger.info(f"[{task_id}] 后台任务启动")
        
        # 步骤 1: 获取音频时长
        logger.info(f"[{task_id}] 开始处理音频")
        task = get_task_by_id(db, task_id)
        if task:
            update_task_status(db, task, "processing", 10)
        
        duration = audio_processor.get_duration(file_path)
        if duration:
            update_task_duration(db, get_task_by_id(db, task_id), duration)
            logger.info(f"[{task_id}] 音频时长：{duration:.1f}秒")
        
        # 步骤 2: 转换为 WAV 格式
        update_task_status(db, get_task_by_id(db, task_id), "processing", 30)
        wav_path = audio_processor.convert_to_wav(file_path)
        if not wav_path:
            raise Exception("音频转换失败")
        
        # 步骤 3: Whisper 转写
        logger.info(f"[{task_id}] 开始转写")
        update_task_status(db, get_task_by_id(db, task_id), "transcribing", 50)
        
        transcription_result = await whisper_service.transcribe(wav_path)
        if not transcription_result:
            raise Exception("Whisper 转写失败")
        
        # 更新转写结果
        task = get_task_by_id(db, task_id)
        update_task_transcription(
            db, task,
            transcription_result['text'],
            transcription_result['segments']
        )
        logger.info(f"[{task_id}] 转写完成，{len(transcription_result['text'])}字符")
        
        # 步骤 4: 话术分析
        logger.info(f"[{task_id}] 开始话术分析")
        update_task_status(db, get_task_by_id(db, task_id), "analyzing", 75)
        
        techniques_result = await whisper_service.analyze_speaking_techniques(
            transcription_result['text']
        )
        
        # 步骤 5: 生成归因报告
        logger.info(f"[{task_id}] 生成归因报告")
        attribution_result = await whisper_service.generate_attribution_report(
            transcription_result['text'],
            techniques_result or {}
        )
        
        # 构建报告数据
        report_data = {
            'task_id': task_id,
            'filename': filename,
            'duration': transcription_result.get('duration'),
            'transcription': transcription_result['text'],
            'segments': transcription_result['segments'],
            'speaking_techniques': techniques_result.get('speaking_techniques', []) if techniques_result else [],
            'attribution_analysis': attribution_result.get('attribution_analysis', []) if attribution_result else [],
            'suggestions': attribution_result.get('suggestions', []) if attribution_result else [],
            'summary': attribution_result.get('summary', '') if attribution_result else '',
            'created_at': datetime.utcnow().isoformat()
        }
        
        # 更新任务完成
        task = get_task_by_id(db, task_id)
        update_task_analysis(db, task, attribution_result or {}, report_data)
        logger.info(f"[{task_id}] 任务完成")
        
        # 清理临时 WAV 文件
        if wav_path and wav_path != file_path:
            audio_processor.cleanup(wav_path)
        
    except Exception as e:
        logger.error(f"[{task_id}] 处理失败：{e}")
        task = get_task_by_id(db, task_id)
        if task:
            update_task_status(db, task, "failed", 0, str(e))
    finally:
        # 关闭数据库会话
        db.close()
        logger.info(f"[{task_id}] 数据库会话已关闭")


def get_task_by_id(db, task_id: str):
    """辅助函数：根据 task_id 获取任务"""
    from sqlalchemy.orm import Session
    from models import Task
    if isinstance(db, Session):
        return db.query(Task).filter(Task.task_id == task_id).first()
    return None


@router.post("", response_model=UploadResponse)
async def upload_audio(
    file: UploadFile = File(..., description="音频文件（MP3/WAV/M4A，最大 2GB）"),
    background_tasks: BackgroundTasks = None
):
    """
    上传音频文件
    
    - **file**: 音频文件（支持 MP3、WAV、M4A 格式）
    - **最大文件大小**: 2GB
    - **返回**: task_id 用于后续查询进度
    """
    # 验证文件
    if not file.filename:
        raise HTTPException(status_code=400, detail="未提供文件名")
    
    ext = Path(file.filename).suffix.lower().lstrip('.')
    allowed = settings.allowed_extensions.split(',')
    if ext not in allowed:
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(
                error="不支持的文件格式",
                detail=f"支持的格式：{', '.join(allowed)}"
            ).model_dump()
        )
    
    # 生成唯一 task_id 和保存路径
    task_id = str(uuid.uuid4())
    save_path = os.path.join(settings.upload_dir, f"{task_id}_{file.filename}")
    
    # 保存文件
    try:
        with open(save_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        file_size = os.path.getsize(save_path)
        
        # 验证文件大小
        if file_size > settings.max_file_size:
            os.remove(save_path)
            return JSONResponse(
                status_code=400,
                content=ErrorResponse(
                    error="文件过大",
                    detail=f"最大支持 {settings.max_file_size / 1024 / 1024:.1f}MB"
                ).model_dump()
            )
        
        # 创建数据库记录
        db = next(get_db())
        try:
            task = create_task(db, task_id, file.filename, save_path, file_size)
            logger.info(f"文件上传成功：{task_id}, {file.filename}, {file_size}字节")
            
            # 使用 threading 启动后台任务（可靠方案）
            import threading
            thread = threading.Thread(
                target=_run_async_task,
                args=(task_id, save_path, file.filename),
                daemon=True
            )
            thread.start()
            logger.info(f"后台任务线程已启动：{task_id}")
            
        finally:
            db.close()
            logger.info(f"数据库会话已关闭")
        
        return UploadResponse(
            task_id=task_id,
            filename=file.filename,
            file_size=file_size,
            status="pending",
            message="文件上传成功，开始处理"
        )
        
    except Exception as e:
        logger.error(f"上传失败：{e}")
        # 清理可能存在的文件
        if os.path.exists(save_path):
            os.remove(save_path)
        raise HTTPException(status_code=500, detail=f"上传失败：{str(e)}")
