"""
直播回放管理功能测试
测试录像存储、播放、剪辑和分享功能
"""

import pytest
import os
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

# 导入服务
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from services.playback import PlaybackService, get_playback_service


class TestPlaybackService:
    """回放服务测试类"""
    
    @pytest.fixture
    def service(self, tmp_path):
        """创建临时存储服务"""
        storage_path = tmp_path / "recordings"
        return PlaybackService(str(storage_path))
    
    @pytest.fixture
    def sample_video(self, tmp_path):
        """创建示例视频文件（模拟）"""
        video_path = tmp_path / "test_video.mp4"
        # 创建一个模拟的视频文件
        video_path.write_bytes(b'\x00' * 1024 * 1024)  # 1MB 模拟文件
        return str(video_path)
    
    @pytest.fixture
    def sample_thumbnail(self, tmp_path):
        """创建示例缩略图文件（模拟）"""
        thumb_path = tmp_path / "test_thumb.jpg"
        thumb_path.write_bytes(b'\x00' * 1024 * 100)  # 100KB 模拟文件
        return str(thumb_path)
    
    def test_add_recording(self, service, sample_video, sample_thumbnail):
        """测试添加录像"""
        recording = service.add_recording(
            file_path=sample_video,
            title="测试录像",
            streamer="测试主播",
            duration=3600,
            categories=["游戏", "直播"],
            tags=["精彩", "回放"],
            description="这是一个测试录像",
            thumbnail_path=sample_thumbnail
        )
        
        assert recording['id'] is not None
        assert recording['title'] == "测试录像"
        assert recording['streamer'] == "测试主播"
        assert recording['duration'] == 3600
        assert "游戏" in recording['categories']
        assert "直播" in recording['categories']
        assert "精彩" in recording['tags']
        assert "回放" in recording['tags']
        assert recording['description'] == "这是一个测试录像"
        assert Path(recording['file_path']).exists()
        assert recording['thumbnail_path'] is not None
        assert Path(recording['thumbnail_path']).exists()
        assert recording['view_count'] == 0
        assert recording['is_public'] == False
    
    def test_get_recording(self, service, sample_video):
        """测试获取录像"""
        recording = service.add_recording(
            file_path=sample_video,
            title="测试录像",
            streamer="测试主播",
            duration=3600
        )
        
        retrieved = service.get_recording(recording['id'])
        assert retrieved is not None
        assert retrieved['id'] == recording['id']
        assert retrieved['title'] == "测试录像"
    
    def test_get_all_recordings(self, service, sample_video):
        """测试获取所有录像"""
        # 添加多个录像
        for i in range(5):
            service.add_recording(
                file_path=sample_video,
                title=f"测试录像{i}",
                streamer=f"主播{i}",
                duration=1000 + i * 100
            )
        
        recordings = service.get_all_recordings()
        assert len(recordings) == 5
        
        # 测试分页
        recordings_page1 = service.get_all_recordings(limit=2, offset=0)
        assert len(recordings_page1) == 2
        
        recordings_page2 = service.get_all_recordings(limit=2, offset=2)
        assert len(recordings_page2) == 2
    
    def test_search_recordings(self, service, sample_video):
        """测试搜索录像"""
        # 添加测试数据
        service.add_recording(
            file_path=sample_video,
            title="英雄联盟精彩集锦",
            streamer="张三",
            duration=3600,
            categories=["游戏"],
            tags=["LOL", "精彩"]
        )
        
        service.add_recording(
            file_path=sample_video,
            title="DOTA2 教学视频",
            streamer="李四",
            duration=7200,
            categories=["游戏", "教学"],
            tags=["DOTA2", "教程"]
        )
        
        service.add_recording(
            file_path=sample_video,
            title="音乐直播回放",
            streamer="王五",
            duration=5400,
            categories=["音乐"],
            tags=["演唱会", "直播"]
        )
        
        # 关键词搜索
        results = service.search_recordings(query="英雄联盟")
        assert len(results) == 1
        assert results[0]['title'] == "英雄联盟精彩集锦"
        
        # 分类筛选
        results = service.search_recordings(categories=["游戏"])
        assert len(results) == 2
        
        # 标签筛选
        results = service.search_recordings(tags=["精彩"])
        assert len(results) == 1
        
        # 主播筛选
        results = service.search_recordings(streamer="张三")
        assert len(results) == 1
        
        # 时长筛选
        results = service.search_recordings(min_duration=5000, max_duration=8000)
        assert len(results) == 2
        
        # 组合筛选
        results = service.search_recordings(categories=["游戏"], tags=["LOL"])
        assert len(results) == 1
    
    def test_update_recording(self, service, sample_video):
        """测试更新录像"""
        recording = service.add_recording(
            file_path=sample_video,
            title="原始标题",
            streamer="主播",
            duration=1000
        )
        
        # 更新
        updated = service.update_recording(recording['id'], {
            'title': '新标题',
            'description': '新描述',
            'categories': ['新分类'],
            'tags': ['新标签'],
            'is_public': True
        })
        
        assert updated['title'] == '新标题'
        assert updated['description'] == '新描述'
        assert '新分类' in updated['categories']
        assert '新标签' in updated['tags']
        assert updated['is_public'] == True
        assert updated['updated_at'] != recording['updated_at']
    
    def test_delete_recording(self, service, sample_video):
        """测试删除录像"""
        recording = service.add_recording(
            file_path=sample_video,
            title="测试录像",
            streamer="主播",
            duration=1000
        )
        
        recording_id = recording['id']
        file_path = recording['file_path']
        
        # 验证文件存在
        assert Path(file_path).exists()
        
        # 删除
        result = service.delete_recording(recording_id)
        assert result == True
        
        # 验证文件已删除
        assert not Path(file_path).exists()
        
        # 验证无法获取
        assert service.get_recording(recording_id) is None
        
        # 删除不存在的录像
        result = service.delete_recording("non-existent-id")
        assert result == False
    
    def test_increment_view_count(self, service, sample_video):
        """测试增加观看次数"""
        recording = service.add_recording(
            file_path=sample_video,
            title="测试录像",
            streamer="主播",
            duration=1000
        )
        
        assert recording['view_count'] == 0
        
        service.increment_view_count(recording['id'])
        updated = service.get_recording(recording['id'])
        assert updated['view_count'] == 1
        
        service.increment_view_count(recording['id'])
        updated = service.get_recording(recording['id'])
        assert updated['view_count'] == 2
    
    def test_create_clip(self, service, sample_video):
        """测试创建片段"""
        recording = service.add_recording(
            file_path=sample_video,
            title="测试录像",
            streamer="主播",
            duration=3600
        )
        
        clip = service.create_clip(
            recording_id=recording['id'],
            start_time=100.5,
            end_time=200.5,
            title="精彩片段",
            description="这是一个精彩片段"
        )
        
        assert clip['id'] is not None
        assert clip['original_recording_id'] == recording['id']
        assert clip['title'] == "精彩片段"
        assert clip['description'] == "这是一个精彩片段"
        assert clip['start_time'] == 100.5
        assert clip['end_time'] == 200.5
        assert clip['duration'] == 100.0
        assert clip['source_file'] == recording['file_path']
    
    def test_get_clips(self, service, sample_video):
        """测试获取片段列表"""
        recording1 = service.add_recording(
            file_path=sample_video,
            title="录像 1",
            streamer="主播",
            duration=3600
        )
        
        recording2 = service.add_recording(
            file_path=sample_video,
            title="录像 2",
            streamer="主播",
            duration=3600
        )
        
        # 为两个录像创建片段
        service.create_clip(recording1['id'], 0, 100, "片段 1-1")
        service.create_clip(recording1['id'], 200, 300, "片段 1-2")
        service.create_clip(recording2['id'], 0, 150, "片段 2-1")
        
        # 获取所有片段
        all_clips = service.get_clips()
        assert len(all_clips) == 3
        
        # 获取特定录像的片段
        clips1 = service.get_clips(recording1['id'])
        assert len(clips1) == 2
        
        clips2 = service.get_clips(recording2['id'])
        assert len(clips2) == 1
    
    def test_generate_share_token(self, service, sample_video):
        """测试生成分享令牌"""
        recording = service.add_recording(
            file_path=sample_video,
            title="测试录像",
            streamer="主播",
            duration=1000
        )
        
        token = service.generate_share_token(recording['id'], expire_hours=24)
        
        assert token is not None
        assert len(token) > 0
        
        # 验证录像已标记为公开
        updated = service.get_recording(recording['id'])
        assert updated['is_public'] == True
        assert updated['share_token'] == token
        assert updated['share_count'] == 1
    
    def test_get_by_share_token(self, service, sample_video):
        """测试通过分享令牌获取录像"""
        recording = service.add_recording(
            file_path=sample_video,
            title="测试录像",
            streamer="主播",
            duration=1000
        )
        
        # 未分享前无法通过令牌获取
        result = service.get_by_share_token("invalid-token")
        assert result is None
        
        # 生成分享令牌
        token = service.generate_share_token(recording['id'])
        
        # 通过令牌获取
        result = service.get_by_share_token(token)
        assert result is not None
        assert result['id'] == recording['id']
        
        # 无效令牌
        result = service.get_by_share_token("wrong-token")
        assert result is None
    
    def test_get_categories(self, service, sample_video):
        """测试获取所有分类"""
        service.add_recording(
            file_path=sample_video,
            title="录像 1",
            streamer="主播",
            duration=1000,
            categories=["游戏", "直播"]
        )
        
        service.add_recording(
            file_path=sample_video,
            title="录像 2",
            streamer="主播",
            duration=1000,
            categories=["音乐", "直播"]
        )
        
        service.add_recording(
            file_path=sample_video,
            title="录像 3",
            streamer="主播",
            duration=1000,
            categories=["游戏", "教学"]
        )
        
        categories = service.get_categories()
        assert len(categories) == 4
        assert "游戏" in categories
        assert "直播" in categories
        assert "音乐" in categories
        assert "教学" in categories
    
    def test_get_tags(self, service, sample_video):
        """测试获取所有标签"""
        service.add_recording(
            file_path=sample_video,
            title="录像 1",
            streamer="主播",
            duration=1000,
            tags=["精彩", "LOL"]
        )
        
        service.add_recording(
            file_path=sample_video,
            title="录像 2",
            streamer="主播",
            duration=1000,
            tags=["教程", "DOTA2"]
        )
        
        tags = service.get_tags()
        assert len(tags) == 4
        assert "精彩" in tags
        assert "LOL" in tags
        assert "教程" in tags
        assert "DOTA2" in tags
    
    def test_get_statistics(self, service, sample_video):
        """测试获取统计信息"""
        # 添加测试数据
        for i in range(3):
            recording = service.add_recording(
                file_path=sample_video,
                title=f"录像{i}",
                streamer="主播",
                duration=3600
            )
            service.increment_view_count(recording['id'])
            service.increment_view_count(recording['id'])
        
        # 创建片段
        recordings = service.get_all_recordings()
        service.create_clip(recordings[0]['id'], 0, 100, "片段 1")
        service.create_clip(recordings[0]['id'], 200, 300, "片段 2")
        service.create_clip(recordings[1]['id'], 0, 150, "片段 3")
        
        stats = service.get_statistics()
        
        assert stats['total_recordings'] == 3
        assert stats['total_duration_seconds'] == 3600 * 3
        assert stats['total_duration_hours'] == 3.0
        assert stats['total_views'] == 6  # 每个录像 2 次观看
        assert stats['total_clips'] == 3
        assert stats['total_storage_bytes'] > 0


