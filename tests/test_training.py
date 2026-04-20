"""
LiveMirror Training Service Tests
主播培训系统测试
"""

import pytest
import sys
import os
from datetime import datetime, timedelta

# 添加 backend 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
from services.training import (
    TrainingService,
    AnchorAssessment,
    TrainingPlan,
    TrainingCourse,
    SimulatedStream,
    SkillLevel,
    TrainingStatus
)


@pytest.fixture
def training_service():
    """培训服务测试夹具"""
    return TrainingService()


class TestAnchorAssessment:
    """主播能力评估测试"""
    
    def test_create_assessment(self, training_service):
        """测试创建能力评估"""
        categories = {
            "communication": 85.0,
            "product_knowledge": 70.0,
            "sales_skill": 75.0,
            "audience_engagement": 90.0,
            "technical_operation": 60.0,
            "emergency_response": 65.0
        }
        
        assessment = training_service.create_assessment(
            anchor_id="anchor001",
            assessor_id="manager001",
            categories=categories
        )
        
        assert assessment.id is not None
        assert assessment.anchor_id == "anchor001"
        assert assessment.assessor_id == "manager001"
        assert assessment.categories == categories
        assert assessment.overall_score > 0
        assert len(assessment.weaknesses) > 0
        assert len(assessment.strengths) > 0
        assert len(assessment.recommendations) > 0
    
    def test_assessment_overall_score(self, training_service):
        """测试评估总体分数计算"""
        categories = {
            "communication": 80.0,
            "product_knowledge": 80.0,
            "sales_skill": 80.0
        }
        
        assessment = training_service.create_assessment(
            anchor_id="anchor001",
            assessor_id="manager001",
            categories=categories
        )
        
        assert assessment.overall_score == 80.0
    
    def test_assessment_weaknesses_identification(self, training_service):
        """测试薄弱环节识别"""
        categories = {
            "communication": 90.0,
            "product_knowledge": 50.0,
            "sales_skill": 85.0
        }
        
        assessment = training_service.create_assessment(
            anchor_id="anchor001",
            assessor_id="manager001",
            categories=categories
        )
        
        # product_knowledge 应该被识别为薄弱环节
        assert "product_knowledge" in assessment.weaknesses
    
    def test_assessment_strengths_identification(self, training_service):
        """测试优势环节识别"""
        categories = {
            "communication": 95.0,
            "product_knowledge": 60.0,
            "sales_skill": 60.0
        }
        
        assessment = training_service.create_assessment(
            anchor_id="anchor001",
            assessor_id="manager001",
            categories=categories
        )
        
        # communication 应该被识别为优势环节
        assert "communication" in assessment.strengths
    
    def test_get_assessment(self, training_service):
        """测试获取评估详情"""
        categories = {"communication": 75.0}
        assessment = training_service.create_assessment(
            anchor_id="anchor001",
            assessor_id="manager001",
            categories=categories
        )
        
        retrieved = training_service.get_assessment(assessment.id)
        assert retrieved is not None
        assert retrieved.id == assessment.id
    
    def test_get_anchor_assessments(self, training_service):
        """测试获取主播的所有评估"""
        training_service.create_assessment(
            anchor_id="anchor001",
            assessor_id="manager001",
            categories={"communication": 70.0}
        )
        training_service.create_assessment(
            anchor_id="anchor001",
            assessor_id="manager002",
            categories={"communication": 80.0}
        )
        training_service.create_assessment(
            anchor_id="anchor002",
            assessor_id="manager001",
            categories={"communication": 75.0}
        )
        
        assessments = training_service.get_anchor_assessments("anchor001")
        assert len(assessments) == 2


