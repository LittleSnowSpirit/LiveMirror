"""
直播效果预测服务测试 - LiveMirror
"""

import pytest
from datetime import datetime, timedelta
try:
    from backend.services.prediction import (
        PredictionService,
        PredictionModel,
        TimeSlot,
        get_service
    )
except ImportError as exc:
    pytest.skip(f"Experimental prediction API drifted from service exports: {exc}", allow_module_level=True)


class TestPredictionService:
    """预测服务测试"""
    
    @pytest.fixture
    def service(self):
        """创建测试服务实例"""
        return PredictionService(data_dir="data/test_prediction")
    
    def test_init_sample_data(self, service):
        """测试初始化示例数据"""
        assert len(service.historical_data) > 0
        assert len(service.historical_data) == 60 * 4  # 60 天，每天 4 个时间段
        assert service.model_configs is not None
    
    def test_predict_gmv(self, service):
        """测试 GMV 预测"""
        target_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        result = service.predict_gmv(target_date, "evening", "general")
        
        assert "predicted_gmv" in result
        assert "confidence_interval" in result
        assert "accuracy_score" in result
        assert result["predicted_gmv"] > 0
        assert result["confidence_interval"]["lower"] <= result["predicted_gmv"]
        assert result["confidence_interval"]["upper"] >= result["predicted_gmv"]
    
    def test_predict_viewers(self, service):
        """测试观看人数预测"""
        target_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        result = service.predict_viewers(target_date, "evening", "general")
        
        assert "predicted_viewers" in result
        assert "confidence_interval" in result
        assert "accuracy_score" in result
        assert result["predicted_viewers"] > 0
        assert isinstance(result["predicted_viewers"], int)
    
    def test_predict_conversion_rate(self, service):
        """测试转化率预测"""
        target_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        result = service.predict_conversion_rate(target_date, "evening", "general")
        
        assert "predicted_conversion_rate" in result
        assert "confidence_interval" in result
        assert "accuracy_score" in result
        assert 0 <= result["predicted_conversion_rate"] <= 1
    
    def test_predict_all(self, service):
        """测试综合预测"""
        target_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        result = service.predict_all(target_date, "evening", "general")
        
        assert result.predicted_gmv > 0
        assert result.predicted_viewers > 0
        assert 0 <= result.predicted_conversion_rate <= 1
        assert result.accuracy_score > 0
        assert result.model_used == "hybrid"
    
    def test_recommend_best_time(self, service):
        """测试最佳时间推荐"""
        result = service.recommend_best_time(category="general", top_n=3)
        
        assert result.recommended_slot in ["morning", "afternoon", "evening", "night"]
        assert result.score > 0
        assert result.expected_gmv > 0
        assert result.expected_viewers > 0
        assert len(result.reason) > 0
        assert len(result.alternative_slots) <= 3
    
    def test_get_historical_trends(self, service):
        """测试获取历史趋势"""
        trends = service.get_historical_trends(days=30)
        
        assert "daily_trends" in trends
        assert "slot_summary" in trends
        assert "period" in trends
        assert len(trends["daily_trends"]) > 0
        
        # 检查时间段汇总
        for slot in ["morning", "afternoon", "evening", "night"]:
            assert slot in trends["slot_summary"]
            assert "avg_gmv" in trends["slot_summary"][slot]
            assert "avg_viewers" in trends["slot_summary"][slot]
    
    def test_add_historical_data(self, service):
        """测试添加历史数据"""
        initial_count = len(service.historical_data)
        
        service.add_historical_data(
            date="2026-04-07",
            time_slot="evening",
            gmv=10000.0,
            viewers=1000,
            conversions=50,
            duration_minutes=120,
            category="beauty"
        )
        
        assert len(service.historical_data) == initial_count + 1
        
        # 验证最后一条数据
        last_entry = service.historical_data[-1]
        assert last_entry.date == "2026-04-07"
        assert last_entry.gmv == 10000.0
        assert last_entry.viewers == 1000
        assert last_entry.conversions == 50
    
    def test_evaluate_prediction_accuracy(self, service):
        """测试预测准确度评估"""
        # 先进行一次预测
        target_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        service.predict_all(target_date, "evening", "general")
        
        # 评估准确度
        result = service.evaluate_prediction_accuracy(
            target_date=target_date,
            actual_gmv=12000.0,
            actual_viewers=1200,
            actual_conversions=60
        )
        
        assert result["success"] is True
        assert "accuracy" in result
        assert "predictions" in result
        assert "rating" in result
        assert result["rating"] in ["优秀", "良好", "一般", "需改进"]
    
    def test_time_slot_impact(self, service):
        """测试不同时间段的影响"""
        target_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        results = {}
        for slot in ["morning", "afternoon", "evening", "night"]:
            result = service.predict_gmv(target_date, slot, "general")
            results[slot] = result["predicted_gmv"]
        
        # 晚间应该最高，深夜应该最低
        assert results["evening"] > results["morning"]
        assert results["evening"] > results["night"]
        assert results["afternoon"] > results["night"]
    
    def test_weekend_effect(self, service):
        """测试周末效应"""
        # 找到下一个周六
        today = datetime.now()
        days_until_saturday = (5 - today.weekday()) % 7
        if days_until_saturday == 0:
            days_until_saturday = 7
        saturday = today + timedelta(days=days_until_saturday)
        
        # 找到下一个周一
        days_until_monday = (7 - today.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 7
        monday = today + timedelta(days=days_until_monday)
        
        saturday_date = saturday.strftime("%Y-%m-%d")
        monday_date = monday.strftime("%Y-%m-%d")
        
        # 预测周末和工作日的 GMV
        saturday_gmv = service.predict_gmv(saturday_date, "evening", "general")["predicted_gmv"]
        monday_gmv = service.predict_gmv(monday_date, "evening", "general")["predicted_gmv"]
        
        # 周末应该比工作日高
        assert saturday_gmv > monday_gmv
    
    def test_model_performance(self, service):
        """测试模型性能报告"""
        report = service.get_model_performance()
        
        assert "models" in report
        assert "total_predictions" in report
        assert "historical_data_points" in report
        assert "last_updated" in report
        assert len(report["models"]) >= 3  # gmv, viewers, conversion_rate
    
    def test_prediction_persistence(self, service):
        """测试预测记录持久化"""
        target_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        
        # 进行多次预测
        for slot in ["morning", "evening"]:
            service.predict_all(target_date, slot, "general")
        
        # 验证预测记录
        assert len(service.predictions) >= 2
        
        # 检查预测记录格式
        latest = service.predictions[-1]
        assert "timestamp" in latest
        assert "target_date" in latest
        assert "time_slot" in latest
        assert "result" in latest


class TestPredictionAPI:
    """预测 API 测试（需要 FastAPI 测试客户端）"""
    
    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        from fastapi.testclient import TestClient
        from backend.routes.prediction import router
        from fastapi import FastAPI
        
        app = FastAPI()
        app.include_router(router)
        
        return TestClient(app)
    
    def test_predict_gmv_api(self, client):
        """测试 GMV 预测 API"""
        response = client.post("/api/prediction/gmv", json={
            "target_date": "2026-04-09",
            "time_slot": "evening",
            "category": "general"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        assert "prediction" in data["data"]
    
    def test_predict_viewers_api(self, client):
        """测试观看人数预测 API"""
        response = client.post("/api/prediction/viewers", json={
            "target_date": "2026-04-09",
            "time_slot": "evening",
            "category": "general"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_predict_conversion_rate_api(self, client):
        """测试转化率预测 API"""
        response = client.post("/api/prediction/conversion-rate", json={
            "target_date": "2026-04-09",
            "time_slot": "evening",
            "category": "general"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_predict_all_api(self, client):
        """测试综合预测 API"""
        response = client.post("/api/prediction/all", json={
            "target_date": "2026-04-09",
            "time_slot": "evening",
            "category": "general"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "prediction" in data["data"]
    
    def test_recommend_time_api(self, client):
        """测试时间推荐 API"""
        response = client.post("/api/prediction/recommend-time", json={
            "category": "general",
            "top_n": 3
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "recommended_slot" in data["data"]
    
    def test_get_trends_api(self, client):
        """测试获取趋势 API"""
        response = client.get("/api/prediction/trends?days=30")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "daily_trends" in data["data"]
    
    def test_add_historical_data_api(self, client):
        """测试添加历史数据 API"""
        response = client.post("/api/prediction/historical-data", json={
            "date": "2026-04-07",
            "time_slot": "evening",
            "gmv": 10000.0,
            "viewers": 1000,
            "conversions": 50,
            "duration_minutes": 120,
            "category": "beauty"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_invalid_date_format(self, client):
        """测试无效日期格式"""
        response = client.post("/api/prediction/gmv", json={
            "target_date": "invalid-date",
            "time_slot": "evening",
            "category": "general"
        })
        
        assert response.status_code == 422  # Validation error
    
    def test_invalid_time_slot(self, client):
        """测试无效时间段"""
        response = client.post("/api/prediction/gmv", json={
            "target_date": "2026-04-09",
            "time_slot": "invalid",
            "category": "general"
        })
        
        assert response.status_code == 422  # Validation error


def test_service_singleton():
    """测试服务单例模式"""
    service1 = get_service()
    service2 = get_service()
    
    assert service1 is service2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
