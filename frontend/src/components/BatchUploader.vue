<template>
  <div class="batch-uploader">
    <!-- 文件选择区域 -->
    <el-upload
      ref="uploadRef"
      class="upload-area"
      drag
      multiple
      :auto-upload="false"
      :on-change="handleFileChange"
      :on-remove="handleFileRemove"
      :file-list="fileList"
    >
      <el-icon class="el-icon--upload"><upload-filled /></el-icon>
      <div class="el-upload__text">
        拖拽文件到此处或<em>点击选择</em>
      </div>
      <template #tip>
        <div class="el-upload__tip">
          支持多文件选择，一次可选择多个文件
        </div>
      </template>
    </el-upload>

    <!-- 批量操作按钮 -->
    <div v-if="fileList.length > 0" class="batch-actions">
      <el-button
        type="primary"
        :loading="isUploadingAll"
        @click="handleUploadAll"
      >
        <el-icon><upload /></el-icon>
        全部开始上传
      </el-button>
      <el-button
        type="danger"
        :disabled="isUploadingAll"
        @click="handleRemoveAll"
      >
        <el-icon><delete /></el-icon>
        全部删除
      </el-button>
    </div>

    <!-- 文件列表和进度 -->
    <div v-if="fileList.length > 0" class="file-list">
      <div class="file-list-header">
        <span>已选择 {{ fileList.length }} 个文件</span>
        <span v-if="totalProgress > 0">
          总进度：{{ totalProgress.toFixed(1) }}%
        </span>
      </div>

      <el-table :data="fileList" style="width: 100%">
        <el-table-column prop="name" label="文件名" min-width="200" />
        <el-table-column label="大小" width="100">
          <template #default="{ row }">
            {{ formatFileSize(row.size) }}
          </template>
        </el-table-column>
        <el-table-column label="进度" width="200">
          <template #default="{ row }">
            <el-progress
              :percentage="row.progress || 0"
              :status="row.status"
              :stroke-width="18"
            />
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag v-if="row.status === 'success'" type="success" size="small">
              完成
            </el-tag>
            <el-tag v-else-if="row.status === 'fail'" type="danger" size="small">
              失败
            </el-tag>
            <el-tag v-else-if="row.status === 'uploading'" type="warning" size="small">
              上传中
            </el-tag>
            <el-tag v-else type="info" size="small">
              待上传
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="100" fixed="right">
          <template #default="{ row, $index }">
            <el-button
              v-if="!row.status || row.status === 'ready' || row.status === 'fail'"
              type="primary"
              link
              size="small"
              :disabled="isUploadingAll"
              @click="handleUploadSingle(row, $index)"
            >
              上传
            </el-button>
            <el-button
              v-else-if="row.status === 'success'"
              type="success"
              link
              size="small"
              @click="handleFileRemove(null, row)"
            >
              删除
            </el-button>
            <el-button
              v-else-if="row.status === 'uploading'"
              type="danger"
              link
              size="small"
              @click="handleCancelUpload(row, $index)"
            >
              取消
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { UploadUserFile, UploadProgressEvent } from 'element-plus'
import { UploadFilled, Upload, Delete } from '@element-plus/icons-vue'

export interface FileWithProgress extends UploadUserFile {
  progress?: number
  status?: 'ready' | 'uploading' | 'success' | 'fail'
  abort?: () => void
}

// Props
const props = defineProps<{
  uploadUrl?: string
  maxFileSize?: number // MB
}>()

// Emits
const emit = defineEmits<{
  (e: 'upload-success', file: FileWithProgress, response: any): void
  (e: 'upload-error', file: FileWithProgress, error: Error): void
  (e: 'upload-progress', file: FileWithProgress, progress: number): void
}>()

// State
const uploadRef = ref()
const fileList = ref<FileWithProgress[]>([])
const isUploadingAll = ref(false)
const uploadingCount = ref(0)

// Computed
const totalProgress = computed(() => {
  if (fileList.value.length === 0) return 0
  const total = fileList.value.reduce((sum, file) => sum + (file.progress || 0), 0)
  return total / fileList.value.length
})

