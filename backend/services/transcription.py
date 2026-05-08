"""Transcription provider abstraction for the LiveMirror core pipeline."""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from pathlib import Path
from shutil import which
from threading import Lock
from typing import Any, Protocol

import httpx

from config import settings


_MODEL_CACHE: dict[tuple[str, str, str], Any] = {}
_MODEL_CACHE_LOCK = Lock()


@dataclass
class TranscriptionResult:
    text: str
    segments: list[dict[str, Any]]
    duration: float | None = None
    language: str | None = None
    model_load_time: float | None = None
    transcribe_time: float | None = None
    total_time: float | None = None


class TranscriptionService(Protocol):
    def transcribe(self, file_path: str) -> TranscriptionResult:
        """Transcribe a local audio or video file."""


class LocalWhisperTranscriptionService:
    """Local faster-whisper implementation loaded lazily at runtime."""

    def __init__(
        self,
        model_name: str | None = None,
        language: str | None = None,
        device: str | None = None,
        compute_type: str | None = None,
    ) -> None:
        self.model_name = model_name or settings.whisper_model
        self.language = language or settings.whisper_language
        self.device = device or settings.whisper_device
        self.compute_type = compute_type or settings.whisper_compute_type
        self._model_key = (self.model_name, self.device, self.compute_type)

    def preflight(self) -> None:
        if which("ffmpeg") is None and which("ffmpeg.exe") is None:
            raise RuntimeError("FFmpeg is required for local Whisper transcription but was not found on PATH.")

        try:
            import faster_whisper  # noqa: F401
        except ImportError as exc:
            raise RuntimeError(
                "faster-whisper is not installed. Run `pip install -r backend/requirements.txt`."
            ) from exc

    def _load_model(self):
        self.preflight()

        with _MODEL_CACHE_LOCK:
            if self._model_key in _MODEL_CACHE:
                return _MODEL_CACHE[self._model_key]

            from faster_whisper import WhisperModel

            kwargs: dict[str, Any] = {}
            if self.device and self.device != "auto":
                kwargs["device"] = self.device
            if self.compute_type and self.compute_type != "default":
                kwargs["compute_type"] = self.compute_type

            model = WhisperModel(self.model_name, **kwargs)
            _MODEL_CACHE[self._model_key] = model
            return model

    def transcribe(self, file_path: str) -> TranscriptionResult:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Media file does not exist: {file_path}")

        total_start = time.time()

        # 加载模型
        model_load_start = time.time()
        model = self._load_model()
        model_load_time = time.time() - model_load_start

        # 转写
        transcribe_start = time.time()
        segments_iter, info = model.transcribe(str(path), language=self.language)
        segments: list[dict[str, Any]] = []
        texts: list[str] = []

        for idx, segment in enumerate(segments_iter):
            text = segment.text.strip()
            texts.append(text)
            segments.append(
                {
                    "id": idx,
                    "start": float(segment.start),
                    "end": float(segment.end),
                    "text": text,
                }
            )

        transcribe_time = time.time() - transcribe_start
        total_time = time.time() - total_start

        return TranscriptionResult(
            text=" ".join(texts).strip(),
            segments=segments,
            duration=getattr(info, "duration", None),
            language=getattr(info, "language", self.language),
            model_load_time=round(model_load_time, 2),
            transcribe_time=round(transcribe_time, 2),
            total_time=round(total_time, 2),
        )


class MockTranscriptionService:
    """Deterministic provider for local tests and CI."""

    def transcribe(self, file_path: str) -> TranscriptionResult:
        filename = Path(file_path).name
        text = (
            "欢迎来到直播间，今天我们先介绍产品亮点。"
            "这款产品适合日常使用，现在下单有直播间优惠。"
            "如果有问题可以在评论区提问，主播会及时回答。"
        )
        return TranscriptionResult(
            text=text,
            duration=18.0,
            language="zh",
            segments=[
                {"id": 0, "start": 0.0, "end": 6.0, "text": f"{filename}: 欢迎来到直播间，今天我们先介绍产品亮点。"},
                {"id": 1, "start": 6.0, "end": 12.0, "text": "这款产品适合日常使用，现在下单有直播间优惠。"},
                {"id": 2, "start": 12.0, "end": 18.0, "text": "如果有问题可以在评论区提问，主播会及时回答。"},
            ],
        )


