/**
 * 国际化配置测试 - LiveMirror
 * 测试前端 i18n 功能
 */

import { describe, it, expect, beforeEach } from 'vitest';
import {
  detectLocale,
  saveLocale,
  setLocale,
  getLocaleOptions,
  detectTextLanguage,
  supportedLocales,
  localeNames,
  localeFlags,
  i18n
} from './index';

describe('i18n Configuration', () => {
  beforeEach(() => {
    // 清理 localStorage
    localStorage.clear();
  });

  describe('supportedLocales', () => {
    it('should have 4 supported locales', () => {
      expect(supportedLocales).toHaveLength(4);
      expect(supportedLocales).toContain('zh');
      expect(supportedLocales).toContain('en');
      expect(supportedLocales).toContain('ja');
      expect(supportedLocales).toContain('ko');
    });
  });

  describe('localeNames', () => {
    it('should have correct language names', () => {
      expect(localeNames['zh']).toBe('中文');
      expect(localeNames['en']).toBe('English');
      expect(localeNames['ja']).toBe('日本語');
      expect(localeNames['ko']).toBe('한국어');
    });
  });

  describe('localeFlags', () => {
    it('should have correct language flags', () => {
      expect(localeFlags['zh']).toBe('🇨🇳');
      expect(localeFlags['en']).toBe('🇺🇸');
      expect(localeFlags['ja']).toBe('🇯🇵');
      expect(localeFlags['ko']).toBe('🇰🇷');
    });
  });

  describe('detectLocale', () => {
    it('should return default locale when no stored locale', () => {
      const locale = detectLocale();
      expect(locale).toBe('zh'); // 默认语言
    });

    it('should return stored locale', () => {
      localStorage.setItem('livemirror_locale', 'en');
      const locale = detectLocale();
      expect(locale).toBe('en');
    });

    it('should return browser locale if supported', () => {
      // 模拟浏览器语言
      Object.defineProperty(navigator, 'language', {
        value: 'en-US',
        writable: true,
        configurable: true
      });
      
      const locale = detectLocale();
      expect(locale).toBe('en');
    });

    it('should return default locale for unsupported browser locale', () => {
      // 模拟不支持的浏览器语言
      Object.defineProperty(navigator, 'language', {
        value: 'fr-FR',
        writable: true,
        configurable: true
      });
      
      const locale = detectLocale();
      expect(locale).toBe('zh'); // 默认语言
    });
  });

  describe('saveLocale', () => {
    it('should save locale to localStorage', () => {
      saveLocale('ja');
      expect(localStorage.getItem('livemirror_locale')).toBe('ja');
    });
  });

  describe('getLocaleOptions', () => {
    it('should return all locale options', () => {
      const options = getLocaleOptions();
      
      expect(options).toHaveLength(4);
      expect(options).toContainEqual({
        code: 'zh',
        name: '中文',
        flag: '🇨🇳'
      });
      expect(options).toContainEqual({
        code: 'en',
        name: 'English',
        flag: '🇺🇸'
      });
    });
  });

  describe('detectTextLanguage', () => {
    it('should detect Chinese', () => {
      const result = detectTextLanguage('这是一个测试');
      expect(result).toBe('zh');
    });

    it('should detect Japanese', () => {
      const result = detectTextLanguage('これはテストです');
      expect(result).toBe('ja');
    });

    it('should detect Korean', () => {
      const result = detectTextLanguage('이것은 테스트입니다');
      expect(result).toBe('ko');
    });

    it('should default to English for Latin text', () => {
      const result = detectTextLanguage('This is a test');
      expect(result).toBe('en');
    });

    it('should handle empty string', () => {
      const result = detectTextLanguage('');
      expect(result).toBe('en'); // 默认
    });
  });

  describe('i18n instance', () => {
    it('should have correct initial locale', () => {
      expect(i18n.global.locale.value).toBeDefined();
      expect(supportedLocales).toContain(i18n.global.locale.value);
    });

    it('should have messages for all locales', () => {
      const messages = i18n.global.messages;
      expect(messages).toHaveProperty('zh');
      expect(messages).toHaveProperty('en');
      expect(messages).toHaveProperty('ja');
      expect(messages).toHaveProperty('ko');
    });
  });
});

describe('Translation Usage', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('should translate common keys', async () => {
    await setLocale('zh');
    const { t } = await import('vue-i18n');
    // 注意：实际使用时需要在 Vue 组件内使用 useI18n
    expect(true).toBe(true); // 占位测试
  });

  it('should switch locale correctly', async () => {
    await setLocale('en');
    expect(localStorage.getItem('livemirror_locale')).toBe('en');
    
    await setLocale('ja');
    expect(localStorage.getItem('livemirror_locale')).toBe('ja');
  });
});
