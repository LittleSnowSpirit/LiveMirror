<template>
  <div class="speech-card" :class="`type-${speech.type}`">
    <div class="card-header">
      <div class="time-info">
        <el-icon><Clock /></el-icon>
        <span>{{ formatTime(speech.timestamp) }}</span>
        <span class="duration">({{ speech.duration }}s)</span>
      </div>
      
      <div class="tags">
        <el-tag
          v-for="tag in speech.tags"
          :key="tag"
          size="small"
          effect="plain"
        >
          {{ tag }}
        </el-tag>
      </div>
    </div>
    
    <div class="card-body">
      <div class="type-badge" :class="speech.type">
        <el-icon v-if="speech.type === 'highlight'"><Star /></el-icon>
        <el-icon v-else-if="speech.type === 'issue'"><Warning /></el-icon>
        <el-icon v-else><ChatDotRound /></el-icon>
        <span>{{ typeLabel }}</span>
      </div>
      
      <div class="content">
        <p class="speech-text">{{ speech.content }}</p>
        
        <div v-if="speech.suggestion" class="suggestion">
          <div class="suggestion-title">
            <el-icon><InfoFilled /></el-icon>
            <span>优化建议</span>
          </div>
          <p class="suggestion-text">{{ speech.suggestion }}</p>
        </div>
      </div>
    </div>
    
    <div class="card-footer">
      <div class="emotion-indicator">
        <span class="emotion-label">情绪:</span>
        <div class="emotion-bar">
          <div
            class="emotion-fill"
            :class="emotionClass"
            :style="{ width: emotionWidth }"
          ></div>
        </div>
        <span class="emotion-value">{{ emotionText }}</span>
      </div>
      
      <div class="actions">
        <el-button size="small" @click="handleCopy">
          <el-icon><CopyDocument /></el-icon>
          复制
        </el-button>
        <el-button size="small" @click="handlePlay">
          <el-icon><VideoPlay /></el-icon>
          播放片段
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { 
  Clock, Star, Warning, ChatDotRound, InfoFilled, 
  CopyDocument, VideoPlay 
} from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import type { SpeechItem } from '@/api'

const props = defineProps<{
  speech: SpeechItem
}>()

const typeLabel = computed(() => {
  switch (props.speech.type) {
    case 'highlight':
      return '爆点时刻'
    case 'issue':
      return '问题片段'
    default:
      return '普通片段'
  }
})

const emotionClass = computed(() => {
  const emotion = props.speech.emotion
  if (emotion > 0.3) return 'positive'
  if (emotion < -0.3) return 'negative'
  return 'neutral'
})

const emotionWidth = computed(() => {
  const emotion = props.speech.emotion
  // 映射 -1~1 到 0~100%
  return `${((emotion + 1) / 2) * 100}%`
})

const emotionText = computed(() => {
  const emotion = props.speech.emotion
  if (emotion > 0.5) return '非常积极'
  if (emotion > 0.3) return '积极'
  if (emotion > -0.3) return '平稳'
  if (emotion > -0.5) return '消极'
  return '非常消极'
})

function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

function handleCopy() {
  navigator.clipboard.writeText(props.speech.content)
  ElMessage.success('已复制到剪贴板')
}

function handlePlay() {
  ElMessage.info('播放功能开发中...')
  // TODO: 实现音频片段播放
}
</script>

<style scoped>
.speech-card {
  border: 1px solid #ebeef5;
  border-radius: 8px;
  overflow: hidden;
  background: #fff;
  transition: all 0.3s;
}

.speech-card:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.speech-card.type-highlight {
  border-left: 4px solid #e6a23c;
}

.speech-card.type-issue {
  border-left: 4px solid #f56c6c;
}

.speech-card.type-normal {
  border-left: 4px solid #909399;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #f5f7fa;
  border-bottom: 1px solid #ebeef5;
}

.time-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #606266;
}

.duration {
  color: #909399;
  font-size: 12px;
}

.tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.card-body {
  padding: 16px;
  display: flex;
  gap: 16px;
}

.type-badge {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5px;
  padding: 10px;
  border-radius: 8px;
  min-width: 80px;
  font-size: 12px;
  font-weight: bold;
}

.type-badge.highlight {
  background: #fdf6ec;
  color: #e6a23c;
}

.type-badge.issue {
  background: #fef0f0;
  color: #f56c6c;
}

.type-badge.normal {
  background: #f4f4f5;
  color: #909399;
}

.type-badge .el-icon {
  font-size: 24px;
}

.content {
  flex: 1;
}

.speech-text {
  margin: 0 0 15px;
  font-size: 15px;
  line-height: 1.8;
  color: #303133;
}

.suggestion {
  background: #f0f9ff;
  border: 1px solid #d9ecff;
  border-radius: 6px;
  padding: 12px;
}

.suggestion-title {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 8px;
}

.suggestion-text {
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
  color: #606266;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: #fafafa;
  border-top: 1px solid #ebeef5;
}

.emotion-indicator {
  display: flex;
  align-items: center;
  gap: 10px;
}

.emotion-label {
  font-size: 14px;
  color: #606266;
}

.emotion-bar {
  width: 150px;
  height: 8px;
  background: #ebeef5;
  border-radius: 4px;
  overflow: hidden;
  position: relative;
}

.emotion-bar::before {
  content: '';
  position: absolute;
  left: 50%;
  top: 0;
  bottom: 0;
  width: 2px;
  background: #909399;
  z-index: 1;
}

.emotion-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s;
}

.emotion-fill.positive {
  background: linear-gradient(90deg, #67c23a 0%, #95d475 100%);
  margin-left: 50%;
}

.emotion-fill.negative {
  background: linear-gradient(90deg, #f56c6c 0%, #f89898 100%);
  margin-right: 50%;
}

.emotion-fill.neutral {
  background: #909399;
  width: 50% !important;
  margin-left: 25%;
}

.emotion-value {
  font-size: 14px;
  color: #606266;
  min-width: 70px;
}

.actions {
  display: flex;
  gap: 8px;
}
</style>
