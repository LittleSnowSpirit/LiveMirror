<template>
  <div class="shared-report-page">
    <div v-if="!verified" class="access-form">
      <el-card class="panel access-card">
        <p class="kicker">分享报告</p>
        <h1>输入提取码</h1>
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
      </el-card>
    </div>

    <div v-else-if="reportData" class="report-content">
      <el-card class="panel">
        <div class="panel-header">
          <div>
            <p class="kicker">分享报告</p>
            <h1>{{ reportData.filename || '分析报告' }}</h1>
          </div>
          <span class="badge">由 LiveMirror 生成</span>
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
        </div>

        <div v-if="reportData.transcription" class="section">
          <h3>转写文本</h3>
          <pre class="transcript">{{ reportData.transcription }}</pre>
        </div>

        <div v-if="reportData.segments && reportData.segments.length" class="section">
          <h3>分段</h3>
          <el-table :data="segmentRows" border>
            <el-table-column prop="index" label="#" width="60" />
            <el-table-column prop="start_time" label="开始" width="100" />
            <el-table-column prop="end_time" label="结束" width="100" />
            <el-table-column prop="content" label="内容" min-width="260" />
          </el-table>
        </div>

        <div v-if="techniqueRows.length || attributionRows.length" class="section two-col">
          <div v-if="techniqueRows.length">
            <h3>话术分析</h3>
            <ul class="list">
              <li v-for="(item, i) in techniqueRows" :key="i">{{ item }}</li>
            </ul>
          </div>
          <div v-if="attributionRows.length">
            <h3>归因分析</h3>
            <ul class="list">
              <li v-for="(item, i) in attributionRows" :key="i">{{ item }}</li>
            </ul>
          </div>
        </div>

        <div v-if="suggestionRows.length" class="section">
          <h3>建议</h3>
          <ul class="list">
            <li v-for="(item, i) in suggestionRows" :key="i">{{ item }}</li>
          </ul>
        </div>

        <div v-if="reportSummaryText" class="section">
          <h3>摘要文案</h3>
          <p class="summary-text">{{ reportSummaryText }}</p>
        </div>
      </el-card>
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
  padding: 28px 24px 40px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  min-height: 100vh;
}

.panel {
  border-radius: 8px;
  background: var(--app-surface);
}

.panel :deep(.el-card__body) {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.access-card {
  max-width: 420px;
  margin: 60px auto;
  width: 100%;
}

.kicker {
  font-size: 12px;
  color: var(--app-primary-strong);
  font-weight: 800;
  text-transform: uppercase;
}

h1 {
  font-size: 28px;
  font-weight: 700;
  color: var(--app-text);
}

h3 {
  font-size: 16px;
  font-weight: 600;
  color: var(--app-text);
  margin-bottom: 8px;
}

.access-hint {
  color: var(--app-text-soft);
  font-size: 14px;
  line-height: 1.6;
}

.access-input {
  max-width: 200px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.badge {
  font-size: 11px;
  color: var(--app-text-faint);
  padding: 4px 8px;
  border: 1px solid var(--app-border);
  border-radius: 4px;
  white-space: nowrap;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 10px;
}

.summary-item {
  padding: 14px;
  border: 1px solid var(--app-border);
  border-radius: 8px;
  background: var(--app-bg-deep);
}

.summary-item .label {
  display: block;
  margin-bottom: 8px;
  color: var(--app-text-soft);
  font-size: 12px;
}

.section {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.transcript {
  padding: 16px;
  border: 1px solid var(--app-border);
  border-radius: 8px;
  background: var(--app-bg-deep);
  color: var(--app-text);
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.7;
}

.two-col {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.two-col > div {
  flex: 1;
  min-width: 280px;
}

.list {
  padding-left: 18px;
  color: var(--app-text-soft);
  line-height: 1.7;
}

.summary-text {
  color: var(--app-text-soft);
  line-height: 1.7;
}

.loading-state {
  padding: 60px 24px;
}

@media (max-width: 720px) {
  .panel-header {
    flex-direction: column;
  }

  .access-card {
    margin: 20px auto;
  }
}
</style>
