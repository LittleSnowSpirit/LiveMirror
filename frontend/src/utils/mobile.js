/**
 * LiveMirror 移动端工具函数
 * 
 * 功能：
 * - 设备检测
 * - 手势支持
 * - 权限管理
 * - 原生功能桥接
 * - PWA 安装检测
 */

// ==================== 设备检测 ====================

/**
 * 检测是否为移动设备
 */
export function isMobile() {
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent) ||
    (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1); // iPadOS
}

/**
 * 检测是否为 iOS 设备
 */
export function isIOS() {
  return /iPad|iPhone|iPod/.test(navigator.userAgent) ||
    (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
}

/**
 * 检测是否为 Android 设备
 */
export function isAndroid() {
  return /Android/.test(navigator.userAgent);
}

/**
 * 获取设备信息
 */
export function getDeviceInfo() {
  return {
    isMobile: isMobile(),
    isIOS: isIOS(),
    isAndroid: isAndroid(),
    userAgent: navigator.userAgent,
    platform: navigator.platform,
    screen: {
      width: screen.width,
      height: screen.height,
      pixelRatio: window.devicePixelRatio
    },
    orientation: screen.orientation?.type || 'unknown'
  };
}

// ==================== 手势支持 ====================

/**
 * 手势配置
 */
export const GESTURE_CONFIG = {
  swipeThreshold: 50,      // 滑动阈值 (px)
  longPressDelay: 500,     // 长按延迟 (ms)
  pinchThreshold: 10,      // 捏合阈值 (px)
  doubleTapDelay: 300      // 双击延迟 (ms)
};

/**
 * 手势检测器类
 */
export class GestureDetector {
  constructor(element, callbacks = {}) {
    this.element = element;
    this.callbacks = {
      onSwipeLeft: callbacks.onSwipeLeft || (() => {}),
      onSwipeRight: callbacks.onSwipeRight || (() => {}),
      onSwipeUp: callbacks.onSwipeUp || (() => {}),
      onSwipeDown: callbacks.onSwipeDown || (() => {}),
      onLongPress: callbacks.onLongPress || (() => {}),
      onDoubleTap: callbacks.onDoubleTap || (() => {}),
      onPinchIn: callbacks.onPinchIn || (() => {}),
      onPinchOut: callbacks.onPinchOut || (() => {})
    };
    
    this.touchStartX = 0;
    this.touchStartY = 0;
    this.touchEndX = 0;
    this.touchEndY = 0;
    this.longPressTimer = null;
    this.lastTapTime = 0;
    this.initialPinchDistance = null;
    
    this.init();
  }
  
  init() {
    this.element.addEventListener('touchstart', this.handleTouchStart.bind(this), { passive: true });
    this.element.addEventListener('touchmove', this.handleTouchMove.bind(this), { passive: true });
    this.element.addEventListener('touchend', this.handleTouchEnd.bind(this), { passive: true });
  }
  
  handleTouchStart(event) {
    this.touchStartX = event.touches[0].clientX;
    this.touchStartY = event.touches[0].clientY;
    
    // 长按检测
    clearTimeout(this.longPressTimer);
    this.longPressTimer = setTimeout(() => {
      this.callbacks.onLongPress({
        x: this.touchStartX,
        y: this.touchStartY
      });
      this.longPressTimer = null;
    }, GESTURE_CONFIG.longPressDelay);
    
    // 双指捏合检测
    if (event.touches.length === 2) {
      this.initialPinchDistance = this.getPinchDistance(event.touches);
    }
  }
  
  handleTouchMove(event) {
    // 取消长按
    if (this.longPressTimer) {
      clearTimeout(this.longPressTimer);
      this.longPressTimer = null;
    }
    
    // 捏合检测
    if (event.touches.length === 2 && this.initialPinchDistance !== null) {
      const currentDistance = this.getPinchDistance(event.touches);
      const diff = currentDistance - this.initialPinchDistance;
      
      if (Math.abs(diff) > GESTURE_CONFIG.pinchThreshold) {
        if (diff < 0) {
          this.callbacks.onPinchIn({ distance: Math.abs(diff) });
        } else {
          this.callbacks.onPinchOut({ distance: diff });
        }
        this.initialPinchDistance = currentDistance;
      }
    }
  }
  
  handleTouchEnd(event) {
    // 取消长按
    if (this.longPressTimer) {
      clearTimeout(this.longPressTimer);
      this.longPressTimer = null;
    }
    
    this.touchEndX = event.changedTouches[0].clientX;
    this.touchEndY = event.changedTouches[0].clientY;
    
    this.detectSwipe();
    this.detectDoubleTap();
    
    this.initialPinchDistance = null;
  }
  
  getPinchDistance(touches) {
    const dx = touches[0].clientX - touches[1].clientX;
    const dy = touches[0].clientY - touches[1].clientY;
    return Math.sqrt(dx * dx + dy * dy);
  }
  
  detectSwipe() {
    const dx = this.touchEndX - this.touchStartX;
    const dy = this.touchEndY - this.touchStartY;
    
    if (Math.abs(dx) < GESTURE_CONFIG.swipeThreshold && 
        Math.abs(dy) < GESTURE_CONFIG.swipeThreshold) {
      return; // 不构成滑动
    }
    
    if (Math.abs(dx) > Math.abs(dy)) {
      // 水平滑动
      if (dx > 0) {
        this.callbacks.onSwipeRight({ distance: dx });
      } else {
        this.callbacks.onSwipeLeft({ distance: Math.abs(dx) });
      }
    } else {
      // 垂直滑动
      if (dy > 0) {
        this.callbacks.onSwipeDown({ distance: dy });
      } else {
        this.callbacks.onSwipeUp({ distance: Math.abs(dy) });
      }
    }
  }
  
  detectDoubleTap() {
    const currentTime = new Date().getTime();
    const tapLength = currentTime - this.lastTapTime;
    
    if (tapLength < GESTURE_CONFIG.doubleTapDelay && tapLength > 0) {
      this.callbacks.onDoubleTap({
        x: this.touchEndX,
        y: this.touchEndY
      });
    }
    
    this.lastTapTime = currentTime;
  }
  
  destroy() {
    clearTimeout(this.longPressTimer);
    this.element.removeEventListener('touchstart', this.handleTouchStart);
    this.element.removeEventListener('touchmove', this.handleTouchMove);
    this.element.removeEventListener('touchend', this.handleTouchEnd);
  }
}

// ==================== 权限管理 ====================

/**
 * 权限类型
 */
export const PERMISSIONS = {
  CAMERA: 'camera',
  MICROPHONE: 'microphone',
  NOTIFICATION: 'notification',
  GEOLOCATION: 'geolocation',
  STORAGE: 'storage'
};

/**
 * 请求权限
 */
export async function requestPermission(permission) {
  try {
    switch (permission) {
      case PERMISSIONS.CAMERA:
        return await requestCameraPermission();
      case PERMISSIONS.MICROPHONE:
        return await requestMicrophonePermission();
      case PERMISSIONS.NOTIFICATION:
        return await requestNotificationPermission();
      case PERMISSIONS.GEOLOCATION:
        return await requestGeolocationPermission();
      case PERMISSIONS.STORAGE:
        return await requestStoragePermission();
      default:
        throw new Error(`Unknown permission: ${permission}`);
    }
  } catch (error) {
    console.error(`[Mobile] Permission ${permission} failed:`, error);
    return { granted: false, error: error.message };
  }
}

/**
 * 请求相机权限
 */
async function requestCameraPermission() {
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    return { granted: false, error: 'Camera API not supported' };
  }
  
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    // 立即停止流，只用于权限检测
    stream.getTracks().forEach(track => track.stop());
    return { granted: true };
  } catch (error) {
    return { granted: false, error: error.name };
  }
}

