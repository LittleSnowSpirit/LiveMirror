<template>
  <div class="theme-switcher" :class="{ 'is-open': isOpen }">
    <!-- 主题切换按钮 -->
    <button
      class="theme-toggle-btn"
      @click="toggleDropdown"
      :title="`当前主题：${themeModeLabel}`"
      aria-label="切换主题"
    >
      <span class="theme-icon">
        <svg v-if="isDark" class="icon-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
        </svg>
        <svg v-else class="icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="5"/>
          <line x1="12" y1="1" x2="12" y2="3"/>
          <line x1="12" y1="21" x2="12" y2="23"/>
          <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
          <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
          <line x1="1" y1="12" x2="3" y2="12"/>
          <line x1="21" y1="12" x2="23" y2="12"/>
          <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
          <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
        </svg>
      </span>
      <span class="chevron">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="6 9 12 15 18 9"/>
        </svg>
      </span>
    </button>

    <!-- 主题选择下拉菜单 -->
    <div class="theme-dropdown" v-if="isOpen" v-click-outside="closeDropdown">
      <!-- 主题模式选择 -->
      <div class="theme-options">
        <button
          class="theme-option"
          :class="{ active: themeMode === ThemeMode.LIGHT }"
          @click="setThemeMode(ThemeMode.LIGHT)"
        >
          <span class="option-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="5"/>
              <line x1="12" y1="1" x2="12" y2="3"/>
              <line x1="12" y1="21" x2="12" y2="23"/>
              <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
              <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
              <line x1="1" y1="12" x2="3" y2="12"/>
              <line x1="21" y1="12" x2="23" y2="12"/>
              <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
              <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
            </svg>
          </span>
          <span class="option-label">明亮模式</span>
          <span class="option-check" v-if="themeMode === ThemeMode.LIGHT">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
          </span>
        </button>

        <button
          class="theme-option"
          :class="{ active: themeMode === ThemeMode.DARK }"
          @click="setThemeMode(ThemeMode.DARK)"
        >
          <span class="option-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
            </svg>
          </span>
          <span class="option-label">暗黑模式</span>
          <span class="option-check" v-if="themeMode === ThemeMode.DARK">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
          </span>
        </button>

        <button
          class="theme-option"
          :class="{ active: themeMode === ThemeMode.SYSTEM }"
          @click="setThemeMode(ThemeMode.SYSTEM)"
        >
          <span class="option-icon">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
              <line x1="8" y1="21" x2="16" y2="21"/>
              <line x1="12" y1="17" x2="12" y2="21"/>
            </svg>
          </span>
          <span class="option-label">跟随系统</span>
          <span class="option-check" v-if="themeMode === ThemeMode.SYSTEM">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3">
              <polyline points="20 6 9 17 4 12"/>
            </svg>
          </span>
        </button>
      </div>

      <!-- 分隔线 -->
      <div class="divider"></div>

      <!-- 快捷切换 -->
      <button class="quick-toggle" @click="toggleTheme">
        <span class="toggle-icon">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="17 1 21 5 17 9"/>
            <path d="M3 11V9a4 4 0 0 1 4-4h14"/>
            <polyline points="7 23 3 19 7 15"/>
            <path d="M21 13v2a4 4 0 0 1-4 4H3"/>
          </svg>
        </span>
        <span class="toggle-label">快速切换</span>
        <span class="toggle-hint">{{ isDark ? '切换到明亮' : '切换到暗黑' }}</span>
      </button>

      <!-- 分隔线 -->
      <div class="divider"></div>

      <!-- 自定义颜色 -->
      <div class="custom-colors-section">
        <div class="section-header">
          <span>主题色自定义</span>
          <button class="reset-btn" @click="resetAllCustomColors" title="重置所有自定义颜色">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="1 4 1 10 7 10"/>
              <path d="M3.51 15a9 9 0 1 0 2.13-9.36L1 10"/>
            </svg>
          </button>
        </div>

        <div class="color-picker-group">
          <label class="color-label">
            <span>主色调</span>
            <input
              type="color"
              :value="customColors['--color-primary'] || getDefaultColor('--color-primary')"
              @input="setCustomColor('--color-primary', $event.target.value)"
              class="color-input"
            />
          </label>
          
          <label class="color-label">
            <span>强调色</span>
            <input
              type="color"
              :value="customColors['--color-accent'] || getDefaultColor('--color-accent')"
              @input="setCustomColor('--color-accent', $event.target.value)"
              class="color-input"
            />
          </label>
        </div>
      </div>

      <!-- 当前状态 -->
      <div class="current-status">
        <span class="status-label">当前:</span>
        <span class="status-value" :class="actualTheme">
          {{ actualTheme === 'dark' ? '🌙 暗黑' : '☀️ 明亮' }}
        </span>
        <span v-if="isSystem" class="system-badge">系统</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { useTheme, ThemeMode } from '../composables/useTheme';

// 使用主题 composable
const {
  themeMode,
  actualTheme,
  isDark,
  isSystem,
  customColors,
  setThemeMode,
  toggleTheme,
  setCustomColor,
  resetAllCustomColors
} = useTheme();

