"""
LiveMirror 话术分析服务
使用通义千问（DashScope）进行直播话术识别与分析
"""
import os
import json
import httpx
from typing import Optional, Dict, Any, List
from datetime import datetime

# DashScope API 配置
DASHSCOPE_API_KEY = os.getenv("DASHSCOPE_API_KEY", "")
DASHSCOPE_API_URL = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"

# 话术类型定义
SPEECH_TYPES = {
    "opening": {
        "name": "开场白/欢迎",
        "description": "主播开场欢迎、自我介绍、直播间介绍",
        "keywords": ["欢迎", "大家好", "欢迎来到", "我是主播", "今天", "开场"],
        "weight": 1.0
    },
    "product_intro": {
        "name": "产品介绍",
        "description": "产品功能、特点、材质、规格等详细介绍",
        "keywords": ["这款", "产品", "功能", "特点", "材质", "规格", "介绍", "详细"],
        "weight": 1.5
    },
    "price_promotion": {
        "name": "价格优惠",
        "description": "价格介绍、折扣、优惠券、满减活动",
        "keywords": ["价格", "优惠", "折扣", "券", "满减", "便宜", "划算", "到手价"],
        "weight": 1.8
    },
    "limited_offer": {
        "name": "限时限量",
        "description": "限时抢购、限量发售、倒计时、库存紧张",
        "keywords": ["限时", "限量", "抢购", "倒计时", "库存", "只剩", "最后", "赶紧"],
        "weight": 2.0
    },
    "interaction": {
        "name": "互动问答",
        "description": "与观众互动、回答问题、引导评论点赞",
        "keywords": ["提问", "回答", "评论", "点赞", "关注", "互动", "有没有", "想要"],
        "weight": 1.2
    },
    "demo": {
        "name": "使用演示",
        "description": "产品使用过程展示、效果演示",
        "keywords": ["演示", "展示", "使用", "操作", "效果", "试一下", "看一下"],
        "weight": 1.5
    },
    "testimonial": {
        "name": "买家秀展示",
        "description": "用户评价、买家秀、反馈展示",
        "keywords": ["买家秀", "评价", "反馈", "用户", "回购", "好评", "晒图"],
        "weight": 1.6
    },
    "closing": {
        "name": "促单成交",
        "description": "引导下单、催单、付款指引",
        "keywords": ["下单", "购买", "付款", "成交", "拍", "去拍", "赶紧买", "不要犹豫"],
        "weight": 2.0
    },
    "qa": {
        "name": "答疑",
        "description": "解答观众疑问、售后说明、物流说明",
        "keywords": ["问题", "疑问", "售后", "物流", "发货", "退换", "解答"],
        "weight": 1.0
    },
    "retention": {
        "name": "留人话术",
        "description": "留住观众、防止流失、引导停留",
        "keywords": ["别走", "留下", "等一下", "马上", "精彩", "不要离开", "继续看"],
        "weight": 1.3
    }
}

