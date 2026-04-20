# ROI 分析功能 - LiveMirror

## 功能概述

ROI（Return on Investment）分析功能提供直播投入产出比的全面分析，帮助优化直播成本结构，提高收益。

### 核心功能

1. **直播成本核算** - 人力/场地/推广/设备等成本分类统计
2. **收益统计** - GMV/利润/佣金等收益项追踪
3. **ROI 计算和趋势** - 自动计算 ROI 并分析趋势
4. **成本优化建议** - AI 驱动的成本优化建议
5. **ROI 对比分析** - 多场次 ROI 对比
6. **ROI 可视化报表** - 图表展示和报告生成

## 技术架构

```
backend/
├── services/
│   └── roi_analysis.py      # ROI 分析服务
├── routes/
│   └── roi.py               # ROI API 路由
└── tests/
    ├── test_roi_analysis.py # 单元测试
    └── generate_roi_sample.py # 示例数据生成

frontend/
├── src/views/
│   └── ROIAnalysis.vue      # ROI 分析页面
└── src/components/
    └── ROIChart.vue         # ROI 图表组件
```

## API 接口

### 基础 URL
```
/api/roi
```

### 场次管理

#### 创建场次
```http
POST /api/roi/sessions
Content-Type: application/json

{
  "date": "2026-04-08",
  "start_time": "19:00",
  "end_time": "22:00",
  "category": "general",
  "costs": [
    {"type": "labor", "name": "主播", "amount": 500},
    {"type": "venue", "name": "场地租赁", "amount": 300},
    {"type": "promotion", "name": "广告投放", "amount": 200}
  ],
  "revenues": [
    {"type": "gmv", "name": "商品销售", "amount": 5000},
    {"type": "profit", "name": "利润", "amount": 1000}
  ],
  "notes": "备注信息"
}
```

#### 获取场次列表
```http
GET /api/roi/sessions?start_date=2026-04-01&end_date=2026-04-30&category=beauty
```

#### 获取场次详情
```http
GET /api/roi/sessions/{session_id}
```

#### 更新场次
```http
PUT /api/roi/sessions/{session_id}
Content-Type: application/json

{
  "notes": "更新备注",
  "category": "beauty"
}
```

#### 删除场次
```http
DELETE /api/roi/sessions/{session_id}
```

### ROI 分析

#### 获取 ROI 指标
```http
GET /api/roi/sessions/{session_id}/metrics
```

响应示例：
```json
{
  "success": true,
  "data": {
    "session_id": "session_2026-04-08_1900",
    "date": "2026-04-08",
    "total_cost": 1000,
    "total_revenue": 1500,
    "gmv": 5000,
    "profit": 1500,
    "roi_percentage": 50.0,
    "roi_ratio": 1.5,
    "cost_breakdown": {
      "labor": 500,
      "venue": 300,
      "promotion": 200
    },
    "revenue_breakdown": {
      "gmv": 5000,
      "profit": 1500
    }
  }
}
```

#### 获取成本分解
```http
GET /api/roi/sessions/{session_id}/cost-breakdown
```

#### 获取优化建议
```http
GET /api/roi/sessions/{session_id}/suggestions
```

响应示例：
```json
{
  "success": true,
  "data": [
    {
      "category": "labor",
      "priority": "high",
      "suggestion": "人力成本占比过高（超过 50%），建议优化人员配置或采用自动化方案",
      "expected_impact": "可降低人力成本 20-30%",
      "estimated_savings": 250.0,
      "implementation_difficulty": "medium"
    }
  ]
}
```

### 对比分析

#### 多场次对比
```http
POST /api/roi/compare
Content-Type: application/json

{
  "session_ids": [
    "session_2026-04-08_1900",
    "session_2026-04-09_1900",
    "session_2026-04-10_1900"
  ]
}
```

#### 获取 ROI 趋势
```http
POST /api/roi/trend
Content-Type: application/json

{
  "start_date": "2026-04-01",
  "end_date": "2026-04-30",
  "group_by": "day"
}
```

`group_by` 可选值：`day`, `week`, `month`

### 报告生成

#### 生成 ROI 报告
```http
POST /api/roi/report
Content-Type: application/json

{
  "session_ids": ["session_1", "session_2"]  // 可选，不传则生成所有场次报告
}
```

### 成本模板

#### 获取成本模板
```http
GET /api/roi/templates/cost
```

## 数据模型

### 成本类型 (CostType)
- `labor` - 人力成本
- `venue` - 场地成本
- `promotion` - 推广成本
- `equipment` - 设备成本
- `other` - 其他成本

### 收益类型 (RevenueType)
- `gmv` - 商品交易总额
- `profit` - 利润
- `commission` - 佣金

### ROI 计算公式
```
ROI = (收益 - 成本) / 成本 × 100%
ROI 比率 = 收益 / 成本
```

## 优化建议规则

### 人力成本优化
- 触发条件：人力成本 > 总成本 × 50%
- 优先级：高
- 建议：优化人员配置或采用自动化方案

