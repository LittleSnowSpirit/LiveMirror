/// <reference lib="webworker" />
declare const self: ServiceWorkerGlobalScope;

import { precacheAndRoute, cleanupOutdatedCaches } from 'workbox-precaching';
import { registerRoute, NavigationRoute } from 'workbox-routing';
import { CacheFirst, NetworkFirst } from 'workbox-strategies';
import { ExpirationPlugin } from 'workbox-expiration';
import { CacheableResponsePlugin } from 'workbox-cacheable-response';
import { createHandlerBoundToURL } from 'workbox-precaching';

// workbox injects the precache manifest here at build time
precacheAndRoute(self.__WB_MANIFEST as any);
cleanupOutdatedCaches();

// Navigation fallback
registerRoute(
  new NavigationRoute(createHandlerBoundToURL('index.html'), {
    denylist: [/^\/api\//, /^\/auth\//],
  })
);

// Google Fonts caching
registerRoute(
  /^https:\/\/fonts\.googleapis\.com\/.*/i,
  new CacheFirst({
    cacheName: 'google-fonts-cache',
    plugins: [
      new ExpirationPlugin({ maxEntries: 10, maxAgeSeconds: 60 * 60 * 24 * 365 }),
      new CacheableResponsePlugin({ statuses: [0, 200] }),
    ],
  }),
  'GET'
);

registerRoute(
  /^https:\/\/fonts\.gstatic\.com\/.*/i,
  new CacheFirst({
    cacheName: 'gstatic-fonts-cache',
    plugins: [
      new ExpirationPlugin({ maxEntries: 10, maxAgeSeconds: 60 * 60 * 24 * 365 }),
      new CacheableResponsePlugin({ statuses: [0, 200] }),
    ],
  }),
  'GET'
);

// API caching
registerRoute(
  /^\/api\/.*/i,
  new NetworkFirst({
    cacheName: 'api-cache',
    networkTimeoutSeconds: 10,
    plugins: [
      new ExpirationPlugin({ maxEntries: 50, maxAgeSeconds: 60 * 60 * 24 }),
      new CacheableResponsePlugin({ statuses: [0, 200] }),
    ],
  }),
  'GET'
);

// Push event handler
self.addEventListener('push', (event: PushEvent) => {
  if (!event.data) return;

  const data = event.data.json();
  const options: NotificationOptions = {
    body: data.message,
    icon: '/icons/icon-192.png',
    badge: '/icons/icon-72.png',
    data: { link: data.link || '/' },
    tag: data.tag || `notification-${data.id}`,
    renotify: true,
    vibrate: [200, 100, 200],
  };

  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});

// Notification click handler — focus existing window or open new one
self.addEventListener('notificationclick', (event: NotificationEvent) => {
  event.notification.close();
  const link = event.notification.data?.link || '/';

  event.waitUntil(
    self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clients) => {
      for (const client of clients) {
        if (client.url.includes(self.location.origin) && 'focus' in client) {
          (client as WindowClient).focus();
          (client as WindowClient).navigate(link);
          return;
        }
      }
      return self.clients.openWindow(link);
    })
  );
});
