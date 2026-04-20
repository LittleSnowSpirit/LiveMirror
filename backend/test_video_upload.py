"""
视频上传功能测试脚本
测试视频上传、音频提取、转写流程
"""

import sys
import os
import time
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from services.video import VideoService, get_service


def test_ffmpeg_availability():
    """测试 ffmpeg 是否可用"""
    print("="*60)
    print("测试 1: FFmpeg 可用性检查")
    print("="*60)
    
    try:
        service = get_service()
        print("✓ FFmpeg 检查通过")
        return True
    except RuntimeError as e:
        print(f"✗ FFmpeg 检查失败：{e}")
        return False


def test_video_validation(video_path):
    """测试视频验证"""
    print("\n" + "="*60)
    print("测试 2: 视频文件验证")
    print("="*60)
    
    service = get_service()
    
    # 检查文件是否存在
    if not Path(video_path).exists():
        print(f"✗ 视频文件不存在：{video_path}")
        return False
    
    # 验证视频
    is_valid, error = service.validate_video(video_path)
    
    if is_valid:
        print(f"✓ 视频验证通过")
        return True
    else:
        print(f"✗ 视频验证失败：{error}")
        return False


def test_video_info(video_path):
    """测试获取视频信息"""
    print("\n" + "="*60)
    print("测试 3: 获取视频信息")
    print("="*60)
    
    service = get_service()
    
    try:
        info = service.get_video_info(video_path)
        
        print(f"✓ 视频信息获取成功")
        print(f"  文件名：{info.filename}")
        print(f"  大小：{info.file_size / (1024*1024):.2f} MB")
        print(f"  时长：{info.duration:.2f}s")
        print(f"  格式：{info.format}")
        print(f"  分辨率：{info.width}x{info.height}")
        print(f"  视频编码：{info.video_codec}")
        print(f"  音频编码：{info.audio_codec}")
        print(f"  有音频：{info.has_audio}")
        
        return True
        
    except Exception as e:
        print(f"✗ 获取视频信息失败：{e}")
        return False


def test_audio_extraction(video_path):
    """测试音频提取"""
    print("\n" + "="*60)
    print("测试 4: 音频提取")
    print("="*60)
    
    service = get_service()
    
    try:
        start_time = time.time()
        audio_path = service.extract_audio(video_path)
        elapsed = time.time() - start_time
        
        # 验证音频文件
        if Path(audio_path).exists():
            audio_size = Path(audio_path).stat().st_size
            print(f"✓ 音频提取成功")
            print(f"  输出路径：{audio_path}")
            print(f"  音频大小：{audio_size / (1024*1024):.2f} MB")
            print(f"  提取耗时：{elapsed:.2f}s")
            return True, audio_path
        else:
            print(f"✗ 音频文件未生成")
            return False, None
            
    except Exception as e:
        print(f"✗ 音频提取失败：{e}")
        return False, None


def test_transcription(audio_path):
    """测试音频转写"""
    print("\n" + "="*60)
    print("测试 5: 音频转写")
    print("="*60)
    
    if not audio_path or not Path(audio_path).exists():
        print("✗ 音频文件不存在，跳过转写测试")
        return False
    
    try:
        from services.whisper import get_service as get_whisper_service
        
        whisper_service = get_whisper_service()
        
        start_time = time.time()
        result = whisper_service.transcribe(
            audio_path,
            model_size="tiny",
            language="zh"
        )
        elapsed = time.time() - start_time
        
        print(f"✓ 转写成功")
        print(f"  模型：{result.model_size}")
        print(f"  语言：{result.language}")
        print(f"  加载时间：{result.model_load_time}s")
        print(f"  转写时间：{result.transcribe_time}s")
        print(f"  总耗时：{result.total_time}s")
        print(f"  文本长度：{len(result.text)}")
        print(f"\n  文本预览：{result.text[:200]}...")
        
        return True
        
    except Exception as e:
        print(f"✗ 转写失败：{e}")
        return False