class DashScopeTranscriptionService:
    """DashScope ASR implementation using SenseVoice / Paraformer models."""

    # 最大轮询次数和间隔（秒）
    MAX_POLL_ATTEMPTS = 120
    POLL_INTERVAL = 5

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:
        self.api_key = api_key or settings.dashscope_api_key
        self.model = model or settings.dashscope_asr_model

    def _check_api_key(self) -> None:
        if not self.api_key:
            raise RuntimeError(
                "DashScope API Key is not configured. "
                "Set the DASHSCOPE_API_KEY environment variable or add it to .env."
            )

    def transcribe(self, file_path: str) -> TranscriptionResult:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Media file does not exist: {file_path}")

        self._check_api_key()

        try:
            import dashscope
            from dashscope.audio.asr import Transcription as DashScopeTranscription
        except ImportError as exc:
            raise RuntimeError(
                "dashscope SDK is not installed. Run `pip install dashscope`."
            ) from exc

        dashscope.api_key = self.api_key

        total_start = time.time()

        # 提交转写任务（异步模式）
        submit_start = time.time()
        file_url = str(path.resolve())

        # DashScope Transcription.call 使用本地文件路径或 URL
        task_response = DashScopeTranscription.call(
            model=self.model,
            file_urls=[file_url],
            language_hints=["zh", "en"],
        )

        # 检查提交是否成功
        if task_response.status_code != 200:
            raise RuntimeError(
                f"DashScope ASR task submission failed: "
                f"status={task_response.status_code}, "
                f"message={getattr(task_response, 'message', 'unknown error')}"
            )

        task_id = task_response.output.get("task_id") if task_response.output else None
        if not task_id:
            raise RuntimeError(
                f"DashScope ASR did not return a task_id. "
                f"Response: {task_response}"
            )

        submit_time = time.time() - submit_start

        # 轮询等待结果
        poll_start = time.time()
        result_data = self._poll_task(task_id, dashscope)
        poll_time = time.time() - poll_start

        total_time = time.time() - total_start

        # 解析结果
        return self._parse_result(
            result_data,
            model_load_time=round(submit_time, 2),
            transcribe_time=round(poll_time, 2),
            total_time=round(total_time, 2),
        )

    def _poll_task(self, task_id: str, dashscope_module) -> dict[str, Any]:
        """轮询 DashScope 异步任务直到完成。"""
        from dashscope.audio.asr import Transcription as DashScopeTranscription

        for _ in range(self.MAX_POLL_ATTEMPTS):
            task_result = DashScopeTranscription.fetch(task_id)

            if task_result.status_code != 200:
                raise RuntimeError(
                    f"DashScope ASR poll failed: "
                    f"status={task_result.status_code}, "
                    f"message={getattr(task_result, 'message', 'unknown error')}"
                )

            output = task_result.output or {}
            task_status = output.get("task_status", "")

            if task_status == "SUCCEEDED":
                return output
            elif task_status in ("FAILED", "UNKNOWN"):
                raise RuntimeError(
                    f"DashScope ASR task {task_id} ended with status: {task_status}. "
                    f"Details: {output}"
                )

            time.sleep(self.POLL_INTERVAL)

        raise RuntimeError(
            f"DashScope ASR task {task_id} timed out after "
            f"{self.MAX_POLL_ATTEMPTS * self.POLL_INTERVAL}s."
        )

    def _parse_result(
        self,
        output: dict[str, Any],
        model_load_time: float,
        transcribe_time: float,
        total_time: float,
    ) -> TranscriptionResult:
        """将 DashScope 返回的 JSON 转换为 TranscriptionResult。"""
        results = output.get("results", [])
        if not results:
            raise RuntimeError(
                f"DashScope ASR returned empty results. Output: {output}"
            )

        # 取第一个结果文件
        first_result_url = results[0].get("transcription_url", "")
        if first_result_url:
            transcription_data = self._fetch_transcription_json(first_result_url)
        else:
            transcription_data = results[0]

        # 解析转写内容
        transcripts = transcription_data.get("transcripts", [])
        segments: list[dict[str, Any]] = []
        texts: list[str] = []
        total_duration = 0.0

        for idx, transcript_entry in enumerate(transcripts):
            sentences = transcript_entry.get("sentences", [])
            for sentence in sentences:
                text = sentence.get("text", "").strip()
                if not text:
                    continue
                start_ms = sentence.get("begin_time", 0)
                end_ms = sentence.get("end_time", 0)
                start_sec = start_ms / 1000.0
                end_sec = end_ms / 1000.0

                texts.append(text)
                segments.append({
                    "id": len(segments),
                    "start": start_sec,
                    "end": end_sec,
                    "text": text,
                })
                total_duration = max(total_duration, end_sec)

        if not segments:
            # 回退：尝试直接从 transcript 字段获取
            for transcript_entry in transcripts:
                full_text = transcript_entry.get("text", "").strip()
                if full_text:
                    texts.append(full_text)
                    segments.append({
                        "id": 0,
                        "start": 0.0,
                        "end": total_duration or 0.0,
                        "text": full_text,
                    })

        return TranscriptionResult(
            text=" ".join(texts).strip(),
            segments=segments,
            duration=total_duration if total_duration > 0 else None,
            language="zh",
            model_load_time=model_load_time,
            transcribe_time=transcribe_time,
            total_time=total_time,
        )

    def _fetch_transcription_json(self, url: str) -> dict[str, Any]:
        """下载 DashScope 返回的转写结果 JSON。"""
        resp = httpx.get(url, timeout=30)
        resp.raise_for_status()
        return resp.json()


