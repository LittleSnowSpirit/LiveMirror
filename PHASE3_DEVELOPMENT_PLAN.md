# LiveMirror 第三阶段开发计划

> **核心定位**：AI 驱动的直播复盘分析系统  
> **开发阶段**：第三阶段 - 深度分析与可视化  
> **版本目标**：v2.1.0 → v2.2.0 → v2.3.0  
> **最后更新**：2026-04-09

---

## 🎯 三大核心方向

```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│   ① 前端可视化          ② 建议生成          ③ 趋势分析  │
│   ───────────          ────────          ────────      │
│   归因分析展示          话术改写示例        跨场次对比   │
│   情绪曲线 + 峰值        Before/After       成长追踪     │
│   话术影响力排行        AI 优化建议         进步/退步识别 │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

**开发策略**：循环迭代，每个方向同步推进，小步快跑

---

## 📋 方向一：前端可视化

**目标**：将归因分析结果以直观、交互的方式呈现给用户

**版本**：v2.1.0  
**预计耗时**：4-6 小时

---

### 1.1 功能清单

| 功能 | 说明 | 优先级 | 状态 |
|------|------|--------|------|
| 情绪曲线可视化 | ECharts 绘制情绪曲线 + 峰值标记 | P0 | ⏳ |
| 话术影响力排行榜 | Top 10 话术卡片展示 | P0 | ⏳ |
| 归因关系图 | 话术→情绪→弹幕的关联可视化 | P1 | ⏳ |
| 弹幕热力时间轴 | 弹幕密度 + 情感分布堆叠图 | P1 | ⏳ |
| 筛选与交互 | 按话术类型/时间段筛选 | P1 | ⏳ |
| 导出可视化报告 | 截图/PDF 导出 | P2 | ⏳ |

---

### 1.2 组件结构

```
frontend/src/components/attribution/
├── EmotionCurve.vue        # 情绪曲线组件
├── SpeechRanking.vue       # 话术影响力排行榜
├── AttributionGraph.vue    # 归因关系图
├── DanmuHeatmap.vue        # 弹幕热力时间轴
├── FilterPanel.vue         # 筛选控制面板
└── ExportReport.vue        # 报告导出组件
```

---

### 1.3 技术方案

**图表库**：ECharts 5.x

**情绪曲线实现**：
```javascript
// EmotionCurve.vue
- x 轴：时间（秒）
- y 轴：情绪分数（0-1）
- 折线图：情绪变化趋势
- 散点图：峰值标记（不同颜色表示等级）
- 工具提示：显示峰值详情
```

**话术排行榜实现**：
```javascript
// SpeechRanking.vue
- 水平条形图：综合评分
- 颜色编码：话术类型
- 点击展开：查看详情和建议
- 支持排序：按情绪/互动/综合评分
```

**归因关系图实现**：
```javascript
// AttributionGraph.vue
- 力导向图或桑基图
- 节点：话术、情绪峰值、弹幕簇
- 边：关联强度（粗细表示）
- 交互：点击高亮相关节点
```

---

### 1.4 API 对接

```javascript
// 获取归因分析数据
const response = await api.post('/api/attribution/analyze', {
  speech_segments: ...,
  emotion_curve: ...,
  danmu_list: ...
});

// 数据转换
const chartData = {
  emotionCurve: response.data.emotion_curve,
  peaks: response.data.emotion_peaks,
  topSpeeches: response.data.top_speeches
};
```

---

### 1.5 验收标准

- [ ] 情绪曲线渲染流畅（60fps）
- [ ] 峰值标记清晰可见
- [ ] 话术卡片支持点击展开
- [ ] 筛选器响应迅速（<100ms）
- [ ] 移动端适配（响应式）
- [ ] 所有图表支持导出图片

---

## 📋 方向二：深化建议生成

**目标**：基于归因结果，生成具体、可执行的话术优化建议

**版本**：v2.2.0  
**预计耗时**：4-6 小时

---

### 2.1 功能清单

| 功能 | 说明 | 优先级 | 状态 |
|------|------|--------|------|
| 话术问题诊断 | 识别具体问题（节奏/措辞/逻辑） | P0 | ⏳ |
| Before/After 示例 | 提供具体改写对比 | P0 | ⏳ |
| 优秀话术推荐 | 推荐同类优秀话术参考 | P1 | ⏳ |
| 建议优先级排序 | 按影响程度排序 | P1 | ⏳ |
| 建议效果预估 | 预估改进后的效果提升 | P2 | ⏳ |
| 一键复制 | 快速复制建议话术 | P2 | ⏳ |

---

### 2.2 建议生成引擎

**文件**：`backend/services/suggestion_engine.py`

**核心能力**：

```python
class SuggestionEngine:
    def diagnose_issues(self, speech: Dict) -> List[Issue]:
        """诊断话术问题"""
        # 检测维度：
        # 1. 节奏问题（过长/过短）
        # 2. 情感表达（平淡/过度）
        # 3. 互动元素（缺少提问/引导）
        # 4. 逻辑结构（混乱/清晰）
        # 5. 关键词使用（促销词/情感词）
        pass
    
    def generate_rewrite(self, speech: Dict, issues: List[Issue]) -> RewriteExample:
        """生成改写示例"""
        # 输出格式：
        # {
        #   "before": "原价 199，今天 99 元",
        #   "after": "平时卖 199 的产品，今天直播间只要 99！立省 100 块！",
        #   "changes": ["增加对比", "强调优惠力度", "加入情绪词"],
        #   "expected_improvement": "+15% 情绪影响"
        # }
        pass
    
    def recommend_similar(self, speech_type: str) -> List[ExcellentExample]:
        """推荐优秀话术参考"""
        # 从优秀场次中检索同类话术
        pass
