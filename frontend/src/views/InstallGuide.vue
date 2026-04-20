<template>
  <div class="install-guide-container">
    <div class="install-guide">
      <!-- 头部 -->
      <div class="guide-header">
        <h1>安装 LiveMirror</h1>
        <p>将应用添加到主屏幕，获得更好的使用体验</p>
      </div>

      <!-- 安装状态检测 -->
      <div v-if="isInstalled" class="installed-status">
        <div class="status-icon">✅</div>
        <h3>已安装</h3>
        <p>LiveMirror 已添加到您的主屏幕</p>
        <button @click="launchApp" class="btn-launch">打开应用</button>
      </div>

      <!-- 安装步骤 -->
      <div v-else class="install-steps">
        <!-- Android / 支持 beforeinstallprompt 的设备 -->
        <div v-if="canInstall" class="step-card highlight">
          <div class="step-number">1</div>
          <div class="step-content">
            <h3>一键安装</h3>
            <p>点击下方按钮，将 LiveMirror 添加到主屏幕</p>
            <button @click="install" class="btn-install-primary">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="7 10 12 15 17 10"/>
                <line x1="12" y1="15" x2="12" y2="3"/>
              </svg>
              添加到主屏幕
            </button>
          </div>
        </div>

        <!-- iOS 安装指南 -->
        <div v-if="isIOS" class="step-card">
          <div class="step-number">2</div>
          <div class="step-content">
            <h3>iOS 安装步骤</h3>
            <p>由于 iOS 限制，需要手动添加</p>
            
            <div class="ios-steps">
              <div class="ios-step">
                <div class="ios-step-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M4 12v8a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-8"/>
                    <polyline points="16 6 12 2 8 6"/>
                    <line x1="12" y1="2" x2="12" y2="15"/>
                  </svg>
                </div>
                <div class="ios-step-text">
                  <strong>步骤 1</strong>
                  <span>点击底部 <strong>分享</strong> 按钮</span>
                </div>
              </div>
              
              <div class="ios-step">
                <div class="ios-step-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="3" y="3" width="18" height="18" rx="2" ry="2"/>
                    <line x1="12" y1="8" x2="12" y2="16"/>
                    <line x1="8" y1="12" x2="16" y2="12"/>
                  </svg>
                </div>
                <div class="ios-step-text">
                  <strong>步骤 2</strong>
                  <span>选择 <strong>"添加到主屏幕"</strong></span>
                </div>
              </div>
              
              <div class="ios-step">
                <div class="ios-step-icon">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="9 11 12 14 22 4"/>
                    <path d="M21 12v7a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11"/>
                  </svg>
                </div>
                <div class="ios-step-text">
                  <strong>步骤 3</strong>
                  <span>点击右上角 <strong>"添加"</strong></span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 其他浏览器 -->
        <div v-if="!canInstall && !isIOS" class="step-card">
          <div class="step-number">1</div>
          <div class="step-content">
            <h3>手动安装</h3>
            <p>在浏览器菜单中选择"安装应用"或"添加到主屏幕"</p>
            
            <div class="browser-hints">
              <div class="browser-hint">
                <strong>Chrome / Edge</strong>
                <span>点击地址栏右侧的安装图标</span>
              </div>
              <div class="browser-hint">
                <strong>Safari</strong>
                <span>分享 → 添加到主屏幕</span>
              </div>
              <div class="browser-hint">
                <strong>Firefox</strong>
                <span>菜单 → 安装</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- PWA 优势 -->
      <div class="pwa-benefits">
        <h2>为什么安装应用？</h2>
        <div class="benefits-grid">
          <div class="benefit-card">
            <div class="benefit-icon">🚀</div>
            <h4>快速启动</h4>
            <p>从主屏幕直接打开，无需打开浏览器</p>
          </div>
          <div class="benefit-card">
            <div class="benefit-icon">📴</div>
            <h4>离线使用</h4>
            <p>无网络时也能查看已缓存的内容</p>
          </div>
          <div class="benefit-card">
            <div class="benefit-icon">🔔</div>
            <h4>消息推送</h4>
            <p>及时接收重要通知和提醒</p>
          </div>
          <div class="benefit-card">
            <div class="benefit-icon">📱</div>
            <h4>原生体验</h4>
            <p>全屏显示，更沉浸的使用体验</p>
          </div>
        </div>
      </div>

      <!-- 功能特性 -->
      <div class="features-section">
        <h2>移动端特性</h2>
        <div class="features-list">
          <div class="feature-item">
            <span class="feature-check">✓</span>
            <span>手势操作支持（滑动、长按、双击）</span>
          </div>
          <div class="feature-item">
            <span class="feature-check">✓</span>
            <span>相机/麦克风权限管理</span>
          </div>
          <div class="feature-item">
            <span class="feature-check">✓</span>
            <span>离线缓存，节省流量</span>
          </div>
          <div class="feature-item">
            <span class="feature-check">✓</span>
            <span>推送通知，不错过重要消息</span>
          </div>
          <div class="feature-item">
            <span class="feature-check">✓</span>
            <span>自适应深色/浅色模式</span>
          </div>
          <div class="feature-item">
            <span class="feature-check">✓</span>
            <span>响应式设计，适配各种屏幕</span>
          </div>
        </div>
      </div>

      <!-- 常见问题 -->
      <div class="faq-section">
        <h2>常见问题</h2>
        <div class="faq-list">
          <div class="faq-item" v-for="(faq, index) in faqs" :key="index">
            <div class="faq-question" @click="toggleFaq(index)">
              <span>{{ faq.q }}</span>
              <span class="faq-toggle">{{ faq.open ? '−' : '+' }}</span>
            </div>
            <div v-if="faq.open" class="faq-answer">
              {{ faq.a }}
            </div>
          </div>
        </div>
      </div>

      <!-- 底部操作 -->
      <div class="guide-footer">
        <button @click="skip" class="btn-skip">暂不安装</button>
        <button v-if="canInstall" @click="install" class="btn-install">立即安装</button>
      </div>
    </div>

    <!-- 安装成功弹窗 -->
    <transition name="modal">
      <div v-if="showSuccessModal" class="modal-overlay" @click="closeSuccessModal">
        <div class="modal-content" @click.stop>
          <div class="success-icon">🎉</div>
          <h3>安装成功！</h3>
          <p>LiveMirror 已添加到您的主屏幕</p>
          <button @click="closeSuccessModal" class="btn-confirm">好的</button>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue';
