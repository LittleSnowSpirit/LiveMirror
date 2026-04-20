<!--
弹幕热力时间轴组件
功能：
- 弹幕密度热力图
- 情感分布堆叠
- 时间轴缩放
- 关键弹幕标记
-->

<template>
  <div class="danmu-heatmap-container">
    <div class="header">
      <h3 class="title">💬 弹幕热力时间轴</h3>
      <div class="controls">
        <button 
          v-for="interval in intervals" 
          :key="interval.value"
          :class="['interval-btn', { active: selectedInterval === interval.value }]"
          @click="selectedInterval = interval.value"
        >
          {{ interval.label }}
        </button>
      </div>
    </div>
    
    <!-- 热力图 -->
    <div ref="chartRef" class="heatmap-chart"></div>
    
    <!-- 统计面板 -->
    <div class="stats-panel">
      <div class="stat-card">
        <div class="stat-icon">📊</div>
        <div class="stat-content">
          <div class="stat-label">总弹幕数</div>
          <div class="stat-value">{{ totalDanmus }}</div>
        </div>
      </div>
      
      <div class="stat-card positive">
        <div class="stat-icon">😊</div>
        <div class="stat-content">
          <div class="stat-label">积极弹幕</div>
          <div class="stat-value">{{ positiveCount }}</div>
          <div class="stat-sub">{{ positiveRatio }}%</div>
        </div>
      </div>
      
      <div class="stat-card negative">
        <div class="stat-icon">😔</div>
        <div class="stat-content">
          <div class="stat-label">消极弹幕</div>
          <div class="stat-value">{{ negativeCount }}</div>
          <div class="stat-sub">{{ negativeRatio }}%</div>
        </div>
      </div>
      
      <div class="stat-card key">
        <div class="stat-icon">⭐</div>
        <div class="stat-content">
          <div class="stat-label">关键弹幕</div>
          <div class="stat-value">{{ keyDanmuCount }}</div>
        </div>
      </div>
    </div>
    
    <!-- 关键弹幕列表 -->
    <div class="key-danmu-list" v-if="keyDanmus.length">
      <h4 class="list-title">🔥 关键弹幕</h4>
      <div class="danmu-items">
        <div 
          v-for="(danmu, index) in displayedKeyDanmus" 
          :key="index"
          class="danmu-item"
          :class="danmu.sentiment"
        >
          <span class="danmu-time">{{ formatTime(danmu.timestamp) }}</span>
          <span class="danmu-content">{{ danmu.content }}</span>
          <span class="danmu-sentiment" :class="danmu.sentiment">
            {{ getSentimentLabel(danmu.sentiment) }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import * as echarts from 'echarts';
import type { EChartsOption } from 'echarts';

// ==================== Types ====================

interface DanmuData {
  timestamp: number;
  content: string;
  sentiment: 'positive' | 'negative' | 'neutral';
  sentiment_score?: number;
  is_key_danmu?: boolean;
  key_type?: string;
}

// ==================== Props ====================

const props = defineProps<{
  danmuList?: DanmuData[];
  height?: string;
  maxKeyDanmus?: number;
}>();

// ==================== State ====================

const chartRef = ref<HTMLElement | null>(null);
const selectedInterval = ref<number>(30); // 默认 30 秒间隔
let chart: echarts.ECharts | null = null;

const intervals = [
  { label: '10 秒', value: 10 },
  { label: '30 秒', value: 30 },
  { label: '1 分钟', value: 60 },
  { label: '2 分钟', value: 120 }
];

// ==================== Computed ====================

const totalDanmus = computed(() => props.danmuList?.length || 0);

const positiveCount = computed(() => 
  props.danmuList?.filter(d => d.sentiment === 'positive').length || 0
);

const negativeCount = computed(() => 
  props.danmuList?.filter(d => d.sentiment === 'negative').length || 0
);

const positiveRatio = computed(() => 
  totalDanmus.value ? ((positiveCount.value / totalDanmus.value) * 100).toFixed(1) : '0'
);

const negativeRatio = computed(() => 
  totalDanmus.value ? ((negativeCount.value / totalDanmus.value) * 100).toFixed(1) : '0'
);

const keyDanmuCount = computed(() => 
  props.danmuList?.filter(d => d.is_key_danmu).length || 0
);

const keyDanmus = computed(() => 
  props.danmuList?.filter(d => d.is_key_danmu) || []
);

const displayedKeyDanmus = computed(() => 
  keyDanmus.value.slice(0, props.maxKeyDanmus || 10)
);

// ==================== Mock Data ====================

const mockDanmuList: DanmuData[] = [
  { timestamp: 5, content: '主播好！', sentiment: 'positive', sentiment_score: 0.5 },
  { timestamp: 10, content: '666', sentiment: 'positive', sentiment_score: 0.8, is_key_danmu: true, key_type: 'praise' },
  { timestamp: 15, content: '这个产品怎么样？', sentiment: 'neutral', sentiment_score: 0 },
  { timestamp: 20, content: '已买！好用！', sentiment: 'positive', sentiment_score: 0.9, is_key_danmu: true, key_type: 'climax' },
  { timestamp: 25, content: '太贵了', sentiment: 'negative', sentiment_score: -0.5 },
  { timestamp: 30, content: '抢到了！', sentiment: 'positive', sentiment_score: 0.95, is_key_danmu: true, key_type: 'climax' },
  { timestamp: 35, content: '质量如何？', sentiment: 'neutral', sentiment_score: 0 },
  { timestamp: 40, content: '值得购买', sentiment: 'positive', sentiment_score: 0.7 },
  { timestamp: 45, content: '假的吧', sentiment: 'negative', sentiment_score: -0.6, is_key_danmu: true, key_type: 'controversy' },
  { timestamp: 50, content: '超级好用', sentiment: 'positive', sentiment_score: 0.85 }
];

// ==================== Methods ====================

const getSentimentColor = (sentiment: string): string => {
  const colorMap: Record<string, string> = {
    'positive': '#52c41a',
    'negative': '#ff4d4f',
    'neutral': '#d9d9d9'
  };
  return colorMap[sentiment] || '#d9d9d9';
};

const getSentimentLabel = (sentiment: string): string => {
  const labelMap: Record<string, string> = {
    'positive': '积极',
    'negative': '消极',
    'neutral': '中性'
  };
  return labelMap[sentiment] || sentiment;
};

const formatTime = (seconds: number): string => {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
};

const aggregateByInterval = (danmus: DanmuData[], interval: number) => {
  if (!danmus.length) return [];
  
  const maxTime = Math.max(...danmus.map(d => d.timestamp));
  const buckets = Math.ceil(maxTime / interval);
  
  const data = [];
  
  for (let i = 0; i < buckets; i++) {
    const startTime = i * interval;
    const endTime = (i + 1) * interval;
    
    const bucketDanmus = danmus.filter(d => startTime <= d.timestamp < endTime);
    
    const positive = bucketDanmus.filter(d => d.sentiment === 'positive').length;
    const negative = bucketDanmus.filter(d => d.sentiment === 'negative').length;
    const neutral = bucketDanmus.filter(d => d.sentiment === 'neutral').length;
    
    data.push({
      time: startTime,
      timeLabel: formatTime(startTime),
      total: bucketDanmus.length,
      positive,
      negative,
      neutral,
      value: bucketDanmus.length // 用于热力图颜色
    });
  }
  
  return data;
};

const initChart = () => {
  if (!chartRef.value) return;
  
  chart = echarts.init(chartRef.value);
  
  const danmus = props.danmuList || mockDanmuList;
  const aggregated = aggregateByInterval(danmus, selectedInterval.value);
  
  const option: EChartsOption = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      },
      formatter: (params: any) => {
        const item = params[0];
        const data = item.data;
        return `
          <div style="font-weight:bold">${data.timeLabel}</div>
          <div>总弹幕：${data.value}条</div>
          <div style="color:#52c41a">积极：${data.positive}条</div>
          <div style="color:#ff4d4f">消极：${data.negative}条</div>
          <div style="color:#999">中性：${data.neutral}条</div>
        `;
      }
    },
    grid: {
      left: '5%',
      right: '5%',
      bottom: '15%',
      top: '10%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: aggregated.map(d => d.timeLabel),
      axisLabel: {
        rotate: 45,
        interval: Math.floor(aggregated.length / 20) // 最多显示 20 个标签
      }
    },
    yAxis: {
      type: 'value',
      name: '弹幕数',
      axisLabel: {
        formatter: '{value}'
      }
    },
    series: [
      {
        name: '总弹幕数',
        type: 'bar',
        data: aggregated.map(d => ({
          value: d.value,
          time: d.time,
          timeLabel: d.timeLabel,
          positive: d.positive,
          negative: d.negative,
          neutral: d.neutral
        })),
        itemStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(24,144,255,0.8)' },
            { offset: 1, color: 'rgba(24,144,255,0.3)' }
          ]),
          borderRadius: [4, 4, 0, 0]
        },
        emphasis: {
          itemStyle: {
            color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
              { offset: 0, color: 'rgba(24,144,255,1)' },
              { offset: 1, color: 'rgba(24,144,255,0.5)' }
            ])
          }
        }
      },
      {
        name: '积极弹幕',
        type: 'bar',
        stack: 'sentiment',
        data: aggregated.map(d => d.positive),
        itemStyle: {
          color: '#52c41a'
        }
      },
      {
        name: '消极弹幕',
        type: 'bar',
        stack: 'sentiment',
        data: aggregated.map(d => d.negative),
        itemStyle: {
          color: '#ff4d4f'
        }
      },
      {
        name: '中性弹幕',
        type: 'bar',
        stack: 'sentiment',
        data: aggregated.map(d => d.neutral),
        itemStyle: {
          color: '#d9d9d9'
        }
      }
    ]
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

