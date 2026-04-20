<template>
  <div class="roi-chart">
    <!-- ROI 趋势图 -->
    <div class="chart-card" v-if="chartType === 'trend'">
      <div class="chart-header">
        <h3>📈 ROI 趋势</h3>
        <div class="chart-legend">
          <span class="legend-item">
            <span class="dot roi"></span>
            ROI (%)
          </span>
          <span class="legend-item">
            <span class="dot cost"></span>
            成本
          </span>
          <span class="legend-item">
            <span class="dot revenue"></span>
            收益
          </span>
        </div>
      </div>
      <div class="chart-container">
        <canvas ref="trendChart"></canvas>
      </div>
      <div class="chart-stats">
        <div class="stat-item" v-if="stats.average_roi">
          <span class="stat-label">平均 ROI</span>
          <span class="stat-value highlight">{{ stats.average_roi.toFixed(2) }}%</span>
        </div>
        <div class="stat-item" v-if="stats.best_roi">
          <span class="stat-label">最高 ROI</span>
          <span class="stat-value positive">{{ stats.best_roi.toFixed(2) }}%</span>
        </div>
        <div class="stat-item" v-if="stats.worst_roi">
          <span class="stat-label">最低 ROI</span>
          <span class="stat-value negative">{{ stats.worst_roi.toFixed(2) }}%</span>
        </div>
        <div class="stat-item" v-if="stats.total_sessions">
          <span class="stat-label">总场次</span>
          <span class="stat-value">{{ stats.total_sessions }}</span>
        </div>
      </div>
    </div>

    <!-- 成本分解饼图 -->
    <div class="chart-card" v-if="chartType === 'cost-breakdown'">
      <div class="chart-header">
        <h3>💸 成本结构</h3>
      </div>
      <div class="chart-content">
        <div class="chart-container-small">
          <canvas ref="costPieChart"></canvas>
        </div>
        <div class="cost-legend">
          <div 
            class="legend-item" 
            v-for="(item, index) in costLegend" 
            :key="item.type"
          >
            <span class="color-dot" :style="{ backgroundColor: costColors[index] }"></span>
            <span class="legend-label">{{ item.name }}</span>
            <span class="legend-value">¥{{ formatNumber(item.amount) }}</span>
            <span class="legend-percent">{{ item.percent.toFixed(1) }}%</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 收益对比柱状图 -->
    <div class="chart-card" v-if="chartType === 'revenue-comparison'">
      <div class="chart-header">
        <h3>📊 收益对比</h3>
      </div>
      <div class="chart-container">
        <canvas ref="revenueBarChart"></canvas>
      </div>
    </div>

    <!-- ROI 分布散点图 -->
    <div class="chart-card" v-if="chartType === 'roi-distribution'">
      <div class="chart-header">
        <h3>🎯 ROI 分布</h3>
      </div>
      <div class="chart-container">
        <canvas ref="roiScatterChart"></canvas>
      </div>
      <div class="distribution-info">
        <div class="info-item">
          <span class="info-label">盈利场次</span>
          <span class="info-value positive">{{ profitableCount }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">亏损场次</span>
          <span class="info-value negative">{{ lossCount }}</span>
        </div>
        <div class="info-item">
          <span class="info-label">盈亏平衡</span>
          <span class="info-value">{{ breakevenCount }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, nextTick, computed } from 'vue'
import { Chart, registerables } from 'chart.js'

// 注册 Chart.js
Chart.register(...registerables)

interface Props {
  data: any[]
  chartType?: string
  costBreakdown?: any
}

const props = withDefaults(defineProps<Props>(), {
  chartType: 'trend'
})

// 图表引用
const trendChart = ref<HTMLCanvasElement | null>(null)
const costPieChart = ref<HTMLCanvasElement | null>(null)
const revenueBarChart = ref<HTMLCanvasElement | null>(null)
const roiScatterChart = ref<HTMLCanvasElement | null>(null)

// 图表实例
let trendChartInstance: Chart | null = null
let costPieChartInstance: Chart | null = null
let revenueBarChartInstance: Chart | null = null
let roiScatterChartInstance: Chart | null = null

// 成本颜色
const costColors = [
  '#3b82f6', // labor - 蓝色
  '#10b981', // venue - 绿色
  '#f59e0b', // promotion - 橙色
  '#8b5cf6', // equipment - 紫色
  '#6b7280'  // other - 灰色
]

// 成本图例
const costLegend = computed(() => {
  if (!props.costBreakdown) return []
  
  const total = Object.values(props.costBreakdown).reduce((sum: any, val: any) => sum + val, 0)
  
  return Object.entries(props.costBreakdown).map(([type, amount]: [string, any]) => ({
    type,
    name: getCostTypeName(type),
    amount,
    percent: total > 0 ? (amount / total) * 100 : 0
  }))
})

// 统计数据
const stats = computed(() => {
  if (!props.data || props.data.length === 0) return {}
  
  const roiValues = props.data.map(d => d.roi_percentage || 0)
  const average_roi = roiValues.reduce((sum, val) => sum + val, 0) / roiValues.length
  const best_roi = Math.max(...roiValues)
  const worst_roi = Math.min(...roiValues)
  const total_sessions = props.data.reduce((sum, d) => sum + (d.session_count || 1), 0)
  
  return {
    average_roi,
    best_roi,
    worst_roi,
    total_sessions
  }
})

// 分布统计
const profitableCount = computed(() => {
  if (props.chartType !== 'roi-distribution') return 0
  return props.data.filter(d => (d.roi || d.roi_percentage || 0) > 0).length
})

const lossCount = computed(() => {
  if (props.chartType !== 'roi-distribution') return 0
  return props.data.filter(d => (d.roi || d.roi_percentage || 0) < 0).length
})

const breakevenCount = computed(() => {
  if (props.chartType !== 'roi-distribution') return 0
  return props.data.filter(d => (d.roi || d.roi_percentage || 0) === 0).length
})

// 监听数据变化
watch(() => props.data, () => {
  renderChart()
}, { deep: true })

watch(() => props.chartType, () => {
  renderChart()
})

onMounted(() => {
  renderChart()
})

// 渲染图表
async function renderChart() {
  await nextTick()
  
  // 销毁旧图表
  destroyCharts()
  
  switch (props.chartType) {
    case 'trend':
      renderTrendChart()
      break
    case 'cost-breakdown':
      renderCostPieChart()
      break
    case 'revenue-comparison':
      renderRevenueBarChart()
      break
    case 'roi-distribution':
      renderRoiScatterChart()
      break
  }
}

// 销毁所有图表
function destroyCharts() {
  if (trendChartInstance) {
    trendChartInstance.destroy()
    trendChartInstance = null
  }
  if (costPieChartInstance) {
    costPieChartInstance.destroy()
    costPieChartInstance = null
  }
  if (revenueBarChartInstance) {
    revenueBarChartInstance.destroy()
    revenueBarChartInstance = null
  }
  if (roiScatterChartInstance) {
    roiScatterChartInstance.destroy()
    roiScatterChartInstance = null
  }
}

// 渲染 ROI 趋势图
function renderTrendChart() {
  const canvas = trendChart.value
  if (!canvas || props.data.length === 0) return
  
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  
  const labels = props.data.map(d => d.period)
  const roiData = props.data.map(d => d.roi_percentage || 0)
  const costData = props.data.map(d => d.total_cost || 0)
  const revenueData = props.data.map(d => d.total_revenue || 0)
  
  trendChartInstance = new Chart(ctx, {
    type: 'line',
    data: {
      labels,
      datasets: [
        {
          label: 'ROI (%)',
          data: roiData,
          borderColor: '#3b82f6',
          backgroundColor: 'rgba(59, 130, 246, 0.1)',
          fill: true,
          tension: 0.4,
          yAxisID: 'y'
        },
        {
          label: '成本',
          data: costData,
          borderColor: '#ef4444',
          backgroundColor: 'rgba(239, 68, 68, 0.1)',
          fill: true,
          tension: 0.4,
          yAxisID: 'y1'
        },
        {
          label: '收益',
          data: revenueData,
          borderColor: '#10b981',
          backgroundColor: 'rgba(16, 185, 129, 0.1)',
          fill: true,
          tension: 0.4,
          yAxisID: 'y1'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'index',
        intersect: false
      },
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          callbacks: {
            label: (context: any) => {
              if (context.dataset.label === 'ROI (%)') {
                return `ROI: ${context.parsed.y.toFixed(2)}%`
              }
              return `${context.dataset.label}: ¥${context.parsed.y.toLocaleString()}`
            }
          }
        }
      },
      scales: {
        x: {
          grid: {
            color: 'rgba(0, 0, 0, 0.1)'
          }
        },
        y: {
          type: 'linear',
          display: true,
          position: 'left',
          title: {
            display: true,
            text: 'ROI (%)'
          },
          grid: {
            color: 'rgba(0, 0, 0, 0.1)'
          }
        },
        y1: {
          type: 'linear',
          display: true,
          position: 'right',
          title: {
            display: true,
            text: '金额 (¥)'
          },
          grid: {
            drawOnChartArea: false
          }
        }
      }
    }
  })
}

