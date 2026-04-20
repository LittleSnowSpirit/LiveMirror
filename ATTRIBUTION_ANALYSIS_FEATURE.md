# 话术 - 数据归因分析功能

> **核心定位**：AI 驱动的直播复盘分析系统，通过话术 - 数据归因分析，帮助主播优化直播效果  
> **版本**：v1.0.0  
> **状态**：✅ 开发完成

---

## 📋 功能概述

话术 - 数据归因分析是 LiveMirror 的**核心功能**，解决以下关键问题：

1. **哪些话术导致了观众情绪高峰？**
2. **哪些话术引发了大量互动？**
3. **哪些话术促进了转化行为？**
4. **如何优化低影响力话术？**

---

## 🎯 核心能力

### 1. 情绪峰值检测

**功能**：自动识别情绪曲线中的显著峰值（爆点/翻车时刻）

**算法特点**：
- 滑动窗口检测局部最大值
- 智能合并时间接近的峰值
- 峰值等级分类（very_high/high/medium/low）
- 估算峰值持续时间

**配置参数**：
- `emotion_peak_threshold`: 0.7（情绪分数阈值）
- `peak_window_seconds`: 30（峰值检测窗口）
- `min_gap`: 15（峰值合并最小间隔）

---

### 2. 话术 - 情绪关联

**功能**：分析每个话术片段对观众情绪的影响

**归因维度**：
1. **话术期间平均情绪** - 话术播放时观众的平均情绪水平
2. **延迟峰值效应** - 话术后 30 秒内是否出现情绪高峰
3. **情绪趋势** - 话术期间情绪是上升还是下降

**输出指标**：
- `emotion_impact`: 情绪影响分数 (0-1)
- `issues`: 诊断出的问题列表
- `suggestions`: 优化建议列表

---

### 3. 话术 - 弹幕关联

**功能**：分析每个话术片段引发的弹幕互动

**统计指标**：
- `total_count`: 弹幕总数
- `positive_count`: 积极弹幕数
- `negative_count`: 消极弹幕数
- `key_danmu_count`: 关键弹幕数（高潮/争议/赞赏）
- `engagement_rate`: 互动率（弹幕数/分钟）
- `positive_ratio`: 积极弹幕比例

---

### 4. 综合归因评分

**功能**：综合多个维度，给出每个话术的综合影响力评分

**评分公式**：
```
overall_score = emotion_impact × 40 + engagement_impact × 40 + conversion_impact × 20
```

**权重配置**（可在 `attribution.py` 中调整）：
```python
self.weights = {
    'emotion': 0.4,      # 情绪影响权重 40%
    'engagement': 0.4,   # 互动影响权重 40%
    'conversion': 0.2    # 转化影响权重 20%
}
```

**置信度评估**：
- 基于数据量（弹幕数量）评估归因结果的可信度
- 20 条弹幕 = 100% 置信度

---

## 📡 API 接口

### 基础信息

- **Base URL**: `http://localhost:8001`
- **API 文档**: `http://localhost:8001/docs`

---

### 1. 执行完整归因分析

```http
POST /api/attribution/analyze
Content-Type: application/json
```

**请求体**：
```json
{
  "speech_segments": [
    {
      "id": "speech_1",
      "type": "opening",
      "content": "欢迎大家来到直播间...",
      "start_time": 0,
      "end_time": 30
    }
  ],
  "emotion_curve": [
    {
      "timestamp": 10.5,
      "score": 0.8,
      "level": "high"
    }
  ],
  "danmu_list": [
    {
      "timestamp": 15.0,
      "content": "666",
      "sentiment": "positive",
      "sentiment_score": 0.8,
      "is_key_danmu": true
    }
  ],
  "top_n": 10
}
```

**响应**：
```json
{
  "success": true,
  "message": "归因分析完成",
  "data": {
    "summary": {
      "total_speech_segments": 50,
      "emotion_peaks_count": 8,
      "total_danmus": 320,
      "analysis_timestamp": "2026-04-09T21:45:00"
    },
    "top_speeches": [
      {
        "speech_id": "speech_15",
        "speech_type": "price_promotion",
        "speech_content": "今天直播间特价，只要 99 元！",
        "start_time": 180,
        "end_time": 210,
        "overall_score": 85.5,
        "emotion_impact": 0.92,
        "engagement_impact": 0.78,
        "confidence": 0.95,
        "issues": [],
        "suggestions": []
      }
    ],
    "emotion_peaks": [
      {
        "timestamp": 185.0,
        "score": 0.95,
        "duration": 25,
        "level": "very_high"
      }
    ],
    "recommendations": [
      {
        "type": "keep_doing",
        "priority": "high",
        "title": "保持价格优惠的话术风格",
        "description": "这类话术情绪影响分数达到 0.92，观众反响很好",
        "example": "今天直播间特价，只要 99 元！"
      }
    ]
  }
}
```

---

### 2. 检测情绪峰值

```http
POST /api/attribution/emotion-peaks
Content-Type: application/json
```

**请求体**：
```json
{
  "emotion_curve": [...],
  "window_seconds": 30
}
```

**响应**：
```json
{
  "success": true,
  "peaks": [
    {
      "timestamp": 185.0,
      "score": 0.95,
      "duration": 25,
      "level": "very_high"
    }
  ],
  "count": 3
}
```

---

### 3. 话术 - 情绪关联

```http
POST /api/attribution/speech-emotion
Content-Type: application/json
```

**请求体**：
```json
{
  "speech_segments": [...],
  "emotion_curve": [...]
}
```

**响应**：
```json
{
  "success": true,
  "results": [
    {
      "speech_id": "speech_1",
      "speech_type": "opening",
      "emotion_impact": 0.65,
      "issues": ["情绪影响力较低"],
      "suggestions": ["尝试增加情感表达或互动元素"]
    }
  ]
}
```

