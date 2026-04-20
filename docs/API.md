# LiveMirror API 接口文档

> 📌 **版本**: V0.1 MVP  
> **最后更新**: 2026-04-08

---

## 📡 基础信息

- **Base URL**: `http://localhost:8000`
- **API 文档**: `http://localhost:8000/docs` (Swagger UI)
- **数据格式**: JSON
- **认证方式**: MVP 阶段无需认证

---

## 🔌 接口列表

### 1. 健康检查

```http
GET /health
```

**响应**:
```json
{
  "status": "ok",
  "timestamp": "2026-04-08T13:00:00Z"
}
```

---

### 2. 音频上传

```http
POST /api/upload
Content-Type: multipart/form-data
```

**请求参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `file` | File | ✅ | 音频文件 (MP3/WAV/M4A)，最大 2GB |
| `speaker_name` | String | ❌ | 主播昵称（用于报告展示） |
| `platform` | String | ❌ | 直播平台 (抖音/快手/淘宝等) |

**响应**:
```json
{
  "task_id": "uuid-string",
  "status": "processing",
  "created_at": "2026-04-08T13:00:00Z",
  "message": "音频已接收，开始转写"
}
```

**错误响应**:
```json
{
  "error": "invalid_file_type",
  "message": "不支持的文件格式，仅支持 MP3/WAV/M4A"
}
```

---

### 3. 任务状态查询

```http
GET /api/task/{task_id}
```

**路径参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| `task_id` | String | 任务 ID |

**响应**:
```json
{
  "task_id": "uuid-string",
  "status": "processing",  // processing / completed / failed
  "progress": 45,  // 进度百分比 0-100
  "current_step": "analyzing_speech",  // uploading / transcribing / analyzing / completed
  "created_at": "2026-04-08T13:00:00Z",
  "updated_at": "2026-04-08T13:02:00Z",
  "error_message": null  // 失败时的错误信息
}
```

---

### 4. 获取分析报告

```http
GET /api/report/{task_id}
```

**路径参数**:
| 参数 | 类型 | 说明 |
|------|------|------|
| `task_id` | String | 任务 ID |

**前置条件**: 任务状态必须为 `completed`

**响应**:
```json
{
  "task_id": "uuid-string",
  "audio_duration": 7200,  // 音频时长（秒）
  "transcript": {
    "segments": [
      {
        "start": 0.0,
        "end": 5.2,
        "text": "欢迎大家来到直播间，今天我们有一款超级划算的产品...",
        "speaker": "主播"
      }
    ]
  },
  "analysis": {
    "summary": "整场直播节奏良好，开场留人话术有效，但在产品介绍环节存在翻车点",
    "highlights": [
      {
        "timestamp": 120,
        "type": "爆点",
        "text": "今天这个价格只有直播间有，库存只有 50 单，抢完就没了！",
        "reason": "限时限量 + 紧迫感营造",
        "effect": "假设订单增长 300%"
      }
    ],
    "issues": [
      {
        "timestamp": 1800,
        "type": "翻车",
        "text": "这个产品我也没用过，厂家说挺好的",
        "problem": "缺乏可信度，暴露不熟悉产品",
        "suggestion": "改为：这款我自己用了 3 个月，最明显的感受是..."
      }
    ],
    "emotion_curve": [
      {"timestamp": 0, "value": 0.6},
      {"timestamp": 300, "value": 0.8},
      {"timestamp": 600, "value": 0.5}
    ],
    "statistics": {
      "total_speeches": 150,
      "highlight_count": 12,
      "issue_count": 8,
      "avg_emotion": 0.65
    }
  },
  "export_urls": {
    "pdf": "/api/export/pdf/{task_id}",
    "json": "/api/export/json/{task_id}"
  }
}
```

---

### 5. 导出报告

```http
GET /api/export/pdf/{task_id}
GET /api/export/json/{task_id}
```

**响应**: 文件下载

---

## 📊 状态码说明

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 404 | 任务不存在 |
| 413 | 文件过大 |
| 415 | 不支持的文件类型 |
| 500 | 服务器内部错误 |

---

## 🔄 前端调用流程

```
1. 上传音频 → POST /api/upload → 获得 task_id
2. 轮询状态 → GET /api/task/{task_id} (每 3 秒)
3. 状态=completed → GET /api/report/{task_id}
4. 渲染报告页面
```

**轮询示例** (前端):
```typescript
async function pollTaskStatus(taskId: string) {
  while (true) {
    const res = await fetch(`/api/task/${taskId}`);
    const data = await res.json();
    
    if (data.status === 'completed') {
      // 跳转到报告页
      router.push(`/report/${taskId}`);
      break;
    } else if (data.status === 'failed') {
      alert('分析失败：' + data.error_message);
      break;
    }
    
    // 更新进度条
    updateProgress(data.progress);
    
    // 3 秒后重试
    await sleep(3000);
  }
}
```

---

## 📝 数据模型定义

### Task (任务)
```typescript
interface Task {
  task_id: string;
  status: 'processing' | 'completed' | 'failed';
  progress: number;  // 0-100
  current_step: 'uploading' | 'transcribing' | 'analyzing' | 'completed';
  created_at: string;
  updated_at: string;
  error_message?: string;
}
```

### AnalysisReport (分析报告)
```typescript
interface AnalysisReport {
  task_id: string;
  audio_duration: number;
  transcript: Transcript;
  analysis: Analysis;
  export_urls: ExportUrls;
}

interface Transcript {
  segments: TranscriptSegment[];
}

interface TranscriptSegment {
  start: number;  // 秒
  end: number;
  text: string;
  speaker: '主播' | '嘉宾' | '未知';
}

interface Analysis {
  summary: string;
  highlights: Highlight[];
  issues: Issue[];
  emotion_curve: EmotionPoint[];
  statistics: Statistics;
}

interface Highlight {
  timestamp: number;
  type: '爆点' | '亮点' | '高转化';
  text: string;
  reason: string;
  effect?: string;
}

interface Issue {
  timestamp: number;
  type: '翻车' | '问题' | '待优化';
  text: string;
  problem: string;
  suggestion: string;
}

interface EmotionPoint {
  timestamp: number;
  value: number;  // 0-1 情绪值
}

interface Statistics {
  total_speeches: number;
  highlight_count: number;
  issue_count: number;
  avg_emotion: number;
}
```

---

## 🔐 安全注意事项

- MVP 阶段无认证，**不要部署到公网**
- 文件上传限制 2GB，防止 DoS
- 后续版本添加 API Key 认证
- 敏感数据（API Key）存储在 `.env` 文件

---

*文档维护：前后端开发代理共同维护，变更需同步更新*
