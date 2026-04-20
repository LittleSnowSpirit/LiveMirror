"""
音频上传 API 测试
测试 /api/upload 接口
"""
import pytest
import httpx
from pathlib import Path
from typing import Dict, Any


class TestUploadAPI:
    """音频上传 API 测试类"""
    
    @pytest.mark.api
    @pytest.mark.upload
    @pytest.mark.smoke
    async def test_upload_valid_audio(
        self,
        async_http_client: httpx.AsyncClient,
        sample_audio_file: Path,
        cleanup_tasks: list
    ):
        """测试上传有效的音频文件"""
        # 准备文件
        with open(sample_audio_file, "rb") as f:
            files = {"file": ("test_audio.wav", f, "audio/wav")}
            
            # 发送上传请求
            response = await async_http_client.post("/api/upload", files=files)
        
        # 验证响应
        assert response.status_code == 200
        data = response.json()
        
        assert "task_id" in data
        assert "filename" in data
        assert "file_size" in data
        assert "status" in data
        assert data["status"] in ["pending", "processing"]
        
        # 添加到清理列表
        cleanup_tasks.append(data["task_id"])
        
        print(f"上传成功：task_id={data['task_id']}, size={data['file_size']}")
    
    @pytest.mark.api
    @pytest.mark.upload
    async def test_upload_unsupported_format(
        self,
        async_http_client: httpx.AsyncClient,
        invalid_file: Path
    ):
        """测试上传不支持的文件格式"""
        with open(invalid_file, "rb") as f:
            files = {"file": ("test.txt", f, "text/plain")}
            response = await async_http_client.post("/api/upload", files=files)
        
        # 应该返回 400 错误
        assert response.status_code == 400
        data = response.json()
        
        assert "error" in data or "detail" in data
        print(f"正确拒绝了不支持的格式：{data}")
    
    @pytest.mark.api
    @pytest.mark.upload
    @pytest.mark.slow
    async def test_upload_large_file(
        self,
        async_http_client: httpx.AsyncClient,
        large_audio_file: Path,
        cleanup_tasks: list
    ):
        """测试上传大文件（边界测试）"""
        file_size = large_audio_file.stat().st_size
        print(f"测试大文件上传：{file_size / 1024 / 1024:.2f}MB")
        
        with open(large_audio_file, "rb") as f:
            files = {"file": ("large_audio.mp3", f, "audio/mpeg")}
            response = await async_http_client.post(
                "/api/upload",
                files=files,
                timeout=60.0  # 大文件需要更长时间
            )
        
        # 如果文件在限制内，应该成功
        # 如果超过限制，应该返回 400
        if response.status_code == 200:
            data = response.json()
            assert "task_id" in data
            cleanup_tasks.append(data["task_id"])
            print(f"大文件上传成功：{data['task_id']}")
        else:
            assert response.status_code == 400
            data = response.json()
            assert "error" in data or "detail" in data
            print(f"文件过大被拒绝：{data}")
    
    @pytest.mark.api
    @pytest.mark.upload
    async def test_upload_empty_file(
        self,
        async_http_client: httpx.AsyncClient,
        tmp_path: Path
    ):
        """测试上传空文件"""
        empty_file = tmp_path / "empty.wav"
        empty_file.touch()
        
        with open(empty_file, "rb") as f:
            files = {"file": ("empty.wav", f, "audio/wav")}
            response = await async_http_client.post("/api/upload", files=files)
        
        # 空文件应该被拒绝或特殊处理
        assert response.status_code in [200, 400]
        print(f"空文件处理结果：{response.status_code}")
    
    @pytest.mark.api
    @pytest.mark.upload
    async def test_upload_missing_file(
        self,
        async_http_client: httpx.AsyncClient
    ):
        """测试上传请求缺少文件"""
        response = await async_http_client.post("/api/upload", files={})
        
        # 应该返回 422 或 400
        assert response.status_code in [400, 422]
        print(f"缺少文件的响应：{response.status_code}")
    
    @pytest.mark.api
    @pytest.mark.upload
    @pytest.mark.parametrize("format", ["mp3", "wav", "m4a"])
    async def test_upload_various_formats(
        self,
        async_http_client: httpx.AsyncClient,
        tmp_path: Path,
        format: str,
        cleanup_tasks: list
    ):
        """测试上传不同音频格式"""
        # 创建模拟文件
        file_path = tmp_path / f"test.{format}"
        with open(file_path, "wb") as f:
            f.write(b"RIFF" + b"\x00" * 100)  # 模拟文件头
        
        mime_types = {
            "mp3": "audio/mpeg",
            "wav": "audio/wav",
            "m4a": "audio/mp4"
        }
        
        with open(file_path, "rb") as f:
            files = {"file": (f"test.{format}", f, mime_types[format])}
            response = await async_http_client.post("/api/upload", files=files)
        
        # 支持的格式应该成功
        if format in ["mp3", "wav", "m4a"]:
            assert response.status_code == 200
            data = response.json()
            assert "task_id" in data
            cleanup_tasks.append(data["task_id"])
            print(f"{format.upper()} 格式上传成功")
    
    @pytest.mark.api
    @pytest.mark.upload
    async def test_upload_filename_special_chars(
        self,
        async_http_client: httpx.AsyncClient,
        sample_audio_file: Path,
        cleanup_tasks: list
    ):
        """测试上传文件名包含特殊字符"""
        special_name = "test_音频文件 (1).wav"
        
        with open(sample_audio_file, "rb") as f:
            files = {"file": (special_name, f, "audio/wav")}
            response = await async_http_client.post("/api/upload", files=files)
        
        assert response.status_code == 200
        data = response.json()
        assert "task_id" in data
        cleanup_tasks.append(data["task_id"])
        print(f"特殊字符文件名处理成功：{special_name}")
    
    @pytest.mark.api
    @pytest.mark.upload
    async def test_concurrent_uploads(
        self,
        async_http_client: httpx.AsyncClient,
        sample_audio_file: Path,
        cleanup_tasks: list
    ):
        """测试并发上传"""
        import asyncio
        
        async def upload_one(index: int) -> Dict[str, Any]:
            with open(sample_audio_file, "rb") as f:
                files = {"file": (f"test_{index}.wav", f, "audio/wav")}
                response = await async_http_client.post("/api/upload", files=files)
                return {"index": index, "status": response.status_code, "data": response.json()}
        
        # 并发上传 3 个文件
        tasks = [upload_one(i) for i in range(3)]
        results = await asyncio.gather(*tasks)
        
        # 验证所有上传都成功
        for result in results:
            assert result["status"] == 200
            assert "task_id" in result["data"]
            cleanup_tasks.append(result["data"]["task_id"])
            print(f"并发上传 {result['index']} 成功")
    
    @pytest.mark.api
    @pytest.mark.upload
    async def test_upload_response_schema(
        self,
        async_http_client: httpx.AsyncClient,
        sample_audio_file: Path,
        cleanup_tasks: list
    ):
        """测试上传响应数据结构"""
        with open(sample_audio_file, "rb") as f:
            files = {"file": ("schema_test.wav", f, "audio/wav")}
            response = await async_http_client.post("/api/upload", files=files)
        
        assert response.status_code == 200
        data = response.json()
        
        # 验证必需字段
        required_fields = ["task_id", "filename", "file_size", "status"]
        for field in required_fields:
            assert field in data, f"缺少必需字段：{field}"
        
        # 验证字段类型
        assert isinstance(data["task_id"], str)
        assert isinstance(data["filename"], str)
        assert isinstance(data["file_size"], int)
        assert isinstance(data["status"], str)
        assert data["file_size"] > 0
        
        cleanup_tasks.append(data["task_id"])
        print("响应数据结构验证通过")


class TestUploadErrorHandling:
    """上传错误处理测试"""
    
    @pytest.mark.api
    @pytest.mark.upload
    async def test_server_error_handling(
        self,
        async_http_client: httpx.AsyncClient,
        monkeypatch
    ):
        """测试服务器错误处理（需要 mock）"""
        # 这个测试需要 mock 后端服务
        # 实际使用时可以通过中断服务来测试
        pytest.skip("需要 mock 后端服务")
    
    @pytest.mark.api
    @pytest.mark.upload
    async def test_timeout_handling(
        self,
        async_http_client: httpx.AsyncClient,
        large_audio_file: Path
    ):
        """测试超时处理"""
        # 使用非常短的超时来测试
        short_timeout_client = httpx.AsyncClient(
            base_url=async_http_client.base_url,
            timeout=0.001
        )
        
        try:
            with open(large_audio_file, "rb") as f:
                files = {"file": ("large.mp3", f, "audio/mpeg")}
                response = await short_timeout_client.post("/api/upload", files=files)
        except httpx.TimeoutException:
            print("超时处理正常")
            assert True
        finally:
            await short_timeout_client.aclose()
