<template>
  <div class="home-page">
    <section class="studio-brief">
      <div class="brief-copy">
        <p class="eyebrow">今日工作台</p>
        <h1 class="gradient-text">把直播素材变成可执行的复盘结论。</h1>
        <p class="hero-copy">
          从上传、任务状态、报告到归因和话术建议，核心链路保持在同一个工作台里，方便运营和创作者继续推进。
        </p>
      </div>

      <div class="hero-actions">
        <el-button type="primary" @click="router.push('/upload')">去上传</el-button>
        <el-button @click="router.push('/report')">看报告</el-button>
        <el-button @click="router.push('/login')">登录</el-button>
      </div>
    </section>

    <section class="metrics-row" aria-label="核心流程概览">
      <StatCard label="入口" value="上传" icon="📤" />
      <StatCard label="产出" value="报告" icon="📊" />
      <StatCard label="优化" value="建议" icon="💡" />
    </section>

    <section class="grid workbench-grid">
      <el-card class="panel workbench-panel stagger-in" style="--stagger-index: 0">
        <div class="panel-header">
          <div>
            <p class="panel-kicker">当前任务</p>
            <h2>最近一次上传</h2>
          </div>
          <el-button text @click="loadLatestTask">刷新</el-button>
        </div>

        <el-skeleton v-if="loading" :rows="3" animated />

        <template v-else-if="latestTaskId">
          <p class="task-id">{{ latestTaskId }}</p>
          <p class="task-file">{{ latestTaskName || '未记录文件名' }}</p>

          <div v-if="taskStatus" class="status-block">
            <el-tag :type="statusTagType(taskStatus.status)" effect="light">
              {{ statusLabel(taskStatus.status) }}
            </el-tag>
            <p class="status-note">进度 {{ taskStatus.progress ?? 0 }}%</p>
            <el-progress :percentage="taskStatus.progress ?? 0" :stroke-width="10" />
          </div>

          <div class="panel-actions">
            <el-button type="primary" @click="openReport">打开报告</el-button>
            <el-button @click="router.push('/report')">手动输入任务 ID</el-button>
          </div>
        </template>

        <el-empty v-else description="还没有上传记录" />
      </el-card>

      <el-card class="panel workbench-panel workflow-panel stagger-in" style="--stagger-index: 1">
        <div class="panel-header">
          <div>
            <p class="panel-kicker">主线流程</p>
            <h2>从文件到结论</h2>
          </div>
        </div>

        <ol class="steps">
          <li><span>01</span>上传文件，创建任务。</li>
          <li><span>02</span>查看任务状态和处理进度。</li>
          <li><span>03</span>进入报告、归因、建议和趋势页面。</li>
        </ol>
      </el-card>

      <el-card class="panel workbench-panel action-panel stagger-in" style="--stagger-index: 2">
        <div class="panel-header">
          <div>
            <p class="panel-kicker">快捷入口</p>
            <h2>直接跳转</h2>
          </div>
        </div>

        <div class="shortcut-grid">
          <el-button class="shortcut-btn" plain @click="router.push('/upload')">上传</el-button>
          <el-button class="shortcut-btn" plain @click="router.push('/report')">报告</el-button>
          <el-button class="shortcut-btn" plain @click="router.push('/attribution')">归因</el-button>
          <el-button class="shortcut-btn" plain @click="router.push('/suggestions')">建议</el-button>
          <el-button class="shortcut-btn" plain @click="router.push('/trends')">趋势</el-button>
          <el-button class="shortcut-btn" plain @click="router.push('/register')">注册</el-button>
        </div>
      </el-card>
    </section>

    <section class="grid capability-grid">
      <el-card class="panel small capability-card stagger-in" style="--stagger-index: 0">
        <p class="panel-kicker">核心能力</p>
        <h3>上传与任务</h3>
        <p class="copy">上传后自动创建任务，按状态进入分析链路。</p>
      </el-card>
      <el-card class="panel small capability-card stagger-in" style="--stagger-index: 1">
        <p class="panel-kicker">核心能力</p>
        <h3>报告与导出</h3>
        <p class="copy">报告页聚合转写、分段、建议和导出操作。</p>
      </el-card>
      <el-card class="panel small capability-card stagger-in" style="--stagger-index: 2">
        <p class="panel-kicker">核心能力</p>
        <h3>分析页</h3>
        <p class="copy">归因、建议和趋势页都只保留主线入口。</p>
      </el-card>
    </section>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { getStoredTaskId, getTaskStatus } from '../api';
import type { TaskInfo } from '../api';
import StatCard from '../components/StatCard.vue';

const router = useRouter();
const loading = ref(false);
const latestTaskId = ref('');
const latestTaskName = ref('');
const taskStatus = ref<TaskInfo | null>(null);

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
    if (!latestTaskId.value) {
      taskStatus.value = null;
      return;
    }

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
  if (!latestTaskId.value) {
    router.push('/report');
    return;
  }

  router.push({ name: 'report', params: { taskId: latestTaskId.value } });
}

onMounted(() => {
  loadLatestTask();
});
</script>

<style scoped>
.home-page {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  width: min(1180px, 100%);
  margin: 0 auto;
  padding: var(--space-6) var(--space-6) var(--space-10);
}

