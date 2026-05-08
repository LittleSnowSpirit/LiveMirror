import { fileURLToPath, URL } from 'node:url';
import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';
import AutoImport from 'unplugin-auto-import/vite';
import Components from 'unplugin-vue-components/vite';
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers';

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
