"""Tests for PDF and image export endpoints."""

import os
import sys
import time
import uuid
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

TEST_ROOT = Path(__file__).resolve().parents[2] / ".tmp" / "export_tests"


def _load_app():
    TEST_ROOT.mkdir(parents=True, exist_ok=True)
    os.environ["DATABASE_URL"] = "sqlite://"
    os.environ["UPLOAD_DIR"] = str(TEST_ROOT / "uploads")
    os.environ["TRANSCRIPTION_PROVIDER"] = "mock"
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import main

    return main.app


def _auth_headers(client: TestClient) -> dict[str, str]:
    username = f"export_user_{uuid.uuid4().hex}"
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


# ==================== PDF Export ====================


def test_export_pdf_compact():
    client = TestClient(_load_app())
    headers = _auth_headers(client)
    task_id = _upload_and_complete(client, headers)

    with patch("services.pdf_generator.generate_pdf") as mock_gen:
        fake_path = str(TEST_ROOT / "fake.pdf")
        Path(fake_path).write_bytes(b"%PDF-1.4 fake")
        mock_gen.return_value = fake_path

        resp = client.get(f"/api/export/{task_id}/pdf?template=compact", headers=headers)
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "application/pdf"
        mock_gen.assert_called_once()
        assert mock_gen.call_args[0][2] == "compact"


def test_export_pdf_detailed():
    client = TestClient(_load_app())
    headers = _auth_headers(client)
    task_id = _upload_and_complete(client, headers)

    with patch("services.pdf_generator.generate_pdf") as mock_gen:
        fake_path = str(TEST_ROOT / "fake.pdf")
        Path(fake_path).write_bytes(b"%PDF-1.4 fake")
        mock_gen.return_value = fake_path

        resp = client.get(f"/api/export/{task_id}/pdf?template=detailed", headers=headers)
        assert resp.status_code == 200
        assert mock_gen.call_args[0][2] == "detailed"


def test_export_pdf_not_found():
    client = TestClient(_load_app())
    headers = _auth_headers(client)
    resp = client.get("/api/export/nonexistent/pdf", headers=headers)
    assert resp.status_code == 404


def test_export_pdf_requires_auth():
    client = TestClient(_load_app())
    assert client.get("/api/export/x/pdf").status_code == 401


# ==================== Image Export ====================


def test_export_image():
    client = TestClient(_load_app())
    headers = _auth_headers(client)
    task_id = _upload_and_complete(client, headers)

    with patch("services.image_exporter.generate_report_image") as mock_gen:
        fake_path = str(TEST_ROOT / "fake.png")
        Path(fake_path).write_bytes(b"\x89PNG fake")
        mock_gen.return_value = fake_path

        resp = client.get(f"/api/export/{task_id}/image", headers=headers)
        assert resp.status_code == 200
        assert resp.headers["content-type"] == "image/png"
        mock_gen.assert_called_once()


def test_export_image_not_found():
    client = TestClient(_load_app())
    headers = _auth_headers(client)
    resp = client.get("/api/export/nonexistent/image", headers=headers)
    assert resp.status_code == 404


def test_export_image_requires_auth():
    client = TestClient(_load_app())
    assert client.get("/api/export/x/image").status_code == 401


# ==================== PDF Generator Unit ====================


def test_pdf_generator_creates_file():
    from services.pdf_generator import generate_pdf

    report = {
        "filename": "test.wav",
        "duration": 60,
        "analysis": {"overall_score": 8},
        "suggestions": [{"priority": "high", "title": "Test", "description": "Desc"}],
        "attribution_analysis": [],
        "summary_text": "Test summary",
    }
    output = generate_pdf("test_unit", report, "compact")
    assert Path(output).exists()
    assert Path(output).stat().st_size > 0
    Path(output).unlink(missing_ok=True)


# ==================== Image Exporter Unit ====================


def test_image_exporter_creates_file():
    from services.image_exporter import generate_report_image

    report = {
        "filename": "test.wav",
        "duration": 60,
        "analysis": {"overall_score": 8},
        "suggestions": [{"priority": "high", "title": "Test", "description": "Desc"}],
        "attribution_analysis": [],
        "summary_text": "Test summary",
    }
    output = generate_report_image("test_unit", report)
    assert Path(output).exists()
    assert Path(output).suffix == ".png"
    Path(output).unlink(missing_ok=True)