.studio-brief {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: var(--space-5);
  padding: var(--space-6);
  border: 1px solid var(--app-glass-border);
  border-radius: var(--radius-lg);
  background:
    linear-gradient(135deg, rgba(167, 139, 250, 0.08), transparent 44%),
    var(--app-glass-bg);
  backdrop-filter: blur(var(--app-glass-blur));
  -webkit-backdrop-filter: blur(var(--app-glass-blur));
  box-shadow: var(--app-shadow-glow);
  transition: box-shadow var(--transition-normal);
}

.studio-brief:hover {
  box-shadow: var(--app-glow);
}

.brief-copy {
  max-width: 720px;
}

.eyebrow,
.panel-kicker {
  color: var(--app-text-soft);
  font-size: var(--text-xs);
  letter-spacing: 0;
  text-transform: uppercase;
}

.studio-brief h1 {
  margin-top: var(--space-2);
  font-size: clamp(var(--text-3xl), 5vw, 52px);
  line-height: 1.15;
  font-weight: 800;
  letter-spacing: 0;
}

.hero-copy,
.copy,
.task-file,
.status-note,
.steps {
  color: var(--app-text-soft);
}

.hero-copy {
  margin-top: var(--space-3);
  max-width: 62ch;
  line-height: 1.7;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  align-content: flex-start;
  justify-content: flex-end;
  min-width: 240px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: var(--space-4);
}

/* Metrics Row — glass stat cards with hover lift */
.metrics-row {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: var(--space-3);
}

.metrics-row > * {
  background: var(--app-glass-bg);
  backdrop-filter: blur(var(--app-glass-blur));
  -webkit-backdrop-filter: blur(var(--app-glass-blur));
  border: 1px solid var(--app-glass-border);
  border-radius: var(--radius-lg);
  transition: transform var(--transition-normal), box-shadow var(--transition-normal), border-color var(--transition-normal);
}

.metrics-row > *:hover {
  transform: translateY(-2px);
  box-shadow: var(--app-glow);
  border-color: rgba(167, 139, 250, 0.2);
}

/* Workbench Grid — gradient left accent border */
.workbench-grid {
  grid-template-columns: minmax(320px, 1.35fr) minmax(260px, 0.9fr) minmax(260px, 0.9fr);
}

.workbench-panel {
  position: relative;
  overflow: hidden;
  background: var(--app-glass-bg);
  backdrop-filter: blur(var(--app-glass-blur));
  -webkit-backdrop-filter: blur(var(--app-glass-blur));
  border: 1px solid var(--app-glass-border);
  transition: box-shadow var(--transition-normal), border-color var(--transition-normal);
}

.workbench-panel::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: var(--app-gradient-primary);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  opacity: 0.6;
  transition: opacity var(--transition-normal);
}

.workbench-panel:hover {
  box-shadow: var(--app-glow);
  border-color: rgba(167, 139, 250, 0.2);
}

.workbench-panel:hover::before {
  opacity: 1;
}

.panel {
  border-radius: var(--radius-lg);
}

.panel :deep(.el-card__body) {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--space-3);
}

.task-id {
  padding: var(--space-2) var(--space-3);
  border: 1px solid var(--app-border);
  border-radius: var(--radius-lg);
  background: var(--app-surface-soft);
  font-size: var(--text-sm);
  font-weight: 700;
  word-break: break-all;
}

.task-file {
  font-size: var(--text-sm);
}

.status-block {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.panel-actions,
.shortcut-grid {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

/* Shortcut buttons — gradient border on hover */
.shortcut-btn {
  position: relative;
  transition: border-color var(--transition-normal), box-shadow var(--transition-normal);
}

.shortcut-btn:hover {
  border-color: transparent;
  box-shadow: var(--app-glow-accent);
}

.shortcut-btn::before {
  content: '';
  position: absolute;
  inset: 0;
  border-radius: inherit;
  padding: 1px;
  background: var(--app-gradient-border);
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask-composite: exclude;
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  pointer-events: none;
  opacity: 0;
  transition: opacity var(--transition-normal);
}

.shortcut-btn:hover::before {
  opacity: 1;
}

.steps {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  padding-left: 0;
  list-style: none;
  line-height: 1.8;
}

.steps li {
  display: grid;
  grid-template-columns: 40px 1fr;
  align-items: center;
  gap: var(--space-2);
}

.steps span {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 32px;
  border-radius: var(--radius-lg);
  background: var(--app-surface-strong);
  color: var(--app-primary-strong);
  font-weight: 800;
}

/* Capability cards — hover scale + glow */
.capability-card {
  transition: transform var(--transition-normal), box-shadow var(--transition-normal), border-color var(--transition-normal);
}

.capability-card:hover {
  transform: scale(1.03);
  box-shadow: var(--app-glow-strong);
  border-color: rgba(167, 139, 250, 0.25);
}

.small h3 {
  font-size: var(--text-lg);
}

@media (max-width: 760px) {
  .studio-brief {
    flex-direction: column;
    align-items: stretch;
    padding: var(--space-5);
  }

  .hero-actions {
    justify-content: flex-start;
    min-width: 0;
  }

  .metrics-row,
  .workbench-grid {
    grid-template-columns: 1fr;
  }
}
</style>
