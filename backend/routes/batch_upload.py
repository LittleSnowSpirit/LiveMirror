"""
批量上传接口
支持一次上传多个音频文件
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from loguru import logger
import uuid
import os
import shutil
from pathlib import Path
from typing import List
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings
from schemas import UploadResponse
from services.database import get_db, create_task
from routes.upload import process_audio_task
import asyncio

router = APIRouter(prefix="/api/batch", tags=["批量上传"])


@router.post("/upload")
async def batch_upload_audio(
    files: List[UploadFile] = File(..., description="音频文件列表"),
):
    """
    批量上传音频文件
    
    - **files**: 音频文件列表（支持 MP3、WAV、M4A 格式）
    - **最大文件数**: 10 个
    - **返回**: task_id 列表
    """
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="最多支持 10 个文件同时上传")
    
    results = []
    db = next(get_db())
    
    try:
        for file in files:
            # 验证文件
            if not file.filename:
                continue
            
            ext = Path(file.filename).suffix.lower().lstrip('.')
            allowed = settings.allowed_extensions.split(',')
            if ext not in allowed:
                logger.warning(f"跳过不支持的格式：{file.filename}")
                continue
            
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
                    logger.warning(f"文件过大：{file.filename}")
                    continue
                
                # 创建数据库记录
                task = create_task(db, task_id, file.filename, save_path, file_size)
                
                # 后台处理任务
                asyncio.create_task(process_audio_task(task_id, save_path, file.filename))
                
                results.append({
                    'filename': file.filename,
                    'task_id': task_id,
                    'file_size': file_size,
                    'status': 'pending'
                })
                
                logger.info(f"批量上传：{task_id}, {file.filename}")
                
            except Exception as e:
                logger.error(f"批量上传失败：{e}")
                continue
    
    finally:
        db.close()
    
    return JSONResponse(
        status_code=200,
        content={
            'count': len(results),
            'tasks': results,
            'message': f'成功上传 {len(results)} 个文件'
        }
    )
