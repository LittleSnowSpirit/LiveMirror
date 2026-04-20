"""
直播间标题优化服务 - LiveMirror
支持 AI 生成标题、评分系统、关键词优化、A/B 测试、历史分析
"""

import json
import re
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from enum import Enum
from pathlib import Path
import random


class TitleCategory(Enum):
    """标题分类"""
    BEAUTY = "beauty"            # 美妆
    FASHION = "fashion"          # 服装
    FOOD = "food"                # 食品
    ELECTRONICS = "electronics"  # 数码
    HOME = "home"                # 家居
    ENTERTAINMENT = "entertainment"  # 娱乐
    EDUCATION = "education"      # 教育
    GENERAL = "general"          # 通用


class TitleScoreFactor(Enum):
    """评分因子"""
    ATTRACTIVENESS = "attractiveness"  # 吸引力
    CLARITY = "clarity"                # 清晰度
    RELEVANCE = "relevance"            # 相关性
    URGENCY = "urgency"                # 紧迫感
    EMOTION = "emotion"                # 情感共鸣
    KEYWORD_OPTIMIZATION = "keyword"   # 关键词优化


class TitleTemplate:
    """标题模板"""
    def __init__(
        self,
        template: str,
        category: TitleCategory,
        description: str,
        effectiveness_score: float = 0.8
    ):
        self.template = template
        self.category = category
        self.description = description
        self.effectiveness_score = effectiveness_score
    
    def generate(self, **kwargs) -> str:
        """使用模板生成标题"""
        result = self.template
        for key, value in kwargs.items():
            result = result.replace(f"{{{key}}}", str(value))
        return result


