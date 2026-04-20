"""
LiveMirror Dashboard Tests
大屏功能测试
"""

import pytest
import asyncio
import json
from datetime import datetime
from fastapi.testclient import TestClient
from fastapi import WebSocket

# 导入服务
from backend.services.dashboard import DashboardService, dashboard_service


class TestDashboardService:
    """大屏服务测试"""
    
    def test_init(self):
        """测试服务初始化"""
        service = DashboardService()
        assert service.active_connections == set()
        assert service.current_data["gmv"] == 0
        assert service.current_data["viewers"] == 0
        assert service.current_data["likes"] == 0
    
    def test_update_data(self):
        """测试数据更新"""
        service = DashboardService()
        service.update_data(gmv=1000.50, viewers=100, likes=50)
        
        assert service.current_data["gmv"] == 1000.50
        assert service.current_data["viewers"] == 100
        assert service.current_data["likes"] == 50
    
    def test_update_data_peak_viewers(self):
        """测试峰值观看人数更新"""
        service = DashboardService()
        service.update_data(viewers=100)
        assert service.current_data["peak_viewers"] == 100
        
        service.update_data(viewers=150)
        assert service.current_data["peak_viewers"] == 150
        
        service.update_data(viewers=120)
        assert service.current_data["peak_viewers"] == 150  # 保持峰值
    
    def test_get_current_data(self):
        """测试获取当前数据"""
        service = DashboardService()
        service.update_data(gmv=5000, viewers=200)
        
        data = service.get_current_data()
        assert data["gmv"] == 5000
        assert data["viewers"] == 200
        
        # 确保返回的是副本
        data["gmv"] = 9999
        assert service.current_data["gmv"] == 5000
    
    def test_reset_data(self):
        """测试重置数据"""
        service = DashboardService()
        service.update_data(gmv=10000, viewers=500, likes=1000)
        
        service.reset_data()
        assert service.current_data["gmv"] == 0
        assert service.current_data["viewers"] == 0
        assert service.current_data["likes"] == 0
    
    def test_simulate_live_data(self):
        """测试模拟直播数据"""
        service = DashboardService()
        initial_gmv = service.current_data["gmv"]
        
        service._simulate_live_data()
        
        # GMV 应该增长
        assert service.current_data["gmv"] > initial_gmv
        # 观看人数应该大于 0
        assert service.current_data["viewers"] > 0
        # 点赞数应该增长
        assert service.current_data["likes"] > 0
    
    @pytest.mark.asyncio
    async def test_connect_disconnect(self):
        """测试 WebSocket 连接和断开"""
        service = DashboardService()
        
        # 创建模拟 WebSocket
        class MockWebSocket:
            def __init__(self):
                self.accepted = False
                self.sent_data = []
            
            async def accept(self):
                self.accepted = True
            
            async def send_json(self, data):
                self.sent_data.append(data)
        
        ws = MockWebSocket()
        await service.connect(ws)
        
        assert ws.accepted == True
        assert len(service.active_connections) == 1
        assert len(ws.sent_data) > 0  # 应该发送了初始数据
        
        service.disconnect(ws)
        assert len(service.active_connections) == 0
    
    @pytest.mark.asyncio
    async def test_broadcast(self):
        """测试广播功能"""
        service = DashboardService()
        
        class MockWebSocket:
            def __init__(self):
                self.sent_data = []
            
            async def send_json(self, data):
                self.sent_data.append(data)
        
        ws1 = MockWebSocket()
        ws2 = MockWebSocket()
        
        # 添加连接
        service.active_connections.add(ws1)
        service.active_connections.add(ws2)
        
        # 广播数据
        test_data = {"type": "test", "value": 123}
        await service.broadcast(test_data)
        
        assert len(ws1.sent_data) == 1
        assert len(ws2.sent_data) == 1
        assert ws1.sent_data[0] == test_data
        assert ws2.sent_data[0] == test_data


