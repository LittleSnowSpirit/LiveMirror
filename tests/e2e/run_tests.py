#!/usr/bin/env python3
"""
LiveMirror E2E 测试运行器
运行所有测试并生成报告
"""

import subprocess
import sys
import json
from datetime import datetime
from pathlib import Path


def run_tests():
    """运行所有 E2E 测试"""
    print("=" * 60)
    print("LiveMirror E2E 测试套件")
    print("=" * 60)
    print(f"开始时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 测试文件列表
    test_files = [
        "test_batch_upload.py",
        "test_export.py",
        "test_history.py",
        "test_error_handling.py",
        "test_performance.py",
    ]
    
    results = []
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    for test_file in test_files:
        print(f"\n{'=' * 60}")
        print(f"运行测试：{test_file}")
        print(f"{'=' * 60}")
        
        cmd = [sys.executable, "-m", "pytest", test_file, "-v", "--tb=short"]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 分钟超时
            )
            
            # 解析结果
            output = result.stdout + result.stderr
            
            # 统计测试结果
            if "passed" in output:
                # 解析 pytest 输出
                import re
                passed_match = re.search(r'(\d+) passed', output)
                failed_match = re.search(r'(\d+) failed', output)
                
                passed = int(passed_match.group(1)) if passed_match else 0
                failed = int(failed_match.group(1)) if failed_match else 0
                
                total_tests += passed + failed
                passed_tests += passed
                failed_tests += failed
                
                status = "✓ 通过" if result.returncode == 0 else "✗ 失败"
                results.append({
                    "file": test_file,
                    "status": status,
                    "passed": passed,
                    "failed": failed,
                    "total": passed + failed
                })
                
                print(f"结果：{status}")
                print(f"  通过：{passed}, 失败：{failed}, 总计：{passed + failed}")
            else:
                results.append({
                    "file": test_file,
                    "status": "✗ 错误",
                    "passed": 0,
                    "failed": 0,
                    "total": 0
                })
                print(f"结果：✗ 错误")
                
        except subprocess.TimeoutExpired:
            results.append({
                "file": test_file,
                "status": "✗ 超时",
                "passed": 0,
                "failed": 0,
                "total": 0
            })
            print(f"结果：✗ 超时")
        except Exception as e:
            results.append({
                "file": test_file,
                "status": f"✗ 错误：{str(e)}",
                "passed": 0,
                "failed": 0,
                "total": 0
            })
            print(f"结果：✗ 错误 - {str(e)}")
    
    # 生成报告
    print(f"\n{'=' * 60}")
    print("测试报告")
    print(f"{'=' * 60}")
    print(f"结束时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    print("详细结果:")
    for result in results:
        print(f"  {result['file']}: {result['status']} "
              f"(通过：{result['passed']}, 失败：{result['failed']}, 总计：{result['total']})")
    
    print()
    print("汇总:")
    print(f"  总测试数：{total_tests}")
    print(f"  通过：{passed_tests}")
    print(f"  失败：{failed_tests}")
    print(f"  通过率：{passed_tests / total_tests * 100:.1f}%" if total_tests > 0 else "  通过率：N/A")
    
    # 保存报告
    report = {
        "timestamp": datetime.now().isoformat(),
        "results": results,
        "summary": {
            "total": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "pass_rate": passed_tests / total_tests * 100 if total_tests > 0 else 0
        }
    }
    
    report_dir = Path("reports")
    report_dir.mkdir(exist_ok=True)
    
    report_file = report_dir / f"e2e_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n报告已保存：{report_file}")
    
    return failed_tests == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
