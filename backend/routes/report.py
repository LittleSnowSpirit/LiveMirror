"""
数据报表管理 API 路由 - LiveMirror
"""

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import json

from backend.services.report_generator import (
    get_service,
    ReportType,
    ExportFormat,
    ReportData
)

router = APIRouter(prefix="/api/report", tags=["数据报表"])

service = get_service()


# ============== 数据模型 ==============

class ReportGenerateRequest(BaseModel):
    """生成报表请求"""
    report_type: str = Field(..., description="报表类型：daily/weekly/monthly")
    start_date: Optional[str] = Field(None, description="开始日期 (ISO 格式)")
    end_date: Optional[str] = Field(None, description="结束日期 (ISO 格式)")
    template_id: Optional[str] = Field(None, description="模板 ID")


class ReportExportRequest(BaseModel):
    """导出报表请求"""
    report_id: str = Field(..., description="报表 ID")
    format: str = Field(..., description="导出格式：pdf/excel/json/csv")
    output_path: Optional[str] = Field(None, description="输出路径")


class TemplateCreateRequest(BaseModel):
    """创建模板请求"""
    name: str = Field(..., description="模板名称")
    report_type: str = Field(..., description="报表类型：daily/weekly/monthly")
    sections: List[Dict[str, Any]] = Field(..., description="章节配置")
    is_default: bool = Field(default=False, description="是否默认模板")


class TemplateUpdateRequest(BaseModel):
    """更新模板请求"""
    name: Optional[str] = Field(None, description="模板名称")
    sections: Optional[List[Dict[str, Any]]] = Field(None, description="章节配置")


class ScheduleCreateRequest(BaseModel):
    """创建定时任务请求"""
    report_type: str = Field(..., description="报表类型：daily/weekly/monthly")
    cron_expression: str = Field(..., description="Cron 表达式")
    template_id: Optional[str] = Field(None, description="模板 ID")
    export_format: str = Field(default="pdf", description="导出格式")
    send_email: bool = Field(default=False, description="是否发送邮件")
    email_recipients: List[str] = Field(default=[], description="邮件接收者")
    send_wechat: bool = Field(default=False, description="是否发送微信")


class ScheduleUpdateRequest(BaseModel):
    """更新定时任务请求"""
    cron_expression: Optional[str] = Field(None, description="Cron 表达式")
    template_id: Optional[str] = Field(None, description="模板 ID")
    export_format: Optional[str] = Field(None, description="导出格式")
    send_email: Optional[bool] = Field(None, description="是否发送邮件")
    email_recipients: Optional[List[str]] = Field(None, description="邮件接收者")
    send_wechat: Optional[bool] = Field(None, description="是否发送微信")
    enabled: Optional[bool] = Field(None, description="是否启用")


# ============== 报表生成接口 ==============

@router.post("/generate", summary="生成报表")
async def generate_report(request: ReportGenerateRequest):
    """生成指定类型的报表"""
    try:
        report_type = ReportType(request.report_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"无效的报表类型：{e}")
    
    # 解析日期
    start_date = None
    end_date = None
    
    if request.start_date:
        try:
            start_date = datetime.fromisoformat(request.start_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="无效的开始日期格式")
    
    if request.end_date:
        try:
            end_date = datetime.fromisoformat(request.end_date)
        except ValueError:
            raise HTTPException(status_code=400, detail="无效的结束日期格式")
    
    # 生成报表
    report_data = service.generate_report(
        report_type=report_type,
        start_date=start_date,
        end_date=end_date,
        template_id=request.template_id
    )
    
    return {
        "success": True,
        "message": "报表生成成功",
        "data": {
            "report_id": report_data.report_id,
            "report_type": report_data.report_type.value,
            "period": {
                "start": report_data.period_start.isoformat(),
                "end": report_data.period_end.isoformat()
            },
            "generated_at": report_data.generated_at.isoformat(),
            "overall_summary": report_data.overall_summary,
            "sections": [
                {
                    "title": section.title,
                    "summary": section.summary,
                    "metrics": [
                        {
                            "name": m.name,
                            "value": m.value,
                            "unit": m.unit,
                            "change_rate": m.change_rate,
                            "trend": m.trend
                        }
                        for m in section.metrics
                    ]
                }
                for section in report_data.sections
            ]
        }
    }


@router.post("/generate/daily", summary="生成日报")
async def generate_daily_report(
    date: Optional[str] = Query(None, description="指定日期 (默认今天)"),
    template_id: Optional[str] = Query(None, description="模板 ID")
):
    """快速生成日报"""
    start_date = None
    if date:
        try:
            start_date = datetime.fromisoformat(date)
            start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        except ValueError:
            raise HTTPException(status_code=400, detail="无效的日期格式")
    
    report_data = service.generate_report(
        report_type=ReportType.DAILY,
        start_date=start_date,
        template_id=template_id
    )
    
    return {
        "success": True,
        "message": "日报生成成功",
        "data": {
            "report_id": report_data.report_id,
            "period": start_date.strftime("%Y-%m-%d") if start_date else datetime.now().strftime("%Y-%m-%d"),
            "summary": report_data.overall_summary
        }
    }


