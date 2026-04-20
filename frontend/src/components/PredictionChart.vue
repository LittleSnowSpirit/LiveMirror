<template>
  <div class="prediction-chart" :style="{ height: height }">
    <div v-if="!data || !data.dates" class="chart-empty">
      <el-empty :description="emptyText" :image-size="80" />
    </div>
    <div v-else ref="chartRef" class="chart-container"></div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  data: {
    type: Object,
    default: null
  },
  type: {
    type: String,
    default: 'gmv',
    validator: (value) => ['gmv', 'viewers', 'conversion'].includes(value)
  },
  height: {
    type: String,
    default: '300px'
  },
  emptyText: {
    type: String,
    default: '暂无数据'
  }
})

const chartRef = ref(null)
let chartInstance = null

// 初始化图表
const initChart = () => {
  if (!chartRef.value || !props.data) return

  // 销毁旧实例
  if (chartInstance) {
    chartInstance.dispose()
  }

  // 创建新实例
  chartInstance = echarts.init(chartRef.value)

  // 获取图表配置
  const option = getChartOption()

  // 设置配置
  chartInstance.setOption(option)

  // 响应式调整
  window.addEventListener('resize', handleResize)
}

// 获取图表配置
const getChartOption = () => {
  const { dates, gmv, viewers, conversion_rates } = props.data
  
  let seriesData, seriesName, unit, color
  
  switch (props.type) {
    case 'gmv':
      seriesData = gmv
      seriesName = 'GMV'
      unit = '¥'
      color = '#67c23a'
      break
    case 'viewers':
      seriesData = viewers
      seriesName = '观看人数'
      unit = '人'
      color = '#409eff'
      break
    case 'conversion':
      seriesData = conversion_rates.map(v => (v * 100).toFixed(2))
      seriesName = '转化率'
      unit = '%'
      color = '#e6a23c'
      break
    default:
      seriesData = gmv
      seriesName = 'GMV'
      unit = '¥'
      color = '#67c23a'
  }

  // 计算趋势线
  const trendData = calculateTrend(seriesData)

  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: (params) => {
        const main = params[0]
        const trend = params[1]
        return `
          <div style="font-weight: 600; margin-bottom: 8px;">${main.axisValue}</div>
          <div style="margin-bottom: 4px;">
            ${main.marker} ${seriesName}: 
            <span style="color: ${color}; font-weight: 600;">
              ${unit === '¥' ? '¥' : ''}${formatValue(main.value)}${unit === '%' ? '%' : unit === '人' ? '人' : ''}
            </span>
          </div>
          <div>
            ${trend.marker} 趋势：${formatValue(trend.value)}${unit === '%' ? '%' : unit === '人' ? '人' : ''}
          </div>
        `
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates.map(date => {
        const d = new Date(date)
        return `${d.getMonth() + 1}/${d.getDate()}`
      }),
      axisLine: {
        lineStyle: {
          color: '#dcdfe6'
        }
      },
      axisLabel: {
        color: '#606266',
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      name: props.type === 'gmv' ? 'GMV (¥)' : 
            props.type === 'viewers' ? '观看人数' : '转化率 (%)',
      nameTextStyle: {
        color: '#909399',
        padding: [0, 0, 0, -40]
      },
      axisLine: {
        lineStyle: {
          color: '#dcdfe6'
        }
      },
      axisLabel: {
        color: '#606266',
        formatter: (value) => {
          if (props.type === 'gmv') {
            return value >= 10000 ? `${(value / 10000).toFixed(1)}万` : value
          } else if (props.type === 'viewers') {
            return value >= 1000 ? `${(value / 1000).toFixed(1)}k` : value
          }
          return value
        }
      },
      splitLine: {
        lineStyle: {
          color: '#f2f6fc',
          type: 'dashed'
        }
      }
    },
    series: [
      {
        name: seriesName,
        type: 'bar',
        data: seriesData,
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: color + 'dd' },
            { offset: 1, color: color + '88' }
          ]),
          borderRadius: [4, 4, 0, 0]
        },
        barWidth: '60%',
        showBackground: true,
        backgroundStyle: {
          color: '#f5f7fa',
          borderRadius: [4, 4, 0, 0]
        }
      },
      {
        name: '趋势线',
        type: 'line',
        data: trendData,
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        itemStyle: {
          color: '#f56c6c',
          borderWidth: 2,
          borderColor: '#fff'
        },
        lineStyle: {
          color: '#f56c6c',
          width: 3,
          type: 'dashed'
        }
      }
    ],
    dataZoom: [
      {
        type: 'slider',
        show: true,
        xAxisIndex: [0],
        start: 0,
        end: 100,
        bottom: 10,
        height: 20,
        borderColor: 'transparent',
        backgroundColor: '#f5f7fa',
        fillerColor: '#d9ecff',
        handleStyle: {
          color: '#409eff'
        }
      },
      {
        type: 'inside',
        xAxisIndex: [0],
        start: 0,
        end: 100
      }
    ]
  }
}

// 计算趋势线 (移动平均)
const calculateTrend = (data) => {
  if (!data || data.length < 3) return data
  
  const windowSize = 3
  const trendData = []
  
  for (let i = 0; i < data.length; i++) {
    if (i < windowSize - 1) {
      trendData.push(data[i])
    } else {
      const window = data.slice(i - windowSize + 1, i + 1)
      const avg = window.reduce((a, b) => a + b, 0) / windowSize
      trendData.push(Number(avg.toFixed(2)))
    }
  }
  
  return trendData
}

// 格式化数值
const formatValue = (value) => {
  if (typeof value !== 'number') return value
  
  if (props.type === 'gmv') {
    return value >= 10000 ? `${(value / 10000).toFixed(2)}万` : value.toLocaleString()
  } else if (props.type === 'viewers') {
    return value >= 1000 ? `${(value / 1000).toFixed(1)}k` : value.toLocaleString()
  }
  return value
}

// 处理窗口大小变化
const handleResize = () => {
  if (chartInstance) {
    chartInstance.resize()
  }
}

// 监听数据变化
watch(() => [props.data, props.type], () => {
  initChart()
}, { deep: true })

// 生命周期
onMounted(() => {
  initChart()
})

onBeforeUnmount(() => {
  if (chartInstance) {
    chartInstance.dispose()
    chartInstance = null
  }
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.prediction-chart {
  width: 100%;
  position: relative;
}

.chart-container {
  width: 100%;
  height: 100%;
}

.chart-empty {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100%;
  min-height: 200px;
}
</style>
