<template>
  <div class="video-player-container">
    <div class="video-player-wrapper" :style="{ aspectRatio: aspectRatio }">
      <video
        ref="videoRef"
        class="video-player"
        :src="videoSrc"
        :poster="poster"
        controls
        @timeupdate="onTimeUpdate"
        @loadedmetadata="onLoadedMetadata"
        @play="onPlay"
        @pause="onPause"
        @ended="onEnded"
        @waiting="onWaiting"
        @playing="onPlaying"
        @error="onError"
      ></video>
      
      <!-- 加载指示器 -->
      <div v-if="isLoading" class="loading-overlay">
        <div class="loading-spinner"></div>
        <span class="loading-text">加载中...</span>
      </div>
      
      <!-- 错误提示 -->
      <div v-if="error" class="error-overlay">
        <div class="error-icon">⚠️</div>
        <span class="error-text">{{ error }}</span>
        <button @click="retry" class="retry-btn">重试</button>
      </div>
    </div>
    
    <!-- 播放控制栏 -->
    <div class="playback-controls" v-if="showControls">
      <!-- 播放/暂停按钮 -->
      <button @click="togglePlay" class="control-btn" title="播放/暂停">
        <span v-if="isPlaying">⏸️</span>
        <span v-else>▶️</span>
      </button>
      
      <!-- 时间显示 -->
      <div class="time-display">
        <span class="current-time">{{ formatTime(currentTime) }}</span>
        <span class="time-separator">/</span>
        <span class="duration">{{ formatTime(duration) }}</span>
      </div>
      
      <!-- 进度条 -->
      <div class="progress-bar-container" @click="seekTo">
        <div class="progress-bar">
          <div class="progress-buffered" :style="{ width: bufferedPercent + '%' }"></div>
          <div class="progress-current" :style="{ width: progressPercent + '%' }"></div>
        </div>
        <div class="progress-thumb" :style="{ left: progressPercent + '%' }"></div>
      </div>
      
      <!-- 倍速控制 -->
      <div class="playback-speed-control">
        <button @click="cycleSpeed" class="speed-btn" title="播放速度">
          {{ playbackRate }}x
        </button>
        <div class="speed-options" v-if="showSpeedOptions">
          <button
            v-for="speed in speedOptions"
            :key="speed"
            @click="setSpeed(speed)"
            :class="{ active: playbackRate === speed }"
          >
            {{ speed }}x
          </button>
        </div>
      </div>
      
      <!-- 音量控制 -->
      <div class="volume-control">
        <button @click="toggleMute" class="control-btn volume-btn" title="音量">
          <span v-if="isMuted">🔇</span>
          <span v-else-if="volume < 0.5">🔉</span>
          <span v-else>🔊</span>
        </button>
        <input
          type="range"
          class="volume-slider"
          min="0"
          max="100"
          v-model.number="volumePercent"
          @input="updateVolume"
        />
      </div>
      
      <!-- 全屏按钮 -->
      <button @click="toggleFullscreen" class="control-btn" title="全屏">
        <span v-if="isFullscreen">🗕</span>
        <span v-else>🗖</span>
      </button>
    </div>
    
    <!-- 片段剪辑工具 -->
    <div v-if="showClipTools" class="clip-tools">
      <div class="clip-time-range">
        <label>开始时间:</label>
        <input
          type="number"
          v-model.number="clipStartTime"
          :max="clipEndTime - 0.1"
          :step="0.1"
          @input="updateClipPreview"
        />
        <span>秒</span>
      </div>
      <div class="clip-time-range">
        <label>结束时间:</label>
        <input
          type="number"
          v-model.number="clipEndTime"
          :min="clipStartTime + 0.1"
          :max="duration"
          :step="0.1"
          @input="updateClipPreview"
        />
        <span>秒</span>
      </div>
      <div class="clip-duration">
        片段时长：{{ formatTime(clipDuration) }}
      </div>
      <button @click="createClip" class="clip-btn" :disabled="!canCreateClip">
        ✂️ 创建片段
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'