### 场地成本优化
- 触发条件：场地成本 > 总成本 × 30%
- 优先级：中
- 建议：考虑长期租赁或共享场地

### 推广成本优化
- 触发条件：推广成本 > 总成本 × 30%
- 优先级：高
- 建议：优化投放策略，提高转化率

### ROI 优化
- 负 ROI：高优先级，建议重新评估策略
- ROI < 50%：中优先级，建议优化成本结构
- ROI >= 50%：低优先级，保持当前策略

### 时长优化
- 时长 < 60 分钟：建议延长直播时间
- 时长 > 240 分钟：建议优化为多场次短时长

## 前端页面

### ROI 分析页面 (`/roi-analysis`)

功能模块：
1. **总体指标卡片** - 总成本/总收益/GMV/整体 ROI
2. **ROI 趋势图表** - 按天/周/月展示 ROI 趋势
3. **成本分解** - 各类成本占比可视化
4. **场次列表** - 筛选/排序/操作
5. **创建场次弹窗** - 添加新的直播场次
6. **对比分析弹窗** - 多场次 ROI 对比
7. **优化建议弹窗** - 查看 AI 优化建议
8. **报告预览弹窗** - 查看和下载报告

### ROI 图表组件

支持的图表类型：
- `trend` - ROI 趋势图（折线图）
- `cost-breakdown` - 成本结构（饼图）
- `revenue-comparison` - 收益对比（柱状图）
- `roi-distribution` - ROI 分布（散点图）

## 测试

### 运行单元测试
```bash
cd C:\Users\LittleXiao\.openclaw\workspace
python -m pytest backend/tests/test_roi_analysis.py -v
```

### 生成示例数据
```bash
python -m backend.tests.generate_roi_sample
```

### 测试覆盖
- ✅ 成本核算测试
- ✅ ROI 计算测试
- ✅ 对比分析测试
- ✅ 优化建议测试
- ✅ 报告生成测试
- ✅ CRUD 操作测试
- ✅ 端到端流程测试

## 使用示例

### Python SDK 使用

```python
from backend.services.roi_analysis import get_service

# 获取服务实例
service = get_service()

# 创建场次
session = service.create_session(
    date="2026-04-08",
    start_time="19:00",
    end_time="22:00",
    category="beauty",
    costs=[
        {"type": "labor", "name": "主播", "amount": 500},
        {"type": "venue", "name": "场地", "amount": 300},
        {"type": "promotion", "name": "推广", "amount": 200}
    ],
    revenues=[
        {"type": "gmv", "name": "销售", "amount": 5000},
        {"type": "profit", "name": "利润", "amount": 1000}
    ]
)

# 计算 ROI 指标
metrics = service.calculate_roi_metrics(session.session_id)
print(f"ROI: {metrics.roi_percentage:.2f}%")

# 获取优化建议
suggestions = service.generate_optimization_suggestions(session.session_id)
for s in suggestions:
    print(f"[{s.priority}] {s.suggestion}")

# 对比多场次
comparison = service.compare_sessions([session_id1, session_id2])
print(f"平均 ROI: {comparison.average_roi:.2f}%")
print(f"最佳场次：{comparison.best_roi_session}")

# 生成报告
report = service.generate_report()
print(f"总利润：¥{report['summary']['total_profit']:,.2f}")
```

## 数据存储

数据存储在 `data/roi_analysis/` 目录：
- `live_sessions.json` - 直播场次数据
- `cost_templates.json` - 成本模板
- `reports.json` - 生成的报告

## 性能优化

1. **数据缓存** - 服务实例内存缓存，避免重复加载
2. **批量操作** - 支持批量创建场次
3. **增量计算** - ROI 指标按需计算
4. **分页查询** - 场次列表支持分页（待实现）

## 未来规划

- [ ] 支持导出 Excel 报告
- [ ] 添加预算功能
- [ ] 集成实际销售数据
- [ ] AI 预测 ROI
- [ ] 实时 ROI 监控告警
- [ ] 多维度分析（主播/品类/时间段）

## 注意事项

1. **数据准确性** - 确保成本和收益数据准确录入
2. **及时更新** - 直播结束后及时更新实际数据
3. **定期分析** - 建议每周/每月进行 ROI 分析
4. **建议参考** - 优化建议仅供参考，需结合实际情况

## 常见问题

### Q: ROI 为负数怎么办？
A: 负 ROI 表示亏损，建议：
1. 查看优化建议，优先执行高优先级建议
2. 分析成本结构，找出可削减的成本
3. 评估收益来源，寻找提升空间
4. 考虑暂停或调整直播策略

### Q: 如何比较不同品类的 ROI？
A: 使用分类筛选功能，分别查看各品类的 ROI 数据，或使用对比分析功能选择不同品类的场次进行对比。

### Q: 优化建议的预计节省金额如何计算？
A: 基于历史数据和行业标准估算，实际节省金额可能有所不同。建议作为参考，结合实际情况调整。

---

**版本**: 1.0.0  
**最后更新**: 2026-04-09  
**作者**: LiveMirror Team