/**
 * 请求麦克风权限
 */
async function requestMicrophonePermission() {
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    return { granted: false, error: 'Microphone API not supported' };
  }
  
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    stream.getTracks().forEach(track => track.stop());
    return { granted: true };
  } catch (error) {
    return { granted: false, error: error.name };
  }
}

/**
 * 请求通知权限
 */
async function requestNotificationPermission() {
  if (!('Notification' in window)) {
    return { granted: false, error: 'Notification API not supported' };
  }
  
  if (Notification.permission === 'granted') {
    return { granted: true };
  }
  
  if (Notification.permission === 'denied') {
    return { granted: false, error: 'Permission denied' };
  }
  
  try {
    const permission = await Notification.requestPermission();
    return { granted: permission === 'granted' };
  } catch (error) {
    return { granted: false, error: error.message };
  }
}

/**
 * 请求地理位置权限
 */
async function requestGeolocationPermission() {
  if (!navigator.geolocation) {
    return { granted: false, error: 'Geolocation API not supported' };
  }
  
  return new Promise((resolve) => {
    navigator.geolocation.getCurrentPosition(
      () => resolve({ granted: true }),
      (error) => resolve({ granted: false, error: error.message }),
      { enableHighAccuracy: false, timeout: 5000 }
    );
  });
}

