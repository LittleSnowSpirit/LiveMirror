# LiveMirror 竞品监控系统

竞品直播间监控和告警功能模块。

## 功能特性

1. **竞品直播间实时监控**
   - 观众数、点赞数、评论数、分享数
   - 商品数量、成交额 (GMV)、平均观看时长
   - 数据自动采集和存储

2. **异常数据告警**
   - 流量突增告警（观众数异常增长）
   - 话术抄袭检测（与己方话术相似度）
   - 成交额阈值告警

3. **竞品动态追踪**
   - 新品上架监控
   - 活动信息追踪

4. **告警通知**
   - 邮件通知（SMTP）
   - 微信通知（企业微信）
   - 前端弹窗和悬浮窗

5. **监控历史查询**
   - 历史数据查询
   - 告警记录查询
   - 话术记录查询
   - 数据导出（CSV）

6. **告警规则配置**
   - 灵活的规则配置
   - 支持多种比较方式
   - 可针对特定竞品或全局规则

## 文件结构

```
backend/
├── services/
│   └── competitor_monitor.py    # 竞品监控服务
├── routes/
│   └── monitor.py               # API 接口
├── tests/
│   └── test_monitor.py          # 测试文件
├── data/                        # 数据存储目录（自动生成）
│   ├── competitors.json         # 竞品信息
│   ├── alert_rules.json         # 告警规则
│   ├── alerts.json              # 告警记录
│   └── notification_config.json # 通知配置
└── README.md                    # 说明文档
```

## 快速开始

### 1. 安装依赖

```bash
pip install fastapi uvicorn pytest pytest-asyncio
```

### 2. 运行测试

```bash
python backend/tests/test_monitor.py
```

### 3. 启动服务

```bash
# 开发模式
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# 生产模式
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 4. 访问 API

- API 文档：http://localhost:8000/docs
- 竞品列表：GET /api/monitor/competitors
- 启动监控：POST /api/monitor/start
- 告警记录：GET /api/monitor/alerts

## API 接口

### 竞品管理

- `GET /api/monitor/competitors` - 获取竞品列表
- `POST /api/monitor/competitors` - 添加竞品
- `DELETE /api/monitor/competitors/{id}` - 删除竞品
- `PUT /api/monitor/competitors/{id}/status` - 更新状态

### 监控控制

- `GET /api/monitor/status` - 获取监控状态
- `POST /api/monitor/start` - 启动监控
- `POST /api/monitor/stop` - 停止监控
- `GET /api/monitor/live-data/{id}` - 获取实时数据
- `GET /api/monitor/live-data/{id}/history` - 获取历史数据

### 告警规则

- `GET /api/monitor/alert-rules` - 获取规则列表
- `POST /api/monitor/alert-rules` - 添加规则
- `DELETE /api/monitor/alert-rules/{id}` - 删除规则
- `PUT /api/monitor/alert-rules/{id}` - 更新规则
- `POST /api/monitor/alert-rules/{id}/toggle` - 切换状态

### 告警记录

- `GET /api/monitor/alerts` - 获取告警列表
- `GET /api/monitor/alerts/{id}` - 获取告警详情

### 话术监控

- `GET /api/monitor/scripts/{competitor_id}` - 获取话术片段
- `POST /api/monitor/scripts/own` - 添加己方话术
- `GET /api/monitor/scripts/own` - 获取己方话术列表

### 通知配置

- `GET /api/monitor/notification-config` - 获取通知配置
- `PUT /api/monitor/notification-config/{channel}` - 更新配置
- `POST /api/monitor/notification/test/{channel}` - 测试通知

### 统计信息

- `GET /api/monitor/stats` - 获取统计信息

## 前端集成

### Vue 组件

```vue
<template>
  <div>
    <!-- 监控页面 -->
    <CompetitorMonitor />
    
    <!-- 告警组件 -->
    <CompetitorAlert ref="alertComponent" />
  </div>
</template>

<script setup>
import CompetitorMonitor from './views/CompetitorMonitor.vue'
import CompetitorAlert from './components/CompetitorAlert.vue'

// 打开告警设置
function openAlertSettings() {
  this.$refs.alertComponent.openSettings()
}

// 查看告警历史
function viewAlertHistory() {
  this.$refs.alertComponent.openHistory()
}
</script>
```

### 路由配置

```javascript
// router/index.js
{
  path: '/monitor',
  name: 'CompetitorMonitor',
  component: () => import('@/views/CompetitorMonitor.vue')
}
```

## 使用示例

### 添加竞品

```python
from backend.services.competitor_monitor import get_monitor_service

service = get_monitor_service()

# 添加抖音竞品
service.add_competitor("竞品 A", "douyin", "room_123456")

# 添加淘宝竞品
service.add_competitor("竞品 B", "taobao", "room_789012")
```

### 配置告警规则

```python
# 流量突增告警（观众数超过平均值 2 倍）
service.add_alert_rule(
    name="流量突增告警",
    rule_type="viewer_spike",
    threshold=2.0,
    comparison="gt"
)

# GMV 超额告警
service.add_alert_rule(
    name="GMV 突破 10 万",
    rule_type="gmv_threshold",
    threshold=100000,
    comparison="gt"
)

# 话术抄袭告警
service.add_alert_rule(
    name="话术相似度告警",
    rule_type="script_plagiarism",
    threshold=0.8,
    comparison="gt"
)
```

### 添加己方话术

```python
# 用于相似度对比
service.add_own_script("宝宝们这个价格真的太低了，只有今天才有这个优惠！")
service.add_own_script("库存不多了，想要的赶紧下单！")
```

### 配置邮件通知

```python
service.update_notification_config("email", {
    "enabled": True,
    "smtp_server": "smtp.qq.com",
    "smtp_port": 587,
    "username": "your_email@qq.com",
    "password": "your_auth_code",
    "recipients": ["ops@example.com", "manager@example.com"]
})
```

### 配置微信通知

```python
service.update_notification_config("wechat", {
    "enabled": True,
    "corp_id": "your_corp_id",
    "agent_id": "your_agent_id",
    "secret": "your_secret",
    "user_ids": ["ops", "manager", "admin"]
})
```

### 查询历史数据

```python
# 获取最近 100 条历史数据
history = service.get_live_data_history(
    competitor_id="competitor_id",
    limit=100
)

# 获取告警记录
alerts = service.get_alerts(
    competitor_id="competitor_id",
    alert_type="viewer_spike",
    start_time="2024-01-01T00:00:00",
    end_time="2024-01-31T23:59:59",
    limit=50
)
```

## 告警类型说明

| 类型 | 说明 | 阈值含义 |
|------|------|----------|
| viewer_spike | 流量突增 | 相对于平均值的倍数（如 2.0 表示 2 倍） |
| script_plagiarism | 话术抄袭 | 相似度分数（0-1，如 0.8 表示 80% 相似） |
| gmv_threshold | 成交额阈值 | 具体金额（如 100000 表示 10 万元） |

## 注意事项

1. **数据采集**：当前使用模拟数据，实际使用需要对接各平台 API
2. **话术识别**：需要集成语音识别或字幕抓取功能
3. **通知服务**：邮件和微信通知需要配置正确的凭证
4. **数据存储**：当前使用 JSON 文件，大数据量建议切换到数据库

## 后续优化

- [ ] 对接抖音/淘宝/快手官方 API
- [ ] 集成语音识别进行实时话术转录
- [ ] 使用数据库存储历史数据
- [ ] 添加数据可视化大屏
- [ ] 支持更多告警类型（如主播更换、背景变化等）
- [ ] 添加竞品对比分析功能
