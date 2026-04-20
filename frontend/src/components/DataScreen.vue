<template>
  <div class="data-screen" :class="[`layout-${layout}`, { 'fullscreen': isFullscreen }]">
    <!-- 头部 -->
    <header class="screen-header">
      <div class="header-left">
        <h1 class="screen-title">
          <span class="live-indicator" :class="{ active: isLive }">●</span>
          LiveMirror 数据大屏
        </h1>
        <span class="update-time">最后更新：{{ lastUpdateTime }}</span>
      </div>
      <div class="header-right">
        <button class="btn btn-icon" @click="toggleLayout" title="切换布局">
          <svg viewBox="0 0 24 24" width="20" height="20">
            <rect x="3" y="3" width="7" height="7" />
            <rect x="14" y="3" width="7" height="7" />
            <rect x="3" y="14" width="7" height="7" />
            <rect x="14" y="14" width="7" height="7" />
          </svg>
        </button>
        <button class="btn btn-icon" @click="toggleFullscreen" title="全屏">
          <svg viewBox="0 0 24 24" width="20" height="20">
            <path d="M7 14H5v5h5v-2H7v-3zm-2-4h2V7h3V5H5v5zm12 7h-3v2h5v-5h-2v3zM14 5v2h3v3h2V5h-5z"/>
          </svg>
        </button>
        <button class="btn btn-icon" @click="exportData" title="导出数据">
          <svg viewBox="0 0 24 24" width="20" height="20">
            <path d="M19 9h-4V3H9v6H5l7 7 7-7zM5 18v2h14v-2H5z"/>
          </svg>
        </button>
        <button class="btn btn-icon" @click="screenshot" title="截图">
          <svg viewBox="0 0 24 24" width="20" height="20">
            <path d="M9 2L7.17 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2h-3.17L15 2H9zm6 15c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5z"/>
          </svg>
        </button>
      </div>
    </header>

    <!-- 主要内容区 -->
    <main class="screen-content">
      <!-- 布局 1: 默认三栏 -->
      <template v-if="layout === 'default'">
        <div class="grid-3">
          <!-- GMV 卡片 -->
          <div class="metric-card primary">
            <div class="metric-icon">💰</div>
            <div class="metric-info">
              <span class="metric-label">总成交额 (GMV)</span>
              <span class="metric-value">¥{{ formatNumber(data.gmv) }}</span>
              <span class="metric-trend positive">↑ 12.5%</span>
            </div>
          </div>
          
          <!-- 观看人数 -->
          <div class="metric-card">
            <div class="metric-icon">👥</div>
            <div class="metric-info">
              <span class="metric-label">当前观看</span>
              <span class="metric-value">{{ formatNumber(data.viewers) }}</span>
              <span class="metric-sub">峰值：{{ formatNumber(data.peak_viewers) }}</span>
            </div>
          </div>
          
          <!-- 订单数 -->
          <div class="metric-card">
            <div class="metric-icon">📦</div>
            <div class="metric-info">
              <span class="metric-label">订单数</span>
              <span class="metric-value">{{ formatNumber(data.orders) }}</span>
              <span class="metric-sub">转化率：{{ data.conversion_rate }}%</span>
            </div>
          </div>
          
          <!-- 互动数据 -->
          <div class="metric-card wide">
            <div class="metric-row">
              <div class="metric-item">
                <span class="metric-icon">❤️</span>
                <span class="metric-value">{{ formatNumber(data.likes) }}</span>
                <span class="metric-label">点赞</span>
              </div>
              <div class="metric-item">
                <span class="metric-icon">💬</span>
                <span class="metric-value">{{ formatNumber(data.comments) }}</span>
                <span class="metric-label">评论</span>
              </div>
              <div class="metric-item">
                <span class="metric-icon">🔗</span>
                <span class="metric-value">{{ formatNumber(data.shares) }}</span>
                <span class="metric-label">分享</span>
              </div>
            </div>
          </div>
          
          <!-- 平均观看时长 -->
          <div class="metric-card">
            <div class="metric-icon">⏱️</div>
            <div class="metric-info">
              <span class="metric-label">平均观看时长</span>
              <span class="metric-value">{{ formatTime(data.avg_watch_time) }}</span>
            </div>
          </div>
        </div>
      </template>

      <!-- 布局 2: GMV 焦点 -->
      <template v-else-if="layout === 'focus-gmv'">
        <div class="grid-focus">
          <div class="focus-card gmv-focus">
            <span class="focus-label">总成交额</span>
            <span class="focus-value">¥{{ formatNumber(data.gmv) }}</span>
            <span class="focus-sub">实时增长中</span>
          </div>
          <div class="side-metrics">
            <div class="side-metric">
              <span class="label">观看</span>
              <span class="value">{{ formatNumber(data.viewers) }}</span>
            </div>
            <div class="side-metric">
              <span class="label">订单</span>
              <span class="value">{{ formatNumber(data.orders) }}</span>
            </div>
            <div class="side-metric">
              <span class="label">转化率</span>
              <span class="value">{{ data.conversion_rate }}%</span>
            </div>
          </div>
        </div>
      </template>

      <!-- 布局 3: 互动优先 -->
      <template v-else-if="layout === 'interaction'">
        <div class="grid-interaction">
          <div class="interaction-card">
            <div class="interaction-icon">❤️</div>
            <div class="interaction-value">{{ formatNumber(data.likes) }}</div>
            <div class="interaction-label">点赞</div>
          </div>
          <div class="interaction-card">
            <div class="interaction-icon">💬</div>
            <div class="interaction-value">{{ formatNumber(data.comments) }}</div>
            <div class="interaction-label">评论</div>
          </div>
          <div class="interaction-card">
            <div class="interaction-icon">🔗</div>
            <div class="interaction-value">{{ formatNumber(data.shares) }}</div>
            <div class="interaction-label">分享</div>
          </div>
          <div class="interaction-card">
            <div class="interaction-icon">👥</div>
            <div class="interaction-value">{{ formatNumber(data.viewers) }}</div>
            <div class="interaction-label">观看</div>
          </div>
        </div>
      </template>

      <!-- 布局 4: 极简模式 -->
      <template v-else-if="layout === 'minimal'">
        <div class="grid-minimal">
          <div class="minimal-item">
            <span class="minimal-value">¥{{ formatNumber(data.gmv) }}</span>
            <span class="minimal-label">GMV</span>
          </div>
          <div class="minimal-item">
            <span class="minimal-value">{{ formatNumber(data.viewers) }}</span>
            <span class="minimal-label">观看</span>
          </div>
          <div class="minimal-item">
            <span class="minimal-value">{{ formatNumber(data.orders) }}</span>
            <span class="minimal-label">订单</span>
          </div>
        </div>
      </template>
    </main>

    <!-- 底部状态栏 -->
    <footer class="screen-footer">
      <div class="connection-status" :class="{ connected: isConnected }">
        <span class="status-dot"></span>
        <span>{{ isConnected ? '实时连接中' : '未连接' }}</span>
      </div>
      <div class="screen-info">
        <span>布局：{{ layoutNames[layout] }}</span>
        <span v-if="isFullscreen">全屏模式</span>
      </div>
    </footer>
  </div>
