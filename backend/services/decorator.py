"""
直播间装修管理服务
提供背景模板、贴纸装饰、文字编辑、方案保存和应用功能
"""

from datetime import datetime
from typing import Dict, List, Optional
import uuid
import json


class DecoratorElement:
    """装修元素基类"""
    
    def __init__(self, element_type: str, name: str):
        self.id = str(uuid.uuid4())
        self.element_type = element_type  # background, sticker, text, image
        self.name = name
        self.x = 0
        self.y = 0
        self.width = 100
        self.height = 100
        self.rotation = 0
        self.opacity = 1.0
        self.z_index = 0
        self.visible = True
        self.locked = False
    
    def to_dict(self) -> Dict:
        """转换为字典格式"""
        return {
            "id": self.id,
            "element_type": self.element_type,
            "name": self.name,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "rotation": self.rotation,
            "opacity": self.opacity,
            "z_index": self.z_index,
            "visible": self.visible,
            "locked": self.locked
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'DecoratorElement':
        """从字典创建实例"""
        element = cls(data.get('element_type', 'sticker'), data.get('name', '元素'))
        element.id = data.get('id', str(uuid.uuid4()))
        element.x = data.get('x', 0)
        element.y = data.get('y', 0)
        element.width = data.get('width', 100)
        element.height = data.get('height', 100)
        element.rotation = data.get('rotation', 0)
        element.opacity = data.get('opacity', 1.0)
        element.z_index = data.get('z_index', 0)
        element.visible = data.get('visible', True)
        element.locked = data.get('locked', False)
        return element


class BackgroundElement(DecoratorElement):
    """背景元素"""
    
    def __init__(self, name: str, image_url: str = "", color: str = "#FFFFFF"):
        super().__init__("background", name)
        self.image_url = image_url
        self.color = color
        self.fit_mode = "cover"  # cover, contain, fill, stretch
    
    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            "image_url": self.image_url,
            "color": self.color,
            "fit_mode": self.fit_mode
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'BackgroundElement':
        element = cls(
            name=data.get('name', '背景'),
            image_url=data.get('image_url', ''),
            color=data.get('color', '#FFFFFF')
        )
        element.id = data.get('id', str(uuid.uuid4()))
        element.x = data.get('x', 0)
        element.y = data.get('y', 0)
        element.width = data.get('width', 1920)
        element.height = data.get('height', 1080)
        element.fit_mode = data.get('fit_mode', 'cover')
        return element


class StickerElement(DecoratorElement):
    """贴纸元素"""
    
    def __init__(self, name: str, image_url: str = "", category: str = "default"):
        super().__init__("sticker", name)
        self.image_url = image_url
        self.category = category  # default, festival, promotion, decoration, emoji
    
    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            "image_url": self.image_url,
            "category": self.category
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'StickerElement':
        element = cls(
            name=data.get('name', '贴纸'),
            image_url=data.get('image_url', ''),
            category=data.get('category', 'default')
        )
        return element


class TextElement(DecoratorElement):
    """文字元素"""
    
    def __init__(self, name: str, content: str = "文字"):
        super().__init__("text", name)
        self.content = content
        self.font_family = "Arial"
        self.font_size = 32
        self.font_weight = "normal"  # normal, bold, bolder
        self.font_style = "normal"  # normal, italic
        self.color = "#000000"
        self.background_color = "transparent"
        self.text_align = "left"  # left, center, right
        self.line_height = 1.5
        self.letter_spacing = 0
    
    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            "content": self.content,
            "font_family": self.font_family,
            "font_size": self.font_size,
            "font_weight": self.font_weight,
            "font_style": self.font_style,
            "color": self.color,
            "background_color": self.background_color,
            "text_align": self.text_align,
            "line_height": self.line_height,
            "letter_spacing": self.letter_spacing
        })
        return data
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TextElement':
        element = cls(
            name=data.get('name', '文字'),
            content=data.get('content', '文字')
        )
        element.id = data.get('id', str(uuid.uuid4()))
        element.x = data.get('x', 0)
        element.y = data.get('y', 0)
        element.width = data.get('width', 200)
        element.height = data.get('height', 50)
        element.rotation = data.get('rotation', 0)
        element.opacity = data.get('opacity', 1.0)
        element.z_index = data.get('z_index', 0)
        element.font_family = data.get('font_family', 'Arial')
        element.font_size = data.get('font_size', 32)
        element.font_weight = data.get('font_weight', 'normal')
        element.font_style = data.get('font_style', 'normal')
        element.color = data.get('color', '#000000')
        element.background_color = data.get('background_color', 'transparent')
        element.text_align = data.get('text_align', 'left')
        element.line_height = data.get('line_height', 1.5)
        element.letter_spacing = data.get('letter_spacing', 0)
        return element