watch([() => props.danmuList, selectedInterval], () => {
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
.danmu-heatmap-container {
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
  margin-bottom: 20px;
  flex-wrap: wrap;
  gap: 12px;
}

.title {
  font-size: 18px;
  font-weight: bold;
  color: #333;
  margin: 0;
}

.controls {
  display: flex;
  gap: 8px;
}

.interval-btn {
  padding: 6px 12px;
  border: 1px solid #d9d9d9;
  background: #fff;
  border-radius: 4px;
  font-size: 13px;
  cursor: pointer;
  transition: all 0.3s;
}

.interval-btn:hover {
  border-color: #1890ff;
  color: #1890ff;
}

.interval-btn.active {
  background: #1890ff;
  color: #fff;
  border-color: #1890ff;
}

.heatmap-chart {
  width: 100%;
  height: v-bind('height || "350px"');
  margin-bottom: 20px;
}

.stats-panel {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
  margin-bottom: 24px;
}

.stat-card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 16px;
  background: #f5f5f5;
  border-radius: 8px;
  border-left: 4px solid #1890ff;
}

.stat-card.positive {
  border-left-color: #52c41a;
  background: #f6ffed;
}

.stat-card.negative {
  border-left-color: #ff4d4f;
  background: #fff1f0;
}

.stat-card.key {
  border-left-color: #fa8c16;
  background: #fff7e6;
}

.stat-icon {
  font-size: 32px;
}

.stat-content {
  flex: 1;
}

.stat-label {
  font-size: 12px;
  color: #666;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.stat-sub {
  font-size: 12px;
  color: #999;
  margin-top: 2px;
}

.key-danmu-list {
  padding-top: 16px;
  border-top: 1px solid #f0f0f0;
}

.list-title {
  font-size: 16px;
  font-weight: bold;
  color: #333;
  margin: 0 0 16px 0;
}

.danmu-items {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.danmu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  background: #fafafa;
  border-radius: 6px;
  border-left: 3px solid #d9d9d9;
}

.danmu-item.positive {
  border-left-color: #52c41a;
  background: #f6ffed;
}

.danmu-item.negative {
  border-left-color: #ff4d4f;
  background: #fff1f0;
}

.danmu-time {
  font-family: monospace;
  font-size: 13px;
  color: #999;
  min-width: 50px;
}

.danmu-content {
  flex: 1;
  font-size: 14px;
  color: #333;
  line-height: 1.5;
}

.danmu-sentiment {
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
}

.danmu-sentiment.positive {
  background: #52c41a;
  color: #fff;
}

.danmu-sentiment.negative {
  background: #ff4d4f;
  color: #fff;
}

.danmu-sentiment.neutral {
  background: #d9d9d9;
  color: #666;
}
</style>
