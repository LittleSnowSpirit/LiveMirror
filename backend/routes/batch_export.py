"""
批量导出路由
支持多选报告、批量导出为 ZIP、自定义格式、进度显示、历史记录、异步导出
"""

import os
import uuid
import asyncio
import tempfile
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Query
from fastapi.responses import StreamingResponse, JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
import sys

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db
from models import Danmu, DanmuBatch, User
from routes.auth import get_current_user
from services.export_service import (
    ExportService,
    AsyncExportTask,
    get_async_task_manager
)

router = APIRouter(prefix="/export", tags=["批量导出"])


# ==================== Pydantic 模型 ====================
from enum import Enum

class ExportFormatEnum(str, Enum):
    """导出格式枚举"""
    JSON = "json"
    MARKDOWN = "markdown"
    PDF = "pdf"


class BatchExportRequest(BaseModel):
    """批量导出请求"""
    batch_ids: List[str] = Field(..., description="要导出的批次 ID 列表")
    export_format: ExportFormatEnum = Field(default=ExportFormatEnum.JSON, description="导出格式")
    include_metadata: bool = Field(default=True, description="是否包含元数据")
    async_export: bool = Field(default=False, description="是否异步导出（大文件推荐）")


class BatchExportResponse(BaseModel):
    """批量导出响应"""
    task_id: Optional[str] = None
    status: str  # pending, processing, completed, failed
    message: str
    download_url: Optional[str] = None
    progress: int = 0  # 0-100
    total_files: int = 0
    processed_files: int = 0


class ExportTaskStatusResponse(BaseModel):
    """导出任务状态响应"""
    task_id: str
    status: str
    progress: int
    total_files: int
    processed_files: int
    download_url: Optional[str] = None
    error_message: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None


class ExportHistoryItem(BaseModel):
    """导出历史记录项"""
    task_id: str
    export_format: str
    file_count: int
    status: str
    created_at: str
    completed_at: Optional[str] = None
    download_url: Optional[str] = None


class ExportHistoryResponse(BaseModel):
    """导出历史记录响应"""
    total: int
    items: List[ExportHistoryItem]


# ==================== 导出历史记录存储 ====================
# 注意：生产环境应该使用数据库存储
export_history: Dict[int, List[Dict]] = {}  # user_id -> [export_records]


def add_to_history(user_id: int, record: Dict):
    """添加导出记录到历史"""
    if user_id not in export_history:
        export_history[user_id] = []
    export_history[user_id].append(record)


def get_user_history(user_id: int, limit: int = 50) -> List[Dict]:
    """获取用户导出历史"""
    if user_id not in export_history:
        return []
    return export_history[user_id][-limit:]


# ==================== 工具函数 ====================
def generate_temp_file(content: bytes, suffix: str = ".tmp") -> str:
    """生成临时文件"""
    fd, path = tempfile.mkstemp(suffix=suffix)
    try:
        os.write(fd, content)
        os.close(fd)
        return path
    except Exception:
        os.close(fd)
        os.unlink(path)
        raise


