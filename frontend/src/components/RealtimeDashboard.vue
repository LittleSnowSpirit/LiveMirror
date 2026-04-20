<template>
  <div class="realtime-dashboard">
    <!-- 顶部状态栏 -->
    <div class="status-bar">
      <div class="connection-status" :class="connectionStatus">
        <span class="status-dot"></span>
        <span class="status-text">{{ statusText }}</span>
      </div>
      <div class="session-info">
        <span>会话：{{ sessionId }}</span>
        <span v-if="sessionDuration">时长：{{ formatDuration(sessionDuration) }}</span>
      </div>
      <div class="latency-display" :class="latencyClass">
        <span class="latency-label">延迟:</span>
        <span class="latency-value">{{ avgLatency }}ms</span>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 左侧：实时转写 -->
      <div class="panel transcription-panel">
        <div class="panel-header">
          <h3>📝 实时转写</h3>
          <div class="panel-actions">
            <button @click="toggleRecording" :disabled="!isConnected" class="btn-record" :class="{ recording: isRecording }">
              {{ isRecording ? '⏹ 停止' : '🎤 开始' }}
            </button>
            <button @click="clearTranscription" class="btn-clear">清空</button>
          </div>
        </div>
        <div class="transcription-content">
          <div class="transcription-text">
            <p v-for="(segment, index) in transcriptionSegments" :key="index" class="segment">
              <span class="segment-index">{{ index + 1 }}</span>
              <span class="segment-text">{{ segment.text }}</span>
              <span class="segment-time">{{ formatTime(segment.timestamp) }}</span>
            </p>
            <p v-if="transcriptionSegments.length === 0" class="empty-state">
              点击"开始"按钮开始录音，或输入文本测试
            </p>
          </div>
        </div>
      </div>

      <!-- 右侧：分析面板 -->
      <div class="panel analysis-panel">
        <!-- 情绪分析 -->
        <div class="analysis-section">
          <h4>😊 情绪分析</h4>
          <div class="sentiment-display">
            <div class="sentiment-gauge">
              <div class="gauge-bar">
                <div class="gauge-fill" :style="{ width: sentimentScore * 100 + '%', backgroundColor: sentimentColor }"></div>
              </div>
              <div class="sentiment-labels">
                <span>负面</span>
                <span>{{ currentSentiment }}</span>
                <span>正面</span>
              </div>
            </div>
            <div class="sentiment-score">{{ (sentimentScore * 100).toFixed(0) }}分</div>
          </div>
          
          <!-- 情绪分布 -->
          <div class="emotion-breakdown" v-if="currentEmotions">
            <div v-for="(value, emotion) in currentEmotions" :key="emotion" class="emotion-item">
              <span class="emotion-name">{{ getEmotionLabel(emotion) }}</span>
              <div class="emotion-bar">
                <div class="emotion-fill" :style="{ width: value * 100 + '%' }"></div>
              </div>
              <span class="emotion-value">{{ (value * 100).toFixed(0) }}%</span>
            </div>
          </div>
        </div>

        <!-- 话术建议 -->
        <div class="analysis-section">
          <h4>💡 话术建议</h4>
          <div class="suggestions-list">
            <div v-for="(suggestion, index) in currentSuggestions" :key="index" class="suggestion-item" :class="getSuggestionPriority(suggestion.priority)">
              <span class="suggestion-icon">{{ getSuggestionIcon(suggestion.priority) }}</span>
              <span class="suggestion-text">{{ suggestion.text || suggestion }}</span>
            </div>
            <p v-if="currentSuggestions.length === 0" class="empty-state">
              暂无建议
            </p>
          </div>
        </div>

        <!-- 风险提示 -->
        <div class="analysis-section" v-if="currentRisks && currentRisks.length > 0">
          <h4>⚠️ 风险提示</h4>
          <div class="risks-list">
            <div v-for="(risk, index) in currentRisks" :key="index" class="risk-item">
              <span class="risk-icon">⚠️</span>
              <span class="risk-text">{{ risk }}</span>
            </div>
          </div>
        </div>

        <!-- 关键词 -->
        <div class="analysis-section">
          <h4>🏷️ 关键词</h4>
          <div class="keywords-cloud">
            <span v-for="(keyword, index) in currentKeywords" :key="index" class="keyword-tag">
              {{ keyword }}
            </span>
            <span v-if="currentKeywords.length === 0" class="empty-state">
              暂无关键词
            </span>
          </div>
        </div>
      </div>
    </div>

    <!-- 底部：性能统计 -->
    <div class="stats-bar">
      <div class="stat-item">
        <span class="stat-label">片段数:</span>
        <span class="stat-value">{{ segmentCount }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">平均延迟:</span>
        <span class="stat-value" :class="latencyClass">{{ avgLatency }}ms</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">最小延迟:</span>
        <span class="stat-value">{{ minLatency }}ms</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">最大延迟:</span>
        <span class="stat-value">{{ maxLatency }}ms</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">消息发送:</span>
        <span class="stat-value">{{ messagesSent }}</span>
      </div>
      <div class="stat-item">
        <span class="stat-label">消息接收:</span>
        <span class="stat-value">{{ messagesReceived }}</span>
      </div>
    </div>

    <!-- 文本测试输入 -->
    <div class="text-test-panel" v-if="showTextTest">
      <h4>📝 文本测试模式</h4>
      <div class="text-input-row">
        <input 
          v-model="testTextInput" 
          @keyup.enter="sendTestText"
          placeholder="输入文本进行实时分析测试..."
          class="text-input"
        />
        <button @click="sendTestText" :disabled="!isConnected" class="btn-send">发送</button>
      </div>
    </div>
  </div>
</template>

<script>
import { createWebSocketClient } from '../utils/websocket_client.js'

export default {
  name: 'RealtimeDashboard',
  
  props: {
    sessionId: {
      type: String,
      default: () => `session_${Date.now()}`
    },
    wsUrl: {
      type: String,
      default: 'ws://localhost:8000/ws/stream/text'
    },
    showTextTest: {
      type: Boolean,
      default: true
    }
  },

  data() {
    return {
      client: null,
      isConnected: false,
      isRecording: false,
      
      // 转写数据
      transcriptionSegments: [],
      
      // 分析数据
      currentSentiment: 'neutral',
      sentimentScore: 0.5,
      currentEmotions: null,
      currentSuggestions: [],
      currentRisks: [],
      currentKeywords: [],
      
      // 性能统计
      sessionDuration: 0,
      segmentCount: 0,
      avgLatency: 0,
      minLatency: 0,
      maxLatency: 0,
      messagesSent: 0,
      messagesReceived: 0,
      latencies: [],
      
      // 文本测试
      testTextInput: '',
      
      // 定时器
      durationTimer: null
    }
  },

  computed: {
    connectionStatus() {
      return this.isConnected ? 'connected' : 'disconnected'
    },
    
    statusText() {
      return this.isConnected ? '已连接' : '未连接'
    },
    
    latencyClass() {
      if (this.avgLatency < 1000) return 'latency-good'
      if (this.avgLatency < 2000) return 'latency-warning'
      return 'latency-bad'
    },
    
    sentimentColor() {
      if (this.sentimentScore > 0.6) return '#10b981'  // green
      if (this.sentimentScore < 0.4) return '#ef4444'  // red
      return '#f59e0b'  // yellow
    }
  },

  mounted() {
    this.initWebSocket()
  },

  beforeUnmount() {
    this.cleanup()
  },

  methods: {
    /**
     * 初始化 WebSocket 连接
     */
    async initWebSocket() {
      this.client = createWebSocketClient({
        url: this.wsUrl,
        sessionId: this.sessionId,
        reconnectInterval: 3000,
        maxReconnectAttempts: 5,
        heartbeatInterval: 10000
      })

      // 注册回调
      this.client.on('onConnected', () => {
        this.isConnected = true
        this.startDurationTimer()
        this.$emit('connected', { sessionId: this.sessionId })
      })

      this.client.on('onDisconnected', () => {
        this.isConnected = false
        this.stopDurationTimer()
        this.$emit('disconnected')
      })

      this.client.on('onReconnecting', (data) => {
        this.$emit('reconnecting', data)
      })

      this.client.on('onError', (error) => {
        console.error('[Dashboard] 错误:', error)
        this.$emit('error', error)
      })

      this.client.on('onTranscription', (message) => {
        this.handleTranscription(message)
      })

      this.client.on('onAnalysis', (message) => {
        this.handleAnalysis(message)
      })

      this.client.on('onStats', (message) => {
        this.handleStats(message)
      })

      // 连接
      try {
        await this.client.connect()
      } catch (error) {
        console.error('[Dashboard] 连接失败:', error)
        this.$emit('connection-error', error)
      }
    },

    /**
     * 处理转写消息
     */
    handleTranscription(message) {
      this.transcriptionSegments.push({
        text: message.text,
        timestamp: message.timestamp,
        segmentIndex: message.segment_index
      })

      // 保持最近 50 条
      if (this.transcriptionSegments.length > 50) {
        this.transcriptionSegments.shift()
      }

      this.segmentCount = message.segment_index
    },

    /**
     * 处理分析消息
     */
    handleAnalysis(message) {
      if (message.analysis) {
        this.currentSentiment = message.analysis.sentiment
        this.sentimentScore = message.analysis.sentiment_score
        this.currentEmotions = message.analysis.emotions
        this.currentSuggestions = message.analysis.suggestions || []
        this.currentRisks = message.analysis.risks || []
        this.currentKeywords = message.analysis.keywords || []
      }

      if (message.performance) {
        this.updateLatency(message.performance.latency_ms)
      }
    },

    /**
     * 处理统计消息
     */
    handleStats(message) {
      if (message.avg_latency_ms) {
        this.updateLatency(message.avg_latency_ms)
      }
      
      if (message.segment_count) {
        this.segmentCount = message.segment_count
      }
    },

    /**
     * 更新延迟统计
     */
    updateLatency(latency) {
      this.latencies.push(latency)
      
      // 保留最近 100 个数据
      if (this.latencies.length > 100) {
        this.latencies.shift()
      }

      this.avgLatency = Math.round(this.latencies.reduce((a, b) => a + b, 0) / this.latencies.length)
      this.minLatency = Math.round(Math.min(...this.latencies))
      this.maxLatency = Math.round(Math.max(...this.latencies))
    },

    /**
     * 切换录音状态
     */
    async toggleRecording() {
      if (this.isRecording) {
        this.stopRecording()
      } else {
        await this.startRecording()
      }
    },

    /**
     * 开始录音
     */
    async startRecording() {
      try {
        await this.client.startRecording()
        this.isRecording = true
        this.$emit('recording-started')
      } catch (error) {
        console.error('[Dashboard] 录音启动失败:', error)
        alert('录音启动失败：' + error.message)
      }
    },

    /**
     * 停止录音
     */
    stopRecording() {
      this.client.stopRecording()
      this.isRecording = false
      this.client.stop()
      this.$emit('recording-stopped')
    },

    /**
     * 清空转写
     */
    clearTranscription() {
      this.transcriptionSegments = []
      this.segmentCount = 0
    },

    /**
     * 发送测试文本
     */
    sendTestText() {
      if (!this.testTextInput.trim()) return
      
      this.client.sendText(this.testTextInput)
      this.testTextInput = ''
    },

    /**
     * 启动时长计时器
     */
    startDurationTimer() {
      const startTime = Date.now()
      this.durationTimer = setInterval(() => {
        this.sessionDuration = Date.now() - startTime
      }, 1000)
    },

    /**
     * 停止时长计时器
     */
    stopDurationTimer() {
      if (this.durationTimer) {
        clearInterval(this.durationTimer)
        this.durationTimer = null
      }
    },

    /**
     * 清理资源
     */
    cleanup() {
      this.stopRecording()
      this.stopDurationTimer()
      if (this.client) {
        this.client.disconnect()
        this.client = null
      }
    },

    /**
     * 格式化时长
     */
    formatDuration(ms) {
      const seconds = Math.floor(ms / 1000)
      const minutes = Math.floor(seconds / 60)
      const hours = Math.floor(minutes / 60)

      if (hours > 0) {
        return `${hours}:${(minutes % 60).toString().padStart(2, '0')}:${(seconds % 60).toString().padStart(2, '0')}`
      }
      return `${minutes}:${(seconds % 60).toString().padStart(2, '0')}`
    },

    /**
     * 格式化时间
     */
    formatTime(timestamp) {
      const date = new Date(timestamp * 1000)
      return date.toLocaleTimeString('zh-CN', { hour12: false })
    },

    /**
     * 获取情绪标签
     */
    getEmotionLabel(emotion) {
      const labels = {
        joy: '开心',
        sadness: '悲伤',
        anger: '愤怒',
        surprise: '惊讶',
        neutral: '中性'
      }
      return labels[emotion] || emotion
    },

    /**
     * 获取建议图标
     */
    getSuggestionIcon(priority) {
      const icons = {
        high: '🔥',
        medium: '💡',
        low: '💭'
      }
      return icons[priority] || '💡'
    },

    /**
     * 获取建议优先级样式
     */
    getSuggestionPriority(suggestion) {
      if (typeof suggestion === 'object' && suggestion.priority) {
        return `priority-${suggestion.priority}`
      }
      return ''
    }
  },

  emits: ['connected', 'disconnected', 'reconnecting', 'error', 'connection-error', 'recording-started', 'recording-stopped']
}
</script>

<style scoped>
.realtime-dashboard {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: #f8fafc;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

/* 状态栏 */
.status-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 20px;
  background: white;
  border-bottom: 1px solid #e2e8f0;
  gap: 20px;
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
}

.connection-status.connected {
  background: #dcfce7;
  color: #166534;
}

.connection-status.disconnected {
  background: #fee2e2;
  color: #991b1b;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
}

.session-info {
  display: flex;
  gap: 16px;
  color: #64748b;
  font-size: 14px;
}

.latency-display {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 600;
}

.latency-display.latency-good {
  background: #dcfce7;
  color: #166534;
}

.latency-display.latency-warning {
  background: #fef3c7;
  color: #92400e;
}

.latency-display.latency-bad {
  background: #fee2e2;
  color: #991b1b;
}

/* 主内容区 */
.main-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  flex: 1;
  gap: 16px;
  padding: 16px;
  overflow: hidden;
}

