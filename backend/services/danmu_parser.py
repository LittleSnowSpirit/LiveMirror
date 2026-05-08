"""弹幕文件解析服务 — 支持 CSV / JSON 格式，自动编码检测。"""

from __future__ import annotations

import csv
import io
import json
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# CSV 列名变体映射 -> 标准字段
_COLUMN_ALIASES: dict[str, list[str]] = {
    "timestamp": ["timestamp", "time", "ts", "datetime", "date", "created_at", "时间"],
    "content": ["content", "text", "msg", "message", "danmu", "弹幕", "内容"],
    "username": ["username", "user", "name", "nickname", "用户", "昵称"],
}

_DETECTED_COLUMNS: dict[str, str] = {}


def _resolve_column(header: str) -> Optional[str]:
    """将 CSV 列名映射到标准字段名。"""
    lower = header.strip().lower()
    for field, aliases in _COLUMN_ALIASES.items():
        if lower in aliases:
            return field
    return None


def _read_file_with_encoding(file_path: str) -> str:
    """读取文件，优先 UTF-8，fallback GBK。"""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    raw = path.read_bytes()

    for encoding in ("utf-8-sig", "utf-8"):
        try:
            return raw.decode(encoding)
        except (UnicodeDecodeError, ValueError):
            continue

    try:
        return raw.decode("gbk")
    except (UnicodeDecodeError, ValueError) as exc:
        raise ValueError(f"Unable to decode file with UTF-8 or GBK: {file_path}") from exc


def _parse_timestamp(value: str) -> float:
    """将时间戳字符串转为 float 秒数。支持纯数字和 mm:ss / HH:MM:SS 格式。"""
    value = value.strip()
    if not value:
        raise ValueError("Empty timestamp")

    # 尝试直接解析为数字
    try:
        return float(value)
    except ValueError:
        pass

    # 尝试 mm:ss 或 HH:MM:SS
    parts = value.split(":")
    if len(parts) == 2:
        try:
            minutes, seconds = parts
            return float(minutes) * 60 + float(seconds)
        except ValueError:
            pass
    elif len(parts) == 3:
        try:
            hours, minutes, seconds = parts
            return float(hours) * 3600 + float(minutes) * 60 + float(seconds)
        except ValueError:
            pass

    raise ValueError(f"Cannot parse timestamp: {value!r}")


def _parse_csv(content: str) -> list[dict]:
    """解析 CSV 格式弹幕。"""
    reader = csv.DictReader(io.StringIO(content))
    if not reader.fieldnames:
        return []

    # 建立列名映射
    column_map: dict[str, str] = {}
    for header in reader.fieldnames:
        field = _resolve_column(header)
        if field:
            column_map[field] = header

    if "content" not in column_map:
        raise ValueError(
            f"CSV missing required 'content' column. "
            f"Found columns: {reader.fieldnames}"
        )

    results: list[dict] = []
    warnings: list[str] = []

    for row_idx, row in enumerate(reader, start=2):  # 行号从 2 开始（1 是 header）
        try:
            content_val = row.get(column_map["content"], "").strip()
            if not content_val:
                continue

            ts_raw = row.get(column_map.get("timestamp", ""), "").strip()
            timestamp = _parse_timestamp(ts_raw) if ts_raw else 0.0

            username_val = row.get(column_map.get("username", ""), "").strip() or "anonymous"

            results.append({
                "timestamp": timestamp,
                "content": content_val,
                "username": username_val,
            })
        except Exception as exc:
            warnings.append(f"Row {row_idx}: {exc}")

    if warnings:
        logger.warning("CSV parse warnings: %s", "; ".join(warnings[:20]))

    return results


def _parse_json(content: str) -> list[dict]:
    """解析 JSON 格式弹幕。支持数组和嵌套结构。"""
    data = json.loads(content)

    # 支持 {"danmu": [...]} 嵌套结构
    if isinstance(data, dict):
        for key in ("danmu", "danmus", "data", "list", "items", "records"):
            if key in data and isinstance(data[key], list):
                data = data[key]
                break
        else:
            raise ValueError(
                f"JSON object missing list field. Expected one of: danmu, data, list, items, records"
            )

    if not isinstance(data, list):
        raise ValueError("JSON must be an array or an object containing an array.")

    results: list[dict] = []
    warnings: list[str] = []

    for idx, item in enumerate(data):
        try:
            if not isinstance(item, dict):
                warnings.append(f"Item {idx}: not an object, skipped")
                continue

            content_val = ""
            for key in ("content", "text", "msg", "message", "danmu"):
                if key in item and str(item[key]).strip():
                    content_val = str(item[key]).strip()
                    break

            if not content_val:
                continue

            timestamp = 0.0
            for key in ("timestamp", "time", "ts", "datetime"):
                if key in item:
                    try:
                        timestamp = _parse_timestamp(str(item[key]))
                    except ValueError:
                        pass
                    break

            username_val = "anonymous"
            for key in ("username", "user", "name", "nickname"):
                if key in item and str(item[key]).strip():
                    username_val = str(item[key]).strip()
                    break

            results.append({
                "timestamp": timestamp,
                "content": content_val,
                "username": username_val,
            })
        except Exception as exc:
            warnings.append(f"Item {idx}: {exc}")

    if warnings:
        logger.warning("JSON parse warnings: %s", "; ".join(warnings[:20]))

    return results


def parse_danmu_file(file_path: str, file_format: str) -> list[dict]:
    """解析弹幕文件，返回统一结构列表。

    Args:
        file_path: 文件路径
        file_format: 文件格式 ("csv" 或 "json")

    Returns:
        [{"timestamp": float, "content": str, "username": str}, ...]
    """
    content = _read_file_with_encoding(file_path)

    fmt = file_format.strip().lower()
    if fmt == "csv":
        return _parse_csv(content)
    elif fmt == "json":
        return _parse_json(content)
    else:
        raise ValueError(f"Unsupported format: {file_format!r}. Use 'csv' or 'json'.")