---

### 4. 话术 - 弹幕关联

```http
POST /api/attribution/speech-danmu
Content-Type: application/json
```

**请求体**：
```json
{
  "speech_segments": [...],
  "danmu_list": [...]
}
```

**响应**：
```json
{
  "success": true,
  "correlation": {
    "speech_1": {
      "total_count": 15,
      "positive_count": 10,
      "negative_count": 2,
      "key_danmu_count": 3,
      "engagement_rate": 30.0,
      "positive_ratio": 0.67
    }
  }
}
```

---

### 5. 获取归因报告

```http
GET /api/attribution/report/{session_id}?top_n=10
```

**响应**：完整归因分析报告（同 `/analyze` 接口）

---

### 6. 获取/更新配置

```http
GET /api/attribution/config
PUT /api/attribution/config
```

---

## 🧪 测试结果

**测试文件**: `backend/tests/test_attribution.py`

**测试覆盖**：
- ✅ 情绪峰值检测 (4 个测试)
- ✅ 话术 - 情绪关联 (2 个测试)
- ✅ 话术 - 弹幕关联 (2 个测试)
- ✅ 完整归因报告 (4 个测试)
- ✅ 边界情况 (3 个测试)
- ✅ 性能测试 (1 个测试)

**测试结果**: **16/16 通过 (100%)**

**性能指标**：
- 100 个话术片段 + 1000 条弹幕分析耗时 < 0.2 秒
- 情绪峰值检测耗时 < 0.01 秒

---

## 💻 使用示例

### Python SDK

```python
from backend.services.attribution import analyze_attribution

# 准备数据
speech_segments = [
    {
        "id": "speech_1",
        "type": "opening",
        "content": "欢迎大家来到直播间",
        "start_time": 0,
        "end_time": 30
    }
]

emotion_curve = [
    {"timestamp": 10, "score": 0.8, "level": "high"}
]

danmu_list = [
    {"timestamp": 15, "content": "666", "sentiment": "positive"}
]

# 执行分析
report = analyze_attribution(
    speech_segments=speech_segments,
    emotion_curve=emotion_curve,
    danmu_list=danmu_list,
    top_n=10
)

# 查看结果
print(f"总话术数：{report['summary']['total_speech_segments']}")
print(f"情绪峰值数：{report['summary']['emotion_peaks_count']}")
print(f"Top 话术：{report['top_speeches'][0]['speech_content']}")
print(f"优化建议：{report['recommendations']}")
```

### JavaScript/前端

```javascript
// 执行归因分析
const response = await fetch('http://localhost:8001/api/attribution/analyze', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    speech_segments: [...],
    emotion_curve: [...],
    danmu_list: [...],
    top_n: 10
  })
});

const result = await response.json();

// 展示 Top 话术
result.data.top_speeches.forEach(speech => {
  console.log(`${speech.speech_type}: ${speech.overall_score}分`);
});

// 展示情绪峰值
result.data.emotion_peaks.forEach(peak => {
  console.log(`峰值时刻：${peak.timestamp}s, 分数：${peak.score}`);
});
```

---

## 🎨 前端可视化建议

### 1. 情绪曲线 + 峰值标记

```
情绪分数
1.0 |           * (峰值)
    |         /   \
0.8 |       *       * (峰值)
    |     /           \
0.6 |   *               *
    | /                 \
0.4 |_______________________ 时间
    0   30   60   90   120
```

### 2. 话术影响力排行榜

```
Top 1: 价格优惠话术 ████████████████ 85.5 分
Top 2: 限时抢购话术 ██████████████   78.2 分
Top 3: 产品介绍话术 ████████████     65.8 分
```

### 3. 归因关系图

```
话术片段 ──→ 情绪峰值 (延迟 5s)
   │
   └──→ 弹幕互动 (+15 条)
```

---

## 🔧 配置调优

### 调整情绪峰值阈值

```python
# backend/services/attribution.py
class AttributionAnalysisService:
    def __init__(self):
        self.emotion_peak_threshold = 0.7  # 降低阈值会检测到更多峰值
```

### 调整归因权重

```python
# 如果更看重互动而非情绪
self.weights = {
    'emotion': 0.3,      # 降低情绪权重
    'engagement': 0.5,   # 提高互动权重
    'conversion': 0.2
}
```

---

## ⚠️ 注意事项

1. **数据质量要求**：
   - 情绪曲线数据点间隔建议 ≤ 10 秒
   - 弹幕时间戳应与话术时间轴对齐
   - 话术分段不应重叠

2. **性能建议**：
   - 单场直播话术片段建议 ≤ 200 个
   - 弹幕数据建议分批处理（每批 ≤ 1000 条）
   - 大规模分析建议使用异步接口

3. **归因准确性**：
   - 置信度 < 0.5 的结果仅供参考
   - 建议结合人工标注验证
   - 多场次数据可提升归因准确度

---

## 📝 后续优化方向

1. **转化归因** - 对接转化数据，完善转化归因维度
2. **语义关联** - 使用 NLP 分析话术内容与弹幕的语义相关性
3. **因果推断** - 引入因果推断算法，提升归因因果性
4. **实时归因** - 支持直播中实时归因分析
5. **跨场次对比** - 同一话术在不同场次的表现对比

---

## 🔗 相关文件

- **服务代码**: `backend/services/attribution.py`
- **API 路由**: `backend/routes/attribution.py`
- **测试文件**: `backend/tests/test_attribution.py`
- **开发计划**: `DEVELOPMENT_PLAN.md`

---

*最后更新：2026-04-09*
