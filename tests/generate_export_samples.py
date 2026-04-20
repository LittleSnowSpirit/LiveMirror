"""
LiveMirror Export Pro - 生成导出样本
用于演示各种导出格式的功能
"""

import sys
import os
import json
from datetime import datetime

# 添加 backend 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))
from services.export_pro import ExportProService, ExportFormat


def generate_sample_data():
    """生成示例数据"""
    return [
        {
            "id": 1,
            "product_name": "智能手表 Pro",
            "category": "电子产品",
            "price": 1299.00,
            "sales": 450,
            "revenue": 584550.00,
            "rating": 4.8
        },
        {
            "id": 2,
            "product_name": "无线耳机 X",
            "category": "电子产品",
            "price": 599.00,
            "sales": 820,
            "revenue": 491180.00,
            "rating": 4.6
        },
        {
            "id": 3,
            "product_name": "机械键盘 K1",
            "category": "电脑配件",
            "price": 399.00,
            "sales": 650,
            "revenue": 259350.00,
            "rating": 4.7
        },
        {
            "id": 4,
            "product_name": "办公椅 Ergo",
            "category": "办公家具",
            "price": 899.00,
            "sales": 230,
            "revenue": 206770.00,
            "rating": 4.5
        },
        {
            "id": 5,
            "product_name": "显示器 27 寸",
            "category": "电脑配件",
            "price": 1599.00,
            "sales": 380,
            "revenue": 607620.00,
            "rating": 4.9
        },
        {
            "id": 6,
            "product_name": "鼠标垫 XL",
            "category": "电脑配件",
            "price": 79.00,
            "sales": 1200,
            "revenue": 94800.00,
            "rating": 4.4
        },
        {
            "id": 7,
            "product_name": "USB 集线器",
            "category": "电脑配件",
            "price": 129.00,
            "sales": 950,
            "revenue": 122550.00,
            "rating": 4.3
        },
        {
            "id": 8,
            "product_name": "笔记本电脑支架",
            "category": "办公家具",
            "price": 199.00,
            "sales": 560,
            "revenue": 111440.00,
            "rating": 4.6
        }
    ]