def get_transcription_service() -> TranscriptionService:
    provider = settings.transcription_provider.lower()
    if provider == "mock":
        return MockTranscriptionService()
    if provider == "local":
        return LocalWhisperTranscriptionService()
    if provider == "dashscope":
        return DashScopeTranscriptionService()
    raise RuntimeError(f"Unsupported transcription provider: {settings.transcription_provider}")


def check_transcription_environment() -> dict[str, Any]:
    provider = settings.transcription_provider.lower()
    if provider == "mock":
        return {
            "provider": "mock",
            "ready": True,
            "details": "Mock transcription is enabled.",
        }
    if provider == "dashscope":
        checks: dict[str, Any] = {
            "provider": "dashscope",
            "model": settings.dashscope_asr_model,
            "api_key_configured": bool(settings.dashscope_api_key),
        }
        try:
            import dashscope  # noqa: F401
            checks["dashscope_sdk"] = True
        except ImportError:
            checks["dashscope_sdk"] = False

        checks["ready"] = bool(checks["api_key_configured"] and checks["dashscope_sdk"])
        if not checks["ready"]:
            missing = []
            if not checks["api_key_configured"]:
                missing.append("DASHSCOPE_API_KEY")
            if not checks["dashscope_sdk"]:
                missing.append("dashscope SDK")
            checks["error"] = f"Missing DashScope transcription dependency: {', '.join(missing)}."
        return checks
    if provider != "local":
        return {
            "provider": settings.transcription_provider,
            "ready": False,
            "error": f"Unsupported transcription provider: {settings.transcription_provider}",
        }

    local_checks: dict[str, Any] = {
        "provider": "local",
        "model": settings.whisper_model,
        "device": settings.whisper_device,
        "compute_type": settings.whisper_compute_type,
        "ffmpeg": which("ffmpeg") or which("ffmpeg.exe"),
    }
    try:
        import faster_whisper  # noqa: F401
        local_checks["faster_whisper"] = True
    except ImportError:
        local_checks["faster_whisper"] = False

    local_checks["ready"] = bool(local_checks["ffmpeg"] and local_checks["faster_whisper"])
    if not local_checks["ready"]:
        missing = []
        if not local_checks["ffmpeg"]:
            missing.append("FFmpeg")
        if not local_checks["faster_whisper"]:
            missing.append("faster-whisper")
        local_checks["error"] = f"Missing local transcription dependency: {', '.join(missing)}."
    return local_checks
