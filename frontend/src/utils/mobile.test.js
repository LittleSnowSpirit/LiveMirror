/**
 * LiveMirror 移动端功能测试
 * 
 * 测试覆盖：
 * 1. 设备检测
 * 2. 手势交互
 * 3. 权限管理
 * 4. PWA 安装
 * 5. 原生功能桥接
 */

import {
  isMobile,
  isIOS,
  isAndroid,
  getDeviceInfo,
  GestureDetector,
  requestPermission,
  checkPermission,
  PERMISSIONS,
  PWAInstallManager,
  NativeBridge,
  WakeLock
} from './mobile';

// ==================== 设备检测测试 ====================

describe('设备检测', () => {
  test('isMobile 应该正确检测移动设备', () => {
    // 保存原始 userAgent
    const originalUserAgent = navigator.userAgent;
    
    // 测试 iOS
    Object.defineProperty(navigator, 'userAgent', {
      value: 'iPhone OS 14_0 like Mac OS X',
      configurable: true
    });
    expect(isMobile()).toBe(true);
    
    // 测试 Android
    Object.defineProperty(navigator, 'userAgent', {
      value: 'Android 10; Mobile',
      configurable: true
    });
    expect(isMobile()).toBe(true);
    
    // 测试桌面
    Object.defineProperty(navigator, 'userAgent', {
      value: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
      configurable: true
    });
    expect(isMobile()).toBe(false);
    
    // 恢复原始 userAgent
    Object.defineProperty(navigator, 'userAgent', {
      value: originalUserAgent,
      configurable: true
    });
  });
  
  test('isIOS 应该正确检测 iOS 设备', () => {
    const originalUserAgent = navigator.userAgent;
    
    Object.defineProperty(navigator, 'userAgent', {
      value: 'iPhone OS 14_0 like Mac OS X',
      configurable: true
    });
    expect(isIOS()).toBe(true);
    
    Object.defineProperty(navigator, 'userAgent', {
      value: 'Android 10; Mobile',
      configurable: true
    });
    expect(isIOS()).toBe(false);
    
    Object.defineProperty(navigator, 'userAgent', {
      value: originalUserAgent,
      configurable: true
    });
  });
  
  test('isAndroid 应该正确检测 Android 设备', () => {
    const originalUserAgent = navigator.userAgent;
    
    Object.defineProperty(navigator, 'userAgent', {
      value: 'Android 10; Mobile',
      configurable: true
    });
    expect(isAndroid()).toBe(true);
    
    Object.defineProperty(navigator, 'userAgent', {
      value: 'iPhone OS 14_0 like Mac OS X',
      configurable: true
    });
    expect(isAndroid()).toBe(false);
    
    Object.defineProperty(navigator, 'userAgent', {
      value: originalUserAgent,
      configurable: true
    });
  });
  
  test('getDeviceInfo 应该返回设备信息', () => {
    const info = getDeviceInfo();
    
    expect(info).toHaveProperty('isMobile');
    expect(info).toHaveProperty('isIOS');
    expect(info).toHaveProperty('isAndroid');
    expect(info).toHaveProperty('userAgent');
    expect(info).toHaveProperty('platform');
    expect(info).toHaveProperty('screen');
    expect(info.screen).toHaveProperty('width');
    expect(info.screen).toHaveProperty('height');
    expect(info.screen).toHaveProperty('pixelRatio');
  });
});

// ==================== 手势检测测试 ====================

