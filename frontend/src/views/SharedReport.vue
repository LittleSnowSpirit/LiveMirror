<template>
  <div class="shared-report-page">
    <div v-if="!verified" class="access-form">
      <div class="access-card">
        <h1>输入访问码</h1>
        <p class="access-hint">请输入 4 位提取码以查看分享的报告。</p>

        <el-input
          v-model="accessCode"
          placeholder="输入 4 位提取码"
          maxlength="4"
          class="access-input"
          @keyup.enter="handleVerify"
        />

        <el-alert v-if="errorMessage" :title="errorMessage" type="error" :closable="false" show-icon />

        <el-button type="primary" :loading="verifying" @click="handleVerify">
          查看报告
        </el-button>
      </div>
    </div>

    <div v-else-if="reportData" class="report-content">
      <div class="report-header">
        <h1>{{ reportData.filename || '分析报告' }}</h1>
        <span class="badge">由 LiveMirror 生成</span>
      </div>

      <div class="summary-grid">
        <div class="summary-item">
          <span class="summary-label">时长</span>
          <span class="summary-value">{{ formatDuration(reportData.duration) }}</span>
        </div>
        <div class="summary-item">
          <span class="summary-label">文件</span>
          <span class="summary-value">{{ reportData.filename }}</span>
        </div>
      </div>

      <div v-if="reportData.transcription" class="section">
        <h2>转写文本</h2>
        <pre class="transcript">{{ reportData.transcription }}</pre>
      </div>

      <div v-if="reportData.segments && reportData.segments.length" class="section">
        <h2>分段</h2>
        <el-table :data="segmentRows" border>
          <el-table-column prop="index" label="#" width="60" />
          <el-table-column prop="start_time" label="开始" width="100" />
          <el-table-column prop="end_time" label="结束" width="100" />
          <el-table-column prop="content" label="内容" min-width="260" />
        </el-table>
      </div>

      <div v-if="techniqueRows.length || attributionRows.length" class="section two-col">
        <div v-if="techniqueRows.length">
          <h2>话术分析</h2>
          <ul class="result-list">
            <li v-for="(item, i) in techniqueRows" :key="i">{{ item }}</li>
          </ul>
        </div>
        <div v-if="attributionRows.length">
          <h2>归因分析</h2>
          <ul class="result-list">
            <li v-for="(item, i) in attributionRows" :key="i">{{ item }}</li>
          </ul>
        </div>
      </div>

      <div v-if="suggestionRows.length" class="section">
        <h2>建议</h2>
        <ul class="result-list">
          <li v-for="(item, i) in suggestionRows" :key="i">{{ item }}</li>
        </ul>
      </div>

      <div v-if="reportSummaryText" class="section">
        <h2>摘要文案</h2>
        <p class="summary-text">{{ reportSummaryText }}</p>
      </div>
    </div>

    <div v-else-if="verifying" class="loading-state">
      <el-skeleton :rows="6" animated />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { useRoute } from 'vue-router';
import { getShareLink } from '../api';
import type { ReportData } from '../api';

const route = useRoute();
const token = computed(() => route.params.token as string);
const accessCode = ref('');
const verifying = ref(false);
const verified = ref(false);
const errorMessage = ref('');
const reportData = ref<ReportData | null>(null);

onMounted(() => {
  if (!token.value) {
    errorMessage.value = '无效的分享链接';
  }
});

async function handleVerify() {
  if (!accessCode.value.trim()) {
    errorMessage.value = '请输入提取码';
    return;
  }

  verifying.value = true;
  errorMessage.value = '';

  try {
    const data = await getShareLink(token.value, accessCode.value.trim());
    reportData.value = data.report;
    verified.value = true;
  } catch (err: unknown) {
    const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail;
    errorMessage.value = msg || '提取码错误或链接已失效';
  } finally {
    verifying.value = false;
  }
}

const segmentRows = computed(() => {
  const segments = reportData.value?.segments || [];
  return segments.map((segment, index) => ({
    index: index + 1,
    start_time: formatTime((segment as Record<string, unknown>).start_time ?? (segment as Record<string, unknown>).start ?? 0),
    end_time: formatTime((segment as Record<string, unknown>).end_time ?? (segment as Record<string, unknown>).end ?? 0),
    content: String((segment as Record<string, unknown>).content ?? (segment as Record<string, unknown>).text ?? ''),
  }));
});

