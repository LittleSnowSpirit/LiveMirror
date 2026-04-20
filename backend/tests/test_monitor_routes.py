"""
竞品监控 API 路由测试 - LiveMirror
"""

import pytest
from fastapi.testclient import TestClient

# 导入主应用
from backend.routes.monitor import router as monitor_router
from fastapi import FastAPI

# 创建测试应用
app = FastAPI()
app.include_router(monitor_router)
client = TestClient(app)


@pytest.fixture
def test_client():
    """创建测试客户端"""
    return client


class TestCompetitorEndpoints:
    """竞品管理接口测试"""
    
    def test_add_competitor(self, test_client):
        """测试添加竞品"""
        response = test_client.post(
            "/api/monitor/competitors",
            json={
                "name": "测试直播间",
                "platform": "douyin",
                "room_id": "test_room_001"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == "测试直播间"
        assert data["data"]["platform"] == "douyin"
        
        return data["data"]["id"]
    
    def test_list_competitors(self, test_client):
        """测试查询竞品列表"""
        response = test_client.get("/api/monitor/competitors")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "competitors" in data["data"]
        assert "total" in data["data"]
    
    def test_get_competitor_detail(self, test_client):
        """测试获取竞品详情"""
        # 先添加一个竞品
        add_response = test_client.post(
            "/api/monitor/competitors",
            json={
                "name": "详情测试",
                "platform": "taobao",
                "room_id": "tb_001"
            }
        )
        competitor_id = add_response.json()["data"]["id"]
        
        # 获取详情
        response = test_client.get(f"/api/monitor/competitors/{competitor_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == "详情测试"
    
    def test_update_competitor(self, test_client):
        """测试更新竞品信息"""
        # 先添加
        add_response = test_client.post(
            "/api/monitor/competitors",
            json={
                "name": "更新前",
                "platform": "douyin",
                "room_id": "update_test"
            }
        )
        competitor_id = add_response.json()["data"]["id"]
        
        # 更新
        response = test_client.put(
            f"/api/monitor/competitors/{competitor_id}",
            json={"name": "更新后"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == "更新后"
    
    def test_delete_competitor(self, test_client):
        """测试删除竞品"""
        # 先添加
        add_response = test_client.post(
            "/api/monitor/competitors",
            json={
                "name": "删除测试",
                "platform": "douyin",
                "room_id": "delete_test"
            }
        )
        competitor_id = add_response.json()["data"]["id"]
        
        # 删除
        response = test_client.delete(f"/api/monitor/competitors/{competitor_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestStreamDataEndpoints:
    """直播数据接口测试"""
    
    def test_update_stream_data(self, test_client):
        """测试更新直播数据"""
        # 先添加竞品
        add_response = test_client.post(
            "/api/monitor/competitors",
            json={
                "name": "流数据测试",
                "platform": "douyin",
                "room_id": "stream_test"
            }
        )
        competitor_id = add_response.json()["data"]["id"]
        
        # 更新数据
        response = test_client.post(
            f"/api/monitor/competitors/{competitor_id}/stream-data",
            json={
                "viewer_count": 1000,
                "like_count": 5000,
                "comment_count": 200,
                "share_count": 50,
                "product_count": 10,
                "transcript": "欢迎来到直播间"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["viewer_count"] == 1000
    
    def test_get_stream_data(self, test_client):
        """测试获取实时数据"""
        # 先添加并更新数据
        add_response = test_client.post(
            "/api/monitor/competitors",
            json={
                "name": "获取数据测试",
                "platform": "douyin",
                "room_id": "get_stream_test"
            }
        )
        competitor_id = add_response.json()["data"]["id"]
        
        test_client.post(
            f"/api/monitor/competitors/{competitor_id}/stream-data",
            json={"viewer_count": 500}
        )
        
        # 获取数据
        response = test_client.get(f"/api/monitor/competitors/{competitor_id}/stream-data")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["viewer_count"] == 500


class TestRuleEndpoints:
    """告警规则接口测试"""
    
    def test_create_rule(self, test_client):
        """测试创建告警规则"""
        response = test_client.post(
            "/api/monitor/rules",
            json={
                "name": "测试规则",
                "alert_type": "traffic_spike",
                "threshold": 2.0,
                "cooldown_minutes": 10
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == "测试规则"
    
    def test_list_rules(self, test_client):
        """测试查询规则列表"""
        response = test_client.get("/api/monitor/rules")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "rules" in data["data"]
    
    def test_update_rule(self, test_client):
        """测试更新规则"""
        # 先创建
        create_response = test_client.post(
            "/api/monitor/rules",
            json={
                "name": "原始规则",
                "alert_type": "promotion_activity"
            }
        )
        rule_id = create_response.json()["data"]["id"]
        
        # 更新
        response = test_client.put(
            f"/api/monitor/rules/{rule_id}",
            json={"name": "更新后的规则", "enabled": False}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["name"] == "更新后的规则"
        assert data["data"]["enabled"] is False
    
    def test_delete_rule(self, test_client):
        """测试删除规则"""
        # 先创建
        create_response = test_client.post(
            "/api/monitor/rules",
            json={
                "name": "删除测试规则",
                "alert_type": "promotion_activity"
            }
        )
        assert create_response.status_code == 200
        rule_id = create_response.json()["data"]["id"]
        
        # 删除
        response = test_client.delete(f"/api/monitor/rules/{rule_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestAlertEndpoints:
    """告警历史接口测试"""
    
    def test_get_alert_history(self, test_client):
        """测试查询告警历史"""
        response = test_client.get("/api/monitor/alerts?days=7")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "alerts" in data["data"]
        assert "pagination" in data["data"]


class TestConfigEndpoints:
    """配置管理接口测试"""
    
    def test_get_config(self, test_client):
        """测试获取配置"""
        response = test_client.get("/api/monitor/config")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "monitor_interval_seconds" in data["data"]
    
    def test_update_config(self, test_client):
        """测试更新配置"""
        response = test_client.put(
            "/api/monitor/config",
            json={"monitor_interval_seconds": 60}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["data"]["monitor_interval_seconds"] == 60
    
    def test_update_notification_config(self, test_client):
        """测试更新通知配置"""
        response = test_client.put(
            "/api/monitor/config/notification",
            json={
                "channel": "wechat",
                "enabled": True,
                "webhook_url": "https://test.webhook.url"
            }
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


class TestStatisticsEndpoints:
    """统计信息接口测试"""
    
    def test_get_statistics(self, test_client):
        """测试获取统计信息"""
        response = test_client.get("/api/monitor/statistics?days=7")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "total_competitors" in data["data"]
        assert "total_alerts" in data["data"]
    
    def test_get_dashboard(self, test_client):
        """测试获取仪表盘数据"""
        response = test_client.get("/api/monitor/dashboard")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "overview" in data["data"]
        assert "recent_competitors" in data["data"]
        assert "recent_alerts" in data["data"]


class TestMonitoringControl:
    """监控控制接口测试"""
    
    def test_start_monitoring(self, test_client):
        """测试开始监控"""
        # 先添加竞品
        add_response = test_client.post(
            "/api/monitor/competitors",
            json={
                "name": "控制测试",
                "platform": "douyin",
                "room_id": "control_test"
            }
        )
        competitor_id = add_response.json()["data"]["id"]
        
        # 开始监控
        response = test_client.post(f"/api/monitor/competitors/{competitor_id}/start")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_pause_monitoring(self, test_client):
        """测试暂停监控"""
        # 先添加并开始
        add_response = test_client.post(
            "/api/monitor/competitors",
            json={
                "name": "暂停测试",
                "platform": "douyin",
                "room_id": "pause_test"
            }
        )
        competitor_id = add_response.json()["data"]["id"]
        test_client.post(f"/api/monitor/competitors/{competitor_id}/start")
        
        # 暂停
        response = test_client.post(f"/api/monitor/competitors/{competitor_id}/pause")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
    
    def test_stop_monitoring(self, test_client):
        """测试停止监控"""
        # 先添加并开始
        add_response = test_client.post(
            "/api/monitor/competitors",
            json={
                "name": "停止测试",
                "platform": "douyin",
                "room_id": "stop_test"
            }
        )
        competitor_id = add_response.json()["data"]["id"]
        test_client.post(f"/api/monitor/competitors/{competitor_id}/start")
        
        # 停止
        response = test_client.post(f"/api/monitor/competitors/{competitor_id}/stop")
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
