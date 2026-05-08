<template>
  <div ref="chartRef" class="comparison-chart"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue';
import echarts from '../../utils/echarts';

interface SpeechPoint {
  time: number;
  text: string;
}

interface DanmuPoint {
  time: number;
  count: number;
  score: number;
}

const props = defineProps<{
  speechData: SpeechPoint[];
  danmuData: DanmuPoint[];
}>();

const chartRef = ref<HTMLElement>();
let chart: echarts.ECharts | null = null;

function formatTime(seconds: number) {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
}

function buildOption() {
  const times = props.danmuData.map((d) => formatTime(d.time));
  const counts = props.danmuData.map((d) => d.count);
  const scores = props.danmuData.map((d) => d.score);
  const avgCount = counts.reduce((a, b) => a + b, 0) / (counts.length || 1);
  const threshold = avgCount * 2;

  // Build highlight areas where count > 2x average
  const highlightAreas: Array<{ xAxis: string }[]> = [];
  let inHighlight = false;
  let startIdx = 0;

  for (let i = 0; i < counts.length; i++) {
    if (counts[i] > threshold && !inHighlight) {
      inHighlight = true;
      startIdx = i;
    } else if ((counts[i] <= threshold || i === counts.length - 1) && inHighlight) {
      highlightAreas.push([{ xAxis: times[startIdx] }, { xAxis: times[i] }]);
      inHighlight = false;
    }
  }

  return {
    tooltip: {
      trigger: 'axis',
      backgroundColor: 'rgba(20, 20, 20, 0.9)',
      borderColor: '#2a2a2a',
      textStyle: { color: '#f0f0f0', fontSize: 12 },
      formatter(params: any) {
        const items = Array.isArray(params) ? params : [params];
        const idx = items[0]?.dataIndex;
        if (idx === undefined) return '';
        const d = props.danmuData[idx];
        if (!d) return '';

        // Find matching speech text
        const speech = props.speechData.find(
          (s) => Math.abs(s.time - d.time) < 15
        );

        let html = `<div style="font-weight:600;margin-bottom:4px">${formatTime(d.time)}</div>`;
        html += `<div>弹幕密度: <b>${d.count}</b></div>`;
        html += `<div>情感得分: <b>${d.score.toFixed(2)}</b></div>`;
        if (speech) {
          html += `<div style="margin-top:4px;color:#a78bfa;max-width:240px;word-break:break-all">话术: ${speech.text}</div>`;
        }
        return html;
      },
    },
    legend: {
      data: ['弹幕密度', '情感得分'],
      textStyle: { color: '#a0a0a0', fontSize: 11 },
      top: 0,
      right: 0,
    },
    grid: { left: 50, right: 50, top: 40, bottom: 40 },
    xAxis: {
      type: 'category',
      data: times,
      axisLabel: { color: '#a0a0a0', fontSize: 11 },
      axisLine: { lineStyle: { color: '#2a2a2a' } },
      axisTick: { show: false },
    },
    yAxis: [
      {
        type: 'value',
        name: '弹幕密度',
        nameTextStyle: { color: '#a0a0a0', fontSize: 10 },
        axisLabel: { color: '#a0a0a0', fontSize: 11 },
        axisLine: { show: false },
        splitLine: { lineStyle: { color: '#2a2a2a', type: 'dashed' } },
      },
      {
        type: 'value',
        name: '情感得分',
        min: -1,
        max: 1,
        nameTextStyle: { color: '#a0a0a0', fontSize: 10 },
        axisLabel: { color: '#a0a0a0', fontSize: 11 },
        axisLine: { show: false },
        splitLine: { show: false },
      },
    ],
    series: [
      {
        name: '弹幕密度',
        type: 'bar',
        yAxisIndex: 0,
        data: counts,
        barWidth: '50%',
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(167, 139, 250, 0.8)' },
            { offset: 1, color: 'rgba(167, 139, 250, 0.3)' },
          ]),
        },
        markArea: {
          silent: true,
          data: highlightAreas.map((area) => [
            {
              ...area[0],
              itemStyle: { color: 'rgba(251, 191, 36, 0.08)' },
            },
            area[1],
          ]),
        },
      },
      {
        name: '情感得分',
        type: 'line',
        yAxisIndex: 1,
        data: scores,
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: { width: 2, color: '#10b981' },
        itemStyle: { color: '#10b981' },
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
  () => [props.danmuData, props.speechData],
  () => {
    if (chart) {
      chart.setOption(buildOption());
    }
  },
  { deep: true }
);
</script>

<style scoped>
.comparison-chart {
  width: 100%;
  height: 360px;
  min-height: 280px;
}
</style>
