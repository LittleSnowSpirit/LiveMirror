/**
 * LiveMirror Service Worker
 * 支持离线访问、缓存策略、后台同步
 */

const CACHE_NAME = 'livemirror-v1'
const RUNTIME_CACHE_NAME = 'livemirror-runtime-v1'

// 预缓存资源
const PRECACHE_ASSETS = [
  '/',
  '/index.html',
  '/manifest.json',
  '/favicon.ico',
]

// 安装事件 - 预缓存
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[ServiceWorker] 预缓存资源')
      return cache.addAll(PRECACHE_ASSETS)
    })
  )
  // 跳过等待，立即激活
  self.skipWaiting()
})

// 激活事件 - 清理旧缓存
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME && name !== RUNTIME_CACHE_NAME)
          .map((name) => caches.delete(name))
      )
    })
  )
  // 接管所有客户端
  self.clients.claim()
})

// 请求拦截 - 缓存策略
self.addEventListener('fetch', (event) => {
  const { request } = event
  const url = new URL(request.url)
  
  // 仅处理同源请求
  if (url.origin !== location.origin) {
    return
  }
  
  // GET 请求处理
  if (request.method === 'GET') {
    // HTML 页面 - 网络优先，失败回退到缓存
    if (request.headers.get('accept')?.includes('text/html')) {
      event.respondWith(
        fetch(request)
          .then((response) => {
            // 克隆响应以便缓存
            const responseClone = response.clone()
            caches.open(CACHE_NAME).then((cache) => {
              cache.put(request, responseClone)
            })
            return response
          })
          .catch(() => {
            return caches.match(request)
          })
      )
      return
    }
    
    // 静态资源 - 缓存优先
    if (
      url.pathname.endsWith('.js') ||
      url.pathname.endsWith('.css') ||
      url.pathname.endsWith('.png') ||
      url.pathname.endsWith('.jpg') ||
      url.pathname.endsWith('.svg') ||
      url.pathname.endsWith('.ico') ||
      url.pathname.endsWith('.woff') ||
      url.pathname.endsWith('.woff2')
    ) {
      event.respondWith(
        caches.match(request).then((cachedResponse) => {
          if (cachedResponse) {
            // 后台更新缓存
            fetch(request).then((response) => {
              if (response.ok) {
                caches.open(CACHE_NAME).then((cache) => {
                  cache.put(request, response)
                })
              }
            })
            return cachedResponse
          }
          return fetch(request)
        })
      )
      return
    }
    
    // API 请求 - 网络优先，失败返回空
    if (url.pathname.startsWith('/api/')) {
      event.respondWith(
        fetch(request)
          .then((response) => {
            const responseClone = response.clone()
            caches.open(RUNTIME_CACHE_NAME).then((cache) => {
              cache.put(request, responseClone)
            })
            return response
          })
          .catch(() => {
            return caches.match(request)
          })
      )
      return
    }
    
    // 其他请求 - 缓存优先
    event.respondWith(
      caches.match(request).then((cachedResponse) => {
        return cachedResponse || fetch(request)
      })
    )
  }
})

// 后台同步
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-data') {
    event.waitUntil(syncData())
  }
})

async function syncData() {
  // 从 IndexedDB 获取待同步数据
  // 这里需要根据实际业务逻辑实现
  console.log('[ServiceWorker] 后台同步数据')
}

// 推送通知
self.addEventListener('push', (event) => {
  const data = event.data?.json() || {}
  const title = data.title || 'LiveMirror 提醒'
  const options = {
    body: data.body || '您有新的消息',
    icon: '/icons/icon-192x192.png',
    badge: '/icons/icon-72x72.png',
    data: data.data,
  }
  
  event.waitUntil(
    self.registration.showNotification(title, options)
  )
})

// 通知点击处理
self.addEventListener('notificationclick', (event) => {
  event.notification.close()
  
  event.waitUntil(
    clients.matchAll({ type: 'window' }).then((clientList) => {
      // 如果已有窗口，聚焦它
      for (const client of clientList) {
        if (client.url === event.notification.data?.url && 'focus' in client) {
          return client.focus()
        }
      }
      // 否则打开新窗口
      if (clients.openWindow) {
        return clients.openWindow(event.notification.data?.url || '/')
      }
    })
  )
})

// 消息处理
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting()
  }
  
  if (event.data && event.data.type === 'CACHE_URLS') {
    event.waitUntil(
      caches.open(CACHE_NAME).then((cache) => {
        return cache.addAll(event.data.urls)
      })
    )
  }
})
