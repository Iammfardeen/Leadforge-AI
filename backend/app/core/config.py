"""
Centralized application configuration.

All values are read from environment variables (see .env.example).
Nothing here should be hardcoded with real secrets — local Docker dev
uses the .env file, production uses Railway/Render env vars.
"""
from functools import lru_cache
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- App ---
    APP_NAME: str = "LeadForge AI"
    ENV: str = "development"  # development | production
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True

    # --- CORS ---
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # --- Supabase ---
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_JWT_SECRET: str = ""

    # --- Database (direct Postgres connection, used by backend for raw queries) ---
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/leadforge"

    # --- Groq (hosted AI, free tier — replaces local Ollama for deployment) ---
    GROQ_API_KEY: str = ""
    GROQ_DEFAULT_MODEL: str = "llama-3.3-70b-versatile"

    # --- Google Places (user-supplied key; this is only a fallback default) ---
    GOOGLE_PLACES_API_KEY: str = ""

    # --- Storage ---
    STORAGE_BUCKET_SCREENSHOTS: str = "screenshots"
    STORAGE_BUCKET_PROPOSALS: str = "proposals"
    STORAGE_BUCKET_REPORTS: str = "reports"

    # --- Playwright / screenshot service ---
    SCREENSHOT_TIMEOUT_MS: int = 30000


@lru_cache
def get_settings() -> Settings:
    return Settings()
