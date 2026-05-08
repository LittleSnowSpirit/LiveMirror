"""数据模型"""
import random
import uuid

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float, Text, ForeignKey, Index, Date
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime, timezone, date as date_type
from typing import Optional
from database import Base
import bcrypt


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    """用户模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    # 个人资料
    avatar_url = Column(String(500), nullable=True)
    nickname = Column(String(100), nullable=True)
    bio = Column(String(500), nullable=True)

    # 关联弹幕
    danmus = relationship("Danmu", back_populates="user", cascade="all, delete-orphan")

    def verify_password(self, plain_password: str) -> bool:
        """验证密码"""
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            self.hashed_password.encode('utf-8')
        )

    @staticmethod
    def hash_password(plain_password: str) -> str:
        """密码加密"""
        return bcrypt.hashpw(
            plain_password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')


class Token(Base):
    """Token 黑名单模型（可选，用于注销）"""
    __tablename__ = "tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String(500), unique=True, index=True, nullable=False)
    user_id = Column(Integer, nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_revoked = Column(Boolean, default=False)
    created_at = Column(DateTime, default=utc_now)


class Danmu(Base):
    """弹幕模型"""
    __tablename__ = "danmus"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    
    # 弹幕内容
    content = Column(Text, nullable=False)
    
    # 时间信息（秒，相对于直播开始）
    timestamp = Column(Float, nullable=False, index=True)
    
    # 用户信息
    username = Column(String(100), nullable=True, index=True)
    user_level = Column(Integer, default=1)  # 用户等级
    
    # 情感分析结果
    sentiment = Column(String(20), default="neutral")  # positive, negative, neutral
    sentiment_score = Column(Float, default=0.0)  # -1.0 到 1.0
    
    # 弹幕类型
    danmu_type = Column(String(50), default="normal")  # normal, highlight, controversy, question, praise
    
    # 互动数据
    like_count = Column(Integer, default=0)
    reply_count = Column(Integer, default=0)
    
    # 关联的话术片段 ID（可选）
    speech_segment_id = Column(Integer, nullable=True, index=True)
    
    # 元数据
    is_key_danmu = Column(Boolean, default=False)  # 是否关键弹幕
    key_type = Column(String(50), nullable=True)  # climax(高潮), controversy(争议), question(提问), praise(赞赏)
    
    created_at = Column(DateTime, default=utc_now, index=True)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
    
    # 关联
    user = relationship("User", back_populates="danmus")
    
    # 复合索引优化查询
    __table_args__ = (
        Index('idx_danmu_timestamp_type', 'timestamp', 'danmu_type'),
        Index('idx_danmu_sentiment', 'sentiment', 'sentiment_score'),
        Index('idx_danmu_key', 'is_key_danmu', 'key_type'),
    )
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "content": self.content,
            "timestamp": self.timestamp,
            "username": self.username,
            "user_level": self.user_level,
            "sentiment": self.sentiment,
            "sentiment_score": self.sentiment_score,
            "danmu_type": self.danmu_type,
            "like_count": self.like_count,
            "reply_count": self.reply_count,
            "speech_segment_id": self.speech_segment_id,
            "is_key_danmu": self.is_key_danmu,
            "key_type": self.key_type,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class DanmuBatch(Base):
    """弹幕批量上传记录模型"""
    __tablename__ = "danmu_batches"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # 批次信息
    batch_id = Column(String(100), unique=True, index=True, nullable=False)
    source_type = Column(String(50), default="upload")  # upload, realtime, import
    
    # 文件信息
    filename = Column(String(255), nullable=True)
    file_format = Column(String(20), default="json")  # json, csv
    
    # 统计信息
    total_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)
    
    # 时间范围
    start_timestamp = Column(Float, nullable=True)
    end_timestamp = Column(Float, nullable=True)
    
    # 状态
    status = Column(String(20), default="processing")  # processing, completed, failed
    error_message = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=utc_now)
    completed_at = Column(DateTime, nullable=True)
    
    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "batch_id": self.batch_id,
            "source_type": self.source_type,
            "filename": self.filename,
            "file_format": self.file_format,
            "total_count": self.total_count,
            "success_count": self.success_count,
            "failed_count": self.failed_count,
            "start_timestamp": self.start_timestamp,
            "end_timestamp": self.end_timestamp,
            "status": self.status,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


# ==================== Core upload and report models ====================

from sqlalchemy import JSON as SAJSON


class Task(Base):
    """Processing task for an uploaded media file."""

    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(100), unique=True, index=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, nullable=False, default=0)
    duration = Column(Float, nullable=True)

    status = Column(String(32), nullable=False, default="pending", index=True)
    current_step = Column(String(64), nullable=False, default="pending")
    provider = Column(String(64), nullable=True)
    progress = Column(Integer, nullable=False, default=0)
    error_message = Column(Text, nullable=True)

    transcription = Column(Text, nullable=True)
    transcription_segments = Column(SAJSON, nullable=True)
    language = Column(String(20), nullable=True)
    analysis_result = Column(SAJSON, nullable=True)
    report_data = Column(SAJSON, nullable=True)

    created_at = Column(DateTime, default=utc_now, index=True)
    started_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)
    completed_at = Column(DateTime, nullable=True)
    data_quality_score = Column(Float, nullable=True)

    reports = relationship("AnalysisReport", back_populates="task", cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        return {
            "task_id": self.task_id,
            "filename": self.filename,
            "file_size": self.file_size,
            "duration": self.duration,
            "status": self.status,
            "current_step": self.current_step,
            "provider": self.provider,
            "progress": self.progress,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
        }


class AnalysisReport(Base):
    """Persisted report payload generated from a task."""

    __tablename__ = "analysis_reports"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String(100), ForeignKey("tasks.task_id"), nullable=False, index=True)
    report_data = Column(SAJSON, nullable=False, default=dict)
    created_at = Column(DateTime, default=utc_now, index=True)

    task = relationship("Task", back_populates="reports")


class ExcellentExample(Base):
    """优秀话术示例模型"""
    __tablename__ = "excellent_examples"

    id = Column(Integer, primary_key=True, index=True)
    speech_type = Column(String(50), nullable=False, index=True)
    content = Column(Text, nullable=False)
    score = Column(Float, nullable=False)
    emotion_impact = Column(Float, nullable=False)
    engagement_rate = Column(Float, nullable=False)
    session_id = Column(String(100), nullable=True)
    timestamp = Column(Float, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "speech_type": self.speech_type,
            "content": self.content,
            "score": self.score,
            "emotion_impact": self.emotion_impact,
            "engagement_rate": self.engagement_rate,
            "session_id": self.session_id,
            "timestamp": self.timestamp,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# ==================== 用户配额和使用记录 ====================

class UserQuota(Base):
    """用户配额模型 — 每周免费分析次数"""
    __tablename__ = "user_quotas"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, index=True)
    weekly_limit = Column(Integer, nullable=False, default=2)
    used_this_week = Column(Integer, nullable=False, default=0)
    week_start_date = Column(Date, nullable=False)

    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "weekly_limit": self.weekly_limit,
            "used_this_week": self.used_this_week,
            "remaining": max(0, self.weekly_limit - self.used_this_week),
            "week_start_date": self.week_start_date.isoformat() if self.week_start_date else None,
        }


class UsageRecord(Base):
    """使用记录模型 — 每次分析的记录"""
    __tablename__ = "usage_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    task_id = Column(String(100), ForeignKey("tasks.task_id"), nullable=True, index=True)
    created_at = Column(DateTime, default=utc_now, index=True)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "task_id": self.task_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


# 添加 Task 表的复合索引
Task.__table_args__ = (
    Index('idx_task_user_created', 'user_id', 'created_at'),
)


def _generate_token() -> str:
    return uuid.uuid4().hex[:8]


def _generate_access_code() -> str:
    return str(random.randint(1000, 9999))


class ShareLink(Base):
    """分享链接模型"""
    __tablename__ = "share_links"

    id = Column(String(32), primary_key=True, default=lambda: uuid.uuid4().hex)
    task_id = Column(String(100), ForeignKey("tasks.task_id"), nullable=False, index=True)
    token = Column(String(8), unique=True, index=True, nullable=False, default=_generate_token)
    access_code = Column(String(4), nullable=False, default=_generate_access_code)
    template_config = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)
    expires_at = Column(DateTime, nullable=True)
    view_count = Column(Integer, default=0)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    task = relationship("Task", foreign_keys=[task_id])
    user = relationship("User", foreign_keys=[user_id])

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "task_id": self.task_id,
            "token": self.token,
            "access_code": self.access_code,
            "template_config": self.template_config,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "view_count": self.view_count,
            "user_id": self.user_id,
        }
