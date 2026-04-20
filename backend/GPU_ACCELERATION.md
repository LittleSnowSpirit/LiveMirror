# Whisper GPU 加速转写

## 概述

本项目支持使用 NVIDIA GPU 加速 Whisper 语音转写，大幅提升转写速度。

## 文件结构

```
backend/
├── services/
│   ├── whisper.py          # 原始 CPU 版本
│   └── whisper_gpu.py      # GPU 加速版本（支持自动 CPU/GPU 切换）
├── utils/
│   └── cuda_check.py       # CUDA 环境检测工具
├── test_gpu_performance.py # GPU 性能对比测试
├── test_whisper_gpu_service.py  # 功能测试
└── GPU_ACCELERATION.md     # 本文档
```

## 功能特性

### 1. CUDA 环境自动检测

```python
from utils.cuda_check import detect_cuda, print_cuda_status

# 检测 CUDA 环境
status = detect_cuda()
print(f"CUDA 可用：{status.available}")
print(f"推荐设备：{status.recommended_device}")
print(f"GPU 数量：{status.gpu_count}")

# 打印详细报告
print_cuda_status()
```

**检测内容包括：**
- nvidia-smi 可用性
- PyTorch CUDA 支持
- TensorFlow GPU 支持
- faster-whisper CUDA 支持
- GPU 显存状态
- 推荐配置（设备 + 计算类型）

### 2. GPU 加速转写服务

```python
from services.whisper_gpu import WhisperGPUService

# 自动检测并配置（推荐）
service = WhisperGPUService()

# 或手动指定
service = WhisperGPUService(
    device="cuda",        # 或 "cpu"
    compute_type="float16",  # 或 "int8", "int8_float16"
    gpu_index=0,          # 多 GPU 时指定
    enable_memory_management=True  # 启用显存管理
)

# 转写音频
result = service.transcribe(
    audio_path="audio.mp3",
    model_size="tiny",    # tiny, base, small, medium, large
    language="zh",        # 语言代码
    use_vad=True,         # 语音活动检测
    beam_size=5
)

print(f"转写时间：{result.transcribe_time}s")
print(f"设备：{result.device}")
print(f"文本：{result.text}")
```

### 3. 自动 CPU/GPU 切换

服务会自动检测 CUDA 可用性，并在以下情况自动回退到 CPU：
- 没有 NVIDIA GPU
- CUDA 驱动未安装
- 显存不足
- faster-whisper 未配置 CUDA 支持

```python
# 即使请求 CUDA，也会自动回退到 CPU（如果不可用）
service = WhisperGPUService(device="cuda")
print(service.device)  # 输出："cpu"（如果 CUDA 不可用）
```

### 4. 显存管理

防止 OOM（Out Of Memory）错误：

```python
from services.whisper_gpu import GPUMemoryManager

# 获取显存统计
stats = service.memory_manager.get_stats()
print(f"总显存：{stats['total_mb']}MB")
print(f"已使用：{stats['allocated_mb']}MB")
print(f"空闲：{stats['free_mb']}MB")

# 清空缓存
service.memory_manager.clear_cache()
service.clear_model_cache()
```

**模型显存需求：**
| 模型 | 显存需求 |
|------|---------|
| tiny | ~500MB  |
| base | ~750MB  |
| small | ~1.5GB |
| medium | ~3.5GB |
| large | ~5GB   |

### 5. 多 GPU 支持

```python
# 指定 GPU 索引
service = WhisperGPUService(gpu_index=1)  # 使用第二个 GPU

# 检查多 GPU 状态
from utils.cuda_check import detect_cuda
status = detect_cuda()
for gpu in status.gpus:
    print(f"GPU {gpu.index}: {gpu.name}, {gpu.total_memory}MB")
```

### 6. 性能监控

```python
# 获取性能统计
stats = service.get_performance_stats()
print(f"总请求数：{stats['total_requests']}")
print(f"GPU 加速比：{stats.get('speedup', 'N/A')}x")

# 保存性能日志
service.save_performance_log("performance_log.json")
```

## 性能测试

### 运行功能测试

```bash
python backend/test_whisper_gpu_service.py
```

**测试内容：**
1. CUDA 环境检测
2. 服务初始化
3. 模型加载
4. 转写功能
5. 自动 CPU/GPU 切换
6. 显存管理
7. 性能统计

### 运行性能对比测试

```bash
python backend/test_gpu_performance.py test_audio/live_streaming_demo.mp3
```