// Props
const props = defineProps({
  videoSrc: {
    type: String,
    required: true
  },
  poster: {
    type: String,
    default: ''
  },
  aspectRatio: {
    type: String,
    default: '16/9'
  },
  autoplay: {
    type: Boolean,
    default: false
  },
  showControls: {
    type: Boolean,
    default: true
  },
  showClipTools: {
    type: Boolean,
    default: false
  },
  startTime: {
    type: Number,
    default: 0
  },
  playbackRates: {
    type: Array,
    default: () => [0.5, 0.75, 1, 1.25, 1.5, 2]
  }
})

// Emits
const emit = defineEmits([
  'play',
  'pause',
  'ended',
  'timeupdate',
  'loadedmetadata',
  'error',
  'clip-create'
])

// 状态
const videoRef = ref(null)
const isLoading = ref(true)
const isPlaying = ref(false)
const isMuted = ref(false)
const isFullscreen = ref(false)
const error = ref('')
const currentTime = ref(0)
const duration = ref(0)
const volume = ref(1)
const playbackRate = ref(1)
const bufferedPercent = ref(0)
const showSpeedOptions = ref(false)

// 剪辑相关
const clipStartTime = ref(0)
const clipEndTime = ref(0)
const clipPreviewStart = ref(null)
const clipPreviewEnd = ref(null)

// 速度选项
const speedOptions = computed(() => props.playbackRates)

// 进度百分比
const progressPercent = computed(() => {
  if (duration.value === 0) return 0
  return (currentTime.value / duration.value) * 100
})

// 音量百分比
const volumePercent = computed({
  get: () => Math.round(volume.value * 100),
  set: (val) => {
    volume.value = val / 100
  }
})

// 剪辑时长
const clipDuration = computed(() => {
  return Math.max(0, clipEndTime.value - clipStartTime.value)
})

// 是否可以创建片段
const canCreateClip = computed(() => {
  return clipDuration.value > 0 && clipEndTime.value <= duration.value
})

// 生命周期
onMounted(() => {
  if (videoRef.value) {
    videoRef.value.volume = volume.value
    if (props.startTime > 0) {
      videoRef.value.currentTime = props.startTime
    }
    if (props.autoplay) {
      videoRef.value.play().catch(err => {
        console.warn('自动播放失败:', err)
      })
    }
  }
  
  // 全屏变化监听
  document.addEventListener('fullscreenchange', handleFullscreenChange)
})

onUnmounted(() => {
  document.removeEventListener('fullscreenchange', handleFullscreenChange)
})

// 方法
const togglePlay = () => {
  if (!videoRef.value) return
  
  if (isPlaying.value) {
    videoRef.value.pause()
  } else {
    videoRef.value.play()
  }
}

const onPlay = () => {
  isPlaying.value = true
  isLoading.value = false
  emit('play', { currentTime: currentTime.value })
}

const onPause = () => {
  isPlaying.value = false
  emit('pause', { currentTime: currentTime.value })
}

const onEnded = () => {
  isPlaying.value = false
  emit('ended')
}

const onTimeUpdate = () => {
  if (videoRef.value) {
    currentTime.value = videoRef.value.currentTime
    
    // 更新缓冲进度
    if (videoRef.value.buffered.length > 0) {
      const bufferedEnd = videoRef.value.buffered.end(videoRef.value.buffered.length - 1)
      bufferedPercent.value = (bufferedEnd / duration.value) * 100
    }
    
    emit('timeupdate', {
      currentTime: currentTime.value,
      duration: duration.value,
      progress: progressPercent.value
    })
  }
}

const onLoadedMetadata = () => {
  if (videoRef.value) {
    duration.value = videoRef.value.duration
    isLoading.value = false
    
    // 设置初始剪辑范围
    if (props.showClipTools) {
      clipStartTime.value = 0
      clipEndTime.value = duration.value
    }
  }
  emit('loadedmetadata', { duration: duration.value })
}