async def process_batch_export(
    task_id: str,
    user_id: int,
    batch_ids: List[str],
    export_format: str,
    db: Session
):
    """异步处理批量导出任务"""
    task_manager = get_async_task_manager()
    export_service = ExportService(db)
    
    try:
        task_manager.update_progress(task_id, 0, "processing")
        
        files_to_zip = []
        total_batches = len(batch_ids)
        
        for i, batch_id in enumerate(batch_ids):
            # 获取批次信息
            batch_info = export_service.get_batch_info(batch_id)
            
            # 获取弹幕数据
            danmus = export_service.get_danmus_for_export(batch_id=batch_id)
            
            # 准备元数据
            metadata = {
                "export_time": datetime.utcnow().isoformat(),
                "batch_id": batch_id,
                "batch_name": batch_info.filename if batch_info else f"Batch_{batch_id}",
                "total_count": len(danmus),
                "user_id": user_id
            }
            
            # 导出文件
            if export_format == "json":
                content = export_service.export_to_json(danmus, metadata)
                filename = f"{batch_id}.json"
            elif export_format == "markdown":
                content = export_service.export_to_markdown(danmus, metadata)
                filename = f"{batch_id}.md"
            elif export_format == "pdf":
                content = export_service.export_to_pdf(danmus, metadata)
                filename = f"{batch_id}.pdf"
            else:
                content = export_service.export_to_json(danmus, metadata)
                filename = f"{batch_id}.json"
            
            files_to_zip.append({
                "name": filename,
                "content": content
            })
            
            # 更新进度
            task_manager.update_progress(task_id, i + 1)
            
            # 短暂暂停避免阻塞
            await asyncio.sleep(0.1)
        
        # 创建 ZIP 压缩包
        if len(files_to_zip) == 1:
            # 单个文件直接返回
            zip_content = files_to_zip[0]["content"]
            if isinstance(zip_content, str):
                zip_content = zip_content.encode('utf-8')
        else:
            # 多个文件打包为 ZIP
            zip_content = export_service.create_zip_archive(
                files_to_zip,
                archive_name=f"export_{task_id}.zip"
            )
        
        # 保存文件到临时目录
        temp_dir = tempfile.gettempdir()
        if len(files_to_zip) == 1:
            filename = files_to_zip[0]["name"]
        else:
            filename = f"export_{task_id}.zip"
        
        file_path = os.path.join(temp_dir, filename)
        with open(file_path, 'wb') as f:
            f.write(zip_content)
        
        # 生成下载 URL（实际项目中应该使用文件存储服务）
        download_url = f"/api/export/download/{task_id}/{filename}"
        
        # 完成任务
        task_manager.complete_task(task_id, download_url)
        
        # 添加到历史记录
        add_to_history(user_id, {
            "task_id": task_id,
            "export_format": export_format,
            "file_count": len(batch_ids),
            "status": "completed",
            "created_at": task_manager.get_task(task_id)["created_at"].isoformat(),
            "completed_at": datetime.utcnow().isoformat(),
            "download_url": download_url,
            "file_path": file_path
        })
        
    except Exception as e:
        # 任务失败
        task_manager.fail_task(task_id, str(e))
        
        # 添加到历史记录
        add_to_history(user_id, {
            "task_id": task_id,
            "export_format": export_format,
            "file_count": len(batch_ids),
            "status": "failed",
            "created_at": task_manager.get_task(task_id)["created_at"].isoformat() if task_manager.get_task(task_id) else datetime.utcnow().isoformat(),
            "completed_at": datetime.utcnow().isoformat(),
            "error_message": str(e)
        })


