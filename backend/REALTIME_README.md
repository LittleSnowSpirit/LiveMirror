# LiveMirror 实时副播功能

实时分析直播音频流，提供话术建议、情绪分析、风险提示等功能。

## 功能特性

### 核心功能

1. **WebSocket 实时音频流处理**
   - 支持 16kHz 采样率音频流传输
   - 可配置缓冲区时长（默认 3 秒）
   - 自动断线重连机制

2. **流式语音转写**
   - 基于 Faster Whisper 引擎
   - 边说边转，低延迟
   - 支持中英文识别

3. **实时话术分析**
   - 延迟 < 3 秒
   - 情绪分析（正面/中性/负面）
   - 关键词提取
   - 话术优化建议
   - 违规风险检测

4. **实时数据看板**
   - 情绪分布可视化
   - 实时转写文本
   - 话术建议推送
   - 性能监控（延迟统计）

## 文件结构

```
backend/
├── services/
│   ├── realtime_analysis.py    # 实时分析服务
│   └── whisper.py              # Whisper 转写服务
├── routes/
│   └── websocket_stream.py     # WebSocket 流处理路由
└── REALTIME_README.md          # 本文档

livemirror-frontend/
├── src/
│   ├── components/
│   │   └── RealtimeDashboard.vue    # 实时看板组件
│   └── utils/
│       └── websocket_client.js      # WebSocket 客户端
└── public/
    └── test-realtime.html           # 测试页面

tests/
└── test_realtime_stream.py          # 自动化测试脚本
```

## 快速开始

### 1. 安装依赖

```bash
# 后端依赖
cd backend
pip install fastapi uvicorn websockets aiohttp

# 前端依赖
cd livemirror-frontend
npm install
```

### 2. 启动后端服务

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**注意**: 确保 `backend/main.py` 中已注册 WebSocket 路由：

```python
from routes import websocket_stream

app.include_router(websocket_stream.router, prefix="/api")
# 或者直接：
# app.include_router(websocket_stream.router)
```

### 3. 测试功能

#### 方式 1: 自动化测试

```bash
cd tests
python test_realtime_stream.py
```

测试项目：
- ✅ WebSocket 连接测试
- ✅ 流式转写测试
- ✅ 实时分析延迟测试
- ✅ 话术建议推送测试
- ✅ 断线重连测试

#### 方式 2: 浏览器测试页面

访问：`http://localhost:5173/test-realtime.html`

功能：
- 一键连接 WebSocket
- 麦克风录音测试
- 文本输入测试
- 实时日志显示

#### 方式 3: 集成到 Vue 应用

在 Vue 组件中使用：

```vue
<template>
  <RealtimeDashboard 
    session-id="my_session_001"
    ws-url="ws://localhost:8000/ws/stream/text"
    :show-text-test="true"
  />
</template>

<script>
import RealtimeDashboard from './components/RealtimeDashboard.vue'

export default {
  components: { RealtimeDashboard }
}
</script>
```

## API 文档

### WebSocket 端点

#### 1. 音频流端点

```
WS /ws/stream/{session_id}?sample_rate=16000&buffer_duration=3000
```

**客户端 -> 服务端消息格式:**

```json
{
  "type": "audio",
  "data": "<base64 编码的 PCM 数据>",
  "duration_ms": 3000
}
```

**服务端 -> 客户端消息格式:**

```json
{
  "type": "transcription_result",
  "session_id": "xxx",
  "segment_index": 1,
  "text": "转写文本",
  "analysis": {
    "sentiment": "positive",
    "sentiment_score": 0.8,
    "keywords": ["产品", "优惠"],
    "suggestions": ["强调价格优势"],
    "risks": [],
    "emotions": {
      "joy": 0.6,
      "neutral": 0.4
    }
  },
  "performance": {
    "transcribe_time_ms": 150.5,
    "analyze_time_ms": 50.2,
    "total_latency_ms": 200.7
  },
  "timestamp": 1712567890.123
}
```

#### 2. 文本流端点（测试用）

```
WS /ws/stream/text/{session_id}
```

**客户端 -> 服务端:**

```json
{
  "type": "text",
  "content": "要分析的文本"
}
```

**控制消息:**

```json
// 心跳
{"type": "ping"}

// 获取统计
{"type": "get_stats"}

// 停止流处理
{"type": "stop"}
```

### REST API

#### 获取流统计

```
GET /stream/stats
```

**响应:**

```json
{
  "active_connections": 2,
  "sessions": [
    {
      "session_id": "xxx",
      "connected": true,
      "duration_seconds": 120.5,
      "message_count": 45
    }
  ]
}
```

#### 获取会话信息

```
GET /stream/session/{session_id}
```

## 性能指标

### 延迟要求

- **目标**: < 3000ms（从说话到显示建议）
- **组成**:
  - 音频采集：3000ms（缓冲区）
  - 语音转写：~500ms（tiny 模型）
  - 实时分析：~50ms
  - 网络传输：~50ms

### 优化建议

1. **模型选择**
   - 开发测试：`tiny` (最快)
   - 生产环境：`base` 或 `small`（更准确）

2. **缓冲区设置**
   - 低延迟场景：1000-2000ms
   - 平衡场景：3000ms（默认）
   - 高准确度：5000ms

3. **采样率**
   - 语音识别：16000Hz（推荐）
   - 高质量音频：44100Hz（更大带宽）

## 话术规则

### 建议规则

| 触发词 | 建议内容 |
|--------|----------|
| 这个/那个 | 使用具体产品名称 |
| 可能/也许 | 使用更肯定的表达 |
| 99 块/元 | 强调价格优势 |
| 买/下单 | 添加行动号召 |

### 风险检测

| 风险类型 | 检测模式 |
|----------|----------|
| 绝对化用语 | 最 X、第一、100% |
| 医疗功效 | 治疗、治愈、疗效 |
| 收益承诺 | 赚钱、暴利 |

## 故障排查

### 连接失败

```bash
# 检查后端服务
curl http://localhost:8000/stream/stats

# 检查 WebSocket
wscat -c ws://localhost:8000/ws/stream/text/test
```

### 延迟过高

1. 检查网络延迟
2. 降低缓冲区时长
3. 使用更小的 Whisper 模型
4. 检查 CPU 使用率

### 转写不准确

1. 检查音频质量（采样率、格式）
2. 调整 VAD 设置
3. 使用更大的 Whisper 模型
4. 检查语言设置

## 开发计划

- [ ] 支持多语言实时切换
- [ ] 自定义话术规则配置
- [ ] 直播观众情绪聚合分析
- [ ] 历史数据回放功能
- [ ] A/B 测试不同话术效果

## 注意事项

⚠️ **音频格式**: 目前支持 16-bit PCM 单声道音频

⚠️ **浏览器兼容性**: 录音功能需要浏览器支持 `getUserMedia` API

⚠️ **生产环境**: 建议配置 WebSocket 超时和连接数限制

---

**版本**: 1.0.0  
**作者**: LiveMirror Team  
**更新时间**: 2026-04-08
