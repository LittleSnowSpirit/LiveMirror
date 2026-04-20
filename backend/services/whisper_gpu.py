"""
LiveMirror Whisper GPU 加速转写服务
支持 CUDA 加速、自动 CPU/GPU 切换、显存管理
"""

import time
import threading
import torch
from pathlib import Path
from typing import Optional, Dict, List
from dataclasses import dataclass
import json
import sys

# 添加父目录到路径以便导入
sys.path.insert(0, str(Path(__file__).parent.parent))
from utils.cuda_check import detect_cuda, CUDAStatus, GPUInfo


@dataclass
class TranscribeResult:
    """转写结果数据类"""
    text: str
    segments: list
    language: str
    model_size: str
    device: str
    compute_type: str
    model_load_time: float
    transcribe_time: float
    total_time: float
    gpu_memory_used: Optional[int] = None  # MB


class GPUMemoryManager:
    """
    GPU 显存管理器
    防止 OOM，优化显存使用
    """
    
    def __init__(self, max_memory_fraction: float = 0.9):
        """
        Args:
            max_memory_fraction: 最大显存使用比例（0-1）
        """
        self.max_memory_fraction = max_memory_fraction
        self._reserved_memory = 0  # MB
        self._lock = threading.Lock()
    
    def get_available_memory(self, gpu_index: int = 0) -> int:
        """
        获取可用显存（MB）
        
        Args:
            gpu_index: GPU 索引
        
        Returns:
            可用显存大小（MB）
        """
        if not torch.cuda.is_available():
            return 0
        
        try:
            total_memory = torch.cuda.get_device_properties(gpu_index).total_memory
            allocated = torch.cuda.memory_allocated(gpu_index)
            reserved = torch.cuda.memory_reserved(gpu_index)
            
            # 计算可用显存（考虑安全边界）
            max_allowed = int(total_memory * self.max_memory_fraction)
            available = max_allowed - allocated - self._reserved_memory
            
            return max(0, available // (1024 * 1024))  # 转换为 MB
        except Exception:
            return 0
    
    def reserve_memory(self, memory_mb: int):
        """
        预留显存
        
        Args:
            memory_mb: 预留显存大小（MB）
        """
        with self._lock:
            self._reserved_memory += memory_mb * 1024 * 1024
    
    def release_memory(self, memory_mb: int):
        """
        释放预留显存
        
        Args:
            memory_mb: 释放显存大小（MB）
        """
        with self._lock:
            self._reserved_memory = max(0, self._reserved_memory - memory_mb * 1024 * 1024)
    
    def clear_cache(self):
        """清空 GPU 缓存"""
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            print("[GPU MEMORY] 已清空 GPU 缓存")
    
    def get_stats(self, gpu_index: int = 0) -> dict:
        """
        获取显存统计
        
        Args:
            gpu_index: GPU 索引
        
        Returns:
            显存统计字典
        """
        if not torch.cuda.is_available():
            return {
                "available": False,
                "total_mb": 0,
                "allocated_mb": 0,
                "reserved_mb": 0,
                "free_mb": 0
            }
        
        try:
            total = torch.cuda.get_device_properties(gpu_index).total_memory // (1024 * 1024)
            allocated = torch.cuda.memory_allocated(gpu_index) // (1024 * 1024)
            reserved = torch.cuda.memory_reserved(gpu_index) // (1024 * 1024)
            
            return {
                "available": True,
                "total_mb": total,
                "allocated_mb": allocated,
                "reserved_mb": reserved,
                "free_mb": total - allocated - reserved,
                "usage_percent": round((allocated / total) * 100, 2) if total > 0 else 0
            }
        except Exception as e:
            return {
                "available": True,
                "error": str(e),
                "total_mb": 0,
                "allocated_mb": 0,
                "reserved_mb": 0,
                "free_mb": 0
            }


class WhisperGPUService:
    """
    Whisper GPU 加速转写服务
    支持自动 CPU/GPU 切换、显存管理、多 GPU
    """
    
    # 模型大小和推荐显存需求（MB）
    MODEL_MEMORY_REQUIREMENTS = {
        "tiny": 500,
        "base": 750,
        "small": 1500,
        "medium": 3500,
        "large": 5000,
        "large-v2": 5000,
        "large-v3": 5000
    }
    
    def __init__(
        self,
        device: Optional[str] = None,
        compute_type: Optional[str] = None,
        gpu_index: int = 0,
        enable_memory_management: bool = True
    ):
        """
        初始化 GPU 服务
        
        Args:
            device: 设备类型 ("cuda", "cpu", 或 None 自动检测)
            compute_type: 计算类型 ("float16", "int8", "int8_float16")
            gpu_index: GPU 索引（多 GPU 时使用）
            enable_memory_management: 是否启用显存管理
        """
        # 自动检测 CUDA 环境
        self.cuda_status = detect_cuda()
        
        # 自动选择设备
        if device is None:
            self.device = self.cuda_status.recommended_device
        else:
            # 如果请求 CUDA 但不可用，自动回退到 CPU
            if device == "cuda" and not self.cuda_status.available:
                print("[GPU SERVICE] 请求 CUDA 但不可用，自动回退到 CPU")
                self.device = "cpu"
            else:
                self.device = device
        
        # 自动选择计算类型
        if compute_type is None:
            self.compute_type = self.cuda_status.recommended_compute_type
        else:
            # 如果回退到 CPU，使用 int8
            if self.device == "cpu":
                self.compute_type = "int8"
            else:
                self.compute_type = compute_type
        
        self.gpu_index = gpu_index
        self.enable_memory_management = enable_memory_management
        
        # 显存管理器
        self.memory_manager = GPUMemoryManager() if enable_memory_management else None
        
        # 模型缓存
        self._model_cache: Dict[str, any] = {}
        self._cache_lock = threading.Lock()
        
        # 性能日志
        self._performance_log: List[dict] = []
        
        print(f"[GPU SERVICE] 初始化完成:")
        print(f"  设备：{self.device}")
        print(f"  计算类型：{self.compute_type}")
        print(f"  GPU 索引：{gpu_index}")
        print(f"  显存管理：{'启用' if enable_memory_management else '禁用'}")
        
        if self.cuda_status.warnings:
            print("  警告:")
            for warning in self.cuda_status.warnings:
                print(f"    [WARN] {warning}")
    
    def _check_model_memory(self, model_size: str) -> bool:
        """
        检查是否有足够显存加载模型
        
        Args:
            model_size: 模型大小
        
        Returns:
            是否有足够显存
        """
        if self.device != "cuda" or not self.enable_memory_management:
            return True
        
        required_memory = self.MODEL_MEMORY_REQUIREMENTS.get(model_size, 1000)
        available_memory = self.memory_manager.get_available_memory(self.gpu_index)
        
        if available_memory < required_memory:
            print(f"[MEMORY CHECK] 显存不足：需要 {required_memory}MB, 可用 {available_memory}MB")
            return False
        
        return True
    
    def _load_model(self, model_size: str) -> any:
        """
        加载 Whisper 模型
        
        Args:
            model_size: 模型大小
        
        Returns:
            WhisperModel 实例
        """
        from faster_whisper import WhisperModel
        
        print(f"[MODEL LOAD] 加载模型 {model_size}...")
        print(f"  设备：{self.device}")
        print(f"  计算类型：{self.compute_type}")
        
        load_start = time.time()
        
        # 根据模型大小调整 workers
        num_workers = 1 if self.device == "cuda" else 4
        
        model = WhisperModel(
            model_size,
            device=self.device,
            compute_type=self.compute_type,
            num_workers=num_workers
        )
        
        load_time = time.time() - load_start
        print(f"[MODEL LOAD] 模型加载完成，耗时 {load_time:.2f}s")
        
        # 记录显存使用
        if self.device == "cuda" and self.enable_memory_management:
            gpu_stats = self.memory_manager.get_stats(self.gpu_index)
            print(f"[MEMORY] GPU 显存使用：{gpu_stats.get('allocated_mb', 0)}MB / {gpu_stats.get('total_mb', 0)}MB")
        
        return model
    
    def get_model(self, model_size: str) -> any:
        """
        获取模型（带缓存）
        
        Args:
            model_size: 模型大小
        
        Returns:
            WhisperModel 实例
        """
        cache_key = f"{model_size}_{self.device}_{self.compute_type}"
        
        with self._cache_lock:
            # 检查缓存
            if cache_key in self._model_cache:
                print(f"[CACHE HIT] 模型 {model_size} 已从缓存加载")
                return self._model_cache[cache_key]
            
            # 检查显存
            if not self._check_model_memory(model_size):
                # 显存不足，尝试清空缓存
                print("[MEMORY] 显存不足，尝试清空缓存...")
                self.clear_model_cache()
                
                # 再次检查
                if not self._check_model_memory(model_size):
                    # 仍然不足，回退到 CPU
                    print("[MEMORY] 显存仍然不足，回退到 CPU 模式")
                    old_device = self.device
                    self.device = "cpu"
                    self.compute_type = "int8"
                    cache_key = f"{model_size}_cpu_int8"
                    
                    if cache_key in self._model_cache:
                        self.device = old_device
                        return self._model_cache[cache_key]
                    
                    self.device = old_device
            
            # 加载模型
            model = self._load_model(model_size)
            
            # 缓存模型
            self._model_cache[cache_key] = model
            
            return model
    
    def clear_model_cache(self):
        """清空模型缓存"""
        with self._cache_lock:
            self._model_cache.clear()
            if self.device == "cuda" and self.enable_memory_management:
                self.memory_manager.clear_cache()
            print("[CACHE] 模型缓存已清空")
    
    def transcribe(
        self,
        audio_path: str,
        model_size: str = "tiny",
        language: str = "zh",
        use_vad: bool = True,
        beam_size: int = 5,
        batch_size: int = 16
    ) -> TranscribeResult:
        """
        转写音频文件
        
        Args:
            audio_path: 音频文件路径
            model_size: 模型大小
            language: 语言代码
            use_vad: 是否使用 VAD 过滤
            beam_size: 束搜索大小
            batch_size: 批处理大小
        
        Returns:
            TranscribeResult 转写结果
        """
        total_start = time.time()
        
        # 获取模型
        model = self.get_model(model_size)
        model_load_time = time.time() - total_start
        
        # 转写
        transcribe_start = time.time()
        print(f"[TRANSCRIBE] 开始转写 {Path(audio_path).name}...")
        
        segments, info = model.transcribe(
            audio_path,
            language=language,
            beam_size=beam_size,
            vad_filter=use_vad
        )
        
        # 收集结果
        text_segments = []
        segment_data = []
        for segment in segments:
            text_segments.append(segment.text)
            segment_data.append({
                "start": segment.start,
                "end": segment.end,
                "text": segment.text
            })
        
        transcribe_time = time.time() - transcribe_start
        total_time = time.time() - total_start
        
        full_text = "".join(text_segments)
        
        # 获取 GPU 显存使用
        gpu_memory_used = None
        if self.device == "cuda" and self.enable_memory_management:
            gpu_stats = self.memory_manager.get_stats(self.gpu_index)
            gpu_memory_used = gpu_stats.get('allocated_mb', 0)
        
        result = TranscribeResult(
            text=full_text,
            segments=segment_data,
            language=info.language,
            model_size=model_size,
            device=self.device,
            compute_type=self.compute_type,
            model_load_time=round(model_load_time, 2),
            transcribe_time=round(transcribe_time, 2),
            total_time=round(total_time, 2),
            gpu_memory_used=gpu_memory_used
        )
        
        # 记录性能数据
        self._log_performance(audio_path, result)
        
        print(f"[COMPLETE] 转写完成 - 总耗时：{total_time:.2f}s, 文本长度：{len(full_text)}")
        print(f"  设备：{self.device}, 计算类型：{self.compute_type}")
        if gpu_memory_used:
            print(f"  GPU 显存使用：{gpu_memory_used}MB")
        
        return result
    
    def _log_performance(self, audio_path: str, result: TranscribeResult):
        """记录性能数据"""
        log_entry = {
            "timestamp": time.time(),
            "audio_path": audio_path,
            "device": result.device,
            "compute_type": result.compute_type,
            "model_size": result.model_size,
            "model_load_time": result.model_load_time,
            "transcribe_time": result.transcribe_time,
            "total_time": result.total_time,
            "text_length": len(result.text),
            "gpu_memory_used": result.gpu_memory_used
        }
        self._performance_log.append(log_entry)
    
    def get_performance_stats(self) -> dict:
        """获取性能统计"""
        if not self._performance_log:
            return {"total_requests": 0}
        
        # 按设备分组统计
        cpu_logs = [r for r in self._performance_log if r["device"] == "cpu"]
        gpu_logs = [r for r in self._performance_log if r["device"] == "cuda"]
        
        def calc_avg(logs):
            if not logs:
                return None
            total = len(logs)
            return {
                "avg_model_load_time": round(sum(r["model_load_time"] for r in logs) / total, 2),
                "avg_transcribe_time": round(sum(r["transcribe_time"] for r in logs) / total, 2),
                "avg_total_time": round(sum(r["total_time"] for r in logs) / total, 2),
                "requests": total
            }
        
        cpu_stats = calc_avg(cpu_logs)
        gpu_stats = calc_avg(gpu_logs)
        
        # 计算加速比
        speedup = None
        if cpu_stats and gpu_stats and gpu_stats["avg_transcribe_time"] > 0:
            speedup = round(cpu_stats["avg_transcribe_time"] / gpu_stats["avg_transcribe_time"], 2)
        
        return {
            "total_requests": len(self._performance_log),
            "cpu_stats": cpu_stats,
            "gpu_stats": gpu_stats,
            "speedup": speedup,
            "current_device": self.device,
            "gpu_memory": self.memory_manager.get_stats(self.gpu_index) if self.enable_memory_management else None
        }
    
    def save_performance_log(self, path: str = "performance_log_gpu.json"):
        """保存性能日志"""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self._performance_log, f, ensure_ascii=False, indent=2)
        print(f"[LOG SAVED] 性能日志已保存到 {path}")


