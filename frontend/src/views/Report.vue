<template>
  <div ref="pageRef" class="report-page">
    <!-- Top bar: query + task info -->
    <el-card class="top-bar" data-animate="fade">
      <div class="top-bar-inner">
        <div class="query-row">
          <el-input v-model="taskIdInput" placeholder="输入任务 ID" />
          <el-button type="primary" :loading="loading" @click="loadReport">加载</el-button>
          <el-button @click="refresh">刷新</el-button>
        </div>
        <div v-if="taskInfo" class="task-meta">
          <span class="task-filename">{{ taskInfo.filename }}</span>
          <el-tag :type="statusTagType(taskInfo.status)" size="small" effect="light">
            {{ statusLabel(taskInfo.status) }}
          </el-tag>
          <el-button :disabled="!taskId" size="small" @click="exportAs('json')">JSON</el-button>
          <el-button :disabled="!taskId" size="small" type="primary" @click="exportAs('markdown')">Markdown</el-button>
        </div>
      </div>
      <el-alert v-if="errorMessage" :title="errorMessage" type="error" :closable="false" show-icon />
    </el-card>

    <el-skeleton v-if="loading && !taskInfo" :rows="6" animated />

    <template v-else>
      <div v-if="taskInfo" class="report-layout">
        <!-- Left column: main content -->
        <div class="report-main" data-stagger>
          <el-card v-if="reportData" class="section-card" data-animate>
            <h3 class="section-heading">转写文本</h3>
            <pre class="transcript">{{ reportData.transcription || '暂无转写文本' }}</pre>
          </el-card>

          <el-card v-if="reportData" class="section-card" data-animate>
            <h3 class="section-heading">分段详情</h3>
            <el-table v-if="segmentRows.length" :data="segmentRows" border>
              <el-table-column prop="index" label="#" width="60" />
              <el-table-column prop="start_time" label="开始" width="100" />
              <el-table-column prop="end_time" label="结束" width="100" />
              <el-table-column prop="content" label="内容" min-width="260" />
            </el-table>
            <el-empty v-else description="暂无分段数据" />
          </el-card>

          <el-card v-if="reportData" class="section-card" data-animate>
            <h3 class="section-heading">话术分析</h3>
            <ul class="analysis-list" v-if="techniqueRows.length" data-stagger>
              <li v-for="(item, index) in techniqueRows" :key="index" data-animate="fade">{{ item }}</li>
            </ul>
            <el-empty v-else description="暂无话术分析" />
          </el-card>

          <el-card v-if="reportData" class="section-card" data-animate>
            <h3 class="section-heading">归因分析</h3>
            <ul class="analysis-list" v-if="attributionRows.length" data-stagger>
              <li v-for="(item, index) in attributionRows" :key="index" data-animate="fade">{{ item }}</li>
            </ul>
            <el-empty v-else description="暂无归因分析" />
          </el-card>

          <el-card v-if="reportData" class="section-card" data-animate>
            <h3 class="section-heading">建议</h3>
            <ul class="analysis-list" v-if="suggestionRows.length" data-stagger>
              <li v-for="(item, index) in suggestionRows" :key="index" data-animate="fade">{{ item }}</li>
            </ul>
            <el-empty v-else description="暂无建议" />
          </el-card>

          <el-card v-if="reportData" class="section-card" data-animate>
            <h3 class="section-heading">摘要文案</h3>
            <p class="summary-text">{{ reportSummaryText }}</p>
          </el-card>

          <el-empty v-if="!reportData && !loading && taskId" description="报告尚未准备好" />
        </div>

        <!-- Right sidebar -->
        <aside class="report-sidebar">
          <el-card v-if="reportData" class="sidebar-card" data-animate style="transition-delay: 120ms">
            <h3 class="section-heading">摘要</h3>
            <dl class="summary-dl">
              <div class="summary-row">
                <dt>时长</dt>
                <dd>{{ formatDuration(reportData.duration) }}</dd>
              </div>
              <div class="summary-row">
                <dt>文件</dt>
                <dd>{{ reportData.filename }}</dd>
              </div>
              <div class="summary-row">
                <dt>任务</dt>
                <dd class="mono">{{ reportData.task_id }}</dd>
              </div>
              <div class="summary-row">
                <dt>进度</dt>
                <dd>{{ taskInfo.progress ?? 0 }}%</dd>
              </div>
            </dl>
            <el-progress v-if="taskInfo.status !== 'completed'" :percentage="taskInfo.progress ?? 0" :stroke-width="6" />
            <p v-if="taskInfo.error_message" class="error-text">{{ taskInfo.error_message }}</p>
          </el-card>

          <el-card class="sidebar-card" data-animate style="transition-delay: 180ms">
            <h3 class="section-heading">导出</h3>
            <ExportPanel v-if="taskId" :task-id="taskId" @share="showShareDialog = true" />
          </el-card>

          <el-card class="sidebar-card" data-animate style="transition-delay: 240ms">
            <h3 class="section-heading">分享</h3>
            <el-button @click="showShareDialog = true">生成分享链接</el-button>
          </el-card>
        </aside>
      </div>
    </template>

    <ShareDialog v-model:visible="showShareDialog" :task-id="taskId" />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, nextTick, watch } from 'vue';
