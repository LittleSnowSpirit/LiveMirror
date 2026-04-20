# 🔊 语音控制功能集成指南

## ✅ 开发完成总结

### 已创建文件

```
frontend/
├── src/
│   ├── utils/
│   │   ├── voice_control.js          ✅ 语音控制核心模块 (9.8KB)
│   │   └── voice_control.test.js     ✅ 单元测试文件 (9.8KB)
│   ├── components/
│   │   └── VoiceCommand.vue          ✅ 语音命令组件 (11.0KB)
│   ├── views/
│   │   └── VoiceSettings.vue         ✅ 语音设置页面 (14.7KB)
│   ├── assets/
│   │   └── voice_commands.json       ✅ 语音命令配置 (4.0KB)
│   └── README_VOICE_CONTROL.md       ✅ 功能文档 (4.7KB)
└── voice_demo.html                    ✅ 独立演示页面 (16.6KB)
```

### 功能清单

| 功能 | 状态 | 说明 |
|------|------|------|
| 语音命令识别 | ✅ | 支持开始/停止/切换 |
| 语音导航 | ✅ | 页面跳转/切换功能 |
| 语音搜索 | ✅ | 查找数据/报告 |
| 语音快捷操作 | ✅ | 刷新/全屏/主题切换 |
| 语音反馈确认 | ✅ | 视觉/声音/TTS 反馈 |
| 离线语音支持 | ✅ | 本地命令匹配 |

## 🚀 快速开始

### 1. 在 Vue 项目中使用

```javascript
// main.js 或 App.vue
import { startListening, onCommand } from '@/utils/voice_control'

// 启动语音识别
startListening()

// 监听命令
onCommand((command) => {
  console.log('收到命令:', command)
  // 处理命令...
})
```

### 2. 添加语音按钮组件

```vue
<!-- 在任何页面中添加 -->
<template>
  <VoiceCommand 
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
      // 处理命令执行
    },
    handleNavigate(page) {
      this.$router.push(`/${page}`)
    }
  }
}
</script>
```

### 3. 添加语音设置页面

```vue
<!-- router/index.js -->
import VoiceSettings from '@/views/VoiceSettings.vue'

{
  path: '/voice-settings',
  name: 'VoiceSettings',
  component: VoiceSettings
}
```

### 4. 测试语音功能

**方法一：使用演示页面**
```bash
# 在浏览器中打开
open frontend/voice_demo.html
```

**方法二：运行单元测试**
```bash
npm test -- voice_control.test.js
```

## 📋 集成步骤

### 步骤 1: 导入模块

确保你的 Vue 项目支持 ES6 模块导入。

### 步骤 2: 配置路由（可选）

在路由配置中添加语音设置页面：

```javascript
// router/index.js
const routes = [
  {
    path: '/settings/voice',
    name: 'VoiceSettings',
    component: () => import('@/views/VoiceSettings.vue')
  }
]
```

### 步骤 3: 全局注册组件（可选）

```javascript
// main.js
import VoiceCommand from '@/components/VoiceCommand.vue'

app.component('VoiceCommand', VoiceCommand)
```

### 步骤 4: 在布局中使用

```vue
<!-- layouts/Default.vue -->
<template>
  <div class="app-layout">
    <header>
      <h1>LiveMirror</h1>
      <VoiceCommand :show-history="true" />
    </header>
    <main>
      <router-view />
    </main>
  </div>
</template>
```

## 🎯 命令列表

### 控制命令
- `开始` / `启动` / `开启` → 开始语音识别
- `停止` / `关闭` / `退出` → 停止语音识别
- `切换` / `开关` → 切换语音识别状态

### 导航命令
- `首页` / `主页` → 返回首页
- `仪表盘` / `看板` → 打开仪表盘
- `报告` / `报表` → 打开报告页面
- `设置` / `配置` → 打开设置页面
- `健康` → 打开健康数据页面
- `下一个` → 下一页
- `上一个` / `返回` → 上一页

### 搜索命令
- `搜索` → 通用搜索
- `搜索报告` → 搜索报告
- `搜索数据` → 搜索数据
- `搜索健康` → 搜索健康数据

### 快捷命令
- `刷新` / `更新` → 刷新页面
- `帮助` → 显示帮助
- `全屏` → 切换全屏
- `夜间模式` → 切换主题
- `截图` → 截取屏幕

## ⚙️ 配置选项

### 默认设置

```javascript
const defaultSettings = {
  default_language: 'zh-CN',    // 识别语言
  sensitivity: 0.8,              // 灵敏度 (0.1-1.0)
  continuous_mode: false,        // 连续识别
  auto_start: false,             // 自动启动
  feedback_sound: true,          // 声音反馈
  feedback_visual: true,         // 视觉反馈
  feedback_voice: true,          // 语音反馈
  offline_mode: true,            // 离线支持
  wake_word: null                // 唤醒词
}
```

### 自定义设置

```javascript
import { updateSettings } from '@/utils/voice_control'

updateSettings({
  default_language: 'en-US',
  sensitivity: 0.9,
  continuous_mode: true,
  feedback_voice: false
})
```