/**
 * 请求存储权限 (Persistent Storage)
 */
async function requestStoragePermission() {
  if (!navigator.storage) {
    return { granted: false, error: 'Storage API not supported' };
  }
  
  try {
    const persisted = await navigator.storage.persist();
    return { granted: persisted };
  } catch (error) {
    return { granted: false, error: error.message };
  }
}

/**
 * 检查权限状态
 */
export async function checkPermission(permission) {
  if ('permissions' in navigator) {
    try {
      const permissionMap = {
        [PERMISSIONS.CAMERA]: 'camera',
        [PERMISSIONS.MICROPHONE]: 'microphone',
        [PERMISSIONS.NOTIFICATION]: 'notifications',
        [PERMISSIONS.GEOLOCATION]: 'geolocation'
      };
      
      const name = permissionMap[permission];
      if (name) {
        const result = await navigator.permissions.query({ name });
        return { state: result.state };
      }
    } catch (error) {
      // 忽略错误
    }
  }
  
  // Fallback: 尝试请求来检测
  return await requestPermission(permission);
}

// ==================== PWA 安装 ====================

/**
 * PWA 安装提示管理器
 */
export class PWAInstallManager {
  constructor() {
    this.deferredPrompt = null;
    this.isInstalled = this.checkInstallStatus();
    
    this.init();
  }
  
  init() {
    window.addEventListener('beforeinstallprompt', (event) => {
      event.preventDefault();
      this.deferredPrompt = event;
      console.log('[Mobile] PWA install prompt ready');
    });
    
    window.addEventListener('appinstalled', () => {
      this.isInstalled = true;
      this.deferredPrompt = null;
      console.log('[Mobile] PWA installed successfully');
    });
  }
  
  /**
   * 检查是否已安装
   */
  checkInstallStatus() {
    return window.matchMedia('(display-mode: standalone)').matches ||
           window.navigator.standalone === true;
  }
  
  /**
   * 是否可以安装
   */
  canInstall() {
    return !this.isInstalled && this.deferredPrompt !== null;
  }
  