describe('手势检测', () => {
  test('GestureDetector 应该正确初始化', () => {
    const element = document.createElement('div');
    const detector = new GestureDetector(element);
    
    expect(detector).toBeDefined();
    expect(detector.element).toBe(element);
    
    detector.destroy();
  });
  
  test('GestureDetector 应该注册触摸事件监听器', () => {
    const element = document.createElement('div');
    const addEventListenerSpy = jest.spyOn(element, 'addEventListener');
    
    const detector = new GestureDetector(element);
    
    expect(addEventListenerSpy).toHaveBeenCalledWith('touchstart', expect.any(Function), { passive: true });
    expect(addEventListenerSpy).toHaveBeenCalledWith('touchmove', expect.any(Function), { passive: true });
    expect(addEventListenerSpy).toHaveBeenCalledWith('touchend', expect.any(Function), { passive: true });
    
    detector.destroy();
    addEventListenerSpy.mockRestore();
  });
  
  test('手势回调应该被正确调用', (done) => {
    const element = document.createElement('div');
    const onSwipeLeft = jest.fn();
    
    const detector = new GestureDetector(element, { onSwipeLeft });
    
    // 模拟触摸事件
    const touchStartEvent = new TouchEvent('touchstart', {
      touches: [{ clientX: 100, clientY: 100 }]
    });
    
    const touchEndEvent = new TouchEvent('touchend', {
      changedTouches: [{ clientX: 50, clientY: 100 }]
    });
    
    element.dispatchEvent(touchStartEvent);
    
    setTimeout(() => {
      element.dispatchEvent(touchEndEvent);
      
      setTimeout(() => {
        expect(onSwipeLeft).toHaveBeenCalled();
        detector.destroy();
        done();
      }, 100);
    }, 100);
  });
});

// ==================== 权限管理测试 ====================

describe('权限管理', () => {
  test('requestPermission 应该处理未知权限', async () => {
    const result = await requestPermission('unknown');
    
    expect(result.granted).toBe(false);
    expect(result.error).toContain('Unknown permission');
  });
  
  test('checkPermission 应该返回权限状态', async () => {
    // 注意：实际测试需要浏览器环境
    const result = await checkPermission(PERMISSIONS.NOTIFICATION);
    
    expect(result).toBeDefined();
    expect(result).toHaveProperty('granted');
  });
  
  test('通知权限检测', async () => {
    if ('Notification' in window) {
      const result = await requestPermission(PERMISSIONS.NOTIFICATION);
      expect(result).toHaveProperty('granted');
    }
  });
});

// ==================== PWA 安装测试 ====================

describe('PWA 安装管理', () => {
  test('PWAInstallManager 应该正确初始化', () => {
    const manager = new PWAInstallManager();
    
    expect(manager).toBeDefined();
    expect(manager).toHaveProperty('isInstalled');
    expect(manager).toHaveProperty('canInstall');
    expect(manager).toHaveProperty('promptInstall');
  });
  
  test('检查安装状态', () => {
    const manager = new PWAInstallManager();
    const isInstalled = manager.checkInstallStatus();
    
    expect(typeof isInstalled).toBe('boolean');
  });
  
  test('iOS 安装指南', () => {
    const manager = new PWAInstallManager();
    const guide = manager.getIOSInstallGuide();
    
    expect(guide).toHaveProperty('steps');
    expect(guide.steps).toBeInstanceOf(Array);
    expect(guide.steps.length).toBeGreaterThan(0);
  });
});

// ==================== 原生功能桥接测试 ====================

describe('原生功能桥接', () => {
  test('NativeBridge 应该包含所有方法', () => {
    expect(NativeBridge).toHaveProperty('capturePhoto');
    expect(NativeBridge).toHaveProperty('recordAudio');
    expect(NativeBridge).toHaveProperty('share');
    expect(NativeBridge).toHaveProperty('clipboardWrite');
    expect(NativeBridge).toHaveProperty('clipboardRead');
    expect(NativeBridge).toHaveProperty('vibrate');
    expect(NativeBridge).toHaveProperty('getBattery');
    expect(NativeBridge).toHaveProperty('getNetworkInfo');
  });
  
  test('剪贴板写入', async () => {
    if (navigator.clipboard) {
      const result = await NativeBridge.clipboardWrite('test');
      expect(result).toHaveProperty('success');
    }
  });
  
  test('剪贴板读取', async () => {
    if (navigator.clipboard) {
      await NativeBridge.clipboardWrite('test data');
      const result = await NativeBridge.clipboardRead();
      expect(result.success).toBe(true);
      expect(result.text).toBe('test data');
    }
  });
  
  test('震动反馈', () => {
    const result = NativeBridge.vibrate(100);
    // 在不支持的设备上返回 false
    expect(typeof result).toBe('boolean');
  });
  
  test('获取网络信息', () => {
    const info = NativeBridge.getNetworkInfo();
    expect(info).toHaveProperty('online');
  });
});

