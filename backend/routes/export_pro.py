"""
专业数据导出 API 接口
提供 Excel、Word、PowerPoint、PDF 等多种格式的导出功能
"""

from fastapi import APIRouter, HTTPException, Query, Body
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Optional, Any
import os

from backend.services.export_pro import (
    export_pro_service,
    ExportFormat,
    ExportTemplate,
    ExportJob
)


router = APIRouter(prefix="/api/export", tags=["export"])


# ==================== 请求/响应模型 ====================

class TemplateCreateRequest(BaseModel):
    """模板创建请求"""
    name: str = Field(..., min_length=1, max_length=100, description="模板名称")
    format: str = Field(..., description="导出格式 (excel/word/powerpoint/pdf/csv/json/custom)")
    config: Dict = Field(..., description="模板配置")
    description: str = Field(default="", max_length=500, description="模板描述")


class TemplateUpdateRequest(BaseModel):
    """模板更新请求"""
    name: Optional[str] = Field(None, description="模板名称")
    config: Optional[Dict] = Field(None, description="模板配置")
    description: Optional[str] = Field(None, description="模板描述")
    enabled: Optional[bool] = Field(None, description="是否启用")


class JobCreateRequest(BaseModel):
    """导出任务创建请求"""
    name: str = Field(..., min_length=1, max_length=100, description="任务名称")
    format: str = Field(..., description="导出格式")
    data_source: str = Field(..., description="数据源")
    template_id: Optional[str] = Field(None, description="模板 ID")
    schedule: Optional[str] = Field(None, description="定时调度 cron 表达式")


class JobUpdateRequest(BaseModel):
    """导出任务更新请求"""
    name: Optional[str] = Field(None, description="任务名称")
    data_source: Optional[str] = Field(None, description="数据源")
    template_id: Optional[str] = Field(None, description="模板 ID")
    schedule: Optional[str] = Field(None, description="定时调度")
    enabled: Optional[bool] = Field(None, description="是否启用")


class ExportRequest(BaseModel):
    """导出请求"""
    format: str = Field(..., description="导出格式")
    data: Any = Field(..., description="要导出的数据")
    template_id: Optional[str] = Field(None, description="模板 ID")
    output_path: Optional[str] = Field(None, description="输出路径")


class TemplateResponse(BaseModel):
    """模板响应"""
    id: str
    name: str
    format: str
    config: Dict
    description: str
    created_at: str
    enabled: bool


class JobResponse(BaseModel):
    """导出任务响应"""
    id: str
    name: str
    format: str
    data_source: str
    template_id: Optional[str]
    schedule: Optional[str]
    enabled: bool
    created_at: str
    last_run: Optional[str]
    last_output_path: Optional[str]
    run_count: int


class ExportResponse(BaseModel):
    """导出响应"""
    success: bool
    output_path: Optional[str]
    info_path: Optional[str]
    format: str
    message: str
    error: Optional[str] = None


# ==================== 模板管理接口 ====================

@router.post("/templates", response_model=TemplateResponse, summary="创建导出模板")
async def create_template(request: TemplateCreateRequest):
    """
    创建新的导出模板
    
    - **name**: 模板名称
    - **format**: 导出格式 (excel/word/powerpoint/pdf/csv/json/custom)
    - **config**: 模板配置（JSON 对象）
    - **description**: 模板描述
    """
    try:
        template = export_pro_service.create_template(
            name=request.name,
            format=request.format,
            config=request.config,
            description=request.description
        )
        return TemplateResponse(**template.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/templates", response_model=List[TemplateResponse], summary="获取模板列表")
async def list_templates(
    format: Optional[str] = Query(None, description="按格式筛选"),
    enabled_only: bool = Query(False, description="是否只返回启用的模板")
):
    """
    获取所有导出模板
    
    - **format**: 可选，按格式筛选 (excel/word/powerpoint/pdf/csv/json/custom)
    - **enabled_only**: 是否只返回启用的模板
    """
    templates = export_pro_service.list_templates(
        format=format,
        enabled_only=enabled_only
    )
    return [TemplateResponse(**t.to_dict()) for t in templates]


@router.get("/templates/{template_id}", response_model=TemplateResponse, summary="获取模板详情")
async def get_template(template_id: str):
    """
    获取指定模板的详细信息
    """
    template = export_pro_service.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    return TemplateResponse(**template.to_dict())


@router.put("/templates/{template_id}", response_model=TemplateResponse, summary="更新模板")
async def update_template(template_id: str, request: TemplateUpdateRequest):
    """
    更新导出模板
    
    只更新提供的字段
    """
    template = export_pro_service.get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    updates = request.dict(exclude_unset=True)
    success = export_pro_service.update_template(template_id, updates)
    if not success:
        raise HTTPException(status_code=500, detail="更新模板失败")
    
    updated = export_pro_service.get_template(template_id)
    return TemplateResponse(**updated.to_dict())


@router.delete("/templates/{template_id}", summary="删除模板")
async def delete_template(template_id: str):
    """
    删除指定导出模板
    """
    success = export_pro_service.delete_template(template_id)
    if not success:
        raise HTTPException(status_code=404, detail="模板不存在")
    return {"message": "模板已删除"}


# ==================== 导出任务管理接口 ====================

@router.post("/jobs", response_model=JobResponse, summary="创建导出任务")
async def create_job(request: JobCreateRequest):
    """
    创建新的导出任务
    
    - **name**: 任务名称
    - **format**: 导出格式
    - **data_source**: 数据源标识
    - **template_id**: 可选的模板 ID
    - **schedule**: 可选的定时调度 cron 表达式
    """
    try:
        job = export_pro_service.create_job(
            name=request.name,
            format=request.format,
            data_source=request.data_source,
            template_id=request.template_id,
            schedule=request.schedule
        )
        return JobResponse(**job.to_dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/jobs", response_model=List[JobResponse], summary="获取导出任务列表")
async def list_jobs(
    format: Optional[str] = Query(None, description="按格式筛选"),
    enabled_only: bool = Query(False, description="是否只返回启用的任务")
):
    """
    获取所有导出任务
    
    - **format**: 可选，按格式筛选
    - **enabled_only**: 是否只返回启用的任务
    """
    jobs = export_pro_service.list_jobs(
        format=format,
        enabled_only=enabled_only
    )
    return [JobResponse(**j.to_dict()) for j in jobs]


@router.get("/jobs/{job_id}", response_model=JobResponse, summary="获取导出任务详情")
async def get_job(job_id: str):
    """
    获取指定导出任务的详细信息
    """
    job = export_pro_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="任务不存在")
    return JobResponse(**job.to_dict())


@router.put("/jobs/{job_id}", response_model=JobResponse, summary="更新导出任务")
async def update_job(job_id: str, request: JobUpdateRequest):
    """
    更新导出任务
    
    只更新提供的字段
    """
    job = export_pro_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    updates = request.dict(exclude_unset=True)
    success = export_pro_service.update_job(job_id, updates)
    if not success:
        raise HTTPException(status_code=500, detail="更新任务失败")
    
    updated = export_pro_service.get_job(job_id)
    return JobResponse(**updated.to_dict())


@router.delete("/jobs/{job_id}", summary="删除导出任务")
async def delete_job(job_id: str):
    """
    删除指定导出任务
    """
    success = export_pro_service.delete_job(job_id)
    if not success:
        raise HTTPException(status_code=404, detail="任务不存在")
    return {"message": "任务已删除"}


@router.post("/jobs/{job_id}/run", response_model=ExportResponse, summary="执行导出任务")
async def run_job(job_id: str, data: Any = Body(..., description="要导出的数据")):
    """
    立即执行导出任务
    
    - **job_id**: 任务 ID
    - **data**: 要导出的数据
    """
    job = export_pro_service.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    result = export_pro_service.run_job(job_id, data)
    
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "导出失败"))
    
    return ExportResponse(**result)


