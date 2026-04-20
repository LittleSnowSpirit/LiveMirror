"""
客服工单系统测试
测试工单创建、流转、统计报表和自动回复功能
"""

import sys
import os
import pytest
from datetime import datetime

# 添加后端路径到系统路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.ticket import (
    TicketService, 
    Ticket, 
    TicketStatus, 
    TicketPriority, 
    TicketCategory
)


@pytest.fixture
def service():
    """创建工单服务实例"""
    return TicketService()


@pytest.fixture
def sample_ticket(service):
    """创建示例工单"""
    return service.create_ticket(
        title="测试工单",
        description="这是一个测试工单",
        customer_id="customer_001",
        category="technical",
        priority="medium"
    )


class TestTicketCreation:
    """测试工单创建功能"""
    
    def test_create_ticket_basic(self, service):
        """测试基本工单创建"""
        ticket = service.create_ticket(
            title="无法登录系统",
            description="用户反馈无法登录，显示错误代码 500",
            customer_id="customer_001"
        )
        
        assert ticket.ticket_id is not None
        assert ticket.title == "无法登录系统"
        assert ticket.description == "用户反馈无法登录，显示错误代码 500"
        assert ticket.customer_id == "customer_001"
        assert ticket.status == TicketStatus.PENDING
        assert ticket.priority == TicketPriority.MEDIUM
        assert ticket.category == TicketCategory.OTHER
    
    def test_create_ticket_with_category(self, service):
        """测试带分类的工单创建"""
        ticket = service.create_ticket(
            title="账单错误",
            description="账单金额不对",
            customer_id="customer_002",
            category="billing"
        )
        
        assert ticket.category == TicketCategory.BILLING
    
    def test_create_ticket_with_priority(self, service):
        """测试带优先级的工单创建"""
        ticket = service.create_ticket(
            title="系统崩溃",
            description="生产环境系统崩溃",
            customer_id="customer_003",
            priority="urgent"
        )
        
        assert ticket.priority == TicketPriority.URGENT
    
    def test_create_ticket_auto_reply(self, service):
        """测试创建工单时的自动回复"""
        ticket = service.create_ticket(
            title="技术问题",
            description="无法连接服务器",
            customer_id="customer_004",
            category="technical"
        )
        
        assert len(ticket.messages) > 0
        assert ticket.messages[0]["sender"] == "system"
        assert "技术团队" in ticket.messages[0]["content"]
    
    def test_create_multiple_tickets(self, service):
        """测试创建多个工单"""
        tickets = []
        for i in range(5):
            ticket = service.create_ticket(
                title=f"工单 {i+1}",
                description=f"测试工单 {i+1}",
                customer_id=f"customer_{i:03d}"
            )
            tickets.append(ticket)
        
        assert len(service.get_all_tickets()) == 5
        assert len(tickets) == 5


class TestTicketWorkflow:
    """测试工单流转功能"""
    
    def test_assign_ticket(self, service, sample_ticket):
        """测试工单分配"""
        success = service.assign_ticket(sample_ticket.ticket_id, "agent_001")
        
        assert success is True
        assert sample_ticket.assigned_to == "agent_001"
        assert sample_ticket.status == TicketStatus.IN_PROGRESS
    
    def test_assign_nonexistent_ticket(self, service):
        """测试分配不存在的工单"""
        success = service.assign_ticket("nonexistent_id", "agent_001")
        assert success is False
    
    def test_update_status(self, service, sample_ticket):
        """测试更新工单状态"""
        success = service.update_ticket_status(sample_ticket.ticket_id, "in_progress")
        
        assert success is True
        assert sample_ticket.status == TicketStatus.IN_PROGRESS
    
    def test_update_to_resolved(self, service, sample_ticket):
        """测试更新为已解决状态"""
        service.update_ticket_status(sample_ticket.ticket_id, "resolved")
        
        assert sample_ticket.status == TicketStatus.RESOLVED
        # 应该有自动回复消息
        resolved_messages = [m for m in sample_ticket.messages if "已解决" in m["content"]]
        assert len(resolved_messages) > 0
    
    def test_add_message_customer(self, service, sample_ticket):
        """测试客户添加消息"""
        success = service.add_message(
            sample_ticket.ticket_id,
            "问题还没有解决",
            "customer_001",
            "customer"
        )
        
        assert success is True
        assert len(sample_ticket.messages) > 0
        assert sample_ticket.messages[-1]["sender_type"] == "customer"
    
    def test_add_message_agent(self, service, sample_ticket):
        """测试客服添加消息"""
        # 先分配工单
        service.assign_ticket(sample_ticket.ticket_id, "agent_001")
        
        # 客服回复
        success = service.add_message(
            sample_ticket.ticket_id,
            "我们正在处理您的问题",
            "agent_001",
            "agent"
        )
        
        assert success is True
        assert sample_ticket.messages[-1]["sender_type"] == "agent"
    
    def test_status_change_on_message(self, service, sample_ticket):
        """测试消息发送后状态自动变化"""
        # 设置为处理中
        service.update_ticket_status(sample_ticket.ticket_id, "in_progress")
        
        # 客户回复
        service.add_message(
            sample_ticket.ticket_id,
            "好的，谢谢",
            "customer_001",
            "customer"
        )
        
        # 状态应该变为等待客户
        assert sample_ticket.status == TicketStatus.WAITING_CUSTOMER
    
    def test_delete_ticket(self, service, sample_ticket):
        """测试删除工单"""
        ticket_id = sample_ticket.ticket_id
        success = service.delete_ticket(ticket_id)
        
        assert success is True
        assert service.get_ticket(ticket_id) is None
    
    def test_delete_nonexistent_ticket(self, service):
        """测试删除不存在的工单"""
        success = service.delete_ticket("nonexistent_id")
        assert success is False


