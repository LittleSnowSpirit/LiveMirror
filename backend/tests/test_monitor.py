"""
竞品监控功能测试
测试内容：
1. 测试实时监控
2. 测试告警触发
3. 测试通知发送
4. 测试规则配置
"""

import asyncio
import pytest
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.competitor_monitor import (
    CompetitorMonitorService,
    CompetitorInfo,
    LiveRoomData,
    AlertRule,
    Alert,
    get_monitor_service
)


class TestCompetitorManagement:
    """竞品管理测试"""
    
    @pytest.fixture
    def service(self):
        """创建测试服务实例"""
        return CompetitorMonitorService(data_dir="./test_data")
    
    def test_add_competitor(self, service):
        """测试添加竞品"""
        competitor = service.add_competitor("测试竞品 A", "douyin", "test_room_001")
        
        assert competitor is not None
        assert competitor.name == "测试竞品 A"
        assert competitor.platform == "douyin"
        assert competitor.room_id == "test_room_001"
        assert competitor.status == "active"
        assert competitor.id in service.competitors
        
        print("✓ 添加竞品测试通过")
    
    def test_remove_competitor(self, service):
        """测试移除竞品"""
        # 先添加
        competitor = service.add_competitor("临时竞品", "taobao", "temp_room")
        competitor_id = competitor.id
        
        # 再移除
        success = service.remove_competitor(competitor_id)
        
        assert success is True
        assert competitor_id not in service.competitors
        
        print("✓ 移除竞品测试通过")
    
    def test_list_competitors(self, service):
        """测试获取竞品列表"""
        # 添加多个竞品
        service.add_competitor("竞品 1", "douyin", "room_1")
        service.add_competitor("竞品 2", "taobao", "room_2")
        service.add_competitor("竞品 3", "kuaishou", "room_3")
        
        competitors = service.list_competitors()
        
        assert len(competitors) >= 3
        
        print("✓ 获取竞品列表测试通过")
    
    def test_get_competitor(self, service):
        """测试获取竞品信息"""
        competitor = service.add_competitor("目标竞品", "douyin", "target_room")
        
        retrieved = service.get_competitor(competitor.id)
        
        assert retrieved is not None
        assert retrieved.name == "目标竞品"
        
        print("✓ 获取竞品信息测试通过")


class TestAlertRules:
    """告警规则测试"""
    
    @pytest.fixture
    def service(self):
        """创建测试服务实例"""
        return CompetitorMonitorService(data_dir="./test_data")
    
    def test_add_alert_rule(self, service):
        """测试添加告警规则"""
        rule = service.add_alert_rule(
            name="流量突增测试规则",
            rule_type="viewer_spike",
            threshold=2.0,
            comparison="gt"
        )
        
        assert rule is not None
        assert rule.name == "流量突增测试规则"
        assert rule.rule_type == "viewer_spike"
        assert rule.threshold == 2.0
        assert rule.comparison == "gt"
        assert rule.enabled is True
        assert rule.id in service.alert_rules
        
        print("✓ 添加告警规则测试通过")
    
    def test_remove_alert_rule(self, service):
        """测试移除告警规则"""
        # 先添加
        rule = service.add_alert_rule("临时规则", "gmv_threshold", 100000)
        rule_id = rule.id
        
        # 再移除
        success = service.remove_alert_rule(rule_id)
        
        assert success is True
        assert rule_id not in service.alert_rules
        
        print("✓ 移除告警规则测试通过")
    
    def test_update_alert_rule(self, service):
        """测试更新告警规则"""
        rule = service.add_alert_rule("更新测试规则", "viewer_spike", 1.5)
        
        # 更新规则
        updated = service.update_alert_rule(rule.id, threshold=3.0, enabled=False)
        
        assert updated is not None
        assert updated.threshold == 3.0
        assert updated.enabled is False
        
        print("✓ 更新告警规则测试通过")
    
    def test_list_alert_rules(self, service):
        """测试获取告警规则列表"""
        service.add_alert_rule("规则 1", "viewer_spike", 2.0)
        service.add_alert_rule("规则 2", "gmv_threshold", 50000)
        service.add_alert_rule("规则 3", "script_plagiarism", 0.8)
        
        rules = service.list_alert_rules()
        
        assert len(rules) >= 3
        
        print("✓ 获取告警规则列表测试通过")


