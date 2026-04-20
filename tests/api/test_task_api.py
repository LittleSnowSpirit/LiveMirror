"""
任务状态 API 测试
测试 /api/task/{task_id} 接口
"""
import pytest
import httpx
import asyncio
from typing import Dict, Any


class TestTaskAPI:
    """任务状态 API 测试类"""
    
    @pytest.mark.api
    @pytest.mark.smoke
    async def test_get_task_not_found(
        self,
        async_http_client: httpx.AsyncClient
    ):
        """查询不存在的任务"""
        fake_task_id = "00000000-0000-0000-0000-000000000000"
        response = await async_http_client.get(f"/api/task/{fake_task_id}")
        
        assert response.status_code == 404
        data = response.json()
        assert "error" in data or "detail" in data
        print(f"正确返回 404：{data}")
    
    @pytest.mark.api
    @pytest.mark.upload
    async def test_get_task_after_upload(
        self,
        async_http_client: httpx.AsyncClient,
        sample_audio_file,
        cleanup_tasks: list,
        task_poll_interval: int,
        task_max_wait_time: int
    ):
        """上传后查询任务状态"""
        # 1. 上传文件
        with open(sample_audio_file, "rb") as f:
            files = {"file": ("status_test.wav", f, "audio/wav")}
            upload_response = await async_http_client.post("/api/upload", files=files)
        
        assert upload_response.status_code == 200
        task_id = upload_response.json()["task_id"]
        cleanup_tasks.append(task_id)
        
        # 2. 轮询任务状态
        max_attempts = task_max_wait_time // task_poll_interval
        for attempt in range(max_attempts):
            response = await async_http_client.get(f"/api/task/{task_id}")
            assert response.status_code == 200
            
            data = response.json()
            assert "task" in data
            task = data["task"]
            
            assert "task_id" in task
            assert "status" in task
            assert "progress" in task
            
            print(f"轮询 {attempt + 1}: status={task['status']}, progress={task['progress']}%")
            
            # 检查是否完成
            if task["status"] in ["completed", "failed"]:
                break
            
            await asyncio.sleep(task_poll_interval)
        else:
            pytest.fail(f"任务在 {task_max_wait_time} 秒内未完成")
        
        # 验证最终状态
        final_status = task["status"]
        assert final_status in ["completed", "failed"]
        print(f"任务最终状态：{final_status}")
    
    @pytest.mark.api
    async def test_get_task_progress_endpoint(
        self,
        async_http_client: httpx.AsyncClient,
        sample_audio_file,
        cleanup_tasks: list
    ):
        """测试进度查询端点 /api/task/{task_id}/progress"""
        # 上传文件
        with open(sample_audio_file, "rb") as f:
            files = {"file": ("progress_test.wav", f, "audio/wav")}
            upload_response = await async_http_client.post("/api/upload", files=files)
        
        task_id = upload_response.json()["task_id"]
        cleanup_tasks.append(task_id)
        
        # 查询进度
        response = await async_http_client.get(f"/api/task/{task_id}/progress")
        assert response.status_code == 200
        
        data = response.json()
        assert "task_id" in data
        assert "status" in data
        assert "progress" in data
        assert "completed" in data
        
        print(f"进度端点响应：{data}")
    
    @pytest.mark.api
    @pytest.mark.parametrize("invalid_id", [
        "",
        "invalid-uuid",
        "123",
        None,
    ])
    async def test_get_task_invalid_id(
        self,
        async_http_client: httpx.AsyncClient,
        invalid_id: str
    ):
        """测试无效任务 ID 的处理"""
        if invalid_id is None:
            # 测试缺失 task_id
            response = await async_http_client.get("/api/task/")
        else:
            response = await async_http_client.get(f"/api/task/{invalid_id}")
        
        # 应该返回 404 或 422
        assert response.status_code in [404, 422]
        print(f"无效 ID '{invalid_id}' 返回 {response.status_code}")
    
    @pytest.mark.api
    async def test_task_status_transitions(
        self,
        async_http_client: httpx.AsyncClient,
        sample_audio_file,
        cleanup_tasks: list,
        task_poll_interval: int
    ):
        """测试任务状态转换流程"""
        # 上传文件
        with open(sample_audio_file, "rb") as f:
            files = {"file": ("transition_test.wav", f, "audio/wav")}
            upload_response = await async_http_client.post("/api/upload", files=files)
        
        task_id = upload_response.json()["task_id"]
        cleanup_tasks.append(task_id)
        
        # 记录状态转换
        status_history = []
        
        # 轮询并记录状态
        for _ in range(30):  # 最多轮询 30 次
            response = await async_http_client.get(f"/api/task/{task_id}")
            data = response.json()
            current_status = data["task"]["status"]
            
            if not status_history or current_status != status_history[-1]:
                status_history.append(current_status)
                print(f"状态变化：{current_status}")
            
            if current_status in ["completed", "failed"]:
                break
            
            await asyncio.sleep(task_poll_interval)
        
        # 验证状态转换合理性
        assert len(status_history) > 0
        assert status_history[0] in ["pending", "processing"]
        assert status_history[-1] in ["completed", "failed"]
        
        print(f"状态转换流程：{' -> '.join(status_history)}")
    
    @pytest.mark.api
    async def test_task_response_schema(
        self,
        async_http_client: httpx.AsyncClient,
        sample_audio_file,
        cleanup_tasks: list
    ):
        """测试任务响应数据结构"""
        # 上传文件
        with open(sample_audio_file, "rb") as f:
            files = {"file": ("schema_test.wav", f, "audio/wav")}
            upload_response = await async_http_client.post("/api/upload", files=files)
        
        task_id = upload_response.json()["task_id"]
        cleanup_tasks.append(task_id)
        
        # 查询任务
        response = await async_http_client.get(f"/api/task/{task_id}")
        assert response.status_code == 200
        
        data = response.json()
        task = data["task"]
        
        # 验证必需字段
        required_fields = [
            "task_id", "filename", "file_size", "status",
            "created_at", "updated_at"
        ]
        
        for field in required_fields:
            assert field in task, f"缺少字段：{field}"
        
        # 验证字段类型
        assert isinstance(task["task_id"], str)
        assert isinstance(task["filename"], str)
        assert isinstance(task["file_size"], int)
        assert isinstance(task["status"], str)
        assert isinstance(task["progress"], int)
        assert 0 <= task["progress"] <= 100
        
        print("任务响应数据结构验证通过")