@router.post("/generate/weekly", summary="生成周报")
async def generate_weekly_report(
    week_start: Optional[str] = Query(None, description="周一日期 (默认本周一)"),
    template_id: Optional[str] = Query(None, description="模板 ID")
):
    """快速生成周报"""
    start_date = None
    if week_start:
        try:
            start_date = datetime.fromisoformat(week_start)
        except ValueError:
            raise HTTPException(status_code=400, detail="无效的日期格式")
    
    report_data = service.generate_report(
        report_type=ReportType.WEEKLY,
        start_date=start_date,
        template_id=template_id
    )
    
    return {
        "success": True,
        "message": "周报生成成功",
        "data": {
            "report_id": report_data.report_id,
            "period": f"{report_data.period_start.strftime('%Y-%m-%d')} 至 {report_data.period_end.strftime('%Y-%m-%d')}",
            "summary": report_data.overall_summary
        }
    }


@router.post("/generate/monthly", summary="生成月报")
async def generate_monthly_report(
    month: Optional[str] = Query(None, description="指定月份 (YYYY-MM, 默认本月)"),
    template_id: Optional[str] = Query(None, description="模板 ID")
):
    """快速生成月报"""
    start_date = None
    if month:
        try:
            start_date = datetime.strptime(month, "%Y-%m")
            start_date = start_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        except ValueError:
            raise HTTPException(status_code=400, detail="无效的月份格式")
    
    report_data = service.generate_report(
        report_type=ReportType.MONTHLY,
        start_date=start_date,
        template_id=template_id
    )
    
    return {
        "success": True,
        "message": "月报生成成功",
        "data": {
            "report_id": report_data.report_id,
            "period": f"{report_data.period_start.strftime('%Y-%m')} 全月",
            "summary": report_data.overall_summary
        }
    }


# ============== 报表查询接口 ==============

@router.get("/list", summary="查询报表列表")
async def list_reports(
    report_type: Optional[str] = Query(None, description="报表类型筛选"),
    limit: int = Query(20, ge=1, le=100, description="每页数量"),
    offset: int = Query(0, ge=0, description="偏移量")
):
    """查询报表列表"""
    rtype = None
    if report_type:
        try:
            rtype = ReportType(report_type)
        except ValueError:
            raise HTTPException(status_code=400, detail="无效的报表类型")
    
    reports = service.list_reports(rtype, limit, offset)
    
    return {
        "success": True,
        "data": {
            "reports": [
                {
                    "report_id": r["report_id"],
                    "report_type": r["report_type"],
                    "period": f"{r['period_start']} 至 {r['period_end']}",
                    "generated_at": r["generated_at"],
                    "summary": r["overall_summary"]
                }
                for r in reports
            ],
            "pagination": {
                "limit": limit,
                "offset": offset,
                "total": len(service.reports)
            }
        }
    }


@router.get("/{report_id}", summary="获取报表详情")
async def get_report(report_id: str):
    """获取指定报表的详细信息"""
    report = service.get_report(report_id)
    
    if not report:
        raise HTTPException(status_code=404, detail="报表不存在")
    
    return {
        "success": True,
        "data": report
    }


# ============== 报表导出接口 ==============

