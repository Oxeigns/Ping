from __future__ import annotations

"""Configuration models and helpers."""

from pydantic import Field, ValidationError, field_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    API_ID: int = Field(..., description="Telegram API ID")
    API_HASH: str = Field(..., description="Telegram API hash")
    BOT_TOKEN: str = Field(..., description="Bot token")
    OWNER_ID: int = Field(..., description="Owner user ID")

    LOG_CHANNEL: int = Field(0, alias="LOG_CHANNEL_ID")
    MODLOG_CHANNEL: int = Field(0, alias="MODLOG_CHANNEL_ID")
    MONGO_URI: str = Field("mongodb://localhost:27017", description="MongoDB URI")
    PANEL_IMAGE: str = Field("", description="Optional panel image URL")
    DEV_URL: str = Field("https://t.me/botsyard", description="Developer URL")
    DEV_NAME: str = Field("Developer", description="Developer name")
    SUCCESS_EMOJI: str = Field("✅")
    ERROR_EMOJI: str = Field("❌")
    WARNING_EMOJI: str = Field("⚠️")
    SUDO_USERS: set[int] = Field(default_factory=set)

    class Config:
        env_file = ".env"
        case_sensitive = False

    @field_validator("SUDO_USERS", mode="before")
    def _split_sudo(cls, v: str | set[int] | None) -> set[int]:
        if not v:
            return set()
        if isinstance(v, set):
            return v
        return {int(x) for x in str(v).split() if x}

    def model_post_init(self, __context) -> None:  # pragma: no cover - pydantic hook
        if not self.SUDO_USERS:
            self.SUDO_USERS = {self.OWNER_ID}


try:  # pragma: no cover - executed at import time
    Config = Settings()
except ValidationError as exc:  # pragma: no cover - configuration must be valid
    raise RuntimeError(f"Configuration error: {exc}") from exc


def validate() -> None:
    """Compatibility wrapper for legacy calls."""
    # Instantiating ``Config`` already validates all fields
    _ = Config
