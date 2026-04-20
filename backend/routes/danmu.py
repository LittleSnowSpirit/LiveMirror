"""弹幕相关接口"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import csv
import io
import json

from database import get_db
from models import Danmu, DanmuBatch, User
from services.danmu_analysis import get_danmu_service

router = APIRouter(prefix="/api/danmu", tags=["弹幕"])
security = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """获取当前用户（可选，弹幕接口可以不需要认证）"""
    # 简化实现，实际应该验证 token
    # 这里返回 None 表示匿名用户也可以上传弹幕
    return None


@router.post("/upload", response_model=Dict[str, Any])
async def upload_danmu(
    file: UploadFile = File(..., description="弹幕文件（JSON 或 CSV）"),
    source_type: str = Form(default="upload"),
    db: Session = Depends(get_db)
):
    """
    上传弹幕文件
    
    支持 JSON 和 CSV 格式：
    - JSON: [{"timestamp": 10.5, "content": "你好", "username": "用户 1"}, ...]
    - CSV: timestamp,content,username,user_level,like_count,reply_count
    """
    try:
        # 读取文件内容
        content = await file.read()
        file_content = content.decode('utf-8')
        
        # 确定文件格式
        file_format = "json"
        if file.filename:
            if file.filename.endswith('.csv'):
                file_format = "csv"
            elif file.filename.endswith('.json'):
                file_format = "json"
        
        # 解析弹幕数据
        service = get_danmu_service()
        if file_format == "csv":
            danmus_data = service.parse_csv(file_content)
        else:
            danmus_data = service.parse_json(file_content)
        
        if not danmus_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="未能解析出有效的弹幕数据"
            )
        
        # 创建批次记录
        batch_id = str(uuid.uuid4())
        batch = DanmuBatch(
            batch_id=batch_id,
            source_type=source_type,
            filename=file.filename,
            file_format=file_format,
            total_count=len(danmus_data),
            status="processing"
        )
        db.add(batch)
        db.commit()
        
        # 处理弹幕数据
        success_count = 0
        failed_count = 0
        
        for danmu_data in danmus_data:
            try:
                # 情感分析
                content_text = danmu_data.get('content', '')
                sentiment, sentiment_score = service.analyze_sentiment(content_text)
                
                # 弹幕分类
                danmu_type = service.classify_danmu_type(content_text, sentiment, sentiment_score)
                
                # 关键弹幕检测
                is_key, key_type = service.detect_key_danmu(
                    content_text,
                    sentiment_score,
                    danmu_data.get('timestamp', 0)
                )
                
                # 创建弹幕记录
                danmu = Danmu(
                    content=content_text,
                    timestamp=danmu_data.get('timestamp', 0),
                    username=danmu_data.get('username'),
                    user_level=danmu_data.get('user_level', 1),
                    sentiment=sentiment,
                    sentiment_score=sentiment_score,
                    danmu_type=danmu_type,
                    like_count=danmu_data.get('like_count', 0),
                    reply_count=danmu_data.get('reply_count', 0),
                    speech_segment_id=danmu_data.get('speech_segment_id'),
                    is_key_danmu=is_key,
                    key_type=key_type
                )
                db.add(danmu)
                success_count += 1
            except Exception as e:
                failed_count += 1
                continue
        
        # 更新批次状态
        batch.success_count = success_count
        batch.failed_count = failed_count
        batch.status = "completed"
        batch.completed_at = datetime.utcnow()
        
        # 更新时间范围
        if danmus_data:
            timestamps = [d.get('timestamp', 0) for d in danmus_data]
            batch.start_timestamp = min(timestamps)
            batch.end_timestamp = max(timestamps)
        
        db.commit()
        db.refresh(batch)
        
        return {
            "success": True,
            "batch_id": batch_id,
            "total_count": len(danmus_data),
            "success_count": success_count,
            "failed_count": failed_count,
            "message": f"成功上传 {success_count} 条弹幕"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"上传失败：{str(e)}"
        )


@router.post("/batch", response_model=Dict[str, Any])
async def upload_danmu_batch(
    danmus: List[Dict[str, Any]],
    source_type: str = "upload",
    db: Session = Depends(get_db)
):
    """
    批量上传弹幕（JSON 格式）
    
    请求体格式：
    {
        "danmus": [
            {"timestamp": 10.5, "content": "你好", "username": "用户 1"},
            ...
        ],
        "source_type": "upload"
    }
    """
    try:
        if not danmus:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="弹幕数据不能为空"
            )
        
        # 创建批次记录
        batch_id = str(uuid.uuid4())
        batch = DanmuBatch(
            batch_id=batch_id,
            source_type=source_type,
            filename="batch_upload",
            file_format="json",
            total_count=len(danmus),
            status="processing"
        )
        db.add(batch)
        db.commit()
        
        # 处理弹幕数据
        service = get_danmu_service()
        success_count = 0
        failed_count = 0
        
        for danmu_data in danmus:
            try:
                content_text = danmu_data.get('content', '')
                if not content_text:
                    failed_count += 1
                    continue
                
                # 情感分析
                sentiment, sentiment_score = service.analyze_sentiment(content_text)
                
                # 弹幕分类
                danmu_type = service.classify_danmu_type(content_text, sentiment, sentiment_score)
                
                # 关键弹幕检测
                is_key, key_type = service.detect_key_danmu(
                    content_text,
                    sentiment_score,
                    danmu_data.get('timestamp', 0)
                )
                
                # 创建弹幕记录
                danmu = Danmu(
                    content=content_text,
                    timestamp=danmu_data.get('timestamp', 0),
                    username=danmu_data.get('username'),
                    user_level=danmu_data.get('user_level', 1),
                    sentiment=sentiment,
                    sentiment_score=sentiment_score,
                    danmu_type=danmu_type,
                    like_count=danmu_data.get('like_count', 0),
                    reply_count=danmu_data.get('reply_count', 0),
                    speech_segment_id=danmu_data.get('speech_segment_id'),
                    is_key_danmu=is_key,
                    key_type=key_type
                )
                db.add(danmu)
                success_count += 1
            except Exception as e:
                failed_count += 1
                continue
        
        # 更新批次状态
        batch.success_count = success_count
        batch.failed_count = failed_count
        batch.status = "completed"
        batch.completed_at = datetime.utcnow()
        
        if danmus:
            timestamps = [d.get('timestamp', 0) for d in danmus]
            batch.start_timestamp = min(timestamps)
            batch.end_timestamp = max(timestamps)
        
        db.commit()
        db.refresh(batch)
        
        return {
            "success": True,
            "batch_id": batch_id,
            "total_count": len(danmus),
            "success_count": success_count,
            "failed_count": failed_count
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量上传失败：{str(e)}"
        )


@router.get("/list", response_model=Dict[str, Any])
async def list_danmu(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    sentiment: Optional[str] = Query(None),
    danmu_type: Optional[str] = Query(None),
    is_key: Optional[bool] = Query(None),
    start_time: Optional[float] = Query(None),
    end_time: Optional[float] = Query(None),
    db: Session = Depends(get_db)
):
    """
    获取弹幕列表（分页）
    
    支持筛选：
    - sentiment: 情感类型 (positive, negative, neutral)
    - danmu_type: 弹幕类型 (normal, highlight, controversy, question, praise)
    - is_key: 是否关键弹幕
    - start_time/end_time: 时间范围
    """
    query = db.query(Danmu)
    
    # 筛选条件
    if sentiment:
        query = query.filter(Danmu.sentiment == sentiment)
    if danmu_type:
        query = query.filter(Danmu.danmu_type == danmu_type)
    if is_key is not None:
        query = query.filter(Danmu.is_key_danmu == is_key)
    if start_time is not None:
        query = query.filter(Danmu.timestamp >= start_time)
    if end_time is not None:
        query = query.filter(Danmu.timestamp <= end_time)
    
    # 总数
    total = query.count()
    
    # 分页
    offset = (page - 1) * page_size
    danmus = query.order_by(Danmu.timestamp).offset(offset).limit(page_size).all()
    
    return {
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": (total + page_size - 1) // page_size,
        "data": [danmu.to_dict() for danmu in danmus]
    }


@router.get("/timeline", response_model=Dict[str, Any])
async def get_danmu_timeline(
    interval: int = Query(30, ge=10, le=300, description="时间间隔（秒）"),
    db: Session = Depends(get_db)
):
    """
    获取弹幕热度时间轴
    """
    # 获取所有弹幕
    danmus = db.query(Danmu).all()
    
    service = get_danmu_service()
    danmus_data = [danmu.to_dict() for danmu in danmus]
    timeline = service.analyze_heatmap(danmus_data, interval_seconds=interval)
    
    return {
        "interval": interval,
        "total_points": len(timeline),
        "data": timeline
    }


@router.get("/summary", response_model=Dict[str, Any])
async def get_danmu_summary(
    db: Session = Depends(get_db)
):
    """
    获取弹幕分析摘要
    """
    danmus = db.query(Danmu).all()
    
    service = get_danmu_service()
    danmus_data = [danmu.to_dict() for danmu in danmus]
    summary = service.generate_summary(danmus_data)
    
    return summary


@router.get("/correlation", response_model=Dict[str, Any])
async def get_speech_correlation(
    db: Session = Depends(get_db)
):
    """
    获取弹幕与话术的关联分析
    """
    danmus = db.query(Danmu).all()
    
    # 这里假设有话术分析服务可以获取话术片段
    # 实际实现需要调用话术分析服务
    speech_segments = []  # TODO: 从话术分析服务获取
    
    service = get_danmu_service()
    danmus_data = [danmu.to_dict() for danmu in danmus]
    correlation = service.correlate_with_speech(danmus_data, speech_segments)
    
    return correlation


@router.get("/key", response_model=Dict[str, Any])
async def get_key_danmus(
    key_type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """
    获取关键弹幕
    """
    query = db.query(Danmu).filter(Danmu.is_key_danmu == True)
    
    if key_type:
        query = query.filter(Danmu.key_type == key_type)
    
    danmus = query.order_by(Danmu.timestamp).limit(limit).all()
    
    return {
        "total": len(danmus),
        "data": [danmu.to_dict() for danmu in danmus]
    }


@router.get("/batch/{batch_id}", response_model=Dict[str, Any])
async def get_batch_status(
    batch_id: str,
    db: Session = Depends(get_db)
):
    """
    获取批量上传状态
    """
    batch = db.query(DanmuBatch).filter(DanmuBatch.batch_id == batch_id).first()
    
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="批次不存在"
        )
    
    return batch.to_dict()


@router.delete("/batch/{batch_id}")
async def delete_batch(
    batch_id: str,
    db: Session = Depends(get_db)
):
    """
    删除批量上传记录及其关联的弹幕
    """
    batch = db.query(DanmuBatch).filter(DanmuBatch.batch_id == batch_id).first()
    
    if not batch:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="批次不存在"
        )
    
    # 删除关联的弹幕（如果实现了级联删除可以省略）
    # db.query(Danmu).filter(...).delete()
    
    db.delete(batch)
    db.commit()
    
    return {"success": True, "message": "批次已删除"}


@router.get("/export/csv")
async def export_danmu_csv(
    sentiment: Optional[str] = Query(None),
    danmu_type: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    """
    导出弹幕为 CSV 格式
    """
    query = db.query(Danmu)
    
    if sentiment:
        query = query.filter(Danmu.sentiment == sentiment)
    if danmu_type:
        query = query.filter(Danmu.danmu_type == danmu_type)
    
    danmus = query.order_by(Danmu.timestamp).all()
    
    # 生成 CSV
    output = io.StringIO()
    writer = csv.writer(output)
    
    # 表头
    writer.writerow([
        'timestamp', 'content', 'username', 'user_level',
        'sentiment', 'sentiment_score', 'danmu_type',
        'like_count', 'reply_count', 'is_key_danmu', 'key_type'
    ])
    
    # 数据
    for danmu in danmus:
        writer.writerow([
            danmu.timestamp,
            danmu.content,
            danmu.username,
            danmu.user_level,
            danmu.sentiment,
            danmu.sentiment_score,
            danmu.danmu_type,
            danmu.like_count,
            danmu.reply_count,
            danmu.is_key_danmu,
            danmu.key_type
        ])
    
    from fastapi.responses import StreamingResponse
    
    output.seek(0)
    return StreamingResponse(
        io.BytesIO(output.getvalue().encode('utf-8')),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=danmus.csv"}
    )
