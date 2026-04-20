"""
直播剧本规划服务 - LiveMirror
支持整场直播剧本生成、分时段内容规划、产品上下架时间规划、互动环节设计、应急预案生成
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
from enum import Enum
from dataclasses import dataclass, asdict, field
import random


class ScriptDuration(Enum):
    """直播时长"""
    ONE_HOUR = "1h"
    TWO_HOURS = "2h"
    THREE_HOURS = "3h"
    FOUR_HOURS = "4h"


class ScriptSectionType(Enum):
    """剧本章节类型"""
    OPENING = "opening"
    PRODUCT_INTRO = "product_intro"
    INTERACTION = "interaction"
    PROMOTION = "promotion"
    BREAK = "break"
    CLOSING = "closing"


class InteractionType(Enum):
    """互动类型"""
    LUCKY_DRAW = "lucky_draw"
    QUIZ = "quiz"
    COUPON = "coupon"
    FLASH_SALE = "flash_sale"
    COMMENT_WALL = "comment_wall"
    GIFT_GIVEAWAY = "gift_giveaway"


@dataclass
class ProductSlot:
    """产品上架时段"""
    product_id: str
    product_name: str
    price: float
    original_price: float
    discount: str
    start_time: str
    end_time: str
    selling_points: List[str] = field(default_factory=list)
    script_lines: List[str] = field(default_factory=list)


@dataclass
class InteractionSlot:
    """互动环节"""
    type: InteractionType
    name: str
    start_time: str
    duration_minutes: int
    description: str
    rules: List[str] = field(default_factory=list)
    prizes: List[str] = field(default_factory=list)
    script_lines: List[str] = field(default_factory=list)


@dataclass
class ScriptSegment:
    """直播剧本片段"""
    segment_id: str
    segment_type: ScriptSectionType
    start_time: str
    end_time: str
    duration_minutes: int
    title: str
    description: str
    script_content: str
    notes: List[str] = field(default_factory=list)
    products: List[ProductSlot] = field(default_factory=list)
    interactions: List[InteractionSlot] = field(default_factory=list)


@dataclass
class EmergencyPlan:
    """应急预案"""
    scenario: str
    probability: str
    impact: str
    response_steps: List[str]
    backup_script: str
    responsible_person: str


@dataclass
class LiveScript:
    """直播剧本"""
    script_id: str
    title: str
    duration: ScriptDuration
    generated_at: datetime
    theme: str
    target_audience: str
    streamer_name: str
    segments: List[ScriptSegment]
    products: List[ProductSlot]
    interactions: List[InteractionSlot]
    emergency_plans: List[EmergencyPlan]
    overall_flow: str
    preparation_checklist: List[str]


class ScriptPlannerService:
    """剧本规划服务"""
    
    def __init__(self, data_dir: str = "data/script_planner"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.scripts_path = self.data_dir / "scripts.json"
        self.templates_path = self.data_dir / "templates.json"
        self.products_path = self.data_dir / "products.json"
        
        self.scripts: Dict[str, Dict] = {}
        self.templates: Dict[str, Dict] = {}
        self.products: Dict[str, Dict] = {}
        
        self._load_scripts()
        self._load_templates()
        self._load_products()
        
        if not self.templates:
            self._init_default_templates()
        
        if not self.products:
            self._init_sample_products()
    
    def _load_scripts(self):
        if self.scripts_path.exists():
            with open(self.scripts_path, "r", encoding="utf-8") as f:
                self.scripts = json.load(f)
    
    def _save_scripts(self):
        with open(self.scripts_path, "w", encoding="utf-8") as f:
            json.dump(self.scripts, f, ensure_ascii=False, indent=2)
    
    def _load_templates(self):
        if self.templates_path.exists():
            with open(self.templates_path, "r", encoding="utf-8") as f:
                self.templates = json.load(f)
    
    def _save_templates(self):
        with open(self.templates_path, "w", encoding="utf-8") as f:
            json.dump(self.templates, f, ensure_ascii=False, indent=2)
    
    def _load_products(self):
        if self.products_path.exists():
            with open(self.products_path, "r", encoding="utf-8") as f:
                self.products = json.load(f)
    
    def _save_products(self):
        with open(self.products_path, "w", encoding="utf-8") as f:
            json.dump(self.products, f, ensure_ascii=False, indent=2)
    
    def _init_default_templates(self):
        default_templates = {
            "standard_2h": {
                "name": "2 小时标准直播模板",
                "duration": "2h",
                "structure": [
                    {"type": "opening", "duration": 10, "title": "开场预热"},
                    {"type": "product_intro", "duration": 25, "title": "第一轮产品介绍"},
                    {"type": "interaction", "duration": 10, "title": "互动抽奖"},
                    {"type": "product_intro", "duration": 25, "title": "第二轮产品介绍"},
                    {"type": "break", "duration": 5, "title": "休息过渡"},
                    {"type": "promotion", "duration": 20, "title": "限时促销"},
                    {"type": "product_intro", "duration": 20, "title": "第三轮产品介绍"},
                    {"type": "interaction", "duration": 10, "title": "问答互动"},
                    {"type": "closing", "duration": 15, "title": "总结收尾"}
                ],
                "is_default": True
            },
            "fast_1h": {
                "name": "1 小时快闪直播模板",
                "duration": "1h",
                "structure": [
                    {"type": "opening", "duration": 5, "title": "快速开场"},
                    {"type": "product_intro", "duration": 20, "title": "核心产品介绍"},
                    {"type": "interaction", "duration": 10, "title": "秒杀互动"},
                    {"type": "promotion", "duration": 15, "title": "限时优惠"},
                    {"type": "closing", "duration": 10, "title": "总结催单"}
                ],
                "is_default": True
            },
            "marathon_4h": {
                "name": "4 小时马拉松直播模板",
                "duration": "4h",
                "structure": [
                    {"type": "opening", "duration": 15, "title": "开场预热"},
                    {"type": "product_intro", "duration": 30, "title": "第一轮产品"},
                    {"type": "interaction", "duration": 15, "title": "抽奖互动"},
                    {"type": "product_intro", "duration": 30, "title": "第二轮产品"},
                    {"type": "break", "duration": 10, "title": "休息"},
                    {"type": "promotion", "duration": 25, "title": "中场促销"},
                    {"type": "product_intro", "duration": 30, "title": "第三轮产品"},
                    {"type": "interaction", "duration": 15, "title": "游戏互动"},
                    {"type": "product_intro", "duration": 30, "title": "第四轮产品"},
                    {"type": "break", "duration": 10, "title": "休息"},
                    {"type": "promotion", "duration": 30, "title": "压轴大促"},
                    {"type": "interaction", "duration": 15, "title": "终极大奖"},
                    {"type": "closing", "duration": 25, "title": "总结收尾"}
                ],
                "is_default": True
            }
        }
        
        self.templates = default_templates
        self._save_templates()
    
    def _init_sample_products(self):
        sample_products = {
            "prod_001": {
                "product_id": "prod_001",
                "name": "智能保温杯",
                "price": 99.0,
                "original_price": 199.0,
                "discount": "5 折",
                "category": "家居用品",
                "selling_points": ["24 小时长效保温", "智能测温显示", "316 不锈钢内胆"],
                "target_audience": "上班族、学生党",
                "script_template": "这款智能保温杯真的是上班族必备！早上装的热水，晚上还是温热的。"
            },
            "prod_002": {
                "product_id": "prod_002",
                "name": "无线蓝牙耳机",
                "price": 159.0,
                "original_price": 399.0,
                "discount": "4 折",
                "category": "数码配件",
                "selling_points": ["主动降噪", "30 小时续航", "蓝牙 5.3"],
                "target_audience": "音乐爱好者、通勤族",
                "script_template": "音质超级棒！降噪效果堪比千元耳机，通勤路上完全隔绝噪音。"
            },
            "prod_003": {
                "product_id": "prod_003",
                "name": "便携式榨汁杯",
                "price": 79.0,
                "original_price": 159.0,
                "discount": "5 折",
                "category": "小家电",
                "selling_points": ["无线便携", "30 秒快速榨汁", "USB 充电"],
                "target_audience": "健身人士、果汁爱好者",
                "script_template": "随时随地都能喝到新鲜果汁！早上放几个水果，30 秒就好！"
            },
            "prod_004": {
                "product_id": "prod_004",
                "name": "护颈记忆枕",
                "price": 129.0,
                "original_price": 299.0,
                "discount": "4.3 折",
                "category": "家居用品",
                "selling_points": ["慢回弹记忆棉", "人体工学设计", "透气枕套"],
                "target_audience": "颈椎不适人群、上班族",
                "script_template": "睡了一周，颈椎真的舒服多了！这个枕头能完美贴合你的脖子。"
            },
            "prod_005": {
                "product_id": "prod_005",
                "name": "LED 化妆镜",
                "price": 89.0,
                "original_price": 199.0,
                "discount": "4.5 折",
                "category": "美妆工具",
                "selling_points": ["三色调光", "触屏调节", "10 倍放大镜"],
                "target_audience": "美妆爱好者",
                "script_template": "化妆再也不怕光线不好了！三种色温随便调，还有 10 倍放大镜。"
            }
        }
        
        self.products = sample_products
        self._save_products()
    
    def _format_time(self, minutes: int) -> str:
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours:02d}:{mins:02d}:00"
    
    def _generate_opening_script(self, theme: str, duration: int) -> ScriptSegment:
        return ScriptSegment(
            segment_id=f"seg_opening_{datetime.now().strftime('%H%M%S')}",
            segment_type=ScriptSectionType.OPENING,
            start_time="00:00:00",
            end_time=self._format_time(duration),
            duration_minutes=duration,
            title="开场预热",
            description="欢迎观众、介绍直播主题、预告福利",
            script_content=f"【开场话术】（{duration}分钟）\n\n欢迎观众来到直播间！\n今天主题是：{theme}\n准备了超多好货和福利！\n新进来的宝宝们记得点点关注！",
            notes=["检查麦克风音量和画面质量", "确认优惠券已上架", "准备抽奖工具"]
        )
    
    def _generate_product_intro_script(self, product: Dict, start_minutes: int, duration: int) -> ScriptSegment:
        start_time = self._format_time(start_minutes)
        end_time = self._format_time(start_minutes + duration)
        
        return ScriptSegment(
            segment_id=f"seg_product_{product['product_id']}_{datetime.now().strftime('%H%M%S')}",
            segment_type=ScriptSectionType.PRODUCT_INTRO,
            start_time=start_time,
            end_time=end_time,
            duration_minutes=duration,
            title=f"产品介绍：{product['name']}",
            description=f"详细介绍{product['name']}的卖点和优惠",
            script_content=f"【产品介绍】{product['name']}\n直播价：{product['price']}元（原价{product['original_price']}元）\n卖点：{', '.join(product.get('selling_points', []))}\n{product.get('script_template', '')}",
            notes=[f"确认{product['name']}库存充足", "准备产品实物展示", "确认优惠券已设置"],
            products=[ProductSlot(
                product_id=product["product_id"],
                product_name=product["name"],
                price=product["price"],
                original_price=product["original_price"],
                discount=product["discount"],
                start_time=start_time,
                end_time=end_time,
                selling_points=product.get("selling_points", [])[:3]
            )]
        )
    
    def _generate_interaction_script(self, interaction_type: InteractionType, start_minutes: int, duration: int) -> ScriptSegment:
        start_time = self._format_time(start_minutes)
        end_time = self._format_time(start_minutes + duration)
        
        configs = {
            InteractionType.LUCKY_DRAW: {
                "name": "幸运抽奖",
                "description": "抽取幸运观众送出精美礼品",
                "rules": ["关注主播 + 加入粉丝团", "公屏扣'想要'参与", "随机抽取 3 位"],
                "prizes": ["品牌保温杯", "无线耳机", "现金红包"]
            },
            InteractionType.QUIZ: {
                "name": "问答互动",
                "description": "有奖问答，答对送礼",
                "rules": ["主播提问", "观众抢答", "第一个答对获奖"],
                "prizes": ["优惠券", "小礼品", "积分奖励"]
            },
            InteractionType.COUPON: {
                "name": "抢券活动",
                "description": "限时抢大额优惠券",
                "rules": ["主播发放优惠券链接", "限时限量", "每人限领一张"],
                "prizes": ["50 元券", "30 元券", "满减券"]
            },
            InteractionType.FLASH_SALE: {
                "name": "秒杀活动",
                "description": "限时秒杀特价商品",
                "rules": ["指定商品限时特价", "限量供应", "每人限购一件"],
                "prizes": ["1 元秒杀", "9.9 元包邮", "买一送一"]
            }
        }
        
        config = configs.get(interaction_type, configs[InteractionType.LUCKY_DRAW])
        
        return ScriptSegment(
            segment_id=f"seg_interaction_{interaction_type.value}_{datetime.now().strftime('%H%M%S')}",
            segment_type=ScriptSectionType.INTERACTION,
            start_time=start_time,
            end_time=end_time,
            duration_minutes=duration,
            title=config["name"],
            description=config["description"],
            script_content=f"【互动环节】{config['name']}\n规则：{', '.join(config['rules'])}\n奖品：{', '.join(config['prizes'])}",
            notes=["提前准备好奖品", "确认抽奖工具正常", "助理记录中奖名单"],
            interactions=[InteractionSlot(
                type=interaction_type,
                name=config["name"],
                start_time=start_time,
                duration_minutes=duration,
                description=config["description"],
                rules=config["rules"],
                prizes=config["prizes"]
            )]
        )
    
    def _generate_promotion_script(self, start_minutes: int, duration: int) -> ScriptSegment:
        start_time = self._format_time(start_minutes)
        end_time = self._format_time(start_minutes + duration)
        
        return ScriptSegment(
            segment_id=f"seg_promotion_{datetime.now().strftime('%H%M%S')}",
            segment_type=ScriptSectionType.PROMOTION,
            start_time=start_time,
            end_time=end_time,
            duration_minutes=duration,
            title="限时促销",
            description="集中促销、组合优惠、满减活动",
            script_content="【促销活动】\n所有产品历史最低价！\n满 200 减 30，满 300 减 50！\n组合更优惠！",
            notes=["确认满减券已设置", "准备组合套餐链接", "设置倒计时工具"]
        )
    
    def _generate_break_script(self, start_minutes: int, duration: int) -> ScriptSegment:
        start_time = self._format_time(start_minutes)
        end_time = self._format_time(start_minutes + duration)
        
        return ScriptSegment(
            segment_id=f"seg_break_{datetime.now().strftime('%H%M%S')}",
            segment_type=ScriptSectionType.BREAK,
            start_time=start_time,
            end_time=end_time,
            duration_minutes=duration,
            title="休息过渡",
            description="短暂休息、背景音乐、预告下一轮",
            script_content="【休息】\n大家稍等一下，休息几分钟～\n可以去逛逛小黄车\n马上回来！",
            notes=["播放背景音乐", "助理继续互动", "主播喝水休息"]
        )
    
    def _generate_closing_script(self, start_minutes: int, duration: int, theme: str) -> ScriptSegment:
        start_time = self._format_time(start_minutes)
        end_time = self._format_time(start_minutes + duration)
        
        return ScriptSegment(
            segment_id=f"seg_closing_{datetime.now().strftime('%H%M%S')}",
            segment_type=ScriptSectionType.CLOSING,
            start_time=start_time,
            end_time=end_time,
            duration_minutes=duration,
            title="总结收尾",
            description="总结直播内容、感谢观众、预告下次直播",
            script_content=f"【结尾】\n今天的'{theme}'主题直播就要结束了！\n感谢所有陪伴的宝宝们！\n下次直播时间是 [时间]，不见不散！",
            notes=["统计今日销售数据", "准备下次直播预告", "确认下播时间"]
        )
    
    def _generate_emergency_plans(self) -> List[EmergencyPlan]:
        return [
            EmergencyPlan(
                scenario="直播间突然断网/断电",
                probability="low",
                impact="high",
                response_steps=["保持冷静", "粉丝群发布通知", "尽快恢复设备", "发放补偿优惠券"],
                backup_script="宝宝们稍等一下，技术小问题，马上回来！",
                responsible_person="主播 + 运营"
            ),
            EmergencyPlan(
                scenario="产品链接错误/价格设置错误",
                probability="medium",
                impact="high",
                response_steps=["立即下架错误链接", "向观众道歉", "快速修正后重新上架", "发放补偿优惠券"],
                backup_script="不好意思宝宝们，链接有点问题，已经修正了！",
                responsible_person="运营 + 客服"
            ),
            EmergencyPlan(
                scenario="黑粉/恶意评论",
                probability="medium",
                impact="medium",
                response_steps=["不要正面回应", "助理快速禁言", "主播转移话题", "必要时举报"],
                backup_script="我们继续看下一款产品...",
                responsible_person="助理 + 主播"
            ),
            EmergencyPlan(
                scenario="库存售罄/超卖",
                probability="medium",
                impact="medium",
                response_steps=["立即下架", "告知观众并道歉", "推荐类似产品", "开启预售通知"],
                backup_script="哇！太火爆了！已经卖完了！下一款更值得期待！",
                responsible_person="运营 + 主播"
            ),
            EmergencyPlan(
                scenario="主播状态不佳/忘词",
                probability="low",
                impact="medium",
                response_steps=["助理提词板提示", "插入互动环节", "播放产品视频过渡", "短暂休息"],
                backup_script="来，我们先抽个奖！",
                responsible_person="助理 + 主播"
            ),
            EmergencyPlan(
                scenario="产品质量问题被曝光",
                probability="low",
                impact="high",
                response_steps=["不要回避", "诚恳道歉", "说明售后政策", "下架相关产品"],
                backup_script="非常抱歉，我们一定会负责到底！请私信客服处理！",
                responsible_person="主播 + 客服 + 运营"
            )
        ]
    
    def generate_script(
        self,
        theme: str,
        duration: ScriptDuration,
        target_audience: str = "所有人",
        streamer_name: str = "主播",
        template_id: Optional[str] = None,
        selected_products: Optional[List[str]] = None
    ) -> LiveScript:
        if template_id and template_id in self.templates:
            template = self.templates[template_id]
        else:
            default_map = {
                ScriptDuration.ONE_HOUR: "fast_1h",
                ScriptDuration.TWO_HOURS: "standard_2h",
                ScriptDuration.THREE_HOURS: "standard_2h",
                ScriptDuration.FOUR_HOURS: "marathon_4h"
            }
            template = self.templates.get(default_map[duration], self.templates["standard_2h"])
        
        duration_minutes_map = {
            ScriptDuration.ONE_HOUR: 60,
            ScriptDuration.TWO_HOURS: 120,
            ScriptDuration.THREE_HOURS: 180,
            ScriptDuration.FOUR_HOURS: 240
        }
        total_minutes = duration_minutes_map[duration]
        
        if selected_products:
            products_to_use = [self.products[pid] for pid in selected_products if pid in self.products]
        else:
            products_to_use = list(self.products.values())
        
        if not products_to_use:
            products_to_use = list(self.products.values())
        
        segments = []
        all_products = []
        all_interactions = []
        current_minutes = 0
        
        structure = template.get("structure", [])
        product_index = 0
        
        for idx, section in enumerate(structure):
            section_type = ScriptSectionType(section["type"])
            section_duration = section["duration"]
            
            if section_type == ScriptSectionType.OPENING:
                segment = self._generate_opening_script(theme, section_duration)
                segments.append(segment)
                current_minutes += section_duration
            
            elif section_type == ScriptSectionType.PRODUCT_INTRO:
                if product_index < len(products_to_use):
                    product = products_to_use[product_index]
                else:
                    product = products_to_use[product_index % len(products_to_use)]
                segment = self._generate_product_intro_script(product, current_minutes, section_duration)
                segments.append(segment)
                all_products.extend(segment.products)
                product_index += 1
                current_minutes += section_duration
            
            elif section_type == ScriptSectionType.INTERACTION:
                interaction_types = list(InteractionType)
                interaction_type = interaction_types[idx % len(interaction_types)]
                segment = self._generate_interaction_script(interaction_type, current_minutes, section_duration)
                segments.append(segment)
                all_interactions.extend(segment.interactions)
                current_minutes += section_duration
            
            elif section_type == ScriptSectionType.PROMOTION:
                segment = self._generate_promotion_script(current_minutes, section_duration)
                segments.append(segment)
                current_minutes += section_duration
            
            elif section_type == ScriptSectionType.BREAK:
                segment = self._generate_break_script(current_minutes, section_duration)
                segments.append(segment)
                current_minutes += section_duration
            
            elif section_type == ScriptSectionType.CLOSING:
                segment = self._generate_closing_script(current_minutes, section_duration, theme)
                segments.append(segment)
                current_minutes += section_duration
        
        emergency_plans = self._generate_emergency_plans()
        
        script_id = f"script_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        overall_flow = f"【{theme}】直播流程概览（{total_minutes}分钟）\n\n"
        for seg in segments:
            overall_flow += f"{seg.start_time} - {seg.title}（{seg.duration_minutes}分钟）\n"
        
        preparation_checklist = [
            "确认所有产品链接和库存正常",
            "设置优惠券和促销活动",
            "准备抽奖工具和奖品",
            "测试直播设备",
            "准备背景音乐和音效",
            "准备提词板",
            "确认助理和客服就位",
            "检查网络稳定性",
            "准备饮用水和润喉糖",
            "熟悉应急预案流程"
        ]
        
        live_script = LiveScript(
            script_id=script_id,
            title=f"{theme}直播剧本",
            duration=duration,
            generated_at=datetime.now(),
            theme=theme,
            target_audience=target_audience,
            streamer_name=streamer_name,
            segments=segments,
            products=all_products,
            interactions=all_interactions,
            emergency_plans=emergency_plans,
            overall_flow=overall_flow,
            preparation_checklist=preparation_checklist
        )
        
        self.scripts[script_id] = {
            "script_id": script_id,
            "title": live_script.title,
            "duration": duration.value,
            "generated_at": datetime.now().isoformat(),
            "theme": theme,
            "target_audience": target_audience,
            "streamer_name": streamer_name,
            "segments": [
                {
                    "segment_id": s.segment_id,
                    "segment_type": s.segment_type.value,
                    "start_time": s.start_time,
                    "end_time": s.end_time,
                    "duration_minutes": s.duration_minutes,
                    "title": s.title,
                    "description": s.description,
                    "script_content": s.script_content,
                    "notes": s.notes
                }
                for s in segments
            ],
            "products": [asdict(p) for p in all_products],
            "interactions": [
                {
                    "type": i.type.value,
                    "name": i.name,
                    "start_time": i.start_time,
                    "duration_minutes": i.duration_minutes,
                    "description": i.description,
                    "rules": i.rules,
                    "prizes": i.prizes
                }
                for i in all_interactions
            ],
            "emergency_plans": [asdict(ep) for ep in emergency_plans],
            "overall_flow": overall_flow,
            "preparation_checklist": preparation_checklist
        }
        self._save_scripts()
        
        return live_script
    
    def get_script(self, script_id: str) -> Optional[Dict]:
        return self.scripts.get(script_id)
    
    def list_scripts(self, limit: int = 20, offset: int = 0) -> List[Dict]:
        scripts = list(self.scripts.values())
        scripts.sort(key=lambda x: x["generated_at"], reverse=True)
        return scripts[offset:offset + limit]
    
    def delete_script(self, script_id: str) -> bool:
        if script_id in self.scripts:
            del self.scripts[script_id]
            self._save_scripts()
            return True
        return False
    
    def export_script(self, script_id: str, format: str = "json", output_path: Optional[str] = None) -> str:
        script = self.scripts.get(script_id)
        if not script:
            raise ValueError(f"剧本不存在：{script_id}")
        
        if output_path:
            output = Path(output_path)
        else:
            output = self.data_dir / f"{script_id}.{format}"
        
        if format == "json":
            with open(output, "w", encoding="utf-8") as f:
                json.dump(script, f, ensure_ascii=False, indent=2)
        elif format == "txt":
            with open(output, "w", encoding="utf-8") as f:
                f.write(f"{'='*60}\n")
                f.write(f"{script['title']}\n")
                f.write(f"{'='*60}\n\n")
                f.write(f"主题：{script['theme']}\n")
                f.write(f"时长：{script['duration']}\n\n")
                f.write(f"{script['overall_flow']}\n\n")
                f.write(f"{'='*60}\n详细剧本\n{'='*60}\n\n")
                for seg in script["segments"]:
                    f.write(f"[{seg['start_time']}] {seg['title']}（{seg['duration_minutes']}分钟）\n")
                    f.write(f"{seg['script_content']}\n\n")
        elif format in ["pdf", "doc", "docx", "word"]:
            txt_output = output.with_suffix(".txt")
            self.export_script(script_id, "txt", str(txt_output))
            return str(txt_output)
        
        return str(output)
    
    def get_templates(self) -> List[Dict]:
        return [
            {
                "template_id": tid,
                "name": t["name"],
                "duration": t["duration"],
                "structure": t["structure"],
                "is_default": t.get("is_default", False)
            }
            for tid, t in self.templates.items()
        ]
    
    def get_products(self, category: Optional[str] = None) -> List[Dict]:
        products = list(self.products.values())
        if category:
            products = [p for p in products if p.get("category") == category]
        return products
    
    def add_product(self, product: Dict) -> str:
        product_id = f"prod_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        product["product_id"] = product_id
        self.products[product_id] = product
        self._save_products()
        return product_id
    
    def get_statistics(self) -> Dict:
        return {
            "total_scripts": len(self.scripts),
            "total_templates": len(self.templates),
            "total_products": len(self.products),
            "scripts_by_duration": {
                duration.value: sum(1 for s in self.scripts.values() if s["duration"] == duration.value)
                for duration in ScriptDuration
            }
        }


_service_instance: Optional[ScriptPlannerService] = None


def get_service() -> ScriptPlannerService:
    global _service_instance
    if _service_instance is None:
        _service_instance = ScriptPlannerService()
    return _service_instance


def generate_1h_script(theme: str, **kwargs) -> LiveScript:
    return get_service().generate_script(theme, ScriptDuration.ONE_HOUR, **kwargs)


def generate_2h_script(theme: str, **kwargs) -> LiveScript:
    return get_service().generate_script(theme, ScriptDuration.TWO_HOURS, **kwargs)


def generate_3h_script(theme: str, **kwargs) -> LiveScript:
    return get_service().generate_script(theme, ScriptDuration.THREE_HOURS, **kwargs)


def generate_4h_script(theme: str, **kwargs) -> LiveScript:
    return get_service().generate_script(theme, ScriptDuration.FOUR_HOURS, **kwargs)
