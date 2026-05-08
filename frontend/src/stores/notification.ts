import { defineStore } from 'pinia';
import { ref } from 'vue';
import { ElNotification } from 'element-plus';
import { notificationWs } from '../utils/websocket';
import {
  getNotifications,
  getUnreadCount,
  markNotificationsRead,
  markAllNotificationsRead,
  deleteNotification,
} from '../api';
import type { NotificationItem } from '../api';

export const useNotificationStore = defineStore('notification', () => {
  const notifications = ref<NotificationItem[]>([]);
  const unreadCount = ref(0);
  const total = ref(0);
  const loading = ref(false);
  const wsConnected = ref(false);

  const typeMap: Record<string, 'success' | 'error' | 'info' | 'warning'> = {
    task_completed: 'success',
    task_failed: 'error',
    danmu_completed: 'success',
    danmu_failed: 'error',
    quota_reset: 'info',
    quota_low: 'warning',
  };

  function connect(token: string) {
    notificationWs.on('init', (msg: any) => {
      wsConnected.value = true;
      if (msg.unread_count !== undefined) {
        unreadCount.value = msg.unread_count;
      }
    });

    notificationWs.on('notification', (msg: any) => {
      const item = msg.notification || msg;
      if (item && item.title) {
        ElNotification({
          title: item.title,
          message: item.message || '',
          type: typeMap[item.type] || 'info',
          duration: 5000,
        });
      }
      unreadCount.value = msg.unread_count ?? unreadCount.value + 1;
    });

    notificationWs.on('unread_count', (msg: any) => {
      if (msg.count !== undefined) {
        unreadCount.value = msg.count;
      }
    });

    notificationWs.on('_close', () => {
      wsConnected.value = false;
    });

    notificationWs.connect(token);
  }

  function disconnect() {
    notificationWs.disconnect();
    wsConnected.value = false;
    notifications.value = [];
    unreadCount.value = 0;
    total.value = 0;
  }

  async function fetchNotifications(page = 1, pageSize = 20, unreadOnly = false, type?: string) {
    loading.value = true;
    try {
      const res = await getNotifications({ page, page_size: pageSize, unread_only: unreadOnly, type });
      notifications.value = res.notifications;
      total.value = res.total;
      unreadCount.value = res.unread_count;
    } finally {
      loading.value = false;
    }
  }

  async function fetchUnreadCount() {
    unreadCount.value = await getUnreadCount();
  }

  async function markRead(ids: number[]) {
    await markNotificationsRead(ids);
    notificationWs.send({ type: 'mark_read', ids });
    for (const item of notifications.value) {
      if (ids.includes(item.id)) {
        item.is_read = true;
      }
    }
    unreadCount.value = Math.max(0, unreadCount.value - ids.length);
  }

  async function markAllRead() {
    await markAllNotificationsRead();
    notificationWs.send({ type: 'mark_all_read' });
    for (const item of notifications.value) {
      item.is_read = true;
    }
    unreadCount.value = 0;
  }

  async function removeNotification(id: number) {
    await deleteNotification(id);
    const idx = notifications.value.findIndex((n) => n.id === id);
    if (idx !== -1) {
      if (!notifications.value[idx].is_read) {
        unreadCount.value = Math.max(0, unreadCount.value - 1);
      }
      notifications.value.splice(idx, 1);
      total.value = Math.max(0, total.value - 1);
    }
  }

  return {
    notifications,
    unreadCount,
    total,
    loading,
    wsConnected,
    connect,
    disconnect,
    fetchNotifications,
    fetchUnreadCount,
    markRead,
    markAllRead,
    removeNotification,
  };
});
