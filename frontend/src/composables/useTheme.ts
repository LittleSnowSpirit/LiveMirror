/**
 * LiveMirror Theme Composable
 * Vue 3 主题切换逻辑
 * 
 * 功能:
 * - 响应式主题状态
 * - 主题切换
 * - 系统主题自动跟随
 * - 主题偏好持久化
 * - 自定义主题色
 */

import { ref, computed, watch, onMounted, onUnmounted, type Ref } from 'vue';
import {
  ThemeMode,
  getStoredTheme,
  saveThemePreference,
  getCustomColors,
  saveCustomColors,
  getSystemTheme,
  getEffectiveTheme,
  applyTheme,
  applyCustomColors,
  watchSystemTheme
} from '../utils/theme';

export interface ThemeConfig {
  mode: ThemeMode;
  customColors: Record<string, string>;
}

export interface UseThemeReturn {
  /** 当前主题模式 */
  themeMode: Ref<ThemeMode>;
  /** 实际生效的主题 (light/dark) */
  actualTheme: Ref<'light' | 'dark'>;
  /** 是否为暗黑模式 */
  isDark: Ref<boolean>;
  /** 是否为明亮模式 */
  isLight: Ref<boolean>;
  /** 是否跟随系统主题 */
  isSystem: Ref<boolean>;
  /** 自定义颜色 */
  customColors: Ref<Record<string, string>>;
  /** 切换主题模式 */
  setThemeMode: (mode: ThemeMode) => void;
  /** 切换暗黑/明亮 */
  toggleTheme: () => void;
  /** 设置自定义颜色 */
  setCustomColor: (property: string, value: string) => void;
  /** 重置自定义颜色 */
  resetCustomColor: (property: string) => void;
  /** 重置所有自定义颜色 */
  resetAllCustomColors: () => void;
  /** 重置为主题默认值 */
  resetTheme: () => void;
  /** 导出主题配置 */
  exportConfig: () => string;
  /** 导入主题配置 */
  importConfig: (jsonString: string) => boolean;
}

/**
 * 主题 Composable
 */
export function useTheme(): UseThemeReturn {
  // 主题模式状态
  const themeMode = ref<ThemeMode>(ThemeMode.SYSTEM);
  
  // 自定义颜色状态
  const customColors = ref<Record<string, string>>({});
  
  // 实际生效的主题 (计算属性)
  const actualTheme = computed<'light' | 'dark'>(() => {
    return getEffectiveTheme(themeMode.value) as 'light' | 'dark';
  });
  
  // 是否为暗黑模式
  const isDark = computed<boolean>(() => actualTheme.value === 'dark');
  
  // 是否为明亮模式
  const isLight = computed<boolean>(() => actualTheme.value === 'light');
  
  // 是否跟随系统主题
  const isSystem = computed<boolean>(() => themeMode.value === ThemeMode.SYSTEM);
  
  // 系统主题监听器
  let unwatchSystem: (() => void) | null = null;
  
  /**
   * 应用当前主题
   */
  function applyCurrentTheme() {
    applyTheme(themeMode.value);
  }
  
  /**
   * 应用自定义颜色
   */
  function applyCurrentCustomColors() {
    applyCustomColors(customColors.value);
  }
  
  /**
   * 设置主题模式
   */
  function setThemeMode(mode: ThemeMode) {
    themeMode.value = mode;
    saveThemePreference({
      mode,
      customColors: customColors.value
    });
    applyCurrentTheme();
  }
  
  /**
   * 切换主题 (暗黑/明亮)
   */
  function toggleTheme() {
    if (themeMode.value === ThemeMode.SYSTEM) {
      // 如果当前是系统主题，切换到与系统相反的主题
      const systemTheme = getSystemTheme();
      setThemeMode(systemTheme === ThemeMode.DARK ? ThemeMode.LIGHT : ThemeMode.DARK);
    } else {
      // 在暗黑和明亮之间切换
      setThemeMode(themeMode.value === ThemeMode.DARK ? ThemeMode.LIGHT : ThemeMode.DARK);
    }
  }
  
  /**
   * 设置自定义颜色
   */
  function setCustomColor(property: string, value: string) {
    customColors.value[property] = value;
    saveThemePreference({
      mode: themeMode.value,
      customColors: customColors.value
    });
    applyCurrentCustomColors();
  }
  
  /**
   * 重置单个自定义颜色
   */
  function resetCustomColor(property: string) {
    delete customColors.value[property];
    saveThemePreference({
      mode: themeMode.value,
      customColors: customColors.value
    });
    
    // 从 DOM 移除该自定义属性
    if (typeof document !== 'undefined') {
      document.documentElement.style.removeProperty(property);
    }
  }
  
  /**
   * 重置所有自定义颜色
   */
  function resetAllCustomColors() {
    customColors.value = {};
    saveThemePreference({
      mode: themeMode.value,
      customColors: {}
    });
    
    // 清除所有自定义样式
    if (typeof document !== 'undefined') {
      const root = document.documentElement;
      // 只清除我们管理的自定义属性
      const customPrefix = '--color-';
      Array.from(root.style)
        .filter(prop => prop.startsWith(customPrefix))
        .forEach(prop => root.style.removeProperty(prop));
    }
  }
  
  /**
   * 重置主题
   */
  function resetTheme() {
    themeMode.value = ThemeMode.SYSTEM;
    customColors.value = {};
    saveThemePreference({
      mode: ThemeMode.SYSTEM,
      customColors: {}
    });
    applyCurrentTheme();
  }
  
  /**
   * 导出主题配置
   */
  function exportConfig(): string {
    const config = {
      preference: {
        mode: themeMode.value,
        customColors: customColors.value
      },
      exportedAt: new Date().toISOString()
    };
    return JSON.stringify(config, null, 2);
  }
  
  /**
   * 导入主题配置
   */
  function importConfig(jsonString: string): boolean {
    try {
      const config = JSON.parse(jsonString);
      
      if (config.preference) {
        if (config.preference.mode) {
          themeMode.value = config.preference.mode;
        }
        if (config.preference.customColors) {
          customColors.value = config.preference.customColors;
        }
        
        saveThemePreference({
          mode: themeMode.value,
          customColors: customColors.value
        });
        
        applyCurrentTheme();
        applyCurrentCustomColors();
      }
      
      return true;
    } catch (error) {
      console.error('Failed to import theme config:', error);
      return false;
    }
  }
  
  /**
   * 监听系统主题变化
   */
  function handleSystemThemeChange(newSystemTheme: ThemeMode) {
    if (themeMode.value === ThemeMode.SYSTEM) {
      applyTheme(ThemeMode.SYSTEM);
    }
  }
  
  // 组件挂载时初始化
  onMounted(() => {
    // 从存储加载主题配置
    const stored = getStoredTheme();
    themeMode.value = stored.mode || ThemeMode.SYSTEM;
    customColors.value = stored.customColors || {};
    
    // 应用主题
    applyCurrentTheme();
    applyCurrentCustomColors();
    
    // 监听系统主题变化
    unwatchSystem = watchSystemTheme(handleSystemThemeChange);
  });
  
  // 组件卸载时清理
  onUnmounted(() => {
    if (unwatchSystem) {
      unwatchSystem();
    }
  });
  
  return {
    themeMode,
    actualTheme,
    isDark,
    isLight,
    isSystem,
    customColors,
    setThemeMode,
    toggleTheme,
    setCustomColor,
    resetCustomColor,
    resetAllCustomColors,
    resetTheme,
    exportConfig,
    importConfig
  };
}

export default useTheme;
