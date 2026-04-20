<template>
  <div class="push-notification-container">
    <!-- 通知权限请求提示 -->
    <div v-if="showPermissionRequest" class="permission-request-card">
      <div class="permission-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/>
          <path d="M13.73 21a2 2 0 0 1-3.46 0"/>
        </svg>
      </div>
      <h3>开启通知提醒</h3>
      <p>接收重要通知和更新提醒</p>
      <div class="permission-actions">
        <button @click="requestPermission" class="btn-primary">
          允许通知
        </button>
        <button @click="dismissPermission" class="btn-secondary">
          暂不开启
        </button>
      </div>
    </div>

    <!-- 通知列表 -->
    <div v-if="notifications.length > 0" class="notification-list">
      <div class="notification-header">
        <h4>通知</h4>
        <button @click="clearAll" class="btn-clear">全部清除</button>
      </div>
      
      <transition-group name="notification-list">
        <div
          v-for="notification in notifications"
          :key="notification.id"
          :class="['notification-item', notification.type]"
          @click="handleClick(notification)"
        >
          <div class="notification-icon">
            <span v-if="notification.type === 'info'">ℹ️</span>
            <span v-else-if="notification.type === 'success'">✅</span>
            <span v-else-if="notification.type === 'warning'">⚠️</span>
            <span v-else-if="notification.type === 'error'">❌</span>
          </div>
          <div class="notification-content">
            <div class="notification-title">{{ notification.title }}</div>
            <div class="notification-body">{{ notification.body }}</div>
            <div class="notification-time">{{ formatTime(notification.timestamp) }}</div>
          </div>
          <button @click.stop="dismiss(notification.id)" class="btn-dismiss">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
      </transition-group>
    </div>

    <!-- 空状态 -->
    <div v-else-if="!showPermissionRequest" class="empty-state">
      <div class="empty-icon">🔔</div>
      <p>暂无通知</p>
    </div>

    <!-- Toast 提示 -->
    <transition name="toast">
      <div v-if="showToast" :class="['toast', toastType]">
        {{ toastMessage }}
      </div>
    </transition>
  </div>
</template>

<script>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { requestPermission, checkPermission } from '../utils/mobile';

