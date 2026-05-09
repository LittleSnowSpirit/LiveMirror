<template>
  <div ref="pageRef" class="home">
    <!-- Hero -->
    <header class="hero">
      <h1 class="hero-title" data-animate>LiveMirror</h1>
      <p class="hero-sub" data-animate style="transition-delay: 100ms">AI 驱动的直播复盘分析系统 — 把直播素材变成可执行的复盘结论</p>
    </header>

    <!-- Quick Actions -->
    <section class="section">
      <h2 class="section-label" data-animate>开始分析</h2>
      <div class="action-grid" data-stagger>
        <router-link to="/upload" class="action-card hover-lift" data-animate="scale">
          <div class="action-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" /><polyline points="17 8 12 3 7 8" /><line x1="12" y1="3" x2="12" y2="15" />
            </svg>
          </div>
          <div class="action-body">
            <span class="action-title">上传分析</span>
            <span class="action-desc">上传音频或视频文件，自动转写并生成分析报告</span>
          </div>
        </router-link>

        <router-link to="/danmu" class="action-card hover-lift" data-animate="scale">
          <div class="action-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
            </svg>
          </div>
          <div class="action-body">
            <span class="action-title">弹幕分析</span>
            <span class="action-desc">上传弹幕数据，分析情感曲线与关键词趋势</span>
          </div>
        </router-link>

        <router-link to="/report" class="action-card hover-lift" data-animate="scale">
          <div class="action-icon">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" /><line x1="16" y1="13" x2="8" y2="13" /><line x1="16" y1="17" x2="8" y2="17" /><polyline points="10 9 9 9 8 9" />
            </svg>
          </div>
          <div class="action-body">
            <span class="action-title">查看报告</span>
            <span class="action-desc">输入任务 ID 查看已有的分析报告和转写结果</span>
          </div>
        </router-link>
      </div>
    </section>

    <!-- Deep Analysis -->
    <section class="section">
      <h2 class="section-label" data-animate>深度优化</h2>
      <div class="feature-list" data-stagger>
        <router-link to="/attribution" class="feature-row" data-animate="slide-left">
          <span class="feature-name">归因分析</span>
          <span class="feature-desc">定位影响观众情绪的关键话术片段</span>
          <svg class="feature-arrow" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="5" y1="12" x2="19" y2="12" /><polyline points="12 5 19 12 12 19" />
          </svg>
        </router-link>
        <router-link to="/suggestions" class="feature-row" data-animate="slide-left">
          <span class="feature-name">话术建议</span>
          <span class="feature-desc">AI 诊断话术问题并给出优化方案</span>
          <svg class="feature-arrow" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="5" y1="12" x2="19" y2="12" /><polyline points="12 5 19 12 12 19" />
          </svg>
        </router-link>
        <router-link to="/trends" class="feature-row" data-animate="slide-left">
          <span class="feature-name">趋势对比</span>
          <span class="feature-desc">跨场次追踪情绪、话术质量和互动率变化</span>
          <svg class="feature-arrow" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <line x1="5" y1="12" x2="19" y2="12" /><polyline points="12 5 19 12 12 19" />
          </svg>
        </router-link>
      </div>
    </section>

    <!-- Recent Activity -->
    <section class="section">
      <div class="section-header">
        <h2 class="section-label" data-animate>最近任务</h2>
        <el-button text size="small" @click="loadLatestTask">刷新</el-button>
      </div>

      <el-skeleton v-if="loading" :rows="2" animated />

      <Transition name="fade-up" appear>
        <div v-if="!loading && latestTaskId" class="task-row" @click="openReport">
          <div class="task-main">
            <span class="task-name">{{ latestTaskName || '未命名文件' }}</span>
            <span class="task-id">{{ latestTaskId.slice(0, 8) }}</span>
          </div>
          <div class="task-meta">
            <el-tag v-if="taskStatus" :type="statusTagType(taskStatus.status)" size="small" effect="light">
              {{ statusLabel(taskStatus.status) }}
            </el-tag>
            <div v-if="taskStatus" class="task-progress-bar">
              <div class="task-progress-fill" :style="{ width: (taskStatus.progress ?? 0) + '%' }"></div>
            </div>
            <span v-if="taskStatus" class="task-pct">{{ taskStatus.progress ?? 0 }}%</span>
          </div>
        </div>
      </Transition>

      <div v-if="!loading && !latestTaskId" class="empty-hint">
        <span>还没有分析记录</span>
        <router-link to="/upload" class="empty-link">开始第一次分析</router-link>
      </div>
    </section>

    <!-- Overview Stats -->
    <section class="section">
      <h2 class="section-label" data-animate>本周概览</h2>
      <div class="stats-row" data-stagger>
        <div class="stat" data-animate="fade">
          <span class="stat-value">{{ analyzedCount }}</span>
          <span class="stat-label">已分析</span>
        </div>
        <div class="stat-divider"></div>
        <div class="stat" data-animate="fade">
          <span class="stat-value">--</span>
          <span class="stat-label">剩余配额</span>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { getStoredTaskId, getTaskStatus } from '../api';
