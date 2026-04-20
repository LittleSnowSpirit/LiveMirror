# LiveMirror 直播效果预测功能

## 功能概述

AI 驱动的直播效果预测系统，基于历史数据使用机器学习模型预测：
- GMV（商品交易总额）
- 观看人数
- 转化率
- 最佳直播时间推荐

## 技术架构

### 预测模型

1. **GMV 预测** - 混合模型 (Hybrid)
   - 线性回归 (40% 权重)：捕捉长期趋势
   - 移动平均 (30% 权重)：平滑短期波动
   - 季节性模型 (30% 权重)：考虑周期性变化

2. **观看人数预测** - 指数平滑模型
   - 平滑系数 α=0.3
   - 对近期数据赋予更高权重

3. **转化率预测** - 移动平均模型
   - 7 天窗口
   - 稳定且响应迅速

### 影响因子

- **时间段影响**：晚间 > 下午 > 早上 > 深夜
- **周末效应**：周末 GMV 比工作日高约 30%
- **增长趋势**：基于历史数据的线性趋势
- **数据充足度**：数据点越多，预测越准确

## API 接口

### 预测接口

```bash
# 综合预测
POST /api/prediction/all
{
  "target_date": "2026-04-09",
  "time_slot": "evening",
  "category": "general"
}

# 单项预测
POST /api/prediction/gmv
POST /api/prediction/viewers
POST /api/prediction/conversion-rate
```

### 时间推荐

```bash
# 获取最佳直播时间
POST /api/prediction/recommend-time
{
  "category": "general",
  "top_n": 3
}

# 简化查询
GET /api/prediction/recommend-time?category=general&top_n=3
```

### 历史趋势

```bash
# 获取历史趋势数据
GET /api/prediction/trends?days=30
```

### 数据管理

```bash
# 添加历史数据
POST /api/prediction/historical-data
{
  "date": "2026-04-07",
  "time_slot": "evening",
  "gmv": 10000.0,
  "viewers": 1000,
  "conversions": 50,
  "duration_minutes": 120,
  "category": "beauty"
}

# 评估预测准确度
POST /api/prediction/evaluate
{
  "target_date": "2026-04-07",
  "actual_gmv": 12000.0,
  "actual_viewers": 1200,
  "actual_conversions": 60
}
```

## 前端页面

### 预测页面 (`/prediction`)

功能：
- 配置预测参数（日期、时间段、分类）
- 展示预测结果（GMV、观看人数、转化率）
- 显示置信区间和准确度
- 影响因子可视化
- 最佳时间推荐
- 历史趋势图表

### 图表组件 (`PredictionChart.vue`)

包含：
- GMV 趋势图（折线图）
- 观看人数趋势图（柱状图）
- 转化率趋势图（折线图）
- 时间段对比图（柱状图）

## 测试

### 运行测试

```bash
python -m pytest backend/tests/test_prediction.py -v
```

### 测试覆盖

- ✅ GMV 预测
- ✅ 观看人数预测
- ✅ 转化率预测
- ✅ 综合预测
- ✅ 时间推荐
- ✅ 历史趋势
- ✅ 数据持久化
- ✅ 准确度评估
- ✅ 时间段影响
- ✅ 周末效应
- ✅ API 接口

### 生成预测样本

```bash
python backend/tests/generate_prediction_sample.py
```

样本输出：`data/prediction/sample.json`

## 使用示例

### Python

```python
from backend.services.prediction import get_service

service = get_service()

# 预测明天晚间时段
result = service.predict_all("2026-04-09", "evening", "general")
print(f"预测 GMV: ¥{result.predicted_gmv:,.2f}")
print(f"预测观众：{result.predicted_viewers:,}")
print(f"预测转化率：{result.predicted_conversion_rate*100:.2f}%")

# 获取时间推荐
rec = service.recommend_best_time()
print(f"推荐时段：{rec.recommended_slot}")
print(f"推荐理由：{rec.reason}")
```

### JavaScript/Frontend

```javascript
// 综合预测
const response = await fetch('/api/prediction/all', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    target_date: '2026-04-09',
    time_slot: 'evening',
    category: 'general'
  })
});

const data = await response.json();
console.log('预测 GMV:', data.data.prediction.predicted_gmv);
console.log('预测观众:', data.data.prediction.predicted_viewers);
console.log('准确度:', data.data.prediction.accuracy_score);

// 获取时间推荐
const recResponse = await fetch('/api/prediction/recommend-time');
const recData = await recResponse.json();
console.log('推荐时段:', recData.data.recommended_slot);
```

## 数据文件

- `data/prediction/historical_data.json` - 历史直播数据
- `data/prediction/model_configs.json` - 模型配置
- `data/prediction/predictions.json` - 预测记录
- `data/prediction/sample.json` - 预测样本（示例）

## 性能指标

### 预测准确度

- **优秀**: ≥90%
- **良好**: ≥80%
- **一般**: ≥70%
- **需改进**: <70%

### 数据要求

- **最低数据点**: 5 个（低于此值使用简单平均）
- **推荐数据点**: ≥30 个
- **最佳数据点**: ≥90 个（3 个月数据）

## 注意事项

1. **数据质量**: 预测准确度依赖于历史数据的质量和数量
2. **冷启动**: 新账号建议先积累 2-4 周数据再进行预测
3. **异常值**: 大促期间的数据可能影响预测，建议单独标记
4. **模型更新**: 每次评估预测准确度后，模型会自动调整权重
5. **置信区间**: 95% 置信水平，实际值有 95% 概率落在区间内

## 未来优化

- [ ] 添加更多预测模型（Prophet、LSTM 等）
- [ ] 支持自定义特征（促销活动、主播影响力等）
- [ ] 实时预测更新
- [ ] A/B 测试集成
- [ ] 预测结果可视化导出

## 相关文件

- `backend/services/prediction.py` - 预测服务核心
- `backend/routes/prediction.py` - API 路由
- `frontend/src/views/Prediction.vue` - 预测页面
- `frontend/src/components/PredictionChart.vue` - 图表组件
- `backend/tests/test_prediction.py` - 测试用例
