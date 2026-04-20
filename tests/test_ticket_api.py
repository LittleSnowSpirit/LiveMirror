"""
客服工单系统 API 测试
测试 FastAPI 路由接口
"""

import sys
import os
from fastapi.testclient import TestClient

# 添加后端路径到系统路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

# 导入路由
from routes.ticket import router
from fastapi import FastAPI

# 创建 FastAPI 应用
app = FastAPI()
app.include_router(router)

# 创建测试客户端
client = TestClient(app)


def test_create_ticket_api():
    """测试创建工单 API"""
    response = client.post(
        "/api/tickets/",
        json={
            "title": "API 测试工单",
            "description": "通过 API 创建的测试工单",
            "customer_id": "api_customer_001",
            "category": "technical",
            "priority": "high"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "API 测试工单"
    assert data["customer_id"] == "api_customer_001"
    assert data["category"] == "technical"
    assert data["priority"] == "high"
    print("[PASS] Create Ticket API")
    return data["ticket_id"]


def test_get_ticket_api(ticket_id):
    """测试获取工单 API"""
    response = client.get(f"/api/tickets/{ticket_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["ticket_id"] == ticket_id
    print("[PASS] Get Ticket API")


def test_get_all_tickets_api():
    """测试获取所有工单 API"""
    response = client.get("/api/tickets/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    print(f"[PASS] Get All Tickets API (total: {len(data)})")


def test_assign_ticket_api(ticket_id):
    """测试分配工单 API"""
    response = client.post(
        f"/api/tickets/{ticket_id}/assign",
        json={"agent_id": "api_agent_001"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["assigned_to"] == "api_agent_001"
    print("[PASS] Assign Ticket API")


def test_update_status_api(ticket_id):
    """测试更新工单状态 API"""
    response = client.put(
        f"/api/tickets/{ticket_id}/status",
        json={"status": "in_progress"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "in_progress"
    print("[PASS] Update Status API")


def test_add_message_api(ticket_id):
    """测试添加消息 API"""
    response = client.post(
        f"/api/tickets/{ticket_id}/messages",
        json={
            "content": "这是通过 API 添加的测试消息",
            "sender": "测试客服",
            "sender_type": "agent"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["messages"]) > 0
    print("[PASS] Add Message API")


def test_get_statistics_api():
    """测试获取统计 API"""
    response = client.get("/api/tickets/statistics")
    if response.status_code != 200:
        print(f"Statistics API Error: {response.status_code} - {response.text}")
    assert response.status_code == 200
    data = response.json()
    assert "total" in data
    assert "by_status" in data
    assert "by_category" in data
    assert "by_priority" in data
    print(f"[PASS] Get Statistics API (total: {data['total']})")


def test_get_auto_reply_templates_api():
    """测试获取自动回复模板 API"""
    response = client.get("/api/tickets/auto-reply/templates")
    assert response.status_code == 200
    data = response.json()
    assert "greeting" in data
    assert "technical" in data
    assert "billing" in data
    print(f"[PASS] Get Auto-Reply Templates API (templates: {len(data)})")


def test_filter_tickets_api():
    """测试筛选工单 API"""
    # 按状态筛选
    response = client.get("/api/tickets/status/in_progress")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    print(f"[PASS] Filter Tickets API (in_progress: {len(data)})")


def test_delete_ticket_api(ticket_id):
    """测试删除工单 API"""
    response = client.delete(f"/api/tickets/{ticket_id}")
    assert response.status_code == 200
    print("[PASS] Delete Ticket API")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Ticket System API Test")
    print("="*60 + "\n")
    
    # 创建工单
    ticket_id = test_create_ticket_api()
    
    # 测试各种 API
    test_get_ticket_api(ticket_id)
    test_get_all_tickets_api()
    test_assign_ticket_api(ticket_id)
    test_update_status_api(ticket_id)
    test_add_message_api(ticket_id)
    test_get_statistics_api()
    test_get_auto_reply_templates_api()
    test_filter_tickets_api()
    test_delete_ticket_api(ticket_id)
    
    print("\n" + "="*60)
    print("All API Tests Passed!")
    print("="*60 + "\n")
