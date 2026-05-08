<template>
  <div class="history-page">
    <el-card class="panel">
      <p class="kicker">历史</p>
      <h1>历史记录</h1>

      <div class="toolbar">
        <el-input
          v-model="searchQuery"
          placeholder="搜索文件名"
          clearable
          class="search-input"
          @input="handleSearch"
        />
        <el-select v-model="statusFilter" placeholder="全部状态" clearable @change="handleFilter">
          <el-option label="排队中" value="pending" />
          <el-option label="转写中" value="transcribing" />
          <el-option label="分析中" value="analyzing" />
          <el-option label="已完成" value="completed" />
          <el-option label="失败" value="failed" />
        </el-select>
        <el-button
          v-if="selectedIds.length > 0"
          type="primary"
          @click="handleBatchExport"
        >
          批量导出 ({{ selectedIds.length }})
        </el-button>
      </div>

      <div v-if="taskStore.loading" class="loading-state">
        <el-skeleton :rows="5" animated />
      </div>

      <div v-else-if="taskStore.tasks.length === 0" class="empty-state">
        <el-empty description="暂无历史记录" />
      </div>

      <div v-else class="task-list">
        <div
          v-for="task in taskStore.tasks"
          :key="task.task_id"
          class="task-card"
          :class="{ selected: selectedIds.includes(task.task_id) }"
        >
          <div class="task-card-header">
            <input
              type="checkbox"
              class="task-checkbox"
              :checked="selectedIds.includes(task.task_id)"
              @change="toggleSelect(task.task_id)"
            />
            <div class="task-info">
              <p class="task-filename">{{ task.filename }}</p>
              <p class="task-meta">
                <span>{{ formatTime(task.created_at) }}</span>
                <span v-if="task.duration"> / {{ formatDuration(task.duration) }}</span>
              </p>
            </div>
            <el-tag :type="statusType(task.status)" size="small">
              {{ statusLabel(task.status) }}
            </el-tag>
          </div>

          <el-progress
            v-if="task.status !== 'completed' && task.status !== 'failed'"
            :percentage="task.progress"
            :stroke-width="6"
            class="task-progress"
          />

          <div class="task-actions">
            <el-button size="small" type="primary" text @click="viewReport(task.task_id)">
              查看报告
            </el-button>
            <el-button size="small" type="danger" text @click="handleDelete(task.task_id)">
              删除
            </el-button>
          </div>
        </div>
      </div>

      <div v-if="taskStore.total > taskStore.pageSize" class="pagination-wrap">
        <el-pagination
          v-model:current-page="currentPage"
          :page-size="taskStore.pageSize"
          :total="taskStore.total"
          layout="prev, pager, next"
          @current-change="handlePageChange"
        />
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { useTaskStore } from '../stores/task';

const router = useRouter();
const taskStore = useTaskStore();

const searchQuery = ref('');
const statusFilter = ref('');
const selectedIds = ref<string[]>([]);
const currentPage = ref(1);

onMounted(() => {
  loadTasks();
});

function loadTasks() {
  const params: Record<string, unknown> = {
    page: currentPage.value,
    page_size: 20,
  };
  if (statusFilter.value) params.status = statusFilter.value;
  if (searchQuery.value) params.search = searchQuery.value;
  taskStore.fetchTasks(params as any);
}

function handleSearch() {
  currentPage.value = 1;
  loadTasks();
}

function handleFilter() {
  currentPage.value = 1;
  loadTasks();
}

function handlePageChange(page: number) {
  currentPage.value = page;
  loadTasks();
}

function toggleSelect(taskId: string) {
  const idx = selectedIds.value.indexOf(taskId);
  if (idx === -1) {
    selectedIds.value.push(taskId);
  } else {
    selectedIds.value.splice(idx, 1);
  }
}

function viewReport(taskId: string) {
  router.push({ name: 'report', params: { taskId } });
}

async function handleDelete(taskId: string) {
  try {
    await ElMessageBox.confirm('确定删除该任务？', '确认', { type: 'warning' });
    await taskStore.deleteTaskItem(taskId);
    ElMessage.success('已删除');
  } catch {
    // cancelled
  }
}

async function handleBatchExport() {
  try {
    const blob = await taskStore.batchExport(selectedIds.value, 'markdown');
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'reports.zip';
    a.click();
    URL.revokeObjectURL(url);
    ElMessage.success('导出完成');
    selectedIds.value = [];
  } catch {
    ElMessage.error('导出失败');
  }
}

function statusType(status: string) {
  const map: Record<string, string> = {
    pending: 'info',
    transcribing: 'warning',
    analyzing: 'warning',
    completed: 'success',
    failed: 'danger',
  };
  return (map[status] || 'info') as any;
}

function statusLabel(status: string) {
  const map: Record<string, string> = {
    pending: '排队中',
    transcribing: '转写中',
    analyzing: '分析中',
    completed: '已完成',
    failed: '失败',
  };
  return map[status] || status;
}

function formatTime(iso: string) {
  if (!iso) return '';
  return new Date(iso).toLocaleString('zh-CN');
}

function formatDuration(seconds: number) {
  const m = Math.floor(seconds / 60);
  const s = seconds % 60;
  return `${m}:${String(s).padStart(2, '0')}`;
}
</script>

<style scoped>
.history-page {
  padding: 28px 24px 40px;
}

.panel {
  width: min(960px, 100%);
  margin: 0 auto;
  border-radius: 8px;
  background: var(--app-surface);
}

.panel :deep(.el-card__body) {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.kicker {
  font-size: 12px;
  color: var(--app-primary-strong);
  font-weight: 800;
  text-transform: uppercase;
}

h1 {
  font-size: 30px;
  font-weight: 700;
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
}

.search-input {
  max-width: 280px;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.task-card {
  padding: 16px;
  border: 1px solid var(--app-border);
  border-radius: 8px;
  background: var(--app-surface-soft);
  transition: border-color var(--transition-fast);
}

.task-card:hover {
  border-color: var(--app-primary);
}

.task-card.selected {
  border-color: var(--app-primary);
  background: var(--app-primary-soft);
}

.task-card-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.task-checkbox {
  width: 16px;
  height: 16px;
  accent-color: var(--app-primary);
  cursor: pointer;
}

.task-info {
  flex: 1;
  min-width: 0;
}

.task-filename {
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.task-meta {
  font-size: 13px;
  color: var(--app-text-soft);
  margin-top: 2px;
}

.task-progress {
  margin-top: 10px;
}

.task-actions {
  display: flex;
  gap: 4px;
  margin-top: 10px;
}

.empty-state {
  padding: 40px 0;
}

.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: 8px;
}

.loading-state {
  padding: 20px 0;
}
</style>