@router.post("/export", summary="导出报表")
async def export_report(request: ReportExportRequest):
    """导出报表为指定格式"""
    try:
        export_format = ExportFormat(request.format)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"无效的导出格式：{e}")
    
    try:
        output_path = service.export_report(
            report_id=request.report_id,
            format=export_format,
            output_path=request.output_path
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    
    return {
        "success": True,
        "message": "报表导出成功",
        "data": {
            "report_id": request.report_id,
            "format": request.format,
            "output_path": output_path
        }
    }


@router.get("/{report_id}/export/{format}", summary="快速导出报表")
async def quick_export(report_id: str, format: str):
    """快速导出报表"""
    try:
        export_format = ExportFormat(format)
    except ValueError:
        raise HTTPException(status_code=400, detail="无效的导出格式")
    
    try:
        output_path = service.export_report(report_id, export_format)
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
async def list_templates(
    report_type: Optional[str] = Query(None, description="报表类型筛选")
):
    """查询所有可用模板"""
    rtype = None
    if report_type:
        try:
            rtype = ReportType(report_type)
        except ValueError:
            raise HTTPException(status_code=400, detail="无效的报表类型")
    
    templates = service.list_templates(rtype)
    
    return {
        "success": True,
        "data": {
            "templates": [
                {
                    "template_id": tid,
                    "name": t["name"],
                    "type": t["type"],
                    "is_default": t.get("is_default", False),
                    "sections_count": len(t.get("sections", [])),
                    "created_at": t.get("created_at")
                }
                for tid, t in templates.items()
            ] if isinstance(templates, dict) else [
                {
                    "template_id": i,
                    **t
                }
                for i, t in enumerate(templates)
            ]
        }
    }


@router.post("/templates", summary="创建自定义模板")
async def create_template(request: TemplateCreateRequest):
    """创建自定义报表模板"""
    try:
        report_type = ReportType(request.report_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"无效的报表类型：{e}")
    
    template_id = service.create_template(
        name=request.name,
        report_type=report_type,
        sections=request.sections,
        is_default=request.is_default
    )
    
    return {
        "success": True,
        "message": "模板创建成功",
        "data": {
            "template_id": template_id,
            "name": request.name
        }
    }


@router.put("/templates/{template_id}", summary="更新模板")
async def update_template(template_id: str, request: TemplateUpdateRequest):
    """更新模板配置"""
    updates = {}
    if request.name:
        updates["name"] = request.name
    if request.sections:
        updates["sections"] = request.sections
    
    success = service.update_template(template_id, updates)
    
    if not success:
        raise HTTPException(status_code=404, detail="模板不存在")
    
    return {
        "success": True,
        "message": "模板更新成功"
    }


@router.delete("/templates/{template_id}", summary="删除模板")
async def delete_template(template_id: str):
    """删除自定义模板"""
    success = service.delete_template(template_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="模板不存在或为默认模板")
    
    return {
        "success": True,
        "message": "模板删除成功"
    }


# ============== 定时任务接口 ==============

@router.get("/schedules", summary="查询定时任务列表")
async def list_schedules():
    """查询所有定时报表任务"""
    schedules = service.list_schedules()
    
    return {
        "success": True,
        "data": {
            "schedules": schedules
        }
    }


@router.post("/schedules", summary="创建定时任务")
async def create_schedule(request: ScheduleCreateRequest):
    """创建定时报表生成任务"""
    try:
        report_type = ReportType(request.report_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"无效的报表类型：{e}")
    
    try:
        export_format = ExportFormat(request.export_format)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"无效的导出格式：{e}")
    
    schedule_id = service.create_schedule(
        report_type=report_type,
        cron_expression=request.cron_expression,
        template_id=request.template_id,
        export_format=export_format,
        send_email=request.send_email,
        email_recipients=request.email_recipients,
        send_wechat=request.send_wechat
    )
    
    return {
        "success": True,
        "message": "定时任务创建成功",
        "data": {
            "schedule_id": schedule_id,
            "report_type": request.report_type,
            "cron": request.cron_expression
        }
    }


@router.put("/schedules/{schedule_id}", summary="更新定时任务")
async def update_schedule(schedule_id: str, request: ScheduleUpdateRequest):
    """更新定时任务配置"""
    updates = {}
    if request.cron_expression:
        updates["cron_expression"] = request.cron_expression
    if request.template_id:
        updates["template_id"] = request.template_id
    if request.export_format:
        try:
            updates["export_format"] = ExportFormat(request.export_format).value
        except ValueError:
            raise HTTPException(status_code=400, detail="无效的导出格式")
    if request.send_email is not None:
        updates["send_email"] = request.send_email
    if request.email_recipients is not None:
        updates["email_recipients"] = request.email_recipients
    if request.send_wechat is not None:
        updates["send_wechat"] = request.send_wechat
    if request.enabled is not None:
        updates["enabled"] = request.enabled
    
    success = service.update_schedule(schedule_id, updates)
    
    if not success:
        raise HTTPException(status_code=404, detail="定时任务不存在")
    
    return {
        "success": True,
        "message": "定时任务更新成功"
    }


@router.delete("/schedules/{schedule_id}", summary="删除定时任务")
async def delete_schedule(schedule_id: str):
    """删除定时任务"""
    success = service.delete_schedule(schedule_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="定时任务不存在")
    
    return {
        "success": True,
        "message": "定时任务删除成功"
    }


@router.post("/schedules/{schedule_id}/toggle", summary="启/停定时任务")
async def toggle_schedule(schedule_id: str):
    """切换定时任务启用状态"""
    schedules = service.list_schedules()
    schedule = next((s for s in schedules if s["schedule_id"] == schedule_id), None)
    
    if not schedule:
        raise HTTPException(status_code=404, detail="定时任务不存在")
    
    new_state = not schedule["enabled"]
    success = service.update_schedule(schedule_id, {"enabled": new_state})
    
    if not success:
        raise HTTPException(status_code=500, detail="更新失败")
    
    return {
        "success": True,
        "message": f"定时任务已{'启用' if new_state else '停用'}",
        "data": {
            "schedule_id": schedule_id,
            "enabled": new_state
        }
    }


# ============== 统计接口 ==============

@router.get("/statistics", summary="获取报表统计")
async def get_statistics():
    """获取报表系统使用统计"""
    return {
        "success": True,
        "data": service.get_statistics()
    }