import { useRoute } from 'vue-router';
import { exportReport, getReport, getStoredTaskId, getTaskStatus, setStoredTaskId } from '../api';
import { ElMessage } from 'element-plus';
import type { ReportData, TaskInfo } from '../api';
import { useReveal } from '../composables/useReveal';
import ExportPanel from '../components/ExportPanel.vue';
import ShareDialog from '../components/ShareDialog.vue';

const showShareDialog = ref(false);
const pageRef = ref<HTMLElement | null>(null);
const { observe } = useReveal();

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

watch(reportData, async () => {
  await nextTick();
  pageRef.value?.querySelectorAll('[data-animate]:not(.is-visible)').forEach(el => observe(el as HTMLElement));
});

onMounted(() => {
  pageRef.value?.querySelectorAll('[data-animate]').forEach(el => observe(el as HTMLElement));
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
  max-width: 1200px;
  margin: 0 auto;
}

.top-bar :deep(.el-card__body) {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.top-bar-inner {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-3);
}

.query-row {
  display: flex;
  gap: var(--space-2);
  flex: 1;
  min-width: 280px;
}

.query-row > :first-child {
  flex: 1;
}

.task-meta {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.task-filename {
  font-size: var(--text-sm);
  font-weight: 600;
  color: var(--app-text);
}

/* Two-column layout */
.report-layout {
  display: flex;
  gap: var(--space-6);
  align-items: flex-start;
}

.report-main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.report-sidebar {
  width: 280px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  position: sticky;
  top: var(--space-6);
}

.section-card :deep(.el-card__body),
.sidebar-card :deep(.el-card__body) {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.section-heading {
  font-size: 13px;
  font-weight: 600;
  color: var(--app-text);
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.transcript {
  padding: var(--space-4);
  border-radius: var(--radius-md);
  background: var(--app-bg-deep);
  color: var(--app-text);
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.7;
  font-family: var(--font-mono);
  font-size: var(--text-sm);
}

.analysis-list {
  padding-left: 18px;
  line-height: 1.7;
  color: var(--app-text-soft);
}

.summary-text {
  color: var(--app-text-soft);
  line-height: 1.7;
}

.summary-dl {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.summary-row {
  display: flex;
  justify-content: space-between;
  gap: var(--space-3);
  font-size: var(--text-sm);
}

.summary-row dt {
  color: var(--app-text-faint);
  flex-shrink: 0;
}

.summary-row dd {
  color: var(--app-text);
  text-align: right;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.summary-row .mono {
  font-family: var(--font-mono);
  font-size: var(--text-xs);
}

.error-text {
  color: var(--app-danger);
  font-size: var(--text-sm);
}

@media (max-width: 900px) {
  .report-layout {
    flex-direction: column;
  }

  .report-sidebar {
    width: 100%;
    position: static;
  }
}

@media (max-width: 640px) {
  .top-bar-inner {
    flex-direction: column;
    align-items: stretch;
  }

  .task-meta {
    justify-content: flex-start;
  }
}
</style>