```

---

### 2.3 问题诊断规则

**节奏问题**：
```python
if duration > 120:  # 超过 2 分钟
    issues.append("话术过长，建议拆分或精简")
elif duration < 10:  # 少于 10 秒
    issues.append("话术过短，可能缺乏细节")
```

**情感表达**：
```python
if emotion_impact < 0.3:
    issues.append("情感表达平淡，建议增加情绪词")
    suggestions.append("试试加入'超级'、'超值'、'限时'等词")
```

**互动元素**：
```python
if not contains_question(speech_content):
    issues.append("缺少互动元素")
    suggestions.append("加入提问：'有没有想要的宝宝？'")
```

---

### 2.4 改写示例模板

**价格优惠话术改写**：
```
Before: "这个产品 99 元"
After:  "平时专柜卖 199 的产品，今天直播间福利价只要 99！立省 100 块！只有今天这个价格！"
改进点:
  - 增加价格对比（专柜价 vs 直播价）
  - 强调优惠力度（立省 100）
  - 制造紧迫感（只有今天）
预期提升：情绪影响 +20%，互动率 +15%
```

**产品介绍话术改写**：
```
Before: "这个面膜补水效果很好"
After:  "这款面膜我连续用了 28 天，皮肤从干燥起皮到现在水嫩嫩的！早上上妆完全不卡粉！"
改进点:
  - 加入使用时长（28 天）
  - 具体效果对比（干燥→水嫩）
  - 场景化描述（上妆不卡粉）
预期提升：情绪影响 +25%，可信度 +30%
```

---

### 2.5 API 接口

```http
POST /api/suggestions/diagnose
Request: { "speech_id": "123", "session_id": "abc" }
Response: {
  "issues": [...],
  "suggestions": [...],
  "rewrite_example": {...}
}

POST /api/suggestions/rewrite
Request: { "speech_content": "...", "speech_type": "price_promotion" }
Response: {
  "before": "...",
  "after": "...",
  "changes": [...],
  "expected_improvement": {...}
}

GET /api/suggestions/excellent-examples?speech_type=price_promotion&limit=5
Response: {
  "examples": [...]
}
```

---

### 2.6 验收标准

- [ ] 80% 的低分话术能生成有效诊断
- [ ] 每条建议包含具体改写示例
- [ ] 改写示例符合话术类型特点
- [ ] 建议可执行性强（用户反馈有用 > 70%）
- [ ] 响应时间 < 500ms

---

## 📋 方向三：趋势分析

**目标**：跨场次追踪主播成长，发现长期问题和进步

**版本**：v2.3.0  
**预计耗时**：4-6 小时

---

### 3.1 功能清单

| 功能 | 说明 | 优先级 | 状态 |
|------|------|--------|------|
| 历史场次列表 | 按时间排序的直播场次 | P0 | ⏳ |
| 情绪趋势图 | 多场次情绪曲线对比 | P0 | ⏳ |
| 话术质量趋势 | 各类话术评分变化 | P0 | ⏳ |
| 互动率趋势 | 观众参与度变化 | P1 | ⏳ |
| 进步/退步识别 | 自动识别显著变化 | P1 | ⏳ |
| 成长报告生成 | 周期性成长报告 | P2 | ⏳ |

---

### 3.2 数据模型

**文件**：`backend/models.py` - 新增表

```python
class TrendMetrics(Base):
    """趋势指标存储"""
    __tablename__ = "trend_metrics"

    id = Column(Integer, primary_key=True)
    session_id = Column(String, index=True)  # 场次 ID
    anchor_time = Column(DateTime, index=True)  # 直播时间
    
    # 核心指标
    avg_emotion_score = Column(Float)  # 平均情绪分
    peak_emotion_score = Column(Float)  # 峰值情绪分
    engagement_rate = Column(Float)  # 互动率
    conversion_rate = Column(Float)  # 转化率（如有）
    
    # 话术质量分
    opening_score = Column(Float)  # 开场话术分
    product_intro_score = Column(Float)  # 产品介绍分
    price_promotion_score = Column(Float)  # 价格话术分
    closing_score = Column(Float)  # 促单话术分
    
    # 综合评分
    overall_score = Column(Float)
    
    # 元数据
    duration_minutes = Column(Integer)
    viewer_count = Column(Integer)
    danmu_count = Column(Integer)
