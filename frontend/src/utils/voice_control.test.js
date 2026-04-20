/**
 * Voice Control Module Tests
 * 语音控制模块测试
 */

import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest'
import {
  VoiceController,
  startListening,
  stopListening,
  toggleListening,
  onCommand,
  onResult,
  onError,
  updateSettings,
  getStatus,
  getCommands,
  isSupported,
  isListening
} from './voice_control'
import voiceCommands from '../assets/voice_commands.json'

describe('VoiceController', () => {
  let controller

  beforeEach(() => {
    // Mock SpeechRecognition
    global.SpeechRecognition = vi.fn().mockImplementation(() => ({
      start: vi.fn(),
      stop: vi.fn(),
      continuous: false,
      interimResults: false,
      lang: 'zh-CN',
      onstart: null,
      onend: null,
      onresult: null,
      onerror: null
    }))
    
    // Mock speechSynthesis
    global.speechSynthesis = {
      speak: vi.fn()
    }
    
    // Mock AudioContext
    global.AudioContext = vi.fn().mockImplementation(() => ({
      createOscillator: vi.fn(() => ({
        connect: vi.fn(),
        start: vi.fn(),
        stop: vi.fn(),
        frequency: { value: 0 },
        type: 'sine'
      })),
      createGain: vi.fn(() => ({
        connect: vi.fn(),
        gain: { setValueAtTime: vi.fn() }
      }))
    }))

    controller = new VoiceController()
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  describe('初始化', () => {
    it('应该正确初始化', () => {
      expect(controller).toBeDefined()
      expect(controller.isSupported).toBe(true)
      expect(controller.isListening).toBe(false)
    })

    it('应该加载语音命令配置', () => {
      const commands = controller.getAvailableCommands()
      expect(commands).toBeDefined()
      expect(commands.control).toBeDefined()
      expect(commands.navigation).toBeDefined()
      expect(commands.search).toBeDefined()
      expect(commands.shortcuts).toBeDefined()
    })

    it('应该初始化离线命令映射', () => {
      expect(controller.offlineCommands.size).toBeGreaterThan(0)
    })
  })

  describe('语音控制', () => {
    it('应该能够启动语音识别', () => {
      const result = controller.start()
      expect(result).toBe(true)
      expect(controller.recognition.start).toHaveBeenCalled()
    })

    it('应该能够停止语音识别', () => {
      controller.start()
      const result = controller.stop()
      expect(result).toBe(true)
      expect(controller.recognition.stop).toHaveBeenCalled()
    })

    it('应该能够切换语音识别状态', () => {
      expect(controller.isListening).toBe(false)
      controller.toggle()
      expect(controller.recognition.start).toHaveBeenCalled()
      controller.toggle()
      expect(controller.recognition.stop).toHaveBeenCalled()
    })

    it('在不支持时应该返回 false', () => {
      global.SpeechRecognition = undefined
      const newController = new VoiceController()
      expect(newController.isSupported).toBe(false)
      const result = newController.start()
      expect(result).toBe(false)
    })
  })

  describe('命令匹配', () => {
    it('应该匹配控制命令', () => {
      const result = controller.matchCommand('开始')
      expect(result).toBeDefined()
      expect(result.category).toBe('control')
      expect(result.action).toBe('start_listening')
    })

    it('应该匹配导航命令', () => {
      const result = controller.matchCommand('打开首页')
      expect(result).toBeDefined()
      expect(result.category).toBe('navigation')
      expect(result.action).toBe('navigate')
      expect(result.params.page).toBe('home')
    })

    it('应该匹配搜索命令', () => {
      const result = controller.matchCommand('搜索报告')
      expect(result).toBeDefined()
      expect(result.category).toBe('search')
      expect(result.action).toBe('search')
      expect(result.params.type).toBe('report')
    })

    it('应该匹配快捷命令', () => {
      const result = controller.matchCommand('刷新')
      expect(result).toBeDefined()
      expect(result.category).toBe('shortcuts')
      expect(result.action).toBe('refresh')
    })

    it('应该计算匹配置信度', () => {
      const exactMatch = controller.matchCommand('开始')
      expect(exactMatch.confidence).toBe(1.0)

      const partialMatch = controller.matchCommand('请开始语音识别')
      expect(partialMatch.confidence).toBeGreaterThanOrEqual(0.8)
    })

    it('未匹配时应该返回 null', () => {
      const result = controller.matchCommand('不存在的命令 xyz123')
      expect(result).toBeNull()
    })
  })

  describe('停用词过滤', () => {
    it('应该移除停用词', () => {
      const result = controller.removeStopWords('我的首页')
      expect(result).not.toContain('的')
    })

    it('应该保留关键词', () => {
      const result = controller.removeStopWords('请帮我打开首页')
      expect(result).toContain('首页')
    })
  })

  describe('回调函数', () => {
    it('应该注册并触发 onStart 回调', () => {
      const callback = vi.fn()
      controller.setCallback('onStart', callback)
      controller.recognition.onstart()
      expect(callback).toHaveBeenCalled()
    })

    it('应该注册并触发 onStop 回调', () => {
      const callback = vi.fn()
      controller.setCallback('onStop', callback)
      controller.recognition.onend()
      expect(callback).toHaveBeenCalled()
    })

    it('应该注册并触发 onResult 回调', () => {
      const callback = vi.fn()
      controller.setCallback('onResult', callback)
      
      const mockEvent = {
        results: [
          [{ transcript: '打开首页' }]
        ]
      }
      controller.recognition.onresult(mockEvent)
      expect(callback).toHaveBeenCalledWith('打开首页')
    })

    it('应该注册并触发 onError 回调', () => {
      const callback = vi.fn()
      controller.setCallback('onError', callback)
      controller.recognition.onerror({ error: 'no-speech' })
      expect(callback).toHaveBeenCalledWith('no-speech')
    })

    it('应该触发 onCommand 回调', () => {
      const callback = vi.fn()
      controller.setCallback('onCommand', callback)
      controller.setCallback('onResult', vi.fn())
      
      controller.recognition.onresult({
        results: [[{ transcript: '开始' }]]
      })
      
      expect(callback).toHaveBeenCalled()
    })
  })

  describe('设置管理', () => {
    it('应该能够更新设置', () => {
      const newSettings = {
        default_language: 'en-US',
        continuous_mode: true
      }
      controller.updateSettings(newSettings)
      
      expect(controller.settings.default_language).toBe('en-US')
      expect(controller.settings.continuous_mode).toBe(true)
      expect(controller.recognition.lang).toBe('en-US')
      expect(controller.recognition.continuous).toBe(true)
    })

    it('应该能够获取状态', () => {
      const status = controller.getStatus()
      expect(status).toHaveProperty('isSupported')
      expect(status).toHaveProperty('isListening')
      expect(status).toHaveProperty('isOffline')
      expect(status).toHaveProperty('settings')
      expect(status).toHaveProperty('commandHistory')
    })
  })

  describe('命令历史', () => {
    it('应该记录命令历史', () => {
      controller.setCallback('onResult', vi.fn())
      controller.processVoiceInput('打开首页')
      
      expect(controller.commandHistory.length).toBeGreaterThan(0)
      expect(controller.commandHistory[0].input).toBe('打开首页')
    })

    it('应该能够清除历史', () => {
      controller.processVoiceInput('打开首页')
      expect(controller.commandHistory.length).toBeGreaterThan(0)
      
      controller.clearHistory()
      expect(controller.commandHistory.length).toBe(0)
    })

    it('应该限制历史数量', () => {
      for (let i = 0; i < 15; i++) {
        controller.processVoiceInput(`命令${i}`)
      }
      expect(controller.commandHistory.length).toBeLessThanOrEqual(10)
    })
  })

  describe('离线模式', () => {
    it('应该支持离线命令匹配', () => {
      controller.isOffline = true
      const result = controller.matchCommand('首页')
      expect(result).toBeDefined()
    })

    it('应该在网络错误时切换到离线模式', () => {
      controller.setCallback('onError', vi.fn())
      controller.recognition.onerror({ error: 'network' })
      expect(controller.isOffline).toBe(true)
    })
  })

  describe('导出函数', () => {
    it('startListening 应该调用控制器的 start 方法', () => {
      const result = startListening()
      expect(result).toBeDefined()
    })

    it('stopListening 应该调用控制器的 stop 方法', () => {
      const result = stopListening()
      expect(result).toBeDefined()
    })

    it('toggleListening 应该调用控制器的 toggle 方法', () => {
      const result = toggleListening()
      expect(result).toBeDefined()
    })

    it('getStatus 应该返回状态', () => {
      const status = getStatus()
      expect(status).toBeDefined()
    })

    it('getCommands 应该返回命令配置', () => {
      const commands = getCommands()
      expect(commands).toBeDefined()
      expect(commands.control).toBeDefined()
    })
  })
})

describe('语音命令配置', () => {
  it('应该包含所有必需的分类', () => {
    expect(voiceCommands.commands.control).toBeDefined()
    expect(voiceCommands.commands.navigation).toBeDefined()
    expect(voiceCommands.commands.search).toBeDefined()
    expect(voiceCommands.commands.shortcuts).toBeDefined()
  })

  it('控制命令应该包含开始/停止/切换', () => {
    expect(voiceCommands.commands.control.start).toBeDefined()
    expect(voiceCommands.commands.control.stop).toBeDefined()
    expect(voiceCommands.commands.control.toggle).toBeDefined()
  })

  it('每个命令都应该有关键词', () => {
    const categories = Object.values(voiceCommands.commands)
    categories.forEach(category => {
      Object.values(category).forEach(cmd => {
        expect(cmd.keywords).toBeDefined()
        expect(cmd.keywords.length).toBeGreaterThan(0)
      })
    })
  })

  it('反馈配置应该完整', () => {
    expect(voiceCommands.feedback.success).toBeDefined()
    expect(voiceCommands.feedback.error).toBeDefined()
    expect(voiceCommands.feedback.listening).toBeDefined()
  })

  it('设置应该有默认值', () => {
    expect(voiceCommands.settings.default_language).toBe('zh-CN')
    expect(voiceCommands.settings.sensitivity).toBe(0.8)
    expect(typeof voiceCommands.settings.offline_mode).toBe('boolean')
  })
})
