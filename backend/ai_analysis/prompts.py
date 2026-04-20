"""
LiveMirror AI 分析模块 - Prompt 模板库
提供直播话术分析的各种 Prompt 模板
"""

# 系统角色定义
SYSTEM_ROLE = """你是一位资深直播运营专家，拥有 5 年直播带货数据分析经验。
你擅长识别主播话术中的关键模式，包括促单技巧、互动策略、产品介绍方法，
以及可能导致翻车的敏感表述。

你的任务是分析直播转写稿，找出"爆点"（高转化话术）和"翻车点"（负面话术），
并给出专业的优化建议。"""

# 话术分段 Prompt
SEGMENTATION_PROMPT = """
请将以下直播转写稿按语义和时间逻辑分成若干段落，每段约 30-60 秒。

要求：
1. 每段包含完整的话术意图（如一个产品介绍、一次促单、一段互动等）
2. 标注每段的开始和结束时间戳
3. 输出严格的 JSON 格式

转写稿：
{transcript}

输出格式：
{{
  "segments": [
    {{
      "segment_id": 1,
      "start_time": "00:00:00",
      "end_time": "00:00:45",
      "content": "段落内容...",
      "word_count": 150
    }}
  ]
}}
"""

# 爆点识别 Prompt
HIGHLIGHT_DETECTION_PROMPT = """
分析以下直播话术段落，识别其中的"爆点"（高转化话术特征）。

爆点特征包括但不限于：
- 限时优惠/紧迫感营造（"只剩最后 X 单"、"倒计时"）
- 价格锚点/对比（"原价 XXX，今天只要 XXX"）
- 促单话术（"想要的扣 1"、"赶紧下单"）
- 信任背书（"我自己也在用"、"销量已破 X 万"）
- 痛点打击（"是不是经常遇到 XXX 问题"）
- 稀缺性营造（"限量"、"绝版"、"独家"）
- 互动引导（"点赞到 X 万抽奖"、"评论扣 XXX"）

请逐段分析，输出严格的 JSON 格式。

话术段落：
{segments}

输出格式：
{{
  "highlights": [
    {{
      "segment_id": 1,
      "timestamp": "00:00:30",
      "type": "限时优惠|价格锚点|促单话术|信任背书|痛点打击|稀缺性营造|互动引导",
      "original_text": "原文内容",
      "effectiveness_score": 8,
      "analysis": "为什么这是爆点的分析"
    }}
  ]
}}
"""

# 翻车识别 Prompt
CRASH_DETECTION_PROMPT = """
分析以下直播话术段落，识别其中的"翻车点"（负面话术/风险表述）。

翻车特征包括但不限于：
- 敏感词/违规词（"最"、"第一"、"绝对"等广告法禁用词）
- 错误表述（产品信息错误、价格说错）
- 冷场/尴尬（长时间停顿、无人互动）
- 负面情绪（抱怨、急躁、不耐烦）
- 争议言论（政治、敏感话题）
- 过度承诺（"保证有效"、"100% 见效"）
- 贬低竞品（直接攻击其他品牌）
- 口误/结巴（明显的话术失误）

请逐段分析，输出严格的 JSON 格式。

话术段落：
{segments}

输出格式：
{{
  "crashes": [
    {{
      "segment_id": 1,
      "timestamp": "00:01:15",
      "type": "敏感词|错误表述|冷场|负面情绪|争议言论|过度承诺|贬低竞品|口误",
      "severity": "low|medium|high|critical",
      "original_text": "原文内容",
      "problem": "具体问题描述",
      "risk_level": 7
    }}
  ]
}}
"""

# 归因分析 Prompt
ATTRIBUTION_PROMPT = """
基于以下直播话术分析结果和假设的数据变化点，进行归因分析。

数据变化点（假设）：
{data_changes}

话术分析结果：
{analysis_results}

请分析：
1. 哪些话术可能导致了数据峰值（爆单/涨粉）
2. 哪些话术可能导致了数据谷值（掉粉/流失）
3. 话术与数据变化的时间关联性

输出严格的 JSON 格式：
{{
  "attributions": [
    {{
      "data_change_type": "爆单|掉粉|涨粉|流失",
      "timestamp": "00:05:30",
      "related_speech": "相关话术",
      "speech_type": "爆点|翻车点",
      "confidence": 0.85,
      "reasoning": "归因推理过程"
    }}
  ]
}}
"""