```

---

### 3.3 趋势分析算法

**文件**：`backend/services/trend_analysis.py`

**核心功能**：

```python
class TrendAnalysisService:
    def calculate_trend(self, metrics: List[float]) -> Dict:
        """计算趋势（上升/下降/平稳）"""
        # 使用线性回归或移动平均
        pass
    
    def detect_significant_change(self, series: List[float]) -> List[Dict]:
        """检测显著变化点"""
        # 识别突变点（如情绪分突然下降）
        pass
    
    def generate_growth_report(self, session_ids: List[str]) -> Dict:
        """生成成长报告"""
        # 对比首期 vs 最新期
        # 识别进步最大的方面
        # 指出仍需改进的问题
        pass
```

---

### 3.4 趋势可视化

**情绪趋势图**：
```
情绪分
1.0 |               *
    |             *   *
0.8 |     *     *       *   ← 上升趋势
    |   *   *             *
0.6 | *                   *
    |________________________ 场次
    1   2   3   4   5   6
```

**雷达图对比**（首期 vs 最新）：
```
        开场话术
          / \
     促单 *   * 产品介绍
        /     \
    互动 *-----* 价格话术
```

---

### 3.5 API 接口

```http
GET /api/trends/sessions?anchor_id={session_id}&limit=10
Response: {
  "sessions": [
    {"id": "123", "date": "2026-04-08", "overall_score": 75},
    ...
  ]
}

GET /api/trends/emotion?session_ids=123,124,125
Response: {
  "trend_data": [...],
  "trend_direction": "up",
  "change_rate": "+12%"
}

GET /api/trends/speech-quality?session_ids=...
Response: {
  "by_type": {
    "opening": {"trend": "up", "scores": [...]},
    "product_intro": {"trend": "stable", "scores": [...]}
  }
}

GET /api/trends/report?session_ids=...
Response: {
  "summary": "...",
  "improvements": [...],
  "areas_to_work_on": [...]
}
```

---

### 3.6 成长报告模板

```markdown
# 直播成长报告

## 概览
- 分析场次：5 场
- 时间跨度：2026-04-01 ~ 2026-04-08
- 整体趋势：📈 进步中

## 进步最大的方面
1. **价格优惠话术** (+18%)
   - 从平均 62 分提升到 80 分
   - 学会了使用价格对比和紧迫感营造

2. **互动引导** (+15%)
   - 提问次数从场均 3 次增加到 8 次
   - 观众弹幕互动率提升 25%

## 仍需改进
1. **产品介绍话术** (波动较大)
   - 建议：增加使用场景描述和用户见证

2. **情绪调动** (近期下降)
   - 建议：参考优秀场次的节奏把控

## 建议
- 保持价格话术的改进方向
- 复习第 3 场的产品介绍方式
- 尝试在第 2 场的高潮段落加入更多互动
```

---

### 3.7 验收标准

- [ ] 支持查看任意场次历史数据
- [ ] 趋势图清晰展示变化方向
- [ ] 能准确识别进步/退步（与人工标注对比 > 80% 一致）
- [ ] 成长报告有具体数据支撑
- [ ] 响应时间 < 1s（10 场以内）

---

## 🔄 循环开发流程

### 迭代 1（v2.1.0）- 基础可视化
- [ ] EmotionCurve.vue 组件
- [ ] SpeechRanking.vue 组件
- [ ] 后端 API 对接
- [ ] 基础样式

### 迭代 2（v2.1.1）- 深化可视化
- [ ] AttributionGraph.vue 组件
- [ ] DanmuHeatmap.vue 组件
- [ ] 筛选交互功能
- [ ] 响应式适配

### 迭代 3（v2.2.0）- 建议生成
- [ ] SuggestionEngine 服务
- [ ] 问题诊断规则
- [ ] Before/After 示例生成
- [ ] 优秀话术推荐

### 迭代 4（v2.2.1）- 建议优化
- [ ] 建议优先级排序
- [ ] 效果预估
- [ ] 前端展示组件
- [ ] 一键复制功能

### 迭代 5（v2.3.0）- 趋势分析
- [ ] TrendMetrics 数据模型
- [ ] TrendAnalysisService 服务
- [ ] 情绪趋势图
- [ ] 话术质量趋势

### 迭代 6（v2.3.1）- 成长报告
- [ ] 进步/退步识别
- [ ] 成长报告生成
- [ ] 报告可视化
- [ ] 导出功能

---

## 📊 成功指标

| 指标 | 当前 | 目标 |
|------|------|------|
| 归因分析可视化覆盖率 | 0% | 100% |
| 建议生成有效率 | 0% | > 80% |
| 趋势分析准确度 | 0% | > 85% |
| 用户满意度 | - | > 75% |

---

## ⚠️ 风险与应对

| 风险 | 影响 | 应对措施 |
|------|------|----------|
| ECharts 性能问题 | 中 | 数据分页加载，限制点数 |
| 建议生成质量低 | 高 | 人工审核 + 迭代优化规则 |
| 趋势数据不足 | 中 | 支持模拟数据，累积真实数据 |
| 前端开发量大 | 中 | 优先核心功能，渐进式完善 |

---

## 📝 开发记录

### 2026-04-09
- ✅ 创建开发计划文档
- ⏳ 开始迭代 1：基础可视化

---

*持续更新中...*
