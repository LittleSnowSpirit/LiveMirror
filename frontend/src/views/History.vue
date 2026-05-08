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
          v-for="(task, idx) in taskStore.tasks"
          :key="task.task_id"
          class="task-card"
          :class="[
            { selected: selectedIds.includes(task.task_id) },
            `status-${task.status}`
          ]"
          :style="{ '--stagger-index': idx }"
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
  padding: var(--space-6) var(--space-6) var(--space-10);
}

/* Glass panel */
.panel {
  width: min(960px, 100%);
  margin: 0 auto;
  border-radius: var(--radius-lg);
  background: var(--app-glass-bg);
  backdrop-filter: blur(var(--app-glass-blur));
  -webkit-backdrop-filter: blur(var(--app-glass-blur));
  border: 1px solid var(--app-glass-border);
  box-shadow: var(--app-shadow-card);
}

.panel :deep(.el-card__body) {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.kicker {
  font-size: var(--text-xs);
  font-weight: 800;
  text-transform: uppercase;
  background: var(--app-gradient-primary);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

h1 {
  font-size: var(--text-3xl);
  font-weight: 700;
  color: var(--app-text);
}

/* Glass toolbar */
.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
  align-items: center;
  padding: var(--space-3);
  border-radius: var(--radius-lg);
  background: var(--app-bg-deep);
  border: 1px solid var(--app-glass-border);
}

.toolbar :deep(.el-input__wrapper),
.toolbar :deep(.el-select__wrapper) {
  background: var(--app-surface-soft);
  border: 1px solid var(--app-glass-border);
  box-shadow: none;
}

.search-input {
  max-width: 280px;
}

.task-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-2);
}

/* Glass task cards with status-colored left border */
.task-card {
  padding: var(--space-4);
  border-radius: var(--radius-lg);
  background: var(--app-glass-bg);
  backdrop-filter: blur(var(--app-glass-blur));
  -webkit-backdrop-filter: blur(var(--app-glass-blur));
  border: 1px solid var(--app-glass-border);
  border-left: 3px solid var(--app-text-faint);
  transition: border-color var(--transition-normal), box-shadow var(--transition-normal), transform var(--transition-normal);
  animation: staggerFadeIn 0.4s ease-out forwards;
  animation-delay: calc(var(--stagger-index, 0) * 60ms);
  opacity: 0;
}

.task-card.status-completed {
  border-left-color: var(--app-success);
}

.task-card.status-transcribing,
.task-card.status-analyzing,
.task-card.status-processing {
  border-left-color: var(--app-warning);
}

.task-card.status-failed {
  border-left-color: var(--app-danger);
}

.task-card.status-pending {
  border-left-color: var(--app-info);
}

.task-card:hover {
  border-color: rgba(167, 139, 250, 0.25);
  box-shadow: var(--app-glow);
  transform: translateY(-2px);
}

.task-card.selected {
  border-color: var(--app-primary);
  background: rgba(167, 139, 250, 0.08);
  box-shadow: var(--app-glow-strong);
}

.task-card-header {
  display: flex;
  align-items: center;
  gap: var(--space-3);
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
  color: var(--app-text);
}

.task-meta {
  font-size: var(--text-xs);
  color: var(--app-text-soft);
  margin-top: 2px;
}

.task-progress {
  margin-top: var(--space-2);
}

.task-actions {
  display: flex;
  gap: var(--space-1);
  margin-top: var(--space-2);
}

.empty-state {
  padding: var(--space-10) 0;
}

/* Pagination with gradient active page */
.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: var(--space-2);
}

.pagination-wrap :deep(.el-pager li.is-active) {
  background: var(--app-gradient-primary) !important;
  color: #fff !important;
  border-radius: var(--radius-md);
}

.pagination-wrap :deep(.el-pager li) {
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
}

.pagination-wrap :deep(.el-pager li:hover) {
  color: var(--app-primary);
}

.loading-state {
  padding: var(--space-5) 0;
}

@keyframes staggerFadeIn {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>