// Methods
const formatFileSize = (bytes: number): string => {
  if (bytes === 0) return '0 B'
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const handleFileChange = (file: FileWithProgress, fileList: UploadUserFile[]) => {
  // 检查文件大小
  if (props.maxFileSize && file.size && file.size > props.maxFileSize * 1024 * 1024) {
    ElMessage.warning(`文件 ${file.name} 超过最大限制 ${props.maxFileSize}MB，已自动移除`)
    uploadRef.value?.handleRemove(file)
    return
  }

  // 初始化文件状态
  file.progress = 0
  file.status = 'ready'
  
  ElMessage.success(`已添加文件：${file.name}`)
}

const handleFileRemove = (_: any, file: FileWithProgress) => {
  // 如果文件正在上传，取消上传
  if (file.abort) {
    file.abort()
  }
  
  const index = fileList.value.findIndex(f => f.uid === file.uid)
  if (index > -1) {
    fileList.value.splice(index, 1)
    ElMessage.info(`已移除文件：${file.name}`)
  }
}

const handleCancelUpload = (file: FileWithProgress, index: number) => {
  if (file.abort) {
    file.abort()
    file.progress = 0
    file.status = 'ready'
    ElMessage.info(`已取消上传：${file.name}`)
  }
}

const uploadFile = async (file: FileWithProgress, index: number) => {
  if (!file.raw) return
  
  uploadingCount.value++
  file.progress = 0
  file.status = 'uploading'
  
  const formData = new FormData()
  formData.append('file', file.raw)
  
  const xhr = new XMLHttpRequest()
  let uploadComplete = false
  
  // 上传进度监听
  xhr.upload.addEventListener('progress', (event: ProgressEvent) => {
    if (event.lengthComputable) {
      const progress = Math.round((event.loaded * 100) / event.total)
      file.progress = progress
      emit('upload-progress', file, progress)
    }
  })
  
  // 上传完成
  xhr.addEventListener('load', () => {
    uploadComplete = true
    uploadingCount.value--
    
    if (xhr.status >= 200 && xhr.status < 300) {
      file.status = 'success'
      file.progress = 100
      try {
        const response = JSON.parse(xhr.responseText)
        emit('upload-success', file, response)
        ElMessage.success(`文件 ${file.name} 上传成功`)
      } catch (e) {
        emit('upload-success', file, xhr.responseText)
        ElMessage.success(`文件 ${file.name} 上传成功`)
      }
    } else {
      file.status = 'fail'
      const error = new Error(`上传失败：${xhr.statusText}`)
      emit('upload-error', file, error)
      ElMessage.error(`文件 ${file.name} 上传失败`)
    }
  })
  
  // 上传错误
  xhr.addEventListener('error', () => {
    uploadComplete = true
    uploadingCount.value--
    file.status = 'fail'
    const error = new Error('网络错误')
    emit('upload-error', file, error)
    ElMessage.error(`文件 ${file.name} 上传失败`)
  })
  
  // 上传取消
  xhr.addEventListener('abort', () => {
    uploadComplete = true
    uploadingCount.value--
    file.progress = 0
    file.status = 'ready'
    ElMessage.info(`文件 ${file.name} 已取消上传`)
  })
  
  // 发送请求
  const uploadUrl = props.uploadUrl || '/api/upload'
  xhr.open('POST', uploadUrl)
  xhr.send(formData)
  
  // 保存取消方法
  file.abort = () => {
    if (!uploadComplete) {
      xhr.abort()
    }
  }
}

const handleUploadSingle = (file: FileWithProgress, index: number) => {
  uploadFile(file, index)
}

const handleUploadAll = async () => {
  const pendingFiles = fileList.value.filter(f => 
    !f.status || f.status === 'ready' || f.progress! < 100 || f.status === 'fail'
  )
  
  if (pendingFiles.length === 0) {
    ElMessage.info('所有文件已完成上传')
    return
  }
  
  isUploadingAll.value = true
  
  // 并发上传（限制同时上传数量）
  const concurrentLimit = 3
  const queue = [...pendingFiles]
  const running: Promise<void>[] = []
  
  const processQueue = async () => {
    while (queue.length > 0) {
      const file = queue.shift()!
      const index = fileList.value.findIndex(f => f.uid === file.uid)
      if (index > -1) {
        await uploadFile(file, index)
      }
    }
  }
  
  // 启动并发任务
  const tasks = Array(Math.min(concurrentLimit, queue.length))
    .fill(null)
    .map(() => processQueue())
  
  await Promise.all(tasks)
  
  isUploadingAll.value = false
  
  // 检查是否全部成功
  const allSuccess = fileList.value.every(f => f.status === 'success')
  if (allSuccess) {
    ElMessage.success('所有文件上传成功！')
  } else {
    const failedCount = fileList.value.filter(f => f.status === 'fail').length
    ElMessage.warning(`上传完成，${failedCount} 个文件失败`)
  }
}

const handleRemoveAll = async () => {
  try {
    await ElMessageBox.confirm('确定要删除所有文件吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    fileList.value.forEach(file => {
      if (file.abort) {
        file.abort()
      }
    })
    
    fileList.value = []
    ElMessage.success('已删除所有文件')
  } catch {
    // 用户取消
  }
}

// 暴露方法给父组件
defineExpose({
  clearFiles: () => {
    fileList.value = []
  },
  getFiles: () => fileList.value
})
</script>

<style scoped>
.batch-uploader {
  width: 100%;
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
}

.batch-actions {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  padding: 12px;
  background-color: var(--el-fill-color-light);
  border-radius: 4px;
}

.file-list {
  margin-top: 20px;
}

.file-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
  padding: 8px 12px;
  background-color: var(--el-fill-color-light);
  border-radius: 4px;
  font-weight: 500;
}

.file-list-header span:last-child {
  color: var(--el-color-primary);
}
</style>
