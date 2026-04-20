<!--
统一 Loading 加载组件
功能：
- Spinner 加载
- 进度条加载
- 骨架屏加载
- 全屏加载
-->

<template>
  <div class="loading-wrapper" :class="[size, { fullscreen }]">
    <!-- Spinner 模式 -->
    <div class="loading-spinner" v-if="type === 'spinner'">
      <div class="spinner"></div>
      <p class="loading-text" v-if="text">{{ text }}</p>
    </div>
    
    <!-- 进度条模式 -->
    <div class="loading-progress" v-else-if="type === 'progress'">
      <div class="progress-bar">
        <div 
          class="progress-fill" 
          :style="{ width: progress + '%' }"
        ></div>
      </div>
      <p class="loading-text" v-if="text">{{ text }} ({{ progress }}%)</p>
    </div>
    
    <!-- 骨架屏模式 -->
    <div class="loading-skeleton" v-else-if="type === 'skeleton'">
      <div class="skeleton-item" v-for="i in skeletonCount" :key="i"></div>
    </div>
  </div>
</template>

<script setup lang="ts">
// ==================== Props ====================

const props = withDefaults(defineProps<{
  type?: 'spinner' | 'progress' | 'skeleton';
  size?: 'small' | 'medium' | 'large';
  text?: string;
  progress?: number;
  skeletonCount?: number;
  fullscreen?: boolean;
}>(), {
  type: 'spinner',
  size: 'medium',
  text: '',
  progress: 0,
  skeletonCount: 3,
  fullscreen: false
});
</script>

<style scoped>
.loading-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.loading-wrapper.fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.9);
  z-index: 9999;
}

/* ==================== Spinner ==================== */

.loading-spinner {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid var(--border-light);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.spinner.small {
  width: 24px;
  height: 24px;
  border-width: 3px;
}

.spinner.large {
  width: 64px;
  height: 64px;
  border-width: 5px;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* ==================== Progress ==================== */

.loading-progress {
  width: 100%;
  max-width: 400px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.progress-bar {
  width: 100%;
  height: 8px;
  background: var(--border-light);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--gradient-primary);
  border-radius: 4px;
  transition: width 0.3s ease;
}

/* ==================== Skeleton ==================== */

.loading-skeleton {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.skeleton-item {
  height: 20px;
  background: linear-gradient(
    90deg,
    var(--bg-tertiary) 25%,
    var(--border-light) 50%,
    var(--bg-tertiary) 75%
  );
  background-size: 200% 100%;
  border-radius: 4px;
  animation: shimmer 1.5s infinite;
}

.skeleton-item:first-child {
  height: 24px;
  width: 60%;
}

.skeleton-item:nth-child(2) {
  height: 16px;
  width: 80%;
}

@keyframes shimmer {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* ==================== Sizes ==================== */

.loading-text {
  font-size: var(--font-sm);
  color: var(--text-secondary);
  margin: 0;
}

.small .loading-text {
  font-size: var(--font-xs);
}

.large .loading-text {
  font-size: var(--font-md);
}
</style>
