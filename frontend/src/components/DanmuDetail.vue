<template>
  <div class="danmu-detail">
    <div class="detail-header">
      <el-button text @click="emit('back')">
        &larr; 返回列表
      </el-button>
    </div>

    <div v-if="loading" class="loading-state">
      <el-skeleton :rows="8" animated />
    </div>

    <div v-else-if="!analysis" class="empty-state">
      <el-empty description="分析中，请稍后刷新..." />
      <el-button type="primary" @click="fetchData" class="refresh-btn">刷新</el-button>
    </div>

    <template v-else>
      <!-- Stat Cards -->
      <div class="stats-row">
        <StatCard label="弹幕总数" :value="metrics.total_count" icon="+" />
        <StatCard label="正面占比" :value="formatPercent(metrics.sentiment_distribution?.positive)" icon="" />
        <StatCard label="负面占比" :value="formatPercent(metrics.sentiment_distribution?.negative)" icon="" />
        <StatCard label="分析状态" :value="statusLabel" icon="" />
      </div>

      <!-- Emotion Curve -->
      <BasePanel title="情感曲线" subtitle="弹幕情感得分随时间变化">
        <EmotionCurve :data="analysis.emotion_curve" />
      </BasePanel>

      <!-- Two columns: word cloud + density -->
      <div class="two-col">
        <BasePanel title="关键词云" subtitle="高频弹幕关键词">
          <WordCloud :data="analysis.keywords" @word-click="handleWordClick" />
        </BasePanel>
        <BasePanel title="弹幕密度" subtitle="各时间段弹幕数量">
          <DanmuDensity :data="densityData" />
        </BasePanel>
      </div>

      <!-- Speech-Danmu Comparison (only when correlation data exists) -->
      <BasePanel
        v-if="analysis.correlation && analysis.correlation.length > 0"
        title="话术-弹幕对比"
        subtitle="主播话术与弹幕反应的关联分析"
      >
        <SpeechDanmuComparison
          :speech-data="speechData"
          :danmu-data="comparisonDanmuData"
        />
      </BasePanel>

      <!-- Top 10 Keywords -->
      <BasePanel title="Top 10 关键词" subtitle="出现频率最高的弹幕关键词">
        <div class="keyword-tags">
          <el-tag
            v-for="kw in topKeywords"
            :key="kw.word"
            :type="sentimentTagType(kw.sentiment)"
            class="keyword-tag"
            effect="plain"
          >
            {{ kw.word }}
            <span class="kw-count">{{ kw.count }}</span>
          </el-tag>
        </div>
      </BasePanel>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { getDanmuAnalysis, type DanmuAnalysisResult } from '../api';
import StatCard from './StatCard.vue';
import BasePanel from './BasePanel.vue';
import EmotionCurve from './charts/EmotionCurve.vue';
import WordCloud from './charts/WordCloud.vue';
import DanmuDensity from './charts/DanmuDensity.vue';
import SpeechDanmuComparison from './charts/SpeechDanmuComparison.vue';

const props = defineProps<{
  batchId: string;
}>();

const emit = defineEmits<{
  back: [];
}>();

const loading = ref(true);
const analysis = ref<DanmuAnalysisResult | null>(null);

const metrics = computed(() => analysis.value?.metrics || { total_count: 0, danmu_density: 0, sentiment_volatility: 0, sentiment_distribution: { positive: 0, negative: 0, neutral: 0 } });

const statusLabel = computed(() => {
  if (!analysis.value) return '';
  const map: Record<string, string> = {
    pending: '待分析',
    analyzing: '分析中',
    completed: '已完成',
    failed: '失败',
  };
  return map[analysis.value.status] || analysis.value.status;
});

const densityData = computed(() => {
  if (!analysis.value?.highlights) return [];
  return analysis.value.highlights.map((h) => ({ time: h.time, count: h.count, avgScore: h.avg_score }));
});

const topKeywords = computed(() => {
  if (!analysis.value?.keywords) return [];
  return [...analysis.value.keywords]
    .sort((a, b) => b.count - a.count)
    .slice(0, 10);
});

const speechData = computed(() => {
  if (!analysis.value?.correlation) return [];
  return analysis.value.correlation.map((c) => ({
    time: c.time,
    text: c.text,
  }));
});

const comparisonDanmuData = computed(() => {
  if (!analysis.value?.correlation) return [];
  return analysis.value.correlation.map((c) => ({
    time: c.time,
    count: c.danmu_count,
    score: c.danmu_score,
  }));
});

function formatPercent(value?: number) {
  if (value == null) return '--';
  return `${(value * 100).toFixed(1)}%`;
}

function sentimentTagType(sentiment: string) {
  if (sentiment === 'positive') return 'success' as const;
  if (sentiment === 'negative') return 'danger' as const;
  return 'info' as const;
}

function handleWordClick(word: string) {
  ElMessage.info(`点击了关键词: ${word}`);
}

async function fetchData() {
  loading.value = true;
  try {
    analysis.value = await getDanmuAnalysis(props.batchId);
  } catch {
    analysis.value = null;
  } finally {
    loading.value = false;
  }
}

onMounted(fetchData);
</script>

<style scoped>
.danmu-detail {
  padding: var(--space-6) var(--space-6) var(--space-10);
  width: min(1100px, 100%);
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.detail-header {
  display: flex;
  align-items: center;
}

/* Stat cards with stagger animation */
.stats-row {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-3);
}

.stats-row > * {
  animation: fadeInUp 0.4s ease both;
}

.stats-row > *:nth-child(1) { animation-delay: 0ms; }
.stats-row > *:nth-child(2) { animation-delay: 80ms; }
.stats-row > *:nth-child(3) { animation-delay: 160ms; }
.stats-row > *:nth-child(4) { animation-delay: 240ms; }

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Chart containers — glass glow on hover */
.two-col {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: var(--space-4);
}

.two-col > :deep(.base-panel) {
  transition: box-shadow var(--transition-fast);
  border: 1px solid var(--app-glass-border);
  border-radius: var(--radius-lg);
}

.two-col > :deep(.base-panel:hover) {
  box-shadow: var(--app-glow);
}

/* Keyword gradient pill badges */
.keyword-tags {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-2);
}

.keyword-tag {
  display: inline-flex;
  align-items: center;
  gap: var(--space-2);
  border: none !important;
  background: var(--app-glass-bg) !important;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border-radius: var(--radius-full) !important;
  padding: 0 var(--space-3) !important;
  height: 28px !important;
  font-size: var(--text-xs) !important;
  transition: box-shadow var(--transition-fast), transform var(--transition-fast);
}

.keyword-tag:hover {
  box-shadow: var(--app-glow);
  transform: translateY(-1px);
}

/* Gradient pill variants for sentiment */
.keyword-tag:deep(.el-tag__content) {
  position: relative;
}

.kw-count {
  font-size: var(--text-xs);
  opacity: 0.7;
}

.loading-state {
  padding: var(--space-6) 0;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-10) 0;
}

.refresh-btn {
  margin-top: var(--space-2);
}

@media (max-width: 720px) {
  .stats-row {
    grid-template-columns: repeat(2, 1fr);
  }

  .two-col {
    grid-template-columns: 1fr;
  }
}
</style>
