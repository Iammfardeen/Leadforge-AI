"""
WhatsApp Generator.

IMPORTANT: this app NEVER sends messages automatically. This route only
generates text content and persists it for the Copy button in the UI.
There is intentionally no integration with the WhatsApp Business API here.
"""
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.core.auth import CurrentUser, get_current_user
from app.db.supabase_client import get_supabase_admin
from app.services import whatsapp as whatsapp_service

router = APIRouter(prefix="/whatsapp", tags=["whatsapp"])


class WhatsAppGenerateRequest(BaseModel):
    tone: Literal["professional", "friendly", "luxury"] = "professional"
    length: Literal["short", "long"] = "short"
    language: Literal["en", "hi"] = "en"


@router.post("/{lead_id}/generate")
def generate_message(lead_id: str, payload: WhatsAppGenerateRequest, user: CurrentUser = Depends(get_current_user)):
    db = get_supabase_admin()
    lead_resp = db.table("leads").select("*").eq("id", lead_id).eq("user_id", user.id).single().execute()
    if not lead_resp.data:
        raise HTTPException(status_code=404, detail="Lead not found")

    profile_resp = db.table("profiles").select("ai_model").eq("id", user.id).maybe_single().execute()
    preferred_model = (profile_resp.data or {}).get("ai_model") or "llama3"

    content = whatsapp_service.generate_message(
        lead=lead_resp.data,
        tone=payload.tone,
        length=payload.length,
        language=payload.language,
        model=preferred_model,
    )

    row = {
        "lead_id": lead_id,
        "user_id": user.id,
        "tone": payload.tone,
        "length": payload.length,
        "language": payload.language,
        "content": content,
    }
    insert_resp = db.table("whatsapp_messages").insert(row).execute()
    return insert_resp.data[0]


@router.get("/{lead_id}/history")
def message_history(lead_id: str, user: CurrentUser = Depends(get_current_user)):
    db = get_supabase_admin()
    resp = (
        db.table("whatsapp_messages")
        .select("*")
        .eq("lead_id", lead_id)
        .eq("user_id", user.id)
        .order("created_at", desc=True)
        .execute()
    )
    return {"messages": resp.data}
