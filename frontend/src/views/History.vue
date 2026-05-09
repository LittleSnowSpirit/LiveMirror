<template>
  <div ref="pageRef" class="history-page">
    <h1 data-animate>历史记录</h1>

    <div class="toolbar" data-animate style="transition-delay: 80ms">
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

    <el-table v-else :data="taskStore.tasks" class="task-table" @selection-change="handleSelectionChange">
      <el-table-column type="selection" width="48" />
      <el-table-column prop="filename" label="文件名" min-width="200" show-overflow-tooltip />
      <el-table-column label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)" size="small" :class="{ 'status-pulse': row.status === 'transcribing' || row.status === 'processing' }">
            {{ statusLabel(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="时长" width="100">
        <template #default="{ row }">
          <span v-if="row.duration">{{ formatDuration(row.duration) }}</span>
          <span v-else class="text-faint">--</span>
        </template>
      </el-table-column>
      <el-table-column label="创建时间" width="180">
        <template #default="{ row }">
          {{ formatTime(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160" fixed="right">
        <template #default="{ row }">
          <el-button size="small" type="primary" text @click="viewReport(row.task_id)">
            查看报告
          </el-button>
          <el-button size="small" type="danger" text @click="handleDelete(row.task_id)">
            删除
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <div v-if="taskStore.total > taskStore.pageSize" class="pagination-wrap" data-animate="fade">
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="taskStore.pageSize"
        :total="taskStore.total"
        layout="prev, pager, next"
        @current-change="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage, ElMessageBox } from 'element-plus';
import { useTaskStore } from '../stores/task';
import { useReveal } from '../composables/useReveal';

const router = useRouter();
const taskStore = useTaskStore();
const pageRef = ref<HTMLElement | null>(null);
const { observe } = useReveal();

const searchQuery = ref('');
const statusFilter = ref('');
const selectedIds = ref<string[]>([]);
const currentPage = ref(1);

onMounted(() => {
  loadTasks();
  pageRef.value?.querySelectorAll('[data-animate]').forEach(el => observe(el as HTMLElement));
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

function handleSelectionChange(rows: any[]) {
  selectedIds.value = rows.map((r: any) => r.task_id);
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
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
  padding: var(--space-6) var(--space-6) var(--space-10);
  max-width: 960px;
  margin: 0 auto;
}

h1 {
  font-size: var(--text-3xl);
  font-weight: 700;
  color: var(--app-text);
}

.toolbar {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
  align-items: center;
}

.search-input {
  max-width: 280px;
}

.text-faint {
  color: var(--app-text-faint);
}

.empty-state {
  padding: var(--space-10) 0;
}

.pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: var(--space-2);
}

.pagination-wrap :deep(.el-pager li.is-active) {
  background: var(--app-primary) !important;
  color: #fff !important;
  border-radius: var(--radius-md);
}

.pagination-wrap :deep(.el-pager li) {
  border-radius: var(--radius-md);
  transition: color var(--transition-fast);
}

.pagination-wrap :deep(.el-pager li:hover) {
  color: var(--app-primary);
}

.loading-state {
  padding: var(--space-5) 0;
}

.status-pulse {
  animation: statusPulse 2s ease-in-out infinite;
}

@keyframes statusPulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.6; }
}
</style>
