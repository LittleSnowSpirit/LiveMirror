# 测试 Fixtures

此目录包含测试所需的示例文件。

## 示例音频文件

### sample_audio.mp3
- 时长：约 5 秒
- 格式：MP3
- 大小：约 80KB
- 用途：基本上传测试

### sample_audio.wav
- 时长：约 5 秒
- 格式：WAV
- 大小：约 400KB
- 用途：WAV 格式测试

### long_audio.mp3
- 时长：约 60 秒
- 格式：MP3
- 大小：约 1MB
- 用途：长音频处理测试

### invalid_format.txt
- 格式：纯文本
- 用途：测试不支持的文件格式

## 生成示例文件

如果示例文件不存在，可以运行以下命令生成：

```bash
# 使用 Python 生成测试音频
python -c "
from utils.test_helpers import create_test_audio_file
from pathlib import Path

# 创建 MP3 示例
create_test_audio_file(
    Path('sample_audio.mp3'),
    duration_seconds=5.0,
    format='mp3'
)

# 创建 WAV 示例
create_test_audio_file(
    Path('sample_audio.wav'),
    duration_seconds=5.0,
    format='wav'
)
"
```

## 注意事项

1. 示例文件仅用于测试，不包含真实语音内容
2. 实际测试中应使用真实音频文件验证完整功能
3. 大文件（>100MB）不应提交到版本控制