class TestDashboardAPI:
    """大屏 API 接口测试"""
    
    @pytest.fixture
    def client(self):
        """创建测试客户端"""
        from fastapi import FastAPI
        from backend.routes.dashboard import router
        
        app = FastAPI()
        app.include_router(router)
        
        with TestClient(app) as client:
            yield client
    
    def test_get_data(self, client):
        """测试获取数据接口"""
        response = client.get("/api/dashboard/data")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert "data" in data
        assert "timestamp" in data
    
    def test_update_data(self, client):
        """测试更新数据接口"""
        response = client.post(
            "/api/dashboard/data/update",
            params={"gmv": 5000, "viewers": 100}
        )
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["data"]["gmv"] == 5000
        assert data["data"]["viewers"] == 100
    
    def test_reset_data(self, client):
        """测试重置数据接口"""
        # 先更新数据
        client.post("/api/dashboard/data/update", params={"gmv": 10000})
        
        # 重置
        response = client.post("/api/dashboard/data/reset")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        
        # 验证数据已重置
        get_response = client.get("/api/dashboard/data")
        assert get_response.json()["data"]["gmv"] == 0
    
    def test_get_templates(self, client):
        """测试获取模板接口"""
        response = client.get("/api/dashboard/templates")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert len(data["templates"]) > 0
        
        # 验证模板结构
        template = data["templates"][0]
        assert "id" in template
        assert "name" in template
        assert "description" in template
    
    def test_export_json(self, client):
        """测试导出 JSON 格式"""
        response = client.get("/api/dashboard/export?format=json")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["format"] == "json"
        assert "data" in data
        assert ".json" in data["filename"]
    
    def test_export_csv(self, client):
        """测试导出 CSV 格式"""
        response = client.get("/api/dashboard/export?format=csv")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] == True
        assert data["format"] == "csv"
        assert "data" in data
        assert ".csv" in data["filename"]
        
        # 验证 CSV 格式
        csv_data = data["data"]
        assert "metric,value" in csv_data  # CSV 头部


class TestDashboardLayouts:
    """大屏布局测试"""
    
    def test_layout_templates(self):
        """测试所有布局模板存在"""
        expected_layouts = [
            "default",
            "focus-gmv",
            "interaction",
            "minimal"
        ]
        
        from backend.routes.dashboard import router
        from fastapi import FastAPI
        from fastapi.testclient import TestClient
        
        app = FastAPI()
        app.include_router(router)
        
        with TestClient(app) as client:
            response = client.get("/api/dashboard/templates")
            data = response.json()
            
            template_ids = [t["id"] for t in data["templates"]]
            
            for layout in expected_layouts:
                assert layout in template_ids, f"布局 {layout} 不存在"


class TestDashboardRealTime:
    """实时数据测试"""
    
    def test_data_update_interval(self):
        """测试数据更新间隔"""
        service = DashboardService()
        
        # 记录初始数据
        initial_gmv = service.current_data["gmv"]
        
        # 模拟多次更新
        for _ in range(10):
            service._simulate_live_data()
        
        # GMV 应该显著增长
        assert service.current_data["gmv"] > initial_gmv
    
    def test_conversion_rate_calculation(self):
        """测试转化率计算"""
        service = DashboardService()
        
        # 设置观看人数和订单数
        service.update_data(viewers=1000, orders=50)
        
        # 验证转化率
        expected_rate = (50 / 1000) * 100
        assert service.current_data["conversion_rate"] == expected_rate
    
    def test_data_consistency(self):
        """测试数据一致性"""
        service = DashboardService()
        
        # 多次更新
        for i in range(100):
            service.update_data(
                gmv=i * 100,
                viewers=100 + i,
                likes=50 + i
            )
            
            data = service.get_current_data()
            
            # 验证数据一致性
            assert data["gmv"] == i * 100
            assert data["viewers"] == 100 + i
            assert data["likes"] == 50 + i


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
