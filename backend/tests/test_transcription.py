"""Tests for the transcription service abstraction layer."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

# Ensure backend package is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.transcription import (
    DashScopeTranscriptionService,
    MockTranscriptionService,
    TranscriptionResult,
    check_transcription_environment,
    get_transcription_service,
)


# ---------------------------------------------------------------------------
# TranscriptionResult dataclass
# ---------------------------------------------------------------------------


class TestTranscriptionResult:
    def test_basic_fields(self):
        result = TranscriptionResult(text="hello", segments=[{"id": 0, "start": 0.0, "end": 1.0, "text": "hello"}])
        assert result.text == "hello"
        assert result.duration is None
        assert result.language is None

    def test_optional_fields(self):
        result = TranscriptionResult(
            text="test",
            segments=[],
            duration=10.0,
            language="zh",
            model_load_time=1.0,
            transcribe_time=5.0,
            total_time=6.0,
        )
        assert result.duration == 10.0
        assert result.language == "zh"
        assert result.model_load_time == 1.0


# ---------------------------------------------------------------------------
# MockTranscriptionService
# ---------------------------------------------------------------------------


class TestMockTranscriptionService:
    def test_returns_deterministic_result(self):
        svc = MockTranscriptionService()
        r1 = svc.transcribe("/fake/path.wav")
        r2 = svc.transcribe("/fake/path.wav")
        assert r1.text == r2.text
        assert len(r1.segments) == 3
        assert r1.language == "zh"
        assert r1.duration == 18.0

    def test_filename_appears_in_first_segment(self):
        svc = MockTranscriptionService()
        result = svc.transcribe("/data/my_stream.wav")
        assert "my_stream.wav" in result.segments[0]["text"]


# ---------------------------------------------------------------------------
# DashScopeTranscriptionService
# ---------------------------------------------------------------------------


class TestDashScopeTranscriptionService:
    """Unit tests for DashScope ASR service with mocked SDK."""

    def test_missing_api_key_raises(self, tmp_path):
        audio = tmp_path / "test.wav"
        audio.write_bytes(b"fake audio")

        with patch("services.transcription.settings") as mock_settings:
            mock_settings.dashscope_api_key = None
            svc_no_key = DashScopeTranscriptionService(api_key=None)
            with pytest.raises(RuntimeError, match="API Key is not configured"):
                svc_no_key.transcribe(str(audio))

    def test_missing_sdk_raises(self, tmp_path):
        audio = tmp_path / "test.wav"
        audio.write_bytes(b"fake audio")

        svc = DashScopeTranscriptionService(api_key="test-key")

        with patch.dict(sys.modules, {"dashscope": None}):
            with pytest.raises(RuntimeError, match="dashscope SDK is not installed"):
                svc.transcribe(str(audio))

    def test_file_not_found_raises(self):
        svc = DashScopeTranscriptionService(api_key="test-key")
        with pytest.raises(FileNotFoundError):
            svc.transcribe("/nonexistent/file.wav")

    def test_transcribe_success(self, tmp_path):
        """Test successful DashScope ASR flow: submit -> poll -> fetch JSON."""
        audio = tmp_path / "test.wav"
        audio.write_bytes(b"fake audio content")

        svc = DashScopeTranscriptionService(api_key="test-key")
        svc.MAX_POLL_ATTEMPTS = 2
        svc.POLL_INTERVAL = 0

        # Mock dashscope module
        mock_dashscope = MagicMock()

        # Mock Transcription.call (submit)
        submit_response = MagicMock()
        submit_response.status_code = 200
        submit_response.output = {"task_id": "task-123"}

        # Mock Transcription.fetch (poll - success)
        poll_response = MagicMock()
        poll_response.status_code = 200
        poll_response.output = {
            "task_status": "SUCCEEDED",
            "results": [
                {
                    "transcription_url": "https://example.com/result.json",
                }
            ],
        }

        mock_transcription_cls = MagicMock()
        mock_transcription_cls.call.return_value = submit_response
        mock_transcription_cls.fetch.return_value = poll_response
        mock_dashscope.audio.asr.Transcription = mock_transcription_cls

        # Mock httpx.get for result JSON download
        result_json = {
            "transcripts": [
                {
                    "sentences": [
                        {"text": "欢迎来到直播间", "begin_time": 0, "end_time": 3000},
                        {"text": "今天给大家推荐好物", "begin_time": 3000, "end_time": 6000},
                    ]
                }
            ]
        }

        mock_httpx_response = MagicMock()
        mock_httpx_response.json.return_value = result_json
        mock_httpx_response.raise_for_status = MagicMock()

        with patch.dict(sys.modules, {"dashscope": mock_dashscope, "dashscope.audio": mock_dashscope.audio, "dashscope.audio.asr": mock_dashscope.audio.asr}):
            with patch("httpx.get", return_value=mock_httpx_response):

                result = svc.transcribe(str(audio))

        assert isinstance(result, TranscriptionResult)
        assert "欢迎来到直播间" in result.text
        assert "今天给大家推荐好物" in result.text
        assert len(result.segments) == 2
        assert result.segments[0]["start"] == 0.0
        assert result.segments[0]["end"] == 3.0
        assert result.segments[1]["start"] == 3.0
        assert result.segments[1]["end"] == 6.0
        assert result.duration == 6.0
        assert result.language == "zh"
        assert result.transcribe_time is not None

    def test_transcribe_poll_failure(self, tmp_path):
        audio = tmp_path / "test.wav"
        audio.write_bytes(b"fake audio")

        svc = DashScopeTranscriptionService(api_key="test-key")
        svc.MAX_POLL_ATTEMPTS = 2
        svc.POLL_INTERVAL = 0

        mock_dashscope = MagicMock()

        submit_response = MagicMock()
        submit_response.status_code = 200
        submit_response.output = {"task_id": "task-456"}

        poll_response = MagicMock()
        poll_response.status_code = 200
        poll_response.output = {"task_status": "FAILED", "message": "Audio format error"}

        mock_transcription_cls = MagicMock()
        mock_transcription_cls.call.return_value = submit_response
        mock_transcription_cls.fetch.return_value = poll_response
        mock_dashscope.audio.asr.Transcription = mock_transcription_cls

        with patch.dict(sys.modules, {"dashscope": mock_dashscope, "dashscope.audio": mock_dashscope.audio, "dashscope.audio.asr": mock_dashscope.audio.asr}):
            with pytest.raises(RuntimeError, match="FAILED"):
                svc.transcribe(str(audio))

    def test_transcribe_submit_failure(self, tmp_path):
        audio = tmp_path / "test.wav"
        audio.write_bytes(b"fake audio")

        svc = DashScopeTranscriptionService(api_key="test-key")

        mock_dashscope = MagicMock()

        submit_response = MagicMock()
        submit_response.status_code = 400
        submit_response.message = "Bad request"

        mock_transcription_cls = MagicMock()
        mock_transcription_cls.call.return_value = submit_response
        mock_dashscope.audio.asr.Transcription = mock_transcription_cls

        with patch.dict(sys.modules, {"dashscope": mock_dashscope, "dashscope.audio": mock_dashscope.audio, "dashscope.audio.asr": mock_dashscope.audio.asr}):
            with pytest.raises(RuntimeError, match="task submission failed"):
                svc.transcribe(str(audio))


# ---------------------------------------------------------------------------
# Factory function and environment check
# ---------------------------------------------------------------------------


class TestFactoryAndEnvironment:
    def test_mock_provider(self):
        with patch("services.transcription.settings") as mock_settings:
            mock_settings.transcription_provider = "mock"
            svc = get_transcription_service()
            assert isinstance(svc, MockTranscriptionService)

    def test_dashscope_provider(self):
        with patch("services.transcription.settings") as mock_settings:
            mock_settings.transcription_provider = "dashscope"
            mock_settings.dashscope_api_key = "test-key"
            mock_settings.dashscope_asr_model = "paraformer-v2"
            svc = get_transcription_service()
            assert isinstance(svc, DashScopeTranscriptionService)

    def test_unsupported_provider_raises(self):
        with patch("services.transcription.settings") as mock_settings:
            mock_settings.transcription_provider = "nonexistent"
            with pytest.raises(RuntimeError, match="Unsupported"):
                get_transcription_service()

    def test_check_env_mock(self):
        with patch("services.transcription.settings") as mock_settings:
            mock_settings.transcription_provider = "mock"
            result = check_transcription_environment()
            assert result["ready"] is True
            assert result["provider"] == "mock"

    def test_check_env_dashscope_ready(self):
        with patch("services.transcription.settings") as mock_settings:
            mock_settings.transcription_provider = "dashscope"
            mock_settings.dashscope_api_key = "test-key"
            mock_settings.dashscope_asr_model = "paraformer-v2"
            # dashscope module available
            result = check_transcription_environment()
            assert result["provider"] == "dashscope"
            assert result["api_key_configured"] is True

    def test_check_env_dashscope_no_key(self):
        with patch("services.transcription.settings") as mock_settings:
            mock_settings.transcription_provider = "dashscope"
            mock_settings.dashscope_api_key = None
            mock_settings.dashscope_asr_model = "paraformer-v2"
            result = check_transcription_environment()
            assert result["ready"] is False
            assert "DASHSCOPE_API_KEY" in result["error"]
