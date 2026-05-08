<template>
  <div class="app-shell">
    <header class="topbar">
      <div class="topbar-left">
        <button
          class="hamburger-btn"
          type="button"
          aria-label="打开导航菜单"
          @click="drawerOpen = true"
        >
          <span class="hamburger-line"></span>
          <span class="hamburger-line"></span>
          <span class="hamburger-line"></span>
        </button>

        <div class="brand">
          <span class="brand-mark">
            <span class="brand-signal" aria-hidden="true"></span>
            LiveMirror
          </span>
          <span class="brand-copy">创作者工作室 · 数据工作台</span>
        </div>
      </div>

      <nav class="nav">
        <RouterLink to="/" class="nav-link">首页</RouterLink>
        <template v-if="authenticated">
          <RouterLink
            v-for="item in navigationFeatures"
            :key="item.id"
            :to="item.frontend_route || '/'"
            class="nav-link"
          >
            {{ item.navigation_label || item.name }}
          </RouterLink>
          <RouterLink to="/history" class="nav-link">历史记录</RouterLink>
          <RouterLink to="/danmu" class="nav-link">弹幕分析</RouterLink>
          <RouterLink to="/profile" class="nav-link">个人中心</RouterLink>
          <button class="theme-toggle" type="button" :aria-label="isDark ? '切换到亮色模式' : '切换到暗色模式'" @click="toggleTheme">
            {{ isDark ? '☾' : '☀' }}
          </button>
          <button class="nav-link nav-button" type="button" @click="handleLogout">退出</button>
        </template>
        <template v-else>
          <RouterLink to="/login" class="nav-link">登录</RouterLink>
          <RouterLink to="/register" class="nav-link">注册</RouterLink>
        </template>
      </nav>
    </header>

    <!-- Mobile drawer overlay -->
    <Transition name="drawer-overlay">
      <div
        v-if="drawerOpen"
        class="drawer-overlay"
        @click="drawerOpen = false"
      />
    </Transition>

    <!-- Mobile drawer -->
    <Transition name="drawer">
      <aside v-if="drawerOpen" class="drawer">
        <div class="drawer-header">
          <span class="brand-mark">
            <span class="brand-signal" aria-hidden="true"></span>
            LiveMirror
          </span>
          <button class="drawer-close" type="button" aria-label="关闭菜单" @click="drawerOpen = false">
            &times;
          </button>
        </div>

        <nav class="drawer-nav">
          <RouterLink to="/" class="drawer-link" @click="drawerOpen = false">首页</RouterLink>
          <template v-if="authenticated">
            <RouterLink
              v-for="item in navigationFeatures"
              :key="item.id"
              :to="item.frontend_route || '/'"
              class="drawer-link"
              @click="drawerOpen = false"
            >
              {{ item.navigation_label || item.name }}
            </RouterLink>
            <RouterLink to="/history" class="drawer-link" @click="drawerOpen = false">历史记录</RouterLink>
            <RouterLink to="/danmu" class="drawer-link" @click="drawerOpen = false">弹幕分析</RouterLink>
            <RouterLink to="/profile" class="drawer-link" @click="drawerOpen = false">个人中心</RouterLink>
          </template>
          <template v-else>
            <RouterLink to="/login" class="drawer-link" @click="drawerOpen = false">登录</RouterLink>
            <RouterLink to="/register" class="drawer-link" @click="drawerOpen = false">注册</RouterLink>
          </template>
        </nav>

        <div class="drawer-footer" v-if="authenticated">
          <button class="drawer-link" type="button" @click="toggleTheme">
            {{ isDark ? '☾ 暗色模式' : '☀ 亮色模式' }}
          </button>
          <button class="drawer-link drawer-logout" type="button" @click="handleLogout(); drawerOpen = false">
            退出登录
          </button>
        </div>
      </aside>
    </Transition>

    <main class="app-main">
      <Transition name="page-fade" mode="out-in">
        <RouterView />
      </Transition>
    </main>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { RouterView, RouterLink } from 'vue-router';
import { useRoute, useRouter } from 'vue-router';
import { getFeatures, isAuthenticated, logout, type FeatureInfo } from './api';

const route = useRoute();
const router = useRouter();
const features = ref<FeatureInfo[]>([]);
const authenticated = ref(isAuthenticated());
const drawerOpen = ref(false);
const isDark = ref(true);

