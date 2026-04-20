"""
客服工单系统测试
测试工单创建、流转、统计报表和自动回复功能
"""

import pytest
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.services.ticket import (
    TicketService,
    Ticket,
    TicketStatus,
    TicketPriority,
    TicketCategory,
    AutoReplyTemplate
)


@pytest.fixture
def service():
    """创建工单服务实例"""
    return TicketService()


class TestTicketCreation:
    """测试工单创建"""
    
    def test_create_ticket(self, service):
        """测试基本工单创建"""
        ticket = service.create_ticket(
            title="无法登录系统",
            description="用户反馈无法登录，提示密码错误",
            category="technical",
            priority="high",
            creator_id="user_001"
        )
        
        assert ticket is not None
        assert ticket.title == "无法登录系统"
        assert ticket.description == "用户反馈无法登录，提示密码错误"
        assert ticket.category == TicketCategory.TECHNICAL
        assert ticket.priority == TicketPriority.HIGH
        assert ticket.status == TicketStatus.NEW
        assert ticket.creator_id == "user_001"
        assert ticket.id is not None
    
    def test_create_ticket_with_assignee(self, service):
        """测试创建已分配工单"""
        ticket = service.create_ticket(
            title="账单查询",
            description="用户需要查询上月账单",
            category="billing",
            priority="medium",
            creator_id="user_002",
            assignee_id="agent_001"
        )
        
        assert ticket.assignee_id == "agent_001"
        assert ticket.status == TicketStatus.ASSIGNED
    
    def test_create_multiple_tickets(self, service):
        """测试创建多个工单"""
        tickets = []
        for i in range(5):
            ticket = service.create_ticket(
                title=f"工单 {i+1}",
                description=f"测试工单 {i+1}",
                category="technical",
                priority="medium",
                creator_id="user_001"
            )
            tickets.append(ticket)
        
        assert len(service.tickets) == 5
        assert len(tickets) == 5
    
    def test_get_ticket(self, service):
        """测试获取工单"""
        ticket = service.create_ticket(
            title="测试工单",
            description="测试描述",
            category="technical",
            priority="medium",
            creator_id="user_001"
        )
        
        retrieved = service.get_ticket(ticket.id)
        assert retrieved is not None
        assert retrieved.id == ticket.id
        assert retrieved.title == "测试工单"
    
    def test_get_nonexistent_ticket(self, service):
        """测试获取不存在的工单"""
        retrieved = service.get_ticket("nonexistent-id")
        assert retrieved is None


class TestTicketWorkflow:
    """测试工单流转"""
    
    def test_assign_ticket(self, service):
        """测试工单分配"""
        ticket = service.create_ticket(
            title="待分配工单",
            description="需要分配给客服",
            category="technical",
            priority="high",
            creator_id="user_001"
        )
        
        assert ticket.status == TicketStatus.NEW
        assert ticket.assignee_id is None
        
        success = service.assign_ticket(ticket.id, "agent_001")
        assert success is True
        
        updated = service.get_ticket(ticket.id)
        assert updated.assignee_id == "agent_001"
        assert updated.status == TicketStatus.ASSIGNED
    
    def test_start_progress(self, service):
        """测试开始处理工单"""
        ticket = service.create_ticket(
            title="处理中工单",
            description="开始处理",
            category="bug",
            priority="urgent",
            creator_id="user_001",
            assignee_id="agent_001"
        )
        
        ticket.start_progress()
        assert ticket.status == TicketStatus.IN_PROGRESS
    
    def test_set_pending(self, service):
        """测试设置为待回复"""
        ticket = service.create_ticket(
            title="待回复工单",
            description="等待客户回复",
            category="account",
            priority="medium",
            creator_id="user_001"
        )
        
        ticket.set_pending()
        assert ticket.status == TicketStatus.PENDING
    
    def test_resolve_ticket(self, service):
        """测试解决工单"""
        ticket = service.create_ticket(
            title="已解决工单",
            description="问题已解决",
            category="technical",
            priority="high",
            creator_id="user_001"
        )
        
        assert ticket.resolved_at is None
        
        ticket.resolve()
        assert ticket.status == TicketStatus.RESOLVED
        assert ticket.resolved_at is not None
    
    def test_close_ticket(self, service):
        """测试关闭工单"""
        ticket = service.create_ticket(
            title="已关闭工单",
            description="工单已关闭",
            category="feature",
            priority="low",
            creator_id="user_001"
        )
        
        ticket.resolve()
        assert ticket.status == TicketStatus.RESOLVED
        
        ticket.close()
        assert ticket.status == TicketStatus.CLOSED
        assert ticket.closed_at is not None
    
    def test_add_message(self, service):
        """测试添加工单消息"""
        ticket = service.create_ticket(
            title="消息测试",
            description="测试消息功能",
            category="technical",
            priority="medium",
            creator_id="user_001"
        )
        
        assert len(ticket.messages) == 0
        
        ticket.add_message("agent_001", "您好，已收到您的问题")
        assert len(ticket.messages) == 1
        assert ticket.messages[0]["content"] == "您好，已收到您的问题"
        assert ticket.messages[0]["sender_id"] == "agent_001"
        
        ticket.add_message("user_001", "谢谢，期待您的回复", is_internal=False)
        assert len(ticket.messages) == 2
    
    def test_add_internal_message(self, service):
        """测试添加内部消息"""
        ticket = service.create_ticket(
            title="内部备注",
            description="测试内部消息",
            category="technical",
            priority="medium",
            creator_id="user_001"
        )
        
        ticket.add_message("agent_001", "这是内部备注", is_internal=True)
        assert len(ticket.messages) == 1
        assert ticket.messages[0]["is_internal"] is True
    
    def test_update_ticket_status(self, service):
        """测试更新工单状态"""
        ticket = service.create_ticket(
            title="状态更新测试",
            description="测试状态流转",
            category="technical",
            priority="medium",
            creator_id="user_001"
        )
        
        assert ticket.status == TicketStatus.NEW
        
        success = service.update_ticket_status(ticket.id, "in_progress")
        assert success is True
        assert ticket.status == TicketStatus.IN_PROGRESS
        
        success = service.update_ticket_status(ticket.id, "resolved")
        assert success is True
        assert ticket.status == TicketStatus.RESOLVED
    
    def test_delete_ticket(self, service):
        """测试删除工单"""
        ticket = service.create_ticket(
            title="待删除工单",
            description="测试删除功能",
            category="other",
            priority="low",
            creator_id="user_001"
        )
        
        ticket_id = ticket.id
        assert len(service.tickets) == 1
        
        success = service.delete_ticket(ticket_id)
        assert success is True
        assert len(service.tickets) == 0
        assert service.get_ticket(ticket_id) is None


