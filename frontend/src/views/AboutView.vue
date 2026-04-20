<template>
  <div class="about-view">
    <header class="header">
      <h1>ℹ️ 关于</h1>
      <ThemeSwitcher />
    </header>

    <main class="main-content">
      <section class="card hero">
        <div class="logo">
          <svg viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="50" r="45" stroke="currentColor" stroke-width="4"/>
            <path d="M50 20 L50 50 L70 70" stroke="currentColor" stroke-width="4" stroke-linecap="round"/>
          </svg>
        </div>
        <h1>LiveMirror</h1>
        <p class="subtitle">实时镜像同步工具</p>
        <p class="version">版本 1.0.0</p>
      </section>

      <section class="card">
        <h2>🎨 暗黑模式特性</h2>
        <div class="features-grid">
          <div class="feature-item">
            <span class="feature-icon">🌓</span>
            <div class="feature-info">
              <h3>主题切换</h3>
              <p>支持明亮和暗黑模式一键切换</p>
            </div>
          </div>
          <div class="feature-item">
            <span class="feature-icon">💻</span>
            <div class="feature-info">
              <h3>系统跟随</h3>
              <p>自动检测并跟随系统主题偏好</p>
            </div>
          </div>
          <div class="feature-item">
            <span class="feature-icon">🎨</span>
            <div class="feature-info">
              <h3>自定义颜色</h3>
              <p>支持自定义主色调和强调色</p>
            </div>
          </div>
          <div class="feature-item">
            <span class="feature-icon">💾</span>
            <div class="feature-info">
              <h3>偏好保存</h3>
              <p>主题偏好自动保存到本地存储</p>
            </div>
          </div>
          <div class="feature-item">
            <span class="feature-icon">✨</span>
            <div class="feature-info">
              <h3>平滑过渡</h3>
              <p>主题切换时带有平滑动画效果</p>
            </div>
          </div>
          <div class="feature-item">
            <span class="feature-icon">📱</span>
            <div class="feature-info">
              <h3>全面适配</h3>
              <p>所有页面和组件完美适配暗黑模式</p>
            </div>
          </div>
        </div>
      </section>

      <section class="card">
        <h2>📋 测试清单</h2>
        <div class="checklist">
          <div class="checklist-item">
            <span class="check-icon">✅</span>
            <span>主题切换功能正常</span>
          </div>
          <div class="checklist-item">
            <span class="check-icon">✅</span>
            <span>系统主题自动跟随</span>
          </div>
          <div class="checklist-item">
            <span class="check-icon">✅</span>
            <span>所有页面暗黑模式适配</span>
          </div>
          <div class="checklist-item">
            <span class="check-icon">✅</span>
            <span>主题色自定义功能</span>
          </div>
          <div class="checklist-item">
            <span class="check-icon">✅</span>
            <span>主题偏好持久化</span>
          </div>
          <div class="checklist-item">
            <span class="check-icon">✅</span>
            <span>平滑过渡动画</span>
          </div>
        </div>
      </section>

      <section class="card">
        <h2>📄 技术栈</h2>
        <div class="tech-stack">
          <span class="tech-badge">Vue 3</span>
          <span class="tech-badge">TypeScript</span>
          <span class="tech-badge">Vite</span>
          <span class="tech-badge">CSS Variables</span>
          <span class="tech-badge">Composition API</span>
        </div>
      </section>

      <section class="card">
        <h2>📝 使用说明</h2>
        <ol class="instructions">
          <li>点击右上角的主题切换按钮</li>
          <li>选择明亮、暗黑或跟随系统模式</li>
          <li>在设置页面可以自定义主题颜色</li>
          <li>主题偏好会自动保存</li>
          <li>可以导出/导入主题配置</li>
        </ol>
      </section>
    </main>

    <footer class="footer">
      <p>LiveMirror © 2026 - 暗黑模式支持已启用</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
import ThemeSwitcher from '../components/ThemeSwitcher.vue';
</script>

<style scoped>
.about-view {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background-color: var(--color-bg-primary);
  color: var(--color-text-primary);
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 40px;
  background-color: var(--color-bg-secondary);
  border-bottom: 1px solid var(--color-border);
}

.header h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.main-content {
  flex: 1;
  padding: 40px;
  display: grid;
  gap: 24px;
  max-width: 900px;
  margin: 0 auto;
  width: 100%;
  box-sizing: border-box;
}

.card {
  background-color: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 24px;
}

.card.hero {
  text-align: center;
  padding: 40px 24px;
}

.hero .logo {
  width: 100px;
  height: 100px;
  margin: 0 auto 20px;
  color: var(--color-primary);
}

.hero h1 {
  margin: 0 0 8px 0;
  font-size: 32px;
  font-weight: 700;
}

.hero .subtitle {
  margin: 0 0 16px 0;
  font-size: 16px;
  color: var(--color-text-secondary);
}

.hero .version {
  display: inline-block;
  padding: 4px 12px;
  background-color: var(--color-bg-tertiary);
  border-radius: 16px;
  font-size: 13px;
  color: var(--color-text-secondary);
}

.card h2 {
  margin: 0 0 20px 0;
  font-size: 18px;
  font-weight: 600;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 16px;
}

.feature-item {
  display: flex;
  gap: 12px;
  padding: 16px;
  background-color: var(--color-bg-tertiary);
  border-radius: 8px;
}

.feature-icon {
  font-size: 28px;
  flex-shrink: 0;
}

.feature-info h3 {
  margin: 0 0 4px 0;
  font-size: 15px;
  font-weight: 500;
}

.feature-info p {
  margin: 0;
  font-size: 13px;
  color: var(--color-text-secondary);
}

.checklist {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.checklist-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background-color: var(--color-bg-tertiary);
  border-radius: 8px;
}

.check-icon {
  font-size: 20px;
}

.tech-stack {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tech-badge {
  padding: 6px 14px;
  background-color: var(--color-bg-tertiary);
  border: 1px solid var(--color-border);
  border-radius: 16px;
  font-size: 13px;
  color: var(--color-text-secondary);
}

.instructions {
  padding-left: 20px;
  color: var(--color-text-primary);
  line-height: 2;
}

.instructions li {
  margin-bottom: 8px;
}

.footer {
  padding: 20px 40px;
  background-color: var(--color-bg-secondary);
  border-top: 1px solid var(--color-border);
  text-align: center;
  color: var(--color-text-secondary);
  font-size: 14px;
}
</style>
