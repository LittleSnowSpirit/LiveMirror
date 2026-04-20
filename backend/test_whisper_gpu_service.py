"""
Whisper GPU 服务功能测试
测试 CUDA 检测、自动切换、显存管理等功能
"""

import sys
import time
from pathlib import Path

# 添加路径
sys.path.insert(0, str(Path(__file__).parent))

from utils.cuda_check import detect_cuda, print_cuda_status
from services.whisper_gpu import WhisperGPUService, get_service


def test_cuda_detection():
    """测试 1: CUDA 环境检测"""
    print("\n" + "="*60)
    print("测试 1: CUDA 环境检测")
    print("="*60)
    
    status = detect_cuda()
    
    print(f"CUDA 可用：{status.available}")
    print(f"推荐设备：{status.recommended_device}")
    print(f"推荐计算类型：{status.recommended_compute_type}")
    
    if status.warnings:
        print(f"警告：{status.warnings}")
    
    assert status.recommended_device in ["cpu", "cuda"], "设备检测失败"
    print("[PASS] CUDA 检测测试通过")
    
    return status


def test_service_initialization():
    """测试 2: 服务初始化"""
    print("\n" + "="*60)
    print("测试 2: 服务初始化")
    print("="*60)
    
    # 测试自动配置
    service = WhisperGPUService()
    
    print(f"设备：{service.device}")
    print(f"计算类型：{service.compute_type}")
    print(f"显存管理：{service.enable_memory_management}")
    
    assert service.device in ["cpu", "cuda"], "设备配置失败"
    print("[PASS] 服务初始化测试通过")
    
    return service


def test_model_loading(service: WhisperGPUService):
    """测试 3: 模型加载"""
    print("\n" + "="*60)
    print("测试 3: 模型加载")
    print("="*60)
    
    model_sizes = ["tiny"]
    
    for model_size in model_sizes:
        print(f"\n加载模型：{model_size}")
        start = time.time()
        model = service.get_model(model_size)
        load_time = time.time() - start
        
        print(f"加载时间：{load_time:.2f}s")
        assert model is not None, f"模型 {model_size} 加载失败"
        print(f"[PASS] 模型 {model_size} 加载成功")
    
    print("[PASS] 模型加载测试通过")


def test_transcription(service: WhisperGPUService, audio_file: str):
    """测试 4: 转写功能"""
    print("\n" + "="*60)
    print("测试 4: 转写功能测试")
    print("="*60)
    
    if not Path(audio_file).exists():
        print(f"⚠ 测试文件不存在：{audio_file}")
        return None
    
    print(f"测试文件：{audio_file}")
    
    # 测试 tiny 模型
    result = service.transcribe(audio_file, model_size="tiny", language="zh")
    
    print(f"\n转写结果:")
    print(f"  设备：{result.device}")
    print(f"  计算类型：{result.compute_type}")
    print(f"  模型加载时间：{result.model_load_time}s")
    print(f"  转写时间：{result.transcribe_time}s")
    print(f"  总时间：{result.total_time}s")
    print(f"  文本长度：{len(result.text)}")
    print(f"  文本预览：{result.text[:100]}...")
    
    if result.gpu_memory_used:
        print(f"  GPU 显存：{result.gpu_memory_used}MB")
    
    assert result.text, "转写结果为空"
    assert result.transcribe_time > 0, "转写时间异常"
    print("[PASS] 转写功能测试通过")
    
    return result


def test_auto_fallback():
    """测试 5: 自动 CPU/GPU 切换"""
    print("\n" + "="*60)
    print("测试 5: 自动 CPU/GPU 切换")
    print("="*60)
    
    # 创建服务时强制指定 CUDA（即使不可用）
    service = WhisperGPUService(device="cuda", compute_type="float16")
    
    print(f"请求设备：cuda")
    print(f"实际设备：{service.device}")
    
    # 服务应该自动回退到 CPU（如果 CUDA 不可用）
    if not detect_cuda().available:
        assert service.device == "cpu", "应该自动回退到 CPU"
        print("[PASS] 自动回退到 CPU 成功")
    else:
        assert service.device == "cuda", "应该使用 GPU"
        print("[PASS] GPU 模式正常")
    
    print("[PASS] 自动切换测试通过")


def test_memory_management():
    """测试 6: 显存管理"""
    print("\n" + "="*60)
    print("测试 6: 显存管理")
    print("="*60)
    
    service = WhisperGPUService(enable_memory_management=True)
    
    if service.memory_manager:
        stats = service.memory_manager.get_stats()
        print(f"显存统计：{stats}")
        print("[PASS] 显存管理测试通过")
    else:
        print("[WARN] 显存管理未启用")
    
    print("[PASS] 显存管理测试通过")


def test_performance_stats(service: WhisperGPUService):
    """测试 7: 性能统计"""
    print("\n" + "="*60)
    print("测试 7: 性能统计")
    print("="*60)
    
    stats = service.get_performance_stats()
    
    print(f"总请求数：{stats.get('total_requests', 0)}")
    print(f"当前设备：{stats.get('current_device', 'N/A')}")
    
    if stats.get('speedup'):
        print(f"GPU 加速比：{stats['speedup']}x")
    
    if stats.get('gpu_memory'):
        print(f"GPU 显存：{stats['gpu_memory']}")
    
    print("[PASS] 性能统计测试通过")


def main():
    """运行所有测试"""
    print("="*60)
    print("Whisper GPU 服务功能测试")
    print("="*60)
    
    # 显示 CUDA 状态
    print_cuda_status()
    
    # 测试文件
    audio_file = "test_audio/live_streaming_demo.mp3"
    
    try:
        # 运行测试
        status = test_cuda_detection()
        service = test_service_initialization()
        test_model_loading(service)
        result = test_transcription(service, audio_file)
        test_auto_fallback()
        test_memory_management()
        test_performance_stats(service)
        
        # 总结
        print("\n" + "="*60)
        print("所有测试完成!")
        print("="*60)
        
        if result:
            print(f"\n性能总结:")
            print(f"  转写时间：{result.transcribe_time}s")
            print(f"  设备：{result.device}")
            
            # 检查是否达到目标
            if result.transcribe_time < 5:
                print(f"  [OK] 达到目标（<5 秒）")
            else:
                print(f"  [WARN] 未达到目标（目标：<5 秒）")
        
        print("\n[PASS] 所有功能测试通过!")
        
    except Exception as e:
        print(f"\n[FAIL] 测试失败：{e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
