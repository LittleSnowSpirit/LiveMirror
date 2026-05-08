<template>
  <section class="base-section">
    <p v-if="kicker" class="kicker">{{ kicker }}</p>
    <h2 v-if="title" class="section-title">{{ title }}</h2>
    <slot />
  </section>
</template>

<script setup lang="ts">
defineProps<{
  title?: string;
  kicker?: string;
}>();
</script>

<style scoped>
.base-section {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.kicker {
  font-size: 13px;
  color: var(--app-text-faint);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin-bottom: 12px;
}

.section-title {
  font-size: 13px;
  color: var(--app-text-faint);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  line-height: 1.3;
}
</style>
