"""Tests for history, user quota/usage, and batch export endpoints."""

import os
import sys
import time
import uuid
from pathlib import Path

from fastapi.testclient import TestClient


TEST_ROOT = Path(__file__).resolve().parents[2] / ".tmp" / "new_endpoint_tests"


def _load_app():
    TEST_ROOT.mkdir(parents=True, exist_ok=True)
    os.environ["DATABASE_URL"] = "sqlite://"
    os.environ["UPLOAD_DIR"] = str(TEST_ROOT / "uploads")
    os.environ["TRANSCRIPTION_PROVIDER"] = "mock"
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import main

    return main.app


def _auth_headers(client: TestClient) -> dict[str, str]:
    username = f"new_ep_user_{uuid.uuid4().hex}"
    password = "Passw0rd!"

    register = client.post(
        "/auth/register",
        json={
            "username": username,
            "email": f"{username}@example.com",
            "password": password,
        },
    )
    assert register.status_code == 201

    login = client.post(
        "/auth/login",
        data={"username": username, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login.status_code == 200
    return {"Authorization": f"Bearer {login.json()['access_token']}"}


def _upload_and_complete(client: TestClient, headers: dict) -> str:
    """Upload a file and wait for processing to finish, returning task_id."""
    upload = client.post(
        "/api/upload",
        files={"file": ("sample.wav", b"fake audio bytes", "audio/wav")},
        headers=headers,
    )
    assert upload.status_code == 200
    task_id = upload.json()["task_id"]

    for _ in range(30):
        task = client.get(f"/api/task/{task_id}", headers=headers)
        if task.json()["task"]["status"] in {"completed", "failed"}:
            break
        time.sleep(0.1)

    return task_id


# ==================== History ====================


def test_history_empty():
    client = TestClient(_load_app())
    headers = _auth_headers(client)
    resp = client.get("/api/history", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert isinstance(body["items"], list)
    assert isinstance(body["total"], int)


def test_history_lists_completed_task():
    client = TestClient(_load_app())
    headers = _auth_headers(client)
    task_id = _upload_and_complete(client, headers)

    resp = client.get("/api/history", headers=headers)
    body = resp.json()
    assert body["total"] >= 1
    ids = [item["task_id"] for item in body["items"]]
    assert task_id in ids


def test_history_filter_by_status():
    client = TestClient(_load_app())
    headers = _auth_headers(client)
    _upload_and_complete(client, headers)

    resp = client.get("/api/history?status=completed", headers=headers)
    body = resp.json()
    assert all(item["status"] == "completed" for item in body["items"])

    resp = client.get("/api/history?status=nonexistent", headers=headers)
    assert resp.json()["total"] == 0


def test_history_search_by_filename():
    client = TestClient(_load_app())
    headers = _auth_headers(client)
    _upload_and_complete(client, headers)

    resp = client.get("/api/history?search=sample", headers=headers)
    body = resp.json()
    assert body["total"] >= 1

    resp = client.get("/api/history?search=zzz_no_match", headers=headers)
    assert resp.json()["total"] == 0


def test_history_pagination():
    client = TestClient(_load_app())
    headers = _auth_headers(client)
    for _ in range(3):
        _upload_and_complete(client, headers)

    resp = client.get("/api/history?page=1&page_size=2", headers=headers)
    body = resp.json()
    assert len(body["items"]) <= 2
    assert body["page"] == 1
    assert body["page_size"] == 2
    assert body["total"] >= 3


def test_history_requires_auth():
    client = TestClient(_load_app())
    assert client.get("/api/history").status_code == 401


# ==================== User Quota ====================


def test_user_quota_returns_defaults():
    client = TestClient(_load_app())
    headers = _auth_headers(client)
    resp = client.get("/api/user/quota", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    quota = body["quota"]
    assert quota["weekly_limit"] == 2
    assert quota["used_this_week"] >= 0
    assert quota["remaining"] >= 0
    assert quota["reset_at"]


def test_user_quota_requires_auth():
    client = TestClient(_load_app())
    assert client.get("/api/user/quota").status_code == 401


# ==================== User Usage ====================


def test_user_usage_empty():
    client = TestClient(_load_app())
    headers = _auth_headers(client)
    resp = client.get("/api/user/usage", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert isinstance(body["records"], list)


def test_user_usage_requires_auth():
    client = TestClient(_load_app())
    assert client.get("/api/user/usage").status_code == 401


# ==================== Batch Export ====================


def test_batch_export_empty_ids():
    client = TestClient(_load_app())
    headers = _auth_headers(client)
    resp = client.post(
        "/api/batch-export",
        json={"task_ids": [], "format": "json"},
        headers=headers,
    )
    assert resp.status_code == 400


def test_batch_export_not_found():
    client = TestClient(_load_app())
    headers = _auth_headers(client)
    resp = client.post(
        "/api/batch-export",
        json={"task_ids": ["nonexistent"], "format": "json"},
        headers=headers,
    )
    assert resp.status_code == 404


def test_batch_export_json():
    client = TestClient(_load_app())
    headers = _auth_headers(client)
    task_id = _upload_and_complete(client, headers)

    resp = client.post(
        "/api/batch-export",
        json={"task_ids": [task_id], "format": "json"},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/zip"


def test_batch_export_markdown():
    client = TestClient(_load_app())
    headers = _auth_headers(client)
    task_id = _upload_and_complete(client, headers)

    resp = client.post(
        "/api/batch-export",
        json={"task_ids": [task_id], "format": "markdown"},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "application/zip"


def test_batch_export_requires_auth():
    client = TestClient(_load_app())
    assert client.post(
        "/api/batch-export",
        json={"task_ids": ["x"], "format": "json"},
    ).status_code == 401


# ==================== Features Registry ====================


def test_features_registry_includes_new_endpoints():
    client = TestClient(_load_app())
    headers = _auth_headers(client)
    resp = client.get("/api/features", headers=headers)
    assert resp.status_code == 200
    ids = {f["id"] for f in resp.json()["features"]}
    assert {"history", "user", "batch_export"}.issubset(ids)


def test_root_includes_new_routes():
    client = TestClient(_load_app())
    body = client.get("/").json()
    routes = body["core_routes"]
    assert "/api/history" in routes
    assert "/api/user" in routes
    assert "/api/batch-export" in routes
