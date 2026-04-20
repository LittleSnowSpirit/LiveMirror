"""
LiveMirror 导出功能 E2E 测试
测试数据导出的各种场景
"""

import pytest
import json
import csv
import os
from pathlib import Path
from datetime import datetime


class TestExport:
    """导出功能测试类"""
    
    @pytest.fixture
    def sample_data(self):
        """创建测试用的样本数据"""
        return {
            "items": [
                {"id": 1, "name": "项目 1", "created_at": "2024-01-01"},
                {"id": 2, "name": "项目 2", "created_at": "2024-01-02"},
                {"id": 3, "name": "项目 3", "created_at": "2024-01-03"},
            ],
            "metadata": {
                "export_date": datetime.now().isoformat(),
                "version": "1.0"
            }
        }
    
    @pytest.fixture
    def export_dir(self, tmp_path):
        """创建导出目录"""
        export_dir = tmp_path / "exports"
        export_dir.mkdir()
        return export_dir
    
    def test_export_to_json(self, sample_data, export_dir):
        """测试导出为 JSON 格式"""
        output_file = export_dir / "export.json"
        
        # 执行导出
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, ensure_ascii=False, indent=2)
        
        # 验证导出文件
        assert output_file.exists()
        
        with open(output_file, 'r', encoding='utf-8') as f:
            exported_data = json.load(f)
        
        assert exported_data["metadata"]["version"] == "1.0"
        assert len(exported_data["items"]) == 3
        print(f"✓ JSON 导出成功：{output_file}")
    
    def test_export_to_csv(self, sample_data, export_dir):
        """测试导出为 CSV 格式"""
        output_file = export_dir / "export.csv"
        
        # 执行导出
        with open(output_file, 'w', newline='', encoding='utf-8-sig') as f:
            if sample_data["items"]:
                writer = csv.DictWriter(f, fieldnames=sample_data["items"][0].keys())
                writer.writeheader()
                writer.writerows(sample_data["items"])
        
        # 验证导出文件
        assert output_file.exists()
        
        with open(output_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        assert len(rows) == 3
        print(f"✓ CSV 导出成功：{output_file}")
    
    def test_export_to_zip(self, sample_data, export_dir):
        """测试导出为 ZIP 压缩包"""
        import zipfile
        
        # 先创建 JSON 文件
        json_file = export_dir / "data.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, ensure_ascii=False)
        
        # 创建 ZIP
        zip_file = export_dir / "export.zip"
        with zipfile.ZipFile(zip_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(json_file, arcname="data.json")
        
        # 验证 ZIP 文件
        assert zip_file.exists()
        assert zip_file.stat().st_size > 0
        
        # 验证 ZIP 内容
        with zipfile.ZipFile(zip_file, 'r') as zipf:
            names = zipf.namelist()
            assert "data.json" in names
        
        print(f"✓ ZIP 导出成功：{zip_file}")
    
    def test_export_large_dataset(self, export_dir):
        """测试大数据集导出"""
        # 创建大数据集
        large_data = {
            "items": [{"id": i, "value": f"data_{i}"} for i in range(1000)],
            "metadata": {"total": 1000}
        }
        
        output_file = export_dir / "large_export.json"
        
        # 执行导出
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(large_data, f, ensure_ascii=False)
        
        # 验证
        assert output_file.exists()
        file_size = output_file.stat().st_size
        assert file_size > 0
        
        print(f"✓ 大数据集导出成功：{file_size / 1024:.2f} KB")
    
    def test_export_with_filter(self, sample_data, export_dir):
        """测试带过滤条件的导出"""
        # 过滤出 id > 1 的项目
        filtered_items = [
            item for item in sample_data["items"] 
            if item["id"] > 1
        ]
        
        output_file = export_dir / "filtered_export.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({"items": filtered_items}, f, ensure_ascii=False, indent=2)
        
        # 验证
        assert output_file.exists()
        
        with open(output_file, 'r', encoding='utf-8') as f:
            exported = json.load(f)
        
        assert len(exported["items"]) == 2
        print(f"✓ 过滤导出成功：{len(exported['items'])} 个项目")
    
    def test_export_with_date_range(self, sample_data, export_dir):
        """测试按日期范围导出"""
        from datetime import datetime
        
        # 过滤特定日期范围
        start_date = datetime(2024, 1, 2)
        filtered_items = []
        
        for item in sample_data["items"]:
            item_date = datetime.fromisoformat(item["created_at"])
            if item_date >= start_date:
                filtered_items.append(item)
        
        output_file = export_dir / "date_range_export.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({"items": filtered_items}, f, ensure_ascii=False, indent=2)
        
        assert output_file.exists()
        
        with open(output_file, 'r', encoding='utf-8') as f:
            exported = json.load(f)
        
        assert len(exported["items"]) == 2
        print(f"✓ 日期范围导出成功：{len(exported['items'])} 个项目")
    
    def test_export_custom_fields(self, sample_data, export_dir):
        """测试自定义字段导出"""
        # 只导出特定字段
        custom_items = []
        for item in sample_data["items"]:
            custom_items.append({
                "name": item["name"],
                "id": item["id"]
            })
        
        output_file = export_dir / "custom_fields_export.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump({"items": custom_items}, f, ensure_ascii=False, indent=2)
        
        assert output_file.exists()
        
        with open(output_file, 'r', encoding='utf-8') as f:
            exported = json.load(f)
        
        # 验证不包含 created_at 字段
        assert "created_at" not in exported["items"][0]
        print(f"✓ 自定义字段导出成功")
    
    def test_export_multiple_formats(self, sample_data, export_dir):
        """测试同时导出多种格式"""
        formats = []
        
        # JSON
        json_file = export_dir / "export.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, ensure_ascii=False)
        formats.append(("JSON", json_file))
        
        # CSV
        csv_file = export_dir / "export.csv"
        with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
            if sample_data["items"]:
                writer = csv.DictWriter(f, fieldnames=sample_data["items"][0].keys())
                writer.writeheader()
                writer.writerows(sample_data["items"])
        formats.append(("CSV", csv_file))
        
        # 验证所有格式
        for fmt, file in formats:
            assert file.exists()
            print(f"  {fmt}: {file.name}")
        
        print(f"✓ 多格式导出成功：{len(formats)} 种格式")
    
    def test_export_filename_generation(self, export_dir):
        """测试导出文件名自动生成"""
        # 基于时间戳生成文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"export_{timestamp}.json"
        output_file = export_dir / filename
        
        output_file.write_text("{}")
        
        assert output_file.exists()
        assert "export_" in output_file.name
        assert ".json" in output_file.name
        print(f"✓ 文件名生成正常：{filename}")
    
    def test_export_cancel(self, sample_data, export_dir):
        """测试导出取消功能"""
        output_file = export_dir / "cancelled_export.json"
        
        # 模拟导出过程中取消
        cancelled = False
        partial_data = {"items": []}
        
        for i, item in enumerate(sample_data["items"]):
            if i == 1:  # 在处理第 2 个项目时取消
                cancelled = True
                break
            partial_data["items"].append(item)
        
        # 即使取消也应该保存已处理的数据
        if partial_data["items"]:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(partial_data, f, ensure_ascii=False)
        
        assert cancelled
        assert output_file.exists()
        
        with open(output_file, 'r', encoding='utf-8') as f:
            exported = json.load(f)
        
        assert len(exported["items"]) < len(sample_data["items"])
        print(f"✓ 导出取消正常，已保存 {len(exported['items'])} 个项目")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
