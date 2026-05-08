"""
数据库操作服务
"""
from datetime import datetime, timezone
from typing import Optional
from sqlalchemy.orm import Session

from config import settings
from database import Base, SessionLocal, engine
from models import Task

def init_db():
    """初始化数据库，创建所有表"""
    Base.metadata.create_all(bind=engine)


def get_db() -> Session:
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_task(
    db: Session,
    task_id: str,
    filename: str,
    file_path: str,
    file_size: int,
    source_type: str = "upload",
    source_url: str | None = None,
) -> Task:
    """创建新任务"""
    task = Task(
        task_id=task_id,
        filename=filename,
        file_path=file_path,
        file_size=file_size,
        source_type=source_type,
        source_url=source_url,
        status="pending",
        current_step="pending",
        provider=settings.transcription_provider,
        progress=0,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task


def get_task(db: Session, task_id: str) -> Optional[Task]:
    """获取任务"""
    return db.query(Task).filter(Task.task_id == task_id).first()


def update_task_status(
    db: Session,
    task: Task,
    status: str,
    progress: int = None,
    error_message: str = None,
    current_step: str = None,
):
    """更新任务状态"""
    task.status = status
    task.current_step = current_step or status
    if task.started_at is None and status not in {"pending", "failed"}:
        task.started_at = datetime.now(timezone.utc)
    if progress is not None:
        task.progress = progress
    if error_message is not None:
        task.error_message = error_message
    db.commit()
    db.refresh(task)

    if status == "failed" and task.user_id:
        try:
            from services.notification_service import create_notification
            create_notification(
                db, task.user_id, "task_failed", "分析失败",
                f"文件 {task.filename} 的分析失败",
                link=f"/report/{task.task_id}",
                metadata={"task_id": task.task_id},
            )
        except Exception:
            pass


def update_task_transcription(db: Session, task: Task, transcription: str, segments: list):
    """更新任务转写结果"""
    task.transcription = transcription
    task.transcription_segments = segments
    task.status = "analyzing"
    task.current_step = "analyzing"
    task.progress = 70
    db.commit()
    db.refresh(task)


def update_task_analysis(db: Session, task: Task, analysis_result: dict, report_data: dict):
    """更新任务分析结果"""
    task.analysis_result = analysis_result
    task.report_data = report_data
    task.status = "completed"
    task.current_step = "completed"
    task.progress = 100
    task.completed_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(task)

    if task.user_id:
        try:
            from services.notification_service import create_notification
            create_notification(
                db, task.user_id, "task_completed", "分析完成",
                f"文件 {task.filename} 的分析已完成",
                link=f"/report/{task.task_id}",
                metadata={"task_id": task.task_id},
            )
        except Exception:
            pass


def update_task_duration(db: Session, task: Task, duration: float):
    """更新音频时长"""
    task.duration = duration
    db.commit()
    db.refresh(task)