import type { TaskInfo } from '../api';
import { useReveal } from '../composables/useReveal';
import { useCountUp } from '../composables/useCountUp';

const router = useRouter();
const loading = ref(false);
const latestTaskId = ref('');
const latestTaskName = ref('');
const taskStatus = ref<TaskInfo | null>(null);

const pageRef = ref<HTMLElement | null>(null);
const { observe } = useReveal();

const analyzedTarget = computed(() => taskStatus.value?.status === 'completed' ? 1 : 0);
const analyzedCount = useCountUp(analyzedTarget, { duration: 800 });

function statusLabel(status: string) {
  const mapping: Record<string, string> = {
    pending: '等待处理',
    processing: '处理中',
    transcribing: '转写中',
    analyzing: '分析中',
    completed: '已完成',
    failed: '已失败'
  };
  return mapping[status] || status;
}

function statusTagType(status: string) {
  if (status === 'completed') return 'success';
  if (status === 'failed') return 'danger';
  if (status === 'processing' || status === 'transcribing' || status === 'analyzing') return 'warning';
  return 'info';
}

async function loadLatestTask() {
  loading.value = true;
  latestTaskId.value = getStoredTaskId();
  latestTaskName.value = localStorage.getItem('livemirror:last-task-name') || '';
  try {
    if (!latestTaskId.value) { taskStatus.value = null; return; }
    const response = await getTaskStatus(latestTaskId.value);
    taskStatus.value = response.task;
    latestTaskName.value = response.task.filename;
  } catch {
    taskStatus.value = null;
  } finally {
    loading.value = false;
  }
}

function openReport() {
  if (!latestTaskId.value) { router.push('/report'); return; }
  router.push({ name: 'report', params: { taskId: latestTaskId.value } });
}

onMounted(() => {
  loadLatestTask();
  pageRef.value?.querySelectorAll('[data-animate]').forEach(el => observe(el as HTMLElement));
});
</script>

<style scoped>
.home {
  width: min(800px, 100%);
  margin: 0 auto;
  padding: var(--space-10) var(--space-6) var(--space-16);
}

/* ========== Hero ========== */
.hero {
  margin-bottom: var(--space-12);
}

.hero-title {
  font-family: var(--font-body);
  font-size: var(--text-3xl);
  font-weight: 700;
  letter-spacing: -0.04em;
  color: var(--app-text);
  margin-bottom: var(--space-3);
  line-height: 1.1;
}

.hero-sub {
  font-size: var(--text-base);
  font-weight: 400;
  color: var(--app-text-soft);
  line-height: 1.6;
  max-width: 520px;
}

/* ========== Section ========== */
.section {
  margin-bottom: var(--space-12);
}

.section-label {
  font-family: var(--font-body);
  font-size: var(--text-xs);
  font-weight: 600;
  color: var(--app-text-faint);
  text-transform: uppercase;
  letter-spacing: 0.08em;
  margin-bottom: var(--space-5);
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-5);
}

.section-header .section-label {
  margin-bottom: 0;
}

/* ========== Action Grid ========== */
.action-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1px;
  background: var(--app-border);
  border: 1px solid var(--app-border);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.action-card {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  padding: var(--space-5);
  background: var(--app-surface);
  text-decoration: none;
  transition: background var(--transition-fast);
}

.action-card:hover {
  background: var(--app-surface-soft);
}

.action-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md);
  background: var(--app-primary-soft);
  color: var(--app-primary);
  flex-shrink: 0;
  transition: transform 200ms ease;
}

.action-card:hover .action-icon {
  transform: scale(1.05);
}

.action-body {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.action-title {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--app-text);
  line-height: 1.4;
}

