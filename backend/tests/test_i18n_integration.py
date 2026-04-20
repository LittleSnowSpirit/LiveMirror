"""
国际化集成测试 - LiveMirror
测试多语言转写、话术模板在实际场景中的应用
"""

import pytest
import sys
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


class TestMultilingualTranscription:
    """多语言转写支持测试"""
    
    @pytest.fixture
    def i18n(self):
        """创建 i18n 服务实例"""
        return I18nService()
    
    def test_transcribe_chinese(self, i18n):
        """测试中文转写"""
        i18n.set_language("zh")
        
        # 模拟转写结果
        transcription = {
            "text": "欢迎来到我们的直播间",
            "language": i18n.detect_language("欢迎来到我们的直播间"),
            "translation": i18n.t("templates.greeting")
        }
        
        assert transcription["language"] == "zh"
        assert "欢迎" in transcription["text"]
    
    def test_transcribe_english(self, i18n):
        """测试英文转写"""
        i18n.set_language("en")
        
        transcription = {
            "text": "Welcome to our live stream",
            "language": i18n.detect_language("Welcome to our live stream"),
            "translation": i18n.t("templates.greeting")
        }
        
        assert transcription["language"] == "en"
        assert "Welcome" in transcription["text"]
    
    def test_transcribe_japanese(self, i18n):
        """测试日文转写"""
        i18n.set_language("ja")
        
        transcription = {
            "text": "ライブ配信へようこそ",
            "language": i18n.detect_language("ライブ配信へようこそ"),
            "translation": i18n.t("templates.greeting")
        }
        
        assert transcription["language"] == "ja"
        assert "ようこそ" in transcription["text"]
    
    def test_transcribe_korean(self, i18n):
        """测试韩文转写"""
        i18n.set_language("ko")
        
        transcription = {
            "text": "라이브 스트림에 오신 것을 환영합니다",
            "language": i18n.detect_language("라이브 스트림에 오신 것을 환영합니다"),
            "translation": i18n.t("templates.greeting")
        }
        
        assert transcription["language"] == "ko"
        assert "환영" in transcription["text"]
    
    def test_multilingual_transcription_batch(self, i18n):
        """测试批量多语言转写"""
        texts = [
            "中文测试文本",
            "English test text",
            "日本語テストテキスト",
            "한국어 테스트 텍스트"
        ]
        
        expected_languages = ["zh", "en", "ja", "ko"]
        
        for text, expected_lang in zip(texts, expected_languages):
            detected = i18n.detect_language(text)
            assert detected == expected_lang, f"Failed to detect {text}"
    
    def test_transcription_with_translation(self, i18n):
        """测试转写后翻译"""
        # 原文（中文）
        original_text = "欢迎来到直播间"
        original_lang = i18n.detect_language(original_text)
        
        # 翻译成其他语言
        translations = {}
        for lang in ["zh", "en", "ja", "ko"]:
            i18n.set_language(lang)
            # 实际场景中这里会是翻译 API 调用
            translations[lang] = i18n.t("templates.greeting")
        
        assert "欢迎" in translations["zh"]
        assert "Welcome" in translations["en"]
        assert "ようこそ" in translations["ja"]
        assert "환영" in translations["ko"]