**测试流程：**
1. CPU 模式测试（多次运行取平均）
2. GPU 模式测试（多次运行取平均）
3. 生成对比报告

**性能目标：**
- 96 秒音频转写时间 < 5 秒
- GPU 加速比 > 3x

### 预期性能提升

| 场景 | CPU 时间 | GPU 时间 | 加速比 |
|------|---------|---------|--------|
| tiny 模型，96s 音频 | ~16s | ~3-5s | 3-5x |
| base 模型，96s 音频 | ~25s | ~5-8s | 3-4x |
| small 模型，96s 音频 | ~40s | ~10-15s | 3-4x |

*实际性能取决于 GPU 型号和显存大小*

## 安装要求

### 硬件要求

- **GPU**: NVIDIA GPU（推荐 GTX 1060 或更高）
- **显存**: 
  - tiny/base: 2GB+
  - small: 4GB+
  - medium: 8GB+
  - large: 10GB+

### 软件要求

```bash
# PyTorch with CUDA
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# faster-whisper with CUDA support
pip install faster-whisper

# 或使用预编译版本
pip install ctranslate2>=4.0
```

### 验证安装

```bash
python -c "import torch; print('CUDA:', torch.cuda.is_available())"
python backend/utils/cuda_check.py
```

## 使用示例

### 基础使用

```python
from services.whisper_gpu import transcribe_audio

# 最简单用法（自动检测 GPU）
result = transcribe_audio("audio.mp3", model_size="tiny")
print(result.text)
```

### 批量处理

```python
from services.whisper_gpu import WhisperGPUService

service = WhisperGPUService()

audio_files = ["file1.mp3", "file2.mp3", "file3.mp3"]
for audio_file in audio_files:
    result = service.transcribe(audio_file, model_size="base")
    print(f"{audio_file}: {result.text[:50]}...")

# 查看性能统计
stats = service.get_performance_stats()
print(f"平均转写时间：{stats['gpu_stats']['avg_transcribe_time']}s")
```

### 错误处理

```python
from services.whisper_gpu import WhisperGPUService
from utils.cuda_check import detect_cuda

# 检查 GPU 可用性
status = detect_cuda()
if not status.available:
    print("GPU 不可用，使用 CPU 模式")

try:
    service = WhisperGPUService()
    result = service.transcribe("audio.mp3")
except Exception as e:
    print(f"转写失败：{e}")
    # 自动回退到 CPU
    service = WhisperGPUService(device="cpu")
    result = service.transcribe("audio.mp3")
```

## 故障排除

### CUDA 不可用

**问题**: `CUDA available: False`

**解决方案**:
1. 确认有 NVIDIA GPU: `nvidia-smi`
2. 安装 CUDA 驱动
3. 安装 PyTorch CUDA 版本
4. 检查 faster-whisper 是否支持 CUDA

### 显存不足 (OOM)

**问题**: `CUDA out of memory`

**解决方案**:
1. 使用更小的模型（tiny 或 base）
2. 使用 int8 量化：`compute_type="int8"`
3. 关闭其他 GPU 应用
4. 清空缓存：`torch.cuda.empty_cache()`

### 转写速度慢

**问题**: GPU 转写速度未达到预期

**解决方案**:
1. 确认使用了 GPU：检查 `result.device`
2. 使用合适的计算类型（float16 最快）
3. 确保 batch_size 合理
4. 检查 GPU 利用率：`nvidia-smi`

## API 参考

### `detect_cuda() -> CUDAStatus`

检测 CUDA 环境，返回详细状态。

### `WhisperGPUService.__init__(device, compute_type, gpu_index, enable_memory_management)`

初始化 GPU 服务。

### `WhisperGPUService.transcribe(audio_path, model_size, language, use_vad, beam_size) -> TranscribeResult`

转写音频文件。

### `WhisperGPUService.get_performance_stats() -> dict`

获取性能统计。

## 总结

GPU 加速转写功能已完全实现，支持：
- ✅ CUDA 环境自动检测
- ✅ GPU 版本 Whisper 模型加载
- ✅ 自动 CPU/GPU 切换
- ✅ 显存管理（防止 OOM）
- ✅ 多 GPU 支持
- ✅ 性能监控和日志

在当前测试环境（无 GPU）下，转写时间为 ~16 秒。在有 NVIDIA GPU 的系统上，预期转写时间可降至 5 秒以内，加速比 3-5x。
