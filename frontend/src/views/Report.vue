<template>
  <div class="report-page">
    <el-card class="panel">
      <div class="header-row">
        <div>
          <p class="kicker">报告</p>
          <h1>查看任务报告</h1>
        </div>
        <div class="header-actions">
          <el-button @click="refresh">刷新</el-button>
          <el-button :disabled="!taskId" @click="exportAs('json')">导出 JSON</el-button>
          <el-button type="primary" :disabled="!taskId" @click="exportAs('markdown')">导出 Markdown</el-button>
        </div>
      </div>

      <div class="query-row">
        <el-input v-model="taskIdInput" placeholder="输入任务 ID" />
        <el-button type="primary" :loading="loading" @click="loadReport">加载</el-button>
      </div>

      <el-alert v-if="errorMessage" :title="errorMessage" type="error" :closable="false" show-icon />
    </el-card>

    <el-skeleton v-if="loading && !taskInfo" :rows="6" animated />

    <template v-else>
      <el-card v-if="taskInfo" class="panel">
        <div class="panel-header">
          <div>
            <p class="kicker">任务状态</p>
            <h2>{{ taskInfo.filename }}</h2>
          </div>
          <el-tag :type="statusTagType(taskInfo.status)" effect="light">
            {{ statusLabel(taskInfo.status) }}
          </el-tag>
        </div>

        <p class="meta">任务 ID：{{ taskInfo.task_id }}</p>
        <p class="meta">进度：{{ taskInfo.progress ?? 0 }}%</p>
        <el-progress :percentage="taskInfo.progress ?? 0" :stroke-width="10" />
        <p v-if="taskInfo.error_message" class="error-text">{{ taskInfo.error_message }}</p>
      </el-card>

      <el-card v-if="reportData" class="panel">
        <div class="panel-header">
          <div>
            <p class="kicker">摘要</p>
            <h2>分析结果</h2>
          </div>
        </div>

        <div class="summary-grid">
          <div class="summary-item">
            <span class="label">时长</span>
            <strong>{{ formatDuration(reportData.duration) }}</strong>
          </div>
          <div class="summary-item">
            <span class="label">文件</span>
            <strong>{{ reportData.filename }}</strong>
          </div>
          <div class="summary-item">
            <span class="label">任务</span>
            <strong>{{ reportData.task_id }}</strong>
          </div>
        </div>

        <div class="section">
          <h3>转写文本</h3>
          <pre class="transcript">{{ reportData.transcription || '暂无转写文本' }}</pre>
        </div>

        <div class="section">
          <h3>分段</h3>
          <el-table v-if="segmentRows.length" :data="segmentRows" border>
            <el-table-column prop="index" label="#" width="60" />
            <el-table-column prop="start_time" label="开始" width="100" />
            <el-table-column prop="end_time" label="结束" width="100" />
            <el-table-column prop="content" label="内容" min-width="260" />
          </el-table>
          <el-empty v-else description="暂无分段数据" />
        </div>

        <div class="section two-col">
          <div>
            <h3>话术分析</h3>
            <ul class="list" v-if="techniqueRows.length">
              <li v-for="(item, index) in techniqueRows" :key="index">{{ item }}</li>
            </ul>
            <el-empty v-else description="暂无话术分析" />
          </div>

          <div>
            <h3>归因分析</h3>
            <ul class="list" v-if="attributionRows.length">
              <li v-for="(item, index) in attributionRows" :key="index">{{ item }}</li>
            </ul>
            <el-empty v-else description="暂无归因分析" />
          </div>
        </div>

        <div class="section two-col">
          <div>
            <h3>建议</h3>
            <ul class="list" v-if="suggestionRows.length">
              <li v-for="(item, index) in suggestionRows" :key="index">{{ item }}</li>
            </ul>
            <el-empty v-else description="暂无建议" />
          </div>

          <div>
            <h3>摘要文案</h3>
            <p class="summary-text">{{ reportSummaryText }}</p>
          </div>
        </div>
      </el-card>

      <el-empty v-else-if="!loading && taskId" description="报告尚未准备好" />
    </template>

    <ExportPanel v-if="taskId" :task-id="taskId" @share="showShareDialog = true" />
    <ShareDialog v-model:visible="showShareDialog" :task-id="taskId" />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import { exportReport, getReport, getStoredTaskId, getTaskStatus, setStoredTaskId } from '../api';
import { ElMessage } from 'element-plus';
import type { ReportData, TaskInfo } from '../api';
import ExportPanel from '../components/ExportPanel.vue';
import ShareDialog from '../components/ShareDialog.vue';

const showShareDialog = ref(false);

const route = useRoute();
const taskIdInput = ref('');
const taskId = computed(() => taskIdInput.value.trim());
const loading = ref(false);
const errorMessage = ref('');
const taskInfo = ref<TaskInfo | null>(null);
const reportData = ref<ReportData | null>(null);

