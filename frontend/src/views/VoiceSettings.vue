<template>
  <div class="voice-settings">
    <div class="settings-header">
      <h2>🎤 语音控制设置</h2>
      <p class="subtitle">配置语音识别和命令选项</p>
    </div>

    <!-- 状态概览 -->
    <div class="status-card">
      <div class="status-item">
        <span class="status-label">浏览器支持</span>
        <span class="status-value" :class="{ 'status-ok': isSupported, 'status-error': !isSupported }">
          {{ isSupported ? '✓ 支持' : '✗ 不支持' }}
        </span>
      </div>
      <div class="status-item">
        <span class="status-label">当前状态</span>
        <span class="status-value" :class="{ 'status-active': isListening }">
          {{ isListening ? '🔴 聆听中' : '⚪ 已停止' }}
        </span>
      </div>
      <div class="status-item">
        <span class="status-label">工作模式</span>
        <span class="status-value" :class="{ 'status-warning': isOffline }">
          {{ isOffline ? '📴 离线模式' : '☁️ 在线模式' }}
        </span>
      </div>
    </div>

    <!-- 基础设置 -->
    <div class="settings-section">
      <h3>基础设置</h3>
      
      <div class="setting-item">
        <div class="setting-info">
          <label>语音识别语言</label>
          <p class="setting-desc">选择语音识别的語言</p>
        </div>
        <select v-model="settings.default_language" @change="saveSettings">
          <option value="zh-CN">简体中文</option>
          <option value="zh-TW">繁體中文</option>
          <option value="en-US">English (US)</option>
          <option value="ja-JP">日本語</option>
          <option value="ko-KR">한국어</option>
        </select>
      </div>

      <div class="setting-item">
        <div class="setting-info">
          <label>识别灵敏度</label>
          <p class="setting-desc">调整语音识别的灵敏度 ({{ Math.round(settings.sensitivity * 100) }}%)</p>
        </div>
        <input 
          type="range" 
          v-model.number="settings.sensitivity"
          min="0.1" 
          max="1.0" 
          step="0.1"
          @change="saveSettings"
          class="range-slider"
        />
      </div>

      <div class="setting-item">
        <div class="setting-info">
          <label>连续识别模式</label>
          <p class="setting-desc">保持持续监听，无需重复点击</p>
        </div>
        <label class="toggle-switch">
          <input type="checkbox" v-model="settings.continuous_mode" @change="saveSettings" />
          <span class="toggle-slider"></span>
        </label>
      </div>

      <div class="setting-item">
        <div class="setting-info">
          <label>自动启动</label>
          <p class="setting-desc">页面加载时自动启动语音识别</p>
        </div>
        <label class="toggle-switch">
          <input type="checkbox" v-model="settings.auto_start" @change="saveSettings" />
          <span class="toggle-slider"></span>
        </label>
      </div>
    </div>

    <!-- 反馈设置 -->
    <div class="settings-section">
      <h3>反馈设置</h3>
      
      <div class="setting-item">
        <div class="setting-info">
          <label>声音反馈</label>
          <p class="setting-desc">执行命令时播放提示音</p>
        </div>
        <label class="toggle-switch">
          <input type="checkbox" v-model="settings.feedback_sound" @change="saveSettings" />
          <span class="toggle-slider"></span>
        </label>
      </div>

      <div class="setting-item">
        <div class="setting-info">
          <label>视觉反馈</label>
          <p class="setting-desc">显示波形和状态提示</p>
        </div>
        <label class="toggle-switch">
          <input type="checkbox" v-model="settings.feedback_visual" @change="saveSettings" />
          <span class="toggle-slider"></span>
        </label>
      </div>

      <div class="setting-item">
        <div class="setting-info">
          <label>语音反馈 (TTS)</label>
          <p class="setting-desc">使用语音合成朗读反馈</p>
        </div>
        <label class="toggle-switch">
          <input type="checkbox" v-model="settings.feedback_voice" @change="saveSettings" />
          <span class="toggle-slider"></span>
        </label>
      </div>
    </div>

    <!-- 离线模式设置 -->
    <div class="settings-section">
      <h3>离线模式</h3>
      
      <div class="setting-item">
        <div class="setting-info">
          <label>启用离线支持</label>
          <p class="setting-desc">在网络不可用时使用本地命令匹配</p>
        </div>
        <label class="toggle-switch">
          <input type="checkbox" v-model="settings.offline_mode" @change="saveSettings" />
          <span class="toggle-slider"></span>
        </label>
      </div>

      <div class="offline-info" v-if="settings.offline_mode">
        <h4>支持的离线命令:</h4>
        <ul class="offline-commands-list">
          <li v-for="(cmd, key) in offlineCommands" :key="key">
            <strong>{{ cmd.keywords[0] }}</strong> - {{ cmd.description }}
          </li>
        </ul>
      </div>
    </div>

    <!-- 唤醒词设置 (高级) -->
    <div class="settings-section">
      <h3>唤醒词 (高级)</h3>
      
      <div class="setting-item">
        <div class="setting-info">
          <label>唤醒词</label>
          <p class="setting-desc">设置唤醒语音助手的关键词 (留空禁用)</p>
        </div>
        <input 
          type="text" 
          v-model="settings.wake_word"
          placeholder="例如：小镜、你好"
          @change="saveSettings"
          class="text-input"
        />
      </div>
    </div>

    <!-- 命令历史 -->
    <div class="settings-section">
      <h3>命令历史</h3>
      
      <div class="history-stats">
        <div class="stat-item">
          <span class="stat-value">{{ commandHistory.length }}</span>
          <span class="stat-label">总命令数</span>
        </div>
        <div class="stat-item">
          <span class="stat-value">{{ todayCommands }}</span>
          <span class="stat-label">今日命令</span>
        </div>
      </div>

      <div class="history-actions">
        <button class="btn btn-secondary" @click="exportHistory">
          📥 导出历史
        </button>
        <button class="btn btn-danger" @click="clearHistory">
          🗑️ 清除历史
        </button>
      </div>
    </div>

    <!-- 测试区域 -->
    <div class="settings-section">
      <h3>测试语音识别</h3>
      
      <div class="test-area">
        <button 
          class="btn btn-primary test-btn"
          @click="testRecognition"
          :disabled="!isSupported || isListening"
        >
          {{ isListening ? '🔴 停止测试' : '🎤 开始测试' }}
        </button>
        
        <div class="test-result" v-if="testTranscript">
          <label>识别结果:</label>
          <p>{{ testTranscript }}</p>
        </div>
        
        <div class="test-result" v-if="lastCommand">
          <label>匹配命令:</label>
          <p><strong>{{ lastCommand.key }}</strong> (置信度：{{ Math.round(lastCommand.confidence * 100) }}%)</label>
        </div>
      </div>
    </div>

    <!-- 帮助 -->
    <div class="settings-section help-section">
      <h3>💡 使用提示</h3>
      <ul class="help-list">
        <li>点击麦克风按钮开始/停止语音识别</li>
        <li>说出命令关键词即可执行操作</li>
        <li>离线模式下仅支持预设的命令</li>
        <li>可以在任意页面使用语音导航</li>
        <li>说"帮助"查看所有可用命令</li>
      </ul>
    </div>
  </div>
