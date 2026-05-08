"""Link parser service — platform detection and video metadata extraction via yt-dlp."""

from __future__ import annotations

import json
import logging
import re
import subprocess
from dataclasses import dataclass
from typing import Optional

from config import settings

logger = logging.getLogger(__name__)

# URL patterns for supported platforms
_DOUYIN_PATTERNS = [
    re.compile(r"https?://(?:www\.)?douyin\.com/video/(?P<id>\w+)"),
    re.compile(r"https?://v\.douyin\.com/(?P<id>[A-Za-z0-9]+)"),
]
_BILIBILI_PATTERNS = [
    re.compile(r"https?://(?:www\.)?bilibili\.com/video/(?P<id>BV[A-Za-z0-9]+)"),
    re.compile(r"https?://(?:www\.)?bilibili\.com/video/(?P<id>av\d+)"),
    re.compile(r"https?://b23\.tv/(?P<id>[A-Za-z0-9]+)"),
]


@dataclass
class LinkInfo:
    platform: str
    video_id: str
    title: str
    duration: int
    thumbnail_url: str
    uploader: str
    error: Optional[str] = None


def parse_url(url: str) -> tuple[str, str]:
    """Identify platform and video ID from a URL.

    Returns (platform, video_id).  Raises ValueError when the URL is not
    recognised.
    """
    for pattern in _DOUYIN_PATTERNS:
        m = pattern.search(url)
        if m:
            return "douyin", m.group("id")

    for pattern in _BILIBILI_PATTERNS:
        m = pattern.search(url)
        if m:
            return "bilibili", m.group("id")

    raise ValueError(f"Unsupported URL: {url}")


def is_supported_url(url: str) -> bool:
    """Return True if *url* matches a known platform pattern."""
    try:
        parse_url(url)
        return True
    except ValueError:
        return False


def get_link_info(url: str) -> LinkInfo:
    """Use yt-dlp --dump-json to fetch video metadata without downloading."""
    try:
        platform, video_id = parse_url(url)
    except ValueError as exc:
        return LinkInfo(
            platform="unknown",
            video_id="",
            title="",
            duration=0,
            thumbnail_url="",
            uploader="",
            error=str(exc),
        )

    try:
        result = subprocess.run(
            [
                settings.yt_dlp_path,
                "--dump-json",
                "--no-download",
                "--no-warnings",
                url,
            ],
            capture_output=True,
            text=True,
            timeout=30,
        )
    except FileNotFoundError:
        return LinkInfo(
            platform=platform,
            video_id=video_id,
            title="",
            duration=0,
            thumbnail_url="",
            uploader="",
            error="yt-dlp not found. Please install it: pip install yt-dlp",
        )
    except subprocess.TimeoutExpired:
        return LinkInfo(
            platform=platform,
            video_id=video_id,
            title="",
            duration=0,
            thumbnail_url="",
            uploader="",
            error="yt-dlp metadata request timed out.",
        )

    if result.returncode != 0:
        stderr = (result.stderr or "").strip()[:200]
        return LinkInfo(
            platform=platform,
            video_id=video_id,
            title="",
            duration=0,
            thumbnail_url="",
            uploader="",
            error=f"yt-dlp failed: {stderr}",
        )

    try:
        info = json.loads(result.stdout)
    except json.JSONDecodeError:
        return LinkInfo(
            platform=platform,
            video_id=video_id,
            title="",
            duration=0,
            thumbnail_url="",
            uploader="",
            error="Failed to parse yt-dlp JSON output.",
        )

    return LinkInfo(
        platform=platform,
        video_id=video_id,
        title=info.get("title", ""),
        duration=int(info.get("duration", 0) or 0),
        thumbnail_url=info.get("thumbnail", ""),
        uploader=info.get("uploader", ""),
        error=None,
    )
