"""Shared background task queue for backend work items."""

from __future__ import annotations

import logging
from concurrent.futures import Future, ThreadPoolExecutor
from threading import Lock
from typing import Any, Callable

from config import settings

logger = logging.getLogger(__name__)


class BackgroundTaskQueue:
    def __init__(self, max_workers: int | None = None, thread_name_prefix: str = "livemirror-task") -> None:
        self.max_workers = max(1, max_workers or settings.task_worker_count)
        self.thread_name_prefix = thread_name_prefix
        self._lock = Lock()
        self._executor: ThreadPoolExecutor | None = None

    def submit(self, task_id: str, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Future:
        with self._lock:
            if self._executor is None:
                self._executor = ThreadPoolExecutor(
                    max_workers=self.max_workers,
                    thread_name_prefix=self.thread_name_prefix,
                )

            future = self._executor.submit(fn, *args, **kwargs)

        future.add_done_callback(lambda done: self._log_failure(task_id, done))
        return future

    def shutdown(self, wait: bool = False) -> None:
        with self._lock:
            executor = self._executor
            self._executor = None

        if executor is not None:
            executor.shutdown(wait=wait, cancel_futures=not wait)

    @staticmethod
    def _log_failure(task_id: str, future: Future) -> None:
        try:
            future.result()
        except Exception:
            logger.exception("Background task %s failed.", task_id)


_queue_lock = Lock()
_task_queue: BackgroundTaskQueue | None = None


def get_task_queue() -> BackgroundTaskQueue:
    global _task_queue
    with _queue_lock:
        if _task_queue is None:
            _task_queue = BackgroundTaskQueue()
        return _task_queue


def shutdown_task_queue(wait: bool = False) -> None:
    global _task_queue
    with _queue_lock:
        queue = _task_queue
        _task_queue = None

    if queue is not None:
        queue.shutdown(wait=wait)
