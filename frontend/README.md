# LiveMirror Frontend - 暗黑模式支持

## 🎨 功能特性

### 主题切换
- ✅ 暗黑/明亮主题一键切换
- ✅ 自动跟随系统主题偏好
- ✅ 主题偏好本地持久化
- ✅ 平滑过渡动画

### 自定义主题
- ✅ 自定义主色调
- ✅ 自定义强调色
- ✅ 导出/导入主题配置
- ✅ 一键重置主题

### 全面适配
- ✅ 所有页面暗黑模式适配
- ✅ 所有组件暗黑模式适配
- ✅ 响应式设计支持

## 📁 项目结构

```
frontend/
├── src/
│   ├── styles/
│   │   └── dark.css          # 暗黑模式主题样式
│   ├── composables/
│   │   └── useTheme.ts       # 主题切换逻辑
│   ├── components/
│   │   └── ThemeSwitcher.vue # 主题切换组件
│   ├── utils/
│   │   └── theme.js          # 主题管理工具
│   ├── views/
│   │   ├── HomeView.vue      # 首页 (测试页面)
│   │   ├── SettingsView.vue  # 设置页面
│   │   └── AboutView.vue     # 关于页面
│   ├── router/
│   │   └── index.ts          # 路由配置
│   ├── App.vue               # 根组件
│   └── main.ts               # 入口文件
├── index.html                # HTML 入口
├── package.json              # 项目配置
├── vite.config.ts            # Vite 配置
├── tsconfig.json             # TypeScript 配置
└── README.md                 # 说明文档
```

## 🚀 快速开始

### 安装依赖

```bash
cd frontend
npm install
```

### 开发模式

```bash
npm run dev
```

访问 http://localhost:3000

### 构建生产版本

```bash
npm run build
```

### 预览生产版本

```bash
npm run preview
```

## 🧪 测试清单

### 1. 主题切换测试
- [ ] 点击主题切换按钮
- [ ] 切换到明亮模式
- [ ] 切换到暗黑模式
- [ ] 切换到跟随系统
- [ ] 验证主题切换流畅

### 2. 页面适配测试
- [ ] 首页所有元素暗黑模式显示正常
- [ ] 设置页面所有元素暗黑模式显示正常
- [ ] 关于页面所有元素暗黑模式显示正常
- [ ] 检查所有页面文字对比度

### 3. 系统主题跟随测试
- [ ] 修改系统主题为明亮
- [ ] 验证应用自动切换到明亮模式
- [ ] 修改系统主题为暗黑
- [ ] 验证应用自动切换到暗黑模式

### 4. 自定义主题色测试
- [ ] 在设置页面选择主色调
- [ ] 验证主色调应用到所有元素
- [ ] 选择强调色
- [ ] 验证强调色应用到所有元素
- [ ] 重置所有自定义颜色
- [ ] 验证恢复到默认颜色

### 5. 持久化测试
- [ ] 切换主题后刷新页面
- [ ] 验证主题偏好被保存
- [ ] 自定义颜色后刷新页面
- [ ] 验证自定义颜色被保存

### 6. 视觉测试
- [ ] 检查所有按钮悬停效果
- [ ] 检查所有输入框焦点效果
- [ ] 检查所有卡片阴影效果
- [ ] 检查所有边框颜色
- [ ] 检查滚动条样式
- [ ] 检查过渡动画流畅度

## 🎨 CSS 变量

### 基础颜色
- `--color-bg-primary` - 主背景色
- `--color-bg-secondary` - 次背景色
- `--color-bg-tertiary` - 第三背景色

### 文字颜色
- `--color-text-primary` - 主文字色
- `--color-text-secondary` - 次文字色
- `--color-text-tertiary` - 第三文字色

### 边框颜色
- `--color-border` - 边框色
- `--color-border-light` - 浅边框色

### 主题色
- `--color-primary` - 主色调
- `--color-primary-hover` - 主色调悬停
- `--color-primary-active` - 主色调激活
- `--color-accent` - 强调色
- `--color-accent-hover` - 强调色悬停

### 状态色
- `--color-success` - 成功色
- `--color-warning` - 警告色
- `--color-error` - 错误色
- `--color-info` - 信息色

### 阴影
- `--shadow-sm` - 小阴影
- `--shadow-md` - 中阴影
- `--shadow-lg` - 大阴影

### 过渡
- `--transition-fast` - 快速过渡 (150ms)
- `--transition-normal` - 正常过渡 (250ms)
- `--transition-slow` - 慢速过渡 (350ms)

## 📝 使用说明

### 在组件中使用主题

```vue
<script setup lang="ts">
import { useTheme, ThemeMode } from '@/composables/useTheme';

const {
  themeMode,
  actualTheme,
  isDark,
  isLight,
  setThemeMode,
  toggleTheme,
  customColors,
  setCustomColor
} = useTheme();
</script>
```

### 在样式中使用 CSS 变量

```css
.my-component {
  background-color: var(--color-bg-secondary);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
}

.my-button:hover {
  background-color: var(--color-primary-hover);
}
```

## 🛠️ 技术栈

- **Vue 3** - 渐进式 JavaScript 框架
- **TypeScript** - 类型安全的 JavaScript
- **Vite** - 下一代前端构建工具
- **CSS Variables** - CSS 自定义属性
- **Composition API** - Vue 3 组合式 API

## 📄 许可证

MIT License
