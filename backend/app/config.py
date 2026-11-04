from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = ROOT / ".env"
_last_mtime: float | None = None


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(ENV_FILE), extra="ignore")

    BOT_TOKEN: str = ""
    FAL_KEY: str = ""
    ADMIN_PASSWORD: str = ""
    SESSION_SECRET: str = ""
    DATABASE_URL: str = f"sqlite:///{(ROOT / 'data' / 'whitmore.db').as_posix()}"
    UPLOAD_DIR: str = str(ROOT / "data" / "uploads")
    APP_URL: str = "http://localhost:8000"  # public base URL (https in production)
    MODE: str = "local"  # local = long polling, production = webhook
    WEBHOOK_SECRET: str = ""
    OWNER_LOGIN: str = "owner"
    INITDATA_MAX_AGE: int = 3600
    FRONTEND_DIST: str = str(ROOT / "frontend" / "dist")

    @property
    def secure_cookies(self) -> bool:
        return self.APP_URL.startswith("https://")


@lru_cache
def _cached_settings() -> Settings:
    return Settings()


def get_settings() -> Settings:
    global _last_mtime
    try:
        mtime = ENV_FILE.stat().st_mtime if ENV_FILE.exists() else None
    except OSError:
        mtime = None
    if mtime != _last_mtime:
        _cached_settings.cache_clear()
        _last_mtime = mtime
    return _cached_settings()