function applyTheme(dark: boolean) {
  document.documentElement.dataset.theme = dark ? '' : 'light';
  if (!dark) {
    document.documentElement.dataset.theme = 'light';
  } else {
    delete document.documentElement.dataset.theme;
  }
}

function toggleTheme() {
  isDark.value = !isDark.value;
  applyTheme(isDark.value);
  localStorage.setItem('theme', isDark.value ? 'dark' : 'light');
}

function initTheme() {
  const saved = localStorage.getItem('theme');
  if (saved === 'light') {
    isDark.value = false;
    applyTheme(false);
  }
}

const navigationFeatures = computed(() => features.value.filter((feature) => (
  feature.enabled
  && feature.healthy
  && Boolean(feature.frontend_route)
  && Boolean(feature.navigation_label)
  && feature.group !== 'legacy'
)));

onMounted(() => {
  initTheme();
  void refreshNavigation();
});

watch(
  () => route.fullPath,
  () => {
    authenticated.value = isAuthenticated();
    void refreshNavigation();
  }
);

async function refreshNavigation() {
  if (!authenticated.value) {
    features.value = [];
    return;
  }

  try {
    const response = await getFeatures();
    features.value = response.features;
  } catch {
    features.value = [];
  }
}

async function handleLogout() {
  logout();
  authenticated.value = false;
  features.value = [];
  await router.push('/login');
}
</script>

<style>
@import './styles/tokens.css';

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html,
body,
#app {
  min-height: 100%;
}

body {
  background: var(--app-bg);
  color: var(--app-text);
  font-family: var(--font-body);
  font-size: var(--text-base);
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

a {
  color: inherit;
}

button,
input,
textarea,
select {
  font: inherit;
}

button,
a,
[role='button'] {
  cursor: pointer;
}

:focus-visible {
  outline: 2px solid var(--app-primary);
  outline-offset: 2px;
}

html {
  scroll-behavior: smooth;
}

h1, h2, h3, h4, h5, h6 {
  font-family: var(--font-heading);
  font-weight: 600;
  letter-spacing: -0.02em;
  line-height: 1.3;
  color: var(--app-text);
}

.app-shell {
  min-height: 100vh;
  background: transparent;
  color: var(--app-text);
}

.topbar {
  position: sticky;
  top: 0;
  z-index: 20;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4);
  padding: var(--space-4) 40px;
  border-bottom: 1px solid var(--app-border);
  background: var(--app-surface);
}

.brand {
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: var(--space-1);
}

.brand-mark {
  display: inline-flex;
  align-items: center;
  gap: 9px;
  font-family: var(--font-heading);
  font-size: 18px;
  font-weight: 600;
  letter-spacing: -0.01em;
}

.brand-signal {
  width: 10px;
  height: 10px;
  border-radius: var(--radius-sm);
  background: var(--app-primary);
  box-shadow: 0 0 0 4px var(--app-primary-soft);
}

.brand-copy {
  font-size: 12px;
  color: var(--app-text-soft);
}

.nav {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: var(--space-2);
}

.nav-link {
  display: inline-flex;
  align-items: center;
  min-height: 34px;
  padding: 0 var(--space-3);
  border: 1px solid transparent;
  border-radius: var(--radius-md);
  background: transparent;
  color: var(--app-text-soft);
  text-decoration: none;
  font-weight: 500;
  font-size: var(--text-sm);
  transition: border-color var(--transition-fast), color var(--transition-fast), background-color var(--transition-fast);
}

.nav-button {
  appearance: none;
}

.nav-link:hover {
  color: var(--app-text);
  border-color: var(--app-border);
}

.nav-link.router-link-active {
  border-color: var(--app-primary);
  color: var(--app-primary);
  background: var(--app-primary-soft);
}

.theme-toggle {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 34px;
  height: 34px;
  border: 1px solid var(--app-border);
  border-radius: var(--radius-full);
  background: transparent;
  color: var(--app-text-soft);
  font-size: 16px;
  cursor: pointer;
  transition: background var(--transition-fast), color var(--transition-fast), border-color var(--transition-fast);
}

.theme-toggle:hover {
  background: var(--app-surface-soft);
  color: var(--app-text);
  border-color: var(--app-border-strong);
}

.app-main {
  min-height: calc(100vh - 69px);
}

