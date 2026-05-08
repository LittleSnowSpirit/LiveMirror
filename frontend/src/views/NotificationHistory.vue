<template>
  <div class="notification-history-page">
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">通知中心</h1>
        <span v-if="store.unreadCount > 0" class="unread-badge">{{ store.unreadCount }} 条未读</span>
      </div>
      <div class="header-actions">
        <el-select v-model="typeFilter" placeholder="全部类型" clearable size="default" style="width: 140px" @change="handleFilterChange">
          <el-option label="任务完成" value="task_completed" />
          <el-option label="任务失败" value="task_failed" />
          <el-option label="弹幕完成" value="danmu_completed" />
          <el-option label="弹幕失败" value="danmu_failed" />
          <el-option label="额度重置" value="quota_reset" />
          <el-option label="额度不足" value="quota_low" />
        </el-select>
        <el-switch v-model="unreadOnly" active-text="只看未读" @change="handleFilterChange" />
        <el-button v-if="store.unreadCount > 0" type="primary" plain @click="handleMarkAllRead">
          全部已读
        </el-button>
      </div>
    </div>

    <div class="notification-list" v-loading="store.loading">
      <template v-if="store.notifications.length > 0">
        <div
          v-for="item in store.notifications"
          :key="item.id"
          class="list-item"
          :class="{ unread: !item.is_read }"
        >
          <div class="item-indicator" :class="{ active: !item.is_read }" />
          <div class="item-icon" :class="typeClass(item.type)">
            <el-icon :size="18">
              <SuccessFilled v-if="isSuccess(item.type)" />
              <WarningFilled v-else-if="isWarning(item.type)" />
              <CircleCloseFilled v-else-if="isError(item.type)" />
              <InfoFilled v-else />
            </el-icon>
          </div>
          <div class="item-body">
            <div class="item-title">{{ item.title }}</div>
            <div class="item-message">{{ item.message }}</div>
            <div class="item-meta">
              <span class="item-time">{{ formatTime(item.created_at) }}</span>
              <span v-if="item.is_read" class="read-tag">已读</span>
              <span v-else class="unread-tag">未读</span>
            </div>
          </div>
          <div class="item-actions">
            <el-button
              v-if="!item.is_read"
              text
              size="small"
              @click="handleMarkRead(item.id)"
            >
              标记已读
            </el-button>
            <el-button
              text
              size="small"
              type="danger"
              @click="handleDelete(item.id)"
            >
              删除
            </el-button>
          </div>
        </div>
      </template>
      <div v-else class="empty-state">
        <el-empty description="暂无通知" />
      </div>
    </div>

    <div v-if="store.total > pageSize" class="pagination-wrapper">
      <el-pagination
        v-model:current-page="currentPage"
        :page-size="pageSize"
        :total="store.total"
        layout="prev, pager, next"
        @current-change="handlePageChange"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { ElSelect, ElOption, ElSwitch, ElButton, ElIcon, ElPagination, ElEmpty } from 'element-plus';
import { SuccessFilled, WarningFilled, CircleCloseFilled, InfoFilled } from '@element-plus/icons-vue';
import { useNotificationStore } from '../stores/notification';

const store = useNotificationStore();

const currentPage = ref(1);
const pageSize = 20;
const typeFilter = ref('');
const unreadOnly = ref(false);

function isSuccess(type: string) {
  return type.includes('completed') || type.includes('success');
}

function isWarning(type: string) {
  return type.includes('low') || type.includes('warning');
}

function isError(type: string) {
  return type.includes('failed') || type.includes('error');
}

function typeClass(type: string) {
  if (isSuccess(type)) return 'type-success';
  if (isWarning(type)) return 'type-warning';
  if (isError(type)) return 'type-error';
  return 'type-info';
}

function formatTime(dateStr: string) {
  return new Date(dateStr).toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
  });
}

function loadData() {
  store.fetchNotifications(currentPage.value, pageSize, unreadOnly.value, typeFilter.value || undefined);
}

