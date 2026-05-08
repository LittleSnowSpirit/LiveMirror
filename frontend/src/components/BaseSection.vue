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
  font-size: var(--text-xs);
  color: var(--app-primary-strong);
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0;
}

.section-title {
  font-family: var(--font-heading);
  font-size: var(--text-2xl);
  font-weight: 600;
  color: var(--app-text);
  letter-spacing: -0.02em;
  line-height: 1.3;
}
</style>