class TestPlaybackAPI:
    """API 接口测试（需要 FastAPI 测试客户端）"""
    
    @pytest.fixture
    def client(self, tmp_path):
        """创建测试客户端"""
        from fastapi.testclient import TestClient
        from fastapi import FastAPI
        from routes.playback import router as playback_router
        
        # 初始化服务路径
        storage_path = tmp_path / "recordings"
        get_playback_service(str(storage_path))
        
        app = FastAPI()
        app.include_router(playback_router)
        
        return TestClient(app)
    
    def test_list_recordings(self, client):
        """测试获取录像列表 API"""
        response = client.get("/api/playback/recordings")
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        assert 'data' in data
        assert 'total' in data
    
    def test_search_recordings_api(self, client):
        """测试搜索录像 API"""
        response = client.get(
            "/api/playback/recordings/search",
            params={"query": "test", "limit": 10}
        )
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
    
    def test_statistics_api(self, client):
        """测试统计信息 API"""
        response = client.get("/api/playback/statistics")
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        assert 'data' in data
    
    def test_categories_api(self, client):
        """测试分类列表 API"""
        response = client.get("/api/playback/categories")
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        assert isinstance(data['data'], list)
    
    def test_tags_api(self, client):
        """测试标签列表 API"""
        response = client.get("/api/playback/tags")
        assert response.status_code == 200
        data = response.json()
        assert data['success'] == True
        assert isinstance(data['data'], list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
