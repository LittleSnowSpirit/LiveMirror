<template>
  <div class="analysis-page">
    <h1>趋势分析</h1>

    <div class="toolbar">
      <el-button @click="loadSessions">刷新场次</el-button>
      <el-button type="primary" :disabled="selectedSessionIds.length < 2" :loading="loading" @click="analyzeTrends">
        开始分析
      </el-button>
    </div>

    <p class="hint">选择至少 2 个场次后再分析。</p>

    <div class="session-list">
      <label
        v-for="session in sessions"
        :key="session.id"
        class="session-row"
        :class="{ selected: selectedSessionIds.includes(session.id) }"
      >
        <input
          type="checkbox"
          :checked="selectedSessionIds.includes(session.id)"
          @change="toggleSession(session.id)"
        />
        <span class="session-date">{{ session.date }}</span>
        <span class="session-anchor">{{ session.anchor_name || '主播' }}</span>
        <span class="session-score">{{ session.overall_score }} 分</span>
      </label>
    </div>

    <el-alert v-if="errorMessage" :title="errorMessage" type="error" :closable="false" show-icon />

    <el-skeleton v-if="loading && !trendReport" :rows="6" animated />

    <template v-else>
      <div v-if="trendReport" class="result-section">
        <h2>成长报告</h2>
        <p class="summary-text">{{ trendReport.summary || '暂无总结' }}</p>
        <div class="summary-grid">
          <div class="summary-item">
            <span class="summary-label">场次数量</span>
            <span class="summary-value">{{ trendReport.total_sessions ?? selectedSessionIds.length }}</span>
          </div>
          <div class="summary-item">
            <span class="summary-label">趋势判断</span>
            <span class="summary-value">{{ trendReport.overall_trend || '未提供' }}</span>
          </div>
        </div>
      </div>

      <div v-if="emotionLines.length" class="result-section">
        <h2>情绪趋势</h2>
        <pre class="result-block">{{ emotionLines.join('\n') }}</pre>
      </div>

      <div v-if="speechLines.length" class="result-section">
        <h2>话术质量趋势</h2>
        <pre class="result-block">{{ speechLines.join('\n') }}</pre>
      </div>

      <div v-if="engagementLines.length" class="result-section">
        <h2>互动趋势</h2>
        <pre class="result-block">{{ engagementLines.join('\n') }}</pre>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { getEmotionTrend, getEngagementTrend, getGrowthReport, getSpeechQualityTrend, getTrendSessions } from '../api';
import { ElMessage } from 'element-plus';
import type { TrendSession } from '../api';

const loading = ref(false);
const errorMessage = ref('');
const sessions = ref<TrendSession[]>([]);
const selectedSessionIds = ref<string[]>([]);
const trendReport = ref<any>(null);
const emotionTrend = ref<any>(null);
const speechTrend = ref<any>(null);
const engagementTrend = ref<any>(null);

const emotionLines = computed(() => summarizeTrendBlock('情绪', emotionTrend.value));
const speechLines = computed(() => summarizeTrendBlock('话术', speechTrend.value));
const engagementLines = computed(() => summarizeTrendBlock('互动', engagementTrend.value));

function summarizeTrendBlock(label: string, payload: any) {
  if (!payload) {
    return [];
  }

  const data = payload.data || payload;
  const lines: string[] = [];

  if (data?.avg_emotion?.trend) {
    lines.push(`${label}均值：${data.avg_emotion.trend}`);
  }

  if (data?.engagement_rate?.trend) {
    lines.push(`互动趋势：${data.engagement_rate.trend}`);
  }

  if (data?.by_type) {
    Object.entries(data.by_type).forEach(([type, value]: [string, any]) => {
      const last = Array.isArray(value?.values) ? value.values[value.values.length - 1] : undefined;
      lines.push(`${type}：${last ?? '无数据'}`);
    });
  }

  if (data?.summary) {
    lines.push(String(data.summary));
  }

  if (!lines.length) {
    lines.push(JSON.stringify(data, null, 2));
  }

  return lines;
}

