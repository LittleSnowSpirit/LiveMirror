"""
LiveMirror GPU 性能对比测试
测试 CPU vs GPU 转写速度，验证 GPU 加速效果
"""

import time
import sys
import json
from pathlib import Path
from typing import List, Dict
from dataclasses import dataclass
import statistics

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent))

from utils.cuda_check import detect_cuda, print_cuda_status


@dataclass
class TestResult:
    """测试结果数据类"""
    model_size: str
    device: str
    compute_type: str
    audio_duration: float  # 秒
    transcribe_time: float  # 秒
    load_time: float  # 秒
    total_time: float  # 秒
    text_length: int
    speed_factor: float  # 实时因子 (音频时长/转写时间)
    gpu_memory_used: int = 0  # MB


class PerformanceTester:
    """性能对比测试器"""
    
    def __init__(self, audio_file: str):
        """
        Args:
            audio_file: 测试音频文件路径
        """
        self.audio_file = audio_file
        self.results: List[TestResult] = []
        
        # 获取音频时长（使用 ffmpeg 或 mutagen）
        self.audio_duration = self._get_audio_duration()
        
        print(f"测试文件：{audio_file}")
        print(f"音频时长：{self.audio_duration:.2f}s")
    
    def _get_audio_duration(self) -> float:
        """获取音频文件时长（秒）"""
        try:
            # 尝试使用 mutagen
            from mutagen.mp3 import MP3
            from mutagen.wave import WAVE
            from mutagen.mp4 import MP4
            
            path = Path(self.audio_file)
            suffix = path.suffix.lower()
            
            if suffix == '.mp3':
                audio = MP3(self.audio_file)
            elif suffix == '.wav':
                audio = WAVE(self.audio_file)
            elif suffix in ['.mp4', '.m4a']:
                audio = MP4(self.audio_file)
            else:
                # 尝试通用方法
                import mutagen
                audio = mutagen.File(self.audio_file)
            
            if audio and audio.info:
                return float(audio.info.length)
        except Exception as e:
            print(f"⚠ 无法获取音频时长：{e}")
        
        # 默认值
        print("⚠ 使用默认音频时长估计值：96s")
        return 96.0
    
    def test_cpu(self, model_size: str = "tiny", runs: int = 3) -> List[TestResult]:
        """
        测试 CPU 模式
        
        Args:
            model_size: 模型大小
            runs: 运行次数
        
        Returns:
            测试结果列表
        """
        print(f"\n{'='*60}")
        print(f"CPU 模式测试 - 模型：{model_size}")
        print(f"{'='*60}")
        
        results = []
        
        for i in range(runs):
            print(f"\n第 {i+1}/{runs} 次运行...")
            
            # 导入 CPU 服务
            from faster_whisper import WhisperModel
            
            load_start = time.time()
            model = WhisperModel(model_size, device="cpu", compute_type="int8")
            load_time = time.time() - load_start
            
            transcribe_start = time.time()
            segments, info = model.transcribe(
                self.audio_file,
                language="zh",
                beam_size=5,
                vad_filter=True
            )
            
            text = "".join([s.text for s in segments])
            transcribe_time = time.time() - transcribe_start
            total_time = load_time + transcribe_time
            
            result = TestResult(
                model_size=model_size,
                device="cpu",
                compute_type="int8",
                audio_duration=self.audio_duration,
                transcribe_time=transcribe_time,
                load_time=load_time,
                total_time=total_time,
                text_length=len(text),
                speed_factor=round(self.audio_duration / transcribe_time, 2) if transcribe_time > 0 else 0
            )
            
            results.append(result)
            self.results.append(result)
            
            print(f"  加载时间：{load_time:.2f}s")
            print(f"  转写时间：{transcribe_time:.2f}s")
            print(f"  总时间：{total_time:.2f}s")
            print(f"  实时因子：{result.speed_factor}x")
            print(f"  文本长度：{len(text)}")
        
        return results
    
    def test_gpu(self, model_size: str = "tiny", runs: int = 3, compute_type: str = "float16") -> List[TestResult]:
        """
        测试 GPU 模式
        
        Args:
            model_size: 模型大小
            runs: 运行次数
            compute_type: 计算类型
        
        Returns:
            测试结果列表
        """
        if not torch.cuda.is_available():
            print("⚠ CUDA 不可用，跳过 GPU 测试")
            return []
        
        import torch
        from faster_whisper import WhisperModel
        
        print(f"\n{'='*60}")
        print(f"GPU 模式测试 - 模型：{model_size}, 计算类型：{compute_type}")
        print(f"{'='*60}")
        print(f"GPU: {torch.cuda.get_device_name(0)}")
        
        results = []
        
        for i in range(runs):
            print(f"\n第 {i+1}/{runs} 次运行...")
            
            # 清空缓存
            torch.cuda.empty_cache()
            
            load_start = time.time()
            model = WhisperModel(model_size, device="cuda", compute_type=compute_type)
            load_time = time.time() - load_start
            
            # 记录显存使用
            gpu_memory = torch.cuda.memory_allocated() // (1024 * 1024)
            
            transcribe_start = time.time()
            segments, info = model.transcribe(
                self.audio_file,
                language="zh",
                beam_size=5,
                vad_filter=True,
                batch_size=16
            )
            
            text = "".join([s.text for s in segments])
            transcribe_time = time.time() - transcribe_start
            total_time = load_time + transcribe_time
            
            result = TestResult(
                model_size=model_size,
                device="cuda",
                compute_type=compute_type,
                audio_duration=self.audio_duration,
                transcribe_time=transcribe_time,
                load_time=load_time,
                total_time=total_time,
                text_length=len(text),
                speed_factor=round(self.audio_duration / transcribe_time, 2) if transcribe_time > 0 else 0,
                gpu_memory_used=gpu_memory
            )
            
            results.append(result)
            self.results.append(result)
            
            print(f"  加载时间：{load_time:.2f}s")
            print(f"  转写时间：{transcribe_time:.2f}s")
            print(f"  总时间：{total_time:.2f}s")
            print(f"  实时因子：{result.speed_factor}x")
            print(f"  GPU 显存：{gpu_memory}MB")
            print(f"  文本长度：{len(text)}")
        
        return results
    
    def compare_results(self, model_size: str) -> dict:
        """
        对比 CPU 和 GPU 结果
        
        Args:
            model_size: 模型大小
        
        Returns:
            对比统计字典
        """
        cpu_results = [r for r in self.results if r.model_size == model_size and r.device == "cpu"]
        gpu_results = [r for r in self.results if r.model_size == model_size and r.device == "cuda"]
        
        if not cpu_results:
            return {"error": "无 CPU 结果"}
        
        def avg(values):
            return statistics.mean(values) if values else 0
        
        def std(values):
            return statistics.stdev(values) if len(values) > 1 else 0
        
        comparison = {
            "model_size": model_size,
            "cpu": {
                "avg_transcribe_time": round(avg([r.transcribe_time for r in cpu_results]), 2),
                "std_transcribe_time": round(std([r.transcribe_time for r in cpu_results]), 2),
                "avg_total_time": round(avg([r.total_time for r in cpu_results]), 2),
                "avg_speed_factor": round(avg([r.speed_factor for r in cpu_results]), 2),
                "runs": len(cpu_results)
            },
            "gpu": None,
            "speedup": None
        }
        
        if gpu_results:
            comparison["gpu"] = {
                "avg_transcribe_time": round(avg([r.transcribe_time for r in gpu_results]), 2),
                "std_transcribe_time": round(std([r.transcribe_time for r in gpu_results]), 2),
                "avg_total_time": round(avg([r.total_time for r in gpu_results]), 2),
                "avg_speed_factor": round(avg([r.speed_factor for r in gpu_results]), 2),
                "avg_gpu_memory": round(avg([r.gpu_memory_used for r in gpu_results]), 0),
                "runs": len(gpu_results)
            }
            
            if comparison["cpu"]["avg_transcribe_time"] > 0 and comparison["gpu"]["avg_transcribe_time"] > 0:
                comparison["speedup"] = round(
                    comparison["cpu"]["avg_transcribe_time"] / comparison["gpu"]["avg_transcribe_time"],
                    2
                )
        
        return comparison
    
    def print_report(self):
        """打印测试报告"""
        print(f"\n{'='*60}")
        print("性能对比测试报告")
        print(f"{'='*60}")
        
        # 按模型分组
        models = set(r.model_size for r in self.results)
        
        for model_size in sorted(models):
            comparison = self.compare_results(model_size)
            
            print(f"\n模型：{model_size}")
            print(f"  CPU 平均转写时间：{comparison['cpu']['avg_transcribe_time']}s ± {comparison['cpu']['std_transcribe_time']}s")
            print(f"  CPU 实时因子：{comparison['cpu']['avg_speed_factor']}x")
            
            if comparison['gpu']:
                print(f"  GPU 平均转写时间：{comparison['gpu']['avg_transcribe_time']}s ± {comparison['gpu']['std_transcribe_time']}s")
                print(f"  GPU 实时因子：{comparison['gpu']['avg_speed_factor']}x")
                print(f"  GPU 显存：{comparison['gpu']['avg_gpu_memory']}MB")
                
                if comparison['speedup']:
                    print(f"\n  🚀 GPU 加速比：{comparison['speedup']}x")
                    
                    # 检查是否达到目标
                    if comparison['gpu']['avg_transcribe_time'] < 5:
                        print(f"  ✅ 达到目标（<5 秒）")
                    else:
                        print(f"  ⚠ 未达到目标（目标：<5 秒）")
            else:
                print(f"  GPU: 不可用")
    
    def save_report(self, path: str = "gpu_performance_report.json"):
        """保存测试报告"""
        report = {
            "audio_file": self.audio_file,
            "audio_duration": self.audio_duration,
            "cuda_status": {
                "available": torch.cuda.is_available() if (torch := __import__('torch', fromlist=[''])) else False,
                "gpu_name": __import__('torch').cuda.get_device_name(0) if __import__('torch').cuda.is_available() else None
            },
            "results": [
                {
                    "model_size": r.model_size,
                    "device": r.device,
                    "compute_type": r.compute_type,
                    "transcribe_time": r.transcribe_time,
                    "load_time": r.load_time,
                    "total_time": r.total_time,
                    "speed_factor": r.speed_factor,
                    "gpu_memory_used": r.gpu_memory_used
                }
                for r in self.results
            ],
            "comparisons": [
                self.compare_results(model_size)
                for model_size in set(r.model_size for r in self.results)
            ]
        }
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"\n报告已保存到：{path}")