# 全局服务实例
_service_instance: Optional[WhisperGPUService] = None


def get_service(
    device: Optional[str] = None,
    compute_type: Optional[str] = None,
    gpu_index: int = 0
) -> WhisperGPUService:
    """
    获取全局 Whisper GPU 服务实例
    
    Args:
        device: 设备类型
        compute_type: 计算类型
        gpu_index: GPU 索引
    
    Returns:
        WhisperGPUService 实例
    """
    global _service_instance
    if _service_instance is None:
        _service_instance = WhisperGPUService(device, compute_type, gpu_index)
    return _service_instance


def transcribe_audio(
    audio_path: str,
    model_size: str = "tiny",
    language: str = "zh"
) -> TranscribeResult:
    """
    便捷函数：转写音频
    
    Args:
        audio_path: 音频文件路径
        model_size: 模型大小
        language: 语言代码
    
    Returns:
        TranscribeResult 转写结果
    """
    service = get_service()
    return service.transcribe(audio_path, model_size, language)


if __name__ == "__main__":
    # 测试 GPU 服务
    import sys
    
    print("=" * 60)
    print("Whisper GPU 服务测试")
    print("=" * 60)
    
    # 显示 CUDA 状态
    from utils.cuda_check import print_cuda_status
    print_cuda_status()
    
    # 测试文件
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
    else:
        audio_file = "test_audio/live_streaming_demo.mp3"
    
    # 检查文件是否存在
    if not Path(audio_file).exists():
        print(f"\n⚠ 测试文件不存在：{audio_file}")
        print("使用方法：python whisper_gpu.py <音频文件路径>")
        sys.exit(1)
    
    # 创建服务
    service = WhisperGPUService()
    
    # 测试转写
    print(f"\n测试转写：{audio_file}")
    result = service.transcribe(audio_file, "tiny", "zh")
    
    print(f"\n结果:")
    print(f"  模型加载时间：{result.model_load_time}s")
    print(f"  转写时间：{result.transcribe_time}s")
    print(f"  总时间：{result.total_time}s")
    print(f"  设备：{result.device}")
    print(f"  计算类型：{result.compute_type}")
    if result.gpu_memory_used:
        print(f"  GPU 显存：{result.gpu_memory_used}MB")
    print(f"  文本预览：{result.text[:100]}...")
    
    # 显示性能统计
    stats = service.get_performance_stats()
    print(f"\n性能统计:")
    print(f"  总请求数：{stats['total_requests']}")
    if stats['speedup']:
        print(f"  GPU 加速比：{stats['speedup']}x")
