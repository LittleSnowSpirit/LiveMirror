# LiveMirror 多直播间对比功能

## 功能概述

多直播间对比分析功能支持同时对比多个直播间的数据表现，通过可视化图表和 AI 智能分析，帮助发现不同直播间之间的差异和优化空间。

## 核心功能

### 1. 多直播间数据模型
- 支持同时对比 2-10 个直播间
- 统一数据格式，包含观众数、互动率、转化率等核心指标
- 自动加载历史数据或生成模拟数据

### 2. 对比指标设计
- **转化率**: 观众购买转化百分比
- **互动率**: 弹幕、点赞等互动行为百分比
- **情绪值**: 观众情绪平均分 (0-100)
- **留存率**: 观众留存百分比
- **五维评分**: 内容质量、互动效果、节奏把控、话术技巧、观众留存

### 3. 对比图表
- **并列柱状图**: 直观对比各直播间核心指标
- **雷达图**: 五维评分全方位对比
- **情绪曲线**: 多直播间情绪变化趋势对比

### 4. 历史趋势对比
- 支持查看直播间历史表现
- 趋势分析和同比/环比对比

### 5. AI 差异分析报告
- 自动识别表现最佳和最差直播间
- 分析关键差异点
- 生成个性化优化建议

### 6. 报告导出
- PDF 格式报告（需安装 reportlab）
- JSON 格式数据导出
- 支持一键分享

## API 接口

### 基础对比
```http
GET /api/compare/?room_ids=room_001,room_002,room_003
```

响应示例:
```json
{
  "success": true,
  "data": {
    "timestamp": "2026-04-08T18:39:36.795418",
    "rooms": [...],
    "metrics_comparison": {...},
    "radar_data": {...},
    "emotion_curves": {...},
    "ai_analysis": {...},
    "recommendations": [...]
  },
  "message": "成功对比 3 个直播间",
  "elapsed_time": 0.05
}
```

### 获取指标对比
```http
GET /api/compare/metrics/room_001,room_002,room_003
```

### 获取雷达图数据
```http
GET /api/compare/radar/room_001,room_002,room_003
```

### 获取情绪曲线
```http
GET /api/compare/emotion/room_001,room_002,room_003
```

### 获取 AI 分析
```http
GET /api/compare/analysis/room_001,room_002,room_003
```

### 导出 PDF 报告
```http
GET /api/compare/export/pdf/room_001,room_002,room_003
```

## 前端使用

### 访问对比页面
```
http://localhost:5173/compare
```

### 操作步骤
1. 在输入框中输入直播间 ID，用逗号分隔
2. 点击"开始对比"按钮
3. 查看对比结果和 AI 分析
4. 切换不同图表类型（指标对比、情绪曲线、五维评分）
5. 导出报告或复制优化建议

## 后端服务

### 服务类
- `CompareAnalysisService`: 核心对比分析服务
- 位置：`backend/services/compare_analysis.py`

### 路由
- 位置：`backend/routes/compare.py`
- 前缀：`/api/compare`

### 主要方法

```python
# 加载直播间数据
service.load_room_data(room_ids: List[str]) -> List[LiveRoomMetrics]

# 计算对比指标
service.calculate_comparison_metrics(rooms) -> Dict

# 生成雷达图数据
service.generate_radar_data(rooms) -> Dict

# 生成情绪曲线
service.generate_emotion_curves(room_ids) -> Dict

# 生成 AI 分析
service.generate_ai_analysis(rooms) -> Dict

# 生成优化建议
service.generate_recommendations(rooms, ai_analysis) -> List[str]

# 执行完整对比
service.compare_rooms(room_ids) -> ComparisonResult

# 导出 PDF 报告
service.export_to_pdf(result, output_path) -> bool
```

## 前端组件

### Compare.vue
- 位置：`livemirror-frontend/src/views/Compare.vue`
- 功能：主对比页面

### CompareChart.vue
- 位置：`livemirror-frontend/src/components/CompareChart.vue`
- 功能：对比图表组件（支持指标、情绪、雷达三种类型）

## 测试

### 运行测试
```bash
python tests/test_compare.py
```

### 测试覆盖
1. ✅ 多直播间数据加载
2. ✅ 对比指标计算
3. ✅ 雷达图数据生成
4. ✅ 情绪曲线生成
5. ✅ AI 差异分析
6. ✅ 优化建议生成
7. ✅ 完整对比流程
8. ✅ 报告导出（PDF/JSON）
9. ✅ 性能测试（3 个直播间对比 < 2 秒）

## 数据模型

### LiveRoomMetrics
```python
@dataclass
class LiveRoomMetrics:
    room_id: str
    room_name: str
    total_viewers: int
    avg_duration: float
    engagement_rate: float
    conversion_rate: float
    emotion_avg: float
    emotion_peak: float
    interaction_count: int
    speech_quality: float
    content_quality: float
    rhythm_control: float
    retention_rate: float
```

### ComparisonResult
```python
@dataclass
class ComparisonResult:
    timestamp: str
    rooms: List[LiveRoomMetrics]
    metrics_comparison: Dict
    radar_data: Dict
    emotion_curves: Dict
    ai_analysis: Dict
    recommendations: List[str]
```

## 性能指标

- **数据加载**: < 0.01s
- **指标计算**: < 0.01s
- **完整对比**: < 0.1s (3 个直播间)
- **报告导出**: < 1s (JSON), < 3s (PDF)

## 依赖

### Python
- fastapi
- reportlab (可选，用于 PDF 导出)
- sqlite3 (内置)

### Node.js
- vue 3
- echarts
- element-plus

## 扩展建议

1. **真实数据集成**: 对接实际直播间数据源
2. **更多图表类型**: 添加热力图、散点图等
3. **自定义指标**: 支持用户自定义对比指标
4. **定时对比**: 设置定时任务自动对比
5. **告警功能**: 指标异常时自动告警

## 注意事项

1. 至少需要 2 个直播间才能进行对比
2. PDF 导出需要安装 `reportlab` 库：`pip install reportlab`
3. 如果没有真实数据，系统会自动生成模拟数据用于演示
4. 建议对比的直播间数量不超过 10 个，以保证图表清晰度

## 更新日志

### v1.0.0 (2026-04-08)
- ✅ 初始版本发布
- ✅ 支持多直播间数据对比
- ✅ 实现指标计算和可视化
- ✅ AI 差异分析报告
- ✅ PDF/JSON 报告导出
- ✅ 完整的测试覆盖
