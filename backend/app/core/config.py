"""
Centralized application configuration.

All values are read from environment variables (see .env.example).
Nothing here should be hardcoded with real secrets — local Docker dev
uses the .env file, production uses Railway/Render env vars.
"""
import json
from functools import lru_cache
from typing import List, Union

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- App ---
    APP_NAME: str = "LeadForge AI"
    ENV: str = "development"  # development | production
    API_V1_PREFIX: str = "/api/v1"
    DEBUG: bool = True

    # --- CORS ---
    # We update the type to Union to allow adaptive string interception
    CORS_ORIGINS: Union[List[str], str] = ["http://localhost:3000"]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        # If it's already a clean list from local defaults, pass it right through
        if isinstance(v, list):
            return v
        
        if isinstance(v, str):
            v = v.strip()
            # If the environment variable is empty, fallback to local dev url
            if not v:
                return ["http://localhost:3000"]
            
            # If it looks like a JSON array string, attempt parsing it
            if v.startswith("[") and v.endswith("]"):
                try:
                    return json.loads(v)
                except json.JSONDecodeError:
                    pass  # Fall back to standard parsing if quotes are malformed
            
            # Bulletproof fallback: split by commas if it's a standard list string
            return [item.strip() for item in v.split(",") if item.strip()]
            
        return v

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