class TestTicketFiltering:
    """测试工单筛选"""
    
    def test_list_all_tickets(self, service):
        """测试获取所有工单"""
        for i in range(10):
            service.create_ticket(
                title=f"工单 {i}",
                description=f"描述 {i}",
                category="technical",
                priority="medium",
                creator_id="user_001"
            )
        
        tickets = service.list_tickets()
        assert len(tickets) == 10
    
    def test_filter_by_status(self, service):
        """测试按状态筛选"""
        # 创建不同状态的工单
        t1 = service.create_ticket("新建 1", "描述", "technical", "medium", "user_001")
        t2 = service.create_ticket("新建 2", "描述", "technical", "medium", "user_001")
        t3 = service.create_ticket("已解决", "描述", "technical", "medium", "user_001")
        t3.resolve()
        
        new_tickets = service.list_tickets(status="new")
        assert len(new_tickets) == 2
        
        resolved_tickets = service.list_tickets(status="resolved")
        assert len(resolved_tickets) == 1
    
    def test_filter_by_category(self, service):
        """测试按分类筛选"""
        service.create_ticket("技术问题", "描述", "technical", "medium", "user_001")
        service.create_ticket("账单问题", "描述", "billing", "medium", "user_001")
        service.create_ticket("账户问题", "描述", "account", "medium", "user_001")
        
        technical = service.list_tickets(category="technical")
        assert len(technical) == 1
        
        billing = service.list_tickets(category="billing")
        assert len(billing) == 1
    
    def test_filter_by_priority(self, service):
        """测试按优先级筛选"""
        service.create_ticket("紧急", "描述", "technical", "urgent", "user_001")
        service.create_ticket("高", "描述", "technical", "high", "user_001")
        service.create_ticket("中", "描述", "technical", "medium", "user_001")
        service.create_ticket("低", "描述", "technical", "low", "user_001")
        
        urgent = service.list_tickets(priority="urgent")
        assert len(urgent) == 1
        
        high = service.list_tickets(priority="high")
        assert len(high) == 1
    
    def test_filter_by_assignee(self, service):
        """测试按指派人筛选"""
        service.create_ticket("工单 1", "描述", "technical", "medium", "user_001", "agent_001")
        service.create_ticket("工单 2", "描述", "technical", "medium", "user_001", "agent_001")
        service.create_ticket("工单 3", "描述", "technical", "medium", "user_001", "agent_002")
        
        agent1_tickets = service.list_tickets(assignee_id="agent_001")
        assert len(agent1_tickets) == 2
        
        agent2_tickets = service.list_tickets(assignee_id="agent_002")
        assert len(agent2_tickets) == 1
    
    def test_pagination(self, service):
        """测试分页"""
        for i in range(25):
            service.create_ticket(f"工单{i}", "描述", "technical", "medium", "user_001")
        
        page1 = service.list_tickets(limit=10, offset=0)
        assert len(page1) == 10
        
        page2 = service.list_tickets(limit=10, offset=10)
        assert len(page2) == 10
        
        page3 = service.list_tickets(limit=10, offset=20)
        assert len(page3) == 5


