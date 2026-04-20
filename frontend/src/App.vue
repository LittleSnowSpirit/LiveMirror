<template>
  <div class="app-shell">
    <header class="topbar">
      <div class="brand">
        <span class="brand-mark">
          <span class="brand-signal" aria-hidden="true"></span>
          LiveMirror
        </span>
        <span class="brand-copy">创作者工作室 · 数据工作台</span>
      </div>

      <nav class="nav">
        <RouterLink to="/" class="nav-link">首页</RouterLink>
        <RouterLink to="/upload" class="nav-link">上传</RouterLink>
        <RouterLink to="/report" class="nav-link">报告</RouterLink>
        <RouterLink to="/attribution" class="nav-link">归因</RouterLink>
        <RouterLink to="/suggestions" class="nav-link">建议</RouterLink>
        <RouterLink to="/trends" class="nav-link">趋势</RouterLink>
      </nav>
    </header>

    <main class="app-main">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue';
import { RouterView, RouterLink } from 'vue-router';
import { initTheme } from './utils/theme';

onMounted(() => {
  initTheme();
});
</script>

<style>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

:root {
  color-scheme: dark;
  --app-bg: #0b1110;
  --app-bg-deep: #080d0c;
  --app-surface: #121b18;
  --app-surface-soft: #18241f;
  --app-surface-strong: #20302a;
  --app-surface-raised: #17211e;
  --app-border: #2b3c35;
  --app-border-strong: #3e554c;
  --app-text: #eef6f2;
  --app-text-soft: #99aaa3;
  --app-text-faint: #71847b;
  --app-primary: #2dd4bf;
  --app-primary-strong: #5eead4;
  --app-primary-soft: rgba(45, 212, 191, 0.14);
  --app-accent: #ff7a59;
  --app-warning: #f2b84b;
  --app-data: #8de0d4;
  --app-success: #4ade80;
  --app-danger: #fb7185;
  --app-shadow: 0 22px 60px rgba(0, 0, 0, 0.34);
  --app-shadow-soft: 0 12px 34px rgba(0, 0, 0, 0.24);

  --el-bg-color: var(--app-surface);
  --el-bg-color-page: var(--app-bg);
  --el-bg-color-overlay: var(--app-surface-raised);
  --el-border-color: var(--app-border);
  --el-border-color-light: var(--app-border);
  --el-border-color-lighter: var(--app-border);
  --el-card-bg-color: var(--app-surface);
  --el-color-primary: var(--app-primary);
  --el-color-primary-light-3: #55decd;
  --el-color-primary-light-5: #2f8f83;
  --el-color-primary-light-7: #255f58;
  --el-color-primary-light-8: #1d463f;
  --el-color-primary-light-9: #17342f;
  --el-color-primary-dark-2: var(--app-primary-strong);
  --el-fill-color: var(--app-surface-soft);
  --el-fill-color-blank: var(--app-surface);
  --el-fill-color-light: var(--app-surface-soft);
  --el-fill-color-lighter: var(--app-surface-soft);
  --el-text-color-primary: var(--app-text);
  --el-text-color-regular: var(--app-text);
  --el-text-color-secondary: var(--app-text-soft);
  --el-text-color-placeholder: var(--app-text-faint);
  --el-mask-color: rgba(8, 13, 12, 0.72);
  --el-disabled-bg-color: #111816;
  --el-disabled-text-color: var(--app-text-faint);
}

[data-theme='dark'] {
  color-scheme: dark;
  --app-bg: #0b1110;
  --app-bg-deep: #080d0c;
  --app-surface: #121b18;
  --app-surface-soft: #18241f;
  --app-surface-strong: #20302a;
  --app-surface-raised: #17211e;
  --app-border: #2b3c35;
  --app-border-strong: #3e554c;
  --app-text: #eef6f2;
  --app-text-soft: #99aaa3;
  --app-text-faint: #71847b;
  --app-primary: #2dd4bf;
  --app-primary-strong: #5eead4;
  --app-primary-soft: rgba(45, 212, 191, 0.14);
  --app-accent: #ff7a59;
  --app-warning: #f2b84b;
  --app-data: #8de0d4;
  --app-success: #4ade80;
  --app-danger: #fb7185;
  --app-shadow: 0 22px 60px rgba(0, 0, 0, 0.34);
  --app-shadow-soft: 0 12px 34px rgba(0, 0, 0, 0.24);
}

html,
body,
#app {
  min-height: 100%;
}

body {
  background:
    linear-gradient(180deg, rgba(45, 212, 191, 0.09), rgba(45, 212, 191, 0) 300px),
    linear-gradient(90deg, rgba(255, 122, 89, 0.05), rgba(255, 122, 89, 0) 460px),
    var(--app-bg);
  color: var(--app-text);
  font-family: Inter, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
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
  outline: 3px solid rgba(15, 118, 110, 0.28);
  outline-offset: 2px;
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
  gap: 16px;
  padding: 14px 24px;
  border-bottom: 1px solid var(--app-border);
  background: rgba(14, 21, 19, 0.9);
  box-shadow: var(--app-shadow-soft);
  backdrop-filter: blur(14px);
}

.brand {
  display: flex;
  min-width: 0;
  flex-direction: column;
  gap: 4px;
}

.brand-mark {
  display: inline-flex;
  align-items: center;
  gap: 9px;
  font-size: 18px;
  font-weight: 700;
  letter-spacing: 0;
}

.brand-signal {
  width: 10px;
  height: 10px;
  border-radius: 3px;
  background: var(--app-accent);
  box-shadow: 0 0 0 4px color-mix(in srgb, var(--app-accent) 16%, transparent);
}

.brand-copy {
  font-size: 12px;
  color: var(--app-text-soft);
}

.nav {
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 8px;
}

.nav-link {
  display: inline-flex;
  align-items: center;
  min-height: 36px;
  padding: 0 12px;
  border: 1px solid var(--app-border);
  border-radius: 8px;
  background: color-mix(in srgb, var(--app-surface) 82%, var(--app-surface-soft));
  color: var(--app-text);
  text-decoration: none;
  font-weight: 600;
  transition: border-color 0.18s ease, color 0.18s ease, background-color 0.18s ease, box-shadow 0.18s ease;
}

.nav-link:hover,
.nav-link.router-link-active {
  border-color: var(--app-primary);
  color: var(--app-primary-strong);
  background: var(--app-primary-soft);
  box-shadow: inset 0 -2px 0 var(--app-primary);
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
  font-weight: 760;
  letter-spacing: 0;
}

.el-card {
  border-color: var(--app-border) !important;
  background:
    linear-gradient(180deg, rgba(45, 212, 191, 0.035), rgba(45, 212, 191, 0)),
    var(--app-surface) !important;
  color: var(--app-text) !important;
  box-shadow: var(--app-shadow-soft) !important;
}

.el-card__body {
  background: transparent !important;
  color: var(--app-text) !important;
}

.el-button {
  border-radius: 8px;
  font-weight: 650;
  letter-spacing: 0;
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
  border-radius: 8px;
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
  border-radius: 8px;
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
}

@media (max-width: 720px) {
  .topbar {
    align-items: flex-start;
    flex-direction: column;
  }

  .nav {
    width: 100%;
    justify-content: flex-start;
  }
}
</style>
