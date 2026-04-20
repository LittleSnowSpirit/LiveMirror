# 竞品监控告警系统 - 开发文档

## 📋 功能概述

竞品监控告警系统为 LiveMirror 平台提供竞品直播间实时监控、异常数据告警、竞品动态追踪等功能。

### 核心功能

1. **竞品直播间实时监控** - 追踪竞品直播间的观众数、点赞、评论等实时数据
2. **异常数据告警** - 流量突增、话术抄袭等异常情况智能告警
3. **竞品动态追踪** - 新品上架、促销活动自动追踪
4. **告警通知** - 支持微信、邮件等多种通知渠道
5. **监控历史查询** - 完整的告警历史和数据分析
6. **告警规则配置** - 灵活的告警规则自定义

## 📁 文件结构

```
backend/
├── services/
│   └── competitor_monitor.py    # 竞品监控服务
├── routes/
│   └── monitor.py               # 监控 API 路由
└── tests/
    ├── test_competitor_monitor.py   # 服务层测试
    └── test_monitor_routes.py       # API 路由测试

frontend/
├── src/views/
│   └── CompetitorMonitor.vue    # 监控页面
└── src/components/
    └── CompetitorAlert.vue      # 告警组件
```

## 🔧 技术架构

### 后端服务

**CompetitorMonitorService** 提供以下核心能力：

- **竞品管理**: 添加、删除、更新竞品直播间
- **实时监控**: 接收并存储直播实时数据
- **告警检测**: 基于规则的异常检测引擎
- **通知发送**: 微信 Webhook、邮件通知
- **商品追踪**: 竞品商品上下架监控
- **配置管理**: 系统配置和通知配置

### 数据模型

```python
# 竞品信息
CompetitorInfo:
    - id: str
    - name: str
    - platform: str (douyin/taobao/kuaishou)
    - room_id: str
    - status: MonitorStatus (active/paused/offline)

# 直播数据
LiveStreamData:
    - viewer_count: int
    - like_count: int
    - comment_count: int
    - transcript: str (话术转写)

# 告警规则
AlertRule:
    - alert_type: AlertType
    - threshold: float
    - cooldown_minutes: int
    - notification_channels: List[str]

# 告警事件
AlertEvent:
    - level: AlertLevel (info/warning/critical)
    - message: str
    - data: Dict
```

## 🚀 API 接口

### 竞品管理

```bash
# 添加竞品
POST /api/monitor/competitors
{
    "name": "XX 官方旗舰店",
    "platform": "douyin",
    "room_id": "room_123",
    "stream_url": "https://..."
}

# 查询列表
GET /api/monitor/competitors?platform=douyin&status=active&keyword=XX

# 更新信息
PUT /api/monitor/competitors/{id}
{
    "name": "新名称",
    "status": "active"
}

# 删除竞品
DELETE /api/monitor/competitors/{id}
```

### 实时监控

```bash
# 更新直播数据
POST /api/monitor/competitors/{id}/stream-data
{
    "viewer_count": 1000,
    "like_count": 5000,
    "comment_count": 200,
    "transcript": "欢迎来到直播间..."
}

# 获取实时数据
GET /api/monitor/competitors/{id}/stream-data

# 获取历史数据
GET /api/monitor/competitors/{id}/stream-history?minutes=60

# 控制监控
POST /api/monitor/competitors/{id}/start
POST /api/monitor/competitors/{id}/pause
POST /api/monitor/competitors/{id}/stop
```

### 告警规则

```bash
# 创建规则
POST /api/monitor/rules
{
    "name": "流量突增告警",
    "alert_type": "traffic_spike",
    "threshold": 2.0,
    "cooldown_minutes": 10,
    "notification_channels": ["wechat", "email"]
}

# 查询规则
GET /api/monitor/rules?alert_type=traffic_spike&enabled_only=true

# 更新规则
PUT /api/monitor/rules/{id}
{
    "enabled": false,
    "threshold": 3.0
}

# 删除规则
DELETE /api/monitor/rules/{id}
```

### 告警历史

```bash
# 查询告警
GET /api/monitor/alerts?competitor_id=xxx&alert_type=traffic_spike&days=7&page=1&page_size=50

# 标记已处理
POST /api/monitor/alerts/{alert_id}/notify
```

### 商品追踪

```bash
# 添加商品
POST /api/monitor/competitors/{id}/products
{
    "id": "prod_001",
    "name": "商品名称",
    "price": 99.9,
    "original_price": 199.9,
    "discount": "5 折",
    "sales_count": 1000
}

# 查询商品
GET /api/monitor/competitors/{id}/products?days=7

# 查询新品
GET /api/monitor/competitors/{id}/products/new?days=7
```

### 配置管理

```bash
# 获取配置
GET /api/monitor/config

# 更新配置
PUT /api/monitor/config
{
    "monitor_interval_seconds": 30,
    "data_retention_days": 30
}

# 更新通知配置
PUT /api/monitor/config/notification
{
    "channel": "wechat",
    "enabled": true,
    "webhook_url": "https://qyapi.weixin.qq.com/..."
}
```