def main():
    """主函数 - 生成所有格式的导出样本"""
    # 设置控制台编码
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    
    print("=" * 60)
    print("LiveMirror 专业数据导出 - 样本生成")
    print("=" * 60)
    print()
    
    # 初始化服务
    service = ExportProService()
    sample_data = generate_sample_data()
    
    print(f"示例数据：{len(sample_data)} 条产品记录")
    print()
    
    # 创建各种模板
    print("📋 创建导出模板...")
    
    templates = {}
    
    # Excel 模板
    templates['excel'] = service.create_template(
        name="产品销售报表（Excel 带图表）",
        format=ExportFormat.EXCEL,
        config={
            "include_charts": True,
            "chart_types": ["bar", "line", "pie"],
            "sheet_name": "销售数据",
            "header_style": {"bold": True, "background": "#4472C4", "color": "#FFFFFF"},
            "auto_filter": True,
            "freeze_panes": "A2"
        },
        description="包含销售数据和可视化图表的 Excel 报表"
    )
    print(f"  ✓ Excel 模板：{templates['excel'].name}")
    
    # Word 模板
    templates['word'] = service.create_template(
        name="销售分析报告（Word）",
        format=ExportFormat.WORD,
        config={
            "include_cover": True,
            "cover_title": "2026 年度产品销售分析报告",
            "include_toc": True,
            "sections": ["summary", "analysis", "charts", "conclusion"],
            "page_numbering": True,
            "header_text": "LiveMirror 数据分析"
        },
        description="专业的 Word 格式销售分析报告"
    )
    print(f"  ✓ Word 模板：{templates['word'].name}")
    
    # PowerPoint 模板
    templates['ppt'] = service.create_template(
        name="销售演示文稿（PowerPoint）",
        format=ExportFormat.POWERPOINT,
        config={
            "slide_layout": "corporate",
            "title_slide": True,
            "include_charts": True,
            "charts_per_slide": 2,
            "theme_color": "#1890ff",
            "footer_text": "LiveMirror"
        },
        description="用于汇报演示的 PowerPoint 文稿"
    )
    print(f"  ✓ PowerPoint 模板：{templates['ppt'].name}")
    
    # PDF 模板
    templates['pdf'] = service.create_template(
        name="专业文档（PDF）",
        format=ExportFormat.PDF,
        config={
            "page_size": "A4",
            "margins": {"top": 2.54, "bottom": 2.54, "left": 2.54, "right": 2.54},
            "font_family": "Arial",
            "font_size": 11,
            "line_spacing": 1.5,
            "include_header_footer": True,
            "watermark": False
        },
        description="专业排版的 PDF 文档"
    )
    print(f"  ✓ PDF 模板：{templates['pdf'].name}")
    
    print()
    print("📤 开始导出样本...")
    print()
    
    results = {}
    
    # Excel 导出
    print("  正在导出 Excel...")
    results['excel'] = service.export_data(
        data=sample_data,
        format=ExportFormat.EXCEL,
        template=templates['excel']
    )
    if results['excel']['success']:
        print(f"    ✓ {results['excel']['message']}")
        print(f"    📁 文件：{results['excel']['output_path']}")
    
    # Word 导出
    print("  正在导出 Word...")
    results['word'] = service.export_data(
        data=sample_data,
        format=ExportFormat.WORD,
        template=templates['word']
    )
    if results['word']['success']:
        print(f"    ✓ {results['word']['message']}")
        print(f"    📁 文件：{results['word']['output_path']}")
    
    # PowerPoint 导出
    print("  正在导出 PowerPoint...")
    results['ppt'] = service.export_data(
        data=sample_data,
        format=ExportFormat.POWERPOINT,
        template=templates['ppt']
    )
    if results['ppt']['success']:
        print(f"    ✓ {results['ppt']['message']}")
        print(f"    📁 文件：{results['ppt']['output_path']}")
    
    # PDF 导出
    print("  正在导出 PDF...")
    results['pdf'] = service.export_data(
        data=sample_data,
        format=ExportFormat.PDF,
        template=templates['pdf']
    )
    if results['pdf']['success']:
        print(f"    ✓ {results['pdf']['message']}")
        print(f"    📁 文件：{results['pdf']['output_path']}")
    
    # CSV 导出
    print("  正在导出 CSV...")
    results['csv'] = service.export_data(
        data=sample_data,
        format=ExportFormat.CSV,
        template=service.create_template(
            name="CSV 导出",
            format=ExportFormat.CSV,
            config={"delimiter": ",", "encoding": "utf-8-sig"}
        )
    )
    if results['csv']['success']:
        print(f"    ✓ {results['csv']['message']}")
        print(f"    📁 文件：{results['csv']['output_path']}")
    
    # JSON 导出
    print("  正在导出 JSON...")
    results['json'] = service.export_data(
        data=sample_data,
        format=ExportFormat.JSON
    )
    if results['json']['success']:
        print(f"    ✓ {results['json']['message']}")
        print(f"    📁 文件：{results['json']['output_path']}")
    
    print()
    print("=" * 60)
    print("✅ 导出样本生成完成！")
    print("=" * 60)
    print()
    
    # 显示导出统计
    print("📊 导出统计:")
    print(f"  - 创建模板数：{len(templates) + 1}")
    print(f"  - 成功导出：{sum(1 for r in results.values() if r['success'])} / {len(results)}")
    print()
    
    # 显示导出信息文件内容
    print("📄 Excel 导出信息预览:")
    if 'info_path' in results['excel']:
        with open(results['excel']['info_path'], 'r', encoding='utf-8') as f:
            info = json.load(f)
            print(json.dumps(info, indent=2, ensure_ascii=False))
    
    print()
    print("💡 提示：实际项目中需要安装以下库来生成真实文件:")
    print("   - Excel: pip install openpyxl xlsxwriter")
    print("   - Word: pip install python-docx")
    print("   - PowerPoint: pip install python-pptx")
    print("   - PDF: pip install reportlab")
    print()


if __name__ == "__main__":
    main()
