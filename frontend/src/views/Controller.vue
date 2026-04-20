<template>
  <div class="controller-page">
    <!-- 顶部状态栏 -->
    <div class="status-bar">
      <div class="status-item">
        <span class="status-label">直播状态:</span>
        <span :class="['status-value', isLive ? 'live' : 'offline']">
          {{ isLive ? '🔴 直播中' : '⚪ 未直播' }}
        </span>
      </div>
      <div class="status-item">
        <span class="status-label">房间 ID:</span>
        <span class="status-value">{{ currentStreamId || '-' }}</span>
      </div>
      <div class="status-item">
        <span class="status-label">弹幕总数:</span>
        <span class="status-value">{{ stats.total_danmaku }}</span>
      </div>
      <div class="status-item">
        <span class="status-label">自动回复:</span>
        <span class="status-value">{{ stats.auto_replies }}</span>
      </div>
      <div class="status-item">
        <span class="status-label">违规处理:</span>
        <span class="status-value">{{ stats.violations_handled }}</span>
      </div>
      <div class="status-item">
        <span class="status-label">预警数:</span>
        <span class="status-value">{{ stats.alerts_triggered }}</span>
      </div>
      
      <div class="action-buttons">
        <button 
          v-if="!isLive" 
          @click="startLive" 
          class="btn btn-start"
          :disabled="starting"
        >
          {{ starting ? '启动中...' : '开始监控' }}
        </button>
        <button 
          v-else 
          @click="stopLive" 
          class="btn btn-stop"
          :disabled="stopping"
        >
          {{ stopping ? '停止中...' : '停止监控' }}
        </button>
      </div>
    </div>

    <!-- 主内容区 -->
    <div class="main-content">
      <!-- 左侧：实时监控 -->
      <div class="left-panel">
        <!-- 观众情绪 -->
        <div class="panel emotion-panel">
          <h3 class="panel-title">📊 观众情绪</h3>
          <div class="emotion-chart">
            <div v-if="currentEmotion" class="emotion-bars">
              <div class="emotion-bar">
                <span class="bar-label">积极</span>
                <div class="bar-container">
                  <div 
                    class="bar-fill positive" 
                    :style="{ width: (currentEmotion.positive * 100) + '%' }"
                  ></div>
                </div>
                <span class="bar-value">{{ (currentEmotion.positive * 100).toFixed(1) }}%</span>
              </div>
              <div class="emotion-bar">
                <span class="bar-label">中性</span>
                <div class="bar-container">
                  <div 
                    class="bar-fill neutral" 
                    :style="{ width: (currentEmotion.neutral * 100) + '%' }"
                  ></div>
                </div>
                <span class="bar-value">{{ (currentEmotion.neutral * 100).toFixed(1) }}%</span>
              </div>
              <div class="emotion-bar">
                <span class="bar-label">消极</span>
                <div class="bar-container">
                  <div 
                    class="bar-fill negative" 
                    :style="{ width: (currentEmotion.negative * 100) + '%' }"
                  ></div>
                </div>
                <span class="bar-value">{{ (currentEmotion.negative * 100).toFixed(1) }}%</span>
              </div>
              <div class="emotion-bar">
                <span class="bar-label">兴奋</span>
                <div class="bar-container">
                  <div 
                    class="bar-fill excited" 
                    :style="{ width: (currentEmotion.excited * 100) + '%' }"
                  ></div>
                </div>
                <span class="bar-value">{{ (currentEmotion.excited * 100).toFixed(1) }}%</span>
              </div>
            </div>
            <div v-else class="no-data">暂无数据</div>
          </div>
        </div>

        <!-- 节奏建议 -->
        <div class="panel suggestion-panel">
          <h3 class="panel-title">💡 直播节奏建议</h3>
          <div class="suggestions-list">
            <div 
              v-for="(suggestion, index) in suggestions" 
              :key="index"
              :class="['suggestion-item', 'priority-' + suggestion.priority]"
            >
              <div class="suggestion-header">
                <span class="suggestion-type">{{ getSuggestionTypeText(suggestion.suggestion_type) }}</span>
                <span class="suggestion-timing">{{ getTimingText(suggestion.timing) }}</span>
              </div>
              <div class="suggestion-reason">{{ suggestion.reason }}</div>
              <div class="suggestion-content">{{ suggestion.content }}</div>
            </div>
            <div v-if="suggestions.length === 0" class="no-data">暂无建议</div>
          </div>
        </div>

        <!-- 预警信息 -->
        <div class="panel alerts-panel">
          <h3 class="panel-title">⚠️ 实时预警</h3>
          <div class="alerts-list">
            <div 
              v-for="(alert, index) in alerts" 
              :key="index"
              :class="['alert-item', alert.level]"
            >
              <div class="alert-time">{{ formatTime(alert.timestamp) }}</div>
              <div class="alert-content">
                <span class="alert-type">{{ alert.type }}</span>
                <span class="alert-message">{{ alert.message }}</span>
              </div>
              <div v-if="alert.user_id" class="alert-user">用户：{{ alert.user_id }}</div>
            </div>
            <div v-if="alerts.length === 0" class="no-data">暂无预警</div>
          </div>
        </div>
      </div>

      <!-- 右侧：弹幕和日志 -->
      <div class="right-panel">
        <!-- 实时弹幕 -->
        <div class="panel danmaku-panel">
          <h3 class="panel-title">💬 实时弹幕</h3>
          <div class="danmaku-list">
            <div 
              v-for="(msg, index) in danmakuMessages" 
              :key="index"
              :class="['danmaku-item', { 'highlight': msg.isHighlight }]"
            >
              <div class="danmaku-user">
                <span class="username">{{ msg.username }}</span>
                <span v-if="msg.is_moderator" class="badge mod">管</span>
                <span v-if="msg.is_fan" class="badge fan">粉</span>
              </div>
              <div class="danmaku-content">{{ msg.content }}</div>
              <div class="danmaku-time">{{ formatTime(msg.timestamp) }}</div>
            </div>
            <div v-if="danmakuMessages.length === 0" class="no-data">等待弹幕...</div>
          </div>
        </div>

        <!-- 操作日志 -->
        <div class="panel logs-panel">
          <h3 class="panel-title">📝 操作日志</h3>
          <div class="logs-list">
            <div 
              v-for="(log, index) in logs" 
              :key="index"
              class="log-item"
            >
              <div class="log-time">{{ formatTime(log.timestamp) }}</div>
              <div class="log-action">{{ log.action }}</div>
              <div class="log-details">{{ formatLogDetails(log.details) }}</div>
            </div>
            <div v-if="logs.length === 0" class="no-data">暂无日志</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, onUnmounted } from 'vue'
