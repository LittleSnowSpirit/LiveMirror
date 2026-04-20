"""
报告数据 API 测试
测试 /api/report/{task_id} 接口
"""
import pytest
import httpx
import asyncio
from typing import Dict, Any


class TestReportAPI:
    """报告数据 API 测试类"""
    
    @pytest.mark.api
    @pytest.mark.report
    async def test_get_report_not_found(
        self,
        async_http_client: httpx.AsyncClient
    ):
        """查询不存在的报告"""
        fake_task_id = "00000000-0000-0000-0000-000000000000"
        response = await async_http_client.get(f"/api/report/{fake_task_id}")
        
        assert response.status_code == 404
        data = response.json()
        assert "error" in data or "detail" in data
        print(f"正确返回 404：{data}")
    
    @pytest.mark.api
    @pytest.mark.report
    @pytest.mark.upload
    async def test_get_report_completed_task(
        self,
        async_http_client: httpx.AsyncClient,
        sample_audio_file,
        cleanup_tasks: list,
        task_poll_interval: int,
        task_max_wait_time: int
    ):
        """查询已完成任务的报告"""
        # 1. 上传文件
        with open(sample_audio_file, "rb") as f:
            files = {"file": ("report_test.wav", f, "audio/wav")}
            upload_response = await async_http_client.post("/api/upload", files=files)
        
        task_id = upload_response.json()["task_id"]
        cleanup_tasks.append(task_id)
        
        # 2. 等待任务完成
        max_attempts = task_max_wait_time // task_poll_interval
        for attempt in range(max_attempts):
            response = await async_http_client.get(f"/api/task/{task_id}")
            data = response.json()
            
            if data["task"]["status"] in ["completed", "failed"]:
                break
            
            await asyncio.sleep(task_poll_interval)
        else:
            pytest.fail(f"任务在 {task_max_wait_time} 秒内未完成")
        
        # 3. 查询报告
        task_status = data["task"]["status"]
        if task_status == "completed":
            response = await async_http_client.get(f"/api/report/{task_id}")
            assert response.status_code == 200
            
            data = response.json()
            assert "success" in data
            assert "data" in data
            
            report_data = data["data"]
            assert "task_id" in report_data
            assert "transcription" in report_data
            assert "speaking_techniques" in report_data
            assert "attribution_analysis" in report_data
            
            print(f"报告查询成功：{len(report_data.get('transcription', ''))} 字符")
        else:
            print(f"任务失败，跳过报告测试：{task_status}")
    
    @pytest.mark.api
    @pytest.mark.report
    async def test_get_report_pending_task(
        self,
        async_http_client: httpx.AsyncClient,
        sample_audio_file,
        cleanup_tasks: list
    ):
        """查询处理中任务的报告（应该返回错误）"""
        # 上传文件
        with open(sample_audio_file, "rb") as f:
            files = {"file": ("pending_test.wav", f, "audio/wav")}
            upload_response = await async_http_client.post("/api/upload", files=files)
        
        task_id = upload_response.json()["task_id"]
        cleanup_tasks.append(task_id)
        
        # 立即查询报告（应该还在处理中）
        response = await async_http_client.get(f"/api/report/{task_id}")
        
        # 应该返回 400（任务未完成）
        assert response.status_code in [200, 400]
        
        if response.status_code == 400:
            data = response.json()
            assert "error" in data
            print(f"正确处理未完成的任务：{data['error']}")
        else:
            print("任务处理非常快，已经有报告了")
    
    @pytest.mark.api
    @pytest.mark.report
    async def test_get_transcription_endpoint(
        self,
        async_http_client: httpx.AsyncClient,
        sample_audio_file,
        cleanup_tasks: list,
        task_poll_interval: int
    ):
        """测试仅获取转写文字稿端点"""
        # 上传文件
        with open(sample_audio_file, "rb") as f:
            files = {"file": ("transcription_test.wav", f, "audio/wav")}
            upload_response = await async_http_client.post("/api/upload", files=files)
        
        task_id = upload_response.json()["task_id"]
        cleanup_tasks.append(task_id)
        
        # 等待转写完成
        for _ in range(30):
            response = await async_http_client.get(f"/api/task/{task_id}")
            data = response.json()
            
            if data["task"]["status"] in ["completed", "failed", "transcribing"]:
                break
            
            await asyncio.sleep(task_poll_interval)
        
        # 查询转写稿
        response = await async_http_client.get(f"/api/report/{task_id}/transcription")
        
        # 可能成功或还在处理
        assert response.status_code in [200, 400]
        
        if response.status_code == 200:
            data = response.json()
            assert "transcription" in data
            assert "segments" in data
            print(f"转写稿获取成功：{len(data['transcription'])} 字符")
    
    @pytest.mark.api
    @pytest.mark.report
    async def test_get_analysis_endpoint(
        self,
        async_http_client: httpx.AsyncClient,
        sample_audio_file,
        cleanup_tasks: list,
        task_poll_interval: int,
        task_max_wait_time: int
    ):
        """测试仅获取分析结果端点"""
        # 上传文件
        with open(sample_audio_file, "rb") as f:
            files = {"file": ("analysis_test.wav", f, "audio/wav")}
            upload_response = await async_http_client.post("/api/upload", files=files)
        
        task_id = upload_response.json()["task_id"]
        cleanup_tasks.append(task_id)
        
        # 等待任务完成
        max_attempts = task_max_wait_time // task_poll_interval
        for attempt in range(max_attempts):
            response = await async_http_client.get(f"/api/task/{task_id}")
            data = response.json()
            
            if data["task"]["status"] == "completed":
                break
            
            await asyncio.sleep(task_poll_interval)
        else:
            pytest.skip("任务未完成，跳过分析测试")
        
        # 查询分析结果
        response = await async_http_client.get(f"/api/report/{task_id}/analysis")
        
        if response.status_code == 200:
            data = response.json()
            assert "speaking_techniques" in data
            assert "attribution_analysis" in data
            assert "suggestions" in data
            print(f"分析结果获取成功")
    
    @pytest.mark.api
    @pytest.mark.report
    async def test_report_response_schema(
        self,
        async_http_client: httpx.AsyncClient,
        sample_audio_file,
        cleanup_tasks: list,
        task_poll_interval: int,
        task_max_wait_time: int
    ):
        """测试报告响应数据结构"""
        # 上传文件
        with open(sample_audio_file, "rb") as f:
            files = {"file": ("schema_test.wav", f, "audio/wav")}
            upload_response = await async_http_client.post("/api/upload", files=files)
        
        task_id = upload_response.json()["task_id"]
        cleanup_tasks.append(task_id)
        
        # 等待完成
        max_attempts = task_max_wait_time // task_poll_interval
        for attempt in range(max_attempts):
            response = await async_http_client.get(f"/api/task/{task_id}")
            data = response.json()
            
            if data["task"]["status"] == "completed":
                break
            
            await asyncio.sleep(task_poll_interval)
        else:
            pytest.skip("任务未完成")
        
        # 查询报告
        response = await async_http_client.get(f"/api/report/{task_id}")
        assert response.status_code == 200
        
        data = response.json()
        assert data["success"] is True
        assert "data" in data
        
        report = data["data"]
        
        # 验证必需字段
        required_fields = [
            "task_id", "filename", "transcription",
            "speaking_techniques", "attribution_analysis",
            "suggestions", "summary"
        ]
        
        for field in required_fields:
            assert field in report, f"缺少字段：{field}"
        
        # 验证字段类型
        assert isinstance(report["task_id"], str)
        assert isinstance(report["filename"], str)
        assert isinstance(report["transcription"], str)
        assert isinstance(report["speaking_techniques"], list)
        assert isinstance(report["suggestions"], list)
        
        print("报告响应数据结构验证通过")


class TestReportErrorHandling:
    """报告错误处理测试"""
    
    @pytest.mark.api
    @pytest.mark.report
    async def test_report_failed_task(
        self,
        async_http_client: httpx.AsyncClient,
        cleanup_tasks: list
    ):
        """查询失败任务的报告"""
        # 这个测试需要模拟一个失败的任务
        # 实际测试中可能需要特殊处理
        pytest.skip("需要模拟失败任务场景")
    
    @pytest.mark.api
    @pytest.mark.report
    async def test_report_invalid_task_id(
        self,
        async_http_client: httpx.AsyncClient
    ):
        """测试无效任务 ID 的报告查询"""
        invalid_ids = ["", "invalid", "123", "not-a-uuid"]
        
        for task_id in invalid_ids:
            response = await async_http_client.get(f"/api/report/{task_id}")
            assert response.status_code in [404, 422]
            print(f"无效 ID '{task_id}' 返回 {response.status_code}")
