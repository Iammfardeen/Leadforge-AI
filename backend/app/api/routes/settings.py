"""
Settings — per-user preferences and API keys (Google Places, SMTP, AI model
choice, brand logo, business name, theme).

Secrets (google_places_api_key, smtp_password) are stored in user_settings
and never echoed back in plaintext on GET — only a masked indicator of
whether a value is set.
"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.core.auth import CurrentUser, get_current_user
from app.db.supabase_client import get_supabase_admin

router = APIRouter(prefix="/settings", tags=["settings"])


class SettingsUpdateRequest(BaseModel):
    business_name: str | None = None
    brand_logo_url: str | None = None
    theme: str | None = None
    ai_model: str | None = None
    google_places_api_key: str | None = None
    google_psi_api_key: str | None = None
    smtp_host: str | None = None
    smtp_port: int | None = None
    smtp_username: str | None = None
    smtp_password: str | None = None
    ollama_base_url: str | None = None


def _mask(value: str | None) -> dict:
    return {"is_set": bool(value)}


@router.get("")
def get_settings_view(user: CurrentUser = Depends(get_current_user)):
    db = get_supabase_admin()

    profile_resp = db.table("profiles").select("*").eq("id", user.id).single().execute()
    settings_resp = db.table("user_settings").select("*").eq("user_id", user.id).maybe_single().execute()

    profile = profile_resp.data or {}
    user_settings = settings_resp.data or {}

    return {
        "business_name": profile.get("business_name"),
        "brand_logo_url": profile.get("brand_logo_url"),
        "theme": profile.get("theme", "dark"),
        "ai_model": profile.get("ai_model", "llama-3.3-70b-versatile"),
        "ollama_base_url": user_settings.get("ollama_base_url", "http://localhost:11434"),
        "google_places_api_key": _mask(user_settings.get("google_places_api_key")),
        "google_psi_api_key": _mask(user_settings.get("google_psi_api_key")),
        "smtp_host": user_settings.get("smtp_host"),
        "smtp_port": user_settings.get("smtp_port"),
        "smtp_username": user_settings.get("smtp_username"),
        "smtp_password": _mask(user_settings.get("smtp_password")),
    }


@router.patch("")
def update_settings(payload: SettingsUpdateRequest, user: CurrentUser = Depends(get_current_user)):
    db = get_supabase_admin()
    data = payload.model_dump(exclude_unset=True)

    profile_fields = {k: v for k, v in data.items() if k in ("business_name", "brand_logo_url", "theme", "ai_model")}
    settings_fields = {
        k: v
        for k, v in data.items()
        if k in ("google_places_api_key", "google_psi_api_key", "smtp_host", "smtp_port", "smtp_username", "smtp_password", "ollama_base_url")
    }

    if profile_fields:
        db.table("profiles").update(profile_fields).eq("id", user.id).execute()

    if settings_fields:
        settings_fields["user_id"] = user.id
        db.table("user_settings").upsert(settings_fields, on_conflict="user_id").execute()

    return {"status": "updated"}
