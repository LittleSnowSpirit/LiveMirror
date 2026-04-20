/**
 * 移动端响应式测试脚本
 * 测试不同屏幕尺寸下的布局表现
 */

// 测试断点
const BREAKPOINTS = {
  xs: 320,   // 小手机
  sm: 480,   // 大手机
  md: 768,   // 平板
  lg: 1024,  // 小桌面
  xl: 1440,  // 大桌面
}

// 测试结果
const testResults = {
  passed: [],
  failed: [],
  warnings: [],
}

/**
 * 测试视口尺寸
 */
function testViewportSize(width, height = 800) {
  return new Promise((resolve) => {
    // 设置视口
    const metaViewport = document.querySelector('meta[name="viewport"]')
    if (metaViewport) {
      metaViewport.setAttribute('content', `width=${width}, initial-scale=1.0`)
    }
    
    // 触发 resize 事件
    window.dispatchEvent(new Event('resize'))
    
    setTimeout(() => {
      resolve({
        width: window.innerWidth,
        height: window.innerHeight,
      })
    }, 100)
  })
}

/**
 * 测试导航显示
 */
function testNavigation() {
  const mobileNav = document.querySelector('.mobile-nav-toggle')
  const desktopNav = document.querySelector('.main-nav')
  const width = window.innerWidth
  
  if (width <= 768) {
    // 移动端应该显示汉堡菜单
    if (mobileNav && getComputedStyle(mobileNav).display !== 'none') {
      testResults.passed.push(`[移动端] 汉堡菜单显示正常 (${width}px)`)
    } else {
      testResults.failed.push(`[移动端] 汉堡菜单未显示 (${width}px)`)
    }
    
    // 桌面导航应该隐藏
    if (desktopNav && getComputedStyle(desktopNav).display === 'none') {
      testResults.passed.push(`[移动端] 桌面导航隐藏正常 (${width}px)`)
    } else {
      testResults.warnings.push(`[移动端] 桌面导航可能未正确隐藏 (${width}px)`)
    }
  } else {
    // 桌面端应该显示桌面导航
    if (desktopNav && getComputedStyle(desktopNav).display !== 'none') {
      testResults.passed.push(`[桌面端] 导航显示正常 (${width}px)`)
    } else {
      testResults.failed.push(`[桌面端] 导航未显示 (${width}px)`)
    }
    
    // 移动端导航应该隐藏
    if (mobileNav && getComputedStyle(mobileNav).display === 'none') {
      testResults.passed.push(`[桌面端] 汉堡菜单隐藏正常 (${width}px)`)
    } else {
      testResults.warnings.push(`[桌面端] 汉堡菜单可能未正确隐藏 (${width}px)`)
    }
  }
}

/**
 * 测试触摸目标大小
 */
function testTouchTargets() {
  const interactiveElements = document.querySelectorAll('button, a, .el-button, .el-menu-item')
  let smallTargets = 0
  
  interactiveElements.forEach(el => {
    const rect = el.getBoundingClientRect()
    const minWidth = Math.min(rect.width, 44)
    const minHeight = Math.min(rect.height, 44)
    
    if (rect.width < 44 || rect.height < 44) {
      smallTargets++
    }
  })
  
  if (smallTargets === 0) {
    testResults.passed.push('[触摸] 所有交互元素尺寸 ≥ 44px')
  } else {
    testResults.warnings.push(`[触摸] ${smallTargets} 个交互元素尺寸 < 44px`)
  }
}

/**
 * 测试图片懒加载
 */
function testLazyLoading() {
  const lazyImages = document.querySelectorAll('img[loading="lazy"], .lazy-image')
  
  if (lazyImages.length > 0) {
    testResults.passed.push(`[性能] 发现 ${lazyImages.length} 个懒加载图片`)
  } else {
    testResults.warnings.push('[性能] 未发现懒加载图片')
  }
}

/**
 * 测试 PWA 配置
 */
function testPWA() {
  // 检查 manifest
  const manifest = document.querySelector('link[rel="manifest"]')
  if (manifest) {
    testResults.passed.push('[PWA] manifest.json 已配置')
  } else {
    testResults.failed.push('[PWA] manifest.json 未配置')
  }
  
  // 检查 Service Worker
  if ('serviceWorker' in navigator) {
    testResults.passed.push('[PWA] 支持 Service Worker')
  } else {
    testResults.warnings.push('[PWA] 不支持 Service Worker')
  }
  
  // 检查主题色
  const themeColor = document.querySelector('meta[name="theme-color"]')
  if (themeColor) {
    testResults.passed.push('[PWA] 主题色已配置')
  } else {
    testResults.warnings.push('[PWA] 主题色未配置')
  }
}

