<script setup lang="ts">
import { ref, onMounted, watch, onBeforeUnmount, computed } from 'vue'
import * as echarts from 'echarts'

interface EmotionDataPoint {
  time: string
  value: number
}

interface CompareChartProps {
  emotionData?: Record<string, EmotionDataPoint[]>
  metricsData?: Record<string, any[]>
  radarData?: Record<string, number[]>
  height?: string
  chartType?: 'emotion' | 'metrics' | 'radar'
  colors?: string[]
}

const props = withDefaults(defineProps<CompareChartProps>(), {
  emotionData: () => ({}),
  metricsData: () => ({}),
  radarData: () => ({}),
  height: '400px',
  chartType: 'metrics',
  colors: () => ['#409EFF', '#67C23A', '#E6A23C', '#F56C6C', '#909399']
})

const chartRef = ref<HTMLElement | null>(null)
let chartInstance: echarts.ECharts | null = null

const radarIndicators = [
  { name: '内容质量', max: 100 },
  { name: '互动效果', max: 100 },
  { name: '节奏把控', max: 100 },
  { name: '话术技巧', max: 100 },
  { name: '观众留存', max: 100 }
]

const initChart = () => {
  if (!chartRef.value) return

  chartInstance = echarts.init(chartRef.value)

  let option: any = {}

  if (props.chartType === 'emotion') {
    option = createEmotionOption()
  } else if (props.chartType === 'radar') {
    option = createRadarOption()
  } else {
    option = createMetricsOption()
  }

  chartInstance.setOption(option)
}

const createEmotionOption = () => {
  const series: any[] = []
  const colors = props.colors

  Object.entries(props.emotionData).forEach(([roomName, data], index) => {
    series.push({
      name: roomName,
      type: 'line',
      smooth: true,
      data: data.map(item => item.value),
      lineStyle: {
        color: colors[index % colors.length],
        width: 2
      },
      itemStyle: {
        color: colors[index % colors.length]
      },
      symbol: 'circle',
      symbolSize: 6
    })
  })

  return {
    title: {
      text: '情绪曲线对比',
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
      data: Object.keys(props.emotionData),
      top: 30
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: 80,
      containLabel: true
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: props.emotionData[Object.keys(props.emotionData)[0]]?.map(item => item.time) || [],
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
    series
  }
}

const createMetricsOption = () => {
  const metrics = ['转化率', '互动率', '情绪值', '留存率']
  const series: any[] = []
  const colors = props.colors

  // 准备数据
  const dataset: any[] = []
  const roomNames = Object.keys(props.metricsData)

  roomNames.forEach((roomName, index) => {
    const roomData = props.metricsData[roomName]
    if (roomData) {
      dataset.push({
        name: roomName,
        value: [
          roomData.find((m: any) => m.value !== undefined)?.value || 0,
          roomData.find((m: any) => m.value !== undefined)?.value || 0,
          roomData.find((m: any) => m.value !== undefined)?.value || 0,
          roomData.find((m: any) => m.value !== undefined)?.value || 0
        ]
      })
    }
  })

  roomNames.forEach((roomName, index) => {
    series.push({
      name: roomName,
      type: 'bar',
      barWidth: '60%',
      data: dataset.find(d => d.name === roomName)?.value || [],
      itemStyle: {
        color: colors[index % colors.length]
      }
    })
  })

  return {
    title: {
      text: '核心指标对比',
      left: 'center',
      textStyle: {
        fontSize: 16,
        fontWeight: 'bold'
      }
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    legend: {
      data: roomNames,
      top: 30
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: 80,
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: metrics,
      name: '指标',
      axisLabel: {
        interval: 0,
        rotate: 30
      }
    },
    yAxis: {
      type: 'value',
      name: '数值',
      axisLabel: {
        formatter: '{value}'
      }
    },
    series
  }
}

const createRadarOption = () => {
  const series: any[] = []
  const colors = props.colors

  Object.entries(props.radarData).forEach(([roomName, data], index) => {
    series.push({
      value: data,
      name: roomName,
      symbol: 'circle',
      symbolSize: 8,
      itemStyle: {
        color: colors[index % colors.length]
      },
      lineStyle: {
        color: colors[index % colors.length],
        width: 2
      },
      areaStyle: {
        color: colors[index % colors.length],
        opacity: 0.3
      }
    })
  })

  return {
    title: {
      text: '五维评分对比',
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
      data: Object.keys(props.radarData),
      top: 30
    },
    radar: {
      indicator: radarIndicators,
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
        name: '评分对比',
        type: 'radar',
        data: series,
        emphasis: {
          lineStyle: {
            width: 4
          }
        }
      }
    ]
  }
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

watch(() => [props.emotionData, props.metricsData, props.radarData, props.chartType], () => {
  initChart()
}, { deep: true })
</script>

<template>
  <div class="compare-chart" :style="{ height: props.height }">
    <div ref="chartRef" class="chart-container"></div>
  </div>
</template>

<style scoped>
.compare-chart {
  width: 100%;
  height: 100%;
}

.chart-container {
  width: 100%;
  height: 100%;
}
</style>
