import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { TaskStatus, AnalysisResult, SpeechItem } from '@/api'

export const useTaskStore = defineStore('task', () => {
  // 当前任务状态
  const currentTaskId = ref<string | null>(null)
  const taskStatus = ref<TaskStatus | null>(null)
  const analysisResult = ref<AnalysisResult | null>(null)
  
  // 上传进度
  const uploadProgress = ref<number>(0)
  const isUploading = ref<boolean>(false)
  
  // 筛选状态
  const filterType = ref<'all' | 'highlight' | 'issue'>('all')
  
  // 计算属性
  const filteredSpeeches = computed(() => {
    if (!analysisResult.value) return []
    
    const speeches = analysisResult.value.speeches
    if (filterType.value === 'all') return speeches
    
    return speeches.filter(speech => {
      if (filterType.value === 'highlight') return speech.type === 'highlight'
      if (filterType.value === 'issue') return speech.type === 'issue'
      return true
    })
  })
  
  const isProcessing = computed(() => {
    return taskStatus.value?.status === 'pending' || taskStatus.value?.status === 'processing'
  })
  
  const isCompleted = computed(() => {
    return taskStatus.value?.status === 'completed'
  })
  
  // 方法
  function setCurrentTask(taskId: string) {
    currentTaskId.value = taskId
  }
  
  function updateTaskStatus(status: TaskStatus) {
    taskStatus.value = status
    if (status.result) {
      analysisResult.value = status.result
    }
  }
  
  function setAnalysisResult(result: AnalysisResult) {
    analysisResult.value = result
  }
  
  function setUploadProgress(progress: number) {
    uploadProgress.value = progress
  }
  
  function setUploading(uploading: boolean) {
    isUploading.value = uploading
  }
  
  function setFilterType(type: 'all' | 'highlight' | 'issue') {
    filterType.value = type
  }
  
  function reset() {
    currentTaskId.value = null
    taskStatus.value = null
    analysisResult.value = null
    uploadProgress.value = 0
    isUploading.value = false
    filterType.value = 'all'
  }
  
  return {
    currentTaskId,
    taskStatus,
    analysisResult,
    uploadProgress,
    isUploading,
    filterType,
    filteredSpeeches,
    isProcessing,
    isCompleted,
    setCurrentTask,
    updateTaskStatus,
    setAnalysisResult,
    setUploadProgress,
    setUploading,
    setFilterType,
    reset,
  }
})
