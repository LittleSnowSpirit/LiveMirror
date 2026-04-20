<template>
  <div class="home-page">
    <section class="studio-brief">
      <div class="brief-copy">
        <p class="eyebrow">今日工作台</p>
        <h1>把直播素材变成可执行的复盘结论。</h1>
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
      <div class="metric-tile">
        <span class="metric-label">入口</span>
        <strong>上传</strong>
        <span>创建分析任务</span>
      </div>
      <div class="metric-tile">
        <span class="metric-label">产出</span>
        <strong>报告</strong>
        <span>转写、分段、摘要</span>
      </div>
      <div class="metric-tile">
        <span class="metric-label">优化</span>
        <strong>建议</strong>
        <span>归因、话术、趋势</span>
      </div>
    </section>

    <section class="grid workbench-grid">
      <el-card class="panel">
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

      <el-card class="panel workflow-panel">
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

      <el-card class="panel action-panel">
        <div class="panel-header">
          <div>
            <p class="panel-kicker">快捷入口</p>
            <h2>直接跳转</h2>
          </div>
        </div>

        <div class="shortcut-grid">
          <el-button plain @click="router.push('/upload')">上传</el-button>
          <el-button plain @click="router.push('/report')">报告</el-button>
          <el-button plain @click="router.push('/attribution')">归因</el-button>
          <el-button plain @click="router.push('/suggestions')">建议</el-button>
          <el-button plain @click="router.push('/trends')">趋势</el-button>
          <el-button plain @click="router.push('/register')">注册</el-button>
        </div>
      </el-card>
    </section>

    <section class="grid capability-grid">
      <el-card class="panel small">
        <p class="panel-kicker">核心能力</p>
        <h3>上传与任务</h3>
        <p class="copy">上传后自动创建任务，按状态进入分析链路。</p>
      </el-card>
      <el-card class="panel small">
        <p class="panel-kicker">核心能力</p>
        <h3>报告与导出</h3>
        <p class="copy">报告页聚合转写、分段、建议和导出操作。</p>
      </el-card>
      <el-card class="panel small">
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
  gap: 18px;
  width: min(1180px, 100%);
  margin: 0 auto;
  padding: 28px 24px 40px;
}

.studio-brief {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
  gap: 20px;
  padding: 28px;
  border: 1px solid var(--app-border);
  border-radius: 8px;
  background:
    linear-gradient(135deg, color-mix(in srgb, var(--app-primary) 10%, transparent), transparent 44%),
    var(--app-surface);
  box-shadow: var(--app-shadow);
}

.brief-copy {
  max-width: 720px;
}

.eyebrow,
.panel-kicker {
  color: var(--app-text-soft);
  font-size: 12px;
  letter-spacing: 0;
  text-transform: uppercase;
}

.studio-brief h1 {
  margin-top: 8px;
  font-size: clamp(28px, 4vw, 46px);
  line-height: 1.2;
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
  margin-top: 12px;
  max-width: 62ch;
  line-height: 1.7;
}

.hero-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-content: flex-start;
  justify-content: flex-end;
  min-width: 240px;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 16px;
}

.metrics-row {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
}

.metric-tile {
  display: flex;
  min-height: 118px;
  flex-direction: column;
  justify-content: space-between;
  padding: 16px;
  border: 1px solid var(--app-border);
  border-radius: 8px;
  background: color-mix(in srgb, var(--app-surface) 72%, var(--app-surface-soft));
  box-shadow: var(--app-shadow-soft);
}

.metric-label {
  color: var(--app-text-soft);
  font-size: 12px;
}

.metric-tile strong {
  color: var(--app-data);
  font-size: 28px;
  font-weight: 800;
}

.metric-tile span:last-child {
  color: var(--app-text-soft);
  font-size: 14px;
}

.workbench-grid {
  grid-template-columns: minmax(320px, 1.35fr) minmax(260px, 0.9fr) minmax(260px, 0.9fr);
}

.panel {
  border-radius: 8px;
}

.panel :deep(.el-card__body) {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 12px;
}

.task-id {
  padding: 10px 12px;
  border: 1px solid var(--app-border);
  border-radius: 8px;
  background: var(--app-surface-soft);
  font-size: 14px;
  font-weight: 700;
  word-break: break-all;
}

.task-file {
  font-size: 14px;
}

.status-block {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.panel-actions,
.shortcut-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.steps {
  display: flex;
  flex-direction: column;
  gap: 12px;
  padding-left: 0;
  list-style: none;
  line-height: 1.8;
}

.steps li {
  display: grid;
  grid-template-columns: 40px 1fr;
  align-items: center;
  gap: 10px;
}

.steps span {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 32px;
  border-radius: 8px;
  background: var(--app-surface-strong);
  color: var(--app-primary-strong);
  font-weight: 800;
}

.small h3 {
  font-size: 18px;
}

@media (max-width: 760px) {
  .studio-brief {
    flex-direction: column;
    align-items: stretch;
    padding: 20px;
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