class TestTicketStatistics:
    """测试工单统计报表功能"""
    
    def test_basic_statistics(self, service):
        """测试基本统计"""
        # 创建多个工单
        service.create_ticket("工单 1", "描述 1", "c1", "technical", "low")
        service.create_ticket("工单 2", "描述 2", "c2", "billing", "medium")
        service.create_ticket("工单 3", "描述 3", "c3", "account", "high")
        
        stats = service.get_statistics()
        
        assert stats["total"] == 3
        assert stats["pending"] == 3
        assert stats["in_progress"] == 0
        assert stats["resolved"] == 0
    
    def test_statistics_by_status(self, service):
        """测试按状态统计"""
        # 创建工单并设置不同状态
        t1 = service.create_ticket("工单 1", "描述 1", "c1")
        t2 = service.create_ticket("工单 2", "描述 2", "c2")
        t3 = service.create_ticket("工单 3", "描述 3", "c3")
        
        service.update_ticket_status(t1.ticket_id, "in_progress")
        service.update_ticket_status(t2.ticket_id, "resolved")
        
        stats = service.get_statistics()
        
        assert stats["by_status"]["pending"] == 1
        assert stats["by_status"]["in_progress"] == 1
        assert stats["by_status"]["resolved"] == 1
    
    def test_statistics_by_category(self, service):
        """测试按分类统计"""
        service.create_ticket("技术 1", "描述", "c1", "technical")
        service.create_ticket("技术 2", "描述", "c2", "technical")
        service.create_ticket("账单 1", "描述", "c3", "billing")
        service.create_ticket("账户 1", "描述", "c4", "account")
        
        stats = service.get_statistics()
        
        assert stats["by_category"]["technical"] == 2
        assert stats["by_category"]["billing"] == 1
        assert stats["by_category"]["account"] == 1
    
    def test_statistics_by_priority(self, service):
        """测试按优先级统计"""
        service.create_ticket("紧急", "描述", "c1", "other", "urgent")
        service.create_ticket("高", "描述", "c2", "other", "high")
        service.create_ticket("中", "描述", "c3", "other", "medium")
        service.create_ticket("低", "描述", "c4", "other", "low")
        
        stats = service.get_statistics()
        
        assert stats["by_priority"]["urgent"] == 1
        assert stats["by_priority"]["high"] == 1
        assert stats["by_priority"]["medium"] == 1
        assert stats["by_priority"]["low"] == 1