</template>

<script>
export default {
  name: 'DataScreen',
  props: {
    initialLayout: {
      type: String,
      default: 'default'
    }
  },
  data() {
    return {
      layout: this.initialLayout,
      layoutNames: {
        'default': '默认布局',
        'focus-gmv': 'GMV 焦点',
        'interaction': '互动优先',
        'minimal': '极简模式'
      },
      isFullscreen: false,
      isConnected: false,
      isLive: true,
      lastUpdateTime: '--:--:--',
      websocket: null,
      data: {
        gmv: 0,
        viewers: 0,
        likes: 0,
        comments: 0,
        shares: 0,
        orders: 0,
        conversion_rate: 0,
        avg_watch_time: 0,
        peak_viewers: 0
      }
    }
  },
  mounted() {
    this.connectWebSocket()
    this.setupFullscreenListener()
  },
  beforeUnmount() {
    this.disconnectWebSocket()
  },
  methods: {
    connectWebSocket() {
      const wsUrl = `ws://${window.location.host}/api/dashboard/ws`
      this.websocket = new WebSocket(wsUrl)
      
      this.websocket.onopen = () => {
        console.log('[DataScreen] WebSocket connected')
        this.isConnected = true
        this.updateTime()
      }
      
      this.websocket.onmessage = (event) => {
        const message = JSON.parse(event.data)
        if (message.type === 'update' || message.type === 'reset') {
          this.data = { ...this.data, ...message.data }
          this.updateTime()
        }
      }
      
      this.websocket.onclose = () => {
        console.log('[DataScreen] WebSocket disconnected')
        this.isConnected = false
        // 尝试重连
        setTimeout(() => this.connectWebSocket(), 3000)
      }
      
      this.websocket.onerror = (error) => {
        console.error('[DataScreen] WebSocket error:', error)
      }
    },
    
    disconnectWebSocket() {
      if (this.websocket) {
        this.websocket.close()
        this.websocket = null
      }
    },
    
    toggleLayout() {
      const layouts = ['default', 'focus-gmv', 'interaction', 'minimal']
      const currentIndex = layouts.indexOf(this.layout)
      this.layout = layouts[(currentIndex + 1) % layouts.length]
      this.$emit('layout-change', this.layout)
    },
    
    toggleFullscreen() {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen().then(() => {
          this.isFullscreen = true
          this.$emit('fullscreen-change', true)
        }).catch(err => {
          console.error('Fullscreen error:', err)
        })
      } else {
        document.exitFullscreen().then(() => {
          this.isFullscreen = false
          this.$emit('fullscreen-change', false)
        })
      }
    },
    
    setupFullscreenListener() {
      document.addEventListener('fullscreenchange', () => {
        this.isFullscreen = !!document.fullscreenElement
        this.$emit('fullscreen-change', this.isFullscreen)
      })
    },
    
    exportData() {
      const format = 'json'
      const dataStr = JSON.stringify(this.data, null, 2)
      const blob = new Blob([dataStr], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `dashboard_export_${new Date().getTime()}.json`
      a.click()
      URL.revokeObjectURL(url)
      this.$emit('export', { format, data: this.data })
    },
    
    screenshot() {
      this.$emit('screenshot')
    },
    
    updateTime() {
      const now = new Date()
      this.lastUpdateTime = now.toLocaleTimeString('zh-CN')
    },
    
    formatNumber(num) {
      if (num >= 10000) {
        return (num / 10000).toFixed(1) + '万'
      }
      return num.toLocaleString('zh-CN')
    },
    
    formatTime(seconds) {
      const mins = Math.floor(seconds / 60)
      const secs = Math.floor(seconds % 60)
      return `${mins}分${secs}秒`
    }
  }
}
</script>

