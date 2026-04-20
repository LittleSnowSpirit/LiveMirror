/**
 * Voice Control Utility Module
 * 语音控制工具 - 支持在线/离线语音识别
 */

import voiceCommands from '../assets/voice_commands.json'

class VoiceController {
  constructor() {
    this.recognition = null
    this.isListening = false
    this.isSupported = false
    this.isOffline = false
    this.callbacks = {
      onStart: null,
      onStop: null,
      onResult: null,
      onError: null,
      onCommand: null
    }
    this.settings = { ...voiceCommands.settings }
    this.commandHistory = []
    this.offlineCommands = new Map()
    
    this.initOfflineCommands()
    this.initRecognition()
  }

  /**
   * 初始化离线命令映射
   */
  initOfflineCommands() {
    const categories = ['control', 'navigation', 'search', 'shortcuts']
    categories.forEach(category => {
      const cmds = voiceCommands.commands[category]
      if (cmds) {
        Object.keys(cmds).forEach(key => {
          const cmd = cmds[key]
          cmd.keywords.forEach(keyword => {
            this.offlineCommands.set(keyword.toLowerCase(), {
              category,
              key,
              action: cmd.action,
              params: cmd.params || {}
            })
          })
        })
      }
    })
  }

  /**
   * 初始化语音识别
   */
  initRecognition() {
    // 检查浏览器支持
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    
    if (SpeechRecognition) {
      this.isSupported = true
      this.recognition = new SpeechRecognition()
      this.recognition.continuous = this.settings.continuous_mode
      this.recognition.interimResults = true
      this.recognition.lang = this.settings.default_language
      
      this.recognition.onstart = () => {
        this.isListening = true
        this.executeCallback('onStart')
        this.feedback('listening')
      }
      
      this.recognition.onend = () => {
        this.isListening = false
        this.executeCallback('onStop')
      }
      
      this.recognition.onresult = (event) => {
        const transcript = Array.from(event.results)
          .map(result => result[0].transcript)
          .join('')
        
        this.executeCallback('onResult', transcript)
        this.processVoiceInput(transcript)
      }
      
      this.recognition.onerror = (event) => {
        this.executeCallback('onError', event.error)
        if (event.error === 'no-speech') {
          this.feedback('error', { input: '未检测到语音' })
        } else if (event.error === 'network') {
          this.isOffline = true
          this.feedback('offline')
        }
      }
    } else {
      this.isSupported = false
      console.warn('浏览器不支持语音识别，使用离线命令模式')
    }
  }

  /**
   * 开始语音识别
   */
  start() {
    if (!this.isSupported) {
      console.warn('语音识别不支持，使用离线模式')
      this.isOffline = true
      this.feedback('offline')
      return false
    }
    
    try {
      this.recognition.start()
      return true
    } catch (error) {
      console.error('启动语音识别失败:', error)
      this.executeCallback('onError', error)
      return false
    }
  }

  /**
   * 停止语音识别
   */
  stop() {
    if (this.recognition && this.isListening) {
      this.recognition.stop()
      return true
    }
    return false
  }

  /**
   * 切换语音识别状态
   */
  toggle() {
    if (this.isListening) {
      return this.stop()
    } else {
      return this.start()
    }
  }

  /**
   * 处理语音输入
   */
  processVoiceInput(transcript) {
    const normalizedInput = transcript.toLowerCase().trim()
    
    // 移除语气词和停用词
    const cleanedInput = this.removeStopWords(normalizedInput)
    
    // 匹配命令
    const matchedCommand = this.matchCommand(cleanedInput)
    
    if (matchedCommand) {
      this.executeCallback('onCommand', matchedCommand)
      this.feedback('success', { command: matchedCommand.key })
      this.commandHistory.push({
        timestamp: Date.now(),
        input: transcript,
        command: matchedCommand
      })
      return matchedCommand
    } else {
      this.feedback('error', { input: transcript })
      return null
    }
  }

  /**
   * 移除停用词
   */
  removeStopWords(text) {
    let result = text
    this.settings.excluded_keywords.forEach(word => {
      const regex = new RegExp(`\\b${word}\\b`, 'g')
      result = result.replace(regex, '')
    })
    return result.trim()
  }

  /**
   * 匹配语音命令
   */
  matchCommand(input) {
    const categories = ['control', 'navigation', 'search', 'shortcuts']
    
    for (const category of categories) {
      const cmds = voiceCommands.commands[category]
      if (!cmds) continue
      
      for (const [key, cmd] of Object.entries(cmds)) {
        for (const keyword of cmd.keywords) {
          if (input.includes(keyword.toLowerCase())) {
            return {
              category,
              key,
              action: cmd.action,
              params: cmd.params || {},
              confidence: this.calculateConfidence(input, keyword)
            }
          }
        }
      }
    }
    
    // 离线模式下的精确匹配
    if (this.isOffline) {
      const offlineCmd = this.offlineCommands.get(input)
      if (offlineCmd) {
        return { ...offlineCmd, confidence: 1.0 }
      }
    }
    
    return null
  }

