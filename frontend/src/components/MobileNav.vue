<template>
  <div class="mobile-nav-container">
    <!-- 汉堡菜单按钮 -->
    <button 
      class="mobile-nav-toggle" 
      :class="{ active: isOpen }"
      @click="toggleNav"
      aria-label="切换导航菜单"
      aria-expanded="isOpen"
    >
      <span class="hamburger"></span>
    </button>

    <!-- 移动端导航面板 -->
    <transition name="slide">
      <nav v-show="isOpen" class="mobile-nav-panel" @click="handlePanelClick">
        <div class="nav-links">
          <RouterLink to="/" @click="closeNav">
            🏠 首页
          </RouterLink>
          <RouterLink to="/dashboard" @click="closeNav">
            📊 数据看板
          </RouterLink>
          <RouterLink to="/upload" @click="closeNav">
            📤 文件上传
          </RouterLink>
          <RouterLink to="/profile" @click="closeNav">
            👤 个人中心
          </RouterLink>
          <RouterLink to="/settings" @click="closeNav">
            ⚙️ 设置
          </RouterLink>
          <RouterLink to="/about" @click="closeNav">
            ℹ️ 关于
          </RouterLink>
        </div>
      </nav>
    </transition>

    <!-- 遮罩层 -->
    <transition name="fade">
      <div v-if="isOpen" class="nav-overlay" @click="closeNav"></div>
    </transition>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const isOpen = ref(false)

const toggleNav = () => {
  isOpen.value = !isOpen.value
  document.body.style.overflow = isOpen.value ? 'hidden' : ''
}

const closeNav = () => {
  isOpen.value = false
  document.body.style.overflow = ''
}

const handlePanelClick = (event: MouseEvent) => {
  // 防止点击面板内部时关闭
  event.stopPropagation()
}

// ESC 键关闭
const handleEscKey = (event: KeyboardEvent) => {
  if (event.key === 'Escape' && isOpen.value) {
    closeNav()
  }
}

// 窗口大小改变时关闭（从移动端切换到桌面端）
const handleResize = () => {
  if (window.innerWidth > 768 && isOpen.value) {
    closeNav()
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleEscKey)
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleEscKey)
  window.removeEventListener('resize', handleResize)
  document.body.style.overflow = ''
})
</script>

<style scoped>
.mobile-nav-container {
  position: relative;
}

.mobile-nav-toggle {
  display: none;
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.5rem;
  z-index: 1000;
}

.mobile-nav-toggle .hamburger {
  display: block;
  width: 24px;
  height: 2px;
  background: var(--el-text-color-regular);
  position: relative;
  transition: all 0.3s ease;
}

.mobile-nav-toggle .hamburger::before,
.mobile-nav-toggle .hamburger::after {
  content: '';
  position: absolute;
  width: 24px;
  height: 2px;
  background: var(--el-text-color-regular);
  transition: all 0.3s ease;
  left: 0;
}

.mobile-nav-toggle .hamburger::before {
  top: -7px;
}

.mobile-nav-toggle .hamburger::after {
  top: 7px;
}

/* 激活状态 */
.mobile-nav-toggle.active .hamburger {
  background: transparent;
}

.mobile-nav-toggle.active .hamburger::before {
  transform: rotate(45deg);
  top: 0;
}

.mobile-nav-toggle.active .hamburger::after {
  transform: rotate(-45deg);
  top: 0;
}

/* 导航面板 */
.mobile-nav-panel {
  position: fixed;
  top: var(--mobile-header-height, 56px);
  left: 0;
  right: 0;
  bottom: 0;
  background: var(--el-bg-color);
  z-index: 998;
  padding: 1rem;
  overflow-y: auto;
}

.nav-links {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.nav-links a {
  display: block;
  padding: 1rem;
  border-radius: 8px;
  text-decoration: none;
  color: var(--el-text-color-regular);
  font-size: 1.1rem;
  transition: all 0.3s;
}

.nav-links a:hover,
.nav-links a.router-link-exact-active {
  background-color: var(--el-fill-color-light);
  color: var(--el-color-primary);
}

/* 遮罩层 */
.nav-overlay {
  position: fixed;
  top: var(--mobile-header-height, 56px);
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 997;
  backdrop-filter: blur(4px);
}

/* 过渡动画 */
.slide-enter-active,
.slide-leave-active {
  transition: all 0.3s ease;
}

.slide-enter-from,
.slide-leave-to {
  transform: translateY(-20px);
  opacity: 0;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* 媒体查询 */
@media (max-width: 768px) {
  .mobile-nav-toggle {
    display: block;
  }
}

@media (min-width: 769px) {
  .mobile-nav-container {
    display: none;
  }
}
</style>
