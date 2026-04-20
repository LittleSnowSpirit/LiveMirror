"""
后台任务执行器
使用 asyncio 直接管理任务，避免 BackgroundTasks 的问题
"""

import asyncio
from typing import Dict, Optional
from datetime import datetime
from loguru import logger
import threading


class TaskRunner:
    """后台任务执行器"""
    
    _instance: Optional['TaskRunner'] = None
    _lock = threading.Lock()
    
    def __new__(cls) -> 'TaskRunner':
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self._task_queue: asyncio.Queue = None
        self._running = False
        self._worker_task: Optional[asyncio.Task] = None
        logger.info("TaskRunner 初始化完成")
    
    def start(self, loop: asyncio.AbstractEventLoop):
        """启动任务执行器"""
        if self._running:
            logger.warning("TaskRunner 已经在运行")
            return
        
        self._running = True
        self._task_queue = asyncio.Queue()
        self._worker_task = loop.create_task(self._worker())
        logger.info("TaskRunner 启动成功")
    
    def stop(self):
        """停止任务执行器"""
        self._running = False
        if self._worker_task:
            self._worker_task.cancel()
        logger.info("TaskRunner 已停止")
    
    async def _worker(self):
        """工作协程"""
        logger.info("TaskRunner worker 启动")
        while self._running:
            try:
                task_func, args = await asyncio.wait_for(
                    self._task_queue.get(),
                    timeout=1.0
                )
                logger.info(f"执行任务：{task_func.__name__}")
                try:
                    await task_func(*args)
                except Exception as e:
                    logger.error(f"任务执行失败：{e}")
                finally:
                    self._task_queue.task_done()
            except asyncio.TimeoutError:
                continue
            except asyncio.CancelledError:
                logger.info("TaskRunner worker 被取消")
                break
            except Exception as e:
                logger.error(f"Worker 异常：{e}")
    
    def submit(self, task_func, *args):
        """提交任务"""
        if not self._running or self._task_queue is None:
            logger.error("TaskRunner 未运行，无法提交任务")
            return False
        
        try:
            self._task_queue.put_nowait((task_func, args))
            logger.info(f"任务已提交：{task_func.__name__}")
            return True
        except Exception as e:
            logger.error(f"提交任务失败：{e}")
            return False


# 全局实例
task_runner = TaskRunner()


def get_task_runner() -> TaskRunner:
    """获取任务执行器实例"""
    return task_runner


def start_task_runner(loop: asyncio.AbstractEventLoop):
    """启动任务执行器"""
    task_runner.start(loop)


def stop_task_runner():
    """停止任务执行器"""
    task_runner.stop()
