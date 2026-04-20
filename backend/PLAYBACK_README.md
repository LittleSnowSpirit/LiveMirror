# 直播回放管理功能文档

## 概述

直播回放管理系统提供完整的录像存储、管理、播放、剪辑和分享功能。

## 功能特性

### 1. 直播录像存储和管理
- 支持上传视频文件并自动存储
- 自动生成唯一 ID 和元数据
- 支持缩略图上传和管理
- 自动记录文件大小、时长等信息

### 2. 录像分类和标签
- 支持多分类管理
- 支持多标签系统
- 可获取所有分类和标签列表
- 支持动态添加分类和标签

### 3. 录像搜索和筛选
- 关键词搜索（标题、描述）
- 按分类筛选
- 按标签筛选
- 按主播筛选
- 按日期范围筛选
- 按时长范围筛选
- 支持组合筛选

### 4. 录像播放（支持倍速）
- HTTP Range 流式播放
- 支持倍速播放（0.5x, 0.75x, 1x, 1.25x, 1.5x, 2x）
- 进度条拖拽
- 音量控制
- 全屏播放
- 自动缓冲显示

### 5. 录像片段剪辑
- 基于时间戳创建片段
- 片段元数据管理
- 片段列表查询
- 支持片段独立播放

### 6. 录像分享功能
- 生成分享令牌
- 自定义过期时间
- 分享链接访问
- 分享次数统计

## API 接口

### 基础 URL
```
/api/playback
```

### 录像管理

#### 获取录像列表
```
GET /api/playback/recordings?limit=20&offset=0
```

#### 搜索录像
```
GET /api/playback/recordings/search?query=关键词&categories=游戏，直播&tags=精彩&streamer=主播&date_from=2024-01-01&date_to=2024-12-31&min_duration=1000&max_duration=7200&limit=20&offset=0
```

#### 获取录像详情
```
GET /api/playback/recordings/{recording_id}
```

#### 上传录像
```
POST /api/playback/recordings?title=标题&streamer=主播&duration=3600&categories=游戏，直播&tags=精彩&description=描述
Content-Type: multipart/form-data

file: (视频文件)
thumbnail: (缩略图，可选)
```

#### 更新录像
```
PUT /api/playback/recordings/{recording_id}
Content-Type: application/json

{
  "title": "新标题",
  "description": "新描述",
  "categories": ["新分类"],
  "tags": ["新标签"],
  "is_public": true
}
```

#### 删除录像
```
DELETE /api/playback/recordings/{recording_id}
```

### 视频播放

#### 流式播放录像
```
GET /api/playback/recordings/{recording_id}/stream
Headers: Range: bytes=0-
```

#### 获取缩略图
```
GET /api/playback/recordings/{recording_id}/thumbnail
```

### 片段剪辑

#### 获取片段列表
```
GET /api/playback/recordings/{recording_id}/clips
```

#### 创建片段
```
POST /api/playback/clips
Content-Type: application/json

{
  "recording_id": "录像 ID",
  "start_time": 100.5,
  "end_time": 200.5,
  "title": "片段标题",
  "description": "片段描述"
}
```

#### 流式播放片段
```
GET /api/playback/clips/{clip_id}/stream
```

### 分享功能

#### 生成分享链接
```
POST /api/playback/share
Content-Type: application/json

{
  "recording_id": "录像 ID",
  "expire_hours": 24
}
```

#### 通过分享令牌获取录像
```
GET /api/playback/share/{share_token}
```

#### 流式播放分享的录像
```
GET /api/playback/share/{share_token}/stream
```

### 统计和元数据

#### 获取统计信息
```
GET /api/playback/statistics
```

#### 获取所有分类
```
GET /api/playback/categories
```

#### 获取所有标签
```
GET /api/playback/tags
```

## 前端组件

### VideoPlayer 组件

位置：`frontend/src/components/VideoPlayer.vue`