def main():
    """主测试函数"""
    import torch
    
    print("=" * 60)
    print("LiveMirror GPU 性能对比测试")
    print("=" * 60)
    
    # 显示 CUDA 状态
    print_cuda_status()
    
    # 测试文件
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
    else:
        audio_file = "test_audio/live_streaming_demo.mp3"
    
    # 检查文件
    if not Path(audio_file).exists():
        print(f"\n❌ 测试文件不存在：{audio_file}")
        print("\n使用方法：python test_gpu_performance.py <音频文件路径>")
        print("示例：python test_gpu_performance.py test_audio/demo.wav")
        sys.exit(1)
    
    # 创建测试器
    tester = PerformanceTester(audio_file)
    
    # 测试配置
    test_models = ["tiny", "base"]
    runs_per_test = 2
    
    # 测试 CPU
    for model in test_models:
        tester.test_cpu(model, runs=runs_per_test)
    
    # 测试 GPU（如果可用）
    if torch.cuda.is_available():
        for model in test_models:
            # 根据显存选择计算类型
            total_memory = torch.cuda.get_device_properties(0).total_memory // (1024 * 1024)
            if total_memory >= 8000:
                compute_type = "float16"
            elif total_memory >= 4000:
                compute_type = "int8_float16"
            else:
                compute_type = "int8"
            
            tester.test_gpu(model, runs=runs_per_test, compute_type=compute_type)
    else:
        print("\n⚠ CUDA 不可用，跳过 GPU 测试")
    
    # 打印报告
    tester.print_report()
    
    # 保存报告
    tester.save_report()
    
    # 总结
    print(f"\n{'='*60}")
    print("测试完成!")
    print(f"{'='*60}")
    
    # 检查是否达到目标
    for model in test_models:
        comparison = tester.compare_results(model)
        if comparison.get('gpu') and comparison.get('speedup'):
            gpu_time = comparison['gpu']['avg_transcribe_time']
            speedup = comparison['speedup']
            
            if gpu_time < 5:
                print(f"✅ {model} 模型：GPU 转写时间 {gpu_time}s < 5s，加速 {speedup}x")
            else:
                print(f"⚠ {model} 模型：GPU 转写时间 {gpu_time}s >= 5s，加速 {speedup}x")


if __name__ == "__main__":
    main()
