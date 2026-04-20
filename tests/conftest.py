"""
Pytest 配置文件
提供全局 fixtures 和配置
"""
import pytest
import os
import sys
import asyncio
from pathlib import Path
from typing import Generator, AsyncGenerator
import httpx
from faker import Faker

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

fake = Faker("zh_CN")

# 配置
BASE_URL = os.getenv("TEST_BASE_URL", "http://localhost:8000")
FRONTEND_URL = os.getenv("TEST_FRONTEND_URL", "http://localhost:5173")
TEST_TIMEOUT = int(os.getenv("TEST_TIMEOUT", "30"))


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环用于异步测试"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def base_url() -> str:
    """返回后端 API 基础 URL"""
    return BASE_URL


@pytest.fixture(scope="session")
def frontend_url() -> str:
    """返回前端基础 URL"""
    return FRONTEND_URL


@pytest.fixture
def http_client() -> Generator[httpx.Client, None, None]:
    """提供同步 HTTP 客户端用于 API 测试"""
    client = httpx.Client(base_url=BASE_URL, timeout=TEST_TIMEOUT)
    yield client
    client.close()


@pytest.fixture
async def async_http_client() -> AsyncGenerator[httpx.AsyncClient, None]:
    """提供异步 HTTP 客户端用于 API 测试"""
    async with httpx.AsyncClient(base_url=BASE_URL, timeout=TEST_TIMEOUT) as client:
        yield client


@pytest.fixture
def sample_audio_file(tmp_path: Path) -> Path:
    """
    创建示例音频文件用于测试
    
    注意：这是一个模拟的音频文件，实际测试中应该使用真实音频
    """
    # 创建一个简单的 WAV 文件头（模拟音频文件）
    audio_path = tmp_path / "sample_audio.wav"
    
    # 简单的 WAV 文件头（44 字节）+ 一些静音数据
    wav_header = bytes([
        0x52, 0x49, 0x46, 0x46,  # RIFF
        0x24, 0x00, 0x00, 0x00,  # 文件大小 - 8
        0x57, 0x41, 0x56, 0x45,  # WAVE
        0x66, 0x6D, 0x74, 0x20,  # fmt 
        0x10, 0x00, 0x00, 0x00,  # 子块大小
        0x01, 0x00,              # 音频格式 (PCM)
        0x01, 0x00,              # 通道数 (单声道)
        0x80, 0x1F, 0x00, 0x00,  # 采样率 (8000Hz)
        0x00, 0x1F, 0x00, 0x00,  # 字节率
        0x01, 0x00,              # 块对齐
        0x08, 0x00,              # 位深度 (8-bit)
        0x64, 0x61, 0x74, 0x61,  # data
        0x00, 0x00, 0x00, 0x00,  # 数据大小
    ])
    
    # 添加一些静音数据（1 秒）
    silence = bytes([128] * 8000)  # 8-bit 静音
    
    with open(audio_path, "wb") as f:
        f.write(wav_header[:44])
        f.write(silence)
    
    return audio_path


@pytest.fixture
def large_audio_file(tmp_path: Path) -> Path:
    """创建一个大音频文件用于边界测试（模拟）"""
    audio_path = tmp_path / "large_audio.mp3"
    
    # 创建一个较大的文件（10MB）
    with open(audio_path, "wb") as f:
        # 写入 MP3 文件头
        f.write(b"ID3" + b"\x00" * 100)
        # 写入大量数据
        chunk_size = 1024 * 1024  # 1MB
        for _ in range(10):
            f.write(os.urandom(chunk_size))
    
    return audio_path


@pytest.fixture
def invalid_file(tmp_path: Path) -> Path:
    """创建无效文件格式用于测试"""
    file_path = tmp_path / "invalid.txt"
    with open(file_path, "w") as f:
        f.write("This is not an audio file")
    return file_path


@pytest.fixture
def supported_audio_formats() -> list:
    """返回支持的音频格式列表"""
    return ["mp3", "wav", "m4a", "flac", "aac", "ogg"]


@pytest.fixture
def task_poll_interval() -> int:
    """任务状态轮询间隔（秒）"""
    return 2


@pytest.fixture
def task_max_wait_time() -> int:
    """任务最大等待时间（秒）"""
    return 300  # 5 分钟


@pytest.fixture
def cleanup_tasks() -> Generator[list, None, None]:
    """
    清理测试创建的任务
    
    用法：
    @pytest.mark.usefixtures("cleanup_tasks")
    async def test_something(cleanup_tasks):
        task_ids = [...]
        cleanup_tasks.extend(task_ids)
    """
    task_ids = []
    yield task_ids
    
    # 注意：清理逻辑需要在测试中手动处理
    # 或者使用单独的清理 fixture


@pytest.fixture
def test_data() -> dict:
    """提供测试数据生成器"""
    return {
        "filename": fake.file_name(extension="mp3"),
        "description": fake.sentence(),
        "user_agent": fake.user_agent(),
    }


# Playwright fixtures
@pytest.fixture(scope="session")
def browser_context_args():
    """配置 Playwright 浏览器上下文"""
    return {
        "viewport": {"width": 1920, "height": 1080},
        "user_agent": "LiveMirror-Test-Bot/1.0",
        "ignore_https_errors": True,
    }


@pytest.fixture
def screenshot_on_failure(request, page):
    """测试失败时自动截图"""
    yield
    if request.node.rep_call and request.node.rep_call.failed:
        screenshot_name = f"{request.node.name}_failure.png"
        screenshot_path = Path(__file__).parent / "screenshots" / screenshot_name
        screenshot_path.parent.mkdir(exist_ok=True)
        page.screenshot(path=str(screenshot_path))
        print(f"Screenshot saved to {screenshot_path}")


def pytest_runtest_makereport(item, call):
    """添加测试结果报告钩子"""
    if "rep_call" not in item.__dict__:
        item.__dict__["rep_call"] = call


@pytest.fixture(autouse=True)
def setup_test_environment():
    """设置测试环境变量"""
    os.environ["TESTING"] = "true"
    yield
    os.environ.pop("TESTING", None)
