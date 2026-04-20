# LiveMirror 话术分析服务

## 📖 概述

基于通义千问（DashScope）的直播带货话术分析服务，支持 10 种话术类型识别、5 维评分机制和智能优化建议。

---

## 🚀 快速开始

### 1. 配置 API Key

```bash
# Windows PowerShell
$env:DASHSCOPE_API_KEY="your_api_key"

# Windows CMD
set DASHSCOPE_API_KEY=your_api_key

# Linux/Mac
export DASHSCOPE_API_KEY=your_api_key
```

### 2. 安装依赖

```bash
cd LiveMirror/backend
pip install -r requirements.txt
```

确保 `requirements.txt` 包含：
```
httpx
sqlalchemy
```

### 3. 运行测试

```bash
python services/test_analysis.py
```

---

## 📋 话术类型

| 代码 | 名称 | 说明 |
|-----|------|------|
| `opening` | 开场白/欢迎 | 主播开场欢迎、自我介绍 |
| `product_intro` | 产品介绍 | 产品功能、特点介绍 |
| `price_promotion` | 价格优惠 | 价格、折扣、优惠券 |
| `limited_offer` | 限时限量 | 限时抢购、库存紧张 |
| `interaction` | 互动问答 | 与观众互动、回答问题 |
| `demo` | 使用演示 | 产品使用展示 |
| `testimonial` | 买家秀展示 | 用户评价、反馈 |
| `closing` | 促单成交 | 引导下单、催单 |
| `qa` | 答疑 | 售后、物流说明 |
| `retention` | 留人话术 | 留住观众、引导停留 |

---

## 💻 使用示例

### 基本用法

```python
from services.whisper import WhisperService

# 初始化服务
service = WhisperService()

# 分析话术
transcript = """
欢迎大家来到直播间！
这款产品超级好用，原价 299，今天只要 199！
只有 50 单，赶紧下单！
"""

result = service.analyze_speech(transcript, detailed=True)

# 查看结果
print(result['analysis_summary'])
print(result['segments'])
print(result['recommendations'])
```

### 生成报告

```python
# 生成人类可读报告
report = service.generate_report(result)
print(report)
```

### 获取话术类型信息

```python
# 获取所有类型
all_types = service.get_all_speech_types()

# 获取特定类型
closing_info = service.get_speech_type_info('closing')
print(closing_info['name'])  # 促单成交
print(closing_info['description'])  # 引导下单、催单、付款指引
```

---

## 📊 输出格式

### 分析结果结构

```json
{
  "analysis_summary": {
    "total_segments": 10,
    "speech_type_distribution": {"opening": 1, "closing": 2},
    "overall_score": 4.2,
    "strengths": ["优势 1", "优势 2"],
    "weaknesses": ["不足 1", "不足 2"]
  },
  "segments": [
    {
      "segment_id": 1,
      "timestamp": "00:00:00",
      "text": "原始文本",
      "speech_types": ["opening"],
      "scores": {
        "attraction": 4,
        "clarity": 5,
        "persuasion": 3,
        "interaction": 4,
        "timing": 5
      },
      "average_score": 4.2,
      "highlights": ["亮点"],
      "improvements": ["改进建议"]
    }
  ],
  "recommendations": {
    "priority_improvements": [...],
    "best_practices": [...],
    "training_focus": [...]
  }
}
```

---

## 🧪 测试

### 运行完整测试

```bash
python services/test_analysis.py
```

测试内容包括：
- ✅ Prompt 优化对比展示
- ✅ 实际话术分析测试
- ✅ JSON 结果输出
- ✅ 人类可读报告生成

### 测试结果

测试成功后会生成：
- `test_result.json` - 详细分析结果
- 控制台输出人类可读报告

---

## 🔧 高级配置

### 自定义评分权重

```python
# 在 whisper.py 中修改 weights 字典
weights = {
    "attraction": 1.2,    # 吸引力权重
    "clarity": 1.0,       # 清晰度权重
    "persuasion": 1.5,    # 说服力权重（最高）
    "interaction": 1.0,   # 互动性权重
    "timing": 1.3         # 时机权重
}
```

### 自定义话术类型

```python
# 在 SPEECH_TYPES 字典中添加新类型
SPEECH_TYPES['new_type'] = {
    "name": "新类型名称",
    "description": "类型描述",
    "keywords": ["关键词 1", "关键词 2"],
    "weight": 1.5
}
```

### 使用精简模式

```python
# 快速分析（适合实时场景）
result = service.analyze_speech(transcript, detailed=False)
```

---

## 📝 API 参考

### WhisperService 类

| 方法 | 说明 | 参数 | 返回值 |
|-----|------|------|--------|
| `analyze_speech()` | 分析话术 | `transcript_text`, `detailed` | `Dict` 分析结果 |
| `generate_report()` | 生成报告 | `analysis_result` | `str` 报告文本 |
| `get_speech_type_info()` | 获取类型信息 | `type_code` | `Dict` 类型信息 |
| `get_all_speech_types()` | 获取所有类型 | 无 | `Dict` 类型字典 |
| `calculate_segment_score()` | 计算综合评分 | `scores` | `float` 综合分 |

---

## ❓ 常见问题

### Q: 如何获取 DashScope API Key？
A: 访问阿里云 DashScope 控制台注册并创建 API Key：https://dashscope.console.aliyun.com/

### Q: 分析结果不准确怎么办？
A: 
1. 确保转录文本质量良好
2. 尝试调整 `temperature` 参数（默认 0.3）
3. 检查话术类型关键词是否覆盖充分

### Q: 如何集成到现有系统？
A: 
1. 导入 `WhisperService` 类
2. 调用 `analyze_speech()` 方法
3. 处理返回的 JSON 结果
4. 可选：使用 `generate_report()` 生成报告

### Q: 支持实时分析吗？
A: 当前版本为离线分析。实时分析需要：
1. 使用流式转录
2. 分段调用分析接口
3. 使用 `detailed=False` 精简模式

---

## 📄 相关文档

- [Prompt 优化报告](PROMPT_OPTIMIZATION.md) - 详细的优化说明
- [测试脚本](test_analysis.py) - 测试用例和对比

---

## 📞 技术支持

- **文件位置**: `LiveMirror/backend/services/whisper.py`
- **版本**: v2.0
- **更新日期**: 2026-04-08

---

*LiveMirror - 让直播更专业*