// ==================== 唤醒锁定测试 ====================

describe('唤醒锁定', () => {
  test('WakeLock 应该正确初始化', () => {
    const wakeLock = new WakeLock();
    expect(wakeLock).toBeDefined();
    expect(wakeLock.wakeLock).toBeNull();
  });
  
  test('WakeLock 请求和释放', async () => {
    const wakeLock = new WakeLock();
    
    if ('wakeLock' in navigator) {
      const requestResult = await wakeLock.request();
      expect(requestResult).toHaveProperty('success');
      
      const releaseResult = await wakeLock.release();
      expect(releaseResult).toHaveProperty('success');
    } else {
      // 不支持的设备
      const result = await wakeLock.request();
      expect(result.success).toBe(false);
      expect(result.error).toContain('not supported');
    }
  });
});

// ==================== 屏幕方向测试 ====================

import { lockOrientation, unlockOrientation, enterFullscreen, exitFullscreen, isFullscreen } from './mobile';

describe('屏幕方向和全屏', () => {
  test('锁屏方向', async () => {
    const result = await lockOrientation('portrait');
    expect(result).toHaveProperty('success');
  });
  
  test('解锁屏方向', async () => {
    const result = await unlockOrientation();
    expect(result).toHaveProperty('success');
  });
  
  test('全屏检测', () => {
    const fullscreen = isFullscreen();
    expect(typeof fullscreen).toBe('boolean');
  });
});

// ==================== 离线缓存测试 ====================

describe('离线缓存', () => {
  test('Service Worker 注册', async () => {
    if ('serviceWorker' in navigator) {
      // 检查 SW 文件是否存在
      const response = await fetch('/service-worker/sw.js');
      expect(response.status).toBe(200);
    }
  });
  
  test('缓存存储', () => {
    if ('caches' in window) {
      expect(window.caches).toBeDefined();
    }
  });
  
  test('localStorage 可用性', () => {
    expect(localStorage).toBeDefined();
    
    // 测试读写
    localStorage.setItem('test', 'data');
    expect(localStorage.getItem('test')).toBe('data');
    localStorage.removeItem('test');
  });
});

// ==================== 推送通知测试 ====================

describe('推送通知', () => {
  test('Notification API 可用性', () => {
    expect('Notification' in window).toBe(true);
  });
  
  test('PushManager API 可用性', () => {
    expect('PushManager' in window).toBe(true);
  });
  
  test('通知权限状态', () => {
    if ('Notification' in window) {
      expect(['default', 'granted', 'denied']).toContain(Notification.permission);
    }
  });
});

// ==================== 性能测试 ====================

describe('性能测试', () => {
  test('手势检测器创建时间', () => {
    const element = document.createElement('div');
    
    const startTime = performance.now();
    const detector = new GestureDetector(element);
    const endTime = performance.now();
    
    expect(endTime - startTime).toBeLessThan(100); // 应该小于 100ms
    
    detector.destroy();
  });
  
  test('权限检查响应时间', async () => {
    const startTime = performance.now();
    await checkPermission(PERMISSIONS.NOTIFICATION);
    const endTime = performance.now();
    
    expect(endTime - startTime).toBeLessThan(1000); // 应该小于 1s
  });
});

// ==================== 兼容性测试 ====================

describe('兼容性测试', () => {
  test('移动端 API 检测', () => {
    const apis = {
      touch: 'ontouchstart' in window,
      notification: 'Notification' in window,
      serviceWorker: 'serviceWorker' in navigator,
      pushManager: 'PushManager' in window,
      mediaDevices: 'mediaDevices' in navigator,
      clipboard: 'clipboard' in navigator,
      wakeLock: 'wakeLock' in navigator
    };
    
    console.log('API 支持情况:', apis);
    
    // 至少应该支持基础 API
    expect(apis.touch).toBe(true);
  });
});
