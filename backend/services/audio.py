"""
音频处理服务
"""
import subprocess
import tempfile
import os
from pathlib import Path
from typing import Optional, Tuple
from loguru import logger
import sys
import os as os_module

sys.path.insert(0, os_module.path.dirname(os_module.path.dirname(os_module.path.abspath(__file__))))
from config import settings


class AudioProcessor:
    """音频处理器"""
    
    def __init__(self):
        self.upload_dir = settings.upload_dir
    
    def validate_file(self, file_path: str, max_size: int = None) -> Tuple[bool, str]:
        """
        验证音频文件
        
        Args:
            file_path: 文件路径
            max_size: 最大文件大小（字节）
        
        Returns:
            (是否有效，错误消息)
        """
        if not os.path.exists(file_path):
            return False, "文件不存在"
        
        # 检查文件大小
        file_size = os.path.getsize(file_path)
        if max_size and file_size > max_size:
            return False, f"文件大小超过限制 ({max_size / 1024 / 1024:.1f}MB)"
        
        # 检查扩展名
        ext = Path(file_path).suffix.lower().lstrip('.')
        allowed = settings.allowed_extensions.split(',')
        if ext not in allowed:
            return False, f"不支持的文件格式：{ext}，支持的格式：{', '.join(allowed)}"
        
        return True, ""
    
    def get_duration(self, file_path: str) -> Optional[float]:
        """
        获取音频时长（秒）
        使用 mutagen 库读取音频时长（无需 ffmpeg）
        
        Args:
            file_path: 文件路径
        
        Returns:
            时长（秒），失败返回 None
        """
        try:
            from mutagen import File as MutagenFile
            audio = MutagenFile(file_path)
            if audio and audio.info:
                return float(audio.info.length)
        except Exception as e:
            logger.error(f"获取音频时长失败 (mutagen): {e}")
        
        # Fallback: 尝试 ffprobe
        try:
            cmd = [
                'ffprobe',
                '-v', 'error',
                '-show_entries', 'format=duration',
                '-of', 'default=noprint_wrappers=1:nokey=1',
                file_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            if result.returncode == 0:
                return float(result.stdout.strip())
        except Exception as e:
            logger.error(f"获取音频时长失败 (ffprobe): {e}")
        return None
    
    def convert_to_wav(self, input_path: str, output_path: str = None) -> Optional[str]:
        """
        转换音频为 WAV 格式（用于 Whisper API）
        注意：OpenAI Whisper API 直接支持 MP3/WAV/M4A 等格式，无需转换
        此方法保留用于后续本地 Whisper 模型
        
        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径（可选）
        
        Returns:
            输出文件路径，失败返回 None
        """
        # 直接返回原文件路径（Whisper API 支持多种格式）
        logger.info(f"跳过音频转换，直接使用原文件：{input_path}")
        return input_path
        
        # 以下代码保留用于未来需要转换时
        # if output_path is None:
        #     output_path = str(Path(input_path).with_suffix('.wav'))
        # try:
        #     cmd = [...]
        #     ...
        # except Exception as e:
        #     logger.error(f"音频转换异常：{e}")
        # return None
    
    def apply_noise_reduction(self, input_path: str, output_path: str = None) -> Optional[str]:
        """
        应用降噪处理（可选功能）
        
        Args:
            input_path: 输入文件路径
            output_path: 输出文件路径（可选）
        
        Returns:
            输出文件路径，失败返回 None
        """
        if output_path is None:
            output_path = str(Path(input_path).with_suffix('_cleaned.wav'))
        
        try:
            # 使用 ffmpeg 的音频滤镜进行简单降噪
            cmd = [
                'ffmpeg',
                '-i', input_path,
                '-af', 'afftdn=nf=-20',  # 降噪 20dB
                '-y',
                output_path
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                logger.info(f"降噪处理成功：{input_path} -> {output_path}")
                return output_path
        except Exception as e:
            logger.error(f"降噪处理异常：{e}")
        return None
    
    def cleanup(self, file_path: str):
        """清理临时文件"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"已清理临时文件：{file_path}")
        except Exception as e:
            logger.warning(f"清理文件失败：{e}")


# 全局实例
audio_processor = AudioProcessor()
