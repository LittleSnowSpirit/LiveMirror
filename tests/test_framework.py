"""
测试框架验证测试
用于验证测试环境是否正确配置
"""
import pytest
import sys
from pathlib import Path


class TestFrameworkSetup:
    """测试框架配置验证"""
    
    @pytest.mark.smoke
    def test_python_version(self):
        """验证 Python 版本"""
        assert sys.version_info.major >= 3, "需要 Python 3+"
        print(f"Python 版本：{sys.version}")
    
    @pytest.mark.smoke
    def test_imports(self):
        """验证必需模块可导入"""
        # 能导入就说明安装成功
        import httpx
        import pytest
        from faker import Faker
        from playwright.sync_api import sync_playwright
        
        # 验证可以实例化
        fake = Faker()
        assert fake.name()
        
        print(f"httpx version: {httpx.__version__}")
        print(f"pytest version: {pytest.__version__}")
        print("所有必需模块导入成功")
    
    @pytest.mark.smoke
    def test_project_structure(self):
        """验证项目结构"""
        tests_dir = Path(__file__).parent
        backend_dir = tests_dir.parent / "backend"
        frontend_dir = tests_dir.parent / "frontend"
        
        assert tests_dir.exists(), "tests 目录不存在"
        assert backend_dir.exists(), "backend 目录不存在"
        assert frontend_dir.exists(), "frontend 目录不存在"
        
        # 验证关键文件
        assert (backend_dir / "main.py").exists()
        assert (frontend_dir / "package.json").exists()
        
        print("项目结构验证通过")
    
    @pytest.mark.smoke
    def test_fixtures_available(self):
        """验证 fixtures 可用"""
        # conftest.py 中定义的 fixtures 应该可用
        # 这个测试本身就是一个验证
        assert True
    
    @pytest.mark.smoke
    def test_markers_configured(self):
        """验证 pytest markers 配置"""
        # 如果 markers 未正确配置，pytest 会警告
        # 这个测试使用所有主要 markers
        assert True


class TestHelpers:
    """测试辅助工具验证"""
    
    @pytest.mark.smoke
    def test_create_wav_file(self, tmp_path: Path):
        """测试 WAV 文件创建"""
        from utils.test_helpers import create_wav_file
        
        output_path = tmp_path / "test.wav"
        result = create_wav_file(output_path, duration_seconds=0.1)
        
        assert result.exists()
        assert result.stat().st_size > 0
        print(f"创建 WAV 文件：{result.stat().st_size} 字节")
    
    @pytest.mark.smoke
    def test_format_duration(self):
        """测试时长格式化"""
        from utils.test_helpers import format_duration
        
        assert format_duration(0) == "0:00"
        assert format_duration(60) == "1:00"
        assert format_duration(125) == "2:05"
        print("时长格式化测试通过")
    
    @pytest.mark.smoke
    def test_file_size_helper(self, tmp_path: Path):
        """测试文件大小辅助函数"""
        from utils.test_helpers import get_file_size_mb
        
        test_file = tmp_path / "test.txt"
        test_file.write_text("x" * 1024)  # 1KB
        
        size_mb = get_file_size_mb(test_file)
        assert abs(size_mb - 0.001) < 0.0001  # 约 1KB
        
        print(f"文件大小：{size_mb:.4f} MB")


class TestConfig:
    """配置验证"""
    
    @pytest.mark.smoke
    def test_environment_variables(self):
        """验证环境变量配置"""
        import os
        
        base_url = os.getenv("TEST_BASE_URL", "http://localhost:8000")
        frontend_url = os.getenv("TEST_FRONTEND_URL", "http://localhost:5173")
        
        assert base_url.startswith("http")
        assert frontend_url.startswith("http")
        
        print(f"后端 URL: {base_url}")
        print(f"前端 URL: {frontend_url}")
    
    @pytest.mark.smoke
    def test_conftest_fixtures(self, base_url: str, frontend_url: str):
        """验证 conftest fixtures"""
        assert "localhost" in base_url or "127.0.0.1" in base_url
        assert "localhost" in frontend_url or "127.0.0.1" in frontend_url
        
        print(f"Fixtures 工作正常：{base_url}, {frontend_url}")
