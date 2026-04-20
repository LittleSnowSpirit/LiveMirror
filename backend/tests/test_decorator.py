"""
直播间装修功能测试
测试装修服务的核心功能
"""

import pytest
import json
from backend.services.decorator import (
    decorator_service,
    BackgroundElement,
    StickerElement,
    TextElement,
    DecoratorScheme
)


class TestDecoratorService:
    """装修服务测试类"""

    def setup_method(self):
        """每个测试前的设置"""
        # 清理现有方案
        decorator_service.schemes = {}
        # 重新初始化预设和贴纸库
        decorator_service._init_default_presets()
        decorator_service._init_sticker_library()

    # ==================== 方案管理测试 ====================

    def test_create_scheme(self):
        """测试创建装修方案"""
        scheme = decorator_service.create_scheme("测试方案", "room_001")
        
        assert scheme is not None
        assert scheme.name == "测试方案"
        assert scheme.room_id == "room_001"
        assert scheme.id is not None
        assert len(decorator_service.schemes) == 1

    def test_get_scheme(self):
        """测试获取装修方案"""
        created = decorator_service.create_scheme("测试方案", "room_001")
        retrieved = decorator_service.get_scheme(created.id)
        
        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == "测试方案"

    def test_list_schemes(self):
        """测试获取方案列表"""
        decorator_service.create_scheme("方案 1", "room_001")
        decorator_service.create_scheme("方案 2", "room_001")
        decorator_service.create_scheme("方案 3", "room_002")
        
        # 获取所有方案
        all_schemes = decorator_service.list_schemes()
        assert len(all_schemes) == 3
        
        # 按房间筛选
        room1_schemes = decorator_service.list_schemes(room_id="room_001")
        assert len(room1_schemes) == 2

    def test_update_scheme(self):
        """测试更新装修方案"""
        scheme = decorator_service.create_scheme("原始方案", "room_001")
        
        # 更新名称
        success = decorator_service.update_scheme(scheme.id, {"name": "新方案名称"})
        assert success is True
        
        updated = decorator_service.get_scheme(scheme.id)
        assert updated.name == "新方案名称"

    def test_delete_scheme(self):
        """测试删除装修方案"""
        scheme = decorator_service.create_scheme("待删除方案", "room_001")
        scheme_id = scheme.id
        
        # 删除方案
        success = decorator_service.delete_scheme(scheme_id)
        assert success is True
        assert len(decorator_service.schemes) == 0
        
        # 验证已删除
        retrieved = decorator_service.get_scheme(scheme_id)
        assert retrieved is None

    # ==================== 方案应用测试 ====================

    def test_apply_scheme(self):
        """测试应用装修方案"""
        scheme1 = decorator_service.create_scheme("方案 1", "room_001")
        scheme2 = decorator_service.create_scheme("方案 2", "room_001")
        
        # 应用方案 1
        success = decorator_service.apply_scheme(scheme1.id)
        assert success is True
        
        # 验证方案 1 为活跃状态
        active = decorator_service.get_active_scheme()
        assert active is not None
        assert active.id == scheme1.id
        assert active.is_active is True
        
        # 验证方案 2 为非活跃状态
        scheme2_retrieved = decorator_service.get_scheme(scheme2.id)
        assert scheme2_retrieved.is_active is False

    def test_get_active_scheme(self):
        """测试获取当前活跃方案"""
        # 初始无活跃方案
        active = decorator_service.get_active_scheme()
        assert active is None
        
        # 创建并应用方案
        scheme = decorator_service.create_scheme("活跃方案", "room_001")
        decorator_service.apply_scheme(scheme.id)
        
        # 获取活跃方案
        active = decorator_service.get_active_scheme()
        assert active is not None
        assert active.id == scheme.id

    # ==================== 预设模板测试 ====================

    def test_get_presets(self):
        """测试获取装修预设"""
        presets = decorator_service.get_presets()
        assert len(presets) > 0
        
        # 验证预设有必要的属性
        preset = presets[0]
        assert preset.id is not None
        assert preset.name is not None
        assert preset.category is not None

    def test_get_presets_by_category(self):
        """测试按分类获取预设"""
        festival_presets = decorator_service.get_presets(category="festival")
        assert len(festival_presets) > 0
        
        for preset in festival_presets:
            assert preset.category == "festival"

    def test_apply_preset(self):
        """测试应用预设到方案"""
        scheme = decorator_service.create_scheme("测试方案", "room_001")
        presets = decorator_service.get_presets()
        preset = presets[0]
        
        # 应用预设
        success = decorator_service.apply_preset(preset.id, scheme.id)
        assert success is True
        
        # 验证方案元素已更新
        updated_scheme = decorator_service.get_scheme(scheme.id)
        assert len(updated_scheme.elements) > 0
        assert preset.usage_count > 0

    # ==================== 贴纸库测试 ====================

    def test_get_sticker_library(self):
        """测试获取贴纸库"""
        stickers = decorator_service.get_sticker_library()
        assert len(stickers) > 0
        
        # 验证贴纸有必要的属性
        sticker = stickers[0]
        assert 'id' in sticker
        assert 'name' in sticker
        assert 'category' in sticker
        assert 'url' in sticker

    def test_get_stickers_by_category(self):
        """测试按分类获取贴纸"""
        festival_stickers = decorator_service.get_sticker_library(category="festival")
        assert len(festival_stickers) > 0
        
        for sticker in festival_stickers:
            assert sticker['category'] == "festival"

    def test_search_stickers(self):
        """测试搜索贴纸"""
        # 搜索关键词
        results = decorator_service.search_stickers("灯笼")
        assert len(results) > 0
        
        # 验证搜索结果包含关键词
        for sticker in results:
            has_keyword = (
                "灯笼" in sticker['name'] or
                any("灯笼" in tag for tag in sticker.get('tags', []))
            )
            assert has_keyword

    # ==================== 元素操作测试 ====================

    def test_add_element_to_scheme(self):
        """测试向方案添加元素"""
        scheme = decorator_service.create_scheme("测试方案", "room_001")
        
        # 添加贴纸元素
        sticker = StickerElement("测试贴纸", "/test/sticker.png", "default")
        sticker.x = 100
        sticker.y = 100
        scheme.add_element(sticker)
        
        assert len(scheme.elements) == 1
        assert scheme.elements[0].name == "测试贴纸"
        assert scheme.elements[0].x == 100
        assert scheme.elements[0].y == 100

    def test_remove_element_from_scheme(self):
        """测试从方案移除元素"""
        scheme = decorator_service.create_scheme("测试方案", "room_001")
        
        # 添加元素
        sticker = StickerElement("待删除贴纸", "/test/sticker.png", "default")
        scheme.add_element(sticker)
        element_id = sticker.id
        
        assert len(scheme.elements) == 1
        
        # 删除元素
        success = scheme.remove_element(element_id)
        assert success is True
        assert len(scheme.elements) == 0

    def test_update_element(self):
        """测试更新元素属性"""
        scheme = decorator_service.create_scheme("测试方案", "room_001")
        
        # 添加文字元素
        text = TextElement("测试文字", "原始内容")
        text.x = 50
        text.y = 50
        scheme.add_element(text)
        element_id = text.id
        
        # 更新属性
        success = scheme.update_element(element_id, {
            'x': 100,
            'y': 100,
            'content': '新内容'
        })
        assert success is True
        
        # 验证更新
        updated_element = None
        for elem in scheme.elements:
            if elem.id == element_id:
                updated_element = elem
                break
        
        assert updated_element is not None
        assert updated_element.x == 100
        assert updated_element.y == 100
        assert updated_element.content == '新内容'

    # ==================== 元素类型测试 ====================

    def test_background_element(self):
        """测试背景元素"""
        bg = BackgroundElement("测试背景", "/test/bg.png", "#FF0000")
        
        assert bg.element_type == "background"
        assert bg.image_url == "/test/bg.png"
        assert bg.color == "#FF0000"
        assert bg.fit_mode == "cover"
        
        # 测试转换为字典
        bg_dict = bg.to_dict()
        assert bg_dict['element_type'] == "background"
        assert bg_dict['image_url'] == "/test/bg.png"
        assert bg_dict['color'] == "#FF0000"

    def test_sticker_element(self):
        """测试贴纸元素"""
        sticker = StickerElement("测试贴纸", "/test/sticker.png", "festival")
        
        assert sticker.element_type == "sticker"
        assert sticker.image_url == "/test/sticker.png"
        assert sticker.category == "festival"
        
        # 测试转换为字典
        sticker_dict = sticker.to_dict()
        assert sticker_dict['element_type'] == "sticker"
        assert sticker_dict['category'] == "festival"

    def test_text_element(self):
        """测试文字元素"""
        text = TextElement("测试文字", "文字内容")
        text.font_size = 36
        text.color = "#00FF00"
        text.font_weight = "bold"
        
        assert text.element_type == "text"
        assert text.content == "文字内容"
        assert text.font_size == 36
        assert text.color == "#00FF00"
        assert text.font_weight == "bold"
        
        # 测试转换为字典
        text_dict = text.to_dict()
        assert text_dict['element_type'] == "text"
        assert text_dict['content'] == "文字内容"
        assert text_dict['font_size'] == 36

    # ==================== 导入导出测试 ====================

    def test_export_scheme(self):
        """测试导出装修方案"""
        scheme = decorator_service.create_scheme("导出测试", "room_001")
        
        # 添加元素
        text = TextElement("测试文字", "内容")
        scheme.add_element(text)
        
        # 导出
        json_str = decorator_service.export_scheme(scheme.id)
        assert json_str is not None
        
        # 验证 JSON 格式
        data = json.loads(json_str)
        assert data['name'] == "导出测试"
        assert data['room_id'] == "room_001"
        assert len(data['elements']) == 1

    def test_import_scheme(self):
        """测试导入装修方案"""
        # 准备 JSON 数据
        scheme_data = {
            "name": "导入的方案",
            "room_id": "room_002",
            "background": {
                "element_type": "background",
                "name": "背景",
                "color": "#123456",
                "fit_mode": "cover"
            },
            "elements": [
                {
                    "element_type": "text",
                    "name": "文字",
                    "content": "测试内容",
                    "x": 100,
                    "y": 100,
                    "width": 200,
                    "height": 50,
                    "font_size": 32,
                    "color": "#FFFFFF"
                }
            ]
        }
        
        json_str = json.dumps(scheme_data, ensure_ascii=False)
        
        # 导入
        imported_scheme = decorator_service.import_scheme(json_str)
        assert imported_scheme is not None
        assert imported_scheme.name == "导入的方案"
        assert imported_scheme.room_id == "room_002"
        assert len(imported_scheme.elements) == 1
        assert imported_scheme.background is not None
        assert imported_scheme.background.color == "#123456"

    # ==================== 实时预览测试 ====================

    def test_scheme_preview_data(self):
        """测试方案预览数据生成"""
        scheme = decorator_service.create_scheme("预览测试", "room_001")
        
        # 设置背景
        bg = BackgroundElement("背景", "", "#ABCDEF")
        scheme.background = bg
        
        # 添加多个元素
        for i in range(5):
            text = TextElement(f"文字{i}", f"内容{i}")
            text.x = i * 50
            text.y = i * 50
            scheme.add_element(text)
        
        # 验证预览数据
        scheme_dict = scheme.to_dict()
        assert scheme_dict['background'] is not None
        assert scheme_dict['background']['color'] == "#ABCDEF"
        assert len(scheme_dict['elements']) == 5
        
        # 验证元素位置
        for i, elem in enumerate(scheme_dict['elements']):
            assert elem['x'] == i * 50
            assert elem['y'] == i * 50


