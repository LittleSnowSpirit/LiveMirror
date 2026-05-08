<template>
  <div ref="chartRef" class="emotion-chart"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue';
import echarts from '../../utils/echarts';

interface EmotionPoint {
  time: number;
  score: number;
  count: number;
  positive: number;
  negative: number;
  neutral: number;
}

const props = defineProps<{
  data: EmotionPoint[];
}>();

const chartRef = ref<HTMLElement>();
let chart: echarts.ECharts | null = null;

function formatTime(seconds: number) {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}

function buildOption() {
  const times = props.data.map((d) => formatTime(d.time));
  const scores = props.data.map((d) => d.score);

  // Find top 3 peaks and bottom 3 valleys
  const indexed = scores.map((s, i) => ({ score: s, idx: i }));
  const sorted = [...indexed].sort((a, b) => b.score - a.score);
  const peaks = sorted.slice(0, 3);
  const valleys = sorted.slice(-3).reverse();

  const markPointData: Array<Record<string, unknown>> = [
    ...peaks.map((p) => ({
      coord: [p.idx, p.score],
      value: p.score.toFixed(2),
      symbol: 'triangle',
      symbolSize: 14,
      symbolRotate: 0,
      itemStyle: { color: '#10b981' },
      label: { show: true, position: 'top', fontSize: 10, color: '#10b981' },
    })),
    ...valleys.map((v) => ({
      coord: [v.idx, v.score],
      value: v.score.toFixed(2),
      symbol: 'triangle',
      symbolSize: 14,
      symbolRotate: 180,
      itemStyle: { color: '#ef4444' },
      label: { show: true, position: 'bottom', fontSize: 10, color: '#ef4444' },
    })),
  ];

  return {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(20, 20, 20, 0.9)',
      borderColor: '#2a2a2a',
      textStyle: { color: '#f0f0f0', fontSize: 12 },
      formatter(params: any) {
        const p = Array.isArray(params) ? params[0] : params;
        const idx = p.dataIndex;
        const d = props.data[idx];
        if (!d) return '';
        return `
          <div style="font-weight:600;margin-bottom:4px">${formatTime(d.time)}</div>
          <div>情感得分: <b>${d.score.toFixed(2)}</b></div>
          <div>弹幕数: ${d.count}</div>
          <div style="color:#10b981">正面: ${d.positive}</div>
          <div style="color:#ef4444">负面: ${d.negative}</div>
          <div style="color:#a0a0a0">中性: ${d.neutral}</div>
        `;
      },
    },
    grid: {
      left: 50,
      right: 20,
      top: 20,
      bottom: 40,
    },
    xAxis: {
      type: 'category',
      data: times,
      axisLabel: { color: '#a0a0a0', fontSize: 11 },
      axisLine: { lineStyle: { color: '#2a2a2a' } },
      axisTick: { show: false },
    },
    yAxis: {
      type: 'value',
      min: -1,
      max: 1,
      splitNumber: 4,
      axisLabel: { color: '#a0a0a0', fontSize: 11 },
      axisLine: { show: false },
      splitLine: { lineStyle: { color: '#2a2a2a', type: 'dashed' } },
    },
    series: [
      {
        type: 'line',
        data: scores,
        smooth: true,
        symbol: 'none',
        lineStyle: { width: 2, color: '#a78bfa' },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(167, 139, 250, 0.25)' },
            { offset: 1, color: 'rgba(167, 139, 250, 0.02)' },
          ]),
        },
        markPoint: {
          data: markPointData,
        },
        markLine: {
          silent: true,
          symbol: 'none',
          lineStyle: { color: '#666', type: 'dashed', width: 1 },
          data: [{ yAxis: 0 }],
          label: {
            show: true,
            position: 'insideEndTop',
            formatter: '中线',
            color: '#666',
            fontSize: 10,
          },
        },
      },
    ],
  };
}

function initChart() {
  if (!chartRef.value) return;
  chart = echarts.init(chartRef.value);
  chart.setOption(buildOption());
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
      chart.setOption(buildOption());
    }
  },
  { deep: true }
);
</script>

<style scoped>
.emotion-chart {
  width: 100%;
  height: 320px;
  min-height: 240px;
}
</style>
