<!--
归因关系图组件
功能：
- 可视化话术→情绪→弹幕的关联关系
- 力导向图布局
- 节点点击高亮
- 关联强度展示
-->

<template>
  <div class="attribution-graph-container">
    <div class="header">
      <h3 class="title">🔗 归因关系图</h3>
      <div class="legend">
        <div class="legend-item">
          <span class="legend-dot speech"></span>
          <span>话术</span>
        </div>
        <div class="legend-item">
          <span class="legend-dot peak"></span>
          <span>情绪峰值</span>
        </div>
        <div class="legend-item">
          <span class="legend-dot danmu"></span>
          <span>弹幕簇</span>
        </div>
      </div>
    </div>
    
    <div ref="chartRef" class="graph-chart"></div>
    
    <!-- 节点详情面板 -->
    <div class="detail-panel" v-if="selectedNode">
      <div class="detail-header">
        <span class="detail-type" :class="selectedNode.category">
          {{ getNodeTypeName(selectedNode.category) }}
        </span>
        <button class="close-btn" @click="selectedNode = null">×</button>
      </div>
      <div class="detail-content">
        <p v-if="selectedNode.content">{{ selectedNode.content }}</p>
        <div class="detail-metrics" v-if="selectedNode.metrics">
          <div class="metric" v-for="(value, key) in selectedNode.metrics" :key="key">
            <span class="metric-label">{{ getMetricLabel(key) }}</span>
            <span class="metric-value">{{ formatMetricValue(key, value) }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import * as echarts from 'echarts';
import type { EChartsOption } from 'echarts';

// ==================== Types ====================

interface GraphNode {
  id: string;
  category: 'speech' | 'peak' | 'danmu';
  name: string;
  content?: string;
  value?: number;
  symbolSize?: number;
  metrics?: Record<string, any>;
}

interface GraphLink {
  source: string;
  target: string;
  value: number;
  strength?: number;
}

interface GraphData {
  nodes: GraphNode[];
  links: GraphLink[];
}

// ==================== Props ====================

const props = defineProps<{
  data?: GraphData;
  height?: string;
}>();

// ==================== Refs ====================

const chartRef = ref<HTMLElement | null>(null);
const selectedNode = ref<GraphNode | null>(null);
let chart: echarts.ECharts | null = null;

// ==================== Mock Data ====================

const mockData: GraphData = {
  nodes: [
    // 话术节点
    {
      id: 'speech_1',
      category: 'speech',
      name: '价格优惠话术',
      content: '今天直播间特价，只要 99 元！',
      value: 85,
      symbolSize: 40,
      metrics: { emotion_impact: 0.92, engagement_rate: 30 }
    },
    {
      id: 'speech_2',
      category: 'speech',
      name: '限时限量话术',
      content: '只剩最后 100 单了！',
      value: 78,
      symbolSize: 35,
      metrics: { emotion_impact: 0.85, engagement_rate: 25 }
    },
    {
      id: 'speech_3',
      category: 'speech',
      name: '产品介绍话术',
      content: '这款产品我亲自用了一个月',
      value: 65,
      symbolSize: 30,
      metrics: { emotion_impact: 0.68, engagement_rate: 15 }
    },
    // 情绪峰值节点
    {
      id: 'peak_1',
      category: 'peak',
      name: '情绪高峰 #1',
      content: '时间：30s, 分数：0.95',
      value: 0.95,
      symbolSize: 25,
      metrics: { score: 0.95, duration: 25 }
    },
    {
      id: 'peak_2',
      category: 'peak',
      name: '情绪高峰 #2',
      content: '时间：65s, 分数：0.88',
      value: 0.88,
      symbolSize: 22,
      metrics: { score: 0.88, duration: 18 }
    },
    // 弹幕簇节点
    {
      id: 'danmu_1',
      category: 'danmu',
      name: '弹幕簇 #1',
      content: '15 条弹幕，80% 积极',
      value: 15,
      symbolSize: 20,
      metrics: { count: 15, positive_ratio: 0.8 }
    },
    {
      id: 'danmu_2',
      category: 'danmu',
      name: '弹幕簇 #2',
      content: '22 条弹幕，75% 积极',
      value: 22,
      symbolSize: 24,
      metrics: { count: 22, positive_ratio: 0.75 }
    }
  ],
  links: [
    // 话术→情绪峰值关联
    { source: 'speech_1', target: 'peak_1', value: 0.9, strength: 0.9 },
    { source: 'speech_2', target: 'peak_2', value: 0.7, strength: 0.7 },
    { source: 'speech_3', target: 'peak_1', value: 0.4, strength: 0.4 },
    // 情绪峰值→弹幕簇关联
    { source: 'peak_1', target: 'danmu_1', value: 0.8, strength: 0.8 },
    { source: 'peak_2', target: 'danmu_2', value: 0.75, strength: 0.75 },
    // 话术→弹幕簇直接关联
    { source: 'speech_1', target: 'danmu_1', value: 0.85, strength: 0.85 },
    { source: 'speech_2', target: 'danmu_2', value: 0.6, strength: 0.6 }
  ]
};

// ==================== Methods ====================

const getNodeColor = (category: string): string => {
  const colorMap: Record<string, string> = {
    'speech': '#1890ff',
    'peak': '#ff4d4f',
    'danmu': '#52c41a'
  };
  return colorMap[category] || '#d9d9d9';
};

const getNodeTypeName = (category: string): string => {
  const nameMap: Record<string, string> = {
    'speech': '📝 话术',
    'peak': '⚡ 情绪峰值',
    'danmu': '💬 弹幕簇'
  };
  return nameMap[category] || category;
};

const getMetricLabel = (key: string): string => {
  const labelMap: Record<string, string> = {
    'emotion_impact': '情绪影响',
    'engagement_rate': '互动率',
    'score': '情绪分数',
    'duration': '持续时间',
    'count': '弹幕数',
    'positive_ratio': '积极比例'
  };
  return labelMap[key] || key;
};

const formatMetricValue = (key: string, value: any): string => {
  if (typeof value === 'number') {
    if (key.includes('ratio') || key.includes('impact')) {
      return (value * 100).toFixed(0) + '%';
    }
    if (key === 'score') {
      return value.toFixed(2);
    }
    return value.toFixed(0);
  }
  return String(value);
};

const initChart = () => {
  if (!chartRef.value) return;
  
  chart = echarts.init(chartRef.value);
  
  const data = props.data || mockData;
  
  const option: EChartsOption = {
    tooltip: {
      formatter: (params: any) => {
        if (params.dataType === 'node') {
          const node = params.data;
          let content = `<div style="font-weight:bold">${node.name}</div>`;
          if (node.content) {
            content += `<div style="font-size:12px;color:#666;margin-top:4px">${node.content}</div>`;
          }
          if (node.metrics) {
            content += `<div style="margin-top:8px;border-top:1px solid #eee;padding-top:4px">`;
            for (const [key, value] of Object.entries(node.metrics)) {
              content += `<div style="font-size:12px">${getMetricLabel(key)}: ${formatMetricValue(key, value)}</div>`;
            }
            content += `</div>`;
          }
          return content;
        }
        return '';
      }
    },
    legend: [{
      data: ['话术', '情绪峰值', '弹幕簇'],
      bottom: 10,
      itemGap: 20
    }],
    series: [
      {
        type: 'graph',
        layout: 'force',
        data: data.nodes.map(node => ({
          id: node.id,
          name: node.name,
          value: node.value,
          symbolSize: node.symbolSize || 20,
          category: node.category,
          content: node.content,
          metrics: node.metrics,
          itemStyle: {
            color: getNodeColor(node.category),
            shadowBlur: 10,
            shadowColor: 'rgba(0,0,0,0.2)'
          },
          label: {
            show: true,
            position: 'right',
            formatter: '{b}',
            fontSize: 12,
            color: '#333'
          }
        })),
        links: data.links.map(link => ({
          source: link.source,
          target: link.target,
          value: link.value,
          lineStyle: {
            width: link.strength ? link.strength * 5 : 2,
            curveness: 0.3,
            opacity: 0.6
          }
        })),
        categories: [
          { name: '话术' },
          { name: '情绪峰值' },
          { name: '弹幕簇' }
        ],
        roam: true,
        draggable: true,
        force: {
          repulsion: 300,
          edgeLength: 150,
          gravity: 0.1
        },
        lineStyle: {
          color: 'source',
          type: 'curve'
        },
        emphasis: {
          focus: 'adjacency',
          lineStyle: {
            width: 8,
            opacity: 1
          }
        }
      }
    ]
  };
  
  chart.setOption(option);
  
  // 节点点击事件
  chart.on('click', (params: any) => {
    if (params.dataType === 'node') {
      selectedNode.value = {
        id: params.data.id,
        category: params.data.category,
        name: params.data.name,
        content: params.data.content,
        metrics: params.data.metrics
      };
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

watch(() => props.data, () => {
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
.attribution-graph-container {
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
  width: 12px;
  height: 12px;
  border-radius: 50%;
  display: inline-block;
}

.legend-dot.speech {
  background: #1890ff;
}

.legend-dot.peak {
  background: #ff4d4f;
}

.legend-dot.danmu {
  background: #52c41a;
}

.graph-chart {
  width: 100%;
  height: v-bind('height || "500px"');
}

.detail-panel {
  margin-top: 16px;
  padding: 16px;
  background: #f5f5f5;
  border-radius: 8px;
  border-left: 4px solid #1890ff;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.detail-type {
  padding: 4px 12px;
  border-radius: 4px;
  font-weight: bold;
  font-size: 14px;
}

.detail-type.speech {
  background: #e6f7ff;
  color: #1890ff;
}

.detail-type.peak {
  background: #fff1f0;
  color: #ff4d4f;
}

.detail-type.danmu {
  background: #f6ffed;
  color: #52c41a;
}

.close-btn {
  width: 24px;
  height: 24px;
  border: none;
  background: transparent;
  font-size: 20px;
  color: #999;
  cursor: pointer;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: #d9d9d9;
  color: #333;
}

.detail-content {
  color: #333;
}

.detail-content p {
  margin: 0 0 12px 0;
  line-height: 1.6;
}

.detail-metrics {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
}

.metric {
  display: flex;
  justify-content: space-between;
  padding: 8px 12px;
  background: #fff;
  border-radius: 4px;
}

.metric-label {
  font-size: 13px;
  color: #666;
}

.metric-value {
  font-weight: bold;
  color: #333;
}
</style>
