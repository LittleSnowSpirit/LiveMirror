# LiveMirror 移动端开发文档

## 概述

LiveMirror 移动端支持包含以下核心功能：

1. **PWA 离线缓存增强** - Service Worker 实现离线访问
2. **移动端手势优化** - 完整的手势检测系统
3. **推送通知支持** - Web Push API 集成
4. **相机/麦克风权限** - 原生媒体 API 桥接
5. **原生功能桥接** - 剪贴板、分享、震动等
6. **APP 安装引导** - PWA 安装流程优化

---

## 目录结构

```
frontend/
├── public/
│   ├── manifest.json              # PWA 清单文件
│   └── offline.html               # 离线页面
├── src/
│   ├── service-worker/
│   │   └── sw.js                  # Service Worker
│   ├── utils/
│   │   ├── mobile.js              # 移动端工具函数
│   │   └── mobile.test.js         # 移动端测试
│   ├── components/
│   │   └── PushNotification.vue   # 推送通知组件
│   ├── views/
│   │   └── InstallGuide.vue       # 安装引导页面
│   └── styles/
│       └── mobile.css             # 移动端样式
└── index.html                     # 入口 HTML（已更新）
```

---

## 功能详解

### 1. PWA 离线缓存

#### Service Worker 配置

文件：`src/service-worker/sw.js`

**缓存策略**:
- **静态资源**: 预缓存（安装时）
- **HTML 页面**: 网络优先，失败回退缓存
- **API 请求**: 网络优先，失败返回缓存或错误
- **图片/资源**: 缓存优先

**缓存版本**:
```javascript
const CACHE_NAME = 'livemirror-v1';
const STATIC_CACHE = 'static-v1';
const DYNAMIC_CACHE = 'dynamic-v1';
```

**使用方法**:
```javascript
// 在 main.ts 中注册
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/service-worker/sw.js');
}
```

#### 离线页面

文件：`public/offline.html`

- 自动检测网络状态
- 网络恢复时自动刷新
- 显示可离线访问的内容列表

---

### 2. 移动端手势

#### GestureDetector 类

文件：`src/utils/mobile.js`

**支持的手势**:
- 左滑 (onSwipeLeft)
- 右滑 (onSwipeRight)
- 上滑 (onSwipeUp)
- 下滑 (onSwipeDown)
- 长按 (onLongPress)
- 双击 (onDoubleTap)
- 捏合缩小 (onPinchIn)
- 捏合放大 (onPinchOut)

**使用示例**:
```javascript
import { GestureDetector } from './utils/mobile';

const element = document.querySelector('.swipe-area');
const detector = new GestureDetector(element, {
  onSwipeLeft: (event) => {
    console.log('左滑', event.distance);
  },
  onSwipeRight: (event) => {
    console.log('右滑', event.distance);
  },
  onLongPress: (event) => {
    console.log('长按', event.x, event.y);
  }
});

// 清理
detector.destroy();
```

**配置选项**:
```javascript
export const GESTURE_CONFIG = {
  swipeThreshold: 50,      // 滑动阈值 (px)
  longPressDelay: 500,     // 长按延迟 (ms)
  pinchThreshold: 10,      // 捏合阈值 (px)
  doubleTapDelay: 300      // 双击延迟 (ms)
};
```

---

### 3. 推送通知

#### PushNotification 组件

文件：`src/components/PushNotification.vue`

**功能**:
- 通知权限请求
- 通知列表展示
- 通知点击处理
- 本地通知存储

**使用示例**:
```vue
<template>
  <PushNotification 
    :auto-request="true"
    :max-notifications="50"
    @notification-click="handleClick"
    @permission-granted="handleGranted"
  />
</template>

<script>
import PushNotification from './components/PushNotification.vue';

export default {
  components: { PushNotification },
  methods: {
    handleClick(notification) {
      console.log('点击通知', notification);
    },
    handleGranted() {
      console.log('权限已授予');
    }
  }
};
</script>
```

**发送通知**:
```javascript
// 从 Service Worker 发送
self.registration.showNotification('标题', {
  body: '内容',
  icon: '/icons/icon-192.png',
  data: { url: '/page' }
});
```

---

### 4. 权限管理

#### 权限类型

```javascript
export const PERMISSIONS = {
  CAMERA: 'camera',
  MICROPHONE: 'microphone',
  NOTIFICATION: 'notification',
  GEOLOCATION: 'geolocation',
  STORAGE: 'storage'
};
```

