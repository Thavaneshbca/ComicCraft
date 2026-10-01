"""Configuration settings for ComicCraft."""

from pathlib import Path
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Application configuration settings loaded from environment or .env file."""

    # Project paths
    BASE_DIR: Path = BASE_DIR
    STATIC_DIR: Path = BASE_DIR / "static"
    PANELS_DIR: Path = BASE_DIR / "static" / "panels"
    EXPORTS_DIR: Path = BASE_DIR / "static" / "exports"
    TEMPLATES_DIR: Path = BASE_DIR / "templates"

    # Application Mode
    MOCK_AI: bool = True
    DEBUG: bool = True
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # Google Gemini Models & API
    GEMINI_API_KEY: str = ""
    GEMINI_OUTLINE_MODEL: str = "gemini-1.5-flash"
    GEMINI_STORY_MODEL: str = "gemini-1.5-pro"

    # Image Generation
    IMAGE_PROVIDER: Literal["huggingface", "local", "mock"] = "huggingface"
    HF_API_KEY: str = ""
    HF_IMAGE_MODEL: str = "runwayml/stable-diffusion-v1-5"

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()

# Ensure critical directories exist
settings.PANELS_DIR.mkdir(parents=True, exist_ok=True)
settings.EXPORTS_DIR.mkdir(parents=True, exist_ok=True)
