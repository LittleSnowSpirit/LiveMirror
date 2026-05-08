"""Tests for the download service."""

import subprocess
import time
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest


def _import():
    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
    from services.downloader import download_audio, cleanup_old_files, DownloadResult
    return download_audio, cleanup_old_files, DownloadResult


download_audio, cleanup_old_files, DownloadResult = _import()


class TestDownloadAudio:
    @patch("services.downloader.subprocess.run")
    @patch("services.downloader.settings")
    def test_success(self, mock_settings, mock_run, tmp_path):
        mock_settings.yt_dlp_path = "yt-dlp"
        mock_settings.max_download_duration = 600

        # Create the expected output file
        audio_file = tmp_path / "vid123.mp3"
        audio_file.write_bytes(b"fake audio")

        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")

        # Patch _probe_duration to avoid needing ffprobe
        with patch("services.downloader._probe_duration", return_value=120):
            result = download_audio("https://example.com/video", str(tmp_path), "vid123")

        assert result.success is True
        assert result.file_path == str(audio_file)
        assert result.duration == 120
        assert result.error is None

    @patch("services.downloader.subprocess.run")
    @patch("services.downloader.settings")
    def test_failure(self, mock_settings, mock_run, tmp_path):
        mock_settings.yt_dlp_path = "yt-dlp"
        mock_settings.max_download_duration = 600
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="download error msg")

        result = download_audio("https://example.com/video", str(tmp_path), "vid123")
        assert result.success is False
        assert "download error" in result.error

    @patch("services.downloader.subprocess.run")
    @patch("services.downloader.settings")
    def test_timeout(self, mock_settings, mock_run, tmp_path):
        mock_settings.yt_dlp_path = "yt-dlp"
        mock_settings.max_download_duration = 600
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="yt-dlp", timeout=600)

        result = download_audio("https://example.com/video", str(tmp_path), "vid123")
        assert result.success is False
        assert "timed out" in result.error

    @patch("services.downloader.subprocess.run")
    @patch("services.downloader.settings")
    def test_ytdlp_not_found(self, mock_settings, mock_run, tmp_path):
        mock_settings.yt_dlp_path = "yt-dlp"
        mock_settings.max_download_duration = 600
        mock_run.side_effect = FileNotFoundError

        result = download_audio("https://example.com/video", str(tmp_path), "vid123")
        assert result.success is False
        assert "not found" in result.error

    @patch("services.downloader.subprocess.run")
    @patch("services.downloader.settings")
    def test_output_file_missing(self, mock_settings, mock_run, tmp_path):
        mock_settings.yt_dlp_path = "yt-dlp"
        mock_settings.max_download_duration = 600
        mock_run.return_value = MagicMock(returncode=0, stdout="", stderr="")
        # Don't create any file — simulate yt-dlp not producing output

        result = download_audio("https://example.com/video", str(tmp_path), "vid123")
        assert result.success is False
        assert "not found" in result.error


class TestCleanupOldFiles:
    def test_removes_old_files(self, tmp_path):
        old_file = tmp_path / "old.mp3"
        old_file.write_bytes(b"old")
        # Set mtime to 48 hours ago
        old_time = time.time() - 48 * 3600
        import os
        os.utime(old_file, (old_time, old_time))

        new_file = tmp_path / "new.mp3"
        new_file.write_bytes(b"new")

        removed = cleanup_old_files(str(tmp_path), max_age_hours=24)
        assert removed == 1
        assert not old_file.exists()
        assert new_file.exists()

    def test_empty_directory(self, tmp_path):
        removed = cleanup_old_files(str(tmp_path))
        assert removed == 0

    def test_nonexistent_directory(self):
        removed = cleanup_old_files("/nonexistent/path")
        assert removed == 0