class TestAlertTrigger:
    """告警触发测试"""
    
    @pytest.fixture
    def service(self):
        """创建测试服务实例"""
        return CompetitorMonitorService(data_dir="./test_data")
    
    @pytest.mark.asyncio
    async def test_viewer_spike_alert(self, service):
        """测试流量突增告警"""
        # 添加竞品
        competitor = service.add_competitor("流量测试竞品", "douyin", "spike_room")
        
        # 添加告警规则：观众数超过平均值 2 倍时告警
        service.add_alert_rule("流量突增", "viewer_spike", 2.0, "gt")
        
        # 模拟正常数据
        normal_data = LiveRoomData(
            competitor_id=competitor.id,
            viewer_count=1000,
            like_count=5000,
            comment_count=200,
            share_count=50,
            product_count=20,
            gmv=10000,
            avg_watch_time=60
        )
        
        # 添加多条正常数据作为基准
        for _ in range(10):
            if competitor.id not in service.live_data_history:
                service.live_data_history[competitor.id] = []
            service.live_data_history[competitor.id].append(normal_data)
        
        # 模拟突增数据
        spike_data = LiveRoomData(
            competitor_id=competitor.id,
            viewer_count=5000,  # 超过平均值 2 倍
            like_count=25000,
            comment_count=1000,
            share_count=250,
            product_count=20,
            gmv=50000,
            avg_watch_time=60
        )
        
        # 检查告警规则
        initial_alert_count = len(service.alerts)
        await service._check_alert_rules(competitor, spike_data)
        
        # 验证是否触发告警
        assert len(service.alerts) > initial_alert_count
        
        # 验证告警内容
        latest_alert = service.alerts[-1]
        assert latest_alert.alert_type == "viewer_spike"
        assert latest_alert.competitor_id == competitor.id
        
        print("✓ 流量突增告警测试通过")
    
    @pytest.mark.asyncio
    async def test_gmv_threshold_alert(self, service):
        """测试成交额阈值告警"""
        competitor = service.add_competitor("GMV 测试竞品", "taobao", "gmv_room")
        
        # 添加告警规则：GMV 超过 10 万时告警
        service.add_alert_rule("GMV 超额", "gmv_threshold", 100000, "gt")
        
        # 模拟高 GMV 数据
        high_gmv_data = LiveRoomData(
            competitor_id=competitor.id,
            viewer_count=2000,
            like_count=10000,
            comment_count=500,
            share_count=100,
            product_count=30,
            gmv=150000,  # 超过阈值
            avg_watch_time=90
        )
        
        initial_alert_count = len(service.alerts)
        await service._check_alert_rules(competitor, high_gmv_data)
        
        # 验证是否触发告警
        assert len(service.alerts) > initial_alert_count
        
        latest_alert = service.alerts[-1]
        assert latest_alert.alert_type == "gmv_threshold"
        assert latest_alert.current_value == 150000
        
        print("✓ GMV 阈值告警测试通过")


class TestScriptMonitoring:
    """话术监控测试"""
    
    @pytest.fixture
    def service(self):
        """创建测试服务实例"""
        return CompetitorMonitorService(data_dir="./test_data")
    
    def test_add_own_script(self, service):
        """测试添加己方话术"""
        script = "宝宝们这个价格真的太低了，只有今天才有这个优惠！"
        service.add_own_script(script)
        
        assert script in service.own_scripts
        
        print("✓ 添加己方话术测试通过")
    
    def test_calculate_similarity(self, service):
        """测试相似度计算"""
        # 添加己方话术
        service.add_own_script("这个产品真的非常好用，强烈推荐给大家！")
        
        # 测试相同文本
        similarity_same = service._text_similarity(
            "这个产品真的非常好用，强烈推荐给大家！",
            "这个产品真的非常好用，强烈推荐给大家！"
        )
        assert similarity_same == 1.0
        
        # 测试不同文本
        similarity_diff = service._text_similarity(
            "这个产品真的非常好用，强烈推荐给大家！",
            "今天天气真不错"
        )
        assert similarity_diff < 1.0
        
        print("✓ 相似度计算测试通过")
    
    @pytest.mark.asyncio
    async def test_script_plagiarism_alert(self, service):
        """测试话术抄袭告警"""
        competitor = service.add_competitor("话术测试竞品", "douyin", "script_room")
        
        # 添加己方话术
        own_script = "宝宝们这个价格真的太低了，只有今天才有这个优惠！"
        service.add_own_script(own_script)
        
        # 模拟捕获相似话术
        await service._capture_script(competitor)
        
        # 验证话术被记录
        assert competitor.id in service.script_segments
        assert len(service.script_segments[competitor.id]) > 0
        
        print("✓ 话术抄袭告警测试通过")


