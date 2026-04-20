# 批量上传功能文档

## 功能概述

LiveMirror 前端批量上传功能已开发完成，支持多文件选择、进度显示和批量操作。

## 技术栈

- **框架**: Vue 3 + TypeScript
- **UI 库**: Element Plus
- **构建工具**: Vite

## 已实现功能

### 1. 多文件选择 ✅
- 支持拖拽上传
- 支持点击选择多个文件
- 文件大小限制检查（默认 100MB）

### 2. 文件列表显示 ✅
- 文件名
- 文件大小（自动格式化）
- 上传进度条
- 上传状态标签（待上传、上传中、完成、失败）
- 单个文件操作按钮（上传/删除/取消）

### 3. 批量操作 ✅
- **全部开始上传**: 并发上传（限制 3 个同时上传）
- **全部删除**: 带确认提示的批量删除
- 总进度显示

### 4. 进度追踪 ✅
- 单个文件实时进度
- 总体平均进度
- 上传统计（成功/失败数量）

### 5. 事件通知 ✅
- `upload-success`: 文件上传成功
- `upload-error`: 文件上传失败
- `upload-progress`: 上传进度更新

## 文件结构

```
src/
├── components/
│   └── BatchUploader.vue    # 批量上传组件（核心）
├── views/
│   └── Upload.vue           # 上传页面
├── router/
│   └── index.ts             # 路由配置（已添加 /upload）
└── App.vue                  # 主应用（已添加导航）
```

## 使用方法

### 基本使用

```vue
<template>
  <BatchUploader
    :upload-url="'/api/upload'"
    :max-file-size="100"
    @upload-success="handleSuccess"
    @upload-error="handleError"
    @upload-progress="handleProgress"
  />
</template>

<script setup lang="ts">
import BatchUploader from '@/components/BatchUploader.vue'
import type { FileWithProgress } from '@/components/BatchUploader.vue'

const handleSuccess = (file: FileWithProgress, response: any) => {
  console.log('上传成功:', file.name)
}

const handleError = (file: FileWithProgress, error: Error) => {
  console.error('上传失败:', file.name, error)
}

const handleProgress = (file: FileWithProgress, progress: number) => {
  console.log('进度:', file.name, progress + '%')
}
</script>
```

### 组件 Props

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| uploadUrl | string | '/api/upload' | 上传接口地址 |
| maxFileSize | number | undefined | 最大文件大小（MB） |

### 组件事件

| 事件名 | 参数 | 说明 |
|--------|------|------|
| upload-success | (file, response) | 文件上传成功 |
| upload-error | (file, error) | 文件上传失败 |
| upload-progress | (file, progress) | 上传进度更新 |

### 组件方法

通过 `ref` 访问：

```ts
const batchUploaderRef = ref()

// 清空文件列表
batchUploaderRef.value.clearFiles()

// 获取文件列表
const files = batchUploaderRef.value.getFiles()
```

## 运行项目

```bash
cd livemirror-frontend

# 安装依赖
npm install

# 开发模式
npm run dev

# 构建生产版本
npm run build

# 类型检查
npm run type-check
```

## 开发服务器

- **本地地址**: http://localhost:5175
- **上传页面**: http://localhost:5175/upload

## 后续优化建议

1. **断点续传**: 支持大文件分片上传和断点续传
2. **图片预览**: 上传图片时显示缩略图
3. **文件夹上传**: 支持上传整个文件夹
4. **上传队列管理**: 支持调整上传顺序
5. **离线缓存**: 支持离线添加文件，网络恢复后上传

## 注意事项

⚠️ **后端接口**: 当前前端已就绪，需要配置实际的后端上传接口地址（`/api/upload`）

⚠️ **CORS**: 如果后端接口跨域，需要在后端配置 CORS

⚠️ **文件大小**: 根据实际需求调整 `maxFileSize` 限制
