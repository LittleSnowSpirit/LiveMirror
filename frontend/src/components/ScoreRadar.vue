<script setup lang="ts">
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'

interface RadarIndicator {
  name: string
  max: number
}

interface ScoreRadarProps {
  data?: number[]
  indicators?: RadarIndicator[]
  title?: string
  height?: string
}

const props = withDefaults(defineProps<ScoreRadarProps>(), {
  data: () => [85, 90, 78, 88, 92],
  indicators: () => [
    { name: '内容质量', max: 100 },
    { name: '互动效果', max: 100 },
    { name: '节奏把控', max: 100 },
    { name: '话术技巧', max: 100 },
    { name: '观众留存', max: 100 }
  ],
  title: '五维评分',
  height: '300px'
})

const chartRef = ref<HTMLElement | null>(null)
let chartInstance: echarts.ECharts | null = null

// 模拟数据（用于演示）
const mockData = [85, 90, 78, 88, 92]
const mockIndicators = [
  { name: '内容质量', max: 100 },
  { name: '互动效果', max: 100 },
  { name: '节奏把控', max: 100 },
  { name: '话术技巧', max: 100 },
  { name: '观众留存', max: 100 }
]

const chartData = props.data.length > 0 ? props.data : mockData
const chartIndicators = props.indicators.length > 0 ? props.indicators : mockIndicators

const initChart = () => {
  if (!chartRef.value) return

  chartInstance = echarts.init(chartRef.value)

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
      trigger: 'item'
    },
    legend: {
      show: false
    },
    radar: {
      indicator: chartIndicators,
      shape: 'circle',
      splitNumber: 5,
      axisName: {
        color: '#666',
        fontSize: 12,
        fontWeight: 'bold'
      },
      splitLine: {
        lineStyle: {
          color: 'rgba(0, 0, 0, 0.1)'
        }
      },
      splitArea: {
        show: true,
        areaStyle: {
          color: ['rgba(255, 255, 255, 0.8)', 'rgba(240, 248, 255, 0.5)']
        }
      },
      axisLine: {
        lineStyle: {
          color: 'rgba(0, 0, 0, 0.1)'
        }
      }
    },
    series: [
      {
        name: '评分',
        type: 'radar',
        data: [
          {
            value: chartData,
            name: '当前评分',
            symbol: 'circle',
            symbolSize: 8,
            itemStyle: {
              color: '#409EFF'
            },
            lineStyle: {
              color: '#409EFF',
              width: 2
            },
            areaStyle: {
              color: 'rgba(64, 158, 255, 0.3)'
            }
          }
        ],
        emphasis: {
          lineStyle: {
            width: 4
          }
        }
      }
    ]
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

watch(() => props.indicators, () => {
  initChart()
}, { deep: true })
</script>

<template>
  <div class="score-radar" :style="{ height: props.height }">
    <div ref="chartRef" class="chart-container"></div>
  </div>
</template>

<style scoped>
.score-radar {
  width: 100%;
  height: 100%;
}

.chart-container {
  width: 100%;
  height: 100%;
}
</style>
