<template>
  <div class="base-panel" :class="{ 'no-padding': noPadding }">
    <div v-if="title || $slots.header" class="panel-header">
      <slot name="header">
        <h3 v-if="title" class="panel-title">{{ title }}</h3>
        <p v-if="subtitle" class="panel-subtitle">{{ subtitle }}</p>
      </slot>
      <slot name="header-right" />
    </div>
    <div class="panel-body">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title?: string;
  subtitle?: string;
  noPadding?: boolean;
}>();
</script>

<style scoped>
.base-panel {
  background: var(--app-surface);
  border: 1px solid var(--app-border);
  border-radius: 6px;
  overflow: hidden;
}

.base-panel:not(.no-padding) {
  padding: var(--space-6);
}

.no-padding .panel-body {
  padding: 0;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--space-3);
  margin-bottom: var(--space-4);
}

.panel-title {
  font-family: var(--font-heading);
  font-size: var(--text-xl);
  font-weight: 600;
  color: var(--app-text);
  letter-spacing: -0.02em;
  line-height: 1.3;
}

.panel-subtitle {
  margin-top: var(--space-1);
  font-size: var(--text-sm);
  color: var(--app-text-soft);
  line-height: 1.5;
}

.panel-body {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}
</style>
