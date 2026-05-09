<template>
  <el-popover
    trigger="click"
    :width="360"
    :show-arrow="false"
    placement="bottom-end"
    popper-class="notification-popover"
    @show="onOpen"
  >
    <template #reference>
      <button class="bell-btn" :class="{ 'has-unread': store.unreadCount > 0 }" type="button" aria-label="通知">
        <el-badge :value="store.unreadCount" :hidden="store.unreadCount === 0" :max="99" :class="{ 'bell-badge': store.unreadCount > 0 }">
          <span class="bell-icon" :class="{ shaking: shouldShake }">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" />
              <path d="M13.73 21a2 2 0 0 1-3.46 0" />
            </svg>
          </span>
        </el-badge>
      </button>
    </template>

    <div class="notification-panel">
      <div class="panel-top">
        <span class="panel-title">通知</span>
        <el-button
          v-if="store.unreadCount > 0"
          text
          size="small"
          @click="handleMarkAllRead"
        >
          全部已读
        </el-button>
      </div>

      <div class="notification-list" data-stagger>
        <template v-if="store.notifications.length > 0">
          <div
            v-for="item in store.notifications"
            :key="item.id"
            class="notification-item"
            :class="{ unread: !item.is_read }"
            @click="handleClick(item)"
          >
            <div class="item-indicator" :class="{ active: !item.is_read }" />
            <div class="item-icon" :class="typeClass(item.type)">
              <el-icon :size="16">
                <SuccessFilled v-if="isSuccess(item.type)" />
                <WarningFilled v-else-if="isWarning(item.type)" />
                <CircleCloseFilled v-else-if="isError(item.type)" />
                <InfoFilled v-else />
              </el-icon>
            </div>
            <div class="item-content">
              <div class="item-title">{{ item.title }}</div>
              <div class="item-message">{{ item.message }}</div>
              <div class="item-time">{{ formatTime(item.created_at) }}</div>
            </div>
          </div>
        </template>
        <div v-else class="empty-state">
          <el-empty description="暂无通知" :image-size="60" />
        </div>
      </div>

      <div class="panel-footer">
        <div class="push-toggle">
          <span class="push-label">推送通知</span>
          <el-switch
            v-model="pushEnabled"
            :disabled="pushDisabled"
            @change="togglePush"
          />
        </div>
        <router-link to="/notifications" class="view-all">
          查看全部
        </router-link>
      </div>
    </div>
  </el-popover>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import { SuccessFilled, WarningFilled, CircleCloseFilled, InfoFilled } from '@element-plus/icons-vue';
import { useNotificationStore } from '../stores/notification';
import { getAccessToken } from '../api';
import type { NotificationItem } from '../api';
import {
  isPushSupported,
  getPushPermissionState,
  isPushSubscribed,
  subscribeToPush,
  unsubscribeFromPush,
} from '../utils/push';

const store = useNotificationStore();
const router = useRouter();
const pushEnabled = ref(false);
const pushSupported = ref(false);
const pushPermission = ref<NotificationPermission>('default');
const shouldShake = ref(false);

watch(() => store.unreadCount, (newVal, oldVal) => {
  if (newVal > (oldVal ?? 0)) {
    shouldShake.value = true;
    setTimeout(() => { shouldShake.value = false; }, 600);
  }
});

const pushDisabled = computed(() => {
  return !pushSupported.value || pushPermission.value === 'denied';
});

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

async function initPushState() {
  pushSupported.value = await isPushSupported();
  if (pushSupported.value) {
    pushPermission.value = await getPushPermissionState();
    pushEnabled.value = await isPushSubscribed();
  }
}

async function togglePush(enabled: boolean) {
  try {
    if (enabled) {
      const ok = await subscribeToPush();
      if (!ok) {
        pushEnabled.value = false;
        if (pushPermission.value === 'denied') {
          ElMessage.warning('浏览器通知权限已被拒绝，请在设置中允许');
        }
        return;
      }
      ElMessage.success('推送通知已开启');
    } else {
      await unsubscribeFromPush();
      ElMessage.info('推送通知已关闭');
    }
  } catch {
    pushEnabled.value = !enabled;
    ElMessage.error('操作失败，请稍后重试');
  }
}

