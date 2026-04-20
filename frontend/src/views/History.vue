<template>
  <div class="history-page">
    <el-card class="history-card">
      <template #header>
        <div class="card-header">
          <el-icon><Document /></el-icon>
          <span>历史记录</span>
          <el-button type="primary" @click="loadHistory" :loading="loading">
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>
      
      <div v-loading="loading" class="history-content">
        <el-table
          v-if="historyList.length > 0"
          :data="historyList"
          style="width: 100%"
          :default-sort="{ prop: 'createdAt', order: 'descending' }"
        >
          <el-table-column prop="filename" label="文件名" min-width="200" />
          <el-table-column prop="duration" label="时长" width="100">
            <template #default="{ row }">
              {{ formatDuration(row.duration) }}
            </template>
          </el-table-column>
          <el-table-column prop="status" label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.status === 'completed' ? 'success' : 'danger'">
                {{ row.status === 'completed' ? '已完成' : '失败' }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="createdAt" label="创建时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.createdAt) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <el-button
                v-if="row.status === 'completed'"
                type="primary"
                size="small"
                @click="viewReport(row.taskId)"
              >
                查看报告
              </el-button>
              <el-button
                type="danger"
                size="small"
                @click="deleteTask(row.taskId)"
              >
                删除
              </el-button>
            </template>
          </el-table-column>
        </el-table>
        
        <el-empty v-else description="暂无历史记录" />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Document, Refresh } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getHistory, deleteTask } from '@/api'
import type { HistoryItem } from '@/api'

const router = useRouter()

const loading = ref(false)
const historyList = ref<HistoryItem[]>([])

function formatDuration(seconds?: number): string {
  if (!seconds) return '-'
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  })
}

async function loadHistory() {
  try {
    loading.value = true
    historyList.value = await getHistory()
  } catch (e: any) {
    ElMessage.error('加载历史记录失败')
  } finally {
    loading.value = false
  }
}

function viewReport(taskId: string) {
  router.push(`/report/${taskId}`)
}

async function deleteTaskById(taskId: string) {
  try {
    await ElMessageBox.confirm('确定要删除这个任务吗？', '确认删除', {
      type: 'warning',
    })
    
    await deleteTask(taskId)
    ElMessage.success('删除成功')
    loadHistory()
  } catch (e: any) {
    if (e !== 'cancel') {
      ElMessage.error('删除失败')
    }
  }
}

onMounted(() => {
  loadHistory()
})
</script>

<style scoped>
.history-page {
  max-width: 1200px;
  margin: 0 auto;
}

.history-card {
  background: rgba(255, 255, 255, 0.95);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header .card-header > span {
  font-size: 18px;
  font-weight: bold;
}

.history-content {
  min-height: 400px;
}
</style>