#### 请求权限

```javascript
import { requestPermission, PERMISSIONS } from './utils/mobile';

// 请求相机权限
const result = await requestPermission(PERMISSIONS.CAMERA);
if (result.granted) {
  console.log('相机权限已授予');
} else {
  console.error('相机权限被拒绝:', result.error);
}
```

#### 检查权限状态

```javascript
import { checkPermission, PERMISSIONS } from './utils/mobile';

const status = await checkPermission(PERMISSIONS.NOTIFICATION);
console.log('通知权限状态:', status.state || status.granted);
```

---

### 5. 原生功能桥接

#### NativeBridge API

文件：`src/utils/mobile.js`

**拍照**:
```javascript
import { NativeBridge } from './utils/mobile';

const photo = await NativeBridge.capturePhoto({
  width: 1280,
  height: 720,
  quality: 0.8,
  sourceType: 'camera' // 'camera' | 'photo-library'
});

console.log(photo.dataUrl); // base64 格式
```

**录音**:
```javascript
const audio = await NativeBridge.recordAudio({
  duration: 10 // 秒
});

console.log(audio.dataUrl);
console.log(audio.blob);
```

**分享**:
```javascript
await NativeBridge.share({
  title: 'LiveMirror',
  text: '看看这个直播分析',
  url: 'https://livemirror.app'
});
```

**剪贴板**:
```javascript
// 写入
await NativeBridge.clipboardWrite('复制的内容');

// 读取
const result = await NativeBridge.clipboardRead();
console.log(result.text);
```

**震动反馈**:
```javascript
// 简单震动
NativeBridge.vibrate(100);

// 模式震动
NativeBridge.vibrate([100, 50, 100]);
```

**获取电池状态**:
```javascript
const battery = await NativeBridge.getBattery();
console.log('电量:', battery.level * 100 + '%');
console.log('充电中:', battery.charging);
```

**获取网络状态**:
```javascript
const network = NativeBridge.getNetworkInfo();
console.log('网络类型:', network.effectiveType);
console.log('在线:', network.online);
```

---

### 6. PWA 安装引导

#### PWAInstallManager

```javascript
import { PWAInstallManager } from './utils/mobile';

const manager = new PWAInstallManager();

// 检查是否可以安装
if (manager.canInstall()) {
  // 显示安装按钮
}

// 提示安装
const result = await manager.promptInstall();
if (result.success) {
  console.log('安装成功');
}
```

#### InstallGuide 页面

文件：`src/views/InstallGuide.vue`

**路由配置**:
```javascript
{
  path: '/install',
  name: 'InstallGuide',
  component: () => import('@/views/InstallGuide.vue')
}
```

**功能**:
- 自动检测设备类型（iOS/Android）
- 显示对应的安装步骤
- 一键安装（Android）
- 安装指南（iOS）
- PWA 优势说明
- 常见问题解答

---

### 7. 设备检测

```javascript
import { isMobile, isIOS, isAndroid, getDeviceInfo } from './utils/mobile';

// 检测设备类型
if (isMobile()) {
  console.log('移动设备');
}

if (isIOS()) {
  console.log('iOS 设备');
}

if (isAndroid()) {
  console.log('Android 设备');
}

// 获取详细设备信息
const info = getDeviceInfo();
console.log(info);
/*
{
  isMobile: true,
  isIOS: false,
  isAndroid: true,
  userAgent: '...',
  platform: '...',
  screen: { width, height, pixelRatio },
  orientation: 'landscape-primary'
}
*/
```

---

### 8. 屏幕方向和全屏

```javascript
import { 
  lockOrientation, 
  unlockOrientation,
  enterFullscreen,
  exitFullscreen,
  isFullscreen
} from './utils/mobile';

// 锁定屏幕方向
await lockOrientation('portrait'); // 'portrait' | 'landscape'

// 解锁屏幕方向
await unlockOrientation();

// 进入全屏
await enterFullscreen(document.documentElement);

// 退出全屏
await exitFullscreen();

// 检查全屏状态
if (isFullscreen()) {
  console.log('当前为全屏模式');
}
```

---

### 9. 唤醒锁定

```javascript
import { WakeLock } from './utils/mobile';

const wakeLock = new WakeLock();

// 请求唤醒锁定
await wakeLock.request();

// 释放唤醒锁定
await wakeLock.release();
```

