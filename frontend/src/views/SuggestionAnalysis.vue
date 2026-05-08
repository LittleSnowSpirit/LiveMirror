<template>
  <div class="analysis-page">
    <h1>话术建议</h1>

    <div class="input-section">
      <div class="form-field">
        <label>任务 ID（可选）</label>
        <el-input v-model="taskIdInput" placeholder="可选：任务 ID" />
      </div>
      <div class="form-field">
        <label>话术类型</label>
        <el-input v-model="speechType" placeholder="话术类型，例如 price_promotion" />
      </div>
      <div class="form-field">
        <label>话术内容</label>
        <el-input v-model="speechContent" type="textarea" :rows="6" placeholder="输入待分析话术" />
      </div>
      <div class="metrics-row">
        <div class="form-field form-field--narrow">
          <label>情绪影响</label>
          <el-input-number v-model="emotionImpact" :min="0" :max="1" :step="0.05" controls-position="right" />
        </div>
        <div class="form-field form-field--narrow">
          <label>互动率</label>
          <el-input-number v-model="engagementRate" :min="0" :step="1" controls-position="right" />
        </div>
        <div class="form-field form-field--narrow">
          <label>综合评分</label>
          <el-input-number v-model="overallScore" :min="0" :max="100" :step="1" controls-position="right" />
        </div>
      </div>

      <div class="actions">
        <el-button type="primary" :loading="loading" @click="runAnalysis">开始分析</el-button>
        <el-button @click="fillSample">填充示例</el-button>
        <el-button @click="loadFromReport">从最近报告填充</el-button>
      </div>

      <el-alert v-if="errorMessage" :title="errorMessage" type="error" :closable="false" show-icon />
    </div>

    <div v-if="reportSuggestions.length" class="result-section">
      <h2>最近报告中的建议</h2>
      <ul class="result-list">
        <li v-for="(item, index) in reportSuggestions" :key="index">{{ item }}</li>
      </ul>
    </div>

    <div v-if="result" class="result-section">
      <h2>分析输出</h2>

      <div v-if="issueRows.length" class="subsection">
        <h3>问题</h3>
        <ul class="result-list">
          <li v-for="(item, index) in issueRows" :key="index">{{ item }}</li>
        </ul>
      </div>

      <div v-if="rewriteRows.length" class="subsection">
        <h3>改写建议</h3>
        <ul class="result-list">
          <li v-for="(item, index) in rewriteRows" :key="index">{{ item }}</li>
        </ul>
      </div>

      <div v-if="exampleRows.length" class="subsection">
        <h3>优秀话术</h3>
        <ul class="result-list">
          <li v-for="(item, index) in exampleRows" :key="index">{{ item }}</li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import { analyzeSuggestion, getReport, getStoredTaskId } from '../api';
import { ElMessage } from 'element-plus';

const taskIdInput = ref('');
const speechType = ref('price_promotion');
const speechContent = ref('');
const emotionImpact = ref(0.45);
const engagementRate = ref(15);
const overallScore = ref(60);
const loading = ref(false);
const errorMessage = ref('');
const result = ref<Record<string, unknown> | null>(null);
const reportSuggestions = ref<string[]>([]);

const resultData = computed(() => asRecord(result.value?.data));
const issueRows = computed(() => flattenResultList(result.value?.issues || resultData.value?.issues));
const rewriteRows = computed(() => flattenResultList([result.value?.rewrite].filter(Boolean) as Array<Record<string, unknown>>));
const exampleRows = computed(() => flattenResultList(result.value?.excellent_examples || resultData.value?.excellent_examples));

function asRecord(value: unknown): Record<string, unknown> | null {
  return value && typeof value === 'object' && !Array.isArray(value) ? value as Record<string, unknown> : null;
}

function flattenResultList(value: unknown) {
  const items = Array.isArray(value) ? value : [];
  return items.map((item: any) => {
    if (typeof item === 'string') {
      return item;
    }

    const title = String(item.title ?? item.type ?? item.name ?? '项目');
    const description = String(item.description ?? item.content ?? item.after ?? item.before ?? '');
    return description ? `${title}：${description}` : title;
  });
}

async function loadFromReport() {
  const taskId = (taskIdInput.value || getStoredTaskId()).trim();
  if (!taskId) {
    ElMessage.warning('请输入任务 ID');
    return;
  }

  try {
    const response = await getReport(taskId);
    const suggestions = response.data.suggestions || [];
    reportSuggestions.value = suggestions.map((item: any) => String(item.description ?? item.content ?? item.title ?? '建议项'));
    speechContent.value = response.data.transcription || speechContent.value;
    taskIdInput.value = taskId;
  } catch {
    ElMessage.warning('报告还没有准备好，先手动分析也可以');
  }
}

function fillSample() {
  speechType.value = 'price_promotion';
  speechContent.value = '这款产品现在只要 99 元，今天下单还会加赠一份试用装。';
  emotionImpact.value = 0.72;
  engagementRate.value = 28;
  overallScore.value = 84;
}

async function runAnalysis() {
  if (!speechContent.value.trim()) {
    ElMessage.warning('请输入话术内容');
    return;
  }

  loading.value = true;
  errorMessage.value = '';

  try {
    const response = await analyzeSuggestion({
      speech: {
        id: `speech_${Date.now()}`,
        type: speechType.value.trim() || 'unknown',
        content: speechContent.value.trim(),
        start_time: 0,
        end_time: Math.max(1, speechContent.value.length / 4)
      },
      metrics: {
        emotion_impact: emotionImpact.value,
        engagement_rate: engagementRate.value,
        overall_score: overallScore.value
      }
    });

    result.value = response as unknown as Record<string, unknown>;
    ElMessage.success('分析完成');
  } catch (error: any) {
    errorMessage.value = error?.response?.data?.detail || '分析失败';
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

h3 {
  font-size: var(--text-base);
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

.metrics-row {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
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

.subsection {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

.subsection + .subsection {
  margin-top: var(--space-2);
  padding-top: var(--space-3);
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

@media (max-width: 720px) {
  .form-field--narrow {
    max-width: 100%;
  }
}
</style>
