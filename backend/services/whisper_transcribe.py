"""
LiveMirror Whisper 转写服务 - 优化版本
支持模型懒加载、缓存、性能优化
"""

import time
import threading
from pathlib import Path
from typing import Optional, Dict
from dataclasses import dataclass
from functools import lru_cache
import json


@dataclass
class TranscribeResult:
    """转写结果数据类"""
    text: str
    segments: list
    language: str
    model_size: str
    model_load_time: float
    transcribe_time: float
    total_time: float


class ModelCache:
    """
    模型缓存管理器
    实现懒加载和模型复用
    """
    
    def __init__(self, max_cache_size: int = 3):
        self._cache: Dict[str, any] = {}
        self._lock = threading.Lock()
        self._max_size = max_cache_size
        self._access_order = []
    
    def get_model(self, model_size: str, device: str = "cpu", compute_type: str = "int8"):
        """
        获取模型（懒加载）
        
        Args:
            model_size: 模型大小
            device: 运行设备
            compute_type: 计算类型
        
        Returns:
            WhisperModel 实例
        """
        cache_key = f"{model_size}_{device}_{compute_type}"
        
        with self._lock:
            # 检查缓存
            if cache_key in self._cache:
                # 更新访问顺序
                if cache_key in self._access_order:
                    self._access_order.remove(cache_key)
                self._access_order.append(cache_key)
                print(f"[CACHE HIT] 模型 {model_size} 已从缓存加载")
                return self._cache[cache_key]
            
            # 缓存未命中，加载模型
            print(f"[CACHE MISS] 开始加载模型 {model_size}...")
            load_start = time.time()
            
            from faster_whisper import WhisperModel
            model = WhisperModel(
                model_size,
                device=device,
                compute_type=compute_type,
                num_workers=1
            )
            
            load_time = time.time() - load_start
            print(f"[LOAD COMPLETE] 模型 {model_size} 加载完成，耗时 {load_time:.2f}s")
            
            # 缓存模型
            if len(self._cache) >= self._max_size:
                # LRU 淘汰
                oldest = self._access_order.pop(0)
                del self._cache[oldest]
                print(f"[CACHE EVICT] 淘汰模型 {oldest}")
            
            self._cache[cache_key] = model
            self._access_order.append(cache_key)
            
            return model
    
    def clear(self):
        """清空缓存"""
        with self._lock:
            self._cache.clear()
            self._access_order.clear()
            print("[CACHE CLEAR] 模型缓存已清空")
    
    def get_stats(self) -> dict:
        """获取缓存统计"""
        return {
            "cached_models": len(self._cache),
            "max_size": self._max_size,
            "models": list(self._cache.keys())
        }


class WhisperService:
    """
    Whisper 转写服务
    支持性能优化和监控
    """
    
    def __init__(self, device: str = "cpu", compute_type: str = "int8"):
        self.device = device
        self.compute_type = compute_type
        self.model_cache = ModelCache()
        self._performance_log = []
    
    def transcribe(
        self,
        audio_path: str,
        model_size: str = "tiny",
        language: str = "zh",
        use_vad: bool = True,
        beam_size: int = 5
    ) -> TranscribeResult:
        """
        转写音频文件
        
        Args:
            audio_path: 音频文件路径
            model_size: 模型大小
            language: 语言代码
            use_vad: 是否使用 VAD 过滤
            beam_size: 束搜索大小
        
        Returns:
            TranscribeResult 转写结果
        """
        total_start = time.time()
        
        # 懒加载模型
        model = self.model_cache.get_model(
            model_size,
            self.device,
            self.compute_type
        )
        
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
        
        result = TranscribeResult(
            text=full_text,
            segments=segment_data,
            language=info.language,
            model_size=model_size,
            model_load_time=round(model_load_time, 2),
            transcribe_time=round(transcribe_time, 2),
            total_time=round(total_time, 2)
        )
        
        # 记录性能数据
        self._log_performance(audio_path, result)
        
        print(f"[COMPLETE] 转写完成 - 总耗时：{total_time:.2f}s, 文本长度：{len(full_text)}")
        
        return result
    
    def _log_performance(self, audio_path: str, result: TranscribeResult):
        """记录性能数据"""
        log_entry = {
            "timestamp": time.time(),
            "audio_path": audio_path,
            **{
                "model_size": result.model_size,
                "model_load_time": result.model_load_time,
                "transcribe_time": result.transcribe_time,
                "total_time": result.total_time,
                "text_length": len(result.text)
            }
        }
        self._performance_log.append(log_entry)
    
    def get_performance_stats(self) -> dict:
        """获取性能统计"""
        if not self._performance_log:
            return {"total_requests": 0}
        
        total = len(self._performance_log)
        avg_load = sum(r["model_load_time"] for r in self._performance_log) / total
        avg_transcribe = sum(r["transcribe_time"] for r in self._performance_log) / total
        avg_total = sum(r["total_time"] for r in self._performance_log) / total
        
        return {
            "total_requests": total,
            "avg_model_load_time": round(avg_load, 2),
            "avg_transcribe_time": round(avg_transcribe, 2),
            "avg_total_time": round(avg_total, 2),
            "cache_stats": self.model_cache.get_stats()
        }
    
    def save_performance_log(self, path: str = "performance_log.json"):
        """保存性能日志"""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self._performance_log, f, ensure_ascii=False, indent=2)
        print(f"[LOG SAVED] 性能日志已保存到 {path}")


# 全局服务实例（单例模式）
_service_instance: Optional[WhisperService] = None


def get_service(device: str = "cpu", compute_type: str = "int8") -> WhisperService:
    """
    获取全局 Whisper 服务实例（懒加载）
    
    Args:
        device: 运行设备
        compute_type: 计算类型
    
    Returns:
        WhisperService 实例
    """
    global _service_instance
    if _service_instance is None:
        _service_instance = WhisperService(device, compute_type)
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
    # 测试服务
    import sys
    
    if len(sys.argv) > 1:
        audio_file = sys.argv[1]
    else:
        audio_file = "test_audio/live_streaming_demo.mp3"
    
    print("="*60)
    print("Whisper 服务测试")
    print("="*60)
    
    # 测试 tiny 模型
    result = transcribe_audio(audio_file, "tiny")
    print(f"\nTiny 模型结果:")
    print(f"  加载时间：{result.model_load_time}s")
    print(f"  转写时间：{result.transcribe_time}s")
    print(f"  总时间：{result.total_time}s")
    print(f"  文本预览：{result.text[:100]}...")
    
    # 测试 base 模型（使用缓存）
    result = transcribe_audio(audio_file, "base")
    print(f"\nBase 模型结果:")
    print(f"  加载时间：{result.model_load_time}s")
    print(f"  转写时间：{result.transcribe_time}s")
    print(f"  总时间：{result.total_time}s")
    
    # 再次测试 tiny（应该使用缓存）
    result = transcribe_audio(audio_file, "tiny")
    print(f"\nTiny 模型（缓存）结果:")
    print(f"  加载时间：{result.model_load_time}s")
    print(f"  转写时间：{result.transcribe_time}s")
    print(f"  总时间：{result.total_time}s")
    
    # 显示性能统计
    service = get_service()
    stats = service.get_performance_stats()
    print(f"\n性能统计:")
    print(f"  总请求数：{stats['total_requests']}")
    print(f"  平均加载时间：{stats['avg_model_load_time']}s")
    print(f"  平均转写时间：{stats['avg_transcribe_time']}s")
    print(f"  平均总时间：{stats['avg_total_time']}s")
    
    # 保存日志
    service.save_performance_log()
