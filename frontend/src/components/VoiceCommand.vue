<template>
  <div class="voice-command" :class="{ 'listening': isListening, 'offline': isOffline }">
    <!-- 语音按钮 -->
    <button 
      class="voice-btn"
      @click="handleToggle"
      :title="isListening ? '停止语音' : '开始语音'"
      :disabled="!isSupported"
    >
      <span class="voice-icon">
        <svg v-if="!isListening" viewBox="0 0 24 24" width="24" height="24">
          <path fill="currentColor" d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
          <path fill="currentColor" d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/>
        </svg>
        <svg v-else viewBox="0 0 24 24" width="24" height="24">
          <path fill="currentColor" d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/>
          <path fill="currentColor" d="M19.07 4.93L17.66 6.34C18.5 7.5 19 8.93 19 10.5c0 4.08-3.05 7.44-7 7.93v3.07h2v-3.07c.61-.07 1.21-.2 1.78-.38l2.92 2.92 1.41-1.41-2.92-2.92c.18-.57.31-1.17.38-1.78H21c-.5-4.39-4.08-7.97-8.47-8.47V5c0-.61.07-1.21.25-1.78l-2.22-2.22c-.18.57-.25 1.17-.25 1.78v1.54c-1.96.25-3.68 1.23-4.93 2.65L3.93 4.93 2.52 6.34l10.6 10.6 1.41-1.41L3.93 4.93z"/>
        </svg>
      </span>
      <span class="offline-badge" v-if="isOffline">离线</span>
    </button>

    <!-- 状态指示器 -->
    <div class="voice-status" v-if="isListening">
      <div class="waveform">
        <span class="wave" v-for="n in 5" :key="n" :style="{ animationDelay: `${n * 0.1}s` }"></span>
      </div>
      <span class="status-text">{{ statusText }}</span>
    </div>

    <!-- 最近命令历史 -->
    <div class="command-history" v-if="showHistory && commandHistory.length > 0">
      <div class="history-header">
        <span>最近命令</span>
        <button class="clear-btn" @click="clearHistory">清除</button>
      </div>
      <ul class="history-list">
        <li v-for="(cmd, index) in commandHistory" :key="index" class="history-item">
          <span class="history-time">{{ formatTime(cmd.timestamp) }}</span>
          <span class="history-input">{{ cmd.input }}</span>
          <span class="history-command">{{ cmd.command.key }}</span>
        </li>
      </ul>
    </div>

    <!-- 帮助提示 -->
    <div class="voice-help" v-if="showHelp">
      <div class="help-header">
        <h4>语音命令</h4>
        <button class="close-btn" @click="$emit('close-help')">✕</button>
      </div>
      <div class="help-content">
        <div class="help-section" v-for="(category, catKey) in commands" :key="catKey">
          <h5>{{ getCategoryName(catKey) }}</h5>
          <ul>
            <li v-for="(cmd, cmdKey) in category" :key="cmdKey">
              <strong>{{ cmd.keywords[0] }}</strong>
              <span class="help-desc">{{ cmd.description }}</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import {
  startListening,
  stopListening,
  toggleListening,
  onCommand,
  onResult,
  onError,
  getStatus,
  getCommands,
  isSupported,
  isListening as checkIsListening
} from '../utils/voice_control'

