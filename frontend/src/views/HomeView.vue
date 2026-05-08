<template>
  <div class="home-page">
    <section class="page-header">
      <h1>首页</h1>
      <p class="page-sub">把直播素材变成可执行的复盘结论</p>
    </section>

    <section class="stats-line">
      <span>本周已分析: <strong>0</strong> 次</span>
      <span class="stats-sep">|</span>
      <span>剩余配额: <strong>--</strong> 次</span>
    </section>

    <section class="quick-actions">
      <h2 class="section-title">快捷操作</h2>
      <div class="action-links">
        <router-link to="/upload" class="action-link">
          <span class="action-icon">📤</span> 上传分析
        </router-link>
        <router-link to="/report" class="action-link">
          <span class="action-icon">📊</span> 查看报告
        </router-link>
        <router-link to="/attribution" class="action-link">
          <span class="action-icon">🎯</span> 归因分析
        </router-link>
        <router-link to="/suggestions" class="action-link">
          <span class="action-icon">💡</span> 话术建议
        </router-link>
      </div>
    </section>

    <section class="recent-tasks">
      <div class="section-header">
        <h2 class="section-title">最近任务</h2>
        <el-button text @click="loadLatestTask">刷新</el-button>
      </div>

      <el-skeleton v-if="loading" :rows="3" animated />

      <div v-else-if="latestTaskId" class="task-list">
        <div class="task-row" @click="openReport">
          <span class="task-name">{{ latestTaskName || '未记录文件名' }}</span>
          <el-tag v-if="taskStatus" :type="statusTagType(taskStatus.status)" size="small" effect="light">
            {{ statusLabel(taskStatus.status) }}
          </el-tag>
          <span class="task-time">{{ latestTaskId.slice(0, 8) }}...</span>
        </div>
      </div>

      <div v-else class="empty-hint">还没有上传记录</div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import { getStoredTaskId, getTaskStatus } from '../api';
import type { TaskInfo } from '../api';

const router = useRouter();
const loading = ref(false);
const latestTaskId = ref('');
const latestTaskName = ref('');
const taskStatus = ref<TaskInfo | null>(null);

function statusLabel(status: string) {
  const mapping: Record<string, string> = {
    pending: '等待处理',
    processing: '处理中',
    transcribing: '转写中',
    analyzing: '分析中',
    completed: '已完成',
    failed: '已失败'
  };

  return mapping[status] || status;
}

function statusTagType(status: string) {
  if (status === 'completed') return 'success';
  if (status === 'failed') return 'danger';
  if (status === 'processing' || status === 'transcribing' || status === 'analyzing') return 'warning';
  return 'info';
}

async function loadLatestTask() {
  loading.value = true;
  latestTaskId.value = getStoredTaskId();
  latestTaskName.value = localStorage.getItem('livemirror:last-task-name') || '';

  try {
    if (!latestTaskId.value) {
      taskStatus.value = null;
      return;
    }

    const response = await getTaskStatus(latestTaskId.value);
    taskStatus.value = response.task;
    latestTaskName.value = response.task.filename;
  } catch {
    taskStatus.value = null;
  } finally {
    loading.value = false;
  }
}

function openReport() {
  if (!latestTaskId.value) {
    router.push('/report');
    return;
  }

  router.push({ name: 'report', params: { taskId: latestTaskId.value } });
}

onMounted(() => {
  loadLatestTask();
});
</script>

<style scoped>
.home-page {
  display: flex;
  flex-direction: column;
  gap: var(--space-6);
  width: min(960px, 100%);
  margin: 0 auto;
  padding: var(--space-6) var(--space-6) var(--space-10);
}

.page-header h1 {
  font-size: var(--text-xl);
  font-weight: 600;
  color: var(--app-text);
}

.page-sub {
  margin-top: var(--space-1);
  font-size: var(--text-sm);
  color: var(--app-text-soft);
}

.stats-line {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  font-size: var(--text-sm);
  color: var(--app-text-soft);
}

.stats-line strong {
  color: var(--app-text);
  font-weight: 600;
}

.stats-sep {
  color: var(--app-border);
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--app-text);
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.quick-actions {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.action-links {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-4);
}

.action-link {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  font-size: var(--text-sm);
  color: var(--app-primary);
  text-decoration: none;
  transition: color var(--transition-fast);
}

.action-link:hover {
  text-decoration: underline;
}

.action-icon {
  font-size: 14px;
}

.recent-tasks {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.task-list {
  border: 1px solid var(--app-border);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.task-row {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--app-border);
  cursor: pointer;
  transition: background var(--transition-fast);
}

.task-row:last-child {
  border-bottom: none;
}

.task-row:hover {
  background: var(--app-surface-soft);
}

.task-name {
  flex: 1;
  font-size: var(--text-sm);
  color: var(--app-text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.task-time {
  font-size: var(--text-xs);
  color: var(--app-text-faint);
  font-family: var(--font-mono);
}

.empty-hint {
  font-size: var(--text-sm);
  color: var(--app-text-faint);
  padding: var(--space-4) 0;
}

@media (max-width: 640px) {
  .action-links {
    flex-direction: column;
    gap: var(--space-2);
  }
}
</style>
