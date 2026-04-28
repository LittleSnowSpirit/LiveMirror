import os
import sys
import time
import uuid
from pathlib import Path

from fastapi.testclient import TestClient


TEST_ROOT = Path(__file__).resolve().parents[2] / ".tmp" / "core_api_tests"


def _load_app():
    TEST_ROOT.mkdir(parents=True, exist_ok=True)
    os.environ["DATABASE_URL"] = "sqlite://"
    os.environ["UPLOAD_DIR"] = str(TEST_ROOT / "uploads")
    os.environ["TRANSCRIPTION_PROVIDER"] = "mock"
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import main

    return main.app


def _auth_headers(client: TestClient) -> dict[str, str]:
    username = f"core_user_{uuid.uuid4().hex}"
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


def test_core_health_and_openapi():
    client = TestClient(_load_app())
    assert client.get("/health").status_code == 200
    assert client.get("/openapi.json").status_code == 200
    assert "/api/features" in client.get("/").json()["core_routes"]


def test_upload_to_report_flow_with_mock_transcription():
    client = TestClient(_load_app())
    headers = _auth_headers(client)

    upload = client.post(
        "/api/upload",
        files={"file": ("sample.wav", b"fake audio bytes", "audio/wav")},
        headers=headers,
    )
    assert upload.status_code == 200
    task_id = upload.json()["task_id"]

    task_payload = None
    for _ in range(30):
        task = client.get(f"/api/task/{task_id}", headers=headers)
        assert task.status_code == 200
        task_payload = task.json()["task"]
        if task_payload["status"] in {"completed", "failed"}:
            break
        time.sleep(0.1)

    assert task_payload is not None
    assert task_payload["status"] == "completed"
    assert task_payload["current_step"] == "completed"
    assert task_payload["provider"] == "mock"
    assert task_payload["started_at"]

    report = client.get(f"/api/report/{task_id}", headers=headers)
    assert report.status_code == 200
    payload = report.json()
    assert payload["success"] is True
    assert payload["data"]["transcription"]

    assert client.get(f"/api/export/{task_id}/json", headers=headers).status_code == 200
    markdown = client.get(f"/api/export/{task_id}/markdown", headers=headers)
    assert markdown.status_code == 200
    assert "LiveMirror" in markdown.text


def test_missing_task_returns_404():
    client = TestClient(_load_app())
    headers = _auth_headers(client)
    assert client.get("/api/task/not-found", headers=headers).status_code == 404
    assert client.get("/api/report/not-found", headers=headers).status_code == 404


def test_feature_registry_requires_authentication_and_lists_enabled_modules():
    client = TestClient(_load_app())
    assert client.get("/api/features").status_code == 401

    headers = _auth_headers(client)
    response = client.get("/api/features", headers=headers)
    assert response.status_code == 200

    payload = response.json()
    assert payload["success"] is True
    enabled_ids = {feature["id"] for feature in payload["features"] if feature["enabled"]}
    assert {"upload", "task", "report", "export", "attribution", "suggestions", "trends"}.issubset(enabled_ids)


def test_core_routes_require_authentication():
    client = TestClient(_load_app())
    assert client.get("/api/features").status_code == 401
    assert client.get("/api/task/not-found").status_code == 401
    assert client.get("/api/report/not-found").status_code == 401
    assert client.get("/api/export/not-found/json").status_code == 401
    assert client.post(
        "/api/upload",
        files={"file": ("sample.wav", b"fake audio bytes", "audio/wav")},
    ).status_code == 401