class TestAutoReply:
    """测试自动回复功能"""
    
    def test_auto_reply_technical(self, service):
        """测试技术类工单自动回复"""
        ticket = service.create_ticket(
            "技术问题",
            "系统报错",
            "c1",
            "technical"
        )
        
        reply = ticket.messages[0]["content"]
        assert "技术团队" in reply
    
    def test_auto_reply_billing(self, service):
        """测试账单类工单自动回复"""
        ticket = service.create_ticket(
            "账单问题",
            "金额不对",
            "c1",
            "billing"
        )
        
        reply = ticket.messages[0]["content"]
        assert "财务团队" in reply
        assert "24 小时" in reply
    
    def test_auto_reply_account(self, service):
        """测试账户类工单自动回复"""
        ticket = service.create_ticket(
            "账户问题",
            "无法登录",
            "c1",
            "account"
        )
        
        reply = ticket.messages[0]["content"]
        assert "账户安全" in reply
        assert "优先处理" in reply
    
    def test_auto_reply_default(self, service):
        """测试默认自动回复"""
        ticket = service.create_ticket(
            "其他问题",
            "咨询",
            "c1",
            "other"
        )
        
        reply = ticket.messages[0]["content"]
        assert "尽快处理" in reply
    
    def test_get_auto_reply_templates(self, service):
        """测试获取所有自动回复模板"""
        templates = service.auto_reply_templates
        
        assert "greeting" in templates
        assert "technical" in templates
        assert "billing" in templates
        assert "account" in templates
        assert "resolved" in templates
        assert "default" in templates


class TestTicketQueries:
    """测试工单查询功能"""
    
    def test_get_ticket_by_id(self, service, sample_ticket):
        """测试通过 ID 获取工单"""
        ticket = service.get_ticket(sample_ticket.ticket_id)
        
        assert ticket is not None
        assert ticket.ticket_id == sample_ticket.ticket_id
    
    def test_get_nonexistent_ticket(self, service):
        """测试获取不存在的工单"""
        ticket = service.get_ticket("nonexistent_id")
        assert ticket is None
    
    def test_get_tickets_by_customer(self, service):
        """测试获取客户的所有工单"""
        service.create_ticket("工单 1", "描述", "customer_001")
        service.create_ticket("工单 2", "描述", "customer_001")
        service.create_ticket("工单 3", "描述", "customer_002")
        
        tickets = service.get_tickets_by_customer("customer_001")
        
        assert len(tickets) == 2
        assert all(t.customer_id == "customer_001" for t in tickets)
    
    def test_get_tickets_by_agent(self, service):
        """测试获取客服的所有工单"""
        t1 = service.create_ticket("工单 1", "描述", "c1")
        t2 = service.create_ticket("工单 2", "描述", "c2")
        t3 = service.create_ticket("工单 3", "描述", "c3")
        
        service.assign_ticket(t1.ticket_id, "agent_001")
        service.assign_ticket(t2.ticket_id, "agent_001")
        service.assign_ticket(t3.ticket_id, "agent_002")
        
        tickets = service.get_tickets_by_agent("agent_001")
        
        assert len(tickets) == 2
        assert all(t.assigned_to == "agent_001" for t in tickets)
    
    def test_get_tickets_by_status(self, service):
        """测试获取指定状态的工单"""
        t1 = service.create_ticket("工单 1", "描述", "c1")
        t2 = service.create_ticket("工单 2", "描述", "c2")
        t3 = service.create_ticket("工单 3", "描述", "c3")
        
        service.update_ticket_status(t1.ticket_id, "in_progress")
        service.update_ticket_status(t2.ticket_id, "resolved")
        
        pending = service.get_tickets_by_status("pending")
        in_progress = service.get_tickets_by_status("in_progress")
        resolved = service.get_tickets_by_status("resolved")
        
        assert len(pending) == 1
        assert len(in_progress) == 1
        assert len(resolved) == 1


class TestTicketModel:
    """测试工单模型功能"""
    
    def test_ticket_to_dict(self, service, sample_ticket):
        """测试工单转字典"""
        ticket_dict = sample_ticket.to_dict()
        
        assert "ticket_id" in ticket_dict
        assert "title" in ticket_dict
        assert "description" in ticket_dict
        assert "status" in ticket_dict
        assert "created_at" in ticket_dict
        assert "updated_at" in ticket_dict
    
    def test_ticket_add_message(self, service, sample_ticket):
        """测试添加工单消息"""
        sample_ticket.add_message("新消息", "测试用户", "customer")
        
        assert len(sample_ticket.messages) > 0
        assert sample_ticket.messages[-1]["content"] == "新消息"
        assert sample_ticket.messages[-1]["sender"] == "测试用户"
    
    def test_ticket_update_status(self, service, sample_ticket):
        """测试更新工单状态"""
        sample_ticket.update_status(TicketStatus.IN_PROGRESS)
        
        assert sample_ticket.status == TicketStatus.IN_PROGRESS
    
    def test_ticket_assign(self, service, sample_ticket):
        """测试工单分配"""
        sample_ticket.assign("agent_001")
        
        assert sample_ticket.assigned_to == "agent_001"
        assert sample_ticket.status == TicketStatus.IN_PROGRESS


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