# ==================== 路由 ====================
@router.post("/batch", response_model=BatchExportResponse)
async def batch_export(
    request: BatchExportRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    批量导出分析报告
    
    - 支持多选报告（batch_ids 列表）
    - 支持自定义格式（JSON/Markdown/PDF）
    - 支持异步导出（大文件推荐）
    - 返回任务 ID 用于查询进度
    """
    if not request.batch_ids:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="至少需要选择一个批次"
        )
    
    # 生成任务 ID
    task_id = str(uuid.uuid4())
    
    # 创建任务
    task_manager = get_async_task_manager()
    task_info = task_manager.create_task(
        task_id=task_id,
        user_id=current_user.id,
        export_format=request.export_format.value,
        batch_ids=request.batch_ids,
        total_files=len(request.batch_ids)
    )
    
    if request.async_export or len(request.batch_ids) > 5:
        # 异步导出
        background_tasks.add_task(
            process_batch_export,
            task_id,
            current_user.id,
            request.batch_ids,
            request.export_format.value,
            db
        )
        
        return BatchExportResponse(
            task_id=task_id,
            status="pending",
            message="导出任务已创建，正在后台处理",
            progress=0,
            total_files=len(request.batch_ids),
            processed_files=0
        )
    else:
        # 同步导出（小文件）
        try:
            await process_batch_export(
                task_id,
                current_user.id,
                request.batch_ids,
                request.export_format.value,
                db
            )
            
            task_info = task_manager.get_task(task_id)
            
            return BatchExportResponse(
                task_id=task_id,
                status=task_info["status"],
                message="导出完成",
                download_url=task_info["result_url"],
                progress=100,
                total_files=len(request.batch_ids),
                processed_files=len(request.batch_ids)
            )
        except Exception as e:
            return BatchExportResponse(
                task_id=task_id,
                status="failed",
                message=f"导出失败：{str(e)}",
                progress=0,
                total_files=len(request.batch_ids),
                processed_files=0
            )


@router.get("/task/{task_id}", response_model=ExportTaskStatusResponse)
def get_export_task_status(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """查询导出任务状态"""
    task_manager = get_async_task_manager()
    task_info = task_manager.get_task(task_id)
    
    if not task_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 检查权限
    if task_info["user_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问此任务"
        )
    
    return ExportTaskStatusResponse(
        task_id=task_info["task_id"],
        status=task_info["status"],
        progress=task_info["progress"],
        total_files=task_info["total_files"],
        processed_files=task_info["processed_files"],
        download_url=task_info["result_url"],
        error_message=task_info.get("error_message"),
        created_at=task_info["created_at"].isoformat(),
        completed_at=task_info["completed_at"].isoformat() if task_info["completed_at"] else None
    )


@router.get("/download/{task_id}/{filename}")
async def download_export_file(
    task_id: str,
    filename: str,
    current_user: User = Depends(get_current_user)
):
    """下载导出文件"""
    task_manager = get_async_task_manager()
    task_info = task_manager.get_task(task_id)
    
    if not task_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="任务不存在"
        )
    
    # 检查权限
    if task_info["user_id"] != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权下载此文件"
        )
    
    # 检查任务状态
    if task_info["status"] != "completed":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="任务尚未完成"
        )
    
    # 查找文件路径（从历史记录中）
    user_history = get_user_history(current_user.id)
    file_record = None
    for record in user_history:
        if record.get("task_id") == task_id:
            file_record = record
            break
    
    if not file_record or not file_record.get("file_path"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件不存在"
        )
    
    file_path = file_record["file_path"]
    
    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="文件已被删除或过期"
        )
    
    # 返回文件
    def iterfile():
        with open(file_path, mode="rb") as file_like:
            yield from file_like
    
    return StreamingResponse(
        iterfile(),
        media_type="application/octet-stream",
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


@router.get("/history", response_model=ExportHistoryResponse)
def get_export_history(
    limit: int = Query(default=50, ge=1, le=200, description="返回记录数量"),
    current_user: User = Depends(get_current_user)
):
    """获取导出历史记录"""
    history = get_user_history(current_user.id, limit)
    
    items = [
        ExportHistoryItem(
            task_id=item["task_id"],
            export_format=item["export_format"],
            file_count=item["file_count"],
            status=item["status"],
            created_at=item["created_at"],
            completed_at=item.get("completed_at"),
            download_url=item.get("download_url")
        )
        for item in history
    ]
    
    return ExportHistoryResponse(
        total=len(history),
        items=items
    )


@router.delete("/history/{task_id}")
def delete_export_history(
    task_id: str,
    current_user: User = Depends(get_current_user)
):
    """删除导出历史记录"""
    user_history = export_history.get(current_user.id, [])
    
    # 查找记录
    record_index = None
    for i, item in enumerate(user_history):
        if item.get("task_id") == task_id:
            record_index = i
            break
    
    if record_index is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="记录不存在"
        )
    
    # 删除文件
    record = user_history[record_index]
    if record.get("file_path") and os.path.exists(record["file_path"]):
        try:
            os.unlink(record["file_path"])
        except Exception:
            pass
    
    # 删除记录
    user_history.pop(record_index)
    
    return {"message": "记录已删除", "success": True}


@router.post("/cleanup")
def cleanup_old_exports(
    days: int = Query(default=7, ge=1, le=30, description="保留天数"),
    current_user: User = Depends(get_current_user)
):
    """清理过期的导出文件"""
    user_history = export_history.get(current_user.id, [])
    
    cutoff_date = datetime.utcnow() - timedelta(days=days)
    removed_count = 0
    
    to_remove = []
    for i, item in enumerate(user_history):
        created_at = datetime.fromisoformat(item["created_at"])
        if created_at < cutoff_date:
            # 删除文件
            if item.get("file_path") and os.path.exists(item["file_path"]):
                try:
                    os.unlink(item["file_path"])
                except Exception:
                    pass
            to_remove.append(i)
            removed_count += 1
    
    # 逆序删除避免索引问题
    for i in reversed(to_remove):
        user_history.pop(i)
    
    return {
        "message": f"已清理 {removed_count} 个过期记录",
        "removed_count": removed_count,
        "success": True
    }


@router.get("/formats")
def get_export_formats():
    """获取支持的导出格式"""
    return {
        "formats": [
            {"value": "json", "label": "JSON", "description": "结构化数据，适合程序处理"},
            {"value": "markdown", "label": "Markdown", "description": "可读性好的文本格式"},
            {"value": "pdf", "label": "PDF", "description": "便携式文档格式，适合打印"}
        ]
    }
