"""弹幕批量存储服务测试。"""

from __future__ import annotations

import json
import os
import sys
import tempfile
from pathlib import Path

import pytest

# 必须在 import database 之前设置，否则会尝试连接 PostgreSQL
os.environ["DATABASE_URL"] = "sqlite://"

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from database import Base, SessionLocal, engine
from models import Danmu, DanmuBatch, User
from services.danmu_service import (
    batch_insert_danmus,
    get_danmu_batch_detail,
    get_danmu_batches,
    get_danmu_by_batch,
)


@pytest.fixture(autouse=True)
def setup_db():
    """每个测试前重建内存数据库。"""
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture
def user(db) -> User:
    u = User(username="testuser", hashed_password="hashed")
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


def _write_json(items: list[dict]) -> str:
    fd, path = tempfile.mkstemp(suffix=".json")
    with os.fdopen(fd, "w") as f:
        json.dump(items, f)
    return path


def _write_csv(content: str) -> str:
    fd, path = tempfile.mkstemp(suffix=".csv")
    with os.fdopen(fd, "w") as f:
        f.write(content)
    return path


class TestBatchInsertDanmus:
    def test_json_batch_insert(self, db, user):
        items = [
            {"timestamp": 1.0, "content": "hello", "username": "alice"},
            {"timestamp": 2.0, "content": "world", "username": "bob"},
            {"timestamp": 3.0, "content": "test", "username": "charlie"},
        ]
        path = _write_json(items)
        batch = batch_insert_danmus(db, user.id, path, "json", "test.json")
        os.unlink(path)

        assert batch.status == "completed"
        assert batch.total_count == 3
        assert batch.success_count == 3
        assert batch.failed_count == 0
        assert batch.filename == "test.json"
        assert batch.file_format == "json"
        assert batch.start_timestamp == 1.0
        assert batch.end_timestamp == 3.0
        assert batch.completed_at is not None
        assert batch.batch_id

    def test_csv_batch_insert(self, db, user):
        csv_content = "timestamp,content,username\n1.0,hello,alice\n2.0,world,bob\n"
        path = _write_csv(csv_content)
        batch = batch_insert_danmus(db, user.id, path, "csv", "test.csv")
        os.unlink(path)

        assert batch.status == "completed"
        assert batch.total_count == 2
        assert batch.success_count == 2

    def test_dedup_within_batch(self, db, user):
        items = [
            {"timestamp": 1.0, "content": "hello", "username": "alice"},
            {"timestamp": 1.0, "content": "hello", "username": "alice"},  # duplicate
            {"timestamp": 2.0, "content": "world", "username": "bob"},
        ]
        path = _write_json(items)
        batch = batch_insert_danmus(db, user.id, path, "json", "dup.json")
        os.unlink(path)

        assert batch.total_count == 3
        assert batch.success_count == 2  # duplicate skipped

    def test_failed_parse(self, db, user):
        fd, path = tempfile.mkstemp(suffix=".json")
        with os.fdopen(fd, "w") as f:
            f.write("not json")
        batch = batch_insert_danmus(db, user.id, path, "json", "bad.json")
        os.unlink(path)

        assert batch.status == "failed"
        assert batch.error_message

    def test_danmu_records_created(self, db, user):
        items = [
            {"timestamp": 1.0, "content": "a", "username": "u1"},
            {"timestamp": 2.0, "content": "b", "username": "u2"},
        ]
        path = _write_json(items)
        batch = batch_insert_danmus(db, user.id, path, "json", "t.json")
        os.unlink(path)

        danmus = db.query(Danmu).filter(Danmu.user_id == user.id).all()
        assert len(danmus) == 2
        contents = {d.content for d in danmus}
        assert contents == {"a", "b"}


class TestGetDanmuBatches:
    def test_returns_user_batches(self, db, user):
        items = [{"timestamp": 1.0, "content": "x", "username": "u"}]
        path = _write_json(items)
        batch_insert_danmus(db, user.id, path, "json", "a.json")
        batch_insert_danmus(db, user.id, path, "json", "b.json")
        os.unlink(path)

        batches = get_danmu_batches(db, user.id)
        assert len(batches) == 2

    def test_empty_for_no_batches(self, db, user):
        batches = get_danmu_batches(db, user.id)
        assert batches == []


class TestGetDanmuBatchDetail:
    def test_found(self, db, user):
        items = [{"timestamp": 1.0, "content": "x", "username": "u"}]
        path = _write_json(items)
        batch = batch_insert_danmus(db, user.id, path, "json", "t.json")
        os.unlink(path)

        detail = get_danmu_batch_detail(db, batch.id)
        assert detail is not None
        assert detail.id == batch.id

    def test_not_found(self, db):
        assert get_danmu_batch_detail(db, 999) is None


class TestGetDanmuByBatch:
    def test_returns_danmus(self, db, user):
        items = [
            {"timestamp": 1.0, "content": "a", "username": "u1"},
            {"timestamp": 2.0, "content": "b", "username": "u2"},
        ]
        path = _write_json(items)
        batch = batch_insert_danmus(db, user.id, path, "json", "t.json")
        os.unlink(path)

        danmus = get_danmu_by_batch(db, batch.id)
        assert len(danmus) == 2
        # ordered by timestamp
        assert danmus[0].timestamp <= danmus[1].timestamp

    def test_limit(self, db, user):
        items = [{"timestamp": float(i), "content": f"d{i}", "username": "u"} for i in range(10)]
        path = _write_json(items)
        batch = batch_insert_danmus(db, user.id, path, "json", "t.json")
        os.unlink(path)

        danmus = get_danmu_by_batch(db, batch.id, limit=3)
        assert len(danmus) == 3

    def test_empty_for_nonexistent_batch(self, db):
        danmus = get_danmu_by_batch(db, 999)
        assert danmus == []
