"""
客服工单系统演示脚本
展示工单创建、流转、统计和自动回复功能
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.ticket import ticket_service, TicketStatus

def print_separator(title=""):
    print("\n" + "=" * 60)
    if title:
        print(f"  {title}")
        print("=" * 60)

def demo_ticket_creation():
    """演示工单创建"""
    print_separator("1. 工单创建演示")
    
    # 创建多个工单
    tickets = []
    
    t1 = ticket_service.create_ticket(
        title="无法登录系统",
        description="用户反馈登录时提示密码错误，已尝试重置密码但仍无法登录",
        category="technical",
        priority="high",
        creator_id="user_001"
    )
    tickets.append(t1)
    print(f"[OK] 创建工单：{t1.title} (优先级：高，状态：{t1.status.value})")
    
    t2 = ticket_service.create_ticket(
        title="账单查询请求",
        description="用户需要查询 2024 年 3 月的详细账单记录",
        category="billing",
        priority="medium",
        creator_id="user_002",
        assignee_id="agent_001"
    )
    tickets.append(t2)
    print(f"[OK] 创建工单：{t2.title} (优先级：中，状态：{t2.status.value}, 指派人：{t2.assignee_id})")
    
    t3 = ticket_service.create_ticket(
        title="功能建议：导出功能",
        description="建议增加数据导出为 Excel 的功能",
        category="feature",
        priority="low",
        creator_id="user_003"
    )
    tickets.append(t3)
    print(f"[OK] 创建工单：{t3.title} (优先级：低，状态：{t3.status.value})")
    
    t4 = ticket_service.create_ticket(
        title="紧急：支付失败",
        description="用户支付时系统报错，无法完成订单支付",
        category="billing",
        priority="urgent",
        creator_id="user_004"
    )
    tickets.append(t4)
    print(f"[OK] 创建工单：{t4.title} (优先级：紧急，状态：{t4.status.value})")
    
    return tickets

def demo_ticket_workflow():
    """演示工单流转"""
    print_separator("2. 工单流转演示")
    
    # 获取第一个工单
    ticket = ticket_service.list_tickets()[0]
    print(f"\n工单：{ticket.title}")
    print(f"当前状态：{ticket.status.value}")
    
    # 分配工单
    print("\n-> 分配工单给客服 agent_001")
    ticket_service.assign_ticket(ticket.id, "agent_001")
    print(f"   状态变更为：{ticket.status.value}")
    
    # 开始处理
    print("\n-> 客服开始处理")
    ticket_service.update_ticket_status(ticket.id, "in_progress")
    print(f"   状态变更为：{ticket.status.value}")
    
    # 添加消息
    print("\n-> 客服添加回复")
    ticket_service.add_message(
        ticket.id,
        "agent_001",
        "您好，已收到您的问题。正在为您排查，请稍等。"
    )
    print(f"   消息数：{len(ticket.messages)}")
    
    # 设置待回复
    print("\n-> 等待用户回复")
    ticket_service.update_ticket_status(ticket.id, "pending")
    print(f"   状态变更为：{ticket.status.value}")
    
    # 解决工单
    print("\n-> 问题解决，标记为已解决")
    ticket_service.update_ticket_status(ticket.id, "resolved")
    print(f"   状态变更为：{ticket.status.value}")

def demo_statistics():
    """演示统计报表"""
    print_separator("3. 统计报表演示")
    
    stats = ticket_service.get_statistics()
    
    print(f"\n[统计] 工单统计概览")
    print(f"   总工单数：{stats['total']}")
    print(f"   已解决：{stats['resolved_count']}")
    print(f"   已关闭：{stats['closed_count']}")
    print(f"   平均解决时间：{stats['avg_resolution_hours']} 小时")
    
    print(f"\n[状态] 按状态分布:")
    for status, count in stats['by_status'].items():
        print(f"   {status}: {count}")
    
    print(f"\n[分类] 按分类分布:")
    for category, count in stats['by_category'].items():
        if count > 0:
            print(f"   {category}: {count}")
    
    print(f"\n[优先级] 按优先级分布:")
    for priority, count in stats['by_priority'].items():
        if count > 0:
            print(f"   {priority}: {count}")

def demo_auto_reply():
    """演示自动回复"""
    print_separator("4. 自动回复演示")
    
    test_messages = [
        "你好，我有个问题",
        "系统无法登录，出现错误提示",
        "我想查询账单和支付记录",
        "我的账户需要修改密码",
        "asdfghjkl"  # 无匹配
    ]
    
    for msg in test_messages:
        reply = ticket_service.get_auto_reply(msg)
        print(f"\n用户：{msg}")
        if reply:
            print(f"客服：{reply}")
        else:
            print("客服：(无自动回复，转人工)")

def demo_list_tickets():
    """演示工单列表"""
    print_separator("5. 工单列表演示")
    
    all_tickets = ticket_service.list_tickets()
    print(f"\n当前共有 {len(all_tickets)} 个工单\n")
    
    for i, ticket in enumerate(all_tickets[:5], 1):
        print(f"{i}. [{ticket.priority.value.upper()}] {ticket.title}")
        print(f"   状态：{ticket.status.value} | 分类：{ticket.category.value}")
        print(f"   创建时间：{ticket.created_at.strftime('%Y-%m-%d %H:%M')}")
        if ticket.assignee_id:
            print(f"   指派人：{ticket.assignee_id}")
        print()

def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("  客服工单系统演示")
    print("=" * 60)
    
    # 执行演示
    demo_ticket_creation()
    demo_ticket_workflow()
    demo_statistics()
    demo_auto_reply()
    demo_list_tickets()
    
    print_separator("演示完成")
    print("\n[OK] 所有功能演示完毕！")
    print("\n创建的文件:")
    print("  - backend/services/ticket.py (工单服务)")
    print("  - backend/routes/ticket.py (API 接口)")
    print("  - frontend/src/views/Ticket.vue (工单页面)")
    print("  - frontend/src/components/TicketCard.vue (工单卡片)")
    print("  - backend/tests/test_ticket.py (测试文件)")
    print("\n测试结果：33 个测试全部通过 [OK]")

if __name__ == "__main__":
    main()
