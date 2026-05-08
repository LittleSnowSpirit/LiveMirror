"""弹幕文件解析服务测试。"""

from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from services.danmu_parser import parse_danmu_file


# ============ CSV Tests ============


class TestParseCSV:
    def _write(self, content: str, encoding: str = "utf-8") -> str:
        fd, path = tempfile.mkstemp(suffix=".csv")
        with os.fdopen(fd, "wb") as f:
            f.write(content.encode(encoding))
        return path

    def test_basic_csv(self):
        path = self._write("timestamp,content,username\n1.0,hello,alice\n2.5,world,bob\n")
        result = parse_danmu_file(path, "csv")
        assert len(result) == 2
        assert result[0]["timestamp"] == 1.0
        assert result[0]["content"] == "hello"
        assert result[0]["username"] == "alice"
        assert result[1]["timestamp"] == 2.5
        os.unlink(path)

    def test_column_aliases(self):
        path = self._write("time,text,user\n10,good morning,charlie\n")
        result = parse_danmu_file(path, "csv")
        assert len(result) == 1
        assert result[0]["timestamp"] == 10.0
        assert result[0]["content"] == "good morning"
        assert result[0]["username"] == "charlie"
        os.unlink(path)

    def test_chinese_columns(self):
        path = self._write("时间,内容,昵称\n5,你好,小明\n", encoding="utf-8")
        result = parse_danmu_file(path, "csv")
        assert len(result) == 1
        assert result[0]["content"] == "你好"
        assert result[0]["username"] == "小明"
        os.unlink(path)

    def test_mm_ss_timestamp(self):
        path = self._write("timestamp,content,username\n1:30,hello,alice\n")
        result = parse_danmu_file(path, "csv")
        assert result[0]["timestamp"] == 90.0
        os.unlink(path)

    def test_hh_mm_ss_timestamp(self):
        path = self._write("timestamp,content,username\n1:30:45,hello,alice\n")
        result = parse_danmu_file(path, "csv")
        assert result[0]["timestamp"] == 5445.0
        os.unlink(path)

    def test_skip_empty_rows(self):
        path = self._write("timestamp,content,username\n1.0,hello,alice\n,,\n2.0,world,bob\n")
        result = parse_danmu_file(path, "csv")
        assert len(result) == 2
        os.unlink(path)

    def test_empty_content_skipped(self):
        path = self._write("timestamp,content,username\n1.0,,alice\n2.0,world,bob\n")
        result = parse_danmu_file(path, "csv")
        assert len(result) == 1
        assert result[0]["content"] == "world"
        os.unlink(path)

    def test_missing_content_column_raises(self):
        path = self._write("timestamp,foo,bar\n1.0,hello,alice\n")
        with pytest.raises(ValueError, match="missing required.*content"):
            parse_danmu_file(path, "csv")
        os.unlink(path)

    def test_default_username_anonymous(self):
        path = self._write("timestamp,content\n1.0,hello\n")
        result = parse_danmu_file(path, "csv")
        assert result[0]["username"] == "anonymous"
        os.unlink(path)


# ============ JSON Tests ============