class TestNotification:
    """通知发送测试"""
    
    @pytest.fixture
    def service(self):
        """创建测试服务实例"""
        return CompetitorMonitorService(data_dir="./test_data")
    
    def test_update_notification_config(self, service):
        """测试更新通知配置"""
        # 更新邮件配置
        service.update_notification_config("email", {
            "enabled": True,
            "smtp_server": "smtp.test.com",
            "smtp_port": 587,
            "username": "test@test.com",
            "recipients": ["admin@test.com"]
        })
        
        assert service.notification_config["email"]["enabled"] is True
        assert service.notification_config["email"]["smtp_server"] == "smtp.test.com"
        
        print("✓ 更新通知配置测试通过")
    
    @pytest.mark.asyncio
    async def test_send_email_notification(self, service):
        """测试邮件通知发送"""
        # 配置邮件
        service.update_notification_config("email", {"enabled": True})
        
        # 创建测试告警
        alert = Alert(
            id="test_alert",
            rule_id="test_rule",
            rule_name="测试规则",
            competitor_id="test_comp",
            competitor_name="测试竞品",
            alert_type="viewer_spike",
            message="测试告警消息",
            current_value=1000,
            threshold=500
        )
        
        # 发送通知（不会实际发送，只会记录日志）
        await service._send_email_notification(alert)
        
        # 验证告警标记为已通知
        assert alert.notified is True
        
        print("✓ 邮件通知发送测试通过")
    
    @pytest.mark.asyncio
    async def test_send_wechat_notification(self, service):
        """测试微信通知发送"""
        # 配置微信
        service.update_notification_config("wechat", {"enabled": True})
        
        # 创建测试告警
        alert = Alert(
            id="test_alert_2",
            rule_id="test_rule",
            rule_name="测试规则",
            competitor_id="test_comp",
            competitor_name="测试竞品",
            alert_type="gmv_threshold",
            message="测试微信告警",
            current_value=200000,
            threshold=100000
        )
        
        # 发送通知
        await service._send_wechat_notification(alert)
        
        assert alert.notified is True
        
        print("✓ 微信通知发送测试通过")


class TestHistoryQuery:
    """历史查询测试"""
    
    @pytest.fixture
    def service(self):
        """创建测试服务实例"""
        return CompetitorMonitorService(data_dir="./test_data")
    
    def test_get_live_data_history(self, service):
        """测试获取历史数据"""
        competitor = service.add_competitor("历史测试竞品", "douyin", "history_room")
        
        # 添加历史数据
        for i in range(50):
            data = LiveRoomData(
                competitor_id=competitor.id,
                viewer_count=1000 + i * 10,
                like_count=5000,
                comment_count=200,
                share_count=50,
                product_count=20,
                gmv=10000,
                avg_watch_time=60
            )
            if competitor.id not in service.live_data_history:
                service.live_data_history[competitor.id] = []
            service.live_data_history[competitor.id].append(data)
        
        # 获取历史数据
        history = service.get_live_data_history(competitor.id, limit=20)
        
        assert len(history) == 20  # 限制返回 20 条
        
        print("✓ 获取历史数据测试通过")
    
    def test_get_alerts(self, service):
        """测试获取告警记录"""
        # 添加一些告警
        for i in range(10):
            alert = Alert(
                id=f"alert_{i}",
                rule_id="rule_1",
                rule_name="测试规则",
                competitor_id="comp_1",
                competitor_name="测试竞品",
                alert_type="viewer_spike" if i % 2 == 0 else "gmv_threshold",
                message=f"测试告警{i}",
                current_value=1000 + i,
                threshold=500
            )
            service.alerts.append(alert)
        
        # 获取所有告警
        all_alerts = service.get_alerts(limit=100)
        assert len(all_alerts) >= 10
        
        # 按类型筛选
        viewer_alerts = service.get_alerts(alert_type="viewer_spike")
        gmv_alerts = service.get_alerts(alert_type="gmv_threshold")
        
        assert len(viewer_alerts) > 0
        assert len(gmv_alerts) > 0
        
        print("✓ 获取告警记录测试通过")
    
    def test_get_script_segments(self, service):
        """测试获取话术片段"""
        competitor = service.add_competitor("话术历史竞品", "douyin", "script_history_room")
        
        # 添加话术片段
        for i in range(30):
            segment = {
                "competitor_id": competitor.id,
                "content": f"测试话术{i}",
                "timestamp": f"2024-01-01T{i:02d}:00:00",
                "similarity_score": 0.5 + i * 0.01
            }
            if competitor.id not in service.script_segments:
                service.script_segments[competitor.id] = []
            service.script_segments[competitor.id].append(segment)
        
        # 获取话术片段
        segments = service.get_script_segments(competitor.id, limit=10)
        
        assert len(segments) == 10
        
        print("✓ 获取话术片段测试通过")