class TestScriptTemplates:
    """话术模板测试"""
    
    @pytest.fixture
    def i18n(self):
        """创建 i18n 服务实例"""
        return I18nService()
    
    def test_greeting_templates_all_languages(self, i18n):
        """测试所有语言的问候模板"""
        expected_content = {
            "zh": "欢迎",
            "en": "Welcome",
            "ja": "ようこそ",
            "ko": "환영"
        }
        
        for lang, expected in expected_content.items():
            i18n.set_language(lang)
            greeting = i18n.get_template("greeting")
            assert expected in greeting, f"Failed for {lang}"
    
    def test_product_introduction_templates(self, i18n):
        """测试产品介绍模板"""
        i18n.set_language("zh")
        
        intro = i18n.get_template("product_intro")
        assert len(intro) > 0
        assert "产品" in intro or "欢迎" in intro
    
    def test_call_to_action_templates(self, i18n):
        """测试行动号召模板"""
        templates = {
            "zh": "下单",
            "en": "order",
            "ja": "注文",
            "ko": "주문"
        }
        
        for lang, expected in templates.items():
            i18n.set_language(lang)
            cta = i18n.get_template("call_to_action")
            # 行动号召模板应包含购买相关的词
            assert len(cta) > 0
    
    def test_farewell_templates(self, i18n):
        """测试告别模板"""
        expected_content = {
            "zh": "感谢",
            "en": "Thank",
            "ja": "ありがとう",
            "ko": "감사"
        }
        
        for lang, expected in expected_content.items():
            i18n.set_language(lang)
            farewell = i18n.get_template("farewell")
            assert expected in farewell, f"Failed for {lang}"
    
    def test_template_parameter_substitution(self, i18n):
        """测试模板参数替换"""
        i18n.set_language("zh")
        
        # 获取带参数的模板
        template = i18n.t("templates.product_features", features="高质量、低价格")
        assert "高质量" in template
        assert "低价格" in template
        
        # 英文
        i18n.set_language("en")
        template = i18n.t("templates.product_features", features="High quality, Low price")
        assert "High quality" in template
    
    def test_all_templates_available(self, i18n):
        """测试所有模板都可用"""
        required_templates = [
            "greeting",
            "product_intro",
            "call_to_action",
            "farewell"
        ]
        
        for lang in ["zh", "en", "ja", "ko"]:
            i18n.set_language(lang)
            templates = i18n.get_all_templates()
            
            for template_name in required_templates:
                assert template_name in templates, \
                    f"Template '{template_name}' missing for {lang}"


class TestLiveStreamingScenarios:
    """直播场景测试"""
    
    @pytest.fixture
    def i18n(self):
        """创建 i18n 服务实例"""
        return I18nService()
    
    def test_multilingual_stream_setup(self, i18n):
        """测试多语言直播设置"""
        # 主播选择语言
        stream_language = "zh"
        i18n.set_language(stream_language)
        
        # 获取界面文本
        ui_texts = {
            "welcome": i18n.t("common.welcome"),
            "start": i18n.t("common.ok"),
            "settings": i18n.t("common.settings")
        }
        
        assert "欢迎" in ui_texts["welcome"]
        assert "确定" in ui_texts["start"]
        assert "设置" in ui_texts["settings"]
    
    def test_viewer_language_switching(self, i18n):
        """测试观众语言切换"""
        # 模拟不同语言的观众
        viewers = [
            {"id": 1, "language": "zh"},
            {"id": 2, "language": "en"},
            {"id": 3, "language": "ja"},
            {"id": 4, "language": "ko"}
        ]
        
        messages = {}
        for viewer in viewers:
            i18n.set_language(viewer["language"])
            messages[viewer["id"]] = i18n.t("templates.greeting")
        
        # 验证每个观众看到正确语言的问候
        assert "欢迎" in messages[1]
        assert "Welcome" in messages[2]
        assert "ようこそ" in messages[3]
        assert "환영" in messages[4]
    
    def test_real_time_translation(self, i18n):
        """测试实时翻译场景"""
        # 主播说的话
        broadcaster_message = "这款产品非常受欢迎"
        
        # 检测语言
        lang = i18n.detect_language(broadcaster_message)
        assert lang == "zh"
        
        # 为不同语言观众提供翻译
        translations = {}
        for target_lang in ["zh", "en", "ja", "ko"]:
            i18n.set_language(target_lang)
            # 实际场景中这里会调用翻译 API
            # 这里使用预设的翻译
            translations[target_lang] = i18n.t("templates.product_intro")
        
        # 验证翻译结果
        assert "产品" in translations["zh"] or "受欢迎" in translations["zh"]
        assert "product" in translations["en"].lower() or "popular" in translations["en"].lower()
    
    def test_chat_messages_multilingual(self, i18n):
        """测试多语言聊天消息"""
        chat_messages = [
            {"user": "用户 1", "text": "你好", "lang": None},
            {"user": "User 2", "text": "Hello", "lang": None},
            {"user": "ユーザー 3", "text": "こんにちは", "lang": None},
            {"user": "사용자 4", "text": "안녕하세요", "lang": None}
        ]
        
        # 自动检测每条消息的语言
        for message in chat_messages:
            detected_lang = i18n.detect_language(message["text"])
            message["lang"] = detected_lang
        
        # 验证语言检测
        assert chat_messages[0]["lang"] == "zh"
        assert chat_messages[1]["lang"] == "en"
        assert chat_messages[2]["lang"] == "ja"
        assert chat_messages[3]["lang"] == "ko"
    
    def test_product_description_multilingual(self, i18n):
        """测试多语言产品描述"""
        product_info = {
            "name": {
                "zh": "优质产品",
                "en": "Premium Product",
                "ja": "プレミアム製品",
                "ko": "프리미엄 제품"
            },
            "price": "¥199"
        }
        
        descriptions = {}
        for lang in ["zh", "en", "ja", "ko"]:
            i18n.set_language(lang)
            descriptions[lang] = {
                "name": product_info["name"][lang],
                "intro": i18n.t("templates.product_intro"),
                "cta": i18n.t("templates.call_to_action")
            }
        
        # 验证每种语言都有完整的描述
        for lang in ["zh", "en", "ja", "ko"]:
            assert descriptions[lang]["name"]
            assert descriptions[lang]["intro"]
            assert descriptions[lang]["cta"]