class TestParseJSON:
    def _write(self, data, encoding: str = "utf-8") -> str:
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "wb") as f:
            f.write(json.dumps(data, ensure_ascii=False).encode(encoding))
        return path

    def test_array_format(self):
        data = [
            {"timestamp": 1.0, "content": "hello", "username": "alice"},
            {"timestamp": 2.5, "content": "world", "username": "bob"},
        ]
        path = self._write(data)
        result = parse_danmu_file(path, "json")
        assert len(result) == 2
        assert result[0]["content"] == "hello"
        os.unlink(path)

    def test_nested_danmu_key(self):
        data = {"danmu": [
            {"timestamp": 1.0, "content": "test", "username": "user1"},
        ]}
        path = self._write(data)
        result = parse_danmu_file(path, "json")
        assert len(result) == 1
        assert result[0]["content"] == "test"
        os.unlink(path)

    def test_nested_data_key(self):
        data = {"data": [{"timestamp": 1.0, "content": "x", "username": "u"}]}
        path = self._write(data)
        result = parse_danmu_file(path, "json")
        assert len(result) == 1
        os.unlink(path)

    def test_nested_list_key(self):
        data = {"list": [{"timestamp": 1.0, "content": "y", "username": "v"}]}
        path = self._write(data)
        result = parse_danmu_file(path, "json")
        assert len(result) == 1
        os.unlink(path)

    def test_text_alias(self):
        data = [{"time": 10, "text": "hi", "user": "charlie"}]
        path = self._write(data)
        result = parse_danmu_file(path, "json")
        assert result[0]["content"] == "hi"
        assert result[0]["username"] == "charlie"
        assert result[0]["timestamp"] == 10.0
        os.unlink(path)

    def test_skip_non_dict_items(self):
        data = [1, "string", {"timestamp": 1.0, "content": "ok", "username": "u"}]
        path = self._write(data)
        result = parse_danmu_file(path, "json")
        assert len(result) == 1
        assert result[0]["content"] == "ok"
        os.unlink(path)

    def test_missing_content_skipped(self):
        data = [{"timestamp": 1.0}, {"timestamp": 2.0, "content": "ok"}]
        path = self._write(data)
        result = parse_danmu_file(path, "json")
        assert len(result) == 1
        os.unlink(path)

    def test_invalid_nested_key_raises(self):
        data = {"unknown_key": []}
        path = self._write(data)
        with pytest.raises(ValueError, match="missing list field"):
            parse_danmu_file(path, "json")
        os.unlink(path)


# ============ Encoding Tests ============


class TestEncoding:
    def _write_bytes(self, content: bytes, suffix: str = ".csv") -> str:
        fd, path = tempfile.mkstemp(suffix=suffix)
        with os.fdopen(fd, "wb") as f:
            f.write(content)
        return path

    def test_utf8_bom(self):
        csv_bytes = "﻿timestamp,content,username\n1.0,hello,alice\n".encode("utf-8-sig")
        path = self._write_bytes(csv_bytes)
        result = parse_danmu_file(path, "csv")
        assert result[0]["content"] == "hello"
        os.unlink(path)

    def test_gbk_fallback(self):
        csv_bytes = "timestamp,content,username\n1.0,你好,小明\n".encode("gbk")
        path = self._write_bytes(csv_bytes)
        result = parse_danmu_file(path, "csv")
        assert result[0]["content"] == "你好"
        os.unlink(path)

    def test_json_utf8_chinese(self):
        data = [{"timestamp": 1.0, "content": "测试弹幕", "username": "用户A"}]
        json_bytes = json.dumps(data, ensure_ascii=False).encode("utf-8")
        path = self._write_bytes(json_bytes, suffix=".json")
        result = parse_danmu_file(path, "json")
        assert result[0]["content"] == "测试弹幕"
        os.unlink(path)


# ============ Error Handling Tests ============


class TestErrorHandling:
    def test_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            parse_danmu_file("/nonexistent/file.csv", "csv")

    def test_unsupported_format(self):
        fd, path = tempfile.mkstemp(suffix=".txt")
        with os.fdopen(fd, "w") as f:
            f.write("hello")
        with pytest.raises(ValueError, match="Unsupported format"):
            parse_danmu_file(path, "xml")
        os.unlink(path)

    def test_empty_csv(self):
        fd, path = tempfile.mkstemp(suffix=".csv")
        with os.fdopen(fd, "w") as f:
            f.write("timestamp,content,username\n")
        result = parse_danmu_file(path, "csv")
        assert result == []
        os.unlink(path)

    def test_empty_json_array(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w") as f:
            json.dump([], f)
        result = parse_danmu_file(path, "json")
        assert result == []
        os.unlink(path)

    def test_invalid_json_raises(self):
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w") as f:
            f.write("{not valid json")
        with pytest.raises(json.JSONDecodeError):
            parse_danmu_file(path, "json")
        os.unlink(path)

    def test_csv_invalid_timestamp_skips_row(self):
        fd, path = tempfile.mkstemp(suffix=".csv")
        with os.fdopen(fd, "w") as f:
            f.write("timestamp,content,username\nnot_a_number,hello,alice\n2.0,world,bob\n")
        result = parse_danmu_file(path, "csv")
        # invalid timestamp row is skipped (logged as warning)
        assert len(result) == 1
        assert result[0]["content"] == "world"
        os.unlink(path)
