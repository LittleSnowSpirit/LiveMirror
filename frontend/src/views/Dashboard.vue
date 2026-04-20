<template>
  <div class="dashboard-page">
    <!-- 数据大屏组件 -->
    <DataScreen
      ref="dataScreen"
      :initial-layout="currentLayout"
      @layout-change="handleLayoutChange"
      @fullscreen-change="handleFullscreenChange"
      @export="handleExport"
      @screenshot="handleScreenshot"
    />
    
    <!-- 控制面板（非全屏时显示） -->
    <div class="control-panel" v-show="!isFullscreen">
      <div class="panel-section">
        <h3>布局选择</h3>
        <div class="layout-options">
          <button
            v-for="(layout, key) in layouts"
            :key="key"
            :class="['layout-btn', { active: currentLayout === key }]"
            @click="setLayout(key)"
          >
            <span class="layout-icon">{{ layout.icon }}</span>
            <span class="layout-name">{{ layout.name }}</span>
          </button>
        </div>
      </div>
      
      <div class="panel-section">
        <h3>实时数据控制</h3>
        <div class="control-buttons">
          <button class="control-btn" @click="toggleAutoUpdate">
            {{ autoUpdate ? '⏸️ 暂停更新' : '▶️ 开始更新' }}
          </button>
          <button class="control-btn danger" @click="resetData">
            🔄 重置数据
          </button>
          <button class="control-btn" @click="exportData">
            📥 导出数据
          </button>
          <button class="control-btn" @click="takeScreenshot">
            📸 截图
          </button>
        </div>
      </div>
      
      <div class="panel-section">
        <h3>当前数据</h3>
        <div class="data-preview">
          <div class="data-row">
            <span class="data-label">GMV:</span>
            <span class="data-value">¥{{ formatNumber(currentData.gmv) }}</span>
          </div>
          <div class="data-row">
            <span class="data-label">观看:</span>
            <span class="data-value">{{ formatNumber(currentData.viewers) }}</span>
          </div>
          <div class="data-row">
            <span class="data-label">订单:</span>
            <span class="data-value">{{ formatNumber(currentData.orders) }}</span>
          </div>
          <div class="data-row">
            <span class="data-label">点赞:</span>
            <span class="data-value">{{ formatNumber(currentData.likes) }}</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 截图提示 -->
    <div class="screenshot-toast" v-if="showScreenshotToast">
      ✅ 截图已保存
    </div>
  </div>
</template>

<script>
import DataScreen from '@/components/DataScreen.vue'