<style scoped>
.data-screen {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  color: #fff;
  overflow: hidden;
}

.data-screen.fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9999;
}

/* 头部 */
.screen-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background: rgba(255, 255, 255, 0.05);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.screen-title {
  font-size: 1.5rem;
  font-weight: bold;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.live-indicator {
  color: #666;
  font-size: 0.8rem;
}

.live-indicator.active {
  color: #ff4757;
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.update-time {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.6);
  margin-left: 1rem;
}

.header-right {
  display: flex;
  gap: 0.5rem;
}

.btn {
  background: rgba(255, 255, 255, 0.1);
  border: none;
  color: #fff;
  padding: 0.5rem;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.btn-icon {
  display: flex;
  align-items: center;
  justify-content: center;
}

/* 内容区 */
.screen-content {
  flex: 1;
  padding: 2rem;
  overflow-y: auto;
}

/* 默认布局 */
.grid-3 {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.metric-card {
  background: rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  transition: transform 0.2s, box-shadow 0.2s;
}

.metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 16px rgba(0, 0, 0, 0.3);
}

.metric-card.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  grid-column: span 2;
}

.metric-card.wide {
  grid-column: span 3;
}

.metric-icon {
  font-size: 2.5rem;
}

.metric-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.metric-label {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.7);
}

.metric-value {
  font-size: 2rem;
  font-weight: bold;
}

.metric-trend {
  font-size: 0.85rem;
}

.metric-trend.positive {
  color: #2ed573;
}

.metric-sub {
  font-size: 0.85rem;
  color: rgba(255, 255, 255, 0.6);
}

.metric-row {
  display: flex;
  justify-content: space-around;
  width: 100%;
}

.metric-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

/* GMV 焦点布局 */
.grid-focus {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 2rem;
  height: 100%;
}

.focus-card {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  border-radius: 16px;
  padding: 3rem;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
  text-align: center;
}

.focus-label {
  font-size: 1.5rem;
  opacity: 0.9;
}

.focus-value {
  font-size: 5rem;
  font-weight: bold;
  margin: 1rem 0;
}

.focus-sub {
  font-size: 1.2rem;
  opacity: 0.8;
}

.side-metrics {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.side-metric {
  background: rgba(255, 255, 255, 0.08);
  border-radius: 12px;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
}

.side-metric .label {
  font-size: 1rem;
  color: rgba(255, 255, 255, 0.7);
}

.side-metric .value {
  font-size: 2.5rem;
  font-weight: bold;
}

/* 互动布局 */
.grid-interaction {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 2rem;
}

.interaction-card {
  background: rgba(255, 255, 255, 0.08);
  border-radius: 16px;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.interaction-icon {
  font-size: 4rem;
}

.interaction-value {
  font-size: 3rem;
  font-weight: bold;
}

.interaction-label {
  font-size: 1.2rem;
  color: rgba(255, 255, 255, 0.7);
}

/* 极简布局 */
.grid-minimal {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 3rem;
}

.minimal-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.minimal-value {
  font-size: 4rem;
  font-weight: bold;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.minimal-label {
  font-size: 1.5rem;
  color: rgba(255, 255, 255, 0.7);
}

/* 底部 */
.screen-footer {
  display: flex;
  justify-content: space-between;
  padding: 1rem 2rem;
  background: rgba(255, 255, 255, 0.05);
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  font-size: 0.9rem;
}

.connection-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #666;
}

.connection-status.connected .status-dot {
  background: #2ed573;
  animation: pulse 2s infinite;
}

.screen-info {
  display: flex;
  gap: 1.5rem;
  color: rgba(255, 255, 255, 0.6);
}

/* 响应式 */
@media (max-width: 1200px) {
  .grid-3 {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .metric-card.primary,
  .metric-card.wide {
    grid-column: span 1;
  }
}

@media (max-width: 768px) {
  .grid-3,
  .grid-interaction,
  .grid-minimal {
    grid-template-columns: 1fr;
  }
  
  .grid-focus {
    grid-template-columns: 1fr;
  }
  
  .screen-header {
    flex-direction: column;
    gap: 1rem;
  }
  
  .screen-footer {
    flex-direction: column;
    gap: 0.5rem;
    text-align: center;
  }
}
</style>
