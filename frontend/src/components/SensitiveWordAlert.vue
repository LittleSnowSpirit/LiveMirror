<template>
  <div class="sensitive-word-alert" v-if="visible" :class="alertClass">
    <!-- 弹窗模式 -->
    <div v-if="mode === 'modal'" class="alert-modal" @click.self="handleClose">
      <div class="modal-content">
        <div class="modal-header" :class="severityClass">
          <i :class="iconClass"></i>
          <span class="modal-title">{{ title }}</span>
        </div>
        <div class="modal-body">
          <div v-if="hits.length > 0" class="hits-detail">
            <div v-for="(hit, index) in displayHits" :key="index" class="hit-item">
              <span class="hit-word">{{ hit.word }}</span>
              <span class="hit-severity">
                <el-tag :type="getSeverityType(hit.severity)" size="small">
                  {{ getSeverityLabel(hit.severity) }}
                </el-tag>
              </span>
              <span v-if="hit.replacement" class="hit-replacement">
                建议：{{ hit.replacement }}
              </span>
            </div>
          </div>
          <div v-if="hits.length > maxDisplay" class="more-hits">
            还有 {{ hits.length - maxDisplay }} 个敏感词...
          </div>
          <div class="hit-context" v-if="context">
            <p class="context-label">检测文本：</p>
            <p class="context-text">{{ context }}</p>
          </div>
        </div>
        <div class="modal-footer">
          <el-button v-if="!shouldBlock" @click="handleContinue">
            继续
          </el-button>
          <el-button type="primary" @click="handleModify">
            修改
          </el-button>
          <el-button v-if="shouldBlock" type="danger" @click="handleClose">
            取消
          </el-button>
        </div>
      </div>
    </div>

    <!-- 横幅模式 -->
    <div v-else-if="mode === 'banner'" class="alert-banner">
      <i :class="iconClass"></i>
      <span class="banner-text">{{ bannerMessage }}</span>
      <el-button text size="small" @click="showDetail">详情</el-button>
      <el-button text size="small" @click="handleClose">
        <i class="el-icon-close"></i>
      </el-button>
    </div>

    <!-- 内联模式 -->
    <div v-else-if="mode === 'inline'" class="alert-inline">
      <div class="inline-header">
        <i :class="iconClass"></i>
        <span class="inline-title">{{ title }}</span>
        <el-button text size="small" @click="handleClose">
          <i class="el-icon-close"></i>
        </el-button>
      </div>
      <div class="inline-content">
        <div v-if="suggestedText" class="suggestion">
          <strong>建议修改为：</strong>
          <span class="suggested-text">{{ suggestedText }}</span>
          <el-button type="primary" size="small" @click="applySuggestion">
            应用建议
          </el-button>
        </div>
        <div class="hits-summary">
          发现 {{ hits.length }} 个敏感词：
          <el-tag
            v-for="(hit, index) in hits.slice(0, 5)"
            :key="index"
            :type="getSeverityType(hit.severity)"
            size="small"
            style="margin-right: 5px;"
          >
            {{ hit.word }}
          </el-tag>
          <span v-if="hits.length > 5" class="more-count">
            等{{ hits.length }}个
          </span>
        </div>
      </div>
    </div>

    <!-- 语音转写实时预警 -->
    <div v-if="mode === 'voice'" class="alert-voice">
      <div class="voice-indicator" :class="severityClass">
        <i class="el-icon-microphone"></i>
        <span class="voice-status">
          {{ shouldBlock ? '已暂停' : '检测中' }}
        </span>
      </div>
      <div v-if="hits.length > 0" class="voice-hits">
        <el-tag
          v-for="(hit, index) in hits.slice(0, 3)"
          :key="index"
          :type="getSeverityType(hit.severity)"
          size="small"
          effect="dark"
        >
          {{ hit.word }}
        </el-tag>
        <span v-if="hits.length > 3" class="voice-more">
          +{{ hits.length - 3 }}
        </span>
      </div>
      <div class="voice-actions">
        <el-button v-if="shouldBlock" type="danger" size="small" @click="handleStopVoice">
          停止录音
        </el-button>
        <el-button size="small" @click="showDetail">查看详情</el-button>
      </div>
    </div>
  </div>

  <!-- 详情对话框 -->
  <el-dialog
    v-model="detailVisible"
    title="敏感词详情"
    width="600px"
  >
    <div class="detail-content">
      <el-table :data="hits" border style="width: 100%">
        <el-table-column prop="word" label="敏感词" width="120" />
        <el-table-column label="级别" width="100">
          <template #default="{ row }">
            <el-tag :type="getSeverityType(row.severity)" size="small">
              {{ getSeverityLabel(row.severity) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="replacement" label="替换建议" />
        <el-table-column prop="reason" label="原因" show-overflow-tooltip />
      </el-table>
      
      <div v-if="suggestedText" class="suggestion-box">
        <h4>智能替换建议：</h4>
        <el-input
          v-model="suggestedText"
          type="textarea"
          :rows="4"
        />
        <el-button type="primary" @click="applySuggestion" style="margin-top: 10px;">
          应用替换
        </el-button>
      </div>
    </div>
    <template #footer>
      <el-button @click="detailVisible = false">关闭</el-button>
      <el-button v-if="!shouldBlock" type="primary" @click="handleContinue">
        忽略并继续
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'

// Props
const props = defineProps({
  modelValue: {
    type: Boolean,
    default: false
  },
  mode: {
    type: String,
    default: 'modal', // modal, banner, inline, voice
    validator: (v) => ['modal', 'banner', 'inline', 'voice'].includes(v)
  },
  hits: {
    type: Array,
    default: () => []
  },
  context: {
    type: String,
    default: ''
  },
  suggestedText: {
    type: String,
    default: ''
  },
  maxDisplay: {
    type: Number,
    default: 5
  },
  autoClose: {
    type: Boolean,
    default: false
  },
  autoCloseDelay: {
    type: Number,
    default: 5000
  }
})

// Emits
const emit = defineEmits(['update:modelValue', 'close', 'continue', 'modify', 'apply-suggestion', 'stop-voice'])

// State
const detailVisible = ref(false)
const autoCloseTimer = ref(null)

// Computed
const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val)
})