class TestDecoratorElements:
    """装修元素测试类"""

    def test_element_base_properties(self):
        """测试元素基础属性"""
        from backend.services.decorator import DecoratorElement
        
        elem = DecoratorElement("sticker", "测试元素")
        
        assert elem.id is not None
        assert elem.element_type == "sticker"
        assert elem.name == "测试元素"
        assert elem.x == 0
        assert elem.y == 0
        assert elem.width == 100
        assert elem.height == 100
        assert elem.rotation == 0
        assert elem.opacity == 1.0
        assert elem.visible is True
        assert elem.locked is False

    def test_element_from_dict(self):
        """测试从字典创建元素"""
        from backend.services.decorator import TextElement
        
        data = {
            "element_type": "text",
            "name": "测试文字",
            "content": "内容",
            "x": 50,
            "y": 50,
            "width": 150,
            "height": 40,
            "font_size": 24,
            "color": "#FF0000"
        }
        
        elem = TextElement.from_dict(data)
        
        assert elem.name == "测试文字"
        assert elem.content == "内容"
        assert elem.x == 50
        assert elem.y == 50
        assert elem.font_size == 24
        assert elem.color == "#FF0000"

    def test_element_z_index(self):
        """测试元素层级"""
        scheme = decorator_service.create_scheme("层级测试", "room_001")
        
        # 添加不同层级的元素
        for i in range(3):
            text = TextElement(f"文字{i}", f"内容{i}")
            text.z_index = i
            scheme.add_element(text)
        
        # 验证排序
        sorted_elements = sorted(scheme.elements, key=lambda e: e.z_index)
        assert sorted_elements[0].z_index == 0
        assert sorted_elements[1].z_index == 1
        assert sorted_elements[2].z_index == 2


# ==================== 运行测试 ====================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
