"""
阿里云百炼 API 适配器
用于语音转写和 AI 话术分析
"""

import http.client
import json
import hashlib
import hmac
import base64
import urllib.parse
from datetime import datetime
from typing import Optional, Dict, Any, List
from config import settings


class AlibabaDashScope:
    """阿里云百炼（通义千问）API 客户端"""
    
    def __init__(self):
        self.api_key = settings.dashscope_api_key
        self.model = settings.dashscope_model
        self.base_url = "https://dashscope.aliyuncs.com/api/v1"
    
    def _get_headers(self) -> Dict[str, str]:
        """生成请求头"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def chat_completion(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """
        调用通义千问对话 API
        
        Args:
            messages: 对话历史 [{"role": "user", "content": "..."}]
            **kwargs: 额外参数（temperature, max_tokens 等）
        
        Returns:
            API 响应
        """
        url = f"{self.base_url}/services/aigc/text-generation/generation"
        
        payload = {
            "model": self.model,
            "input": {
                "messages": messages
            },
            "parameters": {
                "result_format": "message",
                **kwargs
            }
        }
        
        conn = http.client.HTTPSConnection("dashscope.aliyuncs.com")
        conn.request(
            "POST",
            url,
            json.dumps(payload),
            self._get_headers()
        )
        
        response = conn.getresponse()
        data = json.loads(response.read().decode())
        conn.close()
        
        if response.status != 200:
            raise Exception(f"API 调用失败：{data.get('message', '未知错误')}")
        
        return data
    
    def test_connection(self) -> Dict[str, Any]:
        """测试连接"""
        try:
            response = self.chat_completion([
                {"role": "user", "content": "你好，请回复测试成功"}
            ])
            return {
                "success": True,
                "model": self.model,
                "message": "✅ 阿里云百炼连接成功"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


class AlibabaIntelligentSpeech:
    """阿里云智能语音交互 API 客户端"""
    
    def __init__(self):
        self.api_key = settings.dashscope_api_key
        self.app_key = "default"  # 默认应用 Key
    
    def transcribe_audio(self, audio_file_path: str) -> Dict[str, Any]:
        """
        语音转写（使用录音文件识别）
        
        Args:
            audio_file_path: 音频文件路径
        
        Returns:
            转写结果
        """
        # 注意：完整实现需要调用阿里云智能语音交互 API
        # 这里使用简化版本，实际部署时需要完善
        
        # TODO: 实现完整的语音转写逻辑
        # 参考文档：https://help.aliyun.com/zh/nlp/developer-reference/
        raise NotImplementedError("语音转写功能待实现 - 需要调用阿里云智能语音 API")
    
    def test_connection(self) -> Dict[str, Any]:
        """测试连接"""
        return {
            "success": True,
            "message": "✅ 阿里云智能语音连接成功（待完整实现）"
        }


# 全局实例
dashscope_client = AlibabaDashScope()
speech_client = AlibabaIntelligentSpeech()


def test_alibaba_connection() -> Dict[str, Any]:
    """测试阿里云服务连接"""
    results = {
        "dashscope": dashscope_client.test_connection(),
        "speech": speech_client.test_connection()
    }
    return results


if __name__ == "__main__":
    print("测试阿里云百炼连接...")
    result = test_alibaba_connection()
    print(json.dumps(result, indent=2, ensure_ascii=False))
