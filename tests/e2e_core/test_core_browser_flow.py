import os
import re
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

import pytest
from playwright.sync_api import expect, sync_playwright


ROOT = Path(__file__).resolve().parents[2]
RUNTIME = ROOT / "tests" / "e2e_core" / ".runtime"
ARTIFACTS = RUNTIME / "artifacts"
BACKEND_URL = "http://127.0.0.1:8100"
FRONTEND_URL = "http://127.0.0.1:3100"


def _wait_for_url(url: str, timeout: float = 45.0) -> None:
    deadline = time.time() + timeout
    last_error: Exception | None = None

    while time.time() < deadline:
        try:
            with urlopen(url, timeout=2) as response:
                if 200 <= response.status < 500:
                    return
        except (OSError, URLError) as exc:
            last_error = exc
        time.sleep(0.5)

    raise RuntimeError(f"Timed out waiting for {url}: {last_error}")


def _terminate(process: subprocess.Popen) -> None:
    if process.poll() is not None:
        return

    if os.name == "nt":
        subprocess.run(
            ["taskkill", "/PID", str(process.pid), "/T", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
        return

    process.terminate()
    try:
        process.wait(timeout=8)
    except subprocess.TimeoutExpired:
        process.kill()


def _fill_auth_form(page, *values: str) -> None:
    inputs = page.locator(".auth-form input")
    for index, value in enumerate(values):
        inputs.nth(index).fill(value)


def _click_primary_in(page, selector: str) -> None:
    page.locator(selector).locator("button.el-button--primary").first.click()


@pytest.fixture(scope="session")
def live_servers():
    RUNTIME.mkdir(parents=True, exist_ok=True)
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    (RUNTIME / "uploads").mkdir(parents=True, exist_ok=True)

    backend_env = os.environ.copy()
    backend_env.update(
        {
            "DATABASE_URL": "sqlite://",
            "TRANSCRIPTION_PROVIDER": "mock",
            "UPLOAD_DIR": str(RUNTIME / "uploads"),
            "PORT": "8100",
            "CORS_ORIGINS": FRONTEND_URL,
        }
    )

    frontend_env = os.environ.copy()
    frontend_env.update(
        {
            "VITE_API_BASE_URL": f"{BACKEND_URL}/api",
            "VITE_AUTH_BASE_URL": BACKEND_URL,
        }
    )

    backend_out = (ARTIFACTS / "backend.out.log").open("w", encoding="utf-8")
    backend_err = (ARTIFACTS / "backend.err.log").open("w", encoding="utf-8")
    frontend_out = (ARTIFACTS / "frontend.out.log").open("w", encoding="utf-8")
    frontend_err = (ARTIFACTS / "frontend.err.log").open("w", encoding="utf-8")

    backend = subprocess.Popen(
        [sys.executable, "main.py"],
        cwd=ROOT / "backend",
        env=backend_env,
        stdout=backend_out,
        stderr=backend_err,
        text=True,
    )

    try:
        _wait_for_url(f"{BACKEND_URL}/health")

        npm_command = "npm.cmd" if os.name == "nt" else "npm"
        frontend = subprocess.Popen(
            [npm_command, "run", "dev", "--", "--host", "127.0.0.1", "--port", "3100", "--strictPort"],
            cwd=ROOT / "frontend",
            env=frontend_env,
            stdout=frontend_out,
            stderr=frontend_err,
            text=True,
        )
        _wait_for_url(FRONTEND_URL)

        yield
    finally:
        if "frontend" in locals():
            _terminate(frontend)
        _terminate(backend)
        backend_out.close()
        backend_err.close()
        frontend_out.close()
        frontend_err.close()


@pytest.fixture()
def browser_page(live_servers, request):
    issues: list[str] = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        context = browser.new_context(accept_downloads=True, service_workers="block")
        context.tracing.start(screenshots=True, snapshots=True, sources=True)
        page = context.new_page()

        page.on("pageerror", lambda exc: issues.append(f"pageerror: {exc}"))
        page.on(
            "console",
            lambda msg: issues.append(f"console error: {msg.text}")
            if msg.type == "error"
            and "Failed to load resource: the server responded with a status of 400" not in msg.text
            and "Failed to load resource: the server responded with a status of 401" not in msg.text
            else None,
        )
        page.on(
            "requestfailed",
            lambda req: issues.append(f"request failed: {req.method} {req.url} {req.failure}"),
        )
        page.on(
            "response",
            lambda res: issues.append(f"http {res.status}: {res.url}")
            if (res.status == 404 or res.status >= 500) and not res.url.endswith("/favicon.ico")
            else None,
        )

        try:
            yield page, issues
        except Exception:
            screenshot = ARTIFACTS / f"{request.node.name}.png"
            trace = ARTIFACTS / f"{request.node.name}.zip"
            page.screenshot(path=str(screenshot), full_page=True)
            context.tracing.stop(path=str(trace))
            raise
        else:
            context.tracing.stop()
        finally:
            context.close()
            browser.close()


def _unique_user() -> tuple[str, str, str]:
    suffix = str(int(time.time() * 1000))
    return f"e2e_user_{suffix}", f"e2e_{suffix}@example.com", "Passw0rd!"


def _register_and_login(page) -> str:
    username, email, password = _unique_user()

    page.goto(f"{FRONTEND_URL}/register")
    _fill_auth_form(page, username, email, password, password)
    page.locator(".auth-form button[type=submit]").click()
    expect(page).to_have_url(re.compile(r".*/login$"), timeout=10_000)

    _fill_auth_form(page, username, password)
    page.locator(".auth-form button[type=submit]").click()
    expect(page).to_have_url(re.compile(r".*/$"), timeout=10_000)
    return username


def test_register_login_and_me(browser_page):
    page, issues = browser_page
    username, email, password = _unique_user()

    page.goto(f"{FRONTEND_URL}/register")
    _fill_auth_form(page, username, email, password, password)
    page.locator(".auth-form button[type=submit]").click()
    expect(page).to_have_url(re.compile(r".*/login$"), timeout=10_000)

    page.goto(f"{FRONTEND_URL}/register")
    _fill_auth_form(page, username, email, password, password)
    page.locator(".auth-form button[type=submit]").click()
    expect(page.get_by_text("Username already exists.")).to_be_visible(timeout=10_000)

    _fill_auth_form(page, username, email, "123", "123")
    page.locator(".auth-form button[type=submit]").click()
    expect(page.get_by_text("密码长度至少 6 位")).to_be_visible(timeout=10_000)

    _fill_auth_form(page, username, email, password, f"{password}x")
    page.locator(".auth-form button[type=submit]").click()
    expect(page.get_by_text("两次输入的密码不一致")).to_be_visible(timeout=10_000)

    page.goto(f"{FRONTEND_URL}/login")
    _fill_auth_form(page, username, "wrong-password")
    page.locator(".auth-form button[type=submit]").click()
    expect(page.get_by_text("Invalid username or password.")).to_be_visible(timeout=10_000)

    _fill_auth_form(page, username, password)
    page.locator(".auth-form button[type=submit]").click()
    expect(page).to_have_url(re.compile(r".*/$"), timeout=10_000)

    profile = page.evaluate(
        f"""async () => {{
            const token = localStorage.getItem('access_token');
            const response = await fetch('{BACKEND_URL}/auth/me', {{
                headers: {{ Authorization: `Bearer ${{token}}` }}
            }});
            return await response.json();
        }}"""
    )
    assert profile["username"] == username
    assert not issues


def test_upload_report_export_and_analysis_pages(browser_page):
    page, issues = browser_page
    _register_and_login(page)

    sample = RUNTIME / "sample.wav"
    sample.write_bytes(b"RIFF....WAVEfmt fake audio bytes for mock provider")

    page.goto(f"{FRONTEND_URL}/upload")
    expect(page).to_have_url(re.compile(r".*/upload$"), timeout=10_000)

    page.locator("input[type=file]").set_input_files(str(sample))
    expect(page.get_by_text("sample.wav")).to_be_visible()
    _click_primary_in(page, ".actions")
    expect(page.locator(".result-box")).to_be_visible(timeout=20_000)

    task_id = page.locator(".result-box dl div").nth(0).locator("dd").inner_text(timeout=10_000).strip()
    assert task_id

    _click_primary_in(page, ".result-box")
    expect(page).to_have_url(re.compile(r".*/report/.+"), timeout=10_000)

    status_tag = page.locator(".el-tag").first
    for _ in range(30):
        if "已完成" in status_tag.inner_text(timeout=5_000):
            break
        page.locator(".header-actions button").first.click()
        time.sleep(0.5)
    expect(page.get_by_text("转写文本")).to_be_visible()
    expect(page.get_by_text("分析结果")).to_be_visible()

    with page.expect_download() as json_download:
        page.get_by_role("button", name="导出 JSON").click()
    assert json_download.value.suggested_filename.endswith(".json")

    with page.expect_download() as markdown_download:
        page.get_by_role("button", name="导出 Markdown").click()
    assert markdown_download.value.suggested_filename.endswith(".md")

    page.goto(f"{FRONTEND_URL}/attribution")
    page.get_by_role("button", name="填充示例").click()
    page.get_by_role("button", name="开始分析").click()
    expect(page.get_by_text("分析摘要")).to_be_visible(timeout=10_000)

    page.goto(f"{FRONTEND_URL}/suggestions")
    page.get_by_role("button", name="填充示例").click()
    page.get_by_role("button", name="开始分析").click()
    expect(page.get_by_text("分析输出")).to_be_visible(timeout=10_000)

    page.goto(f"{FRONTEND_URL}/trends")
    expect(page.locator(".session-card").first).to_be_visible(timeout=10_000)
    expect(page.get_by_role("button", name="开始分析")).to_be_enabled(timeout=10_000)
    page.get_by_role("button", name="开始分析").click()
    expect(page.get_by_text("成长报告")).to_be_visible(timeout=10_000)

    assert not issues
