"""
阿里云 DashScope 语音识别服务
使用 Paraformer 进行语音转写

文档：https://help.aliyun.com/zh/dashscope/developer-reference/paraformer
"""

import httpx
import time
import hashlib
import hmac
import base64
import json
from pathlib import Path
from typing import Optional, Dict, Any
from loguru import logger


class DashScopeASR:
    """DashScope 语音识别服务"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://dashscope.aliyuncs.com"
        self.timeout = 300  # 5 分钟超时
    
    async def transcribe(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        语音转写
        
        流程：
        1. 上传文件到 DashScope OSS
        2. 提交转写任务
        3. 轮询获取结果
        
        Args:
            file_path: 音频文件路径
        
        Returns:
            转写结果，失败返回 None
        """
        try:
            # 步骤 1: 上传文件获取 URL
            logger.info(f"[DashScope] 上传文件：{file_path}")
            file_url = await self._upload_file(file_path)
            
            if not file_url:
                logger.error("[DashScope] 文件上传失败")
                return None
            
            # 步骤 2: 提交转写任务
            logger.info(f"[DashScope] 提交转写任务：{file_url}")
            task_id = await self._submit_task(file_url)
            
            if not task_id:
                logger.error("[DashScope] 任务提交失败")
                return None
            
            # 步骤 3: 轮询结果
            logger.info(f"[DashScope] 轮询任务结果：{task_id}")
            result = await self._poll_result(task_id)
            
            if result:
                logger.info(f"[DashScope] 转写成功")
                return {
                    'text': result.get('text', ''),
                    'segments': result.get('sentences', []),
                    'duration': result.get('duration', 0),
                    'language': 'zh'
                }
            else:
                logger.error("[DashScope] 转写失败")
                return None
                
        except Exception as e:
            logger.error(f"[DashScope] 转写异常：{e}")
            return None
    
    async def _upload_file(self, file_path: str) -> Optional[str]:
        """上传文件到 DashScope OSS"""
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                url = f"{self.base_url}/api/v1/uploads"
                
                headers = {
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                }
                
                # 请求上传 URL
                payload = {
                    'resource_type': 'audio',
                    'file_name': Path(file_path).name,
                    'file_size': Path(file_path).stat().st_size
                }
                
                response = await client.post(url, headers=headers, json=payload)
                
                if response.status_code != 200:
                    logger.error(f"上传请求失败：{response.text}")
                    return None
                
                upload_info = response.json()
                upload_url = upload_info.get('upload_url')
                file_url = upload_info.get('file_url')
                
                # 上传文件
                with open(file_path, 'rb') as f:
                    upload_response = await client.put(
                        upload_url,
                        content=f.read(),
                        headers={'Content-Type': 'audio/mpeg'}
                    )
                
                if upload_response.status_code == 200:
                    logger.info(f"文件上传成功：{file_url}")
                    return file_url
                else:
                    logger.error(f"文件上传失败：{upload_response.status_code}")
                    return None
                    
        except Exception as e:
            logger.error(f"上传异常：{e}")
            return None
    
    async def _submit_task(self, file_url: str) -> Optional[str]:
        """提交转写任务"""
        try:
            async with httpx.AsyncClient(timeout=60) as client:
                url = f"{self.base_url}/api/v1/services/aigc/audio-transcription/transcription"
                
                headers = {
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                }
                
                payload = {
                    'model': 'paraformer-realtime-v2',
                    'input': {
                        'file_url': file_url
                    },
                    'parameters': {
                        'language': 'zh'
                    }
                }
                
                response = await client.post(url, headers=headers, json=payload)
                
                if response.status_code == 200:
                    result = response.json()
                    task_id = result.get('output', {}).get('task_id')
                    logger.info(f"任务提交成功：{task_id}")
                    return task_id
                else:
                    logger.error(f"任务提交失败：{response.text}")
                    return None
                    
        except Exception as e:
            logger.error(f"提交异常：{e}")
            return None
    
    async def _poll_result(self, task_id: str, max_attempts: int = 60) -> Optional[Dict[str, Any]]:
        """轮询任务结果"""
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                for i in range(max_attempts):
                    url = f"{self.base_url}/api/v1/tasks/{task_id}"
                    
                    headers = {
                        'Authorization': f'Bearer {self.api_key}'
                    }
                    
                    response = await client.get(url, headers=headers)
                    
                    if response.status_code == 200:
                        result = response.json()
                        status = result.get('output', {}).get('status')
                        
                        logger.info(f"任务状态：{status} ({i+1}/{max_attempts})")
                        
                        if status == 'SUCCEEDED':
                            return result.get('output', {})
                        elif status == 'FAILED':
                            logger.error(f"任务失败：{result.get('message', '')}")
                            return None
                        elif status in ('PENDING', 'RUNNING'):
                            await asyncio.sleep(5)
                            continue
                        else:
                            logger.warning(f"未知状态：{status}")
                            await asyncio.sleep(5)
                    else:
                        logger.error(f"查询失败：{response.text}")
                        await asyncio.sleep(5)
                
                logger.error("轮询超时")
                return None
                
        except Exception as e:
            logger.error(f"轮询异常：{e}")
            return None


# 需要导入 asyncio
import asyncio


# 全局实例（延迟初始化）
_asr_service = None

def get_asr_service(api_key: str) -> DashScopeASR:
    """获取 ASR 服务实例"""
    global _asr_service
    if _asr_service is None:
        _asr_service = DashScopeASR(api_key)
    return _asr_service
