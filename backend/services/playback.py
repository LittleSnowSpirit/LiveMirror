"""
直播回放管理服务
负责直播录像的存储、管理、分类、标签、搜索和分享功能
"""

import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Optional, Any
from pathlib import Path
import shutil


class PlaybackService:
    """直播回放管理服务类"""
    
    def __init__(self, storage_path: str = "./storage/recordings"):
        """
        初始化回放服务
        
        Args:
            storage_path: 录像存储路径
        """
        self.storage_path = Path(storage_path)
        self.metadata_path = self.storage_path / "metadata"
        self.clips_path = self.storage_path / "clips"
        
        # 确保目录存在
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.metadata_path.mkdir(parents=True, exist_ok=True)
        self.clips_path.mkdir(parents=True, exist_ok=True)
        
        # 内存缓存元数据
        self._metadata_cache: Dict[str, Dict] = {}
        self._load_all_metadata()
    
    def _load_all_metadata(self):
        """加载所有元数据到缓存"""
        if not self.metadata_path.exists():
            return
            
        for meta_file in self.metadata_path.glob("*.json"):
            try:
                with open(meta_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._metadata_cache[data['id']] = data
            except (json.JSONDecodeError, KeyError):
                continue
    
    def _save_metadata(self, recording_id: str, metadata: Dict):
        """保存元数据到文件"""
        meta_file = self.metadata_path / f"{recording_id}.json"
        with open(meta_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        self._metadata_cache[recording_id] = metadata
    
    def add_recording(
        self,
        file_path: str,
        title: str,
        streamer: str,
        duration: int,
        categories: List[str] = None,
        tags: List[str] = None,
        description: str = "",
        thumbnail_path: str = None
    ) -> Dict:
        """
        添加新的直播录像
        
        Args:
            file_path: 视频文件路径
            title: 录像标题
            streamer: 主播名称
            duration: 时长（秒）
            categories: 分类列表
            tags: 标签列表
            description: 描述
            thumbnail_path: 缩略图路径
            
        Returns:
            录像元数据
        """
        recording_id = str(uuid.uuid4())
        source_path = Path(file_path)
        
        # 移动文件到存储目录
        dest_path = self.storage_path / f"{recording_id}{source_path.suffix}"
        shutil.copy2(source_path, dest_path)
        
        # 处理缩略图
        dest_thumbnail = None
        if thumbnail_path:
            thumb_source = Path(thumbnail_path)
            dest_thumbnail = self.storage_path / f"{recording_id}_thumb{thumb_source.suffix}"
            shutil.copy2(thumb_source, dest_thumbnail)
        
        # 创建元数据
        metadata = {
            'id': recording_id,
            'title': title,
            'streamer': streamer,
            'duration': duration,
            'categories': categories or [],
            'tags': tags or [],
            'description': description,
            'file_path': str(dest_path),
            'file_name': dest_path.name,
            'file_size': dest_path.stat().st_size,
            'thumbnail_path': str(dest_thumbnail) if dest_thumbnail else None,
            'created_at': datetime.now().isoformat(),
            'updated_at': datetime.now().isoformat(),
            'view_count': 0,
            'share_count': 0,
            'is_public': False,
            'share_token': None
        }
        
        self._save_metadata(recording_id, metadata)
        return metadata
    
    def get_recording(self, recording_id: str) -> Optional[Dict]:
        """获取单个录像元数据"""
        return self._metadata_cache.get(recording_id)
    
    def get_all_recordings(self, limit: int = 100, offset: int = 0) -> List[Dict]:
        """获取所有录像列表"""
        recordings = list(self._metadata_cache.values())
        # 按创建时间倒序
        recordings.sort(key=lambda x: x['created_at'], reverse=True)
        return recordings[offset:offset + limit]
    
    def search_recordings(
        self,
        query: str = None,
        categories: List[str] = None,
        tags: List[str] = None,
        streamer: str = None,
        date_from: str = None,
        date_to: str = None,
        min_duration: int = None,
        max_duration: int = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict]:
        """
        搜索和筛选录像
        
        Args:
            query: 搜索关键词（标题、描述）
            categories: 分类筛选
            tags: 标签筛选
            streamer: 主播筛选
            date_from: 起始日期 (ISO format)
            date_to: 结束日期 (ISO format)
            min_duration: 最小时长（秒）
            max_duration: 最大时长（秒）
            limit: 返回数量限制
            offset: 偏移量
            
        Returns:
            匹配的录像列表
        """
        results = []
        
        for recording in self._metadata_cache.values():
            # 关键词搜索
            if query:
                query_lower = query.lower()
                if not (query_lower in recording['title'].lower() or 
                        query_lower in recording['description'].lower()):
                    continue
            
            # 分类筛选
            if categories:
                if not any(cat in recording['categories'] for cat in categories):
                    continue
            
            # 标签筛选
            if tags:
                if not any(tag in recording['tags'] for tag in tags):
                    continue
            
            # 主播筛选
            if streamer:
                if streamer.lower() not in recording['streamer'].lower():
                    continue
            
            # 日期筛选
            if date_from:
                if recording['created_at'] < date_from:
                    continue
            if date_to:
                if recording['created_at'] > date_to:
                    continue
            
            # 时长筛选
            if min_duration is not None:
                if recording['duration'] < min_duration:
                    continue
            if max_duration is not None:
                if recording['duration'] > max_duration:
                    continue
            
            results.append(recording)
        
        # 按创建时间倒序
        results.sort(key=lambda x: x['created_at'], reverse=True)
        return results[offset:offset + limit]
    
    def update_recording(self, recording_id: str, updates: Dict) -> Optional[Dict]:
        """
        更新录像元数据
        
        Args:
            recording_id: 录像 ID
            updates: 要更新的字段
            
        Returns:
            更新后的元数据
        """
        if recording_id not in self._metadata_cache:
            return None
        
        metadata = self._metadata_cache[recording_id].copy()
        
        # 允许更新的字段
        allowed_fields = ['title', 'description', 'categories', 'tags', 'is_public']
        for field in allowed_fields:
            if field in updates:
                metadata[field] = updates[field]
        
        metadata['updated_at'] = datetime.now().isoformat()
        self._save_metadata(recording_id, metadata)
        return metadata
    
    def delete_recording(self, recording_id: str) -> bool:
        """
        删除录像
        
        Args:
            recording_id: 录像 ID
            
        Returns:
            是否删除成功
        """
        if recording_id not in self._metadata_cache:
            return False
        
        metadata = self._metadata_cache[recording_id]
        
        # 删除视频文件
        try:
            video_path = Path(metadata['file_path'])
            if video_path.exists():
                video_path.unlink()
        except Exception:
            pass
        
        # 删除缩略图
        try:
            if metadata.get('thumbnail_path'):
                thumb_path = Path(metadata['thumbnail_path'])
                if thumb_path.exists():
                    thumb_path.unlink()
        except Exception:
            pass
        
        # 删除元数据文件
        meta_file = self.metadata_path / f"{recording_id}.json"
        if meta_file.exists():
            meta_file.unlink()
        
        # 删除相关剪辑
        for clip_file in self.clips_path.glob(f"{recording_id}_*.json"):
            clip_file.unlink()
        
        # 从缓存移除
        del self._metadata_cache[recording_id]
        return True
    
    def increment_view_count(self, recording_id: str):
        """增加观看次数"""
        if recording_id in self._metadata_cache:
            metadata = self._metadata_cache[recording_id].copy()
            metadata['view_count'] = metadata.get('view_count', 0) + 1
            metadata['updated_at'] = datetime.now().isoformat()
            self._save_metadata(recording_id, metadata)
    
    def create_clip(
        self,
        recording_id: str,
        start_time: float,
        end_time: float,
        title: str,
        description: str = ""
    ) -> Optional[Dict]:
        """
        创建录像片段
        
        Args:
            recording_id: 原录像 ID
            start_time: 片段开始时间（秒）
            end_time: 片段结束时间（秒）
            title: 片段标题
            description: 片段描述
            
        Returns:
            片段元数据
        """
        if recording_id not in self._metadata_cache:
            return None
        
        original = self._metadata_cache[recording_id]
        clip_id = str(uuid.uuid4())
        
        clip_metadata = {
            'id': clip_id,
            'original_recording_id': recording_id,
            'title': title,
            'description': description,
            'start_time': start_time,
            'end_time': end_time,
            'duration': end_time - start_time,
            'source_file': original['file_path'],
            'created_at': datetime.now().isoformat(),
            'share_token': None,
            'is_public': False
        }
        
        # 保存片段元数据
        clip_file = self.clips_path / f"{recording_id}_{clip_id}.json"
        with open(clip_file, 'w', encoding='utf-8') as f:
            json.dump(clip_metadata, f, ensure_ascii=False, indent=2)
        
        return clip_metadata
    
    def get_clips(self, recording_id: str = None) -> List[Dict]:
        """
        获取片段列表
        
        Args:
            recording_id: 可选，筛选特定录像的片段
            
        Returns:
            片段列表
        """
        clips = []
        for clip_file in self.clips_path.glob("*.json"):
            try:
                with open(clip_file, 'r', encoding='utf-8') as f:
                    clip = json.load(f)
                    if recording_id is None or clip.get('original_recording_id') == recording_id:
                        clips.append(clip)
            except (json.JSONDecodeError, KeyError):
                continue
        return clips
    
    def generate_share_token(self, recording_id: str, expire_hours: int = 24) -> Optional[str]:
        """
        生成分享令牌
        
        Args:
            recording_id: 录像 ID
            expire_hours: 过期时间（小时）
            
        Returns:
            分享令牌
        """
        if recording_id not in self._metadata_cache:
            return None
        
        metadata = self._metadata_cache[recording_id].copy()
        share_token = str(uuid.uuid4())
        
        metadata['share_token'] = share_token
        metadata['share_expires_at'] = datetime.now().isoformat()
        metadata['is_public'] = True
        metadata['share_count'] = metadata.get('share_count', 0) + 1
        metadata['updated_at'] = datetime.now().isoformat()
        
        self._save_metadata(recording_id, metadata)
        return share_token
    
    def get_by_share_token(self, share_token: str) -> Optional[Dict]:
        """通过分享令牌获取录像"""
        for recording in self._metadata_cache.values():
            if recording.get('share_token') == share_token and recording.get('is_public'):
                return recording
        return None
    
    def get_categories(self) -> List[str]:
        """获取所有分类"""
        categories = set()
        for recording in self._metadata_cache.values():
            categories.update(recording.get('categories', []))
        return sorted(list(categories))
    
    def get_tags(self) -> List[str]:
        """获取所有标签"""
        tags = set()
        for recording in self._metadata_cache.values():
            tags.update(recording.get('tags', []))
        return sorted(list(tags))
    
    def get_statistics(self) -> Dict:
        """获取统计信息"""
        total_recordings = len(self._metadata_cache)
        total_duration = sum(r['duration'] for r in self._metadata_cache.values())
        total_views = sum(r.get('view_count', 0) for r in self._metadata_cache.values())
        total_clips = len(list(self.clips_path.glob("*.json")))
        
        return {
            'total_recordings': total_recordings,
            'total_duration_seconds': total_duration,
            'total_duration_hours': round(total_duration / 3600, 2),
            'total_views': total_views,
            'total_clips': total_clips,
            'total_storage_bytes': sum(r.get('file_size', 0) for r in self._metadata_cache.values())
        }


# 全局服务实例
_playback_service: Optional[PlaybackService] = None


def get_playback_service(storage_path: str = None) -> PlaybackService:
    """获取回放服务单例"""
    global _playback_service
    if _playback_service is None:
        _playback_service = PlaybackService(storage_path or "./storage/recordings")
    return _playback_service