// 下拉菜单状态
const isOpen = ref(false);

// 主题模式标签
const themeModeLabel = computed(() => {
  switch (themeMode.value) {
    case ThemeMode.LIGHT:
      return '明亮';
    case ThemeMode.DARK:
      return '暗黑';
    case ThemeMode.SYSTEM:
      return '系统';
    default:
      return '未知';
  }
});

// 默认颜色映射
const defaultColors: Record<string, string> = {
  '--color-primary': '#2563eb',
  '--color-accent': '#7c3aed'
};

// 获取默认颜色
function getDefaultColor(property: string): string {
  return defaultColors[property] || '#000000';
}

// 切换下拉菜单
function toggleDropdown() {
  isOpen.value = !isOpen.value;
}

// 关闭下拉菜单
function closeDropdown() {
  isOpen.value = false;
}

// 点击外部指令
const vClickOutside = {
  mounted(el: HTMLElement, binding: { value: () => void }) {
    el.clickOutsideEvent = (event: MouseEvent) => {
      if (!(el === event.target || el.contains(event.target as Node))) {
        binding.value();
      }
    };
    document.addEventListener('click', el.clickOutsideEvent);
  },
  unmounted(el: HTMLElement) {
    document.removeEventListener('click', el.clickOutsideEvent);
  }
};
</script>

<style scoped>
.theme-switcher {
  position: relative;
  display: inline-block;
}

.theme-toggle-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background-color: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: 8px;
  cursor: pointer;
  transition: all var(--transition-fast);
  color: var(--color-text-primary);
}

.theme-toggle-btn:hover {
  background-color: var(--color-bg-tertiary);
  border-color: var(--color-primary);
}

.theme-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
}

.theme-icon svg {
  width: 20px;
  height: 20px;
}

.chevron {
  display: flex;
  align-items: center;
  opacity: 0.6;
}

.chevron svg {
  width: 16px;
  height: 16px;
}

.theme-dropdown {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  width: 280px;
  background-color: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  box-shadow: var(--shadow-lg);
  padding: 8px;
  z-index: 1000;
  animation: slideDown 0.2s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.theme-options {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.theme-option {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 10px 12px;
  background: transparent;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  text-align: left;
  color: var(--color-text-primary);
  transition: background-color var(--transition-fast);
}

.theme-option:hover {
  background-color: var(--color-bg-tertiary);
}

.theme-option.active {
  background-color: var(--color-primary);
  color: #ffffff;
}

.option-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
}

.option-icon svg {
  width: 24px;
  height: 24px;
}

.option-label {
  flex: 1;
  font-size: 14px;
}

.option-check {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
}

.option-check svg {
  width: 18px;
  height: 18px;
}

.divider {
  height: 1px;
  background-color: var(--color-border);
  margin: 8px 0;
}

.quick-toggle {
  display: flex;
  align-items: center;
  gap: 12px;
  width: 100%;
  padding: 10px 12px;
  background: transparent;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  text-align: left;
  color: var(--color-text-primary);
  transition: background-color var(--transition-fast);
}

.quick-toggle:hover {
  background-color: var(--color-bg-tertiary);
}

.toggle-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
}

.toggle-icon svg {
  width: 24px;
  height: 24px;
}

.toggle-label {
  flex: 1;
  font-size: 14px;
  font-weight: 500;
}

.toggle-hint {
  font-size: 12px;
  opacity: 0.6;
}

.custom-colors-section {
  margin-top: 8px;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  font-size: 13px;
  font-weight: 500;
  color: var(--color-text-secondary);
}

.reset-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  background: transparent;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  color: var(--color-text-secondary);
  transition: all var(--transition-fast);
}

.reset-btn:hover {
  background-color: var(--color-bg-tertiary);
  color: var(--color-error);
}

.reset-btn svg {
  width: 16px;
  height: 16px;
}

.color-picker-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 8px 12px;
}

.color-label {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  font-size: 13px;
  color: var(--color-text-secondary);
}

.color-input {
  width: 40px;
  height: 28px;
  padding: 0;
  border: 1px solid var(--color-border);
  border-radius: 6px;
  cursor: pointer;
  background-color: var(--color-bg-primary);
}

.color-input::-webkit-color-swatch-wrapper {
  padding: 0;
}

.color-input::-webkit-color-swatch {
  border: none;
  border-radius: 4px;
}

.color-input::-moz-color-swatch {
  border: none;
  border-radius: 4px;
}

.current-status {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  margin-top: 8px;
  background-color: var(--color-bg-tertiary);
  border-radius: 8px;
  font-size: 13px;
}

.status-label {
  color: var(--color-text-secondary);
}

.status-value {
  font-weight: 500;
}

.status-value.dark {
  color: var(--color-primary);
}

.status-value.light {
  color: var(--color-warning);
}

.system-badge {
  margin-left: auto;
  padding: 2px 8px;
  background-color: var(--color-info);
  color: #ffffff;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 500;
}
</style>
