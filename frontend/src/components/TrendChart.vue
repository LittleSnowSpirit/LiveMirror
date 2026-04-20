<script setup lang="ts">
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'

interface TrendDataPoint {
  date: string
  viewers?: number
  engagement?: number
  duration?: number
  score?: number
}

interface TrendChartProps {
  data?: TrendDataPoint[]
  title?: string
  height?: string
  metrics?: string[]
}

const props = withDefaults(defineProps<TrendChartProps>(), {
  data: () => [],
  title: '历史趋势',
  height: '300px',
  metrics: () => ['viewers', 'engagement', 'score']
})

const chartRef = ref<HTMLElement | null>(null)
let chartInstance: echarts.ECharts | null = null

// 模拟数据（用于演示）
const mockData: TrendDataPoint[] = [
  { date: '04-01', viewers: 1200, engagement: 85, score: 88 },
  { date: '04-02', viewers: 1500, engagement: 88, score: 90 },
  { date: '04-03', viewers: 1100, engagement: 82, score: 85 },
  { date: '04-04', viewers: 1800, engagement: 92, score: 93 },
  { date: '04-05', viewers: 2000, engagement: 90, score: 91 },
  { date: '04-06', viewers: 1600, engagement: 87, score: 89 },
  { date: '04-07', viewers: 2200, engagement: 94, score: 95 }
]

const chartData = props.data.length > 0 ? props.data : mockData

const initChart = () => {
  if (!chartRef.value) return

  chartInstance = echarts.init(chartRef.value)

  const series = []
  const colors = ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399']
  const metricNames: Record<string, string> = {
    viewers: '观众人数',
    engagement: '互动率',
    duration: '直播时长',
    score: '综合评分'
  }

  if (props.metrics.includes('viewers')) {
    series.push({
      name: '观众人数',
      type: 'line',
      data: chartData.map(item => item.viewers || 0),
      yAxisIndex: 0,
      lineStyle: { color: colors[0], width: 2 },
      itemStyle: { color: colors[0] },
      smooth: true
    })
  }

  if (props.metrics.includes('engagement')) {
    series.push({
      name: '互动率',
      type: 'line',
      data: chartData.map(item => item.engagement || 0),
      yAxisIndex: 1,
      lineStyle: { color: colors[1], width: 2 },
      itemStyle: { color: colors[1] },
      smooth: true
    })
  }

  if (props.metrics.includes('score')) {
    series.push({
      name: '综合评分',
      type: 'line',
      data: chartData.map(item => item.score || 0),
      yAxisIndex: 1,
      lineStyle: { color: colors[2], width: 2 },
      itemStyle: { color: colors[2] },
      smooth: true
    })
  }

  const option = {
    title: {
      text: props.title,
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'cross'
      }
    },
    legend: {
      data: series.map((s: any) => s.name),
      top: '40px'
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '80px',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: chartData.map(item => item.date),
      name: '日期'
    },
    yAxis: [
      {
        type: 'value',
        name: '观众人数',
        position: 'left',
        axisLabel: {
          formatter: '{value}'
        }
      },
      {
        type: 'value',
        name: '百分比/评分',
        position: 'right',
        min: 0,
        max: 100,
        axisLabel: {
          formatter: '{value}'
        }
      }
    ],
    series: series
  }

  chartInstance.setOption(option)
}

const resizeChart = () => {
  chartInstance?.resize()
}

onMounted(() => {
  initChart()
  window.addEventListener('resize', resizeChart)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', resizeChart)
  chartInstance?.dispose()
})

watch(() => props.data, () => {
  initChart()
}, { deep: true })

watch(() => props.metrics, () => {
  initChart()
}, { deep: true })
</script>

<template>
  <div class="trend-chart" :style="{ height: props.height }">
    <div ref="chartRef" class="chart-container"></div>
  </div>
</template>

<style scoped>
.trend-chart {
  width: 100%;
  height: 100%;
}

.chart-container {
  width: 100%;
  height: 100%;
}
</style>
