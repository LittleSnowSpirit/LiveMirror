<template>
  <div ref="chartRef" class="wordcloud-chart"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue';
import echarts from '../../utils/echarts';
import 'echarts-wordcloud';

interface KeywordItem {
  word: string;
  count: number;
  sentiment: string;
}

const props = defineProps<{
  data: KeywordItem[];
}>();

const emit = defineEmits<{
  'word-click': [word: string];
}>();

const chartRef = ref<HTMLElement>();
let chart: echarts.ECharts | null = null;

function sentimentColor(sentiment: string) {
  switch (sentiment) {
    case 'positive': return '#10b981';
    case 'negative': return '#ef4444';
    default: return '#60a5fa';
  }
}

function buildWordCloudOption() {
  return {
    tooltip: {
      backgroundColor: 'rgba(20, 20, 20, 0.9)',
      borderColor: '#2a2a2a',
      textStyle: { color: '#f0f0f0', fontSize: 12 },
      formatter(item: any) {
        return `<b>${item.name}</b><br/>出现次数: ${item.data?.count || item.value}<br/>情感: ${item.data?.sentimentLabel || ''}`;
      },
    },
    series: [
      {
        type: 'wordCloud',
        shape: 'circle',
        left: 'center',
        top: 'center',
        width: '90%',
        height: '90%',
        sizeRange: [14, 60],
        rotationRange: [-30, 30],
        rotationStep: 15,
        gridSize: 8,
        drawOutOfBound: false,
        layoutAnimation: true,
        textStyle: {
          fontFamily: 'DM Sans, sans-serif',
          fontWeight: 600,
        },
        emphasis: {
          textStyle: {
            textShadowBlur: 4,
            textShadowColor: 'rgba(0,0,0,0.3)',
          },
        },
        data: props.data.map((d) => ({
          name: d.word,
          value: d.count,
          count: d.count,
          sentiment: d.sentiment,
          sentimentLabel: d.sentiment === 'positive' ? '正面' : d.sentiment === 'negative' ? '负面' : '中性',
          textStyle: {
            color: sentimentColor(d.sentiment),
          },
        })),
      },
    ],
  };
}

function buildBarFallbackOption() {
  const top20 = [...props.data].sort((a, b) => b.count - a.count).slice(0, 20);

  return {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(20, 20, 20, 0.9)',
      borderColor: '#2a2a2a',
      textStyle: { color: '#f0f0f0', fontSize: 12 },
    },
    grid: { left: 100, right: 20, top: 10, bottom: 30 },
    xAxis: {
      type: 'value',
      axisLabel: { color: '#a0a0a0', fontSize: 11 },
      axisLine: { lineStyle: { color: '#2a2a2a' } },
      splitLine: { lineStyle: { color: '#2a2a2a', type: 'dashed' } },
    },
    yAxis: {
      type: 'category',
      data: top20.map((d) => d.word).reverse(),
      axisLabel: { color: '#a0a0a0', fontSize: 11 },
      axisLine: { lineStyle: { color: '#2a2a2a' } },
    },
    series: [
      {
        type: 'bar',
        data: top20
          .map((d) => ({
            value: d.count,
            itemStyle: { color: sentimentColor(d.sentiment) },
          }))
          .reverse(),
        barWidth: '60%',
      },
    ],
  };
}

let useWordCloud = true;

function initChart() {
  if (!chartRef.value) return;

  chart = echarts.init(chartRef.value);

  try {
    // Test if wordcloud type is available
    chart.setOption(buildWordCloudOption());
    useWordCloud = true;
  } catch {
    useWordCloud = false;
    chart.setOption(buildBarFallbackOption());
  }

  chart.on('click', (params: any) => {
    if (params.name) {
      emit('word-click', params.name);
    }
  });
}

function handleResize() {
  chart?.resize();
}

onMounted(() => {
  nextTick(() => {
    initChart();
    window.addEventListener('resize', handleResize);
  });
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize);
  chart?.dispose();
  chart = null;
});

watch(
  () => props.data,
  () => {
    if (chart) {
      chart.setOption(useWordCloud ? buildWordCloudOption() : buildBarFallbackOption());
    }
  },
  { deep: true }
);
</script>

<style scoped>
.wordcloud-chart {
  width: 100%;
  height: 320px;
  min-height: 240px;
}
</style>