const techniqueRows = computed(() => flattenItems(reportData.value?.speaking_techniques));
const attributionRows = computed(() => flattenItems(reportData.value?.attribution_analysis));
const suggestionRows = computed(() => flattenItems(reportData.value?.suggestions));

const reportSummaryText = computed(() => {
  if (!reportData.value) return '';
  if (reportData.value.summary_text) return reportData.value.summary_text;
  if (typeof reportData.value.summary === 'string') return reportData.value.summary;
  if (reportData.value.summary) return JSON.stringify(reportData.value.summary, null, 2);
  return '';
});

function flattenItems(items?: Array<Record<string, unknown>>) {
  return (items || []).map((item) => {
    const title = String(item.title ?? item.type ?? item.name ?? '项目');
    const description = String(item.description ?? item.content ?? item.summary ?? '');
    return description ? `${title}：${description}` : title;
  });
}

function formatDuration(seconds?: number | null) {
  if (!seconds || Number.isNaN(seconds)) return '--';
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

function formatTime(value: unknown) {
  if (typeof value !== 'number' || Number.isNaN(value)) return '--';
  return `${value.toFixed(2)}s`;
}
</script>

<style scoped>
.shared-report-page {
  padding: var(--space-6) var(--space-6) var(--space-10);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  min-height: 100vh;
}

/* Access form - centered card */
.access-form {
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1;
}

.access-card {
  max-width: 400px;
  width: 100%;
  padding: var(--space-8);
  border-radius: var(--radius-lg);
  background: var(--app-surface);
  border: 1px solid var(--app-border);
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  align-items: center;
  text-align: center;
}

.access-card h1 {
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--app-text);
  margin: 0;
}

.access-hint {
  color: var(--app-text-soft);
  font-size: var(--text-sm);
  line-height: 1.6;
  margin: 0;
}

.access-input {
  max-width: 200px;
}

/* Report header */
.report-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: var(--space-4);
}

h1 {
  font-size: var(--text-2xl);
  font-weight: 700;
  color: var(--app-text);
}

h2 {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--app-text);
}

.badge {
  font-size: var(--text-xs);
  color: var(--app-text-faint);
  padding: var(--space-1) var(--space-2);
  border: 1px solid var(--app-border);
  border-radius: var(--radius-sm);
  white-space: nowrap;
}

.report-content {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
  max-width: 960px;
  margin: 0 auto;
  width: 100%;
}

/* Summary grid */
.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: var(--space-3);
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
  padding: var(--space-3);
  border: 1px solid var(--app-border);
  border-radius: var(--radius-md);
}

.summary-label {
  font-size: var(--text-xs);
  color: var(--app-text-soft);
}

.summary-value {
  font-size: var(--text-lg);
  font-weight: 600;
  color: var(--app-text);
}

.section {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

/* Transcript - clean monospace block */
.transcript {
  padding: var(--space-4);
  border-radius: var(--radius-md);
  background: var(--app-bg-deep);
  color: var(--app-text);
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.7;
  border: 1px solid var(--app-border);
  font-family: var(--font-mono);
  font-size: var(--text-sm);
}

/* Two-column layout */
.two-col {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-6);
}

.two-col > div {
  flex: 1;
  min-width: 280px;
}

.result-list {
  padding-left: var(--space-4);
  color: var(--app-text-soft);
  line-height: 1.7;
}

.result-list :deep(li) {
  padding: var(--space-2) 0;
  border-bottom: 1px solid var(--app-border);
}

.result-list :deep(li:last-child) {
  border-bottom: none;
}

.summary-text {
  color: var(--app-text-soft);
  line-height: 1.7;
}

.loading-state {
  padding: var(--space-10) var(--space-6);
}

@media (max-width: 720px) {
  .report-header {
    flex-direction: column;
  }

  .access-card {
    margin: 0 var(--space-4);
  }
}
</style>
