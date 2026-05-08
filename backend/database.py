"""Database engine, sessions, and migrations."""

from __future__ import annotations

from pathlib import Path

from sqlalchemy import create_engine, event, inspect
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.pool import StaticPool

from config import settings as _settings


BASE_DIR = Path(__file__).resolve().parent


def _connect_args(database_url: str) -> dict:
    if database_url.startswith("sqlite"):
        return {"check_same_thread": False}
    return {}


def _is_memory_sqlite(database_url: str) -> bool:
    return database_url in {"sqlite://", "sqlite:///:memory:"}


def _is_sqlite(database_url: str) -> bool:
    return database_url.startswith("sqlite")


_engine_kwargs = {
    "connect_args": _connect_args(_settings.database_url),
    "pool_pre_ping": True,
}
if _is_memory_sqlite(_settings.database_url):
    _engine_kwargs["poolclass"] = StaticPool

engine = create_engine(_settings.database_url, **_engine_kwargs)

if _is_sqlite(_settings.database_url):
    @event.listens_for(engine, "connect")
    def _set_sqlite_pragmas(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        if _is_memory_sqlite(_settings.database_url):
            cursor.execute("PRAGMA journal_mode=OFF")
            cursor.execute("PRAGMA synchronous=OFF")
        else:
            cursor.execute("PRAGMA journal_mode=WAL")
            cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()


SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db() -> None:
    import models  # noqa: F401

    if _is_memory_sqlite(_settings.database_url):
        Base.metadata.create_all(bind=engine)
        return

    if _should_stamp_existing_database():
        _stamp_alembic_head()
        return

    if not _run_alembic_upgrade():
        Base.metadata.create_all(bind=engine)


def _should_stamp_existing_database() -> bool:
    if not _is_sqlite(_settings.database_url):
        return False

    inspector = inspect(engine)
    tables = set(inspector.get_table_names())
    known_tables = {"users", "tasks", "danmus", "analysis_reports"}
    return bool(tables & known_tables) and "alembic_version" not in tables


def _run_alembic_upgrade() -> bool:
    try:
        from alembic import command
        from alembic.config import Config
    except ImportError:
        return False

    config = _alembic_config()
    command.upgrade(config, "head")
    return True


def _stamp_alembic_head() -> None:
    try:
        from alembic import command
    except ImportError:
        return

    command.stamp(_alembic_config(), "head")


def _alembic_config():
    from alembic.config import Config

    config = Config(str(BASE_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(BASE_DIR / "migrations"))
    config.set_main_option("sqlalchemy.url", _settings.database_url)
    return config


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