function handleFilterChange() {
  currentPage.value = 1;
  loadData();
}

function handlePageChange(page: number) {
  currentPage.value = page;
  loadData();
}

async function handleMarkRead(id: number) {
  await store.markRead([id]);
}

async function handleMarkAllRead() {
  await store.markAllRead();
}

async function handleDelete(id: number) {
  await store.removeNotification(id);
}

onMounted(() => {
  loadData();
});
</script>

<style scoped>
.notification-history-page {
  width: min(900px, 100%);
  margin: 0 auto;
  padding: var(--space-6) var(--space-4);
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: var(--space-4);
  margin-bottom: var(--space-6);
}

.header-left {
  display: flex;
  align-items: center;
  gap: var(--space-3);
}

.page-title {
  font-family: var(--font-heading);
  font-size: var(--text-2xl);
  font-weight: 600;
  color: var(--app-text);
}

.unread-badge {
  display: inline-flex;
  align-items: center;
  padding: 2px 8px;
  border-radius: var(--radius-full);
  background: var(--app-primary-soft);
  color: var(--app-primary);
  font-size: var(--text-xs);
  font-weight: 500;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  flex-wrap: wrap;
}

.notification-list {
  display: flex;
  flex-direction: column;
  border: 1px solid var(--app-border);
  border-radius: var(--radius-lg);
  overflow: hidden;
  background: var(--app-surface);
  min-height: 200px;
}

.list-item {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  padding: var(--space-4);
  border-bottom: 1px solid var(--app-border);
  transition: background var(--transition-fast);
}

.list-item:last-child {
  border-bottom: none;
}

.list-item:hover {
  background: var(--app-surface-soft);
}

.list-item.unread {
  background: var(--app-primary-soft);
}

.item-indicator {
  width: 3px;
  min-height: 40px;
  border-radius: 2px;
  flex-shrink: 0;
  align-self: stretch;
}

.item-indicator.active {
  background: var(--app-primary);
}

.item-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: var(--radius-md);
  flex-shrink: 0;
}

.item-icon.type-success {
  background: var(--app-success-soft);
  color: var(--app-success);
}

.item-icon.type-warning {
  background: var(--app-warning-soft);
  color: var(--app-warning);
}

.item-icon.type-error {
  background: var(--app-danger-soft);
  color: var(--app-danger);
}

.item-icon.type-info {
  background: var(--app-info-soft);
  color: var(--app-info);
}

.item-body {
  flex: 1;
  min-width: 0;
}

.item-title {
  font-size: var(--text-base);
  font-weight: 500;
  color: var(--app-text);
}

.item-message {
  font-size: var(--text-sm);
  color: var(--app-text-soft);
  margin-top: var(--space-1);
  line-height: 1.5;
}

.item-meta {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  margin-top: var(--space-2);
}

.item-time {
  font-size: var(--text-xs);
  color: var(--app-text-faint);
}

.read-tag,
.unread-tag {
  font-size: var(--text-xs);
  padding: 1px 6px;
  border-radius: var(--radius-sm);
}

.read-tag {
  background: var(--app-surface-soft);
  color: var(--app-text-faint);
}

.unread-tag {
  background: var(--app-primary-soft);
  color: var(--app-primary);
}

.item-actions {
  display: flex;
  align-items: center;
  gap: var(--space-1);
  flex-shrink: 0;
}

.empty-state {
  padding: var(--space-12) 0;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: var(--space-6);
}

@media (max-width: 720px) {
  .notification-history-page {
    padding: var(--space-4) var(--space-3);
  }

  .page-header {
    flex-direction: column;
    align-items: flex-start;
  }

  .header-actions {
    width: 100%;
  }

  .list-item {
    flex-wrap: wrap;
  }

  .item-actions {
    width: 100%;
    justify-content: flex-end;
    margin-top: var(--space-2);
  }
}
</style>