import { isIOS, isMobile, PWAInstallManager } from '../utils/mobile';

export default {
  name: 'InstallGuide',
  
  setup() {
    // 状态
    const installManager = ref(null);
    const showSuccessModal = ref(false);
    const faqs = ref([
      {
        q: '安装后在哪里找到应用？',
        a: '安装后，应用图标会出现在您的主屏幕上，就像普通应用一样。点击图标即可快速启动。',
        open: false
      },
      {
        q: '需要消耗流量吗？',
        a: '安装过程只需要少量流量。安装后，应用会缓存常用资源，离线时也能使用，反而更节省流量。',
        open: false
      },
      {
        q: '安全吗？',
        a: '非常安全。PWA 应用运行在浏览器的安全沙箱中，和访问普通网站一样安全。我们不会访问您的敏感信息。',
        open: false
      },
      {
        q: '如何卸载？',
        a: '长按应用图标，选择"移除"或"卸载"即可。也可以在浏览器设置中管理已安装的 PWA 应用。',
        open: false
      },
      {
        q: '会占用很多存储空间吗？',
        a: '不会。PWA 应用非常轻量，通常只占用几 MB 空间，远小于原生应用。',
        open: false
      }
    ]);
    
    // 计算属性
    const isIOSDevice = computed(() => isIOS());
    const isMobileDevice = computed(() => isMobile());
    
    const canInstall = computed(() => {
      return installManager.value && installManager.value.canInstall();
    });
    
    const isInstalled = computed(() => {
      return installManager.value && installManager.value.isInstalled;
    });
    
    // 初始化
    onMounted(() => {
      installManager.value = new PWAInstallManager();
    });
    
    // 安装
    async function install() {
      if (!installManager.value) return;
      
      const result = await installManager.value.promptInstall();
      
      if (result.success) {
        showSuccessModal.value = true;
      } else {
        console.log('[InstallGuide] Install failed:', result.reason || result.error);
      }
    }
    
    // 启动应用
    function launchApp() {
      // 已经是独立应用模式，无需操作
      console.log('[InstallGuide] App launched');
    }
    
    // 跳过
    function skip() {
      // 可以记录用户选择，下次不再提示
      localStorage.setItem('livemirror_install_skipped', Date.now().toString());
      window.history.back();
    }
    
    // 关闭成功弹窗
    function closeSuccessModal() {
      showSuccessModal.value = false;
    }
    
    // 切换 FAQ
    function toggleFaq(index) {
      faqs.value[index].open = !faqs.value[index].open;
    }
    
    return {
      isIOS: isIOSDevice,
      isMobile: isMobileDevice,
      canInstall,
      isInstalled,
      showSuccessModal,
      faqs,
      install,
      launchApp,
      skip,
      closeSuccessModal,
      toggleFaq
    };
  }
};
</script>

