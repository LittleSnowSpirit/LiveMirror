"""
批量导出功能测试脚本
测试内容：
1. 单个文件导出
2. 批量导出（10 个文件）
3. ZIP 解压验证
4. 导出进度
5. 异步导出
"""

import os
import sys
import json
import zipfile
import tempfile
import asyncio
from datetime import datetime
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database import Base
from models import Danmu, DanmuBatch, User
from services.export_service import ExportService, AsyncExportTask, get_async_task_manager


# ==================== 测试数据库设置 ====================
DATABASE_URL = "sqlite:///./test_livemirror.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def setup_test_database():
    """设置测试数据库"""
    # 先删除旧数据库
    db_path = "test_livemirror.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        print(f"[OK] 已清理旧测试数据库")
    
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    # 创建测试用户
    test_user = User(
        username="test_user",
        email="test@example.com",
        hashed_password=User.hash_password("test_password"),
        is_active=True
    )
    db.add(test_user)
    db.commit()
    
    # 创建测试批次
    test_batches = []
    for i in range(10):
        batch = DanmuBatch(
            user_id=test_user.id,
            batch_id=f"test_batch_{i:03d}",
            filename=f"test_export_{i}.json",
            file_format="json",
            total_count=100,
            success_count=100,
            failed_count=0,
            status="completed",
            start_timestamp=i * 100.0,
            end_timestamp=(i + 1) * 100.0
        )
        db.add(batch)
        test_batches.append(batch)
    
    # 创建测试弹幕
    for batch_idx in range(10):
        for danmu_idx in range(100):
            danmu = Danmu(
                user_id=test_user.id,
                content=f"Test danmu {batch_idx}-{danmu_idx}",
                timestamp=batch_idx * 100.0 + danmu_idx,
                username=f"user_{danmu_idx % 10}",
                user_level=(danmu_idx % 5) + 1,
                sentiment=["positive", "negative", "neutral"][danmu_idx % 3],
                sentiment_score=(danmu_idx % 100) / 100.0 - 0.5,
                danmu_type="normal",
                like_count=danmu_idx % 50,
                reply_count=danmu_idx % 10,
                speech_segment_id=f"test_batch_{batch_idx:03d}",
                is_key_danmu=(danmu_idx % 20 == 0),
                key_type="highlight" if danmu_idx % 20 == 0 else None
            )
            db.add(danmu)
    
    db.commit()
    db.close()
    
    return test_user, test_batches


def cleanup_test_database():
    """清理测试数据库"""
    db_path = "test_livemirror.db"
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            print(f"[OK] 已清理测试数据库：{db_path}")
        except PermissionError:
            # Windows 上文件可能被锁定，忽略
            print(f"[WARN] 测试数据库文件被锁定，稍后手动删除：{db_path}")


