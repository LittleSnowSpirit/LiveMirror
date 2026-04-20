<template>
  <div class="ab-test-chart">
    <!-- 转化率对比柱状图 -->
    <div class="chart-section">
      <h3>📊 转化率对比</h3>
      <div ref="conversionChart" class="chart-container"></div>
    </div>

    <!-- 点击率对比 -->
    <div class="chart-section">
      <h3>📈 点击率对比</h3>
      <div ref="clickChart" class="chart-container"></div>
    </div>

    <!-- 互动率对比 -->
    <div class="chart-section">
      <h3>💬 互动率对比</h3>
      <div ref="interactionChart" class="chart-container"></div>
    </div>

    <!-- 综合指标雷达图 -->
    <div class="chart-section">
      <h3>🎯 综合指标雷达图</h3>
      <div ref="radarChart" class="chart-container"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, nextTick } from 'vue'
import * as echarts from 'echarts'

const props = defineProps({
  comparison: {
    type: Object,
    default: () => ({})
  }
})

const conversionChart = ref(null)
const clickChart = ref(null)
const interactionChart = ref(null)
const radarChart = ref(null)

let chartInstances = {}

// 准备数据
const prepareData = () => {
  const versions = Object.keys(props.comparison)
  const conversionRates = versions.map(v => 
    (props.comparison[v]?.rates?.conversion_rate || 0) * 100
  )
  const clickRates = versions.map(v => 
    (props.comparison[v]?.rates?.click_rate || 0) * 100
  )
  const interactionRates = versions.map(v => 
    (props.comparison[v]?.rates?.interaction_rate || 0) * 100
  )
  const avgWatchTimes = versions.map(v => 
    props.comparison[v]?.rates?.avg_watch_time || 0
  )

  return {
    versions,
    conversionRates,
    clickRates,
    interactionRates,
    avgWatchTimes
  }
}

// 初始化图表
const initCharts = () => {
  if (conversionChart.value) {
    chartInstances.conversion = echarts.init(conversionChart.value)
  }
  if (clickChart.value) {
    chartInstances.click = echarts.init(clickChart.value)
  }
  if (interactionChart.value) {
    chartInstances.interaction = echarts.init(interactionChart.value)
  }
  if (radarChart.value) {
    chartInstances.radar = echarts.init(radarChart.value)
  }
}

// 更新图表
const updateCharts = () => {
  const data = prepareData()
  
  if (Object.keys(props.comparison).length === 0) {
    return
  }

  // 转化率柱状图
  if (chartInstances.conversion) {
    chartInstances.conversion.setOption({
      tooltip: {
        trigger: 'axis',
        formatter: '{b}: {c}%'
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: data.versions,
        axisLabel: {
          fontSize: 14,
          fontWeight: 'bold'
        }
      },
      yAxis: {
        type: 'value',
        name: '转化率 (%)',
        axisLabel: {
          formatter: '{value}%'
        }
      },
      series: [{
        data: data.conversionRates,
        type: 'bar',
        barWidth: '50%',
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#83bff6' },
            { offset: 0.5, color: '#188df0' },
            { offset: 1, color: '#188df0' }
          ])
        },
        label: {
          show: true,
          position: 'top',
          formatter: '{c}%',
          fontSize: 12
        }
      }]
    })
  }

  // 点击率柱状图
  if (chartInstances.click) {
    chartInstances.click.setOption({
      tooltip: {
        trigger: 'axis',
        formatter: '{b}: {c}%'
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: data.versions,
        axisLabel: {
          fontSize: 14,
          fontWeight: 'bold'
        }
      },
      yAxis: {
        type: 'value',
        name: '点击率 (%)',
        axisLabel: {
          formatter: '{value}%'
        }
      },
      series: [{
        data: data.clickRates,
        type: 'bar',
        barWidth: '50%',
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#a8e6cf' },
            { offset: 0.5, color: '#56ab91' },
            { offset: 1, color: '#56ab91' }
          ])
        },
        label: {
          show: true,
          position: 'top',
          formatter: '{c}%',
          fontSize: 12
        }
      }]
    })
  }

  // 互动率柱状图
  if (chartInstances.interaction) {
    chartInstances.interaction.setOption({
      tooltip: {
        trigger: 'axis',
        formatter: '{b}: {c}%'
      },
      grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
      },
      xAxis: {
        type: 'category',
        data: data.versions,
        axisLabel: {
          fontSize: 14,
          fontWeight: 'bold'
        }
      },
      yAxis: {
        type: 'value',
        name: '互动率 (%)',
        axisLabel: {
          formatter: '{value}%'
        }
      },
      series: [{
        data: data.interactionRates,
        type: 'bar',
        barWidth: '50%',
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: '#ffd3b6' },
            { offset: 0.5, color: '#ffaaa5' },
            { offset: 1, color: '#ffaaa5' }
          ])
        },
        label: {
          show: true,
          position: 'top',
          formatter: '{c}%',
          fontSize: 12
        }
      }]
    })
  }

  // 雷达图
  if (chartInstances.radar) {
    const indicator = [
      { name: '转化率', max: Math.max(...data.conversionRates, 10) },
      { name: '点击率', max: Math.max(...data.clickRates, 20) },
      { name: '互动率', max: Math.max(...data.interactionRates, 30) },
      { name: '观看时长', max: Math.max(...data.avgWatchTimes, 200) }
    ]

    const seriesData = data.versions.map((version, index) => ({
      name: `版本 ${version}`,
      value: [
        data.conversionRates[index],
        data.clickRates[index],
        data.interactionRates[index],
        data.avgWatchTimes[index]
      ]
    }))

    const colors = ['#5470c6', '#91cc75', '#fac858', '#ee6666', '#73c0de']

    chartInstances.radar.setOption({
      tooltip: {
        trigger: 'item'
      },
      legend: {
        data: data.versions.map(v => `版本 ${v}`),
        bottom: 10
      },
      radar: {
        indicator: indicator,
        radius: '65%'
      },
      series: [{
        type: 'radar',
        data: seriesData,
        emphasis: {
          lineStyle: {
            width: 4
          }
        },
        lineStyle: {
          width: 2
        },
        areaStyle: {
          opacity: 0.3
        },
        itemStyle: {
          borderWidth: 2
        }
      }]
    })
  }
}

// 响应式调整
const resizeCharts = () => {
  Object.values(chartInstances).forEach(chart => {
    if (chart) {
      chart.resize()
    }
  })
}

// 监听数据变化
watch(() => props.comparison, () => {
  nextTick(() => {
    updateCharts()
  })
}, { deep: true })

// 生命周期
onMounted(() => {
  nextTick(() => {
    initCharts()
    updateCharts()
    
    // 监听窗口大小变化
    window.addEventListener('resize', resizeCharts)
  })
})

// 清理
import { onUnmounted } from 'vue'
onUnmounted(() => {
  window.removeEventListener('resize', resizeCharts)
  Object.values(chartInstances).forEach(chart => {
    if (chart) {
      chart.dispose()
    }
  })
})
</script>

<style scoped>
.ab-test-chart {
  padding: 20px;
}

.chart-section {
  margin-bottom: 30px;
}

.chart-section h3 {
  margin: 0 0 15px 0;
  color: #303133;
  font-size: 16px;
}

.chart-container {
  width: 100%;
  height: 300px;
  background: #fafafa;
  border-radius: 8px;
  padding: 10px;
  box-sizing: border-box;
}
</style>