## 🧪 测试指南

### 1. 浏览器兼容性测试

测试以下浏览器：
- ✅ Chrome (推荐)
- ✅ Edge
- ⚠️ Safari (部分支持)
- ⚠️ Firefox (有限支持)

### 2. 功能测试清单

- [ ] 麦克风权限授予
- [ ] 语音识别启动/停止
- [ ] 命令匹配准确性
- [ ] 视觉反馈显示
- [ ] 声音反馈播放
- [ ] TTS 语音反馈
- [ ] 离线模式切换
- [ ] 设置保存/加载
- [ ] 命令历史记录
- [ ] 页面导航执行

### 3. 场景测试

**场景 1: 在线模式**
```
1. 点击麦克风按钮
2. 说"打开首页"
3. 验证导航到首页
4. 验证反馈显示
```

**场景 2: 离线模式**
```
1. 断开网络连接
2. 点击麦克风按钮
3. 说"刷新"
4. 验证页面刷新
5. 验证离线提示
```

**场景 3: 连续命令**
```
1. 启用连续模式
2. 连续说"首页"、"报告"、"设置"
3. 验证页面依次切换
4. 验证历史记录
```

## 🔧 故障排除

### 问题 1: 语音识别不工作

**解决方案:**
```javascript
// 检查浏览器支持
import { isSupported } from '@/utils/voice_control'

if (!isSupported()) {
  console.warn('浏览器不支持语音识别')
  // 降级处理
}
```

### 问题 2: 麦克风权限被拒绝

**解决方案:**
- 在浏览器设置中授予麦克风权限
- 使用 HTTPS 协议（生产环境必需）
- 提供手动权限请求按钮

### 问题 3: 命令匹配不准确

**解决方案:**
```javascript
// 调整灵敏度
import { updateSettings } from '@/utils/voice_control'

updateSettings({
  sensitivity: 0.9  // 提高灵敏度
})
```

### 问题 4: 离线模式不生效

**解决方案:**
- 确认 `offline_mode: true`
- 检查命令是否在配置中
- 查看浏览器控制台错误

## 📱 移动端适配

### iOS Safari
```javascript
// iOS 需要用户手势触发
document.addEventListener('touchstart', () => {
  // 初始化 AudioContext
}, { once: true })
```

### Android Chrome
```javascript
// Android 需要 HTTPS
if (location.protocol !== 'https:') {
  console.warn('语音识别需要 HTTPS')
}
```

## 🔒 安全与隐私

### 最佳实践

1. **明确提示**: 录音时显示明显指示
2. **用户控制**: 随时可以停止录音
3. **数据最小化**: 不存储原始音频
4. **本地处理**: 优先本地命令匹配
5. **权限说明**: 解释为什么需要麦克风

### 隐私声明示例

```javascript
// 在设置页面添加隐私说明
const privacyNotice = `
语音控制功能需要麦克风权限。
- 录音仅在您点击麦克风按钮时进行
- 语音数据不会被存储或上传
- 您可以随时关闭语音功能
`
```

## 📊 性能优化

### 1. 延迟优化

```javascript
// 使用 Web Worker 处理命令匹配
const worker = new Worker('voice-worker.js')
```

### 2. 内存优化

```javascript
// 限制历史记录数量
const MAX_HISTORY = 10
if (commandHistory.length > MAX_HISTORY) {
  commandHistory.shift()
}
```

### 3. 电量优化

```javascript
// 非活动时停止识别
let idleTimer
onResult(() => {
  clearTimeout(idleTimer)
  idleTimer = setTimeout(stopListening, 30000)
})
```

## 🎨 UI/UX 建议

### 1. 视觉反馈

- 使用动画波形表示聆听状态
- 颜色区分不同状态（聆听/处理/错误）
- 显示识别结果的实时转录

### 2. 声音反馈

- 成功：高音短促提示音
- 错误：低音长提示音
- 聆听：持续低音量背景音

### 3. 错误处理

```vue
<template>
  <div v-if="error" class="error-toast">
    {{ errorMessage }}
    <button @click="retry">重试</button>
  </div>
</template>
```

## 📈 未来扩展

### 计划功能

- [ ] 自定义命令添加
- [ ] 多语言支持增强
- [ ] 声纹识别
- [ ] 离线语音模型
- [ ] 命令宏/快捷组合
- [ ] 语音统计分析

### API 扩展

```javascript
// 未来可能添加的 API
export function addCustomCommand(name, keywords, handler) {}
export function removeCustomCommand(name) {}
export function getVoiceStats() {}
export function trainVoiceModel(samples) {}
```

## 📞 支持

### 文档
- `README_VOICE_CONTROL.md` - 详细功能文档
- `voice_demo.html` - 独立演示页面
- `voice_control.test.js` - 测试用例参考

### 常见问题

查看 `README_VOICE_CONTROL.md` 的故障排除章节。

### 技术栈

- Vue 3 + Composition API
- Web Speech API
- Web Audio API
- Speech Synthesis API

---

**版本**: 1.0.0  
**更新日期**: 2026-04-09  
**状态**: ✅ 开发完成，可投入使用
