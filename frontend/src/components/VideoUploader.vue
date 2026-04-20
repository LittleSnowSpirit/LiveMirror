<template>
  <div class="video-uploader">
    <!-- 文件选择区域 -->
    <el-upload
      ref="uploadRef"
      class="upload-area"
      drag
      :auto-upload="false"
      :on-change="handleFileChange"
      :on-remove="handleFileRemove"
      :file-list="fileList"
      :accept="acceptedFormats"
      :limit="1"
    >
      <el-icon class="el-icon--upload"><video-camera /></el-icon>
      <div class="el-upload__text">
        拖拽视频文件到此处或<em>点击选择</em>
      </div>
      <template #tip>
        <div class="el-upload__tip">
          支持格式：MP4, AVI, MOV, MKV | 最大 2GB
        </div>
      </template>
    </el-upload>

    <!-- 文件信息卡片 -->
    <div v-if="currentFile" class="file-info-card">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>视频信息</span>
            <el-button
              v-if="!isUploading && !uploadSuccess"
              type="danger"
              size="small"
              @click="handleRemoveFile"
            >
              <el-icon><delete /></el-icon>
              删除
            </el-button>
          </div>
        </template>
        
        <div class="info-grid">
          <div class="info-item">
            <span class="label">文件名:</span>
            <span class="value">{{ currentFile.name }}</span>
          </div>
          <div class="info-item">
            <span class="label">文件大小:</span>
            <span class="value">{{ formatFileSize(currentFile.size) }}</span>
          </div>
          <div class="info-item" v-if="videoDuration">
            <span class="label">视频时长:</span>
            <span class="value">{{ formatDuration(videoDuration) }}</span>
          </div>
          <div class="info-item">
            <span class="label">格式:</span>
            <span class="value">{{ currentFile.name.split('.').pop()?.toUpperCase() }}</span>
          </div>
        </div>

        <!-- 上传进度 -->
        <div v-if="isUploading" class="progress-section">
          <el-progress
            :percentage="uploadProgress"
            :status="uploadStatus"
            :stroke-width="20"
          >
            <template #default="{ percentage }">
              <span class="progress-value">{{ percentage }}%</span>
            </template>
          </el-progress>
          <div class="progress-text">
            <span v-if="uploadStatus === 'uploading'">正在上传...</span>
            <span v-if="uploadStatus === 'success'">上传成功！</span>
            <span v-if="uploadStatus === 'exception'">上传失败</span>
          </div>
        </div>

        <!-- 处理状态 -->
        <div v-if="uploadSuccess && processingInfo" class="processing-section">
          <el-alert
            :title="processingInfo.title"
            :type="processingInfo.type"
            :closable="false"
            show-icon
          >
            <template #default>
              <div class="processing-details">
                <div v-if="processingInfo.audioExtracted">
                  ✓ 音频已提取
                </div>
                <div v-if="processingInfo.transcribing">
                  <el-icon class="is-loading"><loading /></el-icon>
                  正在转写分析...
                </div>
                <div v-if="processingInfo.transcriptionComplete">
                  ✓ 转写完成
                </div>
                <div class="processing-time" v-if="processingInfo.processingTime">
                  处理耗时：{{ processingInfo.processingTime }}s
                </div>
              </div>
            </template>
          </el-alert>
        </div>

        <!-- 转写结果预览 -->
        <div v-if="transcriptionResult" class="transcription-section">
          <el-divider>转写结果</el-divider>
          <div class="transcription-text">
            {{ transcriptionResult.text }}
          </div>
          <div class="transcription-meta">
            <el-tag size="small" type="info">
              模型：{{ transcriptionResult.model_size }}
            </el-tag>
            <el-tag size="small" type="info">
              语言：{{ transcriptionResult.language }}
            </el-tag>
            <el-tag size="small" type="info">
              耗时：{{ transcriptionResult.processing_time }}s
            </el-tag>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 上传按钮 -->
    <div v-if="currentFile && !isUploading && !uploadSuccess" class="upload-actions">
      <el-button
        type="primary"
        size="large"
        :loading="isUploading"
        @click="handleUpload"
      >
        <el-icon><upload /></el-icon>
        开始上传
      </el-button>
    </div>

    <!-- 重新上传按钮 -->
    <div v-if="uploadSuccess" class="upload-actions">
      <el-button
        type="primary"
        size="large"
        @click="handleReset"
      >
        <el-icon><refresh /></el-icon>
        上传另一个视频
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  VideoCamera, 
  Upload, 
  Delete, 
  Refresh,
  Loading
} from '@element-plus/icons-vue'

// Props
const props = defineProps({
  uploadUrl: {
    type: String,
    default: '/api/upload/video'
  },
  maxFileSize: {
    type: Number,
    default: 2048 // MB
  },
  autoTranscribe: {
    type: Boolean,
    default: true
  }
})

// Emits
const emit = defineEmits(['upload-success', 'upload-error', 'transcription-complete'])

// State
const uploadRef = ref()
const fileList = ref([])
const currentFile = ref(null)
const isUploading = ref(false)
const uploadProgress = ref(0)
const uploadStatus = ref(null) // 'uploading', 'success', 'exception'
const uploadSuccess = ref(false)
const videoDuration = ref(null)
const processingInfo = ref(null)
const transcriptionResult = ref(null)

// Computed
const acceptedFormats = computed(() => {
  return '.mp4,.avi,.mov,.mkv'
})