class TitleHistoryEntry:
    """标题历史记录"""
    def __init__(
        self,
        title: str,
        category: TitleCategory,
        created_at: datetime,
        metrics: Optional[Dict] = None
    ):
        self.title = title
        self.category = category
        self.created_at = created_at
        self.metrics = metrics or {
            "clicks": 0,
            "views": 0,
            "ctr": 0.0,
            "engagement": 0.0
        }
    
    def to_dict(self) -> Dict:
        return {
            "title": self.title,
            "category": self.category.value,
            "created_at": self.created_at.isoformat(),
            "metrics": self.metrics
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "TitleHistoryEntry":
        return cls(
            title=data["title"],
            category=TitleCategory(data.get("category", "general")),
            created_at=datetime.fromisoformat(data["created_at"]),
            metrics=data.get("metrics")
        )


class TitleOptimizerService:
    """直播间标题优化服务"""
    
    def __init__(self, data_dir: str = "data/title_optimizer"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        # 数据文件路径
        self.history_path = self.data_dir / "title_history.json"
        self.ab_tests_path = self.data_dir / "ab_tests.json"
        self.keywords_path = self.data_dir / "keywords.json"
        self.templates_path = self.data_dir / "templates.json"
        
        # 内存数据
        self.history: List[TitleHistoryEntry] = []
        self.ab_tests: Dict[str, Dict] = {}
        self.keywords: Dict[str, Dict] = {}
        self.templates: List[TitleTemplate] = []
        
        # 加载数据
        self._load_history()
        self._load_ab_tests()
        self._load_keywords()
        self._load_templates()
        
        # 如果没有初始模板，加载默认模板
        if not self.templates:
            self._init_default_templates()
    
    def _load_history(self):
        """加载标题历史"""
        if self.history_path.exists():
            with open(self.history_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.history = [TitleHistoryEntry.from_dict(item) for item in data]
    
    def _save_history(self):
        """保存标题历史"""
        with open(self.history_path, "w", encoding="utf-8") as f:
            json.dump(
                [item.to_dict() for item in self.history],
                f,
                ensure_ascii=False,
                indent=2
            )
    
    def _load_ab_tests(self):
        """加载 A/B 测试数据"""
        if self.ab_tests_path.exists():
            with open(self.ab_tests_path, "r", encoding="utf-8") as f:
                self.ab_tests = json.load(f)
    
    def _save_ab_tests(self):
        """保存 A/B 测试数据"""
        with open(self.ab_tests_path, "w", encoding="utf-8") as f:
            json.dump(self.ab_tests, f, ensure_ascii=False, indent=2)
    
    def _load_keywords(self):
        """加载关键词数据"""
        if self.keywords_path.exists():
            with open(self.keywords_path, "r", encoding="utf-8") as f:
                self.keywords = json.load(f)
    
    def _save_keywords(self):
        """保存关键词数据"""
        with open(self.keywords_path, "w", encoding="utf-8") as f:
            json.dump(self.keywords, f, ensure_ascii=False, indent=2)
    
    def _load_templates(self):
        """加载标题模板"""
        if self.templates_path.exists():
            with open(self.templates_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.templates = [
                    TitleTemplate(
                        template=item["template"],
                        category=TitleCategory(item["category"]),
                        description=item["description"],
                        effectiveness_score=item.get("effectiveness_score", 0.8)
                    )
                    for item in data
                ]
    
    def _save_templates(self):
        """保存标题模板"""
        with open(self.templates_path, "w", encoding="utf-8") as f:
            json.dump(
                [
                    {
                        "template": t.template,
                        "category": t.category.value,
                        "description": t.description,
                        "effectiveness_score": t.effectiveness_score
                    }
                    for t in self.templates
                ],
                f,
                ensure_ascii=False,
                indent=2
            )
    
    def _init_default_templates(self):
        """初始化默认标题模板"""
        default_templates = [
            # 通用模板
            TitleTemplate("🔥{product}限时秒杀！手慢无！", TitleCategory.GENERAL, "紧迫感模板", 0.85),
            TitleTemplate("✨{benefit}的秘密，99% 的人都不知道", TitleCategory.GENERAL, "好奇心模板", 0.88),
            TitleTemplate("💰今天不买亏大了！{product}史低价", TitleCategory.GENERAL, "优惠模板", 0.82),
            TitleTemplate("🎁买{product}送{gift}！仅限今天", TitleCategory.GENERAL, "赠品模板", 0.80),
            
            # 美妆模板
            TitleTemplate("💄{product}让你美到发光！明星同款", TitleCategory.BEAUTY, "美妆明星模板", 0.87),
            TitleTemplate("🌟7 天焕肤！{product}效果惊人", TitleCategory.BEAUTY, "美妆效果模板", 0.85),
            TitleTemplate("💅美妆博主都在用的{product}，绝了！", TitleCategory.BEAUTY, "美妆博主模板", 0.86),
            
            # 服装模板
            TitleTemplate("👗{style}穿搭，美到犯规！", TitleCategory.FASHION, "服装风格模板", 0.84),
            TitleTemplate("🔥显瘦{effect}斤！这件{product}太神了", TitleCategory.FASHION, "服装效果模板", 0.88),
            TitleTemplate("💃明星同款{product}，今天破价！", TitleCategory.FASHION, "服装明星模板", 0.83),
            
            # 食品模板
            TitleTemplate("😋好吃到停不下来！{product}必买", TitleCategory.FOOD, "食品美味模板", 0.86),
            TitleTemplate("🍲正宗{origin}{product}，口水直流", TitleCategory.FOOD, "食品产地模板", 0.84),
            TitleTemplate("🎉网红爆款{product}，尝鲜价！", TitleCategory.FOOD, "食品网红模板", 0.85),
            
            # 数码模板
            TitleTemplate("📱{product}性能炸裂！性价比之王", TitleCategory.ELECTRONICS, "数码性能模板", 0.87),
            TitleTemplate("⚡黑科技{product}，颠覆你的想象", TitleCategory.ELECTRONICS, "数码科技模板", 0.89),
            TitleTemplate("🎮数码发烧友必入{product}！", TitleCategory.ELECTRONICS, "数码发烧友模板", 0.85),
            
            # 家居模板
            TitleTemplate("🏠提升幸福感的{product}，太值了", TitleCategory.HOME, "家居幸福模板", 0.86),
            TitleTemplate("✨收纳神器{product}，家变大了", TitleCategory.HOME, "家居收纳模板", 0.84),
            TitleTemplate("🛋️提升生活品质的{product}推荐", TitleCategory.HOME, "家居品质模板", 0.83),
        ]
        
        self.templates = default_templates
        self._save_templates()
    
    def _init_default_keywords(self):
        """初始化默认关键词"""
        default_keywords = {
            "urgency": {
                "words": ["限时", "秒杀", "手慢无", "仅限今天", "最后 X 小时", "即将涨价", "库存告急"],
                "weight": 1.2
            },
            "emotion": {
                "words": ["美到发光", "绝了", "太神了", "必买", "炸裂", "颠覆", "惊艳"],
                "weight": 1.15
            },
            "benefit": {
                "words": ["省钱", "显瘦", "焕肤", "提升", "改善", "增强", "优化"],
                "weight": 1.1
            },
            "social_proof": {
                "words": ["明星同款", "网红爆款", "博主推荐", "销量第一", "口碑爆棚", "万人好评"],
                "weight": 1.25
            },
            "curiosity": {
                "words": ["秘密", "99% 的人不知道", "揭秘", "内部", "独家", "首次公开"],
                "weight": 1.3
            }
        }
        
        self.keywords = default_keywords
        self._save_keywords()
    
    def generate_titles(
        self,
        product: str,
        category: TitleCategory = TitleCategory.GENERAL,
        count: int = 5,
        context: Optional[Dict] = None
    ) -> List[Dict]:
        """AI 生成吸引人文案"""
        if not self.keywords:
            self._init_default_keywords()
        
        generated = []
        context = context or {}
        
        # 筛选相关模板
        relevant_templates = [
            t for t in self.templates
            if t.category == category or t.category == TitleCategory.GENERAL
        ]
        
        # 按效果分数排序
        relevant_templates.sort(key=lambda t: t.effectiveness_score, reverse=True)
        
        # 生成标题
        for i, template in enumerate(relevant_templates[:count * 2]):
            if len(generated) >= count:
                break
            
            # 准备模板变量
            kwargs = {"product": product}
            
            # 根据上下文填充其他变量
            if "benefit" in context:
                kwargs["benefit"] = context["benefit"]
            else:
                # 从关键词中随机选择一个 benefits
                benefit_keywords = self.keywords.get("benefit", {}).get("words", ["提升"])
                kwargs["benefit"] = random.choice(benefit_keywords)
            
            if "gift" in context:
                kwargs["gift"] = context["gift"]
            else:
                kwargs["gift"] = "精美礼品"
            
            if "style" in context:
                kwargs["style"] = context["style"]
            else:
                kwargs["style"] = "时尚"
            
            if "effect" in context:
                kwargs["effect"] = context["effect"]
            else:
                kwargs["effect"] = "10"
            
            if "origin" in context:
                kwargs["origin"] = context["origin"]
            else:
                kwargs["origin"] = "进口"
            
            title = template.generate(**kwargs)
            
            # 计算评分
            score = self._calculate_score(title, category)
            
            generated.append({
                "title": title,
                "template": template.description,
                "category": category.value,
                "score": score,
                "effectiveness": template.effectiveness_score
            })
        
        # 按评分排序
        generated.sort(key=lambda x: x["score"], reverse=True)
        
        return generated[:count]
    
    def _calculate_score(
        self,
        title: str,
        category: TitleCategory,
        historical_data: Optional[Dict] = None
    ) -> Dict:
        """标题评分系统（点击率预测）"""
        if not self.keywords:
            self._init_default_keywords()
        
        factors = {}
        total_score = 0.0
        max_score = 0.0
        
        # 1. 吸引力评分 (0-100)
        attract_score = self._score_attractiveness(title)
        factors[TitleScoreFactor.ATTRACTIVENESS.value] = attract_score
        total_score += attract_score * 0.25
        max_score += 100 * 0.25
        
        # 2. 清晰度评分 (0-100)
        clarity_score = self._score_clarity(title)
        factors[TitleScoreFactor.CLARITY.value] = clarity_score
        total_score += clarity_score * 0.20
        max_score += 100 * 0.20
        
        # 3. 相关性评分 (0-100)
        relevance_score = self._score_relevance(title, category)
        factors[TitleScoreFactor.RELEVANCE.value] = relevance_score
        total_score += relevance_score * 0.20
        max_score += 100 * 0.20
        
        # 4. 紧迫感评分 (0-100)
        urgency_score = self._score_urgency(title)
        factors[TitleScoreFactor.URGENCY.value] = urgency_score
        total_score += urgency_score * 0.15
        max_score += 100 * 0.15
        
        # 5. 情感共鸣评分 (0-100)
        emotion_score = self._score_emotion(title)
        factors[TitleScoreFactor.EMOTION.value] = emotion_score
        total_score += emotion_score * 0.10
        max_score += 100 * 0.10
        
        # 6. 关键词优化评分 (0-100)
        keyword_score = self._score_keywords(title)
        factors[TitleScoreFactor.KEYWORD_OPTIMIZATION.value] = keyword_score
        total_score += keyword_score * 0.10
        max_score += 100 * 0.10
        
        # 计算总分 (0-100)
        final_score = (total_score / max_score) * 100 if max_score > 0 else 0
        
        # 预测点击率 (基于历史数据校准)
        predicted_ctr = self._predict_ctr(final_score, historical_data)
        
        # 评级
        rating = self._get_rating(final_score)
        
        return {
            "total": round(final_score, 2),
            "predicted_ctr": round(predicted_ctr, 2),
            "rating": rating,
            "factors": {k: round(v, 2) for k, v in factors.items()},
            "max_score": max_score
        }
    
    def _score_attractiveness(self, title: str) -> float:
        """吸引力评分"""
        score = 50.0  # 基础分
        
        # 检查是否包含 emoji
        emoji_pattern = re.compile(r'[\U00010000-\U00010ffff]')
        emojis = emoji_pattern.findall(title)
        if emojis:
            score += min(len(emojis) * 5, 20)  # 最多加 20 分
        
        # 检查是否包含数字
        if re.search(r'\d+', title):
            score += 10
        
        # 检查是否包含感叹号
        if '!' in title or '！' in title:
            score += 5
        
        # 检查长度 (15-30 字最佳)
        length = len(title)
        if 15 <= length <= 30:
            score += 15
        elif 10 <= length <= 40:
            score += 8
        
        return min(score, 100)
    
    def _score_clarity(self, title: str) -> float:
        """清晰度评分"""
        score = 60.0  # 基础分
        
        # 检查是否有明确的产品/主题
        if len(title.split()) >= 3:
            score += 15
        
        # 检查是否有明确的行动号召
        action_words = ["买", "抢", "看", "来", "点击", "进入", "秒杀"]
        if any(word in title for word in action_words):
            score += 15
        
        # 检查是否有明确的价值主张
        value_words = ["价", "省", "送", "免费", "优惠", "折扣", "福利"]
        if any(word in title for word in value_words):
            score += 10
        
        return min(score, 100)
    
    def _score_relevance(self, title: str, category: TitleCategory) -> float:
        """相关性评分"""
        score = 50.0  # 基础分
        
        # 根据分类检查关键词
        category_keywords = {
            TitleCategory.BEAUTY: ["美", "妆", "肤", "唇", "眼", "护肤", "化妆"],
            TitleCategory.FASHION: ["穿", "搭", "衣", "服", "装", "显瘦", "时尚"],
            TitleCategory.FOOD: ["吃", "味", "香", "甜", "辣", "美食", "零食"],
            TitleCategory.ELECTRONICS: ["数码", "电子", "智能", "科技", "性能", "配置"],
            TitleCategory.HOME: ["家", "居", "收纳", "生活", "品质", "幸福"],
        }
        
        keywords = category_keywords.get(category, [])
        matched = sum(1 for kw in keywords if kw in title)
        
        if matched >= 2:
            score += 40
        elif matched >= 1:
            score += 25
        
        return min(score, 100)
    
    def _score_urgency(self, title: str) -> float:
        """紧迫感评分"""
        score = 30.0  # 基础分
        
        urgency_words = ["限时", "秒杀", "今天", "仅限", "最后", "即将", "手慢", "库存"]
        matched = sum(1 for word in urgency_words if word in title)
        
        score += matched * 15
        
        # 检查是否有时间限制
        if re.search(r'\d+[小分时天]', title):
            score += 10
        
        return min(score, 100)
    
    def _score_emotion(self, title: str) -> float:
        """情感共鸣评分"""
        score = 40.0  # 基础分
        
        emotion_words = ["美", "绝", "神", "爱", "喜欢", "惊喜", "惊艳", "炸裂", "必买"]
        matched = sum(1 for word in emotion_words if word in title)
        
        score += matched * 10
        
        # 检查是否有表情符号
        if re.search(r'[\U00010000-\U00010ffff]', title):
            score += 15
        
        return min(score, 100)
    
    def _score_keywords(self, title: str) -> float:
        """关键词优化评分"""
        score = 50.0  # 基础分
        
        for category, data in self.keywords.items():
            words = data.get("words", [])
            weight = data.get("weight", 1.0)
            matched = sum(1 for word in words if word in title)
            if matched > 0:
                score += matched * 10 * weight
        
        return min(score, 100)
    
    def _predict_ctr(self, score: float, historical_data: Optional[Dict] = None) -> float:
        """预测点击率"""
        # 基础 CTR 模型：分数越高，CTR 越高
        # 假设：100 分对应 20% CTR, 50 分对应 5% CTR
        base_ctr = 0.05 + (score / 100) * 0.15
        
        # 如果有历史数据，进行校准
        if historical_data:
            historical_ctr = historical_data.get("avg_ctr", 0)
            if historical_ctr > 0:
                # 简单加权平均
                base_ctr = base_ctr * 0.7 + historical_ctr * 0.3
        
        return base_ctr * 100  # 转换为百分比
    
    def _get_rating(self, score: float) -> str:
        """获取评级"""
        if score >= 90:
            return "S"
        elif score >= 80:
            return "A"
        elif score >= 70:
            return "B"
        elif score >= 60:
            return "C"
        else:
            return "D"
    
    def get_keyword_suggestions(
        self,
        title: str,
        category: TitleCategory = TitleCategory.GENERAL
    ) -> Dict:
        """关键词优化建议"""
        if not self.keywords:
            self._init_default_keywords()
        
        suggestions = {
            "current_keywords": [],
            "missing_keywords": [],
            "recommendations": []
        }
        
        # 检查当前使用的关键词
        for cat, data in self.keywords.items():
            words = data.get("words", [])
            for word in words:
                if word in title:
                    suggestions["current_keywords"].append({
                        "keyword": word,
                        "category": cat,
                        "weight": data.get("weight", 1.0)
                    })
        
        # 推荐缺失的高权重关键词
        for cat, data in self.keywords.items():
            words = data.get("words", [])
            weight = data.get("weight", 1.0)
            
            # 找出未使用的关键词
            unused = [w for w in words if w not in title]
            
            if unused and weight >= 1.2:  # 只推荐高权重关键词
                suggestions["missing_keywords"].append({
                    "keyword": random.choice(unused),
                    "category": cat,
                    "weight": weight,
                    "reason": f"高权重{cat}关键词，可提升吸引力"
                })
        
        # 生成具体建议
        if len(suggestions["current_keywords"]) < 2:
            suggestions["recommendations"].append({
                "type": "add_keywords",
                "message": "建议添加 2-3 个高权重关键词，如：限时、秒杀、明星同款",
                "priority": "high"
            })
        
        if len(title) < 15:
            suggestions["recommendations"].append({
                "type": "increase_length",
                "message": "标题过短，建议扩展到 15-30 字，增加信息量",
                "priority": "medium"
            })
        elif len(title) > 40:
            suggestions["recommendations"].append({
                "type": "decrease_length",
                "message": "标题过长，建议精简到 30 字以内，突出核心卖点",
                "priority": "medium"
            })
        
        if "!" not in title and "！" not in title:
            suggestions["recommendations"].append({
                "type": "add_emotion",
                "message": "可添加感叹号增强情感表达",
                "priority": "low"
            })
        
        return suggestions
    
    def create_ab_test(
        self,
        title_a: str,
        title_b: str,
        category: TitleCategory = TitleCategory.GENERAL,
        duration_hours: int = 24
    ) -> Dict:
        """创建 A/B 测试"""
        test_id = f"ab_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # 计算初始评分
        score_a = self._calculate_score(title_a, category)
        score_b = self._calculate_score(title_b, category)
        
        test = {
            "id": test_id,
            "title_a": title_a,
            "title_b": title_b,
            "category": category.value,
            "created_at": datetime.now().isoformat(),
            "end_at": (datetime.now() + timedelta(hours=duration_hours)).isoformat(),
            "status": "active",
            "metrics": {
                "a": {"views": 0, "clicks": 0, "conversions": 0},
                "b": {"views": 0, "clicks": 0, "conversions": 0}
            },
            "scores": {
                "a": score_a,
                "b": score_b
            },
            "winner": None
        }
        
        self.ab_tests[test_id] = test
        self._save_ab_tests()
        
        return {
            "test_id": test_id,
            "title_a": title_a,
            "title_b": title_b,
            "score_a": score_a["total"],
            "score_b": score_b["total"],
            "predicted_winner": "A" if score_a["total"] > score_b["total"] else "B",
            "duration_hours": duration_hours
        }
    
    def update_ab_test_metrics(
        self,
        test_id: str,
        variant: str,
        views: int = 0,
        clicks: int = 0,
        conversions: int = 0
    ) -> Dict:
        """更新 A/B 测试指标"""
        if test_id not in self.ab_tests:
            raise ValueError(f"A/B 测试不存在：{test_id}")
        
        test = self.ab_tests[test_id]
        
        if variant not in ["a", "b"]:
            raise ValueError("变体必须是 'a' 或 'b'")
        
        # 更新指标
        test["metrics"][variant]["views"] += views
        test["metrics"][variant]["clicks"] += clicks
        test["metrics"][variant]["conversions"] += conversions
        
        # 计算 CTR
        for v in ["a", "b"]:
            if test["metrics"][v]["views"] > 0:
                test["metrics"][v]["ctr"] = (
                    test["metrics"][v]["clicks"] / test["metrics"][v]["views"]
                ) * 100
            else:
                test["metrics"][v]["ctr"] = 0
        
        # 判断获胜者
        ctr_a = test["metrics"]["a"].get("ctr", 0)
        ctr_b = test["metrics"]["b"].get("ctr", 0)
        
        if test["metrics"]["a"]["views"] >= 100 and test["metrics"]["b"]["views"] >= 100:
            if ctr_a > ctr_b * 1.1:  # A 比 B 高 10% 以上
                test["winner"] = "a"
                test["status"] = "completed"
            elif ctr_b > ctr_a * 1.1:  # B 比 A 高 10% 以上
                test["winner"] = "b"
                test["status"] = "completed"
        
        self._save_ab_tests()
        
        return {
            "test_id": test_id,
            "status": test["status"],
            "metrics": test["metrics"],
            "winner": test["winner"],
            "ctr_a": ctr_a,
            "ctr_b": ctr_b
        }
    
    def get_ab_test(self, test_id: str) -> Dict:
        """获取 A/B 测试详情"""
        if test_id not in self.ab_tests:
            raise ValueError(f"A/B 测试不存在：{test_id}")
        
        test = self.ab_tests[test_id]
        
        return {
            "id": test["id"],
            "title_a": test["title_a"],
            "title_b": test["title_b"],
            "category": test["category"],
            "created_at": test["created_at"],
            "end_at": test["end_at"],
            "status": test["status"],
            "metrics": test["metrics"],
            "scores": test["scores"],
            "winner": test["winner"]
        }
    
    def list_ab_tests(self, status: Optional[str] = None) -> List[Dict]:
        """列出 A/B 测试"""
        tests = list(self.ab_tests.values())
        
        if status:
            tests = [t for t in tests if t["status"] == status]
        
        # 按创建时间倒序
        tests.sort(key=lambda x: x["created_at"], reverse=True)
        
        return [
            {
                "id": t["id"],
                "title_a": t["title_a"],
                "title_b": t["title_b"],
                "category": t["category"],
                "status": t["status"],
                "winner": t["winner"],
                "created_at": t["created_at"]
            }
            for t in tests
        ]
    
    def add_to_history(
        self,
        title: str,
        category: TitleCategory = TitleCategory.GENERAL,
        metrics: Optional[Dict] = None
    ):
        """添加到历史记录"""
        entry = TitleHistoryEntry(
            title=title,
            category=category,
            created_at=datetime.now(),
            metrics=metrics
        )
        
        self.history.append(entry)
        self._save_history()
    
    def get_history(
        self,
        category: Optional[TitleCategory] = None,
        days: int = 30,
        limit: int = 100
    ) -> List[Dict]:
        """获取历史记录"""
        filtered = self.history
        
        if category:
            filtered = [h for h in filtered if h.category == category]
        
        # 筛选最近 N 天
        cutoff = datetime.now() - timedelta(days=days)
        filtered = [h for h in filtered if h.created_at >= cutoff]
        
        # 按时间倒序
        filtered.sort(key=lambda x: x.created_at, reverse=True)
        
        return [h.to_dict() for h in filtered[:limit]]
    
    def analyze_history(self, days: int = 30) -> Dict:
        """分析历史记录"""
        cutoff = datetime.now() - timedelta(days=days)
        recent = [h for h in self.history if h.created_at >= cutoff]
        
        if not recent:
            return {
                "total_titles": 0,
                "avg_score": 0,
                "avg_ctr": 0,
                "best_performing": None,
                "category_distribution": {}
            }
        
        # 计算平均指标
        scores = []
        ctrs = []
        category_counts = {}
        
        for entry in recent:
            if entry.metrics:
                if "score" in entry.metrics:
                    scores.append(entry.metrics["score"])
                if "ctr" in entry.metrics:
                    ctrs.append(entry.metrics["ctr"])
            
            cat = entry.category.value
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        # 找出最佳表现
        best = None
        best_ctr = 0
        for entry in recent:
            if entry.metrics and entry.metrics.get("ctr", 0) > best_ctr:
                best_ctr = entry.metrics["ctr"]
                best = entry
        
        return {
            "total_titles": len(recent),
            "avg_score": sum(scores) / len(scores) if scores else 0,
            "avg_ctr": sum(ctrs) / len(ctrs) if ctrs else 0,
            "best_performing": best.to_dict() if best else None,
            "category_distribution": category_counts,
            "time_range": {
                "from": cutoff.isoformat(),
                "to": datetime.now().isoformat()
            }
        }
    
    def get_industry_best_practices(self, category: TitleCategory) -> Dict:
        """获取行业最佳实践参考"""
        practices = {
            TitleCategory.GENERAL: {
                "title_length": "15-30 字",
                "key_elements": ["产品名称", "核心卖点", "优惠信息", "行动号召"],
                "tips": [
                    "使用 emoji 增强视觉吸引力",
                    "包含数字增加可信度",
                    "创造紧迫感促进转化",
                    "突出独特卖点"
                ],
                "examples": [
                    "🔥限时秒杀！XX 产品史低价，手慢无！",
                    "✨99% 的人都不知道的使用技巧，必看！"
                ]
            },
            TitleCategory.BEAUTY: {
                "title_length": "20-35 字",
                "key_elements": ["产品功效", "使用效果", "适用人群", "优惠力度"],
                "tips": [
                    "强调即时效果和长期改善",
                    "使用'明星同款''博主推荐'等社会认同",
                    "避免绝对化用语（广告法）",
                    "突出成分安全性和专业性"
                ],
                "examples": [
                    "💄明星化妆师推荐！7 天焕肤效果惊人",
                    "🌟美妆博主都在用的精华，今天破价！"
                ]
            },
            TitleCategory.FASHION: {
                "title_length": "18-32 字",
                "key_elements": ["款式风格", "穿搭效果", "尺码信息", "材质特点"],
                "tips": [
                    "突出显瘦、显高等视觉效果",
                    "强调搭配场景和风格",
                    "提供尺码建议减少退货",
                    "使用'同款''爆款'等热词"
                ],
                "examples": [
                    "👗显瘦 10 斤！这条裙子太绝了",
                    "🔥明星同款穿搭，今天限时秒杀！"
                ]
            },
            TitleCategory.FOOD: {
                "title_length": "15-28 字",
                "key_elements": ["口味特点", "产地信息", "食用场景", "优惠活动"],
                "tips": [
                    "用'好吃''香''脆'等感官词",
                    "强调正宗产地和传统工艺",
                    "突出健康、无添加等卖点",
                    "创造'尝鲜''必吃'等紧迫感"
                ],
                "examples": [
                    "😋好吃到停不下来！正宗 XX 特产",
                    "🍲网红爆款零食，今天尝鲜价！"
                ]
            },
            TitleCategory.ELECTRONICS: {
                "title_length": "20-35 字",
                "key_elements": ["核心参数", "性能优势", "适用场景", "性价比"],
                "tips": [
                    "突出关键参数和性能提升",
                    "强调性价比和竞品对比",
                    "使用'黑科技''性能炸裂'等热词",
                    "提供使用场景和体验描述"
                ],
                "examples": [
                    "📱性能炸裂！性价比之王就是它",
                    "⚡黑科技新品，颠覆你的想象！"
                ]
            },
            TitleCategory.HOME: {
                "title_length": "18-30 字",
                "key_elements": ["功能特点", "使用效果", "适用场景", "生活品质"],
                "tips": [
                    "强调提升生活品质和幸福感",
                    "突出实用性和便利性",
                    "使用'神器''必备'等推荐词",
                    "展示使用前后的对比效果"
                ],
                "examples": [
                    "🏠提升幸福感的家居好物，太值了",
                    "✨收纳神器！家瞬间变大了"
                ]
            }
        }
        
        return practices.get(category, practices[TitleCategory.GENERAL])


# 单例实例
_service_instance: Optional[TitleOptimizerService] = None


def get_service() -> TitleOptimizerService:
    """获取服务单例"""
    global _service_instance
    if _service_instance is None:
        _service_instance = TitleOptimizerService()
    return _service_instance


# 便捷函数
def generate_titles(product: str, category: str = "general", count: int = 5) -> List[Dict]:
    """生成标题"""
    service = get_service()
    cat = TitleCategory(category)
    return service.generate_titles(product, cat, count)


def score_title(title: str, category: str = "general") -> Dict:
    """评分标题"""
    service = get_service()
    cat = TitleCategory(category)
    return service._calculate_score(title, cat)


def get_keyword_suggestions(title: str, category: str = "general") -> Dict:
    """获取关键词建议"""
    service = get_service()
    cat = TitleCategory(category)
    return service.get_keyword_suggestions(title, cat)
