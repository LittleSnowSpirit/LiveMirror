<template>
  <div class="task-status">
    <div v-if="status === 'pending'" class="status-pending">
      <el-icon class="status-icon spinning"><Loading /></el-icon>
      <div class="status-info">
        <p class="status-title">等待处理...</p>
        <p class="status-message">任务已提交，请稍候</p>
      </div>
    </div>
    
    <div v-else-if="status === 'processing'" class="status-processing">
      <el-icon class="status-icon spinning"><VideoCamera /></el-icon>
      <div class="status-info">
        <p class="status-title">正在分析中...</p>
        <p class="status-message">{{ message || '语音转写与 AI 分析进行中' }}</p>
        <el-progress
          :percentage="progress"
          :format="formatProgress"
          class="progress-bar"
        />
      </div>
    </div>
    
    <div v-else-if="status === 'completed'" class="status-completed">
      <el-icon class="status-icon success"><CircleCheck /></el-icon>
      <div class="status-info">
        <p class="status-title">分析完成!</p>
        <p class="status-message">点击查看详细报告</p>
        <el-button type="primary" @click="handleViewReport">
          <el-icon><View /></el-icon>
          查看报告
        </el-button>
      </div>
    </div>
    
    <div v-else-if="status === 'failed'" class="status-failed">
      <el-icon class="status-icon error"><CircleClose /></el-icon>
      <div class="status-info">
        <p class="status-title">分析失败</p>
        <p class="status-message">{{ message || '请稍后重试' }}</p>
        <el-button type="primary" @click="handleRetry">
          <el-icon><Refresh /></el-icon>
          重试
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed, watch } from 'vue'
import { 
  Loading, VideoCamera, CircleCheck, CircleClose, View, Refresh 
} from '@element-plus/icons-vue'
import { getTaskStatus } from '@/api'
import type { TaskStatus as TaskStatusType } from '@/api'

const props = defineProps<{
  taskId: string
}>()

// WebSocket 连接
let ws: WebSocket | null = null

function connectWebSocket() {
  const wsUrl = `ws://localhost:8000/ws/task/${props.taskId}`
  ws = new WebSocket(wsUrl)
  
  ws.onopen = () => {
    console.log('WebSocket 已连接')
    // 发送心跳
    setInterval(() => {
      if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send('ping')
      }
    }, 30000)
  }
  
  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data)
      console.log('收到任务更新:', data)
      
      if (data.status) {
        emit('status-update', data)
      }
    } catch (e) {
      console.error('解析消息失败:', e)
    }
  }
  
  ws.onerror = (error) => {
    console.error('WebSocket 错误:', error)
  }
  
  ws.onclose = () => {
    console.log('WebSocket 已断开')
    // 重连逻辑
    setTimeout(() => {
      if (props.taskId && !taskCompleted.value) {
        connectWebSocket()
      }
    }, 5000)
  }
}

onMounted(() => {
  connectWebSocket()
})

onBeforeUnmount(() => {
  if (ws) {
    ws.close()
    ws = null
  }
})

const emit = defineEmits<{
  'completed': []
  'failed': [error: string]
}>()

const statusData = ref<TaskStatusType | null>(null)
const pollTimer = ref<number | null>(null)

const status = computed(() => statusData.value?.status || 'pending')
const progress = computed(() => statusData.value?.progress || 0)
const message = computed(() => statusData.value?.message || '')

function formatProgress(percentage: number) {
  if (percentage === 100) {
    return '完成'
  }
  return `${percentage}%`
}

async function pollStatus() {
  try {
    const data = await getTaskStatus(props.taskId)
    statusData.value = data
    
    if (data.status === 'completed') {
      stopPolling()
      emit('completed')
    } else if (data.status === 'failed') {
      stopPolling()
      emit('failed', data.message || '分析失败')
    }
  } catch (e: any) {
    console.error('Polling error:', e)
    statusData.value = {
      taskId: props.taskId,
      status: 'failed',
      progress: 0,
      message: e.response?.data?.message || '查询状态失败',
    }
    stopPolling()
  }
}

function startPolling() {
  pollStatus()
  pollTimer.value = window.setInterval(pollStatus, 2000) // 每 2 秒轮询
}

function stopPolling() {
  if (pollTimer.value) {
    clearInterval(pollTimer.value)
    pollTimer.value = null
  }
}

function handleViewReport() {
  emit('completed')
}

function handleRetry() {
  statusData.value = null
  startPolling()
}

watch(() => props.taskId, (newTaskId) => {
  if (newTaskId) {
    statusData.value = null
    startPolling()
  }
}, { immediate: true })

onMounted(() => {
  if (props.taskId) {
    startPolling()
  }
})

onBeforeUnmount(() => {
  stopPolling()
})
</script>

<style scoped>
.task-status {
  padding: 30px;
  text-align: center;
}

.status-icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.status-icon.spinning {
  animation: spin 1.5s linear infinite;
  color: #409eff;
}

.status-icon.success {
  color: #67c23a;
}

.status-icon.error {
  color: #f56c6c;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.status-info {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
}

.status-title {
  font-size: 20px;
  font-weight: bold;
  color: #303133;
  margin: 0;
}

.status-message {
  font-size: 14px;
  color: #606266;
  margin: 0;
}

.progress-bar {
  width: 100%;
  max-width: 400px;
  margin-top: 15px;
}
</style>
