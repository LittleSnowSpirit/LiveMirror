"""
LiveMirror 多直播间对比接口
提供对比分析、数据导出等功能
"""

from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from pathlib import Path
import os
import time

from services.compare_analysis import (
    CompareAnalysisService,
    get_service,
    ComparisonResult
)

router = APIRouter(prefix="/api/compare", tags=["对比分析"])


class CompareRequest(BaseModel):
    """对比请求模型"""
    room_ids: List[str]
    include_emotion: bool = True
    include_ai_analysis: bool = True


class CompareResponse(BaseModel):
    """对比响应模型"""
    success: bool
    data: Optional[dict] = None
    message: str = ""
    elapsed_time: float = 0.0


@router.post("/", response_model=CompareResponse)
async def compare_rooms(request: CompareRequest):
    """
    多直播间对比分析
    
    Args:
        request: 对比请求，包含直播间 ID 列表
    
    Returns:
        对比分析结果
    """
    if not request.room_ids:
        raise HTTPException(status_code=400, detail="至少需要指定一个直播间 ID")
    
    if len(request.room_ids) < 2:
        raise HTTPException(status_code=400, detail="至少需要两个直播间进行对比")
    
    try:
        start_time = time.time()
        
        # 获取服务实例
        service = get_service()
        
        # 执行对比分析
        result = service.compare_rooms(request.room_ids)
        
        # 转换为字典响应
        from dataclasses import asdict
        response_data = {
            "timestamp": result.timestamp,
            "rooms": [asdict(room) for room in result.rooms],
            "metrics_comparison": result.metrics_comparison,
            "radar_data": result.radar_data,
            "emotion_curves": result.emotion_curves if request.include_emotion else {},
            "ai_analysis": result.ai_analysis if request.include_ai_analysis else {},
            "recommendations": result.recommendations
        }
        
        elapsed = time.time() - start_time
        
        return CompareResponse(
            success=True,
            data=response_data,
            message=f"成功对比{len(result.rooms)}个直播间",
            elapsed_time=round(elapsed, 2)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"对比分析失败：{str(e)}")


@router.get("/")
async def compare_rooms_get(
    room_ids: List[str] = Query(..., description="直播间 ID 列表，用逗号分隔")
):
    """
    多直播间对比分析（GET 方式）
    
    Args:
        room_ids: 直播间 ID 列表
    
    Returns:
        对比分析结果
    """
    if not room_ids:
        raise HTTPException(status_code=400, detail="至少需要指定一个直播间 ID")
    
    if len(room_ids) < 2:
        raise HTTPException(status_code=400, detail="至少需要两个直播间进行对比")
    
    try:
        start_time = time.time()
        
        # 获取服务实例
        service = get_service()
        
        # 执行对比分析
        result = service.compare_rooms(room_ids)
        
        # 转换为字典响应
        from dataclasses import asdict
        response_data = {
            "timestamp": result.timestamp,
            "rooms": [asdict(room) for room in result.rooms],
            "metrics_comparison": result.metrics_comparison,
            "radar_data": result.radar_data,
            "emotion_curves": result.emotion_curves,
            "ai_analysis": result.ai_analysis,
            "recommendations": result.recommendations
        }
        
        elapsed = time.time() - start_time
        
        return {
            "success": True,
            "data": response_data,
            "message": f"成功对比{len(result.rooms)}个直播间",
            "elapsed_time": round(elapsed, 2)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"对比分析失败：{str(e)}")