</template>

<script>
import {
  startListening,
  stopListening,
  getStatus,
  updateSettings,
  getCommands,
  onResult,
  onCommand
} from '../utils/voice_control'
import voiceCommandsData from '../assets/voice_commands.json'

export default {
  name: 'VoiceSettings',
  data() {
    return {
      isSupported: false,
      isListening: false,
      isOffline: false,
      settings: {
        default_language: 'zh-CN',
        sensitivity: 0.8,
        continuous_mode: false,
        auto_start: false,
        feedback_sound: true,
        feedback_visual: true,
        feedback_voice: true,
        offline_mode: true,
        wake_word: null
      },
      commandHistory: [],
      testTranscript: '',
      lastCommand: null,
      commands: {}
    }
  },
  computed: {
    offlineCommands() {
      const result = []
      const categories = ['control', 'navigation', 'search', 'shortcuts']
      categories.forEach(cat => {
        const cmds = this.commands[cat]
        if (cmds) {
          Object.values(cmds).forEach(cmd => {
            result.push(cmd)
          })
        }
      })
      return result
    },
    todayCommands() {
      const today = new Date().toDateString()
      return this.commandHistory.filter(cmd => {
        return new Date(cmd.timestamp).toDateString() === today
      }).length
    }
  },
  mounted() {
    this.loadSettings()
    this.updateStatus()
    this.setupTestListeners()
  },
  beforeUnmount() {
    this.cleanup()
  },
  methods: {
    loadSettings() {
      const saved = localStorage.getItem('voice_settings')
      if (saved) {
        try {
          this.settings = { ...this.settings, ...JSON.parse(saved) }
          updateSettings(this.settings)
        } catch (e) {
          console.error('加载设置失败:', e)
        }
      }
      this.commands = getCommands()
    },

    saveSettings() {
      localStorage.setItem('voice_settings', JSON.stringify(this.settings))
      updateSettings(this.settings)
    },

    updateStatus() {
      const status = getStatus()
      this.isSupported = status.isSupported
      this.isListening = status.isListening
      this.isOffline = status.isOffline
      this.commandHistory = status.commandHistory
    },

    setupTestListeners() {
      onResult((transcript) => {
        this.testTranscript = transcript
      })

      onCommand((command) => {
        this.lastCommand = command
      })

      // 定时更新状态
      this.statusInterval = setInterval(() => {
        this.updateStatus()
      }, 1000)
    },

    testRecognition() {
      if (this.isListening) {
        stopListening()
        this.testTranscript = ''
        this.lastCommand = null
      } else {
        this.testTranscript = ''
        this.lastCommand = null
        startListening()
      }
    },

    clearHistory() {
      if (confirm('确定要清除所有命令历史吗？')) {
        this.commandHistory = []
        // 清除工具模块中的历史
        const { voiceController } = require('../utils/voice_control')
        voiceController.clearHistory()
      }
    },

    exportHistory() {
      const data = JSON.stringify(this.commandHistory, null, 2)
      const blob = new Blob([data], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `voice_history_${new Date().toISOString().split('T')[0]}.json`
      a.click()
      URL.revokeObjectURL(url)
    },

    cleanup() {
      stopListening()
      if (this.statusInterval) {
        clearInterval(this.statusInterval)
      }
    }
  }
}
</script>

<style scoped>
.voice-settings {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px;
}

.settings-header {
  margin-bottom: 32px;
}

.settings-header h2 {
  font-size: 28px;
  color: #333;
  margin: 0 0 8px 0;
}

.subtitle {
  color: #666;
  margin: 0;
}

.status-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 20px;
  display: flex;
  justify-content: space-around;
  margin-bottom: 32px;
  color: white;
}