---

## 样式优化

### 移动端 CSS

文件：`src/styles/mobile.css`

**导入方式**:
```javascript
// 在 main.ts 中
import './styles/mobile.css';
```

**主要功能**:
- 安全区域适配（刘海屏）
- 触摸反馈优化
- 响应式布局
- 手势动画
- 深色模式支持

**常用类**:
```html
<!-- 安全区域 -->
<div class="safe-area-top"></div>
<div class="safe-area-bottom"></div>

<!-- 触摸反馈 -->
<button class="touch-feedback">点击</button>

<!-- 响应式布局 -->
<div class="container">
  <div class="grid grid-cols-2 md:grid-cols-4">
    <!-- 内容 -->
  </div>
</div>

<!-- 卡片 -->
<div class="card">
  <!-- 内容 -->
</div>

<!-- 底部导航 -->
<nav class="mobile-nav">
  <div class="mobile-nav-items">
    <a class="mobile-nav-item active">
      <span class="mobile-nav-icon">🏠</span>
      <span>首页</span>
    </a>
  </div>
</nav>
```

---

## 测试

### 运行测试

```bash
cd frontend
npm test
```

### 测试文件

- `src/utils/mobile.test.js` - 单元测试
- `MOBILE_TEST_REPORT.md` - 测试报告模板

### 手动测试清单

1. **PWA 离线缓存**
   - [ ] Service Worker 注册成功
   - [ ] 静态资源缓存正常
   - [ ] 离线访问正常
   - [ ] 缓存更新正常

2. **推送通知**
   - [ ] 权限请求正常
   - [ ] 通知接收正常
   - [ ] 通知点击正常
   - [ ] 通知列表正常

3. **手势交互**
   - [ ] 滑动检测正常
   - [ ] 长按检测正常
   - [ ] 双击检测正常
   - [ ] 捏合检测正常

4. **权限管理**
   - [ ] 相机权限正常
   - [ ] 麦克风权限正常
   - [ ] 通知权限正常
   - [ ] 权限状态检测正常

5. **APP 安装**
   - [ ] 安装引导页面正常
   - [ ] Android 安装正常
   - [ ] iOS 安装指南正常
   - [ ] 安装状态检测正常

---

## 最佳实践

### 1. 性能优化

- 使用缓存优先策略减少网络请求
- 懒加载非关键资源
- 压缩图片和静态资源
- 使用 WebP 格式

### 2. 用户体验

- 提供离线提示
- 显示加载状态
- 使用骨架屏
- 提供触觉反馈

### 3. 兼容性

- 检测 API 支持情况
- 提供降级方案
- 测试多浏览器
- 适配不同屏幕

### 4. 安全性

- 使用 HTTPS
- 验证用户输入
- 保护敏感数据
- 定期更新依赖

---

## 故障排除

### Service Worker 未注册

**问题**: Service Worker 注册失败

**解决**:
1. 确保使用 HTTPS 或 localhost
2. 检查浏览器控制台错误
3. 清除浏览器缓存
4. 检查 sw.js 路径是否正确

### 推送通知不显示

**问题**: 通知未显示

**解决**:
1. 检查通知权限是否授予
2. 检查 Service Worker 是否正确注册
3. 检查推送订阅是否创建
4. 检查设备通知设置

### 手势检测不灵敏

**问题**: 手势未被检测到

**解决**:
1. 调整手势阈值配置
2. 检查元素是否有正确的监听器
3. 确保调用 destroy() 清理旧实例
4. 检查是否有其他事件冲突

### PWA 无法安装

**问题**: 安装按钮不显示

**解决**:
1. 确保使用 HTTPS
2. 检查 manifest.json 配置
3. 检查 Service Worker 是否激活
4. 清除浏览器缓存和数据

---

## 参考资料

- [PWA 官方文档](https://web.dev/progressive-web-apps/)
- [Service Worker API](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)
- [Web Push API](https://developer.mozilla.org/en-US/docs/Web/API/Push_API)
- [触摸事件](https://developer.mozilla.org/en-US/docs/Web/API/Touch_events)
- [设备 API](https://developer.mozilla.org/en-US/docs/Web/API/Device_apis)

---

**文档版本**: v1.0  
**最后更新**: 2026-04-08  
**维护者**: LiveMirror Team
