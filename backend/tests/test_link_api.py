"""Tests for the link analysis API endpoints."""

import os
import sys
import time
import uuid
from pathlib import Path
from unittest.mock import patch, MagicMock

TEST_ROOT = Path(__file__).resolve().parents[2] / ".tmp" / "link_api_tests"


def _load_app():
    TEST_ROOT.mkdir(parents=True, exist_ok=True)
    os.environ["DATABASE_URL"] = "sqlite://"
    os.environ["UPLOAD_DIR"] = str(TEST_ROOT / "uploads")
    os.environ["DOWNLOAD_DIR"] = str(TEST_ROOT / "downloads")
    os.environ["TRANSCRIPTION_PROVIDER"] = "mock"
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

    import main
    return main.app


def _auth_headers(client):
    from fastapi.testclient import TestClient
    username = f"link_user_{uuid.uuid4().hex[:8]}"
    password = "Passw0rd!"

    client.post(
        "/auth/register",
        json={"username": username, "email": f"{username}@example.com", "password": password},
    )
    login = client.post(
        "/auth/login",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


class TestLinkInfoEndpoint:
    def test_requires_auth(self):
        from fastapi.testclient import TestClient
        client = TestClient(_load_app())
        resp = client.get("/api/link-info", params={"url": "https://www.douyin.com/video/123"})
        assert resp.status_code == 401

    @patch("routes.core_link.get_link_info")
    def test_returns_info(self, mock_info):
        from fastapi.testclient import TestClient
        mock_info.return_value = MagicMock(
            platform="douyin",
            video_id="123",
            title="Test Live",
            duration=300,
            thumbnail_url="https://example.com/thumb.jpg",
            uploader="Streamer",
            error=None,
        )
        client = TestClient(_load_app())
        headers = _auth_headers(client)
        resp = client.get(
            "/api/link-info",
            params={"url": "https://www.douyin.com/video/123"},
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["success"] is True
        assert data["data"]["platform"] == "douyin"
        assert data["data"]["title"] == "Test Live"

    def test_empty_url_returns_400(self):
        from fastapi.testclient import TestClient
        client = TestClient(_load_app())
        headers = _auth_headers(client)
        resp = client.get("/api/link-info", params={"url": ""}, headers=headers)
        assert resp.status_code == 400


class TestAnalyzeLinkEndpoint:
    def test_requires_auth(self):
        from fastapi.testclient import TestClient
        client = TestClient(_load_app())
        resp = client.post("/api/analyze-link", json={"url": "https://www.douyin.com/video/123"})
        assert resp.status_code == 401

    def test_unsupported_url_returns_400(self):
        from fastapi.testclient import TestClient
        client = TestClient(_load_app())
        headers = _auth_headers(client)
        resp = client.post(
            "/api/analyze-link",
            json={"url": "https://www.youtube.com/watch?v=abc"},
            headers=headers,
        )
        assert resp.status_code == 400
        assert "Unsupported" in resp.json()["detail"]

    def test_empty_url_returns_400(self):
        from fastapi.testclient import TestClient
        client = TestClient(_load_app())
        headers = _auth_headers(client)
        resp = client.post("/api/analyze-link", json={"url": "  "}, headers=headers)
        assert resp.status_code == 400

    @patch("routes.core_link.get_task_queue")
    @patch("routes.core_link.get_link_info")
    def test_submit_creates_task(self, mock_info, mock_queue):
        from fastapi.testclient import TestClient
        mock_info.return_value = MagicMock(
            platform="douyin",
            video_id="456",
            title="My Live Replay",
            duration=600,
            thumbnail_url="",
            uploader="Streamer",
            error=None,
        )
        mock_queue.return_value = MagicMock()

        client = TestClient(_load_app())
        headers = _auth_headers(client)
        resp = client.post(
            "/api/analyze-link",
            json={"url": "https://www.douyin.com/video/456"},
            headers=headers,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "task_id" in data
        assert data["source_type"] == "link"
        assert data["status"] == "pending"

    @patch("routes.core_link.get_task_queue")
    @patch("routes.core_link.get_link_info")
    def test_quota_enforcement(self, mock_info, mock_queue):
        from fastapi.testclient import TestClient
        mock_info.return_value = MagicMock(
            platform="douyin",
            video_id="789",
            title="Live",
            duration=100,
            thumbnail_url="",
            uploader="U",
            error=None,
        )
        mock_queue.return_value = MagicMock()

        client = TestClient(_load_app())
        headers = _auth_headers(client)

        # Exhaust the default quota (2 per week)
        for _ in range(2):
            r = client.post(
                "/api/analyze-link",
                json={"url": "https://www.douyin.com/video/789"},
                headers=headers,
            )
            assert r.status_code == 200

        # Third attempt should be rejected
        r = client.post(
            "/api/analyze-link",
            json={"url": "https://www.douyin.com/video/789"},
            headers=headers,
        )
        assert r.status_code == 429
        assert "quota" in r.json()["detail"].lower()
