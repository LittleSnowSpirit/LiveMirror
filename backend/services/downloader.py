"""yt-dlp based audio download service."""

from __future__ import annotations

import logging
import os
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from config import settings

logger = logging.getLogger(__name__)


@dataclass
class DownloadResult:
    success: bool
    file_path: Optional[str]
    duration: int
    error: Optional[str] = None


def download_audio(url: str, output_dir: str, video_id: str) -> DownloadResult:
    """Download audio from *url* using yt-dlp.

    The audio is saved as MP3 in *output_dir* with filename ``{video_id}.mp3``.
    """
    output_path = Path(output_dir) / f"{video_id}.mp3"

    try:
        result = subprocess.run(
            [
                settings.yt_dlp_path,
                "-x",
                "--audio-format",
                "mp3",
                "--audio-quality",
                "0",
                "--no-video",
                "--no-warnings",
                "-o",
                str(output_path),
                url,
            ],
            capture_output=True,
            text=True,
            timeout=settings.max_download_duration,
        )
    except FileNotFoundError:
        return DownloadResult(
            success=False,
            file_path=None,
            duration=0,
            error="yt-dlp not found. Please install it: pip install yt-dlp",
        )
    except subprocess.TimeoutExpired:
        _cleanup_partial(str(output_path))
        return DownloadResult(
            success=False,
            file_path=None,
            duration=0,
            error=f"Download timed out after {settings.max_download_duration}s.",
        )

    if result.returncode != 0:
        _cleanup_partial(str(output_path))
        stderr = (result.stderr or "").strip()[:200]
        return DownloadResult(
            success=False,
            file_path=None,
            duration=0,
            error=f"yt-dlp download failed: {stderr}",
        )

    # yt-dlp may add extension — find the actual file
    actual_path = _find_downloaded_file(output_dir, video_id)
    if actual_path is None:
        return DownloadResult(
            success=False,
            file_path=None,
            duration=0,
            error="Download completed but output file not found.",
        )

    # Probe duration with ffprobe if available, else 0
    duration = _probe_duration(actual_path)

    return DownloadResult(
        success=True,
        file_path=str(actual_path),
        duration=duration,
        error=None,
    )


def cleanup_old_files(directory: str, max_age_hours: int = 24) -> int:
    """Remove files in *directory* older than *max_age_hours*.  Returns count removed."""
    cutoff = time.time() - max_age_hours * 3600
    removed = 0
    dir_path = Path(directory)
    if not dir_path.is_dir():
        return 0

    for entry in dir_path.iterdir():
        if entry.is_file() and entry.stat().st_mtime < cutoff:
            try:
                entry.unlink()
                removed += 1
            except OSError:
                logger.warning("Failed to remove old file: %s", entry)
    return removed


# ---- internal helpers ----


def _find_downloaded_file(output_dir: str, video_id: str) -> Optional[Path]:
    """Locate the downloaded file — yt-dlp might use .mp3, .m4a, .webm etc."""
    dir_path = Path(output_dir)
    for suffix in (".mp3", ".m4a", ".webm", ".opus", ".wav"):
        candidate = dir_path / f"{video_id}{suffix}"
        if candidate.is_file():
            return candidate
    # fallback: look for any file starting with video_id
    for entry in dir_path.iterdir():
        if entry.is_file() and entry.stem == video_id:
            return entry
    return None


def _probe_duration(file_path: str) -> int:
    """Try to get audio duration in seconds via ffprobe.  Returns 0 on failure."""
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "quiet",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                file_path,
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            return int(float(result.stdout.strip()))
    except (FileNotFoundError, subprocess.TimeoutExpired, ValueError):
        pass
    return 0


def _cleanup_partial(file_path: str) -> None:
    """Remove a partially downloaded file if it exists."""
    p = Path(file_path)
    p.unlink(missing_ok=True)
    # Also remove .part files yt-dlp may leave behind
    p.with_suffix(p.suffix + ".part").unlink(missing_ok=True)