import ControllerPanel from '../components/ControllerPanel.vue'

export default {
  name: 'ControllerPage',
  components: {
    ControllerPanel
  },
  setup() {
    // 状态
    const isLive = ref(false)
    const currentStreamId = ref('')
    const starting = ref(false)
    const stopping = ref(false)
    
    // 数据
    const stats = ref({
      total_danmaku: 0,
      auto_replies: 0,
      violations_handled: 0,
      alerts_triggered: 0
    })
    
    const currentEmotion = ref(null)
    const suggestions = ref([])
    const alerts = ref([])
    const danmakuMessages = ref([])
    const logs = ref([])
    
    // WebSocket
    let ws = null
    let pollingTimer = null
    
    // API 基础 URL
    const API_BASE = '/api/controller'
    
    // 开始直播
    const startLive = async () => {
      starting.value = true
      try {
        const response = await fetch(`${API_BASE}/live/start`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            stream_id: 'stream_' + Date.now(),
            room_name: '直播间'
          })
        })
        
        const result = await response.json()
        if (result.code === 0) {
          isLive.value = true
          currentStreamId.value = result.data.stream_id
          startPolling()
          connectWebSocket()
        }
      } catch (error) {
        console.error('启动失败:', error)
        alert('启动失败：' + error.message)
      } finally {
        starting.value = false
      }
    }
    
    // 停止直播
    const stopLive = async () => {
      stopping.value = true
      try {
        const response = await fetch(`${API_BASE}/live/stop`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            stream_id: currentStreamId.value
          })
        })
        
        const result = await response.json()
        if (result.code === 0) {
          isLive.value = false
          stopPolling()
          if (ws) {
            ws.close()
            ws = null
          }
        }
      } catch (error) {
        console.error('停止失败:', error)
      } finally {
        stopping.value = false
      }
    }
    
    // 获取状态
    const fetchStatus = async () => {
      try {
        const response = await fetch(`${API_BASE}/live/status`)
        const result = await response.json()
        
        if (result.code === 0) {
          const data = result.data
          isLive.value = data.is_live
          currentStreamId.value = data.stream_id || ''
          stats.value = data.stats || {}
          currentEmotion.value = data.current_emotion
          suggestions.value = data.recent_suggestions || []
          alerts.value = data.recent_alerts || []
          logs.value = data.recent_logs || []
        }
      } catch (error) {
        console.error('获取状态失败:', error)
      }
    }
    
    // 获取弹幕
    const fetchDanmaku = async () => {
      // 实际场景中应该通过 WebSocket 接收
      // 这里简化处理
    }
    
    // 开始轮询
    const startPolling = () => {
      fetchStatus()
      pollingTimer = setInterval(fetchStatus, 3000)
    }
    
    // 停止轮询
    const stopPolling = () => {
      if (pollingTimer) {
        clearInterval(pollingTimer)
        pollingTimer = null
      }
    }
    
    // 连接 WebSocket
    const connectWebSocket = () => {
      const wsUrl = `ws://${window.location.host}${API_BASE}/ws`
      ws = new WebSocket(wsUrl)
      
      ws.onopen = () => {
        console.log('WebSocket 已连接')
        ws.send(JSON.stringify({
          type: 'subscribe',
          subscribe_to: ['status', 'danmaku', 'alerts']
        }))
      }
      
      ws.onmessage = (event) => {
        const data = JSON.parse(event.data)
        if (data.type === 'status_update') {
          // 更新状态
          const statusData = data.data
          stats.value = statusData.stats || {}
          currentEmotion.value = statusData.current_emotion
          suggestions.value = statusData.recent_suggestions || []
        }
      }
      
      ws.onclose = () => {
        console.log('WebSocket 已断开')
      }
      
      ws.onerror = (error) => {
        console.error('WebSocket 错误:', error)
      }
    }
    
    // 格式化时间
    const formatTime = (timestamp) => {
      if (!timestamp) return ''
      const date = new Date(timestamp * 1000)
      return date.toLocaleTimeString('zh-CN', { 
        hour: '2-digit', 
        minute: '2-digit', 
        second: '2-digit' 
      })
    }
    
    // 获取建议类型文本
    const getSuggestionTypeText = (type) => {
      const map = {
        'promotion': '🛒 促销',
        'interaction': '🎮 互动',
        'break': '☕ 休息',
        'content': '📺 内容'
      }
      return map[type] || type
    }
    
    // 获取时机文本
    const getTimingText = (timing) => {
      const map = {
        'now': '立即',
        'soon': '尽快',
        'later': '稍后'
      }
      return map[timing] || timing
    }
    
    // 格式化日志详情
    const formatLogDetails = (details) => {
      if (!details) return ''
      return Object.entries(details)
        .map(([key, value]) => `${key}: ${value}`)
        .join(', ')
    }
    
    // 生命周期
    onMounted(() => {
      // 初始获取状态
      fetchStatus()
    })
    
    onUnmounted(() => {
      stopPolling()
      if (ws) {
        ws.close()
      }
    })
    
    return {
      isLive,
      currentStreamId,
      starting,
      stopping,
      stats,
      currentEmotion,
      suggestions,
      alerts,
      danmakuMessages,
      logs,
      startLive,
      stopLive,
      formatTime,
      getSuggestionTypeText,
      getTimingText,
      formatLogDetails
    }
  }
}
</script>