.home-page,
.upload-page,
.report-page,
.analysis-page {
  width: min(1180px, 100%);
  margin-right: auto;
  margin-left: auto;
}

.panel.el-card {
  overflow: hidden;
}

.panel h1,
.panel h2,
.panel h3 {
  color: var(--app-text);
  font-family: var(--font-heading);
  font-weight: 600;
  letter-spacing: -0.02em;
  line-height: 1.3;
}

.panel h1 { font-size: var(--text-3xl); }
.panel h2 { font-size: var(--text-2xl); }
.panel h3 { font-size: var(--text-xl); }

.el-card {
  border-color: var(--app-border) !important;
  background: var(--app-surface) !important;
  color: var(--app-text) !important;
  box-shadow: var(--app-shadow-card) !important;
}

.el-card__body {
  background: transparent !important;
  color: var(--app-text) !important;
}

.el-button {
  border-radius: var(--radius-md);
  font-weight: 500;
  letter-spacing: 0.01em;
}

.el-button--primary {
  --el-button-bg-color: var(--app-primary);
  --el-button-border-color: var(--app-primary);
  --el-button-text-color: #06110f;
  --el-button-hover-bg-color: var(--app-primary-strong);
  --el-button-hover-border-color: var(--app-primary-strong);
  --el-button-hover-text-color: #06110f;
  --el-button-active-bg-color: var(--app-primary-strong);
  --el-button-active-border-color: var(--app-primary-strong);
  --el-button-active-text-color: #06110f;
  background-color: var(--app-primary) !important;
  border-color: var(--app-primary) !important;
  color: #06110f !important;
}

.el-button--default,
.el-button.is-plain {
  --el-button-bg-color: var(--app-surface-soft);
  --el-button-border-color: var(--app-border);
  --el-button-text-color: var(--app-text);
  --el-button-hover-bg-color: var(--app-surface-strong);
  --el-button-hover-border-color: var(--app-primary);
  --el-button-hover-text-color: var(--app-primary-strong);
  --el-button-active-bg-color: var(--app-surface-strong);
  --el-button-active-border-color: var(--app-primary);
  background-color: var(--app-surface-soft) !important;
  border-color: var(--app-border) !important;
  color: var(--app-text) !important;
}

.el-button.is-text {
  --el-button-text-color: var(--app-primary-strong);
  --el-button-hover-text-color: var(--app-primary-strong);
  --el-button-hover-bg-color: var(--app-primary-soft);
  background-color: transparent !important;
  border-color: transparent !important;
  color: var(--app-primary-strong) !important;
}

.el-input__wrapper,
.el-textarea__inner {
  background-color: var(--app-bg-deep) !important;
  color: var(--app-text) !important;
  border-radius: var(--radius-md);
  box-shadow: 0 0 0 1px var(--app-border) inset !important;
}

.el-input__inner,
.el-textarea__inner {
  color: var(--app-text) !important;
  -webkit-text-fill-color: var(--app-text);
}

.el-input__inner::placeholder,
.el-textarea__inner::placeholder {
  color: var(--app-text-faint) !important;
  -webkit-text-fill-color: var(--app-text-faint);
}

.el-input-number,
.el-input-number .el-input,
.el-input-number .el-input__wrapper {
  background-color: var(--app-bg-deep) !important;
}

.el-input-number__decrease,
.el-input-number__increase {
  background-color: var(--app-surface-soft) !important;
  border-color: var(--app-border) !important;
  color: var(--app-text-soft) !important;
}

.el-input__wrapper:hover,
.el-textarea__inner:hover {
  box-shadow: 0 0 0 1px var(--app-primary) inset;
}

.el-progress-bar__outer {
  background-color: var(--app-surface-strong);
}

.el-progress-bar__inner {
  background: linear-gradient(90deg, var(--app-primary), var(--app-primary-strong));
}

.el-tag {
  border-color: var(--app-border) !important;
  background-color: var(--app-surface-soft) !important;
  color: var(--app-text) !important;
}

.el-alert {
  border-radius: var(--radius-md);
  background-color: var(--app-surface-soft) !important;
  color: var(--app-text) !important;
}

.el-table {
  --el-table-bg-color: var(--app-surface);
  --el-table-tr-bg-color: var(--app-surface);
  --el-table-header-bg-color: var(--app-surface-soft);
  --el-table-row-hover-bg-color: var(--app-surface-strong);
  --el-table-border-color: var(--app-border);
  --el-table-text-color: var(--app-text);
  --el-table-header-text-color: var(--app-text);
}