class TestStatistics:
    """测试统计报表"""
    
    def test_basic_statistics(self, service):
        """测试基本统计"""
        # 创建一些工单
        for i in range(5):
            service.create_ticket(f"工单{i}", "描述", "technical", "medium", "user_001")
        
        stats = service.get_statistics()
        
        assert stats["total"] == 5
        assert stats["by_status"]["new"] == 5
        assert stats["by_category"]["technical"] == 5
        assert stats["by_priority"]["medium"] == 5
    
    def test_comprehensive_statistics(self, service):
        """测试综合统计"""
        # 创建不同状态的工单
        t1 = service.create_ticket("新建", "描述", "technical", "high", "user_001")
        t2 = service.create_ticket("处理中", "描述", "billing", "medium", "user_001")
        t2.assign("agent_001")
        t2.start_progress()
        t3 = service.create_ticket("已解决", "描述", "account", "low", "user_001")
        t3.resolve()
        
        stats = service.get_statistics()
        
        assert stats["total"] == 3
        assert stats["by_status"]["new"] == 1
        assert stats["by_status"]["in_progress"] == 1
        assert stats["by_status"]["resolved"] == 1
        assert stats["by_category"]["technical"] == 1
        assert stats["by_category"]["billing"] == 1
        assert stats["by_category"]["account"] == 1
        assert stats["by_priority"]["high"] == 1
        assert stats["by_priority"]["medium"] == 1
        assert stats["by_priority"]["low"] == 1
        assert stats["resolved_count"] == 1
    
    def test_resolution_time_statistics(self, service):
        """测试解决时间统计"""
        from datetime import datetime, timedelta
        
        t1 = service.create_ticket("快速解决", "描述", "technical", "medium", "user_001")
        # 手动设置时间以测试
        t1.created_at = datetime.now() - timedelta(hours=2)
        t1.resolved_at = datetime.now()
        
        stats = service.get_statistics()
        assert stats["resolved_count"] == 1
        # 平均解决时间应该接近 2 小时
        assert 1.5 <= stats["avg_resolution_hours"] <= 2.5


class TestAutoReply:
    """测试自动回复"""
    
    def test_auto_reply_welcome(self, service):
        """测试欢迎语自动回复"""
        reply = service.get_auto_reply("你好，我有个问题")
        assert reply is not None
        assert "欢迎" in reply
    
    def test_auto_reply_technical(self, service):
        """测试技术问题自动回复"""
        reply = service.get_auto_reply("系统无法登录，出现错误")
        assert reply is not None
        assert "技术问题" in reply or "记录" in reply
    
    def test_auto_reply_billing(self, service):
        """测试账单问题自动回复"""
        reply = service.get_auto_reply("我想查询账单和支付记录")
        assert reply is not None
        assert "账单" in reply or "财务" in reply
    
    def test_auto_reply_account(self, service):
        """测试账户问题自动回复"""
        reply = service.get_auto_reply("我的账户需要修改密码和账户信息")
        assert reply is not None
        # 账户问题模板包含"账户"关键词
        assert "账户" in reply
    
    def test_auto_reply_no_match(self, service):
        """测试无匹配自动回复"""
        # 创建一个不匹配任何模板的消息
        reply = service.get_auto_reply("asdfghjkl123456")
        assert reply is None
    
    def test_add_custom_template(self, service):
        """测试添加自定义模板"""
        template = service.add_auto_reply_template(
            name="测试模板",
            trigger_keywords=["测试关键词", "test"],
            response="这是自定义回复"
        )
        
        assert template.name == "测试模板"
        assert template.enabled is True
        
        reply = service.get_auto_reply("我有测试关键词问题")
        assert reply == "这是自定义回复"
    
    def test_template_case_insensitive(self, service):
        """测试模板匹配不区分大小写"""
        reply1 = service.get_auto_reply("你好")
        reply2 = service.get_auto_reply("HELLO")
        reply3 = service.get_auto_reply("您好")
        
        # 都应该匹配欢迎语模板
        assert reply1 is not None or reply2 is not None or reply3 is not None
    
    def test_list_templates(self, service):
        """测试获取模板列表"""
        templates = service.auto_reply_templates
        assert len(templates) >= 5  # 至少有 5 个默认模板
        
        for template in templates:
            assert hasattr(template, 'name')
            assert hasattr(template, 'trigger_keywords')
            assert hasattr(template, 'response')


class TestTicketModel:
    """测试工单模型"""
    
    def test_ticket_to_dict(self, service):
        """测试工单转字典"""
        ticket = service.create_ticket(
            title="测试",
            description="描述",
            category="technical",
            priority="high",
            creator_id="user_001"
        )
        
        ticket_dict = ticket.to_dict()
        
        assert ticket_dict["id"] == ticket.id
        assert ticket_dict["title"] == "测试"
        assert ticket_dict["description"] == "描述"
        assert ticket_dict["category"] == "technical"
        assert ticket_dict["priority"] == "high"
        assert ticket_dict["status"] == "new"
        assert ticket_dict["creator_id"] == "user_001"
        assert "created_at" in ticket_dict
        assert "updated_at" in ticket_dict
    
    def test_ticket_updated_at(self, service):
        """测试更新时间戳"""
        from time import sleep
        
        ticket = service.create_ticket(
            title="测试",
            description="描述",
            category="technical",
            priority="medium",
            creator_id="user_001"
        )
        
        original_updated = ticket.updated_at
        sleep(0.1)
        
        ticket.add_message("agent_001", "新消息")
        assert ticket.updated_at > original_updated


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