const shouldBlock = computed(() => {
  return props.hits.some(h => h.severity === 'banned')
})

const severityClass = computed(() => {
  if (shouldBlock.value) return 'severity-banned'
  const hasSerious = props.hits.some(h => h.severity === 'serious')
  return hasSerious ? 'severity-serious' : 'severity-warning'
})

const alertClass = computed(() => {
  return `mode-${props.mode} ${severityClass.value}`
})

const iconClass = computed(() => {
  if (shouldBlock.value) return 'el-icon-error'
  const hasSerious = props.hits.some(h => h.severity === 'serious')
  return hasSerious ? 'el-icon-warning' : 'el-icon-info'
})

const title = computed(() => {
  if (shouldBlock.value) return '🚫 包含禁止内容'
  const hasSerious = props.hits.some(h => h.severity === 'serious')
  return hasSerious ? '⚠️ 包含敏感内容' : '💡 内容优化建议'
})

const bannerMessage = computed(() => {
  const count = props.hits.length
  if (shouldBlock.value) return `发现 ${count} 个禁止词汇，请修改`
  return `发现 ${count} 个敏感词，建议优化`
})

const displayHits = computed(() => {
  // 按严重程度排序
  const severityOrder = { banned: 0, serious: 1, warning: 2 }
  return [...props.hits].sort((a, b) => {
    return severityOrder[a.severity] - severityOrder[b.severity]
  })
})

// Watch
watch(() => props.modelValue, (val) => {
  if (val && props.autoClose) {
    setupAutoClose()
  } else {
    clearAutoClose()
  }
})

// Methods
function setupAutoClose() {
  clearAutoClose()
  autoCloseTimer.value = setTimeout(() => {
    handleClose()
  }, props.autoCloseDelay)
}

function clearAutoClose() {
  if (autoCloseTimer.value) {
    clearTimeout(autoCloseTimer.value)
    autoCloseTimer.value = null
  }
}

function handleClose() {
  clearAutoClose()
  visible.value = false
  emit('close')
}

function handleContinue() {
  handleClose()
  emit('continue')
}

function handleModify() {
  handleClose()
  emit('modify')
}

function showDetail() {
  detailVisible.value = true
}

function applySuggestion() {
  emit('apply-suggestion', props.suggestedText)
  handleClose()
}

function handleStopVoice() {
  emit('stop-voice')
  handleClose()
}

function getSeverityType(severity) {
  const types = {
    warning: 'warning',
    serious: 'danger',
    banned: 'danger'
  }
  return types[severity] || 'info'
}

