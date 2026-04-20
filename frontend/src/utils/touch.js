/**
 * 触摸手势处理工具
 * 支持滑动、缩放、双击等手势
 */

// 手势配置
const GESTURE_CONFIG = {
  // 滑动阈值（像素）
  SWIPE_THRESHOLD: 50,
  // 双击时间间隔（毫秒）
  DOUBLE_TAP_INTERVAL: 300,
  // 长按时间（毫秒）
  LONG_PRESS_DURATION: 500,
  // 缩放最小/最大倍数
  ZOOM_MIN: 0.5,
  ZOOM_MAX: 3,
}

// 存储触摸状态
const touchState = {
  startX: 0,
  startY: 0,
  lastX: 0,
  lastY: 0,
  startTime: 0,
  lastTapTime: 0,
  longPressTimer: null,
  isPinching: false,
  initialPinchDistance: 0,
  currentScale: 1,
}

/**
 * 计算两点间距离（用于捏合缩放）
 */
function getDistance(touch1, touch2) {
  const dx = touch1.clientX - touch2.clientX
  const dy = touch1.clientY - touch2.clientY
  return Math.sqrt(dx * dx + dy * dy)
}

/**
 * 计算中点（用于捏合缩放中心）
 */
function getMidpoint(touch1, touch2) {
  return {
    x: (touch1.clientX + touch2.clientX) / 2,
    y: (touch1.clientY + touch2.clientY) / 2,
  }
}

/**
 * 触摸手势类
 */
export class TouchGesture {
  constructor(element, options = {}) {
    this.element = element
    this.options = {
      onSwipe: options.onSwipe || (() => {}),
      onPinch: options.onPinch || (() => {}),
      onDoubleTap: options.onDoubleTap || (() => {}),
      onLongPress: options.onLongPress || (() => {}),
      onTap: options.onTap || (() => {}),
      ...options,
    }
    
    this.bindEvents()
  }
  
  bindEvents() {
    this.element.addEventListener('touchstart', this.handleTouchStart.bind(this), { passive: false })
    this.element.addEventListener('touchmove', this.handleTouchMove.bind(this), { passive: false })
    this.element.addEventListener('touchend', this.handleTouchEnd.bind(this), { passive: false })
    this.element.addEventListener('touchcancel', this.handleTouchCancel.bind(this), { passive: false })
  }
  
  handleTouchStart(event) {
    const touches = event.touches
    
    // 阻止默认行为（如页面滚动）
    if (this.options.preventScroll) {
      event.preventDefault()
    }
    
    // 清除长按计时器
    if (touchState.longPressTimer) {
      clearTimeout(touchState.longPressTimer)
    }
    
    // 单指触摸
    if (touches.length === 1) {
      const touch = touches[0]
      touchState.startX = touch.clientX
      touchState.startY = touch.clientY
      touchState.lastX = touch.clientX
      touchState.lastY = touch.clientY
      touchState.startTime = Date.now()
      touchState.isPinching = false
      
      // 设置长按计时器
      touchState.longPressTimer = setTimeout(() => {
        this.options.onLongPress({
          x: touch.clientX,
          y: touch.clientY,
          target: event.target,
        })
        touchState.longPressTimer = null
      }, GESTURE_CONFIG.LONG_PRESS_DURATION)
    }
    
    // 双指触摸（捏合）
    if (touches.length === 2) {
      touchState.isPinching = true
      touchState.initialPinchDistance = getDistance(touches[0], touches[1])
      touchState.currentScale = 1
      
      if (touchState.longPressTimer) {
        clearTimeout(touchState.longPressTimer)
      }
    }
  }
  
  handleTouchMove(event) {
    const touches = event.touches
    
    if (this.options.preventScroll) {
      event.preventDefault()
    }
    
    // 清除长按计时器
    if (touchState.longPressTimer) {
      clearTimeout(touchState.longPressTimer)
      touchState.longPressTimer = null
    }
    
    // 单指滑动
    if (touches.length === 1 && !touchState.isPinching) {
      const touch = touches[0]
      touchState.lastX = touch.clientX
      touchState.lastY = touch.clientY
    }
    
    // 双指捏合缩放
    if (touches.length === 2 && touchState.isPinching) {
      const currentDistance = getDistance(touches[0], touches[1])
      const midpoint = getMidpoint(touches[0], touches[1])
      
      const scaleChange = currentDistance / touchState.initialPinchDistance
      const newScale = Math.max(
        GESTURE_CONFIG.ZOOM_MIN,
        Math.min(GESTURE_CONFIG.ZOOM_MAX, scaleChange)
      )
      
      this.options.onPinch({
        scale: newScale,
        midpoint,
        touches,
      })
    }
  }
  