class TestTrainingPlan:
    """培训计划测试"""
    
    def test_create_training_plan(self, training_service):
        """测试创建培训计划"""
        assessment = training_service.create_assessment(
            anchor_id="anchor001",
            assessor_id="manager001",
            categories={
                "communication": 60.0,
                "product_knowledge": 50.0,
                "sales_skill": 70.0
            }
        )
        
        plan = training_service.create_training_plan(
            anchor_id="anchor001",
            assessment_id=assessment.id,
            duration_days=30
        )
        
        assert plan is not None
        assert plan.anchor_id == "anchor001"
        assert plan.assessment_id == assessment.id
        assert plan.duration_days == 30
        assert len(plan.courses) > 0
        assert len(plan.milestones) > 0
        assert plan.status == TrainingStatus.NOT_STARTED
    
    def test_training_plan_milestones(self, training_service):
        """测试培训计划里程碑生成"""
        assessment = training_service.create_assessment(
            anchor_id="anchor001",
            assessor_id="manager001",
            categories={"communication": 60.0}
        )
        
        plan = training_service.create_training_plan(
            anchor_id="anchor001",
            assessment_id=assessment.id,
            duration_days=30
        )
        
        # 应该生成多个里程碑
        assert len(plan.milestones) >= 1
        assert all("target_date" in m for m in plan.milestones)
        assert all("name" in m for m in plan.milestones)
    
    def test_complete_course_in_plan(self, training_service):
        """测试标记课程完成"""
        assessment = training_service.create_assessment(
            anchor_id="anchor001",
            assessor_id="manager001",
            categories={"communication": 60.0}
        )
        
        plan = training_service.create_training_plan(
            anchor_id="anchor001",
            assessment_id=assessment.id,
            duration_days=30
        )
        
        initial_progress = plan.progress
        course_id = plan.courses[0]
        
        success = training_service.complete_course_in_plan(plan.id, course_id)
        assert success is True
        
        updated_plan = training_service.get_training_plan(plan.id)
        assert course_id in updated_plan.completed_courses
        assert updated_plan.progress > initial_progress
    
    def test_complete_all_courses(self, training_service):
        """测试完成所有课程"""
        assessment = training_service.create_assessment(
            anchor_id="anchor001",
            assessor_id="manager001",
            categories={"communication": 60.0}
        )
        
        plan = training_service.create_training_plan(
            anchor_id="anchor001",
            assessment_id=assessment.id,
            duration_days=30
        )
        
        # 完成所有课程
        for course_id in plan.courses:
            training_service.complete_course_in_plan(plan.id, course_id)
        
        updated_plan = training_service.get_training_plan(plan.id)
        assert updated_plan.progress == 100.0
        assert updated_plan.status == TrainingStatus.COMPLETED
    
    def test_get_anchor_active_plan(self, training_service):
        """测试获取主播的活跃培训计划"""
        assessment = training_service.create_assessment(
            anchor_id="anchor001",
            assessor_id="manager001",
            categories={"communication": 60.0}
        )
        
        plan = training_service.create_training_plan(
            anchor_id="anchor001",
            assessment_id=assessment.id,
            duration_days=30
        )
        
        active_plan = training_service.get_anchor_active_plan("anchor001")
        assert active_plan is not None
        assert active_plan.id == plan.id


class TestTrainingCourses:
    """培训课程库测试"""
    
    def test_get_all_courses(self, training_service):
        """测试获取所有课程"""
        courses = training_service.get_all_courses()
        assert len(courses) > 0
        assert all(isinstance(c, TrainingCourse) for c in courses)
    
    def test_get_courses_by_category(self, training_service):
        """测试按类别筛选课程"""
        courses = training_service.get_all_courses(category="communication")
        assert len(courses) > 0
        assert all(c.category == "communication" for c in courses)
    
    def test_get_courses_by_difficulty(self, training_service):
        """测试按难度筛选课程"""
        courses = training_service.get_all_courses(difficulty=SkillLevel.BEGINNER)
        assert len(courses) > 0
        assert all(c.difficulty == SkillLevel.BEGINNER for c in courses)
    
    def test_get_course_by_id(self, training_service):
        """测试通过 ID 获取课程"""
        courses = training_service.get_all_courses()
        if courses:
            course = training_service.get_course(courses[0].id)
            assert course is not None
            assert course.id == courses[0].id
    
    def test_default_courses_initialized(self, training_service):
        """测试默认课程库已初始化"""
        courses = training_service.get_all_courses()
        # 应该有至少几个默认课程
        assert len(courses) >= 5
        
        # 检查课程类别覆盖
        categories = set(c.category for c in courses)
        assert "communication" in categories
        assert "sales_skill" in categories


