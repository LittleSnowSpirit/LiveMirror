"""Tests for share link endpoints."""

import os
import sys
import time
import uuid
from pathlib import Path

from fastapi.testclient import TestClient

TEST_ROOT = Path(__file__).resolve().parents[2] / ".tmp" / "share_tests"


def _load_app():
    TEST_ROOT.mkdir(parents=True, exist_ok=True)
    os.environ["DATABASE_URL"] = "sqlite://"
    os.environ["UPLOAD_DIR"] = str(TEST_ROOT / "uploads")
    os.environ["TRANSCRIPTION_PROVIDER"] = "mock"
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import main

    return main.app


def _auth_headers(client: TestClient) -> dict[str, str]:
    username = f"share_user_{uuid.uuid4().hex}"
    password = "Passw0rd!"
    register = client.post(
        "/auth/register",
        json={"username": username, "email": f"{username}@example.com", "password": password},
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


def _create_share(client: TestClient, headers: dict, task_id: str) -> dict:
    resp = client.post(
        "/api/share",
        json={"task_id": task_id},
        headers=headers,
    )
    assert resp.status_code == 200
    return resp.json()["share"]


# ==================== Create Share ====================


def test_create_share():
    client = TestClient(_load_app())
    headers = _auth_headers(client)
    task_id = _upload_and_complete(client, headers)

    resp = client.post("/api/share", json={"task_id": task_id}, headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    share = body["share"]
    assert len(share["token"]) == 8
    assert len(share["access_code"]) == 4
    assert share["task_id"] == task_id


def test_create_share_with_expiry():
    client = TestClient(_load_app())
    headers = _auth_headers(client)
    task_id = _upload_and_complete(client, headers)

    resp = client.post(
        "/api/share",
        json={"task_id": task_id, "expires_in_days": 7},
        headers=headers,
    )
    assert resp.status_code == 200
    share = resp.json()["share"]
    assert share["expires_at"] is not None


def test_create_share_not_found():
    client = TestClient(_load_app())
    headers = _auth_headers(client)
    resp = client.post("/api/share", json={"task_id": "nonexistent"}, headers=headers)
    assert resp.status_code == 404


def test_create_share_requires_auth():
    client = TestClient(_load_app())
    resp = client.post("/api/share", json={"task_id": "x"})
    assert resp.status_code == 401


# ==================== Get Share ====================


def test_get_share_with_valid_code():
    client = TestClient(_load_app())
    headers = _auth_headers(client)
    task_id = _upload_and_complete(client, headers)
    share = _create_share(client, headers, task_id)

    resp = client.get(
        f"/api/share/{share['token']}?access_code={share['access_code']}",
        headers=headers,
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    assert "report" in body


def test_get_share_invalid_code():
    client = TestClient(_load_app())
    headers = _auth_headers(client)
    task_id = _upload_and_complete(client, headers)
    share = _create_share(client, headers, task_id)

    resp = client.get(
        f"/api/share/{share['token']}?access_code=0000",
        headers=headers,
    )
    assert resp.status_code == 403


def test_get_share_not_found():
    client = TestClient(_load_app())
    headers = _auth_headers(client)
    resp = client.get("/api/share/zzzzzzzz?access_code=1234", headers=headers)
    assert resp.status_code == 404


def test_get_share_increments_view_count():
    client = TestClient(_load_app())
    headers = _auth_headers(client)
    task_id = _upload_and_complete(client, headers)
    share = _create_share(client, headers, task_id)

    client.get(
        f"/api/share/{share['token']}?access_code={share['access_code']}",
        headers=headers,
    )
    resp = client.get(
        f"/api/share/{share['token']}?access_code={share['access_code']}",
        headers=headers,
    )
    assert resp.json()["share"]["view_count"] == 2


# ==================== Delete Share ====================


def test_delete_share():
    client = TestClient(_load_app())
    headers = _auth_headers(client)
    task_id = _upload_and_complete(client, headers)
    share = _create_share(client, headers, task_id)

    resp = client.delete(f"/api/share/{share['token']}", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["success"] is True

    resp = client.get(
        f"/api/share/{share['token']}?access_code={share['access_code']}",
        headers=headers,
    )
    assert resp.status_code == 404


def test_delete_share_requires_owner():
    client = TestClient(_load_app())
    headers1 = _auth_headers(client)
    task_id = _upload_and_complete(client, headers1)
    share = _create_share(client, headers1, task_id)

    headers2 = _auth_headers(client)
    resp = client.delete(f"/api/share/{share['token']}", headers=headers2)
    assert resp.status_code == 403


# ==================== List Shares ====================


def test_list_shares_empty():
    client = TestClient(_load_app())
    headers = _auth_headers(client)
    resp = client.get("/api/shares", headers=headers)
    assert resp.status_code == 200
    assert resp.json()["success"] is True
    assert isinstance(resp.json()["shares"], list)


def test_list_shares():
    client = TestClient(_load_app())
    headers = _auth_headers(client)
    task_id = _upload_and_complete(client, headers)
    _create_share(client, headers, task_id)

    resp = client.get("/api/shares", headers=headers)
    assert len(resp.json()["shares"]) >= 1


def test_list_shares_requires_auth():
    client = TestClient(_load_app())
    assert client.get("/api/shares").status_code == 401