def test_full_pipeline(video_path):
    """测试完整流程"""
    print("\n" + "="*60)
    print("测试 6: 完整流程测试")
    print("="*60)
    
    service = get_service()
    
    try:
        start_time = time.time()
        result = service.process_video(video_path, extract_audio=True)
        total_time = time.time() - start_time
        
        if result.success:
            print(f"✓ 完整流程成功")
            print(f"  总耗时：{total_time:.2f}s")
            print(f"  视频信息：{result.video_info.filename}")
            print(f"  音频路径：{result.audio_path}")
            return True
        else:
            print(f"✗ 完整流程失败：{result.error_message}")
            return False
            
    except Exception as e:
        print(f"✗ 完整流程失败：{e}")
        return False


def test_multiple_formats():
    """测试多种视频格式"""
    print("\n" + "="*60)
    print("测试 7: 多格式支持测试")
    print("="*60)
    
    service = get_service()
    supported_formats = service.SUPPORTED_FORMATS
    
    print(f"支持的视频格式：{', '.join(supported_formats)}")
    print(f"最大文件大小：{service.MAX_FILE_SIZE / (1024*1024*1024):.0f}GB")
    
    return True


def run_all_tests(video_path=None):
    """运行所有测试"""
    print("\n" + "="*60)
    print("LiveMirror 视频上传功能测试")
    print("="*60)
    
    results = {
        "ffmpeg": False,
        "validation": False,
        "info": False,
        "extraction": False,
        "transcription": False,
        "pipeline": False,
        "formats": False
    }
    
    # 测试 1: FFmpeg 可用性
    results["ffmpeg"] = test_ffmpeg_availability()
    
    if not results["ffmpeg"]:
        print("\n✗ FFmpeg 不可用，无法继续测试")
        return results
    
    # 如果有视频文件，进行完整测试
    if video_path and Path(video_path).exists():
        # 测试 2: 视频验证
        results["validation"] = test_video_validation(video_path)
        
        if results["validation"]:
            # 测试 3: 获取视频信息
            results["info"] = test_video_info(video_path)
            
            # 测试 4: 音频提取
            extraction_success, audio_path = test_audio_extraction(video_path)
            results["extraction"] = extraction_success
            
            if extraction_success and audio_path:
                # 测试 5: 音频转写
                results["transcription"] = test_transcription(audio_path)
            
            # 测试 6: 完整流程
            results["pipeline"] = test_full_pipeline(video_path)
    
    # 测试 7: 多格式支持
    results["formats"] = test_multiple_formats()
    
    # 汇总结果
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    test_names = {
        "ffmpeg": "FFmpeg 可用性",
        "validation": "视频验证",
        "info": "视频信息获取",
        "extraction": "音频提取",
        "transcription": "音频转写",
        "pipeline": "完整流程",
        "formats": "多格式支持"
    }
    
    passed = 0
    total = len(results)
    
    for key, success in results.items():
        status = "✓ 通过" if success else "✗ 失败"
        print(f"  {test_names[key]}: {status}")
        if success:
            passed += 1
    
    print(f"\n总计：{passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！视频上传功能正常！")
    else:
        print(f"\n⚠️ 有 {total - passed} 个测试失败，请检查配置")
    
    return results


if __name__ == "__main__":
    # 获取测试视频文件路径
    video_path = None
    
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
    else:
        # 尝试查找测试视频
        test_dirs = [
            Path(__file__).parent.parent / "test_video",
            Path(__file__).parent.parent / "tests",
            Path(__file__).parent.parent / "uploads"
        ]
        
        for test_dir in test_dirs:
            if test_dir.exists():
                video_files = list(test_dir.glob("*.mp4")) + \
                             list(test_dir.glob("*.avi")) + \
                             list(test_dir.glob("*.mov")) + \
                             list(test_dir.glob("*.mkv"))
                
                if video_files:
                    video_path = str(video_files[0])
                    print(f"找到测试视频：{video_path}")
                    break
    
    if video_path:
        run_all_tests(video_path)
    else:
        print("未找到测试视频文件")
        print("用法：python test_video_upload.py <video_path>")
        print("\n运行基础测试...")
        run_all_tests()
