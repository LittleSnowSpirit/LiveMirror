"""Tests for user profile and avatar endpoints."""

import io
import os
import sys
import uuid
from pathlib import Path

from fastapi.testclient import TestClient

TEST_ROOT = Path(__file__).resolve().parents[2] / ".tmp" / "profile_tests"


def _load_app():
    TEST_ROOT.mkdir(parents=True, exist_ok=True)
    os.environ["DATABASE_URL"] = "sqlite://"
    os.environ["UPLOAD_DIR"] = str(TEST_ROOT / "uploads")
    os.environ["TRANSCRIPTION_PROVIDER"] = "mock"
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    import main

    return main.app


def _auth_headers(client: TestClient) -> dict[str, str]:
    username = f"profile_user_{uuid.uuid4().hex}"
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


# ==================== Get Profile ====================


def test_get_profile():
    client = TestClient(_load_app())
    headers = _auth_headers(client)
    resp = client.get("/api/user/profile", headers=headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["success"] is True
    profile = body["profile"]
    assert "username" in profile
    assert "nickname" in profile
    assert "bio" in profile
    assert "avatar_url" in profile


def test_get_profile_requires_auth():
    client = TestClient(_load_app())
    assert client.get("/api/user/profile").status_code == 401


# ==================== Update Profile ====================


def test_update_profile_nickname():
    client = TestClient(_load_app())
    headers = _auth_headers(client)
    resp = client.put(
        "/api/user/profile",
        json={"nickname": "TestNick"},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["profile"]["nickname"] == "TestNick"


def test_update_profile_bio():
    client = TestClient(_load_app())
    headers = _auth_headers(client)
    resp = client.put(
        "/api/user/profile",
        json={"bio": "I am a streamer"},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["profile"]["bio"] == "I am a streamer"


def test_update_profile_persists():
    client = TestClient(_load_app())
    headers = _auth_headers(client)
    client.put("/api/user/profile", json={"nickname": "Persist"}, headers=headers)

    resp = client.get("/api/user/profile", headers=headers)
    assert resp.json()["profile"]["nickname"] == "Persist"


def test_update_profile_requires_auth():
    client = TestClient(_load_app())
    assert client.put("/api/user/profile", json={"nickname": "x"}).status_code == 401


# ==================== Avatar Upload ====================


def _make_png_bytes() -> bytes:
    """Create a minimal valid PNG file."""
    from PIL import Image

    buf = io.BytesIO()
    img = Image.new("RGB", (10, 10), color="red")
    img.save(buf, format="PNG")
    return buf.getvalue()


def _make_jpg_bytes() -> bytes:
    """Create a minimal valid JPEG file."""
    from PIL import Image

    buf = io.BytesIO()
    img = Image.new("RGB", (10, 10), color="blue")
    img.save(buf, format="JPEG")
    return buf.getvalue()


def test_upload_avatar_png():
    client = TestClient(_load_app())
    headers = _auth_headers(client)
    resp = client.post(
        "/api/user/avatar",
        files={"file": ("avatar.png", _make_png_bytes(), "image/png")},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["success"] is True
    assert "avatar_url" in resp.json()


def test_upload_avatar_jpg():
    client = TestClient(_load_app())
    headers = _auth_headers(client)
    resp = client.post(
        "/api/user/avatar",
        files={"file": ("avatar.jpg", _make_jpg_bytes(), "image/jpeg")},
        headers=headers,
    )
    assert resp.status_code == 200
    assert resp.json()["avatar_url"].endswith(".jpg")


def test_avatar_invalid_type():
    client = TestClient(_load_app())
    headers = _auth_headers(client)
    resp = client.post(
        "/api/user/avatar",
        files={"file": ("avatar.gif", b"GIF89a", "image/gif")},
        headers=headers,
    )
    assert resp.status_code == 400


def test_avatar_too_large():
    client = TestClient(_load_app())
    headers = _auth_headers(client)
    big_data = b"\x00" * (2 * 1024 * 1024 + 1)
    resp = client.post(
        "/api/user/avatar",
        files={"file": ("big.png", big_data, "image/png")},
        headers=headers,
    )
    assert resp.status_code == 400


def test_avatar_persists():
    client = TestClient(_load_app())
    headers = _auth_headers(client)
    client.post(
        "/api/user/avatar",
        files={"file": ("avatar.png", _make_png_bytes(), "image/png")},
        headers=headers,
    )
    resp = client.get("/api/user/profile", headers=headers)
    assert resp.json()["profile"]["avatar_url"] is not None


def test_avatar_requires_auth():
    client = TestClient(_load_app())
    assert client.post(
        "/api/user/avatar",
        files={"file": ("avatar.png", _make_png_bytes(), "image/png")},
    ).status_code == 401