// Methods
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDuration = (seconds) => {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

const handleFileChange = (file, fileList) => {
  // 检查文件大小
  if (file.size && file.size > props.maxFileSize * 1024 * 1024) {
    ElMessage.warning(`文件超过最大限制 ${props.maxFileSize}MB`)
    uploadRef.value?.handleRemove(file)
    return
  }

  // 检查文件格式
  const ext = file.name.split('.').pop()?.toLowerCase()
  const supportedFormats = ['mp4', 'avi', 'mov', 'mkv']
  if (!supportedFormats.includes(ext)) {
    ElMessage.warning(`不支持的视频格式：${ext}`)
    uploadRef.value?.handleRemove(file)
    return
  }

  currentFile.value = file
  uploadSuccess.value = false
  processingInfo.value = null
  transcriptionResult.value = null
  
  ElMessage.success(`已选择文件：${file.name}`)
}

const handleFileRemove = (file) => {
  if (isUploading.value) {
    ElMessage.warning('上传中，无法删除')
    return
  }
  
  currentFile.value = null
  fileList.value = []
  videoDuration.value = null
  uploadSuccess.value = false
  processingInfo.value = null
  transcriptionResult.value = null
  
  ElMessage.info('已移除文件')
}

const handleRemoveFile = () => {
  handleFileRemove()
}

const handleUpload = async () => {
  if (!currentFile.value || !currentFile.value.raw) {
    ElMessage.error('请先选择视频文件')
    return
  }

  isUploading.value = true
  uploadProgress.value = 0
  uploadStatus.value = 'uploading'

  const formData = new FormData()
  formData.append('file', currentFile.value.raw)

  const xhr = new XMLHttpRequest()

  // 上传进度监听
  xhr.upload.addEventListener('progress', (event) => {
    if (event.lengthComputable) {
      const progress = Math.round((event.loaded * 100) / event.total)
      uploadProgress.value = progress
    }
  })

  // 上传完成
  xhr.addEventListener('load', async () => {
    isUploading.value = false

    if (xhr.status >= 200 && xhr.status < 300) {
      uploadStatus.value = 'success'
      uploadSuccess.value = true
      uploadProgress.value = 100

      try {
        const response = JSON.parse(xhr.responseText)
        
        // 更新视频信息
        if (response.duration) {
          videoDuration.value = response.duration
        }

        // 更新处理信息
        processingInfo.value = {
          title: '视频处理中',
          type: 'info',
          audioExtracted: response.audio_extracted,
          transcribing: response.audio_extracted,
          transcriptionComplete: false,
          processingTime: response.processing_time?.toFixed(2)
        }

        emit('upload-success', response)
        ElMessage.success('视频上传成功！')

        // 如果有转写结果，显示出来
        if (response.transcription) {
          transcriptionResult.value = response.transcription
          processingInfo.value.transcribing = false
          processingInfo.value.transcriptionComplete = true
          processingInfo.value.title = '转写完成'
          processingInfo.value.type = 'success'
          emit('transcription-complete', response.transcription)
        }

      } catch (e) {
        console.error('解析响应失败:', e)
        ElMessage.success('视频上传成功')
      }
    } else {
      uploadStatus.value = 'exception'
      let errorMessage = '上传失败'
      try {
        const error = JSON.parse(xhr.responseText)
        errorMessage = error.detail || errorMessage
      } catch (e) {
        // 忽略解析错误
      }
      ElMessage.error(errorMessage)
      emit('upload-error', new Error(errorMessage))
    }
  })

  // 上传错误
  xhr.addEventListener('error', () => {
    isUploading.value = false
    uploadStatus.value = 'exception'
    ElMessage.error('网络错误')
    emit('upload-error', new Error('网络错误'))
  })

  // 发送请求
  xhr.open('POST', props.uploadUrl)
  xhr.send(formData)
}

const handleReset = () => {
  currentFile.value = null
  fileList.value = []
  uploadSuccess.value = false
  processingInfo.value = null
  transcriptionResult.value = null
  videoDuration.value = null
  uploadRef.value?.clearFiles()
}

// 暴露方法给父组件
defineExpose({
  reset: handleReset,
  getFile: () => currentFile.value
})
</script>

<style scoped>
.video-uploader {
  width: 100%;
  max-width: 800px;
  margin: 0 auto;
}

.upload-area {
  width: 100%;
  margin-bottom: 20px;
}

.upload-area :deep(.el-upload) {
  width: 100%;
}

.upload-area :deep(.el-upload-dragger) {
  width: 100%;
  padding: 40px 20px;
}

.el-icon--upload {
  font-size: 64px;
  color: var(--el-color-primary);
  margin-bottom: 16px;
}

.file-info-card {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
  margin-bottom: 20px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.label {
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.value {
  color: var(--el-text-color-primary);
  font-weight: 500;
  word-break: break-all;
}

.progress-section {
  margin-top: 20px;
}

.progress-value {
  font-weight: bold;
  color: var(--el-color-primary);
}

.progress-text {
  text-align: center;
  margin-top: 8px;
  color: var(--el-text-color-secondary);
  font-size: 14px;
}

.processing-section {
  margin-top: 20px;
}

.processing-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 14px;
}

.processing-time {
  margin-top: 8px;
  color: var(--el-text-color-secondary);
  font-size: 12px;
}

.transcription-section {
  margin-top: 20px;
}

.transcription-text {
  background: var(--el-fill-color-light);
  padding: 16px;
  border-radius: 4px;
  max-height: 300px;
  overflow-y: auto;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-all;
}

.transcription-meta {
  margin-top: 12px;
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.upload-actions {
  text-align: center;
  margin-top: 30px;
}
</style>
