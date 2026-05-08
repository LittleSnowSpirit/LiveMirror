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
  gap: 2px;
  padding: 0;
  border: none;
  border-radius: 0;
  background: transparent;
}

.stat-icon {
  display: none;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: var(--app-text);
  line-height: 1.2;
}

.stat-label {
  font-size: 11px;
  color: var(--app-text-faint);
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