# 话术分析 Prompt 模板
ANALYSIS_PROMPT_TEMPLATE = """
# 直播带货话术分析任务

## 任务描述
你是一名专业的直播带货话术分析师。请分析以下直播转录文本，识别其中的话术类型、质量，并给出优化建议。

## 话术类型定义
请根据以下类型进行分类：

| 类型代码 | 类型名称 | 说明 |
|---------|---------|------|
| opening | 开场白/欢迎 | 主播开场欢迎、自我介绍、直播间介绍 |
| product_intro | 产品介绍 | 产品功能、特点、材质、规格等详细介绍 |
| price_promotion | 价格优惠 | 价格介绍、折扣、优惠券、满减活动 |
| limited_offer | 限时限量 | 限时抢购、限量发售、倒计时、库存紧张 |
| interaction | 互动问答 | 与观众互动、回答问题、引导评论点赞 |
| demo | 使用演示 | 产品使用过程展示、效果演示 |
| testimonial | 买家秀展示 | 用户评价、买家秀、反馈展示 |
| closing | 促单成交 | 引导下单、催单、付款指引 |
| qa | 答疑 | 解答观众疑问、售后说明、物流说明 |
| retention | 留人话术 | 留住观众、防止流失、引导停留 |

## 评分标准
对每段话术进行以下维度评分（1-5 分）：

1. **吸引力**：是否能吸引观众注意力
2. **清晰度**：表达是否清晰易懂
3. **说服力**：是否能促成购买决策
4. **互动性**：是否有效引导观众互动
5. **时机**：是否在合适的时机使用

## 分析要求
1. 逐段识别话术类型（允许一段话包含多个类型）
2. 对每段话术进行多维度评分
3. 识别优秀话术和需要改进的话术
4. 提供具体的优化建议
5. 统计各类型话术的分布比例

## 输出格式
请严格按照以下 JSON 格式输出（不要输出其他内容）：

```json
{
  "analysis_summary": {
    "total_segments": 整数，总段数，
    "duration_seconds": 整数，总时长（秒）,
    "speech_type_distribution": {
      "类型代码": 出现次数
    },
    "overall_score": 数字，整体评分（1-5）,
    "strengths": ["优势 1", "优势 2"],
    "weaknesses": ["不足 1", "不足 2"]
  },
  "segments": [
    {
      "segment_id": 整数，
      "timestamp": "时间戳",
      "text": "原始文本",
      "speech_types": ["类型代码 1", "类型代码 2"],
      "scores": {
        "attraction": 整数 1-5,
        "clarity": 整数 1-5,
        "persuasion": 整数 1-5,
        "interaction": 整数 1-5,
        "timing": 整数 1-5
      },
      "average_score": 数字，平均分,
      "highlights": ["亮点 1", "亮点 2"],
      "improvements": ["改进建议 1", "改进建议 2"]
    }
  ],
  "recommendations": {
    "priority_improvements": [
      {
        "area": "改进领域",
        "current_issue": "当前问题",
        "suggestion": "具体建议",
        "expected_impact": "预期效果"
      }
    ],
    "best_practices": ["最佳实践 1", "最佳实践 2"],
    "training_focus": ["培训重点 1", "培训重点 2"]
  }
}
```

## 待分析文本
{transcript_text}

## 分析开始
请严格按照上述 JSON 格式输出分析结果，不要包含任何额外说明。
"""

# 精简版分析 Prompt（用于快速分析）
QUICK_ANALYSIS_PROMPT = """
# 直播话术快速分析

分析以下直播文本，识别话术类型并评分。

话术类型：opening(开场白), product_intro(产品介绍), price_promotion(价格优惠), limited_offer(限时限量), interaction(互动), demo(演示), testimonial(买家秀), closing(促单), qa(答疑), retention(留人)

输出 JSON 格式：
{
  "segments": [
    {
      "text": "文本内容",
      "type": "主要类型代码",
      "score": 1-5,
      "note": "简短评语"
    }
  ],
  "summary": {
    "top_type": "最常见类型",
    "avg_score": 平均分,
    "suggestion": "一句话建议"
  }
}

文本：{transcript_text}
"""


