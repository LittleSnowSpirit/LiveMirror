"""Tests for the link parser service."""

import json
import subprocess
from unittest.mock import patch, MagicMock

import pytest


def _import():
    import sys, pathlib
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
    from services.link_parser import parse_url, is_supported_url, get_link_info, LinkInfo
    return parse_url, is_supported_url, get_link_info, LinkInfo


parse_url, is_supported_url, get_link_info, LinkInfo = _import()


class TestParseUrl:
    def test_douyin_standard(self):
        platform, vid = parse_url("https://www.douyin.com/video/7123456789")
        assert platform == "douyin"
        assert vid == "7123456789"

    def test_douyin_short(self):
        platform, vid = parse_url("https://v.douyin.com/abc123")
        assert platform == "douyin"
        assert vid == "abc123"

    def test_bilibili_bv(self):
        platform, vid = parse_url("https://www.bilibili.com/video/BV1xx411c7mD")
        assert platform == "bilibili"
        assert vid == "BV1xx411c7mD"

    def test_bilibili_av(self):
        platform, vid = parse_url("https://www.bilibili.com/video/av12345678")
        assert platform == "bilibili"
        assert vid == "av12345678"

    def test_bilibili_short(self):
        platform, vid = parse_url("https://b23.tv/abcdef")
        assert platform == "bilibili"
        assert vid == "abcdef"

    def test_unsupported_url_raises(self):
        with pytest.raises(ValueError, match="Unsupported URL"):
            parse_url("https://www.youtube.com/watch?v=abc")

    def test_random_string_raises(self):
        with pytest.raises(ValueError):
            parse_url("not a url at all")


class TestIsSupportedUrl:
    def test_douyin(self):
        assert is_supported_url("https://www.douyin.com/video/123") is True

    def test_bilibili(self):
        assert is_supported_url("https://b23.tv/abc") is True

    def test_youtube(self):
        assert is_supported_url("https://www.youtube.com/watch?v=abc") is False

    def test_empty(self):
        assert is_supported_url("") is False


class TestGetLinkInfo:
    @patch("services.link_parser.subprocess.run")
    def test_success(self, mock_run):
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=json.dumps({
                "title": "Test Video",
                "duration": 120,
                "thumbnail": "https://example.com/thumb.jpg",
                "uploader": "TestUser",
            }),
            stderr="",
        )
        info = get_link_info("https://www.douyin.com/video/123")
        assert info.platform == "douyin"
        assert info.title == "Test Video"
        assert info.duration == 120
        assert info.uploader == "TestUser"
        assert info.error is None

    @patch("services.link_parser.subprocess.run")
    def test_ytdlp_failure(self, mock_run):
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="some error")
        info = get_link_info("https://www.douyin.com/video/123")
        assert info.error is not None
        assert "yt-dlp failed" in info.error

    @patch("services.link_parser.subprocess.run")
    def test_ytdlp_not_found(self, mock_run):
        mock_run.side_effect = FileNotFoundError
        info = get_link_info("https://www.douyin.com/video/123")
        assert "yt-dlp not found" in info.error

    @patch("services.link_parser.subprocess.run")
    def test_timeout(self, mock_run):
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="yt-dlp", timeout=30)
        info = get_link_info("https://www.douyin.com/video/123")
        assert "timed out" in info.error

    def test_invalid_url(self):
        info = get_link_info("https://www.youtube.com/watch?v=abc")
        assert info.platform == "unknown"
        assert info.error is not None

    @patch("services.link_parser.subprocess.run")
    def test_bad_json(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="not json", stderr="")
        info = get_link_info("https://www.douyin.com/video/123")
        assert "parse" in info.error.lower() or "JSON" in info.error