export default {
  name: 'VoiceCommand',
  props: {
    showHistory: {
      type: Boolean,
      default: false
    },
    showHelp: {
      type: Boolean,
      default: false
    },
    autoStart: {
      type: Boolean,
      default: false
    }
  },
  data() {
    return {
      isSupported: false,
      isListening: false,
      isOffline: false,
      statusText: '正在聆听...',
      commandHistory: [],
      commands: {}
    }
  },
  mounted() {
    this.init()
    this.setupEventListeners()
    
    if (this.autoStart) {
      this.$nextTick(() => {
        startListening()
      })
    }
  },
  beforeUnmount() {
    this.cleanup()
  },
  methods: {
    init() {
      this.isSupported = isSupported()
      this.commands = getCommands()
      this.updateStatus()
    },

    setupEventListeners() {
      // 语音命令回调
      onCommand((command) => {
        this.$emit('command', command)
        this.executeCommand(command)
      })

      onResult((transcript) => {
        this.$emit('result', transcript)
        this.statusText = `识别：${transcript}`
      })

      onError((error) => {
        this.$emit('error', error)
        console.error('语音识别错误:', error)
      })

      // 视觉反馈事件
      window.addEventListener('voice-visual-feedback', this.handleVisualFeedback)
    },

    handleVisualFeedback(event) {
      const { type, data } = event.detail
      switch (type) {
        case 'listening':
          this.statusText = '正在聆听...'
          break
        case 'success':
          this.statusText = `✓ ${data.command}`
          break
        case 'error':
          this.statusText = `✗ ${data.input}`
          break
        case 'offline':
          this.statusText = '离线模式'
          break
      }
    },

    handleToggle() {
      const result = toggleListening()
      this.updateStatus()
      return result
    },

    executeCommand(command) {
      const { action, params, key } = command
      
      this.$emit('command-executed', { action, params, key })

      switch (action) {
        case 'start_listening':
          startListening()
          break
        case 'stop_listening':
          stopListening()
          break
        case 'toggle_listening':
          toggleListening()
          break
        case 'navigate':
          this.$emit('navigate', params.page)
          break
        case 'navigate_next':
          this.$emit('navigate-next')
          break
        case 'navigate_previous':
          this.$emit('navigate-previous')
          break
        case 'search':
          this.$emit('search', params.type)
          break
        case 'refresh':
          this.$emit('refresh')
          break
        case 'show_help':
          this.$emit('show-help')
          break
        case 'toggle_fullscreen':
          this.toggleFullscreen()
          break
        case 'toggle_theme':
          this.$emit('toggle-theme')
          break
        case 'take_screenshot':
          this.$emit('screenshot')
          break
      }
    },

    toggleFullscreen() {
      if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen()
      } else {
        document.exitFullscreen()
      }
    },

    updateStatus() {
      const status = getStatus()
      this.isListening = status.isListening
      this.isOffline = status.isOffline
      this.commandHistory = status.commandHistory
    },

    clearHistory() {
      this.commandHistory = []
      this.$emit('history-cleared')
    },

    formatTime(timestamp) {
      const date = new Date(timestamp)
      return date.toLocaleTimeString('zh-CN', { 
        hour: '2-digit', 
        minute: '2-digit' 
      })
    },

    getCategoryName(key) {
      const names = {
        control: '控制命令',
        navigation: '导航命令',
        search: '搜索命令',
        shortcuts: '快捷命令'
      }
      return names[key] || key
    },

    cleanup() {
      stopListening()
      window.removeEventListener('voice-visual-feedback', this.handleVisualFeedback)
    }
  }
}
</script>

<style scoped>
.voice-command {
  position: relative;
  display: inline-block;
}

.voice-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 48px;
  border-radius: 50%;
  border: none;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.voice-btn:hover:not(:disabled) {
  transform: scale(1.1);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
}

.voice-btn:active:not(:disabled) {
  transform: scale(0.95);
}

.voice-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.voice-btn.listening {
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% {
    box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
  }
  50% {
    box-shadow: 0 4px 30px rgba(102, 126, 234, 0.8);
  }
}

.offline-badge {
  position: absolute;
  top: -5px;
  right: -5px;
  background: #ff6b6b;
  color: white;
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 10px;
  font-weight: bold;
}

.voice-status {
  position: absolute;
  top: 60px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 10px;
  background: rgba(0, 0, 0, 0.8);
  color: white;
  padding: 8px 16px;
  border-radius: 20px;
  white-space: nowrap;
  z-index: 1000;
}

.waveform {
  display: flex;
  align-items: center;
  gap: 3px;
  height: 20px;
}

.wave {
  width: 3px;
  height: 10px;
  background: #667eea;
  border-radius: 2px;
  animation: wave 1s ease-in-out infinite;
}

@keyframes wave {
  0%, 100% {
    height: 10px;
  }
  50% {
    height: 20px;
  }
}

.command-history {
  position: absolute;
  top: 60px;
  right: 0;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  padding: 16px;
  min-width: 280px;
  max-height: 300px;
  overflow-y: auto;
  z-index: 1000;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  font-weight: bold;
  color: #333;
}

.clear-btn {
  background: none;
  border: none;
  color: #667eea;
  cursor: pointer;
  font-size: 12px;
  padding: 4px 8px;
  border-radius: 4px;
}

.clear-btn:hover {
  background: #f0f0f0;
}

.history-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.history-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 8px;
  border-bottom: 1px solid #eee;
  font-size: 13px;
}

.history-item:last-child {
  border-bottom: none;
}

.history-time {
  color: #999;
  font-size: 11px;
}

.history-input {
  color: #666;
  font-style: italic;
}

.history-command {
  color: #667eea;
  font-weight: bold;
}

.voice-help {
  position: absolute;
  top: 60px;
  right: 0;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
  padding: 20px;
  min-width: 320px;
  max-height: 400px;
  overflow-y: auto;
  z-index: 1000;
}

.help-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 2px solid #667eea;
}

.help-header h4 {
  margin: 0;
  color: #333;
}

.close-btn {
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #999;
  padding: 4px 8px;
}

.close-btn:hover {
  color: #333;
}

.help-content {
  max-height: 340px;
  overflow-y: auto;
}

.help-section {
  margin-bottom: 16px;
}

.help-section h5 {
  color: #667eea;
  margin: 0 0 8px 0;
  font-size: 14px;
}

.help-section ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.help-section li {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
  border-bottom: 1px solid #f0f0f0;
  font-size: 13px;
}

.help-section strong {
  color: #333;
}

.help-desc {
  color: #999;
  font-size: 12px;
}
</style>
