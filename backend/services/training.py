"""
主播培训管理服务
提供主播能力评估、个性化培训计划、课程库、模拟直播、效果追踪和成长曲线功能
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional
import uuid
import math


class SkillLevel(Enum):
    """技能等级"""
    BEGINNER = "beginner"  # 初级
    INTERMEDIATE = "intermediate"  # 中级
    ADVANCED = "advanced"  # 高级
    EXPERT = "expert"  # 专家


class TrainingStatus(Enum):
    """培训状态"""
    NOT_STARTED = "not_started"  # 未开始
    IN_PROGRESS = "in_progress"  # 进行中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"  # 失败


class AssessmentCategory(Enum):
    """评估类别"""
    COMMUNICATION = "communication"  # 沟通能力
    PRODUCT_KNOWLEDGE = "product_knowledge"  # 产品知识
    SALES_SKILL = "sales_skill"  # 销售技巧
    AUDIENCE_ENGAGEMENT = "audience_engagement"  # 观众互动
    TECHNICAL_OPERATION = "technical_operation"  # 技术操作
    EMERGENCY_RESPONSE = "emergency_response"  # 应急处理


class AnchorAssessment:
    """主播能力评估模型"""
    
    def __init__(
        self,
        anchor_id: str,
        assessor_id: str,
        categories: Dict[str, float]
    ):
        self.id = str(uuid.uuid4())
        self.anchor_id = anchor_id
        self.assessor_id = assessor_id
        self.categories = categories  # {category: score}
        self.overall_score = self._calculate_overall()
        self.weaknesses = self._identify_weaknesses()
        self.strengths = self._identify_strengths()
        self.created_at = datetime.now()
        self.recommendations = self._generate_recommendations()
    
    def _calculate_overall(self) -> float:
        """计算总体评分"""
        if not self.categories:
            return 0.0
        return round(sum(self.categories.values()) / len(self.categories), 2)
    
    def _identify_weaknesses(self) -> List[str]:
        """识别薄弱环节"""
        if not self.categories:
            return []
        avg = sum(self.categories.values()) / len(self.categories)
        # 低于平均分 15% 或绝对分数低于 70 的视为薄弱环节
        return [cat for cat, score in self.categories.items() if score < avg * 0.85 or score < 70]
    
    def _identify_strengths(self) -> List[str]:
        """识别优势环节"""
        if not self.categories:
            return []
        avg = sum(self.categories.values()) / len(self.categories)
        return [cat for cat, score in self.categories.items() if score > avg * 1.2]
    
    def _generate_recommendations(self) -> List[str]:
        """生成改进建议"""
        recommendations = []
        category_advice = {
            "communication": "加强语言表达训练，练习清晰流畅的讲解",
            "product_knowledge": "深入学习产品知识，建立完整的产品体系认知",
            "sales_skill": "学习销售话术和技巧，提升转化率",
            "audience_engagement": "增加互动频率，学习调动观众情绪的方法",
            "technical_operation": "熟悉直播设备操作，进行技术演练",
            "emergency_response": "学习应急预案，提升临场应变能力"
        }
        for weakness in self.weaknesses:
            if weakness in category_advice:
                recommendations.append(category_advice[weakness])
        return recommendations
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            "id": self.id,
            "anchor_id": self.anchor_id,
            "assessor_id": self.assessor_id,
            "categories": self.categories,
            "overall_score": self.overall_score,
            "weaknesses": self.weaknesses,
            "strengths": self.strengths,
            "created_at": self.created_at.isoformat(),
            "recommendations": self.recommendations
        }


class TrainingCourse:
    """培训课程模型"""
    
    def __init__(
        self,
        title: str,
        description: str,
        category: str,
        difficulty: SkillLevel,
        duration_minutes: int,
        content_url: str
    ):
        self.id = str(uuid.uuid4())
        self.title = title
        self.description = description
        self.category = category
        self.difficulty = difficulty
        self.duration_minutes = duration_minutes
        self.content_url = content_url
        self.created_at = datetime.now()
        self.enrolled_count = 0
        self.completion_rate = 0.0
        self.average_rating = 0.0
        self.tags: List[str] = []
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category,
            "difficulty": self.difficulty.value,
            "duration_minutes": self.duration_minutes,
            "content_url": self.content_url,
            "created_at": self.created_at.isoformat(),
            "enrolled_count": self.enrolled_count,
            "completion_rate": self.completion_rate,
            "average_rating": self.average_rating,
            "tags": self.tags
        }


class TrainingPlan:
    """个性化培训计划模型"""
    
    def __init__(
        self,
        anchor_id: str,
        assessment_id: str,
        courses: List[str],
        duration_days: int = 30
    ):
        self.id = str(uuid.uuid4())
        self.anchor_id = anchor_id
        self.assessment_id = assessment_id
        self.courses = courses  # 课程 ID 列表
        self.duration_days = duration_days
        self.start_date = datetime.now()
        self.end_date = self.start_date + timedelta(days=duration_days)
        self.status = TrainingStatus.NOT_STARTED
        self.progress = 0.0
        self.completed_courses: List[str] = []
        self.milestones = self._generate_milestones()
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
    
    def _generate_milestones(self) -> List[Dict]:
        """生成培训里程碑"""
        milestones = []
        total = len(self.courses)
        if total == 0:
            return milestones
        
        checkpoint_count = min(4, total)
        for i in range(1, checkpoint_count + 1):
            course_idx = int((i / checkpoint_count) * total) - 1
            milestone_date = self.start_date + timedelta(days=int((i / checkpoint_count) * self.duration_days))
            milestones.append({
                "id": str(uuid.uuid4()),
                "name": f"阶段 {i} 完成",
                "target_course_index": course_idx,
                "target_date": milestone_date.isoformat(),
                "completed": False
            })
        return milestones
    
    def complete_course(self, course_id: str):
        """标记课程完成"""
        if course_id in self.courses and course_id not in self.completed_courses:
            self.completed_courses.append(course_id)
            self.progress = round(len(self.completed_courses) / len(self.courses) * 100, 2)
            self._update_milestones()
            self.updated_at = datetime.now()
            
            if len(self.completed_courses) == len(self.courses):
                self.status = TrainingStatus.COMPLETED
    
    def _update_milestones(self):
        """更新里程碑状态"""
        completed_count = len(self.completed_courses)
        total = len(self.courses)
        for milestone in self.milestones:
            target_idx = milestone["target_course_index"]
            if completed_count > target_idx:
                milestone["completed"] = True
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            "id": self.id,
            "anchor_id": self.anchor_id,
            "assessment_id": self.assessment_id,
            "courses": self.courses,
            "duration_days": self.duration_days,
            "start_date": self.start_date.isoformat(),
            "end_date": self.end_date.isoformat(),
            "status": self.status.value,
            "progress": self.progress,
            "completed_courses": self.completed_courses,
            "milestones": self.milestones,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class SimulatedStream:
    """模拟直播练习模型"""
    
    def __init__(
        self,
        anchor_id: str,
        scenario: str,
        duration_minutes: int
    ):
        self.id = str(uuid.uuid4())
        self.anchor_id = anchor_id
        self.scenario = scenario
        self.duration_minutes = duration_minutes
        self.status = "scheduled"
        self.started_at: Optional[datetime] = None
        self.ended_at: Optional[datetime] = None
        self.score: Optional[float] = None
        self.feedback: List[str] = []
        self.metrics: Dict = {}
        self.recording_url: Optional[str] = None
        self.created_at = datetime.now()
    
    def start(self):
        """开始模拟直播"""
        self.status = "in_progress"
        self.started_at = datetime.now()
    
    def end(self, score: float, feedback: List[str], metrics: Dict):
        """结束模拟直播"""
        self.status = "completed"
        self.ended_at = datetime.now()
        self.score = score
        self.feedback = feedback
        self.metrics = metrics
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            "id": self.id,
            "anchor_id": self.anchor_id,
            "scenario": self.scenario,
            "duration_minutes": self.duration_minutes,
            "status": self.status,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "score": self.score,
            "feedback": self.feedback,
            "metrics": self.metrics,
            "recording_url": self.recording_url,
            "created_at": self.created_at.isoformat()
        }


class AnchorGrowthRecord:
    """主播成长记录模型"""
    
    def __init__(self, anchor_id: str):
        self.id = str(uuid.uuid4())
        self.anchor_id = anchor_id
        self.records: List[Dict] = []
        self.created_at = datetime.now()
    
    def add_record(self, assessment_score: float, completed_courses: int, simulated_streams: int):
        """添加成长记录"""
        self.records.append({
            "date": datetime.now().isoformat(),
            "assessment_score": assessment_score,
            "completed_courses": completed_courses,
            "simulated_streams": simulated_streams
        })
    
    def get_growth_curve(self) -> List[Dict]:
        """获取成长曲线数据"""
        return self.records
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            "id": self.id,
            "anchor_id": self.anchor_id,
            "records": self.records,
            "created_at": self.created_at.isoformat()
        }


class TrainingService:
    """培训管理服务"""
    
    def __init__(self):
        self.assessments: Dict[str, AnchorAssessment] = {}
        self.courses: Dict[str, TrainingCourse] = {}
        self.plans: Dict[str, TrainingPlan] = {}
        self.simulated_streams: Dict[str, SimulatedStream] = {}
        self.growth_records: Dict[str, AnchorGrowthRecord] = {}
        self._init_default_courses()
    
    def _init_default_courses(self):
        """初始化默认课程库"""
        default_courses = [
            ("直播入门基础", "学习直播的基本流程和注意事项", "communication", SkillLevel.BEGINNER, 30),
            ("产品知识精讲", "深入了解产品特性和卖点", "product_knowledge", SkillLevel.INTERMEDIATE, 45),
            ("销售话术技巧", "掌握高效的销售沟通技巧", "sales_skill", SkillLevel.INTERMEDIATE, 40),
            ("观众互动方法", "学习如何调动观众情绪和参与度", "audience_engagement", SkillLevel.ADVANCED, 35),
            ("直播设备操作", "熟悉各类直播设备的使用", "technical_operation", SkillLevel.BEGINNER, 25),
            ("应急处理预案", "学习突发情况的应对方法", "emergency_response", SkillLevel.ADVANCED, 30),
            ("高级销售策略", "提升转化率的进阶技巧", "sales_skill", SkillLevel.EXPERT, 50),
            ("品牌建设与管理", "打造个人直播品牌", "communication", SkillLevel.EXPERT, 60),
        ]
        
        for title, desc, category, difficulty, duration in default_courses:
            course = TrainingCourse(
                title=title,
                description=desc,
                category=category,
                difficulty=difficulty,
                duration_minutes=duration,
                content_url=f"/courses/{category}/{title}"
            )
            course.tags = [category, difficulty.value]
            self.courses[course.id] = course
    
    def create_assessment(
        self,
        anchor_id: str,
        assessor_id: str,
        categories: Dict[str, float]
    ) -> AnchorAssessment:
        """创建能力评估"""
        assessment = AnchorAssessment(anchor_id, assessor_id, categories)
        self.assessments[assessment.id] = assessment
        return assessment
    
    def get_assessment(self, assessment_id: str) -> Optional[AnchorAssessment]:
        """获取评估详情"""
        return self.assessments.get(assessment_id)
    
    def get_anchor_assessments(self, anchor_id: str) -> List[AnchorAssessment]:
        """获取主播的所有评估"""
        return [a for a in self.assessments.values() if a.anchor_id == anchor_id]
    
    def create_training_plan(
        self,
        anchor_id: str,
        assessment_id: str,
        duration_days: int = 30
    ) -> Optional[TrainingPlan]:
        """创建个性化培训计划"""
        assessment = self.assessments.get(assessment_id)
        if not assessment:
            return None
        
        # 根据薄弱环节推荐课程
        recommended_courses = []
        for course_id, course in self.courses.items():
            if course.category in assessment.weaknesses:
                recommended_courses.append(course_id)
        
        # 如果没有薄弱环节，推荐一些进阶课程
        if not recommended_courses:
            for course_id, course in self.courses.items():
                if course.difficulty in [SkillLevel.INTERMEDIATE, SkillLevel.ADVANCED]:
                    recommended_courses.append(course_id)
                if len(recommended_courses) >= 5:
                    break
        
        plan = TrainingPlan(anchor_id, assessment_id, recommended_courses, duration_days)
        self.plans[plan.id] = plan
        return plan
    
    def get_training_plan(self, plan_id: str) -> Optional[TrainingPlan]:
        """获取培训计划"""
        return self.plans.get(plan_id)
    
    def get_anchor_active_plan(self, anchor_id: str) -> Optional[TrainingPlan]:
        """获取主播的活跃培训计划"""
        for plan in self.plans.values():
            if plan.anchor_id == anchor_id and plan.status != TrainingStatus.COMPLETED:
                return plan
        return None
    
    def complete_course_in_plan(self, plan_id: str, course_id: str) -> bool:
        """在培训计划中标记课程完成"""
        plan = self.plans.get(plan_id)
        if plan and course_id in plan.courses:
            plan.complete_course(course_id)
            return True
        return False
    
    def get_all_courses(
        self,
        category: Optional[str] = None,
        difficulty: Optional[SkillLevel] = None
    ) -> List[TrainingCourse]:
        """获取课程列表"""
        courses = list(self.courses.values())
        if category:
            courses = [c for c in courses if c.category == category]
        if difficulty:
            courses = [c for c in courses if c.difficulty == difficulty]
        return courses
    
    def get_course(self, course_id: str) -> Optional[TrainingCourse]:
        """获取课程详情"""
        return self.courses.get(course_id)
    
    def create_simulated_stream(
        self,
        anchor_id: str,
        scenario: str,
        duration_minutes: int = 30
    ) -> SimulatedStream:
        """创建模拟直播练习"""
        stream = SimulatedStream(anchor_id, scenario, duration_minutes)
        self.simulated_streams[stream.id] = stream
        return stream
    
    def start_simulated_stream(self, stream_id: str) -> bool:
        """开始模拟直播"""
        stream = self.simulated_streams.get(stream_id)
        if stream:
            stream.start()
            return True
        return False
    
    def complete_simulated_stream(
        self,
        stream_id: str,
        score: float,
        feedback: List[str],
        metrics: Dict
    ) -> bool:
        """完成模拟直播"""
        stream = self.simulated_streams.get(stream_id)
        if stream:
            stream.end(score, feedback, metrics)
            return True
        return False
    
    def get_simulated_stream(self, stream_id: str) -> Optional[SimulatedStream]:
        """获取模拟直播详情"""
        return self.simulated_streams.get(stream_id)
    
    def get_anchor_simulated_streams(self, anchor_id: str) -> List[SimulatedStream]:
        """获取主播的所有模拟直播"""
        return [s for s in self.simulated_streams.values() if s.anchor_id == anchor_id]
    
    def record_growth(
        self,
        anchor_id: str,
        assessment_score: float,
        completed_courses: int,
        simulated_streams: int
    ):
        """记录主播成长数据"""
        if anchor_id not in self.growth_records:
            self.growth_records[anchor_id] = AnchorGrowthRecord(anchor_id)
        
        self.growth_records[anchor_id].add_record(
            assessment_score,
            completed_courses,
            simulated_streams
        )
    
    def get_growth_curve(self, anchor_id: str) -> List[Dict]:
        """获取主播成长曲线"""
        record = self.growth_records.get(anchor_id)
        if record:
            return record.get_growth_curve()
        return []
    
    def get_training_statistics(self, anchor_id: Optional[str] = None) -> Dict:
        """获取培训统计数据"""
        if anchor_id:
            assessments = [a for a in self.assessments.values() if a.anchor_id == anchor_id]
            plans = [p for p in self.plans.values() if p.anchor_id == anchor_id]
            streams = [s for s in self.simulated_streams.values() if s.anchor_id == anchor_id]
        else:
            assessments = list(self.assessments.values())
            plans = list(self.plans.values())
            streams = list(self.simulated_streams.values())
        
        completed_plans = len([p for p in plans if p.status == TrainingStatus.COMPLETED])
        completed_streams = len([s for s in streams if s.status == "completed"])
        avg_stream_score = 0.0
        if completed_streams > 0:
            avg_stream_score = sum(s.score for s in streams if s.score) / completed_streams
        
        return {
            "total_assessments": len(assessments),
            "total_plans": len(plans),
            "completed_plans": completed_plans,
            "total_simulated_streams": len(streams),
            "completed_streams": completed_streams,
            "average_stream_score": round(avg_stream_score, 2),
            "total_courses": len(self.courses)
        }


# 全局服务实例
training_service = TrainingService()