class DecoratorPreset:
    """装修预设模板"""
    
    def __init__(self, name: str, description: str, category: str = "default"):
        self.id = str(uuid.uuid4())
        self.name = name
        self.description = description
        self.category = category  # default, festival, promotion, minimal, gaming
        self.thumbnail_url = ""
        self.elements: List[DecoratorElement] = []
        self.created_at = datetime.now()
        self.usage_count = 0
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "thumbnail_url": self.thumbnail_url,
            "elements": [e.to_dict() for e in self.elements],
            "created_at": self.created_at.isoformat(),
            "usage_count": self.usage_count
        }


class DecoratorScheme:
    """装修方案"""
    
    def __init__(self, name: str, room_id: str = ""):
        self.id = str(uuid.uuid4())
        self.name = name
        self.room_id = room_id
        self.elements: List[DecoratorElement] = []
        self.background: Optional[BackgroundElement] = None
        self.created_at = datetime.now()
        self.updated_at = datetime.now()
        self.is_active = False
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "name": self.name,
            "room_id": self.room_id,
            "background": self.background.to_dict() if self.background else None,
            "elements": [e.to_dict() for e in self.elements],
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "is_active": self.is_active
        }
    
    def add_element(self, element: DecoratorElement):
        """添加元素"""
        self.elements.append(element)
        self.updated_at = datetime.now()
    
    def remove_element(self, element_id: str) -> bool:
        """移除元素"""
        for i, elem in enumerate(self.elements):
            if elem.id == element_id:
                self.elements.pop(i)
                self.updated_at = datetime.now()
                return True
        return False
    
    def update_element(self, element_id: str, updates: Dict) -> bool:
        """更新元素属性"""
        for elem in self.elements:
            if elem.id == element_id:
                for key, value in updates.items():
                    if hasattr(elem, key):
                        setattr(elem, key, value)
                self.updated_at = datetime.now()
                return True
        return False