function asRecord(value: unknown): Record<string, unknown> | null {
  return value && typeof value === 'object' && !Array.isArray(value) ? value as Record<string, unknown> : null;
}

function toggleSession(sessionId: string) {
  if (selectedSessionIds.value.includes(sessionId)) {
    selectedSessionIds.value = selectedSessionIds.value.filter((id) => id !== sessionId);
    return;
  }

  selectedSessionIds.value = [...selectedSessionIds.value, sessionId];
}

async function loadSessions() {
  loading.value = true;
  errorMessage.value = '';

  try {
    const response = await getTrendSessions(10);
    const list = response.sessions || (response.data?.sessions as TrendSession[] | undefined) || [];
    sessions.value = list;
    selectedSessionIds.value = list.slice(0, 3).map((item) => item.id);
  } catch (error: any) {
    errorMessage.value = error?.response?.data?.detail || '场次列表加载失败';
    sessions.value = [];
    selectedSessionIds.value = [];
  } finally {
    loading.value = false;
  }
}

async function analyzeTrends() {
  if (selectedSessionIds.value.length < 2) {
    ElMessage.warning('至少选择 2 个场次');
    return;
  }

  loading.value = true;
  errorMessage.value = '';

  try {
    const [emotionResponse, speechResponse, engagementResponse, reportResponse] = await Promise.all([
      getEmotionTrend(selectedSessionIds.value),
      getSpeechQualityTrend(selectedSessionIds.value),
      getEngagementTrend(selectedSessionIds.value),
      getGrowthReport(selectedSessionIds.value)
    ]);

    emotionTrend.value = emotionResponse;
    speechTrend.value = speechResponse;
    engagementTrend.value = engagementResponse;
    const reportData = asRecord(reportResponse.data);
    trendReport.value = reportResponse.report || reportData?.report || reportResponse.data || reportResponse;
    ElMessage.success('分析完成');
  } catch (error: any) {
    errorMessage.value = error?.response?.data?.detail || '趋势分析失败';
    trendReport.value = null;
    emotionTrend.value = null;
    speechTrend.value = null;
    engagementTrend.value = null;
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  loadSessions();
});
</script>

<style scoped>
.analysis-page {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  padding: var(--space-6) var(--space-6) var(--space-10);
  max-width: 800px;
  margin: 0 auto;
}

h1 {
  font-size: var(--text-3xl);
  font-weight: 700;
  color: var(--app-text);
}

h2 {
  font-size: var(--text-xl);
  font-weight: 600;
  color: var(--app-text);
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.hint {
  font-size: var(--text-sm);
  color: var(--app-text-soft);
}

.session-list {
  display: flex;
  flex-direction: column;
  gap: 1px;
  border: 1px solid var(--app-border);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.session-row {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  background: var(--app-surface);
  cursor: pointer;
  transition: background var(--transition-fast);
}

.session-row:hover {
  background: var(--app-surface-soft);
}

.session-row.selected {
  background: var(--app-surface-soft);
}

.session-row input[type="checkbox"] {
  accent-color: var(--app-primary);
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.session-date {
  font-size: var(--text-sm);
  color: var(--app-text-soft);
  min-width: 80px;
}

.session-anchor {
  font-weight: 500;
  color: var(--app-text);
  flex: 1;
}

.session-score {
  font-size: var(--text-sm);
  color: var(--app-text-soft);
}

.summary-text {
  color: var(--app-text-soft);
  line-height: 1.7;
}

.result-section {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  padding-top: var(--space-2);
  border-top: 1px solid var(--app-border);
}

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

.result-block {
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

@media (max-width: 720px) {
  .session-row {
    flex-wrap: wrap;
    gap: var(--space-2);
  }
}
</style>
