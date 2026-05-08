"""通知系统后端测试。"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from database import Base
from models import Notification, PushSubscription, User


@pytest.fixture()
def db_session():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()
    engine.dispose()


@pytest.fixture()
def user(db_session):
    u = User(
        username="testuser",
        hashed_password=User.hash_password("password123"),
        email="test@example.com",
    )
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    return u


@pytest.fixture()
def user2(db_session):
    u = User(
        username="otheruser",
        hashed_password=User.hash_password("password456"),
    )
    db_session.add(u)
    db_session.commit()
    db_session.refresh(u)
    return u


# ── Notification 模型 ─────────────────────────────────────────


class TestNotificationModel:
    def test_create_and_to_dict(self, db_session, user):
        n = Notification(
            user_id=user.id,
            type="task_completed",
            title="完成",
            message="任务完成",
            link="/report/abc",
            metadata_={"task_id": "abc"},
        )
        db_session.add(n)
        db_session.commit()
        db_session.refresh(n)

        assert n.id is not None
        assert n.is_read is False
        d = n.to_dict()
        assert d["type"] == "task_completed"
        assert d["title"] == "完成"
        assert d["is_read"] is False
        assert d["metadata"] == {"task_id": "abc"}
        assert d["link"] == "/report/abc"
        assert d["created_at"] is not None

    def test_metadata_column_name(self, db_session, user):
        n = Notification(user_id=user.id, type="t", title="T", message="M")
        db_session.add(n)
        db_session.commit()
        # SQLAlchemy column is metadata_, DB column is metadata
        assert n.metadata_ is None
        d = n.to_dict()
        assert d["metadata"] is None


# ── create_notification ──────────────────────────────────────


class TestCreateNotification:
    def test_creates_in_db(self, db_session, user):
        from services.notification_service import create_notification

        n = create_notification(
            db_session, user.id, "task_failed", "失败", "分析失败",
            link="/report/xyz", metadata={"task_id": "xyz"},
        )
        assert n.id is not None
        assert n.user_id == user.id
        assert n.type == "task_failed"
        assert n.link == "/report/xyz"

        stored = db_session.query(Notification).filter_by(id=n.id).first()
        assert stored is not None
        assert stored.metadata_ == {"task_id": "xyz"}

    def test_emit_called(self, db_session, user):
        from services.notification_service import create_notification, emitter

        received = []

        async def cb(payload):
            received.append(payload)

        emitter.set_loop(__import__("asyncio").get_event_loop())
        emitter.subscribe(user.id, cb)

        n = create_notification(db_session, user.id, "test", "T", "M")
        # emit uses run_coroutine_threadsafe, give it a moment
        import asyncio
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.sleep(0.05))

        assert len(received) == 1
        assert received[0]["type"] == "notification"
        assert received[0]["notification"]["id"] == n.id
        assert received[0]["unread_count"] == 1

        emitter.unsubscribe(user.id, cb)

    def test_emit_failure_does_not_block(self, db_session, user):
        from services.notification_service import create_notification, emitter

        def bad_cb(payload):
            raise RuntimeError("boom")

        emitter.set_loop(__import__("asyncio").get_event_loop())
        emitter.subscribe(user.id, bad_cb)

        # Should not raise
        n = create_notification(db_session, user.id, "test", "T", "M")
        assert n is not None

        emitter.unsubscribe(user.id, bad_cb)


# ── get_notifications ─────────────────────────────────────────


class TestGetNotifications:
    def _seed(self, db_session, user, count=5):
        from services.notification_service import create_notification
        for i in range(count):
            create_notification(
                db_session, user.id, f"type_{i}", f"Title {i}", f"Message {i}",
            )

    def test_pagination(self, db_session, user):
        from services.notification_service import get_notifications
        self._seed(db_session, user, 5)

        items, total, unread = get_notifications(db_session, user.id, page=1, page_size=2)
        assert len(items) == 2
        assert total == 5
        assert unread == 5

        items2, total2, _ = get_notifications(db_session, user.id, page=3, page_size=2)
        assert len(items2) == 1

    def test_unread_only(self, db_session, user):
        from services.notification_service import get_notifications, mark_notifications_read
        self._seed(db_session, user, 3)
        all_items, _, _ = get_notifications(db_session, user.id)
        mark_notifications_read(db_session, [all_items[0]["id"]], user.id)

        items, total, unread = get_notifications(db_session, user.id, unread_only=True)
        assert total == 2
        assert unread == 2

    def test_filter_by_type(self, db_session, user):
        from services.notification_service import create_notification, get_notifications
        create_notification(db_session, user.id, "alpha", "A", "a")
        create_notification(db_session, user.id, "beta", "B", "b")
        create_notification(db_session, user.id, "alpha", "A2", "a2")

        items, total, _ = get_notifications(db_session, user.id, type="alpha")
        assert total == 2

    def test_other_user_isolation(self, db_session, user, user2):
        from services.notification_service import create_notification, get_notifications
        create_notification(db_session, user.id, "t", "T", "M")
        create_notification(db_session, user2.id, "t", "T2", "M2")

        items, total, _ = get_notifications(db_session, user.id)
        assert total == 1
        assert items[0]["title"] == "T"


# ── get_unread_count ──────────────────────────────────────────


class TestGetUnreadCount:
    def test_empty(self, db_session, user):
        from services.notification_service import get_unread_count
        assert get_unread_count(db_session, user.id) == 0

    def test_counts_unread(self, db_session, user):
        from services.notification_service import create_notification, get_unread_count, mark_notifications_read
        create_notification(db_session, user.id, "t", "T", "M")
        create_notification(db_session, user.id, "t", "T", "M")
        assert get_unread_count(db_session, user.id) == 2

        n = db_session.query(Notification).first()
        mark_notifications_read(db_session, [n.id], user.id)
        assert get_unread_count(db_session, user.id) == 1


# ── mark_notifications_read ──────────────────────────────────


class TestMarkRead:
    def test_marks_specific_ids(self, db_session, user):
        from services.notification_service import create_notification, mark_notifications_read, get_unread_count
        n1 = create_notification(db_session, user.id, "t", "T1", "M1")
        n2 = create_notification(db_session, user.id, "t", "T2", "M2")
        n3 = create_notification(db_session, user.id, "t", "T3", "M3")

        mark_notifications_read(db_session, [n1.id, n3.id], user.id)
        assert get_unread_count(db_session, user.id) == 1

        db_session.refresh(n1)
        db_session.refresh(n2)
        assert n1.is_read is True
        assert n2.is_read is False

    def test_ignores_other_users_ids(self, db_session, user, user2):
        from services.notification_service import create_notification, mark_notifications_read, get_unread_count
        n = create_notification(db_session, user2.id, "t", "T", "M")
        mark_notifications_read(db_session, [n.id], user.id)
        assert get_unread_count(db_session, user2.id) == 1


# ── mark_all_read ─────────────────────────────────────────────


class TestMarkAllRead:
    def test_marks_all(self, db_session, user):
        from services.notification_service import create_notification, mark_all_read, get_unread_count
        for i in range(4):
            create_notification(db_session, user.id, "t", f"T{i}", f"M{i}")

        mark_all_read(db_session, user.id)
        assert get_unread_count(db_session, user.id) == 0

    def test_only_affects_own(self, db_session, user, user2):
        from services.notification_service import create_notification, mark_all_read, get_unread_count
        create_notification(db_session, user.id, "t", "T", "M")
        create_notification(db_session, user2.id, "t", "T2", "M2")

        mark_all_read(db_session, user.id)
        assert get_unread_count(db_session, user.id) == 0
        assert get_unread_count(db_session, user2.id) == 1


# ── delete_notification ───────────────────────────────────────


class TestDeleteNotification:
    def test_deletes_existing(self, db_session, user):
        from services.notification_service import create_notification, delete_notification
        n = create_notification(db_session, user.id, "t", "T", "M")
        assert delete_notification(db_session, n.id, user.id) is True
        assert db_session.query(Notification).filter_by(id=n.id).first() is None

    def test_returns_false_for_missing(self, db_session, user):
        from services.notification_service import delete_notification
        assert delete_notification(db_session, 9999, user.id) is False

    def test_cannot_delete_others(self, db_session, user, user2):
        from services.notification_service import create_notification, delete_notification
        n = create_notification(db_session, user2.id, "t", "T", "M")
        assert delete_notification(db_session, n.id, user.id) is False


# ── NotificationEmitter ──────────────────────────────────────


class TestEmitter:
    def test_subscribe_and_emit(self):
        from services.notification_service import NotificationEmitter
        import asyncio

        emitter = NotificationEmitter()
        loop = asyncio.new_event_loop()
        emitter.set_loop(loop)

        received = []

        async def cb(payload):
            received.append(payload)

        emitter.subscribe(1, cb)
        emitter.emit(1, {"hello": "world"})
        loop.run_until_complete(asyncio.sleep(0.05))

        assert len(received) == 1
        assert received[0] == {"hello": "world"}

        emitter.unsubscribe(1, cb)
        emitter.emit(1, {"hello": "again"})
        loop.run_until_complete(asyncio.sleep(0.05))
        assert len(received) == 1

        loop.close()

    def test_no_loop_does_not_crash(self):
        from services.notification_service import NotificationEmitter

        emitter = NotificationEmitter()
        # Should not raise
        emitter.emit(99, {"test": True})

    def test_multiple_subscribers(self):
        from services.notification_service import NotificationEmitter
        import asyncio

        emitter = NotificationEmitter()
        loop = asyncio.new_event_loop()
        emitter.set_loop(loop)

        results_a, results_b = [], []

        async def cb_a(p):
            results_a.append(p)

        async def cb_b(p):
            results_b.append(p)

        emitter.subscribe(1, cb_a)
        emitter.subscribe(1, cb_b)
        emitter.emit(1, {"x": 1})
        loop.run_until_complete(asyncio.sleep(0.05))

        assert len(results_a) == 1
        assert len(results_b) == 1

        emitter.unsubscribe(1, cb_a)
        emitter.emit(1, {"x": 2})
        loop.run_until_complete(asyncio.sleep(0.05))

        assert len(results_a) == 1
        assert len(results_b) == 2

        loop.close()