.action-desc {
  font-size: var(--text-xs);
  color: var(--app-text-faint);
  line-height: 1.5;
}

/* ========== Feature List ========== */
.feature-list {
  display: flex;
  flex-direction: column;
  border: 1px solid var(--app-border);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.feature-row {
  display: flex;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-4) var(--space-5);
  background: var(--app-surface);
  text-decoration: none;
  border-bottom: 1px solid var(--app-border);
  transition: background var(--transition-fast), border-left-color 200ms ease;
  border-left: 3px solid transparent;
}

.feature-row:hover {
  border-left-color: var(--app-primary);
}

.feature-row:last-child {
  border-bottom: none;
}

.feature-row:hover {
  background: var(--app-surface-soft);
}

.feature-name {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--app-text);
  min-width: 72px;
  flex-shrink: 0;
}

.feature-desc {
  flex: 1;
  font-size: var(--text-sm);
  color: var(--app-text-soft);
  line-height: 1.5;
}

.feature-arrow {
  color: var(--app-text-faint);
  flex-shrink: 0;
  transition: color var(--transition-fast), transform var(--transition-fast);
}

.feature-row:hover .feature-arrow {
  color: var(--app-primary);
  transform: translateX(2px);
}

/* ========== Task Row ========== */
.task-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-4);
  padding: var(--space-4) var(--space-5);
  border: 1px solid var(--app-border);
  border-radius: var(--radius-md);
  background: var(--app-surface);
  cursor: pointer;
  transition: background var(--transition-fast), border-color var(--transition-fast);
}

.task-row:hover {
  background: var(--app-surface-soft);
  border-color: var(--app-border-strong);
}

.task-main {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  min-width: 0;
}

.task-name {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--app-text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.task-id {
  font-size: var(--text-xs);
  font-family: var(--font-mono);
  color: var(--app-text-faint);
  flex-shrink: 0;
}

.task-meta {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  flex-shrink: 0;
}

.task-progress-bar {
  width: 80px;
  height: 3px;
  background: var(--app-border);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.task-progress-fill {
  height: 100%;
  background: var(--app-primary);
  border-radius: var(--radius-full);
  animation: progressBar 800ms var(--ease-out-expo) forwards;
}

@keyframes progressBar {
  from { width: 0; }
}

.task-pct {
  font-size: var(--text-xs);
  font-family: var(--font-mono);
  color: var(--app-text-faint);
  min-width: 32px;
  text-align: right;
}

/* ========== Empty Hint ========== */
.empty-hint {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-4) var(--space-5);
  border: 1px solid var(--app-border);
  border-radius: var(--radius-md);
  background: var(--app-surface);
}

.empty-hint span {
  font-size: var(--text-sm);
  color: var(--app-text-faint);
}

.empty-link {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--app-primary);
  text-decoration: none;
}

.empty-link:hover {
  text-decoration: underline;
}

/* ========== Stats Row ========== */
.stats-row {
  display: flex;
  align-items: center;
  gap: var(--space-8);
  padding: var(--space-5);
  border: 1px solid var(--app-border);
  border-radius: var(--radius-md);
  background: var(--app-surface);
}

.stat {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.stat-value {
  font-family: var(--font-body);
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--app-text);
  letter-spacing: -0.03em;
  line-height: 1;
}

.stat-label {
  font-size: var(--text-xs);
  color: var(--app-text-faint);
  letter-spacing: 0.02em;
}

.stat-divider {
  width: 1px;
  height: 32px;
  background: var(--app-border);
}

/* ========== Responsive ========== */
@media (max-width: 640px) {
  .home {
    padding: var(--space-8) var(--space-4) var(--space-12);
  }

  .hero-title {
    font-size: var(--text-2xl);
  }

  .action-grid {
    grid-template-columns: 1fr;
  }

  .task-row {
    flex-direction: column;
    align-items: flex-start;
    gap: var(--space-3);
  }

  .task-meta {
    width: 100%;
  }

  .task-progress-bar {
    flex: 1;
  }
}

/* ========== Transitions ========== */
.fade-up-enter-active {
  transition: opacity 400ms var(--ease-out-expo), transform 400ms var(--ease-out-expo);
}

.fade-up-enter-from {
  opacity: 0;
  transform: translateY(12px);
}

.fade-up-enter-to {
  opacity: 1;
  transform: translateY(0);
}
</style>
