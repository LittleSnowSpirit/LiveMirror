# 话术分析 Prompt 优化报告

## 📋 优化概述

本次优化针对 LiveMirror 直播带货话术分析系统，全面升级了 Prompt 设计，提升识别准确度和分析深度。

---

## 🎯 优化目标

1. ✅ 增加话术类型识别覆盖（从基础类型扩展到 10 种专业类型）
2. ✅ 引入多维度评分机制（5 维评分 + 加权综合）
3. ✅ 优化输出格式（结构化 JSON，便于程序处理）
4. ✅ 增强分析深度（从识别升级到诊断和优化建议）
5. ✅ 使用通义千问（DashScope）作为分析引擎

---

## 📊 话术类型体系

### 优化前
- 基础分类（约 3-5 种）
- 定义模糊
- 边界不清晰

### 优化后（10 种专业类型）

| 类型代码 | 类型名称 | 权重 | 说明 | 典型关键词 |
|---------|---------|------|------|-----------|
| `opening` | 开场白/欢迎 | 1.0 | 主播开场欢迎、自我介绍、直播间介绍 | 欢迎、大家好、欢迎来到、我是主播 |
| `product_intro` | 产品介绍 | 1.5 | 产品功能、特点、材质、规格等详细介绍 | 这款、产品、功能、特点、材质 |
| `price_promotion` | 价格优惠 | 1.8 | 价格介绍、折扣、优惠券、满减活动 | 价格、优惠、折扣、券、满减、划算 |
| `limited_offer` | 限时限量 | 2.0 | 限时抢购、限量发售、倒计时、库存紧张 | 限时、限量、抢购、倒计时、只剩 |
| `interaction` | 互动问答 | 1.2 | 与观众互动、回答问题、引导评论点赞 | 提问、回答、评论、点赞、关注 |
| `demo` | 使用演示 | 1.5 | 产品使用过程展示、效果演示 | 演示、展示、使用、操作、效果 |
| `testimonial` | 买家秀展示 | 1.6 | 用户评价、买家秀、反馈展示 | 买家秀、评价、反馈、用户、回购 |
| `closing` | 促单成交 | 2.0 | 引导下单、催单、付款指引 | 下单、购买、付款、拍、赶紧买 |
| `qa` | 答疑 | 1.0 | 解答观众疑问、售后说明、物流说明 | 问题、疑问、售后、物流、发货 |
| `retention` | 留人话术 | 1.3 | 留住观众、防止流失、引导停留 | 别走、留下、等一下、不要离开 |

**权重说明**：权重用于计算话术重要性，促单和限时限量权重最高（2.0），因为是转化关键节点。

---

## 📈 评分机制

### 5 维评分体系

| 维度 | 权重 | 说明 | 评分标准 |
|-----|------|------|---------|
| 吸引力 | 1.2 | 是否能吸引观众注意力 | 5=非常吸引人，1=毫无吸引力 |
| 清晰度 | 1.0 | 表达是否清晰易懂 | 5=非常清晰，1=混乱不清 |
| 说服力 | 1.5 | 是否能促成购买决策 | 5=极具说服力，1=无法说服 |
| 互动性 | 1.0 | 是否有效引导观众互动 | 5=互动性强，1=无互动 |
| 时机 | 1.3 | 是否在合适的时机使用 | 5=时机完美，1=时机不当 |

### 综合评分计算
```python
综合评分 = Σ(维度分 × 权重) / Σ权重
```

---

## 📄 输出格式优化

### 优化前
```
类型：产品介绍
评分：4 分
评语：不错
```