class DecoratorService:
    """装修服务类"""
    
    def __init__(self):
        self.schemes: Dict[str, DecoratorScheme] = {}
        self.presets: List[DecoratorPreset] = []
        self.sticker_library: List[Dict] = []
        self._init_default_presets()
        self._init_sticker_library()
    
    def _init_default_presets(self):
        """初始化默认装修预设"""
        # 预设 1: 简约风格
        preset1 = DecoratorPreset("简约风格", "干净简洁的直播间背景", "minimal")
        text1 = TextElement("标题", "我的直播间")
        text1.font_family = "Arial"
        text1.font_size = 48
        text1.font_weight = "bold"
        text1.color = "#333333"
        text1.x = 50
        text1.y = 50
        preset1.elements = [
            BackgroundElement("纯色背景", color="#F5F5F5"),
            text1
        ]
        
        # 预设 2: 节日庆典
        preset2 = DecoratorPreset("节日庆典", "喜庆热闹的节日装饰", "festival")
        preset2.elements = [
            BackgroundElement("红色渐变背景", color="#FF6B6B"),
            StickerElement("灯笼", category="festival"),
            StickerElement("彩带", category="festival")
        ]
        
        # 预设 3: 促销活动
        preset3 = DecoratorPreset("促销活动", "吸引眼球的促销装饰", "promotion")
        text3 = TextElement("促销标题", "限时特价！")
        text3.font_family = "Arial"
        text3.font_size = 56
        text3.font_weight = "bold"
        text3.color = "#FF0000"
        preset3.elements = [
            BackgroundElement("促销背景", color="#FFD93D"),
            text3,
            StickerElement("折扣标签", category="promotion")
        ]
        
        # 预设 4: 游戏直播
        preset4 = DecoratorPreset("游戏直播", "酷炫游戏风格", "gaming")
        text4 = TextElement("主播名", "GAME MASTER")
        text4.font_family = "Arial"
        text4.font_size = 42
        text4.font_weight = "bold"
        text4.color = "#00D4FF"
        preset4.elements = [
            BackgroundElement("深色背景", color="#1A1A2E"),
            text4,
            StickerElement("游戏手柄", category="gaming")
        ]
        
        # 预设 5: 默认风格
        preset5 = DecoratorPreset("默认风格", "通用直播间装饰", "default")
        preset5.elements = [
            BackgroundElement("默认背景", color="#FFFFFF")
        ]
        
        self.presets = [preset1, preset2, preset3, preset4, preset5]
    
    def _init_sticker_library(self):
        """初始化贴纸库"""
        self.sticker_library = [
            # 节日类
            {"id": "sticker_festival_001", "name": "红灯笼", "category": "festival", "url": "/assets/stickers/festival/lantern.png", "tags": ["节日", "灯笼", "喜庆"]},
            {"id": "sticker_festival_002", "name": "彩带", "category": "festival", "url": "/assets/stickers/festival/confetti.png", "tags": ["节日", "彩带", "庆祝"]},
            {"id": "sticker_festival_003", "name": "礼花", "category": "festival", "url": "/assets/stickers/festival/fireworks.png", "tags": ["节日", "礼花", "庆祝"]},
            {"id": "sticker_festival_004", "name": "福字", "category": "festival", "url": "/assets/stickers/festival/fortune.png", "tags": ["节日", "福字", "春节"]},
            
            # 促销类
            {"id": "sticker_promo_001", "name": "折扣标签", "category": "promotion", "url": "/assets/stickers/promo/discount-tag.png", "tags": ["促销", "折扣", "标签"]},
            {"id": "sticker_promo_002", "name": "热卖", "category": "promotion", "url": "/assets/stickers/promo/hot-sale.png", "tags": ["促销", "热卖", "推荐"]},
            {"id": "sticker_promo_003", "name": "新品", "category": "promotion", "url": "/assets/stickers/promo/new.png", "tags": ["促销", "新品", "上市"]},
            {"id": "sticker_promo_004", "name": "限时", "category": "promotion", "url": "/assets/stickers/promo/limited-time.png", "tags": ["促销", "限时", "抢购"]},
            
            # 装饰类
            {"id": "sticker_deco_001", "name": "星星", "category": "decoration", "url": "/assets/stickers/deco/star.png", "tags": ["装饰", "星星", "闪亮"]},
            {"id": "sticker_deco_002", "name": "爱心", "category": "decoration", "url": "/assets/stickers/deco/heart.png", "tags": ["装饰", "爱心", "喜欢"]},
            {"id": "sticker_deco_003", "name": "花朵", "category": "decoration", "url": "/assets/stickers/deco/flower.png", "tags": ["装饰", "花朵", "美丽"]},
            {"id": "sticker_deco_004", "name": "边框", "category": "decoration", "url": "/assets/stickers/deco/frame.png", "tags": ["装饰", "边框", "相框"]},
            
            # 表情类
            {"id": "sticker_emoji_001", "name": "笑脸", "category": "emoji", "url": "/assets/stickers/emoji/smile.png", "tags": ["表情", "笑脸", "开心"]},
            {"id": "sticker_emoji_002", "name": "点赞", "category": "emoji", "url": "/assets/stickers/emoji/thumbs-up.png", "tags": ["表情", "点赞", "支持"]},
            {"id": "sticker_emoji_003", "name": "爱心眼", "category": "emoji", "url": "/assets/stickers/emoji/heart-eyes.png", "tags": ["表情", "喜欢", "爱"]},
            
            # 游戏类
            {"id": "sticker_game_001", "name": "游戏手柄", "category": "gaming", "url": "/assets/stickers/gaming/controller.png", "tags": ["游戏", "手柄", "电竞"]},
            {"id": "sticker_game_002", "name": "皇冠", "category": "gaming", "url": "/assets/stickers/gaming/crown.png", "tags": ["游戏", "皇冠", "王者"]},
            {"id": "sticker_game_003", "name": "奖杯", "category": "gaming", "url": "/assets/stickers/gaming/trophy.png", "tags": ["游戏", "奖杯", "胜利"]}
        ]
    
    def create_scheme(self, name: str, room_id: str = "") -> DecoratorScheme:
        """创建装修方案"""
        scheme = DecoratorScheme(name, room_id)
        self.schemes[scheme.id] = scheme
        return scheme
    
    def get_scheme(self, scheme_id: str) -> Optional[DecoratorScheme]:
        """获取装修方案"""
        return self.schemes.get(scheme_id)
    
    def list_schemes(self, room_id: str = "") -> List[DecoratorScheme]:
        """获取装修方案列表"""
        result = list(self.schemes.values())
        if room_id:
            result = [s for s in result if s.room_id == room_id]
        result.sort(key=lambda s: s.updated_at, reverse=True)
        return result
    
    def update_scheme(self, scheme_id: str, updates: Dict) -> bool:
        """更新装修方案"""
        scheme = self.schemes.get(scheme_id)
        if not scheme:
            return False
        
        if 'name' in updates:
            scheme.name = updates['name']
        if 'elements' in updates:
            scheme.elements = [DecoratorElement.from_dict(e) if isinstance(e, dict) else e for e in updates['elements']]
        if 'background' in updates:
            scheme.background = BackgroundElement.from_dict(updates['background']) if updates['background'] else None
        
        scheme.updated_at = datetime.now()
        return True
    
    def delete_scheme(self, scheme_id: str) -> bool:
        """删除装修方案"""
        if scheme_id in self.schemes:
            del self.schemes[scheme_id]
            return True
        return False
    
    def apply_scheme(self, scheme_id: str) -> bool:
        """应用装修方案（设置为活跃）"""
        # 先将所有方案设为非活跃
        for scheme in self.schemes.values():
            scheme.is_active = False
        
        # 设置指定方案为活跃
        scheme = self.schemes.get(scheme_id)
        if scheme:
            scheme.is_active = True
            return True
        return False
    
    def get_active_scheme(self) -> Optional[DecoratorScheme]:
        """获取当前活跃的装修方案"""
        for scheme in self.schemes.values():
            if scheme.is_active:
                return scheme
        return None
    
    def get_presets(self, category: str = "") -> List[DecoratorPreset]:
        """获取装修预设列表"""
        if category:
            return [p for p in self.presets if p.category == category]
        return self.presets
    
    def apply_preset(self, preset_id: str, scheme_id: str) -> bool:
        """应用预设到方案"""
        preset = next((p for p in self.presets if p.id == preset_id), None)
        scheme = self.schemes.get(scheme_id)
        
        if not preset or not scheme:
            return False
        
        # 复制预设的元素到方案
        scheme.elements = []
        scheme.background = None
        
        for elem_data in preset.elements:
            if isinstance(elem_data, BackgroundElement):
                scheme.background = elem_data
            else:
                scheme.elements.append(elem_data)
        
        preset.usage_count += 1
        scheme.updated_at = datetime.now()
        return True
    
    def get_sticker_library(self, category: str = "") -> List[Dict]:
        """获取贴纸库"""
        if category:
            return [s for s in self.sticker_library if s['category'] == category]
        return self.sticker_library
    
    def search_stickers(self, keyword: str) -> List[Dict]:
        """搜索贴纸"""
        keyword_lower = keyword.lower()
        return [
            s for s in self.sticker_library
            if keyword_lower in s['name'].lower() or any(keyword_lower in tag.lower() for tag in s.get('tags', []))
        ]
    
    def export_scheme(self, scheme_id: str) -> Optional[str]:
        """导出装修方案为 JSON"""
        scheme = self.schemes.get(scheme_id)
        if not scheme:
            return None
        return json.dumps(scheme.to_dict(), ensure_ascii=False, indent=2)
    
    def import_scheme(self, json_data: str, name: str = "") -> Optional[DecoratorScheme]:
        """从 JSON 导入装修方案"""
        try:
            data = json.loads(json_data)
            scheme = DecoratorScheme(name or data.get('name', '导入的方案'), data.get('room_id', ''))
            
            if data.get('background'):
                scheme.background = BackgroundElement.from_dict(data['background'])
            
            for elem_data in data.get('elements', []):
                elem_type = elem_data.get('element_type', 'sticker')
                if elem_type == 'text':
                    elem = TextElement.from_dict(elem_data)
                elif elem_type == 'sticker':
                    elem = StickerElement.from_dict(elem_data)
                else:
                    elem = DecoratorElement.from_dict(elem_data)
                scheme.elements.append(elem)
            
            self.schemes[scheme.id] = scheme
            return scheme
        except Exception as e:
            print(f"导入方案失败：{e}")
            return None


# 全局服务实例
decorator_service = DecoratorService()
