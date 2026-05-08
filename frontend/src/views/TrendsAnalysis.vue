<template>
  <div class="analysis-page">
    <el-card class="panel">
      <div class="panel-header">
        <div>
          <p class="kicker">趋势</p>
          <h1>跨场次趋势分析</h1>
        </div>
        <div class="header-actions">
          <el-button @click="loadSessions">刷新场次</el-button>
          <el-button type="primary" :disabled="selectedSessionIds.length < 2" :loading="loading" @click="analyzeTrends">
            开始分析
          </el-button>
        </div>
      </div>

      <div class="selection-box">
        <p class="copy">选择至少 2 个场次后再分析。</p>
        <div class="session-grid">
          <button
            v-for="session in sessions"
            :key="session.id"
            type="button"
            class="session-card"
            :class="{ selected: selectedSessionIds.includes(session.id) }"
            @click="toggleSession(session.id)"
          >
            <span class="session-date">{{ session.date }}</span>
            <strong>{{ session.anchor_name || '主播' }}</strong>
            <span class="session-score">{{ session.overall_score }} 分</span>
          </button>
        </div>
      </div>

      <el-alert v-if="errorMessage" :title="errorMessage" type="error" :closable="false" show-icon />
    </el-card>

    <el-skeleton v-if="loading && !trendReport" :rows="6" animated />

    <template v-else>
      <el-card v-if="trendReport" class="panel">
        <p class="kicker">结果</p>
        <h2>成长报告</h2>
        <p class="summary-text">{{ trendReport.summary || '暂无总结' }}</p>
        <div class="summary-grid">
          <div class="summary-item">
            <span class="label">场次数量</span>
            <strong>{{ trendReport.total_sessions ?? selectedSessionIds.length }}</strong>
          </div>
          <div class="summary-item">
            <span class="label">趋势判断</span>
            <strong>{{ trendReport.overall_trend || '未提供' }}</strong>
          </div>
        </div>
      </el-card>

      <el-card v-if="emotionLines.length" class="panel">
        <p class="kicker">结果</p>
        <h2>情绪趋势</h2>
        <pre class="result-block">{{ emotionLines.join('\n') }}</pre>
      </el-card>

      <el-card v-if="speechLines.length" class="panel">
        <p class="kicker">结果</p>
        <h2>话术质量趋势</h2>
        <pre class="result-block">{{ speechLines.join('\n') }}</pre>
      </el-card>

      <el-card v-if="engagementLines.length" class="panel">
        <p class="kicker">结果</p>
        <h2>互动趋势</h2>
        <pre class="result-block">{{ engagementLines.join('\n') }}</pre>
      </el-card>
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
  gap: 16px;
  padding: 28px 24px 40px;
}

.panel {
  border-radius: 8px;
  background: var(--app-surface);
}

.panel :deep(.el-card__body) {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
}

.kicker {
  font-size: 12px;
  color: var(--app-primary-strong);
  font-weight: 800;
  text-transform: uppercase;
}

.copy,
.summary-text {
  color: var(--app-text-soft);
  line-height: 1.7;
}

.header-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.selection-box {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 14px;
  border: 1px solid var(--app-border);
  border-radius: 8px;
  background: var(--app-bg-deep);
}

.session-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 10px;
}

.session-card {
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding: 14px;
  border: 1px solid var(--app-border);
  border-radius: 8px;
  background: var(--app-surface-soft);
  color: var(--app-text);
  text-align: left;
  cursor: pointer;
  transition: border-color 0.18s ease, background-color 0.18s ease, transform 0.18s ease;
}

.session-card.selected {
  border-color: var(--app-primary);
  background: var(--app-primary-soft);
}

.session-card:hover {
  border-color: var(--app-primary);
}

.session-date,
.session-score {
  color: var(--app-text-soft);
  font-size: 13px;
}

.summary-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}

.summary-item {
  padding: 14px;
  border: 1px solid var(--app-border);
  border-radius: 8px;
  background: var(--app-bg-deep);
}

.label {
  display: block;
  margin-bottom: 8px;
  color: var(--app-text-soft);
  font-size: 12px;
}

.result-block {
  padding: 16px;
  border: 1px solid var(--app-border);
  border-radius: 8px;
  background: var(--app-bg-deep);
  color: var(--app-text);
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.7;
}

@media (max-width: 720px) {
  .panel-header {
    flex-direction: column;
  }
}
</style>
