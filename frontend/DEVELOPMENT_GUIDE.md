# LiveMirror 暗黑模式开发指南

## 📋 开发完成总结

### 已实现功能

#### 1. 暗黑/明亮主题切换 ✅
- 主题切换组件 (`ThemeSwitcher.vue`)
- 支持明亮、暗黑、跟随系统三种模式
- 下拉菜单式 UI，操作直观

#### 2. 自动跟随系统主题 ✅
- 使用 `matchMedia` API 检测系统主题
- 实时监听系统主题变化
- 自动应用系统主题偏好

#### 3. 所有页面适配暗黑模式 ✅
- 首页 (`HomeView.vue`) - 完整测试页面
- 设置页面 (`SettingsView.vue`) - 主题配置
- 关于页面 (`AboutView.vue`) - 功能说明
- 所有组件和元素完全适配

#### 4. 主题色自定义 ✅
- 自定义主色调
- 自定义强调色
- 实时预览效果
- 颜色选择器 UI

#### 5. 主题偏好保存 ✅
- 使用 localStorage 持久化
- 自动保存主题模式
- 自动保存自定义颜色
- 页面刷新后保持偏好

#### 6. 平滑过渡动画 ✅
- CSS transition 实现平滑过渡
- 避免初始加载闪烁
- 过渡时间 250ms，体验流畅

### 文件结构

```
frontend/
├── src/
│   ├── styles/
│   │   └── dark.css              # 暗黑模式主题样式 (7KB)
│   ├── composables/
│   │   └── useTheme.ts           # 主题切换逻辑 (6KB)
│   ├── components/
│   │   └── ThemeSwitcher.vue     # 主题切换组件 (13KB)
│   ├── utils/
│   │   └── theme.js              # 主题管理工具 (5KB)
│   ├── views/
│   │   ├── HomeView.vue          # 首页测试页面 (12KB)
│   │   ├── SettingsView.vue      # 设置页面 (9KB)
│   │   └── AboutView.vue         # 关于页面 (7KB)
│   ├── router/
│   │   └── index.ts              # 路由配置
│   ├── App.vue                   # 根组件
│   └── main.ts                   # 入口文件
├── index.html
├── package.json
├── vite.config.ts
├── tsconfig.json
├── README.md                     # 项目说明
├── VISUAL_TEST_CHECKLIST.md      # 视觉测试清单
└── DEVELOPMENT_GUIDE.md          # 开发指南
```

## 🚀 运行项目

### 1. 安装依赖

```bash
cd frontend
npm install
```

### 2. 启动开发服务器

```bash
npm run dev
```

访问 http://localhost:3000

### 3. 构建生产版本

```bash
npm run build
```

### 4. 预览生产版本

```bash
npm run preview
```

## 🧪 测试步骤

### 快速测试

1. **启动开发服务器**
   ```bash
   npm run dev
   ```

2. **测试主题切换**
   - 点击右上角主题切换按钮
   - 选择"明亮模式"
   - 选择"暗黑模式"
   - 选择"跟随系统"
   - 使用"快速切换"

3. **测试自定义颜色**
   - 打开主题切换下拉菜单
   - 滚动到"主题色自定义"
   - 点击主色调颜色选择器
   - 选择新颜色
   - 观察页面颜色变化

4. **测试所有页面**
   - 首页：检查所有元素
   - 设置：`/#/settings`
   - 关于：`/#/about`

### 详细测试

参考 `VISUAL_TEST_CHECKLIST.md` 进行完整测试。

## 🎨 CSS 变量使用

### 在 Vue 组件中使用

```vue
<template>
  <div class="my-component">内容</div>
</template>

<style scoped>
.my-component {
  background-color: var(--color-bg-secondary);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
}
</style>
```

### 在 TypeScript 中使用

```typescript
import { useTheme } from '@/composables/useTheme';

const { isDark, actualTheme, customColors } = useTheme();

// 根据主题执行逻辑
if (isDark.value) {
  // 暗黑模式逻辑
}
```

## 🛠️ 扩展暗黑模式

### 添加新组件

1. 在新组件中使用 CSS 变量
2. 确保所有颜色使用变量
3. 测试明亮和暗黑模式

```vue
<style scoped>
.new-component {
  /* 使用变量，不要使用硬编码颜色 */
  background-color: var(--color-bg-secondary);
  color: var(--color-text-primary);
}
</style>
```

### 添加新 CSS 变量

在 `dark.css` 中添加：

```css
:root[data-theme="dark"] {
  --color-new-property: #value;
}

:root[data-theme="light"] {
  --color-new-property: #value;
}
```

### 添加新的自定义颜色选项

1. 在 `theme.js` 的 `defaultColors` 中添加
2. 在 `ThemeSwitcher.vue` 中添加颜色选择器
3. 在 `SettingsView.vue` 中添加设置项

## 📝 最佳实践

### 1. 始终使用 CSS 变量

❌ 不好:
```css
.card {
  background-color: #ffffff;
  color: #000000;
}
```

✅ 好:
```css
.card {
  background-color: var(--color-bg-secondary);
  color: var(--color-text-primary);
}
```

### 2. 使用语义化的变量名

❌ 不好:
```css
--color-1: #ffffff;
--color-2: #000000;
```

✅ 好:
```css
--color-bg-primary: #ffffff;
--color-text-primary: #000000;
```

### 3. 确保对比度

- 文字和背景对比度至少 4.5:1 (WCAG AA)
- 使用在线工具检查对比度
- 在两种主题下都测试

### 4. 测试边界情况

- 极长文本
- 空状态
- 错误状态
- 加载状态
- 响应式布局

## 🔧 常见问题

### Q: 主题切换时有闪烁？

A: 确保在 HTML 加载时立即应用主题：

```html
<script>
  // 在 head 中立即执行
  const theme = localStorage.getItem('livemirror_theme_preference');
  document.documentElement.setAttribute('data-theme', theme || 'light');
</script>
```

### Q: 某些元素没有适配暗黑模式？

A: 检查是否使用了硬编码颜色，改为使用 CSS 变量。

### Q: 自定义颜色不生效？

A: 确保在 `theme.js` 的 `defaultColors` 中定义了默认值。

### Q: 系统主题跟随不工作？

A: 检查浏览器是否支持 `matchMedia` API，确保使用 HTTPS 或 localhost。

## 📚 参考资料

- [Vue 3 文档](https://vuejs.org/)
- [Vite 文档](https://vitejs.dev/)
- [CSS Custom Properties](https://developer.mozilla.org/en-US/docs/Web/CSS/Using_CSS_custom_properties)
- [WCAG Contrast Requirements](https://www.w3.org/WAI/WCAG21/Understanding/contrast-minimum.html)

## 🎉 开发完成！

暗黑模式支持已全部实现，可以开始测试和使用了！