class WhisperService:
    """话术分析服务"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or DASHSCOPE_API_KEY
        if not self.api_key:
            raise ValueError("DashScope API Key 未配置，请设置 DASHSCOPE_API_KEY 环境变量")
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def analyze_speech(
        self, 
        transcript_text: str, 
        detailed: bool = True
    ) -> Dict[str, Any]:
        """
        分析直播话术
        
        Args:
            transcript_text: 直播转录文本
            detailed: 是否进行详细分析（默认 True）
        
        Returns:
            分析结果字典
        """
        prompt = ANALYSIS_PROMPT_TEMPLATE.format(
            transcript_text=transcript_text
        ) if detailed else QUICK_ANALYSIS_PROMPT.format(
            transcript_text=transcript_text
        )
        
        payload = {
            "model": "qwen-plus",
            "input": {
                "messages": [
                    {
                        "role": "system",
                        "content": "你是专业的直播带货话术分析师，擅长识别话术类型、评估话术质量、提供优化建议。请严格按照 JSON 格式输出。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            },
            "parameters": {
                "result_format": "message",
                "temperature": 0.3,
                "max_tokens": 4000
            }
        }
        
        try:
            response = httpx.post(
                DASHSCOPE_API_URL,
                headers=self.headers,
                json=payload,
                timeout=60.0
            )
            response.raise_for_status()
            result = response.json()
            
            # 解析响应
            if "output" in result and "choices" in result["output"]:
                content = result["output"]["choices"][0]["message"]["content"]
                # 清理可能的 markdown 代码块标记
                content = self._clean_json_response(content)
                return json.loads(content)
            else:
                raise ValueError(f"DashScope 响应格式异常：{result}")
                
        except httpx.HTTPError as e:
            raise RuntimeError(f"DashScope API 请求失败：{str(e)}")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"分析结果 JSON 解析失败：{str(e)}")
    
    def _clean_json_response(self, content: str) -> str:
        """清理 JSON 响应，移除 markdown 代码块标记"""
        content = content.strip()
        # 移除 ```json 和 ``` 标记
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        return content.strip()
    
    def get_speech_type_info(self, type_code: str) -> Optional[Dict[str, Any]]:
        """获取话术类型详细信息"""
        return SPEECH_TYPES.get(type_code)
    
    def get_all_speech_types(self) -> Dict[str, Dict[str, Any]]:
        """获取所有话术类型定义"""
        return SPEECH_TYPES.copy()
    
    def calculate_segment_score(self, scores: Dict[str, int]) -> float:
        """计算段落综合评分"""
        if not scores:
            return 0.0
        weights = {
            "attraction": 1.2,
            "clarity": 1.0,
            "persuasion": 1.5,
            "interaction": 1.0,
            "timing": 1.3
        }
        total_weight = sum(weights.values())
        weighted_sum = sum(scores.get(k, 0) * v for k, v in weights.items())
        return round(weighted_sum / total_weight, 2)
    
    def generate_report(self, analysis_result: Dict[str, Any]) -> str:
        """生成人类可读的分析报告"""
        summary = analysis_result.get("analysis_summary", {})
        segments = analysis_result.get("segments", [])
        recommendations = analysis_result.get("recommendations", {})
        
        report_lines = [
            "=" * 60,
            "📊 直播话术分析报告",
            "=" * 60,
            "",
            "📈 总体概览",
            f"   总段落数：{summary.get('total_segments', 0)}",
            f"   整体评分：{summary.get('overall_score', 0):.1f}/5.0",
            "",
            "📋 话术类型分布",
        ]
        
        for type_code, count in summary.get("speech_type_distribution", {}).items():
            type_info = self.get_speech_type_info(type_code)
            type_name = type_info["name"] if type_info else type_code
            report_lines.append(f"   {type_name}: {count}次")
        
        report_lines.extend([
            "",
            "✅ 优势",
        ])
        for strength in summary.get("strengths", []):
            report_lines.append(f"   • {strength}")
        
        report_lines.extend([
            "",
            "⚠️ 不足",
        ])
        for weakness in summary.get("weaknesses", []):
            report_lines.append(f"   • {weakness}")
        
        report_lines.extend([
            "",
            "💡 优化建议",
        ])
        for rec in recommendations.get("priority_improvements", []):
            report_lines.append(f"   • {rec.get('area', '')}: {rec.get('suggestion', '')}")
        
        report_lines.extend([
            "",
            "=" * 60,
        ])
        
        return "\n".join(report_lines)


# 测试函数
def test_analysis():
    """测试话术分析功能"""
    # 示例直播文本
    test_transcript = """
    欢迎大家来到我的直播间！我是你们的主播小美，今天给大家带来一款超级好用的产品。
    
    这款面霜是韩国进口的，含有玻尿酸和烟酰胺成分，深层补水保湿，美白淡斑效果非常好。
    
    原价 299 元，今天直播间专属价只要 199 元！还送价值 99 元的面膜一盒！
    
    只有 50 单库存，倒计时 3 分钟！抢完就没有了，赶紧下单！
    
    有宝宝问敏感肌能用吗？可以的，这款是温和配方，敏感肌也适用哦！
    
    来，我给大家演示一下质地，看，很水润，一抹就开，吸收特别快。
    
    看一下买家秀，这位小姐姐用了两周，皮肤明显变白了，她自己都说效果太好了！
    
    不要犹豫了，最后 10 单！拍完下架！1、2、3，上链接！
    
    下单的宝宝记得关注直播间，明天还有更多福利！
    """
    
    service = WhisperService()
    result = service.analyze_speech(test_transcript, detailed=True)
    
    print("分析结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    print("\n" + service.generate_report(result))
    
    return result


if __name__ == "__main__":
    # 运行测试
    test_analysis()
