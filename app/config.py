import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import dotenv_values

MAX_UPLOAD_BYTES = 5 * 1024 * 1024
MAX_JOB_CHARS = 20_000
MAX_CV_CHARS = 40_000


@dataclass(frozen=True)
class Settings:
    database_url: str
    session_secret: str
    ollama_api_key: str
    ollama_model: str = "gemma4:31b"
    ollama_host: str = "https://ollama.com"
    cookie_secure: bool = False
    max_upload_bytes: int = MAX_UPLOAD_BYTES


def normalize_database_url(url: str) -> str:
    if url.startswith("postgres://"):
        return "postgresql+psycopg://" + url[len("postgres://") :]
    if url.startswith("postgresql://") and "+psycopg" not in url.split("://", 1)[0]:
        return "postgresql+psycopg://" + url[len("postgresql://") :]
    return url


def apply_env_file(path: Path) -> None:
    """Fill blank process variables from a .env file. A non-blank process value wins."""
    if not path.is_file():
        return
    for key, value in dotenv_values(path).items():
        if not value or not str(value).strip():
            continue
        current = os.environ.get(key)
        if current is None or not current.strip():
            os.environ[key] = str(value).strip()


def load_settings() -> Settings:
    apply_env_file(Path(__file__).resolve().parent.parent / ".env")
    url = os.environ.get("DATABASE_URL", "sqlite:///./data/greengrass.db")
    secret = os.environ.get("SESSION_SECRET", "dev-only-change-me")
    return Settings(
        database_url=normalize_database_url(url),
        session_secret=secret,
        ollama_api_key=os.environ.get("OLLAMA_API_KEY", "").strip(),
        ollama_model=os.environ.get("OLLAMA_MODEL", "gemma4:31b"),
        ollama_host=os.environ.get("OLLAMA_HOST", "https://ollama.com"),
        cookie_secure=os.environ.get("COOKIE_SECURE", "0") == "1",
    )


def ensure_sqlite_parent(url: str) -> None:
    if not url.startswith("sqlite:///"):
        return
    path = url.removeprefix("sqlite:///")
    if path == ":memory:" or path.startswith("file:"):
        return
    Path(path).parent.mkdir(parents=True, exist_ok=True)
