<template>
  <div class="stat-card">
    <div class="stat-icon" v-if="icon">{{ icon }}</div>
    <div class="stat-value">{{ value }}</div>
    <div class="stat-label">{{ label }}</div>
    <div v-if="trend !== undefined && trend !== null" class="stat-trend" :class="trend > 0 ? 'up' : 'down'">
      {{ trend > 0 ? '+' : '' }}{{ trend }}%
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  label: string;
  value: string | number;
  icon?: string;
  trend?: number;
}>();
</script>

<style scoped>
.stat-card {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  padding: var(--space-4);
  border: 1px solid var(--app-border);
  border-radius: var(--radius-lg);
  background: var(--app-surface);
  box-shadow: var(--app-shadow-card);
  transition: border-color var(--transition-fast);
}

.stat-card:hover {
  border-color: var(--app-primary);
}

.stat-icon {
  font-size: var(--text-2xl);
  line-height: 1;
  margin-bottom: var(--space-1);
}

.stat-value {
  font-family: var(--font-heading);
  font-size: var(--text-2xl);
  font-weight: 800;
  color: var(--app-text);
  letter-spacing: -0.02em;
}

.stat-label {
  font-size: var(--text-sm);
  color: var(--app-text-soft);
}

.stat-trend {
  font-size: var(--text-xs);
  font-weight: 600;
  margin-top: var(--space-1);
}

.stat-trend.up {
  color: var(--app-success);
}

.stat-trend.down {
  color: var(--app-danger);
}
</style>
