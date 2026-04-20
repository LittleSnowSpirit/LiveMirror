"""
CUDA 环境检测工具
检测 GPU 可用性、显存、多 GPU 支持等
"""

import subprocess
import sys
from typing import Dict, List, Optional
from dataclasses import dataclass
import json


@dataclass
class GPUInfo:
    """GPU 信息数据类"""
    index: int
    name: str
    total_memory: int  # MB
    free_memory: int  # MB
    utilization: float  # %
    cuda_compute_capability: Optional[str] = None


@dataclass
class CUDAStatus:
    """CUDA 状态数据类"""
    available: bool
    cuda_version: Optional[str]
    gpu_count: int
    gpus: List[GPUInfo]
    torch_available: bool
    tensorflow_available: bool
    faster_whisper_gpu: bool
    recommended_device: str  # "cuda" or "cpu"
    recommended_compute_type: str  # "float16", "int8", etc.
    warnings: List[str]


def check_nvidia_smi() -> Optional[List[GPUInfo]]:
    """
    通过 nvidia-smi 检查 GPU 状态
    
    Returns:
        GPU 信息列表，如果不可用则返回 None
    """
    try:
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=index,name,memory.total,memory.free,utilization.gpu",
             "--format=csv,noheader,nounits"],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode != 0:
            return None
        
        gpus = []
        for line in result.stdout.strip().split('\n'):
            if not line:
                continue
            parts = [p.strip() for p in line.split(',')]
            if len(parts) >= 5:
                gpus.append(GPUInfo(
                    index=int(parts[0]),
                    name=parts[1],
                    total_memory=int(parts[2]),
                    free_memory=int(parts[3]),
                    utilization=float(parts[4])
                ))
        
        return gpus if gpus else None
    
    except (FileNotFoundError, subprocess.TimeoutExpired, Exception):
        return None


def check_torch_cuda() -> tuple[bool, Optional[str], int]:
    """
    检查 PyTorch CUDA 支持
    
    Returns:
        (是否可用，CUDA 版本，GPU 数量)
    """
    try:
        import torch
        cuda_available = torch.cuda.is_available()
        cuda_version = torch.version.cuda if cuda_available else None
        gpu_count = torch.cuda.device_count() if cuda_available else 0
        return cuda_available, cuda_version, gpu_count
    except ImportError:
        return False, None, 0


def check_tensorflow_gpu() -> bool:
    """检查 TensorFlow GPU 支持"""
    try:
        import tensorflow as tf
        return len(tf.config.list_physical_devices('GPU')) > 0
    except ImportError:
        return False


def check_faster_whisper_gpu() -> bool:
    """
    检查 faster-whisper GPU 支持
    需要 ctranslate2 和 CUDA
    """
    try:
        import ctranslate2
        # 检查是否支持 CUDA
        return ctranslate2.is_cuda_available()
    except ImportError:
        return False
    except Exception:
        return False


def get_torch_gpu_info() -> List[GPUInfo]:
    """
    通过 PyTorch 获取 GPU 详细信息
    
    Returns:
        GPU 信息列表
    """
    try:
        import torch
        if not torch.cuda.is_available():
            return []
        
        gpus = []
        for i in range(torch.cuda.device_count()):
            props = torch.cuda.get_device_properties(i)
            memory_total = props.total_memory // (1024 * 1024)  # MB
            # PyTorch 不直接提供空闲显存，需要估算
            memory_allocated = torch.cuda.memory_allocated(i) // (1024 * 1024) if torch.cuda.is_available() else 0
            memory_reserved = torch.cuda.memory_reserved(i) // (1024 * 1024) if torch.cuda.is_available() else 0
            
            gpus.append(GPUInfo(
                index=i,
                name=props.name,
                total_memory=memory_total,
                free_memory=memory_total - memory_allocated - memory_reserved,
                utilization=0.0,  # PyTorch 不直接提供利用率
                cuda_compute_capability=f"{props.major}.{props.minor}"
            ))
        
        return gpus
    except Exception:
        return []


