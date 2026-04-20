"""
主播培训 API 接口
提供培训管理的 RESTful API
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime

from backend.services.training import (
    training_service,
    SkillLevel,
    TrainingStatus,
    AssessmentCategory
)


router = APIRouter(prefix="/api/training", tags=["training"])


# ==================== 请求/响应模型 ====================

class AssessmentCategoryRequest(BaseModel):
    """评估类别请求"""
    category: str = Field(..., description="评估类别")
    score: float = Field(..., ge=0, le=100, description="评分 (0-100)")


class AssessmentCreateRequest(BaseModel):
    """能力评估创建请求"""
    anchor_id: str = Field(..., description="主播 ID")
    assessor_id: str = Field(..., description="评估人 ID")
    categories: List[AssessmentCategoryRequest] = Field(..., description="评估类别列表")


class TrainingPlanCreateRequest(BaseModel):
    """培训计划创建请求"""
    anchor_id: str = Field(..., description="主播 ID")
    assessment_id: str = Field(..., description="评估 ID")
    duration_days: int = Field(default=30, ge=7, le=90, description="培训周期 (天)")


class CourseCompleteRequest(BaseModel):
    """课程完成请求"""
    plan_id: str = Field(..., description="培训计划 ID")
    course_id: str = Field(..., description="课程 ID")


class SimulatedStreamCreateRequest(BaseModel):
    """模拟直播创建请求"""
    anchor_id: str = Field(..., description="主播 ID")
    scenario: str = Field(..., description="模拟场景")
    duration_minutes: int = Field(default=30, ge=10, le=120, description="时长 (分钟)")


class SimulatedStreamCompleteRequest(BaseModel):
    """模拟直播完成请求"""
    stream_id: str = Field(..., description="模拟直播 ID")
    score: float = Field(..., ge=0, le=100, description="评分")
    feedback: List[str] = Field(default=[], description="反馈列表")
    metrics: Dict = Field(default={}, description="指标数据")


class GrowthRecordRequest(BaseModel):
    """成长记录请求"""
    anchor_id: str = Field(..., description="主播 ID")
    assessment_score: float = Field(..., ge=0, le=100, description="评估分数")
    completed_courses: int = Field(..., ge=0, description="完成课程数")
    simulated_streams: int = Field(..., ge=0, description="模拟直播次数")


# 响应模型
class AssessmentResponse(BaseModel):
    """评估响应"""
    id: str
    anchor_id: str
    assessor_id: str
    categories: Dict[str, float]
    overall_score: float
    weaknesses: List[str]
    strengths: List[str]
    created_at: str
    recommendations: List[str]


class TrainingPlanResponse(BaseModel):
    """培训计划响应"""
    id: str
    anchor_id: str
    assessment_id: str
    courses: List[str]
    duration_days: int
    start_date: str
    end_date: str
    status: str
    progress: float
    completed_courses: List[str]
    milestones: List[Dict]
    created_at: str
    updated_at: str


class TrainingCourseResponse(BaseModel):
    """培训课程响应"""
    id: str
    title: str
    description: str
    category: str
    difficulty: str
    duration_minutes: int
    content_url: str
    created_at: str
    enrolled_count: int
    completion_rate: float
    average_rating: float
    tags: List[str]


class SimulatedStreamResponse(BaseModel):
    """模拟直播响应"""
    id: str
    anchor_id: str
    scenario: str
    duration_minutes: int
    status: str
    started_at: Optional[str]
    ended_at: Optional[str]
    score: Optional[float]
    feedback: List[str]
    metrics: Dict
    recording_url: Optional[str]
    created_at: str


class GrowthCurveResponse(BaseModel):
    """成长曲线响应"""
    anchor_id: str
    records: List[Dict]
    created_at: str


class TrainingStatisticsResponse(BaseModel):
    """培训统计响应"""
    total_assessments: int
    total_plans: int
    completed_plans: int
    total_simulated_streams: int
    completed_streams: int
    average_stream_score: float
    total_courses: int


# ==================== 能力评估接口 ====================

@router.post("/assessments", response_model=AssessmentResponse, summary="创建能力评估")
async def create_assessment(request: AssessmentCreateRequest):
    """
    创建主播能力评估
    
    - **anchor_id**: 主播 ID
    - **assessor_id**: 评估人 ID
    - **categories**: 评估类别列表，包含类别和分数
    """
    categories_dict = {cat.category: cat.score for cat in request.categories}
    assessment = training_service.create_assessment(
        anchor_id=request.anchor_id,
        assessor_id=request.assessor_id,
        categories=categories_dict
    )
    return assessment.to_dict()


@router.get("/assessments/{assessment_id}", response_model=AssessmentResponse, summary="获取评估详情")
async def get_assessment(assessment_id: str):
    """获取能力评估详情"""
    assessment = training_service.get_assessment(assessment_id)
    if not assessment:
        raise HTTPException(status_code=404, detail="评估不存在")
    return assessment.to_dict()


@router.get("/anchors/{anchor_id}/assessments", response_model=List[AssessmentResponse], summary="获取主播评估历史")
async def get_anchor_assessments(anchor_id: str):
    """获取主播的所有能力评估记录"""
    assessments = training_service.get_anchor_assessments(anchor_id)
    return [a.to_dict() for a in assessments]


# ==================== 培训计划接口 ====================

@router.post("/plans", response_model=TrainingPlanResponse, summary="创建培训计划")
async def create_training_plan(request: TrainingPlanCreateRequest):
    """
    创建个性化培训计划
    
    根据能力评估结果自动生成个性化培训计划
    """
    plan = training_service.create_training_plan(
        anchor_id=request.anchor_id,
        assessment_id=request.assessment_id,
        duration_days=request.duration_days
    )
    if not plan:
        raise HTTPException(status_code=404, detail="评估不存在")
    return plan.to_dict()


@router.get("/plans/{plan_id}", response_model=TrainingPlanResponse, summary="获取培训计划")
async def get_training_plan(plan_id: str):
    """获取培训计划详情"""
    plan = training_service.get_training_plan(plan_id)
    if not plan:
        raise HTTPException(status_code=404, detail="培训计划不存在")
    return plan.to_dict()


@router.get("/anchors/{anchor_id}/plan", response_model=Optional[TrainingPlanResponse], summary="获取主播当前培训计划")
async def get_anchor_active_plan(anchor_id: str):
    """获取主播当前活跃的培训计划"""
    plan = training_service.get_anchor_active_plan(anchor_id)
    if plan:
        return plan.to_dict()
    return None


@router.post("/plans/{plan_id}/complete-course", response_model=TrainingPlanResponse, summary="标记课程完成")
async def complete_course(plan_id: str, request: CourseCompleteRequest):
    """在培训计划中标记课程完成"""
    if request.plan_id != plan_id:
        raise HTTPException(status_code=400, detail="培训计划 ID 不匹配")
    
    success = training_service.complete_course_in_plan(plan_id, request.course_id)
    if not success:
        raise HTTPException(status_code=400, detail="课程不在培训计划中")
    
    plan = training_service.get_training_plan(plan_id)
    return plan.to_dict()


# ==================== 培训课程库接口 ====================

@router.get("/courses", response_model=List[TrainingCourseResponse], summary="获取课程列表")
async def get_courses(
    category: Optional[str] = Query(None, description="课程类别"),
    difficulty: Optional[str] = Query(None, description="难度等级")
):
    """获取培训课程列表，支持按类别和难度筛选"""
    difficulty_enum = None
    if difficulty:
        try:
            difficulty_enum = SkillLevel(difficulty)
        except ValueError:
            raise HTTPException(status_code=400, detail="无效的难度等级")
    
    courses = training_service.get_all_courses(category, difficulty_enum)
    return [c.to_dict() for c in courses]


@router.get("/courses/{course_id}", response_model=TrainingCourseResponse, summary="获取课程详情")
async def get_course(course_id: str):
    """获取培训课程详情"""
    course = training_service.get_course(course_id)
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    return course.to_dict()


# ==================== 模拟直播接口 ====================

@router.post("/simulated-streams", response_model=SimulatedStreamResponse, summary="创建模拟直播")
async def create_simulated_stream(request: SimulatedStreamCreateRequest):
    """创建模拟直播练习"""
    stream = training_service.create_simulated_stream(
        anchor_id=request.anchor_id,
        scenario=request.scenario,
        duration_minutes=request.duration_minutes
    )
    return stream.to_dict()


@router.post("/simulated-streams/{stream_id}/start", response_model=SimulatedStreamResponse, summary="开始模拟直播")
async def start_simulated_stream(stream_id: str):
    """开始模拟直播练习"""
    success = training_service.start_simulated_stream(stream_id)
    if not success:
        raise HTTPException(status_code=404, detail="模拟直播不存在")
    
    stream = training_service.get_simulated_stream(stream_id)
    return stream.to_dict()


@router.post("/simulated-streams/{stream_id}/complete", response_model=SimulatedStreamResponse, summary="完成模拟直播")
async def complete_simulated_stream(stream_id: str, request: SimulatedStreamCompleteRequest):
    """完成模拟直播并记录评分"""
    if request.stream_id != stream_id:
        raise HTTPException(status_code=400, detail="模拟直播 ID 不匹配")
    
    success = training_service.complete_simulated_stream(
        stream_id=stream_id,
        score=request.score,
        feedback=request.feedback,
        metrics=request.metrics
    )
    if not success:
        raise HTTPException(status_code=404, detail="模拟直播不存在")
    
    stream = training_service.get_simulated_stream(stream_id)
    return stream.to_dict()


@router.get("/simulated-streams/{stream_id}", response_model=SimulatedStreamResponse, summary="获取模拟直播详情")
async def get_simulated_stream(stream_id: str):
    """获取模拟直播详情"""
    stream = training_service.get_simulated_stream(stream_id)
    if not stream:
        raise HTTPException(status_code=404, detail="模拟直播不存在")
    return stream.to_dict()


@router.get("/anchors/{anchor_id}/simulated-streams", response_model=List[SimulatedStreamResponse], summary="获取主播模拟直播历史")
async def get_anchor_simulated_streams(anchor_id: str):
    """获取主播的所有模拟直播记录"""
    streams = training_service.get_anchor_simulated_streams(anchor_id)
    return [s.to_dict() for s in streams]


# ==================== 成长曲线接口 ====================

@router.post("/growth", response_model=GrowthCurveResponse, summary="记录成长数据")
async def record_growth(request: GrowthRecordRequest):
    """记录主播成长数据"""
    training_service.record_growth(
        anchor_id=request.anchor_id,
        assessment_score=request.assessment_score,
        completed_courses=request.completed_courses,
        simulated_streams=request.simulated_streams
    )
    
    curve = training_service.get_growth_curve(request.anchor_id)
    return {
        "anchor_id": request.anchor_id,
        "records": curve,
        "created_at": datetime.now().isoformat()
    }


@router.get("/anchors/{anchor_id}/growth", response_model=GrowthCurveResponse, summary="获取成长曲线")
async def get_growth_curve(anchor_id: str):
    """获取主播成长曲线数据"""
    records = training_service.get_growth_curve(anchor_id)
    return {
        "anchor_id": anchor_id,
        "records": records,
        "created_at": datetime.now().isoformat()
    }


# ==================== 统计接口 ====================

@router.get("/statistics", response_model=TrainingStatisticsResponse, summary="获取培训统计")
async def get_training_statistics(anchor_id: Optional[str] = Query(None, description="主播 ID")):
    """获取培训统计数据"""
    stats = training_service.get_training_statistics(anchor_id)
    return stats
