<template>
  <div class="batch-export">
    <!-- 报告选择区域 -->
    <el-card class="selection-card">
      <template #header>
        <div class="card-header">
          <span>选择要导出的报告</span>
          <el-button
            v-if="selectedBatchIds.length > 0"
            type="info"
            link
            @click="handleSelectAll(false)"
          >
            取消全选
          </el-button>
        </div>
      </template>

      <!-- 搜索和筛选 -->
      <div class="filter-bar">
        <el-input
          v-model="searchText"
          placeholder="搜索报告名称..."
          clearable
          prefix-icon="Search"
          style="width: 300px"
        />
        <el-select
          v-model="statusFilter"
          placeholder="状态筛选"
          clearable
          style="width: 150px; margin-left: 12px"
        >
          <el-option label="全部" value="" />
          <el-option label="已完成" value="completed" />
          <el-option label="处理中" value="processing" />
          <el-option label="失败" value="failed" />
        </el-select>
      </div>

      <!-- 报告列表 -->
      <el-table
        :data="filteredBatches"
        style="width: 100%; margin-top: 16px"
        @selection-change="handleSelectionChange"
      >
        <el-table-column type="selection" width="55" />
        <el-table-column prop="batch_id" label="批次 ID" width="180" />
        <el-table-column prop="filename" label="文件名" min-width="200" />
        <el-table-column label="弹幕数量" width="100">
          <template #default="{ row }">
            {{ row.total_count || 0 }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag
              :type="row.status === 'completed' ? 'success' : row.status === 'processing' ? 'warning' : 'danger'"
              size="small"
            >
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
      </el-table>

      <!-- 批量操作按钮 -->
      <div class="batch-actions" v-if="selectedBatchIds.length > 0">
        <div class="selected-info">
          已选择 <strong>{{ selectedBatchIds.length }}</strong> 个报告
        </div>
        <div class="action-buttons">
          <el-select v-model="exportFormat" placeholder="选择格式" style="width: 150px">
            <el-option label="JSON" value="json" />
            <el-option label="Markdown" value="markdown" />
            <el-option label="PDF" value="pdf" />
          </el-select>
          <el-checkbox v-model="asyncExport" style="margin-left: 12px">
            异步导出（大文件）
          </el-checkbox>
          <el-button
            type="primary"
            :loading="isExporting"
            @click="handleBatchExport"
            style="margin-left: 12px"
          >
            <el-icon><download /></el-icon>
            开始导出
          </el-button>
        </div>
      </div>
    </el-card>

    <!-- 导出任务列表 -->
    <el-card class="tasks-card" v-if="exportTasks.length > 0">
      <template #header>
        <div class="card-header">
          <span>导出任务</span>
          <el-button type="info" link @click="refreshTasks">
            <el-icon><refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>

      <el-table :data="exportTasks" style="width: 100%">
        <el-table-column prop="task_id" label="任务 ID" width="280" />
        <el-table-column label="格式" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ row.export_format?.toUpperCase() }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="文件数" width="80">
          <template #default="{ row }">
            {{ row.file_count }}
          </template>
        </el-table-column>
        <el-table-column label="进度" width="200">
          <template #default="{ row }">
            <el-progress
              :percentage="getTaskProgress(row)"
              :status="getTaskProgressStatus(row)"
            />
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag
              :type="row.status === 'completed' ? 'success' : row.status === 'failed' ? 'danger' : 'warning'"
              size="small"
            >
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'completed' && row.download_url"
              type="success"
              link
              @click="handleDownload(row)"
            >
              <el-icon><download /></el-icon>
              下载
            </el-button>
            <el-button
              v-if="row.status === 'completed' || row.status === 'failed'"
              type="danger"
              link
              @click="handleDeleteTask(row)"
            >
              <el-icon><delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 导出历史 -->
    <el-card class="history-card">
      <template #header>
        <div class="card-header">
          <span>导出历史</span>
          <el-button type="warning" link @click="handleCleanup">
            <el-icon><delete /></el-icon>
            清理过期记录
          </el-button>
        </div>
      </template>

      <el-table :data="exportHistory" style="width: 100%">
        <el-table-column prop="task_id" label="任务 ID" width="280" />
        <el-table-column label="格式" width="100">
          <template #default="{ row }">
            <el-tag size="small">{{ row.export_format?.toUpperCase() }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="文件数" width="80">
          <template #default="{ row }">
            {{ row.file_count }}
          </template>
        </el-table-column>
        <el-table-column label="状态" width="100">
          <template #default="{ row }">
            <el-tag
              :type="row.status === 'completed' ? 'success' : row.status === 'failed' ? 'danger' : 'info'"
              size="small"
            >
              {{ getStatusText(row.status) }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="150" fixed="right">
          <template #default="{ row }">
            <el-button
              v-if="row.status === 'completed' && row.download_url"
              type="success"
              link
              @click="handleDownloadHistory(row)"
            >
              <el-icon><download /></el-icon>
              下载
            </el-button>
            <el-button
              type="danger"
              link
              @click="handleDeleteHistory(row)"
            >
              <el-icon><delete /></el-icon>
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Download, Delete, Refresh, Search } from '@element-plus/icons-vue'
import axios from 'axios'
import { getToken } from '@/utils/auth'

// API 基础 URL
const API_BASE = '/api'

// 状态
const batches = ref([])
const selectedBatchIds = ref([])
const exportFormat = ref('json')
const asyncExport = ref(false)
const isExporting = ref(false)
const exportTasks = ref([])
const exportHistory = ref([])
const searchText = ref('')
const statusFilter = ref('')

// 计算属性
const filteredBatches = computed(() => {
  return batches.value.filter(batch => {
    const matchSearch = !searchText.value || 
      batch.filename?.toLowerCase().includes(searchText.value.toLowerCase()) ||
      batch.batch_id?.toLowerCase().includes(searchText.value.toLowerCase())
    
    const matchStatus = !statusFilter.value || batch.status === statusFilter.value
    
    return matchSearch && matchStatus
  })
})

// 方法
const getStatusText = (status) => {
  const statusMap = {
    'pending': '等待中',
    'processing': '处理中',
    'completed': '已完成',
    'failed': '失败'
  }
  return statusMap[status] || status
}

const formatDate = (dateStr) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

const getTaskProgress = (task) => {
  if (task.status === 'completed') return 100
  if (task.status === 'failed') return 0
  return task.progress || 0
}

const getTaskProgressStatus = (task) => {
  if (task.status === 'completed') return 'success'
  if (task.status === 'failed') return 'exception'
  return undefined
}

const handleSelectionChange = (selection) => {
  selectedBatchIds.value = selection.map(row => row.batch_id)
}

const handleSelectAll = (selectAll) => {
  // 这个函数实际上不会被调用，因为 el-table 的选择是自动的
  // 这里只是为了代码完整性
}

const handleBatchExport = async () => {
  if (selectedBatchIds.value.length === 0) {
    ElMessage.warning('请至少选择一个报告')
    return
  }

  isExporting.value = true

  try {
    const token = getToken()
    const response = await axios.post(
      `${API_BASE}/export/batch`,
      {
        batch_ids: selectedBatchIds.value,
        export_format: exportFormat.value,
        async_export: asyncExport.value
      },
      {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      }
    )

    const { task_id, status, message } = response.data

    if (status === 'completed') {
      ElMessage.success('导出完成')
      refreshTasks()
    } else {
      ElMessage.success(`导出任务已创建：${task_id}`)
      refreshTasks()
    }

    // 清空选择
    selectedBatchIds.value = []
  } catch (error) {
    console.error('导出失败:', error)
    ElMessage.error(error.response?.data?.detail || '导出失败')
  } finally {
    isExporting.value = false
  }
}

const refreshTasks = async () => {
  try {
    const token = getToken()
    const [tasksResponse, historyResponse] = await Promise.all([
      axios.get(`${API_BASE}/export/history?limit=20`, {
        headers: { 'Authorization': `Bearer ${token}` }
      }),
      axios.get(`${API_BASE}/export/history?limit=50`, {
        headers: { 'Authorization': `Bearer ${token}` }
      })
    ])

    // 这里简化处理，实际应该从不同的接口获取任务和历史
    exportTasks.value = tasksResponse.data.items || []
    exportHistory.value = historyResponse.data.items || []
  } catch (error) {
    console.error('刷新任务列表失败:', error)
  }
}

const handleDownload = async (task) => {
  if (!task.download_url) {
    ElMessage.warning('下载链接不可用')
    return
  }

  try {
    const token = getToken()
    const response = await axios.get(`${API_BASE}${task.download_url}`, {
      headers: { 'Authorization': `Bearer ${token}` },
      responseType: 'blob'
    })

    // 创建下载链接
    const blob = new Blob([response.data], { type: 'application/octet-stream' })
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    
    // 从 download_url 提取文件名
    const filename = task.download_url.split('/').pop() || 'export.zip'
    link.download = filename
    
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    ElMessage.success('下载已开始')
  } catch (error) {
    console.error('下载失败:', error)
    ElMessage.error('下载失败')
  }
}

const handleDownloadHistory = async (record) => {
  await handleDownload(record)
}

const handleDeleteTask = async (task) => {
  try {
    await ElMessageBox.confirm('确定要删除此导出记录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const token = getToken()
    await axios.delete(`${API_BASE}/export/history/${task.task_id}`, {
      headers: { 'Authorization': `Bearer ${token}` }
    })

    ElMessage.success('记录已删除')
    refreshTasks()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除失败:', error)
      ElMessage.error('删除失败')
    }
  }
}

const handleDeleteHistory = async (record) => {
  await handleDeleteTask(record)
}

const handleCleanup = async () => {
  try {
    await ElMessageBox.confirm('确定要清理 7 天前的导出记录吗？', '提示', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    const token = getToken()
    const response = await axios.post(
      `${API_BASE}/export/cleanup?days=7`,
      {},
      {
        headers: { 'Authorization': `Bearer ${token}` }
      }
    )

    ElMessage.success(response.data.message)
    refreshTasks()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('清理失败:', error)
      ElMessage.error('清理失败')
    }
  }
}

const loadBatches = async () => {
  // 加载批次列表（实际项目中应该有专门的接口）
  // 这里模拟数据
  try {
    const token = getToken()
    // 实际应该调用获取批次列表的 API
    // const response = await axios.get(`${API_BASE}/danmu/batches`, {
    //   headers: { 'Authorization': `Bearer ${token}` }
    // })
    // batches.value = response.data.items || []
    
    // 模拟数据用于测试
    batches.value = [
      {
        batch_id: 'batch_001',
        filename: '直播回放_20240101.json',
        total_count: 1250,
        status: 'completed',
        created_at: '2024-01-01T10:00:00Z'
      },
      {
        batch_id: 'batch_002',
        filename: '直播回放_20240102.json',
        total_count: 890,
        status: 'completed',
        created_at: '2024-01-02T14:30:00Z'
      },
      {
        batch_id: 'batch_003',
        filename: '直播回放_20240103.json',
        total_count: 2100,
        status: 'completed',
        created_at: '2024-01-03T09:15:00Z'
      }
    ]
  } catch (error) {
    console.error('加载批次列表失败:', error)
  }
}

// 生命周期
onMounted(() => {
  loadBatches()
  refreshTasks()
})
</script>

<style scoped>
.batch-export {
  max-width: 1400px;
  margin: 0 auto;
  padding: 20px;
}

.selection-card,
.tasks-card,
.history-card {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filter-bar {
  display: flex;
  align-items: center;
  margin-bottom: 16px;
}

.batch-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 16px;
  padding: 12px;
  background-color: var(--el-fill-color-light);
  border-radius: 4px;
}

.selected-info {
  font-size: 14px;
  color: var(--el-text-color-regular);
}

.selected-info strong {
  color: var(--el-color-primary);
  font-size: 16px;
}

.action-buttons {
  display: flex;
  align-items: center;
}

:deep(.el-table) {
  margin-top: 16px;
}

:deep(.el-progress) {
  width: 100%;
}
</style>