@router.post("/export/pdf")
async def export_pdf(request: CompareRequest, background_tasks: BackgroundTasks):
    """
    导出对比报告为 PDF
    
    Args:
        request: 对比请求
        background_tasks: 后台任务
    
    Returns:
        文件下载响应
    """
    if not request.room_ids:
        raise HTTPException(status_code=400, detail="至少需要指定一个直播间 ID")
    
    try:
        # 获取服务实例
        service = get_service()
        
        # 执行对比分析
        result = service.compare_rooms(request.room_ids)
        
        # 生成输出路径
        timestamp = result.timestamp.replace(":", "-").replace(".", "-")
        output_filename = f"compare_report_{timestamp}.pdf"
        output_dir = Path("reports")
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / output_filename
        
        # 导出 PDF
        success = service.export_to_pdf(result, str(output_path))
        
        if not success:
            # 尝试 JSON 格式
            output_filename = output_filename.replace(".pdf", ".json")
            output_path = output_dir / output_filename
            return {
                "success": True,
                "message": "PDF 导出失败，已降级为 JSON 格式",
                "file_path": str(output_path),
                "format": "json"
            }
        
        return {
            "success": True,
            "message": "PDF 报告生成成功",
            "file_path": str(output_path),
            "format": "pdf"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF 导出失败：{str(e)}")


@router.get("/export/pdf/{room_ids}")
async def export_pdf_get(room_ids: str):
    """
    导出对比报告为 PDF（GET 方式）
    
    Args:
        room_ids: 直播间 ID 列表（逗号分隔）
    
    Returns:
        文件下载响应
    """
    room_id_list = [rid.strip() for rid in room_ids.split(",")]
    
    if not room_id_list:
        raise HTTPException(status_code=400, detail="至少需要指定一个直播间 ID")
    
    try:
        # 获取服务实例
        service = get_service()
        
        # 执行对比分析
        result = service.compare_rooms(room_id_list)
        
        # 生成输出路径
        timestamp = result.timestamp.replace(":", "-").replace(".", "-")
        output_filename = f"compare_report_{timestamp}.pdf"
        output_dir = Path("reports")
        output_dir.mkdir(exist_ok=True)
        output_path = output_dir / output_filename
        
        # 导出 PDF
        success = service.export_to_pdf(result, str(output_path))
        
        if not success:
            return JSONResponse(
                content={
                    "success": False,
                    "message": "PDF 导出失败"
                },
                status_code=500
            )
        
        # 返回文件下载
        return FileResponse(
            str(output_path),
            media_type="application/pdf",
            filename=output_filename
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF 导出失败：{str(e)}")


@router.get("/metrics/{room_ids}")
async def get_metrics_comparison(room_ids: str):
    """
    获取直播间指标对比数据
    
    Args:
        room_ids: 直播间 ID 列表（逗号分隔）
    
    Returns:
        指标对比数据
    """
    room_id_list = [rid.strip() for rid in room_ids.split(",")]
    
    if not room_id_list:
        raise HTTPException(status_code=400, detail="至少需要指定一个直播间 ID")
    
    try:
        service = get_service()
        rooms = service.load_room_data(room_id_list)
        metrics = service.calculate_comparison_metrics(rooms)
        
        return {
            "success": True,
            "data": metrics,
            "count": len(rooms)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取指标失败：{str(e)}")


@router.get("/radar/{room_ids}")
async def get_radar_data(room_ids: str):
    """
    获取雷达图数据
    
    Args:
        room_ids: 直播间 ID 列表（逗号分隔）
    
    Returns:
        雷达图数据
    """
    room_id_list = [rid.strip() for rid in room_ids.split(",")]
    
    if not room_id_list:
        raise HTTPException(status_code=400, detail="至少需要指定一个直播间 ID")
    
    try:
        service = get_service()
        rooms = service.load_room_data(room_id_list)
        radar_data = service.generate_radar_data(rooms)
        
        return {
            "success": True,
            "data": radar_data,
            "indicators": [
                "内容质量",
                "互动效果",
                "节奏把控",
                "话术技巧",
                "观众留存"
            ]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取雷达图数据失败：{str(e)}")


@router.get("/emotion/{room_ids}")
async def get_emotion_curves(room_ids: str):
    """
    获取情绪曲线数据
    
    Args:
        room_ids: 直播间 ID 列表（逗号分隔）
    
    Returns:
        情绪曲线数据
    """
    room_id_list = [rid.strip() for rid in room_ids.split(",")]
    
    if not room_id_list:
        raise HTTPException(status_code=400, detail="至少需要指定一个直播间 ID")
    
    try:
        service = get_service()
        emotion_curves = service.generate_emotion_curves(room_id_list)
        
        return {
            "success": True,
            "data": emotion_curves
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取情绪曲线失败：{str(e)}")


@router.get("/analysis/{room_ids}")
async def get_ai_analysis(room_ids: str):
    """
    获取 AI 差异分析报告
    
    Args:
        room_ids: 直播间 ID 列表（逗号分隔）
    
    Returns:
        AI 分析报告
    """
    room_id_list = [rid.strip() for rid in room_ids.split(",")]
    
    if not room_id_list:
        raise HTTPException(status_code=400, detail="至少需要指定一个直播间 ID")
    
    try:
        service = get_service()
        rooms = service.load_room_data(room_id_list)
        ai_analysis = service.generate_ai_analysis(rooms)
        recommendations = service.generate_recommendations(rooms, ai_analysis)
        
        return {
            "success": True,
            "data": {
                "analysis": ai_analysis,
                "recommendations": recommendations
            }
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取 AI 分析失败：{str(e)}")


@router.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "service": "compare_analysis",
        "version": "1.0.0"
    }
