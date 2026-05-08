"""Shared background task queue for backend work items."""

from __future__ import annotations

import logging
from concurrent.futures import Future, ThreadPoolExecutor
from threading import Lock
from typing import Any, Callable

from config import settings

logger = logging.getLogger(__name__)


def process_link_task(task_id: str, url: str) -> None:
    """Full pipeline for a link-based analysis task.

    download -> transcribe -> analyze -> report
    """
    from database import get_db
    from services.core_analysis import build_core_analysis, build_report_data
    from services.database import (
        get_task,
        update_task_analysis,
        update_task_duration,
        update_task_status,
        update_task_transcription,
    )
    from services.downloader import download_audio
    from services.link_parser import parse_url
    from services.transcription import get_transcription_service

    db = next(get_db())
    try:
        task = get_task(db, task_id)
        if task is None:
            return

        # Step 1: Download (0 -> 30%)
        update_task_status(db, task, "downloading", 5, current_step="downloading")
        try:
            platform, video_id = parse_url(url)
        except ValueError as exc:
            update_task_status(db, task, "failed", 0, str(exc))
            return

        from config import settings as cfg

        dl = download_audio(url, cfg.download_dir, video_id)
        if not dl.success:
            update_task_status(db, task, "failed", 0, dl.error or "Download failed")
            return

        # Update file path on the task so transcription can find it
        task.file_path = dl.file_path
        task.file_size = __import__("pathlib").Path(dl.file_path).stat().st_size
        db.commit()

        # Step 2: Transcribe (30 -> 60%)
        update_task_status(db, task, "transcribing", 35, current_step="transcribing")
        service = get_transcription_service()
        result = service.transcribe(dl.file_path)

        task = get_task(db, task_id)
        if task is None:
            return

        update_task_duration(db, task, result.duration or float(dl.duration))
        update_task_transcription(db, task, result.text, result.segments)
        task.language = result.language

        # Data quality scoring
        quality_score = 1.0
        text = result.text or ""
        if not text.strip():
            quality_score = 0.0
        elif len(text.strip()) < 10:
            quality_score = 0.3
        task.data_quality_score = quality_score
        db.commit()

        # Step 3: Analyze (60 -> 100%)
        update_task_status(db, task, "analyzing", 75, current_step="analyzing")
        analysis = build_core_analysis(result.text, result.segments, result.duration)
        report = build_report_data(
            task_id=task.task_id,
            filename=task.filename,
            transcription=result.text,
            segments=result.segments,
            duration=result.duration,
            language=result.language,
            analysis=analysis,
        )
        update_task_analysis(db, task, analysis, report)
    except Exception as exc:
        logger.exception("Link task %s failed", task_id)
        task = get_task(db, task_id)
        if task is not None:
            update_task_status(db, task, "failed", 0, str(exc))
    finally:
        db.close()


class BackgroundTaskQueue:
    def __init__(self, max_workers: int | None = None, thread_name_prefix: str = "livemirror-task") -> None:
        self.max_workers = max(1, max_workers or settings.task_worker_count)
        self.thread_name_prefix = thread_name_prefix
        self._lock = Lock()
        self._executor: ThreadPoolExecutor | None = None
        self._use_celery = False
        self._celery_app = None

        try:
            from celery_app import celery_app
            self._celery_app = celery_app
            self._use_celery = True
            logger.info("任务队列使用 Celery + Redis")
        except Exception:
            logger.info("任务队列使用 ThreadPoolExecutor（Celery 不可用）")

    def submit(self, task_id: str, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Future:
        if self._use_celery and self._celery_app is not None:
            return self._submit_celery(task_id, fn, *args, **kwargs)
        return self._submit_thread(task_id, fn, *args, **kwargs)

    def _submit_celery(self, task_id: str, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Future:
        """通过 Celery 提交任务"""
        from celery_app import celery_app

        @celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
        def run_task(self, task_id: str, fn_name: str, *args, **kwargs):
            try:
                return fn(*args, **kwargs)
            except Exception as exc:
                self.retry(exc=exc)

        result = run_task.delay(task_id, fn.__name__, *args, **kwargs)

        future = Future()
        import threading

        def check_result():
            try:
                res = result.get(timeout=3600)
                future.set_result(res)
            except Exception as e:
                future.set_exception(e)

        thread = threading.Thread(target=check_result, daemon=True)
        thread.start()

        future.add_done_callback(lambda done: self._log_failure(task_id, done))
        return future

    def _submit_thread(self, task_id: str, fn: Callable[..., Any], *args: Any, **kwargs: Any) -> Future:
        """通过线程池提交任务"""
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
