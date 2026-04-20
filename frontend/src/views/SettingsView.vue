<template>
  <div class="settings-view">
    <header class="header">
      <h1>⚙️ 设置</h1>
      <ThemeSwitcher />
    </header>

    <main class="main-content">
      <section class="card">
        <h2>🎨 主题设置</h2>
        
        <div class="setting-group">
          <div class="setting-item">
            <div class="setting-info">
              <h3>主题模式</h3>
              <p>选择明亮、暗黑或跟随系统主题</p>
            </div>
            <div class="setting-control">
              <div class="theme-mode-selector">
                <button
                  :class="{ active: themeMode === ThemeMode.LIGHT }"
                  @click="setThemeMode(ThemeMode.LIGHT)"
                >
                  ☀️ 明亮
                </button>
                <button
                  :class="{ active: themeMode === ThemeMode.DARK }"
                  @click="setThemeMode(ThemeMode.DARK)"
                >
                  🌙 暗黑
                </button>
                <button
                  :class="{ active: themeMode === ThemeMode.SYSTEM }"
                  @click="setThemeMode(ThemeMode.SYSTEM)"
                >
                  💻 系统
                </button>
              </div>
            </div>
          </div>

          <div class="setting-item">
            <div class="setting-info">
              <h3>主色调</h3>
              <p>自定义应用的主要颜色</p>
            </div>
            <div class="setting-control">
              <input
                type="color"
                :value="customColors['--color-primary'] || '#2563eb'"
                @input="setCustomColor('--color-primary', ($event.target as HTMLInputElement).value)"
                class="color-picker"
              />
            </div>
          </div>

          <div class="setting-item">
            <div class="setting-info">
              <h3>强调色</h3>
              <p>自定义应用的强调颜色</p>
            </div>
            <div class="setting-control">
              <input
                type="color"
                :value="customColors['--color-accent'] || '#7c3aed'"
                @input="setCustomColor('--color-accent', ($event.target as HTMLInputElement).value)"
                class="color-picker"
              />
            </div>
          </div>

          <div class="setting-item">
            <div class="setting-info">
              <h3>重置主题</h3>
              <p>恢复默认主题设置</p>
            </div>
            <div class="setting-control">
              <button class="btn btn-danger" @click="resetTheme">
                重置所有设置
              </button>
            </div>
          </div>
        </div>
      </section>

      <section class="card">
        <h2>📊 主题状态</h2>
        <div class="status-grid">
          <div class="status-item">
            <span class="status-label">当前模式:</span>
            <span class="status-value">{{ themeModeLabel }}</span>
          </div>
          <div class="status-item">
            <span class="status-label">实际主题:</span>
            <span class="status-value" :class="actualTheme">
              {{ actualTheme === 'dark' ? '🌙 暗黑' : '☀️ 明亮' }}
            </span>
          </div>
          <div class="status-item">
            <span class="status-label">系统主题:</span>
            <span class="status-value">{{ systemThemeLabel }}</span>
          </div>
          <div class="status-item">
            <span class="status-label">自定义颜色:</span>
            <span class="status-value">{{ Object.keys(customColors).length }} 个</span>
          </div>
        </div>
      </section>

      <section class="card">
        <h2>💾 导入/导出</h2>
        <div class="button-group">
          <button class="btn btn-primary" @click="exportConfig">
            📤 导出配置
          </button>
          <button class="btn btn-secondary" @click="importConfig">
            📥 导入配置
          </button>
        </div>
        <textarea
          v-model="configJson"
          placeholder="配置 JSON 将显示在这里..."
          rows="5"
          class="config-textarea"
        ></textarea>
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import ThemeSwitcher from '../components/ThemeSwitcher.vue';
import { useTheme, ThemeMode } from '../composables/useTheme';

const {
  themeMode,
  actualTheme,
  customColors,
  setThemeMode,
  setCustomColor,
  resetTheme,
  exportConfig,
  importConfig: importThemeConfig
} = useTheme();

const configJson = ref('');

const themeModeLabel = computed(() => {
  switch (themeMode.value) {
    case ThemeMode.LIGHT: return '明亮模式';
    case ThemeMode.DARK: return '暗黑模式';
    case ThemeMode.SYSTEM: return '跟随系统';
    default: return '未知';
  }
});

const systemThemeLabel = computed(() => {
  if (typeof window !== 'undefined' && window.matchMedia) {
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? '暗黑' : '明亮';
  }
  return '未知';
});

function exportConfigWrapper() {
  configJson.value = exportConfig();
}

function importConfigWrapper() {
  if (configJson.value.trim()) {
    const success = importThemeConfig(configJson.value);
    alert(success ? '配置导入成功！' : '配置导入失败，请检查 JSON 格式');
  }
}

// 覆盖导出导入函数
const exportConfig = exportConfigWrapper;
const importConfig = importConfigWrapper;
</script>

<style scoped>
.settings-view {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: var(--color-bg-primary);
  color: var(--color-text-primary);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 40px;
  background-color: var(--color-bg-secondary);
  border-bottom: 1px solid var(--color-border);
}

.header h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.main-content {
  flex: 1;
  padding: 40px;
  display: grid;
  gap: 24px;
  max-width: 900px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}

.card {
  background-color: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 24px;
}

.card h2 {
  margin: 0 0 20px 0;
  font-size: 18px;
  font-weight: 600;
}

.setting-group {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid var(--color-border);
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-info h3 {
  margin: 0 0 4px 0;
  font-size: 15px;
  font-weight: 500;
}

.setting-info p {
  margin: 0;
  font-size: 13px;
  color: var(--color-text-secondary);
}

.theme-mode-selector {
  display: flex;
  gap: 8px;
}

.theme-mode-selector button {
  padding: 8px 16px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background-color: var(--color-bg-tertiary);
  color: var(--color-text-primary);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.theme-mode-selector button:hover {
  background-color: var(--color-border);
}

.theme-mode-selector button.active {
  background-color: var(--color-primary);
  color: #ffffff;
  border-color: var(--color-primary);
}

.color-picker {
  width: 60px;
  height: 36px;
  padding: 0;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  cursor: pointer;
  background-color: var(--color-bg-primary);
}

.btn {
  padding: 10px 20px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all var(--transition-fast);
}

.btn-primary {
  background-color: var(--color-primary);
  color: #ffffff;
}

.btn-primary:hover {
  background-color: var(--color-primary-hover);
}

.btn-secondary {
  background-color: var(--color-bg-tertiary);
  color: var(--color-text-primary);
  border: 1px solid var(--color-border);
}

.btn-secondary:hover {
  background-color: var(--color-border);
}

.btn-danger {
  background-color: var(--color-error);
  color: #ffffff;
}

.btn-danger:hover {
  background-color: #dc2626;
}

.button-group {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.config-textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  background-color: var(--color-bg-tertiary);
  color: var(--color-text-primary);
  font-family: monospace;
  font-size: 13px;
  resize: vertical;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background-color: var(--color-bg-tertiary);
  border-radius: 8px;
}

.status-label {
  color: var(--color-text-secondary);
  font-size: 14px;
}

.status-value {
  font-weight: 500;
  font-size: 14px;
}

.status-value.dark {
  color: var(--color-primary);
}

.status-value.light {
  color: var(--color-warning);
}
</style>
