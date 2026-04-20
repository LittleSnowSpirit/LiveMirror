<script setup lang="ts">
import { ref, onMounted, watch, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'

interface SpeechTypeData {
  name: string
  value: number
}

interface SpeechTypePieProps {
  data?: SpeechTypeData[]
  title?: string
  height?: string
}

const props = withDefaults(defineProps<SpeechTypePieProps>(), {
  data: () => [],
  title: '话术类型分布',
  height: '300px'
})

const chartRef = ref<HTMLElement | null>(null)
let chartInstance: echarts.ECharts | null = null

// 模拟数据（用于演示）
const mockData: SpeechTypeData[] = [
  { name: '产品介绍', value: 35 },
  { name: '互动问答', value: 25 },
  { name: '促销活动', value: 20 },
  { name: '用户感谢', value: 12 },
  { name: '其他', value: 8 }
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
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      right: '5%',
      top: 'middle'
    },
    series: [
      {
        name: '话术类型',
        type: 'pie',
        radius: ['40%', '70%'],
        avoidLabelOverlap: false,
        itemStyle: {
          borderRadius: 10,
          borderColor: '#fff',
          borderWidth: 2
        },
        label: {
          show: true,
          formatter: '{b}: {d}%'
        },
        emphasis: {
          label: {
            show: true,
            fontSize: 14,
            fontWeight: 'bold'
          },
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        },
        labelLine: {
          show: false
        },
        data: chartData
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
  <div class="speech-type-pie" :style="{ height: props.height }">
    <div ref="chartRef" class="chart-container"></div>
  </div>
</template>

<style scoped>
.speech-type-pie {
  width: 100%;
  height: 100%;
}

.chart-container {
  width: 100%;
  height: 100%;
}
</style>
