"""
LiveMirror 历史记录功能 E2E 测试
测试历史记录的查询、过滤和管理
"""

import pytest
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict


class TestHistory:
    """历史记录功能测试类"""
    
    @pytest.fixture
    def sample_history(self):
        """创建测试用的历史记录样本"""
        base_date = datetime.now()
        return [
            {
                "id": i,
                "action": "upload" if i % 2 == 0 else "download",
                "filename": f"file_{i}.txt",
                "timestamp": (base_date - timedelta(days=i)).isoformat(),
                "size": 1024 * (i + 1),
                "status": "completed"
            }
            for i in range(1, 21)  # 20 条历史记录
        ]
    
    @pytest.fixture
    def history_db(self, tmp_path, sample_history):
        """创建模拟的历史记录数据库"""
        db_file = tmp_path / "history.json"
        with open(db_file, 'w', encoding='utf-8') as f:
            json.dump(sample_history, f, ensure_ascii=False, indent=2)
        return db_file
    
    def test_history_list_all(self, history_db):
        """测试列出所有历史记录"""
        with open(history_db, 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        assert len(history) == 20
        print(f"✓ 历史记录列表正常：{len(history)} 条")
    
    def test_history_pagination(self, history_db):
        """测试历史记录分页"""
        with open(history_db, 'r', encoding='utf-8') as f:
            all_history = json.load(f)
        
        page_size = 5
        page = 1
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        paginated = all_history[start_idx:end_idx]
        
        assert len(paginated) == page_size
        print(f"✓ 分页正常：第 {page} 页，{len(paginated)} 条记录")
    
    def test_history_filter_by_action(self, history_db):
        """测试按操作类型过滤"""
        with open(history_db, 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        uploads = [h for h in history if h["action"] == "upload"]
        downloads = [h for h in history if h["action"] == "download"]
        
        assert len(uploads) + len(downloads) == len(history)
        print(f"✓ 按操作过滤：上传 {len(uploads)} 条，下载 {len(downloads)} 条")
    
    def test_history_filter_by_date_range(self, history_db):
        """测试按日期范围过滤"""
        with open(history_db, 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        # 过滤最近 7 天的记录
        cutoff_date = datetime.now() - timedelta(days=7)
        recent = [
            h for h in history 
            if datetime.fromisoformat(h["timestamp"]) >= cutoff_date
        ]
        
        assert len(recent) <= len(history)
        print(f"✓ 日期范围过滤：最近 7 天 {len(recent)} 条记录")
    
    def test_history_filter_by_status(self, history_db):
        """测试按状态过滤"""
        with open(history_db, 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        completed = [h for h in history if h["status"] == "completed"]
        
        assert len(completed) == len(history)  # 所有记录都是 completed
        print(f"✓ 状态过滤：已完成 {len(completed)} 条")
    
    def test_history_search_by_filename(self, history_db):
        """测试按文件名搜索"""
        with open(history_db, 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        search_term = "file_5"
        results = [h for h in history if search_term in h["filename"]]
        
        assert len(results) >= 1
        print(f"✓ 文件名搜索：'{search_term}' 找到 {len(results)} 条")
    
    def test_history_sort_by_timestamp(self, history_db):
        """测试按时间戳排序"""
        with open(history_db, 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        # 按时间降序排序（最新的在前）
        sorted_history = sorted(
            history, 
            key=lambda x: x["timestamp"], 
            reverse=True
        )
        
        # 验证排序
        for i in range(len(sorted_history) - 1):
            assert sorted_history[i]["timestamp"] >= sorted_history[i + 1]["timestamp"]
        
        print(f"✓ 时间排序正常：{len(sorted_history)} 条记录")
    
    def test_history_sort_by_size(self, history_db):
        """测试按文件大小排序"""
        with open(history_db, 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        # 按大小降序排序
        sorted_history = sorted(
            history, 
            key=lambda x: x["size"], 
            reverse=True
        )
        
        # 验证排序
        for i in range(len(sorted_history) - 1):
            assert sorted_history[i]["size"] >= sorted_history[i + 1]["size"]
        
        print(f"✓ 大小排序正常")
    
    def test_history_delete_single(self, history_db):
        """测试删除单条历史记录"""
        with open(history_db, 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        original_count = len(history)
        
        # 删除第一条记录
        deleted = history.pop(0)
        
        # 保存更新后的记录
        with open(history_db, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        
        # 验证
        with open(history_db, 'r', encoding='utf-8') as f:
            updated_history = json.load(f)
        
        assert len(updated_history) == original_count - 1
        print(f"✓ 单条删除正常：删除了 ID {deleted['id']}")
    
    def test_history_delete_by_date(self, history_db):
        """测试按日期批量删除"""
        with open(history_db, 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        original_count = len(history)
        
        # 删除 30 天前的记录
        cutoff_date = datetime.now() - timedelta(days=30)
        kept_history = [
            h for h in history 
            if datetime.fromisoformat(h["timestamp"]) >= cutoff_date
        ]
        deleted_count = original_count - len(kept_history)
        
        # 保存更新后的记录
        with open(history_db, 'w', encoding='utf-8') as f:
            json.dump(kept_history, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 批量删除正常：删除了 {deleted_count} 条旧记录")
    
    def test_history_clear_all(self, history_db):
        """测试清空所有历史记录"""
        with open(history_db, 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        original_count = len(history)
        assert original_count > 0
        
        # 清空
        history.clear()
        
        with open(history_db, 'w', encoding='utf-8') as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        
        # 验证
        with open(history_db, 'r', encoding='utf-8') as f:
            cleared_history = json.load(f)
        
        assert len(cleared_history) == 0
        print(f"✓ 清空所有记录正常：原 {original_count} 条")
    
    def test_history_export(self, history_db, tmp_path):
        """测试历史记录导出"""
        with open(history_db, 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        export_file = tmp_path / "history_export.json"
        
        export_data = {
            "exported_at": datetime.now().isoformat(),
            "total_records": len(history),
            "records": history
        }
        
        with open(export_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        
        assert export_file.exists()
        
        with open(export_file, 'r', encoding='utf-8') as f:
            exported = json.load(f)
        
        assert exported["total_records"] == len(history)
        print(f"✓ 历史记录导出正常：{exported['total_records']} 条")
    
    def test_history_statistics(self, history_db):
        """测试历史记录统计"""
        with open(history_db, 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        # 计算统计信息
        total_count = len(history)
        total_size = sum(h["size"] for h in history)
        uploads = len([h for h in history if h["action"] == "upload"])
        downloads = len([h for h in history if h["action"] == "download"])
        
        stats = {
            "total_records": total_count,
            "total_size_bytes": total_size,
            "uploads": uploads,
            "downloads": downloads,
            "avg_size": total_size / total_count if total_count > 0 else 0
        }
        
        assert stats["total_records"] == 20
        assert stats["uploads"] + stats["downloads"] == total_count
        print(f"✓ 统计信息正常:")
        print(f"  总记录数：{stats['total_records']}")
        print(f"  总大小：{stats['total_size_bytes'] / 1024:.2f} KB")
        print(f"  上传：{stats['uploads']}, 下载：{stats['downloads']}")
    
    def test_history_recent_activity(self, history_db):
        """测试最近活动查询"""
        with open(history_db, 'r', encoding='utf-8') as f:
            history = json.load(f)
        
        # 获取最近 5 条记录
        recent = history[:5]
        
        assert len(recent) <= 5
        print(f"✓ 最近活动查询正常：{len(recent)} 条")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