/**
 * 运行所有测试
 */
export async function runResponsiveTests() {
  console.log('🧪 开始响应式测试...')
  
  // 等待页面加载
  await new Promise(resolve => setTimeout(resolve, 500))
  
  // 测试每个断点
  for (const [name, width] of Object.entries(BREAKPOINTS)) {
    await testViewportSize(width)
    testNavigation()
  }
  
  // 其他测试
  testTouchTargets()
  testLazyLoading()
  testPWA()
  
  // 输出结果
  console.log('\n✅ 通过的测试:')
  testResults.passed.forEach(msg => console.log(`  ✓ ${msg}`))
  
  console.log('\n❌ 失败的测试:')
  testResults.failed.forEach(msg => console.log(`  ✗ ${msg}`))
  
  console.log('\n⚠️ 警告:')
  testResults.warnings.forEach(msg => console.log(`  ⚠ ${msg}`))
  
  console.log('\n📊 测试总结:')
  console.log(`  通过：${testResults.passed.length}`)
  console.log(`  失败：${testResults.failed.length}`)
  console.log(`  警告：${testResults.warnings.length}`)
  
  return {
    passed: testResults.passed.length,
    failed: testResults.failed.length,
    warnings: testResults.warnings.length,
    total: testResults.passed.length + testResults.failed.length + testResults.warnings.length,
  }
}

/**
 * 生成 Lighthouse 风格报告
 */
export function generateLighthouseReport() {
  const scores = {
    performance: 0,
    accessibility: 0,
    bestPractices: 0,
    seo: 0,
    pwa: 0,
  }
  
  // PWA 分数
  const manifest = document.querySelector('link[rel="manifest"]')
  const themeColor = document.querySelector('meta[name="theme-color"]')
  const swSupported = 'serviceWorker' in navigator
  
  if (manifest && themeColor && swSupported) {
    scores.pwa = 100
  } else if (manifest || themeColor) {
    scores.pwa = 50
  }
  
  // 性能分数（基于懒加载）
  const lazyImages = document.querySelectorAll('img[loading="lazy"]')
  if (lazyImages.length > 0) {
    scores.performance = 90
  } else {
    scores.performance = 70
  }
  
  // 可访问性分数（基于触摸目标）
  const interactiveElements = document.querySelectorAll('button, a')
  let accessibleElements = 0
  interactiveElements.forEach(el => {
    const rect = el.getBoundingClientRect()
    if (rect.width >= 44 && rect.height >= 44) {
      accessibleElements++
    }
  })
  scores.accessibility = Math.round((accessibleElements / interactiveElements.length) * 100) || 100
  
  // 最佳实践
  scores.bestPractices = 95
  
  // SEO
  const description = document.querySelector('meta[name="description"]')
  const title = document.title
  if (description && title) {
    scores.seo = 100
  } else if (title) {
    scores.seo = 80
  } else {
    scores.seo = 50
  }
  
  console.log('\n📈 Lighthouse 评分估算:')
  console.log(`  Performance: ${scores.performance}`)
  console.log(`  Accessibility: ${scores.accessibility}`)
  console.log(`  Best Practices: ${scores.bestPractices}`)
  console.log(`  SEO: ${scores.seo}`)
  console.log(`  PWA: ${scores.pwa}`)
  
  const average = Object.values(scores).reduce((a, b) => a + b, 0) / Object.keys(scores).length
  console.log(`\n  平均分：${Math.round(average)}`)
  
  return scores
}

// 自动运行测试（如果在浏览器环境）
if (typeof window !== 'undefined' && typeof document !== 'undefined') {
  // 延迟执行，等待页面完全加载
  setTimeout(() => {
    console.log('📱 移动端适配测试已加载')
    console.log('   运行 runResponsiveTests() 执行测试')
    console.log('   运行 generateLighthouseReport() 生成报告')
  }, 1000)
}

export default {
  runResponsiveTests,
  generateLighthouseReport,
  BREAKPOINTS,
}