export default {
  name: 'DashboardPage',
  components: {
    DataScreen
  },
  data() {
    return {
      currentLayout: 'default',
      layouts: {
        'default': { name: '默认布局', icon: '▦' },
        'focus-gmv': { name: 'GMV 焦点', icon: '💰' },
        'interaction': { name: '互动优先', icon: '❤️' },
        'minimal': { name: '极简模式', icon: '◫' }
      },
      isFullscreen: false,
      autoUpdate: true,
      showScreenshotToast: false,
      currentData: {
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
    this.loadSavedLayout()
    this.pollData()
  },
  methods: {
    setLayout(layout) {
      this.currentLayout = layout
      this.saveLayout(layout)
      // 触发组件切换
      if (this.$refs.dataScreen) {
        this.$refs.dataScreen.layout = layout
      }
    },
    
    handleLayoutChange(layout) {
      this.currentLayout = layout
      this.saveLayout(layout)
    },
    
    handleFullscreenChange(fullscreen) {
      this.isFullscreen = fullscreen
    },
    
    handleExport(event) {
      console.log('[Dashboard] Data exported:', event)
    },
    
    handleScreenshot() {
      this.takeScreenshot()
    },
    
    toggleAutoUpdate() {
      this.autoUpdate = !this.autoUpdate
      // 可以通过 WebSocket 发送控制命令
      this.notifyWebSocket()
    },
    
    resetData() {
      if (confirm('确定要重置所有数据吗？')) {
        fetch('/api/dashboard/data/reset', { method: 'POST' })
          .then(res => res.json())
          .then(data => {
            console.log('[Dashboard] Data reset:', data)
          })
          .catch(err => {
            console.error('[Dashboard] Reset error:', err)
          })
      }
    },
    
    exportData() {
      const format = 'json'
      fetch(`/api/dashboard/export?format=${format}`)
        .then(res => res.json())
        .then(data => {
          if (data.success) {
            const blob = new Blob([JSON.stringify(data.data, null, 2)], { 
              type: 'application/json' 
            })
            const url = URL.createObjectURL(blob)
            const a = document.createElement('a')
            a.href = url
            a.download = data.filename
            a.click()
            URL.revokeObjectURL(url)
          }
        })
        .catch(err => {
          console.error('[Dashboard] Export error:', err)
        })
    },
    
    takeScreenshot() {
      // 使用 html2canvas 截图
      import('html2canvas').then(({ default: html2canvas }) => {
        const element = document.querySelector('.data-screen')
        html2canvas(element, {
          backgroundColor: '#1a1a2e',
          scale: 2
        }).then(canvas => {
          const link = document.createElement('a')
          link.download = `dashboard_screenshot_${new Date().getTime()}.png`
          link.href = canvas.toDataURL('image/png')
          link.click()
          
          // 显示提示
          this.showScreenshotToast = true
          setTimeout(() => {
            this.showScreenshotToast = false
          }, 2000)
        })
      }).catch(err => {
        console.error('[Dashboard] Screenshot error:', err)
        alert('截图失败，请安装 html2canvas 依赖')
      })
    },
    
    saveLayout(layout) {
      localStorage.setItem('dashboard_layout', layout)
    },
    
    loadSavedLayout() {
      const saved = localStorage.getItem('dashboard_layout')
      if (saved && this.layouts[saved]) {
        this.currentLayout = saved
      }
    },
    
    notifyWebSocket() {
      // 可以通过 WebSocket 发送控制命令
      if (this.$refs.dataScreen && this.$refs.dataScreen.websocket) {
        this.$refs.dataScreen.websocket.send(JSON.stringify({
          type: this.autoUpdate ? 'start_update' : 'stop_update'
        }))
      }
    },
    
    pollData() {
      // 定期轮询获取最新数据（作为 WebSocket 的备用）
      setInterval(() => {
        fetch('/api/dashboard/data')
          .then(res => res.json())
          .then(response => {
            if (response.success) {
              this.currentData = response.data
            }
          })
          .catch(err => {
            console.error('[Dashboard] Poll error:', err)
          })
      }, 5000)
    },
    
    formatNumber(num) {
      if (num >= 10000) {
        return (num / 10000).toFixed(1) + '万'
      }
      return num.toLocaleString('zh-CN')
    }
  }
}
</script>

<style scoped>
.dashboard-page {
  width: 100%;
  height: 100vh;
  position: relative;
  overflow: hidden;
}

.control-panel {
  position: fixed;
  bottom: 80px;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(26, 26, 46, 0.95);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 16px;
  padding: 1.5rem;
  display: flex;
  gap: 2rem;
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
  z-index: 100;
  max-width: 90%;
}

.panel-section {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.panel-section h3 {
  margin: 0;
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.7);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.layout-options {
  display: flex;
  gap: 0.5rem;
}

.layout-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
  padding: 0.75rem 1rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  color: #fff;
  cursor: pointer;
  transition: all 0.2s;
}

.layout-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.layout-btn.active {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-color: transparent;
}

.layout-icon {
  font-size: 1.2rem;
}

.layout-name {
  font-size: 0.75rem;
}

.control-buttons {
  display: flex;
  gap: 0.5rem;
}

.control-btn {
  padding: 0.75rem 1rem;
  background: rgba(255, 255, 255, 0.1);
  border: none;
  border-radius: 6px;
  color: #fff;
  cursor: pointer;
  font-size: 0.85rem;
  transition: all 0.2s;
}

.control-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.control-btn.danger:hover {
  background: rgba(239, 68, 68, 0.8);
}

.data-preview {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  min-width: 150px;
}

.data-row {
  display: flex;
  justify-content: space-between;
  gap: 1rem;
}

.data-label {
  color: rgba(255, 255, 255, 0.6);
  font-size: 0.85rem;
}

.data-value {
  color: #fff;
  font-weight: 600;
  font-size: 0.9rem;
}

.screenshot-toast {
  position: fixed;
  top: 2rem;
  left: 50%;
  transform: translateX(-50%);
  background: rgba(46, 213, 115, 0.9);
  color: #fff;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  font-size: 0.9rem;
  animation: slideDown 0.3s ease-out;
  z-index: 1000;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateX(-50%) translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(-50%) translateY(0);
  }
}

/* 响应式 */
@media (max-width: 768px) {
  .control-panel {
    flex-direction: column;
    bottom: 70px;
    width: 90%;
    max-height: 50vh;
    overflow-y: auto;
  }
  
  .layout-options {
    flex-wrap: wrap;
  }
  
  .control-buttons {
    flex-wrap: wrap;
  }
}
</style>