function getSeverityLabel(severity) {
  const labels = {
    warning: '警告',
    serious: '严重',
    banned: '封禁'
  }
  return labels[severity] || severity
}
</script>

<style scoped>
.sensitive-word-alert {
  position: fixed;
  z-index: 9999;
}

/* 弹窗模式 */
.mode-modal {
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
}

.alert-modal {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-content {
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
  overflow: hidden;
}

.modal-header {
  padding: 15px 20px;
  display: flex;
  align-items: center;
  gap: 10px;
  color: white;
  font-weight: bold;
  font-size: 16px;
}

.modal-header.severity-banned {
  background: linear-gradient(135deg, #F56C6C, #E74C3C);
}

.modal-header.severity-serious {
  background: linear-gradient(135deg, #E6A23C, #F39C12);
}

.modal-header.severity-warning {
  background: linear-gradient(135deg, #409EFF, #3498DB);
}

.modal-body {
  padding: 20px;
  max-height: 400px;
  overflow-y: auto;
}

.hits-detail {
  margin-bottom: 15px;
}

.hit-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 0;
  border-bottom: 1px solid #f0f0f0;
}

.hit-word {
  font-weight: bold;
  color: #303133;
  min-width: 80px;
}

.hit-replacement {
  color: #67C23A;
  font-size: 13px;
}

.more-hits {
  text-align: center;
  color: #909399;
  font-size: 13px;
  padding: 10px;
}

.hit-context {
  margin-top: 15px;
  padding: 10px;
  background: #f5f7fa;
  border-radius: 4px;
}

.context-label {
  font-weight: bold;
  color: #606266;
  margin: 0 0 5px 0;
  font-size: 13px;
}

.context-text {
  margin: 0;
  color: #909399;
  font-size: 13px;
  line-height: 1.6;
}

.modal-footer {
  padding: 15px 20px;
  border-top: 1px solid #f0f0f0;
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

/* 横幅模式 */
.mode-banner {
  top: 20px;
  right: 20px;
}

.alert-banner {
  background: white;
  border-left: 4px solid;
  padding: 15px 20px;
  border-radius: 4px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 300px;
  max-width: 500px;
}

.mode-banner.severity-banned {
  border-left-color: #F56C6C;
}

.mode-banner.severity-serious {
  border-left-color: #E6A23C;
}

.mode-banner.severity-warning {
  border-left-color: #409EFF;
}

.banner-text {
  flex: 1;
  color: #303133;
  font-size: 14px;
}

/* 内联模式 */
.mode-inline {
  position: relative;
  top: auto;
  right: auto;
}

.alert-inline {
  background: #FEF0F0;
  border: 1px solid #FDE2E2;
  border-radius: 4px;
  padding: 15px;
  margin-bottom: 15px;
}

.inline-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 10px;
}

.inline-title {
  font-weight: bold;
  color: #F56C6C;
  font-size: 14px;
}

.inline-content {
  font-size: 13px;
  color: #606266;
}

.suggestion {
  margin-bottom: 10px;
  padding: 10px;
  background: white;
  border-radius: 4px;
}

.suggested-text {
  color: #67C23A;
  font-family: monospace;
  margin: 0 10px;
}

.hits-summary {
  line-height: 1.8;
}

.more-count {
  color: #909399;
}

/* 语音模式 */
.mode-voice {
  bottom: 20px;
  right: 20px;
}

.alert-voice {
  background: white;
  border-radius: 8px;
  padding: 15px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.15);
  min-width: 250px;
}

.voice-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 10px;
  padding: 8px;
  border-radius: 4px;
  color: white;
  font-weight: bold;
}

.voice-indicator.severity-banned {
  background: #F56C6C;
}

.voice-indicator.severity-serious {
  background: #E6A23C;
}

.voice-indicator.severity-warning {
  background: #409EFF;
}

.voice-status {
  flex: 1;
}

.voice-hits {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-bottom: 10px;
  min-height: 32px;
}

.voice-more {
  color: #909399;
  font-size: 12px;
  display: flex;
  align-items: center;
}

.voice-actions {
  display: flex;
  gap: 8px;
  justify-content: flex-end;
}

/* 详情对话框 */
.detail-content {
  max-height: 400px;
  overflow-y: auto;
}

.suggestion-box {
  margin-top: 20px;
  padding: 15px;
  background: #f5f7fa;
  border-radius: 4px;
}

.suggestion-box h4 {
  margin: 0 0 10px 0;
  color: #606266;
  font-size: 14px;
}
</style>
