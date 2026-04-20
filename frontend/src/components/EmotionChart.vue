<script setup lang="ts">
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'

interface EmotionDataPoint {
  time: string
  value: number
  label?: string
}

interface EmotionChartProps {
  data?: EmotionDataPoint[]
  title?: string
  height?: string
}

const props = withDefaults(defineProps<EmotionChartProps>(), {
  data: () => [],
  title: '情绪曲线',
  height: '300px'
})

const chartRef = ref<HTMLElement | null>(null)
let chartInstance: echarts.ECharts | null = null

// 模拟数据（用于演示）
const mockData: EmotionDataPoint[] = [
  { time: '00:00', value: 50 },
  { time: '05:00', value: 65 },
  { time: '10:00', value: 45 },
  { time: '15:00', value: 80 },
  { time: '20:00', value: 70 },
  { time: '25:00', value: 55 },
  { time: '30:00', value: 90 },
  { time: '35:00', value: 60 },
  { time: '40:00', value: 75 },
  { time: '45:00', value: 85 }
]

const chartData = props.data.length > 0 ? props.data : mockData

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
      trigger: 'axis',
      formatter: (params: any) => {
        const point = params[0]
        return `${point.name}<br/>情绪值：${point.value}`
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '60px',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: chartData.map(item => item.time),
      name: '时间',
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      name: '情绪值',
      min: 0,
      max: 100,
      axisLabel: {
        formatter: '{value}'
      }
    },
    series: [
      {
        name: '情绪',
        type: 'line',
        smooth: true,
        data: chartData.map(item => item.value),
        lineStyle: {
          color: '#409EFF',
          width: 3
        },
        itemStyle: {
          color: '#409EFF'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(64, 158, 255, 0.5)' },
            { offset: 1, color: 'rgba(64, 158, 255, 0.1)' }
          ])
        },
        markLine: {
          data: [
            { type: 'average', name: '平均值' }
          ],
          lineStyle: {
            color: '#E6A23C',
            type: 'dashed'
          }
        },
        markPoint: {
          data: [
            { type: 'max', name: '最高' },
            { type: 'min', name: '最低' }
          ]
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
</script>

<template>
  <div class="emotion-chart" :style="{ height: props.height }">
    <div ref="chartRef" class="chart-container"></div>
  </div>
</template>

<style scoped>
.emotion-chart {
  width: 100%;
  height: 100%;
}

.chart-container {
  width: 100%;
  height: 100%;
}
</style>