const onWaiting = () => {
  isLoading.value = true
}

const onPlaying = () => {
  isLoading.value = false
}

const onError = (e) => {
  error.value = '视频加载失败，请检查网络连接或稍后重试'
  isLoading.value = false
  emit('error', e)
}

const retry = () => {
  error.value = ''
  isLoading.value = true
  if (videoRef.value) {
    videoRef.value.load()
    videoRef.value.play()
  }
}

const seekTo = (event) => {
  if (!videoRef.value || duration.value === 0) return
  
  const rect = event.currentTarget.getBoundingClientRect()
  const pos = (event.clientX - rect.left) / rect.width
  const newTime = pos * duration.value
  
  videoRef.value.currentTime = Math.max(0, Math.min(newTime, duration.value))
}

const seekToTime = (time) => {
  if (videoRef.value) {
    videoRef.value.currentTime = Math.max(0, Math.min(time, duration.value))
  }
}

const cycleSpeed = () => {
  const currentIndex = speedOptions.value.indexOf(playbackRate.value)
  const nextIndex = (currentIndex + 1) % speedOptions.value.length
  setSpeed(speedOptions.value[nextIndex])
}

const setSpeed = (speed) => {
  playbackRate.value = speed
  if (videoRef.value) {
    videoRef.value.playbackRate = speed
  }
  showSpeedOptions.value = false
}

const toggleSpeedOptions = () => {
  showSpeedOptions.value = !showSpeedOptions.value
}

const updateVolume = () => {
  if (videoRef.value) {
    videoRef.value.volume = volume.value
    isMuted.value = volume.value === 0
  }
}

const toggleMute = () => {
  if (videoRef.value) {
    if (isMuted.value) {
      videoRef.value.muted = false
      isMuted.value = false
      volume.value = volume.value === 0 ? 1 : volume.value
    } else {
      videoRef.value.muted = true
      isMuted.value = true
    }
  }
}

const toggleFullscreen = () => {
  const container = videoRef.value?.parentElement?.parentElement
  
  if (!document.fullscreenElement) {
    container?.requestFullscreen?.()
  } else {
    document.exitFullscreen()
  }
}

const handleFullscreenChange = () => {
  isFullscreen.value = !!document.fullscreenElement
}

