"""
LiveMirror AI 分析模块 - 使用示例

演示如何使用 AI 分析模块进行直播话术分析
"""

import json
from analyzer import create_analyzer, analyze_transcript


def example_basic_usage():
    """基础使用示例"""
    print("=" * 60)
    print("示例 1: 基础使用（便捷函数）")
    print("=" * 60)
    
    transcript = """
    00:00:00 大家好，欢迎来到直播间！
    00:00:30 今天给大家带来一款超级好用的产品，原价 299，今天只要 99！
    00:01:00 想要的宝宝赶紧扣 1，库存不多了！
    00:01:30 我们家的产品是全网第一的，绝对有效！
    """
    
    # 使用便捷函数（无 API Key 时自动降级到规则分析）
    report = analyze_transcript(
        transcript=transcript,
        api_key=None,  # 替换为你的 API Key
        model="deepseek-chat"
    )
    
    print(f"综合得分：{report['summary']['overall_score']}/100")
    print(f"爆点数量：{report['summary']['total_highlights']}")
    print(f"翻车数量：{report['summary']['total_crashes']}")
    print(f"关键洞察：{report['summary']['key_insights']}")
    print()


def example_advanced_usage():
    """高级使用示例"""
    print("=" * 60)
    print("示例 2: 高级使用（自定义配置）")
    print("=" * 60)
    
    transcript = """
    00:00:00 哈喽大家好，欢迎来到直播间！
    00:00:30 先给大家介绍一下今天的主打产品...
    00:01:00 原价是 399 元，但是今天在直播间，只要 199！
    00:01:30 想要的宝宝赶紧扣 1！
    00:02:00 这款精华液是全网销量第一的，绝对有效！
    00:02:30 别家那些都是假货，只有我们这里是正品！
    00:03:00 库存真的不多了，只剩 80 单了！
    00:03:30 倒计时 5 分钟，5 分钟后恢复原价！
    """
    
    # 数据变化点（可选）
    data_changes = [
        {
            "timestamp": "00:01:30",
            "type": "涨粉",
            "value": "+150",
            "description": "互动引导后粉丝增长"
        },
        {
            "timestamp": "00:03:00",
            "type": "爆单",
            "value": "+80",
            "description": "稀缺性营造后订单激增"
        }
    ]
    
    # 创建分析器实例
    analyzer = create_analyzer(
        api_key=None,  # 替换为你的 API Key
        model="deepseek-chat",
        cost_optimization=True  # 启用成本优化
    )
    
    # 执行分析
    report = analyzer.analyze(
        transcript=transcript,
        data_changes=data_changes,
        segment_duration=45  # 每 45 秒一段
    )
    
    # 保存报告
    analyzer.save_report(report, "analysis_report.json")
    print("报告已保存至：analysis_report.json")
    
    # 获取执行摘要
    summary = analyzer.get_executive_summary(report)
    print("\n执行摘要：")
    print(summary)
    print()


def example_api_integration():
    """API 集成示例（FastAPI）"""
    print("=" * 60)
    print("示例 3: API 集成（FastAPI 示例代码）")
    print("=" * 60)
    
    code = '''
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict
from ai_analysis import create_analyzer

app = FastAPI()

# 初始化分析器
analyzer = create_analyzer(
    api_key="your_api_key",
    model="deepseek-chat"
)

class AnalysisRequest(BaseModel):
    transcript: str
    data_changes: Optional[List[Dict]] = None

class AnalysisResponse(BaseModel):
    success: bool
    report: Dict
    message: str

@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_transcript_endpoint(request: AnalysisRequest):
    try:
        report = analyzer.analyze(
            transcript=request.transcript,
            data_changes=request.data_changes
        )
        return {
            "success": True,
            "report": report,
            "message": "分析成功"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "ok"}
'''
    
    print(code)
    print()


def example_report_structure():
    """报告结构示例"""
    print("=" * 60)
    print("示例 4: 报告结构说明")
    print("=" * 60)
    
    structure = {
        "metadata": {
            "analysis_time": "2024-01-01T12:00:00Z",
            "total_duration": "01:30:00",
            "total_segments": 45,
            "model_version": "v1.0",
            "api_model": "deepseek-chat"
        },
        "segments": [
            {
                "segment_id": 1,
                "start_time": "00:00:00",
                "end_time": "00:00:45",
                "content": "段落内容",
                "word_count": 150,
                "speech_type": "产品介绍",
                "is_highlight": False,
                "is_crash": False
            }
        ],
        "highlights": [
            {
                "segment_id": 2,
                "timestamp": "00:01:00",
                "type": "促单话术",
                "original_text": "原文",
                "effectiveness_score": 8,
                "analysis": "分析说明"
            }
        ],
        "crashes": [
            {
                "segment_id": 3,
                "timestamp": "00:02:00",
                "type": "敏感词",
                "severity": "high",
                "original_text": "原文",
                "problem": "问题描述",
                "risk_level": 8
            }
        ],
        "suggestions": [
            {
                "segment_id": 3,
                "original_text": "原文",
                "problem_type": "敏感词",
                "suggestions": [
                    {
                        "version": "A",
                        "rewritten_text": "改写版本 A",
                        "improvement": "改进说明"
                    }
                ]
            }
        ],
        "summary": {
            "total_highlights": 10,
            "total_crashes": 5,
            "critical_crashes": 1,
            "overall_score": 75,
            "key_insights": ["洞察 1", "洞察 2"]
        }
    }
    
    print(json.dumps(structure, ensure_ascii=False, indent=2))
    print()


if __name__ == "__main__":
    print("\n")
    print("*" * 60)
    print("LiveMirror AI 分析模块 - 使用示例")
    print("*" * 60)
    print("\n")
    
    # 运行示例
    example_basic_usage()
    example_advanced_usage()
    example_api_integration()
    example_report_structure()
    
    print("\n")
    print("=" * 60)
    print("所有示例运行完成！")
    print("=" * 60)
    print("\n")
