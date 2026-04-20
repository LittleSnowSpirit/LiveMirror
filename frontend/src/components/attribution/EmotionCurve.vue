<!--
情绪曲线可视化组件
功能：
- ECharts 绘制情绪变化趋势
- 峰值标记（不同颜色表示等级）
- 工具提示显示峰值详情
- 支持缩放和拖拽
-->

<template>
  <div class="emotion-curve-container">
    <div ref="chartRef" class="emotion-chart"></div>
    
    <!-- 峰值图例 -->
    <div class="peak-legend">
      <div class="legend-item">
        <span class="legend-dot very-high"></span>
        <span>极高 (≥0.9)</span>
      </div>
      <div class="legend-item">
        <span class="legend-dot high"></span>
        <span>高 (0.8-0.9)</span>
      </div>
      <div class="legend-item">
        <span class="legend-dot medium"></span>
        <span>中 (0.7-0.8)</span>
      </div>
    </div>
    
    <!-- 统计信息 -->
    <div class="stats-panel" v-if="showStats">
      <div class="stat-item">
        <span class="stat-label">平均情绪</span>
        <span class="stat-value">{{ avgEmotion }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">峰值数量</span>
        <span class="stat-value">{{ peakCount }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">最高峰值</span>
        <span class="stat-value highlight">{{ maxPeak }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue';
import * as echarts from 'echarts';
import type { EChartsOption } from 'echarts';

// ==================== Props & Emits ====================

interface EmotionPoint {
  timestamp: number;
  score: number;
  level?: string;
}

interface PeakData {
  timestamp: number;
  score: number;
  duration: number;
  level: 'very_high' | 'high' | 'medium' | 'low';
}

const props = defineProps<{
  emotionCurve: EmotionPoint[];
  peaks?: PeakData[];
  showStats?: boolean;
  height?: string;
}>();

const emit = defineEmits<{
  (e: 'peak-click', peak: PeakData): void;
}>();

// ==================== Refs ====================

const chartRef = ref<HTMLElement | null>(null);
let chart: echarts.ECharts | null = null;

// ==================== Computed ====================

const avgEmotion = computed(() => {
  if (!props.emotionCurve.length) return '0.00';
  const avg = props.emotionCurve.reduce((sum, p) => sum + p.score, 0) / props.emotionCurve.length;
  return avg.toFixed(2);
});

const peakCount = computed(() => props.peaks?.length || 0);

const maxPeak = computed(() => {
  if (!props.peaks?.length) return '0.00';
  const max = Math.max(...props.peaks.map(p => p.score));
  return max.toFixed(2);
});

// ==================== Methods ====================

const getPeakColor = (level: string): string => {
  const colorMap: Record<string, string> = {
    'very_high': '#ff4d4f',  // 红色
    'high': '#ff7a45',       // 橙色
    'medium': '#ffa940',     // 黄色
    'low': '#ffd666'         // 浅黄
  };
  return colorMap[level] || '#d9d9d9';
};

const initChart = () => {
  if (!chartRef.value) return;
  
  chart = echarts.init(chartRef.value);
  
  const option: EChartsOption = {
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        const point = params[0];
        let content = `<div style="font-weight:bold">时间：${point.value[0]}s</div>`;
        content += `<div>情绪分数：${point.value[1]}</div>`;
        
        // 查找是否有峰值
        const peak = props.peaks?.find(p => 
          Math.abs(p.timestamp - point.value[0]) < 5
        );
        
        if (peak) {
          content += `<div style="color:${getPeakColor(peak.level)};font-weight:bold">
            ⚡ 峰值：${peak.level}
          </div>`;
          content += `<div>持续时间：${peak.duration}s</div>`;
        }
        
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
      type: 'value',
      name: '时间 (秒)',
      nameLocation: 'middle',
      nameGap: 30,
      min: 0,
      axisLabel: {
        formatter: '{value}s'
      }
    },
    yAxis: {
      type: 'value',
      name: '情绪分数',
      min: 0,
      max: 1,
      axisLabel: {
        formatter: (value: number) => value.toFixed(1)
      },
      splitLine: {
        lineStyle: {
          type: 'dashed'
        }
      }
    },
    series: [
      {
        name: '情绪分数',
        type: 'line',
        data: props.emotionCurve.map(p => [p.timestamp, p.score]),
        smooth: true,
        symbol: 'circle',
        symbolSize: 6,
        lineStyle: {
          color: '#1890ff',
          width: 2
        },
        itemStyle: {
          color: '#1890ff'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(24,144,255,0.3)' },
            { offset: 1, color: 'rgba(24,144,255,0.05)' }
          ])
        }
      },
      {
        name: '情绪峰值',
        type: 'scatter',
        data: (props.peaks || []).map(p => [p.timestamp, p.score]),
        symbol: 'diamond',
        symbolSize: 12,
        itemStyle: {
          color: (params: any) => {
            const peak = props.peaks?.find(p => 
              Math.abs(p.timestamp - params.value[0]) < 1
            );
            return peak ? getPeakColor(peak.level) : '#ff4d4f';
          },
          shadowBlur: 10,
          shadowColor: 'rgba(0,0,0,0.3)'
        }
      }
    ]
  };
  
  chart.setOption(option);
  
  // 峰值点击事件
  chart.on('click', (params: any) => {
    if (params.seriesName === '情绪峰值') {
      const peak = props.peaks?.find(p => 
        Math.abs(p.timestamp - params.value[0]) < 1
      );
      if (peak) {
        emit('peak-click', peak);
      }
    }
  });
};

const resizeChart = () => {
  chart?.resize();
};

// ==================== Lifecycle ====================

onMounted(() => {
  initChart();
  window.addEventListener('resize', resizeChart);
});

watch(() => [props.emotionCurve, props.peaks], () => {
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
.emotion-curve-container {
  width: 100%;
  padding: 16px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.emotion-chart {
  width: 100%;
  height: v-bind('height || "400px"');
}

.peak-legend {
  display: flex;
  gap: 16px;
  margin-top: 12px;
  padding: 8px 0;
  border-top: 1px solid #f0f0f0;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  color: #666;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  display: inline-block;
}

.legend-dot.very-high {
  background: #ff4d4f;
}

.legend-dot.high {
  background: #ff7a45;
}

.legend-dot.medium {
  background: #ffa940;
}

.stats-panel {
  display: flex;
  gap: 24px;
  margin-top: 16px;
  padding: 12px;
  background: #f5f5f5;
  border-radius: 6px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-label {
  font-size: 12px;
  color: #666;
}

.stat-value {
  font-size: 18px;
  font-weight: bold;
  color: #333;
}

.stat-value.highlight {
  color: #ff4d4f;
}
</style>
