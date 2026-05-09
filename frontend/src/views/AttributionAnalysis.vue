<template>
  <div ref="pageRef" class="analysis-page">
    <h1 data-animate>归因分析</h1>

    <div class="input-section" data-stagger>
      <div class="form-field" data-animate>
        <label>任务 ID（可选）</label>
        <el-input v-model="taskIdInput" placeholder="可选：任务 ID" />
      </div>
      <div class="form-field" data-animate>
        <label>speech_segments JSON</label>
        <el-input v-model="speechSegmentsText" type="textarea" :rows="6" placeholder="speech_segments JSON" />
      </div>
      <div class="form-field" data-animate>
        <label>emotion_curve JSON</label>
        <el-input v-model="emotionCurveText" type="textarea" :rows="6" placeholder="emotion_curve JSON" />
      </div>
      <div class="form-field" data-animate>
        <label>danmu_list JSON</label>
        <el-input v-model="danmuListText" type="textarea" :rows="6" placeholder="danmu_list JSON" />
      </div>
      <div class="form-field form-field--narrow" data-animate>
        <label>Top N</label>
        <el-input-number v-model="topN" :min="1" :max="20" controls-position="right" />
      </div>

      <div class="actions">
        <el-button type="primary" :loading="loading" @click="runAnalysis">开始分析</el-button>
        <el-button @click="fillSample">填充示例</el-button>
        <el-button @click="loadFromReport">从最近报告填充</el-button>
      </div>

      <el-alert v-if="errorMessage" :title="errorMessage" type="error" :closable="false" show-icon />
    </div>

    <div v-if="result" class="result-section" data-animate>
      <h2>分析摘要</h2>
      <ul v-if="resultSummary.length" class="result-list" data-stagger>
        <li v-for="(item, index) in resultSummary" :key="index" data-animate>{{ item }}</li>
      </ul>
      <p v-else class="empty-result">分析完成，当前示例没有生成摘要列表。</p>
    </div>

    <div v-if="peakRows.length" class="result-section" data-animate>
      <h2>高峰与建议</h2>
      <ul class="result-list" data-stagger>
        <li v-for="(item, index) in peakRows" :key="index" data-animate>{{ item }}</li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, nextTick, watch } from 'vue';
import { analyzeAttribution, getReport, getStoredTaskId } from '../api';
import { ElMessage } from 'element-plus';
import { useReveal } from '@/composables/useReveal';

const { observe } = useReveal();

const pageRef = ref<HTMLElement | null>(null);
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

onMounted(() => {
  pageRef.value?.querySelectorAll('[data-animate]').forEach(el => observe(el as HTMLElement));
});

watch(result, () => {
  nextTick(() => {
    pageRef.value?.querySelectorAll('[data-animate]:not(.is-visible)').forEach(el => observe(el as HTMLElement));
  });
});
</script>

<style scoped>
.analysis-page {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
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

.input-section {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: var(--space-1);
}

.form-field label {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--app-text-soft);
}

.form-field--narrow {
  max-width: 160px;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
  margin-top: var(--space-2);
}

.result-section {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  padding-top: var(--space-2);
  border-top: 1px solid var(--app-border);
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

.empty-result {
  color: var(--app-text-soft);
  line-height: 1.7;
}

@media (max-width: 720px) {
  .form-field--narrow {
    max-width: 100%;
  }
}
</style>