function onOpen() {
  store.fetchNotifications(1, 10);
  // Trigger stagger animation on notification items after data loads
  requestAnimationFrame(() => {
    document.querySelectorAll('.notification-popover .notification-item').forEach((el, i) => {
      (el as HTMLElement).style.transitionDelay = `${i * 60}ms`;
    });
  });
}

async function handleMarkAllRead() {
  await store.markAllRead();
}

async function handleClick(item: NotificationItem) {
  if (!item.is_read) {
    await store.markRead([item.id]);
  }
  if (item.link) {
    router.push(item.link);
  }
}

function formatTime(dateStr: string): string {
  const date = new Date(dateStr);
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  const minutes = Math.floor(diff / 60000);
  if (minutes < 1) return '刚刚';
  if (minutes < 60) return `${minutes}分钟前`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours}小时前`;
  const days = Math.floor(hours / 24);
  return `${days}天前`;
}

onMounted(() => {
  initPushState();
  const token = getAccessToken();
  if (token) store.connect(token);
});
</script>

<style scoped>
.bell-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  padding: 0;
  border: none;
  border-radius: 4px;
  background: transparent;
  color: var(--app-text-soft);
  cursor: pointer;
  transition: background 150ms ease, color 150ms ease;
}

.bell-btn:hover {
  background: var(--app-surface-soft);
  color: var(--app-text);
}

.bell-btn.has-unread .bell-icon {
  animation: pulse 2s ease-in-out infinite;
}

.bell-badge {
  animation: pulse 2s ease infinite;
}

.bell-icon.shaking {
  animation: bellShake 600ms ease-in-out;
}

.bell-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.notification-panel {
  display: flex;
  flex-direction: column;
  max-height: 480px;
}

.panel-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: var(--space-3) var(--space-4);
  border-bottom: 1px solid var(--app-border);
}

.panel-title {
  font-weight: 600;
  font-size: var(--text-base);
  color: var(--app-text);
}

.notification-list {
  flex: 1;
  overflow-y: auto;
  max-height: 380px;
}

.notification-item {
  display: flex;
  align-items: flex-start;
  gap: var(--space-3);
  padding: var(--space-3) var(--space-4);
  cursor: pointer;
  transition: background 150ms ease, opacity 200ms var(--ease-out-expo), transform 200ms var(--ease-out-expo);
  border-bottom: 1px solid var(--app-border);
  opacity: 0;
  transform: translateY(4px);
}

[data-stagger] .notification-item {
  opacity: 1;
  transform: translateY(0);
}

.notification-item:last-child {
  border-bottom: none;
}

.notification-item:hover {
  background: var(--app-surface-soft);
}

.notification-item.unread {
  background: var(--app-surface-soft);
}

.item-indicator {
  width: 3px;
  min-height: 36px;
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
  width: 32px;
  height: 32px;
  border-radius: 4px;
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

.item-content {
  flex: 1;
  min-width: 0;
}

.item-title {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--app-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-message {
  font-size: var(--text-xs);
  color: var(--app-text-soft);
  margin-top: 2px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.item-time {
  font-size: var(--text-xs);
  color: var(--app-text-faint);
  margin-top: var(--space-1);
}

.empty-state {
  padding: var(--space-8) 0;
}

.panel-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-3) var(--space-4);
  border-top: 1px solid var(--app-border);
}

.push-toggle {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.push-label {
  font-size: var(--text-xs);
  color: var(--app-text-soft);
}

.view-all {
  font-size: var(--text-sm);
  color: var(--app-primary);
  text-decoration: none;
  font-weight: 500;
  transition: color 150ms ease;
}

.view-all:hover {
  color: var(--app-primary);
  opacity: 0.8;
}

@media (max-width: 720px) {
  :deep(.notification-popover) {
    width: calc(100vw - 32px) !important;
    max-width: 360px;
  }
}
</style>
