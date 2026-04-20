#!/usr/bin/env python3
"""
LiveMirror 多时长音频性能测试
测试不同时长音频的转写性能
"""

import sys
import json
import time
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.services.whisper import WhisperService, TranscribeResult


def create_test_segments(audio_path: str, durations: list = [10, 30, 60, 96]):
    """
    使用 ffmpeg 创建不同时长的测试音频片段
    
    Args:
        audio_path: 源音频文件路径
        durations: 时长列表（秒）
    
    Returns:
        生成的音频文件路径列表
    """
    import subprocess
    
    generated_files = []
    audio_path = Path(audio_path)
    
    for duration in durations:
        output_path = audio_path.parent / f"test_{duration}s.mp3"
        
        # 使用 ffmpeg 截取音频片段
        cmd = [
            "ffmpeg",
            "-y",  # 覆盖输出
            "-i", str(audio_path),
            "-t", str(duration),
            "-c", "copy",
            str(output_path)
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            generated_files.append((duration, str(output_path)))
            print(f"✓ 生成 {duration}s 测试音频：{output_path.name}")
        except subprocess.CalledProcessError as e:
            print(f"✗ 生成 {duration}s 音频失败：{e}")
        except FileNotFoundError:
            print(f"[WARN] ffmpeg 未安装，跳过音频切片测试")
            return []
    
    return generated_files


def test_multiple_durations(service: WhisperService, test_files: list, model_size: str = "tiny"):
    """
    测试不同时长的音频转写性能
    
    Args:
        service: Whisper 服务实例
        test_files: (时长，文件路径) 列表
        model_size: 模型大小
    """
    results = []
    
    print(f"\n{'='*70}")
    print(f"多时长音频性能测试 - 模型：{model_size}")
    print(f"{'='*70}")
    
    # 预热模型（先转写一次）
    if test_files:
        print(f"\n[预热] 加载模型...")
        service.transcribe(test_files[0][1], model_size)
        print(f"[预热完成] 模型已加载到缓存\n")
    
    for duration, audio_path in test_files:
        print(f"\n测试 {duration}s 音频...")
        result = service.transcribe(audio_path, model_size)
        
        # 计算实时率（RTF = 转写时间 / 音频时长）
        rtf = result.transcribe_time / duration
        
        results.append({
            "duration_seconds": duration,
            "audio_path": audio_path,
            "model_load_time": result.model_load_time,
            "transcribe_time": result.transcribe_time,
            "total_time": result.total_time,
            "text_length": len(result.text),
            "rtf": round(rtf, 3),
            "text_preview": result.text[:50] + "..." if len(result.text) > 50 else result.text
        })
        
        print(f"  加载时间：{result.model_load_time:.2f}s")
        print(f"  转写时间：{result.transcribe_time:.2f}s")
        print(f"  实时率 (RTF): {rtf:.3f}")
        print(f"  文本长度：{len(result.text)} 字符")
    
    return results


def generate_report(results: list, output_path: str = "tests/multi_duration_report.json"):
    """
    生成性能测试报告
    
    Args:
        results: 测试结果列表
        output_path: 输出文件路径
    """
    report = {
        "test_timestamp": datetime.now().isoformat(),
        "test_type": "multi_duration_benchmark",
        "results": results,
        "summary": {}
    }
    
    if results:
        # 计算统计
        total_duration = sum(r["duration_seconds"] for r in results)
        total_transcribe_time = sum(r["transcribe_time"] for r in results)
        avg_rtf = sum(r["rtf"] for r in results) / len(results)
        
        report["summary"] = {
            "total_audio_duration": total_duration,
            "total_transcribe_time": round(total_transcribe_time, 2),
            "average_rtf": round(avg_rtf, 3),
            "fastest_rtf": min(r["rtf"] for r in results),
            "slowest_rtf": max(r["rtf"] for r in results),
            "target_rtf": 0.5,  # 目标：转写时间 < 音频时长的一半
            "meets_target": avg_rtf < 0.5
        }
    
    # 保存报告
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n{'='*70}")
    print(f"测试报告已保存到：{output_path}")
    print(f"{'='*70}")
    
    if report["summary"]:
        print(f"\n摘要:")
        print(f"  总音频时长：{total_duration}s")
        print(f"  总转写时间：{total_transcribe_time:.2f}s")
        print(f"  平均实时率：{avg_rtf:.3f}")
        meets = "[PASS]" if report['summary']['meets_target'] else "[FAIL]"
        print(f"  是否达标：{meets} (目标 RTF < 0.5)")
    
    return report


if __name__ == "__main__":
    # 测试音频路径
    audio_file = "test_audio/live_streaming_demo.mp3"
    
    if not Path(audio_file).exists():
        print(f"错误：音频文件不存在：{audio_file}")
        sys.exit(1)
    
    # 创建服务实例
    service = WhisperService(device="cpu", compute_type="int8")
    
    # 创建测试音频片段
    print("生成测试音频片段...")
    test_files = create_test_segments(audio_file, [10, 30, 60, 96])
    
    if not test_files:
        # 如果没有 ffmpeg，使用原始文件
        print("使用原始音频文件进行测试...")
        test_files = [(96, audio_file)]
    
    # 测试 tiny 模型
    tiny_results = test_multiple_durations(service, test_files, "tiny")
    
    # 测试 base 模型
    print(f"\n\n")
    base_results = test_multiple_durations(service, test_files, "base")
    
    # 生成报告
    generate_report(tiny_results, "tests/tiny_duration_report.json")
    generate_report(base_results, "tests/base_duration_report.json")
    
    # 保存性能日志
    service.save_performance_log("tests/whisper_performance_log.json")
    
    print("\n✓ 所有测试完成!")