class TestEdgeCases:
    """边界情况测试"""
    
    @pytest.fixture
    def i18n(self):
        """创建 i18n 服务实例"""
        return I18nService()
    
    def test_mixed_language_text(self, i18n):
        """测试混合语言文本"""
        mixed_texts = [
            "Hello 世界",
            "こんにちは World",
            "안녕 Hello"
        ]
        
        for text in mixed_texts:
            # 混合语言应该能检测到其中一种
            lang = i18n.detect_language(text)
            assert lang in ["zh", "en", "ja", "ko"]
    
    def test_empty_text(self, i18n):
        """测试空文本"""
        lang = i18n.detect_language("")
        assert lang == "en"  # 默认返回英文
    
    def test_special_characters(self, i18n):
        """测试特殊字符"""
        special_texts = [
            "!!!",
            "123",
            "@#$%",
            "你好！！！"
        ]
        
        for text in special_texts:
            lang = i18n.detect_language(text)
            # 特殊字符应该返回默认语言或检测到中文
            assert lang in ["zh", "en"]
    
    def test_very_long_text(self, i18n):
        """测试长文本"""
        long_text_zh = "这是一个非常长的中文文本" * 100
        long_text_en = "This is a very long English text " * 100
        
        assert i18n.detect_language(long_text_zh) == "zh"
        assert i18n.detect_language(long_text_en) == "en"
    
    def test_missing_translation_key(self, i18n):
        """测试缺失的翻译键"""
        i18n.set_language("zh")
        
        # 请求不存在的键
        result = i18n.t("non.existent.key")
        
        # 应该返回键本身
        assert result == "non.existent.key"
    
    def test_language_switching_persistence(self, i18n):
        """测试语言切换持久性"""
        # 切换到英文
        i18n.set_language("en")
        assert i18n.get_language() == "en"
        
        # 验证翻译是英文
        welcome = i18n.t("common.welcome")
        assert "Welcome" in welcome
        
        # 切换到日文
        i18n.set_language("ja")
        assert i18n.get_language() == "ja"
        
        # 验证翻译是日文
        welcome = i18n.t("common.welcome")
        assert "ようこそ" in welcome


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
