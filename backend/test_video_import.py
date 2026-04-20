"""
视频上传功能导入测试
测试代码导入和基本功能，不需要实际视频文件
"""

import sys
import os

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("="*60)
print("LiveMirror 视频上传功能导入测试")
print("="*60)

# 测试 1: 导入视频服务
print("\n测试 1: 导入视频服务模块...")
try:
    from services.video import VideoService, get_service, VideoInfo, VideoProcessResult
    print("[OK] 视频服务模块导入成功")
    print(f"  支持格式：{VideoService.SUPPORTED_FORMATS}")
    print(f"  最大文件大小：{VideoService.MAX_FILE_SIZE / (1024*1024*1024):.0f}GB")
except Exception as e:
    print(f"[FAIL] 视频服务模块导入失败：{e}")
    sys.exit(1)

# 测试 2: 导入视频上传路由
print("\n测试 2: 导入视频上传路由模块...")
try:
    from routes.video_upload import router, UPLOAD_DIR, MAX_FILE_SIZE, SUPPORTED_FORMATS
    print("[OK] 视频上传路由模块导入成功")
    print(f"  上传目录：{UPLOAD_DIR}")
    print(f"  路由前缀：{router.prefix}")
except Exception as e:
    print(f"[FAIL] 视频上传路由模块导入失败：{e}")
    sys.exit(1)

# 测试 3: 检查路由对象
print("\n测试 3: 检查路由对象...")
try:
    print("[OK] 路由对象创建成功")
    print(f"  路由前缀：{router.prefix}")
    print(f"  路由标签：{router.tags}")
except Exception as e:
    print(f"[FAIL] 路由对象检查失败：{e}")
    sys.exit(1)

# 测试 4: 检查 Whisper 转写服务
print("\n测试 4: 导入 Whisper 转写服务...")
try:
    from services.whisper_transcribe import get_service as get_whisper_service
    print("[OK] Whisper 转写服务模块导入成功")
except Exception as e:
    print(f"[FAIL] Whisper 转写服务模块导入失败：{e}")
    sys.exit(1)

# 测试 5: 检查数据模型
print("\n测试 5: 检查 Pydantic 模型...")
try:
    from routes.video_upload import VideoUploadResponse, VideoInfo as VideoInfoModel, TranscriptionRequest
    print("[OK] Pydantic 模型导入成功")
    print(f"  VideoUploadResponse 字段：{list(VideoUploadResponse.model_fields.keys())}")
except Exception as e:
    print(f"[FAIL] Pydantic 模型导入失败：{e}")
    sys.exit(1)

print("\n" + "="*60)
print("[SUCCESS] 所有导入测试通过！")
print("="*60)
print("\n注意：FFmpeg 未安装，实际视频处理功能需要安装 FFmpeg")
print("安装方法：")
print("  Windows: choco install ffmpeg")
print("  macOS: brew install ffmpeg")
print("  Linux: sudo apt install ffmpeg")
print("\n前端组件位置：")
print("  LiveMirror/frontend/src/components/VideoUploader.vue")
print("\nAPI 文档：")
print("  启动服务后访问 http://localhost:8001/docs")