<style scoped>
.install-guide-container {
  min-height: 100vh;
  background: var(--bg-color, #f5f7fa);
  padding: 24px 16px;
}

.install-guide {
  max-width: 600px;
  margin: 0 auto;
}

/* 头部 */
.guide-header {
  text-align: center;
  margin-bottom: 32px;
}

.guide-header h1 {
  font-size: 28px;
  font-weight: 700;
  color: var(--text-primary, #333);
  margin-bottom: 8px;
}

.guide-header p {
  font-size: 16px;
  color: var(--text-secondary, #666);
}

/* 已安装状态 */
.installed-status {
  background: var(--card-bg, #fff);
  border-radius: 16px;
  padding: 48px 24px;
  text-align: center;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.status-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.installed-status h3 {
  font-size: 24px;
  color: var(--text-primary, #333);
  margin-bottom: 8px;
}

.installed-status p {
  color: var(--text-secondary, #666);
  margin-bottom: 24px;
}

.btn-launch {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 16px 48px;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-launch:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
}

/* 安装步骤 */
.install-steps {
  margin-bottom: 32px;
}

.step-card {
  background: var(--card-bg, #fff);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  display: flex;
  gap: 16px;
}

.step-card.highlight {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.step-card.highlight h3,
.step-card.highlight p {
  color: white;
}

.step-number {
  width: 40px;
  height: 40px;
  background: rgba(102, 126, 234, 0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  color: #667eea;
  flex-shrink: 0;
}

.step-card.highlight .step-number {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.step-content {
  flex: 1;
}

.step-content h3 {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary, #333);
  margin-bottom: 8px;
}

.step-content p {
  font-size: 14px;
  color: var(--text-secondary, #666);
  margin-bottom: 16px;
}

.btn-install-primary {
  background: white;
  color: #667eea;
  border: none;
  padding: 14px 28px;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s;
}

.btn-install-primary svg {
  width: 20px;
  height: 20px;
}

.btn-install-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

/* iOS 步骤 */
.ios-steps {
  margin-top: 16px;
}

.ios-step {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  background: rgba(0, 0, 0, 0.03);
  border-radius: 8px;
  margin-bottom: 8px;
}

.ios-step-icon {
  width: 36px;
  height: 36px;
  background: #667eea;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.ios-step-icon svg {
  width: 20px;
  height: 20px;
  color: white;
}

.ios-step-text {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.ios-step-text strong {
  font-size: 14px;
  color: var(--text-primary, #333);
}

.ios-step-text span {
  font-size: 13px;
  color: var(--text-secondary, #666);
}

/* 浏览器提示 */
.browser-hints {
  margin-top: 16px;
}

.browser-hint {
  padding: 12px;
  background: rgba(0, 0, 0, 0.03);
  border-radius: 8px;
  margin-bottom: 8px;
}

.browser-hint strong {
  display: block;
  font-size: 14px;
  color: var(--text-primary, #333);
  margin-bottom: 4px;
}

.browser-hint span {
  font-size: 13px;
  color: var(--text-secondary, #666);
}

/* PWA 优势 */
.pwa-benefits {
  background: var(--card-bg, #fff);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.pwa-benefits h2 {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary, #333);
  margin-bottom: 20px;
}

.benefits-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.benefit-card {
  text-align: center;
  padding: 16px;
  background: var(--bg-color, #f5f7fa);
  border-radius: 12px;
}

.benefit-icon {
  font-size: 32px;
  margin-bottom: 8px;
}

.benefit-card h4 {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary, #333);
  margin-bottom: 4px;
}

.benefit-card p {
  font-size: 12px;
  color: var(--text-secondary, #666);
  line-height: 1.4;
}

/* 功能特性 */
.features-section {
  background: var(--card-bg, #fff);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.features-section h2 {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary, #333);
  margin-bottom: 20px;
}

.features-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.feature-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 15px;
  color: var(--text-primary, #333);
}

.feature-check {
  color: #48bb78;
  font-weight: 700;
  font-size: 18px;
}

/* 常见问题 */
.faq-section {
  background: var(--card-bg, #fff);
  border-radius: 16px;
  padding: 24px;
  margin-bottom: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.faq-section h2 {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary, #333);
  margin-bottom: 20px;
}

.faq-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.faq-item {
  border: 1px solid var(--border-color, #eee);
  border-radius: 8px;
  overflow: hidden;
}

.faq-question {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  cursor: pointer;
  font-weight: 500;
  color: var(--text-primary, #333);
  transition: background 0.2s;
}

.faq-question:hover {
  background: var(--hover-bg, #f9f9f9);
}

.faq-toggle {
  font-size: 20px;
  color: var(--text-secondary, #666);
}

.faq-answer {
  padding: 0 16px 16px;
  color: var(--text-secondary, #666);
  font-size: 14px;
  line-height: 1.6;
}

/* 底部操作 */
.guide-footer {
  display: flex;
  justify-content: center;
  gap: 16px;
  padding: 24px;
  position: sticky;
  bottom: 0;
  background: var(--bg-color, #f5f7fa);
  backdrop-filter: blur(10px);
}

.btn-skip {
  background: transparent;
  color: var(--text-secondary, #666);
  border: 2px solid var(--border-color, #ddd);
  padding: 14px 32px;
  border-radius: 10px;
  font-size: 15px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-skip:hover {
  border-color: var(--text-secondary, #666);
}

.btn-install {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 14px 32px;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-install:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4);
}

/* 成功弹窗 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.modal-content {
  background: var(--card-bg, #fff);
  border-radius: 20px;
  padding: 40px 32px;
  text-align: center;
  max-width: 320px;
  width: 90%;
}

.success-icon {
  font-size: 64px;
  margin-bottom: 16px;
}

.modal-content h3 {
  font-size: 22px;
  font-weight: 600;
  color: var(--text-primary, #333);
  margin-bottom: 8px;
}

.modal-content p {
  font-size: 15px;
  color: var(--text-secondary, #666);
  margin-bottom: 24px;
}

.btn-confirm {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  padding: 14px 48px;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-confirm:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 16px rgba(102, 126, 234, 0.4);
}

/* 动画 */
.modal-enter-active,
.modal-leave-active {
  transition: all 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-content,
.modal-leave-to .modal-content {
  transform: scale(0.9);
}

/* 移动端优化 */
@media (max-width: 768px) {
  .install-guide-container {
    padding: 16px 12px;
  }
  
  .guide-header h1 {
    font-size: 24px;
  }
  
  .benefits-grid {
    grid-template-columns: 1fr;
  }
  
  .step-card {
    flex-direction: column;
  }
  
  .guide-footer {
    flex-direction: column;
    padding: 16px;
  }
  
  .btn-skip,
  .btn-install {
    width: 100%;
  }
}
</style>