  /**
   * 显示安装提示
   */
  async promptInstall() {
    if (!this.canInstall()) {
      return { success: false, reason: 'Cannot install' };
    }
    
    this.deferredPrompt.prompt();
    
    try {
      const result = await this.deferredPrompt.userChoice;
      console.log('[Mobile] Install prompt result:', result.outcome);
      
      if (result.outcome === 'accepted') {
        this.isInstalled = true;
      }
      
      this.deferredPrompt = null;
      return { success: result.outcome === 'accepted' };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }
  
  /**
   * iOS 安装指南
   */
  getIOSInstallGuide() {
    return {
      steps: [
        '点击 Safari 浏览器底部的分享按钮',
        '在分享菜单中选择"添加到主屏幕"',
        '点击右上角的"添加"'
      ],
      note: 'iOS 设备需要手动添加到主屏幕'
    };
  }
}

// ==================== 原生功能桥接 ====================

/**
 * 调用原生功能
 */
export const NativeBridge = {
  /**
   * 调用相机拍照
   */
  async capturePhoto(options = {}) {
    const {
      width = 1280,
      height = 720,
      quality = 0.8,
      sourceType = 'camera' // 'camera' | 'photo-library'
    } = options;
    
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      throw new Error('Camera API not supported');
    }
    
    const constraints = {
      video: {
        width: { ideal: width },
        height: { ideal: height },
        facingMode: sourceType === 'camera' ? 'environment' : 'user'
      }
    };
    
    const stream = await navigator.mediaDevices.getUserMedia(constraints);
    const video = document.createElement('video');
    video.srcObject = stream;
    
    return new Promise((resolve, reject) => {
      video.onloadedmetadata = () => {
        video.play();
        
        // 创建 canvas 捕获图像
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0);
        
        // 停止流
        stream.getTracks().forEach(track => track.stop());
        
        // 转换为 base64
        const dataUrl = canvas.toDataURL('image/jpeg', quality);
        resolve({
          dataUrl,
          width: canvas.width,
          height: canvas.height
        });
      };
      
      video.onerror = reject;
    });
  },
  
  /**
   * 录制音频
   */
  async recordAudio(options = {}) {
    const { duration = 10 } = options;
    
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      throw new Error('Microphone API not supported');
    }
    
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    const mediaRecorder = new MediaRecorder(stream);
    const chunks = [];
    
    return new Promise((resolve, reject) => {
      mediaRecorder.ondataavailable = (event) => {
        chunks.push(event.data);
      };
      
      mediaRecorder.onstop = () => {
        const blob = new Blob(chunks, { type: 'audio/webm' });
        const reader = new FileReader();
        
        reader.onloadend = () => {
          stream.getTracks().forEach(track => track.stop());
          resolve({
            dataUrl: reader.result,
            blob,
            type: blob.type
          });
        };
        
        reader.onerror = reject;
        reader.readAsDataURL(blob);
      };
      
      mediaRecorder.start();
      
      // 自动停止
      setTimeout(() => {
        mediaRecorder.stop();
      }, duration * 1000);
    });
  },
  
  /**
   * 分享功能
   */
  async share(data) {
    if (!navigator.share) {
      throw new Error('Web Share API not supported');
    }
    
    try {
      await navigator.share(data);
      return { success: true };
    } catch (error) {
      if (error.name !== 'AbortError') {
        console.error('[Mobile] Share failed:', error);
      }
      return { success: false, error: error.message };
    }
  },
  
  /**
   * 剪贴板操作
   */
  async clipboardWrite(text) {
    try {
      await navigator.clipboard.writeText(text);
      return { success: true };
    } catch (error) {
      // Fallback for older browsers
      const textarea = document.createElement('textarea');
      textarea.value = text;
      textarea.style.position = 'fixed';
      textarea.style.opacity = '0';
      document.body.appendChild(textarea);
      textarea.select();
      
      try {
        document.execCommand('copy');
        document.body.removeChild(textarea);
        return { success: true };
      } catch (e) {
        document.body.removeChild(textarea);
        return { success: false, error: e.message };
      }
    }
  },
  
  /**
   * 剪贴板读取
   */
  async clipboardRead() {
    try {
      const text = await navigator.clipboard.readText();
      return { success: true, text };
    } catch (error) {
      return { success: false, error: error.message };
    }
  },
  
  /**
   * 震动反馈
   */
  vibrate(pattern = 100) {
    if (navigator.vibrate) {
      navigator.vibrate(pattern);
      return true;
    }
    return false;
  },
  
  /**
   * 获取电池状态
   */
  async getBattery() {
    if (!navigator.getBattery) {
      return null;
    }
    
    try {
      const battery = await navigator.getBattery();
      return {
        level: battery.level,
        charging: battery.charging,
        chargingTime: battery.chargingTime,
        dischargingTime: battery.dischargingTime
      };
    } catch (error) {
      return null;
    }
  },
  
  /**
   * 获取网络状态
   */
  getNetworkInfo() {
    const connection = navigator.connection || navigator.mozConnection || navigator.webkitConnection;
    
    if (connection) {
      return {
        effectiveType: connection.effectiveType,
        downlink: connection.downlink,
        rtt: connection.rtt,
        saveData: connection.saveData,
        online: navigator.onLine
      };
    }
    
    return {
      online: navigator.onLine
    };
  }
};

