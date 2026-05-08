"""
LiveMirror AI 分析模块 - 主分析逻辑
整合各模块功能，提供完整的 AI 话术分析流程
"""

import json
import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import re

# 导入本地模块
from .prompts import get_prompt, SYSTEM_ROLE
from .classifiers import create_rule_analyzer, KeywordClassifier
from .suggester import create_suggester
from .report_generator import create_report_generator


class LiveMirrorAnalyzer:
    """
    LiveMirror AI 话术分析器
    
    核心功能：
    1. 话术分段
    2. 爆点识别
    3. 翻车识别
    4. 归因分析
    5. 优化建议
    6. 报告生成
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        api_base: str = "https://api.deepseek.com",
        model: str = "deepseek-chat",
        cost_optimization: bool = True
    ):
        """
        初始化分析器
        
        Args:
            api_key: DeepSeek API Key（或 GPT API Key）
            api_base: API 基础 URL
            model: 使用的模型名称
            cost_optimization: 是否启用成本优化（预筛选）
        """
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY")
        self.api_base = api_base
        self.model = model
        self.cost_optimization = cost_optimization
        
        # 初始化子模块
        self.rule_analyzer = create_rule_analyzer()
        self.suggester = create_suggester()
        self.report_generator = create_report_generator(
            model_version="v1.0",
            api_model=model
        )
        
        # 分析缓存
        self._cache = {}
    
    def analyze(
        self,
        transcript: str,
        data_changes: Optional[List[Dict[str, Any]]] = None,
        segment_duration: int = 45
    ) -> Dict[str, Any]:
        """
        完整分析流程
        
        Args:
            transcript: 直播转写稿全文
            data_changes: 数据变化点列表（可选）
            segment_duration: 分段时长（秒），默认 45 秒
        
        Returns:
            完整分析报告
        """
        # Step 1: 话术分段
        print("[Step 1] 话术分段...")
        segments = self._segment_transcript(transcript, segment_duration)
        
        # Step 2: 预筛选（成本优化）
        if self.cost_optimization:
            print("[Step 2] 预筛选段落...")
            priorities = self.rule_analyzer.pre_filter_segments(segments)
        else:
            priorities = {
                "high_priority": segments,
                "medium_priority": [],
                "low_priority": []
            }
        
        # Step 3: AI 分析高优先级段落
        print("[Step 3] AI 深度分析...")
        highlights, crashes = self._ai_analyze_segments(
            priorities["high_priority"],
            data_changes
        )
        
        # Step 4: 规则分析中低优先级段落
        print("[Step 4] 规则分析...")
        rule_highlights, rule_crashes = self._rule_analyze_segments(
            priorities["medium_priority"] + priorities["low_priority"]
        )
        
        # 合并结果
        highlights.extend(rule_highlights)
        crashes.extend(rule_crashes)
        
        # Step 5: 生成优化建议
        print("[Step 5] 生成优化建议...")
        suggestions = self._generate_suggestions(crashes)
        
        # Step 6: 归因分析
        print("[Step 6] 归因分析...")
        attributions = self._analyze_attributions(
            segments, highlights, crashes, data_changes
        )
        
        # Step 7: 生成报告
        print("[Step 7] 生成报告...")
        report = self.report_generator.generate_report(
            segments=segments,
            highlights=highlights,
            crashes=crashes,
            attributions=attributions,
            suggestions=suggestions
        )
        
        print("[完成] 分析完成！")
        return report
    
    def _segment_transcript(
        self,
        transcript: str,
        segment_duration: int = 45
    ) -> List[Dict[str, Any]]:
        """
        将转写稿分段
        
        策略：
        1. 优先按时间戳分割（如果有）
        2. 否则按字数/语义分割
        """
        segments = []
        
        # 尝试提取时间戳
        timestamp_pattern = r'(\d{2}:\d{2}:\d{2}|\d{2}:\d{2})'
        timestamps = list(re.finditer(timestamp_pattern, transcript))
        
        if timestamps:
            # 按时间戳分割
            for i, match in enumerate(timestamps):
                start_time = match.group(1)
                start_pos = match.start()
                
                # 确定结束位置
                if i + 1 < len(timestamps):
                    end_pos = timestamps[i + 1].start()
                    end_time = timestamps[i + 1].group(1)
                else:
                    end_pos = len(transcript)
                    end_time = self._add_seconds_to_time(start_time, segment_duration)
                
                content = transcript[start_pos:end_pos].strip()
                # 移除时间戳本身
                content = re.sub(timestamp_pattern, '', content).strip()
                
                if len(content) > 20:  # 过滤太短的段落
                    segments.append({
                        "segment_id": i + 1,
                        "start_time": start_time,
                        "end_time": end_time,
                        "content": content,
                        "word_count": len(content),
                        "speech_type": "待分析",
                        "is_highlight": False,
                        "is_crash": False
                    })
        else:
            # 按字数分割（假设约 200 字/45 秒）
            words_per_segment = 200
            total_words = len(transcript)
            
            segment_id = 1
            for i in range(0, total_words, words_per_segment):
                content = transcript[i:i + words_per_segment].strip()
                start_time = self._seconds_to_time((segment_id - 1) * segment_duration)
                end_time = self._seconds_to_time(segment_id * segment_duration)
                
                if len(content) > 20:
                    segments.append({
                        "segment_id": segment_id,
                        "start_time": start_time,
                        "end_time": end_time,
                        "content": content,
                        "word_count": len(content),
                        "speech_type": "待分析",
                        "is_highlight": False,
                        "is_crash": False
                    })
                    segment_id += 1
        
        return segments
    
    def _ai_analyze_segments(
        self,
        segments: List[Dict[str, Any]],
        data_changes: Optional[List[Dict[str, Any]]] = None
    ) -> Tuple[List[Dict], List[Dict]]:
        """
        使用 AI 分析段落
        
        Returns:
            (highlights, crashes) 元组
        """
        if not segments:
            return [], []
        
        highlights = []
        crashes = []
        
        # 批量处理（减少 API 调用）
        # 每 5 个段落调用一次 API
        batch_size = 5
        for i in range(0, len(segments), batch_size):
            batch = segments[i:i + batch_size]
            batch_text = "\n\n---\n\n".join([
                f"[段落{seg['segment_id']}] {seg['content']}"
                for seg in batch
            ])
            
            try:
                # 调用 AI API
                result = self._call_ai_api(batch_text, data_changes)
                
                if result:
                    # 解析结果
                    batch_highlights = result.get("highlights", [])
                    batch_crashes = result.get("crashes", [])
                    
                    # 更新段落标记
                    for h in batch_highlights:
                        seg_id = h.get("segment_id")
                        for seg in segments:
                            if seg["segment_id"] == seg_id:
                                seg["is_highlight"] = True
                                break
                    
                    for c in batch_crashes:
                        seg_id = c.get("segment_id")
                        for seg in segments:
                            if seg["segment_id"] == seg_id:
                                seg["is_crash"] = True
                                break
                    
                    highlights.extend(batch_highlights)
                    crashes.extend(batch_crashes)
                    
            except Exception as e:
                print(f"[警告] AI 分析批次 {i//batch_size + 1} 失败：{e}")
                # 降级到规则分析
                rule_h, rule_c = self._rule_analyze_segments(batch)
                highlights.extend(rule_h)
                crashes.extend(rule_c)
        
        return highlights, crashes
    
    def _call_ai_api(
        self,
        text: str,
        data_changes: Optional[List[Dict[str, Any]]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        调用 AI API 进行分析
        
        支持 DeepSeek 和 GPT
        """
        if not self.api_key:
            print("[警告] 未配置 API Key，使用规则分析降级")
            return None
        
        # 构建 Prompt
        data_changes_str = json.dumps(data_changes, ensure_ascii=False) if data_changes else "无"
        
        prompt = get_prompt(
            "full_analysis",
            transcript=text,
            data_changes=data_changes_str
        )
        
        try:
            # 尝试使用 DeepSeek API
            if "deepseek" in self.model.lower():
                result = self._call_deepseek_api(prompt)
            else:
                result = self._call_gpt_api(prompt)
            
            return result
            
        except Exception as e:
            print(f"API 调用失败：{e}")
            return None
    
    def _call_deepseek_api(self, prompt: str) -> Optional[Dict[str, Any]]:
        """调用 DeepSeek API"""
        try:
            import httpx

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": SYSTEM_ROLE},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "response_format": {"type": "json_object"}
            }

            response = httpx.post(
                f"{self.api_base}/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )

            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                return json.loads(content)
            else:
                print(f"DeepSeek API 错误：{response.status_code}")
                return None

        except ImportError:
            print("[警告] 未安装 httpx 库，使用规则分析")
            return None
    
    def _call_gpt_api(self, prompt: str) -> Optional[Dict[str, Any]]:
        """调用 GPT API"""
        try:
            import httpx

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }

            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": SYSTEM_ROLE},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.3,
                "response_format": {"type": "json_object"}
            }

            response = httpx.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                return json.loads(content)
            else:
                print(f"GPT API 错误：{response.status_code}")
                return None
                
        except ImportError:
            print("[警告] 未安装 requests 库，使用规则分析")
            return None
    
    def _rule_analyze_segments(
        self,
        segments: List[Dict[str, Any]]
    ) -> Tuple[List[Dict], List[Dict]]:
        """使用规则分析段落"""
        highlights = []
        crashes = []
        
        for segment in segments:
            content = segment["content"]
            result = self.rule_analyzer.quick_classify(content)
            
            # 如果是潜在爆点
            if result["is_potential_highlight"]:
                highlights.append({
                    "segment_id": segment["segment_id"],
                    "timestamp": segment["start_time"],
                    "type": result["speech_types"][0] if result["speech_types"] else "其他",
                    "original_text": content[:100] + "..." if len(content) > 100 else content,
                    "effectiveness_score": 6,
                    "analysis": "基于关键词规则识别"
                })
            
            # 如果是潜在翻车点
            if result["is_potential_crash"]:
                crashes.append({
                    "segment_id": segment["segment_id"],
                    "timestamp": segment["start_time"],
                    "type": result["crash_types"][0] if result["crash_types"] else "其他",
                    "severity": "medium",
                    "original_text": content[:100] + "..." if len(content) > 100 else content,
                    "problem": "基于关键词规则识别",
                    "risk_level": result["risk_level"]
                })
        
        return highlights, crashes
    
    def _generate_suggestions(
        self,
        crashes: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """生成优化建议"""
        suggestions = self.suggester.generate_batch_suggestions(crashes)
        return [self.suggester.to_dict(s) for s in suggestions]
    
    def _analyze_attributions(
        self,
        segments: List[Dict[str, Any]],
        highlights: List[Dict[str, Any]],
        crashes: List[Dict[str, Any]],
        data_changes: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """归因分析"""
        if not data_changes:
            return []
        
        attributions = []
        
        for change in data_changes:
            change_time = change.get("timestamp", "")
            change_type = change.get("type", "")  # 爆单/掉粉等
            
            # 查找时间相近的话术
            related_speech = None
            speech_type = None
            
            # 检查爆点
            for h in highlights:
                if self._time_close(h["timestamp"], change_time, tolerance=30):
                    related_speech = h["original_text"]
                    speech_type = "爆点"
                    break
            
            # 检查翻车点
            if not related_speech:
                for c in crashes:
                    if self._time_close(c["timestamp"], change_time, tolerance=30):
                        related_speech = c["original_text"]
                        speech_type = "翻车点"
                        break
            
            if related_speech:
                attributions.append({
                    "data_change_type": change_type,
                    "timestamp": change_time,
                    "related_speech": related_speech[:100],
                    "speech_type": speech_type,
                    "confidence": 0.75,
                    "reasoning": f"时间关联：话术发生在数据变化前后 30 秒内"
                })
        
        return attributions
    
    def _time_close(
        self,
        time1: str,
        time2: str,
        tolerance: int = 30
    ) -> bool:
        """判断两个时间是否接近（秒）"""
        try:
            seconds1 = self._time_to_seconds(time1)
            seconds2 = self._time_to_seconds(time2)
            return abs(seconds1 - seconds2) <= tolerance
        except:
            return False
    
    def _time_to_seconds(self, time_str: str) -> int:
        """时间字符串转秒数"""
        parts = time_str.split(":")
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        elif len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        return 0
    
    def _seconds_to_time(self, seconds: int) -> str:
        """秒数转时间字符串"""
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        return f"{h:02d}:{m:02d}:{s:02d}"
    
    def _add_seconds_to_time(self, time_str: str, seconds: int) -> str:
        """给时间字符串增加秒数"""
        total_seconds = self._time_to_seconds(time_str) + seconds
        return self._seconds_to_time(total_seconds)
    
    def save_report(self, report: Dict[str, Any], filepath: str) -> None:
        """保存报告到文件"""
        self.report_generator.save_report(report, filepath)
    
    def get_executive_summary(self, report: Dict[str, Any]) -> str:
        """获取执行摘要"""
        return self.report_generator.generate_executive_summary(report)


def create_analyzer(
    api_key: Optional[str] = None,
    model: str = "deepseek-chat",
    cost_optimization: bool = True
) -> LiveMirrorAnalyzer:
    """工厂函数：创建分析器实例"""
    return LiveMirrorAnalyzer(
        api_key=api_key,
        model=model,
        cost_optimization=cost_optimization
    )


# 便捷函数
def analyze_transcript(
    transcript: str,
    api_key: Optional[str] = None,
    model: str = "deepseek-chat"
) -> Dict[str, Any]:
    """
    便捷函数：一键分析转写稿
    
    Args:
        transcript: 直播转写稿
        api_key: API Key
        model: 模型名称
    
    Returns:
        分析报告
    """
    analyzer = create_analyzer(api_key=api_key, model=model)
    return analyzer.analyze(transcript)


if __name__ == "__main__":
    # 测试代码
    test_transcript = """
    00:00:00 大家好，欢迎来到直播间！今天给大家带来一款超级好用的产品。
    00:00:30 这款产品我自己也在用，效果真的非常好，原价 299，今天只要 99！
    00:01:00 想要的宝宝赶紧扣 1，库存不多了，只剩最后 50 单！
    00:01:30 我们家的产品是全网第一的，绝对有效，保证让你满意！
    00:02:00 别家都是假的，只有我们是正品，他们家质量太差了。
    00:02:30 好了，喜欢的可以直接拍，倒计时 3 分钟！
    """
    
    # 创建分析器（需要配置 API Key）
    # analyzer = create_analyzer(api_key="your_api_key")
    # report = analyzer.analyze(test_transcript)
    # print(json.dumps(report, ensure_ascii=False, indent=2))
    
    print("LiveMirror AI 分析模块已就绪")