#### Props
- `videoSrc`: 视频 URL（必填）
- `poster`: 封面图 URL
- `aspectRatio`: 宽高比，默认 '16/9'
- `autoplay`: 是否自动播放
- `showControls`: 是否显示控制栏
- `showClipTools`: 是否显示剪辑工具
- `startTime`: 起始播放时间（秒）
- `playbackRates`: 倍速选项数组

#### Events
- `play`: 播放时触发
- `pause`: 暂停时触发
- `ended`: 播放结束时触发
- `timeupdate`: 时间更新时触发
- `loadedmetadata`: 元数据加载完成时触发
- `error`: 错误时触发
- `clip-create`: 创建片段时触发

#### Methods
- `play()`: 播放
- `pause()`: 暂停
- `seekTo(time)`: 跳转到指定时间
- `setSpeed(speed)`: 设置播放速度
- `getCurrentTime()`: 获取当前时间
- `getDuration()`: 获取总时长
- `isPlaying()`: 是否正在播放

### Playback 页面

位置：`frontend/src/views/Playback.vue`

功能：
- 录像列表展示（网格布局）
- 搜索和筛选
- 统计信息卡片
- 录像上传
- 录像播放
- 片段剪辑
- 分享功能

## 测试

### 运行测试
```bash
cd backend
python -m pytest tests/test_playback.py -v
```

### 测试覆盖
- ✅ 录像存储测试
- ✅ 录像播放测试
- ✅ 片段剪辑测试
- ✅ 分享功能测试
- ✅ 搜索和筛选测试
- ✅ 分类和标签测试
- ✅ 统计信息测试
- ✅ API 接口测试

## 数据存储

### 目录结构
```
storage/
├── recordings/
│   ├── {recording_id}.mp4          # 视频文件
│   ├── {recording_id}_thumb.jpg    # 缩略图
│   └── metadata/
│       └── {recording_id}.json     # 元数据
└── clips/
    └── {recording_id}_{clip_id}.json  # 片段元数据
```

### 元数据格式
```json
{
  "id": "uuid",
  "title": "标题",
  "streamer": "主播",
  "duration": 3600,
  "categories": ["游戏", "直播"],
  "tags": ["精彩", "回放"],
  "description": "描述",
  "file_path": "路径",
  "file_name": "文件名",
  "file_size": 12345678,
  "thumbnail_path": "缩略图路径",
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00",
  "view_count": 0,
  "share_count": 0,
  "is_public": false,
  "share_token": null
}
```

## 使用示例

### Python SDK 示例
```python
from services.playback import get_playback_service

# 获取服务实例
service = get_playback_service()

# 添加录像
recording = service.add_recording(
    file_path="./video.mp4",
    title="精彩直播回放",
    streamer="主播名称",
    duration=3600,
    categories=["游戏"],
    tags=["LOL", "精彩"],
    description="这是一场精彩的直播"
)

# 搜索录像
results = service.search_recordings(
    query="LOL",
    categories=["游戏"],
    limit=10
)

# 创建片段
clip = service.create_clip(
    recording_id=recording['id'],
    start_time=100.5,
    end_time=200.5,
    title="高光时刻"
)

# 生成分享链接
token = service.generate_share_token(recording['id'], expire_hours=24)

# 获取统计信息
stats = service.get_statistics()
print(f"总录像数：{stats['total_recordings']}")
print(f"总观看次数：{stats['total_views']}")
```

### 前端使用示例
```vue
<template>
  <VideoPlayer
    :video-src="videoUrl"
    :show-clip-tools="true"
    @clip-create="handleClipCreate"
  />
</template>

<script setup>
import VideoPlayer from '@/components/VideoPlayer.vue'

const videoUrl = '/api/playback/recordings/xxx/stream'

const handleClipCreate = ({ startTime, endTime, duration }) => {
  console.log('创建片段:', { startTime, endTime, duration })
}
</script>
```

## 注意事项

1. **文件大小**: 上传大文件时注意服务器存储限制
2. **格式支持**: 视频格式取决于浏览器支持（推荐 MP4）
3. **分享安全**: 分享令牌有过期时间，注意及时更新
4. **性能优化**: 大量录像时建议使用分页和缓存
5. **备份**: 定期备份 storage 目录数据