class TestSimulatedStream:
    """模拟直播练习测试"""
    
    def test_create_simulated_stream(self, training_service):
        """测试创建模拟直播"""
        stream = training_service.create_simulated_stream(
            anchor_id="anchor001",
            scenario="product_introduction",
            duration_minutes=30
        )
        
        assert stream.id is not None
        assert stream.anchor_id == "anchor001"
        assert stream.scenario == "product_introduction"
        assert stream.duration_minutes == 30
        assert stream.status == "scheduled"
    
    def test_start_simulated_stream(self, training_service):
        """测试开始模拟直播"""
        stream = training_service.create_simulated_stream(
            anchor_id="anchor001",
            scenario="sales_pitch",
            duration_minutes=30
        )
        
        success = training_service.start_simulated_stream(stream.id)
        assert success is True
        
        updated_stream = training_service.get_simulated_stream(stream.id)
        assert updated_stream.status == "in_progress"
        assert updated_stream.started_at is not None
    
    def test_complete_simulated_stream(self, training_service):
        """测试完成模拟直播"""
        stream = training_service.create_simulated_stream(
            anchor_id="anchor001",
            scenario="audience_interaction",
            duration_minutes=30
        )
        
        training_service.start_simulated_stream(stream.id)
        
        success = training_service.complete_simulated_stream(
            stream_id=stream.id,
            score=85.0,
            feedback=["表达清晰", "互动良好"],
            metrics={"engagement_rate": 0.75, "conversion_rate": 0.05}
        )
        
        assert success is True
        
        updated_stream = training_service.get_simulated_stream(stream.id)
        assert updated_stream.status == "completed"
        assert updated_stream.score == 85.0
        assert len(updated_stream.feedback) == 2
        assert updated_stream.ended_at is not None
    
    def test_get_anchor_simulated_streams(self, training_service):
        """测试获取主播的所有模拟直播"""
        training_service.create_simulated_stream(
            anchor_id="anchor001",
            scenario="product_introduction",
            duration_minutes=30
        )
        training_service.create_simulated_stream(
            anchor_id="anchor001",
            scenario="sales_pitch",
            duration_minutes=30
        )
        training_service.create_simulated_stream(
            anchor_id="anchor002",
            scenario="audience_interaction",
            duration_minutes=30
        )
        
        streams = training_service.get_anchor_simulated_streams("anchor001")
        assert len(streams) == 2


class TestGrowthCurve:
    """成长曲线测试"""
    
    def test_record_growth(self, training_service):
        """测试记录成长数据"""
        training_service.record_growth(
            anchor_id="anchor001",
            assessment_score=75.0,
            completed_courses=5,
            simulated_streams=3
        )
        
        records = training_service.get_growth_curve("anchor001")
        assert len(records) == 1
        assert records[0]["assessment_score"] == 75.0
        assert records[0]["completed_courses"] == 5
        assert records[0]["simulated_streams"] == 3
    
    def test_multiple_growth_records(self, training_service):
        """测试多次成长记录"""
        training_service.record_growth(
            anchor_id="anchor001",
            assessment_score=70.0,
            completed_courses=3,
            simulated_streams=2
        )
        training_service.record_growth(
            anchor_id="anchor001",
            assessment_score=80.0,
            completed_courses=8,
            simulated_streams=5
        )
        
        records = training_service.get_growth_curve("anchor001")
        assert len(records) == 2
        
        # 验证分数增长
        assert records[1]["assessment_score"] > records[0]["assessment_score"]
    
    def test_get_growth_curve_nonexistent_anchor(self, training_service):
        """测试获取不存在主播的成长曲线"""
        records = training_service.get_growth_curve("nonexistent")
        assert records == []


