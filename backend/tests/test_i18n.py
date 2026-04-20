"""
国际化服务测试 - LiveMirror
测试多语言支持、语言检测、话术模板等功能
"""

import pytest
import sys
import os
from pathlib import Path

# 添加 backend 到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from services.i18n import (
    I18nService,
    LanguageDetector,
    SupportedLanguage,
    get_i18n,
    t,
    detect_language,
)


class TestLanguageDetector:
    """语言检测器测试"""
    
    def test_detect_chinese(self):
        """检测中文"""
        text = "这是一个测试文本"
        result = LanguageDetector.detect(text)
        assert result == SupportedLanguage.ZH
    
    def test_detect_english(self):
        """检测英文"""
        text = "This is a test text"
        result = LanguageDetector.detect(text)
        assert result == SupportedLanguage.EN
    
    def test_detect_japanese(self):
        """检测日文"""
        text = "これはテストテキストです"
        result = LanguageDetector.detect(text)
        assert result == SupportedLanguage.JA
    
    def test_detect_korean(self):
        """检测韩文"""
        text = "이것은 테스트 텍스트입니다"
        result = LanguageDetector.detect(text)
        assert result == SupportedLanguage.KO
    
    def test_detect_mixed_text(self):
        """检测混合文本（以主要语言为准）"""
        text = "Hello 世界"
        result = LanguageDetector.detect(text)
        # 混合文本可能检测为中文或英文，取决于字符数
        assert result in [SupportedLanguage.ZH, SupportedLanguage.EN]
    
    def test_detect_empty_text(self):
        """检测空文本（返回默认语言）"""
        text = ""
        result = LanguageDetector.detect(text)
        assert result == SupportedLanguage.EN
    
    def test_detect_batch(self):
        """批量检测"""
        texts = [
            "中文测试",
            "English test",
            "日本語テスト",
            "한국어 테스트"
        ]
        results = LanguageDetector.detect_batch(texts)
        
        assert results["中文测试"] == SupportedLanguage.ZH
        assert results["English test"] == SupportedLanguage.EN
        assert results["日本語テスト"] == SupportedLanguage.JA
        assert results["한국어 테스트"] == SupportedLanguage.KO


class TestI18nService:
    """国际化服务测试"""
    
    @pytest.fixture
    def i18n(self):
        """创建 i18n 服务实例"""
        return I18nService()
    
    def test_init(self, i18n):
        """测试初始化"""
        assert i18n.current_language == SupportedLanguage.ZH
        assert len(i18n.translations) > 0
    
    def test_set_language(self, i18n):
        """测试设置语言"""
        i18n.set_language("en")
        assert i18n.current_language == SupportedLanguage.EN
        
        i18n.set_language("ja")
        assert i18n.current_language == SupportedLanguage.JA
        
        i18n.set_language("ko")
        assert i18n.current_language == SupportedLanguage.KO
    
    def test_set_unsupported_language(self, i18n):
        """测试设置不支持的语言（应回退到默认）"""
        i18n.set_language("fr")
        assert i18n.current_language == SupportedLanguage.EN
    
    def test_translate_common_keys(self, i18n):
        """测试常见键的翻译"""
        # 中文
        i18n.set_language("zh")
        assert i18n.t("common.welcome") == "欢迎使用 LiveMirror"
        assert i18n.t("common.loading") == "加载中..."
        
        # 英文
        i18n.set_language("en")
        assert i18n.t("common.welcome") == "Welcome to LiveMirror"
        assert i18n.t("common.loading") == "Loading..."
        
        # 日文
        i18n.set_language("ja")
        assert i18n.t("common.welcome") == "LiveMirror へようこそ"
        assert i18n.t("common.loading") == "読み込み中..."
        
        # 韩文
        i18n.set_language("ko")
        assert i18n.t("common.welcome") == "LiveMirror 에 오신 것을 환영합니다"
        assert i18n.t("common.loading") == "로딩 중..."
    
    def test_translate_with_params(self, i18n):
        """测试带参数的翻译"""
        i18n.set_language("zh")
        result = i18n.t("time.minute_ago", n=5)
        assert result == "5 分钟前"
        
        i18n.set_language("en")
        result = i18n.t("time.minute_ago", n=5)
        assert result == "5 minutes ago"
    
    def test_translate_fallback(self, i18n):
        """测试回退机制"""
        # 设置一个不存在的键
        i18n.set_language("zh")
        result = i18n.t("non.existent.key")
        # 应该返回键本身
        assert result == "non.existent.key"
    
    def test_get_template(self, i18n):
        """测试获取话术模板"""
        i18n.set_language("zh")
        greeting = i18n.get_template("greeting")
        assert "欢迎" in greeting
        
        i18n.set_language("en")
        greeting = i18n.get_template("greeting")
        assert "Welcome" in greeting
    
    def test_get_all_templates(self, i18n):
        """测试获取所有模板"""
        i18n.set_language("zh")
        templates = i18n.get_all_templates()
        
        assert "greeting" in templates
        assert "product_intro" in templates
        assert "call_to_action" in templates
        assert "farewell" in templates
    
    def test_get_supported_languages(self, i18n):
        """测试获取支持的语言列表"""
        languages = i18n.get_supported_languages()
        
        assert len(languages) == 4
        assert {"code": "zh", "name": "中文"} in languages
        assert {"code": "en", "name": "English"} in languages
        assert {"code": "ja", "name": "日本語"} in languages
        assert {"code": "ko", "name": "한국어"} in languages
    
    def test_detect_language_method(self, i18n):
        """测试语言检测方法"""
        assert i18n.detect_language("中文测试") == "zh"
        assert i18n.detect_language("English test") == "en"
        assert i18n.detect_language("日本語テスト") == "ja"
        assert i18n.detect_language("한국어 테스트") == "ko"
    
    def test_add_translation(self, i18n, tmp_path):
        """测试添加翻译"""
        # 创建临时目录
        i18n.locales_dir = tmp_path
        i18n._load_all_locales()
        
        # 添加新翻译
        i18n.add_translation("zh", "test.new_key", "测试值")
        
        # 验证翻译
        result = i18n.t("test.new_key", "zh")
        assert result == "测试值"
    
    def test_get_all_translations(self, i18n):
        """测试获取所有翻译"""
        i18n.set_language("zh")
        translations = i18n.get_all_translations()
        
        assert "common" in translations
        assert "features" in translations
        assert "templates" in translations