.el-empty {
  --el-empty-fill-color-0: var(--app-surface-soft);
  --el-empty-fill-color-1: var(--app-surface-strong);
  --el-empty-fill-color-2: var(--app-border);
  --el-empty-fill-color-3: var(--app-border-strong);
  --el-empty-fill-color-4: var(--app-surface-soft);
  --el-empty-fill-color-5: var(--app-surface-strong);
  color: var(--app-text-soft);
}

.el-empty__description,
.el-empty__description p {
  color: var(--app-text-soft) !important;
}

.el-empty__image svg,
.el-empty__image rect,
.el-empty__image path {
  fill: var(--app-surface-strong) !important;
  stroke: var(--app-border) !important;
}

.el-skeleton__item {
  background: linear-gradient(
    90deg,
    var(--app-surface-soft) 25%,
    var(--app-surface-strong) 37%,
    var(--app-surface-soft) 63%
  ) !important;
  background-size: 200% 100% !important;
  animation: skeleton-loading 1.5s ease-in-out infinite !important;
}

@keyframes skeleton-loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* Hamburger button — desktop hidden */
.hamburger-btn {
  display: none;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  padding: 0;
  border: 1px solid var(--app-border);
  border-radius: var(--radius-md);
  background: transparent;
  cursor: pointer;
  flex-shrink: 0;
  gap: 4px;
  flex-direction: column;
}

.hamburger-line {
  display: block;
  width: 18px;
  height: 2px;
  background: var(--app-text);
  border-radius: 1px;
}

.topbar-left {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  min-width: 0;
}

/* Drawer overlay */
.drawer-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  z-index: 40;
}

.drawer-overlay-enter-active,
.drawer-overlay-leave-active {
  transition: opacity 250ms ease;
}

.drawer-overlay-enter-from,
.drawer-overlay-leave-to {
  opacity: 0;
}

/* Drawer panel */
.drawer {
  position: fixed;
  top: 0;
  left: 0;
  bottom: 0;
  width: 280px;
  background: var(--app-surface);
  z-index: 41;
  display: flex;
  flex-direction: column;
  box-shadow: var(--app-shadow);
  overflow-y: auto;
}

.drawer-enter-active,
.drawer-leave-active {
  transition: transform 250ms ease;
}

.drawer-enter-from,
.drawer-leave-to {
  transform: translateX(-100%);
}

.drawer-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-4) var(--space-5);
  border-bottom: 1px solid var(--app-border);
}

.drawer-close {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border: none;
  border-radius: var(--radius-md);
  background: transparent;
  color: var(--app-text-soft);
  font-size: 22px;
  cursor: pointer;
  transition: background var(--transition-fast);
}

.drawer-close:hover {
  background: var(--app-surface-soft);
}

.drawer-nav {
  display: flex;
  flex-direction: column;
  padding: var(--space-3) var(--space-4);
  gap: var(--space-1);
  flex: 1;
}

.drawer-link {
  display: flex;
  align-items: center;
  min-height: 40px;
  padding: 0 var(--space-4);
  border: none;
  border-radius: var(--radius-md);
  background: transparent;
  color: var(--app-text-soft);
  text-decoration: none;
  font-size: var(--text-sm);
  font-weight: 500;
  transition: background var(--transition-fast), color var(--transition-fast);
}

.drawer-link:hover,
.drawer-link.router-link-active {
  background: var(--app-primary-soft);
  color: var(--app-primary);
}

.drawer-footer {
  padding: var(--space-3) var(--space-4);
  border-top: 1px solid var(--app-border);
}

.drawer-logout {
  width: 100%;
  color: var(--app-danger);
}

.drawer-logout:hover {
  background: var(--app-danger-soft);
  color: var(--app-danger);
}

@media (max-width: 720px) {
  .topbar {
    align-items: center;
    flex-direction: row;
    padding: 14px 20px;
  }

  .nav {
    display: none;
  }

  .hamburger-btn {
    display: flex;
  }
}

/* Page transition */
.page-fade-enter-active,
.page-fade-leave-active {
  transition: opacity 250ms ease-out, transform 250ms ease-out;
}

.page-fade-enter-from {
  opacity: 0;
  transform: translateY(8px);
}

.page-fade-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>
