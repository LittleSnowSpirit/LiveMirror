<template>
  <div class="report-timeline">
    <div ref="chartContainer" class="timeline-chart"></div>
    
    <div class="legend">
      <div class="legend-item">
        <span class="legend-color highlight"></span>
        <span>爆点</span>
      </div>
      <div class="legend-item">
        <span class="legend-color issue"></span>
        <span>翻车</span>
      </div>
      <div class="legend-item">
        <span class="legend-color normal"></span>
        <span>普通</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'
import type { EmotionPoint, SpeechItem } from '@/api'

const props = defineProps<{
  data: EmotionPoint[]
  speeches: SpeechItem[]
}>()

const chartContainer = ref<HTMLDivElement | null>(null)
let chart: echarts.ECharts | null = null

function initChart() {
  if (!chartContainer.value) return
  
  chart = echarts.init(chartContainer.value)
  updateChart()
}

function updateChart() {
  if (!chart) return
  
  const emotionData = props.data.map(point => [point.timestamp, point.emotion])
  
  // 标记特殊事件
  const highlightMarks = props.speeches
    .filter(s => s.type === 'highlight')
    .map(s => ({
      xAxis: s.timestamp,
      label: {
        formatter: '🌟',
        fontSize: 16,
      },
    }))
  
  const issueMarks = props.speeches
    .filter(s => s.type === 'issue')
    .map(s => ({
      xAxis: s.timestamp,
      label: {
        formatter: '⚠️',
        fontSize: 16,
      },
    }))
  
  const option: echarts.EChartsOption = {
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        const point = params[0]
        const time = formatTime(point.value[0])
        const emotion = point.value[1]
        const emotionText = emotion > 0.3 ? '积极' : emotion < -0.3 ? '消极' : '平稳'
        return `${time}<br/>情绪：${emotionText} (${(emotion * 100).toFixed(0)}%)`
      },
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '10%',
      containLabel: true,
    },
    xAxis: {
      type: 'value',
      name: '时间',
      axisLabel: {
        formatter: (value: number) => formatTime(value),
      },
      splitLine: {
        show: true,
        lineStyle: {
          type: 'dashed',
        },
      },
    },
    yAxis: {
      type: 'value',
      name: '情绪',
      min: -1,
      max: 1,
      axisLabel: {
        formatter: (value: number) => `${(value * 100).toFixed(0)}%`,
      },
      splitLine: {
        show: true,
        lineStyle: {
          type: 'dashed',
        },
      },
    },
    series: [
      {
        name: '情绪曲线',
        type: 'line',
        smooth: true,
        symbol: 'none',
        data: emotionData,
        lineStyle: {
          color: '#409eff',
          width: 3,
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(64, 158, 255, 0.5)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0.1)' },
          ]),
        },
        markPoint: {
          data: [...highlightMarks, ...issueMarks],
        },
      },
    ],
  }
  
  chart.setOption(option)
}

function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

function handleResize() {
  chart?.resize()
}

onMounted(() => {
  initChart()
  window.addEventListener('resize', handleResize)
})

watch(() => [props.data, props.speeches], () => {
  updateChart()
}, { deep: true })

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  chart?.dispose()
})
</script>

<style scoped>
.report-timeline {
  width: 100%;
}

.timeline-chart {
  width: 100%;
  height: 300px;
}

.legend {
  display: flex;
  justify-content: center;
  gap: 30px;
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #ebeef5;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #606266;
}

.legend-color {
  width: 20px;
  height: 20px;
  border-radius: 50%;
}

.legend-color.highlight {
  background: #e6a23c;
}

.legend-color.issue {
  background: #f56c6c;
}

.legend-color.normal {
  background: #909399;
}
</style>
