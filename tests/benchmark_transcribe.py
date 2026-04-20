#!/usr/bin/env python3
"""
LiveMirror Whisper 转写性能测试脚本
测试不同模型的转写速度和性能
"""

import time
import sys
import json
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

def benchmark_transcribe(model_size: str, audio_path: str, language: str = "zh") -> dict:
    """
    测试单个模型的转写性能
    
    Args:
        model_size: 模型大小 (tiny, base, small, medium, large)
        audio_path: 音频文件路径
        language: 语言代码
    
    Returns:
        性能数据字典
    """
    print(f"\n{'='*60}")
    print(f"测试模型：{model_size}")
    print(f"音频文件：{audio_path}")
    print(f"{'='*60}")
    
    try:
        from faster_whisper import WhisperModel
        
        # 记录开始时间
        start_time = time.time()
        
        # 加载模型（包含下载和加载时间）
        print(f"[{time.time() - start_time:.2f}s] 开始加载模型...")
        model = WhisperModel(
            model_size,
            device="cpu",
            compute_type="int8",
            num_workers=1
        )
        model_load_time = time.time() - start_time
        print(f"[{model_load_time:.2f}s] 模型加载完成")
        
        # 转写音频
        transcribe_start = time.time()
        print(f"[{model_load_time + transcribe_start - start_time:.2f}s] 开始转写...")
        
        segments, info = model.transcribe(
            audio_path,
            language=language,
            beam_size=5,
            vad_filter=True
        )
        
        # 收集结果
        text_segments = []
        for segment in segments:
            text_segments.append(segment.text)
        
        transcribe_time = time.time() - transcribe_start
        total_time = time.time() - start_time
        
        full_text = "".join(text_segments)
        
        # 性能数据
        results = {
            "model_size": model_size,
            "audio_path": audio_path,
            "language": language,
            "model_load_time": round(model_load_time, 2),
            "transcribe_time": round(transcribe_time, 2),
            "total_time": round(total_time, 2),
            "text_length": len(full_text),
            "text_preview": full_text[:100] + "..." if len(full_text) > 100 else full_text
        }
        
        print(f"\n{'='*60}")
        print(f"转写完成!")
        print(f"  模型加载时间：{model_load_time:.2f}s")
        print(f"  转写时间：{transcribe_time:.2f}s")
        print(f"  总时间：{total_time:.2f}s")
        print(f"  转写文本长度：{len(full_text)} 字符")
        print(f"  文本预览：{results['text_preview']}")
        print(f"{'='*60}")
        
        return results
        
    except ImportError as e:
        print(f"错误：需要安装 faster-whisper: pip install faster-whisper")
        return {"error": str(e)}
    except Exception as e:
        print(f"错误：{e}")
        return {"error": str(e)}


def run_benchmark_suite(audio_path: str, models: list = None):
    """
    运行完整的性能测试套件
    
    Args:
        audio_path: 音频文件路径
        models: 要测试的模型列表
    """
    if models is None:
        models = ["tiny", "base"]
    
    all_results = []
    
    print("\n" + "="*60)
    print("LiveMirror Whisper 转写性能测试")
    print("="*60)
    
    for model in models:
        result = benchmark_transcribe(model, audio_path)
        if "error" not in result:
            all_results.append(result)
    
    # 生成对比报告
    if len(all_results) > 1:
        print("\n" + "="*60)
        print("性能对比报告")
        print("="*60)
        print(f"{'模型':<10} {'加载时间':<12} {'转写时间':<12} {'总时间':<12} {'文本长度':<10}")
        print("-"*60)
        for r in all_results:
            print(f"{r['model_size']:<10} {r['model_load_time']:<12.2f} {r['transcribe_time']:<12.2f} {r['total_time']:<12.2f} {r['text_length']:<10}")
        
        # 计算加速比
        base_result = next((r for r in all_results if r['model_size'] == 'base'), None)
        tiny_result = next((r for r in all_results if r['model_size'] == 'tiny'), None)
        
        if base_result and tiny_result:
            speedup = base_result['transcribe_time'] / tiny_result['transcribe_time']
            print(f"\ntiny 相比 base 加速：{speedup:.2f}x")
            print(f"tiny 转写时间节省：{base_result['transcribe_time'] - tiny_result['transcribe_time']:.2f}s")
    
    # 保存结果
    report_path = Path(__file__).parent / "benchmark_results.json"
    with open(report_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"\n结果已保存到：{report_path}")
    
    return all_results


if __name__ == "__main__":
    # 默认测试文件
    default_audio = Path(__file__).parent.parent / "test_audio" / "live_streaming_demo.mp3"
    
    # 从命令行参数获取音频路径
    if len(sys.argv) > 1:
        audio_path = sys.argv[1]
    else:
        audio_path = str(default_audio)
    
    # 检查文件是否存在
    if not Path(audio_path).exists():
        print(f"错误：音频文件不存在：{audio_path}")
        print(f"请将测试音频文件放在：{default_audio}")
        sys.exit(1)
    
    # 运行测试
    run_benchmark_suite(audio_path)
