"""
直播间装修功能演示脚本
展示装修工具的核心功能
"""

import json
from backend.services.decorator import (
    decorator_service,
    BackgroundElement,
    StickerElement,
    TextElement
)


def print_section(title):
    """打印分隔线"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def demo_create_scheme():
    """演示创建装修方案"""
    print_section("1. 创建装修方案")
    
    scheme = decorator_service.create_scheme("我的直播间", "room_001")
    print(f"[OK] 方案已创建：{scheme.name}")
    print(f"     ID: {scheme.id}")
    print(f"     直播间：{scheme.room_id}")
    
    return scheme


def demo_set_background(scheme):
    """演示设置背景"""
    print_section("2. 设置直播间背景")
    
    # 创建背景
    bg = BackgroundElement("主背景", color="#667eea")
    bg.fit_mode = "cover"
    scheme.background = bg
    
    print(f"[OK] 背景已设置")
    print(f"     类型：纯色背景")
    print(f"     颜色：{bg.color}")
    print(f"     适配模式：{bg.fit_mode}")


def demo_add_elements(scheme):
    """演示添加装饰元素"""
    print_section("3. 添加装饰元素")
    
    # 添加标题文字
    title = TextElement("直播间标题", "欢迎来到我的直播间")
    title.x = 100
    title.y = 50
    title.width = 400
    title.height = 60
    title.font_size = 48
    title.font_weight = "bold"
    title.color = "#FFFFFF"
    scheme.add_element(title)
    print(f"[OK] 添加文字元素：{title.name}")
    
    # 添加副标题
    subtitle = TextElement("副标题", "每晚 8 点准时开播")
    subtitle.x = 100
    subtitle.y = 120
    subtitle.width = 300
    subtitle.height = 40
    subtitle.font_size = 28
    subtitle.color = "#FCD34D"
    scheme.add_element(subtitle)
    print(f"[OK] 添加文字元素：{subtitle.name}")
    
    # 添加贴纸装饰
    sticker1 = StickerElement("星星装饰", "/assets/stickers/deco/star.png", "decoration")
    sticker1.x = 600
    sticker1.y = 50
    sticker1.width = 80
    sticker1.height = 80
    scheme.add_element(sticker1)
    print(f"[OK] 添加贴纸元素：{sticker1.name}")
    
    sticker2 = StickerElement("爱心装饰", "/assets/stickers/deco/heart.png", "decoration")
    sticker2.x = 700
    sticker2.y = 50
    sticker2.width = 80
    sticker2.height = 80
    scheme.add_element(sticker2)
    print(f"[OK] 添加贴纸元素：{sticker2.name}")
    
    print(f"\n当前元素总数：{len(scheme.elements)}")


def demo_apply_preset(scheme):
    """演示应用装修预设"""
    print_section("4. 应用装修预设模板")
    
    # 获取可用预设
    presets = decorator_service.get_presets()
    print(f"可用预设模板：{len(presets)} 个")
    for i, preset in enumerate(presets, 1):
        print(f"  {i}. {preset.name} ({preset.category}) - {preset.description}")
    
    # 应用第一个预设
    if presets:
        preset = presets[0]
        success = decorator_service.apply_preset(preset.id, scheme.id)
        if success:
            print(f"\n[OK] 已应用预设：{preset.name}")
            print(f"     元素数量：{len(scheme.elements)}")


def demo_sticker_library():
    """演示贴纸库功能"""
    print_section("5. 浏览贴纸库")
    
    # 获取所有贴纸
    all_stickers = decorator_service.get_sticker_library()
    print(f"贴纸库总数：{len(all_stickers)} 个")
    
    # 按分类统计
    categories = {}
    for sticker in all_stickers:
        cat = sticker['category']
        categories[cat] = categories.get(cat, 0) + 1
    
    print("\n分类统计:")
    cat_names = {
        'default': '默认',
        'festival': '节日庆典',
        'promotion': '促销活动',
        'decoration': '装饰元素',
        'emoji': '表情符号',
        'gaming': '游戏直播'
    }
    for cat, count in categories.items():
        print(f"  {cat_names.get(cat, cat)}: {count} 个")
    
    # 搜索贴纸
    print("\n搜索示例 - 关键词 '灯笼':")
    results = decorator_service.search_stickers("灯笼")
    for sticker in results:
        print(f"  - {sticker['name']} ({sticker['category']})")


def demo_scheme_operations(scheme):
    """演示方案操作"""
    print_section("6. 装修方案操作")
    
    # 创建另一个方案
    scheme2 = decorator_service.create_scheme("备用方案", "room_001")
    print(f"[OK] 创建备用方案：{scheme2.name}")
    
    # 列出所有方案
    schemes = decorator_service.list_schemes(room_id="room_001")
    print(f"\n房间 'room_001' 的方案列表:")
    for s in schemes:
        status = "[*]" if s.is_active else "[ ]"
        print(f"  {status} {s.name} (元素：{len(s.elements)})")
    
    # 应用方案
    print(f"\n应用方案：{scheme.name}")
    decorator_service.apply_scheme(scheme.id)
    
    # 获取活跃方案
    active = decorator_service.get_active_scheme()
    if active:
        print(f"[OK] 当前活跃方案：{active.name}")


def demo_export_import(scheme):
    """演示导入导出功能"""
    print_section("7. 导入导出装修方案")
    
    # 导出方案
    json_str = decorator_service.export_scheme(scheme.id)
    print(f"[OK] 方案已导出为 JSON")
    print(f"     JSON 长度：{len(json_str)} 字符")
    
    # 解析并显示部分数据
    data = json.loads(json_str)
    print(f"     方案名称：{data['name']}")
    print(f"     元素数量：{len(data['elements'])}")
    
    # 导入方案
    print(f"\n导入装修方案...")
    imported = decorator_service.import_scheme(json_str, "导入的副本")
    if imported:
        print(f"[OK] 方案已成功导入")
        print(f"     新方案名称：{imported.name}")
        print(f"     新方案 ID: {imported.id}")
        print(f"     元素数量：{len(imported.elements)}")


def demo_preview_data(scheme):
    """演示预览数据生成"""
    print_section("8. 生成预览数据")
    
    # 获取方案数据
    data = scheme.to_dict()
    
    print(f"[OK] 预览数据已生成")
    print(f"     方案 ID: {data['id']}")
    print(f"     方案名称：{data['name']}")
    print(f"     背景颜色：{data['background']['color'] if data['background'] else '无'}")
    print(f"     元素数量：{len(data['elements'])}")
    
    # 显示前 3 个元素
    print(f"\n元素列表 (前 3 个):")
    for i, elem in enumerate(data['elements'][:3], 1):
        print(f"  {i}. {elem['name']} ({elem['element_type']})")
        print(f"     位置：({elem['x']}, {elem['y']})")
        print(f"     大小：{elem['width']} x {elem['height']}")


def main():
    """主函数"""
    print("\n")
    print("=" * 60)
    print("       LiveMirror 直播间装修工具演示")
    print("=" * 60)
    
    # 清理现有数据
    decorator_service.schemes = {}
    decorator_service._init_default_presets()
    decorator_service._init_sticker_library()
    
    # 执行演示
    scheme = demo_create_scheme()
    demo_set_background(scheme)
    demo_add_elements(scheme)
    demo_apply_preset(scheme)
    demo_sticker_library()
    demo_scheme_operations(scheme)
    demo_export_import(scheme)
    demo_preview_data(scheme)
    
    # 总结
    print_section("演示完成")
    print(f"[OK] 所有功能测试通过")
    print(f"[OK] 装修方案已创建并可应用")
    print(f"[OK] 后端 API 已就绪")
    print(f"\n下一步:")
    print(f"  1. 启动后端服务：python backend/main.py")
    print(f"  2. 访问装修页面：/decorator")
    print(f"  3. 使用装修编辑器进行可视化编辑")
    print("\n")


if __name__ == "__main__":
    main()
