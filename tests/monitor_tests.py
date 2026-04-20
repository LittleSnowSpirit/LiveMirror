#!/usr/bin/env python3
"""
LiveMirror 持续测试监控脚本

功能：
1. 定期运行测试（默认每 30 分钟）
2. 记录测试结果
3. 失败时截图并通知
4. 生成测试趋势报告

使用方法：
    python monitor_tests.py
    
配置：
    修改 MONITOR_CONFIG 字典自定义设置
"""

import subprocess
import time
import json
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

# 配置
MONITOR_CONFIG = {
    # 测试间隔（秒）
    "interval_seconds": 1800,  # 30 分钟
    
    # 测试类型
    "test_markers": ["smoke"],  # 冒烟测试
    
    # 日志配置
    "log_file": "monitor.log",
    "log_level": "INFO",
    
    # 结果记录
    "result_file": "test_results.json",
    "max_results": 100,  # 最多保留多少条历史记录
    
    # 通知配置（可扩展）
    "notify_on_failure": True,
    "notify_method": "log",  # log, email, webhook
    
    # 截图配置
    "save_screenshots": True,
    "screenshot_dir": "screenshots",
    
    # 服务配置
    "backend_url": "http://localhost:8000",
    "frontend_url": "http://localhost:5173",
}


class TestMonitor:
    """测试监控器"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.results_file = Path(config["result_file"])
        self.log_file = Path(config["log_file"])
        self.screenshot_dir = Path(config["screenshot_dir"])
        
        # 设置日志
        self._setup_logging()
        
        # 加载历史结果
        self.results = self._load_results()
        
        self.logger.info("测试监控器初始化完成")
    
    def _setup_logging(self):
        """设置日志"""
        logging.basicConfig(
            level=getattr(logging, self.config["log_level"]),
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler(self.log_file, encoding="utf-8"),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def _load_results(self) -> List[Dict]:
        """加载历史测试结果"""
        if self.results_file.exists():
            try:
                with open(self.results_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception as e:
                self.logger.warning(f"加载历史结果失败：{e}")
        return []
    
    def _save_results(self):
        """保存测试结果"""
        # 限制历史记录数量
        if len(self.results) > self.config["max_results"]:
            self.results = self.results[-self.config["max_results"]:]
        
        with open(self.results_file, "w", encoding="utf-8") as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
    
    def _check_services(self) -> bool:
        """检查服务是否可用"""
        import httpx
        
        try:
            # 检查后端
            with httpx.Client(timeout=5) as client:
                response = client.get(f"{self.config['backend_url']}/health")
                if response.status_code != 200:
                    self.logger.warning(f"后端服务异常：{response.status_code}")
                    return False
            
            # 检查前端
            with httpx.Client(timeout=5) as client:
                response = client.get(self.config["frontend_url"])
                if response.status_code != 200:
                    self.logger.warning(f"前端服务异常：{response.status_code}")
                    return False
            
            return True
        except Exception as e:
            self.logger.warning(f"服务检查失败：{e}")
            return False
    
    def _run_tests(self) -> Dict:
        """运行测试"""
        markers = self.config["test_markers"]
        marker_arg = " and ".join(markers) if markers else ""
        
        cmd = [
            "pytest",
            "-m", marker_arg if marker_arg else "not e2e",
            "-v",
            "--tb=short",
            "--json-report",
            "--json-report-file=none",
        ]
        
        self.logger.info(f"运行测试：{' '.join(cmd)}")
        
        start_time = datetime.now()
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 分钟超时
            )
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            success = result.returncode == 0
            
            test_result = {
                "timestamp": start_time.isoformat(),
                "success": success,
                "duration_seconds": duration,
                "markers": markers,
                "tests_passed": self._parse_test_count(result.stdout, "passed"),
                "tests_failed": self._parse_test_count(result.stdout, "failed"),
                "tests_skipped": self._parse_test_count(result.stdout, "skipped"),
                "error_output": result.stderr if not success else None,
            }
            
            if not success:
                self.logger.error(f"测试失败:\n{result.stdout}\n{result.stderr}")
                
                # 保存截图（如果配置）
                if self.config["save_screenshots"]:
                    self._save_screenshots(start_time)
                
                # 发送通知
                if self.config["notify_on_failure"]:
                    self._send_notification(test_result)
            else:
                self.logger.info(f"测试通过 - 耗时：{duration:.1f}秒")
            
            return test_result
            
        except subprocess.TimeoutExpired:
            self.logger.error("测试执行超时")
            return {
                "timestamp": start_time.isoformat(),
                "success": False,
                "duration_seconds": 300,
                "error_output": "测试执行超时（>5 分钟）"
            }
        except Exception as e:
            self.logger.error(f"测试执行异常：{e}")
            return {
                "timestamp": start_time.isoformat(),
                "success": False,
                "error_output": str(e)
            }
    
    def _parse_test_count(self, output: str, status: str) -> int:
        """解析测试数量"""
        # 示例输出："5 passed, 2 failed, 1 skipped in 10.5s"
        import re
        pattern = rf"(\d+)\s+{status}"
        match = re.search(pattern, output)
        return int(match.group(1)) if match else 0
    
    def _save_screenshots(self, timestamp: datetime):
        """保存失败截图"""
        self.screenshot_dir.mkdir(exist_ok=True)
        
        # 如果 Playwright 生成了截图，复制到截图目录
        playwright_screenshots = Path("screenshots")
        if playwright_screenshots.exists():
            timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
            for screenshot in playwright_screenshots.glob("*.png"):
                dest = self.screenshot_dir / f"{timestamp_str}_{screenshot.name}"
                try:
                    screenshot.rename(dest)
                    self.logger.info(f"保存截图：{dest}")
                except Exception as e:
                    self.logger.warning(f"保存截图失败：{e}")
    
    def _send_notification(self, result: Dict):
        """发送失败通知"""
        method = self.config["notify_method"]
        
        if method == "log":
            self.logger.error(
                f"🚨 测试失败通知:\n"
                f"时间：{result['timestamp']}\n"
                f"通过：{result.get('tests_passed', 0)}\n"
                f"失败：{result.get('tests_failed', 0)}\n"
                f"错误：{result.get('error_output', '未知')[:200]}"
            )
        
        elif method == "webhook":
            # 可扩展：发送 Webhook 通知
            self.logger.info("Webhook 通知功能待实现")
        
        elif method == "email":
            # 可扩展：发送邮件通知
            self.logger.info("邮件通知功能待实现")
    
    def _generate_summary(self) -> Dict:
        """生成测试摘要"""
        if not self.results:
            return {}
        
        recent_results = self.results[-10:]  # 最近 10 次
        passed = sum(1 for r in recent_results if r.get("success", False))
        total = len(recent_results)
        
        avg_duration = sum(
            r.get("duration_seconds", 0) for r in recent_results
        ) / total if total > 0 else 0
        
        return {
            "total_runs": len(self.results),
            "recent_pass_rate": passed / total if total > 0 else 0,
            "recent_passed": passed,
            "recent_total": total,
            "average_duration": avg_duration,
            "last_run": self.results[-1]["timestamp"] if self.results else None,
        }
    
    def run_once(self) -> bool:
        """运行一次测试"""
        # 检查服务
        if not self._check_services():
            self.logger.warning("服务检查失败，跳过测试")
            return False
        
        # 运行测试
        result = self._run_tests()
        
        # 保存结果
        self.results.append(result)
        self._save_results()
        
        # 打印摘要
        summary = self._generate_summary()
        if summary:
            self.logger.info(
                f"测试摘要 - "
                f"通过率：{summary['recent_pass_rate']:.1%}, "
                f"平均耗时：{summary['average_duration']:.1f}s"
            )
        
        return result.get("success", False)
    
    def run_continuous(self):
        """持续运行监控"""
        interval = self.config["interval_seconds"]
        
        self.logger.info(f"开始持续监控，间隔：{interval/60:.0f}分钟")
        
        try:
            while True:
                self.run_once()
                
                next_run = datetime.now() + timedelta(seconds=interval)
                self.logger.info(f"下次运行时间：{next_run.strftime('%H:%M:%S')}")
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            self.logger.info("监控被用户中断")
        except Exception as e:
            self.logger.error(f"监控异常：{e}")
            raise


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="LiveMirror 测试监控器")
    parser.add_argument(
        "--once",
        action="store_true",
        help="只运行一次"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=1800,
        help="运行间隔（秒），默认 1800（30 分钟）"
    )
    parser.add_argument(
        "--markers",
        nargs="+",
        default=["smoke"],
        help="pytest 标记，默认 smoke"
    )
    
    args = parser.parse_args()
    
    # 更新配置
    MONITOR_CONFIG["interval_seconds"] = args.interval
    MONITOR_CONFIG["test_markers"] = args.markers
    
    # 创建监控器
    monitor = TestMonitor(MONITOR_CONFIG)
    
    if args.once:
        success = monitor.run_once()
        sys.exit(0 if success else 1)
    else:
        monitor.run_continuous()


if __name__ == "__main__":
    main()
