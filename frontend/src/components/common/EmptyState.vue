<!--
统一空状态组件
功能：
- 空数据展示
- 插图展示
- 引导操作
-->

<template>
  <div class="empty-state">
    <!-- 插图 -->
    <div class="empty-icon" v-if="icon">
      {{ icon }}
    </div>
    
    <!-- 标题 -->
    <h3 class="empty-title" v-if="title">
      {{ title }}
    </h3>
    
    <!-- 描述 -->
    <p class="empty-description" v-if="description">
      {{ description }}
    </p>
    
    <!-- 操作按钮 -->
    <div class="empty-actions" v-if="actions && actions.length">
      <button
        v-for="(action, index) in actions"
        :key="index"
        class="action-btn"
        :class="action.type || 'primary'"
        @click="handleAction(action)"
      >
        {{ action.text }}
      </button>
    </div>
    
    <!-- 插槽：自定义内容 -->
    <slot></slot>
  </div>
</template>

<script setup lang="ts">
// ==================== Types ====================

interface Action {
  text: string;
  type?: 'primary' | 'secondary';
  onClick?: () => void;
}

// ==================== Props ====================

const props = defineProps<{
  icon?: string;
  title?: string;
  description?: string;
  actions?: Action[];
}>();

const emit = defineEmits<{
  (e: 'action', index: number): void;
}>();

// ==================== Methods ====================

const handleAction = (action: Action, index: number) => {
  if (action.onClick) {
    action.onClick();
  }
  emit('action', index);
};
</script>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 48px 24px;
  text-align: center;
}

.empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-title {
  font-size: var(--font-lg);
  font-weight: var(--font-weight-bold);
  color: var(--text-primary);
  margin: 0 0 8px 0;
}

.empty-description {
  font-size: var(--font-sm);
  color: var(--text-secondary);
  line-height: var(--line-height-normal);
  margin: 0 0 24px 0;
  max-width: 400px;
}

.empty-actions {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  justify-content: center;
}

.action-btn {
  padding: 8px 20px;
  border: none;
  border-radius: var(--radius-md);
  font-size: var(--font-sm);
  font-weight: var(--font-weight-medium);
  cursor: pointer;
  transition: all var(--duration-fast);
}

.action-btn.primary {
  background: var(--primary-color);
  color: #fff;
}

.action-btn.primary:hover {
  background: var(--primary-hover);
}

.action-btn.secondary {
  background: var(--bg-secondary);
  color: var(--text-primary);
}

.action-btn.secondary:hover {
  background: var(--border-normal);
}

/* ==================== 预设空状态样式 ==================== */

.empty-state.no-data .empty-icon {
  font-size: 80px;
}

.empty-state.no-search .empty-icon {
  font-size: 72px;
}

.empty-state.error .empty-icon {
  font-size: 64px;
  color: var(--error-color);
}

/* ==================== 响应式 ==================== */

@media (max-width: 768px) {
  .empty-state {
    padding: 32px 16px;
  }
  
  .empty-icon {
    font-size: 48px !important;
  }
  
  .empty-title {
    font-size: var(--font-md);
  }
}
</style>
