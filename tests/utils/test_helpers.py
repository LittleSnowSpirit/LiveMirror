"""
测试辅助工具
提供通用的测试辅助函数
"""
import asyncio
import time
from typing import Optional, Dict, Any, Callable
from pathlib import Path
import httpx


async def poll_until(
    condition: Callable[[], Any],
    timeout: int = 30,
    interval: float = 1.0,
    description: str = "条件"
) -> Any:
    """
    轮询直到条件满足
    
    Args:
        condition: 返回真值的条件函数
        timeout: 超时时间（秒）
        interval: 轮询间隔（秒）
        description: 条件描述（用于错误信息）
    
    Returns:
        条件函数的返回值
    
    Raises:
        TimeoutError: 超时未满足条件
    """
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        result = condition()
        if result:
            return result
        
        await asyncio.sleep(interval)
    
    raise TimeoutError(f"等待超时：{description} 在 {timeout} 秒内未满足")


async def wait_for_task_completion(
    client: httpx.AsyncClient,
    task_id: str,
    timeout: int = 300,
    interval: int = 2
) -> Dict[str, Any]:
    """
    等待任务完成
    
    Args:
        client: HTTP 客户端
        task_id: 任务 ID
        timeout: 超时时间（秒）
        interval: 轮询间隔（秒）
    
    Returns:
        任务最终状态
    
    Raises:
        TimeoutError: 任务超时未完成
    """
    async def check_task():
        response = await client.get(f"/api/task/{task_id}")
        if response.status_code == 200:
            data = response.json()
            status = data.get("task", {}).get("status", "")
            if status in ["completed", "failed"]:
                return data
        return None
    
    result = await poll_until(
        check_task,
        timeout=timeout,
        interval=interval,
        description=f"任务 {task_id} 完成"
    )
    
    return result


def create_test_audio_file(
    output_path: Path,
    duration_seconds: float = 1.0,
    sample_rate: int = 8000,
    format: str = "wav"
) -> Path:
    """
    创建测试音频文件
    
    Args:
        output_path: 输出文件路径
        duration_seconds: 音频时长（秒）
        sample_rate: 采样率
        format: 文件格式
    
    Returns:
        生成的文件路径
    """
    if format == "wav":
        return create_wav_file(output_path, duration_seconds, sample_rate)
    elif format == "mp3":
        return create_mp3_file(output_path, duration_seconds)
    else:
        raise ValueError(f"不支持的格式：{format}")


def create_wav_file(
    output_path: Path,
    duration_seconds: float = 1.0,
    sample_rate: int = 8000
) -> Path:
    """
    创建 WAV 文件（静音）
    
    Args:
        output_path: 输出文件路径
        duration_seconds: 音频时长（秒）
        sample_rate: 采样率
    
    Returns:
        生成的文件路径
    """
    import wave
    import struct
    
    num_samples = int(duration_seconds * sample_rate)
    
    with wave.open(str(output_path), "w") as wav_file:
        wav_file.setnchannels(1)  # 单声道
        wav_file.setsampwidth(1)  # 8-bit
        wav_file.setframerate(sample_rate)
        
        # 写入静音数据（8-bit 中间值）
        for _ in range(num_samples):
            wav_file.writeframes(struct.pack("B", 128))
    
    return output_path


def create_mp3_file(
    output_path: Path,
    duration_seconds: float = 1.0
) -> Path:
    """
    创建模拟 MP3 文件
    
    注意：这不是真正的 MP3 文件，只是用于测试文件上传
    """
    # 简单的 ID3 标签 + 一些数据
    with open(output_path, "wb") as f:
        # ID3 标签头
        f.write(b"ID3\x04\x00\x00\x00\x00\x00\x00")
        
        # 模拟帧数据
        frame_size = 417  # 典型 MP3 帧大小
        num_frames = int(duration_seconds * 38)  # 约 38 帧/秒
        
        for _ in range(num_frames):
            # 模拟 MP3 帧头
            f.write(b"\xff\xfb\x90\x00")
            f.write(bytes([0x00] * (frame_size - 4)))
    
    return output_path


def get_file_size_mb(file_path: Path) -> float:
    """获取文件大小（MB）"""
    return file_path.stat().st_size / 1024 / 1024


def format_duration(seconds: float) -> str:
    """格式化时长显示"""
    mins = int(seconds // 60)
    secs = int(seconds % 60)
    return f"{mins}:{secs:02d}"


class TestContext:
    """
    测试上下文管理器
    
    用于管理测试资源和状态
    """
    __test__ = False  # 避免 pytest 收集此类
    
    def __init__(self):
        self.task_ids = []
        self.files = []
        self.errors = []
    
    def add_task(self, task_id: str):
        """添加任务 ID 到清理列表"""
        self.task_ids.append(task_id)
    
    def add_file(self, file_path: Path):
        """添加文件到清理列表"""
        self.files.append(file_path)
    
    def add_error(self, error: str):
        """记录错误"""
        self.errors.append(error)
    
    def cleanup(self):
        """清理所有资源"""
        # 清理文件
        for file_path in self.files:
            try:
                if file_path.exists():
                    file_path.unlink()
            except Exception as e:
                print(f"清理文件失败 {file_path}: {e}")
        
        # 重置状态
        self.task_ids.clear()
        self.files.clear()
        self.errors.clear()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.cleanup()


def assert_response_schema(
    response_data: Dict[str, Any],
    required_fields: list,
    field_types: Optional[Dict[str, type]] = None
):
    """
    验证响应数据结构
    
    Args:
        response_data: 响应数据
        required_fields: 必需字段列表
        field_types: 字段类型字典（可选）
    
    Raises:
        AssertionError: 验证失败
    """
    # 检查必需字段
    for field in required_fields:
        assert field in response_data, f"缺少必需字段：{field}"
    
    # 检查字段类型
    if field_types:
        for field, expected_type in field_types.items():
            if field in response_data:
                assert isinstance(response_data[field], expected_type), \
                    f"字段 {field} 类型错误，期望 {expected_type}，实际 {type(response_data[field])}"


async def upload_test_file(
    client: httpx.AsyncClient,
    file_path: Path,
    filename: Optional[str] = None
) -> Dict[str, Any]:
    """
    上传测试文件
    
    Args:
        client: HTTP 客户端
        file_path: 文件路径
        filename: 文件名（可选）
    
    Returns:
        上传响应数据
    """
    if filename is None:
        filename = file_path.name
    
    # 推断 MIME 类型
    ext = file_path.suffix.lower()
    mime_types = {
        ".wav": "audio/wav",
        ".mp3": "audio/mpeg",
        ".m4a": "audio/mp4",
        ".flac": "audio/flac"
    }
    content_type = mime_types.get(ext, "application/octet-stream")
    
    with open(file_path, "rb") as f:
        files = {"file": (filename, f, content_type)}
        response = await client.post("/api/upload", files=files)
    
    response.raise_for_status()
    return response.json()