// ==================== 屏幕方向 ====================

/**
 * 锁定屏幕方向
 */
export async function lockOrientation(orientation) {
  if (screen.orientation && screen.orientation.lock) {
    try {
      await screen.orientation.lock(orientation);
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }
  return { success: false, error: 'Orientation API not supported' };
}

/**
 * 解锁屏幕方向
 */
export async function unlockOrientation() {
  if (screen.orientation && screen.orientation.unlock) {
    try {
      screen.orientation.unlock();
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }
  return { success: false, error: 'Orientation API not supported' };
}

// ==================== 全屏模式 ====================

/**
 * 进入全屏
 */
export async function enterFullscreen(element = document.documentElement) {
  try {
    if (element.requestFullscreen) {
      await element.requestFullscreen();
    } else if (element.webkitRequestFullscreen) {
      await element.webkitRequestFullscreen();
    } else if (element.msRequestFullscreen) {
      await element.msRequestFullscreen();
    }
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

/**
 * 退出全屏
 */
export async function exitFullscreen() {
  try {
    if (document.exitFullscreen) {
      await document.exitFullscreen();
    } else if (document.webkitExitFullscreen) {
      await document.webkitExitFullscreen();
    } else if (document.msExitFullscreen) {
      await document.msExitFullscreen();
    }
    return { success: true };
  } catch (error) {
    return { success: false, error: error.message };
  }
}

/**
 * 检查是否全屏
 */
export function isFullscreen() {
  return document.fullscreenElement ||
         document.webkitFullscreenElement ||
         document.msFullscreenElement;
}

// ==================== 唤醒锁定 ====================

/**
 * 保持屏幕常亮
 */
export class WakeLock {
  constructor() {
    this.wakeLock = null;
  }
  
  async request() {
    if ('wakeLock' in navigator) {
      try {
        this.wakeLock = await navigator.wakeLock.request('screen');
        console.log('[Mobile] Wake Lock active');
        return { success: true };
      } catch (error) {
        return { success: false, error: error.message };
      }
    }
    return { success: false, error: 'Wake Lock API not supported' };
  }
  
  async release() {
    if (this.wakeLock) {
      try {
        await this.wakeLock.release();
        this.wakeLock = null;
        console.log('[Mobile] Wake Lock released');
        return { success: true };
      } catch (error) {
        return { success: false, error: error.message };
      }
    }
    return { success: false, error: 'No active wake lock' };
  }
}

// 导出默认对象
export default {
  isMobile,
  isIOS,
  isAndroid,
  getDeviceInfo,
  GestureDetector,
  GESTURE_CONFIG,
  requestPermission,
  checkPermission,
  PERMISSIONS,
  PWAInstallManager,
  NativeBridge,
  lockOrientation,
  unlockOrientation,
  enterFullscreen,
  exitFullscreen,
  isFullscreen,
  WakeLock
};
