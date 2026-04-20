<template>
  <div class="danmu-timeline">
    <!-- 时间轴图表 -->
    <div class="timeline-chart" ref="chartContainer">
      <canvas ref="chartCanvas"></canvas>
    </div>
    
    <!-- 筛选控制 -->
    <div class="controls">
      <div class="control-group">
        <label>时间间隔：</label>
        <select v-model="interval" @change="loadTimeline">
          <option value="10">10 秒</option>
          <option value="30">30 秒</option>
          <option value="60">1 分钟</option>
          <option value="120">2 分钟</option>
        </select>
      </div>
      
      <div class="control-group">
        <label>筛选：</label>
        <label class="checkbox-label">
          <input type="checkbox" v-model="showPositive" @change="updateFilter">
          <span class="sentiment-dot positive"></span> 积极
        </label>
        <label class="checkbox-label">
          <input type="checkbox" v-model="showNeutral" @change="updateFilter">
          <span class="sentiment-dot neutral"></span> 中性
        </label>
        <label class="checkbox-label">
          <input type="checkbox" v-model="showNegative" @change="updateFilter">
          <span class="sentiment-dot negative"></span> 消极
        </label>
      </div>
      
      <div class="control-group">
        <label class="checkbox-label">
          <input type="checkbox" v-model="showKeyDanmu" @change="updateFilter">
          🔑 关键弹幕
        </label>
      </div>
    </div>
    
    <!-- 统计信息 -->
    <div class="stats">
      <div class="stat-item">
        <span class="stat-label">总弹幕数</span>
        <span class="stat-value">{{ totalDanmus }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">积极</span>
        <span class="stat-value positive">{{ positiveCount }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">中性</span>
        <span class="stat-value neutral">{{ neutralCount }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">消极</span>
        <span class="stat-value negative">{{ negativeCount }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">关键弹幕</span>
        <span class="stat-value key">{{ keyDanmuCount }}</span>
      </div>
    </div>
    
    <!-- 关键弹幕列表 -->
    <div class="key-danmus" v-if="keyDanmus.length > 0">
      <h3>🔑 关键弹幕</h3>
      <div class="danmu-list">
        <div 
          v-for="danmu in keyDanmus" 
          :key="danmu.id"
          :class="['danmu-item', 'key-' + danmu.key_type]"
        >
          <div class="danmu-header">
            <span class="timestamp">{{ formatTime(danmu.timestamp) }}</span>
            <span class="user" v-if="danmu.username">{{ danmu.username }}</span>
            <span class="key-type" :class="danmu.key_type">
              {{ getKeyTypeLabel(danmu.key_type) }}
            </span>
          </div>
          <div class="danmu-content">{{ danmu.content }}</div>
          <div class="danmu-meta">
            <span :class="['sentiment', danmu.sentiment]">
              {{ getSentimentLabel(danmu.sentiment) }}
            </span>
            <span v-if="danmu.like_count > 0">👍 {{ danmu.like_count }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 加载状态 -->
    <div v-if="loading" class="loading">
      <span>加载中...</span>
    </div>
    
    <!-- 错误提示 -->
    <div v-if="error" class="error">
      {{ error }}
    </div>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue'
import axios from 'axios'

const API_BASE = 'http://localhost:8001/api'

export default {
  name: 'DanmuTimeline',
  props: {
    videoId: {
      type: String,
      default: null
    }
  },
  setup() {
    const chartCanvas = ref(null)
    const chartContainer = ref(null)
    const loading = ref(false)
    const error = ref(null)
    
    const interval = ref(30)
    const showPositive = ref(true)
    const showNeutral = ref(true)
    const showNegative = ref(true)
    const showKeyDanmu = ref(true)
    
    const timelineData = ref([])
    const keyDanmus = ref([])
    const totalDanmus = ref(0)
    const positiveCount = ref(0)
    const neutralCount = ref(0)
    const negativeCount = ref(0)
    const keyDanmuCount = ref(0)
    
    let chartCtx = null
    let chartInstance = null
    
    // 加载时间轴数据
    const loadTimeline = async () => {
      loading.value = true
      error.value = null
      
      try {
        const response = await axios.get(`${API_BASE}/danmu/timeline`, {
          params: { interval: interval.value }
        })
        
        timelineData.value = response.data.data || []
        renderChart()
        updateStats()
      } catch (err) {
        error.value = '加载时间轴失败：' + (err.response?.data?.detail || err.message)
        console.error('加载时间轴失败:', err)
      } finally {
        loading.value = false
      }
    }
    
    // 加载关键弹幕
    const loadKeyDanmus = async () => {
      try {
        const response = await axios.get(`${API_BASE}/danmu/key`, {
          params: { limit: 20 }
        })
        keyDanmus.value = response.data.data || []
        keyDanmuCount.value = response.data.total || 0
      } catch (err) {
        console.error('加载关键弹幕失败:', err)
      }
    }
    
    // 加载摘要统计
    const loadSummary = async () => {
      try {
        const response = await axios.get(`${API_BASE}/danmu/summary`)
        const summary = response.data
        
        totalDanmus.value = summary.total_count || 0
        positiveCount.value = summary.sentiment_distribution?.positive || 0
        neutralCount.value = summary.sentiment_distribution?.neutral || 0
        negativeCount.value = summary.sentiment_distribution?.negative || 0
      } catch (err) {
        console.error('加载摘要失败:', err)
      }
    }
    
    // 渲染图表
    const renderChart = () => {
      if (!chartCanvas.value || timelineData.value.length === 0) return
      
      const canvas = chartCanvas.value
      const ctx = canvas.getContext('2d')
      chartCtx = ctx
      
      // 设置画布大小
      const container = chartContainer.value
      canvas.width = container.clientWidth
      canvas.height = 300
      
      const width = canvas.width
      const height = canvas.height
      const padding = 40
      
      // 清空画布
      ctx.clearRect(0, 0, width, height)
      
      // 计算最大值
      const maxCount = Math.max(...timelineData.value.map(d => d.count), 1)
      
      // 绘制坐标轴
      ctx.strokeStyle = '#e0e0e0'
      ctx.lineWidth = 1
      ctx.beginPath()
      ctx.moveTo(padding, padding)
      ctx.lineTo(padding, height - padding)
      ctx.lineTo(width - padding, height - padding)
      ctx.stroke()
      
      // 绘制柱状图
      const barWidth = (width - 2 * padding) / timelineData.value.length
      const barGap = 2
      
      timelineData.value.forEach((point, index) => {
        const x = padding + index * barWidth
        const barHeight = ((point.count || 0) / maxCount) * (height - 2 * padding)
        const y = height - padding - barHeight
        
        // 根据情感绘制不同颜色
        const positiveHeight = ((point.positive || 0) / maxCount) * (height - 2 * padding)
        const neutralHeight = ((point.neutral || 0) / maxCount) * (height - 2 * padding)
        const negativeHeight = ((point.negative || 0) / maxCount) * (height - 2 * padding)
        
        // 绘制堆叠柱状图
        if (showPositive.value) {
          ctx.fillStyle = '#4CAF50'
          ctx.fillRect(x + barGap, height - padding - positiveHeight, barWidth - 2 * barGap, positiveHeight)
        }
        
        if (showNeutral.value) {
          ctx.fillStyle = '#9E9E9E'
          ctx.fillRect(
            x + barGap, 
            height - padding - positiveHeight - neutralHeight, 
            barWidth - 2 * barGap, 
            neutralHeight
          )
        }
        
        if (showNegative.value) {
          ctx.fillStyle = '#F44336'
          ctx.fillRect(
            x + barGap, 
            height - padding - positiveHeight - neutralHeight - negativeHeight, 
            barWidth - 2 * barGap, 
            negativeHeight
          )
        }
        
        // 标记关键弹幕
        if (showKeyDanmu.value && point.key_danmu_count > 0) {
          ctx.fillStyle = '#FF9800'
          ctx.beginPath()
          ctx.arc(x + barWidth / 2, y - 5, 4, 0, Math.PI * 2)
          ctx.fill()
        }
      })
      
      // 绘制时间标签
      ctx.fillStyle = '#666'
      ctx.font = '10px Arial'
      ctx.textAlign = 'center'
      
      const labelStep = Math.ceil(timelineData.value.length / 10)
      timelineData.value.forEach((point, index) => {
        if (index % labelStep === 0) {
          const x = padding + index * barWidth + barWidth / 2
          ctx.fillText(point.timestamp_str, x, height - padding + 15)
        }
      })
      
      // 绘制 Y 轴标签
      ctx.textAlign = 'right'
      for (let i = 0; i <= 4; i++) {
        const y = height - padding - (i / 4) * (height - 2 * padding)
        const value = Math.round((i / 4) * maxCount)
        ctx.fillText(value, padding - 5, y + 3)
      }
    }
    
    // 更新筛选
    const updateFilter = () => {
      renderChart()
    }
    
    // 更新统计
    const updateStats = () => {
      if (timelineData.value.length === 0) return
      
      const total = timelineData.value.reduce((sum, d) => sum + d.count, 0)
      const positive = timelineData.value.reduce((sum, d) => sum + (d.positive || 0), 0)
      const neutral = timelineData.value.reduce((sum, d) => sum + (d.neutral || 0), 0)
      const negative = timelineData.value.reduce((sum, d) => sum + (d.negative || 0), 0)
      const key = timelineData.value.reduce((sum, d) => sum + (d.key_danmu_count || 0), 0)
      
      totalDanmus.value = total
      positiveCount.value = positive
      neutralCount.value = neutral
      negativeCount.value = negative
      keyDanmuCount.value = key
    }
    
    // 格式化时间
    const formatTime = (seconds) => {
      const mins = Math.floor(seconds / 60)
      const secs = Math.floor(seconds % 60)
      return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
    }
    
    // 获取情感标签
    const getSentimentLabel = (sentiment) => {
      const labels = {
        positive: '积极',
        neutral: '中性',
        negative: '消极'
      }
      return labels[sentiment] || sentiment
    }
    
    // 获取关键类型标签
    const getKeyTypeLabel = (keyType) => {
      const labels = {
        climax: '🔥 高潮',
        controversy: '⚠️ 争议',
        praise: '👍 赞赏',
        question: '❓ 提问'
      }
      return labels[keyType] || keyType
    }
    
    onMounted(() => {
      loadTimeline()
      loadKeyDanmus()
      loadSummary()
      
      // 窗口大小变化时重绘图表
      window.addEventListener('resize', () => {
        setTimeout(renderChart, 100)
      })
    })
    
    return {
      chartCanvas,
      chartContainer,
      loading,
      error,
      interval,
      showPositive,
      showNeutral,
      showNegative,
      showKeyDanmu,
      timelineData,
      keyDanmus,
      totalDanmus,
      positiveCount,
      neutralCount,
      negativeCount,
      keyDanmuCount,
      loadTimeline,
      updateFilter,
      formatTime,
      getSentimentLabel,
      getKeyTypeLabel
    }
  }
}
</script>

<style scoped>
.danmu-timeline {
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.timeline-chart {
  margin-bottom: 20px;
  background: #fafafa;
  border-radius: 4px;
  padding: 10px;
}

.controls {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 20px;
  padding: 15px;
  background: #f5f5f5;
  border-radius: 4px;
}

.control-group {
  display: flex;
  align-items: center;
  gap: 10px;
}

.control-group label {
  font-size: 14px;
  color: #666;
}

.checkbox-label {
  display: flex !important;
  align-items: center;
  gap: 5px !important;
  cursor: pointer;
}

.checkbox-label input {
  cursor: pointer;
}

.sentiment-dot {
  display: inline-block;
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.sentiment-dot.positive {
  background: #4CAF50;
}

.sentiment-dot.neutral {
  background: #9E9E9E;
}

.sentiment-dot.negative {
  background: #F44336;
}

.stats {
  display: flex;
  gap: 20px;
  margin-bottom: 20px;
  padding: 15px;
  background: #f9f9f9;
  border-radius: 4px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  min-width: 80px;
}

.stat-label {
  font-size: 12px;
  color: #666;
  margin-bottom: 5px;
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #333;
}

.stat-value.positive {
  color: #4CAF50;
}

.stat-value.neutral {
  color: #9E9E9E;
}

.stat-value.negative {
  color: #F44336;
}

.stat-value.key {
  color: #FF9800;
}

.key-danmus {
  margin-top: 30px;
}

.key-danmus h3 {
  margin-bottom: 15px;
  color: #333;
  font-size: 16px;
}

.danmu-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.danmu-item {
  padding: 12px;
  border-radius: 4px;
  border-left: 4px solid #FF9800;
  background: #fff8e1;
}

.danmu-item.key-climax {
  border-left-color: #F44336;
  background: #ffebee;
}

.danmu-item.key-controversy {
  border-left-color: #9C27B0;
  background: #f3e5f5;
}

.danmu-item.key-praise {
  border-left-color: #4CAF50;
  background: #e8f5e9;
}

.danmu-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
  font-size: 12px;
}

.timestamp {
  color: #666;
  font-family: monospace;
}

.user {
  color: #1976D2;
  font-weight: 500;
}

.key-type {
  padding: 2px 6px;
  border-radius: 3px;
  font-size: 11px;
  background: rgba(0, 0, 0, 0.1);
}

.key-type.climax {
  background: #F44336;
  color: white;
}

.key-type.controversy {
  background: #9C27B0;
  color: white;
}

.key-type.praise {
  background: #4CAF50;
  color: white;
}

.danmu-content {
  font-size: 14px;
  color: #333;
  margin-bottom: 8px;
  line-height: 1.4;
}

.danmu-meta {
  display: flex;
  gap: 15px;
  font-size: 12px;
  color: #666;
}

.sentiment {
  padding: 1px 6px;
  border-radius: 3px;
  font-size: 11px;
}

.sentiment.positive {
  background: #E8F5E9;
  color: #2E7D32;
}

.sentiment.neutral {
  background: #F5F5F5;
  color: #616161;
}

.sentiment.negative {
  background: #FFEBEE;
  color: #C62828;
}

.loading, .error {
  text-align: center;
  padding: 40px;
  color: #666;
}

.error {
  color: #F44336;
}

select {
  padding: 5px 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
}
</style>
