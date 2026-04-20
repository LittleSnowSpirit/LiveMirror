# 🎤 语音控制功能文档

## 概述

LiveMirror 语音控制功能允许用户通过语音命令操作界面，支持在线和离线两种模式。

## 功能特性

### ✅ 已实现功能

1. **语音命令识别**
   - 开始/停止/切换语音识别
   - 支持多种中文表达方式
   - 智能停用词过滤

2. **语音导航**
   - 首页、仪表盘、报告、设置等页面导航
   - 上一页/下一页切换
   - 快速页面跳转

3. **语音搜索**
   - 通用搜索
   - 报告搜索
   - 数据搜索
   - 健康数据搜索

4. **语音快捷操作**
   - 刷新页面
   - 显示帮助
   - 全屏切换
   - 主题切换
   - 截图功能

5. **语音反馈确认**
   - 视觉反馈（波形动画）
   - 声音反馈（提示音）
   - 语音反馈（TTS 朗读）

6. **离线语音支持**
   - 本地命令匹配
   - 网络不可用时自动切换
   - 预设命令离线可用

## 文件结构

```
frontend/src/
├── utils/
│   ├── voice_control.js          # 语音控制核心模块
│   └── voice_control.test.js     # 单元测试
├── components/
│   └── VoiceCommand.vue          # 语音命令组件
├── views/
│   └── VoiceSettings.vue         # 语音设置页面
└── assets/
    └── voice_commands.json       # 语音命令配置
```

## 使用方法

### 1. 基础使用

```javascript
import { startListening, stopListening, onCommand } from '@/utils/voice_control'

// 开始监听
startListening()

// 监听命令
onCommand((command) => {
  console.log('收到命令:', command)
  // command: { category, key, action, params, confidence }
})

// 停止监听
stopListening()
```

### 2. 使用组件

```vue
<template>
  <VoiceCommand 
    :show-history="true"
    :show-help="true"
    :auto-start="false"
    @command="handleCommand"
    @navigate="handleNavigate"
  />
</template>

<script>
import VoiceCommand from '@/components/VoiceCommand.vue'

export default {
  components: { VoiceCommand },
  methods: {
    handleCommand(command) {
      console.log('执行命令:', command)
    },
    handleNavigate(page) {
      this.$router.push(`/${page}`)
    }
  }
}
</script>
```

### 3. 语音设置

```vue
<template>
  <VoiceSettings />
</template>

<script>
import VoiceSettings from '@/views/VoiceSettings.vue'

export default {
  components: { VoiceSettings }
}
</script>
```

## 可用命令

### 控制命令
- **开始** - 开始语音识别
- **停止** - 停止语音识别
- **切换** - 切换语音识别状态

### 导航命令
- **首页** - 返回首页
- **仪表盘** - 打开仪表盘
- **报告** - 打开报告页面
- **设置** - 打开设置页面
- **健康** - 打开健康数据页面
- **下一个** - 切换到下一页
- **上一个** - 切换到上一页

### 搜索命令
- **搜索** - 搜索数据
- **搜索报告** - 搜索报告
- **搜索数据** - 搜索数据
- **搜索健康** - 搜索健康数据

### 快捷命令
- **刷新** - 刷新当前页面
- **帮助** - 显示语音命令帮助
- **全屏** - 切换全屏模式
- **夜间模式** - 切换深色/浅色主题
- **截图** - 截取当前屏幕

## 配置选项

### 基础设置
- `default_language` - 识别语言 (默认：zh-CN)
- `sensitivity` - 识别灵敏度 (0.1-1.0，默认：0.8)
- `continuous_mode` - 连续识别模式 (默认：false)
- `auto_start` - 自动启动 (默认：false)

### 反馈设置
- `feedback_sound` - 声音反馈 (默认：true)
- `feedback_visual` - 视觉反馈 (默认：true)
- `feedback_voice` - 语音反馈 (默认：true)

### 离线设置
- `offline_mode` - 启用离线支持 (默认：true)
- `wake_word` - 唤醒词 (默认：null)

## 事件系统

### 自定义事件

```javascript
// 语音反馈事件
window.addEventListener('voice-feedback', (event) => {
  const { type, config, data } = event.detail
  console.log('反馈:', type, data)
})

// 视觉反馈事件
window.addEventListener('voice-visual-feedback', (event) => {
  const { type, data } = event.detail
  // 更新 UI
})
```

### 组件事件

```vue
<VoiceCommand
  @command="handleCommand"
  @result="handleResult"
  @error="handleError"
  @navigate="handleNavigate"
  @refresh="handleRefresh"
  @show-help="handleShowHelp"
/>
```

## 浏览器兼容性

### 支持的浏览器
- ✅ Chrome 25+
- ✅ Edge 79+
- ✅ Safari 14.1+
- ✅ Firefox 支持有限

### 功能检测

```javascript
import { isSupported } from '@/utils/voice_control'

if (isSupported()) {
  // 使用在线语音识别
} else {
  // 降级到离线模式
}
```

## 测试

### 运行测试

```bash
# 运行单元测试
npm test -- voice_control

# 运行所有测试
npm test
```

### 测试覆盖
- ✅ 语音识别初始化
- ✅ 命令匹配逻辑
- ✅ 停用词过滤
- ✅ 回调函数
- ✅ 设置管理
- ✅ 命令历史
- ✅ 离线模式

## 最佳实践

### 1. 性能优化
- 避免频繁启停语音识别
- 使用连续模式时注意资源消耗
- 定期清理命令历史

### 2. 用户体验
- 提供清晰的视觉反馈
- 在嘈杂环境中降低灵敏度
- 提供命令帮助文档

### 3. 错误处理
```javascript
onError((error) => {
  switch (error) {
    case 'no-speech':
      // 未检测到语音
      break
    case 'network':
      // 网络错误，切换到离线模式
      break
    case 'not-allowed':
      // 用户拒绝麦克风权限
      break
  }
})
```

### 4. 隐私保护
- 明确告知用户何时在录音
- 提供一键关闭功能
- 不存储语音原始数据

## 扩展开发

### 添加新命令

1. 编辑 `voice_commands.json`
```json
{
  "commands": {
    "custom": {
      "my_command": {
        "keywords": ["我的命令", "自定义"],
        "action": "custom_action",
        "params": { "data": "value" },
        "description": "自定义命令描述"
      }
    }
  }
}
```

2. 在组件中处理新动作
```javascript
executeCommand(command) {
  switch (command.action) {
    case 'custom_action':
      // 处理自定义动作
      break
  }
}
```

### 自定义反馈

```javascript
controller.setCallback('onCommand', (command) => {
  // 自定义反馈逻辑
  showCustomNotification(command)
})
```

## 故障排除

### 常见问题

**Q: 语音识别不工作**
- 检查浏览器是否支持
- 确认麦克风权限已授予
- 检查网络连接

**Q: 命令匹配不准确**
- 调整灵敏度设置
- 检查停用词列表
- 使用更清晰的发音

**Q: 离线模式不生效**
- 确认离线模式已启用
- 检查命令是否在预设列表中
- 查看浏览器控制台错误

## 更新日志

### v1.0.0 (2026-04-09)
- ✅ 初始版本发布
- ✅ 支持在线/离线语音识别
- ✅ 完整的命令系统
- ✅ 视觉/声音/语音反馈
- ✅ 设置页面
- ✅ 单元测试覆盖

## 许可证

MIT License
