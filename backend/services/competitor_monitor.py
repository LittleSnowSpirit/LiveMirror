"""
竞品直播间监控服务
功能：
1. 竞品直播间实时监控
2. 异常数据告警（流量突增/话术抄袭）
3. 竞品动态追踪（新品/活动）
4. 告警通知（邮件/微信）
5. 监控历史查询
6. 告警规则配置
"""

import asyncio
import json
import time
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import logging

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class CompetitorInfo:
    """竞品信息"""
    id: str
    name: str
    platform: str  # douyin, taobao, kuaishou, etc.
    room_id: str
    status: str = "active"  # active, inactive
    added_at: str = ""
    
    def __post_init__(self):
        if not self.added_at:
            self.added_at = datetime.now().isoformat()


@dataclass
class LiveRoomData:
    """直播间实时数据"""
    competitor_id: str
    viewer_count: int
    like_count: int
    comment_count: int
    share_count: int
    product_count: int
    gmv: float  # 成交额
    avg_watch_time: float  # 平均观看时长（秒）
    capture_time: str
    
    @classmethod
    def from_dict(cls, data: Dict) -> "LiveRoomData":
        return cls(
            competitor_id=data.get("competitor_id", ""),
            viewer_count=data.get("viewer_count", 0),
            like_count=data.get("like_count", 0),
            comment_count=data.get("comment_count", 0),
            share_count=data.get("share_count", 0),
            product_count=data.get("product_count", 0),
            gmv=data.get("gmv", 0.0),
            avg_watch_time=data.get("avg_watch_time", 0.0),
            capture_time=data.get("capture_time", datetime.now().isoformat())
        )


@dataclass
class AlertRule:
    """告警规则"""
    id: str
    name: str
    competitor_id: str  # 空表示所有竞品
    rule_type: str  # viewer_spike, script_plagiarism, new_product, activity
    threshold: float
    comparison: str  # gt, lt, eq, contains
    enabled: bool = True
    created_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


@dataclass
class Alert:
    """告警记录"""
    id: str
    rule_id: str
    rule_name: str
    competitor_id: str
    competitor_name: str
    alert_type: str
    message: str
    current_value: Any
    threshold: float
    triggered_at: str
    notified: bool = False
    notification_channels: List[str] = None
    
    def __post_init__(self):
        if self.notification_channels is None:
            self.notification_channels = []
        if not self.triggered_at:
            self.triggered_at = datetime.now().isoformat()


@dataclass
class ScriptSegment:
    """直播话术片段"""
    competitor_id: str
    content: str
    timestamp: str
    similarity_score: float = 0.0  # 与己方话术的相似度


