# LiveMirror AI 分析模块

AI 驱动的直播话术分析系统，识别"爆点"和"翻车点"。

## 功能特性

- ✅ **话术分段**：自动将转写稿按时间/语义分段（30-60 秒/段）
- ✅ **爆点识别**：识别高转化话术（促单、限时、优惠等）
- ✅ **翻车识别**：识别负面话术（敏感词、错误表述、冷场等）
- ✅ **归因分析**：关联话术与数据变化（掉粉/爆单时刻）
- ✅ **优化建议**：针对翻车话术给出改写方案
- ✅ **成本优化**：预筛选机制减少 API 调用
- ✅ **JSON 输出**：结构化报告，便于前端渲染

## 项目结构

```
ai_analysis/
├── __init__.py          # 包初始化
├── analyzer.py          # 主分析逻辑
├── prompts.py           # Prompt 模板库
├── classifiers.py       # 话术分类器
├── suggester.py         # 优化建议生成
├── report_generator.py  # 报告生成器
├── test_analyzer.py     # 测试用例
└── README.md            # 本文档
```

## 快速开始

### 1. 安装依赖

```bash
pip install requests
```

### 2. 配置 API Key

```bash
# 方式 1：环境变量
export DEEPSEEK_API_KEY=your_api_key

# 方式 2：代码中配置
analyzer = create_analyzer(api_key="your_api_key")
```

### 3. 使用示例

```python
from ai_analysis import create_analyzer, analyze_transcript

# 方式 1：便捷函数
report = analyze_transcript(
    transcript="直播转写稿内容...",
    api_key="your_api_key"
)

# 方式 2：创建分析器实例
analyzer = create_analyzer(
    api_key="your_api_key",
    model="deepseek-chat",  # 或 "gpt-4"
    cost_optimization=True  # 启用成本优化
)

report = analyzer.analyze(
    transcript="直播转写稿内容...",
    data_changes=[  # 可选：数据变化点
        {
            "timestamp": "00:05:30",
            "type": "爆单",
            "value": "+200"
        }
    ]
)

# 保存报告
analyzer.save_report(report, "analysis_report.json")

# 获取执行摘要
summary = analyzer.get_executive_summary(report)
print(summary)
```

## API 参考

### LiveMirrorAnalyzer

主分析器类。

#### 初始化参数

- `api_key` (str, optional): DeepSeek 或 GPT API Key
- `api_base` (str): API 基础 URL，默认 `"https://api.deepseek.com"`
- `model` (str): 模型名称，默认 `"deepseek-chat"`
- `cost_optimization` (bool): 是否启用成本优化，默认 `True`

#### 主要方法

```python
# 完整分析
analyze(
    transcript: str,
    data_changes: Optional[List[Dict]],
    segment_duration: int = 45
) -> Dict[str, Any]

# 保存报告
save_report(report: Dict[str, Any], filepath: str) -> None

# 获取执行摘要
get_executive_summary(report: Dict[str, Any]) -> str
```

### 报告结构

```json
{
  "metadata": {
    "analysis_time": "2024-01-01T12:00:00Z",
    "total_duration": "01:30:00",
    "total_segments": 45,
    "model_version": "v1.0",
    "api_model": "deepseek-chat"
  },
  "segments": [...],
  "highlights": [...],
  "crashes": [...],
  "attributions": [...],
  "suggestions": [...],
  "summary": {
    "total_highlights": 10,
    "total_crashes": 5,
    "critical_crashes": 1,
    "overall_score": 75,
    "key_insights": ["洞察 1", "洞察 2"]
  }
}
```

## 话术类型

### 爆点类型

| 类型 | 说明 | 示例关键词 |
|------|------|-----------|
| 促单话术 | 催促下单 | "赶紧拍"、"手慢无" |
| 价格锚点 | 价格对比 | "原价 XXX"、"今天只要" |
| 信任背书 | 建立信任 | "我自己也在用"、"销量" |
| 痛点打击 | 戳中痛点 | "是不是经常"、"困扰" |
| 稀缺性营造 | 制造稀缺 | "限量"、"只剩" |
| 互动引导 | 引导互动 | "扣 1"、"点赞" |

### 翻车类型

| 类型 | 说明 | 示例关键词 |
|------|------|-----------|
| 敏感词 | 广告法禁用词 | "最"、"第一"、"绝对" |
| 过度承诺 | 承诺过强 | "保证有效"、"100%" |
| 贬低竞品 | 攻击竞品 | "他家不行"、"垃圾" |
| 负面情绪 | 情绪失控 | "烦死了"、"爱买不买" |
| 错误表述 | 信息错误 | 产品参数错误 |
| 冷场 | 互动缺失 | 长时间停顿 |

## 成本优化策略

启用 `cost_optimization=True` 时：

1. **预筛选**：基于关键词规则快速分类段落
2. **分级处理**：
   - 高优先级（含爆点/翻车关键词）→ AI 深度分析
   - 中优先级（较长段落）→ AI 简化分析
   - 低优先级（短文本）→ 仅规则分类
3. **批量处理**：每 5 个段落合并为一次 API 调用

**效果**：可减少 60-80% 的 API 调用次数

## 运行测试

```bash
cd ai_analysis
python test_analyzer.py
```

测试将验证：
- ✅ 关键词分类器
- ✅ 规则分析器
- ✅ 优化建议生成器
- ✅ 报告生成器
- ✅ 完整分析流程

## 集成到后端 API

```python
# backend/api/routes/analysis.py
from fastapi import APIRouter, HTTPException
from ai_analysis import create_analyzer

router = APIRouter()
analyzer = create_analyzer(api_key=os.getenv("DEEPSEEK_API_KEY"))

@router.post("/analyze")
async def analyze_transcript_endpoint(
    transcript: str,
    data_changes: Optional[List[Dict]] = None
):
    try:
        report = analyzer.analyze(transcript, data_changes)
        return {"success": True, "report": report}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

## 注意事项

1. **API 成本**：建议启用成本优化模式
2. **中文语境**：已针对中文直播优化（口语化、梗、术语）
3. **输出格式**：严格 JSON，便于前端解析
4. **错误处理**：API 失败时自动降级到规则分析

## 扩展开发

### 添加新的话术类型

编辑 `classifiers.py`：

```python
class SpeechType(Enum):
    NEW_TYPE = "新类型"

HIGHLIGHT_KEYWORDS = {
    SpeechType.NEW_TYPE: ["关键词 1", "关键词 2"]
}
```

### 添加新的 Prompt 模板

编辑 `prompts.py`：

```python
NEW_PROMPT = """
你的 Prompt 模板
{variable}
"""
```

### 自定义评分算法

编辑 `report_generator.py`：

```python
def _calculate_overall_score(self, highlights, crashes, critical):
    # 自定义评分逻辑
    pass
```

## 许可证

MIT License

## 联系方式

LiveMirror Team