<style scoped>
.controller-page {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #1a1a2e;
  color: #eee;
  font-family: 'Microsoft YaHei', sans-serif;
}

/* 状态栏 */
.status-bar {
  display: flex;
  align-items: center;
  padding: 15px 20px;
  background: #16213e;
  border-bottom: 2px solid #0f3460;
  gap: 30px;
  flex-wrap: wrap;
}

.status-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.status-label {
  color: #888;
  font-size: 14px;
}

.status-value {
  font-weight: bold;
  font-size: 16px;
}

.status-value.live {
  color: #ff4757;
}

.status-value.offline {
  color: #7f8c8d;
}

.action-buttons {
  margin-left: auto;
}

.btn {
  padding: 10px 25px;
  border: none;
  border-radius: 5px;
  font-size: 15px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-start {
  background: #2ed573;
  color: white;
}

.btn-start:hover:not(:disabled) {
  background: #26af61;
}

.btn-stop {
  background: #ff4757;
  color: white;
}

.btn-stop:hover:not(:disabled) {
  background: #ff3344;
}

/* 主内容区 */
.main-content {
  display: flex;
  flex: 1;
  overflow: hidden;
  gap: 20px;
  padding: 20px;
}

.left-panel, .right-panel {
  display: flex;
  flex-direction: column;
  gap: 20px;
  overflow-y: auto;
}

.left-panel {
  flex: 1;
  min-width: 400px;
}

.right-panel {
  flex: 1.5;
  min-width: 500px;
}

/* 面板 */
.panel {
  background: #16213e;
  border-radius: 10px;
  padding: 15px;
  border: 1px solid #0f3460;
}

.panel-title {
  margin: 0 0 15px 0;
  font-size: 16px;
  color: #fff;
  border-bottom: 1px solid #0f3460;
  padding-bottom: 10px;
}

.no-data {
  text-align: center;
  color: #666;
  padding: 30px;
}

/* 情绪图表 */
.emotion-bars {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.emotion-bar {
  display: flex;
  align-items: center;
  gap: 10px;
}

.bar-label {
  width: 50px;
  font-size: 14px;
  color: #aaa;
}

.bar-container {
  flex: 1;
  height: 20px;
  background: #0f3460;
  border-radius: 10px;
  overflow: hidden;
}

.bar-fill {
  height: 100%;
  transition: width 0.5s ease;
}

.bar-fill.positive {
  background: linear-gradient(90deg, #2ed573, #7bed9f);
}

.bar-fill.neutral {
  background: linear-gradient(90deg, #70a1ff, #1e90ff);
}

.bar-fill.negative {
  background: linear-gradient(90deg, #ff4757, #ff6b81);
}

.bar-fill.excited {
  background: linear-gradient(90deg, #ffa502, #ff7f50);
}

.bar-value {
  width: 50px;
  text-align: right;
  font-size: 13px;
  color: #fff;
}

/* 建议列表 */
.suggestions-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 300px;
  overflow-y: auto;
}

.suggestion-item {
  background: #0f3460;
  border-radius: 8px;
  padding: 12px;
  border-left: 4px solid #70a1ff;
}

.suggestion-item.priority-5 {
  border-left-color: #ff4757;
  background: #1a0a0a;
}

.suggestion-item.priority-4 {
  border-left-color: #ffa502;
}

.suggestion-item.priority-3 {
  border-left-color: #2ed573;
}

.suggestion-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
}

.suggestion-type {
  font-weight: bold;
  font-size: 14px;
}

.suggestion-timing {
  font-size: 12px;
  padding: 2px 8px;
  background: #16213e;
  border-radius: 10px;
  color: #aaa;
}

.suggestion-reason {
  font-size: 13px;
  color: #ccc;
  margin-bottom: 6px;
}

.suggestion-content {
  font-size: 14px;
  color: #fff;
  background: #16213e;
  padding: 8px;
  border-radius: 5px;
}

/* 预警列表 */
.alerts-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  max-height: 250px;
  overflow-y: auto;
}

.alert-item {
  background: #0f3460;
  border-radius: 8px;
  padding: 10px;
  border-left: 4px solid #70a1ff;
}

.alert-item.info {
  border-left-color: #70a1ff;
}

.alert-item.warning {
  border-left-color: #ffa502;
  background: #1a1200;
}

.alert-item.critical {
  border-left-color: #ff4757;
  background: #1a0a0a;
}

.alert-time {
  font-size: 12px;
  color: #888;
  margin-bottom: 5px;
}

.alert-content {
  display: flex;
  gap: 8px;
  align-items: center;
  margin-bottom: 5px;
}

.alert-type {
  font-size: 12px;
  padding: 2px 6px;
  background: #16213e;
  border-radius: 4px;
  color: #aaa;
}

.alert-message {
  font-size: 14px;
  color: #fff;
}

.alert-user {
  font-size: 12px;
  color: #888;
}

/* 弹幕列表 */
.danmaku-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 400px;
  overflow-y: auto;
}

.danmaku-item {
  background: #0f3460;
  border-radius: 8px;
  padding: 10px;
  display: flex;
  gap: 10px;
  align-items: center;
}

.danmaku-item.highlight {
  background: #1a1a3e;
  border: 1px solid #70a1ff;
}

.danmaku-user {
  display: flex;
  align-items: center;
  gap: 5px;
  min-width: 100px;
}

.username {
  font-weight: bold;
  font-size: 13px;
  color: #70a1ff;
}

.badge {
  font-size: 10px;
  padding: 1px 4px;
  border-radius: 3px;
  font-weight: bold;
}

.badge.mod {
  background: #ff4757;
  color: white;
}

.badge.fan {
  background: #ffa502;
  color: white;
}

.danmaku-content {
  flex: 1;
  font-size: 14px;
  color: #fff;
}

.danmaku-time {
  font-size: 11px;
  color: #888;
  min-width: 60px;
  text-align: right;
}

/* 日志列表 */
.logs-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 300px;
  overflow-y: auto;
}

.log-item {
  background: #0f3460;
  border-radius: 8px;
  padding: 10px;
  font-size: 13px;
}

.log-time {
  color: #888;
  font-size: 11px;
  margin-bottom: 5px;
}

.log-action {
  font-weight: bold;
  color: #70a1ff;
  margin-bottom: 5px;
}

.log-details {
  color: #aaa;
  font-size: 12px;
  font-family: monospace;
}

/* 滚动条 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #0f3460;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: #1a5f9e;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #247cc4;
}
</style>