class TestTrainingStatistics:
    """培训统计测试"""
    
    def test_get_training_statistics(self, training_service):
        """测试获取培训统计"""
        # 创建一些测试数据
        assessment = training_service.create_assessment(
            anchor_id="anchor001",
            assessor_id="manager001",
            categories={"communication": 70.0}
        )
        
        plan = training_service.create_training_plan(
            anchor_id="anchor001",
            assessment_id=assessment.id,
            duration_days=30
        )
        
        stream = training_service.create_simulated_stream(
            anchor_id="anchor001",
            scenario="product_introduction",
            duration_minutes=30
        )
        training_service.complete_simulated_stream(
            stream_id=stream.id,
            score=80.0,
            feedback=[],
            metrics={}
        )
        
        stats = training_service.get_training_statistics()
        
        assert stats["total_assessments"] >= 1
        assert stats["total_plans"] >= 1
        assert stats["total_simulated_streams"] >= 1
        assert stats["completed_streams"] >= 1
        assert stats["total_courses"] > 0
    
    def test_get_anchor_specific_statistics(self, training_service):
        """测试获取特定主播的统计"""
        # 创建两个主播的数据
        training_service.create_assessment(
            anchor_id="anchor001",
            assessor_id="manager001",
            categories={"communication": 70.0}
        )
        training_service.create_assessment(
            anchor_id="anchor002",
            assessor_id="manager001",
            categories={"communication": 75.0}
        )
        
        # 获取 anchor001 的统计
        stats = training_service.get_training_statistics(anchor_id="anchor001")
        
        # 应该只包含 anchor001 的数据
        assert stats["total_assessments"] == 1


class TestTrainingPlanModel:
    """培训计划模型测试"""
    
    def test_plan_to_dict(self, training_service):
        """测试培训计划转换为字典"""
        assessment = training_service.create_assessment(
            anchor_id="anchor001",
            assessor_id="manager001",
            categories={"communication": 60.0}
        )
        
        plan = training_service.create_training_plan(
            anchor_id="anchor001",
            assessment_id=assessment.id,
            duration_days=30
        )
        
        plan_dict = plan.to_dict()
        
        assert "id" in plan_dict
        assert "anchor_id" in plan_dict
        assert "courses" in plan_dict
        assert "milestones" in plan_dict
        assert "progress" in plan_dict
        assert "status" in plan_dict
    
    def test_plan_milestone_update(self, training_service):
        """测试计划里程碑更新"""
        assessment = training_service.create_assessment(
            anchor_id="anchor001",
            assessor_id="manager001",
            categories={"communication": 60.0}
        )
        
        plan = training_service.create_training_plan(
            anchor_id="anchor001",
            assessment_id=assessment.id,
            duration_days=30
        )
        
        # 完成一些课程
        for i in range(min(3, len(plan.courses))):
            training_service.complete_course_in_plan(plan.id, plan.courses[i])
        
        updated_plan = training_service.get_training_plan(plan.id)
        
        # 检查里程碑状态更新
        completed_milestones = sum(1 for m in updated_plan.milestones if m["completed"])
        assert completed_milestones > 0


class TestAssessmentModel:
    """评估模型测试"""
    
    def test_assessment_to_dict(self, training_service):
        """测试评估转换为字典"""
        assessment = training_service.create_assessment(
            anchor_id="anchor001",
            assessor_id="manager001",
            categories={"communication": 75.0}
        )
        
        assessment_dict = assessment.to_dict()
        
        assert "id" in assessment_dict
        assert "anchor_id" in assessment_dict
        assert "overall_score" in assessment_dict
        assert "weaknesses" in assessment_dict
        assert "strengths" in assessment_dict
        assert "recommendations" in assessment_dict
    
    def test_assessment_recommendations(self, training_service):
        """测试评估建议生成"""
        assessment = training_service.create_assessment(
            anchor_id="anchor001",
            assessor_id="manager001",
            categories={
                "communication": 40.0,
                "sales_skill": 40.0
            }
        )
        
        # 薄弱环节应该有对应的建议
        assert len(assessment.recommendations) > 0


# 运行测试
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
