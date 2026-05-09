<template>
  <div class="template-selector">
    <div class="selector-header">
      <h3>报告模块配置</h3>
      <div class="preset-actions">
        <el-button size="small" text @click="applyPreset('compact')">简洁</el-button>
        <el-button size="small" text @click="applyPreset('detailed')">详细</el-button>
        <el-button size="small" text @click="applyPreset('data')">数据</el-button>
      </div>
    </div>

    <div ref="moduleListRef" class="module-list" data-stagger>
      <div v-for="(mod, index) in modules" :key="mod.key" class="module-item" data-animate>
        <el-switch v-model="mod.visible" @change="emitConfig" />
        <span class="module-label" :class="{ disabled: !mod.visible }">{{ mod.label }}</span>
        <div class="module-order">
          <el-button
            text
            size="small"
            :disabled="index === 0"
            @click="moveModule(index, -1)"
          >
            &uarr;
          </el-button>
          <el-button
            text
            size="small"
            :disabled="index === modules.length - 1"
            @click="moveModule(index, 1)"
          >
            &darr;
          </el-button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { reactive, onMounted, useTemplateRef } from 'vue';
import { useReveal } from '../composables/useReveal';

interface ModuleConfig {
  key: string;
  label: string;
  visible: boolean;
}

const defaultModules: ModuleConfig[] = [
  { key: 'overall_score', label: '综合得分', visible: true },
  { key: 'highlights', label: '爆点分析', visible: true },
  { key: 'crash_points', label: '翻车点', visible: true },
  { key: 'rhythm', label: '节奏分析', visible: true },
  { key: 'interaction', label: '互动指标', visible: true },
  { key: 'emotion_curve', label: '情绪曲线', visible: true },
  { key: 'speech_diversity', label: '话术多样性', visible: true },
  { key: 'suggestions', label: '建议', visible: true },
];

const presets: Record<string, boolean[]> = {
  compact: [true, true, true, false, false, false, false, true],
  detailed: [true, true, true, true, true, true, true, true],
  data: [true, false, false, true, true, true, true, false],
};

const modules = reactive<ModuleConfig[]>(defaultModules.map((m) => ({ ...m })));
const moduleListRef = useTemplateRef<HTMLElement>('moduleListRef');
const { observe } = useReveal();

onMounted(() => {
  if (moduleListRef.value) {
    moduleListRef.value.querySelectorAll<HTMLElement>('.module-item').forEach(observe);
  }
});

const emit = defineEmits<{
  'update:config': [config: { visible: string[]; order: string[] }];
}>();

function emitConfig() {
  emit('update:config', {
    visible: modules.filter((m) => m.visible).map((m) => m.key),
    order: modules.map((m) => m.key),
  });
}

function moveModule(index: number, direction: number) {
  const target = index + direction;
  if (target < 0 || target >= modules.length) return;
  const temp = modules[index];
  modules[index] = modules[target];
  modules[target] = temp;
  emitConfig();
}

function applyPreset(name: string) {
  const visibility = presets[name];
  if (!visibility) return;
  visibility.forEach((visible, i) => {
    if (modules[i]) modules[i].visible = visible;
  });
  emitConfig();
}
</script>

<style scoped>
.template-selector {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.selector-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.selector-header h3 {
  font-size: 14px;
  font-weight: 600;
  color: var(--app-text);
}

.preset-actions {
  display: flex;
  gap: 4px;
}

.module-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.module-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  border: 1px solid var(--app-border);
  border-radius: 6px;
  background: var(--app-surface-soft);
}

.module-label {
  flex: 1;
  font-size: 14px;
  color: var(--app-text);
  transition: color var(--transition-fast);
}

.module-label.disabled {
  color: var(--app-text-faint);
}

.module-order {
  display: flex;
  gap: 2px;
}

@media (max-width: 720px) {
  .selector-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>
