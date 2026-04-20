"""
敏感词检测服务 - LiveMirror
支持词库管理、实时检测、分级预警、替换建议、使用统计
"""

import json
import re
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from enum import Enum
from pathlib import Path


class SeverityLevel(Enum):
    """敏感词分级"""
    WARNING = "warning"      # 警告级别 - 轻微敏感
    SERIOUS = "serious"      # 严重级别 - 中度敏感
    BANNED = "banned"        # 封禁级别 - 高度敏感


class SensitiveWordCategory(Enum):
    """敏感词分类"""
    GENERAL = "general"          # 通用敏感词
    BEAUTY = "beauty"            # 美妆行业
    FOOD = "food"                # 食品行业
    CLOTHING = "clothing"        # 服装行业
    FINANCE = "finance"          # 金融
    HEALTH = "health"            # 医疗健康
    POLITICS = "politics"        # 政治相关
    ADVERTISING = "advertising"  # 广告违禁词


class SensitiveWordEntry:
    """敏感词条目"""
    def __init__(
        self,
        word: str,
        severity: SeverityLevel,
        category: SensitiveWordCategory = SensitiveWordCategory.GENERAL,
        replacement: Optional[str] = None,
        reason: str = "",
        created_at: Optional[datetime] = None
    ):
        self.word = word
        self.severity = severity
        self.category = category
        self.replacement = replacement
        self.reason = reason
        self.created_at = created_at or datetime.now()
        self.hit_count = 0
    
    def to_dict(self) -> Dict:
        return {
            "word": self.word,
            "severity": self.severity.value,
            "category": self.category.value,
            "replacement": self.replacement,
            "reason": self.reason,
            "created_at": self.created_at.isoformat(),
            "hit_count": self.hit_count
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "SensitiveWordEntry":
        entry = cls(
            word=data["word"],
            severity=SeverityLevel(data["severity"]),
            category=SensitiveWordCategory(data.get("category", "general")),
            replacement=data.get("replacement"),
            reason=data.get("reason", ""),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else None
        )
        entry.hit_count = data.get("hit_count", 0)
        return entry


class SensitiveWordService:
    """敏感词检测服务"""
    
    def __init__(self, data_dir: str = "data/sensitive_words"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 词库文件路径
        self.word_library_path = self.data_dir / "word_library.json"
        self.stats_path = self.data_dir / "usage_stats.json"
        self.industry_packages_path = self.data_dir / "industry_packages.json"
        
        # 内存中的词库
        self.word_library: Dict[str, SensitiveWordEntry] = {}
        self.usage_stats: Dict = {
            "total_checks": 0,
            "total_hits": 0,
            "hits_by_level": {
                "warning": 0,
                "serious": 0,
                "banned": 0
            },
            "hits_by_category": {},
            "daily_stats": {}
        }
        self.industry_packages: Dict[str, List[Dict]] = {}
        
        # 加载数据
        self._load_library()
        self._load_stats()
        self._load_industry_packages()
        
        # 如果没有初始词库，加载默认词库
        if not self.word_library:
            self._init_default_library()
    
    def _load_library(self):
        """加载词库"""
        if self.word_library_path.exists():
            with open(self.word_library_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.word_library = {
                    k: SensitiveWordEntry.from_dict(v) for k, v in data.items()
                }
    
    def _save_library(self):
        """保存词库"""
        with open(self.word_library_path, "w", encoding="utf-8") as f:
            json.dump(
                {k: v.to_dict() for k, v in self.word_library.items()},
                f,
                ensure_ascii=False,
                indent=2
            )
    
    def _load_stats(self):
        """加载使用统计"""
        if self.stats_path.exists():
            with open(self.stats_path, "r", encoding="utf-8") as f:
                self.usage_stats = json.load(f)
    
    def _save_stats(self):
        """保存使用统计"""
        with open(self.stats_path, "w", encoding="utf-8") as f:
            json.dump(self.usage_stats, f, ensure_ascii=False, indent=2)
    
    def _load_industry_packages(self):
        """加载行业词包"""
        if self.industry_packages_path.exists():
            with open(self.industry_packages_path, "r", encoding="utf-8") as f:
                self.industry_packages = json.load(f)
    
    def _save_industry_packages(self):
        """保存行业词包"""
        with open(self.industry_packages_path, "w", encoding="utf-8") as f:
            json.dump(self.industry_packages, f, ensure_ascii=False, indent=2)
    
    def _init_default_library(self):
        """初始化默认敏感词库"""
        default_words = [
            # 警告级别 - 广告违禁词
            ("最", SeverityLevel.WARNING, SensitiveWordCategory.ADVERTISING, "极", "广告法禁止使用绝对化用语"),
            ("第一", SeverityLevel.WARNING, SensitiveWordCategory.ADVERTISING, "领先", "广告法禁止使用绝对化用语"),
            ("顶级", SeverityLevel.WARNING, SensitiveWordCategory.ADVERTISING, "优质", "广告法禁止使用绝对化用语"),
            ("国家级", SeverityLevel.WARNING, SensitiveWordCategory.ADVERTISING, "高品质", "广告法禁止使用绝对化用语"),
            ("世界级", SeverityLevel.WARNING, SensitiveWordCategory.ADVERTISING, "国际水准", "广告法禁止使用绝对化用语"),
            
            # 严重级别 - 虚假宣传
            ("根治", SeverityLevel.SERIOUS, SensitiveWordCategory.HEALTH, "改善", "禁止承诺治疗效果"),
            ("治愈率", SeverityLevel.SERIOUS, SensitiveWordCategory.HEALTH, "有效率", "禁止承诺治疗效果"),
            ("无效退款", SeverityLevel.SERIOUS, SensitiveWordCategory.ADVERTISING, "售后保障", "禁止承诺性用语"),
            ("百分百", SeverityLevel.SERIOUS, SensitiveWordCategory.ADVERTISING, "高度", "禁止绝对化承诺"),
            
            # 封禁级别 - 违法违规
            ("赌博", SeverityLevel.BANNED, SensitiveWordCategory.GENERAL, None, "违法内容"),
            ("诈骗", SeverityLevel.BANNED, SensitiveWordCategory.GENERAL, None, "违法内容"),
            ("传销", SeverityLevel.BANNED, SensitiveWordCategory.GENERAL, None, "违法内容"),
        ]
        
        for word, severity, category, replacement, reason in default_words:
            self.add_word(word, severity, category, replacement, reason)
        
        self._save_library()
    
    def add_word(
        self,
        word: str,
        severity: SeverityLevel,
        category: SensitiveWordCategory = SensitiveWordCategory.GENERAL,
        replacement: Optional[str] = None,
        reason: str = ""
    ) -> bool:
        """添加敏感词"""
        if word in self.word_library:
            return False
        
        entry = SensitiveWordEntry(
            word=word,
            severity=severity,
            category=category,
            replacement=replacement,
            reason=reason
        )
        self.word_library[word] = entry
        self._save_library()
        return True
    
    def remove_word(self, word: str) -> bool:
        """删除敏感词"""
        if word not in self.word_library:
            return False
        
        del self.word_library[word]
        self._save_library()
        return True
    
    def update_word(
        self,
        word: str,
        severity: Optional[SeverityLevel] = None,
        category: Optional[SensitiveWordCategory] = None,
        replacement: Optional[str] = None,
        reason: Optional[str] = None
    ) -> bool:
        """更新敏感词"""
        if word not in self.word_library:
            return False
        
        entry = self.word_library[word]
        if severity:
            entry.severity = severity
        if category:
            entry.category = category
        if replacement is not None:
            entry.replacement = replacement
        if reason is not None:
            entry.reason = reason
        
        self._save_library()
        return True
    
    def get_word(self, word: str) -> Optional[SensitiveWordEntry]:
        """获取敏感词详情"""
        return self.word_library.get(word)
    
    def list_words(
        self,
        category: Optional[SensitiveWordCategory] = None,
        severity: Optional[SeverityLevel] = None,
        keyword: Optional[str] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Tuple[List[Dict], int]:
        """列出敏感词（支持筛选和分页）"""
        filtered = list(self.word_library.values())
        
        if category:
            filtered = [w for w in filtered if w.category == category]
        if severity:
            filtered = [w for w in filtered if w.severity == severity]
        if keyword:
            filtered = [w for w in filtered if keyword.lower() in w.word.lower()]
        
        # 按命中次数排序
        filtered.sort(key=lambda x: x.hit_count, reverse=True)
        
        total = len(filtered)
        start = (page - 1) * page_size
        end = start + page_size
        
        return [w.to_dict() for w in filtered[start:end]], total
    
    def detect(self, text: str) -> List[Dict]:
        """检测文本中的敏感词"""
        self.usage_stats["total_checks"] += 1
        
        hits = []
        for word, entry in self.word_library.items():
            # 使用正则匹配，支持词边界
            pattern = re.compile(re.escape(word), re.IGNORECASE)
            matches = list(pattern.finditer(text))
            
            for match in matches:
                entry.hit_count += 1
                hit_info = {
                    "word": word,
                    "severity": entry.severity.value,
                    "category": entry.category.value,
                    "replacement": entry.replacement,
                    "reason": entry.reason,
                    "position": {
                        "start": match.start(),
                        "end": match.end()
                    },
                    "context": self._get_context(text, match.start(), match.end())
                }
                hits.append(hit_info)
                
                # 更新统计
                self.usage_stats["total_hits"] += 1
                self.usage_stats["hits_by_level"][entry.severity.value] += 1
                
                category_key = entry.category.value
                if category_key not in self.usage_stats["hits_by_category"]:
                    self.usage_stats["hits_by_category"][category_key] = 0
                self.usage_stats["hits_by_category"][category_key] += 1
        
        # 更新每日统计
        today = datetime.now().strftime("%Y-%m-%d")
        if today not in self.usage_stats["daily_stats"]:
            self.usage_stats["daily_stats"][today] = {
                "checks": 0,
                "hits": 0
            }
        self.usage_stats["daily_stats"][today]["checks"] += 1
        self.usage_stats["daily_stats"][today]["hits"] += len(hits)
        
        # 按严重程度排序
        severity_order = {"banned": 0, "serious": 1, "warning": 2}
        hits.sort(key=lambda x: severity_order.get(x["severity"], 3))
        
        self._save_stats()
        return hits
    
    def detect_realtime(self, text: str, callback=None) -> Dict:
        """实时检测（用于语音转写同步检测）"""
        hits = self.detect(text)
        
        result = {
            "text": text,
            "hits": hits,
            "has_sensitive": len(hits) > 0,
            "max_severity": self._get_max_severity(hits),
            "should_block": any(h["severity"] == "banned" for h in hits),
            "suggested_text": self._apply_replacements(text, hits),
            "timestamp": datetime.now().isoformat()
        }
        
        if callback:
            callback(result)
        
        return result
    
    def _get_context(self, text: str, start: int, end: int, radius: int = 10) -> str:
        """获取敏感词上下文"""
        ctx_start = max(0, start - radius)
        ctx_end = min(len(text), end + radius)
        
        prefix = "..." if ctx_start > 0 else ""
        suffix = "..." if ctx_end < len(text) else ""
        
        return f"{prefix}{text[ctx_start:ctx_end]}{suffix}"
    
    def _get_max_severity(self, hits: List[Dict]) -> Optional[str]:
        """获取最高严重程度"""
        if not hits:
            return None
        
        severity_order = {"banned": 3, "serious": 2, "warning": 1}
        max_sev = max(hits, key=lambda x: severity_order.get(x["severity"], 0))
        return max_sev["severity"]
    
    def _apply_replacements(self, text: str, hits: List[Dict]) -> str:
        """应用替换建议"""
        # 按位置倒序排序，避免替换后位置变化
        sorted_hits = sorted(hits, key=lambda x: x["position"]["start"], reverse=True)
        
        result = text
        for hit in sorted_hits:
            if hit["replacement"]:
                start = hit["position"]["start"]
                end = hit["position"]["end"]
                result = result[:start] + hit["replacement"] + result[end:]
        
        return result
    
    def get_statistics(self) -> Dict:
        """获取使用统计"""
        return {
            "library_size": len(self.word_library),
            "total_checks": self.usage_stats["total_checks"],
            "total_hits": self.usage_stats["total_hits"],
            "hit_rate": (
                self.usage_stats["total_hits"] / max(1, self.usage_stats["total_checks"])
            ),
            "hits_by_level": self.usage_stats["hits_by_level"],
            "hits_by_category": self.usage_stats["hits_by_category"],
            "daily_stats": dict(list(self.usage_stats["daily_stats"].items())[-7:])  # 最近 7 天
        }
    
    def get_category_stats(self) -> Dict[str, int]:
        """获取各分类词库数量"""
        stats = {}
        for entry in self.word_library.values():
            cat = entry.category.value
            stats[cat] = stats.get(cat, 0) + 1
        return stats
    
    def install_industry_package(self, category: str, words: List[Dict]) -> bool:
        """安装行业敏感词包"""
        self.industry_packages[category] = words
        self._save_industry_packages()
        
        # 将行业词包添加到主词库
        for word_data in words:
            self.add_word(
                word=word_data["word"],
                severity=SeverityLevel(word_data["severity"]),
                category=SensitiveWordCategory(category),
                replacement=word_data.get("replacement"),
                reason=word_data.get("reason", "")
            )
        
        return True
    
    def get_industry_packages(self) -> List[Dict]:
        """获取已安装的行业词包"""
        return [
            {
                "category": cat,
                "word_count": len(words),
                "installed_at": words[0].get("installed_at", "unknown") if words else "unknown"
            }
            for cat, words in self.industry_packages.items()
        ]
    
    def export_library(self) -> str:
        """导出词库为 JSON"""
        return json.dumps(
            {k: v.to_dict() for k, v in self.word_library.items()},
            ensure_ascii=False,
            indent=2
        )
    
    def import_library(self, json_data: str, merge: bool = True) -> int:
        """导入词库"""
        data = json.loads(json_data)
        count = 0
        
        for word, entry_data in data.items():
            if merge or word not in self.word_library:
                self.word_library[word] = SensitiveWordEntry.from_dict(entry_data)
                count += 1
        
        self._save_library()
        return count


# 单例实例
_service_instance: Optional[SensitiveWordService] = None


def get_service() -> SensitiveWordService:
    """获取服务单例"""
    global _service_instance
    if _service_instance is None:
        _service_instance = SensitiveWordService()
    return _service_instance


# 便捷函数
def detect_sensitive_words(text: str) -> List[Dict]:
    """检测敏感词"""
    return get_service().detect(text)


def detect_realtime(text: str) -> Dict:
    """实时检测"""
    return get_service().detect_realtime(text)
