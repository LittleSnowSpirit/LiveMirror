# LiveMirror 智能场控助手

实时辅助直播运营的智能场控系统，提供弹幕监控、自动回复、违规处理、情绪分析和直播节奏建议。

## 功能特性

### 1. 实时弹幕监控和预警
- 实时接收和处理弹幕消息
- 弹幕频率统计和高峰检测
- 用户行为追踪

### 2. 自动回复常见问题
- 内置常见问题库（FAQ）
- 支持正则表达式匹配
- 自动识别并回复观众问题
- 管理员和高等级用户免打扰

**常见问题示例：**
- "直播什么时候结束" → "直播预计持续到晚上 10 点哦～"
- "有优惠吗" → "当前直播间有专属优惠券，点击直播间下方链接领取！"
- "怎么购买" → "点击直播间下方购物车图标就可以购买啦～"

### 3. 违规言论自动处理
- **辱骂言论**：自动禁言
- **广告信息**：警告处理
- **敏感内容**：自动禁言
- **刷屏行为**：警告处理（60 秒内超过 10 条）

**违规类型：**
- `spam`: 刷屏
- `abuse`: 辱骂
- `advertisement`: 广告
- `sensitive`: 敏感内容

### 4. 观众情绪实时监控
- 积极情绪检测
- 消极情绪预警
- 兴奋度分析
- 情绪趋势追踪（每 10 秒更新）

**情绪指标：**
- 积极（positive）
- 中性（neutral）
- 消极（negative）
- 兴奋（excited）

### 5. 直播节奏建议
根据观众情绪和直播时长，智能生成节奏建议：

- **互动建议**：情绪偏低时，建议抽奖或问答
- **促销建议**：情绪高涨时，推出限时优惠
- **休息建议**：直播 2 小时后，建议短暂休息

### 6. 场控操作日志
- 所有自动操作记录
- 手动操作记录
- 可查询和导出
- 保留最近 500 条记录

## 文件结构

```
backend/
├── services/
│   └── assistant_controller.py    # 场控助手核心服务
├── routes/
│   └── controller.py              # HTTP API 接口
└── tests/
    ├── test_controller_simple.py  # 功能测试
    └── generate_demo_data.py      # 演示数据生成
```

前端文件：
```
frontend/src/
├── views/
│   └── Controller.vue             # 场控页面
└── components/
    └── ControllerPanel.vue        # 场控面板组件
```

## API 接口

### 直播控制
- `POST /api/controller/live/start` - 开始直播监控
- `POST /api/controller/live/stop` - 停止直播监控
- `GET /api/controller/live/status` - 获取直播状态

### 弹幕处理
- `POST /api/controller/danmaku/receive` - 接收弹幕
- `POST /api/controller/danmaku/batch` - 批量接收弹幕

### 预警查询
- `GET /api/controller/alerts` - 获取预警记录
- `GET /api/controller/alerts/stats` - 获取预警统计

### 情绪监控
- `GET /api/controller/emotion/current` - 获取当前情绪
- `GET /api/controller/emotion/trend` - 获取情绪趋势

### 节奏建议
- `GET /api/controller/suggestions` - 获取建议列表
- `GET /api/controller/suggestions/current` - 获取当前建议

### 操作日志
- `GET /api/controller/logs` - 获取操作日志
- `GET /api/controller/logs/stats` - 获取统计

### 配置管理
- `GET /api/controller/config` - 获取配置
- `PUT /api/controller/config/auto-reply` - 更新自动回复配置
- `PUT /api/controller/config/violation` - 更新违规检测配置

### WebSocket
- `WS /api/controller/ws` - 实时数据推送

## 使用示例

### Python 代码示例

```python
from services.assistant_controller import get_controller, DanmakuMessage
from datetime import datetime

# 获取控制器实例
controller = get_controller()

# 开始直播
await controller.start_live("room_12345")

# 接收弹幕
msg = DanmakuMessage(
    user_id="user_001",
    username="小明",
    content="直播什么时候结束",
    timestamp=datetime.now().timestamp()
)

alerts = await controller.receive_danmaku(msg)

# 获取状态
status = controller.get_status()
print(f"弹幕数：{status['stats']['total_danmaku']}")
print(f"自动回复：{status['stats']['auto_replies']}")

# 停止直播
await controller.stop_live()
```

### 前端 Vue 示例

```vue
<template>
  <div>
    <button @click="startLive">开始监控</button>
    <div v-if="isLive">直播中...</div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      isLive: false
    }
  },
  methods: {
    async startLive() {
      const res = await fetch('/api/controller/live/start', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ stream_id: 'room_123' })
      })
      const data = await res.json()
      if (data.code === 0) {
        this.isLive = true
      }
    }
  }
}
</script>
```

## 测试结果

### 功能测试（9 项全部通过）
✅ 开始/停止直播
✅ 接收弹幕
✅ 自动回复
✅ 违规检测
✅ 刷屏检测
✅ 情绪分析
✅ 节奏建议
✅ 获取状态
✅ 操作日志

### 演示数据样本

```json
{
  "statistics": {
    "total_danmaku": 32,
    "auto_replies": 6,
    "violations_handled": 6,
    "alerts_triggered": 7
  },
  "emotion": {
    "positive": 0.22,
    "neutral": 0.75,
    "negative": 0.03,
    "excited": 0.03
  }
}
```

## 配置说明

### 自动回复配置
```python
controller.config["auto_reply_enabled"] = True
controller.faq_responses = {
    r"问题关键词": "回复内容",
    # 支持正则表达式
}
```

### 违规词库配置
```python
controller.violation_keywords = {
    ViolationType.SPAM: ["哈哈哈", "666"],
    ViolationType.ABUSE: ["脏话"],
    ViolationType.ADVERTISEMENT: ["加微信", "QQ"],
}
```

### 监控开关
```python
controller.config = {
    "auto_reply_enabled": True,
    "violation_detection_enabled": True,
    "emotion_monitoring_enabled": True,
    "rhythm_suggestion_enabled": True,
}
```

## 性能指标

- 弹幕处理延迟：< 10ms
- 情绪分析周期：10 秒
- 节奏建议周期：30 秒
- 日志保留数量：500 条
- 弹幕缓冲区：1000 条

## 注意事项

1. **内存管理**：弹幕缓冲区限制 1000 条，超出自动清理
2. **日志轮转**：操作日志保留最近 500 条
3. **并发处理**：支持高并发弹幕接收
4. **异常恢复**：异步任务异常自动重启

## 扩展开发

### 添加新的自动回复
编辑 `assistant_controller.py` 中的 `_load_faq_responses()` 方法

### 添加新的违规类型
1. 在 `ViolationType` 枚举中添加新类型
2. 在 `_load_violation_keywords()` 中添加关键词
3. 在 `_handle_violation()` 中添加处理逻辑

### 自定义情绪分析
重写 `_analyze_current_emotion()` 方法，使用更复杂的 NLP 模型

## 开发者

LiveMirror Team
2026-04-09