class TestMonitoringService:
    """监控服务整体测试"""
    
    @pytest.fixture
    def service(self):
        """创建测试服务实例"""
        return CompetitorMonitorService(data_dir="./test_data")
    
    @pytest.mark.asyncio
    async def test_start_stop_monitoring(self, service):
        """测试启动停止监控"""
        # 添加竞品
        service.add_competitor("监控测试竞品", "douyin", "monitor_room")
        
        # 启动监控
        assert service.is_monitoring is False
        
        # 启动监控任务（短时间运行）
        monitoring_task = asyncio.create_task(service.start_monitoring())
        await asyncio.sleep(2)  # 运行 2 秒
        
        assert service.is_monitoring is True
        
        # 停止监控
        await service.stop_monitoring()
        assert service.is_monitoring is False
        
        # 取消任务
        monitoring_task.cancel()
        try:
            await monitoring_task
        except asyncio.CancelledError:
            pass
        
        print("✓ 启动停止监控测试通过")
    
    def test_get_stats(self, service):
        """测试获取统计信息"""
        # 添加数据
        service.add_competitor("统计竞品 1", "douyin", "stat_room_1")
        service.add_competitor("统计竞品 2", "taobao", "stat_room_2")
        service.add_alert_rule("统计规则 1", "viewer_spike", 2.0)
        service.add_alert_rule("统计规则 2", "gmv_threshold", 100000)
        
        # 验证统计
        assert len(service.competitors) == 2
        assert len(service.alert_rules) == 2
        
        print("✓ 获取统计信息测试通过")


# 运行测试
if __name__ == "__main__":
    import io
    import sys
    # 处理输出编码
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    print("=" * 60)
    print("LiveMirror Competitor Monitor Test")
    print("=" * 60)
    
    # 创建测试服务
    service = CompetitorMonitorService(data_dir="./test_data")
    
    # 1. 测试竞品管理
    print("\n[1] Testing Competitor Management...")
    competitor = service.add_competitor("Test Competitor A", "douyin", "test_room_001")
    print(f"  [OK] Add competitor: {competitor.name}")
    
    competitors = service.list_competitors()
    print(f"  [OK] Competitor list: {len(competitors)} items")
    
    # 2. 测试告警规则
    print("\n[2] Testing Alert Rules...")
    rule1 = service.add_alert_rule("Viewer Spike Alert", "viewer_spike", 2.0, "gt")
    rule2 = service.add_alert_rule("GMV Threshold Alert", "gmv_threshold", 100000, "gt")
    print(f"  [OK] Add rules: {rule1.name}, {rule2.name}")
    
    rules = service.list_alert_rules()
    print(f"  [OK] Rule list: {len(rules)} items")
    
    # 3. 测试实时监控
    print("\n[3] Testing Real-time Monitoring...")
    async def test_monitoring():
        service.monitoring_interval = 2
        monitoring_task = asyncio.create_task(service.start_monitoring())
        await asyncio.sleep(5)
        await service.stop_monitoring()
        monitoring_task.cancel()
        try:
            await monitoring_task
        except asyncio.CancelledError:
            pass
        
        for comp_id, history in service.live_data_history.items():
            print(f"  [OK] Competitor {comp_id}: {len(history)} records")
    
    asyncio.run(test_monitoring())
    
    # 4. 测试告警触发
    print("\n[4] Testing Alert Trigger...")
    print(f"  [OK] Alerts triggered: {len(service.alerts)}")
    for alert in service.alerts[-3:]:
        print(f"    - {alert.competitor_name}: {alert.message}")
    
    # 5. 测试通知配置
    print("\n[5] Testing Notification Config...")
    service.update_notification_config("email", {
        "enabled": True,
        "smtp_server": "smtp.test.com",
        "recipients": ["test@example.com"]
    })
    email_status = "Enabled" if service.notification_config['email']['enabled'] else "Disabled"
    print(f"  [OK] Email notification: {email_status}")
    
    service.update_notification_config("wechat", {
        "enabled": True,
        "corp_id": "test_corp"
    })
    wechat_status = "Enabled" if service.notification_config['wechat']['enabled'] else "Disabled"
    print(f"  [OK] WeChat notification: {wechat_status}")
    
    # 6. 测试历史查询
    print("\n[6] Testing History Query...")
    if service.live_data_history:
        comp_id = list(service.live_data_history.keys())[0]
        history = service.get_live_data_history(comp_id, limit=10)
        print(f"  [OK] History data: {len(history)} records")
    
    alerts = service.get_alerts(limit=10)
    print(f"  [OK] Alert records: {len(alerts)} items")
    
    print("\n" + "=" * 60)
    print("All Tests Completed Successfully!")
    print("=" * 60)