def detect_cuda() -> CUDAStatus:
    """
    全面检测 CUDA 环境
    
    Returns:
        CUDAStatus 包含所有检测信息
    """
    warnings = []
    
    # 检查 nvidia-smi
    nvidia_gpus = check_nvidia_smi()
    cuda_version = None
    if nvidia_gpus:
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                cuda_version = result.stdout.strip().split('\n')[0]
        except Exception:
            pass
    
    # 检查 PyTorch
    torch_cuda, torch_version, torch_gpu_count = check_torch_cuda()
    torch_gpus = get_torch_gpu_info() if torch_cuda else []
    
    # 检查 TensorFlow
    tf_gpu = check_tensorflow_gpu()
    
    # 检查 faster-whisper
    fw_gpu = check_faster_whisper_gpu()
    
    # 确定推荐配置
    gpu_count = len(nvidia_gpus) if nvidia_gpus else (torch_gpu_count if torch_cuda else 0)
    gpus = nvidia_gpus if nvidia_gpus else torch_gpus
    
    if gpu_count > 0:
        recommended_device = "cuda"
        # 根据显存推荐计算类型
        if gpus:
            min_memory = min(g.total_memory for g in gpus)
            if min_memory >= 8000:  # 8GB+
                recommended_compute_type = "float16"
            elif min_memory >= 4000:  # 4GB+
                recommended_compute_type = "int8_float16"
            else:
                recommended_compute_type = "int8"
                warnings.append(f"显存较小 ({min_memory}MB)，使用 int8 量化")
        else:
            recommended_compute_type = "float16"
    else:
        recommended_device = "cpu"
        recommended_compute_type = "int8"
        if not torch_cuda and not nvidia_gpus:
            warnings.append("未检测到 NVIDIA GPU，将使用 CPU 模式")
    
    # 检查 CUDA 工具包
    if gpu_count > 0 and not fw_gpu:
        warnings.append("检测到 GPU 但 faster-whisper 可能未正确配置 CUDA 支持")
    
    return CUDAStatus(
        available=gpu_count > 0,
        cuda_version=cuda_version or torch_version,
        gpu_count=gpu_count,
        gpus=gpus,
        torch_available=torch_cuda,
        tensorflow_available=tf_gpu,
        faster_whisper_gpu=fw_gpu,
        recommended_device=recommended_device,
        recommended_compute_type=recommended_compute_type,
        warnings=warnings
    )


def print_cuda_status(status: Optional[CUDAStatus] = None):
    """
    打印 CUDA 状态报告
    
    Args:
        status: CUDAStatus 对象，如果为 None 则自动检测
    """
    if status is None:
        status = detect_cuda()
    
    print("=" * 60)
    print("CUDA 环境检测报告")
    print("=" * 60)
    print(f"CUDA 可用：{'[YES]' if status.available else '[NO]'}")
    print(f"CUDA 版本：{status.cuda_version or 'N/A'}")
    print(f"GPU 数量：{status.gpu_count}")
    
    if status.gpus:
        print("\nGPU 详细信息:")
        for gpu in status.gpus:
            print(f"  GPU {gpu.index}: {gpu.name}")
            print(f"    总显存：{gpu.total_memory} MB")
            print(f"    空闲显存：{gpu.free_memory} MB")
            if gpu.cuda_compute_capability:
                print(f"    计算能力：{gpu.cuda_compute_capability}")
    
    print(f"\nPyTorch CUDA: {'[Y]' if status.torch_available else '[N]'}")
    print(f"TensorFlow GPU: {'[Y]' if status.tensorflow_available else '[N]'}")
    print(f"faster-whisper GPU: {'[Y]' if status.faster_whisper_gpu else '[N]'}")
    
    print(f"\n推荐配置:")
    print(f"  设备：{status.recommended_device}")
    print(f"  计算类型：{status.recommended_compute_type}")
    
    if status.warnings:
        print("\n警告:")
        for warning in status.warnings:
            print(f"  [WARN] {warning}")
    
    print("=" * 60)
    
    return status


def get_optimal_device_and_compute_type() -> tuple[str, str]:
    """
    获取最优设备和计算类型
    
    Returns:
        (device, compute_type) 元组
    """
    status = detect_cuda()
    return status.recommended_device, status.recommended_compute_type


if __name__ == "__main__":
    # 运行检测
    status = print_cuda_status()
    
    # 输出 JSON 格式（便于程序使用）
    print("\nJSON 输出:")
    print(json.dumps({
        "available": status.available,
        "cuda_version": status.cuda_version,
        "gpu_count": status.gpu_count,
        "gpus": [
            {
                "index": g.index,
                "name": g.name,
                "total_memory_mb": g.total_memory,
                "free_memory_mb": g.free_memory,
                "utilization": g.utilization
            }
            for g in status.gpus
        ],
        "torch_available": status.torch_available,
        "recommended_device": status.recommended_device,
        "recommended_compute_type": status.recommended_compute_type,
        "warnings": status.warnings
    }, indent=2, ensure_ascii=False))