const formatTime = (seconds) => {
  if (isNaN(seconds)) return '00:00'
  
  const hrs = Math.floor(seconds / 3600)
  const mins = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)
  
  if (hrs > 0) {
    return `${hrs}:${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }
  return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
}

// 剪辑相关方法
const updateClipPreview = () => {
  // 可以在这里更新预览
  if (clipStartTime.value < 0) clipStartTime.value = 0
  if (clipEndTime.value > duration.value) clipEndTime.value = duration.value
  if (clipEndTime.value <= clipStartTime.value) {
    clipEndTime.value = clipStartTime.value + 0.1
  }
}

const createClip = () => {
  if (!canCreateClip.value) return
  
  emit('clip-create', {
    startTime: clipStartTime.value,
    endTime: clipEndTime.value,
    duration: clipDuration.value
  })
}

// 暴露方法给父组件
defineExpose({
  play: () => videoRef.value?.play(),
  pause: () => videoRef.value?.pause(),
  seekTo: seekToTime,
  setSpeed: setSpeed,
  getCurrentTime: () => currentTime.value,
  getDuration: () => duration.value,
  isPlaying: () => isPlaying.value
})
</script>

<style scoped>
.video-player-container {
  width: 100%;
  position: relative;
  background: #000;
  border-radius: 8px;
  overflow: hidden;
}

.video-player-wrapper {
  width: 100%;
  position: relative;
}

.video-player {
  width: 100%;
  height: 100%;
  display: block;
}

/* 加载指示器 */
.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.7);
  color: #fff;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  margin-top: 12px;
  font-size: 14px;
}

/* 错误提示 */
.error-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: rgba(0, 0, 0, 0.8);
  color: #fff;
}

.error-icon {
  font-size: 48px;
  margin-bottom: 12px;
}

.error-text {
  font-size: 14px;
  margin-bottom: 16px;
  text-align: center;
  padding: 0 20px;
}

.retry-btn {
  padding: 8px 24px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.retry-btn:hover {
  background: #45a049;
}

/* 播放控制栏 */
.playback-controls {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: linear-gradient(transparent, rgba(0, 0, 0, 0.8));
}

.control-btn {
  background: none;
  border: none;
  color: #fff;
  font-size: 20px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background 0.2s;
}

.control-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

.time-display {
  display: flex;
  align-items: center;
  gap: 4px;
  color: #fff;
  font-size: 13px;
  font-family: monospace;
  min-width: 100px;
}

.time-separator {
  opacity: 0.6;
}

/* 进度条 */
.progress-bar-container {
  flex: 1;
  position: relative;
  height: 20px;
  display: flex;
  align-items: center;
  cursor: pointer;
}

.progress-bar {
  position: relative;
  width: 100%;
  height: 4px;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 2px;
  overflow: hidden;
}

.progress-buffered {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  background: rgba(255, 255, 255, 0.5);
  transition: width 0.1s;
}

.progress-current {
  position: absolute;
  top: 0;
  left: 0;
  height: 100%;
  background: #4CAF50;
  transition: width 0.1s;
}

.progress-thumb {
  position: absolute;
  top: 50%;
  transform: translate(-50%, -50%);
  width: 12px;
  height: 12px;
  background: #fff;
  border-radius: 50%;
  opacity: 0;
  transition: opacity 0.2s;
  pointer-events: none;
}

.progress-bar-container:hover .progress-thumb {
  opacity: 1;
}

/* 倍速控制 */
.playback-speed-control {
  position: relative;
}

.speed-btn {
  background: rgba(255, 255, 255, 0.2);
  border: none;
  color: #fff;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  min-width: 45px;
}

.speed-btn:hover {
  background: rgba(255, 255, 255, 0.3);
}

.speed-options {
  position: absolute;
  bottom: 100%;
  right: 0;
  background: rgba(0, 0, 0, 0.9);
  border-radius: 4px;
  padding: 4px 0;
  margin-bottom: 4px;
  display: flex;
  flex-direction: column;
  min-width: 60px;
}

.speed-options button {
  background: none;
  border: none;
  color: #fff;
  padding: 6px 12px;
  cursor: pointer;
  font-size: 12px;
  text-align: left;
}

.speed-options button:hover {
  background: rgba(255, 255, 255, 0.2);
}

.speed-options button.active {
  color: #4CAF50;
}

/* 音量控制 */
.volume-control {
  display: flex;
  align-items: center;
  gap: 8px;
}

.volume-slider {
  width: 80px;
  height: 4px;
  -webkit-appearance: none;
  background: rgba(255, 255, 255, 0.3);
  border-radius: 2px;
  outline: none;
}

.volume-slider::-webkit-slider-thumb {
  -webkit-appearance: none;
  width: 12px;
  height: 12px;
  background: #fff;
  border-radius: 50%;
  cursor: pointer;
}

/* 片段剪辑工具 */
.clip-tools {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 16px;
  background: #1a1a1a;
  border-top: 1px solid #333;
  flex-wrap: wrap;
}

.clip-time-range {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #fff;
  font-size: 13px;
}

.clip-time-range input {
  width: 80px;
  padding: 4px 8px;
  background: #333;
  border: 1px solid #444;
  border-radius: 4px;
  color: #fff;
  font-size: 13px;
}

.clip-time-range input:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.clip-duration {
  color: #4CAF50;
  font-size: 13px;
  font-weight: 500;
}

.clip-btn {
  padding: 6px 16px;
  background: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
}

.clip-btn:hover:not(:disabled) {
  background: #45a049;
}

.clip-btn:disabled {
  background: #666;
  cursor: not-allowed;
  opacity: 0.5;
}
</style>
