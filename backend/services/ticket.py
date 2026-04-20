"""
客服工单管理服务
提供工单创建、分类、优先级、分配、流转、状态跟踪和统计功能
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
import uuid


class TicketStatus(Enum):
    """工单状态枚举"""
    NEW = "new"  # 新建
    ASSIGNED = "assigned"  # 已分配
    IN_PROGRESS = "in_progress"  # 处理中
    PENDING = "pending"  # 待回复
    RESOLVED = "resolved"  # 已解决
    CLOSED = "closed"  # 已关闭


class TicketPriority(Enum):
    """工单优先级枚举"""
    LOW = "low"  # 低
    MEDIUM = "medium"  # 中
    HIGH = "high"  # 高
    URGENT = "urgent"  # 紧急


class TicketCategory(Enum):
    """工单分类枚举"""
    TECHNICAL = "technical"  # 技术问题
    BILLING = "billing"  # 账单问题
    ACCOUNT = "account"  # 账户问题
    FEATURE = "feature"  # 功能建议
    BUG = "bug"  # Bug 报告
    OTHER = "other"  # 其他


class Ticket:
    """工单模型"""
    
    def __init__(
        self,
        title: str,
        description: str,
        category: TicketCategory,
        priority: TicketPriority,
        creator_id: str,
        assignee_id: Optional[str] = None
    ):
        self.id = str(uuid.uuid4())
        self.title = title
        self.description = description
        self.category = category
        self.priority = priority
        self.status = TicketStatus.NEW
        self.creator_id = creator_id
        self.assignee_id = assignee_id
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.resolved_at: Optional[datetime] = None
        self.closed_at: Optional[datetime] = None
        self.messages: List[Dict] = []  # 工单消息历史
        self.tags: List[str] = []
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "category": self.category.value,
            "priority": self.priority.value,
            "status": self.status.value,
            "creator_id": self.creator_id,
            "assignee_id": self.assignee_id,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "closed_at": self.closed_at.isoformat() if self.closed_at else None,
            "messages": self.messages,
            "tags": self.tags
        }
    
    def add_message(self, sender_id: str, content: str, is_internal: bool = False):
        """添加消息"""
        self.messages.append({
            "id": str(uuid.uuid4()),
            "sender_id": sender_id,
            "content": content,
            "is_internal": is_internal,
            "created_at": datetime.now().isoformat()
        })
        self.updated_at = datetime.now()
    
    def assign(self, assignee_id: str):
        """分配工单"""
        self.assignee_id = assignee_id
        self.status = TicketStatus.ASSIGNED
        self.updated_at = datetime.now()
    
    def start_progress(self):
        """开始处理"""
        self.status = TicketStatus.IN_PROGRESS
        self.updated_at = datetime.now()
    
    def set_pending(self):
        """设置为待回复"""
        self.status = TicketStatus.PENDING
        self.updated_at = datetime.now()
    
    def resolve(self):
        """解决工单"""
        self.status = TicketStatus.RESOLVED
        self.resolved_at = datetime.now()
        self.updated_at = datetime.now()
    
    def close(self):
        """关闭工单"""
        self.status = TicketStatus.CLOSED
        self.closed_at = datetime.now()
        self.updated_at = datetime.now()


class AutoReplyTemplate:
    """自动回复模板"""
    
    def __init__(self, name: str, trigger_keywords: List[str], response: str):
        self.id = str(uuid.uuid4())
        self.name = name
        self.trigger_keywords = trigger_keywords
        self.response = response
        self.enabled = True
    
    def matches(self, text: str) -> bool:
        """检查是否匹配关键词"""
        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in self.trigger_keywords)


class TicketService:
    """工单服务类"""
    
    def __init__(self):
        self.tickets: Dict[str, Ticket] = {}
        self.auto_reply_templates: List[AutoReplyTemplate] = []
        self._init_default_templates()
    
    def _init_default_templates(self):
        """初始化默认自动回复模板"""
        self.auto_reply_templates = [
            AutoReplyTemplate(
                name="欢迎语",
                trigger_keywords=["你好", "hello", "hi", "您好"],
                response="您好！欢迎使用客服工单系统。我们已经收到您的消息，会尽快为您处理。"
            ),
            AutoReplyTemplate(
                name="技术问题确认",
                trigger_keywords=["无法", "不能", "错误", "error", "bug", "故障"],
                response="感谢您的反馈。我们已经记录了您遇到的技术问题，技术团队会尽快排查并给您回复。"
            ),
            AutoReplyTemplate(
                name="账单问题确认",
                trigger_keywords=["费用", "账单", "支付", "充值", "退款", "invoice", "payment"],
                response="您好，关于账单/支付问题，我们会转交给财务专员处理。请提供相关订单号以便我们更快为您解决。"
            ),
            AutoReplyTemplate(
                name="账户问题确认",
                trigger_keywords=["账号", "登录", "密码", "账户", "account", "login"],
                response="您好，账户相关问题我们会优先处理。为了您的账户安全，请提供相关信息以便我们核实后继续协助您。"
            ),
            AutoReplyTemplate(
                name="非工作时间",
                trigger_keywords=[],
                response="您好，当前是非工作时间。我们已收到您的消息，将在下一个工作日尽快处理。紧急问题请拨打客服热线。"
            )
        ]
    
    def create_ticket(
        self,
        title: str,
        description: str,
        category: str,
        priority: str,
        creator_id: str,
        assignee_id: Optional[str] = None
    ) -> Ticket:
        """创建工单"""
        ticket = Ticket(
            title=title,
            description=description,
            category=TicketCategory(category),
            priority=TicketPriority(priority),
            creator_id=creator_id,
            assignee_id=assignee_id
        )
        # 如果有指派人，自动设置为已分配状态
        if assignee_id:
            ticket.status = TicketStatus.ASSIGNED
        self.tickets[ticket.id] = ticket
        return ticket
    
    def get_ticket(self, ticket_id: str) -> Optional[Ticket]:
        """获取工单"""
        return self.tickets.get(ticket_id)
    
    def list_tickets(
        self,
        status: Optional[str] = None,
        category: Optional[str] = None,
        priority: Optional[str] = None,
        assignee_id: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Ticket]:
        """获取工单列表（支持筛选）"""
        result = list(self.tickets.values())
        
        if status:
            result = [t for t in result if t.status.value == status]
        if category:
            result = [t for t in result if t.category.value == category]
        if priority:
            result = [t for t in result if t.priority.value == priority]
        if assignee_id:
            result = [t for t in result if t.assignee_id == assignee_id]
        
        # 按创建时间倒序
        result.sort(key=lambda t: t.created_at, reverse=True)
        
        return result[offset:offset + limit]
    
    def update_ticket_status(self, ticket_id: str, status: str) -> bool:
        """更新工单状态"""
        ticket = self.tickets.get(ticket_id)
        if not ticket:
            return False
        
        status_enum = TicketStatus(status)
        if status_enum == TicketStatus.IN_PROGRESS:
            ticket.start_progress()
        elif status_enum == TicketStatus.PENDING:
            ticket.set_pending()
        elif status_enum == TicketStatus.RESOLVED:
            ticket.resolve()
        elif status_enum == TicketStatus.CLOSED:
            ticket.close()
        
        return True
    
    def assign_ticket(self, ticket_id: str, assignee_id: str) -> bool:
        """分配工单"""
        ticket = self.tickets.get(ticket_id)
        if not ticket:
            return False
        
        ticket.assign(assignee_id)
        return True
    
    def add_message(
        self,
        ticket_id: str,
        sender_id: str,
        content: str,
        is_internal: bool = False
    ) -> bool:
        """添加消息"""
        ticket = self.tickets.get(ticket_id)
        if not ticket:
            return False
        
        ticket.add_message(sender_id, content, is_internal)
        return True
    
    def get_auto_reply(self, content: str) -> Optional[str]:
        """获取自动回复"""
        for template in self.auto_reply_templates:
            if template.enabled and template.matches(content):
                return template.response
        return None
    
    def add_auto_reply_template(
        self,
        name: str,
        trigger_keywords: List[str],
        response: str
    ) -> AutoReplyTemplate:
        """添加自动回复模板"""
        template = AutoReplyTemplate(name, trigger_keywords, response)
        self.auto_reply_templates.append(template)
        return template
    
    def get_statistics(self) -> Dict:
        """获取统计报表"""
        total = len(self.tickets)
        
        # 按状态统计
        status_counts = {}
        for status in TicketStatus:
            status_counts[status.value] = len([t for t in self.tickets.values() if t.status == status])
        
        # 按分类统计
        category_counts = {}
        for category in TicketCategory:
            category_counts[category.value] = len([t for t in self.tickets.values() if t.category == category])
        
        # 按优先级统计
        priority_counts = {}
        for priority in TicketPriority:
            priority_counts[priority.value] = len([t for t in self.tickets.values() if t.priority == priority])
        
        # 平均解决时间（小时）
        resolved_tickets = [t for t in self.tickets.values() if t.resolved_at]
        avg_resolution_hours = 0
        if resolved_tickets:
            total_hours = sum(
                (t.resolved_at - t.created_at).total_seconds() / 3600
                for t in resolved_tickets
            )
            avg_resolution_hours = round(total_hours / len(resolved_tickets), 2)
        
        return {
            "total": total,
            "by_status": status_counts,
            "by_category": category_counts,
            "by_priority": priority_counts,
            "avg_resolution_hours": avg_resolution_hours,
            "resolved_count": len(resolved_tickets),
            "closed_count": len([t for t in self.tickets.values() if t.status == TicketStatus.CLOSED])
        }
    
    def delete_ticket(self, ticket_id: str) -> bool:
        """删除工单"""
        if ticket_id in self.tickets:
            del self.tickets[ticket_id]
            return True
        return False


# 全局服务实例
ticket_service = TicketService()