const segmentRows = computed(() => {
  const segments = reportData.value?.segments || [];
  return segments.map((segment, index) => ({
    index: index + 1,
    start_time: formatTime((segment as any).start_time ?? (segment as any).start ?? 0),
    end_time: formatTime((segment as any).end_time ?? (segment as any).end ?? 0),
    content: String((segment as any).content ?? (segment as any).text ?? '')
  }));
});

const techniqueRows = computed(() => flattenItems(reportData.value?.speaking_techniques));
const attributionRows = computed(() => flattenItems(reportData.value?.attribution_analysis));
const suggestionRows = computed(() => flattenItems(reportData.value?.suggestions));
const reportSummaryText = computed(() => {
  if (!reportData.value) {
    return '暂无摘要';
  }

  if (reportData.value.summary_text) {
    return reportData.value.summary_text;
  }

  if (typeof reportData.value.summary === 'string') {
    return reportData.value.summary;
  }

  if (reportData.value.summary) {
    return JSON.stringify(reportData.value.summary, null, 2);
  }

  return '暂无摘要';
});

function flattenItems(items?: Array<Record<string, unknown>>) {
  return (items || []).map((item) => {
    const title = String(item.title ?? item.type ?? item.name ?? '项目');
    const description = String(item.description ?? item.content ?? item.summary ?? '');
    return description ? `${title}：${description}` : title;
  });
}

function formatDuration(seconds?: number | null) {
  if (!seconds || Number.isNaN(seconds)) {
    return '--';
  }

  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

function formatTime(value: unknown) {
  if (typeof value !== 'number' || Number.isNaN(value)) {
    return '--';
  }

  return `${value.toFixed(2)}s`;
}

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

async function loadReport() {
  const currentTaskId = taskId.value || route.params.taskId?.toString() || route.query.taskId?.toString() || getStoredTaskId();

  if (!currentTaskId) {
    errorMessage.value = '请输入任务 ID';
    taskInfo.value = null;
    reportData.value = null;
    return;
  }

  taskIdInput.value = currentTaskId;
  loading.value = true;
  errorMessage.value = '';

  try {
    setStoredTaskId(currentTaskId);
    const statusResponse = await getTaskStatus(currentTaskId);
    taskInfo.value = statusResponse.task;

    if (statusResponse.task.status === 'completed') {
      const reportResponse = await getReport(currentTaskId);
      reportData.value = reportResponse.data;
      localStorage.setItem('livemirror:last-task-name', reportResponse.data.filename || statusResponse.task.filename);
    } else {
      reportData.value = null;
    }
  } catch (error: any) {
    const message = error?.response?.data?.detail || error?.response?.data?.error || '报告加载失败';
    errorMessage.value = message;
    taskInfo.value = null;
    reportData.value = null;
  } finally {
    loading.value = false;
  }
}

async function exportAs(format: 'json' | 'markdown') {
  if (!taskId.value) {
    ElMessage.warning('请输入任务 ID');
    return;
  }

  try {
    const blob = await exportReport(taskId.value, format);
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `livemirror-report-${taskId.value}.${format === 'json' ? 'json' : 'md'}`;
    link.click();
    URL.revokeObjectURL(url);
    ElMessage.success('导出完成');
  } catch {
    ElMessage.error('导出失败');
  }
}

function refresh() {
  loadReport();
}

onMounted(() => {
  taskIdInput.value = (route.params.taskId?.toString() || route.query.taskId?.toString() || getStoredTaskId() || '').trim();
  if (taskIdInput.value) {
    loadReport();
  }
});
</script>

<style scoped>
.report-page {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  padding: var(--space-6) var(--space-6) var(--space-10);
}

.panel {
  border-radius: var(--radius-lg);
  background: var(--app-surface);
}

.panel :deep(.el-card__body) {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.header-row,
.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--space-4);
}

.kicker {
  font-size: var(--text-xs);
  color: var(--app-primary-strong);
  font-weight: 800;
  text-transform: uppercase;
}

h1,
h2,
h3 {
  color: var(--app-text);
  font-weight: 780;
  letter-spacing: 0;
}

.query-row,
.header-actions,
.summary-grid,
.two-col {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.query-row > :first-child {
  flex: 1;
  min-width: 240px;
}

.meta,
.error-text,
.summary-text,
.list {
  color: var(--app-text-soft);
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
}

.summary-item {
  padding: var(--space-3);
  border: 1px solid var(--app-border);
  border-radius: var(--radius-lg);
  background: var(--app-bg-deep);
}

.summary-item .label {
  display: block;
  margin-bottom: var(--space-2);
  color: var(--app-text-soft);
  font-size: var(--text-xs);
}

.section {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  padding-top: var(--space-1);
}

.transcript {
  padding: var(--space-4);
  border: 1px solid var(--app-border);
  border-radius: var(--radius-lg);
  background: var(--app-bg-deep);
  color: var(--app-text);
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.7;
}

.two-col > div {
  flex: 1;
  min-width: 280px;
}

.list {
  padding-left: 18px;
  line-height: 1.7;
}

@media (max-width: 720px) {
  .header-row,
  .panel-header {
    flex-direction: column;
  }
}
</style>
