<template>
  <div ref="cardEl" class="stat-card hover-lift" data-animate="fade">
    <div class="stat-icon" v-if="icon">{{ icon }}</div>
    <div class="stat-value">{{ displayValue }}</div>
    <div class="stat-label">{{ label }}</div>
    <div v-if="trend !== undefined && trend !== null" class="stat-trend" :class="trend > 0 ? 'up' : 'down'">
      {{ trend > 0 ? '+' : '' }}{{ trend }}%
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue';
import { useCountUp } from '../composables/useCountUp';
import { useReveal } from '../composables/useReveal';

const props = defineProps<{
  label: string;
  value: string | number;
  icon?: string;
  trend?: number;
}>();

const cardEl = ref<HTMLElement | null>(null);
const { observe } = useReveal();
onMounted(() => { if (cardEl.value) observe(cardEl.value); });

const numericValue = computed(() => {
  const n = typeof props.value === 'number' ? props.value : parseFloat(String(props.value));
  return isNaN(n) ? 0 : n;
});

const isNumeric = computed(() => typeof props.value === 'number' || !isNaN(parseFloat(String(props.value))));
const animatedDisplay = useCountUp(numericValue, { duration: 800 });
const displayValue = computed(() => isNumeric.value ? animatedDisplay.value : props.value);
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
