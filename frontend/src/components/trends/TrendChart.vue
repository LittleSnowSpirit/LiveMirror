<!--
趋势折线图组件
功能：
- 多场次趋势可视化
- 支持多指标对比
- 趋势方向指示
- 显著变化标记
-->

<template>
  <div class="trend-chart-container">
    <div class="header">
      <h3 class="title">📈 {{ title }}</h3>
      <div class="legend" v-if="showLegend">
        <div 
          v-for="(series, index) in seriesData" 
          :key="index"
          class="legend-item"
        >
          <span class="legend-dot" :style="{ background: colors[index] }"></span>
          <span>{{ series.name }}</span>
        </div>
      </div>
    </div>
    
    <div ref="chartRef" class="chart"></div>
    
    <!-- 趋势摘要 -->
    <div class="trend-summary" v-if="trendAnalysis">
      <div class="trend-indicator" :class="trendAnalysis.direction">
        <span class="trend-icon">{{ getTrendIcon(trendAnalysis.direction) }}</span>
        <span class="trend-text">
          {{ trendAnalysis.description }}
        </span>
        <span class="trend-change" :class="trendAnalysis.direction">
          {{ formatChange(trendAnalysis.change_rate) }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import * as echarts from 'echarts';
import type { EChartsOption } from 'echarts';

// ==================== Types ====================

interface TrendPoint {
  name: string;
  value: number;
  session_id?: string;
}

interface TrendSeries {
  name: string;
  data: TrendPoint[];
}

interface TrendAnalysis {
  direction: 'up' | 'down' | 'stable';
  change_rate: number;
  description: string;
}

// ==================== Props ====================

const props = defineProps<{
  title?: string;
  seriesData?: TrendSeries[];
  trendAnalysis?: TrendAnalysis;
  showLegend?: boolean;
  height?: string;
}>();

// ==================== Refs ====================

const chartRef = ref<HTMLElement | null>(null);
let chart: echarts.ECharts | null = null;

// ==================== Colors ====================

const colors = ['#1890ff', '#52c41a', '#fa8c16', '#722ed1', '#eb2f96'];

// ==================== Methods ====================

const getTrendIcon = (direction: string): string => {
  const icons = {
    'up': '📈',
    'down': '📉',
    'stable': '➡️'
  };
  return icons[direction] || '📊';
};

const formatChange = (changeRate: number): string => {
  const percent = (changeRate * 100).toFixed(1);
  if (changeRate > 0) return `+${percent}%`;
  if (changeRate < 0) return `${percent}%`;
  return '0%';
};

const initChart = () => {
  if (!chartRef.value) return;
  
  chart = echarts.init(chartRef.value);
  
  const seriesData = props.seriesData || [];
  
  const option: EChartsOption = {
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        let content = `<div style="font-weight:bold">${params[0]?.name}</div>`;
        params.forEach((param: any) => {
          content += `<div style="color:${param.color}">
            ${param.seriesName}: ${param.value}
          </div>`;
        });
        return content;
      }
    },
    grid: {
      left: '5%',
      right: '5%',
      bottom: '10%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: seriesData[0]?.data.map(d => d.name) || [],
      axisLabel: {
        rotate: 45
      }
    },
    yAxis: {
      type: 'value',
      axisLabel: {
        formatter: (value: number) => {
          if (value >= 0 && value <= 1) {
            return value.toFixed(1);
          }
          return value.toFixed(0);
        }
      }
    },
    series: seriesData.map((series, index) => ({
      name: series.name,
      type: 'line',
      data: series.data.map(d => d.value),
      smooth: true,
      symbol: 'circle',
      symbolSize: 8,
      lineStyle: {
        color: colors[index % colors.length],
        width: 3
      },
      itemStyle: {
        color: colors[index % colors.length],
        borderWidth: 2,
        borderColor: '#fff'
      },
      areaStyle: {
        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
          {
            offset: 0,
            color: colors[index % colors.length] + '40'
          },
          {
            offset: 1,
            color: colors[index % colors.length] + '05'
          }
        ])
      }
    }))
  };
  
  chart.setOption(option);
};

const resizeChart = () => {
  chart?.resize();
};

// ==================== Lifecycle ====================

onMounted(() => {
  initChart();
  window.addEventListener('resize', resizeChart);
});

watch(() => props.seriesData, () => {
  chart?.dispose();
  initChart();
}, { deep: true });

// 组件卸载时清理
defineExpose({
  dispose: () => {
    chart?.dispose();
    window.removeEventListener('resize', resizeChart);
  }
});
</script>

<style scoped>
.trend-chart-container {
  width: 100%;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.legend {
  display: flex;
  gap: 16px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #666;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
}

.chart {
  width: 100%;
  height: v-bind('height || "300px"');
}

.trend-summary {
  margin-top: 16px;
  padding: 12px;
  background: #f5f5f5;
  border-radius: 6px;
}

.trend-indicator {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px;
  border-radius: 4px;
}

.trend-indicator.up {
  background: #f6ffed;
  border-left: 4px solid #52c41a;
}

.trend-indicator.down {
  background: #fff1f0;
  border-left: 4px solid #ff4d4f;
}

.trend-indicator.stable {
  background: #e6f7ff;
  border-left: 4px solid #1890ff;
}

.trend-icon {
  font-size: 20px;
}

.trend-text {
  flex: 1;
  font-size: 14px;
  color: #333;
}

.trend-change {
  font-weight: bold;
  font-size: 16px;
}

.trend-change.up {
  color: #52c41a;
}

.trend-change.down {
  color: #ff4d4f;
}

.trend-change.stable {
  color: #1890ff;
}
</style>
