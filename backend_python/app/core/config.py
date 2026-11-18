import os
from pathlib import Path
from typing import Optional

try:
    from dotenv import load_dotenv
    from pydantic_settings import BaseSettings, SettingsConfigDict

    BASE_DIR = Path(__file__).resolve().parents[2]
    load_dotenv(BASE_DIR / ".env")

    class Settings(BaseSettings):
        APP_NAME: str = "Automação GP - API de Integrações"
        DEBUG: bool = True
        PORT: int = 8000
        AUTH_SECRET: Optional[str] = None

        DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/automacao_gp"
        REDIS_URL: str = "redis://localhost:6379/0"

        # Etapa 1: Lead Search (Google Places / Apify)
        GOOGLE_PLACES_API_KEY: Optional[str] = None
        APIFY_API_KEY: Optional[str] = None
        LEAD_PROVIDER: str = "google"
        AI_PROVIDER: str = "gemini"

        # Etapa 2: Digital Triage
        GOOGLE_PAGESPEED_API_KEY: Optional[str] = None
        META_GRAPH_ACCESS_TOKEN: Optional[str] = None
        META_INSTAGRAM_ACCOUNT_ID: Optional[str] = None
        RAPIDAPI_KEY: Optional[str] = None
        RAPIDAPI_HOST: Optional[str] = None

        # Etapa 3 & 4: Diagnosis & Stitch Prompting
        ANTHROPIC_API_KEY: Optional[str] = None
        CLAUDE_MODEL: str = "claude-3-5-haiku-20241022"
        GEMINI_API_KEY: Optional[str] = None
        GEMINI_MODEL: str = "gemini-2.5-flash"

        # Etapa 5: Site Generation
        GOOGLE_STITCH_API_KEY: Optional[str] = None
        GOOGLE_STITCH_BASE_URL: str = "https://stitch.googleapis.com/v1"

        model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    settings = Settings()

except ImportError:
    # Fallback to standard os.getenv if pydantic_settings is not installed yet
    from dotenv import load_dotenv

    BASE_DIR = Path(__file__).resolve().parents[2]
    load_dotenv(BASE_DIR / ".env")

    class SettingsFallback:
        APP_NAME: str = os.getenv("APP_NAME", "Automação GP - API de Integrações")
        DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
        PORT: int = int(os.getenv("PORT", "8000"))
        AUTH_SECRET: Optional[str] = os.getenv("AUTH_SECRET")

        DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/automacao_gp")
        REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

        GOOGLE_PLACES_API_KEY: Optional[str] = os.getenv("GOOGLE_PLACES_API_KEY")
        APIFY_API_KEY: Optional[str] = os.getenv("APIFY_API_KEY")
        LEAD_PROVIDER: str = os.getenv("LEAD_PROVIDER", "google")
        AI_PROVIDER: str = os.getenv("AI_PROVIDER", "gemini")
        GOOGLE_PAGESPEED_API_KEY: Optional[str] = os.getenv("GOOGLE_PAGESPEED_API_KEY")
        META_GRAPH_ACCESS_TOKEN: Optional[str] = os.getenv("META_GRAPH_ACCESS_TOKEN")
        META_INSTAGRAM_ACCOUNT_ID: Optional[str] = os.getenv("META_INSTAGRAM_ACCOUNT_ID")
        RAPIDAPI_KEY: Optional[str] = os.getenv("RAPIDAPI_KEY")
        RAPIDAPI_HOST: Optional[str] = os.getenv("RAPIDAPI_HOST")

        ANTHROPIC_API_KEY: Optional[str] = os.getenv("ANTHROPIC_API_KEY")
        CLAUDE_MODEL: str = os.getenv("CLAUDE_MODEL", "claude-3-5-haiku-20241022")
        GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
        GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

        GOOGLE_STITCH_API_KEY: Optional[str] = os.getenv("GOOGLE_STITCH_API_KEY")
        GOOGLE_STITCH_BASE_URL: str = os.getenv("GOOGLE_STITCH_BASE_URL", "https://stitch.googleapis.com/v1")

    settings = SettingsFallback()