// 渲染成本饼图
function renderCostPieChart() {
  const canvas = costPieChart.value
  if (!canvas || !props.costBreakdown) return
  
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  
  const labels = Object.keys(props.costBreakdown).map(type => getCostTypeName(type))
  const data = Object.values(props.costBreakdown)
  
  costPieChartInstance = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels,
      datasets: [{
        data,
        backgroundColor: costColors,
        borderWidth: 0
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          callbacks: {
            label: (context: any) => {
              const value = context.parsed
              const total = data.reduce((sum, val) => sum + val, 0)
              const percent = total > 0 ? (value / total) * 100 : 0
              return `¥${value.toLocaleString()} (${percent.toFixed(1)}%)`
            }
          }
        }
      }
    }
  })
}

// 渲染收益对比柱状图
function renderRevenueBarChart() {
  const canvas = revenueBarChart.value
  if (!canvas || props.data.length === 0) return
  
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  
  const labels = props.data.map(d => d.session_id || d.period)
  const costData = props.data.map(d => d.total_cost || d.cost || 0)
  const revenueData = props.data.map(d => d.total_revenue || d.revenue || 0)
  
  revenueBarChartInstance = new Chart(ctx, {
    type: 'bar',
    data: {
      labels,
      datasets: [
        {
          label: '成本',
          data: costData,
          backgroundColor: '#ef4444',
          borderRadius: 4
        },
        {
          label: '收益',
          data: revenueData,
          backgroundColor: '#10b981',
          borderRadius: 4
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top'
        },
        tooltip: {
          callbacks: {
            label: (context: any) => {
              return `${context.dataset.label}: ¥${context.parsed.y.toLocaleString()}`
            }
          }
        }
      },
      scales: {
        x: {
          grid: {
            display: false
          }
        },
        y: {
          title: {
            display: true,
            text: '金额 (¥)'
          },
          grid: {
            color: 'rgba(0, 0, 0, 0.1)'
          }
        }
      }
    }
  })
}