# 优化建议 Prompt
SUGGESTION_PROMPT = """
针对以下翻车话术，给出专业的优化改写建议。

翻车话术列表：
{crashes}

要求：
1. 保持原意但规避风险
2. 符合广告法和平台规范
3. 保持话术的自然流畅
4. 给出多个改写方案供选择

输出严格的 JSON 格式：
{{
  "suggestions": [
    {{
      "segment_id": 1,
      "original_text": "原文",
      "problem_type": "问题类型",
      "suggestions": [
        {{
          "version": "A",
          "rewritten_text": "改写版本 A",
          "improvement": "改进说明"
        }},
        {{
          "version": "B",
          "rewritten_text": "改写版本 B",
          "improvement": "改进说明"
        }}
      ]
    }}
  ]
}}
"""

# 综合分析报告 Prompt
FULL_ANALYSIS_PROMPT = """
你是一位资深直播运营专家。请对以下直播转写稿进行全面分析。

直播转写稿：
{transcript}

请完成以下分析任务：
1. 话术分段（每段 30-60 秒）
2. 识别爆点（高转化话术）
3. 识别翻车点（负面话术）
4. 归因分析（关联假设的数据变化）
5. 给出优化建议

数据变化参考（可选）：
{data_changes}

输出严格的 JSON 格式，确保可以直接被程序解析：
{{
  "metadata": {{
    "analysis_time": "2024-01-01T12:00:00Z",
    "total_duration": "01:30:00",
    "total_segments": 45,
    "model_version": "v1.0"
  }},
  "segments": [
    {{
      "segment_id": 1,
      "start_time": "00:00:00",
      "end_time": "00:00:45",
      "content": "内容",
      "word_count": 150,
      "speech_type": "产品介绍|促单|互动|闲聊|其他",
      "is_highlight": false,
      "is_crash": false
    }}
  ],
  "highlights": [
    {{
      "segment_id": 1,
      "timestamp": "00:00:30",
      "type": "类型",
      "original_text": "原文",
      "effectiveness_score": 8,
      "analysis": "分析"
    }}
  ],
  "crashes": [
    {{
      "segment_id": 2,
      "timestamp": "00:01:15",
      "type": "类型",
      "severity": "low|medium|high|critical",
      "original_text": "原文",
      "problem": "问题",
      "risk_level": 7
    }}
  ],
  "attributions": [
    {{
      "data_change_type": "类型",
      "timestamp": "00:05:30",
      "related_speech": "话术",
      "speech_type": "爆点 | 翻车点",
      "confidence": 0.85,
      "reasoning": "推理"
    }}
  ],
  "suggestions": [
    {{
      "segment_id": 2,
      "original_text": "原文",
      "problem_type": "问题类型",
      "suggestions": [
        {{
          "version": "A",
          "rewritten_text": "改写",
          "improvement": "说明"
        }}
      ]
    }}
  ],
  "summary": {{
    "total_highlights": 10,
    "total_crashes": 5,
    "critical_crashes": 1,
    "overall_score": 75,
    "key_insights": ["关键洞察 1", "关键洞察 2"]
  }}
}}
"""


def get_prompt(template_name: str, **kwargs) -> str:
    """
    获取指定模板的 Prompt，并填充变量
    
    Args:
        template_name: 模板名称
        **kwargs: 模板变量
    
    Returns:
        填充后的 Prompt
    """
    templates = {
        "segmentation": SEGMENTATION_PROMPT,
        "highlight_detection": HIGHLIGHT_DETECTION_PROMPT,
        "crash_detection": CRASH_DETECTION_PROMPT,
        "attribution": ATTRIBUTION_PROMPT,
        "suggestion": SUGGESTION_PROMPT,
        "full_analysis": FULL_ANALYSIS_PROMPT,
    }
    
    template = templates.get(template_name)
    if not template:
        raise ValueError(f"Unknown template: {template_name}")
    
    return template.format(**kwargs)