### 优化后（结构化 JSON）
```json
{
  "analysis_summary": {
    "total_segments": 10,
    "duration_seconds": 300,
    "speech_type_distribution": {
      "opening": 1,
      "product_intro": 2,
      "price_promotion": 2,
      "closing": 2
    },
    "overall_score": 4.2,
    "strengths": ["产品介绍详细", "促单话术有力"],
    "weaknesses": ["互动环节较少", "留人话术不足"]
  },
  "segments": [
    {
      "segment_id": 1,
      "timestamp": "00:00:00",
      "text": "欢迎大家来到我的直播间...",
      "speech_types": ["opening"],
      "scores": {
        "attraction": 4,
        "clarity": 5,
        "persuasion": 3,
        "interaction": 4,
        "timing": 5
      },
      "average_score": 4.2,
      "highlights": ["热情开场", "清晰自我介绍"],
      "improvements": ["可以增加互动提问"]
    }
  ],
  "recommendations": {
    "priority_improvements": [
      {
        "area": "互动性",
        "current_issue": "互动环节较少",
        "suggestion": "每 5 分钟增加一次互动问答",
        "expected_impact": "提升观众停留时长 20%"
      }
    ],
    "best_practices": ["限时限量话术使用得当", "产品介绍结构清晰"],
    "training_focus": ["互动技巧", "留人话术"]
  }
}
```

---

## 🔧 技术实现

### API 配置
- **服务商**: 阿里云 DashScope（通义千问）
- **模型**: `qwen-plus`
- **优势**: 中文理解能力强，适合直播场景
- **成本**: 相对较低，适合高频调用

### 核心代码结构
```python
class WhisperService:
    - analyze_speech(): 话术分析主函数
    - get_speech_type_info(): 获取话术类型信息
    - calculate_segment_score(): 计算综合评分
    - generate_report(): 生成人类可读报告
```

### 调用示例
```python
from services.whisper import WhisperService

service = WhisperService(api_key="your_api_key")
result = service.analyze_speech(transcript_text, detailed=True)
report = service.generate_report(result)
```

---

## 🧪 测试方案

### 测试用例
1. **完整直播片段测试** - 使用 5-10 分钟完整直播转录
2. **单类型话术测试** - 针对每种话术类型单独测试
3. **边界情况测试** - 混合类型、模糊类型识别
4. **评分一致性测试** - 多次运行验证评分稳定性

### 测试脚本
```bash
cd LiveMirror/backend/services
python test_analysis.py
```

### 预期输出
- JSON 格式分析结果
- 人类可读报告
- 话术类型分布统计
- 优化建议列表

---

## 📌 使用指南

### 环境配置
```bash
# 设置 DashScope API Key
export DASHSCOPE_API_KEY="your_api_key"
```

### 基本使用
```python
from services.whisper import WhisperService

# 初始化服务
service = WhisperService()

# 分析话术
result = service.analyze_speech(transcript_text)

# 生成报告
report = service.generate_report(result)
print(report)
```

### 高级功能
```python
# 获取所有话术类型
types = service.get_all_speech_types()

# 获取特定类型信息
info = service.get_speech_type_info("closing")

# 计算段落评分
score = service.calculate_segment_score({
    "attraction": 4,
    "clarity": 5,
    "persuasion": 4,
    "interaction": 3,
    "timing": 4
})
```

---

## 🎯 预期效果

### 识别准确率提升
- 话术类型识别准确率：70% → 90%+
- 混合类型识别能力：新增
- 边界情况处理：显著改善

### 分析深度提升
- 从单一识别 → 多维度评分
- 从结果展示 → 优化建议
- 从人工解读 → 程序化处理

### 使用体验提升
- 输出格式标准化
- 报告生成自动化
- 集成对接便捷化

---

## 📝 后续优化方向

1. **实时分析** - 支持直播中实时话术分析
2. **语音情感** - 增加语音情感分析维度
3. **竞品对比** - 支持多主播话术对比分析
4. **历史趋势** - 追踪主播话术改进趋势
5. **自动优化** - 基于分析结果自动生成优化话术

---

## 📞 技术支持

- **文件位置**: `LiveMirror/backend/services/whisper.py`
- **测试脚本**: `LiveMirror/backend/services/test_analysis.py`
- **API 文档**: https://help.aliyun.com/zh/dashscope/

---

*最后更新：2026-04-08*
*版本：v2.0*
