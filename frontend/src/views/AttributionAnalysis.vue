<template>
  <div class="analysis-page">
    <el-card class="panel">
      <div class="panel-header">
        <div>
          <p class="kicker">归因</p>
          <h1>话术与情绪归因分析</h1>
        </div>
        <el-button @click="fillSample">填充示例</el-button>
      </div>

      <div class="form-grid">
        <el-input v-model="taskIdInput" placeholder="可选：任务 ID" />
        <el-input v-model="speechSegmentsText" type="textarea" :rows="8" placeholder="speech_segments JSON" />
        <el-input v-model="emotionCurveText" type="textarea" :rows="8" placeholder="emotion_curve JSON" />
        <el-input v-model="danmuListText" type="textarea" :rows="8" placeholder="danmu_list JSON" />
        <el-input-number v-model="topN" :min="1" :max="20" controls-position="right" />
      </div>

      <div class="actions">
        <el-button type="primary" :loading="loading" @click="runAnalysis">开始分析</el-button>
        <el-button @click="loadFromReport">从最近报告填充</el-button>
      </div>

      <el-alert v-if="errorMessage" :title="errorMessage" type="error" :closable="false" show-icon />
    </el-card>

    <el-card v-if="result" class="panel">
      <p class="kicker">结果</p>
      <h2>分析摘要</h2>
      <ul v-if="resultSummary.length" class="list">
        <li v-for="(item, index) in resultSummary" :key="index">{{ item }}</li>
      </ul>
      <p v-else class="empty-result">分析完成，当前示例没有生成摘要列表。</p>
    </el-card>

    <el-card v-if="peakRows.length" class="panel">
      <p class="kicker">结果</p>
      <h2>高峰与建议</h2>
      <ul class="list">
        <li v-for="(item, index) in peakRows" :key="index">{{ item }}</li>
      </ul>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { analyzeAttribution, getReport, getStoredTaskId } from '../api';
import { ElMessage } from 'element-plus';

const taskIdInput = ref('');
const topN = ref(10);
const speechSegmentsText = ref('[]');
const emotionCurveText = ref('[]');
const danmuListText = ref('[]');
const loading = ref(false);
const errorMessage = ref('');
const result = ref<Record<string, unknown> | null>(null);

const resultData = computed(() => asRecord(result.value?.data));
const resultSummary = computed(() => flattenItems(result.value?.data || result.value?.results || result.value?.correlation || []));
const peakRows = computed(() => flattenItems(resultData.value?.top_speeches || resultData.value?.recommendations || result.value?.peaks || []));

function asRecord(value: unknown): Record<string, unknown> | null {
  return value && typeof value === 'object' && !Array.isArray(value) ? value as Record<string, unknown> : null;
}

function flattenItems(value: unknown) {
  const items = Array.isArray(value) ? value : [];
  return items.map((item: any) => {
    if (typeof item === 'string') {
      return item;
    }

    const title = String(item.title ?? item.speech_type ?? item.speech_id ?? item.name ?? '项目');
    const description = String(item.description ?? item.evidence ?? item.summary ?? item.content ?? '');
    return description ? `${title}：${description}` : title;
  });
}

function fillSample() {
  speechSegmentsText.value = JSON.stringify([
    { id: 's1', type: 'price_promotion', content: '这款产品现在只要 99 元。', start_time: 60, end_time: 70 },
    { id: 's2', type: 'limited_offer', content: '只剩最后 100 单。', start_time: 90, end_time: 100 }
  ], null, 2);

  emotionCurveText.value = JSON.stringify([
    { timestamp: 0, score: 0.35, level: 'low' },
    { timestamp: 30, score: 0.82, level: 'high' }
  ], null, 2);

  danmuListText.value = JSON.stringify([
    { timestamp: 60, content: '好便宜', sentiment: 'positive', is_key_danmu: true },
    { timestamp: 95, content: '还有吗', sentiment: 'neutral', is_key_danmu: false }
  ], null, 2);
}

