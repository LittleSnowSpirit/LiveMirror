"""
本地 Whisper 语音转写服务
使用 faster-whisper 进行本地转写
"""

from pathlib import Path
from typing import Optional, Dict, Any, List
from loguru import logger
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class LocalWhisperService:
    """本地 Whisper 转写服务"""
    
    def __init__(self, model_size: str = "base"):
        """
        初始化 Whisper 服务
        
        Args:
            model_size: 模型大小 (tiny, base, small, medium, large-v2)
                       - tiny: 最快，准确度较低
                       - base: 平衡速度和准确度（推荐）
                       - small: 更准确，较慢
                       - medium/large: 最准确，很慢
        """
        self.model_size = model_size
        self.model = None
        logger.info(f"LocalWhisperService 初始化，模型：{model_size}")
    
    def _load_model(self):
        """懒加载模型"""
        if self.model is None:
            try:
                from faster_whisper import WhisperModel
                logger.info(f"加载 Whisper 模型：{self.model_size}")
                
                # 使用 CPU 运行（如果有 GPU 可以改为 "cuda"）
                self.model = WhisperModel(
                    self.model_size,
                    device="cpu",
                    compute_type="int8"  # 量化加速
                )
                logger.info(f"Whisper 模型加载完成")
            except ImportError:
                logger.error("faster-whisper 未安装，运行：pip install faster-whisper")
                return None
            except Exception as e:
                logger.error(f"模型加载失败：{e}")
                return None
        
        return self.model
    
    async def transcribe(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        转写音频文件
        
        Args:
            file_path: 音频文件路径
        
        Returns:
            转写结果字典，包含 text, segments, duration, language
            失败返回 None
        """
        try:
            # 在线程池中运行（避免阻塞事件循环）
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self._transcribe_sync,
                file_path
            )
            return result
        except Exception as e:
            logger.error(f"Whisper 转写异常：{e}")
            return None
    
    def _transcribe_sync(self, file_path: str) -> Optional[Dict[str, Any]]:
        """同步转写（在线程池中运行）"""
        model = self._load_model()
        if not model:
            return None
        
        try:
            logger.info(f"开始转写：{file_path}")
            
            # 执行转写
            segments, info = model.transcribe(
                file_path,
                language="zh",  # 中文
                vad_filter=True,  # 语音活动检测
                vad_parameters=dict(
                    threshold=0.5,
                    min_speech_duration_ms=500,
                    min_silence_duration_ms=200
                )
            )
            
            logger.info(f"检测语言：{info.language} (置信度：{info.language_probability:.2f})")
            
            # 处理结果
            text_parts = []
            segment_list = []
            
            for segment in segments:
                text_parts.append(segment.text)
                segment_list.append({
                    'start': segment.start,
                    'end': segment.end,
                    'text': segment.text.strip()
                })
            
            full_text = ''.join(text_parts)
            
            logger.info(f"转写完成，{len(full_text)} 字符，{len(segment_list)} 段")
            
            return {
                'text': full_text,
                'segments': segment_list,
                'duration': info.duration,
                'language': info.language
            }
            
        except Exception as e:
            logger.error(f"转写失败：{e}")
            return None


# 全局实例（延迟初始化）
_whisper_service = None

def get_whisper_service(model_size: str = "base") -> LocalWhisperService:
    """获取 Whisper 服务实例"""
    global _whisper_service
    if _whisper_service is None:
        _whisper_service = LocalWhisperService(model_size)
    return _whisper_service
