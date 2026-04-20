/**
 * LiveMirror WebSocket 客户端
 * 支持实时音频流传输、自动重连、心跳保活
 */

class WebSocketClient {
  /**
   * 创建 WebSocket 客户端
   * @param {Object} options 配置选项
   * @param {string} options.url WebSocket 服务器地址
   * @param {string} options.sessionId 会话 ID
   * @param {number} options.sampleRate 音频采样率
   * @param {number} options.bufferDuration 缓冲区时长 (ms)
   * @param {number} options.reconnectInterval 重连间隔 (ms)
   * @param {number} options.maxReconnectAttempts 最大重连次数
   * @param {number} options.heartbeatInterval 心跳间隔 (ms)
   */
  constructor(options = {}) {
    this.options = {
      url: 'ws://localhost:8000/ws/stream',
      sessionId: null,
      sampleRate: 16000,
      bufferDuration: 3000,
      reconnectInterval: 3000,
      maxReconnectAttempts: 5,
      heartbeatInterval: 10000,
      ...options
    }

    this.ws = null
    this.reconnectAttempts = 0
    this.isConnecting = false
    this.isManuallyClosed = false
    this.heartbeatTimer = null
    this.audioContext = null
    this.mediaStream = null
    this.audioProcessor = null

    // 回调函数
    this.callbacks = {
      onConnected: null,
      onDisconnected: null,
      onMessage: null,
      onError: null,
      onReconnecting: null,
      onTranscription: null,
      onAnalysis: null,
      onStats: null
    }

    // 统计信息
    this.stats = {
      connectedAt: null,
      messagesSent: 0,
      messagesReceived: 0,
      bytesSent: 0,
      reconnectCount: 0,
      latencies: []
    }
  }

