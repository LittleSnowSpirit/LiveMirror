/**
 * PWA 注册工具
 * 处理 Service Worker 注册、更新、离线检测
 */

/**
 * 注册 Service Worker
 */
export async function registerServiceWorker(config = {}) {
  const {
    swUrl = '/sw.js',
    onUpdate,
    onOffline,
    onOnline,
  } = config
  
  // 检查是否支持 Service Worker
  if (!('serviceWorker' in navigator)) {
    console.log('[PWA] 不支持 Service Worker')
    return null
  }
  
  try {
    const registration = await navigator.serviceWorker.register(swUrl, {
      scope: '/',
    })
    
    console.log('[PWA] Service Worker 注册成功:', registration.scope)
    
    // 监听更新
    registration.addEventListener('updatefound', () => {
      const newWorker = registration.installing
      if (!newWorker) return
      
      newWorker.addEventListener('statechange', () => {
        if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
          console.log('[PWA] 有新版本可用')
          if (onUpdate) onUpdate(registration)
        }
      })
    })
    
    // 监听消息
    navigator.serviceWorker.addEventListener('message', (event) => {
      console.log('[PWA] 收到消息:', event.data)
    })
    
    return registration
  } catch (error) {
    console.error('[PWA] Service Worker 注册失败:', error)
    return null
  }
}

/**
 * 检测离线状态
 */
export function setupOfflineDetection(config = {}) {
  const { onOffline, onOnline } = config
  
  // 初始状态
  if (!navigator.onLine) {
    if (onOffline) onOffline()
  }
  
  // 监听网络状态变化
  window.addEventListener('offline', () => {
    console.log('[PWA] 离线')
    if (onOffline) onOffline()
  })
  
  window.addEventListener('online', () => {
    console.log('[PWA] 在线')
    if (onOnline) onOnline()
  })
}

/**
 * 提示用户更新
 */
export function showUpdatePrompt(registration) {
  if ('Notification' in window && Notification.permission === 'granted') {
    new Notification('LiveMirror 更新可用', {
      body: '点击刷新以应用最新版本',
      icon: '/icons/icon-192x192.png',
      badge: '/icons/icon-72x72.png',
    }).onclick = () => {
      window.location.reload()
    }
  }
}

/**
 * 请求通知权限
 */
export async function requestNotificationPermission() {
  if (!('Notification' in window)) {
    console.log('[PWA] 不支持通知')
    return 'denied'
  }
  
  if (Notification.permission === 'granted') {
    return 'granted'
  }
  
  if (Notification.permission !== 'denied') {
    const permission = await Notification.requestPermission()
    return permission
  }
  
  return Notification.permission
}

/**
 * 发送消息到 Service Worker
 */
export function sendMessageToSW(message) {
  if (navigator.serviceWorker.controller) {
    navigator.serviceWorker.controller.postMessage(message)
  }
}

/**
 * 预缓存 URLs
 */
export async function precacheUrls(urls) {
  sendMessageToSW({
    type: 'CACHE_URLS',
    urls,
  })
}

/**
 * 检查 PWA 安装状态
 */
export function checkInstallStatus() {
  let deferredPrompt = null
  
  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault()
    deferredPrompt = e
    console.log('[PWA] 可以安装')
  })
  
  return {
    canInstall: () => deferredPrompt !== null,
    promptInstall: async () => {
      if (!deferredPrompt) {
        console.log('[PWA] 无法安装')
        return false
      }
      
      deferredPrompt.prompt()
      const { outcome } = await deferredPrompt.userChoice
      console.log('[PWA] 安装结果:', outcome)
      deferredPrompt = null
      return outcome === 'accepted'
    },
  }
}

/**
 * 完整 PWA 初始化
 */
export async function initPWA(config = {}) {
  const registration = await registerServiceWorker(config)
  setupOfflineDetection(config)
  const installStatus = checkInstallStatus()
  
  return {
    registration,
    installStatus,
    sendMessage: sendMessageToSW,
    precache: precacheUrls,
    requestNotifications: requestNotificationPermission,
  }
}

export default {
  registerServiceWorker,
  setupOfflineDetection,
  showUpdatePrompt,
  requestNotificationPermission,
  sendMessageToSW,
  precacheUrls,
  checkInstallStatus,
  initPWA,
}
