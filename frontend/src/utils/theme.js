/**
 * LiveMirror Theme Manager
 * 主题管理工具
 * 
 * 功能:
 * - 主题切换 (暗黑/明亮)
 * - 系统主题自动跟随
 * - 主题偏好持久化
 * - 自定义主题色
 */

const STORAGE_KEY = 'livemirror_theme_preference';
const CUSTOM_COLORS_KEY = 'livemirror_custom_colors';

/**
 * 主题枚举
 */
export const ThemeMode = {
  LIGHT: 'light',
  DARK: 'dark',
  SYSTEM: 'system'
};

/**
 * 默认主题配置
 */
const DEFAULT_CONFIG = {
  mode: ThemeMode.SYSTEM,
  customColors: {}
};

/**
 * 获取存储的主题偏好
 */
export function getStoredTheme() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      return JSON.parse(stored);
    }
  } catch (error) {
    console.warn('Failed to read theme preference:', error);
  }
  return DEFAULT_CONFIG;
}

/**
 * 保存主题偏好
 */
export function saveThemePreference(config) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(config));
  } catch (error) {
    console.warn('Failed to save theme preference:', error);
  }
}

/**
 * 获取自定义颜色
 */
export function getCustomColors() {
  try {
    const stored = localStorage.getItem(CUSTOM_COLORS_KEY);
    if (stored) {
      return JSON.parse(stored);
    }
  } catch (error) {
    console.warn('Failed to read custom colors:', error);
  }
  return {};
}

/**
 * 保存自定义颜色
 */
export function saveCustomColors(colors) {
  try {
    localStorage.setItem(CUSTOM_COLORS_KEY, JSON.stringify(colors));
  } catch (error) {
    console.warn('Failed to save custom colors:', error);
  }
}

/**
 * 检测系统主题偏好
 */
export function getSystemTheme() {
  if (typeof window === 'undefined' || !window.matchMedia) {
    return ThemeMode.LIGHT;
  }
  
  return window.matchMedia('(prefers-color-scheme: dark)').matches
    ? ThemeMode.DARK
    : ThemeMode.LIGHT;
}

/**
 * 获取实际应该应用的主题
 */
export function getEffectiveTheme(mode) {
  if (mode === ThemeMode.SYSTEM) {
    return getSystemTheme();
  }
  return mode || ThemeMode.LIGHT;
}

/**
 * 应用主题到 DOM
 */
export function applyTheme(theme) {
  if (typeof document === 'undefined') {
    return;
  }
  
  const root = document.documentElement;
  const effectiveTheme = getEffectiveTheme(theme);
  
  // 移除过渡效果以避免初始加载时的闪烁
  root.classList.add('no-transition');
  
  // 设置主题属性
  root.setAttribute('data-theme', effectiveTheme);
  
  // 强制重绘
  requestAnimationFrame(() => {
    requestAnimationFrame(() => {
      root.classList.remove('no-transition');
    });
  });
  
  // 更新 meta theme-color
  updateMetaThemeColor(effectiveTheme);
}

/**
 * 更新 meta theme-color
 */
function updateMetaThemeColor(theme) {
  if (typeof document === 'undefined') {
    return;
  }
  
  let metaThemeColor = document.querySelector('meta[name="theme-color"]');
  
  if (!metaThemeColor) {
    metaThemeColor = document.createElement('meta');
    metaThemeColor.setAttribute('name', 'theme-color');
    document.head.appendChild(metaThemeColor);
  }
  
  const color = theme === 'dark' ? '#0d0d0d' : '#ffffff';
  metaThemeColor.setAttribute('content', color);
}

/**
 * 应用自定义颜色
 */
export function applyCustomColors(colors) {
  if (typeof document === 'undefined') {
    return;
  }
  
  const root = document.documentElement;
  
  Object.entries(colors).forEach(([property, value]) => {
    root.style.setProperty(property, value);
  });
}

/**
 * 监听系统主题变化
 */
export function watchSystemTheme(callback) {
  if (typeof window === 'undefined' || !window.matchMedia) {
    return () => {};
  }
  
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
  
  const handleChange = (event) => {
    const newTheme = event.matches ? ThemeMode.DARK : ThemeMode.LIGHT;
    callback(newTheme);
  };
  
  // 现代浏览器
  if (mediaQuery.addEventListener) {
    mediaQuery.addEventListener('change', handleChange);
  } else if (mediaQuery.addListener) {
    // 旧版浏览器兼容
    mediaQuery.addListener(handleChange);
  }
  
  // 返回取消监听函数
  return () => {
    if (mediaQuery.removeEventListener) {
      mediaQuery.removeEventListener('change', handleChange);
    } else if (mediaQuery.removeListener) {
      mediaQuery.removeListener(handleChange);
    }
  };
}

/**
 * 重置为默认主题
 */
export function resetTheme() {
  saveThemePreference(DEFAULT_CONFIG);
  localStorage.removeItem(CUSTOM_COLORS_KEY);
  applyTheme(DEFAULT_CONFIG.mode);
}

/**
 * 导出主题配置
 */
export function exportThemeConfig() {
  const config = {
    preference: getStoredTheme(),
    customColors: getCustomColors(),
    exportedAt: new Date().toISOString()
  };
  return JSON.stringify(config, null, 2);
}

/**
 * 导入主题配置
 */
export function importThemeConfig(jsonString) {
  try {
    const config = JSON.parse(jsonString);
    
    if (config.preference) {
      saveThemePreference(config.preference);
      applyTheme(config.preference.mode);
    }
    
    if (config.customColors) {
      saveCustomColors(config.customColors);
      applyCustomColors(config.customColors);
    }
    
    return true;
  } catch (error) {
    console.error('Failed to import theme config:', error);
    return false;
  }
}

/**
 * 初始化主题
 */
export function initTheme() {
  const config = getStoredTheme();
  applyTheme(config.mode);
  
  // 如果有自定义颜色，应用它们
  const customColors = getCustomColors();
  if (Object.keys(customColors).length > 0) {
    applyCustomColors(customColors);
  }
  
  return config;
}
