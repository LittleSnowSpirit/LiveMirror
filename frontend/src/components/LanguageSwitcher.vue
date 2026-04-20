<template>
  <div class="language-switcher">
    <button 
      class="language-btn" 
      @click="toggleDropdown"
      :aria-label="t('common.language')"
    >
      <span class="current-flag">{{ currentFlag }}</span>
      <span class="current-name">{{ currentName }}</span>
      <span class="arrow" :class="{ 'arrow-up': isOpen }">▼</span>
    </button>
    
    <transition name="dropdown">
      <div v-if="isOpen" class="dropdown-menu">
        <button
          v-for="lang in languages"
          :key="lang.code"
          class="dropdown-item"
          :class="{ active: currentLocale === lang.code }"
          @click="selectLanguage(lang.code)"
        >
          <span class="flag">{{ lang.flag }}</span>
          <span class="name">{{ lang.name }}</span>
        </button>
      </div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { 
  setLocale, 
  getLocaleOptions, 
  detectLocale,
  type Locale 
} from '../i18n';

const { locale, t } = useI18n();

// 语言选项
const languages = getLocaleOptions();

// 当前语言
const currentLocale = computed(() => locale.value as Locale);

// 当前语言的标志和名称
const currentFlag = computed(() => {
  const lang = languages.find(l => l.code === currentLocale.value);
  return lang?.flag || '🌐';
});

const currentName = computed(() => {
  const lang = languages.find(l => l.code === currentLocale.value);
  return lang?.name || 'Language';
});

// 下拉菜单状态
const isOpen = ref(false);

// 切换下拉菜单
function toggleDropdown() {
  isOpen.value = !isOpen.value;
}

// 选择语言
async function selectLanguage(code: Locale) {
  await setLocale(code);
  isOpen.value = false;
}

// 点击外部关闭下拉菜单
function handleClickOutside(event: MouseEvent) {
  const target = event.target as HTMLElement;
  if (!target.closest('.language-switcher')) {
    isOpen.value = false;
  }
}

// 挂载时添加点击外部监听
import { onMounted, onUnmounted } from 'vue';

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});
</script>

<style scoped>
.language-switcher {
  position: relative;
  display: inline-block;
}

.language-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: var(--bg-secondary, #f5f5f5);
  border: 1px solid var(--border-color, #e0e0e0);
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  color: var(--text-primary, #333);
  transition: all 0.2s ease;
}

.language-btn:hover {
  background: var(--bg-hover, #e8e8e8);
  border-color: var(--primary-color, #1890ff);
}

.current-flag {
  font-size: 18px;
}

.current-name {
  font-weight: 500;
}

.arrow {
  font-size: 10px;
  transition: transform 0.2s ease;
}

.arrow-up {
  transform: rotate(180deg);
}

.dropdown-menu {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  min-width: 160px;
  background: var(--bg-primary, #fff);
  border: 1px solid var(--border-color, #e0e0e0);
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  overflow: hidden;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 10px 16px;
  background: transparent;
  border: none;
  cursor: pointer;
  font-size: 14px;
  color: var(--text-primary, #333);
  transition: background 0.2s ease;
  text-align: left;
}

.dropdown-item:hover {
  background: var(--bg-hover, #f5f5f5);
}

.dropdown-item.active {
  background: var(--primary-color, #1890ff);
  color: #fff;
}

.flag {
  font-size: 18px;
}

/* 下拉动画 */
.dropdown-enter-active,
.dropdown-leave-active {
  transition: all 0.2s ease;
}

.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* 暗黑模式支持 */
@media (prefers-color-scheme: dark) {
  .language-btn {
    background: var(--bg-secondary, #2a2a2a);
    border-color: var(--border-color, #404040);
    color: var(--text-primary, #e0e0e0);
  }
  
  .language-btn:hover {
    background: var(--bg-hover, #3a3a3a);
  }
  
  .dropdown-menu {
    background: var(--bg-primary, #1a1a1a);
    border-color: var(--border-color, #404040);
  }
  
  .dropdown-item {
    color: var(--text-primary, #e0e0e0);
  }
  
  .dropdown-item:hover {
    background: var(--bg-hover, #2a2a2a);
  }
}
</style>