  /**
   * 连接 WebSocket 服务器
   * @returns {Promise<void>}
   */
  async connect() {
    if (this.isConnecting || this.ws?.readyState === WebSocket.OPEN) {
      console.log('[WS] 已连接或正在连接')
      return
    }

    this.isManuallyClosed = false
    this.isConnecting = true

    const wsUrl = `${this.options.url}/${this.options.sessionId}?sample_rate=${this.options.sampleRate}&buffer_duration=${this.options.bufferDuration}`
    console.log('[WS] 尝试连接:', wsUrl)

    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(wsUrl)

        this.ws.onopen = () => {
          console.log('[WS] 连接成功')
          this.isConnecting = false
          this.reconnectAttempts = 0
          this.stats.connectedAt = Date.now()
          this._startHeartbeat()
          
          if (this.callbacks.onConnected) {
            this.callbacks.onConnected()
          }
          resolve()
        }

        this.ws.onmessage = (event) => {
          this._handleMessage(event)
        }

        this.ws.onerror = (error) => {
          console.error('[WS] 连接错误:', error)
          this.isConnecting = false
          
          if (this.callbacks.onError) {
            this.callbacks.onError(error)
          }
          
          if (this.ws.readyState === WebSocket.CONNECTING) {
            reject(error)
          }
        }

        this.ws.onclose = (event) => {
          console.log('[WS] 连接关闭:', event.code, event.reason)
          this.isConnecting = false
          this._stopHeartbeat()
          
          if (this.callbacks.onDisconnected) {
            this.callbacks.onDisconnected(event)
          }

          // 自动重连
          if (!this.isManuallyClosed && this.reconnectAttempts < this.options.maxReconnectAttempts) {
            this._scheduleReconnect()
          }
        }
      } catch (error) {
        this.isConnecting = false
        console.error('[WS] 创建连接失败:', error)
        reject(error)
      }
    })
  }

  /**
   * 断开连接
   */
  disconnect() {
    this.isManuallyClosed = true
    this._stopHeartbeat()
    
    if (this.ws) {
      this.ws.close(1000, 'Client disconnected')
      this.ws = null
    }

    console.log('[WS] 已断开连接')
  }

  /**
   * 发送音频数据
   * @param {Float32Array|Int16Array|ArrayBuffer} audioData 音频数据
   * @param {number} durationMs 音频时长 (ms)
   */
  sendAudio(audioData, durationMs = null) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn('[WS] 连接未就绪，无法发送音频')
      return false
    }

    // 转换音频数据为 Int16Array
    let int16Data
    if (audioData instanceof Float32Array) {
      int16Data = new Int16Array(audioData.length)
      for (let i = 0; i < audioData.length; i++) {
        int16Data[i] = Math.max(-32768, Math.min(32767, audioData[i] * 32767))
      }
    } else if (audioData instanceof Int16Array) {
      int16Data = audioData
    } else if (audioData instanceof ArrayBuffer) {
      int16Data = new Int16Array(audioData)
    } else {
      console.error('[WS] 不支持的音频数据类型')
      return false
    }

    // 转换为 base64
    const base64Data = this._arrayBufferToBase64(int16Data.buffer)
    
    if (durationMs === null) {
      durationMs = (int16Data.length / this.options.sampleRate) * 1000
    }

    const message = {
      type: 'audio',
      data: base64Data,
      duration_ms: durationMs
    }

    this.ws.send(JSON.stringify(message))
    this.stats.messagesSent++
    this.stats.bytesSent += base64Data.length

    console.log(`[WS] 发送音频片段：${durationMs.toFixed(0)}ms, ${int16Data.length} 采样点`)
    return true
  }

  /**
   * 发送文本消息（用于测试）
   * @param {string} text 文本内容
   */
  sendText(text) {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      console.warn('[WS] 连接未就绪，无法发送文本')
      return false
    }

    const message = {
      type: 'text',
      content: text
    }

    this.ws.send(JSON.stringify(message))
    this.stats.messagesSent++

    console.log('[WS] 发送文本:', text)
    return true
  }

  /**
   * 获取统计信息
   * @returns {Object} 统计信息
   */
  getStats() {
    const duration = this.stats.connectedAt ? Date.now() - this.stats.connectedAt : 0
    const avgLatency = this.stats.latencies.length > 0
      ? this.stats.latencies.reduce((a, b) => a + b, 0) / this.stats.latencies.length
      : 0

    return {
      ...this.stats,
      durationMs: duration,
      avgLatencyMs: avgLatency.toFixed(2),
      isConnected: this.ws?.readyState === WebSocket.OPEN
    }
  }

  /**
   * 请求服务器统计
   */
  requestStats() {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      return false
    }

    const message = {
      type: 'get_stats'
    }

    this.ws.send(JSON.stringify(message))
    return true
  }

  /**
   * 停止流处理
   */
  stop() {
    if (!this.ws || this.ws.readyState !== WebSocket.OPEN) {
      return false
    }

    const message = {
      type: 'stop'
    }

    this.ws.send(JSON.stringify(message))
    return true
  }

  /**
   * 注册回调
   * @param {string} event 事件名称
   * @param {Function} callback 回调函数
   */
  on(event, callback) {
    if (this.callbacks.hasOwnProperty(event)) {
      this.callbacks[event] = callback
    } else {
      console.warn(`[WS] 未知事件：${event}`)
    }
  }

  /**
   * 开始录音并发送音频流
   * @returns {Promise<void>}
   */
  async startRecording() {
    try {
      // 获取麦克风权限
      this.mediaStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: this.options.sampleRate,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true
        }
      })

      // 创建音频上下文
      this.audioContext = new (window.AudioContext || window.webkitAudioContext)({
        sampleRate: this.options.sampleRate
      })

      const source = this.audioContext.createMediaStreamSource(this.mediaStream)
      
      // 创建脚本处理器
      const bufferSize = this.options.sampleRate * (this.options.bufferDuration / 1000)
      this.audioProcessor = this.audioContext.createScriptProcessor(bufferSize, 1, 1)

      this.audioProcessor.onaudioprocess = (event) => {
        const inputData = event.inputBuffer.getChannelData(0)
        this.sendAudio(inputData)
      }

      source.connect(this.audioProcessor)
      this.audioProcessor.connect(this.audioContext.destination)

      console.log('[WS] 录音已开始')
    } catch (error) {
      console.error('[WS] 录音启动失败:', error)
      throw error
    }
  }

  /**
   * 停止录音
   */
  stopRecording() {
    if (this.audioProcessor) {
      this.audioProcessor.disconnect()
      this.audioProcessor = null
    }

    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach(track => track.stop())
      this.mediaStream = null
    }

    if (this.audioContext) {
      this.audioContext.close()
      this.audioContext = null
    }

    console.log('[WS] 录音已停止')
  }

  /**
   * 处理接收到的消息
   * @param {MessageEvent} event WebSocket 消息事件
   * @private
   */
  _handleMessage(event) {
    try {
      const message = JSON.parse(event.data)
      this.stats.messagesReceived++

      console.log('[WS] 收到消息:', message.type)

      // 通用消息回调
      if (this.callbacks.onMessage) {
        this.callbacks.onMessage(message)
      }

      // 特定类型消息处理
      switch (message.type) {
        case 'connected':
          console.log('[WS] 服务器确认连接:', message.session_id)
          break

        case 'transcription_result':
        case 'analysis_result':
          if (message.performance?.latency_ms) {
            this.stats.latencies.push(message.performance.latency_ms)
            // 保留最近 100 个延迟数据
            if (this.stats.latencies.length > 100) {
              this.stats.latencies.shift()
            }
          }
          
          if (this.callbacks.onTranscription) {
            this.callbacks.onTranscription(message)
          }
          if (this.callbacks.onAnalysis) {
            this.callbacks.onAnalysis(message)
          }
          break

        case 'stats':
          if (this.callbacks.onStats) {
            this.callbacks.onStats(message)
          }
          break

        case 'pong':
          // 心跳响应，无需处理
          break

        case 'error':
          console.error('[WS] 服务器错误:', message.error)
          if (this.callbacks.onError) {
            this.callbacks.onError(new Error(message.error))
          }
          break

        case 'stopped':
          console.log('[WS] 流处理已停止')
          break
      }
    } catch (error) {
      console.error('[WS] 消息解析失败:', error)
    }
  }

  /**
   * 计划重连
   * @private
   */
  _scheduleReconnect() {
    this.reconnectAttempts++
    console.log(`[WS] 计划重连 (${this.reconnectAttempts}/${this.options.maxReconnectAttempts})`)

    if (this.callbacks.onReconnecting) {
      this.callbacks.onReconnecting({
        attempt: this.reconnectAttempts,
        maxAttempts: this.options.maxReconnectAttempts,
        delay: this.options.reconnectInterval
      })
    }

    setTimeout(() => {
      if (!this.isManuallyClosed) {
        this.stats.reconnectCount++
        this.connect().catch(console.error)
      }
    }, this.options.reconnectInterval)
  }

  /**
   * 启动心跳
   * @private
   */
  _startHeartbeat() {
    this._stopHeartbeat()
    
    this.heartbeatTimer = setInterval(() => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ type: 'ping' }))
      }
    }, this.options.heartbeatInterval)

    console.log(`[WS] 心跳已启动 (间隔：${this.options.heartbeatInterval}ms)`)
  }

  /**
   * 停止心跳
   * @private
   */
  _stopHeartbeat() {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer)
      this.heartbeatTimer = null
      console.log('[WS] 心跳已停止')
    }
  }

  /**
   * ArrayBuffer 转 Base64
   * @param {ArrayBuffer} buffer ArrayBuffer 数据
   * @returns {string} Base64 字符串
   * @private
   */
  _arrayBufferToBase64(buffer) {
    let binary = ''
    const bytes = new Uint8Array(buffer)
    const len = bytes.byteLength
    for (let i = 0; i < len; i++) {
      binary += String.fromCharCode(bytes[i])
    }
    return window.btoa(binary)
  }

  /**
   * Base64 转 ArrayBuffer
   * @param {string} base64 Base64 字符串
   * @returns {ArrayBuffer} ArrayBuffer 数据
   * @private
   */
  _base64ToArrayBuffer(base64) {
    const binaryString = window.atob(base64)
    const len = binaryString.length
    const bytes = new Uint8Array(len)
    for (let i = 0; i < len; i++) {
      bytes[i] = binaryString.charCodeAt(i)
    }
    return bytes.buffer
  }
}

/**
 * 创建 WebSocket 客户端实例
 * @param {Object} options 配置选项
 * @returns {WebSocketClient} WebSocket 客户端实例
 */
export function createWebSocketClient(options = {}) {
  return new WebSocketClient(options)
}

export default WebSocketClient
