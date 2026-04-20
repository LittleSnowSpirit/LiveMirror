"""Transcription provider abstraction for the LiveMirror core pipeline."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from config import settings


@dataclass
class TranscriptionResult:
    text: str
    segments: list[dict[str, Any]]
    duration: float | None = None
    language: str | None = None


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
        self._model = None

    def _load_model(self):
        if self._model is None:
            try:
                from faster_whisper import WhisperModel
            except ImportError as exc:
                raise RuntimeError(
                    "faster-whisper is not installed. Run `pip install -r backend/requirements.txt`."
                ) from exc

            kwargs: dict[str, Any] = {}
            if self.device and self.device != "auto":
                kwargs["device"] = self.device
            if self.compute_type and self.compute_type != "default":
                kwargs["compute_type"] = self.compute_type

            self._model = WhisperModel(self.model_name, **kwargs)
        return self._model

    def transcribe(self, file_path: str) -> TranscriptionResult:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Media file does not exist: {file_path}")

        model = self._load_model()
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

        return TranscriptionResult(
            text=" ".join(texts).strip(),
            segments=segments,
            duration=getattr(info, "duration", None),
            language=getattr(info, "language", self.language),
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


def get_transcription_service() -> TranscriptionService:
    provider = settings.transcription_provider.lower()
    if provider == "mock":
        return MockTranscriptionService()
    if provider == "local":
        return LocalWhisperTranscriptionService()
    raise RuntimeError(f"Unsupported transcription provider: {settings.transcription_provider}")