# ==================== 测试函数 ====================
def test_single_file_export():
    """测试 1: 单个文件导出"""
    print("\n" + "="*60)
    print("测试 1: 单个文件导出")
    print("="*60)
    
    db = TestingSessionLocal()
    export_service = ExportService(db)
    
    try:
        # 获取单个批次的弹幕
        danmus = export_service.get_danmus_for_export(batch_id="test_batch_000", limit=100)
        print(f"[OK] 获取到 {len(danmus)} 条弹幕")
        
        # 测试 JSON 导出
        json_content = export_service.export_to_json(danmus, {"test": "single_export"})
        assert len(json_content) > 0, "JSON 导出内容为空"
        json_data = json.loads(json_content)
        assert len(json_data["danmus"]) == len(danmus), "JSON 弹幕数量不匹配"
        print(f"[OK] JSON 导出成功，大小：{len(json_content)} 字节")
        
        # 测试 Markdown 导出
        md_content = export_service.export_to_markdown(danmus, {"test": "single_export"})
        assert len(md_content) > 0, "Markdown 导出内容为空"
        assert "# LiveMirror 弹幕分析报告" in md_content, "Markdown 格式不正确"
        print(f"[OK] Markdown 导出成功，大小：{len(md_content)} 字节")
        
        # 测试 PDF 导出
        pdf_content = export_service.export_to_pdf(danmus, {"test": "single_export"})
        assert len(pdf_content) > 0, "PDF 导出内容为空"
        print(f"[OK] PDF 导出成功，大小：{len(pdf_content)} 字节")
        
        print("\n[PASS] 测试 1 通过：单个文件导出功能正常")
        return True
        
    except Exception as e:
        print(f"\n[FAIL] 测试 1 失败：{str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def test_batch_export():
    """测试 2: 批量导出（10 个文件）"""
    print("\n" + "="*60)
    print("测试 2: 批量导出（10 个文件）")
    print("="*60)
    
    db = TestingSessionLocal()
    export_service = ExportService(db)
    
    try:
        all_files = []
        
        # 导出 10 个批次
        for i in range(10):
            batch_id = f"test_batch_{i:03d}"
            danmus = export_service.get_danmus_for_export(batch_id=batch_id, limit=100)
            
            json_content = export_service.export_to_json(
                danmus,
                {"batch_id": batch_id, "batch_index": i}
            )
            
            all_files.append({
                "name": f"{batch_id}.json",
                "content": json_content
            })
            
            print(f"  [OK] 导出批次 {i+1}/10: {batch_id} ({len(danmus)} 条弹幕)")
        
        # 创建 ZIP 压缩包
        zip_content = export_service.create_zip_archive(all_files, "batch_export.zip")
        print(f"\n[OK] ZIP 压缩包创建成功，大小：{len(zip_content)} 字节")
        
        # 保存到临时文件
        temp_fd, temp_path = tempfile.mkstemp(suffix=".zip")
        try:
            os.write(temp_fd, zip_content)
            os.close(temp_fd)
            
            # 验证 ZIP 文件
            with zipfile.ZipFile(temp_path, 'r') as zip_file:
                file_list = zip_file.namelist()
                assert len(file_list) == 10, f"ZIP 文件数量不正确：{len(file_list)}"
                print(f"[OK] ZIP 文件验证成功，包含 {len(file_list)} 个文件")
                
                # 验证每个文件内容
                for filename in file_list:
                    with zip_file.open(filename) as f:
                        content = f.read().decode('utf-8')
                        data = json.loads(content)
                        assert "danmus" in data, f"{filename} 格式不正确"
                print(f"[OK] 所有文件内容验证通过")
            
        finally:
            os.unlink(temp_path)
        
        print("\n[PASS] 测试 2 通过：批量导出功能正常")
        return True
        
    except Exception as e:
        print(f"\n[FAIL] 测试 2 失败：{str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def test_zip_extraction():
    """测试 3: ZIP 解压验证"""
    print("\n" + "="*60)
    print("测试 3: ZIP 解压验证")
    print("="*60)
    
    db = TestingSessionLocal()
    export_service = ExportService(db)
    
    try:
        # 创建测试 ZIP
        test_files = [
            {"name": "file1.json", "content": '{"test": 1}'},
            {"name": "file2.md", "content": "# Test"},
            {"name": "file3.txt", "content": "Plain text"}
        ]
        
        zip_content = export_service.create_zip_archive(test_files, "test.zip")
        
        # 解压到临时目录
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, "test.zip")
        
        with open(zip_path, 'wb') as f:
            f.write(zip_content)
        
        # 解压并验证
        with zipfile.ZipFile(zip_path, 'r') as zip_file:
            zip_file.extractall(temp_dir)
            
            # 验证文件
            for file_info in test_files:
                file_path = os.path.join(temp_dir, file_info["name"])
                assert os.path.exists(file_path), f"文件不存在：{file_info['name']}"
                
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    assert content == file_info["content"], f"文件内容不匹配：{file_info['name']}"
                
                print(f"[OK] 验证文件：{file_info['name']}")
        
        # 清理
        import shutil
        shutil.rmtree(temp_dir)
        
        print("\n[PASS] 测试 3 通过：ZIP 解压功能正常")
        return True
        
    except Exception as e:
        print(f"\n[FAIL] 测试 3 失败：{str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


def test_export_progress():
    """测试 4: 导出进度"""
    print("\n" + "="*60)
    print("测试 4: 导出进度")
    print("="*60)
    
    task_manager = get_async_task_manager()
    
    try:
        # 创建任务
        task_id = "test_progress_task"
        task_info = task_manager.create_task(
            task_id=task_id,
            user_id=1,
            export_format="json",
            batch_ids=[f"batch_{i}" for i in range(10)],
            total_files=10
        )
        
        print(f"[OK] 任务创建：{task_id}")
        print(f"  初始状态：{task_info['status']}, 进度：{task_info['progress']}%")
        
        # 更新进度
        for i in range(1, 11):
            task_manager.update_progress(task_id, i)
            task_info = task_manager.get_task(task_id)
            print(f"  [OK] 进度更新：{i}/10 ({task_info['progress']}%)")
        
        # 完成任务
        task_manager.complete_task(task_id, "/download/test.zip")
        task_info = task_manager.get_task(task_id)
        
        print(f"  [OK] 最终状态：{task_info['status']}, 进度：{task_info['progress']}%")
        
        # 验证
        assert task_info['status'] == 'completed', "任务状态不正确"
        assert task_info['progress'] == 100, "进度不是 100%"
        assert task_info['result_url'] == '/download/test.zip', "下载 URL 不正确"
        
        print("\n[PASS] 测试 4 通过：导出进度跟踪功能正常")
        return True
        
    except Exception as e:
        print(f"\n[FAIL] 测试 4 失败：{str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def test_async_export():
    """测试 5: 异步导出"""
    print("\n" + "="*60)
    print("测试 5: 异步导出")
    print("="*60)
    
    db = TestingSessionLocal()
    task_manager = get_async_task_manager()
    
    try:
        from routes.batch_export import process_batch_export
        
        # 创建异步任务
        task_id = "test_async_task"
        task_info = task_manager.create_task(
            task_id=task_id,
            user_id=1,
            export_format="json",
            batch_ids=[f"test_batch_{i:03d}" for i in range(3)],
            total_files=3
        )
        
        print(f"[OK] 异步任务创建：{task_id}")
        print(f"  初始状态：{task_info['status']}")
        
        # 执行异步导出
        await process_batch_export(
            task_id=task_id,
            user_id=1,
            batch_ids=[f"test_batch_{i:03d}" for i in range(3)],
            export_format="json",
            db=db
        )
        
        # 验证结果
        task_info = task_manager.get_task(task_id)
        print(f"  [OK] 最终状态：{task_info['status']}")
        print(f"  [OK] 进度：{task_info['progress']}%")
        print(f"  [OK] 下载 URL: {task_info['result_url']}")
        
        assert task_info['status'] == 'completed', "任务状态不正确"
        assert task_info['progress'] == 100, "进度不是 100%"
        assert task_info['result_url'] is not None, "下载 URL 为空"
        
        print("\n[PASS] 测试 5 通过：异步导出功能正常")
        return True
        
    except Exception as e:
        print(f"\n[FAIL] 测试 5 失败：{str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        db.close()


# ==================== 主测试流程 ====================
async def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*60)
    print("LiveMirror 批量导出功能测试")
    print("="*60)
    print(f"开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = []
    
    # 设置测试数据库
    print("\n正在设置测试数据库...")
    setup_test_database()
    print("[OK] 测试数据库设置完成")
    
    try:
        # 运行测试
        results.append(("单个文件导出", test_single_file_export()))
        results.append(("批量导出", test_batch_export()))
        results.append(("ZIP 解压", test_zip_extraction()))
        results.append(("导出进度", test_export_progress()))
        results.append(("异步导出", await test_async_export()))
        
    finally:
        # 清理
        cleanup_test_database()
    
    # 输出结果
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} - {test_name}")
    
    print(f"\n总计：{passed}/{total} 测试通过")
    
    if passed == total:
        print("\n[SUCCESS] 所有测试通过！")
        return True
    else:
        print(f"\n[WARNING] {total - passed} 个测试失败")
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
