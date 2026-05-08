"""
配置管理模块
"""
from pathlib import Path
from typing import Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent


class CoreSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    app_name: str = "LiveMirror"
    app_version: str = "2.5.0"
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True

    database_url: str = "postgresql://livemirror:livemirror@localhost:5432/livemirror"
    redis_url: str = "redis://localhost:6379/0"
    upload_dir: str = "./uploads"
    max_file_size: int = 2 * 1024 * 1024 * 1024
    allowed_extensions: str = "mp3,wav,m4a,mp4,avi,mov"

    cors_origins: str = "http://localhost:3000,http://localhost:5173,http://localhost:5174"
    secret_key: str = "change-me-in-production"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    task_worker_count: int = 2

    transcription_provider: str = "local"
    whisper_model: str = "base"
    whisper_language: Optional[str] = "zh"
    whisper_device: str = "auto"
    whisper_compute_type: str = "default"

    dashscope_api_key: Optional[str] = None
    dashscope_model: str = "qwen-plus"
    dashscope_asr_model: str = "paraformer-v2"
    openai_api_key: Optional[str] = None
    openai_api_base: str = "https://api.openai.com/v1"

    # Link analysis
    yt_dlp_path: str = "yt-dlp"
    download_dir: str = "./uploads/downloads"
    max_download_duration: int = 600

    log_level: str = "INFO"

    # VAPID for Web Push
    vapid_private_key: str = ""
    vapid_public_key: str = ""
    vapid_subject: str = "mailto:admin@livemirror.com"

    @field_validator("upload_dir")
    @classmethod
    def normalize_upload_dir(cls, value: str) -> str:
        path = Path(value)
        if not path.is_absolute():
            path = BASE_DIR / path
        path.mkdir(parents=True, exist_ok=True)
        return str(path)

    @field_validator("download_dir")
    @classmethod
    def normalize_download_dir(cls, value: str) -> str:
        path = Path(value)
        if not path.is_absolute():
            path = BASE_DIR / path
        path.mkdir(parents=True, exist_ok=True)
        return str(path)

    @field_validator("database_url")
    @classmethod
    def normalize_database_url(cls, value: str) -> str:
        sqlite_prefix = "sqlite:///"
        if value == "sqlite:///:memory:" or not value.startswith(sqlite_prefix):
            return value

        db_path = Path(value[len(sqlite_prefix):])
        if db_path.is_absolute():
            return value

        if db_path.parent == Path(".") and db_path.name == "livemirror.db":
            db_path = Path("data") / "livemirror-dev.db"

        return f"{sqlite_prefix}{(BASE_DIR / db_path).as_posix()}"

    @property
    def allowed_extension_set(self) -> set[str]:
        return {item.strip().lower() for item in self.allowed_extensions.split(",") if item.strip()}

    @property
    def cors_origin_list(self) -> list[str]:
        if self.cors_origins.strip() == "*":
            return ["*"]
        return [item.strip() for item in self.cors_origins.split(",") if item.strip()]


settings = CoreSettings()