// 渲染 ROI 分布散点图
function renderRoiScatterChart() {
  const canvas = roiScatterChart.value
  if (!canvas || props.data.length === 0) return
  
  const ctx = canvas.getContext('2d')
  if (!ctx) return
  
  // 准备散点数据
  const profitableData = props.data
    .filter(d => (d.roi || d.roi_percentage || 0) > 0)
    .map((d, i) => ({
      x: i + 1,
      y: d.roi || d.roi_percentage || 0,
      r: 8
    }))
  
  const lossData = props.data
    .filter(d => (d.roi || d.roi_percentage || 0) < 0)
    .map((d, i) => ({
      x: i + 1,
      y: d.roi || d.roi_percentage || 0,
      r: 8
    }))
  
  roiScatterChartInstance = new Chart(ctx, {
    type: 'scatter',
    data: {
      datasets: [
        {
          label: '盈利',
          data: profitableData,
          backgroundColor: '#10b981',
          borderColor: '#059669'
        },
        {
          label: '亏损',
          data: lossData,
          backgroundColor: '#ef4444',
          borderColor: '#dc2626'
        }
      ]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          position: 'top'
        },
        tooltip: {
          callbacks: {
            label: (context: any) => {
              return `ROI: ${context.parsed.y.toFixed(2)}%`
            }
          }
        }
      },
      scales: {
        x: {
          title: {
            display: true,
            text: '场次'
          },
          grid: {
            color: 'rgba(0, 0, 0, 0.1)'
          }
        },
        y: {
          title: {
            display: true,
            text: 'ROI (%)'
          },
          grid: {
            color: 'rgba(0, 0, 0, 0.1)'
          }
        }
      }
    }
  })
}

// 工具函数
function formatNumber(num: number): string {
  return num.toLocaleString('zh-CN', { maximumFractionDigits: 2 })
}

function getCostTypeName(type: string): string {
  const names: any = {
    labor: '人力成本',
    venue: '场地成本',
    promotion: '推广成本',
    equipment: '设备成本',
    other: '其他成本'
  }
  return names[type] || type
}
</script>

<style scoped>
.roi-chart {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.chart-card {
  background: var(--card-bg);
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.chart-header h3 {
  margin: 0;
  font-size: 1.25rem;
}

.chart-legend {
  display: flex;
  gap: 1rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
}

.dot {
  width: 12px;
  height: 12px;
  border-radius: 50%;
}

.dot.roi {
  background: #3b82f6;
}

.dot.cost {
  background: #ef4444;
}

.dot.revenue {
  background: #10b981;
}

.chart-container {
  height: 300px;
  position: relative;
}

.chart-container-small {
  height: 200px;
  position: relative;
}

.chart-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.chart-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}

.stat-item {
  text-align: center;
}

.stat-label {
  display: block;
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
}

.stat-value {
  display: block;
  font-size: 1.25rem;
  font-weight: bold;
}

.stat-value.highlight {
  color: var(--primary-color);
}

.stat-value.positive {
  color: #10b981;
}

.stat-value.negative {
  color: #ef4444;
}

.cost-legend {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem;
  background: var(--bg-secondary);
  border-radius: 8px;
}

.color-dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  flex-shrink: 0;
}

.legend-label {
  flex: 1;
  font-size: 0.875rem;
}

.legend-value {
  font-weight: 600;
}

.legend-percent {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.distribution-info {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1rem;
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid var(--border-color);
}

.info-item {
  text-align: center;
}

.info-label {
  display: block;
  font-size: 0.875rem;
  color: var(--text-secondary);
  margin-bottom: 0.5rem;
}

.info-value {
  display: block;
  font-size: 1.5rem;
  font-weight: bold;
}

.info-value.positive {
  color: #10b981;
}

.info-value.negative {
  color: #ef4444;
}

/* 响应式 */
@media (max-width: 768px) {
  .chart-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .chart-content {
    grid-template-columns: 1fr;
  }
  
  .distribution-info {
    grid-template-columns: 1fr;
  }
}
</style>