  handleTouchEnd(event) {
    const touches = event.touches
    const changedTouch = event.changedTouches[0]
    
    // 清除长按计时器
    if (touchState.longPressTimer) {
      clearTimeout(touchState.longPressTimer)
      touchState.longPressTimer = null
    }
    
    // 捏合结束
    if (touchState.isPinching) {
      touchState.isPinching = false
      return
    }
    
    // 计算滑动距离和时间
    const deltaX = touchState.lastX - touchState.startX
    const deltaY = touchState.lastY - touchState.startY
    const deltaTime = Date.now() - touchState.startTime
    
    // 检测滑动方向
    if (Math.abs(deltaX) > GESTURE_CONFIG.SWIPE_THRESHOLD ||
        Math.abs(deltaY) > GESTURE_CONFIG.SWIPE_THRESHOLD) {
      
      let direction = ''
      
      if (Math.abs(deltaX) > Math.abs(deltaY)) {
        direction = deltaX > 0 ? 'right' : 'left'
      } else {
        direction = deltaY > 0 ? 'down' : 'up'
      }
      
      this.options.onSwipe({
        direction,
        deltaX,
        deltaY,
        duration: deltaTime,
        target: event.target,
      })
    } else {
      // 点击或双击
      const currentTime = Date.now()
      
      if (currentTime - touchState.lastTapTime < GESTURE_CONFIG.DOUBLE_TAP_INTERVAL) {
        // 双击
        this.options.onDoubleTap({
          x: changedTouch.clientX,
          y: changedTouch.clientY,
          target: event.target,
        })
        touchState.lastTapTime = 0
      } else {
        // 单击
        this.options.onTap({
          x: changedTouch.clientX,
          y: changedTouch.clientY,
          target: event.target,
        })
        touchState.lastTapTime = currentTime
      }
    }
  }
  
  handleTouchCancel() {
    if (touchState.longPressTimer) {
      clearTimeout(touchState.longPressTimer)
      touchState.longPressTimer = null
    }
    touchState.isPinching = false
  }
  
  destroy() {
    this.element.removeEventListener('touchstart', this.handleTouchStart)
    this.element.removeEventListener('touchmove', this.handleTouchMove)
    this.element.removeEventListener('touchend', this.handleTouchEnd)
    this.element.removeEventListener('touchcancel', this.handleTouchCancel)
    
    if (touchState.longPressTimer) {
      clearTimeout(touchState.longPressTimer)
    }
  }
}

/**
 * 创建滑动导航（左右滑动切换页面）
 */
export function createSwipeNavigation(element, callbacks = {}) {
  const gesture = new TouchGesture(element, {
    preventScroll: false,
    onSwipe: (event) => {
      if (event.direction === 'left' && callbacks.onNext) {
        callbacks.onNext()
      } else if (event.direction === 'right' && callbacks.onPrev) {
        callbacks.onPrev()
      }
    },
  })
  
  return {
    destroy: () => gesture.destroy(),
  }
}

/**
 * 创建图片缩放功能
 */
export function createImageZoom(element, options = {}) {
  let currentScale = 1
  let isZoomed = false
  
  const gesture = new TouchGesture(element, {
    preventScroll: true,
    onPinch: (event) => {
      currentScale = event.scale
      element.style.transform = `scale(${currentScale})`
      element.style.transformOrigin = `${event.midpoint.x}px ${event.midpoint.y}px`
      
      if (currentScale > 1 && !isZoomed) {
        isZoomed = true
        options.onZoomIn?.()
      } else if (currentScale <= 1 && isZoomed) {
        isZoomed = false
        options.onZoomOut?.()
      }
    },
    onDoubleTap: (event) => {
      if (isZoomed) {
        currentScale = 1
        element.style.transform = 'scale(1)'
        isZoomed = false
        options.onZoomOut?.()
      } else {
        currentScale = 2
        element.style.transform = `scale(2)`
        element.style.transformOrigin = `${event.x}px ${event.y}px`
        isZoomed = true
        options.onZoomIn?.()
      }
    },
  })
  
  return {
    reset: () => {
      currentScale = 1
      isZoomed = false
      element.style.transform = 'scale(1)'
    },
    destroy: () => gesture.destroy(),
  }
}

/**
 * 检测是否为移动设备
 */
export function isMobileDevice() {
  return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
}

/**
 * 检测是否为触摸设备
 */
export function isTouchDevice() {
  return 'ontouchstart' in window || navigator.maxTouchPoints > 0
}

/**
 * 添加触摸反馈效果
 */
export function addTouchFeedback(elements) {
  const elementList = Array.isArray(elements) ? elements : [elements]
  
  elementList.forEach(el => {
    if (!el) return
    
    el.addEventListener('touchstart', () => {
      el.classList.add('touch-active')
    }, { passive: true })
    
    el.addEventListener('touchend', () => {
      el.classList.remove('touch-active')
    }, { passive: true })
    
    el.addEventListener('touchcancel', () => {
      el.classList.remove('touch-active')
    }, { passive: true })
  })
}

export default {
  TouchGesture,
  createSwipeNavigation,
  createImageZoom,
  isMobileDevice,
  isTouchDevice,
  addTouchFeedback,
}