.status-item {
  text-align: center;
}

.status-label {
  display: block;
  font-size: 14px;
  opacity: 0.9;
  margin-bottom: 8px;
}

.status-value {
  display: block;
  font-size: 18px;
  font-weight: bold;
}

.status-ok {
  color: #4ade80;
}

.status-error {
  color: #f87171;
}

.status-active {
  color: #fbbf24;
}

.status-warning {
  color: #fbbf24;
}

.settings-section {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.settings-section h3 {
  font-size: 18px;
  color: #333;
  margin: 0 0 20px 0;
  padding-bottom: 12px;
  border-bottom: 2px solid #667eea;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 0;
  border-bottom: 1px solid #f0f0f0;
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-info label {
  display: block;
  font-weight: 500;
  color: #333;
  margin-bottom: 4px;
}

.setting-desc {
  font-size: 13px;
  color: #999;
  margin: 0;
}

select, .text-input {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 14px;
  min-width: 150px;
}

.range-slider {
  width: 200px;
  accent-color: #667eea;
}

.toggle-switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 26px;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: 0.3s;
  border-radius: 26px;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 20px;
  width: 20px;
  left: 3px;
  bottom: 3px;
  background-color: white;
  transition: 0.3s;
  border-radius: 50%;
}

input:checked + .toggle-slider {
  background-color: #667eea;
}

input:checked + .toggle-slider:before {
  transform: translateX(24px);
}

.offline-info {
  background: #f8f9fa;
  border-radius: 8px;
  padding: 16px;
  margin-top: 12px;
}

.offline-info h4 {
  margin: 0 0 12px 0;
  color: #667eea;
  font-size: 14px;
}

.offline-commands-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 8px;
}

.offline-commands-list li {
  font-size: 13px;
  color: #666;
}

.offline-commands-list strong {
  color: #333;
}

.history-stats {
  display: flex;
  gap: 24px;
  margin-bottom: 16px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 32px;
  font-weight: bold;
  color: #667eea;
}

.stat-label {
  font-size: 14px;
  color: #999;
}

.history-actions {
  display: flex;
  gap: 12px;
}

.btn {
  padding: 10px 20px;
  border: none;
  border-radius: 6px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary {
  background: #667eea;
  color: white;
}

.btn-primary:hover {
  background: #5568d3;
}

.btn-secondary {
  background: #f0f0f0;
  color: #333;
}

.btn-secondary:hover {
  background: #e0e0e0;
}

.btn-danger {
  background: #f87171;
  color: white;
}

.btn-danger:hover {
  background: #f05555;
}

.test-area {
  text-align: center;
  padding: 20px;
}

.test-btn {
  font-size: 16px;
  padding: 12px 32px;
}

.test-result {
  margin-top: 20px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
  text-align: left;
}

.test-result label {
  display: block;
  font-weight: bold;
  color: #667eea;
  margin-bottom: 8px;
}

.test-result p {
  margin: 0;
  color: #333;
}

.help-section {
  background: #f8f9fa;
}

.help-list {
  list-style: none;
  padding: 0;
  margin: 0;
}

.help-list li {
  padding: 8px 0;
  color: #666;
  font-size: 14px;
}

.help-list li:before {
  content: "• ";
  color: #667eea;
  font-weight: bold;
}
</style>
