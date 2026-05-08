import { fileURLToPath, URL } from 'node:url';
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import AutoImport from 'unplugin-auto-import/vite';
import Components from 'unplugin-vue-components/vite';
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers';
import { VitePWA } from 'vite-plugin-pwa';

/// <reference types="vitest" />

const elementPlusResolver = ElementPlusResolver({
  importStyle: 'css'
});

export default defineConfig({
  plugins: [
    vue(),
    AutoImport({
      resolvers: [elementPlusResolver],
      dts: 'src/auto-imports.d.ts'
    }),
    Components({
      resolvers: [elementPlusResolver],
      dts: 'src/components.d.ts'
    }),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: [
        'favicon.svg',
        'offline.html',
        'icons/icon-*.png',
        'icons/shortcut-*.png'
      ],
      manifest: {
        name: 'LiveMirror',
        short_name: 'LiveMirror',
        description: '直播内容智能分析与优化助手',
        start_url: '/',
        display: 'standalone',
        background_color: '#ffffff',
        theme_color: '#667eea',
        orientation: 'any',
        lang: 'zh-CN',
        dir: 'ltr',
        scope: '/',
        categories: ['productivity', 'utilities'],
        prefer_related_applications: false,
        icons: [
          {
            src: '/icons/icon-72.png',
            sizes: '72x72',
            type: 'image/png',
            purpose: 'any'
          },
          {
            src: '/icons/icon-96.png',
            sizes: '96x96',
            type: 'image/png',
            purpose: 'any'
          },
          {
            src: '/icons/icon-128.png',
            sizes: '128x128',
            type: 'image/png',
            purpose: 'any'
          },
          {
            src: '/icons/icon-144.png',
            sizes: '144x144',
            type: 'image/png',
            purpose: 'any'
          },
          {
            src: '/icons/icon-152.png',
            sizes: '152x152',
            type: 'image/png',
            purpose: 'any'
          },
          {
            src: '/icons/icon-192.png',
            sizes: '192x192',
            type: 'image/png',
            purpose: 'any maskable'
          },
          {
            src: '/icons/icon-384.png',
            sizes: '384x384',
            type: 'image/png',
            purpose: 'any'
          },
          {
            src: '/icons/icon-512.png',
            sizes: '512x512',
            type: 'image/png',
            purpose: 'any maskable'
          }
        ],
        shortcuts: [
          {
            name: '开始分析',
            short_name: '分析',
            description: '快速开始直播分析',
            url: '/report',
            icons: [
              {
                src: '/icons/shortcut-analyze.png',
                sizes: '96x96',
                type: 'image/png'
              }
            ]
          },
          {
            name: '标题优化',
            short_name: '优化',
            description: '优化直播标题',
            url: '/optimizer',
            icons: [
              {
                src: '/icons/shortcut-optimize.png',
                sizes: '96x96',
                type: 'image/png'
              }
            ]
          },
          {
            name: '设置',
            short_name: '设置',
            description: '应用设置',
            url: '/settings',
            icons: [
              {
                src: '/icons/shortcut-settings.png',
                sizes: '96x96',
                type: 'image/png'
              }
            ]
          }
        ],
        share_target: {
          action: '/share',
          method: 'POST',
          enctype: 'multipart/form-data',
          params: {
            title: 'title',
            text: 'text',
            url: 'url',
            files: [
              {
                name: 'files',
                accept: ['image/*', 'video/*', 'audio/*']
              }
            ]
          }
        },
        protocol_handlers: [
          {
            protocol: 'web+livemirror',
            url: '/open?url=%s'
          }
        ]
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,ico,png,svg,woff2}'],
        navigateFallback: 'index.html',
        navigateFallbackDenylist: [/^\/api\//, /^\/auth\//],
        runtimeCaching: [
          {
            urlPattern: /^https:\/\/fonts\.googleapis\.com\/.*/i,
            handler: 'CacheFirst',
            options: {
              cacheName: 'google-fonts-cache',
              expiration: {
                maxEntries: 10,
                maxAgeSeconds: 60 * 60 * 24 * 365
              },
              cacheableResponse: {
                statuses: [0, 200]
              }
            }
          },
          {
            urlPattern: /^https:\/\/fonts\.gstatic\.com\/.*/i,
            handler: 'CacheFirst',
            options: {
              cacheName: 'gstatic-fonts-cache',
              expiration: {
                maxEntries: 10,
                maxAgeSeconds: 60 * 60 * 24 * 365
              },
              cacheableResponse: {
                statuses: [0, 200]
              }
            }
          },
          {
            urlPattern: /^\/api\/.*/i,
            handler: 'NetworkFirst',
            options: {
              cacheName: 'api-cache',
              expiration: {
                maxEntries: 50,
                maxAgeSeconds: 60 * 60 * 24
              },
              cacheableResponse: {
                statuses: [0, 200]
              },
              networkTimeoutSeconds: 10
            }
          }
        ]
      },
      devOptions: {
        enabled: true
      }
    })
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 3000,
    open: true,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      },
      '/auth': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
  },
  test: {
    environment: 'jsdom',
    globals: true,
    include: ['src/**/*.{test,spec}.{ts,js}'],
    server: {
      deps: {
        inline: ['element-plus'],
      },
    },
  }
});