class TestGlobalFunctions:
    """全局函数测试"""
    
    def test_get_i18n_singleton(self):
        """测试单例模式"""
        i18n_1 = get_i18n()
        i18n_2 = get_i18n()
        assert i18n_1 is i18n_2
    
    def test_t_function(self):
        """测试快捷翻译函数"""
        result = t("common.welcome", "zh")
        assert "欢迎" in result
        
        result = t("common.welcome", "en")
        assert "Welcome" in result
    
    def test_detect_language_function(self):
        """测试快捷语言检测函数"""
        assert detect_language("中文") == "zh"
        assert detect_language("English") == "en"


class TestLanguageTemplates:
    """话术模板测试"""
    
    @pytest.fixture
    def i18n(self):
        """创建 i18n 服务实例"""
        return I18nService()
    
    def test_greeting_templates(self, i18n):
        """测试问候模板"""
        templates = {
            "zh": "欢迎",
            "en": "Welcome",
            "ja": "ようこそ",
            "ko": "환영"
        }
        
        for lang, expected in templates.items():
            i18n.set_language(lang)
            greeting = i18n.get_template("greeting")
            assert expected in greeting
    
    def test_product_templates(self, i18n):
        """测试产品模板"""
        i18n.set_language("zh")
        
        # 测试产品介绍
        intro = i18n.get_template("product_intro")
        assert "产品" in intro or "欢迎" in intro
        
        # 测试行动号召
        cta = i18n.get_template("call_to_action")
        assert len(cta) > 0
    
    def test_template_with_params(self, i18n):
        """测试带参数的模板"""
        i18n.set_language("zh")
        
        # 获取模板并手动替换参数
        template = i18n.get_template("product_features")
        result = template.replace("{features}", "高质量、低价格")
        
        assert "高质量" in result
        assert "低价格" in result


class TestLanguageConsistency:
    """语言一致性测试"""
    
    @pytest.fixture
    def i18n(self):
        """创建 i18n 服务实例"""
        return I18nService()
    
    def test_all_languages_have_same_keys(self, i18n):
        """测试所有语言有相同的键"""
        languages = ["zh", "en", "ja", "ko"]
        
        # 获取所有语言的键
        all_keys = {}
        for lang in languages:
            translations = i18n.get_all_translations(lang)
            keys = self._flatten_keys(translations)
            all_keys[lang] = set(keys)
        
        # 检查键是否一致
        zh_keys = all_keys["zh"]
        for lang in languages[1:]:
            missing = zh_keys - all_keys[lang]
            extra = all_keys[lang] - zh_keys
            
            # 允许少量差异，但主要键应该一致
            assert len(missing) < 10, f"{lang} 缺少键：{missing}"
            assert len(extra) < 10, f"{lang} 多余键：{extra}"
    
    def _flatten_keys(self, d: dict, prefix: str = "") -> list:
        """扁平化字典键"""
        keys = []
        for k, v in d.items():
            full_key = f"{prefix}.{k}" if prefix else k
            if isinstance(v, dict):
                keys.extend(self._flatten_keys(v, full_key))
            else:
                keys.append(full_key)
        return keys


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
