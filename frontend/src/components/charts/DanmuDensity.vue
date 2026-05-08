<template>
  <div ref="chartRef" class="density-chart"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue';
import echarts from '../../utils/echarts';

interface DensityPoint {
  time: number;
  count: number;
  avgScore: number;
}

const props = defineProps<{
  data: DensityPoint[];
}>();

const chartRef = ref<HTMLElement>();
let chart: echarts.ECharts | null = null;

function formatTime(seconds: number) {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}

function scoreToColor(score: number) {
  if (score > 0.2) return '#10b981';
  if (score < -0.2) return '#ef4444';
  return '#6b7280';
}

function buildOption() {
  const times = props.data.map((d) => formatTime(d.time));
  const counts = props.data.map((d) => d.count);
  const avgCount = counts.reduce((a, b) => a + b, 0) / (counts.length || 1);

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
        const label = d.avgScore > 0.2 ? '正面' : d.avgScore < -0.2 ? '负面' : '中性';
        return `
          <div style="font-weight:600;margin-bottom:4px">${formatTime(d.time)}</div>
          <div>弹幕数: <b>${d.count}</b></div>
          <div>平均情感: <b>${d.avgScore.toFixed(2)}</b> (${label})</div>
        `;
      },
    },
    grid: { left: 50, right: 20, top: 20, bottom: 40 },
    xAxis: {
      type: 'category',
      data: times,
      axisLabel: { color: '#a0a0a0', fontSize: 11 },
      axisLine: { lineStyle: { color: '#2a2a2a' } },
      axisTick: { show: false },
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: '#a0a0a0', fontSize: 11 },
      axisLine: { show: false },
      splitLine: { lineStyle: { color: '#2a2a2a', type: 'dashed' } },
    },
    series: [
      {
        type: 'bar',
        data: props.data.map((d) => ({
          value: d.count,
          itemStyle: { color: scoreToColor(d.avgScore) },
        })),
        barWidth: '60%',
        markLine: {
          silent: true,
          symbol: 'none',
          lineStyle: { color: '#a78bfa', type: 'dashed', width: 1 },
          data: [{ yAxis: avgCount }],
          label: {
            show: true,
            position: 'insideEndTop',
            formatter: `平均 ${Math.round(avgCount)}`,
            color: '#a78bfa',
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
.density-chart {
  width: 100%;
  height: 320px;
  min-height: 240px;
}
</style>
