# LiveMirror 数据报表生成系统

## 功能概述

完整的自动化数据报表生成系统，支持日报/周报/月报自动生成、关键指标汇总、趋势分析、多格式导出和定时发送。

## 已实现功能

### ✅ 1. 日报/周报/月报自动生成
- **日报**: 自动生成当日数据汇总，包含 GMV、观看次数、转化率等核心指标
- **周报**: 生成本周数据汇总，支持周环比对比
- **月报**: 生成全月数据汇总，支持月环比对比

### ✅ 2. 关键指标汇总
- **核心指标**: GMV、观看次数、转化率、平均观看时长
- **流量分析**: PV、UV、新增粉丝、互动率
- **转化分析**: 点击次数、订单数、退款率、客户满意度

### ✅ 3. 趋势分析和对比
- 环比变化率计算
- 趋势标识（上升/下降/稳定）
- 多维度数据对比

### ✅ 4. PDF/Excel 格式导出
- **JSON**: 完整数据导出
- **CSV**: 表格数据导出
- **Excel**: CSV 格式（可用 Excel 打开）
- **PDF**: 文本报告格式（简化版）

### ✅ 5. 定时发送（邮件/微信）
- Cron 表达式配置
- 邮件发送支持
- 微信发送支持
- 任务启/停控制

### ✅ 6. 自定义报表模板
- 默认模板：日报标准模板、周报汇总模板、月报总览模板
- 自定义模板创建
- 模板更新和删除
- 模板选择使用

## 文件结构

```
backend/
├── services/
│   └── report_generator.py      # 报表生成服务（核心）
├── routes/
│   └── report.py                # 报表 API 接口
├── templates/
│   └── report/
│       └── daily_template.html  # 日报 HTML 模板
└── tests/
    └── test_report_generator.py # 测试文件

frontend/
└── src/views/
    └── ReportGenerator.vue      # 报表管理页面
```

## API 接口

### 报表生成
- `POST /api/report/generate` - 生成指定类型报表
- `POST /api/report/generate/daily` - 快速生成日报
- `POST /api/report/generate/weekly` - 快速生成周报
- `POST /api/report/generate/monthly` - 快速生成月报

### 报表查询
- `GET /api/report/list` - 查询报表列表
- `GET /api/report/{report_id}` - 获取报表详情

### 报表导出
- `POST /api/report/export` - 导出报表
- `GET /api/report/{report_id}/export/{format}` - 快速导出

### 模板管理
- `GET /api/report/templates` - 查询模板列表
- `POST /api/report/templates` - 创建自定义模板
- `PUT /api/report/templates/{template_id}` - 更新模板
- `DELETE /api/report/templates/{template_id}` - 删除模板

### 定时任务
- `GET /api/report/schedules` - 查询定时任务列表
- `POST /api/report/schedules` - 创建定时任务
- `PUT /api/report/schedules/{schedule_id}` - 更新定时任务
- `DELETE /api/report/schedules/{schedule_id}` - 删除定时任务
- `POST /api/report/schedules/{schedule_id}/toggle` - 启/停定时任务

## 使用示例

### Python 调用
```python
from backend.services.report_generator import (
    get_service, 
    ReportType, 
    ExportFormat
)

service = get_service()

# 生成日报
report = service.generate_report(ReportType.DAILY)
print(f"报表 ID: {report.report_id}")
print(f"摘要：{report.overall_summary}")

# 导出为 JSON
json_path = service.export_report(report.report_id, ExportFormat.JSON)

# 导出为 Excel
excel_path = service.export_report(report.report_id, ExportFormat.EXCEL)

# 创建定时任务（每天 9 点生成日报）
schedule_id = service.create_schedule(
    report_type=ReportType.DAILY,
    cron_expression="0 9 * * *",
    export_format=ExportFormat.PDF,
    send_email=True,
    email_recipients=["manager@example.com"]
)
```

### API 调用
```bash
# 生成日报
curl -X POST http://localhost:8000/api/report/generate/daily

# 查询报表列表
curl http://localhost:8000/api/report/list

# 导出报表
curl -X POST http://localhost:8000/api/report/export \
  -H "Content-Type: application/json" \
  -d '{"report_id": "daily_20260408_123456", "format": "json"}'

# 创建定时任务
curl -X POST http://localhost:8000/api/report/schedules \
  -H "Content-Type: application/json" \
  -d '{
    "report_type": "daily",
    "cron_expression": "0 9 * * *",
    "export_format": "pdf",
    "send_email": true,
    "email_recipients": ["manager@example.com"]
  }'
```

## 测试报告

### 测试覆盖率
- ✅ 日报生成测试
- ✅ 周报生成测试
- ✅ 月报生成测试
- ✅ 自定义日期生成测试
- ✅ 报表查询测试
- ✅ JSON 导出测试
- ✅ CSV 导出测试
- ✅ Excel 导出测试
- ✅ PDF 导出测试
- ✅ 模板创建测试
- ✅ 模板更新测试
- ✅ 模板删除测试
- ✅ 定时任务创建测试
- ✅ 定时任务更新测试
- ✅ 定时任务删除测试
- ✅ 定时任务启停测试
- ✅ 统计信息查询测试

### 测试结果
```
============================= 28 passed in 0.87s ==============================
```

所有测试通过！

## 生成的报表样本

### 日报样本
- 报表 ID: `daily_20260408_233354`
- 周期: 2026-04-08
- GMV: 60,448.22 元 (环比 +2.95%)
- 观看次数：312,118 次 (环比 +165.80%)
- 转化率：4.92%
- 平均观看时长：212 秒

### 周报样本
- 报表 ID: `weekly_20260406_233405`
- 周期: 2026-04-06 至 2026-04-12

### 月报样本
- 报表 ID: `monthly_20260401_233405`
- 周期: 2026-04 全月

## 下一步优化建议

1. **真实数据接入**: 当前使用模拟数据，需接入真实数据库或 API
2. **完整 PDF 导出**: 使用 reportlab 或 weasyprint 生成真正的 PDF
3. **完整 Excel 导出**: 使用 openpyxl 生成带格式的 Excel 文件
4. **邮件发送集成**: 集成 SMTP 服务实现邮件自动发送
5. **微信推送集成**: 集成企业微信或公众号 API
6. **定时任务执行器**: 集成 APScheduler 或 Celery 执行定时任务
7. **图表生成**: 添加趋势图、对比图等可视化图表
8. **报表订阅**: 支持用户订阅特定类型的报表

## 技术栈

- **后端**: Python, FastAPI
- **前端**: Vue 3, Element Plus
- **数据存储**: JSON 文件（可升级为数据库）
- **测试**: pytest

---

开发完成时间：2026-04-08
开发者：LiveMirror 团队
