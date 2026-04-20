/**
 * 国际化配置 (i18n) - LiveMirror
 * 支持多语言：中文 (zh)、英文 (en)、日文 (ja)、韩文 (ko)
 */

import { createI18n } from 'vue-i18n';
import type { Locale, I18nOptions } from 'vue-i18n';

// 导入语言包
import zh from '../locales/zh.json';
import en from '../locales/en.json';
import ja from '../locales/ja.json';
import ko from '../locales/ko.json';

// 支持的语言列表
export const supportedLocales: Locale[] = ['zh', 'en', 'ja', 'ko'];

// 语言名称映射
export const localeNames: Record<Locale, string> = {
  zh: '中文',
  en: 'English',
  ja: '日本語',
  ko: '한국어'
};

// 语言标志映射（可选）
export const localeFlags: Record<Locale, string> = {
  zh: '🇨🇳',
  en: '🇺🇸',
  ja: '🇯🇵',
  ko: '🇰🇷'
};

// 默认语言
const DEFAULT_LOCALE: Locale = 'zh';

// 本地存储键
const LOCALE_STORAGE_KEY = 'livemirror_locale';

// 消息定义
const messages = {
  zh,
  en,
  ja,
  ko
};

/**
 * 检测用户语言
 * 优先级：
 * 1. 本地存储的语言设置
 * 2. 浏览器语言设置
 * 3. 默认语言
 */
export function detectLocale(): Locale {
  // 1. 检查本地存储
  const storedLocale = localStorage.getItem(LOCALE_STORAGE_KEY);
  if (storedLocale && supportedLocales.includes(storedLocale)) {
    return storedLocale;
  }

  // 2. 检查浏览器语言
  const browserLocale = navigator.language.split('-')[0];
  if (supportedLocales.includes(browserLocale)) {
    return browserLocale;
  }

  // 3. 返回默认语言
  return DEFAULT_LOCALE;
}

/**
 * 保存语言设置
 */
export function saveLocale(locale: Locale): void {
  localStorage.setItem(LOCALE_STORAGE_KEY, locale);
}

/**
 * 获取当前语言
 */
export function getCurrentLocale(): Locale {
  return storedLocale || detectLocale();
}

// 存储当前语言
let storedLocale: Locale | null = null;

/**
 * 创建 i18n 实例
 */
export const i18n = createI18n({
  legacy: false, // 使用 Composition API
  locale: detectLocale(),
  fallbackLocale: 'en',
  messages,
  silentFallbackWarn: true,
  silentTranslationWarn: true,
});

// 初始化时保存当前语言
storedLocale = i18n.global.locale.value as Locale;

/**
 * 切换语言
 */
export async function setLocale(locale: Locale): Promise<void> {
  if (!supportedLocales.includes(locale)) {
    console.warn(`Unsupported locale: ${locale}`);
    return;
  }

  // 如果语言包未加载，动态加载
  if (!messages[locale]) {
    try {
      const localeMessages = await import(`../locales/${locale}.json`);
      i18n.global.setLocaleMessage(locale, localeMessages.default);
    } catch (error) {
      console.error(`Failed to load locale: ${locale}`, error);
      return;
    }
  }

  // 设置语言
  i18n.global.locale.value = locale;
  storedLocale = locale;
  
  // 保存到本地存储
  saveLocale(locale);
  
  // 设置 HTML lang 属性
  document.documentElement.lang = locale;
}

/**
 * 获取语言切换器选项
 */
export function getLocaleOptions(): Array<{
  code: Locale;
  name: string;
  flag: string;
}> {
  return supportedLocales.map(code => ({
    code,
    name: localeNames[code],
    flag: localeFlags[code]
  }));
}

/**
 * 自动检测文本语言（简单实现）
 * 更准确的检测需要后端支持
 */
export function detectTextLanguage(text: string): Locale {
  const patterns: Array<{ locale: Locale; pattern: RegExp }> = [
    { locale: 'zh', pattern: /[\u4e00-\u9fff]/ },
    { locale: 'ja', pattern: /[\u3040-\u309f\u30a0-\u30ff]/ },
    { locale: 'ko', pattern: /[\uac00-\ud7af]/ },
  ];

  for (const { locale, pattern } of patterns) {
    if (pattern.test(text)) {
      return locale;
    }
  }

  return 'en';
}

// 导出默认
export default i18n;
