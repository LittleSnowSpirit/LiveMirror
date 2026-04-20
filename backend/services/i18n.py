"""
国际化服务 (i18n) - LiveMirror
支持多语言翻译、自动语言检测、语言切换、话术模板
支持语言：中文 (zh)、英文 (en)、日文 (ja)、韩文 (ko)
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum
from datetime import datetime


class SupportedLanguage(Enum):
    """支持的语言"""
    ZH = "zh"  # 中文
    EN = "en"  # 英文
    JA = "ja"  # 日文
    KO = "ko"  # 韩文


class LanguageDetector:
    """自动语言检测器"""
    
    # 语言特征字符范围
    LANGUAGE_RANGES = {
        SupportedLanguage.ZH: [
            (0x4E00, 0x9FFF),   # CJK 统一表意文字
            (0x3400, 0x4DBF),   # CJK 扩展 A
        ],
        SupportedLanguage.JA: [
            (0x3040, 0x309F),   # 平假名
            (0x30A0, 0x30FF),   # 片假名
            (0x4E00, 0x9FFF),   # 汉字
        ],
        SupportedLanguage.KO: [
            (0xAC00, 0xD7AF),   # 韩文音节
            (0x1100, 0x11FF),   # 韩文字母
        ],
    }
    
    # 常见语言词汇特征
    LANGUAGE_PATTERNS = {
        SupportedLanguage.ZH: [
            r'的', r'了', r'是', r'在', r'我', r'有', r'和', r'就', r'不', r'人'
        ],
        SupportedLanguage.JA: [
            r'は', r'が', r'の', r'に', r'を', r'で', r'ます', r'です', r'た', r'る'
        ],
        SupportedLanguage.KO: [
            r'은', r'는', r'이', r'가', r'을', r'를', r'에', r'서', r'요', r'다'
        ],
    }
    
    @classmethod
    def detect(cls, text: str) -> SupportedLanguage:
        """
        检测文本的语言
        
        Args:
            text: 要检测的文本
            
        Returns:
            检测到的语言
        """
        if not text or len(text.strip()) == 0:
            return SupportedLanguage.EN
        
        char_scores = {lang: 0 for lang in SupportedLanguage}
        pattern_scores = {lang: 0 for lang in SupportedLanguage}
        
        # 字符范围评分
        for char in text:
            code_point = ord(char)
            for lang, ranges in cls.LANGUAGE_RANGES.items():
                for start, end in ranges:
                    if start <= code_point <= end:
                        char_scores[lang] += 1
                        break
        
        # 模式匹配评分
        for lang, patterns in cls.LANGUAGE_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    pattern_scores[lang] += 1
        
        # 计算总分
        total_scores = {
            lang: char_scores[lang] * 2 + pattern_scores[lang] * 3
            for lang in SupportedLanguage
        }
        
        # 返回得分最高的语言，如果都为 0 则返回英文
        max_score = max(total_scores.values())
        if max_score == 0:
            return SupportedLanguage.EN
        
        for lang, score in total_scores.items():
            if score == max_score:
                return lang
        
        return SupportedLanguage.EN
    
    @classmethod
    def detect_batch(cls, texts: List[str]) -> Dict[str, SupportedLanguage]:
        """
        批量检测语言
        
        Args:
            texts: 文本列表
            
        Returns:
            文本到语言的映射
        """
        return {text: cls.detect(text) for text in texts}


class I18nService:
    """国际化服务"""
    
    def __init__(self, locales_dir: Optional[str] = None):
        """
        初始化国际化服务
        
        Args:
            locales_dir: 语言包目录路径
        """
        if locales_dir is None:
            locales_dir = str(Path(__file__).parent.parent / "locales")
        
        self.locales_dir = Path(locales_dir)
        self.translations: Dict[str, Dict[str, Any]] = {}
        self.current_language = SupportedLanguage.ZH
        self.fallback_language = SupportedLanguage.EN
        self._load_all_locales()
    
    def _load_all_locales(self) -> None:
        """加载所有语言包"""
        if not self.locales_dir.exists():
            self.locales_dir.mkdir(parents=True, exist_ok=True)
            self._create_default_locales()
        
        for lang in SupportedLanguage:
            self._load_locale(lang.value)
    
    def _create_default_locales(self) -> None:
        """创建默认语言包"""
        default_locales = {
            "zh": {
                "common": {
                    "welcome": "欢迎使用 LiveMirror",
                    "loading": "加载中...",
                    "error": "错误",
                    "success": "成功",
                    "cancel": "取消",
                    "confirm": "确认",
                    "save": "保存",
                    "delete": "删除",
                    "edit": "编辑",
                    "search": "搜索",
                    "settings": "设置",
                    "language": "语言",
                    "close": "关闭",
                    "open": "打开",
                    "yes": "是",
                    "no": "否",
                    "ok": "确定"
                },
                "features": {
                    "ab_testing": "A/B 测试",
                    "competitor_monitor": "竞品监控",
                    "prediction": "销售预测",
                    "report_generator": "报告生成",
                    "roi_analysis": "ROI 分析",
                    "sensitive_words": "敏感词检测",
                    "title_optimizer": "标题优化"
                },
                "messages": {
                    "no_data": "暂无数据",
                    "load_failed": "加载失败",
                    "save_success": "保存成功",
                    "delete_confirm": "确定要删除吗？",
                    "operation_failed": "操作失败",
                    "network_error": "网络错误",
                    "please_try_again": "请重试"
                },
                "templates": {
                    "greeting": "您好！欢迎来到我们的直播间",
                    "product_intro": "这款产品非常受欢迎，今天有特别优惠",
                    "call_to_action": "喜欢的宝宝们赶紧下单吧",
                    "farewell": "感谢大家的观看，我们下次再见"
                }
            },
            "en": {
                "common": {
                    "welcome": "Welcome to LiveMirror",
                    "loading": "Loading...",
                    "error": "Error",
                    "success": "Success",
                    "cancel": "Cancel",
                    "confirm": "Confirm",
                    "save": "Save",
                    "delete": "Delete",
                    "edit": "Edit",
                    "search": "Search",
                    "settings": "Settings",
                    "language": "Language",
                    "close": "Close",
                    "open": "Open",
                    "yes": "Yes",
                    "no": "No",
                    "ok": "OK"
                },
                "features": {
                    "ab_testing": "A/B Testing",
                    "competitor_monitor": "Competitor Monitor",
                    "prediction": "Sales Prediction",
                    "report_generator": "Report Generator",
                    "roi_analysis": "ROI Analysis",
                    "sensitive_words": "Sensitive Words",
                    "title_optimizer": "Title Optimizer"
                },
                "messages": {
                    "no_data": "No data available",
                    "load_failed": "Failed to load",
                    "save_success": "Saved successfully",
                    "delete_confirm": "Are you sure you want to delete?",
                    "operation_failed": "Operation failed",
                    "network_error": "Network error",
                    "please_try_again": "Please try again"
                },
                "templates": {
                    "greeting": "Hello! Welcome to our live stream",
                    "product_intro": "This product is very popular, special offer today",
                    "call_to_action": "If you like it, please order now",
                    "farewell": "Thank you for watching, see you next time"
                }
            },
            "ja": {
                "common": {
                    "welcome": "LiveMirror へようこそ",
                    "loading": "読み込み中...",
                    "error": "エラー",
                    "success": "成功",
                    "cancel": "キャンセル",
                    "confirm": "確認",
                    "save": "保存",
                    "delete": "削除",
                    "edit": "編集",
                    "search": "検索",
                    "settings": "設定",
                    "language": "言語",
                    "close": "閉じる",
                    "open": "開く",
                    "yes": "はい",
                    "no": "いいえ",
                    "ok": "OK"
                },
                "features": {
                    "ab_testing": "A/B テスト",
                    "competitor_monitor": "競合他社監視",
                    "prediction": "販売予測",
                    "report_generator": "レポート生成",
                    "roi_analysis": "ROI 分析",
                    "sensitive_words": "敏感ワード検出",
                    "title_optimizer": "タイトル最適化"
                },
                "messages": {
                    "no_data": "データがありません",
                    "load_failed": "読み込みに失敗しました",
                    "save_success": "保存しました",
                    "delete_confirm": "削除してもよろしいですか？",
                    "operation_failed": "操作に失敗しました",
                    "network_error": "ネットワークエラー",
                    "please_try_again": "もう一度お試しください"
                },
                "templates": {
                    "greeting": "こんにちは！私たちのライブ配信へようこそ",
                    "product_intro": "この商品はとても人気があります、本日特別価格です",
                    "call_to_action": "気に入ったら、今すぐご注文ください",
                    "farewell": "ご視聴ありがとうございました、また次回お会いしましょう"
                }
            },
            "ko": {
                "common": {
                    "welcome": "LiveMirror 에 오신 것을 환영합니다",
                    "loading": "로딩 중...",
                    "error": "오류",
                    "success": "성공",
                    "cancel": "취소",
                    "confirm": "확인",
                    "save": "저장",
                    "delete": "삭제",
                    "edit": "편집",
                    "search": "검색",
                    "settings": "설정",
                    "language": "언어",
                    "close": "닫기",
                    "open": "열기",
                    "yes": "예",
                    "no": "아니오",
                    "ok": "확인"
                },
                "features": {
                    "ab_testing": "A/B 테스트",
                    "competitor_monitor": "경쟁사 모니터링",
                    "prediction": "판매 예측",
                    "report_generator": "보고서 생성",
                    "roi_analysis": "ROI 분석",
                    "sensitive_words": "민감한 단어 감지",
                    "title_optimizer": "제목 최적화"
                },
                "messages": {
                    "no_data": "데이터가 없습니다",
                    "load_failed": "로딩 실패",
                    "save_success": "저장되었습니다",
                    "delete_confirm": "삭제하시겠습니까?",
                    "operation_failed": "작업 실패",
                    "network_error": "네트워크 오류",
                    "please_try_again": "다시 시도해 주세요"
                },
                "templates": {
                    "greeting": "안녕하세요! 저희 라이브 스트림에 오신 것을 환영합니다",
                    "product_intro": "이 제품은 매우 인기가 많습니다, 오늘 특별 할인입니다",
                    "call_to_action": "좋아하시면 지금 바로 주문해 주세요",
                    "farewell": "시청해 주셔서 감사합니다, 다음에 또 만나요"
                }
            }
        }
        
        for lang_code, content in default_locales.items():
            locale_file = self.locales_dir / f"{lang_code}.json"
            with open(locale_file, "w", encoding="utf-8") as f:
                json.dump(content, f, ensure_ascii=False, indent=2)
    
    def _load_locale(self, lang: str) -> None:
        """
        加载指定语言包
        
        Args:
            lang: 语言代码
        """
        locale_file = self.locales_dir / f"{lang}.json"
        
        if locale_file.exists():
            try:
                with open(locale_file, "r", encoding="utf-8") as f:
                    self.translations[lang] = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Warning: Failed to load locale {lang}: {e}")
                self.translations[lang] = {}
        else:
            self.translations[lang] = {}
    
    def reload_locale(self, lang: str) -> None:
        """
        重新加载语言包
        
        Args:
            lang: 语言代码
        """
        self._load_locale(lang)
    
    def set_language(self, lang: str) -> None:
        """
        设置当前语言
        
        Args:
            lang: 语言代码
        """
        try:
            self.current_language = SupportedLanguage(lang)
        except ValueError:
            print(f"Warning: Unsupported language '{lang}', using fallback")
            self.current_language = self.fallback_language
    
    def get_language(self) -> str:
        """获取当前语言代码"""
        return self.current_language.value
    
    def t(self, key: str, lang: Optional[str] = None, **kwargs) -> str:
        """
        翻译文本
        
        Args:
            key: 翻译键（使用点号分隔，如 "common.welcome"）
            lang: 目标语言（可选，默认使用当前语言）
            **kwargs: 替换参数
            
        Returns:
            翻译后的文本
        """
        target_lang = lang or self.current_language.value
        keys = key.split(".")
        
        # 尝试目标语言
        value = self._get_nested_value(self.translations.get(target_lang, {}), keys)
        
        # 如果未找到，尝试回退语言
        if value is None and target_lang != self.fallback_language.value:
            value = self._get_nested_value(
                self.translations.get(self.fallback_language.value, {}), keys
            )
        
        # 如果仍未找到，返回原始键
        if value is None:
            return key
        
        # 替换参数
        if kwargs:
            for k, v in kwargs.items():
                value = value.replace(f"{{{k}}}", str(v))
        
        return value
    
    def _get_nested_value(self, data: Dict, keys: List[str]) -> Optional[Any]:
        """获取嵌套字典的值"""
        current = data
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current
    
    def get_all_translations(self, lang: Optional[str] = None) -> Dict[str, Any]:
        """
        获取所有翻译
        
        Args:
            lang: 语言代码（可选，默认使用当前语言）
            
        Returns:
            翻译字典
        """
        target_lang = lang or self.current_language.value
        return self.translations.get(target_lang, {})
    
    def detect_language(self, text: str) -> str:
        """
        检测文本语言
        
        Args:
            text: 要检测的文本
            
        Returns:
            检测到的语言代码
        """
        return LanguageDetector.detect(text).value
    
    def get_template(self, template_name: str, lang: Optional[str] = None) -> str:
        """
        获取话术模板
        
        Args:
            template_name: 模板名称
            lang: 语言代码（可选）
            
        Returns:
            模板内容
        """
        return self.t(f"templates.{template_name}", lang)
    
    def get_all_templates(self, lang: Optional[str] = None) -> Dict[str, str]:
        """
        获取所有话术模板
        
        Args:
            lang: 语言代码（可选）
            
        Returns:
            模板字典
        """
        target_lang = lang or self.current_language.value
        templates = self._get_nested_value(
            self.translations.get(target_lang, {}), ["templates"]
        )
        return templates or {}
    
    def add_translation(self, lang: str, key: str, value: str) -> None:
        """
        添加或更新翻译
        
        Args:
            lang: 语言代码
            key: 翻译键
            value: 翻译值
        """
        if lang not in self.translations:
            self.translations[lang] = {}
        
        keys = key.split(".")
        current = self.translations[lang]
        
        for i, k in enumerate(keys[:-1]):
            if k not in current:
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
        
        # 保存到文件
        self._save_locale(lang)
    
    def _save_locale(self, lang: str) -> None:
        """保存语言包到文件"""
        locale_file = self.locales_dir / f"{lang}.json"
        
        if lang in self.translations:
            with open(locale_file, "w", encoding="utf-8") as f:
                json.dump(self.translations[lang], f, ensure_ascii=False, indent=2)
    
    def get_supported_languages(self) -> List[Dict[str, str]]:
        """
        获取支持的语言列表
        
        Returns:
            语言信息列表
        """
        return [
            {"code": lang.value, "name": self._get_language_name(lang)}
            for lang in SupportedLanguage
        ]
    
    def _get_language_name(self, lang: SupportedLanguage) -> str:
        """获取语言名称"""
        names = {
            SupportedLanguage.ZH: "中文",
            SupportedLanguage.EN: "English",
            SupportedLanguage.JA: "日本語",
            SupportedLanguage.KO: "한국어"
        }
        return names.get(lang, lang.value)


# 全局实例
_i18n_instance: Optional[I18nService] = None


def get_i18n() -> I18nService:
    """获取全局 i18n 实例"""
    global _i18n_instance
    if _i18n_instance is None:
        _i18n_instance = I18nService()
    return _i18n_instance


def t(key: str, lang: Optional[str] = None, **kwargs) -> str:
    """快捷翻译函数"""
    return get_i18n().t(key, lang, **kwargs)


def detect_language(text: str) -> str:
    """快捷语言检测函数"""
    return get_i18n().detect_language(text)


# Flask/Django 中间件支持
class I18nMiddleware:
    """i18n 中间件基类"""
    
    def __init__(self, i18n_service: Optional[I18nService] = None):
        self.i18n = i18n_service or get_i18n()
    
    def get_language_from_request(self, request) -> str:
        """
        从请求中获取语言
        
        优先级：
        1. URL 参数 (?lang=zh)
        2. Cookie/Bearer
        3. Accept-Language header
        4. 默认语言
        """
        # 检查 URL 参数
        lang = getattr(request, 'args', {}).get('lang')
        if lang:
            return lang
        
        # 检查 Cookie
        cookies = getattr(request, 'cookies', {})
        if cookies:
            lang = cookies.get('language') or cookies.get('lang')
            if lang:
                return lang
        
        # 检查 Accept-Language header
        accept_lang = getattr(request, 'headers', {}).get('Accept-Language', '')
        if accept_lang:
            # 解析 Accept-Language header
            primary_lang = accept_lang.split(',')[0].split('-')[0]
            return primary_lang
        
        # 返回默认语言
        return self.i18n.get_language()


# Flask 特定中间件
try:
    from flask import request, g
    
    class FlaskI18nMiddleware(I18nMiddleware):
        """Flask i18n 中间件"""
        
        def before_request(self):
            lang = self.get_language_from_request(request)
            self.i18n.set_language(lang)
            g.language = lang
            g.i18n = self.i18n
        
        def after_request(self, response):
            # 设置语言 Cookie
            lang = getattr(g, 'language', self.i18n.get_language())
            response.set_cookie('language', lang, max_age=365*24*60*60)
            return response
    
except ImportError:
    FlaskI18nMiddleware = None  # type: ignore


# 导出
__all__ = [
    'I18nService',
    'LanguageDetector',
    'SupportedLanguage',
    'I18nMiddleware',
    'FlaskI18nMiddleware',
    'get_i18n',
    't',
    'detect_language',
]
