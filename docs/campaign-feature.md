# 营销活动策划功能文档

## 功能概述

营销活动策划功能为 LiveMirror 平台提供完整的活动策划、执行追踪和效果分析能力。

## 核心功能

### 1. 活动策划模板

提供 4 种预设活动模板：
- **产品发布活动** - 新产品上市推广
- **促销活动** - 电商促销活动
- **品牌宣传活动** - 品牌知名度提升
- **用户获取活动** - 新用户拉新

每个模板包含：
- 默认预算分配方案
- 推荐推广渠道
- KPI 指标模板
- 最佳实践建议

### 2. 活动时间规划

智能生成活动时间轴，包括：
- 活动开始/结束日期
- 分阶段规划（预热期、爆发期、收尾期等）
- 关键里程碑设置
- 各阶段任务清单

### 3. 预算和 ROI 预估

预算管理功能：
- 总预算设置
- 渠道预算分配
- 实际花费追踪
- ROI 自动计算：`ROI = (收入 - 成本) / 成本 × 100%`

### 4. 活动效果追踪

实时追踪核心指标：
- 曝光量 (Impressions)
- 点击量 (Clicks)
- 转化量 (Conversions)
- CTR (点击率)
- 转化率 (Conversion Rate)
- 获客成本 (CPA)

### 5. 活动复盘报告

自动生成复盘报告，包括：
- 整体评级（优秀/良好/一般/需改进）
- ROI 分析
- 亮点总结
- 待改进项
- 优化建议

### 6. 优秀活动案例库

内置多个行业优秀案例：
- 美妆品牌双 11 营销
- 新消费品牌小红书种草
- APP 春节拉新活动

每个案例包含：
- 活动目标
- 执行策略
- 最终结果
- 经验总结

## 技术架构

### 后端服务

```
backend/
├── services/
│   └── campaign.py      # 活动策划服务
└── routes/
    └── campaign.py      # API 接口路由
```

### 前端组件

```
frontend/src/
├── views/
│   └── Campaign.vue     # 活动策划主页面
└── components/
    └── CampaignCard.vue # 活动卡片组件
```

### 测试文件

```
tests/
└── test_campaign.py     # 功能测试（25 个测试用例）
```

## API 接口

### 活动管理
- `GET /api/campaigns` - 获取活动列表
- `POST /api/campaigns` - 创建新活动
- `GET /api/campaigns/{id}` - 获取活动详情
- `PUT /api/campaigns/{id}` - 更新活动
- `DELETE /api/campaigns/{id}` - 删除活动

### 效果追踪
- `PUT /api/campaigns/{id}/metrics` - 更新效果指标
- `GET /api/campaigns/{id}/report` - 获取效果报告
- `GET /api/campaigns/{id}/review` - 获取复盘报告

### 模板管理
- `GET /api/campaigns/templates` - 获取模板列表
- `POST /api/campaigns/templates/{id}/create` - 从模板创建活动
- `POST /api/campaigns/timeline/generate` - 生成时间规划

### 案例库
- `GET /api/campaigns/cases` - 获取案例列表
- `GET /api/campaigns/cases/{id}` - 获取案例详情
- `POST /api/campaigns/cases` - 添加新案例

## 测试覆盖

所有核心功能均已测试覆盖：
- ✅ 活动创建、读取、更新、删除
- ✅ 模板管理和使用
- ✅ 效果指标追踪
- ✅ ROI 计算
- ✅ 复盘报告生成
- ✅ 案例库管理
- ✅ 时间规划生成
- ✅ 仪表盘统计

**测试结果：25/25 测试通过**

## 使用示例

### 创建新活动

```python
from backend.services.campaign import campaign_service

campaign = campaign_service.create_campaign({
    "name": "春季促销活动",
    "description": "2026 年春季新品促销",
    "campaign_type": "promotion",
    "budget": {
        "total_budget": 100000,
        "actual_spend": 0
    },
    "timeline": {
        "start_date": "2026-04-01",
        "end_date": "2026-04-30"
    },
    "channels": ["微信", "抖音", "小红书"],
    "goals": ["impressions", "conversions", "revenue"]
})
```

### 从模板创建活动

```python
# 获取模板列表
templates = campaign_service.list_templates()

# 从模板创建
campaign = campaign_service.create_from_template(
    template_id="tpl_promotion",
    custom_data={"name": "618 大促"}
)
```

### 更新效果指标

```python
campaign_service.update_metrics(campaign_id, {
    "impressions": 500000,
    "clicks": 25000,
    "conversions": 1000,
    "revenue": 200000
})
```

### 生成复盘报告

```python
review = campaign_service.generate_review_report(campaign_id)
print(f"整体评级：{review['executive_summary']['overall_rating']}")
print(f"亮点：{review['highlights']}")
print(f"建议：{review['recommendations']}")
```

## 后续优化建议

1. **数据可视化** - 添加图表展示活动趋势
2. **A/B 测试支持** - 支持多版本活动对比
3. **自动化报告** - 定时生成并发送报告
4. **集成对接** - 对接广告平台 API 自动拉取数据
5. **智能推荐** - 基于历史数据推荐最优方案