export default {
  name: 'PushNotification',
  
  props: {
    // 是否自动请求权限
    autoRequest: {
      type: Boolean,
      default: false
    },
    // 最大通知数量
    maxNotifications: {
      type: Number,
      default: 50
    }
  },
  
  emits: ['notification-click', 'permission-granted', 'permission-denied'],
  
  setup(props, { emit }) {
    // 状态
    const showPermissionRequest = ref(false);
    const notifications = ref([]);
    const showToast = ref(false);
    const toastMessage = ref('');
    const toastType = ref('info');
    
    // 计算属性
    const permissionGranted = computed(() => {
      return Notification.permission === 'granted';
    });
    
    // 初始化
    onMounted(() => {
      checkNotificationPermission();
      registerServiceWorker();
      loadStoredNotifications();
      
      // 监听通知点击
      if ('serviceWorker' in navigator) {
        navigator.serviceWorker.addEventListener('message', handleSWMessage);
      }
    });
    
    onUnmounted(() => {
      if ('serviceWorker' in navigator) {
        navigator.serviceWorker.removeEventListener('message', handleSWMessage);
      }
    });
    
    // 检查通知权限
    async function checkNotificationPermission() {
      if (!('Notification' in window)) {
        console.log('[PushNotification] Notification API not supported');
        return;
      }
      
      const result = await checkPermission('notification');
      
      if (result.state === 'granted' || result.granted) {
        // 已授权
        showPermissionRequest.value = false;
      } else if (result.state === 'denied' || (result.error && result.error === 'Permission denied')) {
        // 已拒绝
        showPermissionRequest.value = false;
        showToastMessage('通知权限已被拒绝，请在浏览器设置中开启', 'warning');
      } else {
        // 未决定
        if (props.autoRequest) {
          requestPermission();
        } else {
          showPermissionRequest.value = true;
        }
      }
    }
    
    // 请求权限
    async function requestPermission() {
      const result = await requestPermission('notification');
      
      if (result.granted) {
        showPermissionRequest.value = false;
        emit('permission-granted');
        showToastMessage('通知权限已开启', 'success');
        
        // 注册到服务端
        await registerPushSubscription();
      } else {
        showPermissionRequest.value = false;
        emit('permission-denied', result.error);
        showToastMessage('通知权限请求失败', 'error');
      }
    }
    
    // 关闭权限请求
    function dismissPermission() {
      showPermissionRequest.value = false;
    }
    
    // 注册 Service Worker
    async function registerServiceWorker() {
      if ('serviceWorker' in navigator) {
        try {
          const registration = await navigator.serviceWorker.register('/service-worker/sw.js');
          console.log('[PushNotification] SW registered:', registration.scope);
          
          // 请求推送权限
          if ('PushManager' in window) {
            const subscription = await registration.pushManager.getSubscription();
            if (!subscription && Notification.permission === 'granted') {
              await createPushSubscription(registration);
            }
          }
        } catch (error) {
          console.error('[PushNotification] SW registration failed:', error);
        }
      }
    }
    
    // 创建推送订阅
    async function createPushSubscription(registration) {
      try {
        const subscription = await registration.pushManager.subscribe({
          userVisibleOnly: true,
          applicationServerKey: urlBase64ToUint8Array(import.meta.env.VITE_PUSH_PUBLIC_KEY || '')
        });
        
        console.log('[PushNotification] Push subscription:', subscription);
        
        // TODO: 发送订阅到服务器
        // await sendSubscriptionToServer(subscription);
      } catch (error) {
        console.error('[PushNotification] Push subscription failed:', error);
      }
    }
    
    // 注册推送订阅到服务器
    async function registerPushSubscription() {
      if ('serviceWorker' in navigator) {
        const registration = await navigator.serviceWorker.ready;
        const subscription = await registration.pushManager.getSubscription();
        
        if (subscription) {
          // TODO: 发送到服务器
          console.log('[PushNotification] Registering subscription:', subscription);
        }
      }
    }
    
    // 处理 Service Worker 消息
    function handleSWMessage(event) {
      const data = event.data;
      
      if (data && data.type === 'NOTIFICATION') {
        addNotification({
          title: data.title,
          body: data.body,
          type: data.notificationType || 'info',
          data: data.data
        });
      }
    }
    
    // 添加通知
    function addNotification(notification) {
      const newNotification = {
        id: Date.now().toString() + Math.random().toString(36).substr(2, 9),
        title: notification.title,
        body: notification.body,
        type: notification.type || 'info',
        timestamp: Date.now(),
        data: notification.data,
        read: false
      };
      
      notifications.value.unshift(newNotification);
      
      // 限制数量
      if (notifications.value.length > props.maxNotifications) {
        notifications.value = notifications.value.slice(0, props.maxNotifications);
      }
      
      // 存储到 localStorage
      saveNotifications();
    }
    
    // 删除通知
    function dismiss(id) {
      const index = notifications.value.findIndex(n => n.id === id);
      if (index !== -1) {
        notifications.value.splice(index, 1);
        saveNotifications();
      }
    }
    
    // 清除所有
    function clearAll() {
      notifications.value = [];
      saveNotifications();
      showToastMessage('已清除所有通知', 'success');
    }
    
    // 点击通知
    function handleClick(notification) {
      notification.read = true;
      emit('notification-click', notification);
      
      // 如果有数据中的 URL，打开它
      if (notification.data?.url) {
        window.open(notification.data.url, '_blank');
      }
    }
    
    // 格式化时间
    function formatTime(timestamp) {
      const date = new Date(timestamp);
      const now = new Date();
      const diff = now - date;
      
      const minute = 60 * 1000;
      const hour = 60 * minute;
      const day = 24 * hour;
      
      if (diff < minute) {
        return '刚刚';
      } else if (diff < hour) {
        return Math.floor(diff / minute) + '分钟前';
      } else if (diff < day) {
        return Math.floor(diff / hour) + '小时前';
      } else if (diff < 7 * day) {
        return Math.floor(diff / day) + '天前';
      } else {
        return date.toLocaleDateString('zh-CN');
      }
    }
    
    // 存储通知
    function saveNotifications() {
      try {
        localStorage.setItem('livemirror_notifications', JSON.stringify(notifications.value));
      } catch (error) {
        console.error('[PushNotification] Save failed:', error);
      }
    }
    
    // 加载通知
    function loadStoredNotifications() {
      try {
        const stored = localStorage.getItem('livemirror_notifications');
        if (stored) {
          notifications.value = JSON.parse(stored);
        }
      } catch (error) {
        console.error('[PushNotification] Load failed:', error);
      }
    }
    
    // 显示 Toast
    function showToastMessage(message, type = 'info') {
      toastMessage.value = message;
      toastType.value = type;
      showToast.value = true;
      
      setTimeout(() => {
        showToast.value = false;
      }, 3000);
    }
    
    // Base64 转 Uint8Array
    function urlBase64ToUint8Array(base64String) {
      const padding = '='.repeat((4 - base64String.length % 4) % 4);
      const base64 = (base64String + padding)
        .replace(/\-/g, '+')
        .replace(/_/g, '/');
      
      const rawData = window.atob(base64);
      const outputArray = new Uint8Array(rawData.length);
      
      for (let i = 0; i < rawData.length; ++i) {
        outputArray[i] = rawData.charCodeAt(i);
      }
      return outputArray;
    }
    
    // 暴露方法给父组件
    function showNotification(notification) {
      addNotification(notification);
    }
    
    return {
      showPermissionRequest,
      notifications,
      showToast,
      toastMessage,
      toastType,
      permissionGranted,
      requestPermission,
      dismissPermission,
      dismiss,
      clearAll,
      handleClick,
      formatTime,
      showNotification
    };
  }
};
</script>

