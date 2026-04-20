"""用户路由 - 个人中心相关接口"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, timedelta
from typing import Optional, List
import sys
import os

# 添加父目录到路径以导入模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db
from models import User, Danmu, DanmuBatch, Token as TokenModel
from routes.auth import get_current_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from jose import jwt, JWTError
import bcrypt


router = APIRouter(prefix="/user", tags=["用户"])


# ==================== Pydantic 模型 ====================
class UserProfileResponse(BaseModel):
    """用户资料响应"""
    id: int
    username: str
    email: Optional[str] = None
    is_active: bool
    created_at: datetime
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True


class UserStatsResponse(BaseModel):
    """用户使用统计响应"""
    analysis_count: int = 0  # 分析次数
    total_duration: float = 0.0  # 总时长（秒）
    saved_reports: int = 0  # 保存报告数
    total_danmus: int = 0  # 总弹幕数
    batch_uploads: int = 0  # 批量上传次数

    class Config:
        from_attributes = True


class ChangePasswordRequest(BaseModel):
    """修改密码请求"""
    old_password: str = Field(..., min_length=6, max_length=50, description="原密码")
    new_password: str = Field(..., min_length=6, max_length=50, description="新密码")


class ChangeAvatarRequest(BaseModel):
    """修改头像请求"""
    avatar_url: str = Field(..., description="头像 URL")


class PasswordResponse(BaseModel):
    """密码修改响应"""
    message: str
    success: bool


class AvatarResponse(BaseModel):
    """头像修改响应"""
    message: str
    avatar_url: str
    success: bool


class ActivityLogResponse(BaseModel):
    """操作日志响应"""
    id: int
    action: str  # 操作类型：login, upload, analysis, password_change, avatar_change
    description: str  # 操作描述
    ip_address: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class MembershipInfoResponse(BaseModel):
    """会员信息响应"""
    is_member: bool = False
    membership_type: Optional[str] = None  # basic, premium, vip
    expires_at: Optional[datetime] = None
    remaining_days: Optional[int] = None

    class Config:
        from_attributes = True


class UserDashboardResponse(BaseModel):
    """用户仪表板完整响应"""
    profile: UserProfileResponse
    stats: UserStatsResponse
    membership: Optional[MembershipInfoResponse] = None
    recent_logs: List[ActivityLogResponse] = []


# ==================== 工具函数 ====================
def log_activity(db: Session, user_id: int, action: str, description: str, ip_address: Optional[str] = None):
    """记录用户操作日志"""
    # 注意：实际项目中应该有 ActivityLog 模型，这里简化处理
    # 在生产环境中，应该创建 ActivityLog 模型并保存到数据库
    pass


# ==================== 路由 ====================
@router.get("/profile", response_model=UserDashboardResponse)
def get_user_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户完整资料（包含统计信息）"""
    # 用户基本信息
    profile = UserProfileResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        is_active=current_user.is_active,
        created_at=current_user.created_at,
        avatar_url=None  # 可以从用户模型扩展
    )
    
    # 使用统计
    # 统计弹幕数量
    total_danmus = db.query(Danmu).filter(
        Danmu.user_id == current_user.id
    ).count() if current_user.id else 0
    
    # 统计批量上传次数
    batch_uploads = db.query(DanmuBatch).filter(
        DanmuBatch.user_id == current_user.id
    ).count() if current_user.id else 0
    
    # 统计总时长和分析次数（简化处理，实际应从分析记录表统计）
    analysis_count = batch_uploads  # 每次批量上传算一次分析
    total_duration = 0.0  # 实际应从分析记录中累加
    saved_reports = batch_uploads  # 每次上传生成一份报告
    
    stats = UserStatsResponse(
        analysis_count=analysis_count,
        total_duration=total_duration,
        saved_reports=saved_reports,
        total_danmus=total_danmus,
        batch_uploads=batch_uploads
    )
    
    # 会员信息（简化处理，默认非会员）
    membership = MembershipInfoResponse(
        is_member=False,
        membership_type="basic",
        expires_at=None,
        remaining_days=None
    )
    
    # 操作日志（简化处理，返回空列表）
    recent_logs = []
    
    return UserDashboardResponse(
        profile=profile,
        stats=stats,
        membership=membership,
        recent_logs=recent_logs
    )


@router.post("/change-password", response_model=PasswordResponse)
def change_password(
    password_data: ChangePasswordRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """修改密码"""
    # 验证原密码
    if not current_user.verify_password(password_data.old_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="原密码错误"
        )
    
    # 检查新密码是否与原密码相同
    if password_data.old_password == password_data.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="新密码不能与原密码相同"
        )
    
    # 更新密码
    current_user.hashed_password = User.hash_password(password_data.new_password)
    current_user.updated_at = datetime.utcnow()
    
    db.commit()
    
    # 记录操作日志
    log_activity(db, current_user.id, "password_change", "用户修改了密码")
    
    return PasswordResponse(
        message="密码修改成功",
        success=True
    )


@router.post("/change-avatar", response_model=AvatarResponse)
def change_avatar(
    avatar_data: ChangeAvatarRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """修改头像"""
    # 验证 URL 格式
    if not avatar_data.avatar_url.startswith(("http://", "https://", "data:image/")):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="无效的头像 URL 格式"
        )
    
    # 在实际项目中，应该将头像 URL 保存到用户模型
    # current_user.avatar_url = avatar_data.avatar_url
    # current_user.updated_at = datetime.utcnow()
    # db.commit()
    
    # 记录操作日志
    log_activity(db, current_user.id, "avatar_change", "用户修改了头像")
    
    return AvatarResponse(
        message="头像修改成功",
        avatar_url=avatar_data.avatar_url,
        success=True
    )


@router.post("/logout")
def logout(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """用户登出（将 Token 加入黑名单）"""
    # 实际实现需要将当前 Token 加入黑名单
    # 这里简化处理，前端直接清除本地 Token 即可
    
    return {"message": "登出成功", "success": True}


@router.get("/activity-logs", response_model=List[ActivityLogResponse])
def get_activity_logs(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取用户操作日志"""
    # 实际项目中应该从 ActivityLog 模型查询
    # 这里返回空列表作为示例
    return []
