<template>
  <div class="audio-uploader">
    <div
      class="upload-area"
      :class="{
        'is-dragover': isDragover,
        'is-disabled': disabled,
        'has-file': modelValue !== null,
      }"
      @dragenter.prevent="handleDragEnter"
      @dragleave.prevent="handleDragLeave"
      @dragover.prevent
      @drop.prevent="handleDrop"
      @click="handleClick"
    >
      <input
        ref="fileInput"
        type="file"
        accept="audio/*"
        :disabled="disabled"
        @change="handleFileChange"
        class="file-input"
      />
      
      <div v-if="!modelValue" class="upload-placeholder">
        <el-icon class="upload-icon"><UploadFilled /></el-icon>
        <div class="upload-text">
          <p class="main-text">点击或拖拽音频文件到此处上传</p>
          <p class="sub-text">支持 MP3、WAV、M4A 等格式，最大 500MB</p>
        </div>
      </div>
      
      <div v-else class="file-info">
        <el-icon class="file-icon"><Headset /></el-icon>
        <div class="file-details">
          <p class="file-name">{{ modelValue.name }}</p>
          <p class="file-size">{{ formatFileSize(modelValue.size) }}</p>
        </div>
        <el-button
          v-if="!disabled"
          type="danger"
          size="small"
          circle
          @click.stop="handleRemove"
        >
          <el-icon><Close /></el-icon>
        </el-button>
      </div>
    </div>
    
    <div v-if="progress > 0" class="progress-bar">
      <el-progress :percentage="progress" :status="progress === 100 ? 'success' : undefined" />
    </div>
    
    <div class="actions">
      <el-button
        type="primary"
        size="large"
        :disabled="!modelValue || disabled"
        :loading="disabled"
        @click="handleUpload"
      >
        <el-icon><Upload /></el-icon>
        开始分析
      </el-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { UploadFilled, Upload, Headset, Close } from '@element-plus/icons-vue'

const props = defineProps<{
  modelValue: File | null
  progress: number
  disabled: boolean
}>()

const emit = defineEmits<{
  'update:modelValue': [file: File | null]
  'update:progress': [progress: number]
  'upload': [file: File]
}>()

const fileInput = ref<HTMLInputElement | null>(null)
const isDragover = ref(false)

function formatFileSize(bytes: number): string {
  const mb = bytes / (1024 * 1024)
  if (mb >= 1) {
    return `${mb.toFixed(2)} MB`
  }
  const kb = bytes / 1024
  return `${kb.toFixed(2)} KB`
}

function handleDragEnter() {
  if (!props.disabled) {
    isDragover.value = true
  }
}

function handleDragLeave() {
  isDragover.value = false
}

function handleDrop(e: DragEvent) {
  isDragover.value = false
  if (props.disabled) return
  
  const files = e.dataTransfer?.files
  if (files && files.length > 0) {
    const file = files[0]
    if (file.type.startsWith('audio/')) {
      emit('update:modelValue', file)
    }
  }
}

function handleClick() {
  if (!props.disabled) {
    fileInput.value?.click()
  }
}

function handleFileChange(e: Event) {
  const target = e.target as HTMLInputElement
  const files = target.files
  if (files && files.length > 0) {
    emit('update:modelValue', files[0])
  }
}

function handleRemove() {
  emit('update:modelValue', null)
  emit('update:progress', 0)
  if (fileInput.value) {
    fileInput.value.value = ''
  }
}

function handleUpload() {
  if (props.modelValue) {
    emit('upload', props.modelValue)
  }
}

watch(() => props.progress, (newProgress) => {
  if (newProgress === 100) {
    setTimeout(() => {
      emit('update:progress', 0)
    }, 1000)
  }
})
</script>

<style scoped>
.audio-uploader {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.upload-area {
  border: 2px dashed #dcdfe6;
  border-radius: 8px;
  padding: 40px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  background: #fafafa;
}

.upload-area:hover:not(.is-disabled) {
  border-color: #409eff;
  background: #f5f7fa;
}

.upload-area.is-dragover {
  border-color: #409eff;
  background: #ecf5ff;
}

.upload-area.is-disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.upload-area.has-file {
  border-style: solid;
  border-color: #67c23a;
  background: #f0f9ff;
}

.file-input {
  display: none;
}

.upload-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 15px;
}

.upload-icon {
  font-size: 64px;
  color: #409eff;
}

.upload-text {
  color: #606266;
}

.main-text {
  font-size: 16px;
  margin: 0;
  font-weight: 500;
}

.sub-text {
  font-size: 14px;
  margin: 5px 0 0;
  color: #909399;
}

.file-info {
  display: flex;
  align-items: center;
  gap: 15px;
}

.file-icon {
  font-size: 48px;
  color: #67c23a;
}

.file-details {
  flex: 1;
  text-align: left;
}

.file-name {
  margin: 0;
  font-weight: 500;
  color: #303133;
  word-break: break-all;
}

.file-size {
  margin: 5px 0 0;
  font-size: 14px;
  color: #909399;
}

.progress-bar {
  padding: 0 10px;
}

.actions {
  display: flex;
  justify-content: center;
}
</style>