### 统计信息

```bash
# 获取统计
GET /api/monitor/statistics?days=7

# 获取仪表盘
GET /api/monitor/dashboard
```

## ⚙️ 告警规则类型

### 1. 流量突增 (traffic_spike)

检测直播间观众数突然增长。

```json
{
    "alert_type": "traffic_spike",
    "threshold": 2.0,
    "conditions": {
        "window_minutes": 5
    }
}
```

**触发条件**: 当前观众数 / 窗口期平均观众数 >= threshold

### 2. 话术抄袭 (script_plagiarism)

检测竞品话术与自家直播间相似度。

```json
{
    "alert_type": "script_plagiarism",
    "threshold": 0.8,
    "conditions": {
        "min_match_length": 50
    }
}
```

**触发条件**: 话术相似度 >= threshold

### 3. 新品发布 (new_product)

追踪竞品新品上架。

```json
{
    "alert_type": "new_product",
    "enabled": true
}
```

**触发条件**: 检测到新商品 ID

### 4. 促销活动 (promotion_activity)

检测直播间促销活动关键词。

```json
{
    "alert_type": "promotion_activity",
    "conditions": {
        "keywords": ["打折", "促销", "秒杀", "特价"]
    }
}
```

**触发条件**: 话术中包含关键词

## 🔔 通知渠道

### 微信通知

使用企业微信 Webhook：

```json
{
    "notification": {
        "wechat": {
            "enabled": true,
            "webhook_url": "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=xxx"
        }
    }
}
```

### 邮件通知

```json
{
    "notification": {
        "email": {
            "enabled": true,
            "recipients": ["user@example.com"]
        }
    }
}
```

## 🧪 测试

### 运行服务测试

```bash
cd C:\Users\LittleXiao\.openclaw\workspace
python -m pytest backend/tests/test_competitor_monitor.py -v
```

### 运行 API 测试

```bash
python -m pytest backend/tests/test_monitor_routes.py -v
```

### 测试结果

✅ **26 个服务测试全部通过**
✅ **20 个 API 测试全部通过**

测试覆盖：
- 竞品管理（添加、删除、更新、查询）
- 直播数据更新和历史查询
- 告警规则管理
- 告警检测（流量突增、促销活动）
- 告警冷却机制
- 商品追踪
- 告警历史查询
- 配置管理
- 监控控制（启动、暂停、停止）

## 📊 前端组件

### CompetitorMonitor.vue

监控主页面，提供：
- 统计仪表盘
- 竞品列表（支持筛选和搜索）
- 实时数据展示
- 告警规则配置弹窗
- 告警历史查询
- 系统配置

### CompetitorAlert.vue

告警浮窗组件，提供：
- 实时告警通知
- 告警级别显示（info/warning/critical）
- 自动消失
- 声音提示（可选）
- 点击处理

## 🔧 使用示例

### 1. 添加竞品

```python
from backend.services.competitor_monitor import get_service

service = get_service()

competitor = service.add_competitor(
    name="竞品 A 直播间",
    platform="douyin",
    room_id="room_12345"
)
```

### 2. 创建告警规则

```python
from backend.services.competitor_monitor import AlertType

rule = service.add_rule(
    name="流量突增告警",
    alert_type=AlertType.TRAFFIC_SPIKE,
    threshold=2.0,  # 增长 2 倍触发
    cooldown_minutes=10,
    notification_channels=["wechat"]
)
```

### 3. 更新直播数据

```python
from backend.services.competitor_monitor import LiveStreamData

data = LiveStreamData(
    competitor_id=competitor.id,
    viewer_count=1500,
    like_count=8000,
    comment_count=300,
    transcript="今天我们直播间有大促销..."
)

service.update_stream_data(competitor.id, data)
# 自动触发告警检测
```

### 4. 查询告警历史

```python
alerts, total = service.get_alert_history(
    competitor_id=competitor.id,
    days=7,
    page=1,
    page_size=50
)
```

## 📝 注意事项

1. **数据持久化**: 所有数据保存在 `data/competitor_monitor/` 目录
2. **告警冷却**: 避免短时间内重复告警，默认冷却 5 分钟
3. **数据保留**: 默认保留 30 天历史数据
4. **监控间隔**: 建议设置 30-60 秒监控间隔
5. **通知配置**: 微信通知需要配置企业微信 Webhook

## 🚧 待扩展功能

1. **话术抄袭检测**: 需要接入话术库和相似度算法
2. **实时数据采集**: 需要对接各平台 API 或爬虫
3. **数据分析**: 竞品数据趋势分析、对比报告
4. **更多通知渠道**: 钉钉、飞书等
5. **智能告警**: 基于机器学习的异常检测

## 📞 技术支持

如有问题，请查看：
- 服务日志：`logs/competitor_monitor.log`
- 数据目录：`data/competitor_monitor/`
- 测试用例：`backend/tests/test_competitor_monitor.py`
