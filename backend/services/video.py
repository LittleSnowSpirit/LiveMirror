"""
LiveMirror 视频处理服务
支持视频上传、音频提取、转写分析
"""

import os
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Optional, Dict, Tuple
from dataclasses import dataclass
from datetime import datetime
import json


@dataclass
class VideoInfo:
    """视频信息数据类"""
    filename: str
    file_size: int  # bytes
    duration: float  # seconds
    format: str  # mp4, avi, mov, mkv
    width: int
    height: int
    video_codec: str
    audio_codec: str
    has_audio: bool


@dataclass
class VideoProcessResult:
    """视频处理结果"""
    success: bool
    video_info: Optional[VideoInfo]
    audio_path: Optional[str]
    error_message: Optional[str]
    processing_time: float


class VideoService:
    """
    视频处理服务
    使用 ffmpeg 提取音频
    """
    
    # 支持的视频格式
    SUPPORTED_FORMATS = ['mp4', 'avi', 'mov', 'mkv']
    
    # 最大文件大小：2GB
    MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2GB
    
    def __init__(self, temp_dir: str = None):
        """
        初始化视频服务
        
        Args:
            temp_dir: 临时文件目录
        """
        self.temp_dir = temp_dir or tempfile.gettempdir()
        self._ffmpeg_checked = False
        self._ffmpeg_available = None
    
    def _ensure_ffmpeg_available(self):
        """检查 ffmpeg 是否可用（延迟检查）"""
        if self._ffmpeg_checked:
            return self._ffmpeg_available
        
        try:
            result = subprocess.run(
                ['ffmpeg', '-version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                self._ffmpeg_available = False
                print("[WARNING] ffmpeg 未安装或不可用")
            else:
                self._ffmpeg_available = True
                print(f"[FFMPEG] 已就绪：{result.stdout.splitlines()[0]}")
        except FileNotFoundError:
            self._ffmpeg_available = False
            print("[WARNING] ffmpeg 未安装，视频处理功能将不可用")
        except subprocess.TimeoutExpired:
            self._ffmpeg_available = False
            print("[WARNING] ffmpeg 检查超时")
        
        self._ffmpeg_checked = True
        return self._ffmpeg_available
    
    def get_video_info(self, video_path: str) -> VideoInfo:
        """
        获取视频文件信息
        
        Args:
            video_path: 视频文件路径
        
        Returns:
            VideoInfo 视频信息
        """
        self._ensure_ffmpeg_available()
        if not self._ffmpeg_available:
            raise RuntimeError("ffmpeg 未安装，无法处理视频")
        
        video_path = Path(video_path)
        
        if not video_path.exists():
            raise FileNotFoundError(f"视频文件不存在：{video_path}")
        
        # 使用 ffprobe 获取视频信息
        cmd = [
            'ffprobe',
            '-v', 'quiet',
            '-print_format', 'json',
            '-show_format',
            '-show_streams',
            str(video_path)
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode != 0:
            raise RuntimeError(f"ffprobe 执行失败：{result.stderr}")
        
        info = json.loads(result.stdout)
        
        # 解析视频流信息
        video_stream = None
        audio_stream = None
        
        for stream in info.get('streams', []):
            if stream.get('codec_type') == 'video' and video_stream is None:
                video_stream = stream
            elif stream.get('codec_type') == 'audio' and audio_stream is None:
                audio_stream = stream
        
        if not video_stream:
            raise RuntimeError("视频文件中未找到视频流")
        
        format_info = info.get('format', {})
        file_size = int(format_info.get('size', 0))
        duration = float(format_info.get('duration', 0))
        
        return VideoInfo(
            filename=video_path.name,
            file_size=file_size,
            duration=duration,
            format=video_path.suffix.lower().lstrip('.'),
            width=video_stream.get('width', 0),
            height=video_stream.get('height', 0),
            video_codec=video_stream.get('codec_name', 'unknown'),
            audio_codec=audio_stream.get('codec_name', 'none') if audio_stream else 'none',
            has_audio=audio_stream is not None
        )
    
    def extract_audio(
        self,
        video_path: str,
        output_path: str = None,
        audio_format: str = 'wav',
        sample_rate: int = 16000,
        channels: int = 1
    ) -> str:
        """
        从视频中提取音频
        
        Args:
            video_path: 视频文件路径
            output_path: 输出音频路径（可选，默认在临时目录）
            audio_format: 输出音频格式（wav, mp3, m4a）
            sample_rate: 采样率（默认 16000，适合 Whisper）
            channels: 声道数（默认 1，单声道）
        
        Returns:
            str 输出音频文件路径
        """
        video_path = Path(video_path)
        
        if not video_path.exists():
            raise FileNotFoundError(f"视频文件不存在：{video_path}")
        
        # 确定输出路径
        if output_path is None:
            # 在临时目录创建音频文件
            temp_subdir = Path(self.temp_dir) / "livemirror_video"
            temp_subdir.mkdir(parents=True, exist_ok=True)
            output_path = temp_subdir / f"{video_path.stem}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{audio_format}"
        else:
            output_path = Path(output_path)
            # 确保输出目录存在
            output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 构建 ffmpeg 命令
        cmd = [
            'ffmpeg',
            '-i', str(video_path),
            '-vn',  # 不要视频
            '-acodec', 'pcm_s16le' if audio_format == 'wav' else 'libmp3lame',
            '-ar', str(sample_rate),
            '-ac', str(channels),
            '-y',  # 覆盖输出文件
            str(output_path)
        ]
        
        print(f"[EXTRACT] 开始从 {video_path.name} 提取音频...")
        print(f"[EXTRACT] 输出：{output_path.name}, 采样率：{sample_rate}Hz, 声道：{channels}")
        
        start_time = datetime.now()
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 分钟超时
            )
            
            if result.returncode != 0:
                raise RuntimeError(f"ffmpeg 提取失败：{result.stderr}")
            
            elapsed = (datetime.now() - start_time).total_seconds()
            print(f"[EXTRACT] 音频提取完成，耗时 {elapsed:.2f}s")
            
            return str(output_path)
            
        except subprocess.TimeoutExpired:
            raise RuntimeError("音频提取超时（超过 5 分钟）")
    
    def validate_video(self, video_path: str) -> Tuple[bool, Optional[str]]:
        """
        验证视频文件
        
        Args:
            video_path: 视频文件路径
        
        Returns:
            Tuple[bool, Optional[str]] (是否有效，错误消息)
        """
        video_path = Path(video_path)
        
        # 检查文件是否存在
        if not video_path.exists():
            return False, "文件不存在"
        
        # 检查文件大小
        file_size = video_path.stat().st_size
        if file_size > self.MAX_FILE_SIZE:
            return False, f"文件大小超过限制 2GB（当前：{file_size / (1024*1024*1024):.2f}GB）"
        
        # 检查文件格式
        format = video_path.suffix.lower().lstrip('.')
        if format not in self.SUPPORTED_FORMATS:
            return False, f"不支持的视频格式：{format}（支持：{', '.join(self.SUPPORTED_FORMATS)}）"
        
        # 检查是否为有效视频文件
        try:
            info = self.get_video_info(str(video_path))
            if not info.has_audio:
                return False, "视频文件不包含音频轨道"
        except Exception as e:
            return False, f"视频文件损坏或无法读取：{str(e)}"
        
        return True, None
    
    def process_video(
        self,
        video_path: str,
        extract_audio: bool = True,
        cleanup_video: bool = False
    ) -> VideoProcessResult:
        """
        处理视频文件
        
        Args:
            video_path: 视频文件路径
            extract_audio: 是否提取音频
            cleanup_video: 是否清理原视频文件
        
        Returns:
            VideoProcessResult 处理结果
        """
        start_time = datetime.now()
        
        try:
            # 验证视频
            is_valid, error = self.validate_video(video_path)
            if not is_valid:
                return VideoProcessResult(
                    success=False,
                    video_info=None,
                    audio_path=None,
                    error_message=error,
                    processing_time=0
                )
            
            # 获取视频信息
            video_info = self.get_video_info(video_path)
            
            # 提取音频
            audio_path = None
            if extract_audio and video_info.has_audio:
                audio_path = self.extract_audio(video_path)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return VideoProcessResult(
                success=True,
                video_info=video_info,
                audio_path=audio_path,
                error_message=None,
                processing_time=processing_time
            )
            
        except Exception as e:
            processing_time = (datetime.now() - start_time).total_seconds()
            return VideoProcessResult(
                success=False,
                video_info=None,
                audio_path=None,
                error_message=str(e),
                processing_time=processing_time
            )
    
    def cleanup_temp_files(self):
        """清理临时文件"""
        temp_subdir = Path(self.temp_dir) / "livemirror_video"
        if temp_subdir.exists():
            try:
                shutil.rmtree(temp_subdir)
                print(f"[CLEANUP] 已清理临时目录：{temp_subdir}")
            except Exception as e:
                print(f"[CLEANUP] 清理失败：{e}")


# 全局服务实例（单例模式）
_service_instance: Optional[VideoService] = None


def get_service() -> VideoService:
    """获取全局视频服务实例"""
    global _service_instance
    if _service_instance is None:
        _service_instance = VideoService()
    return _service_instance


def process_video_file(
    video_path: str,
    extract_audio: bool = True
) -> VideoProcessResult:
    """
    便捷函数：处理视频文件
    
    Args:
        video_path: 视频文件路径
        extract_audio: 是否提取音频
    
    Returns:
        VideoProcessResult 处理结果
    """
    service = get_service()
    return service.process_video(video_path, extract_audio)


if __name__ == "__main__":
    # 测试服务
    import sys
    
    print("="*60)
    print("视频处理服务测试")
    print("="*60)
    
    # 检查 ffmpeg
    try:
        service = get_service()
        print("✓ ffmpeg 检查通过")
    except RuntimeError as e:
        print(f"✗ ffmpeg 检查失败：{e}")
        sys.exit(1)
    
    # 测试视频文件
    if len(sys.argv) > 1:
        video_file = sys.argv[1]
    else:
        print("\n请提供测试视频文件路径")
        print("用法：python video.py <video_path>")
        sys.exit(0)
    
    print(f"\n测试视频：{video_file}")
    
    # 验证视频
    is_valid, error = service.validate_video(video_file)
    if not is_valid:
        print(f"✗ 视频验证失败：{error}")
        sys.exit(1)
    
    print("✓ 视频验证通过")
    
    # 获取视频信息
    info = service.get_video_info(video_file)
    print(f"\n视频信息:")
    print(f"  文件名：{info.filename}")
    print(f"  大小：{info.file_size / (1024*1024):.2f} MB")
    print(f"  时长：{info.duration:.2f}s")
    print(f"  格式：{info.format}")
    print(f"  分辨率：{info.width}x{info.height}")
    print(f"  视频编码：{info.video_codec}")
    print(f"  音频编码：{info.audio_codec}")
    print(f"  有音频：{info.has_audio}")
    
    # 提取音频
    if info.has_audio:
        print("\n开始提取音频...")
        audio_path = service.extract_audio(video_file)
        print(f"✓ 音频已提取到：{audio_path}")
        
        # 验证提取的音频
        if Path(audio_path).exists():
            audio_size = Path(audio_path).stat().st_size
            print(f"  音频大小：{audio_size / (1024*1024):.2f} MB")
    
    # 显示性能统计
    print("\n处理完成！")