class CompetitorMonitorService:
    """竞品监控服务"""
    
    def __init__(self, data_dir: str = None):
        self.data_dir = Path(data_dir) if data_dir else Path(__file__).parent.parent / "data"
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 数据存储
        self.competitors: Dict[str, CompetitorInfo] = {}
        self.live_data_history: Dict[str, List[LiveRoomData]] = {}  # competitor_id -> history
        self.alert_rules: Dict[str, AlertRule] = {}
        self.alerts: List[Alert] = []
        self.script_segments: Dict[str, List[ScriptSegment]] = {}  # competitor_id -> segments
        
        # 己方话术库（用于相似度对比）
        self.own_scripts: List[str] = []
        
        # 监控状态
        self.is_monitoring = False
        self.monitoring_interval = 60  # 秒
        
        # 通知配置
        self.notification_config = {
            "email": {
                "enabled": False,
                "smtp_server": "",
                "smtp_port": 587,
                "username": "",
                "password": "",
                "recipients": []
            },
            "wechat": {
                "enabled": False,
                "corp_id": "",
                "agent_id": "",
                "secret": "",
                "user_ids": []
            }
        }
        
        # 加载持久化数据
        self._load_data()
    
    def _load_data(self):
        """加载持久化数据"""
        try:
            # 加载竞品信息
            competitors_file = self.data_dir / "competitors.json"
            if competitors_file.exists():
                with open(competitors_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.competitors = {k: CompetitorInfo(**v) for k, v in data.items()}
            
            # 加载告警规则
            rules_file = self.data_dir / "alert_rules.json"
            if rules_file.exists():
                with open(rules_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.alert_rules = {k: AlertRule(**v) for k, v in data.items()}
            
            # 加载历史告警
            alerts_file = self.data_dir / "alerts.json"
            if alerts_file.exists():
                with open(alerts_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.alerts = [Alert(**v) for v in data]
            
            # 加载通知配置
            config_file = self.data_dir / "notification_config.json"
            if config_file.exists():
                with open(config_file, "r", encoding="utf-8") as f:
                    self.notification_config.update(json.load(f))
            
            logger.info(f"加载数据完成：{len(self.competitors)} 个竞品，{len(self.alert_rules)} 条规则")
        except Exception as e:
            logger.error(f"加载数据失败：{e}")
    
    def _save_data(self):
        """保存持久化数据"""
        try:
            # 保存竞品信息
            with open(self.data_dir / "competitors.json", "w", encoding="utf-8") as f:
                json.dump({k: asdict(v) for k, v in self.competitors.items()}, f, ensure_ascii=False, indent=2)
            
            # 保存告警规则
            with open(self.data_dir / "alert_rules.json", "w", encoding="utf-8") as f:
                json.dump({k: asdict(v) for k, v in self.alert_rules.items()}, f, ensure_ascii=False, indent=2)
            
            # 保存历史告警（只保留最近 1000 条）
            with open(self.data_dir / "alerts.json", "w", encoding="utf-8") as f:
                json.dump([asdict(v) for v in self.alerts[-1000:]], f, ensure_ascii=False, indent=2)
            
            # 保存通知配置
            with open(self.data_dir / "notification_config.json", "w", encoding="utf-8") as f:
                json.dump(self.notification_config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存数据失败：{e}")
    
    # ==================== 竞品管理 ====================
    
    def add_competitor(self, name: str, platform: str, room_id: str) -> CompetitorInfo:
        """添加竞品"""
        competitor_id = hashlib.md5(f"{platform}_{room_id}".encode()).hexdigest()[:12]
        
        competitor = CompetitorInfo(
            id=competitor_id,
            name=name,
            platform=platform,
            room_id=room_id
        )
        
        self.competitors[competitor_id] = competitor
        self.live_data_history[competitor_id] = []
        self.script_segments[competitor_id] = []
        self._save_data()
        
        logger.info(f"添加竞品：{name} ({platform})")
        return competitor
    
    def remove_competitor(self, competitor_id: str) -> bool:
        """移除竞品"""
        if competitor_id in self.competitors:
            del self.competitors[competitor_id]
            if competitor_id in self.live_data_history:
                del self.live_data_history[competitor_id]
            if competitor_id in self.script_segments:
                del self.script_segments[competitor_id]
            self._save_data()
            return True
        return False
    
    def list_competitors(self) -> List[CompetitorInfo]:
        """获取竞品列表"""
        return list(self.competitors.values())
    
    def get_competitor(self, competitor_id: str) -> Optional[CompetitorInfo]:
        """获取竞品信息"""
        return self.competitors.get(competitor_id)
    
    # ==================== 实时监控 ====================
    
    async def start_monitoring(self):
        """启动监控"""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        logger.info("启动竞品监控...")
        
        while self.is_monitoring:
            try:
                await self._monitor_all_competitors()
                await asyncio.sleep(self.monitoring_interval)
            except Exception as e:
                logger.error(f"监控异常：{e}")
                await asyncio.sleep(10)
    
    async def stop_monitoring(self):
        """停止监控"""
        self.is_monitoring = False
        logger.info("停止竞品监控")
    
    async def _monitor_all_competitors(self):
        """监控所有竞品"""
        tasks = []
        for competitor in self.competitors.values():
            if competitor.status == "active":
                tasks.append(self._fetch_live_data(competitor))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _fetch_live_data(self, competitor: CompetitorInfo):
        """获取直播间数据（模拟）"""
        try:
            # 这里应该调用实际的平台 API
            # 现在用模拟数据
            capture_time = datetime.now().isoformat()
            live_data = LiveRoomData(
                competitor_id=competitor.id,
                viewer_count=self._simulate_viewer_count(),
                like_count=self._simulate_count(10000),
                comment_count=self._simulate_count(5000),
                share_count=self._simulate_count(1000),
                product_count=self._simulate_count(50),
                gmv=self._simulate_gmv(),
                avg_watch_time=self._simulate_watch_time(),
                capture_time=capture_time
            )
            
            # 保存历史数据
            if competitor.id not in self.live_data_history:
                self.live_data_history[competitor.id] = []
            self.live_data_history[competitor.id].append(live_data)
            
            # 只保留最近 1000 条记录
            if len(self.live_data_history[competitor.id]) > 1000:
                self.live_data_history[competitor.id] = self.live_data_history[competitor.id][-1000:]
            
            # 检查告警规则
            await self._check_alert_rules(competitor, live_data)
            
            # 捕获直播话术
            await self._capture_script(competitor)
            
        except Exception as e:
            logger.error(f"获取 {competitor.name} 数据失败：{e}")
    
    def _simulate_viewer_count(self) -> int:
        """模拟观众数"""
        import random
        base = random.randint(1000, 50000)
        # 偶尔产生流量突增
        if random.random() < 0.05:
            base *= random.randint(2, 5)
        return base
    
    def _simulate_count(self, max_val: int) -> int:
        """模拟计数"""
        import random
        return random.randint(max_val // 10, max_val)
    
    def _simulate_gmv(self) -> float:
        """模拟成交额"""
        import random
        return round(random.uniform(10000, 500000), 2)
    
    def _simulate_watch_time(self) -> float:
        """模拟平均观看时长"""
        import random
        return round(random.uniform(30, 300), 1)
    
    # ==================== 话术监控 ====================
    
    async def _capture_script(self, competitor: CompetitorInfo):
        """捕获直播话术（模拟）"""
        # 实际应该使用语音识别或字幕抓取
        import random
        
        script_templates = [
            "宝宝们这个价格真的太低了，只有今天才有这个优惠！",
            "库存不多了，想要的赶紧下单！",
            "这个产品我们卖了 10 万件，好评率 99%！",
            "新进来的宝宝点个关注，加入粉丝团！",
            "今天直播间专属价，比平时便宜 50 块！",
        ]
        
        content = random.choice(script_templates)
        segment = ScriptSegment(
            competitor_id=competitor.id,
            content=content,
            timestamp=datetime.now().isoformat(),
            similarity_score=self._calculate_similarity(content)
        )
        
        if competitor.id not in self.script_segments:
            self.script_segments[competitor.id] = []
        self.script_segments[competitor.id].append(segment)
        
        # 只保留最近 100 条
        if len(self.script_segments[competitor.id]) > 100:
            self.script_segments[competitor.id] = self.script_segments[competitor.id][-100:]
        
        # 检查话术抄袭告警
        if segment.similarity_score > 0.8:
            await self._trigger_alert(
                rule_id="script_plagiarism",
                rule_name="话术相似度告警",
                competitor=competitor,
                alert_type="script_plagiarism",
                message=f"检测到高相似度话术：{content[:30]}...",
                current_value=segment.similarity_score,
                threshold=0.8
            )
    
    def _calculate_similarity(self, text: str) -> float:
        """计算与己方话术的相似度"""
        if not self.own_scripts:
            return 0.0
        
        max_similarity = 0.0
        for own_script in self.own_scripts:
            similarity = self._text_similarity(text, own_script)
            max_similarity = max(max_similarity, similarity)
        
        return max_similarity
    
    def _text_similarity(self, text1: str, text2: str) -> float:
        """简单的文本相似度计算"""
        # 使用 Jaccard 相似度
        set1 = set(text1)
        set2 = set(text2)
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        return intersection / union if union > 0 else 0.0
    
    def add_own_script(self, script: str):
        """添加己方话术"""
        self.own_scripts.append(script)
    
    # ==================== 告警规则管理 ====================
    
    def add_alert_rule(self, name: str, rule_type: str, threshold: float, 
                       comparison: str = "gt", competitor_id: str = "") -> AlertRule:
        """添加告警规则"""
        rule_id = hashlib.md5(f"{name}_{time.time()}".encode()).hexdigest()[:12]
        
        rule = AlertRule(
            id=rule_id,
            name=name,
            competitor_id=competitor_id,
            rule_type=rule_type,
            threshold=threshold,
            comparison=comparison
        )
        
        self.alert_rules[rule_id] = rule
        self._save_data()
        
        logger.info(f"添加告警规则：{name}")
        return rule
    
    def remove_alert_rule(self, rule_id: str) -> bool:
        """移除告警规则"""
        if rule_id in self.alert_rules:
            del self.alert_rules[rule_id]
            self._save_data()
            return True
        return False
    
    def update_alert_rule(self, rule_id: str, **kwargs) -> Optional[AlertRule]:
        """更新告警规则"""
        if rule_id not in self.alert_rules:
            return None
        
        rule = self.alert_rules[rule_id]
        for key, value in kwargs.items():
            if hasattr(rule, key):
                setattr(rule, key, value)
        
        self._save_data()
        return rule
    
    def list_alert_rules(self, competitor_id: str = None) -> List[AlertRule]:
        """获取告警规则列表"""
        if competitor_id:
            return [r for r in self.alert_rules.values() if r.competitor_id == competitor_id]
        return list(self.alert_rules.values())
    
    # ==================== 告警触发 ====================
    
    async def _check_alert_rules(self, competitor: CompetitorInfo, live_data: LiveRoomData):
        """检查告警规则"""
        for rule in self.alert_rules.values():
            if not rule.enabled:
                continue
            
            # 检查是否针对特定竞品
            if rule.competitor_id and rule.competitor_id != competitor.id:
                continue
            
            triggered = False
            current_value = None
            message = ""
            
            if rule.rule_type == "viewer_spike":
                # 流量突增检测
                history = self.live_data_history.get(competitor.id, [])
                if len(history) >= 2:
                    avg_viewers = sum(d.viewer_count for d in history[-10:-1]) / len(history[-10:-1])
                    current_value = live_data.viewer_count
                    
                    if rule.comparison == "gt" and current_value > avg_viewers * rule.threshold:
                        triggered = True
                        message = f"观众数突增：{current_value} (平均：{avg_viewers:.0f})"
            
            elif rule.rule_type == "script_plagiarism":
                # 话术抄袭已在 _capture_script 中处理
                continue
            
            elif rule.rule_type == "gmv_threshold":
                current_value = live_data.gmv
                if rule.comparison == "gt" and current_value > rule.threshold:
                    triggered = True
                    message = f"成交额超过阈值：¥{current_value:,.2f}"
                elif rule.comparison == "lt" and current_value < rule.threshold:
                    triggered = True
                    message = f"成交额低于阈值：¥{current_value:,.2f}"
            
            if triggered:
                await self._trigger_alert(
                    rule_id=rule.id,
                    rule_name=rule.name,
                    competitor=competitor,
                    alert_type=rule.rule_type,
                    message=message,
                    current_value=current_value,
                    threshold=rule.threshold
                )
    
    async def _trigger_alert(self, rule_id: str, rule_name: str, competitor: CompetitorInfo,
                            alert_type: str, message: str, current_value: Any, threshold: float):
        """触发告警"""
        alert = Alert(
            id=hashlib.md5(f"{rule_id}_{time.time()}".encode()).hexdigest()[:12],
            rule_id=rule_id,
            rule_name=rule_name,
            competitor_id=competitor.id,
            competitor_name=competitor.name,
            alert_type=alert_type,
            message=message,
            current_value=current_value,
            threshold=threshold,
            triggered_at=datetime.now().isoformat()
        )
        
        self.alerts.append(alert)
        self._save_data()
        
        logger.warning(f"告警触发：{alert_type} - {competitor.name} - {message}")
        
        # 发送通知
        await self._send_notifications(alert)
    
    # ==================== 通知发送 ====================
    
    def update_notification_config(self, channel: str, config: Dict):
        """更新通知配置"""
        if channel in self.notification_config:
            self.notification_config[channel].update(config)
            self._save_data()
    
    async def _send_notifications(self, alert: Alert):
        """发送告警通知"""
        tasks = []
        
        if self.notification_config["email"]["enabled"]:
            tasks.append(self._send_email_notification(alert))
        
        if self.notification_config["wechat"]["enabled"]:
            tasks.append(self._send_wechat_notification(alert))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
        
        alert.notified = True
    
    async def _send_email_notification(self, alert: Alert):
        """发送邮件通知"""
        # 实际实现需要 SMTP 配置
        config = self.notification_config["email"]
        logger.info(f"[邮件通知] {alert.competitor_name}: {alert.message}")
        # TODO: 实现实际邮件发送
    
    async def _send_wechat_notification(self, alert: Alert):
        """发送微信通知"""
        # 实际实现需要企业微信 API
        config = self.notification_config["wechat"]
        logger.info(f"[微信通知] {alert.competitor_name}: {alert.message}")
        # TODO: 实现实际微信通知
    
    # ==================== 历史查询 ====================
    
    def get_live_data_history(self, competitor_id: str, 
                             start_time: str = None, 
                             end_time: str = None,
                             limit: int = 100) -> List[LiveRoomData]:
        """获取历史数据"""
        history = self.live_data_history.get(competitor_id, [])
        
        if start_time:
            history = [d for d in history if d.capture_time >= start_time]
        if end_time:
            history = [d for d in history if d.capture_time <= end_time]
        
        return history[-limit:]
    
    def get_alerts(self, competitor_id: str = None, 
                   alert_type: str = None,
                   start_time: str = None,
                   end_time: str = None,
                   limit: int = 100) -> List[Alert]:
        """获取告警记录"""
        alerts = self.alerts
        
        if competitor_id:
            alerts = [a for a in alerts if a.competitor_id == competitor_id]
        if alert_type:
            alerts = [a for a in alerts if a.alert_type == alert_type]
        if start_time:
            alerts = [a for a in alerts if a.triggered_at >= start_time]
        if end_time:
            alerts = [a for a in alerts if a.triggered_at <= end_time]
        
        return alerts[-limit:]
    
    def get_script_segments(self, competitor_id: str, limit: int = 50) -> List[ScriptSegment]:
        """获取话术片段"""
        segments = self.script_segments.get(competitor_id, [])
        return segments[-limit:]
    
    # ==================== 动态追踪 ====================
    
    def track_new_product(self, competitor_id: str, product_info: Dict):
        """追踪新品"""
        logger.info(f"竞品 {competitor_id} 上新：{product_info.get('name', 'Unknown')}")
        # TODO: 实现新品追踪逻辑
    
    def track_activity(self, competitor_id: str, activity_info: Dict):
        """追踪活动"""
        logger.info(f"竞品 {competitor_id} 活动：{activity_info.get('title', 'Unknown')}")
        # TODO: 实现活动追踪逻辑


# 单例实例
_monitor_service: Optional[CompetitorMonitorService] = None


def get_monitor_service() -> CompetitorMonitorService:
    """获取监控服务实例"""
    global _monitor_service
    if _monitor_service is None:
        _monitor_service = CompetitorMonitorService()
    return _monitor_service


if __name__ == "__main__":
    # 测试
    async def test():
        service = get_monitor_service()
        
        # 添加竞品
        service.add_competitor("竞品 A", "douyin", "room_123")
        service.add_competitor("竞品 B", "taobao", "room_456")
        
        # 添加告警规则
        service.add_alert_rule("流量突增告警", "viewer_spike", 2.0, "gt")
        service.add_alert_rule("成交额告警", "gmv_threshold", 100000, "gt")
        
        # 添加己方话术
        service.add_own_script("宝宝们这个价格真的太低了，只有今天才有这个优惠！")
        
        # 启动监控（测试用，只运行 10 秒）
        service.monitoring_interval = 5
        try:
            await asyncio.wait_for(service.start_monitoring(), timeout=10)
        except asyncio.TimeoutError:
            pass
        
        await service.stop_monitoring()
        
        # 查看结果
        print(f"\n竞品列表：{len(service.list_competitors())}")
        print(f"告警记录：{len(service.alerts)}")
        for alert in service.alerts[-5:]:
            print(f"  - {alert.competitor_name}: {alert.message}")
    
    asyncio.run(test())