# ==================== 数据导出接口 ====================

@router.post("/export", response_model=ExportResponse, summary="直接导出数据")
async def export_data(request: ExportRequest):
    """
    直接导出数据，不使用预定义任务
    
    - **format**: 导出格式 (excel/word/powerpoint/pdf/csv/json/custom)
    - **data**: 要导出的数据
    - **template_id**: 可选的模板 ID
    - **output_path**: 可选的输出路径
    """
    template = None
    if request.template_id:
        template = export_pro_service.get_template(request.template_id)
        if not template:
            raise HTTPException(status_code=404, detail="模板不存在")
    
    result = export_pro_service.export_data(
        data=request.data,
        format=request.format,
        template=template,
        output_path=request.output_path
    )
    
    if not result.get("success"):
        raise HTTPException(status_code=500, detail=result.get("error", "导出失败"))
    
    return ExportResponse(**result)


@router.get("/export/{format}/download", summary="下载导出文件")
async def download_export(
    format: str,
    filename: str = Query(..., description="文件名")
):
    """
    下载导出文件
    
    - **format**: 文件格式
    - **filename**: 文件名
    """
    # 构建文件路径
    file_path = f"exports/{filename}"
    
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="文件不存在")
    
    # 设置 MIME 类型
    media_types = {
        "excel": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "word": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "powerpoint": "application/vnd.openxmlformats-officedocument.presentationml.presentation",
        "pdf": "application/pdf",
        "csv": "text/csv",
        "json": "application/json"
    }
    
    media_type = media_types.get(format.lower(), "application/octet-stream")
    
    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=filename
    )


# ==================== 定时任务接口 ====================

@router.get("/scheduled-jobs", response_model=List[Dict], summary="获取定时导出任务")
async def get_scheduled_jobs():
    """
    获取所有定时导出任务及其状态
    """
    return export_pro_service.check_and_run_scheduled_jobs()


@router.post("/scheduled-jobs/check", summary="检查并执行定时任务")
async def check_scheduled_jobs():
    """
    检查并执行所有到期的定时导出任务
    """
    results = export_pro_service.check_and_run_scheduled_jobs()
    return {
        "checked": len(results),
        "jobs": results
    }


# ==================== 导出统计接口 ====================

@router.get("/statistics", summary="获取导出统计")
async def get_export_statistics():
    """
    获取导出统计信息
    
    包含：
    - 模板总数
    - 任务总数
    - 按格式统计
    - 总导出次数
    """
    templates = export_pro_service.list_templates()
    jobs = export_pro_service.list_jobs()
    
    # 按格式统计
    format_counts = {}
    total_runs = 0
    for job in jobs:
        fmt = job.format
        format_counts[fmt] = format_counts.get(fmt, 0) + 1
        total_runs += job.run_count
    
    return {
        "total_templates": len(templates),
        "total_jobs": len(jobs),
        "jobs_by_format": format_counts,
        "total_export_runs": total_runs,
        "scheduled_jobs": len(export_pro_service.get_scheduled_jobs())
    }