.panel {
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid #e2e8f0;
}

.panel-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.panel-actions {
  display: flex;
  gap: 8px;
}

.btn-record {
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  background: #3b82f6;
  color: white;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-record:hover:not(:disabled) {
  background: #2563eb;
}

.btn-record:disabled {
  background: #cbd5e1;
  cursor: not-allowed;
}

.btn-record.recording {
  background: #ef4444;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

.btn-clear {
  padding: 8px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: white;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-clear:hover {
  background: #f1f5f9;
}

/* 转写面板 */
.transcription-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.transcription-text {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.segment {
  display: flex;
  gap: 12px;
  padding: 12px;
  background: #f8fafc;
  border-radius: 8px;
  border-left: 3px solid #3b82f6;
}

.segment-index {
  font-weight: 600;
  color: #64748b;
  min-width: 24px;
}

.segment-text {
  flex: 1;
  color: #1e293b;
  line-height: 1.5;
}

.segment-time {
  color: #94a3b8;
  font-size: 12px;
  white-space: nowrap;
}

.empty-state {
  text-align: center;
  color: #94a3b8;
  padding: 40px;
}

/* 分析面板 */
.analysis-panel {
  padding: 16px;
  overflow-y: auto;
}

.analysis-section {
  margin-bottom: 24px;
}

.analysis-section h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: #475569;
}

/* 情绪显示 */
.sentiment-display {
  margin-bottom: 16px;
}

.sentiment-gauge {
  margin-bottom: 8px;
}

.gauge-bar {
  height: 20px;
  background: #e2e8f0;
  border-radius: 10px;
  overflow: hidden;
  position: relative;
}

.gauge-fill {
  height: 100%;
  border-radius: 10px;
  transition: width 0.3s ease, background-color 0.3s ease;
}

.sentiment-labels {
  display: flex;
  justify-content: space-between;
  font-size: 12px;
  color: #64748b;
  margin-top: 4px;
}

.sentiment-score {
  text-align: center;
  font-size: 24px;
  font-weight: 700;
  color: #1e293b;
}

/* 情绪分布 */
.emotion-breakdown {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.emotion-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.emotion-name {
  width: 60px;
  font-size: 13px;
  color: #64748b;
}

.emotion-bar {
  flex: 1;
  height: 8px;
  background: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
}

.emotion-fill {
  height: 100%;
  background: #3b82f6;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.emotion-value {
  width: 40px;
  text-align: right;
  font-size: 12px;
  color: #64748b;
}

/* 建议列表 */
.suggestions-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.suggestion-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  padding: 10px 12px;
  background: #f8fafc;
  border-radius: 6px;
  font-size: 13px;
}

.suggestion-item.priority-high {
  background: #fef2f2;
  border-left: 3px solid #ef4444;
}

.suggestion-item.priority-medium {
  background: #fffbeb;
  border-left: 3px solid #f59e0b;
}

.suggestion-item.priority-low {
  background: #f0f9ff;
  border-left: 3px solid #3b82f6;
}

.suggestion-icon {
  font-size: 16px;
}

.suggestion-text {
  flex: 1;
  color: #334155;
  line-height: 1.4;
}

/* 风险列表 */
.risks-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.risk-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 6px;
  font-size: 13px;
  color: #991b1b;
}

.risk-icon {
  font-size: 16px;
}

/* 关键词云 */
.keywords-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.keyword-tag {
  padding: 6px 12px;
  background: #e0e7ff;
  color: #4338ca;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 500;
}

/* 统计栏 */
.stats-bar {
  display: flex;
  justify-content: space-around;
  padding: 12px 20px;
  background: white;
  border-top: 1px solid #e2e8f0;
  gap: 16px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.stat-label {
  font-size: 12px;
  color: #64748b;
}

.stat-value {
  font-size: 16px;
  font-weight: 600;
  color: #1e293b;
}

.stat-value.latency-good {
  color: #166534;
}

.stat-value.latency-warning {
  color: #92400e;
}

.stat-value.latency-bad {
  color: #991b1b;
}

/* 文本测试面板 */
.text-test-panel {
  padding: 16px 20px;
  background: white;
  border-top: 1px solid #e2e8f0;
}

.text-test-panel h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: #475569;
}

.text-input-row {
  display: flex;
  gap: 12px;
}

.text-input {
  flex: 1;
  padding: 10px 14px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;
  outline: none;
  transition: border-color 0.2s;
}

.text-input:focus {
  border-color: #3b82f6;
}

.btn-send {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  background: #3b82f6;
  color: white;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-send:hover:not(:disabled) {
  background: #2563eb;
}

.btn-send:disabled {
  background: #cbd5e1;
  cursor: not-allowed;
}

/* 响应式 */
@media (max-width: 1024px) {
  .main-content {
    grid-template-columns: 1fr;
  }
}
</style>