<style scoped>
.push-notification-container {
  width: 100%;
  max-width: 400px;
  margin: 0 auto;
}

/* 权限请求卡片 */
.permission-request-card {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 24px;
  text-align: center;
  color: white;
  box-shadow: 0 10px 40px rgba(102, 126, 234, 0.4);
}

.permission-icon {
  width: 64px;
  height: 64px;
  margin: 0 auto 16px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.permission-icon svg {
  width: 32px;
  height: 32px;
}

.permission-request-card h3 {
  font-size: 20px;
  margin-bottom: 8px;
}

.permission-request-card p {
  font-size: 14px;
  opacity: 0.9;
  margin-bottom: 20px;
}

.permission-actions {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.btn-primary {
  background: white;
  color: #667eea;
  border: none;
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.btn-secondary {
  background: transparent;
  color: white;
  border: 2px solid rgba(255, 255, 255, 0.5);
  padding: 12px 24px;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background: rgba(255, 255, 255, 0.1);
}

/* 通知列表 */
.notification-list {
  background: var(--card-bg, #fff);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.notification-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  border-bottom: 1px solid var(--border-color, #eee);
}

.notification-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.btn-clear {
  background: none;
  border: none;
  color: var(--text-secondary, #666);
  font-size: 13px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
}

.btn-clear:hover {
  background: var(--hover-bg, #f5f5f5);
}

.notification-item {
  display: flex;
  align-items: flex-start;
  padding: 16px;
  border-bottom: 1px solid var(--border-color, #eee);
  cursor: pointer;
  transition: background 0.2s;
}

.notification-item:last-child {
  border-bottom: none;
}

.notification-item:hover {
  background: var(--hover-bg, #f9f9f9);
}

.notification-item.info { border-left: 3px solid #667eea; }
.notification-item.success { border-left: 3px solid #48bb78; }
.notification-item.warning { border-left: 3px solid #ed8936; }
.notification-item.error { border-left: 3px solid #f56565; }

.notification-icon {
  font-size: 20px;
  margin-right: 12px;
  flex-shrink: 0;
}

.notification-content {
  flex: 1;
  min-width: 0;
}

.notification-title {
  font-size: 14px;
  font-weight: 600;
  margin-bottom: 4px;
  color: var(--text-primary, #333);
}

.notification-body {
  font-size: 13px;
  color: var(--text-secondary, #666);
  margin-bottom: 4px;
  line-height: 1.4;
}

.notification-time {
  font-size: 12px;
  color: var(--text-tertiary, #999);
}

.btn-dismiss {
  background: none;
  border: none;
  color: var(--text-tertiary, #999);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  flex-shrink: 0;
  margin-left: 8px;
}

.btn-dismiss:hover {
  background: var(--hover-bg, #f5f5f5);
  color: var(--text-secondary, #666);
}

.btn-dismiss svg {
  width: 16px;
  height: 16px;
}

/* 空状态 */
.empty-state {
  text-align: center;
  padding: 48px 24px;
  color: var(--text-secondary, #666);
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.5;
}

/* Toast */
.toast {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  padding: 12px 24px;
  border-radius: 8px;
  color: white;
  font-size: 14px;
  font-weight: 500;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 9999;
}

.toast.info { background: #667eea; }
.toast.success { background: #48bb78; }
.toast.warning { background: #ed8936; }
.toast.error { background: #f56565; }

/* 动画 */
.notification-list-enter-active,
.notification-list-leave-active {
  transition: all 0.3s ease;
}

.notification-list-enter-from {
  opacity: 0;
  transform: translateX(-30px);
}

.notification-list-leave-to {
  opacity: 0;
  transform: translateX(30px);
}

.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(20px);
}

/* 移动端优化 */
@media (max-width: 768px) {
  .push-notification-container {
    max-width: 100%;
  }
  
  .permission-request-card {
    margin: 16px;
  }
  
  .notification-list {
    margin: 16px;
    border-radius: 12px;
  }
}
</style>
