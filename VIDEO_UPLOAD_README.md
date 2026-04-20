# LiveMirror 视频上传功能

## 功能概述

支持视频文件上传，自动提取音频进行转写分析。

### 支持特性

- ✅ 支持视频格式：MP4, AVI, MOV, MKV
- ✅ 使用 ffmpeg 提取音频
- ✅ 视频文件大小限制：最大 2GB
- ✅ 后端接口：POST /api/upload/video
- ✅ 前端支持视频拖拽上传
- ✅ 显示视频时长和文件大小
- ✅ 自动音频转写分析

## 依赖安装

### 1. 安装 FFmpeg

FFmpeg 是视频处理的核心依赖，用于音频提取。

#### Windows

```powershell
# 使用 Chocolatey
choco install ffmpeg

# 或使用 Scoop
scoop install ffmpeg
```

#### macOS

```bash
# 使用 Homebrew
brew install ffmpeg
```

#### Linux

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install ffmpeg

# CentOS/RHEL
sudo yum install ffmpeg
```

#### 验证安装

```bash
ffmpeg -version
ffprobe -version
```

### 2. 安装 Python 依赖

```bash
cd LiveMirror/backend
pip install -r requirements.txt
```

## API 接口

### 上传视频

```http
POST /api/upload/video
Content-Type: multipart/form-data

file: <video_file>
```

**响应示例：**

```json
{
  "success": true,
  "message": "视频上传成功",
  "video_id": "20260408_180000_demo",
  "filename": "demo.mp4",
  "file_size": 10485760,
  "duration": 120.5,
  "format": "mp4",
  "audio_extracted": true,
  "audio_path": "C:\\temp\\livemirror_video\\20260408_180000_demo.wav",
  "processing_time": 3.45
}
```

### 获取视频信息

```http
GET /api/upload/video/{video_id}
```

### 转写视频

```http
POST /api/upload/video/{video_id}/transcribe
Content-Type: application/json

{
  "model_size": "tiny",
  "language": "zh"
}
```

### 删除视频

```http
DELETE /api/upload/video/{video_id}
```

### 获取支持的格式

```http
GET /api/upload/supported-formats
```

## 前端组件

### VideoUploader 组件

```vue
<template>
  <VideoUploader
    :upload-url="'/api/upload/video'"
    :max-file-size="2048"
    :auto-transcribe="true"
    @upload-success="handleUploadSuccess"
    @upload-error="handleUploadError"
    @transcription-complete="handleTranscriptionComplete"
  />
</template>

<script setup>
import VideoUploader from '@/components/VideoUploader.vue'

const handleUploadSuccess = (response) => {
  console.log('上传成功:', response)
}

const handleUploadError = (error) => {
  console.error('上传失败:', error)
}

const handleTranscriptionComplete = (transcription) => {
  console.log('转写完成:', transcription)
}
</script>
```

## 测试

### 运行测试脚本

```bash
cd LiveMirror/backend
python test_video_upload.py [video_path]
```

如果不提供视频路径，脚本会自动查找测试视频。

### 测试项目

1. ✅ FFmpeg 可用性检查
2. ✅ 视频文件验证
3. ✅ 获取视频信息
4. ✅ 音频提取
5. ✅ 音频转写
6. ✅ 完整流程测试
7. ✅ 多格式支持测试

### 创建测试视频

如果没有测试视频，可以使用 ffmpeg 生成：

```bash
# 生成 10 秒的测试视频（带音频）
ffmpeg -f lavfi -i testsrc=duration=10:size=640x480:rate=30 \
       -f lavfi -i sine=frequency=440:duration=10 \
       -c:v libx264 -c:a aac \
       test_video.mp4
```

## 后端服务集成

### 1. 注册路由

在 `main.py` 中添加：

```python
from routes.video_upload import router as video_upload_router

app.include_router(video_upload_router)
```

### 2. 启动服务

```bash
cd LiveMirror/backend
python main.py
```

服务将在 `http://localhost:8001` 启动。

### 3. API 文档

访问 `http://localhost:8001/docs` 查看 Swagger API 文档。

## 文件结构

```
LiveMirror/
├── backend/
│   ├── routes/
│   │   └── video_upload.py      # 视频上传路由
│   ├── services/
│   │   └── video.py             # 视频处理服务
│   │   └── whisper.py           # Whisper 转写服务
│   ├── test_video_upload.py     # 测试脚本
│   └── main.py                  # 应用入口
├── frontend/
│   └── src/
│       └── components/
│           └── VideoUploader.vue  # 视频上传组件
└── VIDEO_UPLOAD_README.md       # 本文档
```

## 性能优化

### 音频提取优化

- 使用 16kHz 采样率（适合 Whisper）
- 单声道输出（减少文件大小）
- WAV 格式（无损，适合转写）

### 转写优化

- 使用 faster-whisper（比原始 whisper 快 4 倍）
- 模型缓存（避免重复加载）
- VAD 过滤（提高准确度）

### 文件大小限制

- 最大 2GB 视频文件
- 前端和后端双重验证
- 清晰的错误提示

## 常见问题

### Q: ffmpeg 未找到

**A:** 请按照上述步骤安装 ffmpeg，并确保添加到系统 PATH。

### Q: 视频上传失败

**A:** 检查：
1. 文件大小是否超过 2GB
2. 视频格式是否支持（MP4/AVI/MOV/MKV）
3. 视频是否包含音频轨道
4. 视频文件是否损坏

### Q: 转写速度慢

**A:** 可以尝试：
1. 使用更小的模型（tiny 比 base 快）
2. 在 GPU 上运行（需要 CUDA 支持）
3. 减少音频长度

## 下一步

- [ ] 添加视频缩略图生成
- [ ] 支持批量视频上传
- [ ] 添加视频播放功能
- [ ] 转写结果编辑和导出
- [ ] 支持更多视频格式