  /**
   * 计算匹配置信度
   */
  calculateConfidence(input, keyword) {
    const keywordLen = keyword.length
    const inputLen = input.length
    
    if (input === keyword.toLowerCase()) {
      return 1.0
    } else if (input.includes(keyword.toLowerCase())) {
      return 0.8 + (0.2 * (keywordLen / inputLen))
    } else {
      return 0.5
    }
  }

  /**
   * 执行回调
   */
  executeCallback(name, ...args) {
    if (this.callbacks[name] && typeof this.callbacks[name] === 'function') {
      this.callbacks[name](...args)
    }
  }

  /**
   * 反馈给用户
   */
  feedback(type, data = {}) {
    const feedbackConfig = voiceCommands.feedback[type]
    if (!feedbackConfig) return
    
    // 视觉反馈
    if (this.settings.feedback_visual) {
      this.visualFeedback(feedbackConfig.visual, data)
    }
    
    // 声音反馈
    if (this.settings.feedback_sound) {
      this.audioFeedback(feedbackConfig.sound)
    }
    
    // 语音反馈
    if (this.settings.feedback_voice) {
      this.voiceFeedback(feedbackConfig.text, data)
    }
    
    // 触发反馈事件
    window.dispatchEvent(new CustomEvent('voice-feedback', {
      detail: { type, config: feedbackConfig, data }
    }))
  }

  /**
   * 视觉反馈
   */
  visualFeedback(type, data) {
    // 通过事件通知 UI 更新
    window.dispatchEvent(new CustomEvent('voice-visual-feedback', {
      detail: { type, data }
    }))
  }

  /**
   * 音频反馈
   */
  audioFeedback(soundType) {
    // 简单的音频反馈实现
    const audioContext = new (window.AudioContext || window.webkitAudioContext)()
    const oscillator = audioContext.createOscillator()
    const gainNode = audioContext.createGain()
    
    oscillator.connect(gainNode)
    gainNode.connect(audioContext.destination)
    
    switch (soundType) {
      case 'success':
        oscillator.frequency.value = 800
        oscillator.type = 'sine'
        gainNode.gain.setValueAtTime(0.1, audioContext.currentTime)
        oscillator.start(audioContext.currentTime)
        oscillator.stop(audioContext.currentTime + 0.1)
        break
      case 'error':
        oscillator.frequency.value = 300
        oscillator.type = 'sawtooth'
        gainNode.gain.setValueAtTime(0.1, audioContext.currentTime)
        oscillator.start(audioContext.currentTime)
        oscillator.stop(audioContext.currentTime + 0.2)
        break
      case 'listening':
        // 持续的提示音，由 UI 处理
        break
    }
  }

  /**
   * 语音反馈 (TTS)
   */
  voiceFeedback(text, data) {
    if (!('speechSynthesis' in window)) return
    
    let message = text
    Object.keys(data).forEach(key => {
      message = message.replace(`{${key}}`, data[key])
    })
    
    const utterance = new SpeechSynthesisUtterance(message)
    utterance.lang = this.settings.default_language
    utterance.rate = 1.0
    utterance.pitch = 1.0
    window.speechSynthesis.speak(utterance)
  }

  /**
   * 设置回调
   */
  setCallback(name, callback) {
    if (this.callbacks.hasOwnProperty(name)) {
      this.callbacks[name] = callback
    }
  }

  /**
   * 更新设置
   */
  updateSettings(newSettings) {
    this.settings = { ...this.settings, ...newSettings }
    if (this.recognition) {
      this.recognition.lang = this.settings.default_language
      this.recognition.continuous = this.settings.continuous_mode
    }
  }

  /**
   * 获取状态
   */
  getStatus() {
    return {
      isSupported: this.isSupported,
      isListening: this.isListening,
      isOffline: this.isOffline,
      settings: this.settings,
      commandHistory: this.commandHistory.slice(-10)
    }
  }

  /**
   * 获取所有命令
   */
  getAvailableCommands() {
    return voiceCommands.commands
  }

  /**
   * 清除历史
   */
  clearHistory() {
    this.commandHistory = []
  }
}

// 创建单例实例
const voiceController = new VoiceController()

// 导出工具函数
export function startListening() {
  return voiceController.start()
}

export function stopListening() {
  return voiceController.stop()
}

export function toggleListening() {
  return voiceController.toggle()
}

export function onCommand(callback) {
  voiceController.setCallback('onCommand', callback)
}

export function onResult(callback) {
  voiceController.setCallback('onResult', callback)
}

export function onError(callback) {
  voiceController.setCallback('onError', callback)
}

export function updateSettings(settings) {
  voiceController.updateSettings(settings)
}

export function getStatus() {
  return voiceController.getStatus()
}

export function getCommands() {
  return voiceController.getAvailableCommands()
}

export function isSupported() {
  return voiceController.isSupported
}

export function isListening() {
  return voiceController.isListening
}

// 导出类供高级使用
export { VoiceController, voiceController }

export default voiceController