async function loadFromReport() {
  const taskId = (taskIdInput.value || getStoredTaskId()).trim();
  if (!taskId) {
    ElMessage.warning('请输入任务 ID');
    return;
  }

  try {
    const response = await getReport(taskId);
    const segments = response.data.segments || [];
    speechSegmentsText.value = JSON.stringify(segments, null, 2);
    taskIdInput.value = taskId;
  } catch {
    ElMessage.warning('报告还没有准备好，先手动填充数据');
  }
}

async function runAnalysis() {
  loading.value = true;
  errorMessage.value = '';

  try {
    const speechSegments = JSON.parse(speechSegmentsText.value || '[]');
    const emotionCurve = JSON.parse(emotionCurveText.value || '[]');
    const danmuList = JSON.parse(danmuListText.value || '[]');

    const response = await analyzeAttribution({
      speech_segments: speechSegments,
      emotion_curve: emotionCurve,
      danmu_list: danmuList,
      top_n: topN.value
    });

    result.value = response as unknown as Record<string, unknown>;
    ElMessage.success('分析完成');
  } catch (error: any) {
    errorMessage.value = error?.message || error?.response?.data?.detail || '分析失败';
    result.value = null;
  } finally {
    loading.value = false;
  }
}
</script>

<style scoped>
.analysis-page {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  padding: var(--space-6) var(--space-6) var(--space-10);
}

/* Glass panel */
.panel {
  border-radius: var(--radius-lg);
  background: var(--app-glass-bg);
  backdrop-filter: blur(var(--app-glass-blur));
  -webkit-backdrop-filter: blur(var(--app-glass-blur));
  border: 1px solid var(--app-glass-border);
  box-shadow: var(--app-shadow-card);
  transition: box-shadow var(--transition-normal), border-color var(--transition-normal);
  animation: staggerFadeIn 0.4s ease-out forwards;
  opacity: 0;
}

.panel:nth-child(1) { animation-delay: 0ms; }
.panel:nth-child(2) { animation-delay: 80ms; }
.panel:nth-child(3) { animation-delay: 160ms; }

.panel:hover {
  box-shadow: var(--app-glow);
  border-color: rgba(167, 139, 250, 0.15);
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
  gap: var(--space-4);
  position: relative;
  padding-bottom: var(--space-3);
}

.panel-header::after {
  content: '';
  position: absolute;
  left: 0;
  bottom: 0;
  width: 100%;
  height: 1px;
  background: var(--app-gradient-primary-h);
  opacity: 0.3;
}

.kicker {
  font-size: var(--text-xs);
  font-weight: 800;
  text-transform: uppercase;
  background: var(--app-gradient-primary);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

/* Glass form grid */
.form-grid {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
  padding: var(--space-3);
  border-radius: var(--radius-lg);
  background: var(--app-bg-deep);
  border: 1px solid var(--app-glass-border);
  border-left: 3px solid;
  border-image: var(--app-gradient-primary) 1;
}

.form-grid :deep(.el-textarea__inner),
.form-grid :deep(.el-input__wrapper) {
  background: var(--app-surface-soft);
  border: 1px solid var(--app-glass-border);
  box-shadow: none;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.list {
  padding-left: var(--space-4);
  color: var(--app-text-soft);
  line-height: 1.7;
}

.list :deep(li) {
  padding: var(--space-2) 0;
  border-bottom: 1px solid rgba(167, 139, 250, 0.06);
  transition: background var(--transition-fast);
}

.list :deep(li:hover) {
  background: rgba(167, 139, 250, 0.04);
  border-radius: var(--radius-sm);
}

.list :deep(li:last-child) {
  border-bottom: none;
}

.empty-result {
  padding-left: 0;
  color: var(--app-text-soft);
  line-height: 1.7;
}

@keyframes staggerFadeIn {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 720px) {
  .panel-header {
    flex-direction: column;
  }
}
</style>
