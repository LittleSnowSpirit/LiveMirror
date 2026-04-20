<template>
  <transition name="fade">
    <div v-if="showPrompt && canInstall" class="pwa-install-prompt">
      <div class="prompt-content">
        <div class="prompt-header">
          <span class="prompt-icon">📲</span>
          <h3>安装 LiveMirror</h3>
          <button class="prompt-close" @click="dismiss">✕</button>
        </div>
        <p class="prompt-message">
          将 LiveMirror 安装到您的设备，获得更好的使用体验
        </p>
        <div class="prompt-actions">
          <button class="btn-install" @click="install">
            立即安装
          </button>
          <button class="btn-later" @click="dismiss">
            稍后再说
          </button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const showPrompt = ref(false)
const canInstall = ref(false)
let deferredPrompt: any = null

const install = async () => {
  if (!deferredPrompt) return
  
  deferredPrompt.prompt()
  const { outcome } = await deferredPrompt.userChoice
  
  if (outcome === 'accepted') {
    console.log('[PWA] 用户接受安装')
  } else {
    console.log('[PWA] 用户拒绝安装')
  }
  
  deferredPrompt = null
  showPrompt.value = false
}

const dismiss = () => {
  showPrompt.value = false
  localStorage.setItem('pwa-install-dismissed', 'true')
}

onMounted(() => {
  // 检查是否已 dismissed
  const dismissed = localStorage.getItem('pwa-install-dismissed')
  if (dismissed) return
  
  // 监听安装提示
  window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault()
    deferredPrompt = e
    canInstall.value = true
    
    // 延迟显示提示
    setTimeout(() => {
      showPrompt.value = true
    }, 3000)
  })
  
  // 监听安装成功
  window.addEventListener('appinstalled', () => {
    console.log('[PWA] 安装成功')
    showPrompt.value = false
    canInstall.value = false
  })
})
</script>

<style scoped>
.pwa-install-prompt {
  position: fixed;
  bottom: 20px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--el-bg-color);
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
  padding: 1rem;
  max-width: 400px;
  width: calc(100% - 40px);
  z-index: 9999;
}

.prompt-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.prompt-icon {
  font-size: 1.5rem;
}

.prompt-header h3 {
  flex: 1;
  margin: 0;
  font-size: 1.1rem;
  color: var(--el-text-color-primary);
}

.prompt-close {
  background: none;
  border: none;
  font-size: 1.2rem;
  cursor: pointer;
  padding: 0.25rem;
  color: var(--el-text-color-secondary);
}

.prompt-message {
  margin: 0 0 1rem 0;
  color: var(--el-text-color-regular);
  font-size: 0.9rem;
}

.prompt-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-install,
.btn-later {
  flex: 1;
  padding: 0.6rem 1rem;
  border-radius: 6px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-install {
  background: var(--el-color-primary);
  color: #fff;
  border: none;
}

.btn-install:hover {
  background: var(--el-color-primary-light-3);
}

.btn-later {
  background: var(--el-fill-color-light);
  color: var(--el-text-color-regular);
  border: 1px solid var(--el-border-color);
}

.btn-later:hover {
  background: var(--el-fill-color);
}

/* 移动端优化 */
@media (max-width: 480px) {
  .pwa-install-prompt {
    bottom: 10px;
    width: calc(100% - 20px);
  }
  
  .prompt-actions {
    flex-direction: column;
  }
}

/* 过渡动画 */
.fade-enter-active,
.fade-leave-active {
  transition: all 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(20px);
}
</style>