class TestTaskPolling:
    """任务轮询逻辑测试"""
    
    @pytest.mark.api
    async def test_polling_interval_handling(
        self,
        async_http_client: httpx.AsyncClient,
        sample_audio_file,
        cleanup_tasks: list
    ):
        """测试轮询间隔处理"""
        # 上传文件
        with open(sample_audio_file, "rb") as f:
            files = {"file": ("polling_test.wav", f, "audio/wav")}
            upload_response = await async_http_client.post("/api/upload", files=files)
        
        task_id = upload_response.json()["task_id"]
        cleanup_tasks.append(task_id)
        
        # 快速轮询 5 次（测试服务器是否能处理频繁请求）
        for i in range(5):
            response = await async_http_client.get(f"/api/task/{task_id}")
            assert response.status_code == 200
            await asyncio.sleep(0.5)  # 500ms 间隔
        
        print("频繁轮询测试通过")
    
    @pytest.mark.api
    async def test_polling_until_completion(
        self,
        async_http_client: httpx.AsyncClient,
        sample_audio_file,
        cleanup_tasks: list
    ):
        """测试轮询直到完成"""
        # 上传文件
        with open(sample_audio_file, "rb") as f:
            files = {"file": ("complete_test.wav", f, "audio/wav")}
            upload_response = await async_http_client.post("/api/upload", files=files)
        
        task_id = upload_response.json()["task_id"]
        cleanup_tasks.append(task_id)
        
        # 轮询直到完成
        completed = False
        attempts = 0
        max_attempts = 60  # 最多 60 秒
        
        while not completed and attempts < max_attempts:
            response = await async_http_client.get(f"/api/task/{task_id}")
            data = response.json()
            
            status = data["task"]["status"]
            progress = data["task"]["progress"]
            
            print(f"轮询 {attempts + 1}: {status} ({progress}%)")
            
            if status in ["completed", "failed"]:
                completed = True
                print(f"任务完成：{status}")
            
            attempts += 1
            await asyncio.sleep(1)
        
        assert completed, f"任务在 {max_attempts} 秒内未完成"
